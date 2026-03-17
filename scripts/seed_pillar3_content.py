"""Seed Pillar 3 (ML System Design) framework node descriptions.

Usage:
    python scripts/seed_pillar3_content.py

Populates the `description` field for all 19 Pillar 3 leaf nodes
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

# ===== CLASSIC DESIGN PROBLEMS =====

CONTENT["pillar3.design_problems.search_retrieval"] = r"""# Search & Retrieval Systems

## Overview
Search and retrieval systems power query understanding, document ranking, and result serving at scale. A senior MLE must design end-to-end pipelines covering query processing, multi-stage retrieval, relevance ranking, and real-time indexing. This topic appears frequently in interviews at Google, Meta, LinkedIn, and Amazon.

## Core Concepts

### Query Understanding Pipeline
Query processing transforms raw user input into structured intent:

| Stage | Technique | Example |
|-------|-----------|---------|
| Tokenization | WordPiece / BPE | "machine learning" -> ["machine", "learning"] |
| Spell correction | Edit distance + LM | "machin lerning" -> "machine learning" |
| Query expansion | Synonym injection, PRF | "ML" -> "ML OR machine learning" |
| Intent classification | BERT classifier | "buy iPhone 15" -> commercial intent |
| Entity recognition | NER model | "restaurants near Seattle" -> LOC: Seattle |

### Multi-Stage Retrieval Architecture

$$
\text{Candidates} \xrightarrow{\text{L0: Boolean}} \xrightarrow{\text{L1: ANN}} \xrightarrow{\text{L2: Cross-Encoder}} \text{Top-K Results}
$$

- **L0 -- Inverted Index**: BM25 retrieval over inverted index. $O(\text{postings})$ per query term.
- **L1 -- Dense Retrieval**: Bi-encoder produces query/doc embeddings, ANN search (HNSW/ScaNN) returns top-1000. Latency budget: 10-50ms.
- **L2 -- Re-ranking**: Cross-encoder (BERT-based) scores query-doc pairs. Latency: 5-20ms for top-100.

### BM25 Scoring

$$
\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot (1 - b + b \cdot \frac{|d|}{\text{avgdl}})}
$$

where $f(t,d)$ is term frequency, $k_1 \approx 1.2$, $b \approx 0.75$.

### Relevance Metrics

$$
\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{2^{r_i} - 1}{\log_2(i + 1)}
$$

## Implementation

```python
import numpy as np

def bm25_score(
    tf: float, df: int, doc_len: int,
    avg_dl: float, n_docs: int,
    k1: float = 1.2, b: float = 0.75,
) -> float:
    # Compute BM25 score for a single term-document pair.
    idf = np.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
    tf_norm = (tf * (k1 + 1)) / (
        tf + k1 * (1 - b + b * doc_len / avg_dl)
    )
    return float(idf * tf_norm)

def two_stage_retrieve(
    query_emb: np.ndarray,
    index,  # ANN index
    cross_encoder,
    query_text: str,
    doc_texts: list[str],
    top_k_ann: int = 100,
    top_k_final: int = 10,
) -> list[int]:
    # L1 ANN retrieval + L2 cross-encoder re-ranking.
    # L1: ANN search
    ids, _ = index.search(query_emb.reshape(1, -1), top_k_ann)
    candidates = ids[0].tolist()
    # L2: cross-encoder re-rank
    pairs = [(query_text, doc_texts[i]) for i in candidates]
    scores = cross_encoder.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [idx for idx, _ in ranked[:top_k_final]]
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Multi-stage funnel | Any search system | Each stage trades recall for precision at higher compute cost |
| Hybrid sparse+dense | Web/product search | BM25 handles exact match; dense handles semantic similarity |
| Query rewriting | Ambiguous queries | LLM-based rewrite improves recall without index changes |
| Real-time indexing | Fresh content (news, social) | Dual index: batch (daily) + real-time (streaming) |
| Learning to rank | Complex relevance | Pointwise (regression), pairwise (RankNet), listwise (LambdaMART) |

### Common Interview Questions
- [ ] Design a web search engine ranking pipeline
- [ ] How would you handle query autocomplete at scale?
- [ ] Compare BM25 vs dense retrieval -- when does each win?
- [ ] How do you evaluate search quality offline vs online?
- [ ] Design real-time indexing for a social media feed

## Comparisons

| Aspect | Sparse (BM25) | Dense (Bi-Encoder) | Cross-Encoder |
|--------|--------------|-------------------|---------------|
| Latency | ~5ms | ~10-50ms (ANN) | ~100ms (top-100) |
| Exact match | Excellent | Poor | Good |
| Semantic match | Poor | Good | Excellent |
| Index size | Inverted index | Vector index | N/A (no index) |
| Training data | None | Pairs/triplets | Pairs with labels |

## Key Takeaways
- [ ] Multi-stage retrieval balances latency and quality
- [ ] BM25 remains a strong baseline -- always include sparse signals
- [ ] Dense retrieval enables semantic matching but needs ANN infrastructure
- [ ] Online metrics (click-through, dwell time) matter more than offline NDCG
- [ ] Query understanding is often the highest-ROI investment
"""

CONTENT["pillar3.design_problems.recommendation"] = r"""# Recommendation Systems

## Overview
Recommendation systems are the most common ML system design question. They power feeds, product suggestions, content discovery, and matchmaking. A senior MLE must design end-to-end pipelines covering candidate generation, ranking, re-ranking, and serving infrastructure with real-time personalization.

## Core Concepts

### System Architecture

```
User Request
    |
    v
[Candidate Generation] -- 1000s of items, <50ms
    |
    v
[Ranking Model] -- score top-1000, <100ms
    |
    v
[Re-ranking / Business Rules] -- diversity, freshness, ads mixing
    |
    v
[Served Results] -- top 10-50 items
```

### Candidate Generation Strategies

| Strategy | Method | Pros | Cons |
|----------|--------|------|------|
| Collaborative filtering | User-item matrix factorization | Captures taste | Cold start |
| Content-based | Item feature similarity | No cold start for items | Filter bubble |
| Two-tower | Separate user/item encoders | Scalable ANN serving | Less expressive |
| Graph-based | GNN on interaction graph | Rich signals | Complex infrastructure |

### Matrix Factorization

$$
\hat{r}_{ui} = \mu + b_u + b_i + \mathbf{p}_u^T \mathbf{q}_i
$$

Loss with regularization:

$$
\mathcal{L} = \sum_{(u,i) \in \mathcal{K}} (r_{ui} - \hat{r}_{ui})^2 + \lambda(\|\mathbf{p}_u\|^2 + \|\mathbf{q}_i\|^2 + b_u^2 + b_i^2)
$$

### Deep Ranking Models
Modern ranking uses feature-rich models combining:
- **User features**: demographics, history, context (time, device)
- **Item features**: content, popularity, recency, embeddings
- **Cross features**: user-item interaction history, co-occurrence

Architecture choices: Wide & Deep, DCN-v2, DIN (attention over history), DLRM.

### Ranking Loss Functions

Pointwise:
$$
\mathcal{L} = -\sum [y_i \log \hat{y}_i + (1 - y_i) \log(1 - \hat{y}_i)]
$$

Pairwise (BPR):
$$
\mathcal{L} = -\sum_{(u,i,j)} \log \sigma(\hat{r}_{ui} - \hat{r}_{uj})
$$

## Implementation

```python
import numpy as np

class TwoTowerModel:
    # Simplified two-tower candidate generation.

    def __init__(self, user_dim: int, item_dim: int, emb_dim: int) -> None:
        self.user_proj = np.random.randn(user_dim, emb_dim) * 0.01
        self.item_proj = np.random.randn(item_dim, emb_dim) * 0.01

    def user_embedding(self, user_feat: np.ndarray) -> np.ndarray:
        # Project user features to embedding space.
        emb = user_feat @ self.user_proj
        return emb / (np.linalg.norm(emb) + 1e-8)

    def item_embedding(self, item_feat: np.ndarray) -> np.ndarray:
        # Project item features to embedding space.
        emb = item_feat @ self.item_proj
        return emb / (np.linalg.norm(emb) + 1e-8)

    def score(
        self, user_feat: np.ndarray, item_feat: np.ndarray,
    ) -> float:
        # Cosine similarity between user and item.
        u_emb = self.user_embedding(user_feat)
        i_emb = self.item_embedding(item_feat)
        return float(u_emb @ i_emb)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Multi-stage funnel | Any rec system | Candidate gen (recall) -> Ranking (precision) -> Re-rank (business) |
| Two-tower + ANN | Large item catalog | Pre-compute item embeddings, serve via HNSW |
| Feature store | Real-time features | Separate offline (batch) and online (streaming) feature pipelines |
| Explore-exploit | Cold start / novelty | Thompson sampling or epsilon-greedy in re-ranking |
| Session-based | Short sessions, no login | GRU/Transformer over session clicks |

### Common Interview Questions
- [ ] Design a news feed ranking system (Meta)
- [ ] Design product recommendations for e-commerce (Amazon)
- [ ] How do you handle cold-start users and items?
- [ ] How do you balance relevance, diversity, and freshness?
- [ ] Design a notification system that decides what/when to push

## Comparisons

| Aspect | Collaborative Filtering | Two-Tower | Cross-Encoder Ranker |
|--------|------------------------|-----------|---------------------|
| Serving latency | Pre-computed | ANN lookup ~10ms | Per-pair scoring ~50ms |
| Feature richness | User-item only | Moderate | Rich cross-features |
| Cold start | Poor | Better (content features) | Best |
| Scale | Millions | Billions (ANN) | Top-K only |

## Key Takeaways
- [ ] Always design as a multi-stage funnel with explicit latency budgets
- [ ] Two-tower models dominate candidate generation at scale
- [ ] Feature engineering (especially real-time features) often matters more than model architecture
- [ ] Offline metrics (AUC, NDCG) must be validated with online A/B tests
- [ ] Diversity and exploration are critical for long-term engagement
"""

CONTENT["pillar3.design_problems.ads"] = r"""# Ads & Click Prediction

## Overview
Ads systems are among the most revenue-critical ML systems. They combine click-through rate (CTR) prediction, bid optimization, auction mechanisms, and budget pacing. This topic is a staple at Meta, Google, Amazon, and any company with an ads business. Understanding the economics and ML jointly is essential.

## Core Concepts

### Ads Serving Pipeline

```
Ad Request -> Candidate Selection -> CTR Prediction -> Bid Calculation
    -> Auction -> Ad Serving -> Click/Conversion Tracking -> Model Update
```

### Click-Through Rate Prediction
CTR models predict $P(\text{click} | \text{user, ad, context})$:

$$
\text{eCPM} = \text{CTR} \times \text{bid} \times 1000
$$

The ad with highest eCPM wins the auction (simplified).

### Feature Categories

| Category | Examples | Update Frequency |
|----------|----------|-----------------|
| User | Demographics, interests, history | Hourly-daily |
| Ad | Creative, landing page, category | On change |
| Context | Time, device, page content | Real-time |
| Cross | User-ad affinity, historical CTR | Real-time |

### Model Architecture Evolution

| Generation | Model | Key Innovation |
|-----------|-------|---------------|
| 1st | Logistic Regression | Sparse features, interpretable |
| 2nd | GBDT + LR | Non-linear feature crossing |
| 3rd | Wide & Deep | Memorization + generalization |
| 4th | DCN-v2 / DLRM | Explicit cross-network, embedding tables |
| 5th | DIN / DIEN | Attention over user behavior sequence |

### Auction Mechanisms

**Second-price auction** (classical):
$$
\text{payment} = \frac{\text{eCPM}_{\text{2nd}}}{\text{CTR}_{\text{winner}}}
$$

**VCG auction**: Truthful bidding is a dominant strategy. Winner pays the externality they impose on others.

