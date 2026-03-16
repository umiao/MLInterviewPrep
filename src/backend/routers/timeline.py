"""Interview timeline API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.timeline import InterviewEvent
from src.backend.schemas.timeline import (
    InterviewEventCreate,
    InterviewEventResponse,
    InterviewEventUpdate,
)

router = APIRouter()


@router.get("/timeline/events", response_model=list[InterviewEventResponse])
def list_events(
    status: str | None = Query(default=None),
    company_id: int | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
) -> list[InterviewEvent]:
    """List interview events sorted by scheduled_at ascending.

    Args:
        status: Optional filter by event status.
        company_id: Optional filter by company.
        limit: Optional max number of results.
        db: Database session.

    Returns:
        List of interview events.
    """
    query = db.query(InterviewEvent).order_by(InterviewEvent.scheduled_at.asc())
    if status:
        query = query.filter(InterviewEvent.status == status)
    if company_id is not None:
        query = query.filter(InterviewEvent.company_id == company_id)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


@router.post(
    "/timeline/events", response_model=InterviewEventResponse, status_code=201
)
def create_event(
    event: InterviewEventCreate, db: Session = Depends(get_db)
) -> InterviewEvent:
    """Create a new interview event.

    Args:
        event: Event creation data.
        db: Database session.

    Returns:
        Created interview event.
    """
    db_event = InterviewEvent(
        company_id=event.company_id,
        company_name=event.company_name,
        event_type=event.event_type,
        title=event.title,
        description=event.description,
        scheduled_at=event.scheduled_at,
        duration_minutes=event.duration_minutes,
        location=event.location,
        status=event.status,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put(
    "/timeline/events/{event_id}", response_model=InterviewEventResponse
)
def update_event(
    event_id: int,
    event_update: InterviewEventUpdate,
    db: Session = Depends(get_db),
) -> InterviewEvent:
    """Update an interview event (partial).

    Args:
        event_id: ID of the event to update.
        event_update: Partial update data.
        db: Database session.

    Returns:
        Updated interview event.
    """
    db_event = (
        db.query(InterviewEvent).filter(InterviewEvent.id == event_id).first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)

    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/timeline/events/{event_id}")
def delete_event(
    event_id: int, db: Session = Depends(get_db)
) -> dict:
    """Delete an interview event.

    Args:
        event_id: ID of the event to delete.
        db: Database session.

    Returns:
        Deletion confirmation.
    """
    db_event = (
        db.query(InterviewEvent).filter(InterviewEvent.id == event_id).first()
    )
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(db_event)
    db.commit()
    return {"deleted": True}
