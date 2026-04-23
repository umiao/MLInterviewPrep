"""Seed the 15 behavioral themes and tag all questions/examples via keyword rules.

Idempotent: re-running inserts only missing rows. Existing themes and tags are
preserved. After tagging, prints a coverage report and lists any unclassified
questions/examples for human review.

Scenario matrix (from T-P1-353 spec):
- Question text matches >=1 theme keyword rule -> inserts question_theme_tags rows
- Question text matches 0 rules -> logged as "needs-human-review"
- Example matches >=1 rule -> inserts example_theme_tags rows
- Example matches 0 rules -> logged as needs-review
- Re-run -> no duplicate rows
- oncall_prod_incident theme: row exists in behavioral_themes even if count=0
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.backend.database import SessionLocal, get_engine, init_db  # noqa: E402
from src.backend.models.behavioral import (  # noqa: E402
    BehavioralExample,
    BehavioralQuestion,
)
from src.backend.models.behavioral_theme import (  # noqa: E402
    BehavioralTheme,
    ExampleThemeTag,
    QuestionThemeTag,
)

# ---------------------------------------------------------------------------
# Theme definitions
# Order here determines display_order (1-based, matches rough frequency rank).
# ---------------------------------------------------------------------------

THEMES: list[dict] = [
    {
        "slug": "technical_problem_solving",
        "label": "Technical Problem Solving",
        "description": "Diagnosing and solving complex technical problems.",
    },
    {
        "slug": "collaboration_teamwork",
        "label": "Collaboration & Teamwork",
        "description": "Working with teammates, cross-functional partners, and stakeholders.",
    },
    {
        "slug": "leadership_direction",
        "label": "Leadership & Direction",
        "description": "Setting direction, making tough calls, and leading without authority.",
    },
    {
        "slug": "process_systems",
        "label": "Process & Systems",
        "description": "Designing processes, establishing standards, improving workflows.",
    },
    {
        "slug": "failure_setback",
        "label": "Failure & Setback",
        "description": "Mistakes, setbacks, and how you recovered and learned.",
    },
    {
        "slug": "prioritization_tradeoffs",
        "label": "Prioritization & Tradeoffs",
        "description": "Balancing competing priorities and making tradeoffs.",
    },
    {
        "slug": "ownership_accountability",
        "label": "Ownership & Accountability",
        "description": "Taking responsibility and delivering end-to-end.",
    },
    {
        "slug": "data_analysis",
        "label": "Data & Analysis",
        "description": "Using data and metrics to drive decisions.",
    },
    {
        "slug": "conflict_disagreement",
        "label": "Conflict & Disagreement",
        "description": "Disagreements, pushback, and resolving interpersonal tension.",
    },
    {
        "slug": "deadline_pressure",
        "label": "Deadline & Pressure",
        "description": "Tight deadlines and high-stakes delivery.",
    },
    {
        "slug": "mentoring_coaching",
        "label": "Mentoring & Coaching",
        "description": "Developing juniors, mentoring interns, and coaching peers.",
    },
    {
        "slug": "scope_creep_ambiguous",
        "label": "Scope & Ambiguous Requirements",
        "description": "Scope changes, rescoping, and ambiguous requirements.",
    },
    {
        "slug": "code_quality_tech_debt",
        "label": "Code Quality & Tech Debt",
        "description": "Balancing code quality, maintainability, and technical debt.",
    },
    {
        "slug": "ambiguity_uncertainty",
        "label": "Ambiguity & Uncertainty",
        "description": "Operating with incomplete information and unclear goals.",
    },
    {
        "slug": "oncall_prod_incident",
        "label": "On-call & Production Incidents",
        "description": "On-call rotations, outages, and production incident response.",
    },
]

# ---------------------------------------------------------------------------
# Keyword rules (case-insensitive substring match)
# ---------------------------------------------------------------------------

QUESTION_KEYWORDS: dict[str, list[str]] = {
    "technical_problem_solving": [
        "technical decision",
        "technical problem",
        "complex technical",
        "complex problem",
        "technical project",
        "technical details",
        "analyzed a complex",
        "broke it down",
        "solved creatively",
        "solved a problem",
        "creative solution",
        "creatively",
        "difficult technical",
        "complex concept",
        "innovative solution",
    ],
    "collaboration_teamwork": [
        "team member",
        "cross-functional",
        "cross functional",
        "collaborat",
        "stakeholder",
        "within a team",
        "within your team",
        "with a team",
        "team's",
        "team lead",
        "different teams",
        "departments",
        "team.",
    ],
    "leadership_direction": [
        "as a leader",
        "lead ",
        "led ",
        "leading",
        "leader",
        "tough call",
        "delegate",
        "delegating",
        "delegation",
        "empower",
        "mentor",
        "coach",
        "vision",
        "trust someone",
        "built someone",
        "quality while delegating",
        "setting goals",
    ],
    "process_systems": [
        "process",
        "best practices",
        "workflow",
        "system you built",
        "put in place",
        "established",
        "establish ",
        "standards",
        "productivity",
        "optimize",
        "optimized",
        "long-term maintain",
        "improve a process",
        "improved",
        "inefficient",
    ],
    "failure_setback": [
        "failure",
        "failed",
        "mistake",
        "setback",
        "didn't go as planned",
        "didn't work",
        "went wrong",
        "recovered",
        "bounce back",
        "did not go",
        "roadblock",
        "pushed through",
        "lesson",
    ],
    "prioritization_tradeoffs": [
        "prioritize",
        "priorit",
        "trade-off",
        "tradeoff",
        "trade off",
        "balance",
        "competing",
        "weigh ",
        "multiple options",
        "shift priorit",
        "choose one",
        "short-term",
        "long-term",
        "conflict",
    ],
    "ownership_accountability": [
        "ownership",
        "took responsib",
        "above and beyond",
        "take responsibility",
        "complete ownership",
        "bold risk",
        "ethical",
        "resilien",
        "focus on long",
    ],
    "data_analysis": [
        "data",
        "metric",
        "analy",
        "data-driven",
        "insight",
    ],
    "conflict_disagreement": [
        "disagree",
        "conflict",
        "pushback",
        "push back",
        "persuade",
        "bad news",
        "deliver bad",
        "tough call",
        "opposed",
        "dispute",
        "resistance",
    ],
    "deadline_pressure": [
        "deadline",
        "tight deadline",
        "tight ",
        "high-stakes",
        "high stakes",
        "high-pressure",
        "high pressure",
        "time effectively",
        "managed your time",
        "urgent",
        "last minute",
    ],
    "mentoring_coaching": [
        "mentor",
        "coach",
        "junior",
        "intern",
        "struggling team",
        "built someone",
        "develop",
        "train",
        "grow",
        "coached",
    ],
    "scope_creep_ambiguous": [
        "re-scope",
        "rescope",
        "scope",
        "changing requirements",
        "incomplete requirements",
        "adjust to a significant change",
        "unclear project",
        "limited data",
    ],
    "code_quality_tech_debt": [
        "technical debt",
        "tech debt",
        "code quality",
        "quality work",
        "maintainab",
        "scalable and sustainab",
        "future-proof",
        "long-term maintain",
    ],
    "ambiguity_uncertainty": [
        "ambigu",
        "uncertain",
        "uncertainty",
        "unclear",
        "incomplete",
        "limited data",
        "without all the information",
        "vague",
        "lot of ambiguity",
        "high degree of uncertainty",
        "act on incomplete",
    ],
    "oncall_prod_incident": [
        "on-call",
        "oncall",
        "on call",
        "outage",
        "production incident",
        "pager",
        "sev1",
        "sev 1",
        "postmortem",
        "post-mortem",
        "prod incident",
        "production issue",
    ],
}

# Example matching reuses the same keyword map, but the match text is built
# from the example title + STAR fields + principle_tags.

EXAMPLE_KEYWORDS: dict[str, list[str]] = {
    # Start with the same rules, extended with phrases common in the example corpus.
    **QUESTION_KEYWORDS,
}
EXAMPLE_KEYWORDS["technical_problem_solving"] = (
    QUESTION_KEYWORDS["technical_problem_solving"]
    + [
        "problem_solving",
        "architecture",
        "algorithm",
        "model",
        "pipeline",
        "refactor",
        "proof of concept",
        "evaluation framework",
        "relevance",
        "ranking",
        "latency",
        "ndcg",
        "llm",
        "experiment",
        "deploy",
    ]
)
EXAMPLE_KEYWORDS["collaboration_teamwork"] = (
    QUESTION_KEYWORDS["collaboration_teamwork"]
    + [
        "cross-org",
        "cross org",
        "researcher",
        "engineer dynamic",
        "teamwork",
        "align",
        "stakeholder",
        "pm ",
        "partner",
    ]
)
EXAMPLE_KEYWORDS["leadership_direction"] = (
    QUESTION_KEYWORDS["leadership_direction"]
    + [
        "leadership",
        "influence_without_authority",
        "develop_others",
        "earn_trust",
        "disagree_and_commit",
    ]
)
EXAMPLE_KEYWORDS["data_analysis"] = (
    QUESTION_KEYWORDS["data_analysis"]
    + [
        "data_driven",
        "dive_deep",
        "a/b",
        "evaluation",
        "metric limitation",
        "confounder",
    ]
)
EXAMPLE_KEYWORDS["code_quality_tech_debt"] = (
    QUESTION_KEYWORDS["code_quality_tech_debt"]
    + [
        "code review",
        "insist_on_highest_standards",
        "declarative artifactory",
    ]
)
EXAMPLE_KEYWORDS["oncall_prod_incident"] = (
    QUESTION_KEYWORDS["oncall_prod_incident"]
    + [
        "incident",
        "degradation",
        "deprecation",
        "escalation to vp",
        "prod degradation",
        "deployment incident",
    ]
)
EXAMPLE_KEYWORDS["failure_setback"] = (
    QUESTION_KEYWORDS["failure_setback"]
    + [
        "paradox",
        "blind spot",
        "needs_input",
        "failure story",
        "miss",
    ]
)
EXAMPLE_KEYWORDS["conflict_disagreement"] = (
    QUESTION_KEYWORDS["conflict_disagreement"]
    + [
        "disagree_and_commit",
        "have_backbone",
        "authorship",
        "manager resistance",
        "pushing back",
    ]
)
EXAMPLE_KEYWORDS["mentoring_coaching"] = (
    QUESTION_KEYWORDS["mentoring_coaching"]
    + [
        "develop_others",
        "phd intern",
        "notebook to production",
    ]
)
EXAMPLE_KEYWORDS["scope_creep_ambiguous"] = (
    QUESTION_KEYWORDS["scope_creep_ambiguous"]
    + [
        "unreasonable scope",
        "vague ai mandate",
    ]
)
EXAMPLE_KEYWORDS["deadline_pressure"] = (
    QUESTION_KEYWORDS["deadline_pressure"]
    + [
        "policy launch",
        "tight deadline",
    ]
)
EXAMPLE_KEYWORDS["ownership_accountability"] = (
    QUESTION_KEYWORDS["ownership_accountability"]
    + [
        "ownership",
        "escalation",
        "ethics",
    ]
)
EXAMPLE_KEYWORDS["ambiguity_uncertainty"] = (
    QUESTION_KEYWORDS["ambiguity_uncertainty"]
    + [
        "vague",
        "exploration",
        "first principles",
    ]
)
EXAMPLE_KEYWORDS["process_systems"] = (
    QUESTION_KEYWORDS["process_systems"]
    + [
        "platform primitive",
        "framework",
        "goal tracking reform",
        "build_mechanism",
        "norms",
    ]
)

# ---------------------------------------------------------------------------
# Manual overrides for items the keyword rules miss.
# ---------------------------------------------------------------------------

QUESTION_OVERRIDES: dict[str, list[str]] = {
    # Growth / feedback questions missing failure or people themes
    "ADP-1": ["ambiguity_uncertainty", "technical_problem_solving"],
    "ADP-4": ["ambiguity_uncertainty", "scope_creep_ambiguous"],
    "ADP-16": ["failure_setback"],
    "ADP-17": ["leadership_direction"],
    "ADP-19": ["failure_setback", "conflict_disagreement"],
    "ADP-20": ["ownership_accountability"],
    "COL-7": ["collaboration_teamwork", "technical_problem_solving"],
    "EXE-4": ["process_systems", "ownership_accountability"],
    "EXE-7": ["collaboration_teamwork", "deadline_pressure"],
    "IMP-5": ["process_systems", "technical_problem_solving"],
    "IMP-11": ["ownership_accountability", "conflict_disagreement"],
    "IMP-12": ["ownership_accountability"],
    "IMP-14": ["ownership_accountability"],
    "IMP-15": ["ownership_accountability"],
    "INN-1": ["process_systems", "ownership_accountability"],
    "INN-2": ["ownership_accountability", "technical_problem_solving"],
    "INN-3": ["technical_problem_solving"],
    "INN-7": ["technical_problem_solving", "prioritization_tradeoffs"],
    "INN-8": ["technical_problem_solving", "process_systems"],
    "INN-10": ["process_systems", "technical_problem_solving"],
    "LDR-3": ["leadership_direction", "conflict_disagreement"],
    "OWN-3": ["failure_setback"],
    "OWN-7": ["failure_setback"],
    "PS-1": ["technical_problem_solving"],
    "PS-6": ["ownership_accountability", "ambiguity_uncertainty"],
}

EXAMPLE_OVERRIDES: dict[str, list[str]] = {
    "BLOG-01": ["collaboration_teamwork", "leadership_direction"],
    "BLOG-01B": ["technical_problem_solving", "data_analysis"],
    "BLOG-02": ["code_quality_tech_debt", "collaboration_teamwork"],
    "BLOG-03": ["collaboration_teamwork", "technical_problem_solving"],
    "BLOG-04": ["ownership_accountability", "process_systems"],
    "EX-01": ["technical_problem_solving", "data_analysis"],
    "EX-02": ["conflict_disagreement", "ownership_accountability"],
    "EX-03": ["technical_problem_solving", "data_analysis"],
    "EX-04": ["data_analysis", "collaboration_teamwork"],
    "EX-05": ["technical_problem_solving", "prioritization_tradeoffs"],
    "EX-06": ["technical_problem_solving", "process_systems"],
    "EX-07": ["technical_problem_solving", "data_analysis"],
    "EX-08": ["oncall_prod_incident", "technical_problem_solving"],
    "EX-09": ["technical_problem_solving", "ambiguity_uncertainty"],
    "EX-10": ["technical_problem_solving", "data_analysis"],
    "EX-11": ["mentoring_coaching", "leadership_direction"],
    "EX-12": ["mentoring_coaching", "leadership_direction"],
    "EX-12B": ["process_systems", "collaboration_teamwork"],
    "EX-13": ["conflict_disagreement", "collaboration_teamwork"],
    "EX-14": ["ambiguity_uncertainty", "technical_problem_solving"],
    "EX-15": ["oncall_prod_incident", "failure_setback"],
    "EX-16": ["oncall_prod_incident", "deadline_pressure"],
    "EX-17": ["failure_setback", "collaboration_teamwork"],
    "EX-18": ["scope_creep_ambiguous", "conflict_disagreement"],
    "EX-19": ["data_analysis", "collaboration_teamwork"],
    "EX-20": ["ownership_accountability", "conflict_disagreement"],
    "EX-21": ["code_quality_tech_debt", "technical_problem_solving"],
    "EX-22": ["leadership_direction", "technical_problem_solving"],
    "EX-23": ["deadline_pressure", "technical_problem_solving"],
    "EX-24": ["collaboration_teamwork", "data_analysis"],
    "EX-30": ["failure_setback"],
    "EX-31": ["failure_setback", "conflict_disagreement"],
    "EX-32": ["failure_setback", "deadline_pressure"],
}


def _match_themes(text: str, rules: dict[str, list[str]]) -> set[str]:
    """Return set of theme slugs whose keywords appear in lowercased text.

    Args:
        text: Text to search against.
        rules: Mapping of theme slug -> list of keyword substrings.

    Returns:
        Set of matching theme slugs.
    """
    lowered = text.lower()
    matched: set[str] = set()
    for slug, keywords in rules.items():
        for kw in keywords:
            if kw.lower() in lowered:
                matched.add(slug)
                break
    return matched


def _example_match_text(ex: BehavioralExample) -> str:
    """Concatenate example fields used for keyword matching."""
    parts = [
        ex.title or "",
        ex.source_project or "",
        ex.situation or "",
        ex.task or "",
        ex.action or "",
        ex.result or "",
        ex.principle_tags or "",
        ex.analogy or "",
    ]
    return " ".join(parts)


def seed() -> dict:
    """Seed themes and theme tags.

    Returns:
        Coverage report dict with inserted counts and unclassified lists.
    """
    engine = get_engine()
    init_db(engine)

    db = SessionLocal()
    try:
        # --- Step 1: upsert 15 themes ---
        slug_to_theme: dict[str, BehavioralTheme] = {}
        themes_inserted = 0
        for order, spec in enumerate(THEMES, start=1):
            existing = (
                db.query(BehavioralTheme)
                .filter(BehavioralTheme.slug == spec["slug"])
                .first()
            )
            if existing:
                # Keep existing, but refresh label/description/order.
                existing.label = spec["label"]
                existing.description = spec["description"]
                existing.display_order = order
                slug_to_theme[spec["slug"]] = existing
            else:
                t = BehavioralTheme(
                    slug=spec["slug"],
                    label=spec["label"],
                    description=spec["description"],
                    display_order=order,
                )
                db.add(t)
                db.flush()
                slug_to_theme[spec["slug"]] = t
                themes_inserted += 1
        db.commit()

        # --- Step 2: tag questions ---
        questions = db.query(BehavioralQuestion).all()
        q_tag_inserted = 0
        q_unclassified: list[str] = []
        for q in questions:
            matched = _match_themes(q.text, QUESTION_KEYWORDS)
            for slug in QUESTION_OVERRIDES.get(q.question_id, []):
                matched.add(slug)
            if not matched:
                q_unclassified.append(f"{q.question_id}: {q.text}")
                continue
            for slug in matched:
                theme = slug_to_theme[slug]
                existing = (
                    db.query(QuestionThemeTag)
                    .filter(
                        QuestionThemeTag.question_id == q.id,
                        QuestionThemeTag.theme_id == theme.id,
                    )
                    .first()
                )
                if not existing:
                    db.add(
                        QuestionThemeTag(question_id=q.id, theme_id=theme.id)
                    )
                    q_tag_inserted += 1
        db.commit()

        # --- Step 3: tag examples ---
        examples = db.query(BehavioralExample).all()
        ex_tag_inserted = 0
        ex_unclassified: list[str] = []
        for ex in examples:
            text = _example_match_text(ex)
            matched = _match_themes(text, EXAMPLE_KEYWORDS)
            for slug in EXAMPLE_OVERRIDES.get(ex.example_id, []):
                matched.add(slug)
            if not matched:
                ex_unclassified.append(f"{ex.example_id}: {ex.title}")
                continue
            for slug in matched:
                theme = slug_to_theme[slug]
                existing = (
                    db.query(ExampleThemeTag)
                    .filter(
                        ExampleThemeTag.example_id == ex.id,
                        ExampleThemeTag.theme_id == theme.id,
                    )
                    .first()
                )
                if not existing:
                    db.add(
                        ExampleThemeTag(example_id=ex.id, theme_id=theme.id)
                    )
                    ex_tag_inserted += 1
        db.commit()

        return {
            "themes_inserted": themes_inserted,
            "question_tags_inserted": q_tag_inserted,
            "example_tags_inserted": ex_tag_inserted,
            "questions_total": len(questions),
            "questions_unclassified": q_unclassified,
            "examples_total": len(examples),
            "examples_unclassified": ex_unclassified,
        }
    finally:
        db.close()


def main() -> int:
    """Entry point: run seed and print coverage report."""
    report = seed()
    print("=" * 60)
    print("Behavioral theme seed report")
    print("=" * 60)
    print(f"Themes inserted this run: {report['themes_inserted']}")
    print(
        f"Question tags inserted this run: {report['question_tags_inserted']}"
    )
    print(
        f"Example tags inserted this run: {report['example_tags_inserted']}"
    )
    print(f"Total questions: {report['questions_total']}")
    print(
        f"Unclassified questions: {len(report['questions_unclassified'])}"
    )
    for line in report["questions_unclassified"]:
        print(f"  [UNCLASSIFIED-Q] {line}")
    print(f"Total examples: {report['examples_total']}")
    print(
        f"Unclassified examples: {len(report['examples_unclassified'])}"
    )
    for line in report["examples_unclassified"]:
        print(f"  [UNCLASSIFIED-EX] {line}")
    # Acceptance gates per T-P1-353:
    # - <=5% question unclassified
    # - 0 example unclassified
    max_unclassified_q = int(report["questions_total"] * 0.05)
    ok = (
        len(report["questions_unclassified"]) <= max_unclassified_q
        and len(report["examples_unclassified"]) == 0
    )
    if ok:
        print("[OK] Coverage gates met.")
        return 0
    print("[FAIL] Coverage gates NOT met.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
