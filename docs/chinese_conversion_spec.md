# Chinese Conversion & ML Expansion Spec

## Scope
Convert all 147 framework_nodes descriptions from English to Chinese, with deep
expansion for ML-related pillars (2-7). Also convert English company_documents
and fix formula rendering bugs.

## Global Translation Rules

### Language
- **Body text**: All Chinese
- **Section headings**: Keep English (e.g., `## Core Concepts`, `## Interview Patterns`)
- **Technical terms**: First occurrence uses **bold English (Chinese)** format:
  - Example: **Gradient Descent（梯度下降）** 是一种通过迭代更新参数来最小化损失函数的优化方法。
  - After first occurrence, use either English or Chinese consistently
- **Acronyms**: Always expand on first use with full name + Chinese explanation:
  - Example: **SVM (Support Vector Machine，支持向量机)** 是一种...
  - Example: **GBDT (Gradient Boosted Decision Trees，梯度提升决策树)** 通过...

### Math Formulas
- Display math: `$$...$$` (on its own line, with blank lines before/after)
- Inline math: `$...$`
- NEVER put formulas inside ` ``` ` code blocks
- All LaTeX must be KaTeX-compatible
- Every formula MUST have Chinese explanation immediately after

### Structure
Follow the existing template from `docs/framework_content_template.md`:
```
# {Topic Title}   <-- Keep English

## Overview
中文概述（2-3句话说明主题重要性和面试相关性）

## Core Concepts
### {Concept Name}   <-- Keep English subtitles
中文正文解释...
$$
formula
$$
公式解释...

## Implementation
```python
# Code comments can be English
```

## Interview Patterns
| Pattern | When to Use | Key Insight |
中文表格内容...

### Common Interview Questions
- [ ] 中文面试问题

## Comparisons
中文对比表格...

