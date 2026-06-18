"""T-P1-581 BQ-DEPTH-10 seed: set is_primary=1 for the top-40 BQ questions.

Source of truth (Invariant 3) for the primary-story flags. Idempotent,
DB-backup-guarded, and dry-run by default. The DB write happens ONLY with
``--apply`` and ONLY after the user has approved the 40 assignments (the
human-as-verifier gate; see docs/bq_primary_story_assignments_20260421.md).

Each row sets ``question_example_links.is_primary=1`` for exactly one (question,
example) pair. The partial unique index ``ux_qel_primary_per_question`` (WHERE
is_primary=1) allows at most one primary per question, so before flagging the
chosen link we clear is_primary on any sibling link of the same question.

The FINAL pick per row = Claude draft -> DeepSeek QA (keep/swap/flag) -> Claude
accept-default review. The full review record lives in ROWS below and is rendered
into the human-review doc via ``--doc``.

Usage (supervised session):
  PYTHONUTF8=1 /c/Anaconda/python.exe scripts/seed_bq_primary_flags_20260421.py          # dry-run plan
  PYTHONUTF8=1 /c/Anaconda/python.exe scripts/seed_bq_primary_flags_20260421.py --doc    # regen review doc
  PYTHONUTF8=1 /c/Anaconda/python.exe scripts/seed_bq_primary_flags_20260421.py --apply  # write DB (post-approval)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = _ROOT / "data" / "mle_prep.db"
DOC_PATH = _ROOT / "docs" / "bq_primary_story_assignments_20260421.md"
AUDIT_DIR = _ROOT / "logs"

# Each row: question_id, category, final primary, Claude draft, DeepSeek verdict,
# DeepSeek suggested (if swap), DeepSeek reason, Claude decision note.
# decision: "keep" (no DeepSeek change), "accept-swap" (took DeepSeek's swap),
# "override" (kept draft against DeepSeek swap/flag, with reason).
ROWS: list[dict] = [
    # ---- ownership ----
    {"q": "OWN-1", "cat": "ownership", "final": "EX-15", "draft": "EX-15",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Personal failure with clear ownership taken end-to-end.",
     "note": "Matrix oncall/ownership anchor; already the existing primary."},
    {"q": "OWN-2", "cat": "ownership", "final": "EX-23", "draft": "EX-23",
     "ds": "flag", "ds_sug": None, "decision": "keep",
     "ds_reason": "Story leans problem-solving over extra-effort-for-deadline; emphasize how analysis averted delay.",
     "note": "Sole linked story; the flag is a delivery tip, not a swap. Keep."},
    {"q": "OWN-6", "cat": "ownership", "final": "EX-33", "draft": "EX-16",
     "ds": "swap", "ds_sug": "EX-33", "decision": "accept-swap",
     "ds_reason": "EX-16 is reactive risk; EX-33 is a deliberate chosen risk (gave up carry-over protection) -- better fits 'bold risk'.",
     "note": "Accept: EX-33 is a stronger deliberate bold-risk AND frees EX-16 to be PS-6's calculated-risk (removes the OWN-6/PS-6 duplicate)."},
    {"q": "OWN-8", "cat": "ownership", "final": "EX-30", "draft": "EX-30",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Directly answers moving fast + making a mistake with clear ownership.",
     "note": "Canonical move-fast-broke-it ownership story."},
    {"q": "OWN-11", "cat": "ownership", "final": "EX-02", "draft": "EX-02",
     "ds": "swap", "ds_sug": "EX-01", "decision": "override",
     "ds_reason": "EX-01 shows direct personal ownership of diagnosing+solving a silent search issue.",
     "note": "Override: matrix designates EX-02 ('problem follows the person') as the ownership_accountability primary; EX-01 already leads IMP-2/INN-2/PS-11."},
    # ---- adaptability ----
    {"q": "ADP-5", "cat": "adaptability", "final": "EX-30", "draft": "EX-30",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Directly addresses a personal design mistake and the handling.",
     "note": "Matrix failure_setback primary; already the existing primary."},
    {"q": "ADP-19", "cat": "adaptability", "final": "EX-17", "draft": "EX-17",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Only story provided; directly addresses receiving challenging feedback.",
     "note": "Already the existing primary; matrix reliance-vs-trust anchor."},
    {"q": "ADP-11", "cat": "adaptability", "final": "EX-15", "draft": "EX-15",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Sole option; full STAR of a major setback and its recovery.",
     "note": "Recovered-within-a-week-then-reformed arc."},
    {"q": "ADP-10", "cat": "adaptability", "final": "EX-14", "draft": "EX-14",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Shows building a data-driven feasibility plan under a no-precedent mandate.",
     "note": "Matrix ambiguity primary."},
    {"q": "ADP-1", "cat": "adaptability", "final": "EX-14", "draft": "EX-14",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Directly demonstrates rapidly learning GenAI in a week.",
     "note": "Learn-new-tech facet of EX-14."},
    {"q": "ADP-15", "cat": "adaptability", "final": "EX-33B", "draft": "EX-33B",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Clear failure with a strong personal KPI-humility lesson.",
     "note": "Lesson-from-a-project-that-did-not-ship."},
    # ---- impact ----
    {"q": "IMP-11", "cat": "impact", "final": "EX-20", "draft": "EX-20",
     "ds": "swap", "ds_sug": "EX-34", "decision": "override",
     "ds_reason": "EX-34 shows an ethical dilemma via personal conflict with a superior.",
     "note": "Override: EX-20 is the richer ethical dilemma (new-seller fairness trap, PayPal/legal precedent); EX-34 reads more as a policy disagreement, better held for IMP-13 later."},
    {"q": "IMP-2", "cat": "impact", "final": "EX-01", "draft": "EX-01",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Prioritized UX by diagnosing user intent harm invisible to dashboards.",
     "note": "Sole linked story."},
    {"q": "IMP-3", "cat": "impact", "final": "EX-21", "draft": "EX-21",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Balances core-vs-peripheral to ship on time with no residual debt.",
     "note": "Sole linked debt story."},
    {"q": "IMP-10", "cat": "impact", "final": "EX-06", "draft": "EX-06",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Crystallized a single experiment into a reusable allocation platform -- long-term vision.",
     "note": "Platform-primitive long-term-value story."},
    # ---- innovation ----
    {"q": "INN-4", "cat": "innovation", "final": "EX-09", "draft": "EX-09",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Novel proxy-item method that maximized infra reuse.",
     "note": "Proxy-item breakthrough."},
    {"q": "INN-2", "cat": "innovation", "final": "EX-01", "draft": "EX-01",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Directly answers self-initiated project + demonstrates innovation.",
     "note": "Self-initiated Hacker Week prototype (sole linked)."},
    {"q": "INN-8", "cat": "innovation", "final": "EX-03", "draft": "EX-33",
     "ds": "swap", "ds_sug": "EX-03", "decision": "accept-swap",
     "ds_reason": "EX-03 directly challenges the core metric and proposes a new proxy -- a more precise match; EX-33 is about test method, not the traditional approach itself.",
     "note": "Accept: EX-03 ('questioned NDCG, proposed GMB') is squarely 'questioned a traditional approach'; EX-33 better serves COL-5/leadership."},
    {"q": "INN-5", "cat": "innovation", "final": "EX-12B", "draft": "EX-12B",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Shows the process waste (<5% utilization) and a measurable improvement; complete arc.",
     "note": "Notebook->platform migration."},
    # ---- problem_solving ----
    {"q": "PS-1", "cat": "problem_solving", "final": "EX-05", "draft": "EX-05",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Real technical decision with constraints, alternatives, and quantified result.",
     "note": "Latency-budget deployment tradeoff."},
    {"q": "PS-6", "cat": "problem_solving", "final": "EX-16", "draft": "EX-16",
     "ds": "swap", "ds_sug": "EX-33", "decision": "override",
     "ds_reason": "EX-33 shows a deliberate calculated risk (gave up carry-over protection); EX-16 reads as reactive crisis response.",
     "note": "Override: keep EX-16 as the clean calculated-risk (named the risk + bandwidth line-item, already the existing primary); EX-33 now leads OWN-6's bold-risk."},
    {"q": "PS-11", "cat": "problem_solving", "final": "EX-01", "draft": "EX-01",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Data-driven diagnosis (abandon-log slice) driving the decision.",
     "note": "Matrix data_analysis primary."},
    {"q": "PS-2", "cat": "problem_solving", "final": "EX-09", "draft": "EX-09",
     "ds": "swap", "ds_sug": "EX-01", "decision": "override",
     "ds_reason": "EX-01 combines creative diagnosis with strong data-driven insights.",
     "note": "Override: EX-09 (proxy-item generation) is the more distinctly *creative* solution; EX-01 already leads three other rows."},
    {"q": "PS-4", "cat": "problem_solving", "final": "EX-03", "draft": "EX-03",
     "ds": "swap", "ds_sug": "EX-05", "decision": "override",
     "ds_reason": "EX-05 shows explicit structured decomposition vs EX-03's metric analysis.",
     "note": "Override: EX-03 is a solid complex-problem analysis (calibration trap); EX-05 already leads PS-1/PS-10/EXE-3 (avoid 4x concentration)."},
    {"q": "PS-10", "cat": "problem_solving", "final": "EX-05", "draft": "EX-05",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Sole story; directly a tough latency trade-off.",
     "note": "Cost-vs-quality tradeoff."},
    # ---- execution ----
    {"q": "EXE-5", "cat": "execution", "final": "EX-23", "draft": "EX-23",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Fits 'large-scale project with tight deadline' directly.",
     "note": "NYC cross-org launch (30+ people)."},
    {"q": "EXE-3", "cat": "execution", "final": "EX-05", "draft": "EX-05",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "STAR-complete; answers complexity + approach.",
     "note": "Sole linked story."},
    {"q": "EXE-9", "cat": "execution", "final": "EX-33B", "draft": "EX-33B",
     "ds": "swap", "ds_sug": "EX-23", "decision": "override",
     "ds_reason": "EX-33B lacks a project-rescue arc (never shipped); EX-23 shows locating the control failure and recovering item-by-item.",
     "note": "Override (judgment): an honest did-not-ship setback with a strong lesson is a valid 'major setback' answer and preserves diversity; EX-23 already leads OWN-2/EXE-5. DeepSeek's recovery point is noted as a delivery caveat."},
    {"q": "EXE-13", "cat": "execution", "final": "EX-21", "draft": "EX-21",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Explicitly balances an urgent feature against longer-term debt.",
     "note": "Immediate-vs-long-term execution tradeoff."},
    # ---- leadership ----
    {"q": "LDR-1", "cat": "leadership", "final": "EX-12", "draft": "EX-12",
     "ds": "swap", "ds_sug": "EX-11", "decision": "override",
     "ds_reason": "EX-11 is a clearer 1:1 coaching example with a specific communication framework.",
     "note": "Override: keep EX-12 (onboarding/enablement mentoring) here and reserve EX-11 for LDR-2 (performance coaching) so both stories are used and distinct."},
    {"q": "LDR-3", "cat": "leadership", "final": "BLOG-04", "draft": "EX-13",
     "ds": "swap", "ds_sug": "BLOG-04", "decision": "accept-swap",
     "ds_reason": "BLOG-04 is a clearer tough call: knowingly accept a short-term metric drop to fix the system.",
     "note": "Accept: a deliberate tough leadership call with an owned cost; frees EX-13 to be COL-1's conflict primary."},
    {"q": "LDR-6", "cat": "leadership", "final": "EX-22", "draft": "EX-22",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Shows the delegate-vs-do-it-myself decision (maintainability vs intuition).",
     "note": "Delegation-decision story."},
    {"q": "LDR-2", "cat": "leadership", "final": "EX-11", "draft": "EX-11",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Directly addresses a junior's performance/communication gap.",
     "note": "Performance-coaching facet (paired with LDR-1=EX-12)."},
    # ---- collaboration ----
    {"q": "COL-1", "cat": "collaboration", "final": "EX-13", "draft": "EX-13",
     "ds": "swap", "ds_sug": "BLOG-01", "decision": "override",
     "ds_reason": "BLOG-01 exemplifies cross-functional collaboration with a joint technical resolution.",
     "note": "Override: COL-1 is about *disagreement* with a team member; EX-13 (authorship dispute) is the direct fit and the matrix conflict_disagreement primary. BLOG-01 is collaboration, not disagreement."},
    {"q": "COL-3", "cat": "collaboration", "final": "EX-12B", "draft": "BLOG-03",
     "ds": "swap", "ds_sug": "EX-12B", "decision": "accept-swap",
     "ds_reason": "EX-12B shows research/Infra two-team direct collaboration to a shared 5%->40% goal -- a better cross-functional-team fit than a one-sided firefighting pipeline.",
     "note": "Accept: genuine cross-functional teamwork; frees BLOG-03 to lead COL-5's stakeholder-alignment."},
    {"q": "COL-5", "cat": "collaboration", "final": "BLOG-03", "draft": "EX-33",
     "ds": "swap", "ds_sug": "BLOG-03", "decision": "accept-swap",
     "ds_reason": "BLOG-03 directly demonstrates aligning cross-org stakeholders by resolving conflict and building shared infra.",
     "note": "Accept: 'align different teams/stakeholders' is exactly BLOG-03's arc."},
    {"q": "COL-6", "cat": "collaboration", "final": "EX-24", "draft": "EX-24",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Matches the prompt: a complex technical concept (zero-sum allocation) explained to a VP.",
     "note": "Conclusion-first VP explanation."},
    # ---- communication ----
    {"q": "COM-1", "cat": "communication", "final": "EX-19", "draft": "EX-19",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Concrete analogy explains a technical confounder to a non-technical PM.",
     "note": "A/B confounder explained to a PM."},
    {"q": "COM-2", "cat": "communication", "final": "EX-14", "draft": "EX-14",
     "ds": "keep", "ds_sug": None, "decision": "keep",
     "ds_reason": "Persuaded leadership to abandon an agentic GenAI path based on ROI -- a clear, well-structured direction change.",
     "note": "Highest-link persuasion question; EX-14 is the cleanest 'change direction' story."},
    {"q": "COM-3", "cat": "communication", "final": "EX-08", "draft": "EX-08",
     "ds": "swap", "ds_sug": "EX-15", "decision": "override",
     "ds_reason": "EX-15 involves owning a mistake, informing affected teams (bad news), and managing it.",
     "note": "Override: EX-08 (surfacing an unnoticed degradation + VP escalation) is a valid deliver-bad-news story and keeps diversity; EX-15 already leads OWN-1/ADP-11."},
]


def _conn() -> sqlite3.Connection:
    """Open the live DB with row access by name."""
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def _resolve(c: sqlite3.Connection) -> tuple[dict[str, int], dict[str, int], dict[tuple[int, int], int]]:
    """Map question_id->pk, example_id->pk, (q_pk,e_pk)->link_pk."""
    q_map = {r["question_id"]: r["id"] for r in c.execute(
        "SELECT id, question_id FROM behavioral_questions")}
    e_map = {r["example_id"]: r["id"] for r in c.execute(
        "SELECT id, example_id FROM behavioral_examples")}
    link_map = {(r["question_id"], r["example_id"]): r["id"] for r in c.execute(
        "SELECT id, question_id, example_id FROM question_example_links")}
    return q_map, e_map, link_map


def _preflight(c: sqlite3.Connection) -> list[str]:
    """Return a list of fatal problems (empty == OK)."""
    q_map, e_map, link_map = _resolve(c)
    errs: list[str] = []
    seen_q: set[str] = set()
    for row in ROWS:
        q, ex = row["q"], row["final"]
        if q in seen_q:
            errs.append(f"{q}: duplicate question in ROWS")
        seen_q.add(q)
        if q not in q_map:
            errs.append(f"{q}: question not in DB")
            continue
        if ex not in e_map:
            errs.append(f"{q}: example {ex} not in DB")
            continue
        if (q_map[q], e_map[ex]) not in link_map:
            errs.append(f"{q}: ({q}, {ex}) is not an existing link -- is_primary can only flag a link")
    if len(ROWS) != 40:
        errs.append(f"expected 40 rows, got {len(ROWS)}")
    return errs


def plan(c: sqlite3.Connection) -> list[dict]:
    """Compute per-row action (SET / SKIP-already / CLEAR-siblings) without writing."""
    q_map, e_map, link_map = _resolve(c)
    actions = []
    for row in ROWS:
        q, ex = row["q"], row["final"]
        q_pk, e_pk = q_map[q], e_map[ex]
        link_pk = link_map[(q_pk, e_pk)]
        cur = c.execute(
            "SELECT example_id, is_primary FROM question_example_links "
            "WHERE question_id=? AND is_primary=1", (q_pk,)).fetchall()
        cur_primary_e = cur[0]["example_id"] if cur else None
        siblings_to_clear = [r["example_id"] for r in cur if r["example_id"] != e_pk]
        already = (cur_primary_e == e_pk) and not siblings_to_clear
        actions.append({
            "q": q, "final": ex, "link_pk": link_pk, "q_pk": q_pk, "e_pk": e_pk,
            "action": "SKIP" if already else "SET",
            "clear_sibling_pks": siblings_to_clear,
        })
    return actions


def apply(c: sqlite3.Connection, actions: list[dict]) -> dict:
    """Execute the plan inside a transaction. Returns a summary."""
    n_set = n_skip = n_cleared = 0
    for a in actions:
        if a["action"] == "SKIP":
            n_skip += 1
            continue
        # clear sibling primaries first (respect the partial unique index)
        for sib_e in a["clear_sibling_pks"]:
            c.execute(
                "UPDATE question_example_links SET is_primary=0 "
                "WHERE question_id=? AND example_id=?", (a["q_pk"], sib_e))
            n_cleared += 1
        c.execute(
            "UPDATE question_example_links SET is_primary=1 WHERE id=?",
            (a["link_pk"],))
        n_set += 1
    c.commit()
    return {"set": n_set, "skip": n_skip, "siblings_cleared": n_cleared}


def verify(c: sqlite3.Connection) -> list[str]:
    """Post-write invariant check. Returns a list of violations (empty == OK)."""
    q_map, e_map, _ = _resolve(c)
    viol: list[str] = []
    dups = c.execute(
        "SELECT question_id, COUNT(*) n FROM question_example_links "
        "WHERE is_primary=1 GROUP BY question_id HAVING COUNT(*)>1").fetchall()
    for d in dups:
        viol.append(f"question pk {d['question_id']} has {d['n']} primaries (>1)")
    for row in ROWS:
        q_pk, e_pk = q_map[row["q"]], e_map[row["final"]]
        got = c.execute(
            "SELECT is_primary FROM question_example_links "
            "WHERE question_id=? AND example_id=?", (q_pk, e_pk)).fetchone()
        if not got or not got["is_primary"]:
            viol.append(f"{row['q']} -> {row['final']} is_primary not set")
    return viol


def backup_db() -> Path:
    """Copy the live DB to a timestamped .bak next to it (data/ is gitignored)."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = DB_PATH.with_suffix(f".db.bak.bq581_{ts}")
    shutil.copy2(DB_PATH, bak)
    return bak


