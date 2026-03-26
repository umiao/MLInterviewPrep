# NLP: Text Classification Methods

## Overview

Text classification -- assigning a label (spam, sentiment, topic) to a document -- is the backbone NLP task and a frequent MLE interview topic. The field evolved from handcrafted features + classical classifiers (1960s--2010s) to end-to-end deep learning (2013+) to pre-trained language models (2018+). Understanding this progression, the trade-offs at each stage, and when to reach for which approach is essential for system design and modeling questions.

## Core Concepts

### The Text Classification Pipeline

Every text classifier follows the same high-level pattern:

```
Raw Text -> Preprocessing -> Feature Representation -> Classifier -> Label
```

**Preprocessing**: word segmentation, data cleaning (lowercasing, stop-word removal, stemming/lemmatization), statistics (vocabulary building, frequency counts).

The critical design choice is the feature representation: how do you convert variable-length text into a fixed-length numeric vector the classifier can consume?

### Feature Representations: Count-Based

**Bag-of-Words (BOW)**:
Represent each document as a vector of size $|V|$ (vocabulary size). The $i$-th element is the count of the $i$-th word in the document. Simple and effective, but loses word order entirely.

**N-grams**:
Extend BOW by considering adjacent word sequences. A bigram model captures pairs like "not good" that BOW treats as two independent positive/negative words. Uses a Markov assumption: a word depends only on the preceding $N-1$ words. Vocabulary grows as $O(|V|^N)$, so in practice $N \leq 3$.

**TF-IDF (Term Frequency -- Inverse Document Frequency)**:

$$
\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \text{IDF}(t)
$$

where:

$$
\text{TF}(t, d) = \frac{\text{count of } t \text{ in document } d}{\text{total words in } d}, \quad \text{IDF}(t) = \log \frac{N}{|\{d : t \in d\}|}
$$

$N$ = total number of documents. The importance of a word increases with its frequency in a document but decreases with its frequency across the corpus. This down-weights common words ("the", "is") and up-weights discriminative terms.

**Limitations of count-based features**:
- No semantic similarity: "good" and "great" are completely unrelated dimensions
- High dimensionality: vocabulary size can be $10^5$--$10^6$
- Sparse vectors: most entries are zero

### Feature Representations: Dense Embeddings

**Word2Vec** (Mikolov et al., 2013):
Maps each word to a dense, fixed-length vector ($d \approx 100$--$300$) trained to predict context from local windows. Two architectures:

- **CBOW** (Continuous Bag-of-Words): predicts the center word from its surrounding context words. Faster to train, better for frequent words.
- **Skip-gram**: predicts context words from the center word. Better for rare words and small datasets.

Training objective (Skip-gram with negative sampling):

$$
J = \log \sigma(v_c^\top v_w) + \sum_{i=1}^{k} \mathbb{E}_{w_i \sim P_n(w)} \left[ \log \sigma(-v_{w_i}^\top v_w) \right]
$$

Key property: learned vectors capture semantic analogies. $v_{\text{king}} - v_{\text{man}} + v_{\text{woman}} \approx v_{\text{queen}}$.

**GloVe** (Pennington et al., 2014):
Builds a global word co-occurrence matrix $X$ from the entire corpus, then factorizes it. The objective learns vectors such that their dot product approximates the log co-occurrence:

$$
J = \sum_{i,j=1}^{|V|} f(X_{ij}) \left( v_i^\top v_j + b_i + b_j - \log X_{ij} \right)^2
$$

where $f(X_{ij})$ is a weighting function that caps the influence of very frequent co-occurrences.

**Word2Vec vs GloVe**:

| Aspect | Word2Vec | GloVe |
|--------|----------|-------|
| Training signal | Local context windows | Global co-occurrence matrix |
| Approach | Predictive (neural network) | Count-based (matrix factorization) |
| Strengths | Scales well, captures syntax | Captures global statistics, stable |
| Limitation | Both produce a single fixed vector per word -- no polysemy handling |

