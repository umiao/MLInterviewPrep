"""Rewrite EX-01 (behavioral_examples.id=1) "Search Diversity: Intent
Collapse Discovery" STAR/tags/pitch/analogy/tech_terms to match the
golden EX-15/EX-17/EX-02 voice (spoken-English rhythm, short declaratives,
sentence fragments OK, no AI-explainer mode), and refresh the 16
question_example_links.relevance_note rows so the whole page is
internally consistent.

Red-flag scan against the pre-rewrite version (id=1, 2026-04-23):
- Action was bullet-list format ("- Analyzed...", "- Diagnosed...",
  "- Built..."). Golden EX-15/17 are prose, not bullets.
- Result stacked four wins in four sentences ("revenue improvement
  potential" + "multi-year initiative with 200M+" + "fundamentally
  changed how the organization approached ranking optimization" +
  "published at SIGIR"). Reads as boast-stacked; the L5 signal is the
  item-vs-page-level insight, not the trophy count.
- principle_tags was 8 generic Amazon-LP-style labels (ownership,
  innovation, problem_solving, bias_for_action, dive_deep, deliver_
  results, think_big, influence_without_authority). Per the golden
  trait matrix (docs/bq_golden_trait_matrix.md section 2), EX-01's
  actual facets are: invisible-to-standard-metrics (primary for
  data_analysis), root-cause-diagnosis, self-initiated-direction,
  self-assigned-to-end-to-end-prototype, problem-framing-before-
  stakeholder-persuasion, ambiguous-assignment. These specific facets
  should replace the generic LP grab bag.
- No NRG block existed. The narration risk here is real and not
  generic: opening with "200M+ annualized impact" or SIGIR invites
  the interviewer to hear a brag-first story instead of the
  root-cause diagnosis. NRG-v1 makes this explicit.
- cn_elevator_pitch already had a KEY FACTS suffix but was three
  lines and generic ("200M+ annualized impact"); upgrade it to the
  fresh EX-02 / EX-14 pattern with the item-vs-page insight as a
  named KEY FACT.

Boundary check vs T-P0-575 task spec (PRE-APPROVED FOR AUTORUN
2026-04-23 per Discord msg 1496990176625561771):
PERMITTED: voice/length polish matching golden EX-15/17, principle_tag
upgrade from generic to specific facet names, cn_elevator_pitch
rewrite with KEY FACTS suffix, link relevance_note tightening,
propagation surface sync (bq_behavioral_examples.json, bq_story_arcs.
json, seed_behavioral_themes.py, _batch1_cn_pitches.py).
NOT taken: no content-level reframe (the 3-beat arc -- discover
intent collapse via abandon logs -> diagnose item-level scoring as
root cause -> build one-week end-to-end prototype -- is the existing
arc, not a new beat), no inventing new beats, no new red-flag
interpretation, no dual-cut split, no fundamental outcome/lesson
change. The lesson "item-level scoring creates page-level
homogeneity" is the existing lesson -- the rewrite sharpens it and
the NRG-v1 protects against boast-stacking during delivery.

Idempotency: situation field starting with the unique opener phrase
"During Hacker Week I went looking for where our search ranker was
failing silently" indicates the rewrite is already applied. We use
a unique mid-sentence marker not present in the current opener
("During Hacker Week, I discovered that our search ranking system
was silently failing half its users").

Project convention (CLAUDE.md invariant 3): every DB content row
needs a git-tracked idempotent seed script. This is the canonical
source for EX-01 STAR + the propagation surface (title/tags/pitch/
relevance_notes). The cn_elevator_pitch canonical upstream is
scripts/_batch1_cn_pitches.py (line 42, key `1`), edited inline as
part of this same change so re-running _batch1 produces the new
pitch.
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

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
ROW_ID = 1
EXAMPLE_ID = "EX-01"

# Unique mid-sentence marker present only in the new situation opener.
# Current (old) situation starts with "During Hacker Week, I discovered
# that our search ranking system"; new starts with "During Hacker Week
# I went looking for where our search ranker was failing silently".
# The phrase "was failing silently" is absent from the old opener.
IDEMPOTENT_MARKER = "was failing silently"

NEW_TITLE = "Search Diversity --- Intent Collapse via Item-vs-Page Diagnosis"

NEW_SITUATION = (
    "During Hacker Week I went looking for where our search ranker "
    "was failing silently. Standard dashboards looked healthy. But "
    "multi-intent queries like \"pokemon\" returned 90%+ trading "
    "cards, while purchase data showed half the buyers wanted games, "
    "toys, or figures. The dashboard was fine because the dominant-"
    "intent users were fine. The missing half was invisible."
)

NEW_TASK = (
    "No one had assigned this. One week to go from a hunch to a "
    "defensible diagnosis plus a working prototype -- or drop it. "
    "The framing mattered more than the fix. If I couldn't name "
    "precisely why the ranker produced homogeneous pages, nobody "
    "downstream would fund a multi-intent solution on top of a "
    "healthy-looking dashboard."
)

NEW_ACTION = (
    "First pass: abandon-log slice. Sorted queries by post-impression "
    "drop-off and looked for the pattern. Hundreds of high-volume "
    "multi-intent queries collapsed the same way -- one product type "
    "crowded out every other valid interpretation. Not a bug on any "
    "single query. A systematic bias.\n\n"
    "Root-cause call: the ranker scored each item in isolation. It "
    "had no mechanism to reason about the page. When the top candidates "
    "all looked alike, the page looked alike -- by design. Item-level "
    "scoring was producing page-level homogeneity, and no amount of "
    "per-item tuning would fix it. The gap was structural, not a "
    "calibration miss.\n\n"
    "Prototype: diversity-blending layer on top of the existing "
    "ranker. Cheap intent-coverage proxy -- I didn't try to rewrite "
    "holistic ranking in a week. End-to-end in the Hacker Week "
    "window: abandon-log data pipeline, blending algorithm, "
    "experiment framework. Validated against purchase data that the "
    "blended pages surfaced intents the dashboard had never "
    "measured."
)

NEW_RESULT = (
    "The prototype survived review and grew past Hacker Week. "
    "Compounded across verticals into 200M+ annualized impact over "
    "multiple years. The methodology was later written up at SIGIR.\n\n"
    "The lesson I carry: **item-level scoring creates page-level "
    "homogeneity.** Any time a ranker optimizes per-candidate without "
    "a page-level constraint, the top-K will cluster -- and the "
    "dashboard will look fine because the dominant-intent users are "
    "fine. Now before I trust a \"healthy\" search metric I ask which "
    "users it's measuring and which ones it cannot see."
)

NEW_RISK = (
    "Surface risk: one more unshipped Hacker Week prototype, the "
    "abandoned-half stays abandoned, the dashboard keeps looking "
    "healthy. The structural risk is worse. Kept the frame vague "
    "and the story becomes a self-discovery brag; the interviewer "
    "hears \"I had a cool idea\" instead of the actual L5 signal -- "
    "that I named item-level scoring as the cause of page-level "
    "homogeneity and could defend that diagnosis with abandon-log "
    "and purchase-data evidence. Org-level: the whole class of "
    "invisible-to-standard-metrics failures goes unexamined when "
    "nobody pays the cost of the counter-intuitive slice; dashboards "
    "that measure the satisfied users keep winning budget over "
    "investigations into the users who leave.\n\n"
    "<!-- NRG-v1 --> NARRATION GUARD: This is an invisible-to-"
    "standard-metrics / root-cause-diagnosis story. The narration "
    "risk is boast-stacking the outcome -- leading with 200M+ or "
    "SIGIR turns an L5 diagnosis story into an L4 trophy story. "
    "Lead with the invisible half (\"the dashboard was fine because "
    "the dominant-intent users were fine; the missing half was "
    "invisible\") and the item-vs-page diagnosis (\"item-level "
    "scoring was producing page-level homogeneity by design\"). Two "
    "beats must land before the outcome: (1) abandon-log slice "
    "surfaced the pattern standard metrics masked, (2) the ranker "
    "had no page-level reasoning mechanism and that was structural, "
    "not calibration. Save the 200M+ / SIGIR line for the Result, "
    "one beat, no stacking. If the interviewer cuts off mid-story, "
    "the standalone close is \"Item-level scoring creates page-level "
    "homogeneity -- any healthy-looking metric could be measuring "
    "only the users the system didn't lose.\""
)

# Drop generic Amazon-LP tags; use the specific facets claimed in
# docs/bq_golden_trait_matrix.md sections 2.3 (data_analysis) and 2.12
# (ambiguity_uncertainty) for EX-01.
NEW_PRINCIPLE_TAGS = [
    "invisible_to_standard_metrics",
    "root_cause_diagnosis",
    "item_vs_page_level_reasoning",
    "self_initiated_direction",
    "end_to_end_prototype_one_week",
    "problem_framing_before_persuasion",
    "ambiguous_assignment_ownership",
    "dashboard_blindspot_discipline",
]

# Drop the restaurant analogy -- golden EX-14/15/17 all have analogy=None.
# The "item-level scoring creates page-level homogeneity" line carries more
# weight standalone than a food metaphor.
NEW_ANALOGY = None

NEW_TECH_TERMS = json.dumps(
    {
        "LTR (Learning to Rank)": (
            "ML model that scores and orders search results; "
            "pointwise/pairwise LTR scores each item in isolation, "
            "which is precisely the mechanism that creates page-level "
            "homogeneity on multi-intent queries"
        ),
        "Intent collapse": (
            "when a ranker's top-K converges on a single interpretation "
            "of an ambiguous query, crowding out other valid intents"
        ),
        "GMB": (
            "Gross Merchandise Bought -- dollar value of purchases; the "
            "key business metric used to validate whether diversity "
            "blending actually served the invisible half"
        ),
        "Abandon-log slice": (
            "post-impression drop-off analysis; surfaces systematic "
            "failures the dashboard masks because the dashboard only "
            "measures users who stayed"
        ),
    }
)

NEW_CN_PITCH = (
    "Hacker Week 自己去找 search ranker 在哪 silently failing -- "
    "dashboard 显示健康但 multi-intent query 比如 \"pokemon\" 90%+ "
    "返回 trading cards，而购买数据显示一半 buyer 要 games / toys / "
    "figures；abandon-log slice 发现上百个 high-volume query 同样 "
    "collapse，根因不在 per-item calibration 而在 ranker 按 item "
    "独立打分没有 page-level reasoning -- item-level scoring 本身 "
    "在生产 page-level homogeneity；一周内端到端搭出 diversity "
    "blending prototype (abandon-log pipeline + blending 算法 + "
    "实验框架)，用 purchase data 验证"
    " | KEY FACTS: 核心 insight -- item-level scoring creates "
    "page-level homogeneity"
    " | abandon-log slice 暴露 dashboard 看不见的 invisible half"
    " | Hacker Week 一周端到端 prototype"
    " | 200M+ annualized impact 多 vertical 复用; SIGIR 总结方法论"
    " | 核心 lesson: healthy metric 可能只在 measure 没被系统丢掉的那批用户"
)

# question_id (string) -> new relevance_note. Each rewritten to match BOTH
# the question's framing AND the new invisible-to-standard-metrics /
# root-cause-diagnosis / item-vs-page / self-initiated-direction vocabulary
# from the golden trait matrix.
RELEVANCE_NOTES: dict[str, str] = {
    "OWN-6": (
        "Bold risk: spent the full Hacker Week on a self-framed "
        "invisible-to-standard-metrics problem with no assignment and "
        "no guarantee the root-cause diagnosis would hold up."
    ),
    "INN-1": (
        "Identified a failure the dashboard couldn't see -- the "
        "dominant-intent users masked the abandoned half. Abandon-log "
        "slice surfaced the pattern standard metrics had been hiding."
    ),
    "INN-2": (
        "Entirely self-started: chose the problem, framed it as "
        "intent collapse, and shipped an end-to-end prototype (data "
        "pipeline + blending algorithm + experiment framework) inside "
        "one Hacker Week."
    ),
    "PS-15": (
        "Data-only diagnosis: abandon-log slice vs purchase-distribution "
        "slice revealed the invisible-half gap; no user interview, no "
        "ticket, just the two data views the dashboard wasn't joining."
    ),
    "PS-2": (
        "Creative move was the diagnosis, not the algorithm: named "
        "item-level scoring as the cause of page-level homogeneity so "
        "a cheap blending layer could fix it without rewriting "
        "holistic ranking."
    ),
    "IMP-2": (
        "Prioritized the invisible users: half of multi-intent-query "
        "buyers were getting a page that ignored them, and the "
        "dashboard rewarded the team for ignoring them back."
    ),
    "OWN-11": (
        "Owned a problem the org didn't know existed -- framed intent "
        "collapse, diagnosed item-vs-page, prototyped the fix; it "
        "compounded into a multi-year 200M+ annualized initiative."
    ),
    "OWN-9": (
        "Moved fast with incomplete information: one Hacker Week, no "
        "funded scope, no guarantee the item-vs-page diagnosis would "
        "survive review; shipped end-to-end prototype anyway."
    ),
    "INN-9": (
        "Complex-problem creativity was structural: cheap diversity-"
        "blending proxy on top of the existing ranker instead of "
        "rewriting holistic ranking -- the framing made the fix cheap."
    ),
    "INN-10": (
        "Innovation-from-questioning-metrics: asked why healthy-looking "
        "dashboards could coexist with unserved users; abandon-log slice "
        "answered it."
    ),
    "ADP-20": (
        "Self-directed curiosity: Hacker Week scope I defined myself, "
        "driven by the gap between healthy-looking standard metrics "
        "and the abandoned-query pattern nobody was slicing."
    ),
    "PS-11": (
        "Purchase-data slice vs display-data slice was the decision: "
        "one said \"ranker fine,\" the other said \"half the buyers "
        "unserved.\" The disagreement was the signal."
    ),
    "INN-8": (
        "Challenged the default: standard metrics said the system was "
        "healthy, I argued the metric was measuring only the users "
        "the system hadn't lost -- and proved it with abandon-log + "
        "purchase data."
    ),
    "INN-4": (
        "End-to-end diversity-blending prototype validated during "
        "Hacker Week; the methodology was later written up at SIGIR "
        "once the item-vs-page diagnosis was confirmed across "
        "verticals."
    ),
    "IMP-10": (
        "Long-term impact came from the diagnosis, not the prototype: "
        "\"item-level scoring creates page-level homogeneity\" became "
        "a reusable frame that grew a one-week prototype into a "
        "multi-year 200M+ initiative."
    ),
    "EXE-5": (
        "Deadline-tight end-to-end delivery in the Hacker Week window: "
        "abandon-log pipeline + diversity-blending algorithm + "
        "experiment framework, shipped as one working stack."
    ),
}


def main() -> int:
    """Apply the EX-01 rewrite + propagate to title/tags/pitch/relevance_notes."""
    if not DB.exists():
        print(f"[FAIL] db not found: {DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT example_id, title, situation FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()
    if row is None:
        print(f"[FAIL] row id={ROW_ID} not found", file=sys.stderr)
        conn.close()
        return 2

    ex_id, _current_title, current_situation = row
    if ex_id != EXAMPLE_ID:
        print(
            f"[FAIL] row id={ROW_ID} is example_id={ex_id}, expected {EXAMPLE_ID}",
            file=sys.stderr,
        )
        conn.close()
        return 3

    if current_situation and IDEMPOTENT_MARKER in current_situation:
        print(f"[SKIP] {EXAMPLE_ID} already rewritten (situation contains marker)")
        conn.close()
        return 0

    conn.close()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex01_rewrite")
    shutil.copy2(DB, backup)
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB))
    before = conn.execute(
        "SELECT length(situation), length(task), length(action), "
        "length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()

    conn.execute(
        "UPDATE behavioral_examples "
        "SET title = ?, situation = ?, task = ?, action = ?, result = ?, "
        "    risk_statement = ?, principle_tags = ?, "
        "    cn_elevator_pitch = ?, analogy = ?, tech_terms = ? "
        "WHERE id = ?",
        (
            NEW_TITLE,
            NEW_SITUATION,
            NEW_TASK,
            NEW_ACTION,
            NEW_RESULT,
            NEW_RISK,
            json.dumps(NEW_PRINCIPLE_TAGS),
            NEW_CN_PITCH,
            NEW_ANALOGY,
            NEW_TECH_TERMS,
            ROW_ID,
        ),
    )

    after = conn.execute(
        "SELECT length(situation), length(task), length(action), "
        "length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (ROW_ID,),
    ).fetchone()

    fields = ["situation", "task", "action", "result", "risk_statement"]
    print(f"[OK] {EXAMPLE_ID} (id={ROW_ID}) rewritten:")
    print(f"     title: {NEW_TITLE}")
    for f, b, a in zip(fields, before, after, strict=True):
        sign = "+" if a >= b else ""
        print(f"     {f:<16} {b:>5} -> {a:>5} chars ({sign}{a - b})")

    notes_updated = 0
    notes_missing: list[str] = []
    for qid, note in RELEVANCE_NOTES.items():
        q_row = conn.execute(
            "SELECT id FROM behavioral_questions WHERE question_id = ?",
            (qid,),
        ).fetchone()
        if q_row is None:
            notes_missing.append(qid)
            continue
        q_pk = q_row[0]
        cur = conn.execute(
            "UPDATE question_example_links "
            "SET relevance_note = ? "
            "WHERE question_id = ? AND example_id = ?",
            (note, q_pk, ROW_ID),
        )
        if cur.rowcount == 1:
            notes_updated += 1
        elif cur.rowcount == 0:
            notes_missing.append(f"{qid} (no link row)")
        else:
            notes_missing.append(f"{qid} (multi-row update: {cur.rowcount})")

    conn.commit()
    conn.close()

    print(f"[OK] {notes_updated}/{len(RELEVANCE_NOTES)} relevance_notes updated")
    if notes_missing:
        print(f"[WARN] missing/anomalous: {notes_missing}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
