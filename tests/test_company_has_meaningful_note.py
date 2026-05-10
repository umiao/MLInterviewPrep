"""[T-P1-796 / KG-INT A1] Tests for has_meaningful_note composite rule.

Six parametrized cases (one per surface): each adds a row clearing its
threshold -> assert True; remove it -> assert False. Plus targeted tests
for the placeholder-shape filter and the SQL view parity check.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

from src.backend.models.behavioral import BehavioralExample
from src.backend.models.company import Company, CompanyDocument
from src.backend.models.company_tags import (
    BehavioralExampleCompanyTag,
    NodeCompanyTag,
    ProblemCompanyTag,
)
from src.backend.models.framework import FrameworkNode
from src.backend.models.problem import Problem
from src.backend.services.meaningful_note import (
    RED_DOT_CUTOFFS,
    compute_meaningful_note_map,
    has_meaningful_note,
    is_placeholder,
)

# ---------------------------------------------------------------------------
# is_placeholder unit tests (heuristic parity with EDA script)
# ---------------------------------------------------------------------------


class TestIsPlaceholder:
    """Mirror scripts/_eda_red_dot_threshold_2026-05-10.py heuristic."""

    @pytest.mark.parametrize(
        "value",
        [
            None,
            "",
            "   ",
            "abc",  # <5 chars
            "TBD",  # short + pattern
            "TODO finish later",  # short + pattern
            "Placeholder.",  # short + pattern
            "[ ] item not done",  # short + pattern
        ],
    )
    def test_placeholder_shapes(self, value):
        assert is_placeholder(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "Real prep notes for Google: focus on system design and DP.",
            # Long body containing a stray "TODO" still counts as real.
            "x" * 90 + " todo " + "y" * 30,
        ],
    )
    def test_real_shapes(self, value):
        assert is_placeholder(value) is False


# ---------------------------------------------------------------------------
# Per-surface compute_meaningful_note_map tests (6 surfaces)
# ---------------------------------------------------------------------------


def _make_company(db_session, name: str = "TestCo", status: str = "applied") -> Company:
    """Helper: insert a Company with empty notes / prep_notes."""
    c = Company(name=name, status=status, notes=None, prep_notes=None)
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


def _make_problem(db_session) -> Problem:
    p = Problem(
        title="Test Problem", difficulty="medium", pattern="hash_map",
        tags="[]", company_tags="[]", source="test",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


def _make_node(db_session) -> FrameworkNode:
    n = FrameworkNode(
        path="test", depth=0, title="Test", importance=1.0,
        priority="P1", estimated_hours=1,
    )
    db_session.add(n)
    db_session.commit()
    db_session.refresh(n)
    return n


def _make_example(db_session) -> BehavioralExample:
    ex = BehavioralExample(
        example_id="EX-1", title="Test Example",
        situation="s", task="t", action="a", result="r",
    )
    db_session.add(ex)
    db_session.commit()
    db_session.refresh(ex)
    return ex


class TestComputeMeaningfulNoteMapPerSurface:
    """For each of the 6 surfaces: add row clearing cutoff -> True; remove -> False."""

    def test_baseline_no_signal_is_false(self, db_session):
        c = _make_company(db_session, name="EmptyCo")
        m = compute_meaningful_note_map(db_session)
        assert m[c.id] is False

    def test_companies_prep_notes(self, db_session):
        c = _make_company(db_session, name="PrepNotesCo")
        # Cutoff 50: 60-char real string clears.
        c.prep_notes = "Detailed prep notes covering OOD, system design, DP."
        assert len(c.prep_notes) >= RED_DOT_CUTOFFS["companies.prep_notes"]
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is True

        # Remove -> False.
        c.prep_notes = None
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False

    def test_companies_notes(self, db_session):
        c = _make_company(db_session, name="NotesCo")
        c.notes = "Recruiter intro: 5 stages, focus on DP and system design eval."
        assert len(c.notes) >= RED_DOT_CUTOFFS["companies.notes"]
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is True

        c.notes = None
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False

    def test_company_documents_content(self, db_session):
        c = _make_company(db_session, name="DocsCo")
        # Cutoff 100: build a 120-char real string.
        body = (
            "Detailed company prep document discussing system design "
            "fundamentals, DP, and OOD interview style for this org."
        )
        assert len(body) >= RED_DOT_CUTOFFS["company_documents.content"]
        doc = CompanyDocument(
            company_id=c.id, title="Prep", content=body, source_type="manual",
        )
        db_session.add(doc)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is True

        db_session.delete(doc)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False

    def test_problem_company_tags_notes(self, db_session):
        c = _make_company(db_session, name="ProblemTagCo")
        p = _make_problem(db_session)
        # Cutoff 20: 25-char real string.
        tag = ProblemCompanyTag(
            problem_id=p.id, company_id=c.id, relevance="core", source="manual",
            notes="Asked in screen 2024-Q4.",
        )
        assert len(tag.notes) >= RED_DOT_CUTOFFS["problem_company_tags.notes"]
        db_session.add(tag)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is True

        db_session.delete(tag)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False

    def test_node_company_tags_notes(self, db_session):
        c = _make_company(db_session, name="NodeTagCo")
        n = _make_node(db_session)
        tag = NodeCompanyTag(
            node_id=n.id, company_id=c.id, relevance="core", source="manual",
            notes="Recruiter said this pillar is core.",
        )
        assert len(tag.notes) >= RED_DOT_CUTOFFS["node_company_tags.notes"]
        db_session.add(tag)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is True

        db_session.delete(tag)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False

    def test_behavioral_example_company_tags_notes(self, db_session):
        c = _make_company(db_session, name="BeTagCo")
        ex = _make_example(db_session)
        tag = BehavioralExampleCompanyTag(
            example_id=ex.id, company_id=c.id, relevance="core", source="manual",
            notes="Maps to 'Move Fast' attribute.",
        )
        cutoff = RED_DOT_CUTOFFS["behavioral_example_company_tags.notes"]
        assert len(tag.notes) >= cutoff
        db_session.add(tag)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is True

        db_session.delete(tag)
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False


class TestPlaceholderFilterCounts:
    """A short placeholder-shaped string must NOT trigger meaningful=True
    even if it would clear the cutoff by length."""

    def test_short_tbd_blocks(self, db_session):
        c = _make_company(db_session, name="TBDCo")
        # 60 chars but contains 'TBD' AND len < 80 -> placeholder.
        c.prep_notes = "TBD: write prep notes here later (placeholder for sprint)."
        assert len(c.prep_notes) >= RED_DOT_CUTOFFS["companies.prep_notes"]
        assert is_placeholder(c.prep_notes) is True
        db_session.commit()
        assert compute_meaningful_note_map(db_session)[c.id] is False


class TestHasMeaningfulNoteSingle:
    """has_meaningful_note(db, id) is the single-company convenience wrapper."""

    def test_single_company_true(self, db_session):
        c = _make_company(db_session, name="SingleCo")
        c.prep_notes = "Detailed prep notes covering OOD, system design, DP."
        db_session.commit()
        assert has_meaningful_note(db_session, c.id) is True

    def test_single_company_unknown_id(self, db_session):
        # Non-existent ID returns False (not KeyError).
        assert has_meaningful_note(db_session, 999_999) is False


# ---------------------------------------------------------------------------
# API surface: GET /companies returns has_meaningful_note
# ---------------------------------------------------------------------------


class TestListCompaniesApi:
    """End-to-end: GET /companies includes has_meaningful_note for each row."""

    def test_list_includes_flag(self, test_client):
        # Empty -> false.
        empty = test_client.post("/api/companies", json={"name": "EmptyApiCo"}).json()
        # Has meaningful prep_notes -> true.
        with_notes = test_client.post(
            "/api/companies",
            json={
                "name": "WithNotesApiCo",
                "prep_notes": (
                    "Detailed prep notes covering OOD, system design, DP."
                ),
            },
        ).json()

        resp = test_client.get("/api/companies")
        assert resp.status_code == 200
        rows = {c["name"]: c for c in resp.json()}
        assert rows["EmptyApiCo"]["has_meaningful_note"] is False
        assert rows["WithNotesApiCo"]["has_meaningful_note"] is True

        # Returned schema also propagates to GET /companies/{id}.
        single = test_client.get(f"/api/companies/{with_notes['id']}").json()
        assert single["has_meaningful_note"] is True
        empty_single = test_client.get(f"/api/companies/{empty['id']}").json()
        assert empty_single["has_meaningful_note"] is False


# ---------------------------------------------------------------------------
# SQL view parity: company_meaningful_note_v matches the Python rule
# ---------------------------------------------------------------------------


class TestSqlViewParity:
    """The view must agree with compute_meaningful_note_map row-by-row."""

    def test_view_matches_python(self, db_session):
        # Seed three companies covering the main code paths.
        empty = _make_company(db_session, name="ViewEmpty")
        with_prep = _make_company(db_session, name="ViewWithPrep")
        with_prep.prep_notes = (
            "Detailed prep notes covering OOD, system design, DP."
        )
        placeholder = _make_company(db_session, name="ViewPlaceholder")
        placeholder.prep_notes = "TBD: fill me in later."
        db_session.commit()

        py_map = compute_meaningful_note_map(db_session)
        view_rows = db_session.execute(
            text(
                "SELECT company_id, has_meaningful_note "
                "FROM company_meaningful_note_v"
            )
        ).fetchall()
        view_map = {int(r[0]): bool(r[1]) for r in view_rows}

        assert view_map[empty.id] == py_map[empty.id] is False
        assert view_map[with_prep.id] == py_map[with_prep.id] is True
        assert view_map[placeholder.id] == py_map[placeholder.id] is False
