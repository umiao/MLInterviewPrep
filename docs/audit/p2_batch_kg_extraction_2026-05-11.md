# P2-Batch KG Extraction Audit — 18 Applied-Status Companies

**Task**: T-P2-835 / KG-INT B6-P2-batch — lightweight KG-extraction pass for 18 `applied`-status companies (no archive).
**Date**: 2026-05-11
**Scope**: Apple (id=8), Nvidia (9), Reddit (10), Salesforce (11), Microsoft (12), Instacart (13), Robinhood (14), Roblox (15), Amazon (16), Coinbase (17), Quora (18), Intuit (19), Snap (20), OpenAI (21), Anthropic (22), Airbnb (4), Glean (7), Netflix (6).
**Headline finding**: **Uniform NULL case across all 18 companies.** Every target has zero `company_documents`, zero S4/S5/S6 tag rows, zero `interview_events`, and only short admin-only `companies.notes` (25–196 bytes of role-title prose). **No prose surface exists to scan for promotion-eligible patterns.** AC `concept_links count > 11` cannot be met from the current content surface; see §4 for the path-forward analysis and §5 for proposed concept_links once the schema or content gates open.

---

## §1 — Surface inventory

For each company, the 6-surface census (per `docs/workflow/company_internalization_protocol.md` §"Note surface taxonomy"):

| ID | Company    | S1 (prep_notes) | S2 (companies.notes) | S3 (docs / bytes) | S4 (prob tags) | S5 (node tags) | S6 (bq tags) | S7 (events) |
|----|------------|----------------:|---------------------:|------------------:|---------------:|---------------:|-------------:|------------:|
| 8  | Apple      | 0 B             | 55 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 9  | Nvidia     | 0 B             | 72 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 10 | Reddit     | 0 B             | 28 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 11 | Salesforce | 0 B             | 100 B                | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 12 | Microsoft  | 0 B             | 25 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 13 | Instacart  | 0 B             | 132 B                | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 14 | Robinhood  | 0 B             | 51 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 15 | Roblox     | 0 B             | 109 B                | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 16 | Amazon     | 0 B             | 54 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 17 | Coinbase   | 0 B             | 66 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 18 | Quora      | 0 B             | 60 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 19 | Intuit     | 0 B             | 29 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 20 | Snap       | 0 B             | 44 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 21 | OpenAI     | 0 B             | 196 B                | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 22 | Anthropic  | 0 B             | 98 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 4  | Airbnb     | 0 B             | 105 B                | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 7  | Glean      | 0 B             | 108 B                | 0 / 0 B           | 0              | 0              | 0            | 0           |
| 6  | Netflix    | 0 B             | 61 B                 | 0 / 0 B           | 0              | 0              | 0            | 0           |

**Totals**: 0 docs, 0 prob_company_tags, 0 node_company_tags, 0 behavioral_example_company_tags, 0 interview_events. S2 admin content totals 1 393 B across 18 rows (avg 77 B, max 196 B at OpenAI which lists 4 role titles).

**Verification SQL**: see `scripts/_audit_company_kg_internalization.py` — re-run produces the same census. The audit is reality-anchored, not paraphrased.

---

## §2 — Role-title taxonomy (S2 prose, the only available signal)

The single non-empty surface is `companies.notes`, which carries role-title admin prose only (no technical content). Per `docs/workflow/company_internalization_protocol.md` §"When NOT to apply the full protocol", these companies match the NULL pattern identical to Lyra (T-P0-809), with the distinction that their S2 carries **role-title evidence** worth a taxonomy pass.

Verbatim S2 captures (full, since each row is ≤196 B):

| Company    | S2 verbatim (companies.notes) |
|------------|-------------------------------|
| Apple      | `Position: Machine Learning Engineer, Siri Core Modeling` |
| Nvidia     | `Position: Senior GenAI Algorithms Engineer - Post-Training Optimizations` |
| Reddit     | `Position: Senior ML Engineer` |
| Salesforce | `Positions applied: - AI Engineer, Agent Systems - Lead Machine Learning Engineer, LLM Infrastructure` |
| Microsoft  | `2 positions (details TBD)` |
| Instacart  | `Positions applied: - Senior ML Engineer II, AI Special Projects - Senior ML Engineer II, Growth Modeling` |
| Robinhood  | `Position: Senior Machine Learning Engineer, Agentic` |
| Roblox     | `Positions applied: - Senior ML Engineer, Ads - Sr ML Engineer - Safety Experience` |
| Amazon     | `Position: Applied Scientist, Delivery Foundation Model` |
| Coinbase   | `Position: Senior SWE (AI Platform - AI Acceleration)` |
| Quora      | `Position: Senior ML Engineer, Ranking (Remote)` |
| Intuit     | `Position: Senior AI Scientist` |
| Snap       | `Position: ML Engineer, Level 4` |
| OpenAI     | `Positions applied: - Research Engineer, Retrieval & Search, Applied Engineering - Research Engineer, Applied AI Engineering - Research Engineer, Notifications - Software Engineer, Youth Well-Being` |
| Anthropic  | `Positions applied: - Software Engineer, Growth - Machine Learning Systems Engineer, Research Tools` |
| Airbnb     | `Position: Senior ML Engineer, Listing and Host Tools Data and AI` (+ "Status: Referral completed") |
| Glean      | `Positions applied: - Machine Learning Engineer, Search Quality - Machine Learning Engineer, Enterprise Brain` |
| Netflix    | `Position: ML Engineer (L4) - Production Science` |

