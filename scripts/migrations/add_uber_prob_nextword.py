"""
Add Probabilistic Next-Word Generation problem (no library, n-gram LM) to:
  - problems table (new row, tagged Uber)
  - company_documents.id=84 (Uber ML Coding Golden Answer 集合)

Inserts §5 between §4 LogReg and §5 Cross-cutting (which becomes §6),
audit-aux §6 → §7, updates TOC, "4 道核心" → "5 道核心", "4 题" → "5 题",
and refreshes content_hash + updated_at + golden_at.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[2] / "data" / "mle_prep.db"
DOC_ID = 84
COMPANY_UBER = 5

NEW_PROBLEM_TITLE = "Probabilistic Next-Word Generation (N-gram Language Model, no library)"
NEW_PROBLEM_TAGS_JSON = json.dumps(
    ["ml-fundamentals", "nlp", "language-model", "n-gram", "probability", "implementation"]
)
NEW_PROBLEM_COMPANY_JSON = json.dumps(["Uber"])
NEW_PROBLEM_DESCRIPTION = (
    "**Probabilistic Next-Word Generation (N-gram LM)**: 给定文本语料, 从零实现一个 "
    "n-gram language model 用于 next-word prediction / generation. **不允许任何外部库** "
    "(no numpy / nltk / sklearn / torch), 只能用 Python 标准库 (collections, random). "
    "需要支持: (1) 任意阶 n (bigram / trigram / 5-gram), 不只是 bi-gram; (2) start/end "
    "token 处理 (`<s>` / `</s>`); (3) smoothing (add-k Laplace 或 stupid backoff) 解决 "
    "unseen context 的零概率问题; (4) sampling-based generation (greedy / multinomial / "
    "temperature). 评估指标 perplexity. Follow-up: 大词表 (V=10^6, n=5 → V^n 不可存) 用 "
    "MapReduce + 稀疏字典; streaming 数据用 ε-approximate count; 与 neural LM "
    "(RNN / Transformer) 的本质差异 — n-gram 只能按 exact suffix match 泛化, NLM 在语义 "
    "embedding 空间平滑."
)

NEW_SECTION_BODY = """<h2 id="ngram-next-word">5. 概率下一个词生成 (Probabilistic Next-Word Generation, N-gram LM, no library)</h2>

### 5.1 题目 (Problem)

给定一份文本语料, **从零实现一个 n-gram language model (LM)**, 用来做 next-word prediction 和 free-form text generation. **明确禁用任何外部库** — 不允许 numpy / nltk / sklearn / torch / scipy, 只能用 Python 标准库 (`collections`, `random`, `math`). 上来通常以 **bigram (n=2)** 起手, 面试官会立刻 follow-up "**expand 到任意 n**".

