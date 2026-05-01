"""[META-ANC-7] Find Words Containing drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the
"find words containing other words" Meta AI-Native Coding question.
Distills the 7-part Anthropic-style two-phase guide (analyze without AI,
then optimize with AI) into 8 sections covering core philosophy,
6-step AI collaboration framework, 5-tier solution ladder
(Brute -> KMP -> Prefix Trie -> Substring Trie -> Aho-Corasick ->
Suffix Automaton), AC deep dive, keyword glossary, prompt templates,
anti-patterns, and the perfect interview answer template.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='multi_pattern_string_matching'). The pattern column is the
STABLE SLUG -- never rewritten. The title may evolve. A sentinel HTML
comment <!-- ANC_SLUG: meta_anc_find_words_containing --> is embedded
at the top of the description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 6, lines 450-674).
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

SLUG = "meta_anc_find_words_containing"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "multi_pattern_string_matching"
TITLE = (
    "Meta AI-Native Coding - Find Words Containing Other Words "
    "(5-tier ladder: Brute -> KMP -> Trie -> AC -> Suffix Automaton)"
)
DIFFICULTY = "hard"
CATEGORY = "ml_coding"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "Aho-Corasick",
    "fail",
    "trie",
    "KMP",
    "下界",
    "谱系",
]

DESCRIPTION = SENTINEL + r"""

# Find Words Containing Other Words -- Meta AI-Native Coding (5-tier ladder + AC + AI 协作话术)

> **题型**: 给一个 list of words，找出"包含其他 word 作为子串"的单词。例 `[category, cat]` -> `[category]`。Meta AI-Native Coding 现场题，**两阶段**：(1) 不能用 AI，分析已实现 brute-force 解法的时空复杂度；(2) 给出优化方案 + 预计复杂度（不用 AI），然后实现（这时可以用 AI）。
> **场景**: Anthropic 风格的"分阶段、可控使用 AI"考察。表面是 substring matching，**内核**是考你能否独立分析复杂度、估算理论下界、列多层级解法、精确指挥 AI 写代码、Review AI 输出。
> **AI 时代信号**: 考察重点已从"能不能写出代码"转向"能不能精确指挥 AI 写出正确高效健壮的代码"。分阶段题目就是在筛选能否区分这两种能力。

---

## 1. 核心理念 (5 个关键信号)

AI 时代的 coding 面试不再考"能不能写出代码"，而是考"能不能精确指挥 AI"。考察重点：

1. **独立分析复杂度** -- 不依赖 AI（脱口而出 `o in w` 是 O(1) 是典型翻车点；CPython 实际用 Crochemore-Perrin 变体，最坏 O(|w|*|o|)）
2. **估算理论最优下界** -- 决定优化的天花板（本题下界 Ω(N*L)，比这更激进的优化通常拿不到）
3. **列出多层级解法谱系** -- 清晰对比取舍（5 层 Brute -> KMP -> 前缀 Trie -> 子串 Trie -> AC）
4. **精确表达算法意图给 AI** -- 永远先说算法名，再说实现要求；不要让 AI 猜
5. **Review AI 的输出找问题** -- 真读代码（不是扫一眼）；关注循环边界、index、early exit、复杂度是否真如预期

**底线**: 分阶段题目（一阶段不能用 AI，二阶段可以）就是在筛选能不能区分"独立思考"和"精确指挥"两种能力的人。

---

## 2. 与 AI 协作的 6 步框架

### Step 1: Clarify (澄清问题边界)

不要假设。本题的潜在歧义至少：
- "包含" 是子串、前缀、还是后缀？示例 `[category, cat]` 区分不出
- 区分大小写？unicode / ASCII？
- 词可以重复吗？重复词算"包含自己"吗？
- 词长度上限？list 大小？是否流式？
- 输出是 word 本身，还是 `(word, contained_word)` pair？要去重吗？

**Prompt 模板**: "请列出这道题在题面上不明确、需要澄清的点。" (只列问题，不要给解法 -- 防 AI 越界)

### Step 2: Lower Bound (估算理论下界)

**最关键也最容易被跳过**。下界回答："我做到多快算到顶了？"知道下界，才能判断当前方案是否还有优化空间。

