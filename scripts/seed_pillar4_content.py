"""Seed Pillar 4 (Applied ML & Domain-Specific) framework node descriptions.

Usage:
    python scripts/seed_pillar4_content.py

Populates the `description` field for all 18 Pillar 4 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== RECOMMENDER SYSTEMS =====

CONTENT["pillar4.recommender_systems.collaborative_filtering"] = r"""# Collaborative Filtering

## Overview
Collaborative filtering (CF) is the workhorse of recommendation systems at every major tech company. It predicts a user's preference by leveraging the collective behavior of many users. A senior MLE must understand both memory-based and model-based CF, their scalability trade-offs, and the cold-start problem that motivates hybrid approaches.

## Core Concepts

### User-Item Interaction Matrix
Given $$m$$ users and $$n$$ items, define $$R \in \mathbb{R}^{m \times n}$$ where $$r_{ui}$$ is user $$u$$'s rating (or implicit signal) for item $$i$$. In practice $$R$$ is extremely sparse ($$< 1\%$$ filled).

### Memory-Based CF

**User-based**: Find users similar to $$u$$, aggregate their ratings:

$$
\hat{r}_{ui} = \bar{r}_u + \frac{\sum_{v \in \mathcal{N}(u)} \text{sim}(u, v)(r_{vi} - \bar{r}_v)}{\sum_{v \in \mathcal{N}(u)} |\text{sim}(u, v)|}
$$

**Item-based**: Find items similar to $$i$$, aggregate user's ratings on them:

$$
\hat{r}_{ui} = \frac{\sum_{j \in \mathcal{N}(i)} \text{sim}(i, j)\, r_{uj}}{\sum_{j \in \mathcal{N}(i)} |\text{sim}(i, j)|}
$$

**Cosine similarity** between users:

$$
\text{sim}(u, v) = \frac{\mathbf{r}_u \cdot \mathbf{r}_v}{\|\mathbf{r}_u\| \|\mathbf{r}_v\|}
$$

### Model-Based CF: Matrix Factorization

Decompose $$R \approx P Q^T$$ where $$P \in \mathbb{R}^{m \times k}$$ and $$Q \in \mathbb{R}^{n \times k}$$.

**Objective (with biases)**:

$$
\min_{P, Q, b} \sum_{(u,i) \in \Omega} \left(r_{ui} - \mu - b_u - b_i - \mathbf{p}_u^T \mathbf{q}_i\right)^2 + \lambda\left(\|\mathbf{p}_u\|^2 + \|\mathbf{q}_i\|^2 + b_u^2 + b_i^2\right)
$$

where $$\Omega$$ is the set of observed entries.

**ALS (Alternating Least Squares)**: Fix $$Q$$, solve for $$P$$ in closed form, then alternate. Parallelizable -- used at Netflix, Spotify.

**SGD update**: $$\mathbf{p}_u \leftarrow \mathbf{p}_u + \eta (e_{ui} \mathbf{q}_i - \lambda \mathbf{p}_u)$$ where $$e_{ui} = r_{ui} - \hat{r}_{ui}$$.

### Implicit Feedback
When only clicks/views (not ratings) are available, use **Weighted ALS**:

$$
\min \sum_{u,i} c_{ui}\left(p_{ui} - \mathbf{p}_u^T \mathbf{q}_i\right)^2 + \lambda(\|P\|^2 + \|Q\|^2)
$$

where $$c_{ui} = 1 + \alpha \cdot f(r_{ui})$$ is a confidence weight and $$p_{ui} \in \{0,1\}$$ is a preference indicator.

## Implementation

```python
import numpy as np

def als_step(
    R: np.ndarray, U: np.ndarray, V: np.ndarray, lam: float,
) -> np.ndarray:
    # One ALS step: fix V, solve for U.
    k = V.shape[1]
    U_new = np.zeros_like(U)
    for u in range(R.shape[0]):
        rated = R[u] > 0
        V_u = V[rated]
        r_u = R[u, rated]
        A = V_u.T @ V_u + lam * np.eye(k)
        b = V_u.T @ r_u
        U_new[u] = np.linalg.solve(A, b)
    return U_new

# BPR (Bayesian Personalized Ranking) for implicit feedback
def bpr_update(
    U: np.ndarray, V: np.ndarray,
    u: int, i: int, j: int, lr: float, lam: float,
) -> None:
    # One BPR-SGD step: user u prefers item i over item j.
    x_uij = U[u] @ V[i] - U[u] @ V[j]
    sigmoid = 1.0 / (1.0 + np.exp(min(x_uij, 500)))
    U[u] += lr * (sigmoid * (V[i] - V[j]) - lam * U[u])
    V[i] += lr * (sigmoid * U[u] - lam * V[i])
    V[j] += lr * (-sigmoid * U[u] - lam * V[j])
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Cold start mitigation | New users/items with no history | Fall back to content-based, popularity, or use side features |
| Implicit vs explicit | Clicks vs ratings data | Implicit is noisier but far more abundant; use confidence weighting |
| ALS vs SGD | Training matrix factorization | ALS parallelizes across users/items; SGD is simpler but sequential |
| BPR for ranking | Optimize ranking, not rating prediction | Pairwise loss directly optimizes relative ordering |

### Common Interview Questions
- [ ] Explain user-based vs item-based CF. When would you prefer each?
- [ ] Derive the ALS update for one user vector in matrix factorization.
- [ ] How do you handle the cold-start problem in a production recommender?
- [ ] Compare explicit vs implicit feedback and how training differs.
- [ ] How would you evaluate a recommender system offline vs online?

## Comparisons

| Aspect | Memory-Based CF | Model-Based CF (MF) |
|--------|----------------|---------------------|
| Scalability | $$O(mn)$$ similarity computation | $$O(|\Omega| k)$$ training |
| Cold start | No items with no co-ratings | Can incorporate side features |
| Latency | Real-time similarity lookup | Pre-computed embeddings |
| Explainability | "Users like you also liked..." | Latent factors harder to interpret |
| Sparsity handling | Poor with very sparse data | Better -- learns dense factors |

## Key Takeaways
- Matrix factorization is the foundation of modern recommender systems
- ALS enables distributed training; BPR optimizes ranking directly
- Cold start is the central challenge -- hybrid systems combine CF with content features
- Implicit feedback requires confidence weighting, not direct optimization on counts
"""

CONTENT["pillar4.recommender_systems.content_based"] = r"""# Content-Based Recommendation Methods

## Overview
Content-based filtering recommends items similar to what a user has liked before, using item features rather than collaborative signals. It solves the cold-start problem for new items and provides transparent recommendations. A senior MLE must understand feature engineering for items, user profile construction, and when to prefer content-based over collaborative approaches.

## Core Concepts

### User Profile Construction
Build a user profile $$\mathbf{u}$$ from the feature vectors of items they have interacted with:

$$
\mathbf{u} = \frac{\sum_{i \in \mathcal{I}_u} w_i \, \mathbf{x}_i}{\sum_{i \in \mathcal{I}_u} w_i}
$$

where $$\mathbf{x}_i$$ is the feature vector of item $$i$$, $$w_i$$ is the interaction weight (e.g., rating, dwell time), and $$\mathcal{I}_u$$ is the set of items user $$u$$ interacted with.

### TF-IDF for Text Features
For text-heavy items (articles, products), TF-IDF provides a strong baseline:

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \log \frac{N}{|\{d' : t \in d'\}|}
$$

### Similarity Scoring
Score candidate item $$j$$ against user profile $$\mathbf{u}$$:

$$
\text{score}(u, j) = \cos(\mathbf{u}, \mathbf{x}_j) = \frac{\mathbf{u} \cdot \mathbf{x}_j}{\|\mathbf{u}\|\, \|\mathbf{x}_j\|}
$$

### Embedding-Based Content Features
Modern approaches use pre-trained embeddings:

| Feature Source | Model | Dimension |
|---------------|-------|-----------|
| Text | BERT / Sentence-BERT | 768 |
| Images | ResNet / CLIP | 512-2048 |
| Categories | Learned embedding | 32-128 |

Final item representation: $$\mathbf{x}_i = [\mathbf{e}_{\text{text}}; \mathbf{e}_{\text{image}}; \mathbf{e}_{\text{cat}}]$$ (concatenation or projection).

### Learning to Recommend
Train a classifier to predict user-item affinity:

$$
\hat{y}_{ui} = \sigma(\mathbf{w}^T [\mathbf{u}; \mathbf{x}_i] + b)
$$

Loss: binary cross-entropy with negative sampling.

## Implementation

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_user_profile(
    item_features: np.ndarray,
    ratings: np.ndarray,
) -> np.ndarray:
    # Weighted average of item features by user ratings.
    mask = ratings > 0
    if not mask.any():
        return np.zeros(item_features.shape[1])
    weighted = item_features[mask] * ratings[mask, np.newaxis]
    return weighted.sum(axis=0) / ratings[mask].sum()

def content_recommend(
    user_profile: np.ndarray,
    item_features: np.ndarray,
    seen: set[int],
    top_k: int = 10,
) -> list[int]:
    # Recommend top-k unseen items by cosine similarity.
    scores = cosine_similarity(
        user_profile.reshape(1, -1), item_features,
    )[0]
    ranked = np.argsort(-scores)
    return [i for i in ranked if i not in seen][:top_k]
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Feature filter bubble | User only sees similar items | Add diversity/exploration (MMR, epsilon-greedy) |
| Cold start for items | New item with no interactions | Content features provide immediate recommendations |
| Hybrid approach | Combine CF + content | Two-tower model with user and item towers |
| Embedding similarity | Rich unstructured item data | Pre-trained embeddings outperform hand-crafted features |

### Common Interview Questions
- [ ] How do you build a content-based recommender for a news feed?
- [ ] What is the filter bubble problem and how do you mitigate it?
- [ ] Compare TF-IDF vs embedding-based item representations.
- [ ] How would you combine content-based and collaborative filtering?
- [ ] Design a content-based system for a new platform with no user history.

## Comparisons

| Aspect | Content-Based | Collaborative Filtering |
|--------|--------------|------------------------|
| Cold start (new items) | Handles well | Cannot recommend |
| Cold start (new users) | Needs some preferences | Cannot recommend |
| Serendipity | Low (filter bubble) | High (cross-user patterns) |
| Feature engineering | Required | Not needed |
| Scalability | Feature extraction cost | Interaction matrix cost |

## Key Takeaways
- Content-based methods solve the new-item cold-start problem
- Pre-trained embeddings (BERT, CLIP) have largely replaced TF-IDF for feature extraction
- Filter bubble is the main risk -- add diversity mechanisms
- In practice, hybrid systems combining CF + content outperform either alone
"""

CONTENT["pillar4.recommender_systems.deep_recommendation"] = r"""# Deep Recommendation Models

## Overview
Deep learning has transformed recommender systems from matrix factorization into rich, multi-modal neural architectures. A senior MLE must understand the two-tower paradigm, attention-based sequential models, and the retrieval-ranking pipeline used at scale (YouTube, TikTok, Pinterest). These architectures appear in almost every MLE system design interview.

## Core Concepts

### Two-Tower Architecture
Separate user and item encoders produce embeddings, scored by dot product:

$$
\text{score}(u, i) = f_\theta(\mathbf{x}_u)^T g_\phi(\mathbf{x}_i)
$$

- **User tower** $$f_\theta$$: encodes user features + history
- **Item tower** $$g_\phi$$: encodes item features (text, image, metadata)
- At serving: pre-compute item embeddings, use ANN for retrieval

### Wide & Deep (Google, 2016)
Combines memorization (wide) and generalization (deep):

$$
\hat{y} = \sigma\!\left(\mathbf{w}_{\text{wide}}^T [\mathbf{x}; \phi(\mathbf{x})] + \mathbf{w}_{\text{deep}}^T \, a^{(L)} + b\right)
$$

where $$\phi(\mathbf{x})$$ is cross-product features and $$a^{(L)}$$ is the deep network output.

### Deep & Cross Network (DCN)
Explicit feature crossing at each layer:

$$
\mathbf{x}_{l+1} = \mathbf{x}_0 \, \mathbf{x}_l^T \mathbf{w}_l + \mathbf{b}_l + \mathbf{x}_l
$$

This learns bounded-degree feature interactions without manual feature engineering.

### Sequential Recommendation (SASRec)
Self-attention over user's interaction sequence:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d}}\right) V
$$

with causal masking to prevent future information leakage. Captures both short and long-term preferences.

### Multi-Task Learning
Joint optimization of multiple objectives (click, add-to-cart, purchase):

$$
\mathcal{L} = \sum_{t=1}^{T} w_t \mathcal{L}_t + \lambda \|\theta\|^2
$$

Shared bottom layers with task-specific towers (MMoE: Mixture of Experts gating).

### Retrieval-Ranking Pipeline

| Stage | Candidates | Model | Latency |
|-------|-----------|-------|---------|
| Candidate Generation | Millions -> 1000s | Two-tower + ANN | < 50ms |
| Scoring/Ranking | 1000s -> 100s | Deep cross network | < 100ms |
| Re-ranking | 100s -> 10s | Business rules, diversity | < 10ms |

## Implementation

```python
import numpy as np

