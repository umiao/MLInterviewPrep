"""Rewrite EX-33 (MoE -> Allocation Paradigm Shift) per T-P0-578 (BQ-DEPTH-07).

Structural-polish rewrite per story_rewrite_protocol.md autorun boundary:
- Voice/length polish on Action (2293 -> ~1650 chars) and Result (988 -> ~900)
  to match golden EX-15/EX-17 cadence: short declaratives, sentence fragments
  OK, spoken-English rhythm, fewer abstract-noun-for-verb substitutions.
- principle_tags upgrade: drop generic `organizational_change`; add
  `credibility_first` (refused carry-over protection to protect the paradigm
  signal) and `honest_negative_result` (the unique mechanic of this story).
- risk_statement clarification: currently points failure-question users to
  EX-30 (Hash Misdesign, an unrelated project). The designated failure-cut
  of THIS MoE project is EX-33B. Fix the cross-reference to cite both with
  correct disambiguation. Add explicit NRG-v1 narration guard: do NOT lead
  with the 200M GMB number; lead with the `start test` framing so the
  honest-negative-mechanic lands before the downstream receipt.
- cn_elevator_pitch sharpened with KEY FACTS suffix covering the refreshed
  narration guard and paradigm-reframe outcome.
- 12 question_example_links relevance_notes refreshed against the new
  tightened STAR vocabulary.

This is NOT a content-level reframe:
- Same fundamental arc (honest negative result -> paradigm reframe -> 200M GMB)
- Same 3-beat Action structure (`start test` framing / mid-execution
  realization / reframe proposal)
- Same risk posture (staked personal track record on credibility of signal)
- EX-33B coherence preserved: `start test` / refused-to-wrap beat is kept,
  which is the load-bearing beat for EX-33B's "I stopped iterating" framing.

Idempotent via stable-invariant check: skips if the DB already contains the
new evidence_quotes[0] kill-line. Takes a timestamped DB backup with suffix
`_pre_ex33_rewrite` before any write, per protocol step 3.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "mle_prep.db"

EXAMPLE_ID = "EX-33"
KILL_LINE_FIRST_QUOTE = (
    "A wrapped success cannot convince anyone. A credibly honest negative "
    "result was the last empirical chip that flipped the paradigm."
)

NEW_TITLE = (
    "MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest "
    "Negative Result"
)

NEW_SITUATION = (
    "In the eBay search org, the dominant paradigm was pairwise distributed "
    "ranking -- each item scored independently, then sorted. The industry had "
    "moved toward whole-page optimization and reranking. Several senior ICs, "
    "my manager, and I had been flagging the gap for several quarters. The "
    "org agreed at the abstract level but had no concrete path. Shared vision, "
    "no path."
)

NEW_TASK = (
    "Leadership handed me a high-visibility project: migrate search from "
    "boosting to neural ranking plus MoE, consuming about 80 GPU nodes -- "
    "nearly all the org-wide headroom, shared with the cross-org AI intake. "
    "On the surface, a ranker upgrade. In my head, also a critical empirical "
    "test of the ranker-centric paradigm itself. If even the most "
    "sophisticated ranker architecture could not reconcile diversity, "
    "abandonment, and exploration with conversion, that would be the "
    "strongest possible evidence for reframing."
)

NEW_ACTION = (
    "(1) Scoped it as \"start test\", not \"test and launch\". Against org "
    "convention. My manager signed off, but the framing was mine to propose "
    "and own. Convention would have let me wrap a failure as \"carry over to "
    "next quarter\" -- IC's track record protected, paradigm-level signal "
    "destroyed. I gave that protection up on purpose. A wrapped success "
    "cannot convince anyone, and if this project was going to function as a "
    "paradigm test, the result had to be credible either way.\n\n"
    "(2) Mid-execution, something didn't fit. Adding an expert for "
    "abandonment and exploration, I saw it and the conversion expert "
    "co-activate but pull in opposite directions. First guess: under-trained "
    "-- more training rounds. The behavior stayed. Then it clicked: "
    "structural. These goal sets were orthogonal to conversion in a way a "
    "single item-level ranker could not reconcile on one head. Worse, by our "
    "launch criteria -- MRR up, revenue neutral -- this expert was "
    "launchable. Users were not better served. Homogeneity was worse. That "
    "gap made me question MRR itself: the training objective and the metric "
    "shared the same assumptions, so an MRR win did not independently "
    "validate user outcome. MRR was a self-fulfilling proxy, not a KPI.\n\n"
    "(3) Converted the failure into a reframe proposal. Three claims: (a) "
    "the ranker architecture cannot carry goals structurally orthogonal to "
    "conversion; (b) our metric system was masking the blind spot; (c) the "
    "right move was to make the tradeoff explicit as an allocation policy, "
    "so the model could work inside a defined frame instead of carrying "
    "optimization and tradeoff on the same head. I drove it through the "
    "review cycle personally. Several quarters of pre-work from me, senior "
    "ICs, and my manager had already prepared the org psychologically. "
    "MoE's negative result was the last empirical chip."
)

NEW_RESULT = (
    "MoE was officially deprecated. Did not ship. That honest negative "
    "result was the chip that made the reframe credible. The Allocation "
    "direction that came out of it later shipped **200M+ in annualized "
    "GMB** -- the paradigm reframe, not the MoE project itself, was the "
    "real business outcome. Three org-level follow-throughs locked it in: "
    "(1) the team was renamed from \"ranking modeling\" to \"policy "
    "learning\" and eventually \"Allocation team\"; (2) allocation policy "
    "became the team's new main line of work, with authenticated listings, "
    "C2C new listings, and the diversity framework reuse all shipping under "
    "it; (3) leadership's default planning question shifted -- \"what user "
    "problem are we solving and is a ranker the right tool for it\" "
    "replaced \"how do we train a better ranker\". That mental-model change "
    "is irreversible. The 200M figure is its downstream receipt."
)

NEW_RISK_STATEMENT = (
    "I staked my personal track record as collateral when I refused the "
    "carry-over convention. If MoE had been wrapped, the failure would have "
    "been invisible but so would the paradigm lesson. Real costs were "
    "personal (no carry-over protection for my record), team (mindset "
    "adjustment away from \"we are launching something\"), and political "
    "(signaling to leadership that a top-down strategic project might not "
    "work).\n\n"
    "USAGE RULE: do NOT use this framing for pure-failure / \"recent "
    "mistake\" / \"what would you do differently\" questions -- the 200M+ "
    "tail will read as disguised success and backfire. For failure-cut "
    "questions about this same MoE project, use EX-33B (the model-believer "
    "humility cut that stops at the lesson, no rescue). For an unrelated "
    "failure project, use EX-30 (Hash Misdesign).\n\n"
    "NRG-v1 (narration guard): do NOT lead with the 200M GMB number -- "
    "that reads as boast and hides the \"honest negative result\" "
    "credibility mechanic that is the actual L5 signal. Lead with the "
    "\"start test\" framing decision and the deliberate forfeit of "
    "carry-over protection. Let the org-level outcome land at the end as "
    "a receipt of the paradigm reframe, not as the headline."
)

NEW_EVIDENCE_QUOTES = [
    KILL_LINE_FIRST_QUOTE,
    "I scoped it as 'start test', not 'test and launch' -- gave up my "
    "carry-over protection on purpose so the result would be credible either "
    "way.",
    "MRR was a self-fulfilling proxy, not a KPI -- training objective and "
    "metric shared the same assumptions.",
    "The ranker architecture cannot carry goals structurally orthogonal to "
    "conversion on a single head.",
    "The 200M GMB figure is the downstream receipt of the paradigm reframe, "
    "not the point of the story.",
]

NEW_PRINCIPLE_TAGS = [
    "paradigm_shift",
    "honest_negative_result",
    "credibility_first",
    "influence_without_authority",
    "evidence_based_advocacy",
    "coalition_building",
    "calculated_risk",
    "long_term_bet",
]

NEW_ANALOGY = (
    "A wrapped success cannot convince anyone. A credibly honest negative "
    "result was the last chip that flipped the org's paradigm."
)

NEW_TECH_TERMS = {
    "MoE (Mixture of Experts)": (
        "ranker architecture that routes inputs to specialized sub-networks "
        "('experts') combined via a gating mechanism"
    ),
    "Neural ranking": (
        "deep-model-based item scoring that replaces handcrafted boosting "
        "and tree-based rankers"
    ),
    "Pairwise ranking": (
        "training scheme that scores each item independently and sorts, "
        "optimizing pairwise preference"
    ),
    "Whole-page optimization": (
        "optimizing the full result page jointly rather than ranking items "
        "in isolation"
    ),
    "Reranking": (
        "second-stage reorder of a candidate set produced by a base ranker, "
        "typically under page-level constraints"
    ),
    "Allocation policy": (
        "explicit policy that decides how candidates are distributed across "
        "business goals, making tradeoffs visible at the page level"
    ),
    "Expert routing": (
        "the gating-network decision that decides which expert handles a "
        "given query/item"
    ),
    "Item-level ranker": (
        "a ranker that scores candidates one at a time, independent of the "
        "rest of the page"
    ),
    "MRR (Mean Reciprocal Rank)": (
        "position-weighted retrieval metric that turned out to be a "
        "self-fulfilling proxy in this project because the ranker training "
        "objective and the metric shared the same assumptions -- not a real "
        "business KPI"
    ),
}

NEW_CN_ELEVATOR_PITCH = (
    "eBay 搜索 org 范式停在 pairwise distributed ranking; leadership 批 MoE + "
    "neural ranking 项目 ~80 GPU nodes，我把 scope 定为 \"start test\" 而非 "
    "\"test and launch\"——放弃 carry-over 保护，让结果两边都可信。执行中看到"
    " abandonment/exploration expert 与 conversion expert 结构性正交，单头 "
    "item-level ranker 扛不动；MRR up、revenue neutral 按 launch criteria 能"
    "上线，用户并未更好——认清 MRR 是 self-fulfilling proxy 不是 KPI。把失败"
    "转成 reframe 提案——allocation policy 让模型在明确 tradeoff 框内工作，"
    "替代 ranker-centric 规划。MoE deprecate；下游 Allocation 方向 shipped "
    "**200M+ 年化 GMB**；team 从 ranking modeling 改名为 Allocation team；"
    "leadership 默认规划问题从\"怎么训更强 ranker\"换成\"这是不是 ranker 该解"
    "的问题\" | KEY FACTS: ~80 GPU nodes (nearly all org-wide headroom) | "
    "\"start test\" vs \"test and launch\" 弃 carry-over 保护 | MRR = "
    "self-fulfilling proxy, BI/GMB 才是真 KPI | MoE deprecated, 下游 "
    "Allocation 200M+ 年化 GMB | team rename: ranking modeling -> Allocation "
    "team | paradigm reframe 不可逆; default 规划问题换了"
)

# Refreshed relevance_notes (12 links) against the new STAR vocabulary.
NEW_LINK_NOTES: dict[str, str] = {
    "OWN-6": (
        "Bold risk -- scoped a top-down 80-GPU project as \"start test\" not "
        "\"test and launch\"; gave up carry-over protection on purpose so the "
        "paradigm signal would be credible either way."
    ),
    "PS-6": (
        "Calculated risk -- short-term personal cost (no carry-over cover for "
        "my record) traded for long-term org value (paradigm reframe + 200M+ "
        "annualized GMB downstream receipt)."
    ),
    "OWN-10": (
        "Long-term impact -- multi-quarter paradigm push; the receipt is a "
        "team rename (\"ranking modeling\" -> \"Allocation team\") and an "
        "irreversible default planning question, not a single-quarter ship."
    ),
    "IMP-10": (
        "Long-term impact -- full Allocation policy arc: honest negative "
        "result on MoE as the empirical chip, then 200M+ annualized GMB "
        "across authenticated listings / C2C / diversity reuse."
    ),
    "IMP-9": (
        "Short-term vs long-term -- declined a \"launchable\" MoE expert "
        "(MRR up, revenue neutral) and carry-over protection to keep the "
        "paradigm-level signal credible; optimized for the reframe, not the "
        "ship."
    ),
    "INN-6": (
        "New strategy with major improvement -- allocation policy replaced "
        "ranker-centric planning as the team's main line; default question "
        "became \"is a ranker the right tool for this problem\"."
    ),
    "INN-8": (
        "Questioned a traditional approach -- pairwise distributed ranking; "
        "proposed allocation policy to make cross-goal tradeoffs explicit at "
        "the page level instead of forcing them onto one ranker head."
    ),
    "COM-2": (
        "Persuade others to change direction -- convinced the org to deprecate "
        "its own top-down strategic project; the honest negative result was "
        "the persuasion mechanic, not rhetoric."
    ),
    "COL-5": (
        "Align teams/stakeholders on shared goal -- multi-quarter coalition "
        "with senior ICs and my manager so the org was psychologically ready "
        "when the empirical chip landed."
    ),
    "IMP-4": (
        "Improved a system adding significant value -- paradigm reframe "
        "(ranker-centric -> allocation policy) yielded 200M+ annualized GMB "
        "and a durable mental-model change at leadership's planning layer."
    ),
    "INN-1": (
        "Identified an opportunity for improvement -- recognized the paradigm "
        "gap between pairwise item-level ranking and the industry's whole-page "
        "/ allocation direction; surfaced it in an org where vision existed "
        "but no path did."
    ),
    "OWN-9": (
        "Innovate without full information -- ran an 80-GPU empirical test "
        "under strategic uncertainty; the honest negative result itself was "
        "the signal, not a setback to recover from."
    ),
}


def _already_rewritten(conn: sqlite3.Connection) -> bool:
    """Return True if the new kill-line first quote is already persisted."""
    row = conn.execute(
        "SELECT evidence_quotes FROM behavioral_examples WHERE example_id = ?",
        (EXAMPLE_ID,),
    ).fetchone()
    if not row or not row[0]:
        return False
    try:
        quotes = json.loads(row[0]) if isinstance(row[0], str) else row[0]
    except json.JSONDecodeError:
        return False
    if not isinstance(quotes, list) or not quotes:
        return False
    return quotes[0] == KILL_LINE_FIRST_QUOTE


def _backup_db() -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.with_suffix(
        DB_PATH.suffix + f".bak.{ts}_pre_ex33_rewrite"
    )
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] {backup_path.name}")
    return backup_path


def _apply(conn: sqlite3.Connection) -> dict[str, int]:
    """Apply all primary-row + link-note updates atomically. Returns counts."""
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE behavioral_examples
           SET title = ?,
               situation = ?,
               task = ?,
               action = ?,
               result = ?,
               evidence_quotes = ?,
               principle_tags = ?,
               risk_statement = ?,
               analogy = ?,
               tech_terms = ?,
               cn_elevator_pitch = ?
         WHERE example_id = ?
        """,
        (
            NEW_TITLE,
            NEW_SITUATION,
            NEW_TASK,
            NEW_ACTION,
            NEW_RESULT,
            json.dumps(NEW_EVIDENCE_QUOTES, ensure_ascii=False),
            json.dumps(NEW_PRINCIPLE_TAGS, ensure_ascii=False),
            NEW_RISK_STATEMENT,
            NEW_ANALOGY,
            json.dumps(NEW_TECH_TERMS, ensure_ascii=False),
            NEW_CN_ELEVATOR_PITCH,
            EXAMPLE_ID,
        ),
    )
    if cur.rowcount != 1:
        raise RuntimeError(
            f"expected 1 row updated on behavioral_examples, got {cur.rowcount}"
        )

    ex_row = conn.execute(
        "SELECT id FROM behavioral_examples WHERE example_id = ?",
        (EXAMPLE_ID,),
    ).fetchone()
    if not ex_row:
        raise RuntimeError("EX-33 row not found after update")
    ex_row_id = ex_row[0]

    updated_links = 0
    missing_qs: list[str] = []
    for qid_str, note in NEW_LINK_NOTES.items():
        q_row = conn.execute(
            "SELECT id FROM behavioral_questions WHERE question_id = ?",
            (qid_str,),
        ).fetchone()
        if not q_row:
            missing_qs.append(qid_str)
            continue
        q_row_id = q_row[0]
        res = conn.execute(
            "UPDATE question_example_links SET relevance_note = ? "
            "WHERE question_id = ? AND example_id = ?",
            (note, q_row_id, ex_row_id),
        )
        if res.rowcount == 1:
            updated_links += 1
        else:
            missing_qs.append(
                f"{qid_str} (link row not found; rowcount={res.rowcount})"
            )

    if missing_qs:
        raise RuntimeError(
            f"Some question links could not be refreshed: {missing_qs}"
        )

    return {"example_rows": 1, "link_rows": updated_links}


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        if _already_rewritten(conn):
            print("[SKIP] EX-33 already carries the new kill-line; nothing to do")
            return

        conn.close()  # close before copying the file on Windows
        _backup_db()
        conn = sqlite3.connect(str(DB_PATH))

        counts = _apply(conn)
        conn.commit()
    finally:
        conn.close()

    print(
        f"[DONE] EX-33 rewrite applied: "
        f"examples={counts['example_rows']}, links={counts['link_rows']}"
    )
    print(
        f"  action={len(NEW_ACTION)} chars (was 2293), "
        f"result={len(NEW_RESULT)} chars (was 988)"
    )
    print(f"  principle_tags={NEW_PRINCIPLE_TAGS}")


if __name__ == "__main__":
    main()
