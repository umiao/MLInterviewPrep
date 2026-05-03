"""Tighten descriptions on T-P0-701..705 to inline the meta-prompt's core principles.

Throwaway helper. Each rewrite task gets (1) a shared "style invariants" block that
captures the central "Why in prose, What in code" axis plus all binding rules, and
(2) per-problem clarifications on which spec rule cuts where.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = "docs/methodology/ml_impl_note_rewrite_spec.md"
GOLDEN = "docs/drafts/kmeans_golden_v1.md (problem 1064)"

# ---------------------------------------------------------------------------
# Shared style-invariants block — copied verbatim into each rewrite task so an
# autonomous session reading only the task description has the complete rule
# set without re-interpreting the spec.
# ---------------------------------------------------------------------------
STYLE_INVARIANTS = """**Style invariants from `""" + SPEC + """` (AC fails if any violated)**

**Central axis -- "Why in prose, What in code"**:
- Algorithm motivation, geometric intuition, and contrast reasoning go in PROSE BEFORE each code block (1-2 sentences).
- Inside code blocks, the ONLY allowed comments are: shape annotations (`# (n, k)`), step/criterion anchors (`# Step 2`, `# Criterion 3: max iter`), edge cases (`# else: empty cluster fallback`), numerical hints (`# avoid log(0)`).
- Forbidden inside code: algorithm explanations, multi-line comment paragraphs, mixed-CN/EN long sentences, repetition of the prose above. If you see yourself writing inline math-explainer comments, lift them into 1-2 lines of prose ABOVE the code.

**Section granularity = "independently whiteboardable"**:
- `__init__` / class skeleton standalone (one section).
- Each helper standalone: init / E-step / M-step / objective / utility / fit / predict each get their own section.
- Multiple variants of the SAME concept (e.g., uniform vs weighted KNN; vanilla vs ++) live in the SAME section, separated by `**bold subtitle**` -- NOT split into separate sections.
- Main loop standalone, with `# Step N` or `# Criterion N` anchor comments threading the stopping conditions.
- `predict()` standalone even if 1-2 lines.
- Anti-pattern: helpers stuffed into one giant class block. That breaks "whiteboard a single section" usability.

**TL;DR (5-7 lines, blockquote with `>` on every line)**:
- Must enable a reader to recap the algorithm WITHOUT reading anything else.
- Required content: positioning (one line), core loop steps (numbered), edge / degenerate handling, complexity ($O(...)$).
- If the algorithm has a non-typical "soul" (e.g., LR's numerical stability), call it out in TL;DR.

**Variant comparison**:
- Always a TABLE, never prose paragraphs.
- <=5 columns, <=12 chars per cell, headers chosen from {选择方式, 失败模式, 实践默认值, 理论保证, 复杂度}.
- ONE sentence below the table answering "what's the essential difference / when to prefer which".

**Cheat sheet (面试追问)**:
- Format: `> **Q: question text**` followed by 1-3 bullets, each <=2 lines.
- If a Q would need a paragraph, EITHER promote to a body section OR delete -- it does not belong in cheat sheet.

**Typography**:
- All math (including inline complexity) wrapped in `$$...$$`. No bare `$...$`.
- Key terms first occurrence: `**bold**`.
- Algorithm names, library names, variable names: backticks.
- Section dividers: `---`.
- Lists use `-` (never `*`).
- No emoji anywhere.

**Aggressive deletion (do not hesitate)**:
- Paper citations, years, author names.
- "When else would you use X" pedagogical stretch paragraphs.
- "关键要点" / "key takeaways" recap blocks (always duplicate intro).
- Full mathematical proofs (keep only the result formula as a one-liner).
- Multi-line teaching comments inside code.
- Length floor: notes byte length must be at LEAST 30% shorter than baseline. If you fall short, you almost certainly haven't deleted enough -- find more.

**Deviation rule (the ONLY two legitimate exceptions)**:
1. Algorithm's soul lives in a non-typical place (e.g., LR's stable BCE deserves a dedicated section) -- must surface in TL;DR explicitly.
2. A specific followup is high-frequency for THIS algorithm and 1-2 lines aren't enough -- promote to a body section, do NOT stuff into cheat sheet.

