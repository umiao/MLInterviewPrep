"""Tests for company-document PUT endpoint golden marker auto-refresh (T-P1-553)."""
import time
from datetime import datetime

import pytest

from src.backend.models.company import Company, CompanyDocument


@pytest.fixture()
def seed_document(db_session):
    """Insert a company + one document for golden-marker tests."""
    company = Company(name="GoldCo")
    db_session.add(company)
    db_session.flush()
    doc = CompanyDocument(
        company_id=company.id,
        title="Prep Hub",
        content="hello",
        doc_kind="hub_doc",
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(company)
    db_session.refresh(doc)
    return company, doc


def _iso_to_dt(raw: str) -> datetime:
    """Parse an ISO-format timestamp string into datetime."""
    return datetime.fromisoformat(raw)


def test_company_doc_golden_false_to_true_sets_golden_at(test_client, seed_document):
    """AC (a): false->true sets golden_at to a recent time."""
    company, doc = seed_document
    before = datetime.utcnow()
    resp = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": True},
    )
    after = datetime.utcnow()
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_golden"] is True
    assert body["golden_at"] is not None
    stamped = _iso_to_dt(body["golden_at"])
    assert before <= stamped <= after


def test_company_doc_golden_true_to_true_does_not_overwrite(
    test_client, seed_document
):
    """AC (b): re-PUT with is_golden=true but no flip does NOT refresh golden_at."""
    company, doc = seed_document
    resp1 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": True},
    )
    assert resp1.status_code == 200
    first_stamp = resp1.json()["golden_at"]

    time.sleep(0.01)
    resp2 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": True},
    )
    assert resp2.status_code == 200
    assert resp2.json()["golden_at"] == first_stamp


def test_company_doc_golden_true_to_false_keeps_golden_at(
    test_client, seed_document
):
    """AC (c): true->false keeps golden_at pinned."""
    company, doc = seed_document
    resp1 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": True},
    )
    assert resp1.status_code == 200
    first_stamp = resp1.json()["golden_at"]

    resp2 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": False},
    )
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["is_golden"] is False
    assert body["golden_at"] == first_stamp


def test_company_doc_golden_remark_refreshes_golden_at(test_client, seed_document):
    """AC (d): false->true after an unmark refreshes golden_at to a later timestamp."""
    company, doc = seed_document
    resp1 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": True},
    )
    assert resp1.status_code == 200
    first_stamp = _iso_to_dt(resp1.json()["golden_at"])

    resp2 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": False},
    )
    assert resp2.status_code == 200

    time.sleep(0.01)
    resp3 = test_client.put(
        f"/api/companies/{company.id}/documents/{doc.id}",
        json={"is_golden": True},
    )
    assert resp3.status_code == 200
    new_stamp = _iso_to_dt(resp3.json()["golden_at"])
    assert new_stamp > first_stamp
