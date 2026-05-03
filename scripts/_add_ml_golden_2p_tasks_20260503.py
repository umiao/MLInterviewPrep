"""Add second-pass [MLI-GOLDEN-2P-*] tasks (T-P0-706..711) to MLI task_db.

Adds 6 tasks gated on completion of T-P0-705 (first-pass promote):
  706: SPEC update (S)
  707: K-Means golden update (M, dep 706)
  708..711: 4 sub-problem second-pass rewrites (M each, dep 706 + 707 + first-pass parent)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SPEC = "docs/methodology/ml_impl_note_rewrite_spec.md"

# ---------------------------------------------------------------------------
# Shared style block — what the second-pass actually applies.
# ---------------------------------------------------------------------------
COMMON_2P_RULES = """**Two new structural rules to apply (added to spec by T-P0-706 first)**:

**Rule 1 -- Shape-per-line decomposition**:
- Every numpy operation that produces a shape-changing intermediate gets its OWN line with a `# (shape)` comment.
- No 3+ op chains in one expression. Specifically: avoid patterns like `np.array([... for c in centers]).T` -- split into list build, np.array, transpose, each on its own line with shape annotation.
- Inside a code block, prefer "one vector at a time" decomposition: `(d,) -> (n, d) broadcast -> (n,) -> list of K -> (k, n) -> .T -> (n, k) -> argmin -> (n,)` shown as 7 lines, not chained into 1.
- Goal: a reader whiteboarding from this code can trace shapes step-by-step without mental simulation.

**Rule 2 -- End-to-end runnable test block**:
- Every implementation note ends with a `## End-to-end test` section (visible, NOT collapsed) placed AFTER the complete implementation (after main loop / predict / etc.).
- Block must be <=10 lines, use `np.random.rand` (or `np.random.randn`) with named constants `N, D` (and `K` where applicable).
- Must instantiate the class, run `fit()` (and `predict()` if applicable) ONCE, assert output shape with `assert ... .shape == (...)`.
- Must complete in <1s with no external dependencies.
- **Run-and-confirm during the task**: the autonomous session MUST execute the e2e block and confirm it runs cleanly before declaring the task done. Capture stdout to verify no exceptions.

**Per-task common AC**:
- All numpy ops producing shape-changing intermediates have their own line + `# (shape)` comment.
- No 3+ op chains in a single expression.
- Trailing `## End-to-end test` block exists, runs cleanly (verified by execution, not just code inspection).
- `len(notes)` stays AT or BELOW the first-pass byte target (no regression -- shape-per-line adds lines but pruning fluff compensates).
- Manual smoke on `/quick-index?section=ml` -- code block renders, e2e test block visually distinct.
- TL;DR unchanged from first pass (per user direction)."""


SPEC_DESC = f"""**Goal**: Update `{SPEC}` to add the two new structural rules from the second-pass discussion. This task gates the 5 downstream rewrites (T-P0-707..711) -- spec must be canonical source before they execute.

**Edits**:

1. **Add new section** between current "## Inline 注释规范" and "## 表格与对比":

   ### Shape-per-line decomposition

   每个产生形状变化的 numpy 操作单独一行，配 `# (shape)` 注释。禁止把 3+ 步链式操作压缩到一个表达式（典型反例：`np.array([... for c in centers]).T`）。"一次只算一个 vector" 是默认姿态——`(d,)` -> `(n, d)` broadcast -> `(n,)` -> list of K -> `(k, n)` -> `.T` -> `(n, k)` -> argmin -> `(n,)` 应该是 7 行 7 个 shape 注释，不是一行链式。

   目标：白板时读者按行追形状变化，不需要心算 numpy 隐式 broadcast / axis 推导。

2. **Add new section** between current "## 排版细节" and "## 验收清单":

   ### End-to-end test block

   每份笔记末尾必须以 `## End-to-end test` 章节收尾（visible, 不要折叠），位置在完整实现之后（main loop / predict 之类全部讲完）。约束：
   - <=10 行
   - 用 `np.random.rand` / `np.random.randn` + 命名常量 `N, D` (和 `K` 如适用)
   - instantiate class -> `fit()` -> 可选 `predict()` -> assert output shape
   - <1s 内跑完，无外部依赖
   - 改写时 autonomous session 必须真正执行此块（捕获 stdout 验证无异常），不止静态检查

