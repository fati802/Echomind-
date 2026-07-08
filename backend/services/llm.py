import os
import logging
import httpx
from backend.models.event import Event

logger = logging.getLogger(__name__)

def is_configured(val: str) -> bool:
    if not val:
        return False
    val_clean = val.strip()
    return val_clean not in ["", "your_key_here", "your_endpoint_here"]

def generate_mock_answer(events: list) -> str:
    """Generates a warm, simple, rule-based response directly from the events."""
    if not events:
        return "I don't have a record of that yet"
        
    has_more = len(events) > 5
    recent_events = events[:5]
    
    # Sort the 5 most recent chronologically (oldest first)
    recent_events = sorted(recent_events, key=lambda e: e.timestamp)
    
    action_map = {
        "placed": "placed",
        "picked_up": "picked up",
        "handed_over": "handed over",
        "observed": "observed"
    }
    
    sentences = []
    for event in recent_events:
        action_str = action_map.get(event.action, event.action)
        actor_str = f"by {event.actor}" if event.actor else ""
        zone_str = f"in/on the {event.zone}" if event.zone else "somewhere"
        dt_str = event.timestamp.strftime("%I:%M %p on %B %d, %Y")
        
        # Determine confidence level hedging
        if event.confidence >= 0.85:
            # Plain statement
            sentence = f"Your {event.object} was {action_str} {actor_str} {zone_str} at {dt_str}."
        elif 0.6 <= event.confidence < 0.85:
            # Hedge gently
            sentence = f"It looks like your {event.object} was {action_str} {actor_str} {zone_str} at {dt_str}."
        else:
            # Hedge strongly and suggest confirming
            sentence = f"I think I saw your {event.object} {action_str} {actor_str} {zone_str} at {dt_str}, but I'm not fully sure — you may want to double check."
            
        # Clean up spaces
        sentence = " ".join(sentence.split())
        sentences.append(sentence)
        
    if has_more and sentences:
        # Strip the period from the last sentence and append the has_more phrase
        sentences[-1] = sentences[-1].rstrip('.') + ", and a few earlier events."
        
    return " ".join(sentences)

def call_fireworks(prompt: str, system_prompt: str, conversation_history: list = None) -> str:
    """Calls Fireworks AI Chat Completion API."""
    api_key = os.getenv("FIREWORKS_API_KEY")
    if not is_configured(api_key):
        raise ValueError("FIREWORKS_API_KEY is missing or empty.")

    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        for turn in conversation_history:
            q = turn.question if hasattr(turn, "question") else turn.get("question", "")
            a = turn.answer if hasattr(turn, "answer") else turn.get("answer", "")
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "accounts/fireworks/models/glm-5p2",
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 150
    }

    response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
    response.raise_for_status()

    result = response.json()
    answer = result["choices"][0]["message"]["content"].strip()
    if not answer:
        raise ValueError("Empty response received from Fireworks AI.")
    return answer

def call_amd_dev_cloud(prompt: str, system_prompt: str, conversation_history: list = None) -> str:
    """Calls AMD Developer Cloud OpenAI-compatible API."""
    api_url = os.getenv("AMD_DEV_CLOUD_API_URL")
    api_key = os.getenv("AMD_DEV_CLOUD_API_KEY")

    if not is_configured(api_url) or not is_configured(api_key):
        raise ValueError("AMD Developer Cloud API URL or API Key is missing or empty.")

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        for turn in conversation_history:
            q = turn.question if hasattr(turn, "question") else turn.get("question", "")
            a = turn.answer if hasattr(turn, "answer") else turn.get("answer", "")
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": prompt})

    model = os.getenv("AMD_DEV_CLOUD_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 150
    }

    response = httpx.post(api_url, headers=headers, json=payload, timeout=10.0)
    response.raise_for_status()

    result = response.json()
    answer = result["choices"][0]["message"]["content"].strip()
    if not answer:
        raise ValueError("Empty response received from AMD Developer Cloud.")
    return answer

