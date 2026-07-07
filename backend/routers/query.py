from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.query import QueryRequest, QueryResponse
from backend.services.retrieval import retrieve_relevant_events
from backend.services.llm import generate_grounded_answer

router = APIRouter()

@router.post("/api/query", response_model=QueryResponse)
def query_echomind(payload: QueryRequest, db: Session = Depends(get_db)):
    # Basic validation for empty whitespace strings (Pydantic min_length covers empty strings, but let's handle whitespace)
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Question cannot be empty or contain only whitespace.")
        
    # 1. Retrieve matching/relevant events using keyword and temporal matching
    events = retrieve_relevant_events(question, db)
    
    # 2. Call LLM wrapper to generate a warm, patient, strictly grounded answer
    answer = generate_grounded_answer(question, events)
    
    return QueryResponse(
        answer=answer,
        referenced_events=events
    )

@router.post("/api/ask", response_model=QueryResponse)
def ask_echomind(payload: QueryRequest, db: Session = Depends(get_db)):
    """Alias endpoint pointing to the query runner."""
    return query_echomind(payload, db)