### Calibration
CTR models must be well-calibrated for correct bid pricing:

$$
\text{Calibration} = \frac{\text{Predicted avg CTR}}{\text{Observed avg CTR}}
$$

A model with good AUC but poor calibration will over/under-price ads.

## Implementation

```python
import numpy as np

def compute_ecpm(
    ctr: np.ndarray, bid: np.ndarray,
) -> np.ndarray:
    # Compute effective CPM for ranking ads.
    return ctr * bid * 1000.0

def second_price_payment(
    winner_ctr: float,
    second_ecpm: float,
) -> float:
    # Compute cost-per-click in second-price auction.
    if winner_ctr <= 0:
        return 0.0
    return second_ecpm / (winner_ctr * 1000.0)

def budget_pacing(
    remaining_budget: float,
    remaining_time_frac: float,
    spent_so_far: float,
    total_budget: float,
) -> float:
    # Pacing multiplier to smooth budget spend over time.
    ideal_spend = total_budget * (1.0 - remaining_time_frac)
    if ideal_spend <= 0:
        return 1.0
    return max(0.1, min(2.0, remaining_budget / ideal_spend))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Multi-objective | CTR + CVR + quality | Combine P(click) x P(convert|click) x bid x quality score |
| Delayed feedback | Conversion attribution | Conversions arrive hours/days later; need importance weighting |
| Position bias | Ads in ranked lists | Higher positions get more clicks regardless of relevance |
| Explore-exploit | New ads/creatives | Thompson sampling for cold-start ads |
| Budget pacing | Campaign optimization | Smooth spend over time to avoid early exhaustion |

### Common Interview Questions
- [ ] Design a CTR prediction system for a social media ads platform
- [ ] How do you handle delayed conversions in model training?
- [ ] Explain position bias and how to debias your CTR model
- [ ] How would you design budget pacing for ad campaigns?
- [ ] Compare first-price vs second-price auctions for online ads

## Comparisons

| Aspect | Logistic Regression | Deep CTR (DCN-v2) | Sequence Model (DIN) |
|--------|-------------------|-------------------|---------------------|
| Training speed | Fast | Moderate | Slow |
| Feature interaction | Manual crosses | Automatic | Attention-based |
| Serving latency | <1ms | ~5ms | ~10ms |
| Cold start | Good (sparse features) | Moderate | Poor (needs history) |
| Interpretability | High | Low | Low |

## Key Takeaways
- [ ] eCPM = CTR x Bid is the fundamental ranking formula
- [ ] Calibration matters as much as discrimination (AUC)
- [ ] Position bias correction is critical for unbiased training
- [ ] Real-time features (recent clicks, session context) drive most gains
- [ ] Budget pacing and auction design are as important as the ML model
"""

CONTENT["pillar3.design_problems.marketplace"] = r"""# Marketplace & Logistics

## Overview
Marketplace ML systems handle matching supply with demand, dynamic pricing, ETA prediction, and logistics optimization. Common at Uber, DoorDash, Airbnb, and similar two-sided platforms. These systems require balancing multiple stakeholders (buyers, sellers, platform) under real-time constraints.

## Core Concepts

### Two-Sided Marketplace Architecture

```
[Demand Side]          [Platform ML]           [Supply Side]
  Buyer/Rider  <-->  Matching & Pricing  <-->  Seller/Driver
  Search/Browse       ETA Prediction           Inventory/Availability
  Personalization     Fraud Detection          Quality Scoring
```

### Dynamic Pricing (Surge)
Surge pricing balances supply and demand in real-time:

$$
\text{surge\_multiplier} = f\left(\frac{\text{demand\_rate}}{\text{supply\_rate}}\right)
$$

A common model uses log-linear pricing:
$$
\log(\text{price}) = \beta_0 + \beta_1 \log\left(\frac{D}{S}\right) + \beta_2 \cdot \text{features}
$$

### ETA Prediction
Estimated Time of Arrival combines:

$$
\text{ETA} = \text{routing\_time} + \text{pickup\_time} + \text{preparation\_time}
$$

Each component is a separate ML model:
- **Routing**: Graph-based shortest path + traffic ML model
- **Preparation**: Historical order completion times by restaurant/store
- **Pickup**: Driver-to-merchant travel + wait time

### Matching / Dispatch Optimization
Assign orders to drivers by solving:

$$
\min \sum_{i,j} c_{ij} x_{ij} \quad \text{s.t.} \quad \sum_j x_{ij} = 1 \; \forall i, \quad x_{ij} \in \{0,1\}
$$

where $c_{ij}$ is the cost of assigning order $i$ to driver $j$ (distance, ETA, fairness).

### Key Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Conversion rate | Orders / sessions | Maximize |
| ETA accuracy | MAE of predicted vs actual | Minimize |
| Supply utilization | Active time / online time | Balance |
| Defect rate | Cancellations + returns | Minimize |
| Take rate | Platform revenue / GMV | Business target |

## Implementation

```python
import numpy as np

def surge_multiplier(
    demand_rate: float,
    supply_rate: float,
    min_surge: float = 1.0,
    max_surge: float = 3.0,
) -> float:
    # Compute surge pricing multiplier.
    if supply_rate <= 0:
        return max_surge
    ratio = demand_rate / supply_rate
    surge = min_surge + (max_surge - min_surge) * max(0, ratio - 1)
    return min(max_surge, max(min_surge, surge))

def greedy_dispatch(
    order_locs: np.ndarray,   # (n_orders, 2)
    driver_locs: np.ndarray,  # (n_drivers, 2)
) -> list[tuple[int, int]]:
    # Greedy nearest-driver dispatch assignment.
    assignments = []
    available = set(range(len(driver_locs)))
    for oi in range(len(order_locs)):
        best_d, best_dist = -1, float("inf")
        for di in available:
            dist = float(np.linalg.norm(
                order_locs[oi] - driver_locs[di]
            ))
            if dist < best_dist:
                best_d, best_dist = di, dist
        if best_d >= 0:
            assignments.append((oi, best_d))
            available.discard(best_d)
    return assignments
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Batch matching | Ride-hailing, delivery | Collect requests over window, solve assignment globally |
| Geospatial indexing | Location-based matching | H3/S2 hexagonal cells for supply-demand aggregation |
| Multi-objective pricing | Revenue vs growth | Constrained optimization: maximize revenue subject to min conversion |
| Causal inference | Surge impact | Switchback experiments (time-based randomization) for pricing |
| Simulation | Strategy testing | Agent-based simulation before deploying pricing changes |

### Common Interview Questions
- [ ] Design a food delivery dispatch system (DoorDash/Uber Eats)
- [ ] How would you build dynamic pricing for a ride-hailing platform?
- [ ] Design an ETA prediction system with real-time updates
- [ ] How do you handle supply-demand imbalance in a marketplace?
- [ ] Design a search ranking system for Airbnb listings

## Comparisons

| Aspect | Greedy Dispatch | Batch Optimization | RL-Based |
|--------|----------------|-------------------|----------|
| Latency | <100ms | 1-5s batches | <100ms (inference) |
| Optimality | Local | Near-global | Learned policy |
| Complexity | $O(n \cdot m)$ | $O(n^3)$ Hungarian | Training cost |
| Fairness | Poor | Configurable | Reward-shaped |

## Key Takeaways
- [ ] Two-sided marketplaces require balancing buyer/seller/platform objectives
- [ ] Dynamic pricing needs causal evaluation (not just A/B tests -- switchback)
- [ ] ETA accuracy directly impacts conversion and trust
- [ ] Batch matching outperforms greedy dispatch but adds latency
- [ ] Geospatial features (H3 cells, travel times) are critical signals
"""

CONTENT["pillar3.design_problems.nlp_llm"] = r"""# NLP & LLM Systems

## Overview
NLP and LLM system design covers building production systems around language models: chatbots, content generation, entity extraction, and RAG-based applications. This topic has surged in interview importance. A senior MLE must design systems that balance quality, latency, cost, and safety.

## Core Concepts

### LLM Application Architecture

```
User Query -> [Guard Rails] -> [Router / Intent] -> [Retrieval (RAG)]
    -> [Prompt Construction] -> [LLM Inference] -> [Output Validation]
    -> [Response Caching] -> User Response
```

### RAG System Design

$$
P(\text{answer} | q) = \sum_{d \in \text{TopK}} P(\text{answer} | q, d) \cdot P(d | q)
$$

| Component | Options | Latency Budget |
|-----------|---------|---------------|
| Embedding | OpenAI, E5, BGE | 10-30ms |
| Vector DB | Pinecone, Weaviate, pgvector | 10-50ms |
| Re-ranker | Cross-encoder, Cohere | 50-100ms |
| LLM | GPT-4, Claude, Llama | 500-5000ms |

### Prompt Engineering Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| Few-shot | Classification, extraction | Provide 3-5 labeled examples in prompt |
| Chain-of-thought | Reasoning tasks | "Think step by step..." |
| Self-consistency | Improve accuracy | Sample N responses, majority vote |
| ReAct | Tool-using agents | Reason -> Act -> Observe loop |

### Cost Optimization

$$
\text{Cost per query} = \frac{\text{input\_tokens} \times p_{\text{in}} + \text{output\_tokens} \times p_{\text{out}}}{1000}
$$

Key strategies: caching, prompt compression, model routing (cheap model first, escalate), batching.

### Evaluation Framework

| Dimension | Metric | Method |
|-----------|--------|--------|
| Relevance | Answer correctness | LLM-as-judge, human eval |
| Faithfulness | Grounded in context | NLI model or citation check |
| Latency | Time to first token (TTFT) | P50/P95 monitoring |
| Safety | Toxicity, PII leakage | Classifier guardrails |
| Cost | $ per query | Token counting |

## Implementation

```python
from dataclasses import dataclass

@dataclass
class RAGResult:
    # Result from RAG pipeline.
    answer: str
    sources: list[str]
    latency_ms: float

def simple_rag_pipeline(
    query: str,
    embedder,
    vector_db,
    llm,
    top_k: int = 5,
) -> RAGResult:
    # Minimal RAG pipeline: embed -> retrieve -> generate.
    import time
    start = time.monotonic()
    # Step 1: Embed query
    q_emb = embedder.encode(query)
    # Step 2: Retrieve relevant docs
    docs = vector_db.search(q_emb, top_k=top_k)
    # Step 3: Construct prompt with context
    context = "\n\n".join(d.text for d in docs)
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        f"Answer based on the context above:"
    )
    # Step 4: Generate answer
    answer = llm.generate(prompt)
    elapsed = (time.monotonic() - start) * 1000
    return RAGResult(
        answer=answer,
        sources=[d.id for d in docs],
        latency_ms=elapsed,
    )
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| RAG | Knowledge-intensive apps | Retrieval reduces hallucination; chunking strategy matters |
| Model routing | Cost optimization | Use small model for easy queries, large for complex |
| Guardrails | Safety-critical apps | Input/output classifiers + PII detection |
| Streaming | Chat applications | SSE for token-by-token delivery, improves perceived latency |
| Evaluation pipeline | Any LLM app | Automated eval (LLM-as-judge) + human annotation |

### Common Interview Questions
- [ ] Design a customer support chatbot using LLMs
- [ ] How would you build a RAG system for enterprise documents?
- [ ] Design a content moderation system using LLMs
- [ ] How do you evaluate LLM output quality at scale?
- [ ] Design a system for LLM-powered code generation

## Comparisons

| Aspect | Fine-tuned Model | RAG | Prompt Engineering |
|--------|-----------------|-----|-------------------|
| Knowledge update | Retrain needed | Update index | Update prompt |
| Cost | High (training) | Medium (infra) | Low |
| Latency | Fast inference | +retrieval overhead | Minimal |
| Hallucination | Moderate | Low (grounded) | High |
| Customization | Deep | Moderate | Surface |

## Key Takeaways
- [ ] RAG is the default pattern for knowledge-intensive LLM applications
- [ ] Chunking strategy and retrieval quality often matter more than the LLM choice
- [ ] Always design guardrails (input validation, output filtering, PII detection)
- [ ] Cost optimization through caching and model routing is essential at scale
- [ ] Evaluation is the hardest part -- invest in automated + human eval pipelines
"""

CONTENT["pillar3.design_problems.cv"] = r"""# Computer Vision Systems

## Overview
Computer vision system design covers building production pipelines for image classification, object detection, segmentation, and visual search. Common at autonomous driving companies, Meta, Google, Amazon (visual search). A senior MLE must design systems handling high-throughput image processing with strict latency requirements.

## Core Concepts

### CV Pipeline Architecture

```
Image Input -> [Pre-processing] -> [Feature Extraction (Backbone)]
    -> [Task Head] -> [Post-processing] -> [Serving]
