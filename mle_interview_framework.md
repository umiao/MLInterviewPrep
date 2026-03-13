# Mid-Senior MLE 面试系统化准备框架

> **目标**: 以高置信度通过 FAANG + Top Startup 的 Mid-Senior Machine Learning Engineer 面试
> **适用公司**: Nvidia, Google, Airbnb, Uber, LinkedIn, Netflix, Databricks, DoorDash, Scale AI, Perplexity, Glean, Apple, Together AI, Cohere, Character.ai, Harvey AI, Sierra AI, Mistral, Adobe, Roblox, Slack/Salesforce, Amazon, Microsoft, Instacart, Robinhood 等

---

## 目录

1. [面试轮次全景图](#1-面试轮次全景图)
2. [Pillar 1: Coding & Algorithms](#2-pillar-1-coding--algorithms)
3. [Pillar 2: ML Fundamentals & Theory](#3-pillar-2-ml-fundamentals--theory)
4. [Pillar 3: ML System Design](#4-pillar-3-ml-system-design)
5. [Pillar 4: Applied ML & Domain-Specific Knowledge](#5-pillar-4-applied-ml--domain-specific-knowledge)
6. [Pillar 5: ML Infrastructure & MLOps](#6-pillar-5-ml-infrastructure--mlops)
7. [Pillar 6: Deep Learning & LLM Specialization](#7-pillar-6-deep-learning--llm-specialization)
8. [Pillar 7: Math & Statistics Foundations](#8-pillar-7-math--statistics-foundations)
9. [Pillar 8: Behavioral & Leadership](#9-pillar-8-behavioral--leadership)
10. [公司特异性矩阵](#10-公司特异性矩阵)
11. [优先级 Triage 策略](#11-优先级-triage-策略)
12. [每周学习计划模板](#12-每周学习计划模板)

---

## 1. 面试轮次全景图

大多数公司的 mid-senior MLE 面试包含以下轮次的子集:

| 轮次 | 频率 | 典型时长 | 代表公司 |
|------|------|---------|---------|
| Phone Screen (Recruiter) | 100% | 30min | 所有 |
| Coding (Algorithms/DS) | ~95% | 45-60min | Google, Meta, Amazon, Uber, Airbnb, DoorDash |
| ML Coding (实现模型/算法) | ~40% | 45-60min | Nvidia, Netflix, Databricks, Together AI, Mistral |
| ML System Design | ~90% | 45-60min | 几乎所有公司 |
| ML Fundamentals / Theory | ~60% | 30-45min | Google, Apple, Nvidia, Cohere, Character.ai |
| General System Design | ~30% | 45-60min | Google, Amazon, LinkedIn |
| Behavioral / Leadership | ~85% | 30-45min | 所有大厂, Airbnb 尤为重视 |
| Domain Deep Dive / Past Project | ~70% | 45-60min | Netflix, Uber, Airbnb, LinkedIn |
| Take-Home / Practical | ~15% | 数小时-数天 | Scale AI, 部分 startup |
| Research/Paper Discussion | ~20% | 45min | Mistral, Together AI, Cohere, Character.ai |

---

## 2. Pillar 1: Coding & Algorithms

### 2.1 数据结构

| 类别 | 知识点 | 频率 | 例题 |
|------|--------|------|------|
| Array / String | Two pointers, sliding window, prefix sum | ★★★★★ | Merge intervals, Longest substring without repeating |
| HashMap / HashSet | Frequency count, grouping, two-sum pattern | ★★★★★ | Group anagrams, Subarray sum equals K |
| Stack / Queue | Monotonic stack, BFS queue, min-stack | ★★★★ | Daily temperatures, Valid parentheses |
| Linked List | Reverse, merge, cycle detection, LRU cache | ★★★★ | LRU Cache (高频!), Merge K sorted lists |
| Tree / BST | Traversal, LCA, serialize/deserialize | ★★★★★ | Validate BST, Binary tree max path sum |
| Heap / Priority Queue | Top-K, merge sorted, median stream | ★★★★ | Find median from data stream, K closest points |
| Trie | Prefix search, autocomplete | ★★★ | Design autocomplete, Word search II |
| Union-Find | Connected components, redundant edges | ★★★ | Number of islands variant, Accounts merge |
| Segment Tree / BIT | Range query, interval update | ★★ | Range sum query mutable |

### 2.2 算法范式

| 范式 | 关键 Pattern | MLE 相关度 | 例题 |
|------|-------------|-----------|------|
| Binary Search | Search space reduction, rotated arrays, 浮点二分 | ★★★★★ | Search in rotated array, Kth smallest in matrix |
| BFS/DFS | Graph traversal, topological sort, grid search | ★★★★★ | Course schedule, Word ladder |
| Dynamic Programming | Knapsack, LCS, interval DP, bitmask DP | ★★★★ | Edit distance, Coin change, Regular expression matching |
| Greedy | Interval scheduling, Huffman, activity selection | ★★★ | Jump game, Task scheduler |
| Backtracking | Permutations, combinations, constraint satisfaction | ★★★ | N-Queens, Sudoku solver |
| Graph Algorithms | Dijkstra, Bellman-Ford, Floyd-Warshall, MST | ★★★ | Network delay time, Cheapest flights |
| Divide & Conquer | Merge sort variants, quick select | ★★★ | Count of smaller numbers after self |

### 2.3 MLE 特化 Coding 题型

这些题不属于传统 LeetCode，但在 ML 面试中经常出现:

| 题型 | 知识点 | 代表公司 |
|------|--------|---------|
| 矩阵/张量操作 | NumPy broadcasting, einsum, reshape | Nvidia, Google, Together AI |
| 从零实现 ML 算法 | Logistic regression, K-means, KNN, Decision tree (不用sklearn) | Netflix, Apple, Databricks |
| 数据处理 Pipeline | Pandas/Spark 数据清洗、特征工程 | Uber, Airbnb, DoorDash, Instacart |
| Sampling 算法 | Reservoir sampling, weighted sampling, MCMC basics | Google, Uber |
| 概率模拟 | Monte Carlo, A/B test 模拟 | Airbnb, Uber, Robinhood |
| 实现神经网络组件 | Attention, Softmax, BatchNorm, Conv (纯 NumPy/PyTorch) | Nvidia, Together AI, Mistral, Cohere |
| Loss function 实现 | Cross-entropy, focal loss, contrastive loss | Character.ai, Cohere |
| Tokenizer / Text processing | BPE, WordPiece, SentencePiece 实现 | Perplexity, Cohere, Mistral |

### 2.4 刷题策略

- **目标**: 200-300 题 (如果时间有限, 至少 150 高频题)
- **分配**: Easy 20%, Medium 60%, Hard 20%
- **节奏**: 每天 2-3 题, 每题限时 25-40 分钟
- **重点 Pattern**: Sliding Window, Two Pointers, BFS/DFS, DP (背包+区间), Binary Search, Graph (Topo Sort)
- **推荐列表**: Blind 75 → NeetCode 150 → 公司标签题
- **ML Coding**: 单独准备, 手写实现 5-8 个核心算法

---

## 3. Pillar 2: ML Fundamentals & Theory

### 3.1 Supervised Learning

| 子类别 | 知识点 | 深度要求 |
|--------|--------|---------|
| **Linear Models** | Linear/Logistic regression, 正则化 (L1/L2/Elastic Net), 多重共线性, MLE vs MAP | 需要能推导 |
| **Tree Models** | Decision Tree (ID3/C4.5/CART), Random Forest, GBDT, XGBoost, LightGBM, CatBoost | 需要深入理解 splitting criteria, 剪枝, ensemble 原理 |
| **SVM** | Kernel trick, 对偶问题, SMO 算法, margin 的几何意义 | 中等深度, 理解原理 |
| **KNN** | Distance metrics, KD-Tree, Ball Tree, curse of dimensionality | 基础理解 |
| **Naive Bayes** | 条件独立假设, Laplace smoothing, text classification 应用 | 基础理解 |
| **Bias-Variance Tradeoff** | 分解公式, 与模型复杂度的关系, 如何诊断 | 必须精通 |
| **Loss Functions** | MSE, MAE, Huber, Cross-entropy, Hinge, Focal, Contrastive, Triplet | 需要知道何时用什么 |
| **Regularization** | L1 (sparsity), L2 (weight decay), dropout, early stopping, data augmentation | 必须精通 |
| **Evaluation Metrics** | Accuracy, Precision/Recall/F1, AUC-ROC, AUC-PR, NDCG, MAP, MRR, Calibration | 必须精通, 尤其是 ranking metrics |

### 3.2 Unsupervised Learning

| 子类别 | 知识点 |
|--------|--------|
| **Clustering** | K-Means (K-Means++初始化, 收敛证明), DBSCAN, Hierarchical, GMM (EM算法), Spectral Clustering |
| **Dimensionality Reduction** | PCA (特征值分解 vs SVD), t-SNE (perplexity, crowding problem), UMAP, Autoencoders |
| **Anomaly Detection** | Isolation Forest, One-Class SVM, LOF, Autoencoder-based |
| **Topic Modeling** | LDA, NMF |

### 3.3 Optimization

| 知识点 | 详细内容 |
|--------|---------|
| **Gradient Descent 家族** | SGD, Mini-batch, Momentum, Nesterov, Adagrad, RMSProp, Adam, AdamW, LAMB |
| **Learning Rate** | Warmup, cosine annealing, cyclical LR, learning rate finder |
| **Convergence** | 凸优化 vs 非凸, saddle points, local minima, loss landscape |
| **Second-Order Methods** | Newton's method, L-BFGS, Natural Gradient (概念) |
| **Tricks** | Gradient clipping, gradient accumulation, mixed precision training |

### 3.4 Feature Engineering

| 类别 | 技术 |
|------|------|
| **Numerical** | Scaling (Standard/MinMax/Robust), log transform, binning, polynomial features, box-cox |
| **Categorical** | One-hot, label encoding, target encoding, frequency encoding, embeddings |
| **Text** | TF-IDF, word2vec, fastText, character n-grams, subword tokenization |
| **Temporal** | Lag features, rolling stats, time-based splits, cyclical encoding (sin/cos) |
| **Missing Values** | Imputation strategies (mean/median/mode/KNN/MICE), missingness indicators |
| **Feature Selection** | Filter (mutual info, chi2), Wrapper (RFE), Embedded (Lasso, tree importance), SHAP |
| **Feature Crosses** | Interaction terms, polynomial, feature hashing for high-cardinality |

### 3.5 Sampling & Class Imbalance

| 技术 | 说明 |
|------|------|
| **Oversampling** | SMOTE, ADASYN, random oversample |
| **Undersampling** | Random, Tomek links, Edited Nearest Neighbors |
| **Loss Reweighting** | Class weights, focal loss, cost-sensitive learning |
| **Threshold Tuning** | PR curve based optimal threshold |
| **Evaluation** | AUC-PR > AUC-ROC for imbalanced; stratified splits |

### 3.6 Model Selection & Validation

| 知识点 | 详细内容 |
|--------|---------|
| **Cross-Validation** | K-fold, stratified, time-series split, group split, nested CV |
| **Hyperparameter Tuning** | Grid, random, Bayesian (GP, TPE), Hyperband, multi-fidelity |
| **Model Comparison** | Statistical tests (paired t-test, McNemar), confidence intervals |
| **Calibration** | Platt scaling, isotonic regression, reliability diagrams, expected calibration error |

---

## 4. Pillar 3: ML System Design

这是 Mid-Senior MLE 最关键的面试轮次。

### 4.1 通用框架 (推荐使用)

```
Step 1: Clarify Requirements (2-3 min)
  - Business objective / success metric
  - Scale (QPS, data volume, latency requirement)
  - Online vs offline, real-time vs batch
  - Constraints (budget, infra, privacy)

Step 2: Define ML Task (5 min)
  - 问题建模 (classification, regression, ranking, retrieval, generation)
  - 输入/输出定义
  - Baseline approach

Step 3: Data (5-8 min)
  - Data sources (logs, user behavior, content metadata)
  - Labeling strategy (explicit, implicit signals, semi-supervised)
  - Data pipeline (ETL, feature store, data freshness)
  - Sampling strategy, train/val/test split

Step 4: Feature Engineering (5-8 min)
  - User features, item features, context features, cross features
  - Embedding-based features
  - Feature store design (online/offline)

Step 5: Model Architecture (10 min)
  - Candidate models and trade-offs
  - Multi-stage architecture (retrieval → ranking → re-ranking)
  - Ensemble / stacking strategies
  - Loss function selection

Step 6: Training Pipeline (5 min)
  - Training infra (distributed training, GPU allocation)
  - Online learning vs periodic retraining
  - Feature/label leakage prevention

Step 7: Evaluation (5 min)
  - Offline metrics (与 business metric 的关联)
  - Online metrics (A/B test, interleaving)
  - Guardrail metrics

Step 8: Serving & Deployment (5-8 min)
  - Serving architecture (model server, feature serving, caching)
  - Latency budget breakdown
  - A/B testing framework
  - Shadow deployment / canary release

Step 9: Monitoring & Iteration (3-5 min)
  - Data drift / concept drift detection
  - Model performance monitoring
  - Feedback loop design
  - Iteration roadmap
```

### 4.2 经典 ML System Design 题目矩阵

| 领域 | 题目 | 关键技术点 | 目标公司 |
|------|------|-----------|---------|
| **Search/Retrieval** | Design a search ranking system | BM25 → learned ranking, two-tower, semantic search, query understanding | Google, Perplexity, Glean, Amazon |
| **Search/Retrieval** | Design a query autocomplete system | Trie + ML ranking, personalization, real-time update | Google, Amazon, Microsoft |
| **Search/Retrieval** | Design a semantic search engine | Dense retrieval (bi-encoder), ANN index (FAISS/ScaNN), re-ranker (cross-encoder) | Glean, Perplexity, Google |
| **Recommendation** | Design a content recommendation system (feed) | Multi-stage (recall → ranking → reranking), collaborative filtering, deep models | LinkedIn, Netflix, DoorDash |
| **Recommendation** | Design a "People You May Know" system | Graph-based features, link prediction, GNN, privacy constraints | LinkedIn |
| **Recommendation** | Design a video recommendation system | Multi-modal features, watch-time prediction, exploration/exploitation | Netflix, YouTube |
| **Ads** | Design an ad click prediction system | Feature interaction (DeepFM, DCN), calibration, bid optimization | Google Ads, Microsoft, Salesforce |
| **Ads** | Design ad relevance scoring | Query-ad matching, CTR/CVR prediction, multi-task learning | Google, Microsoft |
| **Marketplace** | Design pricing/surge pricing model | Supply-demand modeling, causal inference, geo-temporal features | Uber, Airbnb, DoorDash, Instacart |
| **Marketplace** | Design ETA prediction system | Spatial-temporal modeling, graph neural networks, real-time features | Uber, DoorDash, Instacart |
| **Marketplace** | Design a matching/dispatch system | Bipartite matching, online optimization, fairness constraints | Uber, DoorDash |
| **NLP** | Design a spam/abuse detection system | Text classification, multimodal, adversarial robustness, human-in-loop | LinkedIn, Airbnb, Slack |
| **NLP** | Design an entity extraction system | NER, relation extraction, knowledge graph | Salesforce, Glean, Harvey AI |
| **NLP** | Design a question-answering system | RAG architecture, retrieval + generation, hallucination mitigation | Perplexity, Glean, Harvey AI |
| **NLP/LLM** | Design a chatbot / conversational AI | Dialog management, LLM serving, guardrails, memory | Character.ai, Sierra AI, Salesforce |
| **NLP/LLM** | Design a document summarization system | Extractive + abstractive, faithfulness evaluation, long-context | Harvey AI, Glean, Adobe |
| **CV** | Design an image classification/moderation pipeline | CNN/ViT, data augmentation, active learning, edge deployment | Apple, Scale AI, Roblox |
| **CV** | Design a visual search system | Image embeddings, ANN search, multimodal fusion | Airbnb (listing photos), Adobe |
| **Fraud/Trust** | Design a fraud detection system | Imbalanced classification, real-time scoring, graph features | Robinhood, Uber, Airbnb, Instacart |
| **Fraud/Trust** | Design an account takeover detection system | Behavioral biometrics, anomaly detection, session analysis | Robinhood, DoorDash |
| **Infra** | Design a feature store | Online/offline serving, consistency, backfill, point-in-time correctness | Databricks, Uber, Airbnb |
| **Infra** | Design an ML training platform | Distributed training, experiment tracking, hyperparameter optimization | Databricks, Nvidia, Scale AI |
| **GenAI** | Design an LLM-powered code assistant | Code generation, RAG over codebase, evaluation (HumanEval), latency | Microsoft Copilot, Adobe |
| **GenAI** | Design a multimodal content generation pipeline | Text-to-image, image editing, style transfer, safety filtering | Adobe, Character.ai |

### 4.3 ML System Design 高频 Building Blocks

需要熟练掌握的组件, 能在面试中快速展开:

| Building Block | 核心知识 |
|---------------|---------|
| **Two-Tower Model** | User tower + Item tower, dot product, negative sampling, in-batch negatives |
| **Multi-Stage Ranking** | Candidate retrieval (ANN) → Pre-ranking (light model) → Ranking (heavy model) → Re-ranking (diversity, business rules) |
| **Approximate Nearest Neighbor (ANN)** | FAISS (IVF, PQ, HNSW), ScaNN, Annoy, Pinecone, Milvus; tradeoffs: recall vs latency vs memory |
| **Feature Store** | Feast, Tecton; online (Redis/DynamoDB) vs offline (Hive/S3); point-in-time correctness |
| **Embedding** | Word2Vec, Item2Vec, Graph embeddings (Node2Vec, DeepWalk), pre-trained (BERT, CLIP) |
| **Real-time Feature Computation** | Flink/Spark Streaming, Kafka, sliding window aggregations |
| **A/B Testing** | Randomization unit, sample size calculation, multiple testing correction, novelty/primacy effects |
| **Exploration/Exploitation** | Epsilon-greedy, UCB, Thompson Sampling, contextual bandits |
| **Knowledge Distillation** | Teacher-student, soft labels, intermediate layer matching |
| **Multi-Task Learning** | Shared-bottom, MMoE, PLE; task relationships, loss weighting |
| **Calibration** | Platt scaling, isotonic regression, temperature scaling; why it matters for CTR prediction |
| **Negative Sampling** | Random negatives, hard negatives, in-batch negatives, curriculum learning |
| **Data Flywheel** | User feedback → labeling → retraining → better model → more engagement → more data |

---

## 5. Pillar 4: Applied ML & Domain-Specific Knowledge

### 5.1 Recommender Systems (LinkedIn, Netflix, DoorDash, Instacart, Airbnb)

| 知识点 | 详细内容 |
|--------|---------|
| **Collaborative Filtering** | User-based CF, Item-based CF, Matrix Factorization (ALS, SVD++), implicit vs explicit feedback |
| **Content-Based** | TF-IDF profiles, embedding similarity, cold-start handling |
| **Deep Recommendation** | Wide & Deep, DeepFM, DCN v2, DIN (Deep Interest Network), DIEN, SIM |
| **Sequential Rec** | GRU4Rec, SASRec, BERT4Rec, transformer-based session models |
| **Graph-based Rec** | PinSage (Pinterest), LightGCN, GAT for social networks |
| **Multi-objective** | Engagement vs revenue vs long-term retention; Pareto optimization, scalarization |
| **Diversity & Exploration** | DPP (Determinantal Point Process), MMR, coverage metrics |
| **Cold Start** | Content-based fallback, popularity-based, bandits, meta-learning |
| **Real-time Personalization** | Session-based features, real-time embedding updates, streaming infrastructure |

### 5.2 Search & Information Retrieval (Google, Amazon, Perplexity, Glean, Microsoft)

| 知识点 | 详细内容 |
|--------|---------|
| **Classic IR** | BM25, TF-IDF, inverted index, query expansion |
| **Neural Retrieval** | Bi-encoder (dense retrieval), cross-encoder (re-ranking), ColBERT, SPLADE |
| **Query Understanding** | Intent classification, query rewriting, entity recognition, spell correction |
| **Learning to Rank** | Pointwise (regression), Pairwise (RankNet, LambdaRank), Listwise (ListNet, LambdaMART) |
| **Evaluation** | NDCG, MAP, MRR, precision@k, interleaving experiments |
| **Retrieval-Augmented Generation (RAG)** | Chunking strategies, embedding models, hybrid search (sparse + dense), re-ranking, citation generation |
| **Knowledge Graphs** | Entity linking, relation extraction, graph-based QA |
| **Multi-modal Search** | CLIP-based, text-image alignment, visual QA |

### 5.3 NLP & LLM Applications (Perplexity, Glean, Harvey AI, Character.ai, Cohere, Mistral, Sierra AI)

| 知识点 | 详细内容 |
|--------|---------|
| **Text Classification** | BERT fine-tuning, few-shot with LLM, prompt-based classification |
| **NER & IE** | Sequence labeling (BiLSTM-CRF, BERT-CRF), span extraction, joint extraction |
| **Summarization** | Extractive (TextRank, BertSum), Abstractive (Seq2Seq, T5), faithfulness metrics (FactCC, QAGS) |
| **Sentiment/Aspect Analysis** | Fine-grained sentiment, aspect-based, emotion detection |
| **Question Answering** | Extractive QA (SQuAD-style), Generative QA, Open-domain QA, RAG |
| **Dialog Systems** | Task-oriented (NLU→DM→NLG), Open-domain (LLM-based), guardrails, safety |
| **LLM Application Patterns** | Prompt engineering, chain-of-thought, ReAct, tool use, function calling, structured output |

### 5.4 Ads & Monetization (Google Ads, Microsoft, Salesforce)

| 知识点 | 详细内容 |
|--------|---------|
| **CTR Prediction** | Feature interaction models (FM, DeepFM, DCN), calibration, freshness |
| **CVR Prediction** | Delayed conversion, counterfactual prediction, multi-touch attribution |
| **Bid Optimization** | Second-price auction, pacing, budget allocation, ROI optimization |
| **Multi-Task** | CTR + CVR + engagement jointly; ESMM (Entire Space Multi-Task Model) |
| **Creative Optimization** | Auto-generated ad copy, image selection, multi-armed bandit for creative |

### 5.5 Marketplace & Logistics (Uber, DoorDash, Airbnb, Instacart)

| 知识点 | 详细内容 |
|--------|---------|
| **Dynamic Pricing** | Supply-demand equilibrium, price elasticity, geospatial modeling |
| **ETA Prediction** | Graph-based routing, traffic prediction, spatial-temporal models (ST-GCN) |
| **Matching/Dispatch** | Bipartite matching, Hungarian algorithm, online matching with forecasting |
| **Demand Forecasting** | Time-series (Prophet, DeepAR), spatial decomposition, event features |
| **Causal Inference** | Treatment effect estimation, propensity score matching, instrumental variables, diff-in-diff |
| **Geospatial ML** | H3 hexagonal indexing, spatial features, geo-embedding |

### 5.6 Computer Vision (Apple, Nvidia, Scale AI, Adobe, Roblox)

| 知识点 | 详细内容 |
|--------|---------|
| **Classification** | ResNet, EfficientNet, ViT, DeiT, ConvNeXt |
| **Detection** | YOLO (v5-v8), DETR, Faster R-CNN, anchor-free (FCOS, CenterNet) |
| **Segmentation** | U-Net, Mask R-CNN, SAM (Segment Anything), panoptic segmentation |
| **Generative** | GAN (StyleGAN), Diffusion Models, VAE, ControlNet |
| **Self-Supervised** | SimCLR, BYOL, MAE, DINO, CLIP |
| **3D/Video** | NeRF, 3D Gaussian Splatting, video understanding (SlowFast, TimeSformer) |
| **Edge Deployment** | MobileNet, quantization, pruning, TensorRT, CoreML |

### 5.7 Trust & Safety / Fraud Detection (Robinhood, Uber, Airbnb)

| 知识点 | 详细内容 |
|--------|---------|
| **Anomaly Detection** | Statistical (z-score, IQR), ML (Isolation Forest, Autoencoder), graph-based |
| **Graph-based Fraud** | Device graphs, transaction graphs, GNN for fraud rings |
| **Real-time Scoring** | Low-latency serving, feature freshness, cascading models |
| **Adversarial Robustness** | Feature drift under adversarial manipulation, model stability |
| **Explainability** | SHAP, LIME for regulatory compliance, audit trails |

---

## 6. Pillar 5: ML Infrastructure & MLOps

### 6.1 Training Infrastructure

| 知识点 | 详细内容 |
|--------|---------|
| **Distributed Training** | Data Parallelism, Model Parallelism (Tensor/Pipeline), FSDP, DeepSpeed ZeRO (Stage 1/2/3) |
| **GPU Programming Concepts** | CUDA basics, memory hierarchy, GPU utilization, profiling (nsight, PyTorch profiler) |
| **Mixed Precision** | FP16, BF16, FP8, loss scaling, when/why to use |
| **Training Frameworks** | PyTorch DDP, FSDP, DeepSpeed, Megatron-LM, JAX/Flax, Ray Train |
| **Experiment Tracking** | MLflow, Weights & Biases, experiment reproducibility |
| **Hyperparameter Optimization** | Optuna, Ray Tune, Bayesian Optimization, Population-Based Training |

### 6.2 Serving Infrastructure

| 知识点 | 详细内容 |
|--------|---------|
| **Model Serving** | TorchServe, Triton Inference Server, TFServing, vLLM, TensorRT-LLM |
| **Optimization** | Quantization (INT8/INT4, GPTQ, AWQ), Pruning, Knowledge Distillation, ONNX export |
| **LLM Serving** | KV-cache, PagedAttention (vLLM), continuous batching, speculative decoding |
| **Latency Optimization** | Batching strategies, model caching, request routing, GPU sharing |
| **Scaling** | Horizontal scaling, autoscaling, load balancing, GPU cluster management |

### 6.3 Data Infrastructure

| 知识点 | 详细内容 |
|--------|---------|
| **Data Processing** | Spark (PySpark), Flink, Beam; batch vs streaming |
| **Feature Store** | Feast, Tecton, Databricks Feature Store; online/offline consistency |
| **Data Quality** | Great Expectations, schema validation, data drift monitoring |
| **Data Versioning** | DVC, Delta Lake, lakehouse architecture |
| **Label Management** | Label Studio, Snorkel (programmatic labeling), active learning loops |

### 6.4 ML Pipeline & Ops

| 知识点 | 详细内容 |
|--------|---------|
| **Orchestration** | Airflow, Kubeflow Pipelines, Prefect, Dagster, Argo Workflows |
| **CI/CD for ML** | Model validation gates, shadow deployment, A/B testing infra |
| **Monitoring** | Data drift (PSI, KS-test), model performance decay, feature importance shift |
| **Model Registry** | MLflow Model Registry, versioning, lineage tracking |
| **Containerization** | Docker, Kubernetes, GPU scheduling (nvidia-docker) |

---

## 7. Pillar 6: Deep Learning & LLM Specialization

### 7.1 Transformer 深度理解

| 知识点 | 深度要求 | 详细内容 |
|--------|---------|---------|
| **Self-Attention** | 必须能手推 | Q, K, V 计算, Scaled dot-product, 复杂度 O(n²d) |
| **Multi-Head Attention** | 必须精通 | Head 数量的影响, concatenation, 不同 head 学到不同 pattern |
| **Position Encoding** | 必须精通 | Sinusoidal, learned, RoPE (旋转位置编码), ALiBi |
| **Layer Normalization** | 需理解 | Pre-norm vs post-norm, RMSNorm, 训练稳定性 |
| **Feed-Forward** | 需理解 | FFN 的 role (key-value memories), SwiGLU activation |
| **Attention Variants** | 需了解 | MHA, MQA, GQA; Flash Attention, Ring Attention |
| **Architecture Variants** | 需了解 | Encoder-only (BERT), Decoder-only (GPT), Encoder-Decoder (T5) |

### 7.2 Pre-trained Language Models

| 模型族 | 关键知识 |
|--------|---------|
| **BERT 系** | MLM + NSP, fine-tuning patterns, [CLS] embedding, tokenization (WordPiece) |
| **GPT 系** | Autoregressive LM, in-context learning, emergence, scaling laws |
| **T5 / BART** | Text-to-text framework, denoising pre-training, conditional generation |
| **LLaMA / Mistral** | Open-source LLM, 架构创新 (GQA, SwiGLU, RoPE), 社区生态 |
| **Mixture of Experts** | Mistral MoE, Switch Transformer, routing, load balancing, expert specialization |

### 7.3 LLM Training & Alignment

| 阶段 | 知识点 |
|------|--------|
| **Pre-training** | 数据收集与清洗, tokenizer training, 训练策略 (chinchilla scaling), curriculum learning |
| **Supervised Fine-Tuning (SFT)** | Instruction tuning data, format, chat templates |
| **RLHF** | Reward model training, PPO algorithm, KL divergence constraint |
| **DPO / Alternatives** | Direct Preference Optimization, ORPO, KTO; 相比 RLHF 的优缺点 |
| **Parameter-Efficient Fine-Tuning** | LoRA, QLoRA, adapter layers, prefix tuning, prompt tuning |
| **Evaluation** | Benchmarks (MMLU, HumanEval, MT-Bench), LLM-as-judge, contamination |

### 7.4 LLM Inference Optimization

| 技术 | 详细内容 |
|------|---------|
| **KV Cache** | 原理, memory management, PagedAttention |
| **Quantization** | GPTQ, AWQ, SmoothQuant, FP8; accuracy-latency tradeoff |
| **Speculative Decoding** | Draft model + verification, Medusa, lookahead decoding |
| **Continuous Batching** | Dynamic batching, iteration-level scheduling |
| **Serving Systems** | vLLM, TensorRT-LLM, Triton, SGLang |
| **Long Context** | Rope scaling, context caching, sparse attention patterns |

### 7.5 Retrieval-Augmented Generation (RAG) 深度

| 组件 | 知识点 |
|------|--------|
| **Chunking** | Fixed-size, semantic, recursive, parent-child, late chunking |
| **Embedding Models** | OpenAI, Cohere Embed, E5, BGE, GTE; 选择标准 (MTEB benchmark) |
| **Vector Database** | Pinecone, Weaviate, Milvus, Qdrant, pgvector; index types (HNSW, IVF) |
| **Hybrid Search** | Sparse (BM25) + Dense, reciprocal rank fusion, learned sparse (SPLADE) |
| **Re-ranking** | Cross-encoder, ColBERT, Cohere Rerank, diversity re-ranking |
| **Advanced RAG** | Query decomposition, self-RAG, CRAG, multi-hop reasoning, citation |
| **Evaluation** | Retrieval (Recall@K, MRR), Generation (faithfulness, relevance, answer quality) |
| **Hallucination Mitigation** | Grounding, attribution, factual consistency checking, constrained generation |

### 7.6 Multimodal Models

| 知识点 | 详细内容 |
|--------|---------|
| **Vision-Language** | CLIP, BLIP-2, LLaVA, GPT-4V architecture concepts |
| **Image Generation** | Stable Diffusion, DALL-E architecture, latent diffusion, ControlNet |
| **Audio** | Whisper, audio spectrogram transformers, TTS (bark, VITS) |
| **Fusion Strategies** | Early fusion, late fusion, cross-attention fusion |

---

## 8. Pillar 7: Math & Statistics Foundations

### 8.1 Probability & Statistics

| 知识点 | MLE 面试相关度 | 详细内容 |
|--------|--------------|---------|
| **Probability Basics** | ★★★★★ | Bayes' theorem, conditional probability, independence, chain rule |
| **Common Distributions** | ★★★★★ | Bernoulli, Binomial, Poisson, Gaussian, Exponential, Beta, Dirichlet |
| **Expectation & Variance** | ★★★★★ | Law of total expectation/variance, covariance, correlation |
| **MLE & MAP** | ★★★★★ | 推导 MLE for Gaussian/Bernoulli, prior 的 role, conjugate priors |
| **Central Limit Theorem** | ★★★★ | 应用于 A/B testing, confidence intervals |
| **Hypothesis Testing** | ★★★★ | p-value, Type I/II errors, power, multiple testing (Bonferroni, FDR) |
| **Bayesian Inference** | ★★★ | Posterior computation, MCMC (Metropolis-Hastings, Gibbs), variational inference basics |
| **Information Theory** | ★★★ | Entropy, cross-entropy, KL divergence, mutual information |

### 8.2 Linear Algebra

| 知识点 | MLE 面试相关度 | 详细内容 |
|--------|--------------|---------|
| **Matrix Operations** | ★★★★★ | Multiplication, transpose, inverse, rank, trace |
| **Eigendecomposition** | ★★★★ | Eigenvalues/eigenvectors, PCA derivation, spectral theorem |
| **SVD** | ★★★★ | Full vs truncated, 应用于 matrix factorization / dimensionality reduction |
| **Matrix Calculus** | ★★★ | Gradient of matrix expressions, chain rule for tensors |
| **Positive (Semi-)Definite** | ★★★ | Kernel functions, covariance matrices |

### 8.3 Calculus & Optimization

| 知识点 | MLE 面试相关度 | 详细内容 |
|--------|--------------|---------|
| **Multivariable Calculus** | ★★★★ | Gradients, Jacobian, Hessian |
| **Chain Rule** | ★★★★★ | Backpropagation derivation |
| **Convex Optimization** | ★★★ | Convex sets/functions, KKT conditions, duality |
| **Lagrange Multipliers** | ★★★ | Constrained optimization, SVM dual derivation |

---

## 9. Pillar 8: Behavioral & Leadership

### 9.1 常见问题类别

| 类别 | 典型问题 | 准备要点 |
|------|---------|---------|
| **Technical Leadership** | "Tell me about a time you led a technically complex project" | 强调技术决策、架构选择、trade-off 分析 |
| **Influence Without Authority** | "How did you convince stakeholders to adopt your approach?" | Data-driven persuasion, prototype, cross-team collaboration |
| **Conflict Resolution** | "Describe a disagreement with a teammate" | Focus on resolution, not blame; what you learned |
| **Ambiguity** | "How do you handle ambiguous requirements?" | Structured approach to break down ambiguity, seeking clarity |
| **Failure & Learning** | "Tell me about a project that failed" | Honest, reflective, specific learnings, how you applied them |
| **Impact** | "What is the most impactful ML project you worked on?" | Quantified business impact, technical innovation |
| **Mentorship** | "How have you helped junior engineers grow?" | Code reviews, 1:1s, knowledge sharing, pair programming |
| **Cross-functional** | "How do you work with PMs/data scientists/stakeholders?" | Understanding business context, translating requirements |
| **Prioritization** | "How do you prioritize competing projects?" | Framework (impact vs effort), alignment with team goals |
| **Culture Fit** | "Why this company?" | Research company values, genuine alignment |

### 9.2 STAR 框架 + Quantification

```
Situation: 简洁的背景 (1-2 句)
Task: 你的具体责任 (1 句)
Action: 你做了什么 (详细, 3-5 句, 突出 YOUR contribution)
Result: 量化成果 (数字！revenue, latency, accuracy, adoption rate)
```

### 9.3 公司特化 Behavioral

| 公司 | 特别关注 |
|------|---------|
| **Google** | Googleyness, cognitive ability, leadership (for senior) |
| **Amazon** | 16 Leadership Principles (必须用LP语言回答!) |
| **Airbnb** | Core values (Belong Anywhere), culture fit 非常重要 |
| **Netflix** | Culture deck, freedom & responsibility, candor |
| **Uber** | Great Minds Don't Think Alike, We Build Globally We Live Locally |
| **LinkedIn** | Transformation, Integrity, Collaboration, Humor, Results |
| **Apple** | Attention to detail, user experience obsession, secrecy |
| **Meta** | Move fast, be bold, focus on impact |

### 9.4 准备策略

- 准备 8-10 个高质量 STAR 故事, 覆盖上述类别
- 每个故事都要有**量化的 result**
- 针对 Amazon 单独准备 LP mapping
- 练习简洁表达 (每个故事 2-3 分钟)
- 准备 2-3 个"问面试官的问题" (关于 team, tech stack, growth, culture)

---

## 10. 公司特异性矩阵

### 10.1 面试侧重点 Heatmap

| 公司 | Coding | ML Theory | ML Sys Design | Infra/MLOps | Behavioral | LLM/DL | Domain |
|------|--------|-----------|--------------|-------------|------------|--------|--------|
| Google (Search/Ads) | ★★★★★ | ★★★★ | ★★★★★ | ★★★ | ★★★★ | ★★★ | Search/Ads |
| Nvidia | ★★★★ | ★★★★ | ★★★ | ★★★★★ | ★★★ | ★★★★★ | GPU/CUDA |
| Airbnb | ★★★★ | ★★★ | ★★★★★ | ★★★ | ★★★★★ | ★★ | Marketplace |
| Uber (ML) | ★★★★ | ★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★ | Marketplace |
| LinkedIn | ★★★★ | ★★★★ | ★★★★★ | ★★★ | ★★★★ | ★★★ | RecSys/Search |
| Netflix | ★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★ | RecSys |
| Databricks | ★★★★ | ★★★★ | ★★★★ | ★★★★★ | ★★★ | ★★★★ | Infra |
| DoorDash | ★★★★ | ★★★ | ★★★★★ | ★★★ | ★★★★ | ★★ | Marketplace |
| Scale AI | ★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★ | ★★★★ | Data/Infra |
| Perplexity | ★★★ | ★★★★ | ★★★★★ | ★★★★ | ★★★ | ★★★★★ | Search/RAG |
| Glean | ★★★ | ★★★★ | ★★★★★ | ★★★ | ★★★ | ★★★★★ | Search/RAG |
| Apple (ML) | ★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★★ | On-device ML |
| Together AI | ★★★ | ★★★★★ | ★★★ | ★★★★★ | ★★★ | ★★★★★ | LLM Infra |
| Cohere | ★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★ | ★★★★★ | NLP/LLM |
| Character.ai | ★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★ | ★★★★★ | LLM/Dialog |
| Harvey AI | ★★★ | ★★★★ | ★★★★★ | ★★★ | ★★★ | ★★★★★ | LLM/Legal |
| Sierra AI | ★★★ | ★★★★ | ★★★★★ | ★★★ | ★★★★ | ★★★★★ | LLM/Agent |
| Mistral | ★★★ | ★★★★★ | ★★★ | ★★★★★ | ★★ | ★★★★★ | LLM Core |
| Adobe (MLE) | ★★★★ | ★★★★ | ★★★★ | ★★★ | ★★★★ | ★★★★ | GenAI/CV |
| Roblox | ★★★★ | ★★★ | ★★★★ | ★★★ | ★★★★ | ★★★ | CV/3D |
| Slack/Salesforce | ★★★★ | ★★★ | ★★★★ | ★★★ | ★★★★ | ★★★★ | NLP/Einstein |
| Amazon (Search) | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ | ★★★★★ | ★★★ | Search/LP |
| Microsoft (Bing) | ★★★★ | ★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | Search/LLM |
| Instacart | ★★★★ | ★★★ | ★★★★★ | ★★★ | ★★★★ | ★★ | Marketplace |
| Robinhood | ★★★★ | ★★★ | ★★★★ | ★★★ | ★★★★ | ★★ | Fraud/Finance |

### 10.2 公司分组策略

根据面试准备的相似度, 可以分组准备:

**Group A: LLM-First Companies (LLM 深度优先)**
- Together AI, Cohere, Character.ai, Mistral, Perplexity, Glean, Harvey AI, Sierra AI
- 侧重: Transformer 细节, LLM training/serving, RAG, alignment

**Group B: Search & Ranking (搜索排序优先)**
- Google, Amazon Search, Microsoft Bing, LinkedIn
- 侧重: Learning-to-Rank, retrieval, query understanding, large-scale ranking systems

**Group C: Marketplace & Dynamic Systems (市场/动态系统)**
- Uber, Airbnb, DoorDash, Instacart, Robinhood
- 侧重: Pricing, ETA, matching, causal inference, fraud detection

**Group D: Infra & Platform (基础设施)**
- Nvidia, Databricks, Scale AI
- 侧重: Distributed training, GPU optimization, data pipeline, MLOps

**Group E: Product ML (产品ML)**
- Netflix, Adobe, Roblox, Slack/Salesforce, Apple
- 侧重: RecSys, CV, on-device ML, product sense

---

## 11. 优先级 Triage 策略

### 11.1 优先级矩阵 (按投入产出比排序)

```
P0 (最高优先级, 覆盖所有公司):
├── ML System Design (90% 公司考)
├── Coding/Algorithms (95% 公司考)
├── Behavioral/STAR Stories (85% 公司考)
└── ML Fundamentals (Core: bias-variance, regularization, evaluation metrics)

P1 (高优先级, 覆盖大部分公司):
├── Transformer Architecture 深度理解
├── Recommender Systems 基础
├── Search/Retrieval 基础
├── LLM Training & Serving 基础
└── Feature Engineering & Feature Store

P2 (中优先级, 根据目标公司选择):
├── RAG Architecture 深度
├── Distributed Training (DeepSpeed, FSDP)
├── LLM Alignment (RLHF, DPO)
├── Marketplace ML (pricing, ETA, matching)
├── Ads ML (CTR/CVR prediction)
└── Causal Inference

P3 (选择性准备):
├── Computer Vision (if targeting Apple/Nvidia/Adobe/Roblox)
├── GPU Programming (if targeting Nvidia)
├── On-device ML (if targeting Apple)
├── Graph Neural Networks
├── Reinforcement Learning
└── 3D/Multimodal (if targeting Adobe/Roblox)
```

### 11.2 时间分配建议 (假设 6-8 周准备期)

| 模块 | 每周投入 | 总时间 | 策略 |
|------|---------|--------|------|
| Coding | 1-1.5h/天 | ~70h | 每天 2-3 题, 优先 Medium, 分 pattern 刷 |
| ML System Design | 1h/天 | ~50h | 每周完整练习 2-3 个 design, mock interview |
| ML Theory | 30min/天 | ~25h | Flash cards + 写 notes, 重推导 |
| LLM/DL 深度 | 1h/天 | ~50h | 读论文 + 实现 + 总结 |
| Behavioral | 30min/天 前2周 | ~7h | 写 STAR stories, 练习 |
| Domain Knowledge | 1h/天 | ~50h | 根据 target companies 选择性深入 |
| Mock Interviews | 2-3次/周 | ~20h | 与人对练, 录音回放 |

### 11.3 学习资源推荐

| 资源 | 覆盖模块 | 推荐度 |
|------|---------|--------|
| **Designing Machine Learning Systems** (Chip Huyen) | ML Sys Design | ★★★★★ |
| **Machine Learning System Design Interview** (Ali Aminian) | ML Sys Design | ★★★★★ |
| **NeetCode 150** / Blind 75 | Coding | ★★★★★ |
| **LeetCode** 公司标签题 | Coding | ★★★★★ |
| **Stanford CS229** notes | ML Theory | ★★★★ |
| **Stanford CS224N** | NLP/LLM | ★★★★ |
| **Andrej Karpathy: Let's build GPT** | Transformer | ★★★★★ |
| **Jay Alammar's Blog** (Illustrated Transformer 等) | DL Visualization | ★★★★ |
| **Eugene Yan's Blog** (RecSys, ML Systems) | RecSys / ML Sys | ★★★★ |
| **Made With ML** (Goku Mohandas) | Applied ML | ★★★★ |
| **Papers With Code** | SOTA tracking | ★★★★ |
| **Hugging Face Blog / Docs** | LLM 实践 | ★★★★ |
| **Pramp / Interviewing.io** | Mock Interviews | ★★★★★ |
| **Glassdoor / Blind** | 面经收集 | ★★★★ |

---

## 12. 每周学习计划模板

### Week 1-2: 基础强化

| 日 | 上午 (Coding) | 下午 (ML) | 晚上 (System Design) |
|---|-------------|----------|-------------------|
| 周一 | LeetCode: Array/String patterns ×3 | ML Theory: Linear models, bias-variance | 读 Chip Huyen Ch1-3 |
| 周二 | LeetCode: HashMap/Two Pointer ×3 | ML Theory: Tree models (GBDT, XGBoost) | ML Sys Design: Recommendation system |
| 周三 | LeetCode: BFS/DFS ×3 | ML Theory: Evaluation metrics deep dive | 读 Chip Huyen Ch4-6 |
| 周四 | LeetCode: Binary Search ×3 | ML Theory: Feature engineering | ML Sys Design: Search ranking |
| 周五 | LeetCode: DP ×3 | ML Theory: Loss functions, optimization | Mock Interview #1 |
| 周六 | LeetCode: Graph/Topo Sort ×3 | Transformer: 手推 attention, 实现 | ML Sys Design: Ad CTR prediction |
| 周日 | 复习本周错题 | 写 flash cards, 复习 | Behavioral: 写 STAR stories ×3 |

### Week 3-4: 深度拓展

| 重点 | 内容 |
|------|------|
| Coding | 转向公司标签题, 每天 2-3 题, 加入 ML Coding (手写算法) |
| ML Theory | 深入: SVM 推导, EM 算法, Bayesian inference, information theory |
| System Design | 每周 3 个完整 design: RecSys, Fraud detection, RAG system |
| DL/LLM | Transformer 细节, BERT/GPT 对比, position encoding, attention variants |
| Behavioral | 完善 8-10 个 STAR stories, 开始 mock interview behavioral rounds |

### Week 5-6: 专项攻克 + Mock

| 重点 | 内容 |
|------|------|
| Coding | Hard 题比例提升到 30%, 限时训练 |
| System Design | 针对 target companies 的特定 design (marketplace, LLM serving 等) |
| LLM 深度 | LLM training pipeline, RLHF/DPO, serving optimization, RAG 深度 |
| Domain | 根据公司分组深入 (e.g., LLM companies → alignment + serving) |
| Mock | 每周 3-4 次 mock (Coding + System Design + Behavioral 轮换) |

### Week 7-8: 冲刺 + 公司特化

| 重点 | 内容 |
|------|------|
| 面经 | 收集目标公司面经, 集中练习高频题 |
| 薄弱项 | 根据 mock 反馈补强薄弱环节 |
| 公司研究 | 深入研究每家公司的 ML blog, 了解他们的 tech stack 和 challenges |
| 模拟面试 | 模拟完整 onsite 流程 (4-5 轮连续) |
| 心理准备 | 调整作息, 保持状态 |

---

## 附录: 快速参考卡片

### A. ML System Design 常用 Trade-off 列表

| Trade-off | 左侧 | 右侧 | 如何取舍 |
|-----------|------|------|---------|
| Latency vs Throughput | 低延迟 (实时) | 高吞吐 (批量) | 看用户体验需求 |
| Accuracy vs Latency | 复杂模型 | 简单模型 | 分阶段: 重模型离线, 轻模型在线 |
| Freshness vs Cost | 实时更新 | 批量更新 | 根据数据变化速度决定 |
| Exploration vs Exploitation | 发现新内容 | 推荐已知好内容 | 用 bandit / epsilon-greedy |
| Precision vs Recall | 高精度 (少误报) | 高召回 (少漏报) | 看业务: spam→recall, 推荐→precision |
| Online vs Offline | 实时学习 | 离线批训练 | 看数据分布变化速度 |
| Global vs Personalized | 一个模型 | 每人一个 | Multi-task 折中 |
| Simple vs Complex | Logistic Regression | Deep Neural Network | 先 baseline, 再迭代 |

### B. 常被追问的面试 Follow-up 问题

- "How would you handle cold-start users/items?"
- "What if your data has significant label noise?"
- "How would you detect and handle data drift in production?"
- "How would you scale this to 10x the current traffic?"
- "What metrics would you use to evaluate this offline vs online?"
- "How would you ensure fairness in this system?"
- "What would be your v1 vs v2 vs v3 iteration plan?"
- "How would you debug a sudden drop in model performance?"
- "How would you handle a situation where offline metrics improve but online metrics don't?"
- "What are the failure modes of this system?"

### C. 必须能白板推导的公式

1. Logistic Regression 的 MLE → Cross-Entropy Loss 推导
2. Softmax 函数及其梯度
3. Backpropagation (链式法则在简单网络上的应用)
4. PCA 的推导 (最大化方差 → 特征值问题)
5. Bayes' Theorem 的实际应用 (spam filter, medical test)
6. Attention mechanism 的计算 (QKV → scaled dot-product → softmax → weighted sum)
7. A/B Test 的 sample size 计算
8. Bias-Variance 分解
9. Information Gain / Gini Impurity 的计算
10. Adam optimizer 的更新规则

---

> **使用说明**: 本框架设计为可迭代的活文档。建议:
> 1. 根据自己的 timeline 和 target companies 调整优先级
> 2. 每完成一个知识点打 ✅
> 3. 记录每次 mock interview 的反馈, 更新薄弱项
> 4. 补充公司面经和实际面试题到对应 section
> 5. 定期 review 和 update 自己的 STAR stories
