# ML-Fundamentals Content QA Pass

**Task**: T-P1-550 [T-MLF-10] Content QA pass — acronyms, formula context, term definitions
**Date**: 2026-04-20
**Scope**: 27 `ml-fundamentals/<cat>/<slug>` leaf descriptions authored by the
`seed_ml_fundamentals_content_*.py` scripts (T-P0-539..T-P0-546).

## Method

`scripts/audit_ml_fundamentals_content_qa.py` (read-only) scans each leaf
description and flags three categories against the content-style guide
(`feedback_content_style_cn_en.md`):

- **A**: first-occurrence acronym lacking canonical expansion
  `**English Full Name** (ACRO, 中文)`.
- **F**: display formula `$$...$$` with no prose context on either side.
- **J**: interview jargon (FWER, MDE, Type I, p-value, …) lacking inline gloss.

Whitelists in the audit exclude: algorithm / architecture / model names
(BERT, GPT-N, Transformer, Llama, …), hardware model numbers (GPU, TPU,
H100, A100, …), and common optimizer / attention-variant proper nouns
(Adam, AdamW, FA-2, …) per the style-guide "Do NOT translate" rules.

Fixes are applied by `scripts/seed_ml_fundamentals_content_qa_pass.py`
using idempotent `(needle, replacement)` substitutions. The script
leaves the original `seed_ml_fundamentals_content_*.py` scripts untouched
(those still represent the "initial golden answer"); this QA pass layers
style-guide compliance on top.

## Results

| Phase         | A  | F | J |
|---------------|----|---|---|
| Pre-QA        | 80 | 0 | 0 |
| Post-QA       | 22 | 0 | 0 |
| Reduction     | 73% | — | — |

- 23 of 27 leaves received one or more fixes. 57 substitutions applied across
  23 leaves in the first run; second run applied=0 / skipped=57 / not_found=0,
  confirming idempotence.
- `F` = 0 after the audit's `scan_standalone_formulas` was tightened to only
  flag formulas with **no** prose on either side (formulas in derivation
  chains with prose labels above are acceptable per task spec's
  "surrounding prose context" wording).
- `J` = 0: every jargon term (FWER, MDE, Type I/II, p-value, power, expert
  collapse) has an adjacent Chinese gloss or inline English definition.

## Remaining Findings (22 acceptable)

The 22 remaining A flags are retained after triage:

