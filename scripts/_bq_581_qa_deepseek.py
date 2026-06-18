"""T-P1-581 BQ-DEPTH-10: DeepSeek QA pass over the top-40 primary-story draft.

One-off (prefix ``_``) QA tool, NOT a DB writer. It:
  1. Holds the Claude-drafted 40 assignments (question_id -> primary example).
  2. Pulls full per-question context from the live DB (question text + every
     linked candidate example with its title + cn_elevator_pitch).
  3. Asks DeepSeek (temperature 0, judgment mode) to judge each row:
     keep / swap (-> suggested example) / flag, with a one-line reason.
  4. Writes docs/bq_primary_story_assignments_20260421.md (human review doc, with
     the DeepSeek verdict column) + a machine-readable JSON sidecar the seed
     script consumes after user approval.

The primary candidate for each row MUST be an existing link for that question
(is_primary is set ON a link row), so a swap suggestion is only honored if the
suggested example is also already linked to the same question.

Run from a SUPERVISED session (it needs scripts/lib/.env.deepseek):
  PYTHONUTF8=1 /c/Anaconda/python.exe scripts/_bq_581_qa_deepseek.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import deepseek_creds  # noqa: E402

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "bq_primary_story_assignments_20260421.md"
)
SIDECAR_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "bq_primary_story_assignments_20260421.deepseek.json"
)

# --- Claude-drafted 40 assignments: (question_id, primary_example_id, rationale) ---
# Selection = top-40 high-probability BQ questions (company overlap + asked
# frequency intuition), spanning all 9 categories. Primary chosen from each
# question's already-linked examples, guided by docs/bq_golden_trait_matrix.md.
ASSIGNMENTS: list[tuple[str, str, str]] = [
    # ownership (5)
    ("OWN-1", "EX-15", "On-call-caused deprecation incident: ran the scan, missed the pipelines, absorbed the rollback personally, then converted it into an ownership-transfer governance pattern -- complete end-to-end ownership of a failure."),
    ("OWN-2", "EX-23", "NYC large-scale launch under a hard 2-week/1-month deadline: the cleanest above-and-beyond delivery-under-pressure arc (sole linked story)."),
    ("OWN-6", "EX-16", "Cross-DC same-day solo rollout + recovery: a genuinely bold operational risk owned end-to-end (manager couldn't get PD quota, went solo)."),
    ("OWN-8", "EX-30", "Moving fast and made a mistake: the hash-capability misdesign shipped and the orphan-capability leak was mine -- the canonical move-fast-broke-something ownership story."),
    ("OWN-11", "EX-02", "Took ownership of a challenging problem by relocating teams -- 'the problem follows the person'; the matrix's ownership_accountability primary."),
    # adaptability (6)
    ("ADP-5", "EX-30", "Made a mistake: domain-depth-is-not-design-authority post-mortem; matrix failure_setback primary (already set)."),
    ("ADP-19", "EX-17", "Most challenging feedback: senior-IC reliance-vs-trust, declined the air-cover so trust reset directly with the reviewer (already set)."),
    ("ADP-11", "EX-15", "Major setback overcome: the deprecation rollback, recovered within a week and reframed into a lasting governance change."),
    ("ADP-10", "EX-14", "Plan in a highly ambiguous situation: no-precedent GenAI mandate scoped via a 1-week feasibility study instead of brainstorming; matrix ambiguity primary."),
    ("ADP-1", "EX-14", "Quickly learn a new technology: learned LLM/GenAI from a standing start and turned it into reusable LLM-as-Judge evaluation infra."),
    ("ADP-15", "EX-33B", "Biggest lesson from a failed project: MoE over-iteration -- a model-believer's humility lesson from a project that did NOT ship."),
    # impact (4)
    ("IMP-11", "EX-20", "Ethical dilemma: seller-risk fairness escalation (new sellers trapped by zero-history = high-risk); the stable ethics anchor story."),
    ("IMP-2", "EX-01", "Prioritized user experience: intent-collapse diagnosis fixed a UX harm invisible to the standard dashboard metrics."),
    ("IMP-3", "EX-21", "Tech debt vs feature delivery: the declarative-artifactory tech-debt balance (sole linked debt story)."),
    ("IMP-10", "EX-06", "Long-term value: the allocation framework built as a reusable platform primitive rather than a one-off win."),
    # innovation (4)
    ("INN-4", "EX-09", "Implemented an innovative solution: the conversational-search proxy-item breakthrough that maximized reuse of existing infra."),
    ("INN-2", "EX-01", "Started an idea on my own: self-initiated Hacker Week search-diversity prototype (sole linked story)."),
    ("INN-8", "EX-33", "Questioned a traditional approach: named the ceiling of pairwise ranking and drove the MoE->allocation paradigm shift; matrix leadership_direction primary."),
    ("INN-5", "EX-12B", "Improved an inefficient process: notebook->ML-platform migration that lifted team utilization off a <5% baseline."),
    # problem_solving (6)
    ("PS-1", "EX-05", "Difficult technical decision: relevance-filtering deployment-feasibility tradeoff under a hard latency budget (two of three paths failed)."),
    ("PS-6", "EX-16", "Calculated risk: cross-DC same-day rollout, named the risk and the counterpart-bandwidth line-item (already set)."),
    ("PS-11", "EX-01", "Used data to make a key decision: the abandon-log slice exposed intent collapse the dashboard masked; matrix data_analysis primary."),
    ("PS-2", "EX-09", "Solved a problem creatively: proxy-item generation as a creative bridge across the LLM-search adaptation gap."),
    ("PS-4", "EX-03", "Analyzed a complex problem: first-principles retake of the challenging-sale NDCG proxy (GMB calibration trap)."),
    ("PS-10", "EX-05", "Tough trade-off: the deployment-feasibility cut is a clean cost-vs-quality tradeoff arc (sole linked story)."),
    # execution (4)
    ("EXE-5", "EX-23", "Managed a large-scale project: the NYC tight-deadline cross-org launch end-to-end (30+ people)."),
    ("EXE-3", "EX-05", "Complex technical problem solved: the relevance-filtering deployment under latency budget (sole linked story)."),
    ("EXE-9", "EX-33B", "Major project setback: MoE deprecated / did-not-ship is a real, owned setback on the project card."),
    ("EXE-13", "EX-21", "Balance immediate vs longer-term: tech-debt-vs-feature is the canonical immediate-vs-long-term execution tradeoff."),
    # leadership (4)
    ("LDR-1", "EX-12", "Coached/mentored someone: helped PhD interns move from notebook to production with a reusable template."),
    ("LDR-3", "EX-13", "Tough call as a leader: the authorship dispute, held the contribution-based norm through manager mediation."),
    ("LDR-6", "EX-22", "Delegate vs handle yourself: handed the hashing-algorithm decision to the researcher, shifting from designer to quality gatekeeper."),
    ("LDR-2", "EX-11", "Performance issues with a junior: coached an intern through an overpromise / goal-visibility perception gap."),
    # collaboration (4)
    ("COL-1", "EX-13", "Disagreed with a team member: the authorship conflict resolved by principle + mediation; matrix conflict_disagreement primary."),
    ("COL-3", "BLOG-03", "Cross-functional team: cross-org boundary defense via the LLM relevance pipeline, partnering across orgs on the real need."),
    ("COL-5", "EX-33", "Align teams/stakeholders on a shared goal: the MoE->allocation org-level reframe aligned the org on a new paradigm."),
    ("COL-6", "EX-24", "Communicate a complex technical concept to a stakeholder: explained ranking as zero-sum allocation to a VP, conclusion-first."),
    # communication (3)
    ("COM-1", "EX-19", "Explain technical to non-technical: explained an A/B-test confounder (mixed treated/untreated sellers) to a PM with a concrete analogy."),
    ("COM-2", "EX-14", "Persuade others to change direction: talked leadership out of the agentic-search mandate with one week of ROI math (the highest-link persuasion question)."),
    ("COM-3", "EX-08", "Deliver bad news: surfaced a slow search-baseline degradation no one had noticed and escalated module arbitration to a VP."),
]

JUDGE_SYSTEM = (
    "You are a senior FAANG behavioral-interview coach doing QA on a candidate's "
    "primary-story assignments. For a given behavioral question and a set of "
    "candidate STAR stories (all already linked to that question), judge whether "
    "the candidate's CHOSEN primary story is the single best one to lead with. "
    "Consider: does the story directly answer THIS question's intent? STAR "
    "completeness? Is there a clearly better-fitting story among the other "
    "candidates? Respond ONLY with a compact JSON object, no prose, no markdown "
    'fences: {"verdict": "keep"|"swap"|"flag", "suggested_example_id": '
    '"<id or null>", "reason": "<=30 words>"}. '
    "Use 'swap' ONLY if another listed candidate is clearly better (put its id in "
    "suggested_example_id). Use 'flag' if the choice is defensible but you have a "
    "caveat the candidate should know. Use 'keep' if the choice is the best "
    "available. The reason may be in Chinese or English."
)


def _conn() -> sqlite3.Connection:
    """Open the live DB read-only-ish connection."""
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def _load_context(c: sqlite3.Connection) -> dict[str, dict]:
    """Build {question_id: {text, category, candidates:[{example_id,title,pitch}]}}."""
    q_by_code: dict[str, dict] = {}
    for q in c.execute(
        "SELECT id, question_id, text, category_name FROM behavioral_questions"
    ):
        q_by_code[q["question_id"]] = {
            "row_id": q["id"],
            "text": q["text"],
            "category": q["category_name"],
            "candidates": [],
        }
    rows = c.execute(
        """SELECT q.question_id AS qcode, e.example_id AS ecode, e.title AS title,
                  e.cn_elevator_pitch AS pitch, e.result AS result
           FROM question_example_links l
           JOIN behavioral_questions q ON l.question_id = q.id
           JOIN behavioral_examples e ON l.example_id = e.id"""
    )
    for r in rows:
        if r["qcode"] in q_by_code:
            pitch = (r["pitch"] or r["result"] or "").strip().replace("\n", " ")
            q_by_code[r["qcode"]]["candidates"].append(
                {"example_id": r["ecode"], "title": r["title"], "pitch": pitch[:280]}
            )
    return q_by_code


def _judge_row(cli, model: str, qctx: dict, chosen: str) -> dict:
    """Run one DeepSeek judgment call for a single (question, chosen primary)."""
    cand_lines = []
    for cand in qctx["candidates"]:
        mark = " <-- CANDIDATE'S CHOICE" if cand["example_id"] == chosen else ""
        cand_lines.append(
            f"- {cand['example_id']} | {cand['title']}{mark}\n    {cand['pitch']}"
        )
    user = (
        f"QUESTION ({qctx['category']}): {qctx['text']}\n\n"
        f"CANDIDATE STORIES (all already linked to this question):\n"
        + "\n".join(cand_lines)
        + f"\n\nThe candidate chose {chosen} as the primary. Judge it."
    )
    resp = cli.chat.completions.create(
        model=model,
        temperature=0,
        # deepseek-v4-pro is a reasoning model: reasoning_tokens consume the
        # budget before any content is emitted, so a small cap truncates the
        # JSON to empty. Give ample headroom (lesson: token_limits).
        max_tokens=3000,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    raw = (resp.choices[0].message.content or "").strip()
    # tolerate accidental ```json fences
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        out = json.loads(raw)
    except json.JSONDecodeError:
        out = {"verdict": "flag", "suggested_example_id": None,
               "reason": f"UNPARSEABLE: {raw[:120]}"}
    return out


def main() -> int:
    """Run the QA pass and emit the assignments doc + JSON sidecar."""
    from openai import OpenAI

    creds = deepseek_creds.load()
    print(f"[581-QA] DeepSeek creds: {creds!r}")
    cli = OpenAI(api_key=creds.key, base_url=creds.base_url)

    c = _conn()
    ctx = _load_context(c)

    # Validate every chosen primary is an existing link.
    errors = []
    for qcode, chosen, _ in ASSIGNMENTS:
        if qcode not in ctx:
            errors.append(f"{qcode}: question not in DB")
            continue
        cand_ids = {x["example_id"] for x in ctx[qcode]["candidates"]}
        if chosen not in cand_ids:
            errors.append(f"{qcode}: chosen {chosen} not linked (links: {sorted(cand_ids)})")
    if errors:
        print("[581-QA] PREFLIGHT FAILED -- chosen primary must be an existing link:")
        for e in errors:
            print("   ", e)
        return 2
    print(f"[581-QA] preflight OK: all {len(ASSIGNMENTS)} chosen primaries are linked.")

    results = []
    for i, (qcode, chosen, rationale) in enumerate(ASSIGNMENTS, 1):
        verdict = _judge_row(cli, creds.model, ctx[qcode], chosen)
        sug = verdict.get("suggested_example_id")
        # a swap suggestion is only valid if the suggested example is also linked
        valid_swap = False
        if verdict.get("verdict") == "swap" and sug:
            cand_ids = {x["example_id"] for x in ctx[qcode]["candidates"]}
            valid_swap = sug in cand_ids and sug != chosen
        results.append({
            "question_id": qcode,
            "question_text": ctx[qcode]["text"],
            "category": ctx[qcode]["category"],
            "claude_primary": chosen,
            "rationale": rationale,
            "deepseek_verdict": verdict.get("verdict", "flag"),
            "deepseek_suggested": sug,
            "deepseek_swap_valid": valid_swap,
            "deepseek_reason": verdict.get("reason", ""),
        })
        print(f"  [{i:2}/40] {qcode:7} chose {chosen:8} -> {verdict.get('verdict'):4}"
              f" {('=> '+str(sug)) if sug else ''}  {verdict.get('reason','')[:60]}")

    SIDECAR_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[581-QA] wrote sidecar -> {SIDECAR_PATH}")

    _write_doc(results)
    print(f"[581-QA] wrote doc -> {DOC_PATH}")

    n_keep = sum(1 for r in results if r["deepseek_verdict"] == "keep")
    n_swap = sum(1 for r in results if r["deepseek_verdict"] == "swap")
    n_flag = sum(1 for r in results if r["deepseek_verdict"] == "flag")
    print(f"[581-QA] DeepSeek: keep={n_keep} swap={n_swap} flag={n_flag}")
    return 0


def _write_doc(results: list[dict]) -> None:
    """Render the human-review assignments doc (markdown)."""
    lines: list[str] = []
    lines.append("# BQ-DEPTH-10 (T-P1-581) -- Top-40 Primary-Story Assignments")
    lines.append("")
    lines.append("> **Status: AWAITING USER APPROVAL before DB write.** Each row sets")
    lines.append("> `question_example_links.is_primary=1` for the chosen (question, example)")
    lines.append("> pair. The partial unique index `ux_qel_primary_per_question` guarantees")
    lines.append("> at most one primary per question.")
    lines.append(">")
    lines.append("> **Flow** (human-as-verifier): Claude drafted the 40 -> DeepSeek QA judged")
    lines.append("> each (keep / swap / flag) -> **you approve** -> idempotent `.bak`-guarded seed.")
    lines.append(">")
    lines.append("> Selection = top-40 high-probability questions (company overlap + asked")
    lines.append("> frequency) across all 9 categories; each primary chosen from that question's")
    lines.append("> already-linked candidates, guided by `docs/bq_golden_trait_matrix.md`.")
    lines.append("")
    n_keep = sum(1 for r in results if r["deepseek_verdict"] == "keep")
    n_swap = sum(1 for r in results if r["deepseek_verdict"] == "swap")
    n_flag = sum(1 for r in results if r["deepseek_verdict"] == "flag")
    lines.append(f"**DeepSeek QA summary:** keep={n_keep}, swap={n_swap}, flag={n_flag} "
                 f"(model `deepseek-v4-pro`, temperature 0).")
    lines.append("")
    lines.append("| # | Question | Claude primary | DeepSeek | DeepSeek note |")
    lines.append("|---|----------|----------------|----------|---------------|")
    for i, r in enumerate(results, 1):
        v = r["deepseek_verdict"]
        badge = {"keep": "KEEP", "swap": "SWAP", "flag": "FLAG"}.get(v, v.upper())
        if v == "swap" and r["deepseek_suggested"]:
            valid = "" if r["deepseek_swap_valid"] else " (NOT LINKED - reject)"
            badge += f" -> {r['deepseek_suggested']}{valid}"
        qtext = r["question_text"].replace("|", "\\|")
        note = (r["deepseek_reason"] or "").replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {i} | **{r['question_id']}** {qtext} | `{r['claude_primary']}` "
            f"| {badge} | {note} |"
        )
    lines.append("")
    lines.append("## Per-row rationale (Claude)")
    lines.append("")
    for r in results:
        lines.append(f"- **{r['question_id']} -> `{r['claude_primary']}`** "
                     f"({r['category']}): {r['rationale']}")
    lines.append("")
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
