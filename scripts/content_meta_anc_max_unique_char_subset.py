"""[META-ANC-2] Max Unique Character Subset drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the Max
Unique Character Subset Meta AI-Native Coding question. Distills the
backtracking -> state-compression DP ladder + the XOR-prev trick that
collapses the prev pointer Node into a single integer dp value.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='bitmask_dp_subset_sum'). The pattern column is the STABLE SLUG
-- never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_max_unique_char_subset --> is embedded at the
top of the description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 2, lines 129-150).
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

SLUG = "meta_anc_max_unique_char_subset"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "bitmask_dp_subset_sum"
TITLE = "Meta AI-Native Coding - Max Unique Character Subset (backtrack -> bitmask DP)"
DIFFICULTY = "hard"
CATEGORY = "algorithm"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "XOR",
    "bitmap",
    "state-compression",
    "snapshot",
    "anagram",
    "不相交",
]

DESCRIPTION = SENTINEL + r"""

# Max Unique Character Subset -- Meta AI-Native Coding (backtrack -> bitmask DP)

> **题型**: 同一道题 4 问递进 (Q1-Q4)；前两问允许暴力回溯，后两问要求处理万级单词的状态压缩 DP。
> **场景**: Meta AI-Native Coding 现场题——Q3-Q4 明确鼓励 AI 协同，重点考察"你能否精确指挥 AI 写出 state-compression DP 并讲清 XOR-prev 这一步"。
> **评分信号**: 能独立讲出"不相交约束让 OR 退化成 XOR"= senior signal；只会 backtracking = baseline。

---

## 1. 题面

给定一个单词列表 `words`，从中选出一个**子集** `S`，使得 `S` 内任意两个单词的字母两两不重叠（disjoint），且 `S` 覆盖的不同字母总数最多。返回这个**单词子集本身**（不是字母数）。

- 字母表: 26 小写字母 (扩展可到 36 位含数字)
- 数据规模: Q1-Q2 玩具尺寸 (~12 词, 暴力可过)；Q3-Q4 万级单词。
- 朴素 backtracking 跑不过 Q3-Q4，必须升级到 **state-compression DP** (状态压缩动态规划)。

---

## 2. 解法谱系表

| 档位 | 思路 | 状态空间 | 复杂度 | 适用条件 |
|------|------|----------|--------|----------|
| Q1-Q2 Backtracking | DFS 枚举每个单词选/不选；用当前已用字母 mask 剪枝 | 路径树 | $O(2^n)$ | $n \le 20$，玩具尺寸 |
| Q1-Q2 + popcount 剪枝 | mask 满 26 位立即 return | 同上 | $O(2^n)$ 但常数小 | 同上 |
| Q3-Q4 **state-compression DP** | dp: dict[mask, word_index]，遍历 word，内层遍历 dp snapshot | $O(2^{26})$ 上限，实际 reachable mask 远稀疏 | $O(n \cdot 2^{26})$ 上限 / 实际 $O(n \cdot R)$，$R$ = reachable mask 数 | 万级 $n$ |
| Q3-Q4 + anagram dedup | 同 bitmap 的多个 anagram 只保留一个代表 | 同上但 $n_{eff}$ 减小 | 同上 | 实战必加，$n$ 降几倍 |
| (扩展) 36 位含数字 | mask 改 Python `int` (任意精度)；剪枝改 `(1<<36)-1` | 状态空间巨大但稀疏 | 同上 | 字母+数字混合 |

**关键洞察 1**: $2^{26} \approx 6.7 \times 10^7$，看似爆炸；但 reachable mask 由输入单词的 bitmap 张成的 OR 闭包决定，实战中远稀疏——这是 DP 能跑过的根本原因。

**关键洞察 2**: 对万级数据，$O(n \cdot 2^n)$ 完全不可行，$O(n \cdot 2^{26})$ 是把指数从 $n$ 移到 26（字母表大小）——**字母表是常数**，所以复杂度本质是线性 of n，乘一个大常数。

---

## 3. 核心 元规律：XOR-prev 技巧 (这一步是 senior signal)

朴素 DP 设计会想：用 `dp: dict[mask, Node]`，`Node` 存 `(word_index, prev_pointer)` 以便重建路径。**坏处**：每个 mask 持有 Node 对象，内存爆。

**洞察**: DP 转移要求 `prevMask & wordMask == 0`（**不相交**约束）。这意味着：

```
prevMask | wordMask == prevMask + wordMask == prevMask ^ wordMask
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                  (因为没有 1 位重合，所以三种二进制运算等价)
```