**对应 problems table**: id=$NEW_ID [db://$NEW_ID] *Probabilistic Next-Word Generation (N-gram Language Model, no library)*.

### 5.2 Clarify (澄清问题)

VO 实战必问清单:

- **n-gram 阶数 $n$?** bi-gram (n=2) / tri-gram (n=3) / 通用 n? 面试官常说 "先写 bi-gram, 再 expand". 写代码就要把 $n$ 做成参数, 别 hard-code.
- **词表大小 $V$ 量级?** $V \\le 10^4$ 直接 in-memory dict; $V \\ge 10^6$ 要稀疏 + pruning.
- **句子边界?** 用 `<s>` (start) 和 `</s>` (end) special token, **prepend $n-1$ 个 `<s>`** 让第一个词也有 context, **append `</s>`** 让模型学会"何时停".
- **Smoothing 选择?** unsmoothed 会在 unseen context 上返回 0 prob, 一遇到训练集没见过的 prefix 就 KeyError / NaN. 至少要 **add-k (Laplace)** 或 **stupid backoff**.
- **Generation 模式?** greedy argmax / 按 conditional dist multinomial 采样 / top-k / temperature scaling? 面试官最常考"按 prob 采样" + "加 temperature".
- **评估?** 训练集 next-word accuracy / held-out perplexity? Perplexity 是 NLP 标配.
- **OOV 处理?** 测试集里出现训练集没有的词 — 通常预处理时把低频 (count < threshold) 替换为 `<unk>`.
- **复现性?** `random` 模块的 seed 固定, 否则面试官说"再跑一遍"输出就变了.

### 5.3 Brute-force (暴力 baseline) — Bigram with raw counts

最朴素版本: 只支持 bi-gram, 没有 smoothing, 字典存条件计数:

```python
import random
from collections import defaultdict, Counter

def train_bigram(corpus):
    # corpus: list of token lists, e.g. [["the","cat","sat"], ...]
    model = defaultdict(Counter)
    for sent in corpus:
        sent = ["<s>"] + sent + ["</s>"]
        for prev, w in zip(sent, sent[1:]):
            model[prev][w] += 1
    return model

def generate_bigram(model, max_len=20, seed=0):
    rng = random.Random(seed)
    out, prev = [], "<s>"
    for _ in range(max_len):
        if prev not in model:
            break
        dist = model[prev]
        words, weights = list(dist.keys()), list(dist.values())
        nxt = rng.choices(words, weights=weights, k=1)[0]
        if nxt == "</s>":
            break
        out.append(nxt)
        prev = nxt
    return out
```

**问题**:
1. **零概率**: 测试时 `prev` 没在训练集里出现 → `model[prev]` 是空 Counter → `random.choices` 报错或返回空.
2. **只看 1 个词的 history**: bi-gram 完全忽略再前面的语境, 生成出来的句子局部连贯但全局漂移.
3. **不支持 expand 到 trigram / 5-gram** 不改架构没法加阶.
4. **不可评估** — 没有 prob 接口, 没法算 perplexity.

### 5.4 Optimal — generic n-gram + stupid backoff + temperature sampling

把架构改成: **每个阶都存一份 count dict**, 推断时从最长阶往下 backoff, 生成时按平滑后的 prob 采样, 还要支持 temperature.

**Stupid Backoff** (Brants et al. 2007, Google 1T-token 论文): 不是合法概率 (不归一化), 但**在大数据下经验上比 Kneser-Ney 还好**, 且实现极简:

$$S(w_i \\mid w_{i-n+1}^{i-1}) = \\begin{cases} \\dfrac{c(w_{i-n+1}^{i})}{c(w_{i-n+1}^{i-1})} & \\text{if } c(w_{i-n+1}^{i}) > 0 \\\\[6pt] \\alpha \\cdot S(w_i \\mid w_{i-n+2}^{i-1}) & \\text{otherwise} \\end{cases}$$

其中 $\\alpha = 0.4$ 是经验值. 一直 backoff 到 unigram, 最后兜底 $1/V$ uniform.

**Add-k (Laplace)**: 对每个 (context, word) 加 $k$ 平滑 (常 $k = 0.01$):

$$P(w \\mid \\text{ctx}) = \\frac{c(\\text{ctx}, w) + k}{c(\\text{ctx}) + k V}$$

完整实现 (~70 行, pure stdlib):

```python
import math
import random
from collections import defaultdict, Counter

class NGramLM:
    \"\"\"Pure-Python n-gram language model, no external libraries.

    Supports: arbitrary n, stupid-backoff sampling, add-k smoothing,
    temperature, perplexity evaluation.
    \"\"\"

    def __init__(self, n: int = 3, k: float = 0.01, alpha: float = 0.4):
        assert n >= 1
        self.n = n
        self.k = k                # add-k Laplace
        self.alpha = alpha        # stupid-backoff weight
        # counts[order] = dict mapping (w_{i-order+1}, ..., w_{i-1}) -> Counter of next words
        # order = 1 means unigram (empty context tuple)
        self.counts = [defaultdict(Counter) for _ in range(n)]
        self.totals = [defaultdict(int) for _ in range(n)]   # sum over Counter values
        self.vocab: set[str] = set()

    # ---- Train ----
    def fit(self, corpus: list[list[str]]) -> None:
        for sent in corpus:
            self.vocab.update(sent)
            padded = ["<s>"] * (self.n - 1) + list(sent) + ["</s>"]
            for order in range(1, self.n + 1):
                for i in range(len(padded) - order + 1):
                    ctx = tuple(padded[i:i + order - 1])    # () for unigram
                    w = padded[i + order - 1]
                    self.counts[order - 1][ctx][w] += 1
                    self.totals[order - 1][ctx] += 1
        self.vocab.update(["<s>", "</s>"])

    # ---- Probability with stupid-backoff + add-k ----
    def prob(self, context: tuple[str, ...], w: str) -> float:
        # Try longest order first, backoff to lower orders.
        for order in range(min(len(context) + 1, self.n), 0, -1):
            sub_ctx = tuple(context[-(order - 1):]) if order > 1 else ()
            total = self.totals[order - 1].get(sub_ctx, 0)
            if total == 0:
                continue
            cnt = self.counts[order - 1][sub_ctx].get(w, 0)
            if cnt > 0:
                weight = self.alpha ** (self.n - order)
                V = max(len(self.vocab), 1)
                return weight * (cnt + self.k) / (total + self.k * V)
        # Last-resort uniform
        return 1.0 / max(len(self.vocab), 1)

    # ---- Sample next word with temperature ----
    def sample_next(
        self,
        context: tuple[str, ...],
        rng: random.Random,
        temperature: float = 1.0,
    ) -> str:
        # Find longest order whose context has non-zero count, sample from it.
        for order in range(min(len(context) + 1, self.n), 0, -1):
            sub_ctx = tuple(context[-(order - 1):]) if order > 1 else ()
            dist = self.counts[order - 1].get(sub_ctx)
            if dist and self.totals[order - 1].get(sub_ctx, 0) > 0:
                words = list(dist.keys())
                # Temperature: weights = count^(1/T). T<1 sharpens, T>1 flattens.
                if temperature == 1.0:
                    weights = [float(dist[w]) for w in words]
                else:
                    weights = [float(dist[w]) ** (1.0 / max(temperature, 1e-6)) for w in words]
                return rng.choices(words, weights=weights, k=1)[0]
        # Fallback: uniform random over vocab
        return rng.choice(sorted(self.vocab))

    # ---- Generate ----
    def generate(
        self,
        max_len: int = 30,
        seed: int | None = None,
        temperature: float = 1.0,
    ) -> list[str]:
        rng = random.Random(seed)
        ctx = ["<s>"] * (self.n - 1)
        out: list[str] = []
        for _ in range(max_len):
            sub = tuple(ctx[-(self.n - 1):]) if self.n > 1 else ()
            nxt = self.sample_next(sub, rng, temperature=temperature)
            if nxt == "</s>":
                break
            out.append(nxt)
            ctx.append(nxt)
        return out

    # ---- Evaluate perplexity on held-out corpus ----
    def perplexity(self, corpus: list[list[str]]) -> float:
        # PP = exp( -1/N * sum log p(w_i | ctx_i) )
        log_sum, N = 0.0, 0
        for sent in corpus:
            padded = ["<s>"] * (self.n - 1) + list(sent) + ["</s>"]
            for i in range(self.n - 1, len(padded)):
                ctx = tuple(padded[i - (self.n - 1):i])
                w = padded[i]
                p = self.prob(ctx, w)
                log_sum += -math.log(max(p, 1e-12))
                N += 1
        return math.exp(log_sum / max(N, 1))


if __name__ == "__main__":
    corpus = [
        "the cat sat on the mat".split(),
        "the dog sat on the chair".split(),
        "the cat ran away from the dog".split(),
        "a dog barked at the cat".split(),
        "the mat was on the floor".split(),
    ]
    lm = NGramLM(n=3, k=0.01, alpha=0.4)
    lm.fit(corpus)
    print("sample (T=1.0)  :", " ".join(lm.generate(seed=0, temperature=1.0)))
    print("sample (T=0.5)  :", " ".join(lm.generate(seed=0, temperature=0.5)))
    print("p(sat | the,cat):", lm.prob(("the", "cat"), "sat"))
    print("perplexity      :", lm.perplexity(corpus))
```

**端到端验证**: `python ngram_lm.py` 必须打印出**真实的句子片段** (不是 KeyError), `prob` 大于 0, `perplexity` 是合理 finite 数值.

**关键实现要点**:
- **每阶独立 dict**: `counts[order-1]` 存阶 `order` 的 (ctx → next-word Counter), 这样 expand 到任意 n 不用改架构, 训练和推断的内层循环天然支持 backoff.
- **`<s>` 填充 $n-1$ 个**: 第一个真实词的 context 是 $n-1$ 个 `<s>`, 否则 `padded[i:i+order-1]` 在 i=0 处会越界拿空 tuple — 那其实是 unigram 而不是想要的 high-order.
- **`<unk>` / OOV**: 训练时遇到 vocab 之外的词替换为 `<unk>` (这里省略未实现, 面试官 drill 到才补). 简单做法: 预处理时把 count < threshold 的词全部 map 到 `<unk>`.
- **Temperature**: weights = count^(1/T). T → 0 退化为 argmax (greedy); T → ∞ 趋近 uniform.
- **数值稳定**: log-prob 和用 `math.log(max(p, 1e-12))`, 避免 `log(0) = -inf`.

### 5.5 Trade-off (权衡)

**$n$ 的选择**:

| n | 上下文捕捉 | 数据需求 | sparsity 风险 |
|---|---|---|---|
| 1 (unigram) | 无 (词频) | 任意 | 最低 |
| 2 (bigram) | 1 词 | 中等 ($\\ge 10^5$ tokens) | 低 |
| 3 (trigram) | 2 词 | 大 ($\\ge 10^7$ tokens) | 中 |
| 4-5 | 3-4 词 | 极大 ($\\ge 10^9$) | 高 (大多 unseen) |
| $> 5$ | 长程 | 不实际 | 几乎全 unseen |

**Smoothing 方法对比**:

| 方法 | 优点 | 缺点 | 何时用 |
|---|---|---|---|
| **Add-k (Laplace)** | 实现 5 行, 总是 > 0 | 把太多 mass 给 unseen, 高频词 prob 被低估 | toy / 小数据 |
| **Good-Turing** | 用"见过 $r+1$ 次的"个数估"见过 $r$ 次的"真实期望 | 实现复杂; 高 $r$ 处 noisy | 中等数据 |
| **Kneser-Ney** | 用 continuation count $\\|\\{w' : c(w', w) > 0\\}\\|$ 衡量 "$w$ 作为延续词的多样性"; 是 NLM 之前的 SOTA | 实现 30+ 行, 推导难记 | 论文 baseline / 离线 |
| **Stupid Backoff** | 极简, 大数据下经验最好, Google 1T-token 用 | **不是合法 prob distribution** (不归一化) | 工业大数据 / 排序场景 |
| **Linear Interpolation** | $\\hat P = \\sum_{i} \\lambda_i P_i$ where $\\lambda_i$ 学到 | 总是用所有 order; 不稀疏 | mid-range; 易调 |