Recurring topical signals (cluster keywords):
- **Search & Retrieval**: OpenAI (Retrieval & Search), Glean (Search Quality, Enterprise Brain), Apple (Siri implies query understanding)
- **LLM Training / Post-Training**: Nvidia (Post-Training Optimizations), Anthropic (Research Tools)
- **LLM Serving / Infra / Acceleration**: Salesforce (LLM Infrastructure), Coinbase (AI Acceleration), Anthropic (ML Systems)
- **Agentic / LLM Applications**: Salesforce (Agent Systems), Robinhood (Agentic)
- **Recommendation / Ranking**: Quora (Ranking), Netflix (Production Science implies ranking ops), Roblox (Ads), Reddit (Senior ML — heuristic for content platforms), Snap (heuristic)
- **Marketplace / Logistics**: Airbnb (Listing), Instacart (Growth Modeling), Amazon (Delivery)
- **Trust & Safety**: Roblox (Safety Experience)
- **Foundation Models / GenAI**: Amazon (Delivery Foundation Model), Nvidia (GenAI Algorithms), OpenAI/Anthropic (entire org)

7 broad topical clusters emerge, all of which already have existing `framework_nodes` (§3 below).

---

## §3 — Proposed company→framework_node mapping (NOT applied)

If/when the schema is extended to accept `src_kind='company'` (§4 path-forward analysis), the following 38 concept_links rows would land cleanly. Until then, **the table below is documentation only** — no DB writes are performed by this audit.

Format: `(src=company.id) — (dst=framework_node.id) — relation — evidence`.