```

### Model Architecture Choices

| Task | Architecture | Output |
|------|-------------|--------|
| Classification | ResNet, EfficientNet, ViT | Class probabilities |
| Detection | YOLO, DETR, Faster R-CNN | Bounding boxes + classes |
| Segmentation | Mask R-CNN, SAM | Pixel-level masks |
| Visual search | CNN/ViT backbone + embedding | Feature vectors for ANN |

### Object Detection Metrics

$$
\text{AP} = \int_0^1 p(r) \, dr
$$

where $p(r)$ is precision at recall $r$. mAP averages AP across classes.

**IoU (Intersection over Union)**:
$$
\text{IoU} = \frac{|B_{\text{pred}} \cap B_{\text{gt}}|}{|B_{\text{pred}} \cup B_{\text{gt}}|}
$$

Detection is correct if $\text{IoU} \geq 0.5$ (AP@0.5) or averaged over thresholds (AP@[.5:.95]).

### Non-Maximum Suppression (NMS)

```
1. Sort detections by confidence score
2. Pick highest-scoring detection, add to output
3. Remove all detections with IoU > threshold (0.5) with picked box
4. Repeat until no detections remain
```

### Serving Considerations

| Concern | Solution |
|---------|----------|
| Latency | TensorRT, ONNX Runtime, quantization (INT8) |
| Throughput | Batch inference, GPU sharing |
| Image size | Resize/crop pipeline, tiling for large images |
| Model size | Knowledge distillation, pruning, MobileNet |

## Implementation

```python
import numpy as np

def nms(
    boxes: np.ndarray,    # (N, 4) [x1, y1, x2, y2]
    scores: np.ndarray,   # (N,)
    iou_threshold: float = 0.5,
) -> list[int]:
    # Non-Maximum Suppression for object detection.
    order = scores.argsort()[::-1]
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(int(i))
        if len(order) == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        yy1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        xx2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        yy2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_r = (boxes[rest, 2] - boxes[rest, 0]) * (boxes[rest, 3] - boxes[rest, 1])
        iou = inter / (area_i + area_r - inter + 1e-8)
        order = rest[iou <= iou_threshold]
    return keep
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Two-stage detection | High accuracy needed | Region proposal + classification (Faster R-CNN) |
| Single-stage detection | Real-time inference | YOLO/SSD trades accuracy for speed |
| Visual search pipeline | E-commerce, similar images | Backbone embedding + ANN index |
| Edge deployment | Mobile/IoT | MobileNet + quantization + TensorRT |
| Active learning | Limited labels | Uncertainty sampling to prioritize annotation |

### Common Interview Questions
- [ ] Design an image-based product search system (Google Lens)
- [ ] How would you build a real-time object detection system for autonomous driving?
- [ ] Design a content moderation system for images/video
- [ ] How do you handle class imbalance in detection tasks?
- [ ] Design a visual quality inspection system for manufacturing

## Comparisons

| Aspect | CNN (ResNet) | ViT | YOLO v8 |
|--------|-------------|-----|---------|
| Inductive bias | Translation equivariance | Global attention | Anchor-free detection |
| Data efficiency | Good (small datasets) | Needs large data | Good with pretrain |
| Inference speed | Fast | Moderate | Very fast |
| Best for | Classification | Large-scale classification | Real-time detection |

## Key Takeaways
- [ ] Choose architecture based on latency vs accuracy tradeoff for your use case
- [ ] NMS and post-processing design significantly impact detection quality
- [ ] Model optimization (quantization, distillation) is critical for production serving
- [ ] Visual search = backbone embedding + ANN index (same pattern as text search)
- [ ] Data quality and annotation strategy often matter more than model architecture
"""

CONTENT["pillar3.design_problems.fraud_trust"] = r"""# Fraud & Trust Safety

## Overview
Fraud detection and trust & safety systems protect platforms from abuse: payment fraud, fake accounts, spam, scams, and policy violations. These systems operate under extreme class imbalance, adversarial attackers, and strict latency requirements. Common at fintech (Stripe, PayPal), marketplaces (Amazon, eBay), and social platforms (Meta, Twitter).

## Core Concepts

### Fraud Detection Pipeline

```
Event (transaction/action)
    |
    v
[Real-time Rules Engine] -- hard blocks (velocity, blocklist)
    |
    v
[ML Risk Scoring] -- P(fraud) in <50ms
    |
    v
[Decision Engine] -- approve / review / block
    |
    v
[Human Review Queue] -- for borderline cases
    |
    v
[Feedback Loop] -- labels flow back to retrain
```

### Feature Engineering for Fraud

| Feature Type | Examples | Computation |
|-------------|----------|-------------|
| Velocity | Txns in last 1h/24h/7d | Sliding window counters |
| Graph | Device sharing, IP clustering | Connected components |
| Behavioral | Typing speed, navigation pattern | Session analytics |
| Historical | Past chargebacks, account age | Lookup tables |
| Network | Shared payment methods, addresses | Graph features |

### Class Imbalance Handling
Fraud rates typically 0.1-1%. Strategies:

$$
\mathcal{L}_{\text{weighted}} = -\sum [w_+ \cdot y \log \hat{y} + w_- \cdot (1-y) \log(1-\hat{y})]
$$

| Strategy | When to Use |
|----------|------------|
| Class weights ($w_+ = 100$) | Always a good baseline |
| SMOTE / oversampling | Tabular data, small datasets |
| Focal loss: $\alpha(1-p_t)^\gamma \text{CE}$ | Deep models, hard examples |
| Anomaly detection | Unsupervised, novel fraud |
| Ensemble with isolation forest | Complement supervised model |

### Evaluation Metrics
Standard accuracy is misleading. Use:

$$
\text{Precision@k} = \frac{\text{true frauds in top-k predictions}}{k}
$$

Key metrics: **Precision-Recall AUC**, **F1 at operating point**, **False Positive Rate at target True Positive Rate**, **$ saved / $ lost**.

### Adversarial Considerations
Fraudsters adapt. Key defenses:
- **Feature velocity**: Detect feature distribution drift
- **Model versioning**: A/B test new models against current
- **Ensemble diversity**: Multiple model types resist same attack vector
- **Delayed labels**: Chargebacks arrive 30-90 days later

## Implementation

```python
import numpy as np
from collections import defaultdict

class VelocityCounter:
    # Sliding window event counter for fraud features.

    def __init__(self, window_seconds: int = 3600) -> None:
        self.window = window_seconds
        self.events: dict[str, list[float]] = defaultdict(list)

    def add_event(self, key: str, timestamp: float) -> None:
        # Record an event for a given entity.
        self.events[key].append(timestamp)

    def count(self, key: str, current_time: float) -> int:
        # Count events in the sliding window.
        cutoff = current_time - self.window
        times = self.events.get(key, [])
        # Prune old events
        valid = [t for t in times if t > cutoff]
        self.events[key] = valid
        return len(valid)

def fraud_risk_score(
    features: np.ndarray,
    model,
    rules_blocked: bool,
) -> tuple[float, str]:
    # Compute fraud risk score with rules + ML.
    if rules_blocked:
        return 1.0, "BLOCK"
    score = float(model.predict_proba(features.reshape(1, -1))[0, 1])
    if score > 0.9:
        return score, "BLOCK"
    if score > 0.5:
        return score, "REVIEW"
    return score, "APPROVE"
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Rules + ML hybrid | Any fraud system | Rules catch known patterns; ML catches novel ones |
| Graph-based detection | Account networks | Fraud rings share devices/IPs/payment methods |
| Streaming features | Real-time decisions | Flink/Kafka for velocity counters |
| Human-in-the-loop | High-value decisions | ML triages, humans decide borderline cases |
| Feedback delay | Label latency | Train on confirmed labels, use semi-supervised for recent |

### Common Interview Questions
- [ ] Design a real-time payment fraud detection system
- [ ] How do you handle the 30-90 day label delay for chargebacks?
- [ ] Design a fake account detection system for a social platform
- [ ] How do you evaluate a fraud model when labels are noisy?
- [ ] How would you detect coordinated inauthentic behavior (fraud rings)?

## Comparisons

| Aspect | Rules Engine | Supervised ML | Graph Neural Network |
|--------|-------------|--------------|---------------------|
| Latency | <1ms | 5-20ms | 50-200ms |
| Adaptability | Manual updates | Retraining | Retraining |
| Novel fraud | Poor | Moderate | Good (structural) |
| Interpretability | High | Moderate (SHAP) | Low |
| Cold start | Works immediately | Needs labels | Needs graph |

## Key Takeaways
- [ ] Always combine rules (fast, interpretable) with ML (adaptive, generalizable)
- [ ] Class imbalance requires careful metric selection (PR-AUC, not accuracy)
- [ ] Graph features (device/IP/payment sharing) are the most powerful fraud signals
- [ ] Design for adversarial adaptation -- fraudsters will probe and evolve
- [ ] Feedback loops and label quality are the biggest long-term challenges
"""

CONTENT["pillar3.design_problems.infra"] = r"""# ML Infrastructure Design

## Overview
ML infrastructure design covers the systems that support the ML lifecycle: training pipelines, model serving, feature stores, experiment tracking, and monitoring. This topic tests your ability to design reliable, scalable platforms that enable fast iteration. Common at all large tech companies and increasingly at startups.

## Core Concepts

### ML Platform Architecture

```
[Data Layer]          [Training Layer]        [Serving Layer]
 Feature Store         Training Pipeline       Model Server
 Data Warehouse        Experiment Tracker      A/B Testing
 Streaming (Kafka)     Model Registry          Feature Serving
 Label Management      Hyperparameter Tuning   Monitoring/Alerts
```

### Training Pipeline Design

| Component | Tool Examples | Purpose |
|-----------|-------------|---------|
| Orchestration | Airflow, Kubeflow, Metaflow | DAG scheduling, retries |
| Data processing | Spark, Ray, Dask | Distributed feature computation |
| Training | PyTorch + DDP/FSDP, DeepSpeed | Distributed training |
| Experiment tracking | MLflow, W&B, Neptune | Metrics, artifacts, reproducibility |
| Model registry | MLflow, Vertex AI | Version control, promotion gates |

### Model Serving Patterns

| Pattern | Latency | Throughput | Use Case |
|---------|---------|-----------|----------|
| Online (sync) | <50ms | Moderate | Real-time predictions |
| Batch | Hours | Very high | Daily recommendations |
| Streaming | ~seconds | High | Near-real-time scoring |
| Edge | <10ms | Per-device | Mobile, IoT |

### Feature Store Architecture

$$
\text{Feature freshness} = t_{\text{serving}} - t_{\text{event}}
$$

| Mode | Freshness | Storage | Examples |
|------|-----------|---------|----------|
| Batch | Hours-days | Data warehouse | User aggregates |
| Streaming | Seconds-minutes | Redis/DynamoDB | Recent clicks |
| On-demand | Real-time | Computed at request | Current location |

### Model Monitoring

| What to Monitor | Metric | Alert Threshold |
|----------------|--------|-----------------|
| Prediction drift | KL divergence, PSI | PSI > 0.2 |
| Feature drift | Kolmogorov-Smirnov test | p < 0.01 |
| Latency | P50, P95, P99 | P95 > SLA |
| Error rate | 5xx / total | > 0.1% |
| Business metrics | CTR, conversion | > 2 sigma drop |

Population Stability Index:
$$
\text{PSI} = \sum_{i=1}^{n} (p_i - q_i) \ln\left(\frac{p_i}{q_i}\right)
$$

## Implementation

```python
from dataclasses import dataclass, field