def call_llm_provider(prompt: str, system_prompt: str, conversation_history: list = None, events: list = None) -> tuple[str, str]:
    """
    Routes the LLM query logic through configured providers with a cascading fallback.
    Primary is AMD Developer Cloud, secondary is Fireworks AI, and final is mock-template.
    """
    provider = os.getenv("LLM_PROVIDER", "amd").lower().strip()

    if provider == "amd":
        # 1. Try AMD Developer Cloud
        try:
            logger.info("Attempting LLM call via AMD Developer Cloud (primary)...")
            answer = call_amd_dev_cloud(prompt, system_prompt, conversation_history)
            return answer, "amd"
        except Exception as e:
            logger.error(f"AMD Developer Cloud call failed: {str(e)}. Cascading to Fireworks AI...")

        # 2. Try Fireworks AI as backup
        try:
            logger.info("Attempting LLM call via Fireworks AI (backup)...")
            answer = call_fireworks(prompt, system_prompt, conversation_history)
            return answer, "fireworks_fallback"
        except Exception as e:
            logger.error(f"Fireworks AI call failed: {str(e)}. Falling back to mock-template mode...")

        # 3. Fallback to mock template
        return generate_mock_answer(events or []), "mock_fallback"

    elif provider == "fireworks":
        # 1. Try Fireworks AI
        try:
            logger.info("Attempting LLM call via Fireworks AI (primary)...")
            answer = call_fireworks(prompt, system_prompt, conversation_history)
            return answer, "fireworks_fallback"
        except Exception as e:
            logger.error(f"Fireworks AI call failed: {str(e)}. Cascading to AMD Developer Cloud...")

        # 2. Try AMD Developer Cloud as backup
        try:
            logger.info("Attempting LLM call via AMD Developer Cloud (backup)...")
            answer = call_amd_dev_cloud(prompt, system_prompt, conversation_history)
            return answer, "amd"
        except Exception as e:
            logger.error(f"AMD Developer Cloud call failed: {str(e)}. Falling back to mock-template mode...")

        # 3. Fallback to mock template
        return generate_mock_answer(events or []), "mock_fallback"

    else:
        # provider is "mock" or invalid config
        logger.info(f"LLM_PROVIDER is set to '{provider}'. Running in mock mode directly.")
        return generate_mock_answer(events or []), "mock_fallback"

def check_amd_health() -> bool:
    """Performs a lightweight health check against AMD Developer Cloud."""
    api_url = os.getenv("AMD_DEV_CLOUD_API_URL")
    api_key = os.getenv("AMD_DEV_CLOUD_API_KEY")
    if not api_url or not api_key:
        return False
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": os.getenv("AMD_DEV_CLOUD_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct"),
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        }
        response = httpx.post(api_url, headers=headers, json=payload, timeout=5.0)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"AMD health check failed: {str(e)}")
        return False

def check_fireworks_health() -> bool:
    """Performs a lightweight health check against Fireworks AI."""
    api_key = os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        return False
    try:
        url = "https://api.fireworks.ai/inference/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        }
        response = httpx.post(url, headers=headers, json=payload, timeout=5.0)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Fireworks health check failed: {str(e)}")
        return False