## Key Takeaways
- [ ] 中文要点
```

### Quality Checklist (per node)
1. All acronyms expanded with full English name + Chinese explanation on first use
2. All formulas have Chinese explanation
3. No formulas inside code blocks
4. Chinese body text throughout (except headings, terms, code)
5. Target size met (see per-pillar targets)
6. Code snippets preserved with English comments

---

## Per-Pillar Execution Specs

### Pillar 1: Coding & Algorithms (20 nodes)
**Node IDs**: 44-63
**Type**: Pure translation (no expansion needed)
**Target size**: Keep ~5K chars per node
**Empty nodes to fill**:
- Node 45 (HashMap/HashSet): Write new ~5K Chinese content covering hash function design,
  collision resolution (chaining vs open addressing), load factor, amortized O(1),
  common interview patterns (two-sum, group anagram, LRU cache)

**Translation notes**:
- Algorithm names stay English: "Binary Search", "Dynamic Programming", etc.
- Complexity notation stays: O(n log n), etc.
- Code snippets: keep Python code as-is, translate surrounding explanation

### Pillar 2: ML Fundamentals & Theory (25 nodes)
**Node IDs**: 64-88
**Type**: Translation + DEEP expansion
**Target size**: 6-10K chars per node (up from ~3-4K)

**Empty nodes to fill**:
- Node 65 (Tree Models): Write comprehensive new content (~8K chars)
- Node 79 (Categorical Features): Write comprehensive new content (~6K chars)

**Expansion requirements by node**:

#### Node 64 — Linear Models (currently 3.9K -> target 8K+)
Must include complete **GLM (Generalized Linear Models)** section:
- GLM framework: $$g(\mu) = X\beta$$ where $g$ is the link function
- Specific link functions table:

| Model | Distribution | Link Function | Formula | Use Case |
|-------|-------------|---------------|---------|----------|
| Linear Regression | Gaussian | Identity | $$g(\mu) = \mu$$ | Continuous output |
| Logistic Regression | Bernoulli | Logit | $$g(\mu) = \ln\frac{\mu}{1-\mu}$$ | Binary classification |
| Poisson Regression | Poisson | Log | $$g(\mu) = \ln(\mu)$$ | Count data |
| Probit Regression | Bernoulli | Probit | $$g(\mu) = \Phi^{-1}(\mu)$$ | Binary (latent normal) |
| Gamma Regression | Gamma | Inverse | $$g(\mu) = \frac{1}{\mu}$$ | Positive continuous |

- Exponential family form: $$f(y|\theta) = h(y) \exp(\eta(\theta) \cdot T(y) - A(\theta))$$
- Maximum likelihood estimation for each
- Regularized variants (Ridge, Lasso, Elastic Net) with penalty terms

#### Node 65 — Tree Models (NEW, target 8K+)
Must cover:
- Decision Tree splitting criteria:
  - Information Gain: $$IG(S,A) = H(S) - \sum_{v} \frac{|S_v|}{|S|} H(S_v)$$
  - Gini Impurity: $$Gini(S) = 1 - \sum_{i=1}^{C} p_i^2$$
  - Variance Reduction (regression)
- ID3 vs C4.5 vs CART differences
- Random Forest: bagging + feature subsampling, $$m \approx \sqrt{p}$$
- GBDT: $$F_m(x) = F_{m-1}(x) + \eta \cdot h_m(x)$$ where $h_m$ fits negative gradient
- XGBoost specifics: regularized objective, second-order Taylor expansion
  $$\mathcal{L}^{(t)} \approx \sum_{i=1}^{n} [g_i f_t(x_i) + \frac{1}{2} h_i f_t^2(x_i)] + \Omega(f_t)$$
- LightGBM: GOSS + EFB, leaf-wise growth vs level-wise
- CatBoost: ordered boosting, target encoding for categoricals
- Feature importance methods: split-based, gain-based, permutation

#### Node 66 — SVM (currently 3.6K -> target 7K+)
Must add:
- Primal problem: $$\min_{w,b} \frac{1}{2}\|w\|^2 \text{ s.t. } y_i(w^Tx_i + b) \geq 1$$
- Dual problem derivation via Lagrange multipliers
- Kernel trick: $$K(x_i, x_j) = \phi(x_i)^T \phi(x_j)$$
- Common kernels table: Linear, Polynomial, RBF, Sigmoid with formulas
- Soft margin: slack variables $\xi_i$, C parameter tradeoff
- SMO algorithm key idea
- SVM vs Logistic Regression comparison

#### Node 68 — Loss Functions (currently 3.9K -> target 8K+)
Must list each loss with formula + gradient + use case:
- MSE: $$L = \frac{1}{n}\sum(y-\hat{y})^2$$, gradient: $$\frac{\partial L}{\partial \hat{y}} = \frac{2}{n}(\hat{y}-y)$$
- MAE: $$L = \frac{1}{n}\sum|y-\hat{y}|$$
- Huber Loss: piecewise definition with delta parameter
- Cross-Entropy: $$L = -\sum y_i \log(\hat{y}_i)$$
- Binary CE: $$L = -[y\log(p) + (1-y)\log(1-p)]$$
- Focal Loss: $$L = -\alpha_t(1-p_t)^\gamma \log(p_t)$$, explain gamma effect
- Hinge Loss: $$L = \max(0, 1 - y \cdot f(x))$$
- KL Divergence: $$D_{KL}(P\|Q) = \sum P(x)\log\frac{P(x)}{Q(x)}$$
- Contrastive Loss, Triplet Loss for embeddings

#### Node 69 — Regularization (currently 8K -> target 10K+)
Must add:
- L1 geometric interpretation (diamond constraint -> sparsity)
- L2 geometric interpretation (circle constraint -> small weights)
- Elastic Net: $$\lambda_1\|w\|_1 + \lambda_2\|w\|_2^2$$
- Dropout as approximate Bayesian inference
- Weight Decay vs L2 regularization difference in Adam
- Early stopping as implicit regularization
- Data augmentation as regularization

#### Node 70 — Evaluation Metrics (currently 3.2K -> target 7K+)
Must cover:
- Precision, Recall, F1 with formulas
- AUC-ROC: interpretation, calculation method
- AUC-PR: when to use over ROC
- Log Loss formula
- NDCG for ranking: $$NDCG@k = \frac{DCG@k}{IDCG@k}$$
- MAP@K
- Regression: MSE, RMSE, MAE, R-squared, Adjusted R-squared
- Calibration metrics: ECE, reliability diagram

#### Node 74 — Gradient Descent Family (currently 3.7K -> target 7K+)
Must include update rules for each optimizer:
- SGD: $$\theta_{t+1} = \theta_t - \eta \nabla L(\theta_t)$$
- Momentum: $$v_t = \gamma v_{t-1} + \eta \nabla L$$, $$\theta_{t+1} = \theta_t - v_t$$
- Nesterov: lookahead gradient
- AdaGrad: $$\theta_{t+1} = \theta_t - \frac{\eta}{\sqrt{G_t + \epsilon}} \nabla L$$
- RMSProp: exponential moving average of squared gradients
- Adam: $$m_t, v_t$$ with bias correction, full update formula
- AdamW: decoupled weight decay
- LAMB / LARS for large-batch training

#### Node 79 — Categorical Features (NEW, target 6K+)
Must cover:
- One-Hot Encoding: pros (linear models), cons (high cardinality)
- Label Encoding: ordinal assumption
- Target Encoding: $$\hat{y}_c = \lambda \cdot \bar{y}_c + (1-\lambda) \cdot \bar{y}_{global}$$
- Frequency/Count Encoding
- Binary Encoding
- Embedding (learned representations for deep models)
- CatBoost ordered target encoding
- Handling high-cardinality: hashing trick, embedding

#### Remaining nodes (67, 71-73, 75-78, 80-88):
- Translate to Chinese
- Expand with additional formulas where applicable
- Ensure all concepts are explained with Chinese prose
- Add interview-relevant examples

### Pillar 3: ML System Design (19 nodes)
**Node IDs**: 89-107
**Type**: Translation + moderate expansion
**Target size**: 6-8K chars per node

**Expansion focus**:
- System architecture descriptions in Chinese
- Latency/throughput analysis with concrete numbers
- Design pattern formulas (e.g., Two-Tower: $$score(u,i) = f(u)^T g(i)$$)
- Multi-Stage Ranking: recall -> pre-ranking -> ranking -> re-ranking pipeline
- A/B Testing: statistical formulas (sample size, MDE, power)
- Feature Store: online/offline architecture patterns
- Knowledge Distillation: $$L = \alpha L_{hard} + (1-\alpha) T^2 L_{soft}$$

### Pillar 4: Applied ML & Domain-Specific (18 nodes)
**Node IDs**: 108-125
**Type**: Translation + expansion
**Target size**: 6-10K (large nodes like 111, 114, 115 keep current size)

**Expansion focus**:
- Collaborative Filtering: matrix factorization $$R \approx U^TV$$
- Learning to Rank: already 33K, just translate
- CTR Prediction: DeepFM, DCN architecture formulas
- Causal Inference: ATE, CATE, propensity score formulas
- SHAP: Shapley value formula $$\phi_i = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N|-|S|-1)!}{|N|!}[f(S \cup \{i\}) - f(S)]$$

### Pillar 5: ML Infrastructure & MLOps (15 nodes)
**Node IDs**: 126-140
**Type**: Translation + moderate expansion
**Target size**: 6-8K chars per node

**Expansion focus**:
- Distributed Training: Data Parallel, Model Parallel, Pipeline Parallel formulas
- Mixed Precision: FP16/BF16/FP8 representation, loss scaling
- Quantization: INT8/INT4 calibration methods
- Model Monitoring: PSI, KS test for drift detection

### Pillar 6: Deep Learning & LLM Specialization (24 nodes)
**Node IDs**: 141-164
**Type**: Translation + deep expansion
**Target size**: 6-10K chars per node

**Expansion focus**:
- Self-Attention: $$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
- Multi-Head: $$\text{MultiHead}(Q,K,V) = \text{Concat}(head_1,...,head_h)W^O$$
- RoPE: rotation matrix derivation
- Flash Attention: tiling algorithm, IO complexity
- LoRA: $$W' = W + BA$$ where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times k}$
- RLHF: reward model training -> PPO optimization
- KV Cache: memory formula $$2 \times n_{layers} \times d_{model} \times seq\_len \times batch$$
- Quantization: GPTQ (layer-wise), AWQ (activation-aware), SmoothQuant
- RAG: chunking strategies, retrieval metrics, reranking

### Pillar 7: Math & Statistics Foundations (14 nodes)
**Node IDs**: 165-178
**Type**: Translation + DEEP expansion (rigorous math)
**Target size**: 6-10K chars per node

**Expansion requirements by node**:

#### Node 165 — Probability Basics
- Bayes theorem: $$P(A|B) = \frac{P(B|A)P(A)}{P(B)}$$ with full derivation
- Total probability: $$P(B) = \sum_i P(B|A_i)P(A_i)$$
- Independence vs conditional independence

#### Node 166 — Common Distributions
For each distribution give: PDF/PMF, CDF, E[X], Var[X], MGF, ML use case
- Bernoulli, Binomial, Poisson, Geometric
- Uniform, Gaussian, Exponential, Gamma, Beta, Chi-squared, Student-t

#### Node 168 — MLE & MAP
- MLE derivation for Gaussian: $$\hat{\mu}_{MLE} = \frac{1}{n}\sum x_i$$
- MAP with prior: $$\hat{\theta}_{MAP} = \arg\max P(\theta|D) = \arg\max P(D|\theta)P(\theta)$$
- Connection: MAP with uniform prior = MLE
- Concrete example: Bernoulli MLE vs MAP with Beta prior

#### Node 170 — Hypothesis Testing
- Type I/II error definitions with formulas
- p-value: $$p = P(T \geq t_{obs} | H_0)$$
- Power: $$1 - \beta = P(\text{reject } H_0 | H_1 \text{ true})$$
- Sample size formula for A/B testing
- Multiple testing correction: Bonferroni, FDR

#### Node 172 — Information Theory
- Entropy: $$H(X) = -\sum p(x) \log p(x)$$
- Cross-entropy: $$H(p,q) = -\sum p(x) \log q(x)$$
- KL divergence: properties, asymmetry
- Mutual information: $$I(X;Y) = H(X) - H(X|Y)$$
- Connection to ML loss functions

#### Node 178 — Convex Optimization
- KKT conditions (all 4): stationarity, primal feasibility, dual feasibility, complementary slackness
- Lagrange dual derivation
- Strong vs weak duality
- Connection to SVM optimization

### Pillar 8: Behavioral & Leadership (12 nodes)
**Node IDs**: 179-190
**Type**: Pure translation (no expansion needed)
**Target size**: Keep current ~6-9K chars per node

**Translation notes**:
- Company names stay English: Google, Amazon, Airbnb
- Framework names stay English: STAR-T, Leadership Principles
- Story structures translate the pattern, keep the examples relatable

---

## Execution Method

Each task runs as an autonomous session via `autonomous_run.sh`. The session:

1. Reads this spec file for context
2. Queries framework_nodes for the target pillar nodes
3. For each node:
   a. Read current English description
   b. Translate to Chinese following the rules above
   c. Expand with formulas/examples per the per-node specs
   d. Validate: check no formulas in code blocks, size target met
   e. UPDATE framework_nodes SET description=? WHERE id=?
4. Commits changes to the database
5. Updates PROGRESS.md and task status

**Database path**: `data/mle_prep.db`
**Table**: `framework_nodes`
**Column**: `description` (TEXT)

**Validation script** (run after each node update):
```python
import sqlite3, re
conn = sqlite3.connect('data/mle_prep.db')
for node_id in TARGET_IDS:
    desc = conn.execute('SELECT description FROM framework_nodes WHERE id=?', (node_id,)).fetchone()[0]
    # Check 1: No formulas inside code blocks
    code_blocks = re.findall(r'```[\s\S]*?```', desc)
    for block in code_blocks:
        assert '$$' not in block, f'Node {node_id}: formula inside code block!'
    # Check 2: Size target
    assert len(desc) >= MIN_SIZE, f'Node {node_id}: too short ({len(desc)} chars)'
    # Check 3: Has Chinese characters
    assert re.search(r'[\u4e00-\u9fff]', desc), f'Node {node_id}: no Chinese found!'
    print(f'Node {node_id}: OK ({len(desc)} chars)')
```

---

## Company Documents Phase

### T-P0-119: Fix formula rendering
- Query all 13 docs: `SELECT id, content FROM company_documents`
- Find code blocks containing `$$`: regex ```` ```[\s\S]*?\$\$[\s\S]*?``` ````
- Extract formulas, replace code block with bare `$$...$$`
- UPDATE the fixed content back

### T-P1-128: Convert Doc 2 + Doc 3
- Doc 2 (id=2, 504 chars): LinkedIn scheduling notes -> Chinese
- Doc 3 (id=3, 4.9K chars): Uber phone screen prep -> Chinese
- Keep interview question content structure

### T-P1-129: Convert Doc 4
- Doc 4 (id=4, 20K chars): DoorDash project deep dive -> Chinese
- Heavy technical content, keep all code/formulas, translate explanations

### T-P1-130: Rebuild All-in-One (Doc 19)
- Depends on: T-P0-119, T-P1-128, T-P1-129
- Merge docs 12-18, 20 content into doc 19
- Regenerate with updated content
