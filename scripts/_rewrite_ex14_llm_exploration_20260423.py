"""Rewrite EX-14 (behavioral_examples.id=18) "LLM Exploration".

Replaces title/situation/task/action/result/risk_statement/principle_tags/
cn_elevator_pitch/analogy/tech_terms with a polished version matching the
golden EX-15/EX-17 voice (spoken-English rhythm, prose not bullets, sentence
fragments OK, no AI explainer mode).

Why the rewrite (red-flag scan against the old version):
- Bullet-form Action reads like an AI explainer rather than spoken English
- "Convinced manager to pivot from flashy agentic to pragmatic LLM-as-Judge"
  framed as a persuasion win -- masks the actual move (the 1-week ROI math
  that disqualified the agentic path before any prototype existed)
- LLM-as-Judge presented as an obvious pivot -- buries the scoping discipline
- Generic principle_tags (adaptability/innovation/problem_solving) miss the
  matrix-claimed facets (feasibility-first, no-precedent scoping, agentic-
  search-killed) that defend EX-14's primary roles in scope_creep_ambiguous
  and ambiguity_uncertainty themes
- Generic AI-quality-inspector analogy dilutes the kill-line
- tech_terms includes Krippendorff's alpha that is not in the new STAR

Boundary check vs T-P0-577 task spec (PRE-APPROVED FOR AUTORUN 2026-04-23):
PERMITTED: voice/length polish, principle_tag upgrade, cn_elevator_pitch
rewrite with KEY FACTS suffix, link relevance_note tightening, propagation
sync. NOT taken: no content-level reframe (the kill-then-pivot arc is the
existing arc, not a new beat), no new red-flag interpretation invented, no
dual-cut split, no fundamental outcome/lesson change. The new lesson
"Feasibility is the real authoring; pitch decks are downstream of it" is a
sharpened crystallization of the existing lesson, not a new one.

Idempotency: situation field starting with the new opener "In 2023,
leadership wanted to" indicates the rewrite is already applied. (The OLD
opener "In 2023, leadership wanted to 'upgrade to GenAI' for expert-like"
shares the prefix; we use a unique mid-sentence marker after that.)

Project convention (CLAUDE.md): every DB content row needs a git-tracked
idempotent seed script. This is the canonical source for EX-14 STAR + the
propagation surface (title/tags/pitch/relevance_notes). The cn_elevator_pitch
canonical upstream is `scripts/_batch2_cn_pitches.py` (line 40), edited
inline as part of this same change so re-running it produces the new pitch.
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
ROW_ID = 18
EXAMPLE_ID = "EX-14"

# Unique mid-sentence marker present only in the new situation opener.
IDEMPOTENT_MARKER = "but the brief was a hand wave"

NEW_TITLE = (
    "LLM Exploration --- Killing the Agentic Mandate with One Week of ROI Math"
)

NEW_SITUATION = (
    "In 2023, leadership wanted to \"upgrade to GenAI\" -- expert-like search "
    "experiences, agentic flows -- but the brief was a hand wave. I got a "
    "sandbox, some API credits, no requirements, no precedent in our "
    "production stack. Explore on your own."
)

NEW_TASK = (
    "Find a real, business-impactful LLM application -- but the bigger task "
    "underneath was scoping. Without a feasibility-first cut, the exploration "
    "would drift into the agentic search demo leadership half-imagined: "
    "high-visibility, weeks of prototype, then quietly deprioritized. The "
    "job was to disqualify the obvious path before sunk cost made it harder, "
    "then earn the budget to pursue the unglamorous one."
)

NEW_ACTION = (
    "First move: a 1-week feasibility study on the agentic path, framed as "
    "ROI math. LLM couldn't plug into the indexing pipeline. Couldn't read "
    "live inventory. Throughput maxed at tens of QPS against a 40K-peak "
    "surface; latency was prohibitive for real-time. The numbers killed the "
    "path before any prototype.\n\n"
    "That bought me the standing to push the harder argument: skip the "
    "headline demo, find the highest-value low-hanging fruit, use it to "
    "build org confidence in LLMs as a tool. The agentic version would be "
    "a pitch; this would be infrastructure.\n\n"
    "The fit was the relevance backlog -- severe mislabels, edge cases "
    "where human annotators themselves disagreed. LLM-as-Judge was cheap "
    "to operate, easy to audit, aimed at the surface where humans were "
    "already failing. The build hit three separate issues: inter-rater "
    "agreement low enough to invalidate AI-vs-human alignment as a metric, "
    "immature instruction-following (JSON failures, NSFW blocks), and an "
    "initial no-lift offline comparison I traced to dataset quality rather "
    "than model quality. Each was a separate diagnosis."
)

NEW_RESULT = (
    "LLM-as-Judge won across multiple relevance metrics, delivered GMB "
    "improvement, and lifted user engagement. It became the production "
    "measurement infrastructure for the team, then for ads, then for "
    "several other groups -- a solo exploration scaled into org-wide "
    "infra without ever shipping the demo leadership originally asked "
    "for.\n\n"
    "The lesson I carry: **the cheapest move in a vague AI mandate is the "
    "one nobody assigns -- disqualify the obvious path with a week of ROI "
    "math before sunk cost makes the kill politically expensive.** "
    "Feasibility is the real authoring; pitch decks are downstream of it."
)

NEW_RISK = (
    "Surface risk: I waste a quarter on the agentic demo, ship a video, "
    "leadership loses interest, exploration gets deprioritized, and the "
    "relevance backlog stays broken. The structural risk is harder. "
    "Without a feasibility-first cut at the start, every ambiguous mandate "
    "becomes a sunk-cost trap -- once the first prototype exists, the "
    "political cost of killing it grows faster than the evidence against "
    "it. Org-level: missing the GenAI window means competitors set the "
    "vocabulary for what AI in our domain looks like, and our team plays "
    "catch-up on someone else's frame.\n\n"
    "<!-- NRG-v1 --> NARRATION GUARD: This is a 'feasibility-first kill -> "
    "pragmatic pivot' story. The narration risk is jumping straight to "
    "LLM-as-Judge as if it were the obvious answer. Lead with the kill -- "
    "the 1-week ROI math against the agentic path, including the specific "
    "constraints (no indexing-pipeline integration, tens of QPS vs 40K "
    "peak, latency prohibitive for real-time). Only then introduce the "
    "pivot. The pivot needs the kill to land; without it, this sounds "
    "like \"I had a clever idea\" instead of \"I scoped through "
    "disqualification.\" If the interviewer cuts off after the feasibility "
    "cut, the standalone close is \"Feasibility is the real authoring; "
    "pitch decks are downstream of it.\""
)

NEW_PRINCIPLE_TAGS = [
    "adaptability",
    "ownership",
    "innovation",
    "feasibility_first",
    "no_precedent_scoping",
    "ROI_math_disqualification",
    "infrastructure_over_demo",
]

# Drop the generic AI-quality-inspector analogy -- the kill-line carries
# more weight without it. EX-15 and EX-17 both have analogy=None.
NEW_ANALOGY = None

# Drop Krippendorff (no longer in the STAR). Keep LLM-as-Judge + QPS.
NEW_TECH_TERMS = json.dumps(
    {
        "LLM-as-Judge": (
            "using a large language model to evaluate/label data quality "
            "instead of human annotators"
        ),
        "QPS": "queries per second",
    }
)

NEW_CN_PITCH = (
    "2023 年 leadership 要 'upgrade to GenAI'，给 sandbox + "
    "API credits 自己探，没有 requirements、没"
    "有 LLM precedent；先用 1 周 feasibility 把 "
    "agentic search 路径用 ROI math 杀掉 -- 不能"
    "接 indexing pipeline、tens of QPS vs 40K peak、latency "
    "不适合 real-time；换来 standing 推 manager "
    "跳过 headline demo 找 highest-value low-hanging fruit，"
    "落到 relevance backlog 上的 LLM-as-Judge -- 不是"
    "因为新颖，是因为 cheap to operate、"
    "easy to audit、瞄准人类 annotator 已经做"
    "不好的面"
    " | KEY FACTS: 1 周 ROI math 杀 agentic"
    " | 不接 indexing pipeline + tens of QPS vs 40K peak"
    " | LLM-as-Judge 挂到 relevance backlog"
    " | solo exploration -> 多团队 production measurement infra"
    " | 核心 lesson: feasibility 才是 real authoring"
)

# question_id (string) -> new relevance_note. Each rewritten to match BOTH
# the question's framing AND the new feasibility-first / ROI-math-kill /
# infrastructure-over-demo facet vocabulary from
# docs/bq_golden_trait_matrix.md.
RELEVANCE_NOTES: dict[str, str] = {
    "ADP-1": (
        "1-week ROI-math feasibility study scoped a no-precedent GenAI "
        "mandate -- learned the LLM stack via disqualification, not tutorials."
    ),
    "ADP-4": (
        "Killed the agentic-search path with 1-week feasibility math, "
        "pivoted to LLM-as-Judge against the relevance backlog."
    ),
    "ADP-6": (
        "No requirements, no LLM precedent in our stack -- scoped through "
        "feasibility math rather than brainstorming."
    ),
    "ADP-7": (
        "Vague AI mandate had no requirements -- substituted feasibility "
        "analysis for the missing requirements."
    ),
    "ADP-8": (
        "Made the agentic-search disqualification call from QPS, latency, "
        "and integration numbers alone, before any prototype existed."
    ),
    "ADP-10": (
        "Built a 1-week structured feasibility on the obvious path before "
        "committing to any LLM application."
    ),
    "COM-2": (
        "Walked manager off the agentic-search headline path using ROI "
        "math, not vision -- pivot was an infrastructure argument, not a "
        "pitch."
    ),
    "EXE-4": (
        "Took the LLM industry hype as input but applied feasibility math "
        "to disqualify the headline application before chasing it."
    ),
    "IMP-4": (
        "Solo LLM-as-Judge exploration scaled into org-wide measurement "
        "infrastructure adopted by ads and several other teams."
    ),
    "INN-3": (
        "Picked LLM-as-Judge over agentic search by feasibility-first "
        "scoping -- ROI math chose the experiment, not novelty."
    ),
    "INN-4": (
        "LLM-as-Judge for relevance labeling -- the move wasn't the "
        "technique, it was the pivot away from agentic search to it."
    ),
    "INN-6": (
        "LLM-as-Judge became production measurement infrastructure adopted "
        "by ads and several other teams."
    ),
    "PS-2": (
        "Disqualified the headline agentic-search path with ROI math, "
        "then found low-hanging fruit at the relevance backlog -- "
        "creativity in scoping, not in building."
    ),
}


def main() -> int:
    """Apply the EX-14 rewrite + propagate to title/tags/pitch/relevance_notes."""
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

    ex_id, current_title, current_situation = row
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
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex14_rewrite")
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
