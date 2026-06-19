"""T-P2-585 BQ-DEPTH-14 Phase E: narrow probe-drift detector.

Read-only watchdog that flags ``behavioral_questions.probe_notes`` rows whose
underlying story has drifted since the probe was written -- so the human knows
*which* probe panels are stale and need a refresh pass.

NARROW BY DESIGN (per user direction). Monitoring arbitrary STAR-field edits
produces noise the user learns to ignore, so the detector fires ONLY when one of
these changes on a *linked* example since ``probe_notes_updated_at``:

  * ``behavioral_examples.principle_tags``  (the leadership-principle signal set)
  * ``behavioral_examples.risk_statement``  (the narration-guard / risk framing)
  * ``behavioral_examples.result``          (the outcome)
  * Narrative rewrite: SHA of ``situation+task+action+result`` changed AND the
    text delta exceeds ``--narrative-threshold`` (default 30%).

"Since ``probe_notes_updated_at``" is implemented with a baseline snapshot
(``data/probe_drift_baseline.json``, runtime state, gitignored). The baseline is
(re)captured for a question only when its ``probe_notes_updated_at`` changes
(i.e. the probe was regenerated) or on first observation; otherwise the stored
snapshot is held fixed so a real drift keeps being reported on every run until
someone refreshes the probe. Field edits never silently re-baseline.

Contract (T-P2-585 AC):
  * Read-only DB access (``mode=ro`` URI) -- never writes the DB.
  * Silent on no work -- no report file, no stdout when nothing drifted.
  * False-positive: run with no example changes -> 0 reports.
  * True-positive: mutate one linked ``risk_statement`` -> exactly 1 report.

Usage::

    PYTHONUTF8=1 /c/Anaconda/python.exe scripts/detect_probe_drift.py
    PYTHONUTF8=1 /c/Anaconda/python.exe scripts/detect_probe_drift.py --strict   # exit 1 if drift
    PYTHONUTF8=1 /c/Anaconda/python.exe scripts/detect_probe_drift.py --verbose  # narrate no-op runs

Cron note (optional, NOT a hook): a ``session_context.py`` reminder may suggest a
periodic run; this script never installs anything itself.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mle_prep.db"
BASELINE_PATH = ROOT / "data" / "probe_drift_baseline.json"
DOCS = ROOT / "docs"

# The four narrow drift-relevant fields. Order fixed for stable reporting.
TRACKED_FIELDS = ("principle_tags", "risk_statement", "result", "narrative")
DEFAULT_NARRATIVE_THRESHOLD = 0.30


def _norm_tags(raw: str | None) -> list[str]:
    """Parse a principle_tags JSON array into a sorted list of strings.

    Sorted so a pure reordering of the same tag set is NOT flagged as drift
    (order carries no semantic meaning for the signal-set comparison). Falls
    back to a single-element list of the raw string if JSON parsing fails.
    """
    if not raw:
        return []
    try:
        val = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [raw]
    if isinstance(val, list):
        return sorted(str(x) for x in val)
    return [str(val)]


def _narrative_text(ex: sqlite3.Row | dict) -> str:
    """Concatenate the STAR narrative (situation+task+action+result).

    This is the text whose rewrite the narrative-hash trigger watches.
    """
    parts = [ex["situation"], ex["task"], ex["action"], ex["result"]]
    return "\n".join((p or "") for p in parts)


def compute_fingerprint(ex: sqlite3.Row | dict) -> dict:
    """Reduce one example row to its drift-relevant fingerprint.

    Returns the raw comparable values (not hashes) so the narrative delta ratio
    can be computed against a prior text; principle_tags is normalized to a
    sorted list and risk_statement/result are kept as exact strings.
    """
    return {
        "principle_tags": _norm_tags(ex["principle_tags"]),
        "risk_statement": ex["risk_statement"] or "",
        "result": ex["result"] or "",
        "narrative": _narrative_text(ex),
    }


def narrative_change_ratio(old: str, new: str) -> float:
    """Fraction of the narrative that changed: ``1 - SequenceMatcher.ratio``.

    0.0 == identical, 1.0 == completely different. Compared against the
    ``--narrative-threshold`` so only substantive rewrites fire.
    """
    if old == new:
        return 0.0
    return 1.0 - SequenceMatcher(None, old, new).ratio()


def _example_reasons(base_fp: dict, cur_fp: dict, threshold: float) -> list[dict]:
    """Compare a baseline vs current fingerprint; return per-field drift reasons.

    Each reason is ``{field, detail}``. ``detail`` is a short human preview used
    verbatim in the report's ``diff_preview`` column.
    """
    reasons: list[dict] = []

    if base_fp["principle_tags"] != cur_fp["principle_tags"]:
        old_set, new_set = set(base_fp["principle_tags"]), set(cur_fp["principle_tags"])
        added = sorted(new_set - old_set)
        removed = sorted(old_set - new_set)
        bits = []
        if added:
            bits.append(f"+{added}")
        if removed:
            bits.append(f"-{removed}")
        reasons.append({"field": "principle_tags", "detail": " ".join(bits) or "reordered"})

    if base_fp["risk_statement"] != cur_fp["risk_statement"]:
        reasons.append({
            "field": "risk_statement",
            "detail": _preview_pair(base_fp["risk_statement"], cur_fp["risk_statement"]),
        })

    if base_fp["result"] != cur_fp["result"]:
        reasons.append({
            "field": "result",
            "detail": _preview_pair(base_fp["result"], cur_fp["result"]),
        })

    ratio = narrative_change_ratio(base_fp["narrative"], cur_fp["narrative"])
    if ratio > threshold:
        reasons.append({
            "field": "narrative",
            "detail": f"narrative rewrite {ratio:.0%} (> {threshold:.0%} threshold)",
        })

    return reasons


def _preview_pair(old: str, new: str, width: int = 70) -> str:
    """One-line before/after preview for a changed text field."""
    def _trim(s: str) -> str:
        s = " ".join((s or "").split())
        return s[:width] + ("..." if len(s) > width else "")
    return f"was: '{_trim(old)}' -> now: '{_trim(new)}'"


def detect_drift(rows: list[dict], baseline: dict, threshold: float) -> tuple[list[dict], dict]:
    """Core comparison. Returns ``(findings, new_baseline)``.

    ``rows`` is the gathered DB state: one dict per question with keys
    ``question_id``, ``probe_notes_updated_at`` and ``examples`` (a mapping of
    ``example_id -> fingerprint``).

    Baseline policy:
      * question unseen, or its ``probe_notes_updated_at`` changed -> capture a
        fresh snapshot, emit NO finding (the probe is in sync with the story).
      * otherwise -> hold the stored snapshot fixed and compare; any drift is
        reported. Newly-linked examples are merged into the carried snapshot
        silently (a brand-new link is not itself a narrow dry-field drift).
    """
    findings: list[dict] = []
    new_baseline: dict = {}

    for row in rows:
        qid = row["question_id"]
        cur_ts = row["probe_notes_updated_at"]
        cur_examples = row["examples"]
        base_q = baseline.get(qid)

        if base_q is None or base_q.get("probe_notes_updated_at") != cur_ts:
            # First sight or probe regenerated -> (re)baseline, no finding.
            new_baseline[qid] = {
                "probe_notes_updated_at": cur_ts,
                "examples": cur_examples,
            }
            continue

        # Same probe generation: hold baseline fixed, compare each example.
        base_examples = dict(base_q.get("examples", {}))
        for ex_id, cur_fp in cur_examples.items():
            base_fp = base_examples.get(ex_id)
            if base_fp is None:
                # Newly-linked story after the probe was written: track it going
                # forward (merge in) but do not flag -- narrow-field rule.
                base_examples[ex_id] = cur_fp
                continue
            reasons = _example_reasons(base_fp, cur_fp, threshold)
            for r in reasons:
                findings.append({
                    "question_id": qid,
                    "example_id": ex_id,
                    "drift_reason": r["field"],
                    "diff_preview": r["detail"],
                })

        new_baseline[qid] = {
            "probe_notes_updated_at": cur_ts,
            "examples": base_examples,  # held fixed (+ merged new links)
        }

    return findings, new_baseline


def gather_rows(conn: sqlite3.Connection) -> list[dict]:
    """Read every question carrying probe_notes, with its linked examples.

    Only questions with both ``probe_notes`` and ``probe_notes_updated_at`` set
    are in scope (an un-probed question can't have stale probe_notes).
    """
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q_rows = cur.execute(
        """
        SELECT id, question_id, probe_notes_updated_at
        FROM behavioral_questions
        WHERE probe_notes IS NOT NULL AND probe_notes_updated_at IS NOT NULL
        ORDER BY question_id
        """
    ).fetchall()

    out: list[dict] = []
    for q in q_rows:
        ex_rows = cur.execute(
            """
            SELECT e.example_id, e.situation, e.task, e.action, e.result,
                   e.principle_tags, e.risk_statement
            FROM question_example_links l
            JOIN behavioral_examples e ON e.id = l.example_id
            WHERE l.question_id = ?
            ORDER BY e.example_id
            """,
            (q["id"],),
        ).fetchall()
        examples = {ex["example_id"]: compute_fingerprint(ex) for ex in ex_rows}
        out.append({
            "question_id": q["question_id"],
            "probe_notes_updated_at": q["probe_notes_updated_at"],
            "examples": examples,
        })
    return out


def load_baseline(path: Path) -> dict:
    """Load the baseline snapshot, or an empty dict on first run / corruption."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_baseline(path: Path, data: dict) -> None:
    """Persist the baseline snapshot (runtime state under gitignored data/)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def render_report(findings: list[dict], date_str: str) -> str:
    """Render the drift report markdown for a non-empty finding set."""
    lines = [
        f"# BQ probe-drift report -- {date_str}",
        "",
        f"{len(findings)} drift signal(s) across "
        f"{len({f['question_id'] for f in findings})} question(s). Each row means a "
        "linked story's narrow drift-field changed since the probe was last "
        "written -- regenerate the probe_notes for that question to clear it.",
        "",
        "| question_id | linked_example_id | drift_reason | diff_preview |",
        "|-------------|-------------------|--------------|--------------|",
    ]
    for f in sorted(findings, key=lambda x: (x["question_id"], x["example_id"], x["drift_reason"])):
        preview = f["diff_preview"].replace("|", "\\|")
        lines.append(
            f"| {f['question_id']} | {f['example_id']} | {f['drift_reason']} | {preview} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    """CLI entry point. Returns 0, or 1 under ``--strict`` when drift is found."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--narrative-threshold", type=float, default=DEFAULT_NARRATIVE_THRESHOLD,
        help="min fraction (0-1) of narrative change to flag (default 0.30)",
    )
    ap.add_argument(
        "--strict", action="store_true",
        help="exit 1 if any drift was found (for cron/CI)",
    )
    ap.add_argument(
        "--verbose", action="store_true",
        help="narrate no-op runs (otherwise silent on no work)",
    )
    args = ap.parse_args()

    if not DB_PATH.exists():
        print(f"[ERROR] DB not found: {DB_PATH}")
        return 2

    # Read-only connection: mode=ro guarantees no DB write can occur (AC).
    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        rows = gather_rows(conn)
    finally:
        conn.close()

    baseline = load_baseline(BASELINE_PATH)
    findings, new_baseline = detect_drift(rows, baseline, args.narrative_threshold)
    save_baseline(BASELINE_PATH, new_baseline)

    if not findings:
        if args.verbose:
            print(f"[OK] no probe drift across {len(rows)} probed question(s).")
        return 0

    date_str = datetime.now().strftime("%Y%m%d")
    report_path = DOCS / f"bq_probe_drift_report_{date_str}.md"
    report_path.write_text(render_report(findings, date_str), encoding="utf-8")
    print(
        f"[DRIFT] {len(findings)} signal(s) across "
        f"{len({f['question_id'] for f in findings})} question(s) -> {report_path}"
    )
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
