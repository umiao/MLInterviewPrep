"""[META-ANC-8] Card Game Sum-15 drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the
Card-Game pick-3-summing-to-15 Meta AI-Native Coding question. Distills
the 4-question ladder (UT debug -> naive strategy -> simulate measure ->
optimize), the 5-tier perfect-rate ladder (Naive Greedy -> Heuristic ->
Backtrack -> Monte Carlo rollout -> Expectimax DP), the Tier-5 DP recipe,
the Implementation Pitfalls table, the 4-step AI-collab Meta-Prompt, and
the core "AI-trap" reflection ('看了一眼没认真 validate 就贴进去') into one
description.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='backtrack_dp_monte_carlo'). The pattern column is the STABLE
SLUG -- never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_card_game_sum15 --> is embedded at the top of
the description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 7, lines 684-755).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.company_tags import ProblemCompanyTag  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

SLUG = "meta_anc_card_game_sum15"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "backtrack_dp_monte_carlo"
TITLE = (
    "Meta AI-Native Coding - Card Game Sum-15 "
    "(5-tier ladder: greedy -> heuristic -> backtrack -> MC rollout -> expectimax DP)"
)
DIFFICULTY = "hard"
CATEGORY = "ml_coding"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "Monte Carlo",
    "Expectimax",
    "rollout",
    "lru_cache",
    "validate",
    "澄清",
]

DESCRIPTION = SENTINEL + r"""

# Card Game Sum-15 -- Meta AI-Native Coding (5-tier ladder + Expectimax DP + AI-collab Meta-Prompt)

> **题型**: 36 张牌 (1..9 各 4 张, 像扑克的四花色), 初始台面随机 16 张; 每回合从台面挑 3 张和=15 拿走得 15 分, 然后从牌库随机补 3 张, 直到台面再也凑不出 valid triple = game over。完美局 = 12 对 = 180 分。
> **场景**: Meta AI-Native Coding 现场题; 4 问递进 (修 UT -> 写 naive strategy -> 跑 100 次测胜率 -> 优化策略到接近满分)。
> **时间预算 (60min round)**: orientation + 修 UT 之后, 主实现 + 优化只剩约 30 分钟。**Q1 必须 ≤5 分钟搞定**, **Q4 才有 10-15 分钟**。这是后面所有"选 Tier X"决策的硬约束。
> **AI-trap signature**: 楼主第 4 问只剩 10 分钟, 让 AI 直接生成了 150 行 DP 代码, **"看了一眼没认真 validate 就贴进去"**, 跑过了 test 但解释 DP 思路时嗑嗑巴巴。这是 AI 面试最大失分模式 -- 算法**选你 hold 得住的那一档**, 不是选最优那档。

---

## 1. 题面 + 关键常数

```
牌库     : 36 张 = 1..9 各 4 张 (四花色)
初始台面 : 随机抽 16 张
回合     : 选 3 张和=15 -> 拿走得 15 分 -> 牌库随机补 3 张 (台面回到 16)
终止     : 台面再也凑不出 valid triple = game over
完美局   : 12 对 = 12 * 15 = 180 分 (拿光 36 张牌)
```

**合法 rank multiset 13 种** (枚举出来面试官看到你做过功课):

```
(1,5,9)(1,6,8)(1,7,7)
(2,4,9)(2,5,8)(2,6,7)
(3,3,9)(3,4,8)(3,5,7)(3,6,6)
(4,4,7)(4,5,6)
(5,5,5)
```

**注意花色维度**: 上面 13 种是 **rank multiset**。如果澄清第 2 问 (花色须互异) 答 yes, 同一 rank multiset 的物理牌组合数差异很大:

- `(5,5,5)`: $\binom{4}{3} = 4$ 种花色组合
- `(1,7,7)`: $4 \times \binom{4}{2} = 24$ 种
- `(1,5,9)`: $4 \times 4 \times 4 = 64$ 种

实现层面: rank-level DP 决定 "拿哪个 multiset", suit filter 单独函数从台面挑具体物理牌。**两件事解耦**, 见 §5 Pitfalls。

---

## 2. 澄清五问 (开场必问 -- 这是 senior signal)

不澄清直接动键盘 = junior。开场静默 30 秒先把这五问全问完:

