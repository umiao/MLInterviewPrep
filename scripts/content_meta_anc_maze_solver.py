"""[META-ANC-1] Maze Solver drawer (Meta AI-Native Coding inventory).

Inserts ONE problems row that becomes the db://<id> drawer for the Maze
Solver Meta AI-Native Coding question (5-question ladder, Q1 print-priority
through Q5 bomb-mask).

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='bfs_state_bitmask'). The pattern column is the STABLE SLUG --
never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_maze_solver --> is embedded at the top of the
description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md (Section 1).
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

SLUG = "meta_anc_maze_solver"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "bfs_state_bitmask"
TITLE = "Meta AI-Native Coding - Maze Solver (5-question ladder)"
DIFFICULTY = "hard"
CATEGORY = "algorithm"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "bitmask",
    "BFS",
    "blast",
    "复杂度",
    "visited",
    "状态空间",
]

DESCRIPTION = SENTINEL + r"""

# Maze Solver -- Meta AI-Native Coding (5-question ladder)

> **题型**: codebase-debug + 算法迭代；同一份 Maze repo 上 4-5 个递进任务，难度由浅入深。
> **场景**: Meta AI-Native Coding 现场题——前两关通常禁用 AI；后两关明确鼓励 AI 协同。
> **评分**: Q1-Q3 通过 = baseline；Q4 钥匙 + bitmask = 中档；Q5 炸弹 + 派生信息 = senior 信号。

---

## 1. 5-question ladder

| Q | 任务 | 关键考点 | 难度 |
|---|------|----------|------|
| Q1 | 基础修复 + 格式控制（**不**让 AI 写） | 起终点 / 路径符 (`*`) 显示优先级 + diff 严格匹配 | Easy |
| Q2 | 基础算法修复 (**Breadth-First Search** (BFS, 广度优先) / **Depth-First Search** (DFS, 深度优先)) | 缺 `visited` 死循环；入队前去重 | Easy |
| Q3 | 移动规则限制（指令门 `> < ^ v`） | 改 `get_neighbors` 按字符裁剪方向集合 | Medium |
| Q4 | 钥匙与门 (Key & Door) | `visited = (x, y, mask)`，可调 Claude Opus 协同 | Medium |
| Q5 | 炸弹 (Bomb) 半径两格炸墙 | `bomb_mask` + 派生信息查表，AI 写 `get_affected_area` | Hard |

Q1 的坑是起点 / 终点符号被路径符 `*` 覆盖、Windows / Unix 换行差异让 diff 翻车，**不是**算法。Q4-Q5 才进入 state-bitmask 的核心战场。

---

## 2. 解法谱系表（5 档复杂度）

| 档位 | 状态空间 V | 每状态代价 | 总复杂度 | 适用条件 |
|------|------------|------------|----------|----------|
| Vanilla BFS（无 visited） | 路径树展开 $(4+k)^n$ | $O(1)$ 邻居 | 指数爆炸 | 玩具尺寸 |
| + `visited (x, y)` | $W \cdot H$ | $\times 4$ 邻居 | $O(WH)$ | Q2 baseline |
| + 指令门 | $W \cdot H$ | $\times 1\sim 4$（裁剪） | $O(WH)$ | Q3，复杂度不变 |
| + 钥匙 bitmask | $W \cdot H \cdot 2^k$ | $\times 4$ | $O(WH \cdot 2^k)$ | Q4，$k \le 8$ 任意；$k \ge 25$ 放弃 |
| + 炸弹 bomb_mask | $W \cdot H \cdot 2^k \cdot 2^b$ | $\times 4$ | $O(WH \cdot 2^k \cdot 2^b)$ | Q5，$b \le 8$ ok |

**关键洞察**: 加 `visited` 之后路径长度从复杂度里**消失**——`(4+k)^n` 是无去重 DFS 路径树的展开，加状态去重就降级成线性。**真正的指数爆炸来源是状态维度的增加**（多一种机制 → 多一个 mask），不是邻接数。

实战量级感：$k \le 8$ 时 $2^k \le 256$，bitmask BFS 随便跑；$k \approx 15\sim 20$ 紧张要看网格大小；$k \ge 25$ 换启发式或 **Travelling Salesman Problem** (TSP, 旅行商问题)-like 建模。

---

## 3. 状态空间洞察（一定要能口头讲清楚）

