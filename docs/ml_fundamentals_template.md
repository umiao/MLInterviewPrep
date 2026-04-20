# ML Fundamentals Portal — Canonical Content Template

**Status**: v1 (post Cat 1-2 T1 fill, T-P0-540 barrier checkpoint)
**Scope**: Authoring template for the 27 leaves under `framework_nodes` whose `path` starts with `ml-fundamentals/`. Distinct from but compatible with `docs/framework_node_content_template_20260416.md` (the broader 47-node KG schema): ML-Fundamentals leaves are interview-question-sized units, so they lean on a fixed 5-section narrative rather than the always-visible + drawer split.
**Source of truth for content**: `data/ml_fundamentals_inventory.yaml` (27 items, per-item `acronyms_to_expand` + `cleanup_notes`).
**Date**: 2026-04-20

---

## 1. The contract a leaf description makes with its reader

A reader landing on `/ml-fundamentals?cat=<category>&slug=<slug>` (T-P0-547 wires the deep-link) and opening the drawer should be able to say within ~2 minutes of reading top-to-bottom:

> *"I can answer this in an interview: setup → derivation → why it works → what they'd push on next."*

The 5 sections below exist to make that contract uniform across all 27 leaves. T1 leaves (Cat 1-4) do verbatim cleanup of the source attachment and may use slightly different section titles; T2/T3 leaves (Cat 5-7) and any new authoring should follow this canonical structure.

---

## 2. Canonical 5-section structure

Each leaf description starts with `# <Title (Chinese primary, English in parens if helpful)>` and contains the following 5 numbered H2 sections **in order**. Section bodies use Chinese prose with English preserved for math, algorithm names, and acronyms.

### Section 1 — `## 1. 问题设定`
- **Purpose**: Define the problem, the random sources, the assumed distributions, and any notation the rest of the page uses. The "what" before any "why".
- **Required content**:
  - Problem statement in 1-3 sentences.
  - Notation table or inline definitions for every symbol used later (e.g., $f(x)$, $\hat{f}_D$, $\bar{f}$, $\sigma^2$, $D$).
  - First-occurrence acronym expansion per `inventory.yaml acronyms_to_expand` using format `**English full term** (acronym, 中文译名)` — e.g., `**Independent and Identically Distributed** (IID, 独立同分布)`.