@dataclass
class ModelVersion:
    # Model registry entry.
    name: str
    version: int
    artifact_path: str
    metrics: dict[str, float] = field(default_factory=dict)
    stage: str = "staging"  # staging | production | archived

class SimpleModelRegistry:
    # In-memory model registry for illustration.

    def __init__(self) -> None:
        self.models: dict[str, list[ModelVersion]] = {}

    def register(self, model: ModelVersion) -> None:
        # Register a new model version.
        if model.name not in self.models:
            self.models[model.name] = []
        self.models[model.name].append(model)

    def promote(self, name: str, version: int) -> None:
        # Promote a model version to production.
        for mv in self.models.get(name, []):
            if mv.stage == "production":
                mv.stage = "archived"
            if mv.version == version:
                mv.stage = "production"

    def get_production(self, name: str) -> ModelVersion | None:
        # Get the current production model.
        for mv in reversed(self.models.get(name, [])):
            if mv.stage == "production":
                return mv
        return None
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Feature store | Any production ML | Decouple feature engineering from model training/serving |
| Shadow deployment | Safe rollout | Run new model alongside old, compare outputs |
| Canary release | Gradual rollout | Route 1% -> 5% -> 25% -> 100% of traffic |
| Circuit breaker | Fault tolerance | Fall back to simple model if primary fails |
| Training-serving skew | Debug accuracy drops | Same feature code must run in both paths |

### Common Interview Questions
- [ ] Design a feature store for a large-scale recommendation system
- [ ] How would you set up model monitoring and alerting?
- [ ] Design a model serving system that handles 100K QPS
- [ ] How do you prevent training-serving skew?
- [ ] Design an experiment platform for A/B testing ML models

## Comparisons

| Aspect | Batch Serving | Online Serving | Streaming |
|--------|-------------|---------------|-----------|
| Latency | Hours | <50ms | Seconds |
| Compute | Offline cluster | GPU fleet | Stream processor |
| Freshness | Stale | Real-time | Near-real-time |
| Cost | Low (spot instances) | High (always-on) | Medium |
| Complexity | Simple | High (SLA, fallbacks) | Medium |

## Key Takeaways
- [ ] Feature stores solve the training-serving skew problem
- [ ] Model monitoring (drift detection) is as important as model training
- [ ] Shadow/canary deployments are essential for safe model rollouts
- [ ] Design for failure: circuit breakers, fallback models, graceful degradation
- [ ] The ML platform should optimize for iteration speed, not just model performance
"""

CONTENT["pillar3.design_problems.genai"] = r"""# Generative AI Systems

## Overview
Generative AI system design covers building production applications around image generation, text-to-image, code generation, and multimodal systems. This is the newest category in ML system design interviews. Focus areas include prompt management, safety/alignment, cost control, and quality evaluation.

## Core Concepts

### GenAI Application Architecture

```
User Input -> [Safety Filter] -> [Prompt Template] -> [Model Selection]
    -> [Generation] -> [Quality Filter] -> [Output Post-processing]
    -> [Caching Layer] -> User Output
```

### Model Selection Strategy

| Factor | Consideration |
|--------|-------------|
| Quality | Larger models produce better output |
| Latency | Smaller models are faster; quantization helps |
| Cost | Token pricing varies 100x across model sizes |
| Control | Fine-tuned models follow instructions better |
| Safety | RLHF-aligned models are safer but may refuse valid requests |

### Diffusion Models (Image Generation)

Forward process adds noise:
$$
q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t} x_{t-1}, \beta_t I)
$$

Reverse process learns to denoise:
$$
p_\theta(x_{t-1} | x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \sigma_t^2 I)
$$

Training objective (simplified):
$$
\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]
$$

### Serving Optimization

| Technique | Speedup | Quality Impact |
|-----------|---------|---------------|
| KV cache | 2-3x | None |
| Speculative decoding | 2-3x | None |
| Quantization (INT8/INT4) | 2-4x | Minor |
| Distillation | 5-10x | Moderate |
| Prompt caching | Variable | None |
| Batching (continuous) | 2-8x throughput | None |

### Safety & Alignment

| Layer | Method | Purpose |
|-------|--------|---------|
| Input filter | Classifier | Block harmful prompts |
| System prompt | Instructions | Guide model behavior |
| RLHF/DPO | Training | Align with human preferences |
| Output filter | Classifier + rules | Catch harmful outputs |
| Watermarking | Spectral embedding | Detect AI-generated content |

## Implementation

```python
from dataclasses import dataclass

@dataclass
class GenerationConfig:
    # Configuration for text generation.
    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9

def model_router(
    query: str,
    complexity_score: float,
    configs: dict[str, GenerationConfig],
) -> GenerationConfig:
    # Route to appropriate model based on query complexity.
    if complexity_score < 0.3:
        return configs["small"]   # Fast, cheap
    if complexity_score < 0.7:
        return configs["medium"]  # Balanced
    return configs["large"]       # High quality

def semantic_cache_key(
    query: str, embedder,
    cache: dict[str, str],
    threshold: float = 0.95,
) -> str | None:
    # Check semantic cache for similar previous queries.
    q_emb = embedder.encode(query)
    for cached_query, cached_response in cache.items():
        c_emb = embedder.encode(cached_query)
        sim = float(q_emb @ c_emb / (
            (q_emb @ q_emb) ** 0.5 * (c_emb @ c_emb) ** 0.5 + 1e-8
        ))
        if sim > threshold:
            return cached_response
    return None
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Model cascade | Cost optimization | Small model first, escalate only if needed |
| Semantic caching | Repeated queries | Embedding similarity for cache hits |
| Human feedback loop | Quality improvement | Thumbs up/down -> fine-tuning data |
| Watermarking | Content provenance | Embed detectable signals in generated content |
| Guardrails pipeline | Safety | Multi-layer input/output filtering |

### Common Interview Questions
- [ ] Design a text-to-image generation platform (DALL-E/Midjourney)
- [ ] How would you build a code generation assistant?
- [ ] Design a content generation system with quality and safety controls
- [ ] How do you optimize costs for an LLM-powered application at scale?
- [ ] Design an AI writing assistant with real-time collaboration

## Comparisons

| Aspect | API-based (GPT-4) | Self-hosted (Llama) | Fine-tuned |
|--------|-------------------|--------------------|-----------|
| Setup cost | Zero | GPU infrastructure | Training + infra |
| Per-query cost | High | Low (amortized) | Low |
| Customization | Prompt only | Full control | Deep control |
| Latency | Variable (shared) | Predictable | Predictable |
| Data privacy | Data leaves org | On-premise | On-premise |

## Key Takeaways
- [ ] Model routing and caching are the two biggest levers for cost reduction
- [ ] Multi-layer safety (input filter + system prompt + output filter) is mandatory
- [ ] Evaluation is the hardest challenge -- invest in automated + human eval
- [ ] Latency optimization: KV cache, continuous batching, speculative decoding
- [ ] Design for model swappability -- the best model changes every few months
"""

# ===== BUILDING BLOCKS =====

CONTENT["pillar3.building_blocks.two_tower_model"] = r"""# Two-Tower Model

## Overview
The two-tower (dual encoder) architecture is the workhorse of large-scale retrieval. It independently encodes queries and items into a shared embedding space, enabling sub-linear retrieval via ANN. Used at Google, Meta, YouTube, LinkedIn for candidate generation in search and recommendations.

## Core Concepts

### Architecture

```
[User Features]          [Item Features]
      |                        |
  [User Tower]           [Item Tower]
  (MLP/Transformer)      (MLP/Transformer)
      |                        |
  user_emb (d-dim)       item_emb (d-dim)
      \                      /
       \                    /
        cosine_similarity(u, v)
              |
          relevance score
```

### Training Objective

Contrastive loss with in-batch negatives:

$$
\mathcal{L} = -\frac{1}{B} \sum_{i=1}^{B} \log \frac{\exp(\text{sim}(u_i, v_i) / \tau)}{\sum_{j=1}^{B} \exp(\text{sim}(u_i, v_j) / \tau)}
$$

where $\tau$ is a temperature parameter and $B$ is batch size.

### Key Design Decisions

| Decision | Options | Tradeoff |
|----------|---------|----------|
| Similarity function | Cosine, dot product | Cosine normalizes magnitude; dot product allows popularity signal |
| Negative sampling | In-batch, hard negatives | Hard negatives improve quality but need careful mining |
| Temperature $\tau$ | 0.05 - 0.1 | Lower = sharper distribution = harder training |
| Embedding dimension | 64 - 256 | Higher = more expressive but slower ANN |
| Shared layers | None, partial, full | Shared bottom layers reduce params but limit asymmetry |

### Serving Pattern

1. **Offline**: Pre-compute all item embeddings, build ANN index (HNSW, ScaNN)
2. **Online**: Compute user embedding from real-time features, query ANN index
3. **Latency**: User tower ~5ms, ANN lookup ~10ms = total ~15ms

### Limitations
- Cannot model fine-grained query-item interactions (no cross-attention)
- User and item representations are independent -- misses feature crosses
- Quality ceiling compared to cross-encoders (but 1000x faster at scale)

## Implementation

```python
import numpy as np

class TwoTower:
    # Simplified two-tower with random projections.

    def __init__(self, user_dim: int, item_dim: int, emb_dim: int) -> None:
        self.w_user = np.random.randn(user_dim, emb_dim) * 0.01
        self.w_item = np.random.randn(item_dim, emb_dim) * 0.01

    def encode_user(self, feat: np.ndarray) -> np.ndarray:
        # Encode user features to embedding.
        e = feat @ self.w_user
        return e / (np.linalg.norm(e, axis=-1, keepdims=True) + 1e-8)

    def encode_item(self, feat: np.ndarray) -> np.ndarray:
        # Encode item features to embedding.
        e = feat @ self.w_item
        return e / (np.linalg.norm(e, axis=-1, keepdims=True) + 1e-8)

    def contrastive_loss(
        self, u: np.ndarray, v: np.ndarray, tau: float = 0.07,
    ) -> float:
        # In-batch contrastive loss.
        sims = (u @ v.T) / tau  # (B, B)
        # Positive pairs on diagonal
        labels = np.arange(len(u))
        log_softmax = sims - np.log(
            np.exp(sims).sum(axis=1, keepdims=True)
        )
        return float(-log_softmax[labels, labels].mean())
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| In-batch negatives | Large batch training | Free negatives from other examples in batch |
| Hard negative mining | Improve precision | Mine from ANN neighbors or previous model's errors |
| Multi-task towers | Multiple retrieval tasks | Shared backbone with task-specific heads |
| Periodic re-indexing | Item catalog changes | Rebuild ANN index daily/hourly |
| Feature refresh | Real-time personalization | Update user embedding with streaming features |

### Common Interview Questions
- [ ] How does two-tower differ from cross-encoder for retrieval?
- [ ] Why use in-batch negatives vs explicit negative sampling?
- [ ] How do you handle cold-start items with no interaction history?
- [ ] How do you decide embedding dimension and ANN algorithm?
- [ ] How would you add real-time features to the user tower?

