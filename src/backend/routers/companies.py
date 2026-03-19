"""Company management API routes."""
import json
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.company import Company, CompanyDocument, CompanyTopicWeight
from src.backend.models.framework import FrameworkNode
from src.backend.schemas.company import (
    CompanyCreate,
    CompanyDocumentCreate,
    CompanyDocumentResponse,
    CompanyDocumentUpdate,
    CompanyResponse,
    CompanyUpdate,
    TopicWeightCreate,
)

router = APIRouter()


def _company_to_response(c: Company) -> dict:
    """Convert Company ORM to response dict."""
    return {
        "id": c.id,
        "name": c.name,
        "group_tag": c.group_tag,
        "interview_stages": c.interview_stages_list,
        "status": c.status,
        "applied_at": c.applied_at,
        "notes": c.notes,
        "prep_notes": c.prep_notes,
    }


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(
    status: str | None = Query(default=None),
    group_tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict]:
    """List companies with optional filters."""
    query = db.query(Company)
    if status:
        query = query.filter(Company.status == status)
    if group_tag:
        query = query.filter(Company.group_tag == group_tag)
    return [_company_to_response(c) for c in query.all()]


@router.post("/companies", response_model=CompanyResponse, status_code=201)
def create_company(
    company: CompanyCreate, db: Session = Depends(get_db)
) -> dict:
    """Create a new company."""
    existing = db.query(Company).filter(Company.name == company.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Company '{company.name}' already exists",
        )

    db_company = Company(
        name=company.name,
        group_tag=company.group_tag,
        interview_stages=json.dumps(company.interview_stages, ensure_ascii=False),
        status=company.status,
        applied_at=company.applied_at,
        notes=company.notes,
        prep_notes=company.prep_notes,
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return _company_to_response(db_company)


@router.put("/companies/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update a company (partial)."""
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "interview_stages" and value is not None:
            setattr(db_company, field, json.dumps(value, ensure_ascii=False))
        else:
            setattr(db_company, field, value)

    db.commit()
    db.refresh(db_company)
    return _company_to_response(db_company)


@router.delete("/companies/{company_id}")
def delete_company(
    company_id: int, db: Session = Depends(get_db)
) -> dict:
    """Delete a company and cascade-delete its topic weights."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    weight_count = (
        db.query(CompanyTopicWeight)
        .filter(CompanyTopicWeight.company_id == company_id)
        .count()
    )
    db.query(CompanyTopicWeight).filter(
        CompanyTopicWeight.company_id == company_id
    ).delete()
    db.delete(company)
    db.commit()
    return {"deleted": True, "weights_removed": weight_count}


@router.post("/companies/{company_id}/prep-notes/import")
async def import_prep_notes(
    company_id: int,
    file: UploadFile = File(...),
    mode: Literal["append", "replace"] = Form("append"),
    db: Session = Depends(get_db),
) -> dict:
    """Import prep notes from a .md file.

    Args:
        company_id: Target company ID.
        file: Uploaded markdown file.
        mode: 'append' concatenates with separator, 'replace' overwrites.
        db: Database session.

    Returns:
        Updated company response dict.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    content = (await file.read()).decode("utf-8")

    if mode == "replace" or not company.prep_notes:
        company.prep_notes = content
    else:
        company.prep_notes = company.prep_notes + "\n\n---\n\n" + content

    db.commit()
    db.refresh(company)
    return _company_to_response(company)


@router.post("/companies/{company_id}/weights", status_code=200)
def upsert_topic_weights(
    company_id: int,
    weights: list[TopicWeightCreate],
    db: Session = Depends(get_db),
) -> dict:
    """Batch upsert topic weights for a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    inserted = 0
    updated = 0
    for w in weights:
        existing = (
            db.query(CompanyTopicWeight)
            .filter(
                CompanyTopicWeight.company_id == company_id,
                CompanyTopicWeight.framework_node_id == w.framework_node_id,
            )
            .first()
        )
        if existing:
            existing.weight = w.weight
            updated += 1
        else:
            db.add(CompanyTopicWeight(
                company_id=company_id,
                framework_node_id=w.framework_node_id,
                weight=w.weight,
            ))
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": updated}


@router.delete("/companies/{company_id}/weights/{node_id}")
def delete_topic_weight(
    company_id: int, node_id: int, db: Session = Depends(get_db)
) -> dict:
    """Delete a single topic weight for a company."""
    weight = (
        db.query(CompanyTopicWeight)
        .filter(
            CompanyTopicWeight.company_id == company_id,
            CompanyTopicWeight.framework_node_id == node_id,
        )
        .first()
    )
    if not weight:
        raise HTTPException(status_code=404, detail="Topic weight not found")
    db.delete(weight)
    db.commit()
    return {"deleted": True}


@router.get("/companies/{company_id}")
def get_company(company_id: int, db: Session = Depends(get_db)) -> dict:
    """Get company details with topic weights."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    weights = (
        db.query(CompanyTopicWeight, FrameworkNode.title)
        .join(FrameworkNode, CompanyTopicWeight.framework_node_id == FrameworkNode.id)
        .filter(CompanyTopicWeight.company_id == company_id)
        .all()
    )

    resp = _company_to_response(company)
    resp["topic_weights"] = [
        {
            "node_id": w[0].framework_node_id,
            "node_title": w[1],
            "weight": w[0].weight,
        }
        for w in weights
    ]
    return resp


@router.get("/companies/{company_id}/focus")
def get_company_focus(
    company_id: int, db: Session = Depends(get_db)
) -> list[dict]:
    """Get framework nodes weighted by company topic weights, filtered to progress < 80."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    rows = (
        db.query(CompanyTopicWeight, FrameworkNode)
        .join(FrameworkNode, CompanyTopicWeight.framework_node_id == FrameworkNode.id)
        .filter(
            CompanyTopicWeight.company_id == company_id,
            FrameworkNode.progress_pct < 80,
        )
        .order_by(CompanyTopicWeight.weight.desc())
        .all()
    )

    return [
        {
            "node_id": node.id,
            "title": node.title,
            "weight": weight.weight,
            "progress_pct": node.progress_pct,
            "confidence": node.confidence_level,
        }
        for weight, node in rows
    ]


# --- Company Documents ---


@router.get(
    "/companies/{company_id}/documents",
    response_model=list[CompanyDocumentResponse],
)
def list_documents(
    company_id: int,
    db: Session = Depends(get_db),
) -> list[CompanyDocument]:
    """List all child documents for a company.

    Args:
        company_id: Company ID.
        db: Database session.

    Returns:
        List of CompanyDocument objects.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return (
        db.query(CompanyDocument)
        .filter(CompanyDocument.company_id == company_id)
        .order_by(CompanyDocument.created_at)
        .all()
    )


@router.post(
    "/companies/{company_id}/documents",
    response_model=CompanyDocumentResponse,
    status_code=201,
)
def create_document(
    company_id: int,
    body: CompanyDocumentCreate,
    db: Session = Depends(get_db),
) -> CompanyDocument:
    """Create a child document for a company.

    Args:
        company_id: Company ID.
        body: Document creation data.
        db: Database session.

    Returns:
        Created CompanyDocument object.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    doc = CompanyDocument(
        company_id=company_id,
        title=body.title,
        content=body.content,
        source_type=body.source_type,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get(
    "/companies/{company_id}/documents/{doc_id}",
    response_model=CompanyDocumentResponse,
)
def get_document(
    company_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
) -> CompanyDocument:
    """Get a single company document.

    Args:
        company_id: Company ID.
        doc_id: Document ID.
        db: Database session.

    Returns:
        CompanyDocument object.
    """
    doc = (
        db.query(CompanyDocument)
        .filter(
            CompanyDocument.id == doc_id,
            CompanyDocument.company_id == company_id,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put(
    "/companies/{company_id}/documents/{doc_id}",
    response_model=CompanyDocumentResponse,
)
def update_document(
    company_id: int,
    doc_id: int,
    body: CompanyDocumentUpdate,
    db: Session = Depends(get_db),
) -> CompanyDocument:
    """Update a company document (title and/or content).

    Args:
        company_id: Company ID.
        doc_id: Document ID.
        body: Update data.
        db: Database session.

    Returns:
        Updated CompanyDocument object.
    """
    doc = (
        db.query(CompanyDocument)
        .filter(
            CompanyDocument.id == doc_id,
            CompanyDocument.company_id == company_id,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/companies/{company_id}/documents/{doc_id}", status_code=204)
def delete_document(
    company_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a company document.

    Args:
        company_id: Company ID.
        doc_id: Document ID.
        db: Database session.
    """
    doc = (
        db.query(CompanyDocument)
        .filter(
            CompanyDocument.id == doc_id,
            CompanyDocument.company_id == company_id,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