class TwoTowerModel:
    # Simplified two-tower for illustration.

    def __init__(self, user_dim: int, item_dim: int, emb_dim: int) -> None:
        self.W_user = np.random.randn(user_dim, emb_dim) * 0.01
        self.W_item = np.random.randn(item_dim, emb_dim) * 0.01

    def user_embed(self, x_user: np.ndarray) -> np.ndarray:
        return x_user @ self.W_user

    def item_embed(self, x_item: np.ndarray) -> np.ndarray:
        return x_item @ self.W_item

    def score(self, x_user: np.ndarray, x_item: np.ndarray) -> float:
        u = self.user_embed(x_user)
        v = self.item_embed(x_item)
        return float(u @ v)

# In-batch negatives for contrastive learning
def in_batch_loss(
    user_embs: np.ndarray, item_embs: np.ndarray, temp: float = 0.1,
) -> float:
    # Softmax cross-entropy with in-batch negatives.
    logits = user_embs @ item_embs.T / temp  # (B, B)
    labels = np.arange(logits.shape[0])
    # Numerically stable softmax CE
    shifted = logits - logits.max(axis=1, keepdims=True)
    log_sum_exp = np.log(np.exp(shifted).sum(axis=1))
    loss = -shifted[np.arange(len(labels)), labels] + log_sum_exp
    return float(loss.mean())
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Two-tower + ANN | Large-scale retrieval | Decoupled towers enable offline item indexing |
| In-batch negatives | Contrastive learning at scale | Free negatives from the batch, but popularity bias |
| Multi-task learning | Multiple engagement signals | MMoE balances task-specific vs shared representations |
| Feature crossing | Sparse categorical features | DCN/DeepFM automate what feature engineers used to do manually |

### Common Interview Questions
- [ ] Walk through the YouTube recommendation pipeline from candidate generation to ranking.
- [ ] Why use a two-tower model instead of a single joint model for retrieval?
- [ ] How do in-batch negatives work and what are their limitations?
- [ ] Compare Wide & Deep, DCN, and DeepFM architectures.
- [ ] How would you add a new optimization objective (e.g., dwell time) to an existing multi-task model?

## Comparisons

| Aspect | Matrix Factorization | Two-Tower | Full Cross-Network |
|--------|---------------------|-----------|-------------------|
| Feature support | IDs only | Rich features | Rich features |
| Serving | Fast dot product | ANN retrieval | Full forward pass |
| Training | ALS/SGD on ratings | Contrastive/softmax | Pointwise/pairwise |
| Expressiveness | Linear interactions | Non-linear towers | Explicit + implicit crosses |
| Use case | Candidate gen | Candidate gen | Ranking stage |

## Key Takeaways
- The retrieval-ranking funnel is the standard architecture for large-scale recommenders
- Two-tower models decouple user and item computation for efficient serving
- Sequential models (SASRec, BERT4Rec) capture temporal user behavior
- Multi-task learning is essential when optimizing multiple engagement signals
"""

# ===== SEARCH & INFORMATION RETRIEVAL =====

CONTENT["pillar4.search_ir.classic_ir"] = r"""# Classic IR: BM25 & TF-IDF

## Overview
Classic information retrieval methods remain the backbone of search systems at every tech company. BM25 is still a strong baseline that outperforms many neural methods on short queries. A senior MLE must understand term-frequency models, inverted indices, and why these "simple" methods are hard to beat for keyword-matching tasks.

## Core Concepts

### TF-IDF
Term frequency-inverse document frequency weights terms by their discriminative power:

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \text{IDF}(t)
$$

$$
\text{IDF}(t) = \log \frac{N}{|\{d : t \in d\}|}
$$

where $$N$$ is the total number of documents.

### BM25 (Okapi BM25)
The standard probabilistic ranking function:

$$
\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}
$$

| Parameter | Typical Value | Effect |
|-----------|--------------|--------|
| $$k_1$$ | 1.2 - 2.0 | Term frequency saturation |
| $$b$$ | 0.75 | Document length normalization |
| avgdl | Corpus-dependent | Average document length |

Key insight: $$k_1$$ controls how quickly TF saturates (diminishing returns for repeated terms). $$b$$ penalizes long documents.

### Inverted Index
The data structure enabling sub-linear retrieval:

```
"machine" -> [(doc1, pos=[3,17]), (doc5, pos=[1])]
"learning" -> [(doc1, pos=[4,18]), (doc2, pos=[7])]
```

**Posting list operations**: intersection (AND), union (OR), skip pointers for efficiency.

### Evaluation Metrics

$$
\text{Precision@k} = \frac{|\text{relevant docs in top-k}|}{k}
$$

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{rel_i} - 1}{\log_2(i + 1)}
$$

$$
\text{MAP} = \frac{1}{|Q|} \sum_{q \in Q} \text{AP}(q), \quad \text{AP} = \frac{\sum_{k} P@k \cdot \text{rel}(k)}{|\text{relevant}|}
$$

## Implementation

```python
import math
from collections import Counter

def bm25_score(
    query_terms: list[str],
    doc_terms: list[str],
    doc_freq: dict[str, int],
    n_docs: int,
    avgdl: float,
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    # Compute BM25 score for a single document.
    tf = Counter(doc_terms)
    dl = len(doc_terms)
    score = 0.0
    for t in query_terms:
        if t not in tf:
            continue
        df = doc_freq.get(t, 0)
        idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)
        numerator = tf[t] * (k1 + 1)
        denominator = tf[t] + k1 * (1 - b + b * dl / avgdl)
        score += idf * numerator / denominator
    return score

def ndcg_at_k(relevances: list[int], k: int) -> float:
    # Compute NDCG@k from a ranked list of relevance scores.
    dcg = sum(
        (2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(relevances[:k])
    )
    ideal = sorted(relevances, reverse=True)[:k]
    idcg = sum(
        (2**rel - 1) / math.log2(i + 2) for i, rel in enumerate(ideal)
    )
    return dcg / idcg if idcg > 0 else 0.0
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| BM25 as baseline | Any search system | Always start here -- surprisingly hard to beat |
| Length normalization | Documents of varying length | $$b$$ parameter prevents long-doc bias |
| TF saturation | Repeated terms | One occurrence of "ML" matters; ten does not matter 10x more |
| Inverted index design | System design interviews | Skip pointers, compression, sharding |

### Common Interview Questions
- [ ] Explain BM25 and the role of each parameter ($$k_1$$, $$b$$).
- [ ] Why is BM25 often better than TF-IDF for ranking?
- [ ] Design an inverted index that can handle 1B documents.
- [ ] What is NDCG and why is it preferred over precision for graded relevance?
- [ ] How would you combine BM25 with a neural re-ranker?

## Comparisons

| Aspect | TF-IDF | BM25 | Neural Retrieval |
|--------|--------|------|-----------------|
| Term frequency | Linear | Saturating | Learned |
| Length normalization | Cosine norm | $$b$$ parameter | Implicit |
| Semantic matching | None (exact match) | None (exact match) | Yes |
| Latency | Very fast | Very fast | Slower (embeddings) |
| Training data needed | None | None | Large amounts |

## Key Takeaways
- BM25 is still the strongest lexical baseline; always benchmark against it
- The inverted index is the fundamental data structure of search engineering
- NDCG is the standard offline metric for search quality with graded relevance
- In production, BM25 is typically the first-stage retriever before neural re-ranking
"""

CONTENT["pillar4.search_ir.neural_retrieval"] = r"""# Neural Retrieval

## Overview
Neural retrieval replaces or augments lexical matching with learned dense representations. This enables semantic search -- matching queries to documents by meaning, not just keywords. A senior MLE must understand dense retrieval, cross-encoders, the bi-encoder vs cross-encoder trade-off, and how to deploy these models at scale with approximate nearest neighbor (ANN) search.

## Core Concepts

### Dense Retrieval (Bi-Encoder)
Encode query and document independently:

$$
\text{score}(q, d) = E_q(q)^T E_d(d)
$$

where $$E_q, E_d$$ are typically BERT-based encoders. Documents are encoded offline; queries at serving time.

### Cross-Encoder
Joint encoding of query-document pairs:

$$
\text{score}(q, d) = \text{MLP}(\text{BERT}([q; \text{SEP}; d]))
$$

More expressive (full attention between $$q$$ and $$d$$) but $$O(n)$$ inference cost -- only feasible for re-ranking.

### Contrastive Training
InfoNCE loss with in-batch negatives:

$$
\mathcal{L} = -\log \frac{\exp(E_q(q)^T E_d(d^+) / \tau)}{\sum_{d' \in \mathcal{B}} \exp(E_q(q)^T E_d(d') / \tau)}
$$

**Hard negative mining** is critical: random negatives are too easy; BM25-retrieved non-relevant docs provide more signal.

### ColBERT: Late Interaction
Token-level interaction between query and document:

$$
\text{score}(q, d) = \sum_{i} \max_{j} \mathbf{q}_i^T \mathbf{d}_j
$$

Maintains separate encodings but uses MaxSim for richer matching than a single dot product.

### ANN Search at Scale
| Algorithm | Index Build | Query Time | Memory |
|-----------|------------|------------|--------|
| HNSW | Slow | $$O(\log n)$$ | High |
| IVF-PQ | Moderate | Sub-linear | Low (compressed) |
| ScaNN | Moderate | Sub-linear | Moderate |

## Implementation

```python
import numpy as np

def contrastive_loss(
    q_embs: np.ndarray, d_embs: np.ndarray, temperature: float = 0.05,
) -> float:
    # InfoNCE loss with in-batch negatives.
    logits = q_embs @ d_embs.T / temperature
    labels = np.arange(logits.shape[0])
    shifted = logits - logits.max(axis=1, keepdims=True)
    log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    return -float(log_probs[np.arange(len(labels)), labels].mean())

def colbert_score(
    q_tokens: np.ndarray, d_tokens: np.ndarray,
) -> float:
    # ColBERT MaxSim late interaction score.

    q_tokens: (Lq, dim), d_tokens: (Ld, dim)

    sim_matrix = q_tokens @ d_tokens.T  # (Lq, Ld)
    return float(sim_matrix.max(axis=1).sum())

def reciprocal_rank_fusion(
    *ranked_lists: list[str], k: int = 60,
) -> list[str]:
    # Fuse multiple ranked lists using RRF.
    scores: dict[str, float] = {}
    for rlist in ranked_lists:
        for rank, doc_id in enumerate(rlist):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Bi-encoder + ANN | First-stage retrieval at scale | Pre-compute doc embeddings, ANN for sub-linear search |
| Cross-encoder re-ranking | Top-k re-ranking | Much more accurate but too slow for full corpus |
| Hybrid BM25 + dense | Production search systems | Lexical and semantic signals are complementary |
| Hard negative mining | Training dense retrievers | Without hard negatives, model learns trivial distinctions |

