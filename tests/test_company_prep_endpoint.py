"""Tests for T-P0-215: unified GET /api/companies/:id/prep endpoint."""
from __future__ import annotations

import pytest
from sqlalchemy import event

from src.backend.models import (
    BehavioralExample,
    BehavioralExampleCompanyTag,
    Company,
    CompanyDocument,
    FrameworkNode,
    NodeCompanyTag,
    Problem,
    ProblemCompanyTag,
)
from src.backend.models.knowledge_card import CompanyCardOverlay, KnowledgeCard


@pytest.fixture()
def seed_prep_data(db_session):
    """Seed 3 companies with 5 tags each + 1 hub doc + 1 overlay for company A."""
    companies: list[Company] = []
    for name in ("Google", "Meta", "Uber"):
        c = Company(name=name)
        db_session.add(c)
        companies.append(c)
    db_session.flush()

    # Problems
    problems: list[Problem] = []
    for i, title in enumerate(("P1", "P2", "P3"), start=1):
        p = Problem(title=title, difficulty="medium", leetcode_id=1000 + i)
        db_session.add(p)
        problems.append(p)

    # Framework nodes
    nodes: list[FrameworkNode] = []
    for i, path in enumerate(("root.a", "root.b")):
        n = FrameworkNode(path=path, depth=0, title=f"N{i}")
        db_session.add(n)
        nodes.append(n)

    # Behavioral examples
    examples: list[BehavioralExample] = []
    for i in range(2):
        ex = BehavioralExample(
            example_id=f"EX-{i+10}",
            title=f"T{i}",
            situation=f"S{i}",
            task=f"T{i}",
            action=f"A{i}",
            result=f"R{i}",
        )
        db_session.add(ex)
        examples.append(ex)
    db_session.flush()

    google = companies[0]

    # Google: 2 core problems, 1 likely, 1 core node, 1 stretch node,
    # 1 core BQ + 1 hub doc + 1 prep_note doc + 1 card+overlay
    db_session.add_all([
        ProblemCompanyTag(
            problem_id=problems[0].id, company_id=google.id, relevance="core"
        ),
        ProblemCompanyTag(
            problem_id=problems[1].id, company_id=google.id, relevance="core"
        ),
        ProblemCompanyTag(
            problem_id=problems[2].id, company_id=google.id, relevance="likely"
        ),
        NodeCompanyTag(
            node_id=nodes[0].id, company_id=google.id, relevance="core"
        ),
        NodeCompanyTag(
            node_id=nodes[1].id, company_id=google.id, relevance="stretch"
        ),
        BehavioralExampleCompanyTag(
            example_id=examples[0].id,
            company_id=google.id,
            relevance="core",
            company_attribute="Googleyness",
        ),
        CompanyDocument(
            company_id=google.id,
            title="Google Prep Hub",
            content="# Hub content\n\nbody",
            doc_kind="hub_doc",
        ),
        CompanyDocument(
            company_id=google.id,
            title="Side note",
            content="aux",
            doc_kind="prep_note",
        ),
    ])

    card = KnowledgeCard(
        slug="transformer", title="Transformer", canonical_body="core body"
    )
    db_session.add(card)
    db_session.flush()
    db_session.add(
        CompanyCardOverlay(
            card_id=card.id,
            company_id=google.id,
            angle="product",
            overlay_body="google-specific",
        )
    )

    # Meta: 1 problem only (sparse company)
    db_session.add(
        ProblemCompanyTag(
            problem_id=problems[0].id, company_id=companies[1].id, relevance="core"
        )
    )

    # Uber: no tags (empty company)

    db_session.commit()
    return {
        "google": google,
        "meta": companies[1],
        "uber": companies[2],
    }


def test_prep_endpoint_returns_all_segments(
    test_client, db_engine, seed_prep_data
):
    """AC1: endpoint returns populated three-segment response for Google."""
    google_id = seed_prep_data["google"].id
    resp = test_client.get(f"/api/companies/{google_id}/prep")
    assert resp.status_code == 200
    body = resp.json()

    assert body["company"]["name"] == "Google"
    assert body["hub_doc"] is not None
    assert body["hub_doc"]["title"] == "Google Prep Hub"
    assert body["hub_doc"]["content"].startswith("# Hub content")

    # documents excludes hub_doc
    doc_kinds = [d["doc_kind"] for d in body["documents"]]
    assert "hub_doc" not in doc_kinds
    assert "prep_note" in doc_kinds

    assert len(body["problems"]["core"]) == 2
    assert len(body["problems"]["likely"]) == 1
    assert body["problems"]["stretch"] == []

    assert len(body["framework_nodes"]["core"]) == 1
    assert len(body["framework_nodes"]["stretch"]) == 1

    assert len(body["behavioral_stories"]) == 1
    story = body["behavioral_stories"][0]
    assert story["company_attribute"] == "Googleyness"
    assert "Situation" in story["content"]
    assert "Result" in story["content"]

    assert len(body["knowledge_cards"]) == 1
    card = body["knowledge_cards"][0]
    assert card["slug"] == "transformer"
    assert len(card["overlays"]) == 1
    assert card["overlays"][0]["angle"] == "product"


def test_prep_endpoint_empty_company_returns_three_segments(
    test_client, db_engine, seed_prep_data
):
    """AC5+AC6: empty-tag company returns all three-segment keys + 0 stories."""
    uber_id = seed_prep_data["uber"].id
    resp = test_client.get(f"/api/companies/{uber_id}/prep")
    assert resp.status_code == 200
    body = resp.json()

    for key in ("core", "likely", "stretch"):
        assert body["problems"][key] == []
        assert body["framework_nodes"][key] == []

    assert body["hub_doc"] is None
    assert body["documents"] == []
    assert body["behavioral_stories"] == []


def test_prep_endpoint_404_unknown_company(test_client, db_engine):
    """Unknown company returns 404."""
    resp = test_client.get("/api/companies/99999/prep")
    assert resp.status_code == 404


def test_prep_endpoint_n_plus_one_guard(
    test_client, db_engine, seed_prep_data
):
    """AC3: total SQL statements for a single request <= 8."""
    statements: list[str] = []

    @event.listens_for(db_engine, "before_cursor_execute")
    def _count(conn, cursor, statement, params, context, executemany):
        statements.append(statement)

    google_id = seed_prep_data["google"].id
    try:
        resp = test_client.get(f"/api/companies/{google_id}/prep")
        assert resp.status_code == 200
    finally:
        event.remove(db_engine, "before_cursor_execute", _count)

    select_count = sum(
        1 for s in statements if s.strip().lower().startswith("select")
    )
    assert select_count <= 8, (
        f"N+1 guard: expected <= 8 SELECTs, got {select_count}. "
        f"Statements: {statements}"
    )


def test_prep_endpoint_response_shape_validated(
    test_client, db_engine, seed_prep_data
):
    """AC4: response validates against CompanyPrepResponse schema."""
    from src.backend.schemas.company import CompanyPrepResponse

    google_id = seed_prep_data["google"].id
    resp = test_client.get(f"/api/companies/{google_id}/prep")
    assert resp.status_code == 200
    CompanyPrepResponse.model_validate(resp.json())
