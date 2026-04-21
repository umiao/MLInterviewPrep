"""Seed cn_elevator_pitch for the 7 behavioral master stories.

Idempotent: re-running overwrites with the same exact strings. Run this
AFTER applying migration 17 (adds cn_elevator_pitch column). Includes a
PRAGMA preflight that fails loudly if the column is missing, because
SQLite will silently no-op UPDATEs against a non-existent column under
some pragma configurations.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PITCHES: dict[str, str] = {
    "EX-15": (
        # Rewritten 2026-04-20 -- structural reframe story (was "process improvement").
        # Owns the dashboard blind spot, absorbs rollback, reframes single-choice
        # "who must migrate" into double-choice with ownership transfer, escalates to
        # senior leadership for capacity-budget boundary.
        "\u6211\u81ea\u5df1\u7684 traffic dashboard \u76f2\u533a\u6f0f\u6389\u4e86 hardcoded \u8c03\u7528"
        "\uff0c\u4e0b\u7ebf legacy model \u540e 3-4 \u4e2a Query Understanding pipeline "
        "\u88ab block\uff1b\u4e0d\u4e89\u6d41\u7a0b\u5bf9\u9519\u5148\u5403 rollback\uff0c"
        "\u4e00\u5468\u5185\u5168\u90e8 unblock \u6362\u5230 credibility\uff0c\u518d\u628a "
        "\"\u8c01\u5fc5\u987b\u8fc1\u79fb\" \u8fd9\u9053\u5355\u9009\u9898 reframe \u4e3a "
        "\u542b ownership transfer \u7684\u53cc\u9009\u9898\uff0c\u63a8\u5230 senior leadership "
        "\u5212\u6e05 capacity ownership \u8fb9\u754c"
        " | KEY FACTS: 1 \u5468 unblock 3-4 pipelines"
        " | dashboard \u76f2\u533a (URL params \u4e0d\u8bb0 hardcoded)"
        " | \u5f15\u5165 ownership transfer \u7b2c\u4e09\u9009\u9879"
        " | senior leadership boundary \u51b3\u8bae"
    ),
    "EX-16": (
        # Rewritten 2026-04-20 -- failure-cut story (was redemption-tail).
        # Owns the cross-team rollout manager couldn't get budgeted, absorbs
        # rollback, declines to deflect with available evidence, drives the
        # counterpart-bandwidth-as-line-item lesson into an org-level
        # senior-bench approver policy. Artifactory tail dropped -- belongs
        # only in calculated-risk framing per NRG-v2.
        "Manager \u6ca1\u62ff\u5230 cross-team PD quota \u8ba9\u6211\u72ec\u81ea"
        "\u625b release-by-DC rollout\uff1bDC2 \u51e0\u5206\u949f\u5185 panic out\uff0c"
        "rollback \u662f\u6211\u7684\uff0c\u6ca1\u62ff\u624b\u4e0a\u7684\u8bc1\u636e\u6307"
        "\u5bf9\u65b9\u800c\u662f framing \u6210 context gap\uff0c\u4e8b\u540e\u63a8\u52a8"
        "\u4e86 search engine \u5c42\u7684 cross-team senior-bench approver policy"
        " | KEY FACTS: DC2 \u51e0\u5206\u949f panic out"
        " | \u4e09\u5206\u4e4b\u4e00 quarter \u4fee\u590d + RCA \u4ee3\u4ef7"
        " | senior IC joint debug \u63ed\u51fa partial artifactory migration"
        " | org-level approver policy \u81f3\u4eca in effect"
    ),
    "EX-17": (
        "\u6536\u5230 senior IC \u4e25\u5389\u53cd\u9988\"\u7f3a\u4e4f\u57fa\u672c\u5de5\u7a0b"
        "\u7d20\u517b\"\uff1b\u4e0d push back \u800c\u5185\u5316\u6839\u56e0\u2014\u2014"
        "\u538b\u529b\u4e0b\u672a\u963b\u6321 manager shortcut\u2014\u2014\u91cd\u5efa"
        "\u4fe1\u8a89\u4e0e gate-keeping \u8d23\u4efb"
        " | KEY FACTS: senior IC \u4e25\u5389\u53cd\u9988"
        " | 'lacked basic engineering quality'"
        " | over-promise \u6839\u56e0"
        " | \u540e\u7eed gate-keeping \u8d23\u4efb"
    ),
    "EX-30": (
        "\u9ad8\u901f PM \u5408\u4f5c\u671f\u4e0a\u7ebf\"\u6570\u5b66\u4f18\u96c5\"hash"
        " \u672a\u8be2\u95ee\u4e0b\u6e38 consumer\uff1b\u81f4 2-3 \u4e2a\u4e0b\u6e38 DS"
        " \u56e2\u961f\u6570\u5468\u5206\u6790\u65f6\u95f4\u635f\u5931\uff1b\u8de8\u56e2\u961f"
        " rescue \u63d0\u6848\u88ab\u62d2\uff0c\u6700\u7ec8\u91c7\u7eb3 indexing \u56e2\u961f"
        " prior art"
        " | KEY FACTS: 2-3 \u4e2a\u4e0b\u6e38 DS/\u4ea7\u54c1\u56e2\u961f"
        " | \u6570\u5468\u5206\u6790\u65f6\u95f4\u635f\u5931"
        " | \u8de8\u56db\u56e2\u961f rescue \u63d0\u6848\u88ab\u62d2"
        " | \u56de\u5f52 indexing \u56e2\u961f prior art"
    ),
    "EX-33B": (
        "\u4f5c\u4e3a model believer \u5728 MoE \u4e0a\u5c42\u5c42\u8fed\u4ee3\u2014\u2014"
        "\u4fee bias\u3001\u4fee router\u3001\u52a0\u6b63\u4ea4 expert\uff1b\u8017\u5c3d"
        " ~80 GPU \u540e\u8ba4\u6e05 BI/GMB \u662f\u771f KPI\uff0cMRR \u662f self-fulfilling"
        " proxy"
        " | KEY FACTS: ~80 GPU \u8282\u70b9 | BI + GMB \u771f KPI | MRR \u4e0d\u662f KPI"
        " | \u6280\u672f unblocked \u4f46 business unlaunchable"
    ),
    "EX-34": (
        "\u5728 BBE \u9879\u76ee\u548c principal researcher disagree on seller-level"
        " \u7edd\u5bf9\u98ce\u9669 policy\uff1b\u7528\u65b0\u5356\u5bb6/\u5c0f\u5356\u5bb6"
        " false-positive \u6570\u636e + '\u7edd\u5bf9\u6807\u51c6\u662f lazy non-action"
        " \u4f2a\u88c5'\u91cd\u65b0\u6846\u5b9a\u95ee\u9898\uff1b\u843d\u5730 listing-level"
        " + cumulative seller escalation \u4e24\u5c42\u673a\u5236\uff0c\u5e76\u628a\u5bf9\u65b9"
        "\u771f\u5b9e\u987e\u8651\uff08audit \u4e00\u81f4\u6027\uff09\u53d8\u6210\u673a\u5236"
        "\u4fdd\u969c"
        " | KEY FACTS: BBE \u98ce\u9669 enforcement \u7c92\u5ea6"
        " | seller-level absolutism vs listing-level"
        " | \u65b0\u5356\u5bb6/\u5c0f\u5356\u5bb6 false-positive \u6570\u636e"
        " | listing-level + \u7d2f\u79ef\u5347\u7ea7"
        " | absolutism smell test"
    ),
    "EX-09B": (
        "\u5728 LLM \u5bf9\u8bdd\u641c\u7d22 design \u9636\u6bb5\u63d0\u51fa query rewrite"
        " \u8def\u5f84\u4f1a\u8ba9\u7528\u6237\u539f\u59cb query \u6d41\u5165\u4e0b\u6e38"
        " log/\u8bad\u7ec3\u6570\u636e\u7684 privacy \u98ce\u9669\uff1b\u4e0e team"
        " \u5171\u540c develop proxy item \u751f\u6210\u8def\u5f84\uff0c\u8ba9\u539f\u59cb"
        " query \u6c38\u4e0d\u6d41\u5165\u4e0b\u6e38\uff0c\u5e76\u628a privacy \u4f18\u52bf"
        "\u5199\u5165 design doc"
        " | KEY FACTS: query rewrite \u662f\u57fa\u4e8e query clustering/autocomplete"
        " \u7684\u81ea\u7136\u5ef6\u4f38"
        " | proxy item \u5b8c\u5168\u6d88\u9664 leakage\uff08eliminate not mitigate\uff09"
        " | privacy benefit \u5199\u5165 design doc"
        " | \u4e0e EX-09 \u662f\u540c project \u4e24\u4e2a\u72ec\u7acb cut"
    ),
}


def main() -> None:
    """Seed cn_elevator_pitch for the 7 master stories."""
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        cols = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(behavioral_examples)"
            ).fetchall()
        }
        if "cn_elevator_pitch" not in cols:
            raise SystemExit(
                "cn_elevator_pitch column missing --- run the migration in "
                "src/backend/database.py (version 17) first"
            )

        updated = 0
        missing: list[str] = []
        for example_id, pitch in PITCHES.items():
            cur = conn.execute(
                "UPDATE behavioral_examples SET cn_elevator_pitch = ? "
                "WHERE example_id = ?",
                (pitch, example_id),
            )
            if cur.rowcount == 0:
                missing.append(example_id)
            else:
                updated += 1
        conn.commit()

        if missing:
            raise SystemExit(
                f"[FAIL] Missing example rows (not updated): {missing}"
            )

        print(f"[DONE] Updated {updated}/7 master-story pitches")
        for example_id in PITCHES:
            row = conn.execute(
                "SELECT substr(cn_elevator_pitch, 1, 40) "
                "FROM behavioral_examples WHERE example_id = ?",
                (example_id,),
            ).fetchone()
            preview = row[0] if row and row[0] else "<NULL>"
            print(f"  {example_id}: {preview}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