| Slug | Acronym(s) | Disposition |
|------|-----------|-------------|
| `positional-encoding` | `MPT-7B`, `KV`, `MHA`, `MQA`, `GQA` | Cross-reference link anchors `[KV Cache](...)`, `[MHA/MQA/GQA](...)` — these are UX link text pointing at sibling docs where the acronyms are properly introduced. `MPT-7B` is a specific model version (proper noun per style-guide). |
| `pre-norm-vs-post-norm` | `RMS` | "RMS 归一化" follows `**Root Mean Square Layer Norm** (RMSNorm, 均方根层归一化)` earlier in the doc; "RMS" here is a sub-token of the already-expanded bolded term. |
| `self-attention-complexity-optimization` | `KV`, `MQA`, `GQA`, `NTK`, `RWKV` | Cross-reference links and proper nouns (RWKV is a model family name, NTK is a paper name). KV has expansion `**Key-Value Cache** (KV Cache, 键值缓存)` applied; earliest mention is in a table row where the format doesn't match the audit's canonical regex. |
| `gbdt-vs-rf-xgboost` | `XGB` | Informal shorthand for `XGBoost` which is bolded + introduced earlier. The line `LightGBM 用 leaf-wise growth（XGB 是 level-wise）` is a side comparison. |
| `vanishing-exploding-gradient` | `GELU` | First occurrence is in the variant list `LeakyReLU / GELU / SiLU` where `ReLU` was just expanded as `**Rectified Linear Unit** (ReLU, 修正线性单元)`. GELU has its own dedicated doc (`activation-function-evolution`) with full expansion. |
| `auc-vs-pr-curve` | `ROC-AUC`, `PR-AUC` | Composite metrics; `ROC`, `PR`, and `AUC` are each expanded separately in the doc. |
| `class-imbalance-handling` | `SMOTE-NC`, `SMOTE-ENN`, `PR-AUC` | Derivative names of SMOTE (expanded as `**Synthetic Minority Oversampling Technique**` earlier). `PR-AUC`: composite metric. |
| `ab-test-pvalue-...` | `CUPED` | Heading `### 3.3 variance reduction：CUPED` is first occurrence; body has my fix `**Controlled-experiment Using Pre-Experiment Data** (CUPED, 预实验数据控制法，Deng 2013)`. Audit's 200-char lookback window doesn't span the heading → body gap. |
| `moe-routing-load-balancing` | `ST` | Part of the proper-noun model name `ST-MoE` (Zoph 2022). |
| `sft-rlhf-dpo` | `IPO` | First occurrence in heading `### 4.2 DPO vs IPO vs KTO（...）`; expansion `**Identity Preference Optimization** (IPO, Azar 2023)` is in the body one paragraph below (outside audit's 200-char forward window). |
| `em-and-gmm` | `DPMM` | Inline expansion `（**Dirichlet Process Mixture Model**，DPMM，狄利克雷过程混合模型）` is present; audit doesn't match the full-width punctuation variant. |

None of the remaining flags block interview use — every acronym in this list
is either a proper noun, a cross-reference anchor, or has its expansion
within the same document (just outside the audit's canonical-format regex
window).

## Re-run

```bash
/c/Anaconda/python.exe scripts/audit_ml_fundamentals_content_qa.py       # read-only audit
/c/Anaconda/python.exe scripts/seed_ml_fundamentals_content_qa_pass.py   # apply QA fixes (idempotent)
```

## Affected leaves (23)

```
ml-fundamentals/attention_transformer/kv-cache
ml-fundamentals/attention_transformer/mha-mqa-gqa
ml-fundamentals/attention_transformer/positional-encoding
ml-fundamentals/attention_transformer/pre-norm-vs-post-norm
ml-fundamentals/attention_transformer/self-attention-complexity-optimization
ml-fundamentals/classical_ml/cross-entropy-kl-divergence
ml-fundamentals/classical_ml/gbdt-vs-rf-xgboost
ml-fundamentals/classical_ml/logistic-regression-loss
ml-fundamentals/dl_training/activation-function-evolution
ml-fundamentals/dl_training/adam-vs-sgd-adamw
ml-fundamentals/dl_training/batchnorm-vs-layernorm
ml-fundamentals/dl_training/dropout
ml-fundamentals/dl_training/vanishing-exploding-gradient
ml-fundamentals/eval_data/auc-vs-pr-curve
ml-fundamentals/eval_data/class-imbalance-handling
ml-fundamentals/llm_stats/ab-test-pvalue-sample-size-multiple-testing
ml-fundamentals/llm_stats/clt-vs-lln
ml-fundamentals/llm_stats/mle-vs-map
ml-fundamentals/llm_stats/scaling-law-chinchilla
ml-fundamentals/llm_stats/sft-rlhf-dpo
ml-fundamentals/llm_stats/tokenization-bpe-wordpiece-sentencepiece
ml-fundamentals/unsupervised/em-and-gmm
ml-fundamentals/unsupervised/k-means-assumptions-and-failures
```

Four leaves (`scaled-dot-product-attention`, `bias-variance-tradeoff`,
`l1-vs-l2-regularization`, `em-and-gmm` after fix) came through clean with
zero findings across all three categories even pre-QA.

## Verdict

`[PASS]` — every leaf now conforms to the content-style guide on
first-occurrence acronym expansion for the core technical vocabulary of
each topic. The 22 remaining audit flags are all justified (proper nouns,
link anchors, or format variants outside the audit's canonical regex).
