# Uber MLE -- BPS (Behavioral + Problem Solving) Prep Materials

> **Stage**: BPS Screen (after Recruiter Screen)
>
> **Format**: 1hr on HackerRank with screen share. Combines coding, D&A (Design & Architecture), and ML fundamentals.
>
> **Recruiter-confirmed structure**: 5min intro, 40-50min coding + D&A, 5min Q&A.

---

## 1. BPS Format Overview

The BPS replaces the previous 2-round phone screen. It is a single 1hr session that evaluates coding ability, system thinking, and communication together.

| Segment | Duration | Focus |
|---------|----------|-------|
| Intro & warm-up | ~5 min | Brief self-intro, interviewer introduces the format |
| Coding + D&A | ~40-50 min | Algorithm problem(s) on HackerRank + design/architecture discussion |
| Q&A | ~5 min | Your questions for the interviewer |

**What Uber evaluates in BPS:**
- **Technical competence** -- Can you solve algorithm problems cleanly under time pressure?
- **Communication** -- Do you explain your thinking? Can you drive the conversation?
- **Design & Architecture** -- Can you discuss a complex past project with a high-level diagram?
- **ML fundamentals** -- KNN, bias-variance, model evaluation basics

**After BPS, the pipeline is:**

| Stage | Focus |
|-------|-------|
| Recruiter Screen | Background fit, motivation, logistics |
| **BPS** | Coding + D&A + ML fundamentals (YOU ARE HERE) |
| Virtual Onsite (4 rounds) | Coding & Data, Applied ML, System Design, Behavioral |

---

## 2. Time Allocation Strategy (1hr)

> The biggest mistake is spending the entire hour coding. Budget your time.

| Phase | Time | What to do |
|-------|------|------------|
| **Intro** | 0:00-0:05 | 60-sec self-intro. Interviewer sets context. |
| **Problem 1** | 0:05-0:25 | Clarify -> approach -> code -> test. ~20 min. |
| **Follow-ups / Problem 2** | 0:25-0:40 | Variants, optimization, or a second problem. |
| **D&A discussion** | 0:40-0:50 | Complex past project walkthrough with diagram. |
| **ML fundamentals** | 0:50-0:55 | KNN, metrics, bias-variance quick-fire. |
| **Your questions** | 0:55-1:00 | 1-2 prepared reverse questions. |

**Notes from 1p3a reports:**
- Some BPS sessions are heavily coding-weighted (two LC problems + follow-ups)
- Others mix a case study (UberEats metrics, feature evaluation) with lighter coding (pandas, fizzbuzz)
- The D&A portion may be woven into coding discussion or come separately
- Interviewer may start with a brief resume chat before the first problem

---

## 3. Problem-Solving Approach

**Do NOT jump straight into coding.** The interviewer evaluates your thought process.

1. **Clarify the objective** -- Restate the problem, confirm constraints and edge cases
2. **Explore multiple approaches** -- Discuss 2-3 possible solutions at a high level
3. **Analyze tradeoffs** -- Compare time/space complexity, readability, edge case handling
4. **Propose and justify your choice** -- Explain why this approach fits best
5. **Code it cleanly** -- Implement with clear structure and meaningful variable names
6. **Test proactively** -- Walk through your own test cases before running

**Anticipate and lead the cadence.** Don't wait for the interviewer to prompt each step -- drive the conversation forward.

---

## 4. Problem Categorization by Pattern

Problems from Uber BPS interviews, organized by algorithm pattern for targeted practice.

### BFS / DFS (most frequent)