def write_doc() -> None:
    """Render the human-review assignments doc from ROWS."""
    n = {"keep": 0, "accept-swap": 0, "override": 0}
    for r in ROWS:
        n[r["decision"]] = n.get(r["decision"], 0) + 1
    lines: list[str] = []
    lines.append("# BQ-DEPTH-10 (T-P1-581) -- Top-40 Primary-Story Assignments")
    lines.append("")
    lines.append("> **Status: AWAITING USER APPROVAL before DB write.** Each row sets")
    lines.append("> `question_example_links.is_primary=1` for one (question, example) pair.")
    lines.append("> The partial unique index `ux_qel_primary_per_question` guarantees at most")
    lines.append("> one primary per question.")
    lines.append(">")
    lines.append("> **Flow** (human-as-verifier): Claude drafted 40 -> DeepSeek QA judged each")
    lines.append("> (keep / swap / flag, `deepseek-v4-pro`, temp 0) -> Claude accept-default")
    lines.append("> review -> **you approve** -> idempotent `.bak`-guarded seed `--apply`.")
    lines.append(">")
    lines.append("> Selection = top-40 high-probability questions (company overlap + asked")
    lines.append("> frequency) across all 9 categories; each primary chosen from that question's")
    lines.append("> already-linked candidates, guided by `docs/bq_golden_trait_matrix.md`.")
    lines.append("")
    lines.append(f"**Review tally:** {n.get('keep',0)} kept as drafted (DeepSeek concurred), "
                 f"{n.get('accept-swap',0)} swapped on DeepSeek's advice, "
                 f"{n.get('override',0)} overrode DeepSeek (kept draft, reason in note). "
                 "All 40 primaries are verified existing links.")
    lines.append("")
    lines.append("| # | Question | FINAL primary | Draft | DeepSeek | Decision |")
    lines.append("|---|----------|---------------|-------|----------|----------|")
    for i, r in enumerate(ROWS, 1):
        ds = r["ds"].upper()
        if r["ds"] == "swap" and r["ds_sug"]:
            ds += f"->{r['ds_sug']}"
        changed = "" if r["final"] == r["draft"] else f" (was `{r['draft']}`)"
        qtext = _q_text(r["q"]).replace("|", "\\|")
        dec = {"keep": "keep", "accept-swap": "ACCEPT swap", "override": "OVERRIDE"}[r["decision"]]
        lines.append(
            f"| {i} | **{r['q']}** {qtext} | `{r['final']}`{changed} | `{r['draft']}` "
            f"| {ds} | {dec} |")
    lines.append("")
    lines.append("## Per-row reasoning")
    lines.append("")
    for r in ROWS:
        lines.append(f"### {r['q']} -> `{r['final']}` ({r['cat']})")
        lines.append(f"- *DeepSeek ({r['ds']}{('->'+r['ds_sug']) if r['ds_sug'] else ''}):* "
                     f"{r['ds_reason']}")
        lines.append(f"- *Claude decision ({r['decision']}):* {r['note']}")
        lines.append("")
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


