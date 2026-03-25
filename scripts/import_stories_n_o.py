"""Import Story N (EX-23) and Story O (EX-24) and add cross-reference sweep.

Part of T-P1-49: Map remaining gap questions to existing stories.
"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
docs_dir = project_root / "docs"
examples_path = docs_dir / "bq_behavioral_examples.json"
questions_path = docs_dir / "bq_clustered_questions.json"


def main() -> None:
    """Run the import and cross-reference sweep."""
    with open(examples_path, encoding="utf-8") as f:
        data = json.load(f)

    # PART 1: Add EX-23 (Story N)
    ex23 = {
        "id": "EX-23",
        "title": "Large-Scale Project with Tight Deadlines --- NYC C2C Policy Launch",
        "source_project": "C2C Policy Launch --- NYC Hub",
        "situation": (
            "NYC hub's C2C business was declining for several consecutive weeks "
            "as competitors captured market share. VP demanded a test within 2 weeks "
            "and a policy launch proposal within 1 month. Project involved 30+ people "
            "across a large org."
        ),
        "task": (
            "As project lead, needed to deliver a policy test and launch framework "
            "under extremely tight timeline, while maintaining daily updates and "
            "weekly VP meeting cadence."
        ),
        "action": (
            "Phase 1: Inventoried all workstreams, identified critical path, ensured "
            "30+ people did not block each other. Phase 2: After test launch, discovered "
            "control effectiveness below expectations. Team suspected logging issues "
            "(Kafka fluctuation causing data gaps). While fixing logging, continued "
            "digging deeper --- discovered upstream web request gateway team had silently "
            "fixed an incident by overwriting the control property, causing silent failure. "
            "Drove cross-team resolution. Phase 3: Found deeper structural issue --- "
            "multiple policies tested successfully independently but competed for top "
            "slots when launched simultaneously. Convinced VP to limit scope rather than "
            "combo-launch all policies."
        ),
        "result": (
            "Project delivered within deadline, framework successfully launched. More "
            "importantly, helped team avoid a wrong direction --- blindly combo-launching "
            "policies whose effects would cancel each other out."
        ),
        "evidence_quotes": [
            "VP demanded test within 2 weeks, launch proposal within 1 month, 30+ person project",
            "Upstream gateway team silently fixed an incident by overwriting control property",
            "Multiple policies competed for top slots when combo-launched",
        ],
        "principle_tags": ["execution", "problem_solving", "ownership"],
        "cross_references": [
            {"question_id": "EXE-5", "relevance_note": "Managed 30+ person project under VP 2-week test deadline"},
            {"question_id": "EXE-6", "relevance_note": "Balanced VP urgency, upstream gateway team fix, and combo launch scope"},
            {"question_id": "EXE-9", "relevance_note": "Recovered from silent upstream overwrite causing test failure"},
            {"question_id": "EXE-12", "relevance_note": "Shifted priorities when combo launch structural problem discovered"},
            {"question_id": "PS-4", "relevance_note": "Broke down complex problem: logging vs gateway vs allocation"},
            {"question_id": "OWN-2", "relevance_note": "Went above and beyond to meet VP 2-week deadline"},
            {"question_id": "OWN-4", "relevance_note": "Took responsibility for 30+ person team performance and VP-level delivery"},
            {"question_id": "EXE-7", "relevance_note": "Handled delay caused by upstream gateway team silently overwriting control property"},
            {"question_id": "EXE-10", "relevance_note": "Managed 2-week test deadline + 1-month launch proposal + daily updates + weekly VP meetings"},
            {"question_id": "EXE-14", "relevance_note": "Maintained daily team updates and weekly VP cadence while managing 30+ person critical path"},
            {"question_id": "COL-7", "relevance_note": "Worked with 30+ people across technical teams and VP-level stakeholders"},
            {"question_id": "COL-8", "relevance_note": "Managed VP expectations on timeline and scope while coordinating with multiple technical teams"},
            {"question_id": "COL-9", "relevance_note": "Balanced competing priorities: VP urgency, gateway team fix, and combo launch scope tradeoffs"},
            {"question_id": "ADP-3", "relevance_note": "Requirements shifted when structural problem discovered mid-project, adapted scope accordingly"},
            {"question_id": "PS-8", "relevance_note": "High uncertainty project: unknown logging issues, silent upstream failures, untested policy interactions"},
        ],
    }

    # PART 2: Add EX-24 (Story O)
    ex24 = {
        "id": "EX-24",
        "title": "Explaining Allocation Problem to VP --- C2C Policy Launch Communication",
        "source_project": "C2C Policy Launch --- VP Communication",
        "situation": (
            "During debugging the C2C policy launch, discovered two levels of issues: "
            "upstream gateway silent overwrite (tactical) and ranking is fundamentally "
            "an allocation problem (strategic). Needed to communicate these findings "
            "at weekly VP meeting."
        ),
        "task": (
            "VP saw several independent tests succeeding and naturally wanted to "
            "combo-launch them for maximum effect. Needed to explain why this intuition "
            "was wrong, using non-technical language to change VP decision."
        ),
        "action": (
            "Communication strategy: conclusion first, then expand. Told VP three things: "
            "(1) we are currently overestimating the achievable adjustment effect, "
            "(2) we may be underestimating impact on default ranking, "
            "(3) this is not an execution problem but a structural one. "
            "Then explained in VP-accessible terms: each policy performs well independently "
            "because it monopolizes top slots, but when launched simultaneously they "
            "compete --- no free lunch. This is fundamentally an allocation problem, "
            "not simple addition. Recommended limiting scope to highest-ROI adjustments first."
        ),
        "result": (
            "VP accepted the analysis and adjusted project direction. The allocation "
            "framing also became the team mental model for thinking about ranking "
            "strategy going forward."
        ),
        "evidence_quotes": [
            "Conclusion first, then expand: overestimating effect, underestimating default ranking impact, structural not execution problem",
            "Free-lunch analogy: each policy monopolizes top slots independently, but they compete when combined",
            "VP accepted analysis and adjusted project direction",
        ],
        "principle_tags": ["communication", "collaboration", "impact"],
        "cross_references": [
            {"question_id": "COL-6", "relevance_note": "Explained allocation problem (policies competing for top slots) to VP using free-lunch analogy"},
            {"question_id": "COM-1", "relevance_note": "Translated ranking allocation concept into non-technical terms for VP decision"},
            {"question_id": "COM-2", "relevance_note": "Persuaded VP to limit scope rather than combo-launch all policies"},
            {"question_id": "PS-11", "relevance_note": "Used data showing independent test results dont add up to justify scope change"},
            {"question_id": "INN-7", "relevance_note": "Reframed combo-launch as structural allocation problem rather than just an execution issue"},
        ],
    }

    # Check if already exists
    existing_ids = {ex["id"] for ex in data["examples"]}
    if "EX-23" not in existing_ids:
        data["examples"].append(ex23)
        print("[DONE] Added EX-23 (Story N)")
    else:
        print("[SKIP] EX-23 already exists")

    if "EX-24" not in existing_ids:
        data["examples"].append(ex24)
        print("[DONE] Added EX-24 (Story O)")
    else:
        print("[SKIP] EX-24 already exists")

    # PART 3: Cross-reference sweep for uncovered questions
    # Map: example_id -> list of (question_id, relevance_note)
    new_xrefs = {
        "EX-17": [
            ("OWN-3", "Received difficult feedback from senior IC about credibility and handled it constructively"),
            ("ADP-17", "Senior IC feedback revealed growth area in credibility-building; adjusted approach accordingly"),
        ],
        "EX-08": [
            ("ADP-13", "Escalated prod degradation to VP, maintained team morale through incident resolution"),
        ],
        "EX-10": [
            ("OWN-5", "Established debiased evaluation framework ensuring consistent quality in experiment results"),
        ],
        "EX-15": [
            ("OWN-7", "Demonstrated resilience through model deprecation incident recovery and process improvement"),
            ("OWN-8", "Model deprecation incident where fast-moving deployment missed compatibility checks"),
            ("ADP-2", "Adjusted approach after model deprecation broke production; rebuilt with resilience patterns"),
            ("ADP-13", "Recovered from model deprecation failure and built process improvements to prevent recurrence"),
        ],
        "EX-02": [
            ("OWN-7", "Showed resilience by transferring teams rather than accepting organizational constraints"),
            ("ADP-17", "Recognized own gap: had not translated business case into team OKR language early enough"),
        ],
        "EX-05": [
            ("OWN-8", "Over-invested in latency optimization before validating deployability --- moved fast, corrected course"),
        ],
        "EX-01": [
            ("OWN-9", "Invested Hacker Week building diversity prototype with incomplete information about production viability"),
            ("INN-9", "Creative solution: cheap intent-coverage proxy instead of expensive holistic ranking rewrite"),
            ("INN-10", "Identified intent collapse as innovation area through abandoned query data analysis"),
            ("ADP-20", "Self-initiated Hacker Week project driven by curiosity about abandoned query patterns"),
        ],
        "EX-06": [
            ("OWN-10", "Allocation framework grew from Hacker Week prototype to 200M+ annualized long-term platform impact"),
            ("INN-12", "Scaled diversity ranking from single vertical to 200M+ annualized impact across multiple verticals"),
            ("PS-7", "Balanced risk of challenging core ranking assumptions against potential 200M+ reward"),
            ("IMP-9", "Invested in reusable allocation framework over short-term single-vertical win"),
            ("EXE-13", "Balanced immediate experiment wins with building a long-term reusable platform primitive"),
        ],
        "EX-09": [
            ("INN-9", "Proxy item breakthrough for conversational search --- creative workaround for cold-start problem"),
            ("PS-9", "Built conversational search proxy on incomplete information about user intent patterns"),
            ("ADP-7", "Conversational search started with uncertain outcomes; proxy item approach emerged through iteration"),
            ("ADP-9", "Established proxy-based metrics for unclear conversational search project"),
            ("ADP-10", "Created plan for conversational search in ambiguous environment with no prior art"),
        ],
        "EX-14": [
            ("INN-3", "Explored LLM technologies to find pragmatic application matching team capabilities"),
            ("ADP-1", "Quickly learned LLM capabilities when given vague AI mandate from leadership"),
            ("ADP-7", "LLM exploration started with incomplete requirements from vague AI mandate"),
            ("ADP-10", "Created structured plan to evaluate LLM applications in highly ambiguous AI mandate"),
            ("EXE-4", "Incorporated LLM industry trends into pragmatic team project planning"),
        ],
        "EX-22": [
            ("LDR-10", "Researcher gained deep ownership and confidence through structured delegation of hashing decision"),
        ],
        "EX-16": [
            ("ADP-1", "Quickly learned cross-datacenter deployment patterns when stretching beyond comfort zone"),
        ],
        "EX-12": [
            ("INN-13", "Improved established notebook-only workflow by building production template class for research team"),
        ],
        "EX-21": [
            ("INN-3", "Chose declarative Artifactory approach after evaluating multiple technology options"),
            ("INN-13", "Improved well-established but manual Artifactory config process with declarative PoC"),
            ("EXE-13", "Balanced immediate feature work with longer-term tech debt reduction through Artifactory PoC"),
            ("IMP-9", "Weighed short-term manual config against long-term declarative approach"),
        ],
        "EX-20": [
            ("IMP-12", "Seller risk modeling raised responsible innovation concerns about fairness in automated decisions"),
            ("IMP-13", "Escalated ethical concern about seller risk model fairness rather than shipping known-biased model"),
        ],
        "EX-11": [
            ("OWN-5", "Taught intern structured goal-setting ensuring consistent quality in deliverables"),
        ],
    }

    added_count = 0
    for ex in data["examples"]:
        if ex["id"] in new_xrefs:
            existing_qids = {xr["question_id"] for xr in ex.get("cross_references", [])}
            for qid, note in new_xrefs[ex["id"]]:
                if qid not in existing_qids:
                    ex.setdefault("cross_references", []).append({
                        "question_id": qid,
                        "relevance_note": note,
                    })
                    added_count += 1

    print(f"[DONE] Added {added_count} new cross-references to existing examples")

    # Update metadata
    data["metadata"]["total_examples"] = len(data["examples"])
    data["metadata"]["last_updated"] = "2026-03-25"
    data["metadata"]["update_task_id"] = "T-P1-49"

    with open(examples_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Verify coverage
    covered = set()
    for ex in data["examples"]:
        for xr in ex.get("cross_references", []):
            covered.add(xr["question_id"])
    for ans in data.get("blog_proj_existing_answers", []):
        for xr in ans.get("cross_references", []):
            covered.add(xr["question_id"])

    with open(questions_path, encoding="utf-8") as f:
        qs = json.load(f)
    all_q = set()
    for cat in qs["categories"]:
        for q in cat["questions"]:
            all_q.add(q["id"])

    uncovered = sorted(all_q - covered)
    coverage_pct = round(len(covered) / len(all_q) * 100, 1)
    print(f"\n[SUMMARY] Coverage: {len(covered)}/{len(all_q)} ({coverage_pct}%)")
    if uncovered:
        print(f"Still uncovered ({len(uncovered)}): {uncovered}")
    else:
        print("All questions have at least one example!")


if __name__ == "__main__":
    main()
