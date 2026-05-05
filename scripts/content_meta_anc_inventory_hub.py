"""[META-ANC-9] AI-Native Coding Inventory & Cheat Sheet hub doc.

Inserts ONE company_documents row that becomes the cd://<id> drawer hub for
the 8 Meta AI-Native Coding problems (1098..1105). Mirrors the Meta-OA hub
doc id=80 pattern: drawer-link cards via [title](db://N) markdown + 跨题
共通考点 + 临场 prompt 模板 + 离场 cheat sheet.

Idempotency policy (FIX #3 -- sentinel-only):
- Discovery key = sentinel HTML comment in content column (LIKE).
- The sentinel `<!-- META_AI_NATIVE_CODING_INVENTORY_20260501 -->` is the
  ONLY discovery key. NOT title (style-drift), NOT content_hash (fragile).
- The 8 source problems must all exist (assert 8 rows with
  source='Meta-AI-Native-Coding-2026-05-01'); abort otherwise.

COMPANY_ID self-check (FIX #7): query Meta by name, assert == 31.

NOOP normalization (FIX #5): semantic compare (strip per-line trailing
whitespace, force LF, collapse 3+ blank lines to 2).

Required-keywords assertion (FIX #8): all of
['Maze', 'Max Unique', 'Friend Recommendation', 'Sparse Matrix',
'Linear Regression', 'Compiler', 'Find Words', 'Card Game',
'跨题', '离场', 'cd://', 'db://'] present, plus exactly 8 db:// links.

No-emoji + UTF-8 + ruff-clean.

Reference golden examples:
- Hub-doc UPSERT pattern: scripts/seed_meta_oa_prep_hub.py (id=80).
- Sentinel-UPSERT semantics: scripts/content_meta_anc_card_game_sum15.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company, CompanyDocument  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

SENTINEL = "<!-- META_AI_NATIVE_CODING_INVENTORY_20260501 -->"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
TITLE = "[Meta] AI-Native Coding Inventory & Cheat Sheet (2026-05-01)"
DOC_KIND = "hub_doc"
SOURCE_TYPE = "manual"

REQUIRED_KEYWORDS = [
    "Maze",
    "Max Unique",
    "Friend Recommendation",
    "Sparse Matrix",
    "Linear Regression",
    "Compiler",
    "Find Words",
    "Card Game",
    "跨题",
    "离场",
    "cd://",
    "db://",
]


CONTENT = SENTINEL + r"""

# Meta AI-Native Coding -- Inventory & Cheat Sheet (2026-05-01)

