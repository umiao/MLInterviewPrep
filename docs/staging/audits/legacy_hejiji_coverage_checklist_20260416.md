# Legacy 合集 Coverage Checklist (Docs 19 / 21 / 22 / 27)

Per-concept review artifact for the legacy aggregate documents. Per
user instruction, **nothing is auto-deprecated**; this checklist exists
so each concept can be signed off individually before the surrounding
合集 doc is removed.

## How to use

For each concept below:

1. Read the **Status** + **Where** + **Action** triple.
2. If the action is `migrate to node <id>` or `create new node`, do the
   migration first (separate task), then check **User-verified
   migration complete**.
3. Once every concept inside a doc has its first checkbox set, the doc
   itself can be marked safe to delete — check **Signed off for
   deletion** on every row.

## Status vocabulary

- **COVERED** — equivalent canonical content already exists in a
  framework_node or other company_document. The 合集 copy is
  redundant.
- **PARTIAL** — some framework_node touches the topic but lacks the
  depth, derivation, or company-specific framing in this 合集.
  Migration target is named in the **Where** field.
- **UNIQUE** — this 合集 is the sole authoritative source. A new node
  must be created (or the content absorbed into an existing node)
  before this concept can be deleted.

## Action vocabulary

- `safe` — no migration needed; concept can be removed once verified.
- `migrate to node <id>` — content belongs in an existing framework_node.
- `create new node` — content needs a brand-new framework_node.

## Summary

- **Total concepts**: 78
  - COVERED: 19
  - PARTIAL: 35
  - UNIQUE: 24
- **Source DB**: `data/mle_prep.db`
- **Generator**: `scripts/audit_legacy_hejiji_coverage.py`
- **Determinism**: re-running the generator produces a byte-identical
  file (no timestamps in body, sorted iteration, fixed UTF-8 newline
  output).

## Doc 19 — Adobe MLE Prep: All-in-One (Day 1-8 + Prep Script)

- **Concepts**: 46  (COVERED: 5, PARTIAL: 24, UNIQUE: 17)
- **Source**: `company_documents.id = 19` (124940 chars)

### 19.1 Diffusion Models 深度指南 (Day 1 整章)

- **Status**: UNIQUE
- **Where**: no diffusion node in framework_nodes (pillar6 covers transformers/LLM only)
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.2 Diffusion §1 数学符号 (高斯/单位矩阵)

- **Status**: COVERED
- **Where**: node 165 probability_basics, node 173 matrix_operations
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.3 Diffusion §2 前向过程 (加噪 + 重参数化 + 方差守恒)

- **Status**: UNIQUE
- **Where**: no node covers diffusion forward process
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.4 Diffusion §3 噪声调度 β_t (cosine vs linear)

- **Status**: UNIQUE
- **Where**: no node covers noise schedule
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.5 Diffusion §4 时间步嵌入 (Sinusoidal/Scale-Shift)

- **Status**: PARTIAL
- **Where**: node 143 position_encoding mentions Sinusoidal; diffusion-time-step framing missing
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.6 Diffusion §5 反向过程 + DDPM 训练目标 + 采样伪代码

- **Status**: UNIQUE
- **Where**: no node covers reverse process / DDPM sampling
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.7 Diffusion §6 Latent Diffusion / Stable Diffusion Pipeline

- **Status**: UNIQUE
- **Where**: no node covers Latent Diffusion / Stable Diffusion
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.8 Diffusion §7 Classifier-Free Guidance (CFG)

- **Status**: UNIQUE
- **Where**: no node covers CFG
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.9 Diffusion §8 条件注入方式全景 (cross-attn vs concat)

- **Status**: UNIQUE
- **Where**: no node covers conditional injection
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.10 Diffusion §9+§15 ControlNet (Zero Convolution + 训练 + IP-Adapter)

- **Status**: UNIQUE
- **Where**: no node covers ControlNet / IP-Adapter
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.11 Diffusion §10 DDPM vs DDIM 深度对比 + SDE 统一框架

- **Status**: UNIQUE
- **Where**: no node covers DDIM or SDE framework
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.12 Diffusion §11 Positional Embedding (Absolute/Sinusoidal/Relative/RoPE)

- **Status**: PARTIAL
- **Where**: node 143 position_encoding (high-level only; lacks proofs)
- **Action**: migrate to node 143
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.13 Diffusion §12 KV-Cache (含 Prefill vs Decode)