1. **数值能否重复?** `(5,5,5)` / `(1,7,7)` 是否合法? (一般答 yes, 但**必须问**)
2. **花色须互异?** 选中的 3 张物理牌是否要求不同花色? (影响 §1 物理牌枚举数 + 实现里 suit filter 的形式)
3. **输入信息?** Strategy 函数的 input 是上帝视角 (整个发牌顺序) 还是只有当前台面 + 牌库 multiset? (一般是后者)
4. **终止条件?** 台面无 valid triple 就 game over, 还是必须等牌库空? (前者; 不必死等)
5. **目标函数?** 最大化**期望分数** vs 最大化**拿到 perfect 180 的概率**? -- 两者不等价: 期望分下宁愿稳拿一个 triple, perfect 概率下可能要赌全清。Bellman 方程形式不同 (见 §4 V 和 P 两个版本), 这一问能让面试官眼前一亮。

---

## 3. 分级解法表 (5 tier 完整保留 -- 讲得出 = 拿分)

| Tier | 思路 | 现场能写? | 现场能解释? | 推荐用法 |
|------|------|---------|-----------|---------|
| 1 Naive Greedy | 扫到第一个 sum=15 的 triple 就拿 | 可 5 行 | 可 一句话 | **Q2 必交** (baseline) |
| 2 Heuristic Greedy | 优先拿"瓶颈 rank" (台面已堆 4 张快卡死的) + "不灵活 rank" (1/9 只在 3 triple 出现, 8/2 同, 见 §10 SCARCITY) | 可 10 行 | 可 scarcity + bottleneck 两条规则 | **Q4 plan A 必交**, 跑 measure 拿数字 |
| 3 Table-only Backtrack | 当前台面 DFS+memo, **忽略补牌随机性** | 勉强 20 行容易出 bug | 勉强 要解释"忽略 refill"的不一致 | **跳过** (现场 ROI 低, 不诚实) |
| 4 Monte Carlo Rollout | 每个候选 triple 跑 K 次随机 rollout 取均值, 选最高的 | 可 15-20 行 | 可 "采样近似 expectation" | **Q4 plan B**, 时间够再加 |
| 5 Expectimax DP | state=(table, deck), 对超几何分布求期望 | 不可 50+ 行错率高 | 不可 多元超几何讲不清楚 | **只口述, 不写** |

**实战节奏 (Q4 ~10-15 分钟内最优策略)**:

1. 先口头报 Tier 1 -> 5 爬升路线, 让面试官看到你脑里有完整 ladder。
2. **先交 Tier 2 (heuristic) + measure 框架** -- 跑 100 局拿数字, 比 Tier 1 baseline 提升明显就行。
3. 如果还有 5+ 分钟, 加 Tier 4 (MC rollout); 没时间就**只口述 MC + Tier 5 DP** 思路。

> **关键反射 (面试官明确表态: "可以用 AI, 但你必须知道代码在做什么")**: Q4 即使没时间写 MC, 也要能口头讲清 state transition (`table' = table - triple + draw, deck' = deck - draw`) + expectation 怎么算 (对 draw 的多元超几何分布加权)。**讲得出来的代码**等于写出来的代码; **写得出来但讲不出来的代码**等于零分。

不要报具体百分比 (除非真跑过 1000 局), 改口"经验上 Tier 2 比 Tier 1 提升明显, MC 接近最优, Tier 5 DP 是理论最优"。面试官追问"你怎么知道 60%?"会很尴尬。

---

## 4. Tier 5 DP 思路 (口述模板, 不写)

State 设计:

```
table[1..9]  : 9-tuple, 每个 rank 当前台面有几张  (取值 0..4)
deck[1..9]   : 9-tuple, 每个 rank 牌库剩几张      (取值 0..4)
state        = (table, deck)  长度 18 的 tuple
```

Bellman 方程 (目标 = 期望分):

```
V(t, d) = 0                                       if no valid triple in t
V(t, d) = max_triple { 15 + E_draw[ V(t', d') ] } otherwise
  其中 t' = t - triple + draw,  d' = d - draw
       draw ~ MultivariateHypergeometric(d, size=min(3, |d|))
```

变体 (目标 = 满分概率, 见 §2 第 5 问):

```
P(t, d) = 0                                      if no valid triple in t and t != ∅
P(∅, ∅) = 1
P(t, d) = max_triple { E_draw[ P(t', d') ] }      otherwise
```

(把 `15 +` 换成乘法递推, 边界 taken 满 = 1。)

