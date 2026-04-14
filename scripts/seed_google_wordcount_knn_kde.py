"""Seed Google coding prep for T-P2-211.

Three talking-point problems from the Google 2026-04-17 prep flag list:
  (1) Distributed word count across many documents (MapReduce vs bounded machines).
  (2) KNN vs K-means distinction; zero-shot classification via KNN over
      embedding space; applicability conditions.
  (3) Kernel density estimation (Parzen window) as a smoothed soft-KNN
      alternative; 1-D Gaussian kernel numerics.

Chinese prose; algorithm names, code, complexity, and acronyms stay English
per feedback_lc_notes_chinese. Idempotent: UPSERTs by (leetcode_id NULL, title).
"""
from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from math import exp, pi, sqrt
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"

TITLE = "Distributed Word Count + KNN/K-means 0-shot + Kernel Density (Parzen)"

DESCRIPTION = """Google coding/ML interview triple (custom, non-LC; T-P2-211).

(1) Word-count across `D` documents totalling `N` tokens with vocabulary `V`.
    Variants:
      - Unbounded workers: classic MapReduce (map -> shuffle -> reduce).
      - `M` fixed workers (bounded): per-worker local Counter + combiner,
        then a single reducer or K-way merge across partitions.
      - Constraints on the reduce operator: must be associative and
        commutative so the shuffle grouping is order-independent.

(2) KNN vs K-means. Surface difference: K-means is unsupervised clustering
    (partitions points into k groups by Lloyd's iteration), KNN is a
    supervised non-parametric classifier/regressor (label = vote among k
    nearest training points). Google loves the zero-shot angle: given a
    pretrained embedding model `f: x -> R^d`, classify a new point by
    nearest-neighbour lookup against a small labelled prototype set --
    no gradient update needed, works as long as the embedding space
    respects class semantics.

(3) Kernel density estimation. Follow-up to KNN: instead of a hard `k`,
    smooth over all training points with a Gaussian kernel of bandwidth
    `h`. Parzen window density estimator:
      p_hat(x) = (1 / (N * h)) * sum_i K((x - x_i) / h)
    Class-conditional KDE + Bayes rule gives a smooth classifier; the
    bandwidth `h` is the regulariser (bias/variance trade-off).

Expected follow-ups:
(A) What if documents live on different machines and we can't ship the
    raw text across the network? -> combiner locally, ship the partial
    Counter only (O(V_local) words), merge at reducer.
(B) Why is KNN usable zero-shot but K-means not? Because KNN only needs
    a metric + labelled anchors; K-means needs k and Lloyd iterations
    which require the full point cloud.
(C) How do you pick bandwidth h for KDE? Silverman's rule of thumb
    `h = 1.06 * sigma * N^(-1/5)` for Gaussian data; or cross-validation
    minimising negative log-likelihood on held-out points.
(D) KDE vs histogram: histograms are piecewise-constant (high variance
    at bin edges); KDE is smooth, differentiable, and bandwidth replaces
    bin-width as the sole hyperparameter.
"""

