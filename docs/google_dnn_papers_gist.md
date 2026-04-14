# Google DNN / Recs & Search Papers — One-Page Gist

Talking-points cheatsheet for Google SWE III / ML interviews. Each entry: **What · Why-mattered · Architecture · Gotcha**. Not a deep dive — these are the 1-2 sentence hooks that show familiarity.

---

## 1. YouTube DNN (Covington et al., 2016)
- **What**: Two-stage recommender — candidate generation DNN + ranking DNN — for YouTube video recs.
- **Why mattered**: First large-scale industrial paper framing recs as two towers of deep nets instead of matrix factorization; defined the "retrieve then rank" playbook the industry still uses.
- **Architecture**: Candidate gen = watch embeddings + search embeddings + demographics → MLP → softmax over millions of videos (sampled); serves via ANN on learned user vector. Ranker = richer features (impression context, freshness, video-age-at-watch) → weighted-LR-style output for expected watch time.
- **Gotcha**: "Example age" feature (time since video upload) is critical — without it the model over-recommends old viral videos because the training distribution skews old. Predict expected watch time, not CTR, to avoid clickbait.

## 2. DSSM / Two-Tower (Huang et al., 2013; Google two-tower sampled softmax, Yi et al., 2019)
- **What**: Query tower + item tower producing embeddings whose dot product = relevance; trained with in-batch sampled softmax.
- **Why mattered**: Decouples query and item encoding so item embeddings can be precomputed and served via ANN (ScaNN/Faiss); the retrieval standard at Google/YouTube/Pinterest/etc.
- **Architecture**: Two independent MLPs (or transformers) → L2-normalize → dot product or cosine; loss = softmax over in-batch negatives with sampling bias correction `logQ(i)`.
- **Gotcha**: In-batch negatives are biased toward popular items (they appear in more batches). Without the `-log Q(i)` correction, the model under-retrieves head items; with it, you must estimate item frequency online. Also: can't represent query-item cross features — anything requiring interaction must go in the ranker.

## 3. Wide & Deep (Cheng et al., Google, 2016)
- **What**: Jointly trained linear ("wide") model with crossed categorical features + DNN ("deep") over embeddings; used in Google Play store recs.
- **Why mattered**: Canonical answer to "memorization vs generalization" — wide memorizes exceptions (e.g., specific app co-installs), deep generalizes via embeddings. Birthed the hybrid-architecture family.
- **Architecture**: Wide = logistic regression on hand-crafted feature crosses; Deep = embedding lookup → MLP; logits summed, joint SGD (FTRL for wide, AdaGrad for deep).
- **Gotcha**: The "wide" part still needs manual feature engineering of crosses — that's what DeepFM/DCN tried to eliminate. Joint training requires two optimizers; in practice teams replaced wide with DCN/xDeepFM to remove the manual crosses.

## 4. DeepFM (Guo et al., 2017)
- **What**: Factorization Machine + DNN sharing the same embedding layer; learns low-order (FM second-order interactions) and high-order (DNN) feature crosses end-to-end.
- **Why mattered**: Removed the hand-crafted-crosses dependency of Wide & Deep; became a standard CTR baseline.
- **Architecture**: Shared embedding `e_i` per field; FM part = sum of `<e_i, e_j>` pairs; DNN part = concat(e) → MLP; sigmoid(FM + DNN + linear).
- **Gotcha**: FM only captures order-2 interactions; if your signal is deeply nonlinear across many fields, DNN carries the load and the FM term becomes cosmetic. Memory explodes with many high-cardinality fields (each field needs its own embedding table).

## 5. DCN / DCN-V2 (Wang et al., Google, 2017 / 2020)
- **What**: Deep & Cross Network — explicit high-order feature-cross layers (`x_{l+1} = x_0 · (w^T x_l) + b + x_l`) stacked in parallel with a DNN.
- **Why mattered**: Provides a parameter-efficient, bounded-degree cross structure; DCN-V2 replaced the vector `w` with a low-rank matrix, making it expressive enough to deploy at Google scale (ads, YouTube).
- **Architecture**: Cross network produces degree-`L` polynomial interactions of input; parallel or stacked with DNN tower; concat → logit.
- **Gotcha**: Original DCN's rank-1 cross is too restrictive (one scalar weighting per pair); always use DCN-V2 in practice. Cross layers are sensitive to input scaling — normalize/batch-norm inputs or training diverges.