### Common Interview Questions
- [ ] Compare bi-encoder and cross-encoder for search. When would you use each?
- [ ] How does hard negative mining improve dense retrieval training?
- [ ] Explain ColBERT's late interaction mechanism and its trade-offs.
- [ ] Design a hybrid retrieval system combining BM25 and dense retrieval.
- [ ] How would you handle embedding drift when documents are updated frequently?

## Comparisons

| Aspect | BM25 | Bi-Encoder | Cross-Encoder | ColBERT |
|--------|------|-----------|---------------|---------|
| Semantic matching | No | Yes | Yes | Yes |
| Serving latency | Fastest | Fast (ANN) | Slow ($$O(n)$$) | Moderate |
| Expressiveness | Low | Medium | Highest | High |
| Index size | Inverted index | Dense vectors | N/A (no index) | Token-level vectors |
| Use case | First stage | First stage | Re-ranking | Either |

## Key Takeaways
- Dense retrieval enables semantic matching beyond keyword overlap
- The bi-encoder/cross-encoder trade-off is latency vs accuracy
- Hard negative mining is the single most impactful training improvement
- Hybrid BM25 + dense retrieval outperforms either method alone in production
"""

CONTENT["pillar4.search_ir.query_understanding"] = r"""# Query Understanding

## Overview
Query understanding (QU) transforms raw user queries into structured search intents. It bridges the gap between what users type and what the search system needs to retrieve. A senior MLE must understand query classification, expansion, rewriting, spell correction, and entity recognition -- these directly impact search relevance at every major tech company.

## Core Concepts

### Query Classification
Classify queries into intent categories:

$$
P(\text{intent} \mid q) = \text{softmax}(\mathbf{W}\, \text{BERT}(q) + \mathbf{b})
$$

| Intent Type | Example | Action |
|-------------|---------|--------|
| Navigational | "youtube" | Direct to site |
| Informational | "how does BM25 work" | Show knowledge results |
| Transactional | "buy running shoes" | Show product listings |
| Local | "coffee near me" | Trigger location search |

### Query Expansion
Add related terms to improve recall:

**Pseudo-relevance feedback (PRF)**: Retrieve top-k docs with original query, extract frequent terms, expand:

$$
q_{\text{expanded}} = \alpha \cdot q + (1 - \alpha) \sum_{d \in \text{top-k}} \text{TF-IDF}(t, d) \cdot t
$$

**Synonym expansion**: Use embeddings to find semantically similar terms:

$$
\text{synonyms}(t) = \{t' : \cos(E(t), E(t')) > \theta\}
$$

### Spell Correction
**Noisy channel model**:

$$
\hat{q} = \arg\max_{q'} P(q' \mid q) = \arg\max_{q'} P(q \mid q') \, P(q')
$$

where $$P(q \mid q')$$ is the error model (edit distance) and $$P(q')$$ is the language model.

**Edit distance** (Levenshtein): minimum insertions, deletions, substitutions to transform $$q$$ into $$q'$$.

### Named Entity Recognition (NER) in Queries
Short queries make NER harder:
- "iphone 15 pro max case" -> [product: "iphone 15 pro max"] [category: "case"]
- "flights from SFO to JFK" -> [origin: "SFO"] [destination: "JFK"]

Sequence labeling with BIO tags using BERT + CRF.

### Query Rewriting
Neural query rewriting for better retrieval:

$$
q_{\text{rewritten}} = \text{Seq2Seq}(q_{\text{original}}, \text{context})
$$

At scale, use LLMs for query rewriting with few-shot prompts.

## Implementation

```python
def edit_distance(s1: str, s2: str) -> int:
    # Compute Levenshtein edit distance.
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1],
                )
    return dp[m][n]

def pseudo_relevance_feedback(
    query_terms: list[str],
    top_docs: list[list[str]],
    alpha: float = 0.6,
    n_expand: int = 5,
) -> list[str]:
    # Expand query with frequent terms from top documents.
    from collections import Counter
    doc_terms = Counter()
    for doc in top_docs:
        doc_terms.update(set(doc))
    for t in query_terms:
        del doc_terms[t]  # Remove original query terms
    expansion = [t for t, _ in doc_terms.most_common(n_expand)]
    return query_terms + expansion
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Spell correction | Noisy/mobile queries | Noisy channel = error model x language model |
| Query expansion | Low recall situations | PRF is unsupervised; embedding expansion needs less tuning |
| Intent classification | Multi-vertical search | Route queries to specialized backends |
| Entity tagging | Structured search (e-commerce, travel) | Enables slot-filling for structured retrieval |

### Common Interview Questions
- [ ] How would you build a spell correction system for a search engine?
- [ ] Explain pseudo-relevance feedback and its failure modes.
- [ ] Design a query understanding pipeline for an e-commerce search.
- [ ] How do you handle ambiguous queries ("apple" -- fruit or company)?
- [ ] When would you use LLM-based query rewriting vs traditional expansion?

## Comparisons

| Approach | Latency | Training Data | Recall Impact |
|----------|---------|--------------|---------------|
| Synonym dictionaries | Negligible | Manual curation | Moderate |
| Pseudo-relevance feedback | High (2 retrievals) | None | High |
| Embedding expansion | Low | Unlabeled text | Moderate |
| Neural rewriting (LLM) | High | Query logs | Highest |
| Spell correction | Low | Query logs + dictionary | Critical for typos |

## Key Takeaways
- Query understanding is the highest-leverage component in a search system
- Spell correction alone can improve relevance by 5-10% on mobile traffic
- Intent classification routes queries to the right search vertical
- Modern systems use LLMs for query rewriting but cache results for latency
"""

CONTENT["pillar4.search_ir.learning_to_rank"] = r"""# Learning to Rank

## Overview
Learning to Rank (LTR) trains ML models to produce optimal orderings of search results. It is the core ranking component in every production search engine. A senior MLE must understand pointwise, pairwise, and listwise approaches, the features that matter, and how to train and evaluate ranking models at scale.

## Core Concepts

### Three Approaches to LTR

**Pointwise**: Predict relevance score independently for each document:

$$
\mathcal{L}_{\text{pointwise}} = \sum_{(q,d)} \ell(\hat{y}_{qd}, y_{qd})
$$

where $$\ell$$ is MSE or cross-entropy. Ignores inter-document relationships.

**Pairwise** (RankNet, LambdaMART): Optimize relative ordering:

$$
P(d_i \succ d_j \mid q) = \sigma(s_i - s_j)
$$

$$
\mathcal{L}_{\text{pairwise}} = -\sum_{d_i \succ d_j} \log \sigma(s_i - s_j)
$$

**Listwise** (ListNet, ApproxNDCG): Optimize over the full ranked list:

$$
\mathcal{L}_{\text{listwise}} = -\sum_q \text{NDCG}(q, \pi_\theta)
$$

Since NDCG is non-differentiable, use softmax approximation or lambda gradients.

### LambdaMART
The most widely used LTR algorithm in production. Combines gradient-boosted trees with lambda gradients:

$$
\lambda_{ij} = \frac{-\sigma}{1 + e^{\sigma(s_i - s_j)}} |\Delta \text{NDCG}_{ij}|
$$

where $$|\Delta \text{NDCG}_{ij}|$$ weights each pair by how much swapping $$i$$ and $$j$$ changes NDCG. This directly optimizes the ranking metric.

### Feature Engineering for LTR

| Category | Features | Examples |
|----------|----------|---------|
| Query-Document | Relevance signals | BM25, TF-IDF, BERT score |
| Document | Quality signals | PageRank, freshness, length |
| Query | Difficulty signals | Query length, frequency, entropy |
| User | Personalization | Click history, location, device |
| Interaction | Historical | CTR for this query-doc pair |

### Position Bias
Users click higher-ranked results regardless of relevance. Must correct for this:

$$
P(\text{click} \mid q, d, \text{pos}) = P(\text{examine} \mid \text{pos}) \cdot P(\text{relevant} \mid q, d)
$$

**Inverse propensity weighting (IPW)**: weight training examples by $$1 / P(\text{examine} \mid \text{pos})$$.

## Implementation

```python
import numpy as np

def pairwise_loss(
    scores: np.ndarray, relevances: np.ndarray,
) -> float:
    # RankNet pairwise cross-entropy loss.
    n = len(scores)
    loss = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if relevances[i] > relevances[j]:
                diff = scores[i] - scores[j]
                loss += np.log(1 + np.exp(-diff))
                count += 1
    return loss / max(count, 1)

def lambda_weight(
    scores: np.ndarray,
    relevances: np.ndarray,
    i: int, j: int,
) -> float:
    # Compute lambda gradient weight for a pair.
    sigma = 1.0
    s_diff = scores[i] - scores[j]
    rho = 1.0 / (1.0 + np.exp(sigma * s_diff))
    # Approximate delta NDCG
    ranks = np.argsort(-scores)
    rank_i = int(np.where(ranks == i)[0][0])
    rank_j = int(np.where(ranks == j)[0][0])
    gain_i = (2**relevances[i] - 1)
    gain_j = (2**relevances[j] - 1)
    discount_i = 1.0 / np.log2(rank_i + 2)
    discount_j = 1.0 / np.log2(rank_j + 2)
    delta_ndcg = abs(
        (gain_i - gain_j) * (discount_i - discount_j)
    )
    return rho * delta_ndcg
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| LambdaMART | Production ranking with tabular features | GBT + lambda gradients = NDCG-aware optimization |
| Position debiasing | Training on click data | Clicks are biased by position; IPW corrects for examination probability |
| Feature importance | Debugging ranking quality | BM25 + click features typically dominate |
| Online learning | Rapidly changing relevance | Periodic retraining or bandit-based exploration |

### Common Interview Questions
- [ ] Explain pointwise, pairwise, and listwise LTR approaches with trade-offs.
- [ ] What are lambda gradients and why are they used in LambdaMART?
- [ ] How do you handle position bias when training on click logs?
- [ ] Design the feature set for a ranking model at an e-commerce search engine.
- [ ] How would you evaluate whether a new ranking model is better? Describe offline and online evaluation.

## Comparisons

| Aspect | Pointwise | Pairwise (RankNet) | LambdaMART | Listwise |
|--------|-----------|-------------------|-----------|----------|
| Optimization | Per-doc loss | Pair ordering | NDCG-weighted pairs | Full list metric |
| Model | Any regressor | Neural net | GBT | Neural net |
| Speed | Fastest training | Moderate | Fast (GBT) | Slowest |
| Metric alignment | Low | Medium | High | Highest |
| Production use | Rare | Research | Very common | Growing |

## Key Takeaways
- LambdaMART (GBT + lambda gradients) is the industry standard for tabular ranking
- Position bias correction is essential when training on click data
- Feature engineering matters more than model architecture for LTR
- The trend is toward neural ranking (cross-encoders) for re-ranking, with LambdaMART as the main ranker
"""

# ===== NLP & LLM APPLICATIONS =====

CONTENT["pillar4.nlp_llm_applications.text_classification"] = r"""# Text Classification

## Overview
Text classification assigns labels to text and is one of the most common ML tasks in production. Applications range from spam detection and sentiment analysis to content moderation and intent routing. A senior MLE must understand the progression from bag-of-words to fine-tuned transformers, including when simpler models suffice.

## Core Concepts

### Classical Approaches

**Bag-of-Words + Logistic Regression**:

$$
P(y \mid x) = \sigma(\mathbf{w}^T \text{TF-IDF}(x) + b)
$$

Surprisingly strong baseline. Fast to train, interpretable, works well with limited data.

**Naive Bayes**:

$$
P(y \mid x) = \frac{P(y) \prod_i P(x_i \mid y)}{P(x)}
$$

Assumes feature independence. Despite this unrealistic assumption, works well for text due to high dimensionality.

### Deep Learning Approaches

**TextCNN** (Kim, 2014): Convolutions over word embeddings with multiple filter sizes:

$$
h_i = \text{ReLU}(\mathbf{W} \cdot x_{i:i+k-1} + b)
$$

Max-pool over sequence, concatenate filter outputs, classify.

**Fine-tuned BERT**:

$$
P(y \mid x) = \text{softmax}(\mathbf{W} \cdot \text{BERT}_{\text{[CLS]}}(x) + \mathbf{b})
$$

### Multi-Label Classification
Multiple labels per document (e.g., topics, tags):

$$
\mathcal{L} = -\sum_{i=1}^{L} \left[y_i \log \hat{y}_i + (1 - y_i) \log(1 - \hat{y}_i)\right]
$$

Use sigmoid per label (not softmax). Threshold tuning per label is critical.

### Few-Shot Classification with LLMs
In-context learning without fine-tuning:

```
Classify the sentiment: "The movie was terrible but I couldn't stop watching."
Options: positive, negative, mixed
Answer: mixed
```

Cost-effective for low-volume, high-cardinality classification tasks.

### Class Imbalance
| Technique | When to Use | Implementation |
|-----------|------------|---------------|
| Class weights | Moderate imbalance (1:10) | $$w_c = N / (C \cdot N_c)$$ in loss |
| Focal loss | Severe imbalance | $$\mathcal{L} = -\alpha_t (1 - p_t)^\gamma \log p_t$$ |
| Oversampling (SMOTE) | Small datasets | Synthetic minority examples |
| Threshold tuning | Precision-recall trade-off | Per-class decision boundaries |

## Implementation

```python
import numpy as np

def focal_loss(
    y_true: np.ndarray, y_pred: np.ndarray,
    gamma: float = 2.0, alpha: float = 0.25,
) -> float:
    # Focal loss for class-imbalanced classification.
    eps = 1e-7
    y_pred = np.clip(y_pred, eps, 1 - eps)
    pt = np.where(y_true == 1, y_pred, 1 - y_pred)
    alpha_t = np.where(y_true == 1, alpha, 1 - alpha)
    loss = -alpha_t * (1 - pt) ** gamma * np.log(pt)
    return float(loss.mean())

def calibrate_threshold(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    target_precision: float = 0.95,
) -> float:
    # Find threshold achieving target precision.
    thresholds = np.linspace(0, 1, 1000)
    for t in reversed(thresholds):
        preds = (y_scores >= t).astype(int)
        tp = ((preds == 1) & (y_true == 1)).sum()
        fp = ((preds == 1) & (y_true == 0)).sum()
        precision = tp / max(tp + fp, 1)
        if precision >= target_precision:
            return float(t)
    return 1.0
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Baseline first | Any classification task | LogReg + TF-IDF before BERT; often sufficient |
| Focal loss | Imbalanced classes (fraud, spam) | Down-weights easy examples, focuses on hard ones |
| Few-shot LLM | Low volume, changing categories | No training data needed; prompt engineering suffices |
| Active learning | Limited labeling budget | Uncertainty sampling to label the most informative examples |

### Common Interview Questions
- [ ] You have 100 labeled examples per class. What model would you use?
- [ ] How do you handle a 1:1000 class imbalance in spam detection?
- [ ] Compare fine-tuned BERT vs few-shot GPT for classification.
- [ ] How would you deploy a text classifier that needs to handle new categories?
- [ ] Explain focal loss and when it outperforms standard cross-entropy.

## Comparisons

| Aspect | LogReg + TF-IDF | TextCNN | Fine-tuned BERT | Few-shot LLM |
|--------|----------------|---------|----------------|--------------|
| Training data needed | 100s-1000s | 1000s-10000s | 100s (fine-tune) | 0-10 (in-context) |
| Latency | < 1ms | ~5ms | ~50ms | ~500ms |
| Accuracy ceiling | Medium | Medium-High | Highest | High |
| Cost | Lowest | Low | Moderate | Highest per query |
| Interpretability | High | Low | Low | Moderate (CoT) |

## Key Takeaways
- Always start with LogReg + TF-IDF as a baseline; it is often sufficient
- Fine-tuned BERT is the accuracy ceiling for most text classification tasks
- Class imbalance requires both loss function changes and threshold tuning
- Few-shot LLMs are ideal for prototyping or low-volume, high-cardinality tasks
"""

CONTENT["pillar4.nlp_llm_applications.question_answering"] = r"""# Question Answering

## Overview
Question Answering (QA) systems find or generate answers to natural language questions. This is central to search, chatbots, and knowledge management systems. A senior MLE must understand extractive QA, generative QA, retrieval-augmented generation (RAG), and how to evaluate and improve QA systems in production.

## Core Concepts

### Extractive QA
Find the answer span within a given context:

$$
P(\text{start}=i, \text{end}=j \mid q, c) = \text{softmax}(\mathbf{w}_s^T h_i) \cdot \text{softmax}(\mathbf{w}_e^T h_j)
$$

where $$h_i$$ are BERT hidden states for the context tokens. Constraint: $$j \geq i$$ and $$j - i < \text{max\_len}$$.

### Generative QA
Generate the answer token-by-token:

$$
P(a \mid q, c) = \prod_{t=1}^{T} P(a_t \mid a_{<t}, q, c)
$$

using an encoder-decoder (T5) or decoder-only (GPT) model.

### Retrieval-Augmented Generation (RAG)
Combines retrieval with generation:

1. **Retrieve**: $$\mathcal{D} = \text{top-k}(\text{retriever}(q))$$
2. **Augment**: $$\text{context} = [d_1; d_2; \ldots; d_k]$$
3. **Generate**: $$a = \text{LLM}(q, \text{context})$$

$$
P(a \mid q) = \sum_{d \in \mathcal{D}} P(d \mid q) \cdot P(a \mid q, d)
$$

### RAG Challenges

| Challenge | Cause | Mitigation |
|-----------|-------|-----------|
| Hallucination | LLM generates beyond context | Cite sources, constrained decoding |
| Lost in the middle | Attention drops mid-context | Rerank passages, put best first/last |
| Retrieval failure | Query-document mismatch | Query rewriting, hybrid retrieval |
| Stale knowledge | Index not updated | Incremental indexing pipeline |

### Evaluation Metrics

| Metric | Formula | Use Case |
|--------|---------|----------|
| Exact Match (EM) | $$\mathbb{1}[\hat{a} = a^*]$$ | Short answers |
| F1 (token overlap) | $$2 \cdot \frac{P \cdot R}{P + R}$$ | Extractive QA |
| ROUGE-L | Longest common subsequence | Generative QA |
| Faithfulness | % claims supported by context | RAG systems |

## Implementation

```python
import numpy as np

def extractive_qa_decode(
    start_logits: np.ndarray,
    end_logits: np.ndarray,
    max_span: int = 30,
) -> tuple[int, int, float]:
    # Decode best answer span from start/end logits.
    start_probs = np.exp(start_logits) / np.exp(start_logits).sum()
    end_probs = np.exp(end_logits) / np.exp(end_logits).sum()
    best_score = -float("inf")
    best_start, best_end = 0, 0
    for s in range(len(start_probs)):
        for e in range(s, min(s + max_span, len(end_probs))):
            score = start_probs[s] * end_probs[e]
            if score > best_score:
                best_score = score
                best_start, best_end = s, e
    return best_start, best_end, float(best_score)

def compute_f1(prediction: str, ground_truth: str) -> float:
    # Compute token-level F1 between prediction and ground truth.
    pred_tokens = prediction.lower().split()
    gt_tokens = ground_truth.lower().split()
    common = set(pred_tokens) & set(gt_tokens)
    if not common:
        return 0.0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)
    return 2 * precision * recall / (precision + recall)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| RAG pipeline | Knowledge-intensive QA | Retrieval grounds generation, reducing hallucination |