NOTES = """## Distributed Word Count + KNN/K-means + KDE (Google 2026-04-17)

### Part 1 -- 分布式 Word Count

#### 1.1 无界机器数 (MapReduce 经典题)

把问题拆成三阶段：**Map -> Shuffle -> Reduce**。

- **Map**：每台 worker 独立处理自己分到的文档切片。对每个 token 发射
  `(word, 1)` 键值对。纯 stateless，可无限横向扩展。
- **Shuffle**：框架按 `word` 的 hash 把键值对路由到同一个 reducer。
  **关键约束**：reduce 算子必须是**结合律 + 交换律**（associative &
  commutative），不然 shuffle 内的任意重排就会改变结果。加法满足；
  "取平均"不满足（需要改成 `(sum, count)` 对 + 结合律求和）。
- **Reduce**：对每个 `word` 把所有 `1` 求和。

```python
# Conceptual MapReduce form
def mapper(doc: str):
    for tok in doc.split():
        yield (tok.lower(), 1)

def reducer(word: str, counts: Iterable[int]) -> tuple[str, int]:
    return (word, sum(counts))
```

复杂度：$O(N)$ 总工作量，wall-clock $O(N/M + V \\log V)$，其中 $M$ 是 worker
数，$V$ 是词表大小（reducer 合并阶段）。Shuffle 的网络字节数是
$O(N)$（每个 token 一条 KV），这是工业级瓶颈，**combiner 是必问
优化**。

#### 1.2 有界机器数 + Combiner

给定固定 `M` 台机器，每台内存能装下 $O(V)$ 的 Counter：

```python
from collections import Counter
from typing import Iterable

def worker_local(docs: Iterable[str]) -> Counter:
    c: Counter = Counter()
    for doc in docs:
        c.update(doc.lower().split())
    return c  # ship this to reducer, not the raw (word,1) pairs

def reducer_merge(partials: list[Counter]) -> Counter:
    out: Counter = Counter()
    for p in partials:
        out.update(p)
    return out
```

**Why better**: 网络字节从 $O(N)$ 降到 $O(\\sum_m V_m)$；当每个文档重复词
很多时（自然语言通常如此，Zipf's law）这是大数量级的节省。Hadoop 的
`Combiner` 接口就是这个抽象。

#### 1.3 进一步分片：Hash-partition reducer

如果 $V$ 大到一台 reducer 也装不下：把 word 按 `hash(word) % R` 分到
$R$ 个 reducer。每 reducer 只合并分到它的子词表，最终 K-way merge 或
直接输出。Spark/Hadoop 默认行为。

#### 1.4 错误对照表

| 想法 | 为什么挂 |
|------|---------|
| 所有 worker 写同一个 global dict | 竞态 + 锁瓶颈；没用到分布式 |
| mapper 直接发 `(word, 1)`，不要 combiner | 网络字节 $O(N)$，Zipf 下 10-100x 浪费 |
| reduce 算子用 "平均词频" | 不结合律；shuffle 重排改结果；要改成 `(sum, count)` |
| 按文档分片但 reducer 收整个 partial Counter 字典 | 同上，仍是 combiner 的正路 |
| 把文档按 worker 数等分但不考虑长度 | data skew；几篇长文档拖死一个 worker。Salting 或按 token count 分 |

---

### Part 2 -- KNN vs K-means，以及 0-shot

#### 2.1 本质区别

| 维度 | KNN (K-Nearest Neighbors) | K-means |
|------|--------------------------|---------|
| 监督信号 | 有标签 | 无标签 |
| 目标 | 预测 `y = f(x)` | 划分数据为 $k$ 个簇 |
| 训练 | 懒惰：存下所有 $(x_i, y_i)$ | Lloyd 迭代直到收敛 |
| 推理 | 找 $k$ 个最近邻，投票/平均 | 对新点找最近 centroid |
| 超参 | $k$ + 距离度量 | $k$ + 初始化 + 迭代次数 |
| 前置条件 | 必须有少量已标注锚点 | 只需点集 |

两者都用**距离/相似度**，容易混。考察时千万不要把 K-means 说成
"k 个最近邻的分类器"。

#### 2.2 0-shot via KNN over Embedding Space

**设定**：有预训练 encoder $f: \\mathcal{X} \\to \\mathbb{R}^d$（例如
CLIP、sentence-BERT、YouTube DNN item tower）。新类来了，只有少量
anchor/prototype $\\{(p_c, c)\\}_{c \\in \\text{classes}}$。

**推理**：对 query $x$：
```python
def zero_shot_knn(x, prototypes, k=1):
    e_x = encoder(x)
    sims = [(cosine(e_x, encoder(p)), c) for p, c in prototypes]
    sims.sort(reverse=True)
    topk = sims[:k]
    # majority vote (or weighted by similarity)
    return Counter(c for _, c in topk).most_common(1)[0][0]
```

**为什么能 work**：encoder 已在大量数据上学到语义几何；相同类别的
embedding 自然聚在一起。KNN 在这个空间等价于最近 prototype 分类。

**与纯 KNN 的区别**：经典 KNN 用**原始特征**的距离，受 scale / 无关
特征影响巨大（**curse of dimensionality** 更严重）。0-shot KNN 用
**学习得到的** embedding，维度小 ($d \\le 1024$) 且语义对齐。

#### 2.3 K-means 能 0-shot 吗？

不能（直接意义上）。K-means 需要**整个点集**才能跑 Lloyd。如果你有
点集 + 想把新类嵌入其中，做法是：
1. 对已有数据跑 K-means，得到 $k$ 个 centroid；
2. 对新类的 anchor 跑最近 centroid 分配 -> 得到 "类 -> centroid" 映射；
3. 新点 $x$ 最近 centroid -> 类。

这本质上仍是 **centroid-based 最近邻**，不是 K-means 的"训练"。

---

### Part 3 -- Kernel Density Estimation (Parzen Window)

#### 3.1 动机：soft KNN

KNN 的硬阈值 $k$ 不连续：一个点移动一点点可能跳到不同的 $k$ 邻居，
决策边界锯齿。KDE 用**平滑权重**代替硬阈值。

#### 3.2 定义

一维 Parzen 估计，Gaussian kernel $K(u) = \\frac{1}{\\sqrt{2\\pi}} e^{-u^2/2}$，
bandwidth $h$：

$$
\\hat{p}(x) = \\frac{1}{N h} \\sum_{i=1}^{N} K\\!\\left(\\frac{x - x_i}{h}\\right)
$$

多维：$K(u) = \\frac{1}{(2\\pi)^{d/2}} e^{-\\|u\\|^2/2}$，分母换成 $N h^d$。

#### 3.3 Python 实现

```python
from math import exp, pi, sqrt

def gaussian_kernel_1d(u: float) -> float:
    return exp(-0.5 * u * u) / sqrt(2.0 * pi)

def kde_1d(x: float, samples: list[float], h: float) -> float:
    n = len(samples)
    total = sum(gaussian_kernel_1d((x - xi) / h) for xi in samples)
    return total / (n * h)
```

#### 3.4 Bandwidth 选择 (bias/variance)

- $h$ 太小 -> 近似 N 个 delta 函数；**variance 极高**，overfit 采样噪声。
- $h$ 太大 -> 近似常数函数；**bias 极高**，丢细节。
- **Silverman's rule of thumb**（Gaussian 数据）：
  $h^* = 1.06 \\cdot \\hat\\sigma \\cdot N^{-1/5}$。
- 或 **cross-validation** 最大化 held-out log-likelihood：
  $\\max_h \\sum_{i} \\log \\hat{p}_{-i}(x_i; h)$。

#### 3.5 从 KDE 到分类器 (Bayes)

每个类别 $c$ 独立做 class-conditional KDE $\\hat{p}(x \\mid c)$，配合
先验 $\\hat{P}(c) = N_c / N$：
$$
\\hat{P}(c \\mid x) \\propto \\hat{P}(c) \\cdot \\hat{p}(x \\mid c).
$$
这就是 **kernel Bayes classifier**，可以看作 soft-KNN 的概率化版本。

#### 3.6 与 KNN/histogram 的对照

| 方法 | 平滑性 | 超参 | 存储 | 评估 |
|------|-------|------|------|------|
| Histogram | 分段常数 | bin 宽度 | $O(V)$ bin | $O(1)$ |
| KNN density ($k$-th NN 距离) | 分段光滑 | $k$ | $O(N)$ | $O(\\log N)$ with KD-tree |
| KDE (Parzen) | $C^\\infty$ (Gaussian) | $h$ | $O(N)$ | $O(N)$ naive, $O(\\log N)$ with tree |

#### 3.7 复杂度

Naive KDE evaluation at one query: $O(N)$. 对 $M$ 个 query: $O(MN)$.
加速：ball-tree / KD-tree / fast Gauss transform $\\to O((M+N) \\log N)$
或 $O((M+N) \\log(1/\\epsilon))$ 近似。

---

### 面试应答 checklist

1. **Word count**: 先问"多少机器、数据在哪、输出要到哪、能用 Spark
   吗？"。主解法说出 MapReduce 三阶段 + combiner。强调结合律 / 交换律。
2. **KNN vs K-means**: 一句话 = "KNN 有监督懒惰分类，K-means 无监督
   迭代聚类"。0-shot 要引到 embedding space + prototype lookup。
3. **KDE**: 写出 Parzen 公式，Gaussian kernel 5 行代码；谈 bandwidth
   bias/variance；类条件 KDE + Bayes 给软分类器。
4. **Cross-connections**: KDE 是 KNN 的平滑版；两者都受 curse of
   dimensionality 影响，高维下用 embedding 降维再做才可靠。
"""


