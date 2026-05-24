"""Rewrite Google Prep Hub (id=53) into a pure 3-tier navigation index.

Per T-P1-534 [T-GOOG-REORG-HUB]. Decision: id=53 is the single landing page
for /companies/3/prep; all content lives in other docs, reached via cd://.

Tiering:
  - Tier 1 (this doc): self-identify as landing/index
  - Tier 2 (live execution): cd://51 Interview Prep Note, cd://38 Recruiter Call
  - Tier 3 (study materials, by bucket):
      Quick-review:              52, 57
      Fundamentals:              55, 56
      Ranking losses & metrics:  60, 61, 65
      Calibration & eval:        62, 63, 67
      Retrieval & embeddings:    72, 64
      Production gotchas:        68, 69

Scope:
  - id=53 content is replaced (old T-P1-530 <!-- DEDUPED_20260419 --> and
    the original <!-- HUB_REORG_20260419 --> sentinels are overwritten by the
    new <!-- HUB_REORG_20260419_CD --> sentinel).
  - id=38 and id=51 are NOT touched; their SHA-256 hashes are captured before
    and after and compared.
  - No other of the 14 Tier-3 docs is touched.

Idempotency: the new sentinel <!-- HUB_REORG_20260419_CD --> gates the write.
Second run = 0 writes.

T-P1-676: migrated all 16 sub-doc links from db://N (ProblemDrawer scheme) to
cd://N (CompanyDocDrawer scheme). Reason: every Tier-2 / Tier-3 sub-doc id
(38/51/52/55/56/57/60-65/67-69/72) collides with an unrelated problems.id row
sharing the same numeric id; the legacy db:// scheme routed clicks to the
wrong drawer (cross-table corruption). cd:// is the resolver-correct scheme
per T-P0-672/673/674. validate_new_content now refuses any stale db://N for
sub-doc IDs as a regression.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
# T-P1-676: bumped sentinel so the cd:// migration is detected as a NEW
# write even when the old HUB_REORG body shape is otherwise unchanged.
SENTINEL = "<!-- HUB_REORG_20260419_CD -->"
LEGACY_SENTINEL = "<!-- HUB_REORG_20260419 -->"

# IDs that MUST remain byte-identical before/after this seed.
GUARD_IDS = (38, 51)

# Target doc to rewrite.
TARGET_ID = 53
EXPECTED_TITLE = "Google 2026-04-17 Prep Hub"

NEW_CONTENT = SENTINEL + """
# Google SWE III — Prep Hub