下界来源：
- 输入下界：必须读完所有输入 -> 本题 Ω(N*L)
- 输出下界：必须产出全部结果 -> Ω(|输出|)
- 信息论下界：比较模型下排序 Ω(n log n)
- 不可避免工作：每个潜在答案至少要被验证或排除一次

**本题下界 Ω(N*L)**。任何 N^2*L 或更慢的方案都还有优化空间；trie 路线值得追求；比 N*L 更激进通常达不到。

### Step 3: Solution Ladder (列出解法谱系)

从朴素到精妙，列 3-5 层，每层给复杂度。这是给面试官看你思维广度的最好方式。具体见 §3。

### Step 4: Pick Sweet Spot (选型 -- 主动 propose tradeoff)

不一定选最优。要平衡：实现复杂度 vs 性能提升 / 出错风险 vs 时间预算 / 面试官想看的深度。

**话术示例**: "我可以给您实现 trie 子串版，O(N*L^2)，30 行代码确定能跑过；或者升级到 Aho-Corasick，O(N*L)，但代码 80+ 行。考虑到面试时间，我建议先实现前者验证逻辑正确，时间还充足再升级。可以吗？"

**主动提出 trade-off 比沉默地选一个方案更专业** -- 这是 senior signal。

### Step 5: 分工原则 (你做 vs AI 做)

| 你做                        | AI 做             |
|-----------------------------|-------------------|
| 选算法、设计方案            | 写样板代码        |
| 推导复杂度                  | 处理语法细节      |
| 列边界条件                  | 生成测试用例      |
| Review 代码逻辑             | 解释陌生 API      |
| 验证最终复杂度              | 重构、改名        |

**最重要的反模式**: 让 AI "想个方法"或"给最优解"。这等于把考察的核心能力让出去。AI 给的解法你看不懂或不会复杂度分析时，整套答辩都会塌。

### Step 6: Verify (验证)

- 跑 edge case：空 list、单词、重复词、空串、单字符词、超长词
- 真读 AI 的代码（不是扫一眼），关注循环边界、index、early exit
- 拿一个具体输入，沿着代码手算一遍
- Validate 最终复杂度符合你的预期

---

## 3. 解法谱系表 (5 层完整保留 -- 命脉)

| Level | 算法                           | 时间复杂度          | 空间          | 备注                                              |
|-------|--------------------------------|---------------------|---------------|---------------------------------------------------|
| L0    | Brute force `o in w`           | O(N^2 * L^2) 最坏   | O(1)          | `in` 在 CPython 是 Crochemore-Perrin，最坏 O(L^2) |
| L1    | KMP 替换 substring search      | O(N^2 * L)          | O(L)          | 没解决 N 个 pattern 轮着试这个根本问题            |
| L2    | 前缀 Trie                      | O(N*L) 达到下界     | O(N*L)        | 只对前缀包含有效                                  |
| L3    | 子串 Trie (每起点扫)           | O(N*L^2)            | O(N*L)        | 大多数面试这层够，30-50 行                        |
| L4    | Aho-Corasick (trie + fail)     | O(N*L + 命中数)     | O(N*L)        | KMP 多模版，最优解，80+ 行                        |
| L5    | 后缀自动机 / Generalized SA    | O(N*L)              | O(N*L)        | 200+ 行，知道存在即可                             |

### L0 Brute Force 详细

```python
def find_containing(words):
    result = []
    for w in words:
        for o in words:
            if w != o and o in w:
                result.append(w)
                break
    return result
```

要点：
- 双重循环 N^2
- `o in w` 在 CPython 内部是 Crochemore-Perrin 的变体，最坏 O(|w|*|o|)，平均接近 O(|w| + |o|)
- 因此最坏 O(N^2 * L^2)，平均 O(N^2 * L)
- **常见漏点**: 脱口而出"O(N^2)"，忘了 substring search 不是 O(1)

### L1 KMP 替换 (单模 -> 多模 的本质区别)

把 brute force 里的 `in` 换成 KMP，单次匹配从最坏 O(L^2) 降到 O(L)。但**没有解决"N 个 pattern 要轮着试"这个根本问题** -- 每对 (text, pattern) 还是独立匹配。

按长度排序、命中早停等都是常数优化，不改复杂度。这一层主要是**教学价值**：让你看清"单模 vs 多模"的本质区别 -- 这是导向 AC 的桥梁。

### L2 前缀 Trie (达到下界但只对前缀有效)

