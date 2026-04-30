"""Slim Google Interview Prep Note (id=51) by replacing duplicated sections with cd://38 refs.

Per T-P1-535 [T-GOOG-REORG-SLIM51]. id=38 (Recruiter Call Prep) is the source
of truth for the 4 ML Domain dims and the 4 Hiring Attributes + Googleyness
sub-signals. id=51 currently duplicates both; this seed replaces each with a
short pointer and keeps the rest of the live-execution content intact:
schedule, Day-of Logistics, deep-QA prep, quick-review pointers, 90s intro,
Story Short-list, STAR reminder, G&L question predictions, Last-minute mindset.

Scope:
  - id=51 content replaced in place; sentinel gates the write.
  - id=38 MUST remain byte-identical (sha256 guard pre/post).
  - No other docs touched.

Idempotency: a NEW sentinel <!-- HUB_REORG_20260419_SLIM51_CD --> gates the
write. The old <!-- HUB_REORG_20260419_SLIM51 --> sentinel is treated as
stale and overwritten on first re-run after T-P1-676. Second run with the
new sentinel = 0 writes.

T-P1-676: migrated the 2 sub-doc links from db://38 (ProblemDrawer) to
cd://38 (CompanyDocDrawer). problems.id=38 ('Word Search II') and
company_documents.id=38 ('Google SWE III (AI/ML) -- Recruiter Call Prep')
are unrelated rows that share id 38; the legacy db:// scheme routed clicks
to the wrong drawer. validate_new_content now asserts the cd:// scheme and
refuses any stale db://38 link as a regression.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
# T-P1-676: bumped sentinel so the cd:// migration is detected as a NEW write
# even when the old SLIM51 body is byte-identical apart from the link scheme.
SENTINEL = "<!-- HUB_REORG_20260419_SLIM51_CD -->"
LEGACY_SENTINEL = "<!-- HUB_REORG_20260419_SLIM51 -->"

GUARD_IDS = (38,)

TARGET_ID = 51
EXPECTED_TITLE = "Google 2026-04-17 Interview Prep Note"

NEW_CONTENT = SENTINEL + """
# Google \u9762\u8bd5\u51c6\u5907 \u2014 2026-04-20 mock + 2026-04-21 R1 (rescheduled)

> R1 \u6539\u671f\u81f3\u5468\u4e8c (2026-04-21)\uff1b\u5468\u4e00 (2026-04-20) \u591a\u4e86\u4e00\u573a Google Champion Mock Coding\u3002**\u6b63\u5f0f R1 \u4f18\u5148\u7ea7\u9ad8\u4e8e\u4efb\u4f55\u51b2\u7a81\u7684 mock interview**\u3002

---

## \u65e5\u7a0b (Pacific Time)

| \u65e5\u671f | \u65f6\u6bb5 | \u65f6\u957f | \u7c7b\u578b | \u51c6\u5907\u91cd\u70b9 |
|------|------|------|------|---------|
| **Mon 2026-04-20** | **10:00 \u2013 11:00** | 60 min | **Google Champion Mock Coding** (Google Meet) | \u7b97\u6cd5 / DS / \u73b0\u573a\u53e3\u8ff0 + \u8fb9\u754c + \u590d\u6742\u5ea6 |
| **Tue 2026-04-21** | **11:15 \u2013 12:00** | 45 min | **R1 #1 \u2014 ML Basics & Knowledge** | ML domain / \u6a21\u578b\u7406\u8bba / \u6570\u636e + \u7279\u5f81 / ML-product \u5224\u65ad |
| Tue 2026-04-21 | 12:00 \u2013 13:15 | 75 min buffer | \u5348\u9910 / \u590d\u76d8\u5207\u6362 | \u7ad9\u8d77\u6765\u8d70\u52a8\uff0c\u522b\u4e00\u76f4\u60f3\u4e0a\u4e00\u573a |
| **Tue 2026-04-21** | **13:15 \u2013 14:00** | 45 min | **R1 #2 \u2014 BQ / Googleyness & Leadership** | STAR stories / \u56db\u5c5e\u6027\u5bf9\u5e94 / \u771f\u5b9e\u51b2\u7a81\u573a\u666f |