**Generation 模式对比**:

| 模式 | 效果 | 缺点 |
|---|---|---|
| **Greedy argmax** | 每步取 prob 最大 | deterministic, 重复 (loop) 严重 |
| **Pure multinomial sampling** | 多样 | 长度长时易 derail (走偏) |
| **Top-k sampling** | 截断 tail, k=40 是经验值 | k 选多少要 tune |
| **Top-p (nucleus) sampling** | 截断累积 prob ≥ p, 自适应 | 实现稍复杂 |
| **Temperature scaling** | 平滑/锐化分布 | 单独不够, 通常和 top-k/p 合用 |
| **Beam search** | 找全局高 prob 序列 | 输出"安全"无聊; 不如 sampling 多样 |

**bi-gram → trigram 的真实差异**: bi-gram 生成的句子局部连贯但话题漂移 ("the cat sat on the dog barked"); trigram 让 "the cat" 限定下个词的搜索, 一致性显著提升, 但 unseen trigram 比例也跳到 80%+ — 强依赖 backoff.

**为什么不直接用 NLM (RNN / Transformer)?**: n-gram 的强项是**速度** (查表 O(1)) 和**可解释** (你能看出"为什么生成这个词" — 因为某个 trigram count 很高); 弱项是泛化 — 只能按 **exact suffix match** 工作, 没见过的 prefix 即使语义相似也没法借鉴. NLM 在 embedding 空间平滑, 但需要 GPU + 1000x 训练数据.