| Chunking strategy | Long documents | Overlap chunks to avoid splitting answers |
| Re-ranking retrieved passages | Improve RAG quality | Cross-encoder re-ranker before generation |
| Answer verification | High-stakes QA | Check if answer is entailed by the context |

### Common Interview Questions
- [ ] Design a RAG system for customer support. What are the key components?
- [ ] How do you evaluate whether a RAG system is hallucinating?
- [ ] Compare extractive vs generative QA. When would you use each?
- [ ] How do you choose chunk size and overlap for document indexing?
- [ ] What is the "lost in the middle" problem and how do you mitigate it?

## Comparisons

| Aspect | Extractive QA | Generative QA | RAG |
|--------|--------------|---------------|-----|
| Answer source | Span in context | Generated text | Retrieved context + generation |
| Hallucination risk | None (exact span) | High | Medium (grounded) |
| Answer quality | Limited by context | Fluent, complete | Best of both |
| Knowledge scope | Single passage | Parametric memory | Full corpus |
| Latency | Low (~50ms) | Medium (~200ms) | High (retrieval + generation) |

## Key Takeaways
- RAG is the standard architecture for production QA systems
- Retrieval quality is the bottleneck -- invest in chunking, reranking, and hybrid search
- Hallucination detection requires faithfulness evaluation, not just fluency
- Extractive QA is still preferred when exact quotes are needed (legal, medical)
"""

CONTENT["pillar4.nlp_llm_applications.llm_application_patterns"] = r"""# LLM Application Patterns

## Overview
Building production LLM applications requires more than calling an API. A senior MLE must understand prompt engineering, fine-tuning strategies, agent architectures, guardrails, and cost optimization. These patterns are increasingly the focus of MLE interviews at companies deploying LLMs at scale.

## Core Concepts

### Prompt Engineering Patterns

| Pattern | Description | When to Use |
|---------|------------|-------------|
| Zero-shot | Direct instruction, no examples | Simple, well-defined tasks |
| Few-shot | Examples in the prompt | Complex format or reasoning |
| Chain-of-thought (CoT) | "Think step by step" | Math, logic, multi-step reasoning |
| Self-consistency | Sample multiple CoT, majority vote | Improve reasoning reliability |
| ReAct | Reason + Act interleaved | Tool use and information gathering |

### Fine-Tuning Strategies

**Full fine-tuning**: Update all parameters. Best accuracy but expensive.

**LoRA (Low-Rank Adaptation)**:

$$
W' = W + \Delta W = W + BA
$$

where $$B \in \mathbb{R}^{d \times r}$$, $$A \in \mathbb{R}^{r \times d}$$, $$r \ll d$$. Reduces trainable parameters by 100-1000x.

**QLoRA**: Quantize base model to 4-bit, apply LoRA adapters. Enables fine-tuning 65B models on a single GPU.

| Method | Parameters | Memory | Quality |
|--------|-----------|--------|---------|
| Full fine-tune | 100% | 4x model size | Best |
| LoRA ($$r$$=16) | ~0.1% | 1.2x model size | Near-best |
| QLoRA | ~0.1% | 0.3x model size | Slightly lower |
| Prompt tuning | ~0.001% | 1x model size | Lower |

### Agent Architectures

**ReAct Loop**:
```
Thought: I need to find the current stock price.
Action: search("AAPL stock price")
Observation: AAPL is trading at $178.50
Thought: Now I can answer the question.
Answer: Apple stock is currently at $178.50.
```

**Multi-agent**: Specialized agents collaborating (planner, researcher, coder, critic).

### Guardrails & Safety

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| Input | Classifier + regex | Block prompt injection, PII |
| System prompt | Constitutional rules | Behavioral constraints |
| Output | Classifier + filter | Block toxic/harmful content |
| Structural | JSON schema validation | Ensure parseable output |

### Cost Optimization

$$
\text{Cost} = \text{input\_tokens} \times r_{\text{in}} + \text{output\_tokens} \times r_{\text{out}}
$$

| Technique | Savings | Trade-off |
|-----------|---------|-----------|
| Caching (semantic) | 50-80% | Stale responses |
| Prompt compression | 30-50% | Information loss |
| Model routing (small -> large) | 40-60% | Latency for hard queries |
| Batch processing | 20-40% | Higher latency |

## Implementation

