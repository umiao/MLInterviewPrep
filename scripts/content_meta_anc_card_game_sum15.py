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

# Card Game Sum-15 -- Meta AI-Native Coding (5-tier ladder + Expectimax DP + AI-collab)

> **Guiding Principles**: dedup (留主战场, 砍重复); tablify (multiset / 五问 / 5-tier / Pitfalls 全表格); 平铺直叙 (说一次就够, 删 senior signal puffery); 代码上移, 理论作注解。

## §0 题型

36 张牌 (1..9 各 4, 四花色), 初始台面 16 张; 每回合选 3 张 sum=15 拿走得 15 分 + 牌库随机补 3 张, 凑不出 = 终止。完美局 12 组 = 180。Q1 修 UT / Q2 naive / Q3 跑 100 局 / Q4 优化。

**60min round 时间预算**: orientation + 修 UT 之后, 主实现 + 优化只剩约 30 分钟。**Q1 必须 <=5 分钟搞定**, **Q4 才有 10-15 分钟**。这是后面所有 Tier 选档决策的硬约束。

## §1 合法 triple (rank multiset, 13 种)

| anchor | multisets |
|---|---|
| 1 | (1,5,9) (1,6,8) (1,7,7) |
| 2 | (2,4,9) (2,5,8) (2,6,7) |
| 3 | (3,3,9) (3,4,8) (3,5,7) (3,6,6) |
| 4 | (4,4,7) (4,5,6) |
| 5 | (5,5,5) |

花色互异时同 multiset 物理组合数差 4-64 倍 (e.g. (5,5,5)=4, (1,7,7)=24, (1,5,9)=64), suit filter 与 rank-level DP 解耦。

## §2 澄清五问

| # | 问 | 默认答 | 影响 |
|---|---|---|---|
| 1 | 数值能否重复? | yes | (5,5,5) / (1,7,7) 是否合法 |
| 2 | 花色须互异? | 一般 yes | suit filter + 物理组合数 |
| 3 | input 视角? | 局部 (台面+牌库 multiset) | 上帝视角才能真 expectimax |
| 4 | 终止条件? | 台面无 valid triple | 不必等牌库空 |
| 5 | 目标函数? | 期望分 vs 满分概率 | Bellman 形式不等价 (V vs P) |

第 5 问关键: 期望分下宁愿稳拿 triple, 满分概率下可能要赌全清。

## §3 现场代码模板 (~50 行)

```python
TRIPLES = [(1,5,9),(1,6,8),(1,7,7),(2,4,9),(2,5,8),(2,6,7),
           (3,3,9),(3,4,8),(3,5,7),(3,6,6),(4,4,7),(4,5,6),(5,5,5)]
TRIPLE_NEEDS = [tuple([t.count(r) for r in range(1,10)]) for t in TRIPLES]
# state: table/deck = 9-tuple, table[i] = count of rank (i+1)

def find_triples(table):
    return [TRIPLES[i] for i, need in enumerate(TRIPLE_NEEDS)
            if all(table[j] >= need[j] for j in range(9))]

import random
def apply_triple(table, deck, triple):
    t, d = list(table), list(deck)
    for r in triple: t[r-1] -= 1
    pool = [r for r, c in enumerate(d, 1) for _ in range(c)]   # 用 d 不用 deck (防御性)
    random.shuffle(pool)
    drawn = pool[:min(3, len(pool))]
    for c in drawn:
        d[c-1] -= 1; t[c-1] += 1
    return tuple(t), tuple(d), 15

# SCARCITY: rank r 出现在 k 个 triple 里取 1/k
# 1/2/8/9 各 3 个 -> 1/3; 3/4/6/7 各 4 个 -> 1/4; 5 出现 5 个 -> 1/5
SCARCITY = (0, 1/3, 1/3, 1/4, 1/4, 1/5, 1/4, 1/4, 1/3, 1/3)

def strategy_naive(table, deck):                          # Tier 1
    ts = find_triples(table)
    return ts[0] if ts else None

def strategy_heuristic(table, deck):                      # Tier 2
    ts = find_triples(table)
    if not ts: return None
    def score(t):
        s = sum(SCARCITY[r] for r in t)
        s += sum(2 for r in t if table[r-1] == 4)         # 卡死 rank 优先清
        return s
    return max(ts, key=score)

def rollout(table, deck):
    score = 0
    while True:
        ts = find_triples(table)
        if not ts: return score
        table, deck, pts = apply_triple(table, deck, random.choice(ts))
        score += pts

def strategy_mc(table, deck, K=30):                       # Tier 4 (Monte Carlo)
    ts = find_triples(table)
    if not ts: return None
    def avg(t):
        return sum(rollout(*apply_triple(table, deck, t)[:2]) for _ in range(K))
    return max(ts, key=avg)

def simulate_one(strategy):
    deck = [4]*9
    table = list(deck)  # 初始发 16 张, 发牌细节让 AI 写
    # while find_triples(table): apply strategy, accumulate score

def measure(strategy, n=100): return [simulate_one(strategy) for _ in range(n)]
```