### 5.6 Follow-up scaling (大规模)

**Q: "$V = 10^6$, $n = 5$ → $V^n = 10^{30}$ 不可存怎么办?"**

→ 实际数据下 99.99% 的 ($V^n$) 组合都是 0, 只存**真实出现过的** n-gram (sparse dict). 训练 $T$ 个 token 最多产生 $T$ 个 unique n-gram, 内存 $O(T)$ 而不是 $O(V^n)$. 加 **count-based pruning**: 丢弃 count = 1 的 entry (Zipf 长尾), 内存再减半到 75%. 极致用 **Bloom filter** 当 "is in vocab" gate.

**Q: "Corpus $T = 10^{12}$ tokens (Google web crawl) 怎么训?"**

→ **MapReduce**: mapper emit (n-gram, 1), reducer 累加 → (n-gram, count). 这是 Google 2007 *"Large Language Models in Machine Translation"* (Brants et al.) 的实现. 论文里发现: 在 1T tokens 下, **stupid backoff 经验上和 Kneser-Ney 等价但实现简单 100x**, 这才让 stupid backoff 出名.

**Q: "Streaming, 数据持续来?"**

→ **Count-Min Sketch** 或 **Reservoir Counting** 做 ε-approximate count. 内存 $O(1/\\epsilon \\cdot \\log(1/\\delta))$ 不依赖 unique n-gram 数. trade off 是 count 上 bias (偏高), 但用于 ranking / sampling 影响小.

