"""[META-ANC-5] Linear Regression drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the hand-derived
Linear Regression Meta AI-Native Coding question. Distills the closed-form
normal-equation derivation (with the dimension-alignment insight that explains
why X^T appears, not X), the three numpy implementations (inv / solve / pinv),
the O(nd^2 + d^3) complexity, and the high-frequency follow-up cluster
(Ridge / Lasso / collinearity / Batch-vs-SGD / unsorted-sparse) into one
description.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='normal_equation_lstsq'). The pattern column is the STABLE SLUG --
never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_linear_regression --> is embedded at the top of the
description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 4 second half, lines 267-286).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.company_tags import ProblemCompanyTag  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

SLUG = "meta_anc_linear_regression"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "normal_equation_lstsq"
TITLE = "Meta AI-Native Coding - Linear Regression (closed-form X^TX + Ridge/Lasso/SGD follow-ups)"
DIFFICULTY = "medium"
CATEGORY = "ml_coding"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "Meta AI-Native Coding",
    "normal equation",
    "closed-form",
]

DESCRIPTION = SENTINEL + r"""

# Linear Regression -- Meta AI-Native Coding

> **题型**: 给点集, 最小化 MSE, 手推最小二乘 normal equation 的 closed-form 解并实现.
> **场景**: Meta AI-Native Coding MLE / 实习向. 考的不是会不会调 sklearn, 而是能不能自己推导 + 讲清楚每个 numpy API 背后是什么数值算法.
> **AI 协同**: 让 AI 推导导数 + 给 closed-form 模板没问题; 但 "$X^T$ 是为了维度对齐" 这种洞察必须自己讲——这是这题的 senior signal.

完整推导 ($X^T X w = X^T y$), 四种 numpy 实现的数值稳定性对比 (`inv` / `solve` / `lstsq` / `pinv`), `LinearRegression` 类双路径实现 (closed-form + full-batch GD), Ridge / Lasso / 共线 / Batch-Mini-SGD 等高频 follow-up——见下方**题解笔记**.
"""


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines down to 2. Forbids accidental [UPDATED] reports caused
    by trailing-whitespace drift or platform line-ending differences.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _assert_required_keywords(description: str) -> None:
    """Abort if any REQUIRED-KEYWORD is missing from the description."""
    for kw in REQUIRED_KEYWORDS:
        if kw not in description:
            raise RuntimeError(
                f"[META-ANC-5] missing keyword {kw!r} -- regenerate"
            )


def _assert_no_emoji(description: str) -> None:
    """Project rule: no emoji characters in content."""
    for ch in description:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1FAFF
            or 0x1F000 <= cp <= 0x1F2FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"[META-ANC-5] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_linear_regression() -> int:
    """Insert or update the Linear Regression drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-5] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-5] expected Meta company_id=31, got {company_id}"
            )
        print(f"[OK] target company: id={company_id} name='Meta'")

        existing = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .first()
        )

        normalized_new = _normalize(DESCRIPTION)

        if existing is None:
            problem = Problem(
                title=TITLE,
                description=DESCRIPTION,
                difficulty=DIFFICULTY,
                pattern=PATTERN,
                category=CATEGORY,
                source=SOURCE,
                description_source=DESCRIPTION_SOURCE,
                is_completed=False,
                comfort_level=0,
            )
            db.add(problem)
            db.flush()
            pid = int(problem.id)
            print(
                f"[INSERT] problems id={pid} title={TITLE!r} "
                f"len={len(DESCRIPTION)}"
            )
        else:
            pid = int(existing.id)
            normalized_old = _normalize(existing.description or "")
            if normalized_old == normalized_new:
                print(
                    f"[NOOP] problems id={pid} description "
                    f"semantically identical (len={len(DESCRIPTION)})"
                )
            else:
                old_len = len(existing.description or "")
                existing.description = DESCRIPTION
                existing.title = TITLE
                existing.difficulty = DIFFICULTY
                existing.category = CATEGORY
                existing.description_source = DESCRIPTION_SOURCE
                print(
                    f"[UPDATED] problems id={pid} old_len={old_len} "
                    f"new_len={len(DESCRIPTION)} "
                    f"delta={len(DESCRIPTION) - old_len:+d}"
                )

        existing_tag = (
            db.query(ProblemCompanyTag)
            .filter(
                ProblemCompanyTag.problem_id == pid,
                ProblemCompanyTag.company_id == company_id,
            )
            .first()
        )
        if existing_tag is None:
            tag = ProblemCompanyTag(
                problem_id=pid,
                company_id=company_id,
                relevance="core",
                source="manual",
                notes="Meta AI-Native Coding 2026-05-01 inventory",
            )
            db.add(tag)
            print(
                f"[INSERT] problem_company_tags problem_id={pid} "
                f"company_id={company_id} relevance=core"
            )
        else:
            print(
                f"[NOOP] problem_company_tags problem_id={pid} "
                f"company_id={company_id} already present"
            )

        db.commit()

        final = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .one()
        )
        print(
            f"[VERIFY] problems id={final.id} pattern={final.pattern!r} "
            f"source={final.source!r} desc_len="
            f"{len(final.description or '')}"
        )
        return int(final.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upsert_meta_anc_linear_regression()