所以 `newMask = prevMask | wordMask = prevMask ^ wordMask`，**两边再 XOR 一次 wordMask** 即可反推：

```
prevMask = newMask ^ wordMask
```

**结论**: dp value 可以**只存 word_index** (单个 int)，不需要 `prev` 指针——重建路径时用 `cur ^= masks[w]` 反推。这把内存从 `O(R) * sizeof(Node)` 压到 `O(R) * sizeof(int)`。

**面试金句** (Section 8 一句话): **"不相交约束让 OR 退化成 XOR，prev 指针折叠进 XOR 关系，dp value 就是一个整数。"**——这一句让面试官立刻知道你不仅会写 DP，还看清了**这个 DP 特有的代数结构**。比任何复杂代码都更能体现思考深度。

**反例（什么时候不能用）**: 若题目允许字母重叠（`prevMask | wordMask` 时存在多个不同 prevMask 都能产生同一 newMask），反推不再唯一，必须存指针——所以这是**约束特定**的优化，不通用。

---

## 4. 关键代码 idiom

**(a) Bitmap 编码 + popcount filter + anagram dedup（预处理 3 步，自己写不让 AI 写）：**

```python
def preprocess(words):
    # Return (uniq_words, masks): bitmap-deduped, self-disjoint words only.
    seen_masks = {}  # mask -> representative word
    for w in words:
        m = 0
        for c in w:
            m |= 1 << (ord(c) - ord('a'))
        # 自身含重复字母的剔除 (popcount(m) != len(w))
        if bin(m).count('1') != len(w):
            continue
        # 相同 bitmap 的 anagram 只保留一个代表
        if m not in seen_masks:
            seen_masks[m] = w
    uniq_words = list(seen_masks.values())
    masks = [m for m in seen_masks.keys()]
    return uniq_words, masks
```

**(b) State-compression DP 主循环（snapshot iteration 是 0/1 背包性质保证）：**

```python
def solve(words):
    uniq_words, masks = preprocess(words)
    dp = {0: -1}  # mask -> word_index (将我们带到这个 mask 的最后一个单词)
    FULL = (1 << 26) - 1

    for i, m in enumerate(masks):
        # 关键：遍历 dp 的 snapshot，避免同一单词在本轮被重复使用 (0/1 背包性)
        for prev_mask in list(dp.keys()):
            if prev_mask & m == 0:  # disjoint 约束
                new_mask = prev_mask | m  # == prev_mask ^ m
                if new_mask not in dp:  # 同一 mask 不重复写入
                    dp[new_mask] = i
                    # 剪枝: mask 覆盖全部 26 位立即返回
                    if new_mask == FULL:
                        return reconstruct(uniq_words, masks, dp, FULL)

    best_mask = max(dp.keys(), key=lambda k: bin(k).count('1'))
    return reconstruct(uniq_words, masks, dp, best_mask)
```

**(c) 路径重建 (XOR-prev 反推)：**

```python
def reconstruct(uniq_words, masks, dp, best_mask):
    # 从 best_mask 反推路径: cur ^= masks[w] 直到 cur == 0.
    path = []
    cur = best_mask
    while cur != 0:
        w = dp[cur]
        path.append(uniq_words[w])
        cur ^= masks[w]  # XOR 反推 prev_mask
    return path
```

---

## 5. 预处理 3 步 cheat sheet

| 步骤 | 做什么 | 为什么 |
|------|--------|--------|
| 1. Bitmap 编码 | 每个 word -> 26 位 int (`mask |= 1 << (ord(c)-ord('a'))`) | 把字符串相交检查 O(L) 降到位运算 O(1) |
| 2. Popcount filter | 丢弃 `popcount(mask) != len(word)` 的 word（自身含重复字母） | 这种 word 永远不能进 S（自己跟自己不相交都做不到），早剔除 |
| 3. Anagram dedup | 相同 bitmap 的多个 word（如 `"abc"`/`"bca"`/`"cab"`）只保留一个代表 | 它们对 dp 状态空间贡献完全相同；保留多个只是浪费内层循环 |

**实战量级感**: 万级 words，预处理后通常剩 30%-60%，dp 的 reachable mask 数从 $2^{26}$ 上限缩到几万到百万级。

---

## 6. 剪枝 + 边界