**Q: "Distributed inference (在线 serving 100K QPS)?"**

→ Sharding by **first $k$ words of context** (consistent hashing); 每 shard 装一部分 dict. backoff 时如果 longer order 在另一台机器, 跨 shard RPC 一次. 工程上常用 LSM-tree (RocksDB) 或 hash-sharded Redis. 谷歌的 SRILM / KenLM 是经典开源实现.

**Q: "OOV 在线突发新词怎么办?"**

→ 用 **subword tokenization** (BPE / WordPiece / SentencePiece) 把 vocab 控制在 $V = 32K$ 内, 任何新词都能拆成 subword 序列. 这同时是 NLM 标配 (GPT/BERT/T5 全用 BPE/WordPiece). n-gram 也可以基于 subword 训, 退化为 character-level 时 $V \\le 256$.

**Q: "n-gram vs Neural LM 应该什么时候用?"**

→ **n-gram 赢的场景**: latency 严格 (< 1ms 查表) / 解释性要求高 / 小语料 (< 1M tokens 还不够 NLM warm up) / 候选 reranking (n-gram score 当 feature). **NLM 赢的场景**: 长程依赖 (n-gram 阶 > 5 不可行) / 跨语义泛化 / open-domain generation (ChatGPT). 工业上常 **二阶段**: NLM 当 generator + n-gram 当 cheap reranker filter.

**Q: "Perplexity 多少算好?"**

→ 强 baseline (1B tokens 训 trigram + Kneser-Ney) 在 PTB / WikiText 上 perplexity ≈ 100-150; GPT-2 small ≈ 30; GPT-3 / 4 < 20. **重点不是绝对值, 而是同一测试集上的相对比较**.

### 5.7 行业黑话 (Industry idioms)