把所有词插 trie，每个词末尾打 end-of-word 标记；对每个词 w 从根按字符走，途中遇到 end-of-word（且不是 w 自己的终点）-> w 包含某个真前缀词。

复杂度：建 trie O(N*L)，每次查询 O(L)，命中早停。**总 O(N*L)，达到下界**。

边界：要排除"w 自己的终点" -- 简单做法是先建 trie 后查询，查询时记录是否还在最后一个字符。

### L3 子串 Trie (每起点扫一遍)

```python
for w in words:
    for start in range(len(w)):
        node = root
        for i in range(start, len(w)):
            if w[i] not in node.children:
                break
            node = node.children[w[i]]
            if node.is_end and not is_self_match(start, i, w):
                # hit
                ...
```

- 时间 O(N*L^2)，比 brute 的 O(N^2*L^2) 好一个 N 因子
- 空间 O(N*L) 存 trie
- **实现门槛低，30-50 行，大多数面试这层就够了**

### L4 Aho-Corasick -- 见 §4 详解

### L5 后缀自动机 / Generalized Suffix Tree

把所有词拼起来建 generalized suffix automaton，对每个词查询其完整字符串是否作为子串出现。构建 O(总长度)，查询 O(|w|)，总 O(N*L)。**实现成本极高（200+ 行）**，面试基本不会要求 -- "知道存在并能解决问题"就够了。

---

## 4. Aho-Corasick 详解 (这题的高分点)

### 直觉：为什么需要 AC

KMP 解决"1 个 pattern 在 1 个 text 里"。当你有 K 个 pattern 都要在同一个 text 里找，KMP 跑 K 遍是 O(K * |text|)。**AC 把 K 个 pattern 编译成一个共享自动机，扫一次 text 就能找出所有命中** -- O(|text| + 命中数)。**它就是 KMP 的"多模式版本"。**

### 三个组件

1. **Trie 骨架**: 所有 pattern 插入 trie
2. **Fail 指针**: 每个节点指向"当前节点对应字符串的最长真后缀，且这个真后缀也是 trie 中某条路径的前缀" -- 这是 KMP failure function 在 trie 上的推广
3. **Output 链**: 每个节点维护"如果走到这里，会自然命中哪些 pattern" -- 通过 fail 链传递

### Fail 指针定义 (类比 KMP)

在文本里匹配 pattern，匹配到位置 i 失败时，KMP 不回退到开头，而是跳到 pattern 内部一个聪明的位置（最长 proper border）。AC 把这个想法搬到 trie：
- 你正沿着 trie 走 text，到了节点 v（代表已匹配的字符串 P）
- 下一个字符不在 v 的子节点里 -> 不要重启，跳到 fail(v)
- **fail(v) = "P 的最长真后缀，使其在 trie 中也是某条路径的前缀"**

### 具体例子: 模式 `["he", "she", "hers"]`，text 喂 `"she"`

- 沿 trie 走完 root -> s -> h -> e（即 "she" 节点）
- fail(she) = he（因为 "he" 是 "she" 的最长真后缀，且 trie 中有 "he" 这条路径）
- 这意味着：每当我们走完 "she"，应顺着 fail 链同时检查"是否在 'he' 这个 pattern 上也命中了"
- **输出 "she" 和 "he" 两个命中**

### 为什么是线性

**关键 insight**: 主指针每前进 1 步，fail 跳跃总长度的均摊是 O(1)。这与 KMP 是同样的均摊论证 -- fail 指针只能往浅处跳（depth 严格变小），而每次主指针深入一步 depth 才 +1。所以**总 fail 跳跃数 <= 总主指针前进数 = O(|text|)**。加上每个命中输出 O(1)，总 O(|text| + 命中数)。

### 构建步骤

1. 把所有 pattern 插入 trie，O(总 pattern 长度)
2. **BFS** 遍历 trie，按层计算 fail 指针：
   - 第 1 层节点的 fail 全是 root
   - 对节点 u 经字符 c 到子节点 v：让 f = fail(u)；沿 fail 链找到第一个有 c 子节点的 f'，则 fail(v) = f'.children[c]；找不到则 fail(v) = root
3. 匹配阶段：单指针沿 trie 走 text，遇到无效转移走 fail，每个节点检查自身 + fail 链上的 output

### 工程实现要点