| Problem | Pattern | Key idea |
|---------|---------|----------|
| LC 994 (Rotting Oranges) | Multi-source BFS | Enqueue all rotten cells, BFS layer-by-layer |
| LC 1020 (Number of Enclaves) | Border BFS/DFS | Start from border, mark reachable land |
| LC 1197 (Min Knight Moves) | BFS on grid | Variant: finite board size n |
| LC 230 (Kth Smallest in BST) | Inorder traversal | Iterative + recursive; variant: kth largest |
| LC 337 (House Robber III) | Tree DP (DFS) | rob/not-rob states per node |
| LC 549 (Longest Consecutive Seq II) | Tree DFS | Track increasing/decreasing lengths |
| LC 987 (Vertical Order Traversal) | BFS/DFS + column tracking | Sort by column, then row, then value |
| LC 2791 (Palindrome Paths in Tree) | DFS + bitmask XOR | Prefix XOR on path, count palindrome-formable |
| 2D Grid Nearest Exit | BFS | Standard BFS from start to boundary |
| Lock Combination | BFS on state space | Minimum steps to unlock |
| City Graph BFS Sort | BFS + sorting | Sort by distance, tie-break by index |

### Union Find

| Problem | Pattern | Key idea |
|---------|---------|----------|
| LC 547 (Number of Provinces) | Union Find / DFS | Connected components in adjacency matrix |
| LC 1697 (Edge Length Limited Paths) | Offline sort + UF | Sort queries and edges together |
| Rider Connection Log | UF with timestamps | Earliest time all riders connected; block events need BFS rebuild |

### Binary Search

| Problem | Pattern | Key idea |
|---------|---------|----------|
| LC 977 (Squares of Sorted Array) | Two-pointer (not BS, but sorted array) | Compare absolute values from both ends |
| LC 981 (Time Based KV Store) | Binary search on timestamps | Follow-ups: 1M+ req/sec, thread safety |
| Purchase Optimization | Prefix sum + BS | Max items purchasable given budget |
| Elevator Binary Search | Array jump + BS | Minimum starting index |
| Max Throughput with Budget | BS on target | Binary search the answer |

### Dynamic Programming

| Problem | Pattern | Key idea |
|---------|---------|----------|
| Jump Game Prime Variant | DP + prime sieve | Jump +1 or +prime ending in 3 |
| LC 337 (House Robber III) | Tree DP | rob/not-rob per node |
| Non-overlapping Interval Triples | Sorting + DP/greedy | Count valid triple groups |
| Balanced Permutation | Track min/max position | Check subarray permutations as k increases |

### Monotonic Stack

| Problem | Pattern | Key idea |
|---------|---------|----------|
| Price Discount | Monotonic stack | Next smaller element for each price |

### Sliding Window

| Problem | Pattern | Key idea |
|---------|---------|----------|
| Shortest Subarray with k Distinct | Two-pointer + counter | Standard sliding window minimum |

### OOD (Object-Oriented Design)

| Problem | Pattern | Key idea |
|---------|---------|----------|
| Cart & Pricing Engine | Strategy pattern | Item customization, surge, discounts, promos |
| Parking Lot | Class hierarchy | Motorcycle vs regular spot constraints |
| Customer Revenue & Referral | Tree aggregation | Revenue propagation up referral tree |

### Greedy / Math

| Problem | Pattern | Key idea |
|---------|---------|----------|
| Min Operations n->0 | Binary/NAF analysis | n%4==1 -> -1, n%4==3 -> +1 |
| Task Assignment to 2 People | Sort by reward diff | Greedy assignment of k tasks |
| Elevator/Stairs Energy | BS on split point | Minimize time difference |

---

## 5. D&A (Design & Architecture) Prep

The D&A segment asks you to discuss a complex past project. The interviewer wants to see you draw a high-level diagram and explain the system flow.

### What to prepare

Pick 1-2 projects you can explain end-to-end in 8-10 minutes with a diagram.

**Project 1: Ranking-as-Allocation Framework**

Diagram elements:
- Query -> Retrieval (embedding-based / rule-based) -> Candidate set
- Candidate set -> Pointwise scoring -> Session-level allocation layer
- Allocation layer: multi-objective constraints (exposure, conversion, risk)
- Late-stage re-ranking with MoE architecture
- A/B experiment framework with diagnostic tooling