def verify_examples() -> None:
    """Numerical self-checks for all three parts."""
    # --- Part 1: distributed word count ---
    docs = [
        "the quick brown fox",
        "the lazy dog",
        "the fox jumps over the lazy dog",
    ]
    # Single-machine baseline
    truth = Counter()
    for d in docs:
        truth.update(d.split())

    # Simulate 2 workers + combiner
    def worker(batch: list[str]) -> Counter:
        c: Counter = Counter()
        for d in batch:
            c.update(d.split())
        return c

    partials = [worker(docs[:1]), worker(docs[1:])]
    merged: Counter = Counter()
    for p in partials:
        merged.update(p)
    assert dict(merged) == dict(truth), (merged, truth)
    assert merged["the"] == 4
    assert merged["fox"] == 2
    assert merged["dog"] == 2

    # Simulate mapper -> shuffle -> reducer (order-independent reduce)
    pairs: list[tuple[str, int]] = []
    for d in docs:
        for tok in d.split():
            pairs.append((tok, 1))
    shuffled: dict[str, list[int]] = defaultdict(list)
    for w, v in pairs:
        shuffled[w].append(v)
    reduced = {w: sum(vs) for w, vs in shuffled.items()}
    assert reduced == dict(truth)

    # --- Part 2: KNN zero-shot in a toy 2-D embedding space ---
    prototypes = [((0.0, 0.0), "cat"), ((10.0, 10.0), "dog")]
    query = (0.5, 0.1)

    def l2(a: tuple[float, float], b: tuple[float, float]) -> float:
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    dists = [(l2(query, p), c) for p, c in prototypes]
    dists.sort()
    assert dists[0][1] == "cat", dists

    # --- Part 3: Gaussian KDE sanity ---
    # Standard normal sampled at many points: density at 0 should exceed density at 3.
    import random

    random.seed(0)
    samples = [random.gauss(0.0, 1.0) for _ in range(2000)]
    h = 1.06 * 1.0 * (len(samples) ** (-1 / 5))  # Silverman

    def kde(x: float) -> float:
        return sum(exp(-0.5 * ((x - xi) / h) ** 2) / sqrt(2.0 * pi)
                   for xi in samples) / (len(samples) * h)

    p0 = kde(0.0)
    p3 = kde(3.0)
    assert p0 > p3, (p0, p3)
    # true N(0,1) density at 0 ~= 0.3989; KDE estimate should be in the right ballpark
    assert 0.30 < p0 < 0.50, p0

    print("word-count + KNN 0-shot + KDE self-checks: all passed [OK]")


