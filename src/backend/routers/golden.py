"""Golden Collection aggregator API.

Returns the union of items marked `is_golden=True` across the three
content tables (framework_nodes, behavioral_examples, company_documents),
normalized into a single response shape so the frontend can render them
as a unified curated collection. Items are sorted by `golden_at DESC`,
with NULLs (legacy rows that were promoted before the field existed)
sorted to the bottom.

The `url_path` per item is computed here so the frontend stays a thin
renderer; rules:
- framework_node whose `path` starts with `ml-fundamentals/` and has 3
  `/`-segments -> `/ml-fundamentals?cat=<cat>&slug=<slug>` (matches the
  MLFundamentals page param contract).
- any other framework_node -> `/framework/<id>` (the Framework page reads
  `:nodeId` from useParams and expands to the matching node).
- behavioral_example -> `/behavioral` (the BehavioralQuestions page does
  not currently URL-drive its drawer; deep-linking lands the user on the
  page where they can find the example by title).
- company_document -> `/companies/<company_id>/prep?tab=docs&doc=<doc_id>`
  (matches PrepNotesPage's `parsePrepParams` contract).

The preview is the first 200 chars of the most descriptive text field
for each type (description / situation / content), with newlines
collapsed to spaces so the card renders cleanly.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.database import get_db
from src.backend.models.behavioral import BehavioralExample
from src.backend.models.company import CompanyDocument
from src.backend.models.framework import FrameworkNode

router = APIRouter()

PREVIEW_LEN = 200


def _preview(text: str | None) -> str:
    """Collapse newlines and truncate to PREVIEW_LEN chars."""
    if not text:
        return ""
    flat = " ".join(text.split())
    return flat[:PREVIEW_LEN]


def _framework_url(node: FrameworkNode) -> str:
    """Compute the deep-link URL for a framework node.

    ML Fundamentals leaves use the `?cat=&slug=` contract; everything
    else falls back to the generic `/framework/<id>` route.
    """
    parts = (node.path or "").split("/")
    if len(parts) == 3 and parts[0] == "ml-fundamentals":
        return f"/ml-fundamentals?cat={parts[1]}&slug={parts[2]}"
    return f"/framework/{node.id}"


def _behavioral_url(_ex: BehavioralExample) -> str:
    """Deep-link target for a behavioral example.

    The BehavioralQuestions page does not currently expose a URL-driven
    drawer; landing on `/behavioral` is the deepest stable target.
    """
    return "/behavioral"


def _company_doc_url(doc: CompanyDocument) -> str:
    """Deep-link to a company document via PrepNotesPage tab+doc params."""
    return f"/companies/{doc.company_id}/prep?tab=docs&doc={doc.id}"


def _serialize_framework(node: FrameworkNode) -> dict[str, Any]:
    """Normalize a framework_node row into the unified golden item shape."""
    return {
        "id": node.id,
        "item_type": "framework_node",
        "title": node.title,
        "preview": _preview(node.description),
        "golden_at": node.golden_at,
        "url_path": _framework_url(node),
    }


def _serialize_behavioral(ex: BehavioralExample) -> dict[str, Any]:
    """Normalize a behavioral_example row into the unified golden item shape."""
    return {
        "id": ex.id,
        "item_type": "behavioral_example",
        "title": ex.title,
        "preview": _preview(ex.situation),
        "golden_at": ex.golden_at,
        "url_path": _behavioral_url(ex),
    }


def _serialize_company_doc(doc: CompanyDocument) -> dict[str, Any]:
    """Normalize a company_document row into the unified golden item shape."""
    return {
        "id": doc.id,
        "item_type": "company_document",
        "title": doc.title,
        "preview": _preview(doc.content),
        "golden_at": doc.golden_at,
        "url_path": _company_doc_url(doc),
    }


def _sorted_desc(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort items by golden_at DESC, NULLs last."""
    has_ts = [i for i in items if i["golden_at"] is not None]
    no_ts = [i for i in items if i["golden_at"] is None]
    has_ts.sort(key=lambda i: i["golden_at"], reverse=True)
    return has_ts + no_ts


@router.get("/golden")
def list_golden(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return the unified list of items marked `is_golden=True`.

    Unions across framework_nodes, behavioral_examples, and
    company_documents. Each item carries `item_type` so the frontend can
    filter into the per-type tabs without an extra request, and a
    pre-computed `url_path` for one-click deep-linking back to the
    origin page.
    """
    framework_rows = (
        db.query(FrameworkNode).filter(FrameworkNode.is_golden.is_(True)).all()
    )
    behavioral_rows = (
        db.query(BehavioralExample)
        .filter(BehavioralExample.is_golden.is_(True))
        .all()
    )
    doc_rows = (
        db.query(CompanyDocument)
        .filter(CompanyDocument.is_golden.is_(True))
        .all()
    )

    items: list[dict[str, Any]] = []
    items.extend(_serialize_framework(n) for n in framework_rows)
    items.extend(_serialize_behavioral(e) for e in behavioral_rows)
    items.extend(_serialize_company_doc(d) for d in doc_rows)

    return _sorted_desc(items)