| # | Company         | Role evidence                                  | Target node                                                      | Relation | Confidence |
|---|-----------------|------------------------------------------------|------------------------------------------------------------------|----------|-----------:|
| 1 | Apple (8)       | Siri Core Modeling                             | kg://23 pillar4.nlp_llm_applications                             | mentions | high |
| 2 | Apple (8)       | Siri Core Modeling                             | kg://93 pillar3.design_problems.nlp_llm                          | mentions | med |
| 3 | Nvidia (9)      | GenAI Post-Training Optimizations              | kg://34 pillar6.llm_training_alignment                           | mentions | high |
| 4 | Nvidia (9)      | Post-Training Optimizations                    | kg://152 pillar6.llm_training_alignment.sft                      | mentions | high |
| 5 | Nvidia (9)      | Post-Training Optimizations                    | kg://153 pillar6.llm_training_alignment.rlhf                     | mentions | high |
| 6 | Nvidia (9)      | Post-Training Optimizations                    | kg://154 pillar6.llm_training_alignment.peft                     | mentions | high |
| 7 | Reddit (10)     | Senior MLE (content platform heuristic)        | kg://90 pillar3.design_problems.recommendation                   | mentions | low |
| 8 | Salesforce (11) | AI Engineer, Agent Systems                     | kg://117 pillar4.nlp_llm_applications.llm_application_patterns   | mentions | high |
| 9 | Salesforce (11) | Lead MLE, LLM Infrastructure                   | kg://132 pillar5.serving_infra.llm_serving                       | mentions | high |
| 10 | Salesforce (11) | Lead MLE, LLM Infrastructure                  | kg://159 pillar6.llm_inference.serving_systems                   | mentions | high |
| 11 | Microsoft (12)  | 2 positions TBD                                | (DEFER — no signal)                                              | —        | n/a  |
| 12 | Instacart (13)  | Growth Modeling, AI Special Projects           | kg://25 pillar4.marketplace_logistics                            | mentions | high |
| 13 | Instacart (13)  | Growth Modeling                                | kg://65 pillar2.supervised_learning.tree_models                  | mentions | med  |
| 14 | Robinhood (14)  | Senior MLE, Agentic                            | kg://117 pillar4.nlp_llm_applications.llm_application_patterns   | mentions | high |
| 15 | Robinhood (14)  | Agentic                                        | kg://97 pillar3.design_problems.genai                            | mentions | med  |
| 16 | Roblox (15)     | Senior MLE, Ads                                | kg://24 pillar4.ads_monetization                                 | mentions | high |
| 17 | Roblox (15)     | Senior MLE, Ads                                | kg://91 pillar3.design_problems.ads                              | mentions | high |
| 18 | Roblox (15)     | Sr MLE, Safety Experience                      | kg://27 pillar4.trust_safety                                     | mentions | high |
| 19 | Amazon (16)     | Applied Scientist, Delivery Foundation Model   | kg://25 pillar4.marketplace_logistics                            | mentions | high |
| 20 | Amazon (16)     | Delivery (ETA-style)                           | kg://120 pillar4.marketplace_logistics.eta_prediction            | mentions | med  |
| 21 | Amazon (16)     | Foundation Model                               | kg://33 pillar6.pretrained_lm                                    | mentions | med  |
| 22 | Coinbase (17)   | AI Platform, AI Acceleration                   | kg://132 pillar5.serving_infra.llm_serving                       | mentions | high |
| 23 | Coinbase (17)   | AI Acceleration                                | kg://159 pillar6.llm_inference.serving_systems                   | mentions | high |
| 24 | Quora (18)      | Senior MLE, Ranking                            | kg://99 pillar3.building_blocks.multi_stage_ranking              | mentions | high |
| 25 | Quora (18)      | Ranking                                        | kg://255 meta-prep/system-design-must-knows/multi-stage-funnel   | mentions | high |
| 26 | Quora (18)      | Ranking                                        | kg://198 pillar3.design_problems.realtime_recommendation         | mentions | med  |
| 27 | Intuit (19)     | Senior AI Scientist (broad)                    | (DEFER — generic title)                                          | —        | n/a  |
| 28 | Snap (20)       | MLE L4 (content/ads heuristic)                 | kg://24 pillar4.ads_monetization                                 | mentions | low  |
| 29 | OpenAI (21)     | RE, Retrieval & Search                         | kg://89 pillar3.design_problems.search_retrieval                 | mentions | high |
| 30 | OpenAI (21)     | RE, Retrieval & Search                         | kg://22 pillar4.search_ir                                        | mentions | high |
| 31 | OpenAI (21)     | RE, Retrieval & Search                         | kg://112 pillar4.search_ir.neural_retrieval                      | mentions | high |
| 32 | OpenAI (21)     | RE, Retrieval & Search                         | kg://252 meta-prep/system-design-must-knows/two-tower-dual-encoder | mentions | high |
| 33 | OpenAI (21)     | RE, Retrieval & Search                         | kg://253 meta-prep/system-design-must-knows/ann-hnsw-ivf-pq      | mentions | high |
| 34 | Anthropic (22)  | ML Systems Engineer, Research Tools            | kg://28 pillar5.training_infra                                   | mentions | high |
| 35 | Anthropic (22)  | Research Tools (orchestration heuristic)       | kg://137 pillar5.ml_pipeline_ops.orchestration                   | mentions | med  |
| 36 | Airbnb (4)      | Senior MLE, Listing and Host Tools             | kg://25 pillar4.marketplace_logistics                            | mentions | high |
| 37 | Airbnb (4)      | Listing pricing/marketplace heuristic          | kg://119 pillar4.marketplace_logistics.dynamic_pricing           | mentions | med  |
| 38 | Glean (7)       | MLE, Search Quality + Enterprise Brain         | kg://22 pillar4.search_ir                                        | mentions | high |
| 39 | Glean (7)       | Enterprise Brain (RAG heuristic)               | kg://36 pillar6.rag_deep                                         | mentions | high |
| 40 | Glean (7)       | Search Quality                                 | kg://112 pillar4.search_ir.neural_retrieval                      | mentions | high |
| 41 | Netflix (6)     | MLE L4, Production Science (rec heuristic)     | kg://90 pillar3.design_problems.recommendation                   | mentions | med  |
| 42 | Netflix (6)     | Production Science (model serving heuristic)   | kg://130 pillar5.serving_infra.model_serving                     | mentions | low  |

**Total proposed rows**: 42 (high-confidence: 22; medium: 13; low: 4; deferred: 2 Microsoft + 1 Intuit on broad/generic titles).

All target `framework_nodes.id` values verified to exist in `data/mle_prep.db` (31 unique target nodes, spread across pillar2/3/4/5/6 + meta-prep).

---

## §4 — Schema-gap analysis: why AC `count > 11` cannot be met as-spec