```python
from typing import Any

def exponential_backoff_retry(
    func: Any, max_retries: int = 3, base_delay: float = 1.0,
) -> Any:
    # Retry with exponential backoff for API calls.
    import time
    for attempt in range(max_retries):
        try:
            return func()
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay * 2**attempt)
    return None

def semantic_cache_key(query: str, embeddings: Any) -> str:
    # Generate cache key based on semantic similarity.
    import hashlib
    # In practice, use embedding similarity with a threshold
    normalized = query.lower().strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def structured_output_parse(
    raw: str, schema: dict[str, type],
) -> dict[str, Any]:
    # Parse and validate structured LLM output.
    import json
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from markdown code block
        start = raw.find("{")
        end = raw.rfind("}") + 1
        parsed = json.loads(raw[start:end])
    result = {}
    for key, expected_type in schema.items():
        if key in parsed:
            result[key] = expected_type(parsed[key])
    return result
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| RAG vs fine-tuning | Adding knowledge vs behavior | RAG for facts, fine-tuning for style/format |
| Eval-driven development | Any LLM application | Build evals before building the system |
| Cascading models | Cost optimization | Route easy queries to small models |
| Structured output | Integration with code | JSON mode + schema validation |

### Common Interview Questions
- [ ] When would you fine-tune vs use RAG vs prompt engineering?
- [ ] How do you evaluate an LLM-powered feature in production?
- [ ] Design a guardrail system to prevent prompt injection.
- [ ] How would you reduce LLM API costs by 50% without quality loss?
- [ ] Compare LoRA fine-tuning to full fine-tuning: trade-offs and when to use each.

## Comparisons

| Aspect | Prompt Engineering | RAG | Fine-Tuning |
|--------|-------------------|-----|-------------|
| Setup time | Minutes | Hours-Days | Days-Weeks |
| Knowledge update | Prompt change | Re-index | Re-train |
| Cost per query | Highest (long prompts) | Medium | Lowest |
| Customization | Format only | Knowledge | Behavior + format |
| Hallucination | Highest | Lowest (grounded) | Medium |

## Key Takeaways
- Start with prompting, add RAG for knowledge, fine-tune for behavior
- Evaluation is the hardest and most important part of LLM development
- LoRA makes fine-tuning accessible; QLoRA makes it cheap
- Guardrails are a layered defense -- no single technique is sufficient
- Cost optimization through caching and model routing is essential at scale
"""

# ===== ADS & MONETIZATION =====

CONTENT["pillar4.ads_monetization.ctr_prediction"] = r"""# CTR Prediction

## Overview
Click-through rate (CTR) prediction is the core ML problem in computational advertising, driving billions in revenue at Google, Meta, Amazon, and other ad platforms. The task is to predict $$P(\text{click} \mid \text{user}, \text{ad}, \text{context})$$ accurately at massive scale. A senior MLE must understand feature interactions, calibration, and the unique challenges of ads ML.

## Core Concepts

### Problem Formulation
Binary classification: predict whether a user will click on an ad:

$$
\hat{y} = P(\text{click} \mid \mathbf{x}) = f(\mathbf{x}_{\text{user}}, \mathbf{x}_{\text{ad}}, \mathbf{x}_{\text{context}})
$$

Revenue = bid price x predicted CTR (expected cost per click):

$$
\text{eCPM} = \text{bid} \times \hat{p}_{\text{click}} \times 1000
$$

### Feature Interactions
The key challenge: rich interactions between sparse categorical features.

**Factorization Machines (FM)**:

$$
\hat{y} = w_0 + \sum_i w_i x_i + \sum_{i<j} \langle \mathbf{v}_i, \mathbf{v}_j \rangle x_i x_j
$$

where $$\mathbf{v}_i \in \mathbb{R}^k$$ are latent vectors. Captures pairwise interactions in $$O(nk)$$ instead of $$O(n^2)$$.

**DeepFM**: Combines FM with a deep network:

$$
\hat{y} = \sigma\!\left(\text{FM}(\mathbf{x}) + \text{DNN}(\mathbf{x})\right)
$$

### Calibration
CTR models must be well-calibrated because bids depend on predicted probabilities:

$$
\text{Calibration}: E[\hat{p}] = E[y]
$$

Measured by **Expected Calibration Error (ECE)**:

$$
\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} \left|\text{acc}(B_b) - \text{conf}(B_b)\right|
$$

**Platt scaling**: $$p_{\text{calibrated}} = \sigma(a \cdot \text{logit} + b)$$ where $$a, b$$ are fit on a validation set.

### Feature Hashing (Hashing Trick)

$$
\phi_{\text{hash}}(x) = \text{sign}(h_2(x)) \cdot \mathbf{e}_{h_1(x) \bmod m}
$$

Maps high-cardinality categoricals to a fixed-size vector. Trades collisions for memory efficiency.

### Real-Time Serving Constraints

| Constraint | Typical Target | Implication |
|------------|---------------|-------------|
| Latency | < 10ms p99 | No complex models at full scale |
| QPS | 1M+ | Need model compression/distillation |
| Feature freshness | Minutes | Near real-time feature pipelines |
| Model freshness | Hours-Daily | Online learning or frequent retraining |

## Implementation

```python
import numpy as np

def fm_interaction(
    x: np.ndarray, V: np.ndarray,
) -> float:
    # Compute FM pairwise interaction term in O(nk).
    # V: (n, k), x: (n,)
    vx = V.T @ x  # (k,)
    v2x2 = (V**2).T @ (x**2)  # (k,)
    return 0.5 * float((vx**2 - v2x2).sum())

def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    # Compute ECE for a calibrated probability model.
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (y_prob >= lo) & (y_prob < hi)
        if mask.sum() == 0:
            continue
        avg_pred = y_prob[mask].mean()
        avg_true = y_true[mask].mean()
        ece += mask.sum() / len(y_true) * abs(avg_true - avg_pred)
    return ece

def platt_scaling(
    logits: np.ndarray, y_true: np.ndarray,
) -> tuple[float, float]:
    # Fit Platt scaling parameters (a, b).
    from scipy.optimize import minimize

    def nll(params: np.ndarray) -> float:
        a, b = params
        p = 1.0 / (1.0 + np.exp(-(a * logits + b)))
        p = np.clip(p, 1e-7, 1 - 1e-7)
        return -float((y_true * np.log(p) + (1 - y_true) * np.log(1 - p)).mean())

    result = minimize(nll, [1.0, 0.0], method="Nelder-Mead")
    return float(result.x[0]), float(result.x[1])
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Calibration check | Any CTR model | Poorly calibrated -> wrong bid -> revenue loss |
| Feature crossing | Sparse categoricals | FM/DCN automate what manual feature engineering does |
| Online learning | Non-stationary CTR | User behavior shifts fast; daily retraining is often too slow |
| Negative downsampling | Imbalanced clicks | Sample negatives, then recalibrate: $$p' = p / (p + (1-p)/w)$$ |

### Common Interview Questions
- [ ] Why is calibration critical for CTR models but not for ranking models?
- [ ] Explain Factorization Machines and how they handle sparse feature interactions.
- [ ] How would you handle a new ad with no click history (cold start)?
- [ ] Design a CTR prediction system that serves 1M QPS with < 10ms latency.
- [ ] What happens if your CTR model is poorly calibrated? How do you detect and fix it?

## Comparisons

| Aspect | Logistic Regression | FM | DeepFM | DCN |
|--------|-------------------|----|--------|-----|
| Feature interactions | Manual crosses | Pairwise latent | Auto + deep | Explicit cross layers |
| Scalability | Best | Good | Moderate | Moderate |
| Interpretability | High | Medium | Low | Low |
| Accuracy | Baseline | Better | Best (often) | Best (often) |
| Training speed | Fastest | Fast | Slow | Slow |

## Key Takeaways
- Calibration is more important than accuracy in ads -- revenue depends on correct probabilities
- Feature interactions are the core challenge; FM/DCN automate this
- Negative downsampling + recalibration is standard for handling click imbalance
- Real-time serving constraints drive architecture choices (distillation, feature caching)
"""

# ===== MARKETPLACE & LOGISTICS =====

CONTENT["pillar4.marketplace_logistics.dynamic_pricing"] = r"""# Dynamic Pricing

## Overview
Dynamic pricing adjusts prices in real-time based on supply, demand, and market conditions. It is a core ML application at ride-sharing (Uber/Lyft surge pricing), e-commerce (Amazon), airlines, and hotels. A senior MLE must understand demand estimation, price optimization, and the causal challenges of pricing experiments.

## Core Concepts

### Demand Estimation
Model demand as a function of price:

$$
D(p) = D_0 \cdot e^{-\alpha p + \mathbf{\beta}^T \mathbf{x}}
$$

where $$\alpha$$ is price elasticity, $$D_0$$ is baseline demand, and $$\mathbf{x}$$ are contextual features (time, location, weather).

**Price elasticity of demand**:

$$
\epsilon = \frac{\partial D / D}{\partial p / p} = \frac{p}{D} \cdot \frac{\partial D}{\partial p}
$$

- $$|\epsilon| > 1$$: elastic (price-sensitive users, e.g., leisure travel)
- $$|\epsilon| < 1$$: inelastic (price-insensitive users, e.g., business travel)

### Revenue Optimization
Maximize revenue $$R(p) = p \cdot D(p)$$:

$$
\frac{dR}{dp} = D(p) + p \cdot D'(p) = 0
$$