### Day-of Logistics
- Mock (4/20)\uff1aGoogle Meet \u94fe\u63a5\u5728 Google Calendar \u9080\u8bf7\uff1b\u63d0\u524d 5 \u5206\u949f\u52a0\u5165\uff1b\u8fd9\u662f Google Champion Program \u552f\u4e00\u4e00\u573a mock\uff0c**\u4e0d\u8981 no-show**\u3002
- \u6b63\u5f0f R1 (4/21)\uff1aZoom \u94fe\u63a5\u5728 Google Calendar \u9080\u8bf7\uff0c**\u63d0\u524d 5 \u5206\u949f\u52a0\u5165**
- \u53cc\u5c4f\uff1a\u4e3b\u5c4f\u89c6\u9891\uff0c\u526f\u5c4f\u653e\u8fd9\u4efd prep note + `bq_improved_stories.md` + \u4e00\u5f20\u7a7a\u767d scratch
- \u7eb8\u7b14 + \u6c34 + \u8033\u673a\u5907\u7528\uff08Zoom \u65ad\u4e86\u5207\u624b\u673a\u70ed\u70b9\uff09
- \u4e2d\u95f4 75 min buffer (12:00 \u2013 13:15)\uff1a\u5148\u5403\u996d\uff0c**\u4e0d\u770b R1 #1 \u7684\u590d\u76d8**\uff0c\u5927\u8111\u4f1a\u6302\u5728\u4e0a\u4e00\u573a\u3002\u540e\u534a\u6bb5\u5feb\u901f\u8fc7 Round 2 \u7684 story short-list\u3002

---

## Round 1 \u2014 ML Basics & Knowledge (4/21 11:15)