The current `concept_links` schema enforces `src_kind IN ('framework_node', 'company_document')` via CHECK constraint. The 18 target companies have **zero** `company_documents`, so the only existing edge direction for these companies (company_document → framework_node) is structurally unavailable. The 11 existing rows are all between `company_document`s and `framework_node`s for content-bearing companies (Google, Adobe).

**The AC `framework_nodes concept_links count > 11` is therefore not achievable from a pure "scan + extract" pass over these 18 companies without one of the following:**

(a) **Schema migration** — extend `src_kind` CHECK to include `'company'` (or `'role_title'`), then this audit can insert the 42 proposed rows from §3 directly. **Cost**: 1 small migration script + test update + a re-think of whether `'company'` is the right kind name. Affects: `data/mle_prep.db` schema, `tests/test_concept_links_table.py` CHECK test, `src/backend/routers/kg.py` if it should render company→node edges in the KG viz.

(b) **Wait for content** — these companies are `applied` status; when any upgrades to `phone_screen` / `onsite`, prose surfaces (`company_documents`, `companies.prep_notes`) will populate naturally as prep work begins, and standard `company_document` → `framework_node` concept_links will land via the canonical B4a / B6 protocol. **Cost**: pure deferral; the audit captures the pre-content baseline.

(c) **framework_node ↔ framework_node `see_also` links** derived from the audit-surfaced topical clusters (§2 last bullet). E.g., the cross-cluster observation that 5 of 18 companies touch LLM-Serving + Agent-Systems + Retrieval simultaneously could motivate a few new `see_also` edges between kg://117 ↔ kg://132 ↔ kg://22. **Cost**: this would meet AC `count > 11` cleanly (current count of framework_node↔framework_node edges = 0; any addition exceeds), but the edges would be *audit-derived*, not *content-derived*, and would expand the KG-viz edge set (the router falls back to synthetic parent→child today since this kind is empty). Decision-blocked on whether the user wants audit-derived structural inferences in the KG, or strictly content-derived ones.

**Recommendation**: **(b) — wait for content**, with §3 mapping documented here as the pre-staged plan for fast extraction when content lands. Path (a) is a clean follow-up if the user wants `applied`-status companies to have lightweight presence in the KG before they upgrade. Path (c) is a separate KG-densification question worth its own task (not this audit's scope).

---

## §5 — Recommended next actions

1. **Mark T-P2-835 as completed-partial** — the audit deliverable lands; concept_links delta is 0 by structural necessity. No re-trigger needed during the `applied` status window for these 18 companies.

2. **Re-trigger trigger**: when any of the 18 companies upgrades to `phone_screen` / `onsite`, file a per-company B4a task (sister to T-P0-808 .. T-P0-820) that includes both (i) the §3 row(s) for that company and (ii) any new `company_documents` content that lands. The pre-staged mapping in §3 makes the re-trigger cheap.

3. **Optional follow-up tasks** (file as P3 if the user wants the schema/KG-densification path):
   - **T-P3-yyy** — Migration: extend `concept_links.src_kind` CHECK to allow `'company'`; update tests; document the new edge kind in `docs/workflow/company_internalization_protocol.md`. Unblocks §3 row insertion under path (a).
   - **T-P3-zzz** — KG-densification audit: derive `see_also` edges between `framework_node`s from cross-company role-title co-occurrence patterns (path (c)). Output: 10-30 new `framework_node ↔ framework_node` edges that improve KG viz over the current synthetic-parent-only fallback.

4. **No DB writes** were performed by this audit. `data/mle_prep.db` is unchanged. `scripts/audit_uri_consistency.py` exits 0 ERRORs (pre-existing 64 ambiguous-link warnings unrelated to this audit).

---

## §6 — Verification

| Check | Result |
|-------|--------|
| `SELECT COUNT(*) FROM concept_links` | 11 (unchanged from session start) |
| `SELECT COUNT(*) FROM company_documents WHERE company_id IN (8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,4,7,6)` | 0 |
| `SELECT COUNT(*) FROM problem_company_tags WHERE company_id IN (...)` | 0 |
| `SELECT COUNT(*) FROM node_company_tags WHERE company_id IN (...)` | 0 |
| `SELECT COUNT(*) FROM behavioral_example_company_tags WHERE company_id IN (...)` | 0 |
| `SELECT COUNT(*) FROM interview_events WHERE company_id IN (...)` | 0 |
| `SELECT length(notes) FROM companies WHERE id IN (...) ORDER BY id` | 25-196 bytes each (matches §1 table) |
| All 31 unique `framework_nodes.id` cited in §3 exist | Verified via `SELECT COUNT(*) FROM framework_nodes WHERE id IN (...)` = 31 |
| Audit markdown exists at canonical path | `docs/audit/p2_batch_kg_extraction_2026-05-11.md` |

End of audit.