**多元超几何分布的 draw**: 从牌库 `d` (总共 |d| 张) 不放回抽 size 张, 每个 rank 抽到 k_i 张的概率 = `prod(C(d_i, k_i)) / C(|d|, size)`。Python 里:
- 直接展开所有可能的 draw 组合 + 算概率 -> 加权求和。
- 或用 `scipy.stats.multivariate_hypergeom` (面试现场不用)。

**复杂度估计 (这里数学要算对)**:
- 朴素上界 `5^9 * 5^9 ≈ 4 * 10^12` -- 太松。
- 用约束 `table[i] + deck[i] + taken[i] = 4`: 每个 rank 的有效 (t, d) 对 = $\binom{4+2}{2} = 15$ (枚举 t+d ≤ 4 的非负整数对), joint state 上界 $= 15^9 \approx 4 \times 10^{10}$。
- 可达状态实测在 $10^7 \sim 10^8$ 量级。
- 每个 state 候选 triple ≤ 13, 每个 triple 的 draw 分布 size=3 的多元超几何只需展开 ≤ ~50 项。
- **Python `lru_cache` 顶不住** ($10^7$+ states + 字典常数), C++ 可行但现场 30 分钟写不完。

**实战取舍**: 现场不写 Tier 5, 写 Tier 4 (MC rollout) 做采样近似 -- 给 lru_cache 喂 (table, deck) 跑 K=30 次 rollout 就够了。

---

## 5. Implementation Pitfalls (对照表 -- 这些坑面试官一眼看出来你犯没犯)

| 坑 / 不要写 | 推荐 / 要写 | 理由 |
|------------|-----------|------|
| `def f(x, memo={}):` | `@lru_cache(maxsize=None)` | 默认参数 dict 共享坑; lru_cache 一行解决 |
| `memo` 当参数到处传 | 全局 lru_cache | 无回退需求, 全局共享更干净 |
| 用 `list` 当 state | 用 `tuple` 当 state | list 不可 hash; lru_cache 要求 hashable |
| rank 和 suit 一起 DP | rank-level DP + suit filter 单独函数 | 对称性 + 灵活性; 把 "凑 sum=15" 和 "花色合法" 解耦 (见 §1 物理牌枚举数差 4-64 倍) |
| 直接 `random.sample(deck, 3)` 当超几何抽 | 按 rank 多项式系数加权枚举 | Tier 5 期望计算需要精确分布, 不是 sample (Tier 4 MC 用 sample OK) |
| 改 state 后忘记 sort tuple | rank 按位置编码 (`table[i]` = rank=i+1 张数) | 位置编码自然有序, 不需 sort |
| **Q1 修 UT 时只改 if 分支** | 保证 **state transition consistency** -- 台面拿走的牌在所有依赖 state 的地方都同步移除 | simulation 类题 Q1 UT-bug 80% 是这个: deck/table/taken 三个 view 漏同步 |

---

## 6. AI 协作 Meta-Prompt (4 步 + 反向坑防呆)

**写 prompt 通则**:
- 每个 prompt 不超过 5 行需求 (Coditioning 反模式 = "一个大 prompt 让 AI 生成整个 word game")。
- 永远先让 AI 给 **stub + signature**, 你 review 接口对了再让填 body。
- AI 写完后做 **1 个具体例子的纸笔 trace** -- 1 分钟能抓 80% 的 AI bug。例: `table=(4,0,0,0,0,0,0,0,4)` (4 个 1 + 4 个 9, 没 5), `find_triples` 应该返回 `[]` 不是 `[(1,5,9)]`。
- **CoderPad 里的 AI 不一定是 frontier 模型**, 可能是小模型, DP/复杂代码错率比大模型高很多 -- 越要 validate。

下面这个脚本可以直接喂给 GPT / Claude, 针对这类"游戏策略 + 期望分析"题型。占位符用 `{{...}}` 标出:

```
═══ 1. CLARIFY ═══
我有一道游戏策略题, 在写代码前请帮我列出所有需要先澄清的问题。
不要动键盘。先问:
  - 数值/物体能否重复?
  - 花色/标签维度是否独立?
  - 输入信息: 上帝视角 vs 局部视角?
  - 随机性来源是什么 (发牌顺序 / 抽样结果)?
  - 终止条件: {{补全候选}}
  - 目标函数: 最大化期望 vs 最大化某事件概率?
然后再开始建模。

═══ 2. TIER ═══
列出该题的 Tier 1 -> 5 解法爬升路线:
  Tier 1: greedy baseline           (能讲一句话)
  Tier 2: heuristic greedy          (优先处理瓶颈 / 不灵活元素)
  Tier 3: brute-force backtrack     (DFS + memo, 忽略随机) -- 可跳过
  Tier 4: Monte Carlo rollout       (每候选跑 K 次随机 rollout)
  Tier 5: 真 expectimax DP          (对随机分布求期望)
为每一档给出: 核心思路 / 何时收敛 / 复杂度估计 / 在面试里的用途。

═══ 3. NARRATE ═══
我要 paste 进 IDE 之前, 先你出 stub + signature -> 我 review ->
你填 body -> 我读 -> 我对面试官讲 "这段在做 X 因为 Y" -> 再 paste。
每段不超过 30 行。

═══ 4. BUFFER ═══
留 5 分钟 validate + 解释。宁可在 Tier 2 (heuristic greedy)
讲透原理, 也不要在 Tier 5 贴爆 150 行 DP 代码自己解释不出来。
最后一问"完美策略每次都能拿满分吗"答: **不能** -- 见 §7 反例。

═══ 5. PAPER-TRACE (反向坑防呆) ═══
AI 写完任何 > 30 行的算法, 在 paste 前我必须:
  - 选 1 个 corner state (e.g. table=(4,0,...,0,4))
  - 在白板/纸上手动 trace 第一个回合
  - 对比 AI 输出, 不一致 = AI 错 (默认错)
```

---

## 7. 一句话防呆

> **"看了一眼没认真 validate 就贴进去"是 AI 面试最大失分点。算法选你 hold 得住的那一档, 不要选最优那档。**

楼主第 4 问就是这么翻车的: AI 出 150 行 DP, 没 validate 就贴, 跑过 test 但解释不出。**反射动作**: AI 给的代码超过 30 行, 强制自己读 + 在白板上画 1 个示例, 再贴进 IDE。讲不出来的代码 = 不存在的代码。

**反例 "完美策略每次都能拿满分吗"** -- 答: **不能**, 但分两层:

- **理论极端**: 初始台面如果是 4 张 9 + 4 张 8 + 4 张 7 + 4 张 6, 最小可能 triple sum = 6+7+8 = 21 > 15, 直接 game over。**P 极低** (`C(16,16)/C(36,16) ≈ 1/7.3 亿`), 但逻辑成立。
- **现实 failure mode**: 中后期补牌随机连抽 4 张同 rank, 把 table 卡死 -- 这才是面试官真想听的"实际 failure mode"。

两个都说 = 既有理论极端又有实际洞察, 面试官更认。

---

## 8. 备考迁移

这道题骨架是"枚举三元组 + 状态压缩 DP / MC 采样近似", 可以打到的题:

- **3Sum / 3Sum Closest / 4Sum** -- 枚举 triple 骨架 + 排序 + 双指针。
- **subset-sum / partition equal subset** -- 枚举 + 状态压缩 DP。
- **Partition to K Equal Sum Subsets (LC 698)** -- 回溯 + 剪枝 + bitmask state。
- **Backtrack + memoization 模板** -- 30 行内手写 (Word Break / Decode Ways / Stickers to Spell Word)。
- **Monte Carlo rollout / MCTS 入门** -- 随机模拟近似最优, 不一定要真 expectimax。"优化题不一定要真最优"在 ML 面试是常考点。
- **State 压缩成 tuple/frozenset** -- 让 `@lru_cache` 工作的标准技巧。
- **Hypergeometric / Multivariate Hypergeometric** -- 不放回抽样的精确分布; 经典在"洗牌"和"卡牌组成"题里出现。

> **Hello Interview / Coditioning 多份近期考报推荐**: 先去做 **Meta career page 的 practice puzzle** -- 多人反映 puzzle 比真题还难。puzzle 1 小时内 90+ 分通关 = 真面试稳了。本笔记的 5-tier 框架 + §10 代码骨架就是为 puzzle 准备的肌肉记忆。

平时刷题强制"先口述再让 AI 写", 训练肌肉记忆 -- 这道题的核心 senior signal 不是写出 DP, 是: (1) **澄清五问先问清** (含 expected vs perfect), (2) **5-tier ladder 口头爬一遍**, (3) **Tier 选你能讲透的那档**, (4) **AI 给 150 行强制 validate**。

---

## 9. 一图流总结