>\u56db\u4e2a\u8003\u5bdf\u7ef4\u5ea6\u8be6\u89c1 [Recruiter Call Prep](cd://38) \u00a7ML Domain Interview \u8003\u5bdf\u65b9\u5411

### \u6df1\u5ea6\u95ee\u7b54\u51c6\u5907 (high-signal \u8bdd\u9898)
- **Ranking losses**: BCE / pairwise hinge / listwise ListNet / LambdaRank \u2014 \u63a8\u5bfc + \u4f55\u65f6\u7528
- **Calibration**: Platt / Isotonic / temperature scaling\uff1bGMB bidding \u7684\u6821\u51c6\u9677\u9631
- **Eval offline/online \u4e0d\u4e00\u81f4**: counterfactual eval / IPS / \u53bb\u504f NDCG\uff08\u6211\u7684 SIGIR paper\uff09
- **LTR \u2192 Two-tower retrieval**: \u4e3a\u4ec0\u4e48\u5206\u5c42\u3001negative sampling \u7b56\u7565
- **A/B test**: \u6837\u672c\u91cf\u3001MDE\u3001SRM\u3001novelty effect (\u5df2\u6709 study note: pillar7.probability_statistics.ab_test_sample_size)
- **Feature drift / \u76d1\u63a7**: PSI\u3001KL\u3001Jensen-Shannon\u3001\u5206\u9636\u6bb5 alert

### \u5feb\u901f\u590d\u4e60 pointer
- `docs/doordash_ml_domain_ranking.md` \u2014 \u6392\u5e8f\u635f\u5931 + eval
- `docs/doordash_ml_domain_features_dl.md` \u2014 \u7279\u5f81\u5de5\u7a0b + DL \u57fa\u7840
- `docs/doordash_ml_domain_fundamentals.md` \u2014 bias/variance, regularization
- `docs/doordash_ml_domain_case_study.md` \u2014 \u5b8c\u6574 ML case \u7ed3\u6784
- `/framework/pillar7` \u2014 \u6982\u7387\u7edf\u8ba1\uff08A/B \u6837\u672c\u91cf note \u5df2\u5c31\u7eea\uff09

### \u5f00\u573a / \u81ea\u6211\u4ecb\u7ecd (90 \u79d2\u7248)
"\u6211\u662f Shenghui\uff0c\u76ee\u524d Pinterest staff SWE\uff0c\u4e4b\u524d\u5728 Etsy \u4e3b\u5bfc search ranking\u3002\u4e24\u6761\u4e3b\u7ebf\uff1a\u4e00\u662f search diversity\uff0c\u53d1\u73b0 intent collapse \u95ee\u9898\uff0c\u91cd\u65b0\u5b9a\u4e49\u8bc4\u4f30\u6307\u6807\u4e3a GMB \u800c\u975e Sale NDCG\uff0c\u6700\u7ec8\u5e73\u53f0\u5316\u6210\u53ef\u590d\u7528\u7684 allocation primitive\uff0c\u8de8\u5782\u76f4\u8fbe\u6210 200M+ \u5e74\u5316 GMB\u3002\u4e8c\u662f\u7ebf\u4e0a\u5b9e\u9a8c\u4e25\u8c28\u6027\uff0c\u8bbe\u8ba1\u53bb\u504f NDCG \u6846\u67b6\u53d1\u8868\u4e8e SIGIR\u3002\u6211\u6700\u64c5\u957f\u628a\u6a21\u7cca\u7684\u4e1a\u52a1\u4fe1\u53f7\u7ffb\u8bd1\u6210\u5177\u4f53\u7684 ranking/eval \u95ee\u9898\u3002"

---

## Round 2 \u2014 BQ / Googleyness & Leadership (4/21 13:15)

>4 Hiring Attributes + 5 Googleyness \u5b50\u4fe1\u53f7\u8be6\u89c1 [Recruiter Call Prep](cd://38) \u00a7G&L \u8003\u5bdf\u65b9\u5411

### Story Short-list (\u5bf9\u5e94 Googleyness)

| Signal | Story | \u5173\u952e\u4e00\u53e5\u8bdd |
|--------|-------|-----------|
| Ambiguity + Bias for Action | **EX-01 Hacker Week** | "\u4e00\u5468\u5185\u4ece\u53d1\u73b0 intent collapse \u5230 prototype \u9a8c\u8bc1\uff0c\u6ca1\u4eba\u8ba9\u6211\u505a\uff0c\u662f silent failure \u8ba9\u6211\u505a\u7684" |
| Challenge status quo + Have backbone | **EX-03 GMB vs Sale NDCG** | "\u884c\u4e1a\u6807\u51c6\u6307\u6807\u7cfb\u7edf\u6027\u504f\u597d\u4f4e\u4ef7\u5546\u54c1\uff0c\u6211\u4ece\u7b2c\u4e00\u6027\u539f\u7406\u8d28\u7591\u5e76\u63d0\u51fa\u66ff\u4ee3" |
| Collaboration + Earn trust | **EX-04 Stakeholder \u6559\u80b2** | "MRR \u4e0b\u964d\u5f15\u53d1\u8b66\u60d5\uff0c\u6211\u8981\u89e3\u91ca\u4e3a\u4ec0\u4e48'\u53d8\u5dee'\u7684\u6307\u6807\u6070\u6070\u8bf4\u660e\u7cfb\u7edf\u5728\u53d8\u597d" |
| **Conflict w/ Manager (polished)** | **EX-02 \u4e3b\u52a8\u8f6c\u56e2\u961f \u2192 [`[google-g&l] STORY A`](./bq_improved_stories.md#google-gl-story-a-conflict-with-manager----strategic-team-transfer-ex-02)** | "\u7ecf\u7406\u8bf4\u8d85\u51fa scope\uff0c\u6211\u6ca1\u7ee7\u7eed\u5728\u9519\u8bef\u8fb9\u754c\u786c\u63a8\uff0c\u8f6c\u5230 Final Ranking team \u91cd\u65b0\u5b9a\u4e49\u95ee\u9898" |
| **Conflict across Teams (polished)** | **EX-08 VP escalation \u2192 [`[google-g&l] STORY B`](./bq_improved_stories.md#google-gl-story-b-conflict-across-teams----vp-escalation-on-cumulative-degradation-ex-08)** | "\u6a21\u5757\u6570\u91cf\u6fc0\u589e\u5bfc\u81f4\u8d28\u91cf\u9000\u5316\u65f6\uff0c\u6211\u63a8\u52a8\u5efa\u7acb\u6a21\u5757\u4ef2\u88c1\u673a\u5236\uff0c\u4e0d\u662f\u56de\u907f\u5347\u7ea7" |
| **Failure + Growth (polished)** | **EX-17 Harsh feedback \u2192 [`[google-g&l] STORY C`](./bq_improved_stories.md#google-gl-story-c-failure--growth----harsh-feedback-into-mutual-respect-ex-17)** | "senior IC \u8bf4\u6211\u7f3a\u4e4f\u57fa\u672c\u5de5\u7a0b\u7d20\u517b\uff0c\u6211\u6ca1\u8fa9\u89e3\uff0c\u628a researcher \u6539\u52a8\u7684\u9505\u4e5f\u63a5\u4e0b\u6765\uff0c\u6700\u7ec8\u4ece\u5bf9\u7acb\u53d8\u6210\u6700\u5e38 review \u6211 PR \u7684\u4eba" |

> **T-P0-200 polish note (2026-04-14)**: The three rows marked **polished** link to STAR 2-3 min versions in `bq_improved_stories.md` under the `# [google-g&l]` section, each tagged with the Google Hiring Attribute + Googleyness sub-signal they target. Use those versions for Round 2 delivery; the Tier-1 originals (EX-02/08/17) remain canonical for non-Google interviews.

---

## Last-minute \u5fc3\u6001

- **\u4e0d\u8981**\u5728 Round 1 \u80cc\u516c\u5f0f\uff0c**\u8981**\u8bb2\u771f\u5b9e\u7684 ranking/eval \u7ecf\u9a8c
- **\u4e0d\u8981**\u5728 Round 2 \u628a story \u8bb2\u6210 PR \u7a3f\uff0c**\u8981**\u8bb2\u5177\u4f53\u7684\u5bf9\u8bdd\u548c\u6743\u8861
- Round 1 \u88ab\u6311\u6218\u65f6\u4e0d\u8981\u7acb\u523b\u6539\u7b54\u6848\u2014\u2014**\u5148\u6f84\u6e05 assumption**\uff0c\u518d\u8c03\u6574
- Round 2 \u88ab\u8ffd\u95ee\u7ec6\u8282\u65f6\u4e0d\u8981\u7f16\u2014\u2014**\u627f\u8ba4\u4e0d\u8bb0\u5f97 exact \u6570\u5b57**\uff0c\u7ed9 range + reasoning
- Mock interview \u51b2\u7a81\u7684\u8bdd\uff0c**\u6b63\u5f0f Google \u9762\u8bd5\u4f18\u5148**\uff0cmock \u53ef\u4ee5\u6539\u671f/\u53d6\u6d88
- 4/20 Google Champion Mock \u662f\u96be\u5f97\u7684 dry-run \u673a\u4f1a\uff1a\u7528\u5b83\u5bf9\u9f50\u53e3\u8ff0\u8282\u594f\u3001scratch \u4e60\u60ef\u3001protocol\uff1b\u4e0d\u8981\u628a\u5b83\u5f53\u6210"\u7ec3\u624b"\u6577\u884d\u3002

\u795d\u597d\u8fd0\u3002
"""


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
    """Sanity-check the new slim content before writing."""
    import re

    length = len(content)
    if not (4200 <= length <= 4800):
        raise RuntimeError(
            f"new content length {length} outside 4200-4800 window"
        )
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing from new content")
    cd_refs = re.findall(r"cd://(\d+)", content)
    if cd_refs.count("38") != 2:
        raise RuntimeError(
            f"expected exactly 2 cd://38 refs, found {cd_refs.count('38')}"
        )
    extra_cd = {int(r) for r in cd_refs} - {38}
    if extra_cd:
        raise RuntimeError(
            f"new content has unexpected cd refs: {sorted(extra_cd)}"
        )
    # T-P1-676 regression guard: refuse any stale db://N for sub-doc IDs.
    # company_documents.id=38 collides with problems.id=38, so db://38 routes
    # to the wrong drawer (cross-table corruption).
    db_refs = re.findall(r"db://(\d+)", content)
    if db_refs:
        raise RuntimeError(
            f"new content still has stale db:// refs {db_refs} -- must use "
            f"cd:// for sub-doc links (T-P1-676 cross-table-corruption fix)"
        )
    # Schedule rows must be preserved verbatim.
    schedule_markers = (
        "Mon 2026-04-20",
        "10:00 \u2013 11:00",
        "Tue 2026-04-21",
        "11:15 \u2013 12:00",
        "13:15 \u2013 14:00",
    )
    for m in schedule_markers:
        if m not in content:
            raise RuntimeError(f"schedule marker missing: {m!r}")
    # Story Short-list and bq_improved_stories.md anchors must survive.
    story_anchors = (
        "Story Short-list",
        "bq_improved_stories.md#google-gl-story-a",
        "bq_improved_stories.md#google-gl-story-b",
        "bq_improved_stories.md#google-gl-story-c",
    )
    for m in story_anchors:
        if m not in content:
            raise RuntimeError(f"story anchor missing: {m!r}")
    # Removed sections must NOT reappear.
    forbidden = (
        "### \u9762\u8bd5\u5b98\u671f\u5f85\u7684\u7ef4\u5ea6",  # Round 1 dims header
        "Google \u7684 Hiring Attributes (4 \u6761",           # Round 2 table header
        "Googleyness \u7684 5 \u4e2a\u5b50\u4fe1\u53f7",       # 5 sub-signals list
    )
    for m in forbidden:
        if m in content:
            raise RuntimeError(f"forbidden content still present: {m!r}")


def main() -> int:
    """Apply the slim rewrite idempotently, guarding id=38 byte-identical."""
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
                    f"guard doc id={did} changed during seed "
                    f"(before={before}, after={after})"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
