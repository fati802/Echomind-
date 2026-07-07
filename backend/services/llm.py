import os
import logging
import httpx
from backend.models.event import Event

logger = logging.getLogger(__name__)

def generate_mock_answer(events: list) -> str:
    """Generates a warm, simple, rule-based response directly from the events."""
    if not events:
        return "I don't have a record of that yet"
        
    sentences = []
    for event in events:
        actor_str = f"by {event.actor}" if event.actor else ""
        zone_str = f"in/on the {event.zone}" if event.zone else "somewhere"
        dt_str = event.timestamp.strftime("%I:%M %p on %B %d, %Y")
        
        # Build a comforting sentence matching the action
        if event.action == "placed":
            sentence = f"Your {event.object} was placed {actor_str} {zone_str} at {dt_str}."
        elif event.action == "picked_up":
            sentence = f"Your {event.object} was picked up {actor_str} {zone_str} at {dt_str}."
        elif event.action == "handed_over":
            sentence = f"Your {event.object} was handed over {actor_str} {zone_str} at {dt_str}."
        else:
            sentence = f"Your {event.object} was observed {actor_str} {zone_str} at {dt_str}."
            
        sentences.append(sentence)
        
    return " ".join(sentences)

def generate_grounded_answer(question: str, events: list) -> tuple[str, str]:
    """
    Generates a grounded answer from events using Fireworks AI or a rule-based mock fallback.
    Returns:
        (answer, mode) - where mode is 'live' or 'mock'
    """
    # 1. If no events are retrieved, return the exact fallback string immediately
    if not events:
        return "I don't have a record of that yet", "mock"
        
    api_key = os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        logger.info("FIREWORKS_API_KEY is missing or empty. Running in MOCK mode.")
        return generate_mock_answer(events), "mock"
        
    # Format events list as readable context for the prompt
    formatted_events = []
    for event in events:
        actor_str = event.actor if event.actor else "someone"
        zone_str = event.zone if event.zone else "an unknown area"
        dt_str = event.timestamp.strftime("%I:%M %p on %B %d, %Y")
        formatted_events.append(
            f"- At {dt_str}: {actor_str} {event.action} the {event.object} in/on the {zone_str}."
        )
    context = "\n".join(formatted_events)
    
    system_prompt = (
        "You are EchoMind, a warm, patient, and reassuring visual memory assistant for dementia patients. "
        "Your task is to answer the user's question about their day strictly using the provided event log context.\n\n"
        "Grounding Rules:\n"
        "1. You must answer ONLY from the details explicitly stated in the event records. Never use general or external knowledge.\n"
        "2. If the context does not contain the answer to the question, you must respond with EXACTLY: "
        "\"I don't have a record of that yet\" - do not add any explanation, greetings, or details.\n"
        "3. Keep the tone warm, comforting, plain-language, and reassuring.\n"
        "4. Never produce medical advice, health diagnoses, or treatment recommendations.\n\n"
        f"Event Log Context:\n{context}"
    )
    
    # Call Fireworks AI chat completions
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.0,
        "max_tokens": 150
    }
    
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()
            if not answer:
                return generate_mock_answer(events), "mock"
            return answer, "live"
        else:
            logger.error(f"Fireworks AI API error: {response.status_code} - {response.text}. Falling back to MOCK mode.")
            return generate_mock_answer(events), "mock"
    except httpx.RequestError as e:
        logger.error(f"Network error calling Fireworks AI: {str(e)}. Falling back to MOCK mode.")
        return generate_mock_answer(events), "mock"