```
4 问递进 (60min round, 主力时间约 30min):
  Q1 修 UT     -> 看 if/else, state transition consistency, 5 分钟过
  Q2 naive     -> 3Sum-style greedy, 跑通就行 (Tier 1)
  Q3 measure   -> 让 AI generate 100-game UT, 自己微调; 报"baseline 量级"
  Q4 优化      -> 别上来就 DP! 走 5-tier ladder (剩 10-15 分钟)
        |
        v
澄清五问 (重复值? 花色? 视角? 终止? **期望分 vs 满分概率?**)
        |
        v
口头 Tier 1 -> 5 爬升 (greedy -> heuristic -> backtrack -> MC -> expectimax)
        |
        v
Q4 plan A: 先交 Tier 2 (heuristic) + measure 跑 100 局拿数字
        |
   有 5+ min -> 加 Tier 4 (MC rollout)
   时间紧   -> 只口述 MC + Tier 5 DP state=(table,deck) + Bellman + 多元超几何
        |
        v
反射: AI 给的代码 > 30 行 = 强制 validate + 纸笔 trace + 讲一遍再贴
        |
        v
"完美策略?" 答: 不能 (4·9+4·8+4·7+4·6 极端反例 P≈1/7.3 亿;
                   现实反例 = 中后期连抽 4 张同 rank 卡死 table)
```

**记住**: 这道题的差异化签名 = (1) **澄清五问先问** (senior signal 第 1 道关, 含 expected-vs-perfect), (2) **5-tier ladder 口头爬完** (展示深度), (3) **Q4 先 Tier 2 拿数字, 时间够再加 Tier 4** (hold 得住), (4) **AI 长代码强制 validate + 纸笔 trace** (不被 AI 反向坑爆), (5) 备考迁移到 3Sum / subset-sum / MC rollout 模板。**算法选你 hold 得住的那一档** -- 这是 AI 面试时代第一原则。

---

## 10. 现场打字模板 (~50 行, 全背)

> AI 面试时间紧, 必须有肌肉记忆。下面 ~50 行覆盖 Tier 1/2/4 + 测量框架, 比"AI 出 150 行 DP"短一倍以上, 每行你都能解释。这就是 senior signal。

### 10.1 全局常量 (5 行)

```python
TRIPLES = [(1,5,9),(1,6,8),(1,7,7),(2,4,9),(2,5,8),(2,6,7),
           (3,3,9),(3,4,8),(3,5,7),(3,6,6),(4,4,7),(4,5,6),(5,5,5)]
TRIPLE_NEEDS = [tuple([t.count(r) for r in range(1,10)]) for t in TRIPLES]
# state convention: table/deck = 9-tuple, table[i] = count of rank (i+1)
```

### 10.2 找所有可用 triple (4 行)

```python
def find_triples(table):
    return [TRIPLES[i] for i, need in enumerate(TRIPLE_NEEDS)
            if all(table[j] >= need[j] for j in range(9))]
```

### 10.3 应用一个 triple + 随机补牌 (10 行)

```python
import random
def apply_triple(table, deck, triple):
    t, d = list(table), list(deck)
    for r in triple: t[r-1] -= 1                      # remove triple
    pool = [r for r, c in enumerate(deck, 1) for _ in range(c)]
    random.shuffle(pool)
    drawn = pool[:min(3, len(pool))]
    for c in drawn:
        d[c-1] -= 1
        t[c-1] += 1
    return tuple(t), tuple(d), 15
```

### 10.4 三档 strategy (~15 行)

SCARCITY 推导: rank `r` 出现在多少个 triple 里, 越少越 scarce, 取倒数。
- rank 1: 出现在 (1,5,9)(1,6,8)(1,7,7) = 3 个 triple -> 1/3
- rank 5: 出现在 5 个 triple -> 1/5
- rank 1/2/8/9 (3 个) > rank 3/4/6/7 (4 个) > rank 5 (5 个)

```python
# Tier 1: greedy
def strategy_naive(table, deck):
    ts = find_triples(table)
    return ts[0] if ts else None

# Tier 2: heuristic — 1/triple_count, scarce ranks 优先 + 卡死的 rank 立即清
SCARCITY = (0, 1/3, 1/3, 1/4, 1/4, 1/5, 1/4, 1/4, 1/3, 1/3)  # index 1..9
def strategy_heuristic(table, deck):
    ts = find_triples(table)
    if not ts: return None
    def score(t):
        s = sum(SCARCITY[r] for r in t)
        s += sum(2 for r in t if table[r-1] == 4)  # clear stuck ranks first
        return s
    return max(ts, key=score)

# Tier 4: MC rollout
def strategy_mc(table, deck, K=30):
    ts = find_triples(table)
    if not ts: return None
    def avg(t):
        total = 0
        for _ in range(K):
            total += rollout(*apply_triple(table, deck, t)[:2])
        return total
    return max(ts, key=avg)

def rollout(table, deck):
    score = 0
    while True:
        ts = find_triples(table)
        if not ts: return score
        t = random.choice(ts)
        table, deck, pts = apply_triple(table, deck, t)
        score += pts
```