$$
p^* = -\frac{D(p^*)}{D'(p^*)} = \frac{1}{\alpha} \quad \text{(for log-linear demand)}
$$

### Surge Pricing (Ride-sharing)
Dynamic multiplier based on supply-demand imbalance:

$$
m = \max\!\left(1,\; 1 + \gamma \cdot \frac{D_t - S_t}{S_t}\right)
$$

where $$D_t$$ is demand, $$S_t$$ is supply at time $$t$$. Capped to avoid extreme surges.

### Causal Challenges
Naive regression on $$(p, D)$$ pairs gives biased elasticity because price is endogenous:

$$
\text{Correlation} \neq \text{Causation}: \quad \text{cov}(p, D) > 0 \text{ (prices rise with demand)}
$$

Solutions: **instrumental variables**, **A/B tests with random price assignment**, **regression discontinuity** at price thresholds.

### Fairness Considerations

| Concern | Example | Mitigation |
|---------|---------|-----------|
| Geographic discrimination | Higher prices in low-income areas | Geographic price caps |
| Temporal exploitation | Surge during emergencies | Emergency pricing freezes |
| Algorithmic collusion | Competing algorithms converge to high prices | Regulatory oversight |

## Implementation

```python
import numpy as np

def optimal_price_log_linear(
    alpha: float, beta: np.ndarray, x: np.ndarray, base_demand: float,
) -> tuple[float, float]:
    # Find revenue-maximizing price for log-linear demand.
    p_star = 1.0 / alpha
    d_star = base_demand * np.exp(-alpha * p_star + beta @ x)
    revenue = p_star * d_star
    return p_star, float(revenue)

def surge_multiplier(
    demand: float, supply: float,
    gamma: float = 0.5, max_surge: float = 3.0,
) -> float:
    # Compute surge pricing multiplier.
    if supply <= 0:
        return max_surge
    ratio = (demand - supply) / supply
    multiplier = 1.0 + gamma * max(0, ratio)
    return min(multiplier, max_surge)

def ab_test_price_effect(
    revenue_treat: np.ndarray,
    revenue_control: np.ndarray,
) -> tuple[float, float]:
    # Estimate average treatment effect of price change.
    ate = float(revenue_treat.mean() - revenue_control.mean())
    se = float(np.sqrt(
        revenue_treat.var() / len(revenue_treat)
        + revenue_control.var() / len(revenue_control)
    ))
    return ate, se
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Elasticity estimation | Any pricing decision | Determines whether to raise or lower price |
| A/B testing prices | Measuring price sensitivity | Must randomize price, not just observe |
| Multi-segment pricing | Heterogeneous users | Different users have different price sensitivity |
| Supply-demand balancing | Two-sided marketplaces | Price is a lever to equilibrate supply and demand |

### Common Interview Questions
- [ ] Design a surge pricing system for a ride-sharing platform.
- [ ] How would you estimate price elasticity using observational data?
- [ ] What are the risks of A/B testing prices? How do you mitigate them?
- [ ] How do you balance revenue optimization with user experience/fairness?
- [ ] A competitor undercuts your price. How does your pricing model respond?

## Comparisons

| Aspect | Rule-Based Pricing | Demand Model | Bandit/RL |
|--------|-------------------|-------------|-----------|
| Adaptiveness | Low | Medium | High |
| Data needs | Domain expertise | Historical data | Online interactions |
| Optimality | Suboptimal | Near-optimal (if model correct) | Optimal (converges) |
| Interpretability | High | Medium | Low |
| Cold start | Rules work immediately | Needs data | Needs exploration |

## Key Takeaways
- Price elasticity estimation is the foundation of dynamic pricing
- Naive regression on price-demand is biased -- use causal inference or A/B tests
- Surge pricing balances supply and demand but requires fairness guardrails
- Multi-segment pricing captures heterogeneous price sensitivity
"""

CONTENT["pillar4.marketplace_logistics.eta_prediction"] = r"""# ETA Prediction

## Overview
Estimated Time of Arrival (ETA) prediction is critical for ride-sharing, food delivery, logistics, and navigation services. Accurate ETAs directly impact customer satisfaction, driver dispatch, and pricing. A senior MLE must understand the feature engineering, modeling, and evaluation challenges unique to spatial-temporal prediction.

## Core Concepts

### Problem Formulation
Predict travel time $$T$$ given origin, destination, departure time, and context:

$$
\hat{T} = f(\text{origin}, \text{dest}, t_{\text{depart}}, \mathbf{x}_{\text{context}})
$$

where context includes weather, traffic, road conditions, and historical patterns.

### Feature Engineering

| Feature Category | Examples | Encoding |
|-----------------|---------|----------|
| Spatial | Origin/dest lat-lng, road segments | H3/S2 hexagonal cells, graph embeddings |
| Temporal | Hour, day of week, holidays | Cyclical: $$\sin(2\pi h/24), \cos(2\pi h/24)$$ |
| Route | Distance, num turns, road types | Aggregated from routing graph |
| Real-time | Live traffic speed, incidents | Sliding window averages |
| Historical | Segment speed by time-of-day | Lookup table + smoothing |

### Modeling Approaches

**Segment-based**: Decompose route into segments, predict per-segment time:

$$
\hat{T}_{\text{route}} = \sum_{s \in \text{route}} \hat{T}_s = \sum_s \frac{d_s}{\hat{v}_s}
$$

where $$d_s$$ is segment length and $$\hat{v}_s$$ is predicted speed.

**End-to-end**: Predict total time directly from origin-destination features:

$$
\hat{T} = \text{GBT}(\text{origin\_h3}, \text{dest\_h3}, \text{distance}, \text{hour}, \text{traffic}, \ldots)
$$

**Graph Neural Network**: Encode road network as graph, propagate traffic state:

$$
\mathbf{h}_v^{(l+1)} = \text{UPDATE}\!\left(\mathbf{h}_v^{(l)}, \text{AGGREGATE}(\{\mathbf{h}_u^{(l)} : u \in \mathcal{N}(v)\})\right)
$$

### Loss Functions

$$
\text{MAE} = \frac{1}{n}\sum_i |T_i - \hat{T}_i|
$$

$$
\text{MAPE} = \frac{1}{n}\sum_i \frac{|T_i - \hat{T}_i|}{T_i}
$$

For asymmetric costs (underestimate is worse than overestimate):

$$
\mathcal{L}_{\text{quantile}} = \sum_i \begin{cases} \tau (T_i - \hat{T}_i) & \text{if } T_i \geq \hat{T}_i \\ (1-\tau)(\hat{T}_i - T_i) & \text{otherwise}\end{cases}
$$

## Implementation

```python
import numpy as np

def cyclical_encode(value: float, period: float) -> tuple[float, float]:
    # Encode cyclical feature (e.g., hour -> sin/cos).
    return (
        np.sin(2 * np.pi * value / period),
        np.cos(2 * np.pi * value / period),
    )

def segment_eta(
    segment_distances: np.ndarray,
    segment_speeds: np.ndarray,
) -> float:
    # Compute route ETA from segment distances and predicted speeds.
    mask = segment_speeds > 0
    times = np.zeros_like(segment_distances)
    times[mask] = segment_distances[mask] / segment_speeds[mask]
    times[~mask] = segment_distances[~mask] / 5.0  # fallback: 5 m/s
    return float(times.sum())

def quantile_loss(
    y_true: np.ndarray, y_pred: np.ndarray, tau: float = 0.75,
) -> float:
    # Asymmetric quantile loss (penalize underestimates more).
    residual = y_true - y_pred
    loss = np.where(residual >= 0, tau * residual, (tau - 1) * residual)
    return float(loss.mean())
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Cyclical encoding | Time features | Hours wrap around; sin/cos captures continuity |
| Segment decomposition | Explainable ETAs | Allows per-segment debugging and updates |
| Quantile regression | Under/over-estimate asymmetry | Delivery apps penalize late more than early |
| Live traffic fusion | Real-time updates | Blend historical model with live sensor data |

### Common Interview Questions
- [ ] Design an ETA prediction system for a food delivery service.
- [ ] How do you handle the cold-start problem for new road segments?
- [ ] Why use quantile regression instead of mean prediction for ETA?
- [ ] How would you detect and handle anomalous traffic events (accidents)?
- [ ] Compare segment-based vs end-to-end ETA models. Trade-offs?

## Comparisons

| Aspect | Segment-Based | End-to-End GBT | Graph Neural Network |
|--------|--------------|----------------|---------------------|
| Interpretability | High | Medium | Low |
| Accuracy | Good baseline | Better | Best (with enough data) |
| Real-time updates | Easy (per segment) | Requires refeature | Propagates through graph |
| Training data | Segment labels | OD pair labels | Road graph + labels |
| Cold start (new roads) | Needs segment data | Needs OD history | Can generalize via graph |

## Key Takeaways
- ETA prediction is fundamentally a spatial-temporal problem
- Cyclical encoding for time features is essential
- Quantile regression accounts for asymmetric costs (late vs early)
- Segment-based models are more debuggable; end-to-end models are more accurate
"""

CONTENT["pillar4.marketplace_logistics.causal_inference"] = r"""# Causal Inference for ML

## Overview
Causal inference answers "what would happen if" questions that prediction models cannot. It is essential for pricing experiments, feature launches, and policy evaluation in marketplaces and beyond. A senior MLE must understand the potential outcomes framework, common estimators, and when observational methods can (and cannot) replace A/B tests.

## Core Concepts

### Potential Outcomes Framework
For each unit $$i$$, define potential outcomes $$Y_i(1)$$ (treated) and $$Y_i(0)$$ (control):

$$
\text{ATE} = E[Y_i(1) - Y_i(0)]
$$

**Fundamental problem**: We observe only one potential outcome per unit.

$$
Y_i^{\text{obs}} = T_i \cdot Y_i(1) + (1 - T_i) \cdot Y_i(0)
$$

### Ignorability (Unconfoundedness)
If treatment assignment is independent of potential outcomes given covariates:

$$
(Y(0), Y(1)) \perp T \mid X
$$

then we can estimate causal effects from observational data. A/B testing guarantees this by design.

### Propensity Score Methods

**Propensity score**: $$e(x) = P(T=1 \mid X=x)$$

**Inverse Propensity Weighting (IPW)**:

$$
\hat{\text{ATE}}_{\text{IPW}} = \frac{1}{n}\sum_i \left[\frac{T_i Y_i}{e(X_i)} - \frac{(1-T_i) Y_i}{1 - e(X_i)}\right]
$$

**Doubly robust estimator** (AIPW): combines outcome model and propensity score:

$$
\hat{\tau}_{\text{DR}} = \frac{1}{n}\sum_i \left[\hat{\mu}_1(X_i) - \hat{\mu}_0(X_i) + \frac{T_i(Y_i - \hat{\mu}_1(X_i))}{e(X_i)} - \frac{(1-T_i)(Y_i - \hat{\mu}_0(X_i))}{1-e(X_i)}\right]
$$

Consistent if EITHER the outcome model OR propensity score is correct.

### Difference-in-Differences (DiD)
For before/after comparisons with a control group:

$$
\hat{\tau}_{\text{DiD}} = (E[Y_{\text{treat}}^{\text{after}}] - E[Y_{\text{treat}}^{\text{before}}]) - (E[Y_{\text{ctrl}}^{\text{after}}] - E[Y_{\text{ctrl}}^{\text{before}}])
$$

Assumes **parallel trends**: absent treatment, treated and control would have followed the same trajectory.

### Instrumental Variables (IV)
When there is unmeasured confounding, use an instrument $$Z$$ that affects treatment but not outcome directly:

$$
\hat{\tau}_{\text{IV}} = \frac{\text{Cov}(Y, Z)}{\text{Cov}(T, Z)}
$$

**Two-stage least squares (2SLS)**:
1. Regress $$T$$ on $$Z$$: $$\hat{T} = \gamma Z + \delta X$$
2. Regress $$Y$$ on $$\hat{T}$$: $$Y = \tau \hat{T} + \beta X + \epsilon$$

### Heterogeneous Treatment Effects (CATE)

$$
\tau(x) = E[Y(1) - Y(0) \mid X = x]
$$

Methods: **Causal Forest** (random forest with causal splitting criterion), **meta-learners** (S-learner, T-learner, X-learner).

## Implementation

```python
import numpy as np

def ipw_ate(
    y: np.ndarray, t: np.ndarray, propensity: np.ndarray,
) -> float:
    # Inverse propensity weighted ATE estimator.
    propensity = np.clip(propensity, 0.01, 0.99)  # clip for stability
    treated = (t * y / propensity).mean()
    control = ((1 - t) * y / (1 - propensity)).mean()
    return float(treated - control)

def did_estimator(
    y_treat_before: np.ndarray, y_treat_after: np.ndarray,
    y_ctrl_before: np.ndarray, y_ctrl_after: np.ndarray,
) -> tuple[float, float]:
    # Difference-in-differences estimator with SE.
    treat_diff = y_treat_after.mean() - y_treat_before.mean()
    ctrl_diff = y_ctrl_after.mean() - y_ctrl_before.mean()
    ate = treat_diff - ctrl_diff
    # Bootstrap SE (simplified)
    se = float(np.sqrt(
        y_treat_after.var() / len(y_treat_after)
        + y_treat_before.var() / len(y_treat_before)
        + y_ctrl_after.var() / len(y_ctrl_after)
        + y_ctrl_before.var() / len(y_ctrl_before)
    ))
    return ate, se

def t_learner(
    x: np.ndarray, y: np.ndarray, t: np.ndarray,
) -> np.ndarray:
    # T-learner: separate models for treatment and control.
    from sklearn.ensemble import GradientBoostingRegressor
    model_1 = GradientBoostingRegressor(n_estimators=100)
    model_0 = GradientBoostingRegressor(n_estimators=100)
    model_1.fit(x[t == 1], y[t == 1])
    model_0.fit(x[t == 0], y[t == 0])
    cate = model_1.predict(x) - model_0.predict(x)
    return cate
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| A/B test design | Gold standard for causal questions | Ensures ignorability by design |
| DiD | Policy changes with before/after data | Check parallel trends assumption |
| IPW | Observational data with measured confounders | Clip propensity scores for stability |
| Uplift modeling | Targeting treatment to responsive users | CATE identifies who benefits most |

### Common Interview Questions
- [ ] When can you use observational data instead of A/B tests for causal inference?
- [ ] Explain the doubly robust estimator and why it is preferred over IPW alone.
- [ ] Design an experiment to measure the effect of a new pricing algorithm.
- [ ] What is the parallel trends assumption and how do you verify it?
- [ ] How would you estimate heterogeneous treatment effects for a marketing campaign?

## Comparisons

| Method | Assumptions | Strengths | Weaknesses |
|--------|-----------|-----------|-----------|
| A/B Test (RCT) | Random assignment | Unbiased, gold standard | Expensive, slow, ethical limits |
| IPW | No unmeasured confounders | Flexible, semiparametric | Extreme weights, variance |
| DiD | Parallel trends | Uses observational data | Assumption untestable |
| IV | Valid instrument exists | Handles unmeasured confounding | Hard to find valid instruments |
| Causal Forest | SUTVA, overlap | Heterogeneous effects | Needs large samples |

## Key Takeaways
- A/B testing is the gold standard but not always feasible -- know the alternatives
- Doubly robust estimators are preferred over IPW alone for robustness
- Always check assumptions: parallel trends for DiD, overlap for propensity methods
- Heterogeneous treatment effects (CATE) enable personalized decision-making
"""

# ===== COMPUTER VISION =====

CONTENT["pillar4.computer_vision.classification"] = r"""# Image Classification

## Overview
Image classification assigns a label to an input image and is the foundation of computer vision. Understanding CNN architectures, transfer learning, and modern vision transformers is essential for any MLE working on vision tasks. These concepts appear in both ML fundamentals and system design interviews.

## Core Concepts

### Convolutional Neural Networks

**Convolution operation**:

$$
(f * g)(i, j) = \sum_{m} \sum_{n} f(m, n) \cdot g(i-m, j-n)
$$

**Output dimension**: For input $$H \times W$$, kernel $$k$$, stride $$s$$, padding $$p$$:

$$
H_{\text{out}} = \left\lfloor\frac{H + 2p - k}{s}\right\rfloor + 1
$$

**Parameter count**: For $$C_{\text{in}}$$ input channels, $$C_{\text{out}}$$ output channels, kernel $$k$$:

$$
\text{params} = C_{\text{out}} \times (C_{\text{in}} \times k^2 + 1)
$$

### Key Architectures

| Architecture | Year | Key Innovation | Top-1 (ImageNet) |
|-------------|------|---------------|-------------------|
| AlexNet | 2012 | ReLU, dropout, GPU training | 63.3% |
| VGG-16 | 2014 | Small 3x3 filters, depth | 74.4% |
| ResNet-50 | 2015 | Skip connections | 76.1% |
| EfficientNet-B7 | 2019 | Compound scaling | 84.3% |
| ViT-L/16 | 2020 | Pure transformer on patches | 87.8% |

### Residual Connections (ResNet)

$$
\mathbf{y} = \mathcal{F}(\mathbf{x}, \{W_i\}) + \mathbf{x}
$$

Solves vanishing gradient: gradient flows directly through skip connection. Enables training of 100+ layer networks.

### Vision Transformer (ViT)
Split image into patches, flatten, project to embeddings:

$$
\mathbf{z}_0 = [\mathbf{x}_{\text{class}}; \mathbf{x}_1^p E; \mathbf{x}_2^p E; \ldots; \mathbf{x}_N^p E] + \mathbf{E}_{\text{pos}}
$$

where $$E \in \mathbb{R}^{(P^2 \cdot C) \times D}$$ is the patch projection and $$P$$ is patch size.

Standard transformer encoder processes the sequence. Classification from the [CLS] token.

### Transfer Learning
Fine-tune pre-trained models for downstream tasks:

1. **Feature extraction**: Freeze backbone, train new classifier head
2. **Fine-tuning**: Unfreeze top layers, train with small learning rate
3. **Progressive unfreezing**: Gradually unfreeze layers from top to bottom

$$
\text{lr}_{\text{layer } l} = \text{lr}_{\text{base}} \cdot \gamma^{L - l}
$$

where $$\gamma < 1$$ gives lower learning rates to earlier layers (discriminative LR).

### Data Augmentation
| Technique | Effect | When to Use |
|-----------|--------|-------------|
| Random crop + flip | Spatial invariance | Always |
| Color jitter | Color invariance | Natural images |
| Mixup | $$\tilde{x} = \lambda x_i + (1-\lambda) x_j$$ | Regularization |
| CutMix | Patch-based mixing | Better than Mixup for localization |
| RandAugment | Automated policy search | Large-scale training |

## Implementation

```python
import numpy as np

def conv2d_output_size(
    h: int, w: int, kernel: int, stride: int = 1, padding: int = 0,
) -> tuple[int, int]:
    # Compute output spatial dimensions of a conv layer.
    h_out = (h + 2 * padding - kernel) // stride + 1
    w_out = (w + 2 * padding - kernel) // stride + 1
    return h_out, w_out

def count_conv_params(
    c_in: int, c_out: int, kernel: int, bias: bool = True,
) -> int:
    # Count parameters in a conv layer.
    return c_out * (c_in * kernel * kernel + (1 if bias else 0))

def mixup(
    x1: np.ndarray, y1: np.ndarray,
    x2: np.ndarray, y2: np.ndarray,
    alpha: float = 0.2,
) -> tuple[np.ndarray, np.ndarray]:
    # Mixup data augmentation.
    lam = np.random.beta(alpha, alpha)
    x_mixed = lam * x1 + (1 - lam) * x2
    y_mixed = lam * y1 + (1 - lam) * y2
    return x_mixed, y_mixed
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Transfer learning | Limited labeled data | Pre-trained ImageNet models transfer well to most domains |
| Progressive unfreezing | Fine-tuning stability | Prevents catastrophic forgetting of low-level features |
| ViT vs CNN | Architecture choice | ViT wins with large data; CNNs have better inductive bias for small data |
| Inference optimization | Production deployment | Knowledge distillation, quantization, TensorRT |

### Common Interview Questions
- [ ] Explain how residual connections solve the vanishing gradient problem.
- [ ] Compare CNNs and Vision Transformers. When would you choose each?
- [ ] How does transfer learning work and why is it so effective?
- [ ] Calculate the number of parameters in a ResNet-50.
- [ ] Design an image classification system for a product catalog with 100K categories.

## Comparisons

| Aspect | CNN (ResNet) | ViT | EfficientNet |
|--------|-------------|-----|-------------|
| Inductive bias | Translation equivariance | None (learned) | Compound scaling |
| Data efficiency | Good (small datasets) | Poor (needs large data) | Good |
| Scalability | Diminishing returns past 150 layers | Scales with data and compute | Scales efficiently |
| Speed | Fast inference | Slower (quadratic attention) | Optimized |
| Pre-training | ImageNet | ImageNet-21k, JFT-300M | ImageNet |

## Key Takeaways
- ResNet's skip connections are the most important architectural innovation in CNNs
- Vision Transformers dominate with sufficient data; CNNs remain competitive for small datasets
- Transfer learning is the default approach -- training from scratch is rarely justified
- Data augmentation is as important as model architecture for generalization
"""

CONTENT["pillar4.computer_vision.detection"] = r"""# Object Detection

## Overview
Object detection localizes and classifies objects within images, producing bounding boxes with class labels. It is central to autonomous driving, surveillance, retail analytics, and medical imaging. A senior MLE must understand the two-stage vs one-stage paradigm, anchor-based vs anchor-free designs, and the evaluation metrics unique to detection.

## Core Concepts

### Problem Formulation
For each object $$k$$ in image $$I$$, predict:
- Bounding box: $$(x, y, w, h)$$ or $$(x_1, y_1, x_2, y_2)$$
- Class label: $$c_k \in \{1, \ldots, C\}$$
- Confidence: $$p_k$$

### Intersection over Union (IoU)

$$
\text{IoU}(A, B) = \frac{|A \cap B|}{|A \cup B|} = \frac{|A \cap B|}{|A| + |B| - |A \cap B|}
$$

Used for: matching predictions to ground truth, NMS threshold, evaluation.

### Two-Stage Detectors (Faster R-CNN)
1. **Region Proposal Network (RPN)**: Generate candidate boxes (objectness + box regression)
2. **ROI Pooling/Align**: Extract fixed-size features per proposal
3. **Classification + Refinement**: Classify and refine each proposal

**Anchor boxes**: Pre-defined boxes at multiple scales and aspect ratios. RPN predicts offsets:

$$
t_x = \frac{x - x_a}{w_a}, \quad t_y = \frac{y - y_a}{h_a}, \quad t_w = \log\frac{w}{w_a}, \quad t_h = \log\frac{h}{h_a}
$$

### One-Stage Detectors (YOLO, SSD)
Predict boxes and classes directly from feature maps without a proposal stage:

**YOLOv3**: Divide image into $$S \times S$$ grid. Each cell predicts $$B$$ boxes:

$$
\text{Loss} = \lambda_{\text{coord}} \mathcal{L}_{\text{box}} + \mathcal{L}_{\text{obj}} + \mathcal{L}_{\text{cls}}
$$

### Anchor-Free Detectors (FCOS, CenterNet)
Predict objects as center points + distances to box edges:

$$
(l, t, r, b) = \text{distances from center to left, top, right, bottom edges}
$$

Eliminates anchor hyperparameters. Simpler, often competitive.

### Feature Pyramid Network (FPN)
Multi-scale feature fusion for detecting objects at different sizes:

$$
P_l = \text{Conv}_{1 \times 1}(C_l) + \text{Upsample}(P_{l+1})
$$

where $$C_l$$ are backbone features at level $$l$$ and $$P_l$$ are pyramid features.

### Non-Maximum Suppression (NMS)
Remove duplicate detections:
1. Sort by confidence
2. Keep highest-confidence box
3. Remove all boxes with $$\text{IoU} > \theta$$ with the kept box
4. Repeat

Soft-NMS decays scores instead of hard removal: $$s_i \leftarrow s_i \cdot e^{-\text{IoU}^2 / \sigma}$$.

### Evaluation: Mean Average Precision (mAP)

$$
\text{AP}_c = \int_0^1 P(R)\, dR
$$

$$
\text{mAP} = \frac{1}{C} \sum_{c=1}^{C} \text{AP}_c
$$

COCO uses mAP averaged over IoU thresholds [0.5:0.05:0.95].

## Implementation

```python
import numpy as np

def compute_iou(box1: np.ndarray, box2: np.ndarray) -> float:
    # Compute IoU between two boxes [x1, y1, x2, y2].
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0

def nms(
    boxes: np.ndarray, scores: np.ndarray, threshold: float = 0.5,
) -> list[int]:
    # Non-Maximum Suppression. Returns indices of kept boxes.
    order = scores.argsort()[::-1]
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(int(i))
        if len(order) == 1:
            break
        ious = np.array([
            compute_iou(boxes[i], boxes[j]) for j in order[1:]
        ])
        remaining = np.where(ious <= threshold)[0]
        order = order[remaining + 1]
    return keep

def anchor_offsets(
    gt_box: np.ndarray, anchor: np.ndarray,
) -> np.ndarray:
    # Compute regression targets from anchor to ground truth.
    xa, ya = anchor[0], anchor[1]
    wa = anchor[2] - anchor[0]
    ha = anchor[3] - anchor[1]
    xg, yg = gt_box[0], gt_box[1]
    wg = gt_box[2] - gt_box[0]
    hg = gt_box[3] - gt_box[1]
    return np.array([
        (xg - xa) / wa, (yg - ya) / ha,
        np.log(wg / wa), np.log(hg / ha),
    ])
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Two-stage for accuracy | High-accuracy requirements | RPN + refinement gives best precision |
| One-stage for speed | Real-time detection | YOLO trades some accuracy for speed |
| FPN for multi-scale | Objects at varying sizes | Essential for detecting small objects |
| NMS alternatives | Crowded scenes | Soft-NMS or learned NMS for overlapping objects |

### Common Interview Questions
- [ ] Explain the difference between one-stage and two-stage detectors.
- [ ] What is the role of anchor boxes and how do you choose their sizes?
- [ ] Walk through the NMS algorithm. What are its limitations?
- [ ] How does FPN improve detection of small objects?
- [ ] Design an object detection system for autonomous driving. What metrics matter?

## Comparisons

| Aspect | Faster R-CNN | YOLOv8 | DETR | FCOS |
|--------|-------------|--------|------|------|
| Architecture | Two-stage | One-stage | Transformer | Anchor-free |
| Speed | Moderate | Fast | Slow | Fast |
| Accuracy (COCO mAP) | ~42 | ~44 | ~43 | ~41 |
| NMS needed | Yes | Yes | No (set prediction) | Yes |
| Complexity | High | Medium | Medium | Low |

## Key Takeaways
- IoU is the fundamental metric connecting detection predictions to ground truth
- FPN is essential for multi-scale detection and is used in nearly all modern detectors
- The trend is toward anchor-free, NMS-free architectures (DETR, FCOS)
- mAP@[.5:.95] is the standard evaluation metric (COCO benchmark)
"""

# ===== TRUST & SAFETY / FRAUD DETECTION =====

CONTENT["pillar4.trust_safety.anomaly_detection"] = r"""# Anomaly Detection for Fraud

## Overview
Anomaly detection identifies unusual patterns that deviate from expected behavior. In fraud detection, the cost of missed fraud (false negatives) is orders of magnitude higher than false alarms. A senior MLE must understand statistical, ML-based, and graph-based anomaly detection methods, along with the unique challenges of adversarial, evolving fraud patterns.

## Core Concepts

### Statistical Methods

**Z-score**: Flag points beyond $$k$$ standard deviations:

$$
z_i = \frac{x_i - \mu}{\sigma}, \quad \text{anomaly if } |z_i| > k
$$

**Isolation Forest**: Anomalies are easier to isolate. Average path length in random trees:

$$
s(x, n) = 2^{-E[h(x)] / c(n)}
$$

where $$h(x)$$ is path length and $$c(n)$$ is the average path length in a random BST. Score $$\approx 1$$ for anomalies.

### ML-Based Methods

**Autoencoder anomaly detection**: Train on normal data, flag high reconstruction error:

$$
\text{score}(x) = \|x - \hat{x}\|^2 = \|x - \text{Dec}(\text{Enc}(x))\|^2
$$

Anomaly threshold: $$\text{score}(x) > \mu_{\text{train}} + k \cdot \sigma_{\text{train}}$$

**One-Class SVM**: Learn a decision boundary around normal data:

$$
\min_{w, \xi, \rho} \frac{1}{2}\|w\|^2 + \frac{1}{\nu n}\sum_i \xi_i - \rho
$$

subject to $$w^T \phi(x_i) \geq \rho - \xi_i$$.

### Graph-Based Methods
Model entities as a graph (users, devices, accounts) and detect anomalous structures:

| Pattern | Detection | Example |
|---------|----------|---------|
| Star pattern | Node with unusually high degree | One device linked to many accounts |
| Dense subgraph | Subgraph with anomalous density | Fraud ring of accounts |
| Temporal burst | Sudden activity spike | Bot attack |
| Feature propagation | GNN label spreading | Risk score diffusion through network |

### Handling Extreme Imbalance
Fraud rates are typically 0.01-0.1%:

| Technique | When to Use | Notes |
|-----------|------------|-------|
| Undersampling majority | Small training data | Lose information |
| SMOTE | Moderate imbalance | Synthetic minority examples |
| Cost-sensitive learning | Any | Weight: $$w_{\text{fraud}} = \text{cost\_ratio}$$ |
| Anomaly-first, classify-second | Very rare fraud | Two-stage: detect anomaly, then classify type |

### Adversarial Robustness
Fraudsters actively adapt:

$$
\text{Arms race}: \quad \text{model}_{t+1} = f(\text{fraud patterns}_{t}) \quad \text{but} \quad \text{fraud}_{t+1} = g(\text{model}_{t})
$$

Mitigations: model ensemble diversity, feature engineering on hard-to-spoof signals (device fingerprint, behavioral biometrics, graph structure).

## Implementation

```python
import numpy as np

def isolation_forest_score(
    path_lengths: np.ndarray, n_samples: int,
) -> np.ndarray:
    # Compute anomaly scores from average path lengths.
    # c(n) = 2 * (ln(n-1) + 0.5772) - 2*(n-1)/n
    euler = 0.5772156649
    c_n = 2 * (np.log(max(n_samples - 1, 1)) + euler) - 2 * (n_samples - 1) / n_samples
    return 2 ** (-path_lengths / c_n)

def autoencoder_threshold(
    reconstruction_errors: np.ndarray,
    k: float = 3.0,
) -> float:
    # Set anomaly threshold at k standard deviations above mean.
    return float(reconstruction_errors.mean() + k * reconstruction_errors.std())

def precision_recall_at_k(
    y_true: np.ndarray, scores: np.ndarray, k: int,
) -> tuple[float, float]:
    # Precision and recall at top-k anomaly scores.
    top_k_idx = np.argsort(-scores)[:k]
    tp = y_true[top_k_idx].sum()
    precision = tp / k
    recall = tp / max(y_true.sum(), 1)
    return float(precision), float(recall)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Two-stage detection | Very rare events | Anomaly detection -> fraud classification |
| Feature velocity | Temporal fraud patterns | Rate of change matters more than absolute values |
| Graph features | Account-level fraud | Fraud rings visible in graph structure |
| Model staleness | Adversarial fraud | Retrain frequently; monitor feature drift |

### Common Interview Questions
- [ ] Design a fraud detection system for a payment platform. What features would you use?
- [ ] How do you handle 0.01% fraud rate in training?
- [ ] Compare Isolation Forest, Autoencoder, and One-Class SVM for anomaly detection.
- [ ] How do you detect fraud rings using graph-based methods?
- [ ] Your fraud model performance is degrading monthly. What is happening and how do you fix it?

## Comparisons

| Method | Supervision | Strengths | Weaknesses |
|--------|-----------|-----------|-----------|
| Z-score / rules | None | Fast, interpretable | Only univariate, misses complex patterns |
| Isolation Forest | None | Handles high dimensions | Less accurate on subspace anomalies |
| Autoencoder | Semi (normal only) | Learns complex normal patterns | Threshold sensitivity |
| One-Class SVM | Semi (normal only) | Strong theoretical guarantees | Scalability |
| Supervised (XGBoost) | Full | Best accuracy | Needs labeled fraud examples |
| GNN | Graph structure | Detects relational fraud | Needs graph data |

## Key Takeaways
- Fraud detection is an adversarial problem -- models degrade as fraudsters adapt
- Graph-based features capture fraud patterns invisible to tabular models
- Cost-sensitive learning is essential given extreme class imbalance
- Two-stage (anomaly detection + classification) works well for very rare fraud
"""

CONTENT["pillar4.trust_safety.explainability"] = r"""# Explainability: SHAP & LIME

## Overview
Model explainability is critical for trust & safety, compliance, and debugging. Regulators require explanations for automated decisions (GDPR, ECOA). A senior MLE must understand local vs global explanations, SHAP values (the gold standard), LIME, and when simpler methods suffice.

## Core Concepts

### SHAP (SHapley Additive exPlanations)
Based on Shapley values from cooperative game theory. The contribution of feature $$i$$ to prediction $$f(x)$$:

$$
\phi_i = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!\,(|N|-|S|-1)!}{|N|!} \left[f(S \cup \{i\}) - f(S)\right]
$$