Q2 交 Tier 1 + measure; Q4 交 Tier 2 + 跑数字; 时间够再加 Tier 4。

## §4 5-tier 分级

| Tier | 思路 | 写? | 讲? | 用 |
|---|---|---|---|---|
| 1 Naive Greedy | 第一个 sum=15 | 5 行 | 一句 | Q2 baseline |
| 2 Heuristic Greedy | scarcity + bottleneck | 10 行 | 两规则 | Q4 plan A |
| 3 Table Backtrack | DFS+memo, 忽略 refill | 20 行易 bug | 不诚实 | 跳过 |
| 4 Monte Carlo Rollout | 每候选 K 次随机模拟取均值 | 15-20 行 | 采样近似 expectation | Q4 plan B |
| 5 Expectimax DP | state=(table,deck), 多元超几何加权 | 50+ 行 | 讲不清 | 只口述 |

Q4 先口头报 ladder 1->5, 然后交 Tier 2 + measure 拿数字; 不报具体百分比 (除非真跑过 1000 局), 改口"Tier 2 比 Tier 1 提升明显, MC 接近最优"。

## §5 Tier 5 DP 口述模板

State: table[1..9] + deck[1..9], joint 18-tuple。

Bellman (期望分):
```
V(t,d) = 0                                if no valid triple in t
V(t,d) = max_triple { 15 + E_draw[V(t',d')] }
  t' = t - triple + draw,  d' = d - draw
  draw ~ MultivariateHypergeometric(d, size=min(3,|d|))
```

满分概率版: `15 +` 换乘法递推, P(empty,empty)=1。

多元超几何: 从 d 不放回抽 size 张, 每 rank 抽 k_i 张概率 = `prod(C(d_i,k_i)) / C(|d|,size)`, 枚举所有 draw 组合加权求和。

复杂度: t[i]+d[i]+taken[i]=4 约束 -> 每 rank 有效 (t,d) 对 15 个 -> joint 上界 15^9 ~ 4*10^10, 实测可达态 10^7-10^8。Python lru_cache 顶不住, C++ 可行但现场 30min 写不完, 故只口述, 改写 Tier 4 MC。

## §6 Pitfalls

| 不要 | 要 | 理由 |
|---|---|---|
| `def f(x, memo={})` / memo 传参 / list state | `@lru_cache` + tuple state | 默认 dict 共享坑; lru_cache 要 hashable |
| rank+suit 一起 DP | rank-level DP + suit filter 单独函数 | 物理组合差 4-64 倍, 解耦 |
| `random.sample(deck,3)` 算期望 | Tier 5 按多项式系数枚举; Tier 4 sample OK | 期望需精确分布 |
| Q1 UT 只改 if 分支 | 检查 deck/table/taken 三 view 同步 | simulation Q1 bug 80% 是这个 |

## §7 AI 协作 4 步

1. **Clarify** -- 让 AI 先列澄清问题, 不动键盘。
2. **Ladder** -- 让 AI 给 Tier 1->5 思路 + 复杂度。
3. **Stub -> review -> body -> 讲一遍 -> paste** -- 每段 <=30 行, 能讲"在做 X 因为 Y"才贴。
4. **Validate** -- AI 给 >30 行强制纸笔 trace 一个 corner case (e.g. table=(4,0,0,0,0,0,0,0,4), find_triples 应返回 [] 不是 [(1,5,9)])。CoderPad 的 AI 可能是小模型, DP 错率高。

一句话 prompt: "先列澄清问题; 给 Tier 1->5 ladder + 复杂度; 然后只给 stub + signature, 我 review 后再填 body, 每段 <=30 行。"

## §8 反例 -- "完美策略每次都拿满分吗?"

不能:
- **理论极端**: 初始 4*9+4*8+4*7+4*6, 最小 triple sum=21>15, 直接终止。P=C(16,16)/C(36,16) ~ 1/7.3 亿。
- **现实 failure**: 中后期补牌连抽 4 张同 rank 卡死 table。

两个都答 = 既有理论极端又有实际洞察。

## §9 临场 timeline (4 行)

```
Q1 修 UT (<=5min) -> Q2 Tier 1 + measure -> Q3 跑 100 局
-> Q4 (10-15min): 报 ladder 1->5 -> 交 Tier 2 + measure -> 时间够加 Tier 4
反射: AI > 30 行 = 强制 validate + 纸笔 trace + 讲一遍再贴
"完美策略?" 答: 不能 (理论极端 P~1/7.3 亿; 现实连抽 4 同 rank 卡死)
```

---

## 附录: 备考迁移

骨架 = 枚举三元组 + 状态压缩 DP / MC 采样近似:
- 3Sum / 3Sum Closest / 4Sum
- Subset-sum / Partition Equal Subset / Partition to K Equal Sum (LC 698)
- Backtrack + memoization (Word Break, Decode Ways, Stickers to Spell Word)
- Monte Carlo rollout / MCTS 入门 -- "优化题不一定要真最优"在 ML 面常考
- State 压缩成 tuple/frozenset 喂 @lru_cache
- Multivariate Hypergeometric -- 不放回抽样精确分布
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