> **用法**: 考前 / round 间扫这一页。8 张速查卡片在下方; 点 [打开完整题解] 链接, drawer 在右侧 slide-over 弹出 -- ESC 或点遮罩关闭。
> **场景**: Meta AI-Native onsite coding round 备考。每题 5-7 分钟过卡片, 卡住的题 [打开完整题解] 进 db://<id> 看完整 ladder + AI 协同分工。
> **嵌入**: 本页同时挂在 [Meta] AI-Native Onsite Prep (cd://82) §T5 板块下方。

## 快速跳转

[Maze](db://1098) · [Max Unique](db://1099) · [Friend Recommendation](db://1100) · [Sparse Matrix](db://1101) · [Linear Regression](db://1102) · [Compiler](db://1103) · [Find Words](db://1104) · [Card Game](db://1105)

---

## 8 题速查表

| # | 题目 | 类型 | 最优复杂度 | 核心技巧 | 完整题解 |
|---|------|------|------------|----------|---------|
| 1 | Maze Solver | 5-question ladder, BFS | $O(W \cdot H \cdot 2^k \cdot 2^b)$ | bitmask state (key + bomb), is_wall 查表 | [打开 -> Maze](db://1098) |
| 2 | Max Unique Character Subset | bitmask DP | $O(N \cdot 2^{26})$ subset 转移 | 26-bit bitmap, prevMask = newMask ^ wordMask 反推 | [打开 -> Max Unique](db://1099) |
| 3 | Friend Recommendation | L1->L6 graph + meta-ability | $O(V + E + V \log V)$ | adjacency dict + co-friend count + top-k heap | [打开 -> Friend Recommendation](db://1100) |
| 4 | Sparse Matrix Ops | COO/CSR/CSC + dot/matmul | $O(\text{nnz}_1 + \text{nnz}_2)$ | 双指针 dot product, 稀疏端遍历 + 哈希查稠密端 | [打开 -> Sparse Matrix](db://1101) |
| 5 | Linear Regression | 闭式解 + Ridge/Lasso/SGD | $O(n d^2 + d^3)$ | $w = (X^T X)^{-1} X^T y$, np.linalg.lstsq 不显式求逆 | [打开 -> Linear Regression](db://1102) |
| 6 | Compiler Optimization | cost-model regression | $O(P \cdot N) \cdot$ search | 8-block Meta-Prompt, lstsq 反推 cost, B/C 解耦 | [打开 -> Compiler](db://1103) |
| 7 | Find Words Containing Other Words | 5-tier 字符串匹配 | $O(\sum \lvert w_i \rvert)$ | Trie + end-of-word, 走到途中遇 end = 命中 | [打开 -> Find Words](db://1104) |
| 8 | Card Game Sum-15 | 5-tier game strategy | state $\le 15^9 \approx 4 \times 10^{10}$ | Tier 2 (heuristic) + measure 必交; Tier 4 (MC rollout) 时间够再加; Tier 5 DP 只口述 | [打开 -> Card Game](db://1105) |

---

## 1. Maze Solver -- BFS + state bitmask

5-question ladder: Q1 print priority -> Q2 visited -> Q3 directional gates -> Q4 key & door (bitmask) -> Q5 bomb (bombMask).

- 状态空间 = $W \cdot H \cdot 2^k \cdot 2^b$, **不是** $4^n$ -- 加 visited 后路径长度从复杂度里消失。
- visited key **必须**用完整 state `(x, y, mask, bomb_mask)`, 写成 `(x, y)` = 漏掉"绕路捡钥匙再回来"。
- bomb 派生信息 (墙是否消失) 用查表 `is_wall(x, y, mask)` 反推, **不**进 visited -- 状态空间从 32 倍降到 $2^b$。
- bitmask 编解码 (`mask | (1 << i)`, `mask & (1 << i)`) 自己写, 别让 AI 帮忙 -- idiom 化 + 节省时间。
- $k \ge 25$ 临界点: bitmask 不再可行, 换启发式或 TSP-like 建模。

**[打开完整题解 -> Maze Solver](db://1098)**

---

## 2. Max Unique Character Subset -- bitmask DP

LeetCode 1239 变种, 字典里挑词集合 = 互不相交字母 (each word -> 26-bit bitmap)。

- 预处理三步: word -> 26-bit bitmap; 自身有重复字母直接丢 (`popcount(mask) != len(word)`); 同 bitmap 只留一个代表 (anagram 去重)。
- DP `dict[mask] -> word_index`, 不要存 prev 指针 -- `prevMask = newMask ^ wordMask` 数学反推, 节省内存。
- 转移用 snapshot 防止"同词多次使用" (0/1 背包性质)。
- 剪枝: 一旦 `mask == (1 << 26) - 1` 立即返回 (满字母无需继续)。
- 路径重建: `w = dp[cur]; cur ^= masks[w]` 循环到 `cur == 0`。

**[打开完整题解 -> Max Unique Character Subset](db://1099)**

---

## 3. Friend Recommendation -- L1 valid-fix -> L6 meta-ability

6-level ladder: L1 修 valid-friend -> L2 mutual-friend count -> L3 top-k by score -> L4 weight by recency -> L5 second-degree closure -> L6 元能力 (interviewer 让你解释自己的设计选择)。

- adjacency `dict[user] -> set[user]`, 双向边添加时务必两端各 add 一次 -- valid-friend 校验最常翻车点。
- mutual count 用 `len(adj[u] & adj[v])` (set intersection); $O(\min(|adj[u]|, |adj[v]|))$。
- top-k 用 heap `heapq.nlargest(k, candidates, key=score)`; full sort 是 $O(V \log V)$, 浪费。
- L6 元能力题: 面试官故意问"为什么不用 X 算法" -- 答之前先反问 spec, 不要直接背诵 tradeoff。
- AI-trap signature: 楼主沉默 paste-试-paste-试, 没外化思考过程 -- 这是 AI 面试沉默死。

**[打开完整题解 -> Friend Recommendation](db://1100)**

---

## 4. Sparse Matrix Ops -- COO / CSR / CSC

稀疏向量点积 + 稀疏矩阵乘法 + 三种存储格式对比 (COO 构建快 / CSR SpMV 友好 / CSC 取列友好)。

- 双指针 dot 模板: 两边都按 idx 升序, `i, j` 双指针归并; 复杂度 $O(\text{nnz}_1 + \text{nnz}_2)$。
- 一稀一稠时, 遍历稀疏端 + 哈希查稠密端 -> $O(\text{nnz}_{\text{small}})$。
- CSR x CSC = 经典乘法搭配 (A 取行 + B 取列, 归约成稀疏 dot)。工业界惯例: 构建期 COO, 运算期 `.tocsr()`。
- subcubic matmul (Strassen $O(n^{2.807})$ / Coppersmith-Winograd ~$O(n^{2.37})$) 只口述, **不写** -- 现实里 BLAS GEMM 用 cache blocking + SIMD 把 $O(n^3)$ 常数压扁了。
- CSR 转置 = CSC 同表 (互为视角), $O(1)$。

**[打开完整题解 -> Sparse Matrix Ops](db://1101)**

---

## 5. Linear Regression -- 闭式解推导

最小化 $L(w) = \|Xw - y\|^2$, 求导得 $\nabla_w L = 2 X^T (Xw - y)$, 令为 0 -> $w = (X^T X)^{-1} X^T y$。

- 维度对齐先想清: $\nabla_w L \in \mathbb{R}^{d \times 1}$ -> 前面必须是 $X^T \in \mathbb{R}^{d \times n}$ 不是 $X$。
- 三种实现: `np.linalg.inv(X.T @ X) @ X.T @ y` (教科书, 慢且不稳) / `np.linalg.solve(X.T @ X, X.T @ y)` (推荐 LU) / `np.linalg.lstsq` 或 `pinv` (最稳 SVD)。
- Ridge: $w = (X^T X + \lambda I)^{-1} X^T y$, $\lambda I$ 抬高所有特征值, 永远可逆。
- Lasso 没闭式解 (L1 在 0 处不可导), 但 coordinate descent 单维子问题有 soft-thresholding 解析。
- collinearity 处理: Ridge / pinv / 删冗余特征 / PCA。

**[打开完整题解 -> Linear Regression](db://1102)**

---

## 6. Compiler Optimization -- cost-model regression from tests

楼主 1/5 翻车题 (GPT 幻觉 + 面试官 "no universal definition")。骨架: parse -> optimize -> featurize -> fit lstsq -> search pass-combo for max_error == 0。

- 核心反射: **test 给的数字是验证我, 还是定义问题?** 如果是后者 -> 方程组 / lstsq 立即启动。
- 8-block Meta-Prompt: INPUT / UNKNOWNS / FEATURE EXTRACTION / EQUATIONS / SOLVE / VALIDATE / ITERATE / OUTPUT (verbatim 抄进现场)。
- B/C 解耦: 建模 (B) 和 pass 应用 (C) 分两步 -- B 用 lstsq optimize=IDENTITY 反推权重, C 暴力 search 组合。
- 残差性质: 系统性 = 漏特征, 随机 = 模型形式错。
- AI-trap signature: **LLM 给的常数永远要问你怎么得到的** -- 不引用源 = 默认错。

**[打开完整题解 -> Compiler Optimization](db://1103)**

---

## 7. Find Words Containing Other Words -- 5-tier 字符串匹配

5-tier ladder: Brute $O(N^2 L)$ -> KMP $O(NL)$ -> Trie $O(\sum |w|)$ -> Aho-Corasick (AC) -> Suffix Automaton。

- Trie 主流派写法: 所有 pattern 插入 trie + end-of-word 标记; 对每个 word w 从根走, 途中遇 end (非 w 自己终点) -> 命中真前缀。
- Aho-Corasick = Trie + KMP failure -- fail 链 + output 链, 多模式匹配的标准答案。
- 理论下界 $\Omega(N \cdot L)$ (necessary 读完所有字符) -- AC 把这个下界打到了, Brute 是 $O(N^2 L)$ 慢一个量级。
- 复杂度自己复算: AI 给的 $O(N \log N)$ 答案 100% 错 (字符串匹配没 log)。
- 4 个 prompt 模板 (Clarify / Verify / Implement / Review) 全在 db:// 题解里, 离场前回看一遍。

**[打开完整题解 -> Find Words Containing Other Words](db://1104)**

---

## 8. Card Game Sum-15 -- 5-tier game strategy

36 张牌 (1..9 各 4 张), 每回合挑 3 张和=15 拿走得 15 分, 直到台面凑不出 valid triple = game over。完美局 = 12 组 = 180 分。

- **澄清五问开场**: (1) 数值能否重复? (2) 花色须互异? (3) input 上帝视角 vs 局部视角? (4) 终止条件? (5) 目标 = 最大化期望分 vs 最大化 perfect 180 概率? -- Bellman V vs P 两个版本不等价。
- **5-tier ladder**: greedy -> heuristic -> backtrack (跳过) -> Monte Carlo rollout -> expectimax DP。**不报具体百分比** (除非真跑过), 改口 "baseline / heuristic 提升 / MC 接近最优"。
- **时间预算 (60min round)**: Q1 修 UT 必须 <=5min, Q4 只剩 10-15min。**先交 Tier 2 (heuristic) + measure 拿数字**; 时间够再加 Tier 4 (MC rollout); Tier 5 DP `state=(table, deck)` + Bellman + 多元超几何**只口述**。
- **AI-trap signature**: 楼主第 4 问让 AI 写了 150 行 DP 没 validate 就贴 -- 跑过 test 但解释不出。**算法选你 hold 得住的那一档**。CoderPad 里的 AI 可能是小模型, DP 错率更高 -- 越要 1 个具体例子纸笔 trace (e.g. `table=(4,0,0,0,0,0,0,0,4)` -> `find_triples` 应返 `[]`)。
- **反例 "完美策略每次拿满分?"**: 否, 双层答 -- (理论极端) 初始台面 4*9+4*8+4*7+4*6 直接 game over, P~1/7.3 亿; (现实 failure) 中后期连抽 4 张同 rank 卡死 table。
- **复杂度算对**: state 上界 $15^9 \approx 4 \times 10^{10}$ (用约束 t+d<=4, per-rank 15 个有效 (t,d) 对), 可达 $10^7 \sim 10^8$ -- Python `lru_cache` 顶不住, 现场用 MC 采样近似。

**[打开完整题解 -> Card Game Sum-15](db://1105)**

---

## 跨题 共通考点 (5-7 条)

1. **状态空间设计是核心考点** -- Maze (key + bomb mask), Card Game ((table, deck)), Max Unique (26-bit) 三题都吃这点。新机制就问"要不要加 mask 维度"。
2. **复杂度自己复算** -- AI 给的复杂度公式 100% review 一遍。Compiler 反射 / Find Words 字符串没 log / Maze 路径长度从公式里消失 -- 这三个 trap 都中过。
3. **理论下界先想** -- Find Words 的 $\Omega(N \cdot L)$ / Card Game 的 $15^9 \approx 4 \times 10^{10}$ 状态空间上界 (可达 $10^7 \sim 10^8$) / Sparse Matrix 的 $\Theta(\text{nnz})$ -- 知道下界才知道优化天花板在哪。
4. **离散 + 连续混合时分两步** -- Compiler 阶段 B (建模 lstsq) 和 C (pass 组合搜索) 解耦。Max Unique 也是 (bitmap 预处理离散 + DP 转移连续 mask)。
5. **LLM 给的常数没引用源 = 默认错** -- Compiler 反射出场, Maze 复杂度复算同源。看到 magic number 就反问"你怎么得到的"。
6. **idiom 自己写, 模板代码 AI 帮** -- bitmask 编解码 / 双指针 dot / 闭式解推导 = 自己写到肌肉记忆; 边界 case 测试 / blast-area helper / `parse_ir` 模板 = AI 帮写。
7. **澄清开场 30 秒 = senior signal** -- Card Game 五问 (重复? 花色? 视角? 终止? 目标函数?) / Maze (符号优先级?) / Friend Recommendation (有向无向?) -- 不澄清直接动键盘 = junior 信号。

---

## 临场 prompt 写作 4 模板 (Find Words 提炼, 8 题通用)

**1. CLARIFY** (开场静默 30 秒, 不动键盘):
```
我有一道 <题型> 题。在写代码前请帮我列出所有需要先澄清的问题:
- 输入约束 (size / range / 重复 / 排序)
- 输出格式 (return type / tie-break)
- 边界 case (empty / single / 全相同)
- 终止条件
不要写代码, 只列问题。
```

**2. VERIFY 复杂度**:
```
我打算用 <算法> 解这题, 复杂度估算 $O(<formula>)$。
帮我 review 这个公式: 状态数怎么来? 每状态代价怎么来?
有没有理论下界? 我估的紧不紧?
```

**3. IMPLEMENT 给算法名+约束+边界**:
```
请帮我写 <算法名> 的 Python 实现。约束:
- input: <type 签名>
- 边界: <empty / single>
- 复杂度目标: $O(<formula>)$
- idiom 部分 (e.g. bitmask 编解码) 我自己写, 你只给骨架。
```

**4. REVIEW 检查复杂度 + edge case + 易追问行号**:
```
review 这段代码:
- 复杂度公式 (state count x per-state cost)
- edge case 漏没漏 (empty / single / overflow / tie)
- 哪几行最容易被面试官追问"这里为什么"?
```

---

## AI 协作分工通则 (做对 vs 翻车 对照表)

| 自己做 (做对) | AI 做 (做对) | AI 做 (翻车) |
|--------------|------------|-------------|
| 状态空间设计 (Maze mask / Card (table, deck)) | 边界 case 测试输入生成 | 全题代码生成 (Card 4: 150 行 DP 没 validate) |
| bitmask 编解码 idiom (Maze 钥匙 / Max Unique 26-bit) | blast-area helper / 坐标变换 | 复杂度公式 (Find Words: AI 给 $O(N \log N)$ 错) |
| 双指针 dot (Sparse Matrix) | parse_ir 模板代码 (Compiler) | 常数无引用源 (Compiler: GPT 给 cost 数字没 derive) |
| 闭式解推导 (Linear Regression $X^T X$) | 解释陌生算法 (AC fail link / Strassen 分治) | 状态空间 ad-hoc (Card: AI 把 list 当 state, lru_cache 挂) |
| 复杂度公式复算 + 理论下界 | 翻译已设计的状态机为代码 | senior signal 类问题 (Friend Rec L6: 沉默 paste-试 死) |
| Review AI 输出 + 主动指错 | 命名 / 注释 / 重构 | 算法选最优档 (选 hold 不住的, 解释不出) |

底线: **AI 给的代码 > 30 行强制读 + 在白板画 1 个示例再贴**。讲不出来的代码 = 不存在的代码。

---

## 离场 60s checklist (round 结束前自检 5 条)

- [ ] 我开口第一句是 clarification 还是 high-level idea? (clarification 优先, 不澄清直接动键盘 = junior)
- [ ] 心里的图被 interviewer 看到了吗? (不止 AI 文本 -- 白板画一个具体例子, $n=2/3$ 的 trace)
- [ ] 主动指出过 AI 输出的 1+ 个问题吗? ("这复杂度我怀疑, 让我重算" / "这常数没 derive, 我先 sanity check")
- [ ] 对每个选择讲过 tradeoff 吗? (Tier 选哪档 + 为什么不用 Tier 5 / 为什么不用 Trie)
- [ ] 做最终 validate 而非盲贴吗? (Card 第 4 问 / Compiler / Find Words 都败在没 validate)

---

## AI 面试最大失分模式 (3 条 tombstone)

1. **Card Game 模式 -- "看了一眼没认真 validate 就贴进去"**
   楼主第 4 问只剩 10 分钟, AI 出 150 行 DP, 没 validate 就 paste, 跑过 test 但解释 DP 思路嗑嗑巴巴。**反射动作**: AI 给的代码 > 30 行 = 强制读 + 画示例 + 讲一遍再贴。

2. **Compiler 模式 -- "LLM 给常数没问怎么得到的"**
   GPT 幻觉的 cost 数字 + 面试官 "no universal definition" 想点醒, 楼主没接住直接代入。**反射动作**: 看到 magic number 就反问"你这个数从哪推的?"; 不引用源 = 默认错。

3. **Friend Recommendation 模式 -- 沉默 paste-试-paste-试**
   L6 元能力题面试官想看你的设计选择思考过程, 楼主一直 paste 代码没外化思考。**反射动作**: 每次贴前一句"我打算 X 因为 Y", 贴后一句"现在 trace 一遍 $n=2$ 的 case"。

---

> **一句话总览**: AI 面试时代第一原则 = **算法选你 hold 得住的那一档**, 不是选最优那档。澄清 30 秒先开场, 复杂度自己复算, AI 给长代码强制 validate -- 8 题通用。
"""


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines to 2.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _assert_required_keywords(content: str) -> None:
    """Abort if any REQUIRED-KEYWORD is missing from the content."""
    for kw in REQUIRED_KEYWORDS:
        if kw not in content:
            raise RuntimeError(
                f"[META-ANC-9] missing keyword {kw!r} -- regenerate"
            )


def _assert_db_link_count(content: str, expected: int) -> None:
    """Assert exactly `expected` distinct db://N ids are referenced.

    The hub legitimately re-cites each problem id in 3 surfaces (快速跳转 /
    速查表 / 每题 close-out card). The invariant is on the count of distinct
    ids, not raw markdown-link occurrences.
    """
    ids = set(re.findall(r"db://(\d+)", content))
    if len(ids) != expected:
        raise RuntimeError(
            f"[META-ANC-9] expected exactly {expected} distinct db:// ids, "
            f"got {len(ids)} ({sorted(int(i) for i in ids)})"
        )


def _assert_no_emoji(content: str) -> None:
    """Project rule: no emoji characters in content."""
    for ch in content:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1FAFF
            or 0x1F000 <= cp <= 0x1F2FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"[META-ANC-9] emoji character U+{cp:04X} found at "
                f"position {content.index(ch)}"
            )


def _resolve_company_id(db) -> int:
    """Look up Meta company by name; assert id == 31."""
    company_id = (
        db.query(Company).filter(Company.name == "Meta").one().id
    )
    if company_id != 31:
        raise RuntimeError(
            f"[META-ANC-9] expected Meta company_id=31, got {company_id}"
        )
    return int(company_id)


def _assert_8_source_problems(db) -> list[tuple[int, str]]:
    """Assert all 8 META-ANC problems exist; return [(id, title), ...]."""
    rows = (
        db.query(Problem.id, Problem.title)
        .filter(Problem.source == SOURCE)
        .order_by(Problem.id.asc())
        .all()
    )
    if len(rows) != 8:
        raise RuntimeError(
            f"[META-ANC-9] only {len(rows)} drawers found, expected 8 -- "
            "run META-ANC-1..8 first"
        )
    return [(int(r.id), str(r.title)) for r in rows]


def _assert_db_links_match_problems(
    content: str, problem_ids: list[int]
) -> None:
    """Every db://N in content must hit a problem in `problem_ids`."""
    referenced = set(int(m) for m in re.findall(r"db://(\d+)", content))
    expected = set(problem_ids)
    missing = expected - referenced
    extra = referenced - expected
    if missing:
        raise RuntimeError(
            f"[META-ANC-9] hub missing db:// links for problem ids: "
            f"{sorted(missing)}"
        )
    if extra:
        raise RuntimeError(
            f"[META-ANC-9] hub references unknown problem ids via db://: "
            f"{sorted(extra)}"
        )


def upsert_meta_anc_inventory_hub() -> int:
    """Insert or update the AI-Native Coding Inventory hub; return doc id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in CONTENT:
        raise RuntimeError(f"[META-ANC-9] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(CONTENT)
    _assert_db_link_count(CONTENT, expected=8)
    _assert_no_emoji(CONTENT)

    try:
        company_id = _resolve_company_id(db)
        print(f"[OK] target company: id={company_id} name='Meta'")

        problem_rows = _assert_8_source_problems(db)
        problem_ids = [pid for pid, _ in problem_rows]
        print(
            f"[OK] all 8 source problems present: "
            f"ids={problem_ids[0]}..{problem_ids[-1]}"
        )

        _assert_db_links_match_problems(CONTENT, problem_ids)
        print("[OK] all 8 db:// links match problem ids in DB")

        # Sentinel-only discovery (FIX #3): query content LIKE %sentinel%.
        existing = (
            db.query(CompanyDocument)
            .filter(
                CompanyDocument.company_id == company_id,
                CompanyDocument.content.like(f"%{SENTINEL}%"),
            )
            .first()
        )

        normalized_new = _normalize(CONTENT)

        if existing is None:
            doc = CompanyDocument(
                company_id=company_id,
                title=TITLE,
                content=CONTENT,
                source_type=SOURCE_TYPE,
                doc_kind=DOC_KIND,
                is_golden=False,
            )
            db.add(doc)
            db.flush()
            doc_id = int(doc.id)
            print(
                f"[INSERT] company_documents id={doc_id} title={TITLE!r} "
                f"len={len(CONTENT)}"
            )
        else:
            doc_id = int(existing.id)
            normalized_old = _normalize(existing.content or "")
            if normalized_old == normalized_new:
                print(
                    f"[NOOP] company_documents id={doc_id} content "
                    f"semantically identical (len={len(CONTENT)})"
                )
            else:
                old_len = len(existing.content or "")
                existing.content = CONTENT
                existing.title = TITLE
                existing.doc_kind = DOC_KIND
                existing.source_type = SOURCE_TYPE
                print(
                    f"[UPDATED] company_documents id={doc_id} "
                    f"old_len={old_len} new_len={len(CONTENT)} "
                    f"delta={len(CONTENT) - old_len:+d}"
                )

        db.commit()

        final = (
            db.query(CompanyDocument)
            .filter(
                CompanyDocument.company_id == company_id,
                CompanyDocument.content.like(f"%{SENTINEL}%"),
            )
            .one()
        )
        print(
            f"[VERIFY] company_documents id={final.id} title={final.title!r} "
            f"doc_kind={final.doc_kind!r} content_len="
            f"{len(final.content or '')}"
        )
        return int(final.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upsert_meta_anc_inventory_hub()