**Critical limitation of static embeddings**: the word "bank" gets the same vector whether it means "river bank" or "financial bank." This motivates contextual embeddings.

### Classical Classifiers for Text

Once text is represented as a vector, any classifier can be applied. The most common for text:

**Naive Bayes (NB)**:
Assumes feature independence given the class. Despite this unrealistic assumption, works surprisingly well for text -- especially with small data. Fast to train, handles high-dimensional sparse features naturally.

$$
\hat{y} = \arg\max_k \; P(y=k) \prod_{j=1}^{D} P(x_j \mid y=k)
$$

Multinomial NB is the standard choice for text (word counts as features).

**Support Vector Machine (SVM)**:
Finds the maximum-margin hyperplane separating classes. Excels in high-dimensional spaces (large vocabulary). With a linear kernel and TF-IDF features, SVM was the go-to text classifier before deep learning. Handles sparse features efficiently.

**K-Nearest Neighbors (KNN)**:
Classifies by majority vote of $k$ nearest training examples. Simple but slow at inference ($O(n)$ per query). Weighted variants (NWKNN) address class imbalance by upweighting neighbors from rare classes.

**Decision Trees / Ensembles**:
Trees are interpretable but lack generalization for text. Random Forest and boosting ensembles (AdaBoost, XGBoost) improve performance but are rarely the first choice for raw text data -- they work better when combined with engineered features.

| Classifier | Strengths | Weaknesses | Best For |
|-----------|-----------|------------|----------|
| Naive Bayes | Fast, small data, probabilistic | Independence assumption, poor with correlated features | Spam detection, baseline |
| SVM | High-dim, robust, strong with TF-IDF | Slow to train on large data, needs feature engineering | Medium-size text, linear separability |
| KNN | Simple, no training | Slow inference, sensitive to $k$ and distance metric | Few classes, small data |
| Ensembles | Strong with engineered features | Need structured features, not end-to-end | Tabular features from text |

### Deep Learning: Sequence Models

Deep learning models learn feature extraction and classification jointly, eliminating manual feature engineering.

**Recurrent Neural Networks (RNN)**:
Process text sequentially, maintaining a hidden state that summarizes information seen so far:

$$
h_t = \tanh(W_h h_{t-1} + W_x x_t + b)
$$

The final hidden state (or a pooled combination) serves as the document representation for classification. RNNs naturally handle variable-length input and capture word order.

**Limitations**: sequential processing prevents parallelization (slow training); later tokens dominate the hidden state (biased toward recent words); vanilla RNNs struggle with long-range dependencies due to vanishing gradients.

**LSTM / GRU**: Gating mechanisms (forget gate, input gate, output gate) allow selective memory retention, partially alleviating the vanishing gradient problem. Bidirectional variants process text in both directions to capture full context.

**Convolutional Neural Networks (CNN)**:
Apply 1D convolution filters over word embedding sequences. Each filter detects a local n-gram pattern (e.g., "not good", "very impressive"). Multiple filter sizes capture different n-gram lengths.

- Advantages: parallel computation (fast), excellent at capturing local patterns
- Disadvantage: limited receptive field for global dependencies
- Can operate at character-level (robust to misspellings/morphology) or word-level

### Deep Learning: Attention and Transformers

**Self-Attention Mechanism**:
Computes a weighted combination of all positions in the input, allowing each word to attend to every other word regardless of distance:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

This solves the long-range dependency problem of RNNs while enabling full parallelization.

**Transformer Architecture**:
Stacks self-attention layers with feed-forward networks, position encodings, and residual connections. The encoder processes the full input bidirectionally; the decoder generates output autoregressively. For classification, typically the encoder output (e.g., [CLS] token representation) is fed to a classifier head.

Key advantages over RNNs:
- Fully parallelizable (no sequential bottleneck)
- Captures global dependencies via attention
- Scales to very long sequences with appropriate attention variants

### Pre-trained Language Models

The paradigm shift: pre-train a large model on massive unlabeled text, then fine-tune on the target task with a small labeled dataset. This is transfer learning for NLP.