- **Markov assumption order $n-1$**: n-gram 假设 "下个词只依赖前 $n-1$ 个词", 即 $(n-1)$-阶 Markov chain. 知道 "n-gram 是 $(n-1)$-阶 Markov 模型" 这个等价显得理论功底.
- **Perplexity (PP)**: $\\exp(-\\frac{1}{N} \\sum_i \\log p(w_i \\mid \\text{ctx}_i))$ — 每个词的 "几何平均 1/prob", 直观理解为 "模型有效地在多少个等概率候选里挑". PP=100 ≈ "在 100 个候选里乱猜".
- **Cross-entropy = log-perplexity**: $\\text{PP} = 2^{H}$ (用 log2) 或 $e^H$ (用 ln). 同一回事, 两个名字别混.
- **Stupid Backoff**: Brants 2007, Google translation team. **"naive 但 work"** 的代表作.
- **Modified Kneser-Ney**: pre-NLM 的 SOTA, Heafield's KenLM 库的默认 smoothing.
- **OOV (Out-of-vocabulary) / `<unk>` 处理**: 工业上常 "low-freq replacement" (count < 5 替换为 `<unk>`) + subword tokenization (BPE).
- **Zipfian distribution**: 词频遵循 $f \\propto 1/r$, 长尾极多 — 这是为什么 smoothing 是必需的.
- **Backoff vs Interpolation**: backoff 只在高阶 unseen 时下放; interpolation 总是按 $\\lambda_i$ 加权所有阶. interpolation 表达力强但参数多.
- **Distributed n-gram** (Heafield's KenLM, Google Brants et al.): probing hash + trie, GB 级 binary 文件磁盘原地查询.
- **Switchback test** 在 generation quality 评测里用得少, 这一题 follow-up 不太会被问到, 但如果被问 "怎么 A/B test 两个 LM" — 答 "user-level randomization + downstream metric (BLEU / human eval), 不要 sentence-level 因为同一 user 的 utterance 有相关性".
- **Beam search width**: NLM generation 里 beam=4 是经验默认; n-gram 里也常用同一思路做 K-best decoding.

---
"""

CROSS_CUTTING_FIRST_LINE = "Uber VO ML coding 不是纯 LeetCode — 你写出来还要**讲明白**. 推荐 talk track:"


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # ---- 1) Insert problem row ----
    new_id = (c.execute("SELECT MAX(id) FROM problems").fetchone()[0] or 0) + 1
    print(f"new problem id: {new_id}")

    notes = (NEW_SECTION_BODY.replace("$NEW_ID", str(new_id)))
    # Per-problem notes: a digest pointing back to the doc-84 anchor
    problem_notes = (
        f"## {NEW_PROBLEM_TITLE}\n\n"
        f"### 题目描述\n"
        f"从零实现 n-gram language model 用于 next-word prediction / generation. "
        f"**禁用任何外部库** (no numpy / nltk / sklearn / torch), 只能用 Python 标准库 "
        f"(`collections`, `random`, `math`). 上来先写 bigram, follow-up expand 到任意 n.\n\n"
        f"### 完整 golden answer\n\n"
        f"详见 [Uber ML Coding Golden Answer 集合 §5](db://doc/{DOC_ID}#ngram-next-word) — "
        f"包含 7 节标准结构: 题目 / Clarify / Brute-force bigram / Optimal generic-n + "
        f"stupid-backoff + temperature / Trade-off (n 阶选择 + smoothing 对比 + generation 模式) "
        f"/ Follow-up scaling (MapReduce / Count-Min Sketch / NLM 对比) / 行业黑话 "
        f"(Perplexity / Markov order / Stupid Backoff / Kneser-Ney / OOV / Zipfian).\n\n"
        f"### 核心代码 sketch (~70 行 pure stdlib)\n\n"
        f"```python\n"
        f"import math, random\n"
        f"from collections import defaultdict, Counter\n\n"
        f"class NGramLM:\n"
        f"    def __init__(self, n=3, k=0.01, alpha=0.4):\n"
        f"        self.n, self.k, self.alpha = n, k, alpha\n"
        f"        self.counts = [defaultdict(Counter) for _ in range(n)]\n"
        f"        self.totals = [defaultdict(int) for _ in range(n)]\n"
        f"        self.vocab = set()\n\n"
        f"    def fit(self, corpus):\n"
        f"        for sent in corpus:\n"
        f"            self.vocab.update(sent)\n"
        f"            padded = ['<s>'] * (self.n - 1) + list(sent) + ['</s>']\n"
        f"            for order in range(1, self.n + 1):\n"
        f"                for i in range(len(padded) - order + 1):\n"
        f"                    ctx = tuple(padded[i:i + order - 1])\n"
        f"                    w = padded[i + order - 1]\n"
        f"                    self.counts[order - 1][ctx][w] += 1\n"
        f"                    self.totals[order - 1][ctx] += 1\n"
        f"        self.vocab.update(['<s>', '</s>'])\n\n"
        f"    def prob(self, context, w):\n"
        f"        # Stupid backoff with add-k Laplace fallback.\n"
        f"        for order in range(min(len(context) + 1, self.n), 0, -1):\n"
        f"            sub = tuple(context[-(order - 1):]) if order > 1 else ()\n"
        f"            tot = self.totals[order - 1].get(sub, 0)\n"
        f"            if tot == 0: continue\n"
        f"            cnt = self.counts[order - 1][sub].get(w, 0)\n"
        f"            if cnt > 0:\n"
        f"                weight = self.alpha ** (self.n - order)\n"
        f"                V = max(len(self.vocab), 1)\n"
        f"                return weight * (cnt + self.k) / (tot + self.k * V)\n"
        f"        return 1.0 / max(len(self.vocab), 1)\n\n"
        f"    def generate(self, max_len=30, seed=None, temperature=1.0):\n"
        f"        rng = random.Random(seed)\n"
        f"        ctx = ['<s>'] * (self.n - 1)\n"
        f"        out = []\n"
        f"        for _ in range(max_len):\n"
        f"            sub = tuple(ctx[-(self.n - 1):]) if self.n > 1 else ()\n"
        f"            for order in range(min(len(sub) + 1, self.n), 0, -1):\n"
        f"                sc = tuple(sub[-(order - 1):]) if order > 1 else ()\n"
        f"                dist = self.counts[order - 1].get(sc)\n"
        f"                if dist and self.totals[order - 1].get(sc, 0) > 0:\n"
        f"                    words = list(dist.keys())\n"
        f"                    if temperature == 1.0:\n"
        f"                        weights = [float(dist[w]) for w in words]\n"
        f"                    else:\n"
        f"                        weights = [float(dist[w]) ** (1.0 / max(temperature, 1e-6)) for w in words]\n"
        f"                    nxt = rng.choices(words, weights=weights, k=1)[0]\n"
        f"                    break\n"
        f"            else:\n"
        f"                nxt = rng.choice(sorted(self.vocab))\n"
        f"            if nxt == '</s>': break\n"
        f"            out.append(nxt); ctx.append(nxt)\n"
        f"        return out\n\n"
        f"    def perplexity(self, corpus):\n"
        f"        log_sum, N = 0.0, 0\n"
        f"        for sent in corpus:\n"
        f"            padded = ['<s>'] * (self.n - 1) + list(sent) + ['</s>']\n"
        f"            for i in range(self.n - 1, len(padded)):\n"
        f"                ctx = tuple(padded[i - (self.n - 1):i])\n"
        f"                p = self.prob(ctx, padded[i])\n"
        f"                log_sum += -math.log(max(p, 1e-12))\n"
        f"                N += 1\n"
        f"        return math.exp(log_sum / max(N, 1))\n"
        f"```\n\n"
        f"### Cross-link\n"
        f"- 主 golden answer: doc {DOC_ID} §5 (anchor `#ngram-next-word`)\n"
        f"- 跨题对比: 与 K-Means [db://1064] 同属 Uber Round 2 ML Coding from-scratch 系列\n"
    )

    c.execute(
        """
        INSERT INTO problems (
            id, leetcode_id, title, url, difficulty, tags, pattern, category,
            source, company_tags, priority, is_completed, comfort_level,
            created_at, framework_node_id, description, neetcode_slug,
            description_source, notes, frequency_rank, family
        ) VALUES (
            ?, NULL, ?, NULL, 'medium', ?, 'ML Implementation', 'ml_coding',
            'uber_prep,custom', ?, 1, 0, NULL,
            ?, NULL, ?, NULL,
            'manual', ?, NULL, NULL
        )
        """,
        (
            new_id,
            NEW_PROBLEM_TITLE,
            NEW_PROBLEM_TAGS_JSON,
            NEW_PROBLEM_COMPANY_JSON,
            now_iso(),
            NEW_PROBLEM_DESCRIPTION,
            problem_notes,
        ),
    )

    # ---- 2) Tag with Uber ----
    # Inspect tag table schema
    cols = [r[1] for r in c.execute("PRAGMA table_info(problem_company_tags)")]
    if cols == ["problem_id", "company_id"]:
        c.execute(
            "INSERT OR IGNORE INTO problem_company_tags (problem_id, company_id) VALUES (?, ?)",
            (new_id, COMPANY_UBER),
        )
    else:
        # Schema with extra cols (created_at/etc); insert defensively
        col_str = ",".join(cols)
        placeholders = ",".join(["?"] * len(cols))
        row = []
        for col in cols:
            if col == "problem_id":
                row.append(new_id)
            elif col == "company_id":
                row.append(COMPANY_UBER)
            elif col == "created_at":
                row.append(now_iso())
            else:
                row.append(None)
        c.execute(
            f"INSERT OR IGNORE INTO problem_company_tags ({col_str}) VALUES ({placeholders})",
            row,
        )

    # ---- 3) Update doc 84 content ----
    content = c.execute(
        "SELECT content FROM company_documents WHERE id=?", (DOC_ID,)
    ).fetchone()[0]

    # 3a) Header text: "Scope: 4 道核心" → "5 道核心"
    content = content.replace(
        "**Scope**: 4 道核心 ML coding 题",
        "**Scope**: 5 道核心 ML coding 题",
    )

    # 3b) TOC insertion + renumber
    toc_old = (
        "1. [几何中位数 (Geometric Median)](#geometric-median)\n"
        "2. [K-Means (numpy-only)](#kmeans-numpy)\n"
        "3. [线性回归 from scratch (Linear Regression)](#linear-regression-from-scratch)\n"
        "4. [逻辑回归 from scratch (Logistic Regression)](#logistic-regression-from-scratch)\n"
        "5. [跨题通用面试要点 (Cross-cutting Interview Tactics)](#cross-cutting-tactics)\n"
        "6. [Audit-Discovered 辅助卡片 (Depth-2 Auxiliary Cards)](#audit-aux-cards)\n"
        "   - 6.1 [Multi-treatment Uplift Modeling 直觉卡](#uplift-meta-learners)\n"
        "   - 6.2 [Lagrangian Relaxation 伪代码卡](#lagrangian-relaxation)"
    )
    toc_new = (
        "1. [几何中位数 (Geometric Median)](#geometric-median)\n"
        "2. [K-Means (numpy-only)](#kmeans-numpy)\n"
        "3. [线性回归 from scratch (Linear Regression)](#linear-regression-from-scratch)\n"
        "4. [逻辑回归 from scratch (Logistic Regression)](#logistic-regression-from-scratch)\n"
        "5. [概率下一个词生成 (N-gram LM, no library)](#ngram-next-word)\n"
        "6. [跨题通用面试要点 (Cross-cutting Interview Tactics)](#cross-cutting-tactics)\n"
        "7. [Audit-Discovered 辅助卡片 (Depth-2 Auxiliary Cards)](#audit-aux-cards)\n"
        "   - 7.1 [Multi-treatment Uplift Modeling 直觉卡](#uplift-meta-learners)\n"
        "   - 7.2 [Lagrangian Relaxation 伪代码卡](#lagrangian-relaxation)"
    )
    if toc_old not in content:
        raise SystemExit("ERROR: TOC pattern not found — abort.")
    content = content.replace(toc_old, toc_new)

    # 3c) Renumber the H2s for cross-cutting (5 → 6) and audit-aux (6 → 7)
    content = content.replace(
        '<h2 id="cross-cutting-tactics">5. 跨题通用面试要点 (Cross-cutting Interview Tactics)</h2>',
        '<h2 id="cross-cutting-tactics">6. 跨题通用面试要点 (Cross-cutting Interview Tactics)</h2>',
    )
    content = content.replace(
        '<h2 id="audit-aux-cards">6. Audit-Discovered 辅助卡片 (Depth-2 Auxiliary Cards)</h2>',
        '<h2 id="audit-aux-cards">7. Audit-Discovered 辅助卡片 (Depth-2 Auxiliary Cards)</h2>',
    )
    # Sub-section labels (6.1/6.2 → 7.1/7.2)
    content = content.replace(
        '<h3 id="uplift-meta-learners">6.1 Multi-treatment Uplift Modeling 直觉卡',
        '<h3 id="uplift-meta-learners">7.1 Multi-treatment Uplift Modeling 直觉卡',
    )
    content = content.replace(
        '<h3 id="lagrangian-relaxation">6.2 Lagrangian Relaxation 伪代码卡',
        '<h3 id="lagrangian-relaxation">7.2 Lagrangian Relaxation 伪代码卡',
    )
    # Cross-cutting subsection numbers 5.1-5.4 → 6.1-6.4
    for old_num, new_num in [
        ("### 5.1 这 4 题的共同面试结构", "### 6.1 这 5 题的共同面试结构"),
        ("### 5.2 共同的数值稳定性陷阱", "### 6.2 共同的数值稳定性陷阱"),
        ("### 5.3 共同的 follow-up scaling 套路", "### 6.3 共同的 follow-up scaling 套路"),
        ('### 5.4 共同的"行业黑话"开关词', '### 6.4 共同的"行业黑话"开关词'),
    ]:
        if old_num not in content:
            raise SystemExit(f"ERROR: subsection {old_num!r} not found")
        content = content.replace(old_num, new_num)

    # The two audit-aux internal labels "6.1 行业黑话" / "6.2 行业黑话" → 7.1 / 7.2
    content = content.replace("**6.1 行业黑话**:", "**7.1 行业黑话**:")
    content = content.replace("**6.2 行业黑话**:", "**7.2 行业黑话**:")

    # Author note: 4 题 → 5 题
    content = content.replace(
        "> **作者注**: 这 4 题是 Uber Round 2 ML Coding 的 canonical set.",
        "> **作者注**: 这 5 题是 Uber Round 2 ML Coding 的 canonical set.",
    )
    # Cross-cutting prose mentions "这 4 题" — turn into "这 5 题"
    content = content.replace(
        "Uber VO ML coding 不是纯 LeetCode",
        "Uber VO ML coding 不是纯 LeetCode",
    )  # untouched, just sanity

    # 3d) Insert new section before Cross-cutting
    cross_cut_marker = '<h2 id="cross-cutting-tactics">6. 跨题通用面试要点'
    if cross_cut_marker not in content:
        raise SystemExit("ERROR: cross-cutting marker not found after renumber")
    content = content.replace(
        cross_cut_marker,
        notes + "\n" + cross_cut_marker,
    )

    # 3e) hash + timestamp
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    now = now_iso()
    c.execute(
        """
        UPDATE company_documents
        SET content = ?, content_hash = ?, updated_at = ?, golden_at = ?
        WHERE id = ?
        """,
        (content, content_hash, now, now, DOC_ID),
    )

    conn.commit()

    # ---- 4) Verify ----
    new_len = len(content)
    print(f"updated doc {DOC_ID}: new content length = {new_len}")
    print(f"new content_hash = {content_hash}")
    tag_check = c.execute(
        "SELECT problem_id, company_id FROM problem_company_tags WHERE problem_id=?",
        (new_id,),
    ).fetchone()
    print(f"tag row: {tag_check}")

    conn.close()
    print("DONE")


if __name__ == "__main__":
    main()