- **Status**: PARTIAL
- **Where**: node 156 kv_cache_paged_attention (high-level; lacks Q/K/V dimension analysis here)
- **Action**: migrate to node 156
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.14 Diffusion §13 为什么预测噪声 (variance / score-matching / v-pred)

- **Status**: UNIQUE
- **Where**: no node covers epsilon/x0/v parameterizations
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.15 Diffusion §14 VAE (Encoder-Decoder + KL + 重参数化 + β-VAE + VQ-VAE)

- **Status**: UNIQUE
- **Where**: no node covers VAE
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.16 Diffusion §16 图像生成产业格局与技术演进

- **Status**: UNIQUE
- **Where**: no node covers gen-image industry landscape
- **Action**: safe (industry-context narrative; absorb summary into diffusion node)
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.17 Alignment §1 RLHF 三阶段 Pipeline (SFT + RM + PPO)

- **Status**: PARTIAL
- **Where**: node 153 rlhf (overview; this doc has full PPO loss derivation)
- **Action**: migrate to node 153
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.18 Alignment §2 DPO 完整推导 (从 RLHF KL 到闭式)

- **Status**: PARTIAL
- **Where**: node 153 rlhf mentions DPO but lacks closed-form derivation
- **Action**: migrate to node 153
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.19 Alignment §3 DPO vs RLHF 对比

- **Status**: PARTIAL
- **Where**: node 153 rlhf
- **Action**: migrate to node 153
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.20 Alignment §4 RLHF/DPO 变体 (KTO, IPO, ORPO, etc.)

- **Status**: PARTIAL
- **Where**: node 153 rlhf
- **Action**: migrate to node 153
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.21 Alignment §5 LLM 知识蒸馏 (response/feature/relation distillation)

- **Status**: PARTIAL
- **Where**: node 106 knowledge_distillation (general KD; lacks LLM-specific tactics)
- **Action**: migrate to node 106
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.22 DT §一 为什么需要分布式训练 (compute/memory/throughput motivation)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training (entry point; lacks motivation framing)
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.23 DT §二 GPU 显存模型 (HBM vs SRAM)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training; HBM/SRAM framing here is unique
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.24 DT §三 四种并行策略全景 (DP/TP/PP/FSDP)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training; comparison table is unique
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.25 DT §四 DP 详解 (gradient all-reduce, ring vs tree)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.26 DT §五 TP 详解 (column-wise/row-wise split)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.27 DT §六 PP 详解 (GPipe vs 1F1B vs interleaved)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.28 DT §七 FSDP / ZeRO 详解 (stage 1/2/3)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.29 DT §八 3D 并行 (DP+TP+PP composition)

- **Status**: PARTIAL
- **Where**: node 126 distributed_training
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.30 DT §九 Activation Checkpointing

- **Status**: PARTIAL
- **Where**: node 126 distributed_training
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.31 DT §十 通信原语 (all-reduce, all-gather, reduce-scatter, broadcast)

- **Status**: UNIQUE
- **Where**: no node covers collective communication primitives
- **Action**: migrate to node 126
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.32 RoPE §2 旋转位置编码 (复数旋转矩阵 + 相对位置编码性质)

- **Status**: PARTIAL
- **Where**: node 143 position_encoding (lists RoPE; lacks rotation-matrix derivation)
- **Action**: migrate to node 143
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.33 RoPE §3 PE 方法对比 (Absolute/Sinusoidal/Relative/RoPE/ALiBi)

- **Status**: PARTIAL
- **Where**: node 143 position_encoding
- **Action**: migrate to node 143
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.34 RoPE §4 长上下文扩展 (PI, NTK-aware, YaRN, LongRoPE)

- **Status**: UNIQUE
- **Where**: no node covers long-context extension techniques
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.35 RoPE §5 视频生成 (Sora-style spatial-temporal architecture)

- **Status**: UNIQUE
- **Where**: no node covers video generation
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.36 Day5 §一 FlashAttention (tiling + online-softmax)

- **Status**: PARTIAL
- **Where**: node 146 attention_variants (mentions Flash; lacks tiling/IO derivation)
- **Action**: migrate to node 146
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.37 Day5 §二 量化 (PTQ/QAT/INT8/FP8)

- **Status**: PARTIAL
- **Where**: node 157 quantization, node 131 serving_optimization
- **Action**: migrate to node 157
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.38 Day5 §三 Serving Optimization (batching, scheduling)

