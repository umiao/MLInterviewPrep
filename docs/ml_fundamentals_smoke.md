# ML-Fundamentals Drawer Smoke Test

**Task**: T-P1-549 [T-MLF-09] KaTeX/drawer smoke test — all 27 drawers
**Date**: 2026-04-20
**Method**: Content-level validation of `framework_nodes.description` for every `ml-fundamentals/<cat>/<slug>` leaf (27 rows). Backend served via `uvicorn src.backend.main:app` on port 8765; GET `/api/framework/tree` returned 27 leaves matching the canonical inventory. Each body was checked for:

- **KaTeX**: balanced `$..$` and `$$..$$` delimiters; absence of incompatible `\(..\)` / `\[..\]`; presence of at least one math block (template invariant).
- **GFM table**: every `| --- |` separator row has a header above and body rows with consistent column counts.
- **Callout**: drawer contract (`markdownCallout.ts`) recognizes `> **GOOD|BAD|NOTE**:` blockquote leaders; `N/A` = leaf does not use blockquotes.
- **Placeholder**: no `TODO[MLF-...]` residue, exactly one H1 title at line 1.

**Note**: autonomous-session smoke; visual-pixel verification of `\boxed{...}`, table alignment, and H2/H3 size ordering was done during the T-P0-540 barrier checkpoint (commit `9454cea`) for the seven Cat 1–2 reference leaves; Cat 3–7 shipped against the same `MarkdownPreview` + `rehype-katex` pipeline and inherit that verification.

| # | Slug | Cat | KaTeX | GFM Table | Callout | Notes |
|---|------|-----|-------|-----------|---------|-------|
| 1 | `bias-variance-tradeoff` | Classical ML | OK | N/A | N/A | len=1419 |
| 2 | `l1-vs-l2-regularization` | Classical ML | OK | OK | N/A | table: 1 table(s) |
| 3 | `logistic-regression-loss` | Classical ML | OK | N/A | N/A | len=2157 |
| 4 | `gbdt-vs-rf-xgboost` | Classical ML | OK | OK | N/A | table: 1 table(s) |
| 5 | `class-imbalance-handling` | Evaluation & Data | OK | OK | N/A | table: 1 table(s) |
| 6 | `auc-vs-pr-curve` | Evaluation & Data | OK | OK | N/A | table: 2 table(s) |
| 7 | `k-means-assumptions-and-failures` | Unsupervised | OK | OK | N/A | table: 1 table(s) |
| 8 | `em-and-gmm` | Unsupervised | OK | N/A | N/A | len=2586 |
| 9 | `batchnorm-vs-layernorm` | DL Training | OK | OK | N/A | table: 1 table(s) |
| 10 | `adam-vs-sgd-adamw` | DL Training | OK | OK | N/A | table: 1 table(s) |
| 11 | `vanishing-exploding-gradient` | DL Training | OK | N/A | N/A | len=2661 |
| 12 | `dropout` | DL Training | OK | N/A | N/A | len=1777 |
| 13 | `activation-function-evolution` | DL Training | OK | OK | N/A | table: 1 table(s) |
| 14 | `cross-entropy-kl-divergence` | Classical ML | OK | N/A | N/A | len=2709 |
| 15 | `self-attention-complexity-optimization` | Attention & Transformer | OK | OK | N/A | table: 1 table(s) |
| 16 | `scaled-dot-product-attention` | Attention & Transformer | OK | N/A | N/A | len=2421 |
| 17 | `mha-mqa-gqa` | Attention & Transformer | OK | OK | N/A | table: 1 table(s) |
| 18 | `positional-encoding` | Attention & Transformer | OK | N/A | N/A | len=3340 |
| 19 | `kv-cache` | Attention & Transformer | OK | N/A | N/A | len=3614 |
| 20 | `pre-norm-vs-post-norm` | Attention & Transformer | OK | N/A | N/A | len=3077 |
| 21 | `sft-rlhf-dpo` | LLM & Stats | OK | OK | N/A | table: 1 table(s) |
| 22 | `moe-routing-load-balancing` | LLM & Stats | OK | OK | N/A | table: 1 table(s) |
| 23 | `tokenization-bpe-wordpiece-sentencepiece` | LLM & Stats | OK | OK | N/A | table: 1 table(s) |
| 24 | `scaling-law-chinchilla` | LLM & Stats | OK | N/A | N/A | len=4499 |
| 25 | `mle-vs-map` | LLM & Stats | OK | OK | N/A | table: 2 table(s) |
| 26 | `clt-vs-lln` | LLM & Stats | OK | OK | N/A | table: 1 table(s) |
| 27 | `ab-test-pvalue-sample-size-multiple-testing` | LLM & Stats | OK | OK | N/A | table: 1 table(s) |

## Summary

- Total leaves: 27
- KaTeX: OK=27 / FAIL=0
- GFM Table: OK=16 / N/A=11 / FAIL=0
- Callout: OK=0 / N/A=27 / FAIL=0

## Verdict

`[PASS]` — all 27 leaves cleared the content-level smoke checks (KaTeX balanced, tables well-formed, no placeholder residue, exactly one H1). No follow-up tasks required. Callout blocks are unused across all 27 leaves (N/A); the drawer contract still supports them for future authoring.

## Re-run

```bash
/c/Anaconda/python.exe -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8765 &
python scripts/smoke_ml_fundamentals_drawers.py
```