where $$N$$ is the set of all features and $$f(S)$$ is the model output using only features in $$S$$ (marginalizing over the rest).

**Properties (uniqueness)**:
- **Efficiency**: $$\sum_i \phi_i = f(x) - E[f(x)]$$ (contributions sum to prediction)
- **Symmetry**: Equal features get equal attribution
- **Linearity**: $$\phi_i(f + g) = \phi_i(f) + \phi_i(g)$$
- **Dummy**: Unused features get zero attribution

### TreeSHAP
Exact SHAP values for tree-based models in $$O(TLD^2)$$:

$$
\phi_i = \sum_{\text{paths containing } i} \text{contribution weighted by tree structure}
$$

Much faster than exact Shapley computation ($$O(2^n)$$).

### LIME (Local Interpretable Model-agnostic Explanations)
Approximate model locally with an interpretable model:

$$
\xi(x) = \arg\min_{g \in G} \mathcal{L}(f, g, \pi_x) + \Omega(g)
$$

where:
- $$\pi_x$$: proximity kernel around $$x$$
- $$\mathcal{L}$$: fidelity loss (how well $$g$$ approximates $$f$$ near $$x$$)
- $$\Omega(g)$$: complexity penalty (e.g., number of non-zero coefficients)

**Process**:
1. Perturb input $$x$$ to generate neighborhood samples
2. Get model predictions on perturbations
3. Fit weighted linear model (or decision tree)
4. Report coefficients as feature importances