- **Status**: PARTIAL
- **Where**: node 158 continuous_batching, node 159 serving_systems, node 132 llm_serving
- **Action**: migrate to node 158
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.39 PS §A Transformer 基础

- **Status**: COVERED
- **Where**: nodes 32, 141-147 (transformer pillar6.transformer.*)
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.40 PS §B Multimodal AI (CLIP, LLaVA, BLIP)

- **Status**: COVERED
- **Where**: node 164 vision_language
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.41 PS §C LoRA / QLoRA

- **Status**: COVERED
- **Where**: node 154 peft
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.42 PS §D PyTorch 实操

- **Status**: PARTIAL
- **Where**: no dedicated PyTorch node; coverage spread across nodes 60, 63, 74
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.43 PS §F GAN 相关

- **Status**: UNIQUE
- **Where**: no node covers GAN
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.44 扩散精要 §一 UNet (down/up sampling, skip connections)

- **Status**: UNIQUE
- **Where**: no node covers UNet architecture
- **Action**: migrate to node <new diffusion node>
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.45 扩散精要 §八 MQA / GQA

- **Status**: COVERED
- **Where**: node 146 attention_variants (MQA/GQA/Flash)
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 19.46 扩散精要 §十 CLIP (contrastive image-text training)

- **Status**: PARTIAL
- **Where**: node 164 vision_language (lists CLIP; lacks contrastive-loss derivation)
- **Action**: migrate to node 164
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

## Doc 21 — [合集] 概率统计 + 数学推导

- **Concepts**: 12  (COVERED: 7, PARTIAL: 2, UNIQUE: 3)
- **Source**: `company_documents.id = 21` (66829 chars)

### 21.1 §1 Weighted Probability Sampling / Multinomial (含 Alias Method O(1) 证明)

- **Status**: PARTIAL
- **Where**: node 62 sampling_algorithms (general); node 166 common_distributions (Multinomial); Alias Method derivation here is unique
- **Action**: migrate to node 62
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.2 §2 N Random Variables 的 E[X̄] 与 Var[X̄]

- **Status**: COVERED
- **Where**: node 167 expectation_variance, node 169 clt
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.3 §3 Simpson's Paradox (Email Campaign 实例)