- **Length**: ~300-600 chars.
- **Example (from #1 Bias-Variance)**:
  > 真实数据生成过程：$y = f(x) + \epsilon, \ E[\epsilon]=0, \ \text{Var}(\epsilon)=\sigma^2$。我们从分布中采样一个 **Independent and Identically Distributed** (IID, 独立同分布) 训练集 $D$...

### Section 2 — `## 2. 推导`
- **Purpose**: The math. Derive the central result the reader needs to know.
- **Required content**:
  - Step-by-step derivation. Every algebraic move ("加减 $\bar{f}$"，"展开后三个交叉项都为 0"，"由 sigmoid + CE 漂亮消去") must be visible — do NOT collapse to the result.
  - Boxed final result via `$$\boxed{\ldots}$$` so the reader can spot the key takeaway at a glance.
  - If the topic is algorithmic rather than analytic (e.g., #4 GBDT/RF/XGBoost), substitute "core algorithmic mechanism" — the residual-fit recursion, the 2nd-order Taylor split-gain, the closed-form leaf weight.
- **Length**: ~600-1500 chars (math-heavy).
- **Formula formatting**: see §3.

### Section 3 — `## 3. 物理意义 / 直觉`
- **Purpose**: Explain WHY the math is the right answer. The interviewer's "what does this term mean intuitively?" follow-up.
- **Required content**:
  - Per-term physical interpretation (e.g., "Bias² = 模型族表达能力不够；Variance = 同一族对训练扰动敏感；σ² = 数据本身的随机性").
  - Geometric / probabilistic / information-theoretic intuition where applicable (e.g., L1 ball corners, OLS ellipse contours, KL non-symmetry, AUC = Mann-Whitney U).
  - Connect back to first-principles ("for L2 the罚项 force decays to 0 as $w_i \to 0$, so it can never land on 0; L1 has constant force and a non-trivial subgradient interval at 0").
- **Length**: ~400-1000 chars.

### Section 4 — `## 4. 常见追问 / Tradeoffs`
- **Purpose**: The 2-5 questions an interviewer will ask after the canonical answer. Pre-empts them.
- **Required content** (mix as appropriate per topic):
  - Variants and edge cases (Elastic Net, Focal Loss, sliding-window HLL, label smoothing).
  - Tradeoffs (bias-variance under double descent, GBDT vs RF on noisy data, MSE-vs-CE for classification).
  - Common misconceptions ("'CMS only over-estimates' — but CMM with median estimator is no longer an upper bound").
  - Distinct subsections allowed (`### Label smoothing 的信息论解释`，`### Distillation`，`### Wasserstein distance`) when 3+ follow-ups deserve their own headers.
- **Length**: ~500-1500 chars.

### Section 5 — `## 5. 参考` *(optional but recommended)*
- **Purpose**: Pointers to deeper resources, related leaves, or company-doc back-links.
- **Required content** (when present):
  - Cross-links to sibling ml-fundamentals leaves: `[L1 vs L2](/ml-fundamentals?cat=classical_ml&slug=l1-vs-l2-regularization)`.
  - Cross-links to other framework nodes when topic spans pillars: `详见 [Bias-Variance](/framework/67)`.
  - Company-doc back-links (if topic was first surfaced by a real interview): `(Pinterest senior MLE 复习 doc-58)`.
  - Seminal-paper citations only when they add value an interviewer might quiz on (Flajolet HLL 2007, Friedman GBDT 2001).
- **Length**: ≤ 500 chars. **Omit the section entirely** if no substantive references exist — empty stubs are worse than no section.

---

## 3. Formatting rules

### 3.1 KaTeX math
- **Inline**: `$...$` (e.g., `$y = f(x) + \epsilon$`).
- **Display**: `$$...$$` on its own line, surrounded by blank lines. Display blocks should be the only thing on that line.
- **Boxed final result**: use `$$\boxed{\ldots}$$` for the section's takeaway equation.
- **Backslashes**: in Python seed scripts, use raw strings `r"""..."""` so backslashes are literal.
- **No triple-rendering**: the source attachment renders every formula 3× (LaTeX + glyph dump + glyph dump). Collapse to a single KaTeX block.

### 3.2 Acronym expansion
- **First-occurrence format**: `**English full term** (acronym, 中文译名)` — bold English + acronym in parens + Chinese gloss.
  - Example: `**Karush-Kuhn-Tucker** (KKT, 一阶最优性条件)`, `**Mean Squared Error** (MSE, 均方误差)`.
- **List authoritative acronyms in `inventory.yaml acronyms_to_expand`** for each leaf — e.g., MSE/IID for #1; SMOTE/AUC/PR/ROC for #5.
- **Subsequent mentions**: bare acronym (`KKT 稳定条件...`).
- **Algorithm names not in the acronym list** (XGBoost, LightGBM, GBDT) still get one-time expansion: `**XGBoost** (XGBoost, 极致梯度提升)`.

### 3.3 Section header convention
- **Always numbered**: `## 1. ...`, `## 2. ...`, etc. The number in the heading lets the reader quickly find a referenced section in conversation.
- **Section titles in Chinese**: `问题设定`, `推导`, `物理意义`, `常见追问`, `参考`. T1 verbatim-cleanup leaves may keep source-style headers (e.g., `## 2. 次梯度视角`); new authoring should match the canonical 5 names.
- **Sub-headers**: `### <topic>` for distinct follow-ups inside §4 — see #14 CE/KL §7 (`### Label smoothing 的信息论解释`，`### Distillation`，`### Focal loss`，`### Wasserstein distance`).

### 3.4 Language
- **Prose**: Chinese by default (per `feedback_content_style_cn_en`).
- **English preserved**: math (LaTeX), algorithm names at first mention (`**Stochastic Gradient Descent** (SGD, 随机梯度下降)`), library names (sklearn, XGBoost, LightGBM), complexity notation (`$O(n \log n)$`), code blocks.
- **Punctuation**: Chinese full-width punctuation in prose (，。：；！？) ; ASCII punctuation inside math, code, and acronym parens.

### 3.5 GFM tables
- Use GitHub-flavored markdown tables for compact comparisons (XGBoost-vs-GBDT delta table, AUC-vs-PR-AUC under imbalance). Include a header row + alignment row.
- Tables MUST render in the drawer (verified during T-P0-540 dev-server review).

### 3.6 Code blocks
- Use ```` ```python ```` fences for runnable snippets.
- Keep code ≤ 30 lines; longer snippets belong in a separate `## 推导` step or on a sibling node.
- Add 2-3 line commentary after each code block — never leave code unexplained.

---

## 4. Boundary conditions & guardrails

### 4.1 What MUST be in every leaf
1. `# <Title>` H1 at the top, exactly one.
2. At least one `$...$` or `$$...$$` math block (validate_content() guard in seed scripts).
3. At least one `## ` section header (validate_content() guard).
4. First-occurrence acronym expansion per inventory.

### 4.2 What MUST NOT be in a leaf
- HTML comments or machine-parseable markers (`<!-- KG:67:reference -->`). Use prose links instead.
- Drawer markers (`## Drawer: derivation`). ML-Fundamentals leaves are flat — no nested drawers. The whole description renders inside the leaf's framework drawer; no further progressive disclosure is needed at this level.
- Verbatim duplication of the source attachment's triple-rendered formulas (collapse to single KaTeX block).
- Emojis (per project CLAUDE.md: never use emoji characters in code, docs, configs, or hook output).

### 4.3 Length budget (soft)
- **T1 leaf** (Cat 1-4): ~1500-3500 chars total. Cat 1-2 actuals: 1419-3304 chars per the T-P0-539 fill.
- **T2 leaf** (Cat 5 attention/transformer): ~3000-5000 chars. Concept density is higher; expect more derivation in §2.
- **T3 leaf** (Cat 6-7 SFT/RLHF/MoE/MLE-MAP): ~4000-7000 chars. These get Y-depth treatment; §2 may have multi-part derivations and §4 typically has 4-6 sub-headers.

If a leaf legitimately blows past the upper end (e.g., #21 SFT/RLHF/DPO ~ 7500 chars), file the overage as a calibration signal during T-P0-543 and document under `## 5. 参考` why depth was warranted.

### 4.4 Tier-coupled cleanup workload
- **T1 (verbatim cleanup)**: dedupe triple-rendered formulas; expand first-occurrence acronyms; preserve every derivation step from source. No new content authoring.
- **T2 (moderate reformat)**: T1 + restructure into the canonical 5-section ordering if source uses a different layout; add §3 (物理意义) if source jumped from setup to follow-ups.
- **T3 (deep expansion)**: full canonical authoring against the template; source may be only a 1-2 paragraph sketch. Y-depth items (#21 SFT/RLHF/DPO, #22 MoE, #25 MLE vs MAP) need full §2 derivations + §4 with 4-6 follow-up sub-headers.

---

## 5. Idempotent seed-script convention

Every leaf description is owned by exactly one seed script. Convention from T-P0-539:

```python
# scripts/seed_ml_fundamentals_content_<cat>.py
LEAVES: dict[str, tuple[str, str]] = {
    "ml-fundamentals/<category>/<slug>": (placeholder, new_description),
    ...
}
```

Required guards (copy from `seed_ml_fundamentals_content_cat12.py`):
- **Pre-flight `validate_content()`**: every staged description has `$` math + `## ` header before any DB write.
- **Conflict guard**: if `current_description` is neither the placeholder (`TODO[MLF-<slug>]`) nor the new content, abort with `[CONFLICT]` — never overwrite a human-edited intermediate state.
- **SHA-256 audit**: log pre/post hash of the affected (path, description) pairs.
- **Idempotency**: second run yields `updated=0 skipped=N`. Hash unchanged across re-runs.
- **Acceptance counts**: `[FAIL]` if `updated + skipped != expected_leaf_count`.

Re-run is the test: `python scripts/seed_ml_fundamentals_content_<cat>.py` should print `updated=0` on the second invocation and the post-hash must match the first run's post-hash.

---

## 6. Frontend rendering contract (verified during T-P0-540 dev-server review)

The ML-Fundamentals page (`MLFundamentals.tsx`, T-P0-547) renders each leaf's `framework_nodes.description` inside the drawer using the same Markdown stack as the rest of the app:

- `react-markdown` + `remark-gfm` + `remark-math` + `rehype-katex`
- `rehype-katex` MUST receive `$...$` (inline) and `$$...$$` (display) — no `\(...\)` or `\[...\]`.
- `remark-gfm` enables tables, strikethrough, task lists, autolinks.
- KaTeX CSS must be imported in the page (already loaded globally per existing framework drawer).

**Manual review checklist (user fills during this barrier)**:
- [ ] KaTeX inline math renders cleanly (no raw `$` visible)
- [ ] KaTeX display blocks center properly with adequate vertical spacing
- [ ] `\boxed{...}` renders the takeaway box
- [ ] Bold `**English** (acronym, 中文)` renders bold + parens correctly
- [ ] GFM tables align (XGBoost-vs-GBDT comparison in #4, AUC-vs-PR comparison in #6)
- [ ] Numbered section headers `## 1. 问题设定` render at correct H2 size
- [ ] Sub-headers `### Label smoothing` render at H3 (smaller than H2)
- [ ] Long Chinese prose lines wrap correctly at the drawer width
- [ ] No double-rendering of formulas (sign that the source's triple-render wasn't fully collapsed)

If the dev-server review surfaces issues, fix them BEFORE approving the template — downstream T-MLF-04...T-MLF-06d will inherit any rendering bugs at scale.

---

## 7. Worked example reference

The 7 Cat 1-2 leaves shipped in T-P0-539 (commit `9454cea`) are the reference implementation:

| ID | Slug | Section count | Length | Special features |
|---|---|---|---|---|
| 1 | bias-variance-tradeoff | 4 | 1419 | Add-and-subtract $\bar{f}$ derivation |
| 2 | l1-vs-l2-regularization | 5 + deep-dive | 3304 | OLS normal eq + ellipse-contour deep-dive section |
| 3 | logistic-regression-loss | 5 | ~1900 | Sigmoid + CE gradient cancellation |
| 4 | gbdt-vs-rf-xgboost | 4 | ~2400 | XGBoost 2nd-order Taylor + closed-form leaf + split-gain table |
| 5 | class-imbalance-handling | 5 | ~2200 | 4-lever taxonomy + SMOTE pitfalls |
| 6 | auc-vs-pr-curve | 5 | ~2100 | AUC = Mann-Whitney U identity, PR-vs-ROC under imbalance |
| 14 | cross-entropy-kl-divergence | 7 + sub-headers | ~2900 | CE = H(P) + KL relation, forward vs reverse KL semantics |

These shipped with section names that vary slightly from the canonical 5 (T1 = verbatim source-style cleanup). New authoring (Cat 3-7) should converge on the canonical `问题设定 / 推导 / 物理意义 / 常见追问 / 参考` ordering wherever the source structure permits.

---

## 8. What this template explicitly does NOT decide

- **Per-leaf content** — that's owned by individual seed scripts (`seed_ml_fundamentals_content_<cat>.py`).
- **Sidebar / navItem placement** (T-P0-548).
- **Deep-link URL scheme** beyond `?cat=<category>&slug=<slug>` (T-P0-547).
- **Cross-pillar back-links** to non-ml-fundamentals framework nodes (Phase 4+ concern; for now use inline prose).
- **Search / filter UX** on the portal page itself — out of MLF-Phase-1 scope.

---

## Revision Log

- **v1 (2026-04-20)**: Initial canonical template, derived from the 7 Cat 1-2 leaves shipped in T-P0-539. Awaits user review during T-P0-540 barrier checkpoint before T-MLF-04...T-MLF-11 proceed.
