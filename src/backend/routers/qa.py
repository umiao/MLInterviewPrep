"""Q&A session API routes."""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.problem import QASession
from src.backend.services.llm_service import LLMService

router = APIRouter()


@router.post("/qa/chat")
def qa_chat(body: dict, db: Session = Depends(get_db)) -> dict:
    """Multi-turn Q&A conversation.

    Body: {session_id, problem_id, topic, message}
    """
    session_id = body.get("session_id")
    problem_id = body.get("problem_id")
    topic = body.get("topic", "general")
    message = body.get("message", "")

    if not message:
        raise HTTPException(status_code=422, detail="message is required")

    now = datetime.utcnow()
    timestamp = now.isoformat()

    if session_id is not None:
        qa_session = db.query(QASession).filter(QASession.id == session_id).first()
        if not qa_session:
            raise HTTPException(status_code=404, detail="Session not found")
        messages = json.loads(qa_session.messages)
    else:
        qa_session = QASession(
            problem_id=problem_id,
            topic=topic,
            messages="[]",
            created_at=now,
        )
        db.add(qa_session)
        db.flush()
        messages = []

    # Append user message
    messages.append({"role": "user", "content": message, "timestamp": timestamp})

    # Build LLM conversation (strip timestamps for API)
    llm_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    system_prompt = (
        "You are an expert MLE interview coach. "
        "Be concise and direct. Push toward optimal solutions."
    )

    llm = LLMService()
    reply = llm.chat(
        system_prompt=system_prompt,
        messages=llm_messages,
    )

    # Handle error response
    reply_text = json.dumps(reply, ensure_ascii=False) if isinstance(reply, dict) else reply

    # Append assistant message
    messages.append({
        "role": "assistant",
        "content": reply_text,
        "timestamp": datetime.utcnow().isoformat(),
    })

    qa_session.messages = json.dumps(messages, ensure_ascii=False)
    db.commit()
    db.refresh(qa_session)

    return {
        "session_id": qa_session.id,
        "reply": reply_text,
        "messages": messages,
    }


@router.post("/qa/{session_id}/summarize")
def summarize_session(
    session_id: int, db: Session = Depends(get_db)
) -> dict:
    """Summarize a QA session using LLM."""
    qa_session = db.query(QASession).filter(QASession.id == session_id).first()
    if not qa_session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = json.loads(qa_session.messages)
    conversation_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages
    )

    llm = LLMService()
    summary = llm.chat(
        system_prompt=(
            "Summarize this interview prep Q&A session in 2-3 bullet points. "
            "Focus on key insights and areas for improvement."
        ),
        messages=[{"role": "user", "content": conversation_text}],
    )

    summary_text = json.dumps(summary, ensure_ascii=False) if isinstance(summary, dict) else summary

    qa_session.summary = summary_text
    db.commit()

    return {"session_id": session_id, "summary": summary_text}


@router.get("/qa/sessions")
def list_sessions(
    problem_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List QA sessions (without full messages)."""
    query = db.query(QASession)
    if problem_id is not None:
        query = query.filter(QASession.problem_id == problem_id)

    sessions = query.order_by(QASession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "problem_id": s.problem_id,
            "topic": s.topic,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "summary": s.summary,
        }
        for s in sessions
    ]