_Q_TEXT_CACHE: dict[str, str] = {}


def _q_text(qcode: str) -> str:
    """Fetch a question's text (cached) for the doc table."""
    if not _Q_TEXT_CACHE:
        c = _conn()
        for r in c.execute("SELECT question_id, text FROM behavioral_questions"):
            _Q_TEXT_CACHE[r["question_id"]] = r["text"]
        c.close()
    return _Q_TEXT_CACHE.get(qcode, "?")


def main() -> int:
    """CLI entry: dry-run plan (default), --doc, or --apply."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write to DB (post-approval)")
    ap.add_argument("--doc", action="store_true", help="regenerate the review doc and exit")
    args = ap.parse_args()

    if args.doc:
        write_doc()
        print(f"[581-seed] wrote review doc -> {DOC_PATH}")
        return 0

    if not DB_PATH.exists():
        print(f"[581-seed] DB not found: {DB_PATH}", file=sys.stderr)
        return 2
    c = _conn()
    errs = _preflight(c)
    if errs:
        print("[581-seed] PREFLIGHT FAILED:")
        for e in errs:
            print("   ", e)
        return 2
    actions = plan(c)
    n_set = sum(1 for a in actions if a["action"] == "SET")
    n_skip = sum(1 for a in actions if a["action"] == "SKIP")
    print(f"[581-seed] plan: {n_set} to SET, {n_skip} already correct (SKIP). "
          f"{'APPLY' if args.apply else 'DRY-RUN'}")
    for a in actions:
        tag = a["action"]
        sib = f" (clear {len(a['clear_sibling_pks'])} sibling)" if a["clear_sibling_pks"] else ""
        print(f"   {tag:4} {a['q']:7} -> {a['final']}{sib}")

    if not args.apply:
        print("[581-seed] DRY-RUN -- no DB write. Re-run with --apply after approval.")
        return 0

    bak = backup_db()
    print(f"[581-seed] DB backed up -> {bak.name}")
    summary = apply(c, actions)
    viol = verify(c)
    audit = {
        "task": "T-P1-581", "ts": datetime.now().isoformat(timespec="seconds"),
        "backup": bak.name, "summary": summary,
        "rows": [{"q": r["q"], "final": r["final"], "draft": r["draft"],
                  "decision": r["decision"]} for r in ROWS],
        "violations": viol,
    }
    AUDIT_DIR.mkdir(exist_ok=True)
    audit_path = AUDIT_DIR / f"bq_581_primary_seed_{datetime.now():%Y%m%d_%H%M%S}.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[581-seed] applied: {summary}; audit -> {audit_path.name}")
    if viol:
        print("[581-seed] POST-WRITE VIOLATIONS:")
        for v in viol:
            print("   ", v)
        return 3
    print("[581-seed] OK -- every targeted question has exactly one is_primary=1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