### 10.5 跑 100 局 (5 行 -- 框架, 发牌细节让 AI 写)

```python
def measure(strategy, n=100):
    return [simulate_one(strategy) for _ in range(n)]

def simulate_one(strategy):
    deck = [4]*9
    table = list(deck)  # init: deal 16 cards from full deck (AI 写发牌)
    # ... loop: while find_triples(table): apply strategy, accumulate score
```

**关键**: 上面 ~50 行就是你的肌肉记忆。Q2 交 §10.4 Tier 1 + §10.5 measure (10 行); Q4 交 §10.4 Tier 2 + 跑数字 (~25 行); 时间够再加 Tier 4 (~15 行)。**比 150 行 DP 短一倍, 每行都能解释**。
"""


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines down to 2. Forbids accidental [UPDATED] reports caused
    by trailing-whitespace drift or platform line-ending differences.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _assert_required_keywords(description: str) -> None:
    """Abort if any REQUIRED-KEYWORD is missing from the description."""
    for kw in REQUIRED_KEYWORDS:
        if kw not in description:
            raise RuntimeError(
                f"[META-ANC-8] missing keyword {kw!r} -- regenerate"
            )


def _assert_no_emoji(description: str) -> None:
    """Project rule: no emoji characters in content."""
    for ch in description:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1FAFF
            or 0x1F000 <= cp <= 0x1F2FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"[META-ANC-8] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_card_game_sum15() -> int:
    """Insert or update the Card Game Sum-15 drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-8] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-8] expected Meta company_id=31, got {company_id}"
            )
        print(f"[OK] target company: id={company_id} name='Meta'")

        existing = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .first()
        )

        normalized_new = _normalize(DESCRIPTION)

        if existing is None:
            problem = Problem(
                title=TITLE,
                description=DESCRIPTION,
                difficulty=DIFFICULTY,
                pattern=PATTERN,
                category=CATEGORY,
                source=SOURCE,
                description_source=DESCRIPTION_SOURCE,
                is_completed=False,
                comfort_level=0,
            )
            db.add(problem)
            db.flush()
            pid = int(problem.id)
            print(
                f"[INSERT] problems id={pid} title={TITLE!r} "
                f"len={len(DESCRIPTION)}"
            )
        else:
            pid = int(existing.id)
            normalized_old = _normalize(existing.description or "")
            if normalized_old == normalized_new:
                print(
                    f"[NOOP] problems id={pid} description "
                    f"semantically identical (len={len(DESCRIPTION)})"
                )
            else:
                old_len = len(existing.description or "")
                existing.description = DESCRIPTION
                existing.title = TITLE
                existing.difficulty = DIFFICULTY
                existing.category = CATEGORY
                existing.description_source = DESCRIPTION_SOURCE
                print(
                    f"[UPDATED] problems id={pid} old_len={old_len} "
                    f"new_len={len(DESCRIPTION)} "
                    f"delta={len(DESCRIPTION) - old_len:+d}"
                )

        existing_tag = (
            db.query(ProblemCompanyTag)
            .filter(
                ProblemCompanyTag.problem_id == pid,
                ProblemCompanyTag.company_id == company_id,
            )
            .first()
        )
        if existing_tag is None:
            tag = ProblemCompanyTag(
                problem_id=pid,
                company_id=company_id,
                relevance="core",
                source="manual",
                notes="Meta AI-Native Coding 2026-05-01 inventory",
            )
            db.add(tag)
            print(
                f"[INSERT] problem_company_tags problem_id={pid} "
                f"company_id={company_id} relevance=core"
            )
        else:
            print(
                f"[NOOP] problem_company_tags problem_id={pid} "
                f"company_id={company_id} already present"
            )

        db.commit()

        final = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .one()
        )
        print(
            f"[VERIFY] problems id={final.id} pattern={final.pattern!r} "
            f"source={final.source!r} desc_len="
            f"{len(final.description or '')}"
        )
        return int(final.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upsert_meta_anc_card_game_sum15()
