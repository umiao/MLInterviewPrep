# ML-Fundamentals Content QA Audit

**Task**: T-P1-550 [T-MLF-10] content QA pass -- acronym expansions, formula context, jargon definitions

Audit categories: **A** = acronym lacks first-occurrence expansion (`**English** (ACRO, 中文)`). **F** = standalone display formula with no adjacent prose. **J** = jargon lacks inline definition.

| # | Slug | A | F | J | Top findings |
|---|------|---|---|---|--------------|
| 1 | `kv-cache` | 0 | 0 | 0 | (clean) |
| 2 | `mha-mqa-gqa` | 0 | 0 | 0 | (clean) |
| 3 | `positional-encoding` | 5 | 0 | 0 | A: GQA, KV, MHA, MPT-7B, MQA |
| 4 | `pre-norm-vs-post-norm` | 1 | 0 | 0 | A: RMS |
| 5 | `scaled-dot-product-attention` | 0 | 0 | 0 | (clean) |
| 6 | `self-attention-complexity-optimization` | 5 | 0 | 0 | A: GQA, KV, MQA, NTK, RWKV |
| 7 | `bias-variance-tradeoff` | 0 | 0 | 0 | (clean) |
| 8 | `cross-entropy-kl-divergence` | 0 | 0 | 0 | (clean) |
| 9 | `gbdt-vs-rf-xgboost` | 1 | 0 | 0 | A: XGB |
| 10 | `l1-vs-l2-regularization` | 0 | 0 | 0 | (clean) |
| 11 | `logistic-regression-loss` | 0 | 0 | 0 | (clean) |
| 12 | `activation-function-evolution` | 0 | 0 | 0 | (clean) |
| 13 | `adam-vs-sgd-adamw` | 0 | 0 | 0 | (clean) |
| 14 | `batchnorm-vs-layernorm` | 0 | 0 | 0 | (clean) |
| 15 | `dropout` | 0 | 0 | 0 | (clean) |
| 16 | `vanishing-exploding-gradient` | 1 | 0 | 0 | A: GELU |
| 17 | `auc-vs-pr-curve` | 2 | 0 | 0 | A: PR-AUC, ROC-AUC |
| 18 | `class-imbalance-handling` | 3 | 0 | 0 | A: PR-AUC, SMOTE-ENN, SMOTE-NC |
| 19 | `ab-test-pvalue-sample-size-multiple-testing` | 1 | 0 | 0 | A: CUPED |
| 20 | `clt-vs-lln` | 0 | 0 | 0 | (clean) |
| 21 | `mle-vs-map` | 0 | 0 | 0 | (clean) |
| 22 | `moe-routing-load-balancing` | 1 | 0 | 0 | A: ST |
| 23 | `scaling-law-chinchilla` | 0 | 0 | 0 | (clean) |
| 24 | `sft-rlhf-dpo` | 1 | 0 | 0 | A: IPO |
| 25 | `tokenization-bpe-wordpiece-sentencepiece` | 0 | 0 | 0 | (clean) |
| 26 | `em-and-gmm` | 1 | 0 | 0 | A: DPMM |
| 27 | `k-means-assumptions-and-failures` | 0 | 0 | 0 | (clean) |

## Totals -- A=22 F=0 J=0

## Per-leaf Details

### positional-encoding  (`ml-fundamentals/attention_transformer/positional-encoding`)

**Acronyms (first-occurrence expansion missing):**

- `MPT-7B`
    - excerpt: `i vs RoPE 谁外推好  ALiBi 外推几乎无损（斜率独立于长度），在 MPT-7B 上测试   训练外推到   质量仍稳。RoPE 裸外推会掉点（高频相位周期性错位），必须配 NTK / Y`
- `KV` -- canonical: Key-Value
    - excerpt: `2023 (NTK-aware)、Peng 2023 (YaRN)。 - 与 [KV Cache](/ml-fundamentals?cat=attention_transformer&slug=kv`
- `MHA` -- canonical: Multi-Head Attention
    - excerpt: `attention_transformer&slug=kv-cache) 和 [MHA/MQA/GQA](/ml-fundamentals?cat=attention_transformer&slug`
- `MQA` -- canonical: Multi-Query Attention
    - excerpt: `ntion_transformer&slug=kv-cache) 和 [MHA/MQA/GQA](/ml-fundamentals?cat=attention_transformer&slug=mha`
- `GQA` -- canonical: Grouped-Query Attention
    - excerpt: `n_transformer&slug=kv-cache) 和 [MHA/MQA/GQA](/ml-fundamentals?cat=attention_transformer&slug=mha-mqa`


### pre-norm-vs-post-norm  (`ml-fundamentals/attention_transformer/pre-norm-vs-post-norm`)

**Acronyms (first-occurrence expansion missing):**

- `RMS`
    - excerpt: `aling：     RMSNorm 去掉 mean centering，只做 RMS 归一化：     省掉一个 mean 的 reduction + 减法 +   参数。实证上质量几乎无损，计算省`


### self-attention-complexity-optimization  (`ml-fundamentals/attention_transformer/self-attention-complexity-optimization`)

**Acronyms (first-occurrence expansion missing):**