def upsert_problem(cur: sqlite3.Cursor) -> int:
    cur.execute(
        "SELECT id FROM problems WHERE leetcode_id IS NULL AND title=?",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(
        ["mapreduce", "distributed", "knn", "k-means", "kde", "parzen",
         "zero-shot", "embedding", "ml-fundamentals"],
        ensure_ascii=False,
    )
    company_json = json.dumps(["Google"], ensure_ascii=False)
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET description=?, notes=?, tags=?, pattern=?, category=?, "
            "company_tags=?, source=?, difficulty=?, priority=? WHERE id=?",
            (DESCRIPTION, NOTES, tags_json, "distributed-ml-fundamentals", "algorithm",
             company_json, SOURCE_BADGE, "medium", 2, pid),
        )
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, description, notes, tags, pattern, "
        "category, company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (TITLE, DESCRIPTION, NOTES, tags_json, "distributed-ml-fundamentals", "algorithm",
         company_json, SOURCE_BADGE, "medium", 2, now),
    )
    return cur.lastrowid


def main() -> None:
    verify_examples()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    pid = upsert_problem(cur)
    conn.commit()
    cur.execute(
        "SELECT id, title, length(description), length(notes) FROM problems WHERE id=?",
        (pid,),
    )
    r = cur.fetchone()
    print(f"problem id={r[0]} title={r[1]!r} desc_len={r[2]} notes_len={r[3]}")
    conn.close()


if __name__ == "__main__":
    main()