**ELMo** (Embeddings from Language Models, 2018):
Trains a bidirectional LSTM language model. Produces context-dependent word embeddings by combining all LSTM layer outputs with learned weights. Same word gets different vectors in different contexts. Architecture: LSTM-based (not Transformer).

**GPT** (Generative Pre-trained Transformer, 2018):
Autoregressive (left-to-right) Transformer decoder. Pre-trains on next-token prediction. Fine-tunes by adding a classification head. Unidirectional -- each token can only attend to previous tokens.

**BERT** (Bidirectional Encoder Representations from Transformers, 2019):
Transformer encoder pre-trained with two objectives:
1. **MLM** (Masked Language Modeling): randomly mask 15% of tokens, predict the masked tokens from context (bidirectional)
2. **NSP** (Next Sentence Prediction): predict whether two sentences are consecutive (later shown to be less important)

For classification: take the [CLS] token output, add a linear layer, fine-tune on labeled data.

**Variants**:
- **SpanBERT**: masks contiguous spans instead of random tokens; uses Span Boundary Objective (SBO) to predict span content from boundary tokens; removes NSP task
- **BART**: sequence-to-sequence denoising autoencoder; introduces noise (token masking, sentence permutation, deletion) and reconstructs the original; good for generation tasks

### Traditional vs Deep Learning Trade-offs

| Factor | Traditional (BOW/TF-IDF + Classifier) | Deep Learning (RNN/CNN/Transformer) |
|--------|---------------------------------------|-------------------------------------|
| Data requirement | Hundreds--thousands of samples | Thousands--millions of samples |
| Training speed | Minutes | Hours--days (pre-training: weeks) |
| Interpretability | High (feature weights are meaningful) | Low (black box) |
| Feature engineering | Required (critical for performance) | Learned automatically |
| Accuracy (large data) | Good baseline, plateaus | State-of-the-art |
| Compute cost | CPU sufficient | GPU/TPU needed |
| Domain adaptation | Requires new features | Fine-tune pre-trained model |

**When NOT to use a transformer**: (1) very small labeled dataset with no domain-similar pre-trained model, (2) strict latency/memory constraints, (3) when interpretability is required, (4) when a simple TF-IDF + logistic regression baseline already meets the accuracy threshold.

## Implementation