### Global vs Local Explanations

| Type | Method | Output |
|------|--------|--------|
| Local | SHAP values, LIME | Why this prediction? |
| Global | SHAP summary plot, feature importance | What drives the model overall? |
| Example-based | Prototypes, counterfactuals | What similar/different inputs look like |

### Permutation Feature Importance (Global)

$$
\text{Importance}(i) = \text{metric}(\mathbf{y}, f(\mathbf{X})) - \text{metric}(\mathbf{y}, f(\mathbf{X}_{\text{shuffle } i}))
$$

Shuffle feature $$i$$ column, measure performance drop. Model-agnostic but can be misleading with correlated features.

### Counterfactual Explanations
Find the smallest change to input that flips the prediction:

$$
x^* = \arg\min_{x'} d(x, x') \quad \text{s.t. } f(x') \neq f(x)
$$

"Your loan was denied. If your income were $5K higher, it would be approved."

## Implementation

```python
import numpy as np

def permutation_importance(
    model_predict: object,
    X: np.ndarray,
    y: np.ndarray,
    metric_fn: object,
    n_repeats: int = 10,
) -> np.ndarray:
    # Compute permutation feature importance.
    baseline = metric_fn(y, model_predict(X))
    importances = np.zeros((X.shape[1], n_repeats))
    for j in range(X.shape[1]):
        for r in range(n_repeats):
            X_perm = X.copy()
            X_perm[:, j] = np.random.permutation(X_perm[:, j])
            importances[j, r] = baseline - metric_fn(y, model_predict(X_perm))
    return importances.mean(axis=1)

def lime_explain(
    predict_fn: object,
    x: np.ndarray,
    n_samples: int = 1000,
    kernel_width: float = 0.75,
) -> np.ndarray:
    # Simplified LIME explanation for tabular data.
    n_features = len(x)
    # Generate perturbations
    perturbations = np.random.binomial(1, 0.5, (n_samples, n_features))
    samples = np.where(perturbations, x, np.zeros_like(x))
    # Get predictions
    preds = predict_fn(samples)
    # Compute kernel weights
    distances = np.sqrt(((perturbations - 1) ** 2).sum(axis=1))
    weights = np.exp(-distances**2 / kernel_width**2)
    # Fit weighted linear regression
    W = np.diag(weights)
    coefs = np.linalg.lstsq(
        perturbations.T @ W @ perturbations,
        perturbations.T @ W @ preds,
        rcond=None,
    )[0]
    return coefs
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| SHAP for compliance | Regulated domains (finance, health) | Uniquely satisfies axioms; defensible |
| LIME for quick debugging | Model-agnostic, fast iteration | Good for initial exploration |
| Feature importance for monitoring | Production model health | Detect feature drift via importance shifts |
| Counterfactuals for users | Customer-facing explanations | Actionable: "change X to get Y" |

### Common Interview Questions
- [ ] Explain SHAP values and their theoretical guarantees.
- [ ] Compare SHAP and LIME. When would you prefer each?
- [ ] How do you explain a black-box model's decision to a non-technical stakeholder?
- [ ] What is the difference between feature importance and SHAP values?
- [ ] Design an explanation system for a loan approval model. What regulatory requirements apply?

## Comparisons

| Aspect | SHAP | LIME | Permutation Importance |
|--------|------|------|----------------------|
| Scope | Local (aggregatable to global) | Local only | Global only |
| Theory | Game theory (Shapley) | Local fidelity | Empirical |
| Consistency | Guaranteed (axioms) | Not guaranteed | Misleading with correlations |
| Speed | Slow (exact), fast (TreeSHAP) | Fast | Moderate |
| Model-agnostic | KernelSHAP: yes; TreeSHAP: trees only | Yes | Yes |
| Additivity | $$\sum \phi_i = f(x) - E[f]$$ | No guarantee | N/A |

## Key Takeaways
- SHAP is the gold standard for local explanations due to its theoretical guarantees
- TreeSHAP makes SHAP practical for tree-based models in production
- LIME is useful for quick, model-agnostic debugging but lacks consistency guarantees
- Counterfactual explanations are most actionable for end users
- Regulatory compliance often requires explainability -- design for it from the start
"""


# ---------------------------------------------------------------------------
# Main: Write content to database
# ---------------------------------------------------------------------------

def main() -> None:
    """Populate framework_nodes with Pillar 4 content."""
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
