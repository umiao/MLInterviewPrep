"""Rewrite EX-02 (behavioral_examples.id=2) "Overcoming Manager Resistance
via Proactive Team Transfer" -> "Diversity Ranking --- Moving the Problem to
Its Right Home".

Replaces title/situation/task/action/result/risk_statement/principle_tags/
cn_elevator_pitch/analogy/tech_terms with a polished version matching the
golden EX-15/EX-17/EX-14 voice (spoken-English rhythm, prose not bullets,
sentence fragments OK, no AI explainer mode).

Why the rewrite (red-flag scan against the old version):
- Bullet-form Action reads like an AI explainer rather than spoken English
- Title "Overcoming Manager Resistance via Proactive Team Transfer" frames
  the manager as antagonist -- masks the actual move (structural relocation
  call based on charter/OKR mismatch, not interpersonal persuasion)
- "After winning Hacker Week" has a brag undertone; the signal is the
  stalled-project + charter-mismatch, not the win
- Old Action omits the pre-negotiation with Final Ranking team lead before
  the transfer went up -- a key move that turned a cold org ask into a warm
  sponsor. Without it, the story reads as "I quit and found a new team"
  rather than "I landed a warm sponsor before the formal request."
- Generic principle_tags (ownership/adaptability/leadership) miss the
  matrix-claimed primary facet `ownership-follows-person : transferred
  teams to own the problem rather than accept structural constraint`
- cn_elevator_pitch lacks a KEY FACTS suffix matching the fresh
  EX-14/EX-15 golden pattern

Boundary check vs T-P0-576 task spec (PRE-APPROVED FOR AUTORUN 2026-04-23):
PERMITTED: voice/length polish, principle_tag upgrade, cn_elevator_pitch
rewrite with KEY FACTS suffix, link relevance_note tightening, propagation
sync. NOT taken: no content-level reframe (the charter-mismatch-then-
relocate arc is the existing arc, not a new beat), no new red-flag
interpretation invented, no dual-cut split, no fundamental outcome/lesson
change. The new lesson "the problem follows the person, not the org chart"
is the existing lesson (the current Result already has "problem follows
the person"); the rewrite sharpens it and the NRG-v1 makes the structural-
not-interpersonal framing explicit.

Idempotency: situation field starting with the new opener "After Hacker
Week I had a working diversity-ranking prototype" indicates the rewrite is
already applied. We use a unique mid-sentence marker ("a working diversity-
ranking prototype") not present in the current opener ("After winning
Hacker Week, my diversity ranking project stalled").

Project convention (CLAUDE.md): every DB content row needs a git-tracked
idempotent seed script. This is the canonical source for EX-02 STAR + the
propagation surface (title/tags/pitch/relevance_notes). The cn_elevator_
pitch canonical upstream is `scripts/_batch1_cn_pitches.py` (line 49),
edited inline as part of this same change so re-running it produces the
new pitch.
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
ROW_ID = 2
EXAMPLE_ID = "EX-02"

# Unique mid-sentence marker present only in the new situation opener.
# The current (old) situation starts with "After winning Hacker Week, my
# diversity ranking project stalled"; this marker is absent there.
IDEMPOTENT_MARKER = "a working diversity-ranking prototype"

NEW_TITLE = (
    "Diversity Ranking --- Moving the Problem to Its Right Home"
)

NEW_SITUATION = (
    "After Hacker Week I had a working diversity-ranking prototype -- "
    "200M+ GMB opportunity on multi-intent queries the existing "
    "dashboards missed. My manager judged it out of scope. Our relevance "
    "team's charter was filtering thresholds, not ranking allocation. "
    "No experiment slots, no resources, project about to die."
)

NEW_TASK = (
    "Not: argue harder. The mismatch was structural -- a ranking problem "
    "sitting inside a relevance team whose OKRs measured precision and "
    "recall against filtering thresholds, not allocation across intents. "
    "No amount of reframing would change what the team was actually "
    "measured on. The real task was to decide whether to relocate the "
    "problem to a charter that fit, knowing the transfer would cost "
    "political capital and rebuild time, and to move it without burning "
    "the bridge behind me."
)

NEW_ACTION = (
    "First I tried the soft move. Reframed the project in relevance-"
    "threshold language -- if I could make it fit the existing OKRs, "
    "nobody had to move. It didn't fit. The team was measured on "
    "filtering; the work was an allocation problem wearing a relevance "
    "hat.\n\n"
    "The failure was the signal, not a setback. The next move was "
    "structural: find the team whose charter already covers allocation, "
    "and make the transfer the clean way.\n\n"
    "I went to the Final Ranking team's lead before formally raising "
    "the transfer. Walked them through diversity as intent-aware slot "
    "allocation in the final-ranking stage -- so they saw it on their "
    "own charter, not as an import from someone else's team. By the "
    "time the transfer request went up the chain, I already had a "
    "sponsor inside the receiving team, not a cold ask.\n\n"
    "I also named my own gap to my manager upfront: I should have "
    "translated the business case into OKR language before Hacker Week, "
    "not after, and found a ranking-team sponsor in advance instead of "
    "discovering the charter mismatch post-prototype. That ack kept the "
    "conversation structural instead of adversarial. I left cleanly -- "
    "no skip-level, no hero narrative -- because a clean exit is what "
    "protects the next cross-team move anyone tries."
)

NEW_RESULT = (
    "First experiment in the new team delivered +1% GMB. The allocation "
    "framework was reused across multiple verticals and compounded into "
    "200M+ annualized impact -- the idea survived the move and scaled "
    "well beyond the original scope.\n\n"
    "The lesson I carry: **when organizational structure blocks a "
    "validated idea, the cheapest move is to relocate the idea, not to "
    "keep arguing about whether the structure is wrong.** The problem "
    "follows the person, not the org chart. Now before any new project "
    "I pressure-test it against the receiving team's OKR language up "
    "front; if the language doesn't fit, that's a day-zero scoping "
    "issue, not a post-prototype one."
)

NEW_RISK = (
    "Surface risk: manager refuses the transfer, project dies in place, "
    "the 200M+ opportunity stays on the floor. The structural risk is "
    "worse. Kept arguing inside the relevance charter and I'd have "
    "burned credit persuading a team to measure something they weren't "
    "set up to measure, and exited on bad terms -- the next engineer "
    "trying a cross-charter move would inherit my scars. Org-level: the "
    "whole class of 'validated-but-homeless' projects dies quietly when "
    "nobody pays the political cost of relocating them; charter "
    "mismatches get rationalized as \"not the right time\" and the org "
    "stops producing them.\n\n"
    "<!-- NRG-v1 --> NARRATION GUARD: This is a 'structural-relocation, "
    "not interpersonal-conflict' story. The narration risk is making "
    "the manager the antagonist (\"my manager wouldn't let me do it\"). "
    "Lead with the charter mismatch -- ranking problem inside a "
    "relevance team whose OKRs measured filtering, not allocation. Two "
    "beats must land before the outcome: (1) the soft reframe tried "
    "and failed because OKRs are what a team is measured on, not what "
    "they can aspire to; (2) I pre-negotiated with the receiving "
    "team's lead before the transfer went up -- turning a cold org "
    "move into a warm sponsor. If the interviewer cuts off mid-story, "
    "the standalone close is \"The problem follows the person, not the "
    "org chart -- relocate the idea instead of arguing about whether "
    "the structure is wrong.\""
)

NEW_PRINCIPLE_TAGS = [
    "ownership",
    "adaptability",
    "leadership",
    "structural_relocation",
    "problem_follows_person",
    "preemptive_sponsorship",
    "OKR_language_discipline",
    "clean_exit_protects_future_moves",
]

# Drop any analogy -- the golden EX-14/EX-15/EX-17 all have analogy=None.
# The "problem follows the person" line carries more weight standalone.
NEW_ANALOGY = None

# Minimal tech_terms: the story is organizational, not technical. Two
# abbreviations the narration uses earn a gloss; the rest is prose.
NEW_TECH_TERMS = json.dumps(
    {
        "GMB": (
            "Gross Merchandise Bought -- the dollar value of purchases, "
            "the key business metric for search ranking quality"
        ),
        "OKR": (
            "Objectives and Key Results -- the framework used to set and "
            "measure team-level goals; charter mismatch often shows up as "
            "an OKR-language mismatch first"
        ),
    }
)

NEW_CN_PITCH = (
    "Hacker Week 做出 diversity ranking prototype -- "
    "200M+ GMB opportunity 但 manager 判 out of scope，"
    "team charter 是 relevance filtering thresholds 而不是 "
    "ranking allocation，OKRs 结构上对不上；先试 soft "
    "reframe 把 project 包装进 relevance 语言，失败 -- "
    "OKRs 是 team 被 measure 的东西，不是 aspire 的东西；"
    "做了 structural call 转到 Final Ranking team，把 "
    "diversity 重新定义成 intent-aware slot allocation；"
    "正式申请前先和 receiving team lead 预谈，cold 转组 "
    "变成 warm sponsor；对前 manager 也 name 了自己的 "
    "gap -- 应该在 Hacker Week 之前就把 business case "
    "translate 成 OKR 语言"
    " | KEY FACTS: structural call 而非 political win"
    " | soft reframe 失败是信号不是 setback"
    " | 转组前先预谈 receiving team lead"
    " | +1% GMB 首次实验 -> 200M+ annualized impact"
    " | 核心 lesson: problem follows the person, not the org chart"
)

# question_id (string) -> new relevance_note. Each rewritten to match BOTH
# the question's framing AND the new structural-relocation /
# problem-follows-person / OKR-language-discipline / preemptive-sponsorship
# facet vocabulary from docs/bq_golden_trait_matrix.md.
RELEVANCE_NOTES: dict[str, str] = {
    "ADP-14": (
        "Charter-mismatch roadblock -- ranking problem in a relevance "
        "team's scope. Tried the soft reframe first, then made the "
        "structural call to relocate instead of arguing harder."
    ),
    "ADP-17": (
        "Own-gap ack upfront: should have translated business case into "
        "OKR language and secured a ranking-team sponsor before Hacker "
        "Week, not after the prototype."
    ),
    "ADP-4": (
        "Soft reframe inside the team's charter failed because OKRs are "
        "what a team is measured on, not what they aspire to -- switched "
        "to structural relocation."
    ),
    "COL-3": (
        "Pre-negotiated with Final Ranking team's lead before the "
        "transfer went up -- cold ask became warm sponsor; allocation "
        "framework later reused across multiple verticals."
    ),
    "COL-5": (
        "Reframed diversity as an intent-aware slot-allocation problem "
        "so it mapped to the receiving team's charter -- alignment "
        "through re-language, not persuasion."
    ),
    "COM-2": (
        "Walked the receiving team's lead through diversity-as-"
        "allocation in their own charter language before the transfer "
        "request went up -- a structural sell, not a vision pitch."
    ),
    "OWN-11": (
        "Structural-relocation ownership -- moved the problem to the "
        "charter that fit rather than waiting for the charter to change."
    ),
    "OWN-7": (
        "Resilience as a structural call -- cut the losing argument "
        "inside the relevance charter, relocated the problem cleanly; "
        "problem follows the person, not the org chart."
    ),
}


def main() -> int:
    """Apply the EX-02 rewrite + propagate to title/tags/pitch/relevance_notes."""
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
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex02_rewrite")
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