- **状态空间维度** $V$：你的 `visited` 集合最多容纳多少不同状态。Vanilla 是 $W \cdot H$；带 $k$ 把钥匙是 $W \cdot H \cdot 2^k$；带 $b$ 个一次性炸弹是 $W \cdot H \cdot 2^k \cdot 2^b$。
- **每状态处理代价**：出队后枚举多少邻居（4 邻接 / 8 邻接 / 马步 ×8）。常数因子可以吸收进大 O，但显式写出来便于变种适配。
- **派生信息**：`bomb_mask` 决定哪些墙被炸毁——这是**确定性派生**，**不进** `visited`。本质：状态里只存触发开关 (`bomb_mask`)，墙是否消失靠查表函数从 mask 反推。
  - 朴素错法：把"被炸毁的格子集合"塞进状态 → 5 格 × 32 局部组合 = 32 倍 visited 爆炸，且不通用。
  - 正确做法：状态空间从"5 格 × 32 种局部组合"降到"$b$ 个炸弹 × $2^b$"，可扩展到任意爆炸半径——半径 5 还是 50，状态空间不变。

---

## 4. 核心 idiom 代码段（3 块要练到肌肉记忆）

**(a) Bitmask key 编解码**（自己写，不让 AI 帮——浪费时间且容易抄错位运算）：

```python
# 拿到钥匙 c (假设 c 是 'a'-'z')
new_mask = mask | (1 << (ord(c) - ord('a')))

# 检查持有钥匙 c（用于开门）
has_key = mask & (1 << (ord(c) - ord('a')))

# visited 用完整状态做 key（钥匙单调不减，但 BFS 仍按 (x, y, mask) 去重）
visited = set()
visited.add((x, y, mask))
```

**(b) Bomb-mask wall lookup helper**（让 AI 写 `compute_blast_area`，自己写 `is_wall` 查表）：

```python
# 预处理：每个炸弹 -> 它能炸毁的墙坐标集合
affected_walls = {}  # bomb_id -> set of (x, y)
for bid, (bx, by) in enumerate(bomb_positions):
    affected_walls[bid] = compute_blast_area(bx, by, radius=2)

# 查询：在当前 bomb_mask 下，(x, y) 是否仍是墙
def is_wall(x, y, bomb_mask):
    if grid[x][y] != '#':
        return False
    for bid in range(num_bombs):
        if bomb_mask & (1 << bid) and (x, y) in affected_walls[bid]:
            return False  # 已被炸毁
    return True
```

**(c) Directional `get_neighbors`**（引导砖只裁剪选项集合，BFS 框架不变）：

```python
def get_neighbors(x, y, mask, bomb_mask):
    c = grid[x][y]
    if   c == '>': dirs = [(0, 1)]
    elif c == '<': dirs = [(0, -1)]
    elif c == '^': dirs = [(-1, 0)]
    elif c == 'v': dirs = [(1, 0)]
    else:          dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    # ... 然后正常生成 neighbors
```

---

## 5. AI 协同分工对照表

| 让 AI 做 | 自己做更快 / 更靠谱 |
|----------|---------------------|
| 生成 blast-area / 坐标变换 helper | bitmask 编解码（idiom 化） |
| 把已设计好的状态机翻译成代码 | 状态空间设计（核心考点） |
| 生成边界 case 测试输入 | `visited` 的 debug |
| 解释陌生代码 | 复杂度分析（AI 经常给错式子，让它 review 而非主导） |

底线：**AI 给的复杂度公式一定要自己复算一遍**。状态空间设计能解释清楚比代码跑得过更重要——面试官会追问"为什么要这样建模"。

---

## 6. 速查 cheat-sheet（面试前 5 分钟过一遍）

- [ ] 状态空间维度想清楚了吗？每个新机制都问"要不要加 mask 维度"。
- [ ] `visited` 用的是**完整状态**，不是 `(x, y)`。grep 一遍确认 key 是完整 tuple。
- [ ] bitmask 操作 `|=`, `&` 写对了，没把 `1 <<` 的位置算错。
- [ ] 派生信息（炸弹炸过的墙）通过查表算，不进 `visited`。
- [ ] 起点 / 终点的打印优先级保护了（Q1 diff 翻车点：行尾空格 / Windows-Unix 换行）。
- [ ] 复杂度能口头分析：状态数 × 邻接数，分别说出每一项的含义。
- [ ] $k$ 或 $b$ 太大时，能说出 bitmask 不再可行的临界点和替代思路（启发式搜索 / TSP-like 建模）。
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
                f"[META-ANC-1] missing keyword {kw!r} -- regenerate"
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
                f"[META-ANC-1] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_maze_solver() -> int:
    """Insert or update the Maze Solver drawer; return the problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-1] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-1] expected Meta company_id=31, got {company_id}"
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

        db.refresh(existing if existing else problem)
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
    upsert_meta_anc_maze_solver()