- `RWKV`
    - excerpt: `attention，天然  ，长序列性能媲美 Transformer。 - **RWKV**：RNN 风格的 recurrence + Transformer 的 parallel 训练。 - **M`
- `KV` -- canonical: Key-Value
    - excerpt: `向 |  ## 6. 常见追问  - **Key-Value Cache** (KV Cache, 键值缓存)：推理时前面 token 的   要重用，显存随序列线性增长，是长上下文推理的主要瓶颈。优`
- `GQA` -- canonical: Grouped-Query Attention
    - excerpt: `token 的   要重用，显存随序列线性增长，是长上下文推理的主要瓶颈。优化：GQA / MQA（多 query head 共享 K, V，显存砍数倍）、PagedAttention (vLLM，按`
- `MQA` -- canonical: Multi-Query Attention
    - excerpt: `的   要重用，显存随序列线性增长，是长上下文推理的主要瓶颈。优化：GQA / MQA（多 query head 共享 K, V，显存砍数倍）、PagedAttention (vLLM，按 page`
- `NTK`
    - excerpt: `context）：通常是 FlashAttention + RoPE 长度外推（NTK / YaRN）+ sliding window 混合，而不是单一技术。  ## 7. Linear Attent`


### gbdt-vs-rf-xgboost  (`ml-fundamentals/classical_ml/gbdt-vs-rf-xgboost`)

**Acronyms (first-occurrence expansion missing):**

- `XGB`
    - excerpt: `s XGBoost**：LightGBM 用 leaf-wise growth（XGB 是 level-wise），GOSS 采样，叶子数比深度更关键，通常更快但更容易过拟合小数据。 - **CatB`


### vanishing-exploding-gradient  (`ml-fundamentals/dl_training/vanishing-exploding-gradient`)

**Acronyms (first-occurrence expansion missing):**

- `GELU`
    - excerpt: `eLU, 修正线性单元)（正半轴导数恒为 1）及其变体 LeakyReLU / GELU / SiLU。这是最基础也最有效的一步。  ### 初始化  让每层的输入输出方差大致保持一致：  - **X`


### auc-vs-pr-curve  (`ml-fundamentals/eval_data/auc-vs-pr-curve`)

**Acronyms (first-occurrence expansion missing):**

- `ROC-AUC`
    - excerpt: `| 场景 | 首选 | |-----|------| | 类别大致平衡 | ROC-AUC | | 不平衡 + 关心少数类的检出质量 | PR-AUC（也叫 Average Precision）`
- `PR-AUC`
    - excerpt: `类别大致平衡 | ROC-AUC | | 不平衡 + 关心少数类的检出质量 | PR-AUC（也叫 Average Precision） | | 欺诈 / 罕见病 / 异常检测 | PR | | 两个`


### class-imbalance-handling  (`ml-fundamentals/eval_data/class-imbalance-handling`)

**Acronyms (first-occurrence expansion missing):**

- `SMOTE-NC`
    - excerpt: `边界。 - **对 categorical features 没定义**：需要 SMOTE-NC。 - **Leakage 隐患**：SMOTE 必须在 train / val split 之后对训练`
- `SMOTE-ENN`
    - excerpt: `合成邻居。 - **改进**：Borderline-SMOTE（只在边界插值）、SMOTE-ENN（插完再用 **Edited Nearest Neighbors** (ENN, 编辑最近邻) 清噪声`
- `PR-AUC`
    - excerpt: `最近邻) 清噪声）。  ## 4. 实战 recipe  1. 先看指标：换成 PR-AUC / F1 / Recall@**False Positive Rate** (FPR, 假正率)，很多时候`


### ab-test-pvalue-sample-size-multiple-testing  (`ml-fundamentals/llm_stats/ab-test-pvalue-sample-size-multiple-testing`)

**Acronyms (first-occurrence expansion missing):**

- `CUPED`
    - excerpt: `CI 自行判断价值。  ### 3.3 variance reduction：CUPED  **Controlled-experiment Using Pre-Experiment Data** (`


### moe-routing-load-balancing  (`ml-fundamentals/llm_stats/moe-routing-load-balancing`)

**Acronyms (first-occurrence expansion missing):**

- `ST`
    - excerpt: `### 2.4 Router z-loss：数值稳定的正则  Switch 和 ST-MoE（Zoph 2022）观察到：路由 softmax 的 logit 幅度会慢慢 drift 到很大值（因为`


### sft-rlhf-dpo  (`ml-fundamentals/llm_stats/sft-rlhf-dpo`)

**Acronyms (first-occurrence expansion missing):**

- `IPO`
    - excerpt: `；数据噪声大要调大   防过拟合到噪声偏好对。  ### 4.2 DPO vs IPO vs KTO（**Kahneman-Tversky Optimization**，KTO，前景理论偏好优化） —`


### em-and-gmm  (`ml-fundamentals/unsupervised/em-and-gmm`)

**Acronyms (first-occurrence expansion missing):**

- `DPMM`
    - excerpt: `re`（**Dirichlet Process Mixture Model**，DPMM，狄利克雷过程混合模型）把 K 设得偏大让它自动压掉多余分量。 - **协方差奇异**：某个分量只分到 1-2`