3. **Update §验收清单** -- add 2 items:
   - [ ] 所有 shape-changing numpy 操作单独成行，配 `# (shape)` 注释
   - [ ] `## End-to-end test` 章节存在且执行通过（autonomous session 实跑过）

4. **Update §"4 道题的具体锚点"** -- per-problem note that the e2e block uses `(N, D)` for LR / KNN, `(N, D, K)` for K-Means (already golden), `(N, D)` binary y for LogReg, `(N, D)` for Geometric Median.

**Acceptance criteria**:
- Spec file gains 2 new top-level sections + 2 checklist items + 4-anchor updates.
- `git diff` shows clean structural edits, no whole-file rewrite.
- Spec still <10KB after edits (small addition only).
- Validate: `git log --oneline {SPEC}` shows the commit; `wc -l {SPEC}` increased reasonably (~20-40 lines).
"""


KMEANS_DESC = f"""**Goal**: Update K-Means golden (problem 1064) with the second-pass rules from `{SPEC}` (after T-P0-706 lands). Plus refine empty-cluster prose. TL;DR unchanged.

**Three concrete edits**:

**Edit 1 -- shape-per-line rewrite** of `_assign_to_nearest_center` and `_init_centers_plusplus` in the seed-script's `notes` content. Current `_assign_to_nearest_center` packs 3 ops in one expression:

```python
sq_dists = np.array([np.sum((data - c) ** 2, axis=1) for c in self.cluster_centers]).T  # (n, k)
```

Rewrite to:
```python
def _assign_to_nearest_center(self, data):
    # data: (n, d),  self.cluster_centers: (k, d)
    per_centroid = []
    for c in self.cluster_centers:                 # c: (d,)
        diff = data - c                            # (n, d)  -- broadcast
        sq_dist = np.sum(diff ** 2, axis=1)        # (n,)
        per_centroid.append(sq_dist)
    sq_dists = np.array(per_centroid).T            # list of K (n,) -> (k, n) -> .T -> (n, k)
    return np.argmin(sq_dists, axis=1)             # (n,)
```

Same treatment for `_init_centers_plusplus` -- show shape transitions per line.

**Edit 2 -- empty-cluster prose** (above the `_recompute_centers` code block, NOT in TL;DR):

> Empty cluster fallback 是 K-Means 的防御代码，不是常用路径。触发条件：(a) `K > 真实簇数` 时 iter>=1 mean 漂移可让某 cluster 失去所有成员；(b) 数据有重复行 + K-Means++ 抽到两个相同点。N>>K + 合理的 K 选择下两种都罕见。**实务上应在 K 选择阶段（elbow / silhouette）解决，不依赖 fallback 兜底**。

Plus add 1 bullet to "K 怎么选" cheat sheet item: `- 选错 K 的尾迹: 空簇 / silhouette 跌入负值 / SSE 曲线没拐点。`

**Edit 3 -- e2e test block** at the end (visible, after `predict`):

```markdown
## End-to-end test

```python
import numpy as np
N, D, K = 200, 3, 4
data = np.random.rand(N, D)
km = KMeans(num_clusters=K, random_state=42).fit(data)
assert km.cluster_labels.shape == (N,)
assert km.cluster_centers.shape == (K, D)
print(f"SSE = {{km.total_sse:.3f}}")
```
```