**Doubt rule**: when uncertain whether to keep a passage, default to DELETE.
"""


def _build_lr() -> str:
    return f"""**Goal**: Rewrite problem 1102 (Linear Regression) notes to match the K-Means golden style ({GOLDEN}). Spec: `{SPEC}`.

**Per-problem anchors (from spec section "Linear Regression")**:
- The PRIMARY structure is a comparison TABLE between closed-form and GD -- NOT two side-by-side independent code blocks. Treat them as one method with two implementations, contrasted on:
  - complexity ($O(d^3)$ vs $O(n d T)$)
  - numerical stability (QR / SVD vs learning-rate tuning)
  - scalability (large $d$ -> GD wins)
- Closed-form result: keep ONLY the one-line conclusion $\\hat\\beta = (X^TX)^{{-1}}X^Ty$. Do NOT reproduce the full least-squares derivation.
- Code: use `np.linalg.lstsq(X, y, rcond=None)` (the existing seed already does this -- 1-line prose-before-code explains "why not `np.linalg.inv`": numerical stability via SVD).
- Followups (cheat sheet): regularization closed-form differences (Ridge has $(X^TX+\\lambda I)^{{-1}}$, Lasso has none); collinearity -> SVD / pseudo-inverse; when normal equation is singular.

{STYLE_INVARIANTS}

**Workflow**:
1. Audit `db://1102` propagation: `scripts/content_meta_anc_inventory_hub.py` line 89 has a summary cell describing this problem ("$w = (X^T X)^{{-1}} X^T y$, np.linalg.lstsq 不显式求逆"). Verify post-rewrite the cell is still factually accurate; if it drifts, edit + re-run that hub seed atomically with this task.
2. Read current `problems.notes` for 1102 (baseline 9,894 chars).
3. Edit notes content in `scripts/seed_linear_regression_20260502.py`.
4. Run the seed script (idempotent UPSERT).
5. Length check: `len(notes)` <= 6,900 (>=30% reduction).
6. Manual smoke: `http://localhost:5173/quick-index?section=ml` -> click Linear Regression -> all sections render, no KaTeX `ParseError`, code highlighted, table renders, cheat sheet blockquotes render.

**Acceptance criteria**:
- All style invariants above hold (literal byte-level audit, not "looks fine").
- Closed-form vs GD presented as table, not two parallel code blocks.
- `len(notes)` <= 6,900.
- Hub doc line 89 summary still accurate (or updated atomically).
- Manual smoke passes on `/quick-index?section=ml`.
"""


def _build_knn() -> str:
    return f"""**Goal**: Rewrite problem 1106 (KNN + Weighted) notes to match K-Means golden style ({GOLDEN}). Spec: `{SPEC}`.

**Per-problem anchors (from spec section "KNN")**:
- KNN has NO training loop -- `fit()` is just store-data (single-line section is fine). The substance is in `predict()`. Split predict into THREE standalone sections, each with 1-2 lines of prose explaining WHAT/WHY before the code:
  1. distance computation (broadcasted euclidean)
  2. top-K selection (`np.argpartition` for $O(n)$ vs full sort)
  3. voting / weighted average
- Variants live in the voting section as `**bold subtitle**`: uniform vs distance-weighted ($w_i = 1/d_i$ or $1/d_i^2$), classification vs regression weighting differences. Variant comparison TABLE summarizes them.
- Followups (cheat sheet): K odd to avoid ties; curse of dimensionality (高维下距离趋同); KD-tree / Ball tree query $O(\\log n)$; classification vs regression weighting differences.

{STYLE_INVARIANTS}

**Workflow**:
1. Audit `db://1106` propagation: confirm no production references outside the seed script (current grep shows none in `scripts/` besides the seed itself).
2. Read current `problems.notes` for 1106 (baseline 9,246 chars).
3. Edit notes content in `scripts/seed_knn_20260502.py`.
4. Run the seed script.
5. Length check: `len(notes)` <= 6,500 (>=30% reduction).
6. Manual smoke on `/quick-index?section=ml` -> KNN card.

