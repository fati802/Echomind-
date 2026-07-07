import os
import logging
import httpx
from backend.models.event import Event

logger = logging.getLogger(__name__)

def generate_grounded_answer(question: str, events: list) -> str:
    # 1. If no events are retrieved, return the exact fallback string immediately
    if not events:
        return "I don't have a record of that yet"
        
    api_key = os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        logger.error("FIREWORKS_API_KEY is not set.")
        return "I don't have a record of that yet"
        
    # Format events list as readable context for the prompt
    formatted_events = []
    for event in events:
        actor_str = event.actor if event.actor else "someone"
        zone_str = event.zone if event.zone else "an unknown area"
        # Format date as e.g. "02:15 PM on July 07, 2026"
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
                return "I don't have a record of that yet"
            return answer
        else:
            logger.error(f"Fireworks AI API error: {response.status_code} - {response.text}")
            return "I don't have a record of that yet"
    except httpx.RequestError as e:
        logger.error(f"Network error calling Fireworks AI: {str(e)}")
        return "I don't have a record of that yet"