- **早停**: 一旦 `mask == (1<<26)-1`（全字母覆盖）立即 `return`——上界已达，无需继续。
- **同一 mask 不重复写入** dp: 若某 word_i 路径已到达 mask m，后续别的 word_j 也能到 m 时**不更新**——因为目标只看 popcount(mask)，谁先到都一样，重写徒增内存。
- **snapshot iteration**: `for prev_mask in list(dp.keys())` 而不是直接 `for prev_mask in dp`——前者拷贝当前 keys 防止本轮新加的 mask 被同一 word 二次使用（0/1 背包不允许同 word 用两次）。
- **扩展到 36 位**: 题目允许字母+数字时 mask 用 Python `int`（无 32/64 位限制），FULL = `(1<<36)-1`，剪枝条件改即可，其它代码不变。

---

## 7. AI 协同 prompt 模板（照搬源材料金句段，完整保留）

> 我有一个"最大唯一字符子集"问题：给定单词列表，选出一个子集使得子集内所有单词的字母两两不重叠，且覆盖的不同字母总数最多。返回这个单词子集本身（不是字母数）。
>
> 数据规模可达万级单词，请用状态压缩 DP 实现，并满足以下约束：
>
> 1. **预处理**: (a) 把每个单词转成 26 位 bitmap；(b) 丢弃自身包含重复字母的单词（即 `popcount(mask) != len(word)`）；(c) 对相同 bitmap 的单词（包括 anagram）只保留一个代表。
>
> 2. **DP 设计**: 用 `dp: dict[int, int]` 存"已达到的 mask -> 把我们带到这个 mask 的单词 index"。不要用带 prev 指针的 Node 类；利用一个数学性质来省内存——因为 DP 转移要求 `prevMask & wordMask == 0`，所以 `newMask = prevMask | wordMask = prevMask ^ wordMask`，两边再异或 wordMask 即可反推 prevMask。
>
> 3. **转移**: 对每个单词外层循环，内层遍历当前 dp 的 snapshot（避免同一单词被重复使用——这是 0/1 背包性质）。同一个 mask 不要重复写入。
>
> 4. **剪枝**: 一旦 mask 覆盖全部 26 位（或题目约定的 36 位包含数字时取 `(1<<36)-1`）立即停止并返回。
>
> 5. **路径重建函数**: 从 best_mask 出发，循环执行 `w = dp[cur]; path.append(words[w]); cur ^= masks[w]`，直到 `cur == 0`。
>
> 请用 Python 实现，关键步骤加注释解释为什么这样写（特别是 XOR 反推那一步和 snapshot 那一步），最后给一个小测试用例验证既能输出最大字母数也能正确重建出单词列表。

**配套元规律口语版**: 喂这段 prompt 之前先口头交代 _"已知朴素 backtracking 写法跑不过大数据集，所以引导你给出 state-compression DP"_——这句话给 AI 提供"为什么不接受朴素解"的 context，让它跳过 baseline 直接给目标解法。

---

## 8. 一句话 元规律 (面试用来秀洞察)

> **"这道题的不相交约束让 OR 退化成 XOR——dp 转移上 `prevMask | wordMask = prevMask ^ wordMask`，所以可以把 prev 指针折叠进 XOR 关系，dp value 就是一个整数。"**

讲完这句紧跟一个反例: _"如果允许重叠（比如 prevMask | wordMask 时存在多个 prevMask 都能产生同一 newMask），反推不再唯一，就必须存指针。"_

这两句话连起来——展示**洞察**+**洞察的边界**——是这道题最高分的回答模式。

---

## 9. AI 协同分工对照表

| 让 AI 做 | 自己做更快/更靠谱 |
|----------|-------------------|
| 把 prompt 第 7 节那段一次性翻译成代码 | XOR 反推那一步的注释（这是 senior signal，要自己讲） |
| 生成单元测试和边界 case | snapshot iteration 为什么 list(...) 拷贝（0/1 背包性，自己讲） |
| 解释 popcount 在 CPython 的实现（`bin().count('1')` vs `int.bit_count()`） | 状态空间的复杂度上界推导（$2^{26}$ vs reachable） |
| 给一个 36 位扩展版本 | "不相交让 OR 退化成 XOR" 这句金句的口头表述节奏 |

底线: **AI 给的复杂度公式自己复算一遍**。state-compression DP 的复杂度公式 AI 经常写成 $O(n \cdot 2^n)$ 或漏掉 reachable 稀疏性这一项，让它 review 而非主导。
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
                f"[META-ANC-2] missing keyword {kw!r} -- regenerate"
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
                f"[META-ANC-2] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_max_unique_char_subset() -> int:
    """Insert or update the Max Unique Char Subset drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-2] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-2] expected Meta company_id=31, got {company_id}"
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
    upsert_meta_anc_max_unique_char_subset()