```python
# TF-IDF + SVM baseline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=50000, ngram_range=(1, 2))),
    ("clf", LinearSVC(C=1.0)),
])
pipeline.fit(train_texts, train_labels)
predictions = pipeline.predict(test_texts)

# BERT fine-tuning (HuggingFace)
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=num_classes
)

def tokenize(batch):
    return tokenizer(batch["text"], padding=True, truncation=True)

train_dataset = train_dataset.map(tokenize, batched=True)
trainer = Trainer(
    model=model,
    args=TrainingArguments(output_dir="./results", num_train_epochs=3),
    train_dataset=train_dataset,
)
trainer.train()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| "Design a text classification system" | System design round | Start with requirements (latency, accuracy, data size), propose TF-IDF baseline, iterate to BERT if needed |
| "Compare Word2Vec vs BERT embeddings" | Modeling knowledge | Word2Vec: static, one vector per word, no context. BERT: contextual, different vectors per usage. BERT captures polysemy |
| "When would you NOT use a transformer?" | Practical trade-offs | Small data, strict latency, interpretability needed, or baseline already sufficient |
| "TF-IDF vs learned embeddings" | Feature engineering | TF-IDF: sparse, interpretable, no training needed. Embeddings: dense, semantic similarity, need training data |
| "RNN vs CNN for text" | Architecture choice | RNN: sequential, good for order-dependent tasks. CNN: parallel, good for local pattern detection. Transformer beats both |
| "How does BERT handle polysemy?" | NLP fundamentals | Bidirectional self-attention produces different representations for "bank" in "river bank" vs "bank account" |
| "Walk through the evolution of text features" | Breadth question | BOW -> N-gram -> TF-IDF -> Word2Vec/GloVe -> ELMo -> GPT/BERT. Each step adds context awareness |

### Common Interview Questions

- [ ] Explain TF-IDF and why IDF is needed
- [ ] What is the difference between CBOW and Skip-gram?
- [ ] How does self-attention differ from RNN hidden states?
- [ ] Why is BERT bidirectional while GPT is not?
- [ ] What are the pre-training objectives of BERT?
- [ ] How would you design a text classifier with 500 labeled examples?
- [ ] When would Naive Bayes outperform a deep learning model?
- [ ] What is the computational complexity of self-attention?

## Comparisons

### Embedding Methods

| Aspect | BOW / TF-IDF | Word2Vec / GloVe | ELMo | BERT |
|--------|-------------|------------------|------|------|
| Vector type | Sparse, high-dim | Dense, static | Dense, contextual | Dense, contextual |
| Context-aware | No | No (one vector per word) | Yes (biLSTM layers) | Yes (self-attention) |
| Training data | Target corpus only | Unlabeled corpus | Unlabeled corpus | Unlabeled corpus |
| Polysemy handling | None | None | Partial (LSTM context) | Full (bidirectional attention) |
| Dimensionality | $|V|$ (10K--100K) | 100--300 | 1024 | 768 (base) / 1024 (large) |
| Pre-trained available | N/A | Yes (Google News, Common Crawl) | Yes (allennlp) | Yes (HuggingFace) |

### Model Architectures for Text Classification

| Aspect | Naive Bayes | SVM + TF-IDF | CNN | RNN/LSTM | Transformer/BERT |
|--------|-------------|-------------|-----|----------|-----------------|
| Data efficiency | High | High | Medium | Medium | Low (pre-train) / High (fine-tune) |
| Training speed | Fast | Fast | Medium | Slow (sequential) | Slow (pre-train) / Medium (fine-tune) |
| Inference speed | Fast | Fast | Fast | Slow | Medium |
| Long-range dependencies | None | None | Limited (filter size) | Yes (with LSTM) | Full (self-attention) |
| Feature engineering | Required | Required | Minimal | Minimal | None (end-to-end) |
| State-of-the-art accuracy | No | No | Sometimes | Sometimes | Yes |

### When to Use What

| Scenario | Recommended Approach | Why |
|----------|---------------------|-----|
| < 1K labeled samples, no compute | TF-IDF + Naive Bayes or SVM | Data-efficient, no GPU needed |
| 1K--10K samples, domain-specific | Fine-tune BERT (or distilled variant) | Transfer learning compensates for small data |
| 10K+ samples, latency-critical | TF-IDF + logistic regression or distilled model | Sub-millisecond inference |
| Multilabel classification | BERT with sigmoid outputs | Handles label co-occurrence naturally |
| Real-time classification at scale | Lightweight model (TF-IDF + LR) or ONNX-exported BERT | Production latency constraints |
| Interpretability required | TF-IDF + linear model | Feature weights are directly interpretable |

## Key Takeaways

- [ ] Text classification evolved through three eras: count-based features (BOW, TF-IDF), dense embeddings (Word2Vec, GloVe), and pre-trained language models (BERT, GPT)
- [ ] TF-IDF remains a strong baseline -- always start here before reaching for deep learning
- [ ] Word2Vec (CBOW/Skip-gram) and GloVe produce static embeddings; the same word always gets the same vector regardless of context
- [ ] BERT's bidirectional self-attention produces contextual embeddings that handle polysemy, making it the default choice for accuracy
- [ ] The pre-train then fine-tune paradigm (transfer learning) is the key insight: massive unlabeled data for representation learning, small labeled data for task adaptation
- [ ] RNNs are sequential and biased toward recent tokens; CNNs capture local patterns efficiently; Transformers capture global dependencies with full parallelism
- [ ] For interview system design: start with requirements, propose a simple baseline (TF-IDF + SVM), discuss when and why to upgrade to BERT
- [ ] Practical trade-offs matter: Naive Bayes with 100 samples can beat BERT with 100 samples; BERT with 10K samples beats everything classical
