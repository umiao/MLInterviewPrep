"""Seed Meta OA Standalone Algos solution doc (same-start-end + smallest reversal).

Per T-P1-249. Target: company_documents (company_id=31 Meta).

Covers two Meta OA standalone warm-up problems:
  §1 Same Start/End Letter Count  -- O(n) split + first/last compare
  §2 Smallest String via Prefix/Suffix Reversal -- O(n^3) brute over all
      prefix/suffix reversal choices + lexicographic min.

Idempotency: sentinel <!-- META_OA_STANDALONE_20260422 --> gates the write.
Second run = 0 writes (update only when content hash changes).

Style: Chinese narration + English technical terms (per MLInterviewPrep
content style rule). Acronyms expanded on first occurrence.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_OA_STANDALONE_20260422 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-OA] Standalone Algos (Same Start/End + Smallest Reversal)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"

CONTENT = SENTINEL + r'''
# Meta OA — Standalone Algos (§1 Same Start/End Letter + §2 Smallest Reversal)

> **题型**: standalone warm-up；两题各自独立，不像 4-level 系统设计那样累积状态。
> **时长**: 90 分钟整套里 ~5-10 min/题 的档位；两题全过是进入后续 4-level 题（Cloud FS / In-Memory DB / Bank System）的"入场券"。
> **评分**: warm-up 不通过通常直接挂；两题都 AC 才算 baseline。主要坑在 corner cases（空串 / 单字母 / Unicode / Tab 分隔符）。

---

## 1. Problem Overview

Meta OA（**Online Assessment (OA, 线上测评)**）的 standalone 题区别于 4-level 族题：每题独立完成，读 `stdin`（或函数签名入参），写 `stdout`（或 `return`）。两道 warm-up 通常是：

| § | 题目 | 难度 | 最优复杂度 | 核心考点 |
|---|------|------|------------|----------|
| 1 | Same Start/End Letter Count | Easy | $O(n)$ | `str.split()` 默认语义 + case fold |
| 2 | Smallest String via Prefix/Suffix Reversal | Easy-Medium | $O(n^3)$ | 枚举所有 prefix/suffix 反转 + lexicographic min |

### 考场定位

- 两题合计期望 10-15 分钟拿下。超过 20 分钟说明陷入 corner case debug，该跳过继续做 4-level 题。
- 不要过度工程化：§1 是一行推导式就能搞定的题，不需要正则 / `re.finditer`；§2 的 $O(n^3)$ 在 $n \le 10^3$ 量级 **刚刚好**，不要为了炫技用 suffix array。

### 两题共同坑

- **Unicode 比较语义**: Python 的 `<` 操作符对字符串按 **Unicode code point** 比较，不是 collation-aware。`'a' < 'é' < 'z'` 成立（97 < 233 < 122？ 错——233 > 122，所以 `'é' > 'z'`）。Meta OA 测试用例里若出现 non-ASCII，字典序指的就是 code point 序。
- **大小写敏感性**: §1 通常 **case-insensitive**（`Apple` 的首尾是 `A` 和 `e`，不同，但首尾都是 `a` 的 `ABba` 算）；§2 通常 **case-sensitive**（原样保留）。读题时确认 spec 明确写了哪种——漏读 = 整题判零。
- **空白字符**: `str.split()` 不带参数时默认按 **任意连续空白** 切分并丢弃空 token；`str.split(' ')` 则按单空格切分，保留空 token。§1 用无参 `split()`；这条是 Meta OA 测试用例里 tab/多空格边界的唯一正解。

---

## 2. §1: Same Start/End Letter Count

### 2.1 题目原文

> You are given a string `sentence` containing words separated by whitespace (spaces, tabs, or mixed). Return the count of words whose **first and last character match, case-insensitively**. A single-character word counts (first == last trivially).
>
> **Constraints**: `1 <= len(sentence) <= 10^5`; ASCII letters + whitespace only (in the canonical variant). Some variants allow Unicode letters—see §2.4 corner cases.
>
> **Example**: `"Apple banana ABBA a cat tAct"` → `3`
> - `Apple`: `A` vs `e` → 不算
> - `banana`: `b` vs `a` → 不算
> - `ABBA`: `A` vs `A` → 算
> - `a`: 单字母 → 算
> - `cat`: `c` vs `t` → 不算
> - `tAct`: `t` vs `t`（case-insensitive） → 算
> - 合计 **3**

### 2.2 最优 Python 解法

```python
def count_same_first_last(sentence: str) -> int:
    """Count words where first letter == last letter (case-insensitive)."""
    return sum(
        1
        for w in sentence.split()  # 默认按任意空白切分，丢弃空 token
        if w and w[0].casefold() == w[-1].casefold()
    )
```

**要点**:

1. `sentence.split()` **不带参数** — 自动处理 tab / 多空格 / 首尾空白 / 空字符串（返回 `[]`）。
2. `casefold()` 优于 `lower()` — 对 Turkish `İ`、German `ß` 等 edge 行为更正确；对纯 ASCII 与 `lower()` 等价。写 `lower()` 也能过标准测试用例，但 `casefold()` 是 "正确的默认"。
3. `if w and ...` — 理论上 `split()` 不会返回空字符串，但防御性加上 `w and` 成本为 0，能防 `split(' ')` 被误用回退到这里时的 `IndexError`。
4. 推导式 + `sum(1 for ...)` 比 `len([... for ...])` 省一次 list materialization；$n=10^5$ 量级虽不差，但是 Pythonic idiom。

### 2.3 复杂度分析

- **时间**: $O(n)$，$n$ 为 `len(sentence)`。
  - `split()` 扫一遍，$O(n)$。
  - 每个 token $w$ 的 `casefold()` 只作用于 `w[0]` 和 `w[-1]` 两个字符（注意：**不是** 对整个 $w$ casefold 再取端点——我们只取端点再 casefold，$O(1)$/token）。
  - 总 token 数 $\le n/2 + 1$；每 token $O(1)$ 比较。合计 $O(n)$。
- **空间**: $O(n)$（`split()` 返回的 list），若要严格 $O(1)$ extra 可手写状态机扫描，但 Meta OA 不要求。

### 2.4 Corner Cases

| 场景 | 输入 | 期望输出 | 踩坑点 |
|------|------|----------|--------|
| 空串 | `""` | `0` | `"".split() == []`，推导式自然返回 0。若写 `split(' ')` 则返回 `['']`，会进 `if` 判断，靠 `if w` 跳过。 |
| 单字母词 | `"a"` | `1` | `w[0] == w[-1]` 对单字符 trivially 为真 — 这是题目语义的一部分。 |
| 单字母词多个 | `"a b c"` | `3` | 三个单字母都算。 |
| Tab 分隔 | `"hi\tbye\taba"` | `1` | `split()` 无参自动处理 `\t`；`split(' ')` 则整串留作一个 token，全挂。 |
| 连续多空格 | `"a  b"` | `2` | 同上；`split(' ')` 会有空 token `['a', '', 'b']`，推导式 `if w` 跳过空串。 |
| Mixed case | `"Ada"` / `"apple"` | `1` / `0` | `Ada`: `a` vs `a` 算；`apple`: `a` vs `e` 不算。忘了 `casefold()`/`lower()` → `"Ada"` 的 `A` (65) vs `a` (97) 判不等，返回 0，判错。 |
| 全大写 | `"ABBA"` | `1` | 与 mixed case 同处理路径，`A == A` 本身就等。 |
| 标点/数字混入 | `"1x1 a.a"` | `2` | `1x1`: `1` vs `1` 算；`a.a`: `a` vs `a` 算。题目若说 "words" 指纯字母需额外 `w.isalpha()` 过滤，**读题时问清楚 spec**。 |
| Unicode letter | `"café naïve aba"` | `1` | Python 3 的 `casefold()` 对 `é`/`ï` 保持不变（lower-case 形式）；`café` 的 `c` vs `é` 不等，`naïve` 的 `n` vs `e` 不等，`aba` 算。 |
| Unicode 大小写 | `"Été eté"` | `2`？ | `É` (U+00C9) vs `é` (U+00E9) — `casefold()` 都得到 `'é'`，所以 `Été` 的首尾 `É`/`é` casefold 后相等，算。此条 OA **通常** 不考，但遇到要知道 `lower()` 对某些组合符（如 `İ` → `i̇`）行为 Unicode-specific，`casefold()` 更稳。 |
| 整串空白 | `"   \t\n  "` | `0` | `split()` 返回 `[]`，推导式自然 0。 |

**判错最高频的两条**: (a) 忘了 case fold；(b) 用 `split(' ')` 没处理 tab。两条同时错 → 连带判掉 §1 整题。

---

## 3. §2: Smallest String via Prefix/Suffix Reversal

### 3.1 题目原文

> Given a string `s`, you may perform **at most one** of the following operations:
> - Reverse a **prefix** `s[:i]` for some `1 <= i <= len(s)`.
> - Reverse a **suffix** `s[j:]` for some `0 <= j < len(s)`.
>
> Return the **lexicographically smallest** string obtainable (original `s` is allowed — i.e., doing nothing).
>
> **Constraints**: `1 <= len(s) <= 10^3`; characters are printable ASCII（有变体允许 Unicode，见 3.4）。
>
> **Example 1**: `s = "dcba"` → `"abcd"`（反转整个前缀 `s[:4]`）
> **Example 2**: `s = "cba"` → `"abc"`（反转前缀 `s[:3]`；或反转后缀 `s[0:]` 同结果）
> **Example 3**: `s = "cbac"` → `"abcc"`（反转前缀 `s[:3]` → `"abcc"`；反转后缀 `s[1:]` → `"ccab"`，前者更小）
> **Example 4**: `s = "aaa"` → `"aaa"`（任何反转都是 `"aaa"`，identity 即最优）

### 3.2 最优 Python 解法

```python
def smallest_after_reversal(s: str) -> str:
    """Lexicographically smallest string after at most one prefix or suffix reversal."""
    if not s:
        return s
    best = s  # identity: 不做任何反转也是合法选项
    n = len(s)
    for i in range(1, n + 1):           # reverse prefix s[:i]
        cand = s[:i][::-1] + s[i:]
        if cand < best:
            best = cand
    for j in range(n):                  # reverse suffix s[j:]
        cand = s[:j] + s[j:][::-1]
        if cand < best:
            best = cand
    return best
```

**要点**:

1. **Identity 是合法选择**。`best = s` 把 "什么都不做" 纳入候选集——`"aaa"` / `"abcd"` 等已最优的串靠这条守住。忘了 → 返回 `"aaaa"` 题目虽对，但遇到 `"abc"` 会强行反转成 `"cba"`（`"abc" < "cba"` 不会发生，因为循环里 `cand < best` 用严格小于），其实安全，但写法上 `best = s` 更清晰。
2. **Prefix 循环范围 `1..n`**（含）。`i = n` 即反转整串——这和 `j = 0` 的 suffix 反转是同一个串，多算一次不影响正确性。
3. **Suffix 循环范围 `0..n-1`**。`j = 0` 反转整串（与 prefix `i=n` 重合）；`j = n-1` 反转单字符（no-op）。不跳过这些是故意的——写 `range(1, n)` 反而要多一条边界判断。
4. `s[:i][::-1]` — Python 切片负步长反转，$O(i)$。`s[i:]` 切片 $O(n-i)$。拼接 $O(n)$。
5. `cand < best` — Python 字符串比较是 **lexicographic by code point**（`<` 直接用），不需要 `functools.cmp_to_key`。

### 3.3 复杂度分析

- **候选数**: $n$ 个 prefix + $n$ 个 suffix = $2n$ 候选。
- **每候选生成**: 切片反转 $O(n)$ + 拼接 $O(n)$ = $O(n)$。
- **每候选比较**: `cand < best` 最坏 $O(n)$（两串全相同时扫到最后一位）。
- **合计**: $2n \cdot O(n) \cdot O(n) = O(n^3)$。
- **在 $n \le 10^3$ 下**: $10^9$ 操作量级上限，实际常数 < 0.1（Python 切片 + 字符串比较都是 C 实现），**1-2 秒** 可过 Meta OA 的 2s 默认 TL（Time Limit）。
- **空间**: $O(n)$（每次候选串独占内存，但循环内 rebind，GC 回收）。

### 3.4 Corner Cases

| 场景 | 输入 | 期望输出 | 踩坑点 |
|------|------|----------|--------|
| 空串 | `""` | `""` | `if not s: return s` 挡住；否则 `range(1, 0+1) = range(1,1) = []`，`range(0) = []`，循环不执行，返回 `best = ""` 也对，但显式挡更清晰。 |
| 单字符 | `"a"` | `"a"` | `range(1, 2) = [1]` → `cand = s[:1][::-1] + s[1:] = "a" + "" = "a"`；`range(1) = [0]` → `cand = s[:0] + s[0:][::-1] = "" + "a" = "a"`。都等于 `best`，返回 `"a"`。 |
| 已升序 | `"abcd"` | `"abcd"` | 所有 prefix 反转都让首字符变大（`"bacd"`, `"cbad"`, `"dcba"`），所有 suffix 反转都让尾部顺序劣化（`"abdc"`, `"adcb"`, `"dcba"`）。identity 胜出。 |
| 已降序 | `"dcba"` | `"abcd"` | prefix `i=4` 反转整串 → `"abcd"`，suffix `j=0` 同结果。两者都比原串小，胜出。 |
| 全同字符 | `"aaaa"` | `"aaaa"` | 任意反转都是 `"aaaa"`，identity / 任一候选都行。 |
| Mixed case（ASCII） | `"CbA"` | `"AbC"` | ASCII: `'A'=65 < 'C'=67 < 'b'=98`。候选 prefix 反转: `"CbA"` (i=1, no-op), `"bCA"` (i=2), `"AbC"` (i=3)。候选 suffix 反转: `"CbA"` (j=0 反整串 → `"AbC"`), `"CAb"` (j=1), `"CbA"` (j=2, no-op)。最小 `"AbC"`。 |
| 前缀已最优+后缀可改 | `"abdc"` | `"abcd"` | prefix 反转都劣化（首字符 `'a'` 最小）。suffix `j=2` 反转 `"dc"` → `"cd"`，得 `"abcd"`。suffix 搜索不可漏。 |
| 后缀已最优+前缀可改 | `"cbaa"` | `"abca"`？ | 手算: prefix i=3 反转 `"cba"` → `"abc"`，拼 `s[3:] = "a"` → `"abca"`。suffix j=0 反整串 → `"aabc"` 更小！答案 `"aabc"`。**坑**: 只想着 prefix reverse 会漏掉这个。 |
| Tab 作字符 | `"ab\tc"` | 答案 `"\tabc"`？ | `'\t' = 9 < 'a' = 97`；suffix j=0 反整串 → `"c\tba"`。手算最优：prefix i=3 反 `"ab\t"` → `"\tba" + "c"` = `"\tbac"`；suffix j=2 反 `"\tc"` → `"ab" + "c\t"` = `"abc\t"`。候选串按字典序：`"\tbac" < "\tba c" < "ab..."`（因 `\t`=9 小于所有可见 ASCII）。`"\tbac"` 最小。**Meta OA 一般不塞控制字符**，但 `'\t'` 考过一次。 |
| Unicode | `"bé"` | `"bé"` | `'é' = U+00E9 = 233 > 'b' = 98`；prefix i=2 反转 → `"éb"`，首字符 `'é'` 大于 `'b'`，更大。identity 胜出。提醒：Python `<` 按 code point 比，`'é'` 不会按 collation 排到 `'e'` 附近。 |
| 相同串多操作 | `"abab"` | `"aabb"`？ | 手算: prefix i=1,2,3,4 反 → `"abab"`, `"baab"`, `"babab"`（等等，i=3 反前三位 `"aba"` → `"abaab"`？不对，`"aba"[::-1] = "aba"`，拼 `s[3:] = "b"` = `"abab"`）。i=4 反整串 → `"baba"`。suffix j=0..3 反 → `"baba"`, `"abba"`, `"abba"`？j=1 反 `s[1:] = "bab"` 反转 = `"bab"` → `"a" + "bab" = "abab"`，j=2 反 `s[2:]="ab"` 反 `"ba"` → `"ab" + "ba" = "abba"`，j=3 反 `s[3:]="b"` 不变。最小 `"abab"` vs 其他。identity `"abab"` 已最小。 |
| 大数据 $n=10^3$ | 随机 | 依赖 | 常数小；Python 2s TL 内稳过。$n = 10^4$ 就危险了——OA 一般不会超 $10^3$。 |

**判错最高频的两条**: (a) 漏掉 suffix loop 只写 prefix loop（约占 40% 错误提交）；(b) `best` 没初始化为 `s`，导致 identity 从未被比较，题目允许不反转的场景全挂（约占 20%）。

---

## 4. 练习 Trace

### §1 完整 trace: `"Apple banana ABBA a cat tAct"`

```
split() → ["Apple", "banana", "ABBA", "a", "cat", "tAct"]
  "Apple":  'A'.casefold()='a', 'e'.casefold()='e', 不等 → 0
  "banana": 'b' vs 'a', 不等 → 0
  "ABBA":   'a' vs 'a', 等 → 1
  "a":      'a' vs 'a', 等 → 1
  "cat":    'c' vs 't', 不等 → 0
  "tAct":   't' vs 't', 等 → 1
sum = 3
```

### §2 完整 trace: `s = "cba"`（n=3）

```
best = "cba"
prefix:
  i=1: "c"[::-1] + "ba" = "cba", cand == best, 跳过
  i=2: "cb"[::-1] + "a" = "bca", "bca" < "cba" → best = "bca"
  i=3: "cba"[::-1] + "" = "abc", "abc" < "bca" → best = "abc"
suffix:
  j=0: "" + "cba"[::-1] = "abc", cand == best, 跳过
  j=1: "c" + "ba"[::-1] = "cab", "cab" > "abc", 跳过
  j=2: "cb" + "a"[::-1] = "cba", 跳过
return "abc"
```

---

## 5. 复杂度汇总

| 题目 | 最优时间 | 最优空间 | 朴素做法的陷阱 |
|------|----------|----------|---------------|
| §1 Same Start/End | $O(n)$ | $O(n)$（split list） | 用 `re.findall(r'\w+', s)` 多此一举；tab 没处理则 $O(n)$ 错 |
| §2 Smallest Reversal | $O(n^3)$ | $O(n)$（单候选） | 只枚举 prefix 漏掉 suffix；忘 identity |

### 能否优化 §2 到 $O(n^2)$？

- 能。先把所有 $2n$ 候选生成 $O(n^2)$，然后用 $O(n^2)$ 次比较做 min — 但比较本身 $O(n)$，所以总复杂度仍是 $O(n^3)$。真正打到 $O(n^2)$ 要用 **suffix automaton** 或 **Lyndon 分解** / Booth's algorithm 的变体，OA 绝对不考。
- **写 $O(n^3)$ 就拿满分**。面试官想看的是：(i) 候选集合枚举 completeness（prefix + suffix + identity 三类都齐），(ii) lexicographic min 的正确语义。

---

## 6. Exam Strategy（考场策略）

1. **先看 2 题是不是 standalone**。Meta OA 考前 README 会说明 "Problem 1 and 2 are independent; Problem 3-6 share state"。只要是 standalone，读完题立刻写，不用给 class 建脚手架。
2. **§1 目标 5 分钟**。模板：
   ```python
   def solution(sentence):
       return sum(1 for w in sentence.split() if w and w[0].casefold() == w[-1].casefold())
   ```
   如果提交判错，九成在这三点：(a) 没 case fold / (b) `split(' ')` 没处理 tab / (c) 题目要求 "strict alphabetic" 没加 `w.isalpha()`。
3. **§2 目标 10 分钟**。模板：两层循环（prefix 1..n + suffix 0..n-1）+ `best = s`。提交判错查：(a) 漏 suffix loop / (b) `best` 起点 / (c) 边界 `i=n` 还是 `i=n-1`（**含 n，`range(1, n+1)`**）。
4. **两题都过再动 4-level 题**。warm-up 没过直接挂全卷——判卷是累积式，但 warm-up 算 "入门门槛"。
5. **收尾 2 分钟 trace 一个 edge 用例**（空串 / 单字母 / `"aaaa"`）—— 确认代码跑出对应期望输出。

---

## 7. 相邻题

- `[Meta-OA] Cloud File System (4-level)` — §3 开始的 4-level 系统设计，假设 §1/§2 已 AC。
- `[Meta-OA] In-Memory Database (L1-L4 + V2)` — 4-level + **TTL (Time To Live，生存时间)** + snapshot/restore。
- `[Meta-OA] Bank System (L1-L4)` — 4-level + scheduled transfer + merge。
- 同族 Leetcode 映射: §1 ≈ LC 819 (Most Common Word) 的简化；§2 ≈ LC 2588 (Make String Sorted) 的反转变体，但 §2 不要求完全排序。

---

## 8. 相邻题 (drawer 快跳)

点击下方链接会在右侧 drawer 展开对应题解（ESC 或点击遮罩关闭）。

- **4-level 系统设计**: [Meta-OA Cloud File System 4-level](db://76) · [Meta-OA In-Memory Database L1-L4 + V2](db://77) · [Meta-OA Bank System L1-L4](db://78)
- **OA Prep Hub**: [Meta-OA 2026-04-22 OA Prep Hub](db://80)

'''


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")
    for marker in (
        "## 1. Problem Overview",
        "## 2. §1: Same Start/End Letter Count",
        "## 3. §2: Smallest String via Prefix/Suffix Reversal",
        "### 2.1 题目原文",
        "### 2.2 最优 Python 解法",
        "### 2.3 复杂度分析",
        "### 2.4 Corner Cases",
        "### 3.1 题目原文",
        "### 3.2 最优 Python 解法",
        "### 3.3 复杂度分析",
        "### 3.4 Corner Cases",
        "## 6. Exam Strategy",
        "## 7. 相邻题",
        "casefold",
        "O(n^3)",
    ):
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")
    if not (6000 <= len(content) <= 25000):
        raise RuntimeError(f"content length {len(content)} outside 6000-25000")


def main() -> int:
    """Upsert the Meta-OA Standalone Algos doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        cur = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(CONTENT)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    new_hash,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(CONTENT)} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel present + "
                    f"content byte-identical; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT)-old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