## Comparisons

| Aspect | Two-Tower | Cross-Encoder | Matrix Factorization |
|--------|-----------|--------------|---------------------|
| Inference | $O(1)$ per pair + ANN | $O(n)$ per query | Pre-computed |
| Expressiveness | Moderate | High | Low |
| Feature support | Rich features | Rich features | ID-only (basic) |
| Scale | Billions of items | Top-K only | Millions |

## Key Takeaways
- [ ] Two-tower enables billion-scale retrieval via pre-computed embeddings + ANN
- [ ] In-batch negatives are simple and effective but can be biased toward popular items
- [ ] Temperature and hard negative mining are the key hyperparameters to tune
- [ ] The serving pattern (offline item index + online user encoding) is universal
- [ ] Quality ceiling exists -- always pair with a re-ranking stage
"""

CONTENT["pillar3.building_blocks.multi_stage_ranking"] = r"""# Multi-Stage Ranking

## Overview
Multi-stage ranking is the standard architecture for serving ML predictions at scale. Each stage narrows the candidate set while increasing model complexity. This pattern appears in search, recommendations, ads, and feed ranking at every major tech company.

## Core Concepts

### The Ranking Funnel

$$
\text{Full Catalog} \xrightarrow{L0} \text{10K} \xrightarrow{L1} \text{1K} \xrightarrow{L2} \text{100} \xrightarrow{L3} \text{10-50}
$$

| Stage | Name | Model | Latency | Items |
|-------|------|-------|---------|-------|
| L0 | Pre-filtering | Rules, inverted index | <1ms | 10K |
| L1 | Candidate gen | Two-tower, ANN | 10-20ms | 1K |
| L2 | Ranking | Deep model (DCN, DIN) | 20-50ms | 100 |
| L3 | Re-ranking | Business rules, diversity | <10ms | 10-50 |

### Stage Design Principles

**L1 -- Candidate Generation**: Optimize for **recall**. Missing a good item here means it is lost forever. Use multiple retrieval sources:
- Collaborative filtering candidates
- Content-based (embedding similarity)
- Popular/trending items
- Personalized history-based

**L2 -- Ranking**: Optimize for **precision/NDCG**. Feature-rich model that scores each candidate independently:

$$
\text{score}(u, i) = f_\theta(\text{user\_features}, \text{item\_features}, \text{cross\_features})
$$

**L3 -- Re-ranking**: Apply business constraints:
- Diversity (MMR or DPP)
- Freshness boost
- Ads insertion slots
- Author/source diversity

### Maximal Marginal Relevance (MMR)

$$
\text{MMR} = \arg\max_{d_i \in R \setminus S} \left[\lambda \cdot \text{Rel}(d_i) - (1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j)\right]
$$

Balances relevance (first term) with diversity (second term).

### Latency Budget Management
Total budget (e.g., 200ms) is divided across stages:

$$
t_{\text{total}} = t_{L0} + t_{L1} + t_{L2} + t_{L3} + t_{\text{network}} + t_{\text{feature\_fetch}}
$$

Feature fetching (from feature store) often dominates latency.

## Implementation

```python
import numpy as np

def multi_stage_rank(
    user_features: np.ndarray,
    candidate_gen,       # L1: returns candidate IDs
    ranker,              # L2: scores candidates
    item_features: dict, # item_id -> features
    diversity_lambda: float = 0.3,
    top_k: int = 20,
) -> list[int]:
    # Multi-stage ranking pipeline.
    # L1: Candidate generation (recall-optimized)
    candidates = candidate_gen.retrieve(user_features, k=500)
    # L2: Ranking (precision-optimized)
    scores = []
    for cid in candidates:
        feat = item_features.get(cid)
        if feat is not None:
            s = ranker.score(user_features, feat)
            scores.append((cid, s))
    scores.sort(key=lambda x: -x[1])
    ranked = scores[:100]
    # L3: Re-ranking with MMR for diversity
    selected: list[int] = []
    remaining = list(ranked)
    while len(selected) < top_k and remaining:
        best_idx, best_score = 0, -float("inf")
        for idx, (cid, rel) in enumerate(remaining):
            div_penalty = 0.0
            for sid in selected:
                sim = float(np.dot(
                    item_features[cid], item_features[sid]
                ))
                div_penalty = max(div_penalty, sim)
            mmr = (1 - diversity_lambda) * rel - diversity_lambda * div_penalty
            if mmr > best_score:
                best_idx, best_score = idx, mmr
        selected.append(remaining[best_idx][0])
        remaining.pop(best_idx)
    return selected
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Multiple retrieval sources | Broad recall | Merge candidates from CF, content, trending |
| Score calibration | Cross-source ranking | Normalize scores across different L1 sources |
| Feature caching | Latency optimization | Pre-fetch hot features, lazy-load cold ones |
| Cascading models | Progressive filtering | Each stage uses a superset of previous features |
| Online-offline consistency | Debugging | Log features at prediction time for offline replay |

### Common Interview Questions
- [ ] Why not use one powerful model instead of multiple stages?
- [ ] How do you decide the number of candidates at each stage?
- [ ] How do you ensure diversity in the final results?
- [ ] How do you debug when a good item doesn't appear in results?
- [ ] How do you handle latency budgets across stages?

## Comparisons

| Aspect | Single-Stage | Multi-Stage | End-to-End (RL) |
|--------|-------------|-------------|-----------------|
| Latency | Cannot scan all items | Controlled per stage | Amortized |
| Quality | Best per-item | Near-optimal | Optimizes list-level |
| Debuggability | Simple | Stage-by-stage analysis | Black box |
| Engineering | Simple | Moderate | Complex |

## Key Takeaways
- [ ] Multi-stage ranking is not optional at scale -- you cannot score billions of items with a heavy model
- [ ] Recall at L1 is the ceiling for the entire system -- invest heavily here
- [ ] Re-ranking (L3) handles business requirements that pure ML models cannot
- [ ] Feature fetch latency often dominates -- optimize with caching and pre-computation
- [ ] Log predictions and features at each stage for debugging and offline analysis
"""

CONTENT["pillar3.building_blocks.ann"] = r"""# Approximate Nearest Neighbor (ANN)

## Overview
ANN algorithms enable sub-linear similarity search over massive vector collections. They are the backbone of embedding-based retrieval in search, recommendations, and RAG systems. Understanding ANN tradeoffs (recall vs latency vs memory) is essential for any retrieval system design.

## Core Concepts

### Why Approximate?
Exact nearest neighbor search is $O(n \cdot d)$ for $n$ vectors of dimension $d$. For $n = 10^9$ and $d = 256$, this takes seconds per query. ANN trades small accuracy loss for 100-1000x speedup.

### Algorithm Families

| Family | Algorithm | Idea |
|--------|-----------|------|
| Tree-based | Annoy | Random projection trees, search multiple trees |
| Hash-based | LSH | Hash similar vectors to same bucket |
| Graph-based | HNSW | Navigable small-world graph, greedy search |
| Quantization | IVF-PQ | Cluster + product quantization for compression |
| Learned | ScaNN | Learned quantization with anisotropic loss |

### HNSW (Hierarchical Navigable Small World)

Builds a multi-layer graph where:
- Layer 0: All vectors, densely connected
- Layer $l$: Subset of vectors, $\sim n \cdot e^{-l}$ nodes
- Search: Start at top layer, greedily descend

Key parameters:
- **M**: Max connections per node (controls graph density)
- **ef_construction**: Search width during build (quality vs build time)
- **ef_search**: Search width during query (recall vs latency)

### IVF-PQ (Inverted File + Product Quantization)

1. **IVF**: Cluster vectors into $k$ cells using k-means. At query time, search only top-$n_{\text{probe}}$ cells.
2. **PQ**: Split $d$-dimensional vector into $m$ sub-vectors, quantize each to $b$ bits:

$$
\text{Memory per vector} = m \times b \text{ bits}
$$

For $d=256$, $m=32$, $b=8$: memory = 32 bytes (vs 1024 bytes for float32).

Approximate distance:
$$
\hat{d}(x, y) = \sum_{j=1}^{m} d(x_j, c_{q(y_j)})
$$

### Recall-Latency Tradeoff

$$
\text{Recall@k} = \frac{|\text{ANN top-k} \cap \text{exact top-k}|}{k}
$$

Typical targets: Recall@10 > 0.95 with <10ms latency.

## Implementation

```python
import numpy as np

class SimpleIVF:
    # Simplified IVF index for illustration.

    def __init__(self, n_clusters: int = 100) -> None:
        self.n_clusters = n_clusters
        self.centroids: np.ndarray | None = None
        self.buckets: dict[int, list[tuple[int, np.ndarray]]] = {}

    def build(self, vectors: np.ndarray) -> None:
        # Build index using k-means clustering.
        # Simplified: random centroids
        idx = np.random.choice(len(vectors), self.n_clusters, replace=False)
        self.centroids = vectors[idx].copy()
        # Assign vectors to nearest centroid
        for i, v in enumerate(vectors):
            dists = np.linalg.norm(self.centroids - v, axis=1)
            c = int(np.argmin(dists))
            self.buckets.setdefault(c, []).append((i, v))

    def search(
        self, query: np.ndarray, k: int = 10, n_probe: int = 5,
    ) -> list[tuple[int, float]]:
        # Search top-k nearest neighbors.
        assert self.centroids is not None
        # Find nearest clusters
        c_dists = np.linalg.norm(self.centroids - query, axis=1)
        top_clusters = np.argsort(c_dists)[:n_probe]
        # Search within selected clusters
        candidates = []
        for c in top_clusters:
            for idx, vec in self.buckets.get(int(c), []):
                dist = float(np.linalg.norm(query - vec))
                candidates.append((idx, dist))
        candidates.sort(key=lambda x: x[1])
        return candidates[:k]
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| HNSW | Low latency, moderate scale | Best recall/latency tradeoff up to ~10M vectors |
| IVF-PQ | Billion-scale, memory constrained | Compression enables in-memory billion-scale |
| Hybrid (IVF-HNSW) | Large scale + low latency | IVF for partitioning, HNSW within partitions |
| GPU ANN (RAFT) | Ultra-high throughput | GPU-accelerated for batch queries |
| Filtered search | Metadata constraints | Pre-filter or post-filter with attribute predicates |

### Common Interview Questions
- [ ] Compare HNSW vs IVF-PQ -- when would you choose each?
- [ ] How do you handle real-time index updates (new items)?
- [ ] What is the recall-latency tradeoff and how do you tune it?
- [ ] How does product quantization reduce memory?
- [ ] How do you add metadata filtering to ANN search?

## Comparisons

| Aspect | HNSW | IVF-PQ | ScaNN | Annoy |
|--------|------|--------|-------|-------|
| Recall@10 | 0.98+ | 0.90-0.95 | 0.95+ | 0.90 |
| Latency (1M) | ~1ms | ~2ms | ~0.5ms | ~5ms |
| Memory/vector | Full (4d bytes) | Compressed (m bytes) | Compressed | Full |
| Build time | Slow | Fast | Medium | Fast |
| Update support | Partial | Rebuild needed | Rebuild | Rebuild |

## Key Takeaways
- [ ] HNSW is the default choice for most use cases (<100M vectors)
- [ ] IVF-PQ enables billion-scale search with acceptable recall
- [ ] Tuning ef_search (HNSW) or n_probe (IVF) controls recall-latency tradeoff
- [ ] Product quantization reduces memory 10-30x with modest recall loss
- [ ] Real-time updates are challenging -- most systems use periodic re-indexing
"""

CONTENT["pillar3.building_blocks.feature_store"] = r"""# Feature Store