Key talking points:
- Why session-level allocation instead of pointwise ranking
- Multi-objective tradeoffs: how to balance competing business metrics
- MoE architecture: when and why it outperforms single model
- Production considerations: latency budget, gradual rollout

**Project 2: LLM-Based Evaluation Pipeline**

Diagram elements:
- Data pipeline: sample queries -> retrieve search results -> pair with labels
- LLM inference: prompt engineering -> calibration -> batch async serving
- Evaluation: agreement metrics vs human judges -> dashboard
- Adoption: org-wide integration for Search & Ads experiments

Key talking points:
- Why LLM-as-judge: cost reduction (94%), latency reduction (90%)
- Calibration methodology: how to ensure reliability
- Failure modes and guardrails
- How this accelerates experiment velocity

### D&A tips from 1p3a reports

- Interviewer may ask you to draw a high-level diagram on the HackerRank shared editor
- Expect follow-up questions like "Why did you choose X over Y?" and "What would you do differently?"
- One report noted the interviewer was not satisfied with "it took two weeks to build" -- emphasize WHY decisions were complex, not just time spent
- "Have more conversation, don't just give answers" -- engage with the interviewer's questions

---

## 6. ML Fundamentals Review

Recruiter explicitly mentions KNN and ML fundamentals. Be prepared for quick-fire questions.

### KNN (K-Nearest Neighbors)

| Topic | Key points |
|-------|-----------|
| Algorithm | Store all training data. For new point: compute distances to all points, find k nearest, vote (classification) or average (regression). |
| Distance metrics | Euclidean (L2), Manhattan (L1), Cosine similarity. Choice depends on data. |
| k selection | Small k = overfit (noisy), large k = underfit (too smooth). Use cross-validation. |
| Weighted KNN | Weight by 1/distance -- closer neighbors have more influence. |
| Optimization | KD-tree (low dim), Ball tree (higher dim), LSH (approximate, very high dim). |
| Curse of dimensionality | As dimensions increase, distances converge -- KNN becomes meaningless. |
| Feature scaling | Must normalize/standardize features; KNN is distance-sensitive. |
| Categorical features | Hamming distance, or encode then use standard distance. |
| Pros/Cons | No training phase, interpretable, non-parametric. Slow at inference, memory-heavy, sensitive to irrelevant features. |

### Core ML Concepts

| Concept | Quick answer |
|---------|-------------|
| Bias-variance tradeoff | High bias = underfitting (model too simple). High variance = overfitting (model too complex). Goal: minimize total error = bias^2 + variance + irreducible noise. |
| Overfitting | Model memorizes training data, fails on unseen data. Signs: train acc >> val acc. Remedies: more data, regularization, simpler model, dropout, early stopping. |
| Cross-validation | k-fold: split data into k folds, train on k-1, validate on 1, rotate. Gives robust estimate of generalization. Stratified CV for imbalanced classes. |
| Precision vs Recall | Precision = TP/(TP+FP) -- of predicted positives, how many correct? Recall = TP/(TP+FN) -- of actual positives, how many found? F1 = harmonic mean. |
| ROC-AUC | Plot TPR vs FPR at different thresholds. AUC = probability that model ranks random positive above random negative. 0.5 = random, 1.0 = perfect. |
| Regularization | L1 (Lasso): sparse features, feature selection. L2 (Ridge): small weights, prevents large coefficients. Elastic Net: both. |
| Gradient descent | Update weights in direction of negative gradient. Learning rate controls step size. Variants: SGD, mini-batch, Adam (adaptive). |
| Decision trees | Split on feature that maximizes information gain (ID3/C4.5) or Gini impurity reduction (CART). Prone to overfitting -- use pruning or ensembles. |
| Random Forest | Bagging + feature subsampling. Reduces variance vs single tree. |
| Boosting | Sequential ensemble: each model corrects errors of previous. AdaBoost, GBDT, XGBoost. Reduces bias. |

---

## 7. HackerRank Tips

The BPS coding is done on HackerRank with screen share.

