"""Tests for the T-P2-585 BQ-DEPTH-14 narrow probe-drift detector.

Covers the two contract ACs (false-positive: no change -> 0 reports;
true-positive: mutate one risk_statement -> exactly 1 report) plus the narrow-
field rule (an *untracked* STAR field like ``task`` must NOT fire) and the
narrative-threshold / re-baseline-on-probe-regeneration behavior.

The detector's pure core (``detect_drift`` / ``compute_fingerprint`` /
``gather_rows``) is exercised against an in-process SQLite DB built from the real
SQLAlchemy models, so the column names stay in lockstep with the schema.
"""
import importlib
import sys
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

detect = importlib.import_module("detect_probe_drift")

from src.backend.database import Base  # noqa: E402
from src.backend.models.behavioral import (  # noqa: E402
    BehavioralExample,
    BehavioralQuestion,
    QuestionExampleLink,
)

_TS = datetime(2026, 6, 18, 12, 0, 0)


@pytest.fixture()
def db():
    """In-memory SQLite with the behavioral schema; yields a raw connection."""
    engine = create_engine("sqlite://", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, future=True)
    sess = session_factory()

    q = BehavioralQuestion(
        question_id="OWN-1", text="Tell me about ownership.",
        category_id="ownership", category_name="Ownership",
        probe_notes='{"core_signal": "x"}', probe_notes_updated_at=_TS,
    )
    ex = BehavioralExample(
        example_id="EX-01", title="The ranking story",
        situation="S text", task="T text", action="A text", result="R text",
        principle_tags='["ownership", "diagnosis"]',
        risk_statement="Risk: boast-stacking the outcome.",
    )
    sess.add_all([q, ex])
    sess.flush()
    sess.add(QuestionExampleLink(
        question_id=q.id, example_id=ex.id, is_primary=True,
        relevance_note="primary",
    ))
    sess.commit()

    # Hand the detector the live sqlite connection behind the SQLAlchemy engine.
    raw = engine.raw_connection()
    yield raw, sess, ex
    raw.close()
    sess.close()


def _run(raw, baseline, threshold=detect.DEFAULT_NARRATIVE_THRESHOLD):
    rows = detect.gather_rows(raw.driver_connection)
    return detect.detect_drift(rows, baseline, threshold)


def test_first_run_establishes_baseline_no_findings(db):
    """First observation captures a baseline and reports nothing."""
    raw, _sess, _ex = db
    findings, baseline = _run(raw, {})
    assert findings == []
    assert "OWN-1" in baseline
    assert "EX-01" in baseline["OWN-1"]["examples"]


def test_no_change_zero_reports(db):
    """AC false-positive: a second run with no DB change -> 0 findings."""
    raw, _sess, _ex = db
    _f1, baseline = _run(raw, {})
    findings, _b2 = _run(raw, baseline)
    assert findings == []


def test_mutated_risk_statement_one_report(db):
    """AC true-positive: mutate one risk_statement -> exactly 1 finding."""
    raw, sess, ex = db
    _f1, baseline = _run(raw, {})

    ex.risk_statement = "Risk: completely rewritten framing."
    sess.commit()

    findings, _b2 = _run(raw, baseline)
    assert len(findings) == 1
    assert findings[0]["question_id"] == "OWN-1"
    assert findings[0]["example_id"] == "EX-01"
    assert findings[0]["drift_reason"] == "risk_statement"


def test_principle_tags_change_flags(db):
    """principle_tags edit (added tag) is a tracked-field drift."""
    raw, sess, ex = db
    _f1, baseline = _run(raw, {})

    ex.principle_tags = '["ownership", "diagnosis", "new_signal"]'
    sess.commit()

    findings, _b2 = _run(raw, baseline)
    assert len(findings) == 1
    assert findings[0]["drift_reason"] == "principle_tags"
    assert "new_signal" in findings[0]["diff_preview"]


def test_principle_tags_reorder_is_not_drift(db):
    """Reordering the same tag set must NOT fire (sorted comparison)."""
    raw, sess, ex = db
    _f1, baseline = _run(raw, {})

    ex.principle_tags = '["diagnosis", "ownership"]'  # same set, reordered
    sess.commit()

    findings, _b2 = _run(raw, baseline)
    assert findings == []


def test_untracked_star_field_is_not_drift(db):
    """Narrow rule: editing ``task`` (not a tracked field) must NOT fire.

    But the same edit changes the narrative concatenation; a SMALL edit stays
    under the 30% threshold, so the narrative trigger also stays silent.
    """
    raw, sess, ex = db
    _f1, baseline = _run(raw, {})

    ex.task = "T text slightly extended."  # small, sub-threshold change
    sess.commit()

    findings, _b2 = _run(raw, baseline)
    assert findings == []


def test_large_narrative_rewrite_flags(db):
    """A wholesale STAR rewrite trips the narrative-delta trigger."""
    raw, sess, ex = db
    _f1, baseline = _run(raw, {})

    ex.situation = "Entirely different situation paragraph " * 5
    ex.action = "Entirely different action paragraph " * 5
    sess.commit()

    findings, _b2 = _run(raw, baseline)
    reasons = {f["drift_reason"] for f in findings}
    assert "narrative" in reasons


def test_drift_persists_until_probe_regenerated(db):
    """Drift keeps reporting across runs until probe_notes_updated_at changes."""
    raw, sess, ex = db
    _f1, baseline = _run(raw, {})

    ex.risk_statement = "Risk: rewritten."
    sess.commit()

    findings_a, baseline_a = _run(raw, baseline)
    assert len(findings_a) == 1
    # Re-run without regenerating the probe: still flagged (baseline held fixed).
    findings_b, baseline_b = _run(raw, baseline_a)
    assert len(findings_b) == 1


def test_probe_regeneration_clears_drift(db):
    """Bumping probe_notes_updated_at re-baselines and clears the drift."""
    raw, sess, ex = db
    q = sess.query(BehavioralQuestion).filter_by(question_id="OWN-1").one()
    _f1, baseline = _run(raw, {})

    ex.risk_statement = "Risk: rewritten."
    sess.commit()
    findings_a, _ba = _run(raw, baseline)
    assert len(findings_a) == 1

    # Operator regenerates the probe (new timestamp): drift considered resolved.
    q.probe_notes_updated_at = datetime(2026, 6, 19, 9, 0, 0)
    sess.commit()
    findings_b, _bb = _run(raw, baseline)
    assert findings_b == []


def test_narrative_change_ratio_bounds():
    """Sanity: identical -> 0.0, disjoint -> high."""
    assert detect.narrative_change_ratio("abc", "abc") == 0.0
    assert detect.narrative_change_ratio("aaaa", "zzzz") > 0.9