- **BFS 顺序（不是 DFS）** 保证计算 fail(v) 时 fail(u) 已就绪
- output 链要预计算（或用懒求值），避免匹配时反复遍历
- 进阶：把 fail 链折叠成完整 DFA（goto 函数），匹配阶段每步真正 O(1) -- 这就是教科书里的"AC automaton 的 DFA 形式"

### 面试中的取舍策略

- 时间紧 -> trie 子串版（每起点扫一遍）足够，O(N*L^2) 在 N、L <= 1000 都能过
- 时间宽裕 + 面试官明确想看高阶解法 -> AC
- **一开始就提 AC、说出"这是 KMP 在多模式上的推广"是加分项**
- 但不要没建立简单解法就跳到 AC -- 会让面试官觉得你只会背高阶模板，不懂基础

---

## 5. 关键名词速查表

| 名词                       | 一句话解释                                                    |
|----------------------------|---------------------------------------------------------------|
| Trie / 前缀树              | 把字符串集合按前缀共享存储的树                                |
| KMP failure function       | 失配时跳到的位置，等于已匹配串的最长 proper border            |
| Proper border              | 既是 string 非空前缀又是非空后缀的字符串（不含整串本身）      |
| Aho-Corasick               | Trie + fail 指针的多模式匹配自动机                            |
| Suffix array               | 把所有后缀字典序排序后的索引数组，O(n log n) 或 O(n) 构建     |
| Suffix automaton           | 接受所有后缀的最小 DFA，O(n) 构建                             |
| Generalized suffix tree    | 多个串的后缀树                                                |
| Z-function                 | 每位置的"以该位置开始的最长子串等于整串前缀"的长度            |
| Manacher                   | O(n) 找所有回文子串中心                                       |
| Substring search 单模式    | KMP / Boyer-Moore / Rabin-Karp / Crochemore-Perrin            |
| Multi-pattern search       | Aho-Corasick / Commentz-Walter / Wu-Manber                    |
| 均摊分析                   | 一系列操作总开销 / 操作数，单次最坏可能高但总和受控           |

---

## 6. AI 协作的具体话术 (4 个 prompt 模板 + 4 个反模式)

### Prompt 1: 澄清阶段

> "我有这道题：[题面]。在动手前，请列出：(1) 题面中模糊或多解读的点；(2) 必须确认的边界条件；(3) 输入规模假设。**请只列问题，不要给解法。**"

最后一句很关键 -- 防止 AI 越界给方案。

### Prompt 2: 让 AI 验证你的复杂度

> "我打算用 [算法名] 解这道题。我推导的时间复杂度是 O(...)，空间 O(...)。请审查这个推导，**特别检查 [可能漏掉的开销，如 substring search 的真实代价、hash 冲突、动态扩容等]**。"

明确指出潜在陷阱，AI 才会针对性检查。

### Prompt 3: 实现阶段

> "请用 Python 实现 ['Aho-Corasick automaton']。要求：(1) 显式注释每段对应算法的哪一阶段（建 trie / 计算 fail / 匹配）；(2) 处理这些 edge case：空 list、单字符词、重复词、空字符串；(3) 不引入除标准库外的依赖。"

注意：**先说算法名，再说实现要求**。永远不要让 AI 猜你想要什么。

### Prompt 4: 审查阶段

> "对于这段代码：[code]。请检查：(1) 时间复杂度是否真的是我预期的 O(...)？(2) 哪些 edge case 没处理？(3) 哪一行最有可能在面试中被追问？给出具体行号。"

### 反模式 (不要这样 prompt)

- "帮我写一个高效的解法"
- "这道题最优解是什么？"
- "请帮我做这道面试题"
- "这段代码哪里可以优化？"（太开放，AI 会瞎改）

---

## 7. 备考刷题清单

**必须熟练 (trie 类)**:
- LC 208 Implement Trie / LC 648 Replace Words (前缀 trie 模板) / LC 720 Longest Word in Dictionary / LC 642 Design Search Autocomplete

**推荐 (trie + DP / 高阶组合)**:
- LC 472 Concatenated Words / LC 212 Word Search II (trie + 回溯) / LC 1268 Search Suggestions

**KMP 类**:
- LC 28 Implement strStr / LC 459 Repeated Substring Pattern / LC 1392 Longest Happy Prefix (KMP failure 直接应用) / LC 214 Shortest Palindrome

