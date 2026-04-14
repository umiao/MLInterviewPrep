"""Company management API routes."""
import json
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session, joinedload

from src.backend.database import get_db
from src.backend.models.behavioral import BehavioralExample
from src.backend.models.company import Company, CompanyDocument, CompanyTopicWeight
from src.backend.models.company_tags import (
    BehavioralExampleCompanyTag,
    NodeCompanyTag,
    ProblemCompanyTag,
)
from src.backend.models.framework import FrameworkNode
from src.backend.models.knowledge_card import CompanyCardOverlay, KnowledgeCard
from src.backend.models.problem import Problem
from src.backend.schemas.company import (
    CompanyCreate,
    CompanyDocumentCreate,
    CompanyDocumentResponse,
    CompanyDocumentUpdate,
    CompanyPrepResponse,
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


# --- Unified Prep Endpoint (T-P0-215) ---


_RELEVANCE_KEYS = ("core", "likely", "stretch")


def _empty_segments() -> dict[str, list]:
    """Return a three-segment dict with empty lists."""
    return {k: [] for k in _RELEVANCE_KEYS}


def _problem_summary(p: Problem) -> dict[str, Any]:
    """Compact problem metadata for list views (no description body)."""
    return {
        "id": p.id,
        "leetcode_id": p.leetcode_id,
        "title": p.title,
        "url": p.url,
        "difficulty": p.difficulty,
        "category": p.category,
        "pattern": p.pattern,
        "is_completed": bool(p.is_completed),
        "comfort_level": p.comfort_level,
    }


def _node_summary(n: FrameworkNode) -> dict[str, Any]:
    """Compact framework node metadata."""
    return {
        "id": n.id,
        "path": n.path,
        "depth": n.depth,
        "title": n.title,
        "status": n.status,
        "progress_pct": n.progress_pct,
        "priority": n.priority,
    }


def _behavioral_story_markdown(ex: BehavioralExample) -> str:
    """Concatenate STAR fields into a markdown-like string."""
    parts: list[str] = []
    for label, val in (
        ("Situation", ex.situation),
        ("Task", ex.task),
        ("Action", ex.action),
        ("Result", ex.result),
    ):
        if val:
            parts.append(f"**{label}**\n\n{val}")
    return "\n\n".join(parts)


def _doc_meta(d: CompanyDocument) -> dict[str, Any]:
    """Company document metadata (no content body)."""
    return {
        "id": d.id,
        "company_id": d.company_id,
        "title": d.title,
        "source_type": d.source_type,
        "doc_kind": d.doc_kind,
        "created_at": d.created_at,
        "updated_at": d.updated_at,
    }


@router.get("/companies/{company_id}/prep", response_model=CompanyPrepResponse)
def get_company_prep(
    company_id: int, db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Unified prep view: company + hub doc + tagged entities + overlays.

    Returns a dict with keys:
        company, hub_doc (or None), documents, problems{core,likely,stretch},
        framework_nodes{core,likely,stretch}, knowledge_cards[],
        behavioral_stories[].

    Content bodies are inlined only for ``hub_doc``; other documents return
    metadata only (drawer fetches full content via existing per-doc endpoint).
    """
    # Q1: company
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Q2: hub_doc (most recent by updated_at, via doc_kind enum)
    hub = (
        db.query(CompanyDocument)
        .filter(
            CompanyDocument.company_id == company_id,
            CompanyDocument.doc_kind == "hub_doc",
        )
        .order_by(CompanyDocument.updated_at.desc())
        .first()
    )
    hub_doc: dict[str, Any] | None = None
    if hub is not None:
        hub_doc = {
            **_doc_meta(hub),
            "content": hub.content,
        }

    # Q3: other documents (metadata only)
    other_docs = (
        db.query(CompanyDocument)
        .filter(
            CompanyDocument.company_id == company_id,
            CompanyDocument.doc_kind != "hub_doc",
        )
        .order_by(CompanyDocument.created_at)
        .all()
    )
    documents = [_doc_meta(d) for d in other_docs]

    # Q4: problem tags joined with problem
    problem_tags = (
        db.query(ProblemCompanyTag)
        .options(joinedload(ProblemCompanyTag.problem))
        .filter(ProblemCompanyTag.company_id == company_id)
        .all()
    )
    problems = _empty_segments()
    for t in problem_tags:
        if t.relevance in problems and t.problem is not None:
            problems[t.relevance].append(_problem_summary(t.problem))

    # Q5: node tags joined with framework node
    node_tags = (
        db.query(NodeCompanyTag)
        .options(joinedload(NodeCompanyTag.node))
        .filter(NodeCompanyTag.company_id == company_id)
        .all()
    )
    framework_nodes = _empty_segments()
    for t in node_tags:
        if t.relevance in framework_nodes and t.node is not None:
            framework_nodes[t.relevance].append(_node_summary(t.node))

    # Q6: behavioral example tags joined with example
    be_tags = (
        db.query(BehavioralExampleCompanyTag)
        .options(joinedload(BehavioralExampleCompanyTag.example))
        .filter(BehavioralExampleCompanyTag.company_id == company_id)
        .all()
    )
    behavioral_stories: list[dict[str, Any]] = []
    for t in be_tags:
        if t.example is None:
            continue
        behavioral_stories.append({
            "example_id": t.example.example_id,
            "id": t.example.id,
            "title": t.example.title,
            "company_attribute": t.company_attribute,
            "relevance": t.relevance,
            "content": _behavioral_story_markdown(t.example),
        })

    # Q7: knowledge cards + overlays for this company (single join query)
    overlay_rows = (
        db.query(KnowledgeCard, CompanyCardOverlay)
        .join(
            CompanyCardOverlay,
            (CompanyCardOverlay.card_id == KnowledgeCard.id)
            & (CompanyCardOverlay.company_id == company_id),
            isouter=True,
        )
        .order_by(KnowledgeCard.slug)
        .all()
    )
    card_map: dict[int, dict[str, Any]] = {}
    for card, overlay in overlay_rows:
        entry = card_map.get(card.id)
        if entry is None:
            entry = {
                "id": card.id,
                "slug": card.slug,
                "title": card.title,
                "canonical_body": card.canonical_body,
                "tags": json.loads(card.tags) if card.tags else [],
                "overlays": [],
            }
            card_map[card.id] = entry
        if overlay is not None:
            entry["overlays"].append({
                "angle": overlay.angle,
                "overlay_body": overlay.overlay_body,
            })
    knowledge_cards = list(card_map.values())

    return {
        "company": _company_to_response(company),
        "hub_doc": hub_doc,
        "documents": documents,
        "problems": problems,
        "framework_nodes": framework_nodes,
        "knowledge_cards": knowledge_cards,
        "behavioral_stories": behavioral_stories,
    }