## Overview
A feature store is a centralized system for managing, computing, storing, and serving ML features. It solves training-serving skew, promotes feature reuse, and provides consistent feature freshness guarantees. This is a critical infrastructure component tested in system design interviews.

## Core Concepts

### Why Feature Stores?

| Problem | Without Feature Store | With Feature Store |
|---------|---------------------|-------------------|
| Training-serving skew | Different code paths | Single definition, dual materialization |
| Feature reuse | Copy-paste across teams | Shared feature catalog |
| Freshness SLA | Ad-hoc, inconsistent | Declarative freshness guarantees |
| Point-in-time correctness | Label leakage risk | Built-in time-travel queries |
| Feature discovery | Ask around | Searchable catalog with metadata |

### Architecture

```
[Feature Definitions (code)]
        |
   [Transformation Engine]
    /                  \
[Batch Pipeline]    [Stream Pipeline]
(Spark/Airflow)     (Flink/Kafka)
    \                  /
[Offline Store]    [Online Store]
(Data Warehouse)   (Redis/DynamoDB)
    |                  |
[Training]         [Serving]
```

### Feature Freshness Tiers

| Tier | Freshness | Compute | Storage | Example |
|------|-----------|---------|---------|---------|
| Batch | Hours-days | Spark job | Warehouse | 30-day purchase count |
| Near-real-time | Minutes | Flink/Kafka | Redis | Session click count |
| Real-time | Milliseconds | At request time | Computed | Current GPS location |

### Point-in-Time Correctness

For training data, features must reflect what was known **at prediction time**, not at label time:

$$
\text{features}(t) = \{f_i(t) : f_i \text{ was available at time } t\}
$$

Without this, you get **label leakage** -- the model sees future information during training.

### Key Design Decisions

| Decision | Options | Tradeoff |
|----------|---------|----------|
| Online store | Redis, DynamoDB, Bigtable | Latency vs cost vs scale |
| Offline store | S3/GCS + Parquet, warehouse | Cost vs query flexibility |
| Transformation | SQL, PySpark, Pandas | Expressiveness vs performance |
| Registry | Central catalog | Feature discoverability |
| Monitoring | Drift detection per feature | Operational overhead |

## Implementation

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class FeatureDefinition:
    # Feature metadata and configuration.
    name: str
    entity_key: str     # e.g., "user_id", "item_id"
    freshness: str      # "batch", "nearline", "realtime"
    dtype: str          # "float", "int", "string", "embedding"
    description: str = ""
    owner: str = ""
    tags: list[str] = field(default_factory=list)

class SimpleFeatureStore:
    # In-memory feature store for illustration.

    def __init__(self) -> None:
        self.registry: dict[str, FeatureDefinition] = {}
        self.online: dict[str, dict[str, Any]] = {}  # feature -> {entity: value}

    def register(self, defn: FeatureDefinition) -> None:
        # Register a feature definition.
        self.registry[defn.name] = defn

    def materialize(
        self, feature: str, entity_values: dict[str, Any],
    ) -> None:
        # Write feature values to online store.
        if feature not in self.registry:
            raise KeyError(f"Unknown feature: {feature}")
        self.online.setdefault(feature, {}).update(entity_values)

    def get_online_features(
        self, features: list[str], entity_key: str, entity_id: str,
    ) -> dict[str, Any]:
        # Fetch features for a single entity at serving time.
        result = {}
        for f in features:
            store = self.online.get(f, {})
            result[f] = store.get(entity_id)
        return result
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Dual materialization | Training + serving consistency | Same transform code, different storage backends |
| Feature versioning | Schema evolution | Version features to avoid breaking consumers |
| Backfill pipeline | Historical features for training | Recompute features for past timestamps |
| Feature monitoring | Drift detection | Alert when feature distributions shift |
| Entity key design | Multi-entity features | Composite keys (user_id, item_id) for interaction features |

### Common Interview Questions
- [ ] How does a feature store prevent training-serving skew?
- [ ] Design a feature store that supports batch and real-time features
- [ ] How do you handle point-in-time correctness for training data?
- [ ] How would you monitor feature quality and freshness?
- [ ] When would you NOT use a feature store?

## Comparisons

| Aspect | Feast | Tecton | Hopsworks | Custom |
|--------|-------|--------|-----------|--------|
| Hosting | Self-managed | Managed | Managed/self | Self |
| Real-time | Basic | Advanced | Advanced | Flexible |
| Transformations | Limited | Full pipeline | Full pipeline | Custom |
| Cost | Free (OSS) | Enterprise | Enterprise | Engineering time |

## Key Takeaways
- [ ] Feature stores solve training-serving skew -- the #1 silent ML bug
- [ ] Point-in-time correctness prevents label leakage in training data
- [ ] Design features with freshness tiers (batch / near-real-time / real-time)
- [ ] Feature monitoring (drift, null rates, latency) is essential
- [ ] Start simple (batch features + Redis) and add complexity as needed
"""

CONTENT["pillar3.building_blocks.embedding"] = r"""# Embedding Techniques

## Overview
Embeddings transform discrete or high-dimensional inputs into dense, low-dimensional vector representations. They are foundational to modern ML systems -- powering search, recommendations, NLP, and multimodal applications. Understanding embedding training, serving, and quality evaluation is critical for senior MLE interviews.

## Core Concepts

### Embedding Types

| Input Type | Method | Output |
|-----------|--------|--------|
| Words/tokens | Word2Vec, GloVe, subword (BPE) | Token embeddings |
| Sentences/docs | BERT, E5, BGE, Sentence-BERT | Text embeddings |
| Users/items | Two-tower, matrix factorization | Entity embeddings |
| Images | CNN/ViT backbone | Visual embeddings |
| Categorical features | Learned lookup table | Feature embeddings |

### Word2Vec (Skip-gram)

Predict context words from center word:

