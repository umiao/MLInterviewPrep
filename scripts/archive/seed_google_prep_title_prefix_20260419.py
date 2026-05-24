"""Add [R1/<bucket>] prefix to 14 Google R1 Tier-3 doc titles for visual grouping.

Per T-P2-536 [T-GOOG-REORG-PREFIX]. Flat list on /companies/3/prep does not
visually group docs by topic. Since the doc drawer sorts alphabetically, a
prefix like [R1/Quick], [R1/Fund], [R1/Rank], [R1/Eval], [R1/Retr], [R1/Prod]
auto-buckets the 14 Tier-3 drill/quick-review docs.

Scope:
  - company_documents.title UPDATE ONLY (content column untouched).
  - 14 docs: id in {52, 57, 55, 56, 60, 61, 65, 62, 63, 67, 72, 64, 68, 69}.
  - Tier-1/Tier-2 prep docs (id=38, 51, 53) MUST remain byte-identical on title
    AND content (sha256 guard pre/post on their content, title equality check).

Idempotency: a title that already starts with '[R1/' is left alone; second run
writes 0 rows. The NEW_TITLES dict holds the target string, so even if a run
is interrupted mid-batch, each row converges to the same target on next run.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# Tier-1/Tier-2 docs whose title AND content must be preserved exactly.
GUARD_IDS = (38, 51, 53)
GUARD_EXPECTED_TITLES = {
    38: "Google SWE III (AI/ML) -- Recruiter Call Prep",
    51: "Google 2026-04-17 Interview Prep Note",
    53: "Google 2026-04-17 Prep Hub",
}

# id -> new title
NEW_TITLES: dict[int, str] = {
    # Quick-review (2)
    52: "[R1/Quick] Google DNN / Key Papers Gist",
    57: "[R1/Quick] Staging 13 Flashcards",
    # Fundamentals (2)
    55: "[R1/Fund] Regularization Deep Dive",
    56: "[R1/Fund] Bias-Variance + Overfitting Diagnosis",
    # Ranking losses & metrics (3)
    60: "[R1/Rank] LambdaRank / LambdaMART",
    61: "[R1/Rank] NDCG / MAP / MRR + Position Bias",
    65: "[R1/Rank] Multi-Objective Ranking (DPP / MMR)",
    # Calibration & eval (3)
    62: "[R1/Eval] Calibration: Platt / Isotonic / Temperature",
    63: "[R1/Eval] IPS / Counterfactual / Debiased NDCG",
    67: "[R1/Eval] A/B Test Rigor: Sample Size / SRM / CUPED",
    # Retrieval & embeddings (2)
    72: "[R1/Retr] MF to Two-Tower Bridge",
    64: "[R1/Retr] Two-Tower Retrieval Deep Dive",
    # Production gotchas (2)
    68: "[R1/Prod] Feature Drift: PSI / KL / JS / KS",
    69: "[R1/Prod] Train-Serve Skew / Leakage / Temporal Split",
}


def content_sha256(conn: sqlite3.Connection, doc_id: int) -> str:
    """Return sha256 hex of company_documents.content for doc_id."""
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id = ?",
        (doc_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"guard doc id={doc_id} missing")
    content = row[0] or ""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def title_of(conn: sqlite3.Connection, doc_id: int) -> str:
    """Return current title for doc_id, or empty string if missing."""
    row = conn.execute(
        "SELECT title FROM company_documents WHERE id = ?",
        (doc_id,),
    ).fetchone()
    return row[0] if row else ""


def main() -> int:
    """Apply the prefix rename idempotently. Return 0 on success."""
    if not DB_PATH.exists():
        print(f"[FAIL] db missing at {DB_PATH}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        # Guard pre-state: snapshot title + content hash for id=38/51/53.
        guard_pre: dict[int, tuple[str, str]] = {}
        for gid in GUARD_IDS:
            t = title_of(conn, gid)
            h = content_sha256(conn, gid)
            guard_pre[gid] = (t, h)
            expected = GUARD_EXPECTED_TITLES[gid]
            if t != expected:
                print(
                    f"[FAIL] guard id={gid} title mismatch pre-run\n"
                    f"       expected: {expected!r}\n"
                    f"       actual:   {t!r}",
                    file=sys.stderr,
                )
                return 2

        # Verify every target id exists before any write.
        missing = []
        for tid in NEW_TITLES:
            row = conn.execute(
                "SELECT id FROM company_documents WHERE id = ?",
                (tid,),
            ).fetchone()
            if row is None:
                missing.append(tid)
        if missing:
            print(f"[FAIL] target ids missing: {missing}", file=sys.stderr)
            return 3

        updates = 0
        skipped = 0
        for tid, new_title in NEW_TITLES.items():
            cur_title = title_of(conn, tid)
            if cur_title == new_title:
                print(f"[UNCHANGED] id={tid} already has target title")
                skipped += 1
                continue
            if cur_title.startswith("[R1/"):
                # Already-prefixed but different from target -> surface as warning
                # so a human inspects before we silently overwrite.
                print(
                    f"[WARN] id={tid} already prefixed but differs from target\n"
                    f"       current: {cur_title!r}\n"
                    f"       target:  {new_title!r}",
                    file=sys.stderr,
                )
            conn.execute(
                "UPDATE company_documents SET title = ? WHERE id = ?",
                (new_title, tid),
            )
            print(
                f"[UPDATE] id={tid} title\n"
                f"         was: {cur_title!r}\n"
                f"         now: {new_title!r}"
            )
            updates += 1

        # Guard post-state: title + content hash must match pre-state for id=38/51/53.
        for gid in GUARD_IDS:
            t_post = title_of(conn, gid)
            h_post = content_sha256(conn, gid)
            t_pre, h_pre = guard_pre[gid]
            if t_post != t_pre:
                conn.rollback()
                print(
                    f"[FAIL] guard id={gid} title changed\n"
                    f"       pre:  {t_pre!r}\n"
                    f"       post: {t_post!r}",
                    file=sys.stderr,
                )
                return 4
            if h_post != h_pre:
                conn.rollback()
                print(
                    f"[FAIL] guard id={gid} content sha256 changed "
                    f"pre={h_pre[:16]}... post={h_post[:16]}...",
                    file=sys.stderr,
                )
                return 5

        conn.commit()
        print(f"[OK] updates={updates} skipped={skipped} guards=OK")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
