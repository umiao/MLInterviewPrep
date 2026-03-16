"""Company service: shared business logic for company operations."""
import logging

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.models.company import Company

logger = logging.getLogger(__name__)


def get_or_create_company(name: str, db: Session) -> Company:
    """Get an existing company by name (case-insensitive) or create a new one.

    Handles race conditions where two concurrent requests try to create
    the same company simultaneously by catching IntegrityError and retrying.

    Args:
        name: Company name to look up or create.
        db: SQLAlchemy database session.

    Returns:
        Existing or newly created Company instance.
    """
    # Try case-insensitive lookup first
    existing = (
        db.query(Company)
        .filter(func.lower(Company.name) == name.lower())
        .first()
    )
    if existing:
        return existing

    # Create new company
    new_company = Company(name=name)
    db.add(new_company)
    try:
        db.flush()
        return new_company
    except IntegrityError:
        db.rollback()
        # Race condition: another request created it first, retry lookup
        existing = (
            db.query(Company)
            .filter(func.lower(Company.name) == name.lower())
            .first()
        )
        if existing:
            return existing
        # If still not found, re-raise (unexpected)
        raise