**Aho-Corasick (罕见但出现就是难题)**:
- 洛谷 P3796 AC 自动机简单版 / 洛谷 P5357 AC 二次加强版 (fail 树 DP)

**后缀结构 (高阶，了解即可)**:
- LC 1044 Longest Duplicate Substring / LC 1923 Longest Common Subpath

---

## 8. 完美面试回答模板 (6 阶段话术节奏)

把前面 7 部分串起来 -- 面试中可以直接套用：

**澄清阶段**: "好的。先确认几个问题：'包含'是指子串还是前缀？示例 `[category, cat]` 不能区分。词可以重复吗？输出是只要包含的 word 还是 `(word, contained)` 对？输入规模大概多少？"

**下界阶段**: "让我先想下界。我们必须读完所有词，所以是 Ω(N*L)。这告诉我目标是线性。"

**谱系阶段**: "解法谱系大致是这样：
- Brute force O(N^2 * L^2) 因为每个 substring search 最坏 O(L^2)
- 一个直接优化是把 substring search 换成 KMP，得 O(N^2 * L)，但根本问题是 N 个 pattern 还在轮着试 -- 这是经典多模匹配场景，单模式工具治标不治本
- Trie 路线：所有词建 trie，每个词查询时检查路径上是否提前命中 end-of-word。前缀版直接 O(N*L)，子串版每个起点试一遍是 O(N*L^2)
- 最优是 Aho-Corasick，O(N*L + 命中数)，原理是 trie + KMP 风格的 fail 指针，把不同 pattern 的部分匹配信息共享。"

**选型阶段**: "时间所限，我先实现 trie 子串版，确定逻辑正确后，如果时间允许我们升级到 AC。可以吗？"

**实现阶段**: 你画 trie 结构，列边界条件，再让 AI 写代码（用 §6 Prompt 3 模板）

**验证阶段**: 手算一两个测试用例，跑边界

**这套话术覆盖了**: 澄清 -> 下界 -> 谱系 -> 沟通 -> 取舍 -> 验证。即使最后没时间写到 AC，**过程已经满分**。

---

## 一图流总结

```
分阶段题: phase1 (no AI) 分析复杂度 -> phase2 (with AI) 优化实现
        |
        v
6 步框架: Clarify / Lower Bound / Solution Ladder / Pick Sweet Spot / 分工 / Verify
        |
        v
本题下界: Ω(N*L)  (N = 词数, L = 平均长度)
        |
        v
5 层谱系:
  L0 Brute        O(N^2 * L^2)    Crochemore-Perrin 最坏
  L1 KMP 单模     O(N^2 * L)      没解决多 pattern 根本问题
  L2 前缀 Trie    O(N*L)          达到下界, 但只前缀
  L3 子串 Trie    O(N*L^2)        每起点扫, 30-50 行, 面试常用
  L4 AC           O(N*L + 命中)   trie + fail, 80+ 行, KMP 多模版
  L5 后缀自动机   O(N*L)          200+ 行, 知道即可
        |
        v
AC 三组件: Trie 骨架 + Fail 指针 + Output 链
        |
        v
Fail 指针: 节点 v 字符串 P 的最长真后缀, 且也是 trie 中某条路径的前缀
        |
        v
线性: 主指针前进 1 步, fail 跳跃总长均摊 O(1) (fail 只能往浅处跳)
        |
        v
6 阶段话术: 澄清 -> 下界 -> 谱系 -> 选型 -> 实现 -> 验证
        |
        v
反射: AI 时代面试 = 精确指挥 + Review, 不是把"想方法"让出去
```

**记住**: 这道题的差异化签名 = (1) 把 substring search 真实复杂度（不是 O(1)）讲出来，(2) 把"单模 vs 多模"本质区别讲出来（KMP 治标不治本 -> AC 治本），(3) 主动 propose tradeoff 不沉默选最优，(4) Step 5 分工原则讲出来（你设计 + AI 写）。四件事讲到 + AC 的 fail 指针均摊论证讲出来 = senior signal。
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
                f"[META-ANC-7] missing keyword {kw!r} -- regenerate"
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
                f"[META-ANC-7] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_find_words_containing() -> int:
    """Insert or update the Find Words Containing drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-7] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-7] expected Meta company_id=31, got {company_id}"
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
    upsert_meta_anc_find_words_containing()
