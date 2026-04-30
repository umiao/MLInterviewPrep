"""Tests for GET /company-documents/{doc_id} (id-only resolver, T-P0-671)."""
import pytest

from src.backend.models.company import Company, CompanyDocument


@pytest.fixture()
def seed_doc(db_session):
    """Insert a company + one document for resolver tests."""
    company = Company(name="DrawerCo")
    db_session.add(company)
    db_session.flush()
    doc = CompanyDocument(
        company_id=company.id,
        title="Drawer Doc",
        content="hello drawer",
        source_type="manual",
        doc_kind="prep_note",
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(company)
    db_session.refresh(doc)
    return company, doc


def test_get_company_document_by_id_returns_200_with_full_payload(
    test_client, seed_doc
):
    """200 response contains the full CompanyDocumentResponse payload."""
    company, doc = seed_doc
    resp = test_client.get(f"/api/company-documents/{doc.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == doc.id
    assert body["company_id"] == company.id
    assert body["title"] == "Drawer Doc"
    assert body["content"] == "hello drawer"
    assert body["source_type"] == "manual"
    assert body["doc_kind"] == "prep_note"
    assert body["is_golden"] is False
    assert body["golden_at"] is None


def test_get_company_document_404_for_missing_id(test_client, seed_doc):
    """Unknown doc_id returns 404 with detail message."""
    resp = test_client.get("/api/company-documents/9999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"