def generate_grounded_answer(question: str, events: list, conversation_history: list = None) -> tuple[str, str]:
    """
    Generates a grounded answer from events using the cascading LLM provider router or a rule-based mock fallback.
    Returns:
        (answer, mode) - where mode is 'amd', 'fireworks_fallback', 'mock', or 'mock_fallback'
    """
    # 1. If no events are retrieved, return the exact fallback string immediately
    if not events:
        return "I don't have a record of that yet", "mock"

    amd_key = os.getenv("AMD_DEV_CLOUD_API_KEY")
    fireworks_key = os.getenv("FIREWORKS_API_KEY")
    provider = os.getenv("LLM_PROVIDER", "amd").lower().strip()

    # If provider is explicitly set to mock, or if both api keys are missing/empty/placeholder, run in mock mode
    if provider == "mock" or (not is_configured(amd_key) and not is_configured(fireworks_key)):
        logger.info("No LLM provider keys set or provider is 'mock'. Running in MOCK mode.")
        return generate_mock_answer(events), "mock"

    # Multi-event: Keep 5 most recent, sort chronologically
    has_more = len(events) > 5
    events_to_use = events[:5]
    events_to_use = sorted(events_to_use, key=lambda e: e.timestamp)

    # Format events list as readable context for the prompt
    formatted_events = []
    for event in events_to_use:
        actor_str = event.actor if event.actor else "someone"
        zone_str = event.zone if event.zone else "an unknown area"
        dt_str = event.timestamp.strftime("%I:%M %p on %B %d, %Y")

        # Classify certainty based on confidence
        if event.confidence >= 0.85:
            certainty = "Certain"
        elif 0.6 <= event.confidence < 0.85:
            certainty = "Likely"
        else:
            certainty = "Unsure"

        formatted_events.append(
            f"- At {dt_str}: {actor_str} {event.action} the {event.object} in/on the {zone_str}. [Certainty: {certainty}]"
        )

    if has_more:
        formatted_events.append("- (Note: There are also a few earlier events matching this query that are not listed here)")

    context = "\n".join(formatted_events)

    system_prompt = (
        "You are EchoMind, a warm, patient, and reassuring visual memory assistant for dementia patients. "
        "Your task is to answer the user's question about their day strictly using the provided event log context.\n\n"
        "Grounding Rules:\n"
        "1. You must answer ONLY from the details explicitly stated in the event records. Never use general or external knowledge.\n"
        "2. If the context does not contain the answer to the question, you must respond with EXACTLY: "
        "\"I don't have a record of that yet\" - do not add any explanation, greetings, or details.\n"
        "3. Keep the tone warm, comforting, plain-language, and reassuring.\n"
        "4. Never produce medical advice, health diagnoses, or treatment recommendations.\n"
        "5. The Certainty tag of each event determines how certain it is. Adapt your response phrasing based on the Certainty:\n"
        "   - If Certainty is 'Certain', state the fact plainly without any hedging (e.g. 'Your glasses were placed on the kitchen shelf...').\n"
        "   - If Certainty is 'Likely', hedge gently using phrases like 'It looks like...' or 'It seems that...'.\n"
        "   - If Certainty is 'Unsure', hedge strongly and suggest checking (e.g. 'I think I saw... but I'm not fully sure — you may want to double check.').\n"
        "6. Do not include raw confidence numbers, 'Certainty', 'Certain', 'Likely', or 'Unsure' tags in your output response. Only use them to guide your phrasing.\n"
        "7. If there are earlier events not listed (indicated by the Note in context), you must append ', and a few earlier events.' to the end of your answer.\n\n"
        f"Event Log Context:\n{context}"
    )

    # Call cascading LLM provider router
    answer, mode = call_llm_provider(question, system_prompt, conversation_history, events)

    if mode in ["amd", "fireworks_fallback"]:
        # Grounding validation
        if answer.lower() == "i don't have a record of that yet":
            return answer, mode

        # Extract key detail words from the events
        key_words = set()
        for event in events_to_use:
            if event.object:
                key_words.add(event.object.lower())
            if event.zone:
                key_words.add(event.zone.lower())
                # Split words to also check parts of zone (e.g. "kitchen" or "shelf")
                for w in event.zone.lower().split():
                    if w not in ["the", "in", "on", "at", "a", "an", "of", "and"]:
                        key_words.add(w)
            if event.action:
                action_clean = event.action.lower().replace("_", " ")
                key_words.add(action_clean)
                for w in action_clean.split():
                    key_words.add(w)

        # Check if any key details are referenced in the answer (case-insensitive substring check)
        answer_lower = answer.lower()
        has_grounding = any(kw in answer_lower for kw in key_words)
        if not has_grounding:
            logger.warning(f"LLM grounding validation failed. LLM returned: '{answer}'. Falling back to mock template.")
            return generate_mock_answer(events), "mock_fallback"

        # If has_more was True, ensure ", and a few earlier events." is appended if not already present
        if has_more:
            clean_ans = answer.strip().rstrip(".").lower()
            if not clean_ans.endswith("and a few earlier events"):
                answer = answer.rstrip('.') + ", and a few earlier events."

        return answer, mode

    return answer, mode