- **Status**: UNIQUE
- **Where**: no node covers Simpson's Paradox
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.4 §4 Queueing Theory (M/M/1, single vs multi-queue, Little's Law)

- **Status**: UNIQUE
- **Where**: no node covers queueing theory (node 46 stack_queue is data-structure level, unrelated)
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.5 §5 身高分布 (Normal) vs LinkedIn Connections (power-law/log-normal)

- **Status**: PARTIAL
- **Where**: node 166 common_distributions (lacks power-law / log-normal framing for social-network data)
- **Action**: migrate to node 166
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.6 §6 Class Imbalance 处理

- **Status**: COVERED
- **Where**: node 16 sampling_class_imbalance, node 84 oversampling, node 85 loss_reweighting
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.7 §7 Sampling from Large Dataset 与模型验证

- **Status**: COVERED
- **Where**: node 62 sampling_algorithms, node 86 cross_validation
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.8 §8 Overfitting Prevention (tree-specific: max_depth, min_samples_leaf, subsample)

- **Status**: COVERED
- **Where**: node 65 tree_models, node 194 regularization
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.9 §9 L1/L2 Regularization 与 Bias (KKT primal-dual + Ridge bias 推导 + James-Stein)

- **Status**: COVERED
- **Where**: node 195 bias_variance_geometric (T-P0-474 absorbed L1/L2 proofs + James-Stein here)
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.10 §10 Random Forest Theory (bagging + 特征随机化 + OOB)

- **Status**: COVERED
- **Where**: node 65 tree_models
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.11 §11 MLE (Normal closed-form + GMM + EM 完整推导)

- **Status**: UNIQUE
- **Where**: node 168 mle_map (general MLE only; GMM-EM derivation unique to this doc)
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 21.12 §12 Reservoir Sampling (Algorithm R + Algorithm L + 加权变体)

- **Status**: COVERED
- **Where**: node 62 sampling_algorithms
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

## Doc 22 — [合集] System Design

- **Concepts**: 12  (COVERED: 3, PARTIAL: 6, UNIQUE: 3)
- **Source**: `company_documents.id = 22` (59880 chars)

### 22.1 §1 Typeahead / Autocomplete System

- **Status**: COVERED
- **Where**: node 89 search_retrieval, node 111 classic_ir
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.2 §2 Recommendation System (Short Video) — LinkedIn-flavored

- **Status**: PARTIAL
- **Where**: node 90 recommendation, node 198 realtime_recommendation (general; LinkedIn short-video specifics missing)
- **Action**: migrate to node 198
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.3 §3 Metrics Monitoring / Exception Monitoring

- **Status**: PARTIAL
- **Where**: node 139 monitoring (model-drift focused; metrics-pipeline specifics here)
- **Action**: migrate to node 139
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.4 §4 Job Scheduler

- **Status**: UNIQUE
- **Where**: no node covers job scheduler (general SD outside ML scope)
- **Action**: safe (kept as LinkedIn-specific reference; no migration needed)
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.5 §5 KV Store (Single Machine)

- **Status**: UNIQUE
- **Where**: no node covers KV store (general SD outside ML scope)
- **Action**: safe (kept as LinkedIn-specific reference; no migration needed)
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.6 §6 Personalized InMail (LLM-powered)

- **Status**: PARTIAL
- **Where**: node 93 nlp_llm, node 117 llm_application_patterns; LinkedIn InMail framing unique
- **Action**: migrate to node 117
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.7 §7 Top K Search Words (Count-Min/Heavy Hitters)

- **Status**: COVERED
- **Where**: node 196 streaming_topk (3-axis canonical framework)
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.8 §8 Ranking System (LinkedIn job/feed multi-stage ranking)

- **Status**: PARTIAL
- **Where**: node 99 multi_stage_ranking, node 114 learning_to_rank; LinkedIn-specific ranking specifics missing
- **Action**: migrate to node 99
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.9 §9 isMalicious API (URL/content classifier serving)

- **Status**: PARTIAL
- **Where**: node 95 fraud_trust, node 27 trust_safety; API/serving design specific here
- **Action**: migrate to node 95
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.10 §10 LinkedIn Skills Data Mining

- **Status**: UNIQUE
- **Where**: no node covers skill extraction / data-mining pipelines
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.11 §11 Inverted Document Search

- **Status**: COVERED
- **Where**: node 89 search_retrieval, node 111 classic_ir (BM25/TF-IDF)
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 22.12 附录 LinkedIn SD 面试通用策略

- **Status**: PARTIAL
- **Where**: no dedicated SD-strategy node; advice is LinkedIn-specific
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

## Doc 27 — [合集] ML 理论 + 手写实现

- **Concepts**: 8  (COVERED: 4, PARTIAL: 3, UNIQUE: 1)
- **Source**: `company_documents.id = 27` (185703 chars)

### 27.1 T1 Gradient Descent (BGD/SGD/MBGD + Gradient Clipping)

- **Status**: COVERED
- **Where**: node 74 gradient_descent
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.2 T2 Linear Regression (Normal Eq + GD + OLS assumptions + GLM)

- **Status**: COVERED
- **Where**: node 64 linear_models
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.3 T3 Logistic Regression (BCE + Softmax)

- **Status**: COVERED
- **Where**: node 64 linear_models
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.4 T4 KNN + K-Means (从零实现)

- **Status**: PARTIAL
- **Where**: node 71 clustering (K-Means); KNN missing dedicated node
- **Action**: migrate to node 71
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.5 T5 Naive Bayes (Gaussian/Multinomial/Bernoulli)

- **Status**: PARTIAL
- **Where**: node 165 probability_basics (Bayes); no dedicated Naive Bayes node
- **Action**: create new node
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.6 T6 Tree Models (DT + RF + GBDT + XGBoost from scratch)

- **Status**: COVERED
- **Where**: node 65 tree_models
- **Action**: safe
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.7 T7 Weight Initialization (Xavier/He/LeCun + 完整推导)

- **Status**: PARTIAL
- **Where**: node 77 training_tricks (high-level); init derivations unique here
- **Action**: migrate to node 77
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集

### 27.8 T8 Optimizers (Momentum/Nesterov/AdaGrad/RMSprop/Adam/AdamW from scratch)

- **Status**: UNIQUE
- **Where**: node 74 gradient_descent (mentions; lacks RMSprop/Adam from-scratch code)
- **Action**: migrate to node 74
- [ ] User-verified migration complete
- [ ] Signed off for deletion from this 合集