**Acceptance criteria**:
- All style invariants above hold.
- `predict()` is split into 3 distinct sections (distance / top-K / vote), each with prose-before-code.
- Uniform vs weighted in ONE section via `**bold subtitle**` + a comparison TABLE with one-sentence summary.
- `len(notes)` <= 6,500.
- Manual smoke passes on `/quick-index?section=ml`.
"""


def _build_logreg() -> str:
    return f"""**Goal**: Rewrite problem 1107 (Logistic Regression) notes to match K-Means golden style ({GOLDEN}). Spec: `{SPEC}`. **Heaviest cut**: 15,964 -> ~11,200 (>=30%).

**Per-problem anchors (from spec section "Logistic Regression" -- this algorithm's soul is numerical stability)**:
- TL;DR MUST mention the stable BCE form: `np.logaddexp` or `log1p(exp(-|z|))`. This is the deviation-rule case 1 -- soul lives in non-typical place, declare it in TL;DR.
- DEDICATED section "Numerical stability" -- the RARE case where a math derivation IS allowed inline (per spec deviation rule). Show:
  - $\\log(1 + e^z)$ overflows when $z$ is large positive
  - the equivalent stable form $\\max(z, 0) + \\log(1 + e^{{-|z|}})$
  - 1-2 lines of prose above explaining WHY each form has different overflow behavior
- All other followups stay in cheat sheet (1-3 bullets each):
  - why LR has no closed form (sigmoid -> likelihood non-quadratic, not $X^TX$ form)
  - softmax extension (multi-class generalization)
  - class imbalance (class weight / focal loss)
  - L1 vs L2 regularization geometric meaning (sparsity vs shrinkage)

{STYLE_INVARIANTS}

**Workflow**:
1. Audit `db://1107` propagation: confirm no production references outside the seed script.
2. Read current `problems.notes` for 1107 (baseline 15,964 chars). Expect substantial cuts -- this is where the spec's "default to delete" rule earns the most.
3. Edit notes content in `scripts/seed_logistic_regression_20260502.py`.
4. Run the seed script.
5. Length check: `len(notes)` <= 11,200.
6. Manual smoke on `/quick-index?section=ml` -> Logistic Regression card. Confirm the stable-BCE math block renders cleanly in KaTeX.

**Acceptance criteria**:
- All style invariants above hold.
- TL;DR explicitly names the stable BCE form (`np.logaddexp` or `log1p(exp(-|z|))`).
- "Numerical stability" is its OWN top-level section (NOT buried in BCE inline comments). It is the ONLY section where math derivation appears.
- Followups (no closed form / softmax / imbalance / L1 vs L2) live in cheat sheet, 1-3 bullets each, never as body sections.
- `len(notes)` <= 11,200 (>=30% cut from 15,964).
- Manual smoke passes on `/quick-index?section=ml`.
"""


def _build_geomed() -> str:
    return f"""**Goal**: Rewrite problem 1108 (Geometric Median) notes to match K-Means golden style ({GOLDEN}). Spec: `{SPEC}`. Includes a title rename across two surfaces.

**Per-problem anchors (from spec section "Geometric Median")**:
- TITLE RENAME (drop "1999" per spec): two surfaces.
  - DB title: currently `Geometric Median (Weber 问题, L2 距离和最小)` -> rename to `Geometric Median (Weiszfeld + Vardi-Zhang variant)` via the seed script's `title=` field.
  - Frontend hardcoded label: `src/frontend/src/pages/QuickIndex.tsx` lines 74-80 currently shows "Geometric Median (Weiszfeld + Vardi-Zhang 1999)" -> change "1999" to "variant".
- Core formula (TL;DR or first section): Weiszfeld iteration $$x_{{t+1}} = \\frac{{\\sum w_i x_i}}{{\\sum w_i}}, \\quad w_i = \\frac{{1}}{{\\|x_i - x_t\\|}}$$
- What Vardi-Zhang fixes: $w_i \\to \\infty$ degeneracy when iterate lands on a data point. Implementation: detect hit + switch update formula. Show this in code with a clear `# else: anchor-point fallback` style comment.
- Variant TABLE: vanilla Weiszfeld vs Vardi-Zhang with column headers chosen from {{退化处理, 收敛性, 实现复杂度}}.
- Followups (cheat sheet): vs mean / coordinate-wise median ($L_2$ robust center vs $L_1$ per-axis median); why no closed form (一阶条件含 $x$ 的 norm); convergence (convex + Lipschitz -> Weiszfeld a.e. convergence). Reference the existing `db://262` Best Meeting Point problem for the $L_1$ contrast (already cited in current seed).

{STYLE_INVARIANTS}

**Workflow**:
1. Audit `db://1108` propagation: confirm no production references outside the seed script.
2. Read current `problems.notes` for 1108 (baseline 9,723 chars).
3. Edit BOTH the title field AND the notes content in `scripts/seed_geometric_median_20260502.py`.
4. Edit `src/frontend/src/pages/QuickIndex.tsx` to replace "1999" with "variant" in the hardcoded label (lines 74-80 area).
5. Run the seed script.
6. Length check: `len(notes)` <= 6,800 (>=30% reduction).
7. Manual smoke: `/quick-index?section=ml` shows label "Vardi-Zhang variant" (no "1999"); drawer title also says "variant"; renders cleanly.

**Acceptance criteria**:
- All style invariants above hold.
- Neither DB title NOR `QuickIndex.tsx` label contains "1999".
- Vanilla Weiszfeld vs Vardi-Zhang as a TABLE on {{退化处理, 收敛性, 实现复杂度}} with one-sentence summary.
- `len(notes)` <= 6,800.
- Manual smoke passes on `/quick-index?section=ml`.
"""


def _build_promote() -> str:
    return f"""**Goal**: After T-P0-701..704 pass their own AC, do a workspace-wide visual smoke pass and promote all 4 problems to `is_golden=1` with timestamp.

**Workflow**:
1. Visit `http://localhost:5173/quick-index?section=ml`. Click each of 1102, 1106, 1107, 1108. For each, verify on the RENDERED output (not just markdown source):
   - All KaTeX renders cleanly (no `ParseError` overlays).
   - All code blocks render with syntax highlighting.
   - Variant tables render as proper HTML tables (not raw markdown).
   - Followup cheat-sheet blockquotes render as styled quotes.
2. Cross-check the spec "验收清单" (9 items) against the RENDERED output for each of the 4 problems. The check is whether style invariants hold visually -- not just textually.
3. Hub-doc audit: re-read `scripts/content_meta_anc_inventory_hub.py` line 89 summary cell. If LR rewrite changed the closed-form discussion (e.g., dropped Ridge from main body), confirm the cell still represents what's actually in the note. Update + re-run the hub seed if drifted.
4. Write `scripts/mark_4_ml_problems_golden_20260503.py` modeled on `scripts/mark_kmeans_golden_20260502.py`. For each id in (1102, 1106, 1107, 1108), set `is_golden=1, golden_at=CURRENT_TIMESTAMP`. Idempotent (re-running is a no-op if already golden).
5. Run `python scripts/audit_uri_consistency.py` -- compare findings against pre-rewrite baseline. Zero new failures.

**Acceptance criteria**:
- All 4 problems show the golden badge on `/quick-index?section=ml`.
- Spec "验收清单" verified against RENDERED output for each of the 4 (not just source).
- Hub doc line 89 summary still accurate (or updated alongside, with the hub seed re-run).
- URI consistency audit: zero new failures vs pre-rewrite baseline.
- `mark_4_ml_problems_golden_20260503.py` is committed and idempotent.
"""


def main() -> int:
    cmds = [
        {"cmd": "update", "id": "T-P0-701", "description": _build_lr()},
        {"cmd": "update", "id": "T-P0-702", "description": _build_knn()},
        {"cmd": "update", "id": "T-P0-703", "description": _build_logreg()},
        {"cmd": "update", "id": "T-P0-704", "description": _build_geomed()},
        {"cmd": "update", "id": "T-P0-705", "description": _build_promote()},
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