> Tier-1 landing。4/20 10:00 PT mock + 4/21 11:15 / 13:15 PT R1 两场；日程详见 [cd://51](cd://51)。

## Tier 2 — 现场执行
- [Interview Prep Note](cd://51)
- [Recruiter Call Prep](cd://38)

## Tier 3 — 复习材料

**Quick-review**
- [DNN / Key Papers Gist](cd://52)
- [Staging 13 Flashcards](cd://57)

**Fundamentals**
- [Regularization](cd://55)
- [Bias-Variance](cd://56)

**Ranking losses & metrics**
- [LambdaRank / LambdaMART](cd://60)
- [NDCG / MAP / MRR](cd://61)
- [Multi-Objective (DPP / MMR)](cd://65)

**Calibration & eval**
- [Platt / Isotonic / Temp](cd://62)
- [IPS / Debiased NDCG](cd://63)
- [A/B Rigor: SRM / CUPED](cd://67)

**Retrieval & embeddings**
- [MF \u2192 Two-Tower Bridge](cd://72)
- [Two-Tower Retrieval](cd://64)

**Production gotchas**
- [Feature Drift: PSI / KL / JS / KS](cd://68)
- [Train-Serve Skew / Leakage](cd://69)
"""

EXPECTED_CD_REFS = {38, 51, 52, 55, 56, 57, 60, 61, 62, 63, 64, 65, 67, 68, 69, 72}


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of a UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def collect_guard_hashes(conn: sqlite3.Connection) -> dict[int, str]:
    """Snapshot SHA-256 of content column for GUARD_IDS."""
    out: dict[int, str] = {}
    for did in GUARD_IDS:
        row = conn.execute(
            "SELECT content FROM company_documents WHERE id = ?", (did,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"guard doc id={did} missing")
        out[did] = sha256_bytes(row[0])
    return out


def validate_new_content(content: str) -> None:
    """Sanity-check the new Tier-1 landing content before writing."""
    import re

    length = len(content)
    if not (500 <= length <= 900):
        raise RuntimeError(
            f"new content length {length} outside 500-900 window"
        )
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing from new content")
    refs = {int(m) for m in re.findall(r"cd://(\d+)", content)}
    missing = EXPECTED_CD_REFS - refs
    extra = refs - EXPECTED_CD_REFS
    if missing:
        raise RuntimeError(f"new content missing cd refs: {sorted(missing)}")
    if extra:
        raise RuntimeError(f"new content has unexpected cd refs: {sorted(extra)}")
    # T-P1-676 regression guard: refuse any stale db://N for sub-doc IDs.
    # Every Tier-2/Tier-3 ID collides with an unrelated problems.id row, so
    # db://N would route to ProblemDrawer instead of CompanyDocDrawer.
    stale = {int(m) for m in re.findall(r"db://(\d+)", content)}
    bad = sorted(stale & EXPECTED_CD_REFS)
    if bad:
        raise RuntimeError(
            f"new content contains stale db:// refs to sub-doc IDs {bad} "
            f"(T-P1-676 cross-table-corruption regression). Use cd:// per "
            f"T-P0-672/673/674."
        )
    # Tier self-identify markers.
    for marker in ("Tier-1 landing", "Tier 2", "Tier 3"):
        if marker not in content:
            raise RuntimeError(f"tier marker missing: {marker!r}")


def main() -> int:
    """Apply the Tier-1 hub rewrite idempotently, guarding id=38 and id=51."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_new_content(NEW_CONTENT)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        guard_before = collect_guard_hashes(conn)
        for did, h in guard_before.items():
            print(f"[GUARD-PRE ] doc {did} sha256={h[:12]}...")

        row = conn.execute(
            "SELECT title, content FROM company_documents WHERE id = ?",
            (TARGET_ID,),
        ).fetchone()
        if row is None:
            print(f"[ERROR] target doc {TARGET_ID} not found")
            return 1
        cur_title, cur_content = row
        if cur_title != EXPECTED_TITLE:
            print(
                f"[WARN] title mismatch: stored={cur_title!r} "
                f"expected={EXPECTED_TITLE!r} -- title NOT changed"
            )

        if SENTINEL in cur_content:
            print(
                f"[UNCHANGED] doc {TARGET_ID} ({cur_title}) -- "
                f"sentinel '{SENTINEL}' already present; 0 writes"
            )
        else:
            new_hash = sha256_bytes(NEW_CONTENT)
            now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute(
                "UPDATE company_documents "
                "SET content = ?, content_hash = ?, updated_at = ? "
                "WHERE id = ?",
                (NEW_CONTENT, new_hash, now, TARGET_ID),
            )
            conn.commit()
            old_len = len(cur_content)
            new_len = len(NEW_CONTENT)
            print(
                f"[UPDATE] doc {TARGET_ID} rows={cur.rowcount} "
                f"old_len={old_len} new_len={new_len} "
                f"delta={new_len - old_len:+d}"
            )

        guard_after = collect_guard_hashes(conn)
        for did in GUARD_IDS:
            before = guard_before[did]
            after = guard_after[did]
            status = "OK" if before == after else "CHANGED"
            print(
                f"[GUARD-POST] doc {did} sha256={after[:12]}... {status}"
            )
            if before != after:
                raise RuntimeError(
                    f"guard doc id={did} changed during seed (before={before}, after={after})"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