### Before the interview

- [ ] Familiarize yourself with HackerRank IDE (test it at hackerrank.com/test)
- [ ] Set your preferred language to Python 3
- [ ] Know the keyboard shortcuts: Run (Ctrl+Enter), Submit
- [ ] Practice writing code without local IDE autocomplete

### During the interview

| Tip | Why |
|-----|-----|
| **Run your code frequently** | 1p3a reports confirm interviewers expect you to run and debug. Don't submit untested code. |
| **Write your own test cases** | Add edge cases in the custom input box. Shows thoroughness. |
| **Use print statements for debugging** | If stuck, add prints to trace execution. Remove before final submission. |
| **Comment your approach first** | Write pseudocode in comments, then fill in code. Interviewer sees your thought process. |
| **Screen share etiquette** | Close unnecessary tabs. Keep only HackerRank + blank notepad. No peeking at solutions. |
| **Talk while coding** | Narrate what you're doing: "Now I'm handling the edge case where..." |
| **Don't panic on follow-ups** | Follow-ups are expected (variant, optimization, complexity). Think out loud. |
| **Time awareness** | If stuck for >5 min, discuss what you've tried and ask for a hint. Better than silent struggle. |

### Common HackerRank gotchas

- Input parsing: use `input().split()` or `sys.stdin` for large inputs
- Python recursion limit: `sys.setrecursionlimit(10000)` for DFS on large graphs
- Output format: match expected output exactly (trailing newlines, spaces)
- Collections available: `from collections import defaultdict, deque, Counter`
- Heapq: `import heapq` -- Python only has min-heap; negate values for max-heap

---

## 8. Content Areas Summary

| Area | Details | Priority |
|------|---------|----------|
| **BFS/DFS** | Graph traversal, tree problems, grid search -- most frequent pattern in Uber BPS | Critical |
| **Union Find** | Connected components, offline queries with sorted edges | High |
| **Binary Search** | Search on answer, time-based lookups, sorted array manipulation | High |
| **Dynamic Programming** | Tree DP, jump game variants, interval problems | High |
| **OOD** | Cart/pricing, parking lot, referral tree -- clean class design | Medium-High |
| **ML fundamentals** | KNN implementation, bias-variance, metrics, CV | Medium-High |
| **D&A project discussion** | High-level diagram, trade-off reasoning, design decisions | Medium-High |
| **Syntax fluency** | Write clean Python without IDE autocomplete; interviewer notices hesitation | High |
| **Edge/corner cases** | Proactively identify: empty input, single element, overflow, duplicates | High |
| **Complexity analysis** | State time and space complexity for every approach discussed | High |

---

## 9. BPS Checklist

### Coding prep
- [ ] Practice 5+ problems from each high-frequency pattern (BFS/DFS, UF, BS, DP)
- [ ] Solve at least 3 problems on HackerRank specifically (not local IDE)
- [ ] Practice 2-3 OOD problems (class design, strategy pattern)
- [ ] Time yourself: 20 min per medium, 25 min per medium-hard

### ML prep
- [ ] Implement KNN from scratch (distance metrics, k selection, weighted)
- [ ] Review ANN concepts (LSH, KD-tree, ball tree)
- [ ] Rapid-fire: bias-variance, precision-recall, ROC-AUC, regularization

### D&A prep
- [ ] Prepare 2 project walkthroughs with diagrams (8-10 min each)
- [ ] Practice explaining trade-off decisions out loud
- [ ] Prepare for "why X over Y" follow-ups

### Communication prep
- [ ] Practice talking through solutions aloud while coding
- [ ] Do at least 2 mock interviews with the "clarify -> explore -> tradeoff -> code" flow
- [ ] Practice driving the conversation -- don't wait for interviewer prompts

### Logistics
- [ ] Test HackerRank IDE and screen share setup
- [ ] Prepare quiet environment + wired headphones
- [ ] Have this document + resume open for quick reference
- [ ] Water ready, phone on silent