$$
\mathcal{L} = -\sum_{(w, c) \in D} \log \sigma(v_c^T v_w) - \sum_{(w, c') \in D'} \log \sigma(-v_{c'}^T v_w)
$$

where $D$ is positive pairs, $D'$ is negative samples, $\sigma$ is sigmoid.

### Contrastive Learning for Embeddings

InfoNCE loss (used in CLIP, SimCLR, E5):

$$
\mathcal{L} = -\log \frac{\exp(\text{sim}(z_i, z_j^+) / \tau)}{\sum_{k=1}^{N} \exp(\text{sim}(z_i, z_k) / \tau)}
$$

### Embedding Quality Metrics

| Metric | What it Measures | How to Compute |
|--------|-----------------|---------------|
| Intrinsic: analogy | Relational structure | "king - man + woman = queen" |
| Intrinsic: clustering | Semantic grouping | Silhouette score on categories |
| Extrinsic: retrieval | Downstream utility | Recall@K on retrieval task |
| Alignment | Cross-modal consistency | Embedding similarity of matched pairs |
| Uniformity | Space utilization | $\log \mathbb{E}[e^{-2\|z_i - z_j\|^2}]$ |

### Embedding Dimension Selection

Rule of thumb:

$$
d \approx \min(600, \; 4 \times (\text{vocab size})^{0.25})
$$

In practice, 64-512 dimensions. Higher dimensions increase expressiveness but also memory and ANN latency.

## Implementation

```python
import numpy as np

class EmbeddingTable:
    # Simple embedding lookup table with L2 normalization.

    def __init__(self, vocab_size: int, dim: int) -> None:
        # Xavier initialization
        scale = np.sqrt(2.0 / (vocab_size + dim))
        self.weights = np.random.randn(vocab_size, dim) * scale

    def lookup(self, ids: list[int]) -> np.ndarray:
        # Lookup and L2-normalize embeddings.
        embs = self.weights[ids]
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        return embs / (norms + 1e-8)

    def similarity(self, id_a: int, id_b: int) -> float:
        # Cosine similarity between two embeddings.
        a = self.lookup([id_a])[0]
        b = self.lookup([id_b])[0]
        return float(np.dot(a, b))

def mean_pooling(
    token_embeddings: np.ndarray,
    attention_mask: np.ndarray,
) -> np.ndarray:
    # Mean pooling over token embeddings (sentence embedding).
    mask = attention_mask[:, :, None]  # (B, T, 1)
    summed = (token_embeddings * mask).sum(axis=1)
    counts = mask.sum(axis=1).clip(min=1e-8)
    return summed / counts
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Pre-trained + fine-tune | Most NLP tasks | Start with BERT/E5, fine-tune on domain data |
| Embedding compression | Memory optimization | PQ, scalar quantization, or dimensionality reduction |
| Multi-modal embeddings | Cross-modal search | CLIP-style training aligns text and image spaces |
| Embedding versioning | Production updates | Retrained embeddings need ANN index rebuild |
| Negative mining | Improve retrieval quality | Hard negatives from current model's top-K errors |

### Common Interview Questions
- [ ] How do you train embeddings for a new domain with limited data?
- [ ] When would you use pre-trained vs task-specific embeddings?
- [ ] How do you handle embedding drift when models are updated?
- [ ] Compare mean pooling vs CLS token for sentence embeddings
- [ ] How do you compress embeddings for billion-scale serving?

## Comparisons

| Aspect | Word2Vec | BERT (CLS) | Sentence-BERT | E5/BGE |
|--------|---------|------------|---------------|--------|
| Granularity | Word | Token/sentence | Sentence | Sentence |
| Context-aware | No | Yes | Yes | Yes |
| Training data | Unlabeled text | Unlabeled text | NLI pairs | Diverse pairs |
| Retrieval quality | Low | Moderate | Good | Best |

## Key Takeaways
- [ ] Embeddings are the universal interface between discrete data and ML models
- [ ] Contrastive learning (InfoNCE) is the dominant training paradigm
- [ ] Embedding quality directly determines retrieval system quality
- [ ] Compression (PQ, quantization) enables billion-scale deployment
- [ ] Always evaluate embeddings on the downstream task, not just intrinsic metrics
"""

CONTENT["pillar3.building_blocks.realtime_features"] = r"""# Real-time Feature Computation

## Overview
Real-time feature computation provides fresh signals for ML predictions within milliseconds to seconds of events occurring. This is critical for fraud detection (recent transaction velocity), recommendations (session clicks), and dynamic pricing (current supply/demand). Designing low-latency, high-throughput feature pipelines is a key system design skill.

## Core Concepts

### Feature Freshness Spectrum

```
[Batch: hours]  ->  [Near-RT: minutes]  ->  [Real-time: ms]
  Spark/Hive         Flink/Kafka            At-request compute
  Warehouse          Redis/DynamoDB         In-memory
```

### Stream Processing Architecture

```
[Event Source] -> [Kafka] -> [Stream Processor (Flink)]
    -> [Aggregation] -> [Online Store (Redis)] -> [Feature Serving]
```

### Common Real-time Feature Patterns

| Pattern | Example | Window |
|---------|---------|--------|
| Sliding window count | Clicks in last 1h | Time-based |
| Sliding window avg | Avg spend in last 24h | Time-based |
| Session aggregates | Items viewed this session | Session-scoped |
| Last-N events | Last 5 search queries | Count-based |
| Exponential decay | Weighted recent activity | Continuous |

### Windowed Aggregation

Tumbling window (non-overlapping):
$$
f(t) = \text{AGG}(\{e_i : t_{\text{start}} \leq e_i.t < t_{\text{end}}\})
$$

Sliding window (overlapping):
$$
f(t) = \text{AGG}(\{e_i : t - w \leq e_i.t < t\})
$$

### Exponential Moving Average

Efficiently computed without storing all events:

$$
\text{EMA}(t) = \alpha \cdot x_t + (1 - \alpha) \cdot \text{EMA}(t-1)
$$

where $\alpha = 1 - e^{-\Delta t / \text{halflife}}$ for time-weighted decay.

### Challenges

| Challenge | Solution |
|-----------|----------|
| Late-arriving events | Watermarks + allowed lateness |
| Exactly-once semantics | Kafka transactions + idempotent writes |
| High cardinality keys | Approximate structures (HyperLogLog, Count-Min Sketch) |
| Feature serving latency | Pre-computed, cached in Redis |
| Backfill for training | Replay events through same pipeline |

## Implementation

```python
import time
from collections import defaultdict, deque

class SlidingWindowCounter:
    # Sliding window event counter with O(1) amortized count.

    def __init__(self, window_secs: int = 3600) -> None:
        self.window = window_secs
        self.queues: dict[str, deque[float]] = defaultdict(deque)

    def add(self, key: str, ts: float | None = None) -> None:
        # Record an event.
        ts = ts or time.monotonic()
        self.queues[key].append(ts)

    def count(self, key: str, now: float | None = None) -> int:
        # Count events in the current window.
        now = now or time.monotonic()
        q = self.queues[key]
        cutoff = now - self.window
        while q and q[0] < cutoff:
            q.popleft()
        return len(q)

class ExponentialMovingAvg:
    # Time-weighted exponential moving average.

    def __init__(self, halflife_secs: float = 3600.0) -> None:
        self.halflife = halflife_secs
        self.state: dict[str, tuple[float, float]] = {}  # key -> (ema, last_ts)

    def update(self, key: str, value: float, ts: float) -> float:
        # Update EMA with a new observation.
        if key not in self.state:
            self.state[key] = (value, ts)
            return value
        prev_ema, prev_ts = self.state[key]
        import math
        dt = max(0.0, ts - prev_ts)
        alpha = 1.0 - math.exp(-dt / self.halflife)
        new_ema = alpha * value + (1 - alpha) * prev_ema
        self.state[key] = (new_ema, ts)
        return new_ema
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Lambda architecture | Batch + real-time features | Batch for accuracy, stream for freshness |
| Kappa architecture | Stream-only | Simplify by treating everything as a stream |
| Feature logging | Training data generation | Log features at prediction time for offline replay |
| Approximate aggregation | High cardinality | HyperLogLog for distinct counts, CMS for frequencies |
| Dual-write consistency | Feature store update | Write to both batch and online store from single source |

### Common Interview Questions
- [ ] How do you ensure consistency between batch and real-time features?
- [ ] Design a real-time feature pipeline for fraud detection
- [ ] How do you handle late-arriving events in a streaming pipeline?
- [ ] When would you use approximate data structures (HLL, CMS)?
- [ ] How do you backfill real-time features for historical training data?

## Comparisons

| Aspect | Batch (Spark) | Near-RT (Flink) | At-Request |
|--------|-------------|-----------------|------------|
| Freshness | Hours | Seconds-minutes | Milliseconds |
| Throughput | Very high | High | Request-limited |
| Complexity | Low | Medium | High |
| Cost | Low (spot) | Medium (always-on) | High (per-request) |
| Backfill | Easy | Medium (replay) | Difficult |

## Key Takeaways
- [ ] Feature freshness directly impacts model quality for time-sensitive applications
- [ ] Sliding window aggregations are the most common real-time feature pattern
- [ ] Exponential moving average is a memory-efficient alternative to window aggregation
- [ ] Late events and exactly-once semantics are the main engineering challenges
- [ ] Log features at prediction time to enable consistent offline training
"""

CONTENT["pillar3.building_blocks.ab_testing"] = r"""# A/B Testing

## Overview
A/B testing is the gold standard for evaluating ML model changes in production. It provides causal evidence of impact on business metrics. A senior MLE must understand experimental design, statistical analysis, and common pitfalls. This topic is tested at every major tech company.

## Core Concepts

### Experiment Design

```
[Traffic] -> [Randomization Unit] -> [Control (A)] -> [Metric Collection]
                                  -> [Treatment (B)] -> [Metric Collection]
                                           |
                                     [Statistical Test]
                                           |
                                     [Ship / Iterate]
```

### Hypothesis Testing Framework

**Null hypothesis**: $H_0: \mu_B - \mu_A = 0$ (no effect)
**Alternative**: $H_1: \mu_B - \mu_A \neq 0$

**Z-test for proportions** (e.g., CTR):

$$
Z = \frac{\hat{p}_B - \hat{p}_A}{\sqrt{\hat{p}(1-\hat{p})\left(\frac{1}{n_A} + \frac{1}{n_B}\right)}}
$$

where $\hat{p} = \frac{n_A \hat{p}_A + n_B \hat{p}_B}{n_A + n_B}$ is the pooled proportion.

### Sample Size Calculation

For desired power $1 - \beta$ and significance $\alpha$:

$$
n = \frac{(z_{\alpha/2} + z_\beta)^2 \cdot 2\sigma^2}{\delta^2}
$$

where $\delta$ is the minimum detectable effect (MDE) and $\sigma^2$ is the variance.

### Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| Peeking | Inflated false positive rate | Sequential testing (always-valid p-values) |
| Network effects | Interference between units | Cluster randomization |
| Simpson's paradox | Segment-level vs overall effect | Pre-stratification |
| Novelty effect | Short-term engagement spike | Run for multiple weeks |
| Multiple testing | Inflated family-wise error | Bonferroni or FDR correction |

### Variance Reduction Techniques

**CUPED** (Controlled-experiment Using Pre-Experiment Data):

$$
\hat{\mu}_{\text{CUPED}} = \bar{Y} - \theta(\bar{X} - \mathbb{E}[X])
$$

where $\theta = \text{Cov}(X, Y) / \text{Var}(X)$ and $X$ is pre-experiment metric.

Variance reduction: $\text{Var}(\hat{\mu}_{\text{CUPED}}) = \text{Var}(Y)(1 - \rho_{XY}^2)$

Can reduce required sample size by 30-50%.

## Implementation

```python
import numpy as np
from scipy import stats

def ab_test_proportions(
    conversions_a: int, total_a: int,
    conversions_b: int, total_b: int,
    alpha: float = 0.05,
) -> dict[str, float]:
    # Two-proportion z-test for A/B experiment.
    p_a = conversions_a / total_a
    p_b = conversions_b / total_b
    p_pool = (conversions_a + conversions_b) / (total_a + total_b)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/total_a + 1/total_b))
    z_stat = (p_b - p_a) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    return {
        "p_a": p_a, "p_b": p_b,
        "lift": (p_b - p_a) / p_a if p_a > 0 else 0.0,
        "z_stat": z_stat, "p_value": p_value,
        "significant": p_value < alpha,
    }

def sample_size_proportions(
    baseline_rate: float,
    mde: float,  # relative minimum detectable effect
    alpha: float = 0.05,
    power: float = 0.8,
) -> int:
    # Required sample size per group.
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    n = ((z_a + z_b) ** 2 * (p1*(1-p1) + p2*(1-p2))) / (p2 - p1) ** 2
    return int(np.ceil(n))
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Sequential testing | Want to peek at results | Always-valid confidence sequences |
| Stratified randomization | Heterogeneous population | Reduces variance, ensures balance |
| Switchback experiments | Network effects (marketplace) | Randomize by time period + region |
| Multi-armed bandit | Exploration cost is high | Thompson sampling or UCB |
| Interleaving | Ranking experiments | More sensitive than parallel A/B |

### Common Interview Questions
- [ ] How do you determine sample size for an A/B test?
- [ ] What is peeking and how do you address it?
- [ ] How would you test a recommendation algorithm change?
- [ ] Explain CUPED and when to use it
- [ ] How do you handle multiple metrics in one experiment?

## Comparisons

| Aspect | A/B Test | Multi-Armed Bandit | Interleaving |
|--------|---------|-------------------|-------------|
| Statistical rigor | High | Moderate | High |
| Regret during test | Fixed | Minimized | Fixed |
| Sample efficiency | Low | High | Very high |
| Use case | Ship/no-ship | Continuous optimization | Ranking comparison |

## Key Takeaways
- [ ] Always calculate required sample size BEFORE running the experiment
- [ ] CUPED reduces variance and required sample size by 30-50%
- [ ] Peeking inflates false positives -- use sequential testing if you need to peek
- [ ] Network effects require special designs (switchback, cluster randomization)
- [ ] Guard rail metrics (latency, errors, revenue) must not regress
"""

CONTENT["pillar3.building_blocks.exploration_exploitation"] = r"""# Exploration / Exploitation

## Overview
The exploration-exploitation tradeoff is fundamental to ML systems that must both leverage known-good options and discover potentially better ones. It appears in recommendations (new content discovery), ads (new creative testing), and any system with feedback loops. Understanding bandit algorithms and their production implementation is essential.

## Core Concepts

### The Multi-Armed Bandit Problem

At each step $t$, choose arm $a_t$ from $K$ arms, observe reward $r_t$:

$$
\text{Regret}(T) = T \cdot \mu^* - \sum_{t=1}^{T} \mu_{a_t}
$$

where $\mu^* = \max_a \mu_a$ is the best arm's expected reward.

### Key Algorithms

| Algorithm | Strategy | Regret Bound |
|-----------|----------|-------------|
| Epsilon-greedy | Random explore with prob $\epsilon$ | $O(\epsilon T + K/\epsilon)$ |
| UCB1 | Optimistic: pick $\arg\max(\hat{\mu}_a + \sqrt{\frac{2\ln t}{n_a}})$ | $O(\sqrt{KT \ln T})$ |
| Thompson Sampling | Sample from posterior, pick max | $O(\sqrt{KT \ln T})$ |
| LinUCB | Contextual: $\hat{\mu} = x^T\theta + \alpha\sqrt{x^T A^{-1} x}$ | $O(d\sqrt{T \ln T})$ |

### Thompson Sampling (Beta-Bernoulli)

For binary rewards (click/no-click):

$$
\theta_a \sim \text{Beta}(\alpha_a, \beta_a)
$$

Update rule:
- Click: $\alpha_a \leftarrow \alpha_a + 1$
- No click: $\beta_a \leftarrow \beta_a + 1$

At each step: sample $\theta_a$ for each arm, pick $\arg\max_a \theta_a$.

### UCB (Upper Confidence Bound)

$$
a_t = \arg\max_a \left[\hat{\mu}_a + c\sqrt{\frac{\ln t}{n_a}}\right]
$$

The second term is the **exploration bonus** -- arms played less get higher bonus.

### Contextual Bandits
When context (user features) is available:

$$
r_t = f(x_t, a_t) + \epsilon_t
$$

LinUCB assumes linear reward: $\mathbb{E}[r|x, a] = x^T \theta_a$

## Implementation

```python
import numpy as np

class ThompsonSampling:
    # Thompson Sampling for Bernoulli bandits.

    def __init__(self, n_arms: int) -> None:
        self.alpha = np.ones(n_arms)  # successes + 1
        self.beta = np.ones(n_arms)   # failures + 1

    def select_arm(self) -> int:
        # Sample from posterior and pick best arm.
        samples = np.random.beta(self.alpha, self.beta)
        return int(np.argmax(samples))

    def update(self, arm: int, reward: float) -> None:
        # Update posterior with observed reward.
        if reward > 0.5:
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1

class EpsilonGreedy:
    # Epsilon-greedy with decay.

    def __init__(self, n_arms: int, epsilon: float = 0.1) -> None:
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = np.zeros(n_arms)
        self.values = np.zeros(n_arms)

    def select_arm(self) -> int:
        # Select arm with epsilon-greedy strategy.
        if np.random.random() < self.epsilon:
            return int(np.random.randint(self.n_arms))
        return int(np.argmax(self.values))

    def update(self, arm: int, reward: float) -> None:
        # Incremental mean update.
        self.counts[arm] += 1
        n = self.counts[arm]
        self.values[arm] += (reward - self.values[arm]) / n
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Thompson Sampling | Default choice | Simple, effective, naturally handles uncertainty |
| Epsilon-greedy | Baseline / simple systems | Easy to implement, epsilon decay over time |
| Contextual bandit | User-specific exploration | LinUCB for personalized content |
| Batched updates | High throughput systems | Collect rewards in batches, update periodically |
| Explore-then-commit | Limited exploration budget | Explore for N rounds, then exploit forever |

### Common Interview Questions
- [ ] When would you use Thompson Sampling vs UCB?
- [ ] How do you implement exploration in a recommendation system?
- [ ] How do contextual bandits differ from standard A/B tests?
- [ ] How do you handle delayed rewards in a bandit setting?
- [ ] Design an explore/exploit system for news article recommendations

## Comparisons

| Aspect | Epsilon-Greedy | UCB1 | Thompson Sampling |
|--------|---------------|------|-------------------|
| Implementation | Trivial | Simple | Simple |
| Regret | $O(T^{2/3})$ | $O(\sqrt{KT\ln T})$ | $O(\sqrt{KT\ln T})$ |
| Adaptability | Fixed $\epsilon$ | Automatic | Automatic |
| Batching | Easy | Difficult | Easy |
| Bayesian | No | No | Yes |

## Key Takeaways
- [ ] Thompson Sampling is the default choice -- simple, robust, and easy to batch
- [ ] Exploration is essential to avoid feedback loops and filter bubbles
- [ ] Contextual bandits personalize exploration using user features
- [ ] In production, exploration budget must be capped (e.g., max 5% exploration traffic)
- [ ] Delayed rewards and batched updates are the main production challenges
"""

CONTENT["pillar3.building_blocks.knowledge_distillation"] = r"""# Knowledge Distillation

## Overview
Knowledge distillation transfers knowledge from a large "teacher" model to a smaller "student" model, enabling deployment under latency and memory constraints. It is critical for production serving where model size directly impacts cost and latency. Common in search ranking, NLP, and edge deployment.

## Core Concepts

### Distillation Framework

```
[Teacher Model (large)]  -->  soft labels (logits/probs)
         |                           |
         v                           v
   [Training Data]  +  [Soft Label Loss]  =  [Student Model (small)]
```

### Distillation Loss

Hinton's knowledge distillation:

$$
\mathcal{L} = \alpha \cdot \mathcal{L}_{\text{CE}}(y, \hat{y}_s) + (1 - \alpha) \cdot T^2 \cdot \text{KL}(\sigma(z_t/T) \| \sigma(z_s/T))
$$

where:
- $z_t, z_s$: teacher and student logits
- $T$: temperature (typically 2-20, higher = softer)
- $\alpha$: balance between hard and soft labels
- $\sigma$: softmax function

### Why Soft Labels Work

Soft probability distributions contain **dark knowledge**:
- A cat image: $P(\text{cat}) = 0.9, P(\text{dog}) = 0.08, P(\text{car}) = 0.001$
- The relative probabilities between non-target classes encode similarity structure
- Higher temperature $T$ amplifies these inter-class relationships

### Distillation Variants

| Variant | What is Transferred | Use Case |
|---------|-------------------|----------|
| Logit distillation | Output probabilities | Classification |
| Feature distillation | Intermediate representations | When architectures differ |
| Attention distillation | Attention maps | Transformer models |
| Self-distillation | Same architecture, fewer layers | Progressive compression |
| Data distillation | Teacher labels unlabeled data | Limited labeled data |

### Compression Ratios

| Domain | Teacher | Student | Speedup | Quality Loss |
|--------|---------|---------|---------|-------------|
| NLP | BERT-Large | DistilBERT | 2x | ~3% |
| NLP | GPT-4 | GPT-3.5 | 10x | ~5-10% |
| Vision | ResNet-152 | ResNet-18 | 6x | ~2% |
| Ranking | Deep cross-net | 2-layer MLP | 10x | ~1-3% |

## Implementation

```python
import numpy as np

def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    # Temperature-scaled softmax.
    scaled = logits / temperature
    exp_scaled = np.exp(scaled - scaled.max(axis=-1, keepdims=True))
    return exp_scaled / exp_scaled.sum(axis=-1, keepdims=True)

def distillation_loss(
    student_logits: np.ndarray,
    teacher_logits: np.ndarray,
    hard_labels: np.ndarray,
    temperature: float = 4.0,
    alpha: float = 0.5,
) -> float:
    # Compute knowledge distillation loss.
    # Soft loss: KL divergence between teacher and student
    teacher_probs = softmax(teacher_logits, temperature)
    student_probs = softmax(student_logits, temperature)
    kl_div = (teacher_probs * np.log(
        teacher_probs / (student_probs + 1e-8) + 1e-8
    )).sum(axis=-1).mean()
    soft_loss = temperature ** 2 * kl_div
    # Hard loss: cross-entropy with true labels
    student_probs_hard = softmax(student_logits, 1.0)
    hard_loss = -np.log(
        student_probs_hard[range(len(hard_labels)), hard_labels] + 1e-8
    ).mean()
    return float(alpha * hard_loss + (1 - alpha) * soft_loss)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Online distillation | Continuous model updates | Teacher scores used as training signal for student |
| Progressive distillation | Very large compression | Multiple rounds of teacher -> student |
| Ensemble distillation | Multiple teachers | Average teacher logits or use mixture |
| Task-specific distillation | Domain adaptation | Distill on in-domain data for better transfer |
| Two-stage: pretrain + distill | NLP models | Pretrain student, then distill task-specific knowledge |

### Common Interview Questions
- [ ] Why does distillation work better than training a small model from scratch?
- [ ] How do you choose the temperature parameter?
- [ ] When would you use feature distillation vs logit distillation?
- [ ] How do you distill from an ensemble of teachers?
- [ ] Design a distillation pipeline for a production ranking model

## Comparisons

| Aspect | Distillation | Pruning | Quantization |
|--------|-------------|---------|-------------|
| Compression type | Architecture | Weights | Precision |
| Typical ratio | 2-10x | 2-5x | 2-4x |
| Quality loss | Low | Low-moderate | Very low |
| Training cost | Full retrain | Fine-tune | Calibration only |
| Combinable | Yes | Yes | Yes |

## Key Takeaways
- [ ] Soft labels contain "dark knowledge" -- inter-class similarity information
- [ ] Temperature controls the softness: higher T reveals more structure
- [ ] Distillation is often combined with quantization and pruning for maximum compression
- [ ] Online distillation enables continuous improvement of production models
- [ ] The teacher model quality is the ceiling for student performance
"""

CONTENT["pillar3.building_blocks.multi_task_learning"] = r"""# Multi-Task Learning

## Overview
Multi-task learning (MTL) trains a single model on multiple related objectives simultaneously. It enables shared representations, reduces serving cost (one model vs many), and can improve generalization through implicit regularization. Widely used in ranking (CTR + CVR + engagement), NLP, and recommendation systems.

## Core Concepts

### MTL Architecture Patterns

**Hard parameter sharing**:
```
[Input Features]
       |
  [Shared Layers]
    /    |    \
[Head1] [Head2] [Head3]
 CTR     CVR    Dwell
```

**Soft parameter sharing**:
```
[Input]    [Input]    [Input]
   |          |          |
[Tower1]  [Tower2]  [Tower3]
   |          |          |
   +-- regularize similarity --+
```

### Loss Weighting

Naive sum often fails because task gradients conflict:

$$
\mathcal{L}_{\text{total}} = \sum_{k=1}^{K} w_k \mathcal{L}_k
$$

**Uncertainty weighting** (Kendall et al.):

$$
\mathcal{L} = \sum_k \frac{1}{2\sigma_k^2} \mathcal{L}_k + \log \sigma_k
$$

where $\sigma_k$ is a learnable task-specific uncertainty parameter.

### Progressive Layered Extraction (PLE)

Addresses negative transfer with task-specific and shared experts:

$$
\text{output}_k = \text{gating}_k(\text{shared\_experts}, \text{task\_k\_experts})
$$

### Multi-Gate Mixture of Experts (MMoE)

$$
y_k = h_k\left(\sum_{i=1}^{n} g_k^{(i)}(x) \cdot f_i(x)\right)
$$

where $g_k$ is a gating network for task $k$ and $f_i$ are shared expert networks.

### Gradient Conflict Resolution

| Method | Approach |
|--------|----------|
| GradNorm | Normalize gradient magnitudes across tasks |
| PCGrad | Project conflicting gradients to orthogonal direction |
| CAGrad | Find common descent direction |
| Nash-MTL | Bargaining solution for gradient directions |

## Implementation

```python
import numpy as np

class MTLModel:
    # Simplified multi-task learning model.

    def __init__(
        self, input_dim: int, hidden_dim: int, n_tasks: int,
    ) -> None:
        self.shared_w = np.random.randn(input_dim, hidden_dim) * 0.01
        self.heads = [
            np.random.randn(hidden_dim, 1) * 0.01
            for _ in range(n_tasks)
        ]
        # Learnable uncertainty weights (log sigma^2)
        self.log_vars = np.zeros(n_tasks)

    def forward(self, x: np.ndarray) -> list[np.ndarray]:
        # Forward pass through shared layers + task heads.
        shared = np.maximum(0, x @ self.shared_w)  # ReLU
        return [shared @ head for head in self.heads]

    def uncertainty_weighted_loss(
        self, losses: list[float],
    ) -> float:
        # Kendall uncertainty weighting.
        total = 0.0
        for k, loss_k in enumerate(losses):
            precision = np.exp(-self.log_vars[k])
            total += precision * loss_k + self.log_vars[k]
        return float(total)

def pcgrad_project(
    grads: list[np.ndarray],
) -> list[np.ndarray]:
    # PCGrad: project conflicting gradients.
    projected = [g.copy() for g in grads]
    for i in range(len(grads)):
        for j in range(len(grads)):
            if i == j:
                continue
            dot = np.dot(projected[i].ravel(), grads[j].ravel())
            if dot < 0:  # Conflicting
                projected[i] -= (
                    dot / (np.dot(grads[j].ravel(), grads[j].ravel()) + 1e-8)
                ) * grads[j]
    return projected
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| MMoE | Tasks with different data distributions | Gating allows task-specific expert selection |
| PLE | Known negative transfer risk | Task-specific experts prevent interference |
| Auxiliary tasks | Improve main task | Add related task (e.g., predicting dwell time helps CTR) |
| Sequential training | Task dependency | Train task A first, freeze, add task B |
| Distill-then-MTL | Production serving | Distill separate teachers into one MTL student |

### Common Interview Questions
- [ ] When does multi-task learning help vs hurt?
- [ ] How do you handle gradient conflicts between tasks?
- [ ] Compare hard vs soft parameter sharing
- [ ] How would you design an MTL model for CTR + CVR prediction?
- [ ] How do you decide which tasks to jointly train?

## Comparisons

| Aspect | Single-Task Models | Hard Sharing MTL | MMoE | PLE |
|--------|-------------------|-----------------|------|-----|
| Serving cost | K models | 1 model | 1 model | 1 model |
| Negative transfer | None | High risk | Lower | Lowest |
| Task correlation needed | N/A | High | Medium | Low |
| Parameters | K x N | N + K heads | N x experts | N x (shared + task) experts |

## Key Takeaways
- [ ] MTL reduces serving cost from K models to 1 and can improve generalization
- [ ] Gradient conflict is the main challenge -- use uncertainty weighting or PCGrad
- [ ] MMoE/PLE architectures handle heterogeneous tasks better than hard sharing
- [ ] Start with hard sharing as a baseline, add complexity only if negative transfer observed
- [ ] Task relatedness determines MTL benefit -- unrelated tasks can hurt each other
"""

# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

def main() -> None:
    """Populate Pillar 3 leaf nodes with content."""
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
