import re
from datetime import datetime, date, timedelta, time
from typing import Tuple, Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from backend.models.event import Event

def parse_time_reference(question: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Detects time phrases in the question and converts them into a date/time range filter.
    Returns (start_time, end_time).
    """
    question_lower = question.lower()
    today = date.today()
    
    if "yesterday" in question_lower:
        start = datetime.combine(today - timedelta(days=1), time.min)
        end = datetime.combine(today - timedelta(days=1), time.max)
        return start, end
    elif "tomorrow" in question_lower:
        start = datetime.combine(today + timedelta(days=1), time.min)
        end = datetime.combine(today + timedelta(days=1), time.max)
        return start, end
    elif "this morning" in question_lower:
        start = datetime.combine(today, time(5, 0, 0))
        end = datetime.combine(today, time(11, 59, 59, 999999))
        return start, end
    elif "this afternoon" in question_lower:
        start = datetime.combine(today, time(12, 0, 0))
        end = datetime.combine(today, time(14, 59, 59, 999999))
        return start, end
    elif "this evening" in question_lower:
        start = datetime.combine(today, time(15, 0, 0))
        end = datetime.combine(today, time(18, 59, 59, 999999))
        return start, end
    elif "tonight" in question_lower:
        start = datetime.combine(today, time(19, 0, 0))
        # Night spans from 19:00 to 04:59 of next day
        end = datetime.combine(today + timedelta(days=1), time(4, 59, 59, 999999))
        return start, end
    elif "today" in question_lower:
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        return start, end
    elif "last time" in question_lower or "recently" in question_lower:
        return None, None
        
    return None, None

def retrieve_relevant_events(question: str, db: Session, limit: int = 5, conversation_history: list = None):
    # Normalize question
    question_lower = question.lower()
    
    # 1. Detect temporal relevance keywords
    start_time, end_time = parse_time_reference(question_lower)
    
    # 2. Extract query keywords
    cleaned_question = re.sub(r'[^a-zA-Z0-9\s]', '', question_lower)
    cleaned_words = cleaned_question.split()
    
    # Common stopwords to exclude from keyword search
    stopwords = {
        "the", "and", "a", "an", "for", "with", "where", "what", "who", "when", 
        "how", "did", "have", "has", "had", "are", "was", "were", "been", "is", 
        "you", "your", "my", "this", "that", "those", "these", "there", "their",
        "today", "yesterday", "tomorrow", "morning", "afternoon", "evening", "tonight", "recently", "last", "time",
        "before", "after", "then", "next", "first", "previous", "earlier", "here"
    }

    keywords = [word for word in cleaned_words if len(word) > 2 and word not in stopwords]
    
    # Pronoun resolution
    has_pronoun = any(p in cleaned_words for p in ["that", "it", "them"])
    if has_pronoun and conversation_history:
        for turn in reversed(conversation_history):
            turn_q = turn.question if hasattr(turn, "question") else turn.get("question", "")
            turn_q_lower = turn_q.lower()
            cleaned_turn_q = re.sub(r'[^a-zA-Z0-9\s]', '', turn_q_lower)
            turn_words = [w for w in cleaned_turn_q.split() if len(w) > 2]
            turn_keywords = [w for w in turn_words if w not in stopwords]
            if turn_keywords:
                keywords = turn_keywords
                break
                
    # Calculate offset for consecutive "before" / "before that" queries
    offset = 0
    if "before" in cleaned_words:
        offset = 1
        if conversation_history:
            for turn in reversed(conversation_history):
                t_q = turn.question if hasattr(turn, "question") else turn.get("question", "")
                if "before" in re.sub(r'[^a-zA-Z0-9\s]', '', t_q.lower()).split():
                    offset += 1
                else:
                    break

    query = db.query(Event)
    
    # Apply date filter if detected
    if start_time and end_time:
        query = query.filter(Event.timestamp >= start_time, Event.timestamp <= end_time)
        
    # If we have keywords, filter by matching any of them across object, actor, zone, or action
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Event.object.ilike(f"%{kw}%"))
            filters.append(Event.actor.ilike(f"%{kw}%"))
            filters.append(Event.zone.ilike(f"%{kw}%"))
            filters.append(Event.action.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    elif not start_time:
        # If no keywords and no date filter, just return empty list (safe for grounding)
        return []
        
    # Order by timestamp descending (most recent/relevant first), apply offset, and limit
    results = query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
    return results