**Workflow**:
1. Read `{SPEC}` (post-706) to confirm rules.
2. Read current `problems.notes` for 1064 from DB (5,755 chars baseline).
3. Edit notes content in `scripts/seed_kmeans_golden_v1.py` (or wherever 1064's content lives -- audit `seed_kmeans_*` scripts; the doc-source is `docs/drafts/kmeans_golden_v1.md` and the seed reads from there).
4. Run the seed script (idempotent UPSERT).
5. **Run the e2e block** as a real Python file -- save to `/tmp/test_kmeans_e2e.py` and `python /tmp/test_kmeans_e2e.py`. Must exit 0.
6. Length check: `len(notes)` may grow modestly (shape-per-line adds lines) but should stay <=7,500 (a ~30% headroom over baseline 5,755).
7. Manual smoke on `/quick-index?section=ml` -> K-Means card.

**Acceptance criteria**:
- All 3 edits land verbatim per above (shape-per-line on 2 helpers, empty-cluster prose, e2e block).
- TL;DR is byte-identical to pre-edit (per user: "我觉得没必要改TLDR").
- E2e block executes cleanly when run as a Python file (exit 0, no exceptions).
- `len(notes)` <= 7,500.
- K-Means still has `is_golden=1` (don't accidentally clear).

{COMMON_2P_RULES}
"""


def _per_problem_desc(problem_id: int, name: str, baseline_bytes: int, target_bytes: int,
                      seed_script: str, e2e_template: str, specifics: str) -> str:
    return f"""**Goal**: Apply second-pass rules to problem {problem_id} ({name}) per `{SPEC}` (post-706). Anchored to the K-Means golden updated in T-P0-707.

**Edits**:

1. **Shape-per-line rewrite** for every numpy block in the note. Specifically:
{specifics}

2. **`## End-to-end test` block** at the very end (after all body sections):

```python
{e2e_template}
```

**Workflow**:
1. Read updated spec `{SPEC}`.
2. Read updated K-Means golden (problem 1064) for shape-per-line reference.
3. Read current `problems.notes` for {problem_id} (post-first-pass; ~{target_bytes} chars from T-P0-{problem_id - 1102 + 701}).
4. Edit notes content in `scripts/{seed_script}`.
5. Run seed script (idempotent UPSERT).
6. **Run the e2e block** -- save to `/tmp/test_{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}_e2e.py` and `python /tmp/test_..._e2e.py`. Must exit 0.
7. Length check: `len(notes)` <= {target_bytes} (no regression vs first-pass; ideally a slight reduction since we're trimming non-shape comments while adding shape annotations).
8. Manual smoke on `/quick-index?section=ml`.

**Acceptance criteria (specific)**:
- Every shape-changing numpy op in the note has its own line + `# (shape)` comment.
- No 3+ op chains in a single expression.
- E2e block executes cleanly (exit 0).
- `len(notes)` <= {target_bytes}.
- TL;DR byte-identical to first-pass version.

{COMMON_2P_RULES}
"""


LR_2P_DESC = _per_problem_desc(
    problem_id=1102,
    name="Linear Regression",
    baseline_bytes=9894,
    target_bytes=6900,
    seed_script="seed_linear_regression_20260502.py",
    e2e_template="""## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 200, 5
X = np.random.randn(N, D)
true_w = np.random.randn(D)
y = X @ true_w + 0.01 * np.random.randn(N)
lr = LinearRegression().fit(X, y)
preds = lr.predict(X)
assert preds.shape == (N,)
print(f"MSE = {np.mean((preds - y) ** 2):.4f}")
```""",
    specifics="""   - The closed-form code path: split `X.T @ X`, `X.T @ y`, `np.linalg.lstsq` into separate lines with shape annotations on each intermediate.
   - The GD code path: per-iteration gradient `(2/N) * X.T @ (X @ w - y)` should split: `pred = X @ w  # (N,)`, `residual = pred - y  # (N,)`, `grad = (2/N) * X.T @ residual  # (D,)`, `w = w - lr * grad  # (D,)`.
   - The closed-form vs GD comparison TABLE (from first pass) stays unchanged; just the code blocks under each variant get the shape-per-line treatment.""",
)


KNN_2P_DESC = _per_problem_desc(
    problem_id=1106,
    name="KNN",
    baseline_bytes=9246,
    target_bytes=6500,
    seed_script="seed_knn_20260502.py",
    e2e_template="""## End-to-end test

```python
import numpy as np
np.random.seed(0)
N_train, N_test, D, K = 100, 20, 4, 5
X_train = np.random.rand(N_train, D)
y_train = np.random.randint(0, 3, N_train)
X_test = np.random.rand(N_test, D)
knn = KNN(k=K).fit(X_train, y_train)
preds = knn.predict(X_test)
assert preds.shape == (N_test,)
print(f"Predicted classes: {np.unique(preds)}")
```""",
    specifics="""   - Distance computation section: split `data - x` (broadcast), squared, sum, sqrt onto separate lines with shape comments.
   - Top-K selection: `np.argpartition(dists, K)[:K]` gets a shape line; the resulting indices' shape `(K,)` annotated.
   - Voting: counts/weights array assembly and final argmax each get their own line.
   - The 3 split predict sections from first pass benefit MOST from this rule -- each section already has prose-before-code, now also has shape-per-line within code.""",
)


LOGREG_2P_DESC = _per_problem_desc(
    problem_id=1107,
    name="Logistic Regression",
    baseline_bytes=15964,
    target_bytes=11200,
    seed_script="seed_logistic_regression_20260502.py",
    e2e_template="""## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 200, 4
X = np.random.randn(N, D)
y = (X @ np.random.randn(D) > 0).astype(int)
lr = LogisticRegression().fit(X, y)
preds = lr.predict(X)
probs = lr.predict_proba(X)
assert preds.shape == (N,)
assert probs.shape == (N,)
print(f"Train accuracy = {(preds == y).mean():.3f}")
```""",
    specifics="""   - Sigmoid forward: `z = X @ w + b  # (N,)`, separate from the sigmoid call itself.
   - Stable BCE section (the dedicated section from first pass): the math derivation stays as-is (allowed exception per spec deviation rule), but the np code implementation MUST be shape-per-line.
   - GD update: `pred = sigmoid(z)`, `error = pred - y`, `grad_w = X.T @ error / N`, `grad_b = error.mean()` -- each on its own line with shape.
   - Multi-class softmax (if covered): explicit shape transitions for `(N, K)` logits -> softmax -> per-class CE loss.""",
)


GEOMED_2P_DESC = _per_problem_desc(
    problem_id=1108,
    name="Geometric Median",
    baseline_bytes=9723,
    target_bytes=6800,
    seed_script="seed_geometric_median_20260502.py",
    e2e_template="""## End-to-end test

```python
import numpy as np
np.random.seed(0)
N, D = 50, 3
points = np.random.rand(N, D)
gm = GeometricMedian().fit(points)
assert gm.median_.shape == (D,)
print(f"Geometric median: {gm.median_}")
print(f"Mean for comparison: {points.mean(axis=0)}")
```""",
    specifics="""   - Weiszfeld iteration: `diffs = points - x_t  # (N, D)`, `dists = np.linalg.norm(diffs, axis=1)  # (N,)`, `weights = 1 / dists  # (N,)`, `x_next = (weights[:, None] * points).sum(axis=0) / weights.sum()  # (D,)` -- each on its own line.
   - Vardi-Zhang degenerate-handling branch: shape-per-line for the on-data-point detection + the modified update.
   - The variant comparison TABLE (from first pass) stays unchanged.
   - Title rename done in T-P0-704; second pass does NOT redo it.""",
)


def main() -> int:
    cmds = [
        # ----- adds -----
        {"cmd": "add", "title": "[MLI-GOLDEN-2P-SPEC] Update ml_impl_note_rewrite_spec.md: shape-per-line + e2e-test-block rules",
         "priority": "P0", "complexity": "S", "description": SPEC_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-2P-KMEANS] K-Means golden (1064) second pass: shape-per-line + e2e block + empty-cluster prose",
         "priority": "P0", "complexity": "M", "description": KMEANS_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-2P-LR] Linear Regression (1102) second pass: shape-per-line + e2e block",
         "priority": "P0", "complexity": "M", "description": LR_2P_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-2P-KNN] KNN (1106) second pass: shape-per-line + e2e block",
         "priority": "P0", "complexity": "M", "description": KNN_2P_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-2P-LOGREG] Logistic Regression (1107) second pass: shape-per-line + e2e block",
         "priority": "P0", "complexity": "M", "description": LOGREG_2P_DESC},
        {"cmd": "add", "title": "[MLI-GOLDEN-2P-GEOMED] Geometric Median (1108) second pass: shape-per-line + e2e block",
         "priority": "P0", "complexity": "M", "description": GEOMED_2P_DESC},
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