## 6. SASRec / BERT4Rec (Kang & McAuley 2018 / Sun et al. 2019)
- **What**: Sequential recs modeled as next-item prediction over user's interaction history with self-attention (causal = SASRec; bidirectional + masked-item = BERT4Rec).
- **Why mattered**: Brought transformer sequence modeling to recs; outperformed GRU4Rec/Caser and became the standard for session-based / sequential retrieval (YouTube, TikTok, e-commerce).
- **Architecture**: Item-ID embedding + positional embedding → stacked self-attention blocks → predict next item via dot product with item-embedding matrix.
- **Gotcha**: Item vocabulary softmax blows up — use sampled softmax or in-batch negatives. Sequence length is capped (e.g., last 50 items); very active users get truncated, very inactive users get padded — both hurt quality. Cold-start items have no embedding; need side-info fusion.

## 7. PinSAGE (Ying et al., Pinterest × Stanford, 2018)
- **What**: GraphSAGE applied to Pinterest's 3B-node pin-board graph for learning pin embeddings used in retrieval.
- **Why mattered**: Showed GNNs can scale to web-scale graphs via random-walk-based neighborhood sampling and MapReduce inference; embeddings served Related Pins and Home Feed.
- **Architecture**: For each pin, sample short random walks to define neighborhood; aggregate neighbor features (importance-weighted by visit counts) through K GraphSAGE layers → pin embedding. Trained with max-margin loss against hard negatives.
- **Gotcha**: Random-walk neighborhood sampling is the critical trick — uniform-neighbor sampling doesn't scale and yields noisy aggregations. Hard-negative mining (items slightly related but wrong) is essential; random negatives are too easy and the loss collapses.

## 8. Item2Vec / Airbnb Embeddings (Barkan 2016 / Grbovic & Cheng 2018)
- **What**: Word2Vec-style skip-gram applied to sessions of items (co-occurring pins, listing bookings, songs).
- **Why mattered**: Cheap, powerful baseline for item similarity; Airbnb's listing embeddings with booked-listing as global context became the textbook case study for domain-specific tweaks to skip-gram.
- **Architecture**: Treat user session as a sentence, items as words; train skip-gram with negative sampling. Airbnb added: booking as "global context" added to every window; market-level negative sampling (negatives from same market as positive).
- **Gotcha**: Cold-start handled by averaging type/location embeddings — a hack that works surprisingly well. Pure co-occurrence embeddings don't capture content — fuse with content features (image, text) for new items.

## 9. MoE Ranking / Multi-Gate MoE (MMoE, Ma et al., Google, 2018)
- **What**: Multi-task learning with shared expert sub-networks and per-task gating — each task picks a weighted blend of experts.
- **Why mattered**: Deployed in YouTube ranking (engagement + satisfaction) and Ads; solved the multi-task seesaw where one task regresses when you add another.
- **Architecture**: Shared input → N expert MLPs; per-task gate (softmax over experts) → task-specific weighted sum → task tower → task loss. Total loss = weighted sum of task losses.
- **Gotcha**: Gates collapse — one expert ends up dominating all tasks if tasks are correlated. Add gate entropy regularization or use PLE (Progressive Layered Extraction) which separates task-specific vs shared experts explicitly. Also: task-loss weighting is a major hyperparameter; uncertainty-weighted loss (Kendall 2018) helps.

## 10. Contrastive Pretraining for Recs (CLIP-style / SimCSE / SSL4Rec)
- **What**: Self-supervised pretraining on item features (image+text for visual recs, augmented sequences for sequential recs) before supervised fine-tuning.
- **Why mattered**: Addresses cold-start and long-tail items by learning content-grounded embeddings that don't need interaction data. CLIP-style dual encoders power multi-modal search (Google Search, Pinterest Lens).
- **Architecture**: Dual encoder (image + text or sequence-aug-A + sequence-aug-B) → InfoNCE loss with in-batch negatives; fine-tune with supervised recs loss.
- **Gotcha**: Pretraining objective must align with downstream — pretraining on image-text alignment then fine-tuning on click doesn't always transfer (distributional shift). Temperature `τ` in InfoNCE is load-bearing; wrong scale and gradients vanish or explode.

---

## Quick Cross-Cutting Talking Points
- **Retrieval vs ranking split**: YouTube DNN defined it. Retrieval = two-tower + ANN (can't use query-item crosses); ranking = full feature crosses + MMoE heads.
- **Feature crosses evolution**: Hand-crafted (Wide&Deep) → FM-learned (DeepFM) → explicit polynomial (DCN-V2) → attention-learned (AutoInt, transformers).
- **Cold-start playbook**: Content embeddings (PinSAGE, CLIP), side-info fusion (Airbnb type/location), meta-learning (MeLU), or fallback to popularity-by-segment.
- **Negative sampling**: In-batch (cheap, biased — needs logQ correction) → hard negatives (PinSAGE) → mixed (random + hard) — hardest lever for retrieval quality.
- **Multi-task**: Shared-bottom → MMoE → PLE. Gate regularization and task-loss weighting are the operational pain points.
