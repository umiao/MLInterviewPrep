"""One-shot task adder for the [MLI-GOLDEN-*] batch (4 ML notes + promote).

Throwaway helper (prefixed `_`). Adds 5 tasks via task_db.py batch.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = "docs/methodology/ml_impl_note_rewrite_spec.md"
GOLDEN_REF = "docs/drafts/kmeans_golden_v1.md (problem 1064 in DB)"

LR_DESC = f"""**Goal**: Rewrite problem 1102 (Linear Regression) notes per `{SPEC}`, matching the K-Means golden style (`{GOLDEN_REF}`).

**Per-problem anchors** (spec section "Linear Regression"):
- Closed-form vs GD as a comparison TABLE (not two side-by-side code blocks).
- Compare on: complexity ($O(d^3)$ vs $O(n d T)$), numerical stability (QR/SVD vs LR tuning), scalability (large d -> GD).
- Followups: regularization closed-form differences (Ridge has $(X^TX+\\lambda I)^{{-1}}$, Lasso doesn't), 共线性 -> SVD/pseudo-inverse, normal equation 何时奇异.
- Drop full least-squares derivation; keep only $\\hat\\beta = (X^TX)^{{-1}}X^Ty$ as conclusion line.

**Workflow**:
1. Audit propagation: `db://1102` is referenced in `scripts/content_meta_anc_inventory_hub.py` line 89 summary cell. Confirm rewrite leaves that summary accurate; if not, edit hub script too and re-run it.
2. Read current `problems.notes` for 1102 (9,894 chars) to establish baseline.
3. Edit `scripts/seed_linear_regression_20260502.py` notes content.
4. Run the seed script (idempotent UPSERT).
5. Length check: notes byte length <= 6,900 (>=30% reduction from 9,894).
6. Visual smoke test on `http://localhost:5173/quick-index?section=ml` -> Linear Regression card -> renders without KaTeX errors.

**Acceptance criteria**:
- All 9 items in spec "验收清单" pass.
- Closed-form vs GD presented as a table, not two side-by-side code blocks.
- `len(notes)` <= 6,900.
- Hub doc line 89 summary still factually accurate (or updated atomically).
- Manual smoke: `/quick-index?section=ml` -> click Linear Regression -> all sections render.
"""

KNN_DESC = f"""**Goal**: Rewrite problem 1106 (KNN + Weighted) notes per `{SPEC}`, matching K-Means golden style (`{GOLDEN_REF}`).

**Per-problem anchors** (spec section "KNN"):
- `fit()` is just store-data; main code lives in `predict()`. Split predict into THREE sections: distance computation / top-K selection / voting.
- Variant table: uniform vs distance-weighted ($w_i = 1/d_i$ or $1/d_i^2$).
- Followups: K odd to avoid ties, curse of dimensionality (高维下距离趋同), KD-tree / Ball tree ($O(\\log n)$ query), classification vs regression weighting differences.

**Workflow**:
1. Audit `db://1106` propagation: confirm no production references outside the seed script (current grep shows none in scripts/ besides the seed itself).
2. Read current `problems.notes` for 1106 (9,246 chars).
3. Edit `scripts/seed_knn_20260502.py` notes content.
4. Run the seed script.
5. Length check: notes byte length <= 6,500.
6. Visual smoke test on `/quick-index?section=ml` -> KNN card.

**Acceptance criteria**:
- All 9 items in spec "验收清单" pass.
- `predict()` is split into 3 sections (distance / top-K / vote).
- Uniform vs weighted is a TABLE with one-sentence summary.
- `len(notes)` <= 6,500.
- Manual smoke: `/quick-index?section=ml` -> click KNN -> renders cleanly.
"""

LOGREG_DESC = f"""**Goal**: Rewrite problem 1107 (Logistic Regression) notes per `{SPEC}`, matching K-Means golden style (`{GOLDEN_REF}`). This is the heaviest cut: 15,964 -> ~11,200.

**Per-problem anchors** (spec section "Logistic Regression"):
- TL;DR MUST mention stable BCE via `np.logaddexp` or `log1p(exp(-|z|))`.
- DEDICATED section "Numerical stability" (rare exception where math derivation is allowed): show $\\log(1+e^z)$ overflow at large $z$ + the equivalent $\\max(z,0) + \\log(1+e^{{-|z|}})$.
- Followups: why LR has no closed form (sigmoid -> likelihood non-quadratic), softmax extension, class imbalance (class weight / focal loss), L1/L2 geometric meaning.

**Workflow**:
1. Audit `db://1107` propagation: confirm no production references outside the seed script.
2. Read current `problems.notes` for 1107 (15,964 chars) -- expect significant cuts.
3. Edit `scripts/seed_logistic_regression_20260502.py` notes content.
4. Run the seed script.
5. Length check: notes byte length <= 11,200 (>=30% reduction).
6. Visual smoke test on `/quick-index?section=ml` -> Logistic Regression card.

**Acceptance criteria**:
- All 9 items in spec "验收清单" pass.
- TL;DR explicitly mentions stable BCE form.
- "Numerical stability" is its OWN section (not buried in BCE inline comments).
- `len(notes)` <= 11,200.
- Manual smoke: `/quick-index?section=ml` -> click Logistic Regression -> renders cleanly, including the stable-BCE math block.
"""

GEOMED_DESC = f"""**Goal**: Rewrite problem 1108 (Geometric Median) notes per `{SPEC}`, matching K-Means golden style (`{GOLDEN_REF}`). Includes title rename (drop "1999").

**Per-problem anchors** (spec section "Geometric Median"):
- TITLE RENAME: drop "1999". Two surfaces:
  - DB title: currently `Geometric Median (Weber 问题, L2 距离和最小)` -> rename to `Geometric Median (Weiszfeld + Vardi-Zhang variant)` via the seed script.
  - Frontend hardcoded label: `src/frontend/src/pages/QuickIndex.tsx` currently shows "Geometric Median (Weiszfeld + Vardi-Zhang 1999)" -> change "1999" to "variant".
- Core formula: Weiszfeld iteration $x_{{t+1}} = \\frac{{\\sum w_i x_i}}{{\\sum w_i}}, w_i = 1/\\|x_i - x_t\\|$.
- What Vardi-Zhang fixes: $w_i \\to \\infty$ degeneracy when iterate lands on a data point. Implementation: detect hit + switch update formula.
- Variant table: vanilla Weiszfeld vs Vardi-Zhang on (退化处理 / 收敛性 / 实现复杂度).
- Followups: vs mean / coordinate-wise median ($L_2$ robust center vs $L_1$ per-axis median), why no closed form (一阶条件含 $x$ 的 norm), 收敛性 (convex + Lipschitz -> Weiszfeld a.e. convergence).

**Workflow**:
1. Audit `db://1108` propagation: confirm no production references outside the seed script.
2. Read current `problems.notes` for 1108 (9,723 chars).
3. Edit `scripts/seed_geometric_median_20260502.py` -- BOTH the title field AND the notes content.
4. Edit `src/frontend/src/pages/QuickIndex.tsx` to update the hardcoded label (line ~74-80 area).
5. Run the seed script.
6. Length check: notes byte length <= 6,800.
7. Visual smoke test: index page label says "variant" not "1999"; drawer title also says "variant".

**Acceptance criteria**:
- All 9 items in spec "验收清单" pass.
- Neither DB title nor `QuickIndex.tsx` label contains "1999".
- Vanilla Weiszfeld vs Vardi-Zhang is a TABLE with one-sentence summary.
- `len(notes)` <= 6,800.
- Manual smoke: `/quick-index?section=ml` -> Geometric Median card label says "variant"; drawer renders cleanly.
"""

PROMOTE_DESC = """**Goal**: After T-A/B/C/D pass, do a workspace-wide visual smoke pass and promote all 4 problems to `is_golden=1` with timestamp.

**Workflow**:
1. Visit `http://localhost:5173/quick-index?section=ml`. Click each of 1102, 1106, 1107, 1108. Verify:
   - All KaTeX renders cleanly (no `ParseError` overlays).
   - Code blocks render with syntax highlighting.
   - Variant tables render.
   - Followup cheat-sheet blockquotes render.
2. Cross-check the spec "验收清单" against the rendered output (not just markdown source).
3. Audit `scripts/content_meta_anc_inventory_hub.py` line 89 summary cell -- confirm still accurate; update if not.
4. Write `scripts/mark_4_ml_problems_golden_20260503.py` (model after `scripts/mark_kmeans_golden_20260502.py`). Set `is_golden=1, golden_at=CURRENT_TIMESTAMP` for 1102, 1106, 1107, 1108. Idempotent.
5. Run `python scripts/audit_uri_consistency.py` -- no new failures.

**Acceptance criteria**:
- All 4 problems show the golden badge on `/quick-index?section=ml`.
- Spec "验收清单" verified against RENDERED output for all 4.
- Hub doc line 89 summary still accurate (or updated alongside, with the hub seed re-run).
- URI consistency audit passes (no new failures vs pre-rewrite baseline).
- New mark script committed and idempotent (re-running is a no-op on subsequent passes).
"""


def main() -> int:
    cmds = [
        {"cmd": "add", "title": "[MLI-GOLDEN-LR] Linear Regression (1102) golden-style rewrite per meta-prompt",
         "priority": "P0", "complexity": "M", "description": LR_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-KNN] KNN (1106) golden-style rewrite per meta-prompt",
         "priority": "P0", "complexity": "M", "description": KNN_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-LOGREG] Logistic Regression (1107) golden-style rewrite + dedicated numerical-stability section",
         "priority": "P0", "complexity": "L", "description": LOGREG_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-GEOMED] Geometric Median (1108) golden-style rewrite + drop '1999' from title (DB + QuickIndex.tsx)",
         "priority": "P0", "complexity": "M", "description": GEOMED_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-PROMOTE] Smoke test 4 rewrites on /quick-index?section=ml + mark all 4 is_golden=1",
         "priority": "P0", "complexity": "S", "description": PROMOTE_DESC},
    ]
    payload = json.dumps(cmds, ensure_ascii=False)
    res = subprocess.run(
        [sys.executable, ".claude/hooks/task_db.py", "batch", "--commands", payload],
        cwd=str(PROJECT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    sys.stdout.write(res.stdout)
    sys.stderr.write(res.stderr)
    return res.returncode


if __name__ == "__main__":
    sys.exit(main())
