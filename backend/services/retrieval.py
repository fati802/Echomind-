import re
from datetime import date, timedelta
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from backend.models.event import Event

def retrieve_relevant_events(question: str, db: Session, limit: int = 5):
    # Normalize question
    question_lower = question.lower()
    
    # 1. Detect temporal relevance keywords
    date_filter = None
    if "today" in question_lower:
        date_filter = date.today()
    elif "yesterday" in question_lower:
        date_filter = date.today() - timedelta(days=1)
        
    # 2. Extract query keywords
    cleaned_question = re.sub(r'[^a-zA-Z0-9\s]', '', question_lower)
    words = [word for word in cleaned_question.split() if len(word) > 2]
    
    # Common stopwords to exclude from keyword search
    stopwords = {
        "the", "and", "a", "an", "for", "with", "where", "what", "who", "when", 
        "how", "did", "have", "has", "had", "are", "was", "were", "been", "is", 
        "you", "your", "my", "this", "that", "those", "these", "there", "their",
        "today", "yesterday"  # Handled separately
    }
    keywords = [word for word in words if word not in stopwords]
    
    query = db.query(Event)
    
    # Apply date filter if detected
    if date_filter:
        query = query.filter(func.date(Event.timestamp) == date_filter)
        
    # If we have keywords, filter by matching any of them across object, actor, zone, or action
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Event.object.ilike(f"%{kw}%"))
            filters.append(Event.actor.ilike(f"%{kw}%"))
            filters.append(Event.zone.ilike(f"%{kw}%"))
            filters.append(Event.action.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    elif not date_filter:
        # If no keywords and no date filter, just return empty or recent events (empty list is safer for grounding)
        return []
        
    # Order by timestamp descending (most recent/relevant first) and limit
    results = query.order_by(Event.timestamp.desc()).limit(limit).all()
    return results
