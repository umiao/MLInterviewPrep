"""Seed Google coding prep for T-P1-208: Jammed Keyboard Dictionary Match.

Custom (non-LC) problem: on a jammed keyboard, certain keys are fused into
equivalence groups -- pressing any letter in a group types the same "bucket".
Given the group partition, a typed string, and a dictionary of candidate
words, return all dictionary words that could have produced the typed
string (i.e., same length and each letter sits in the same group).

Solutions captured: (1) signature-bucket hash index, (2) group-keyed trie.
Follow-up chain: multi-query preprocessing, dynamic dictionary, shifting
groups, memory-tight hashing.

Idempotent: re-running updates in place. Chinese prose; code + complexity
in English per feedback_lc_notes_chinese.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"

TITLE = "Jammed Keyboard Dictionary Match"

DESCRIPTION = """Google coding interview (custom, non-LC).

Setting: a keyboard has some keys physically jammed together into
equivalence groups. Each group is a set of letters that all register as
"the same key". You are given:
- `groups`: a partition of the 26 lowercase letters into disjoint groups,
  e.g., `[{a,b,c}, {d,e}, {f}, ...]`.
- `typed`: a string that was produced on the jammed keyboard.
- `dictionary`: a list of candidate words.

Return every word in the dictionary that *could* have produced `typed` --
that is, every word `w` such that `len(w) == len(typed)` and for all `i`,
letters `w[i]` and `typed[i]` belong to the same group.

Example: groups = [{a,b,c}, {d,e,f}, ...], typed = "bad",
dictionary = ["cab", "abc", "bed", "bee", "cad", "dab", "bade"].
Signature of typed = (G0, G0, G1) where G0={a,b,c}, G1={d,e,f}.
Matches: "cab"(G0,G0,G0) no, "abc"(G0,G0,G0) no, "bed"(G1,G1,G1) no,
"cad"(G0,G0,G1) yes, "dab"(G1,G0,G0) no, "bade" length mismatch.
-> Answer: ["cad"].

Follow-up chain:
(A) Many queries, fixed dictionary and fixed groups: preprocess once.
(B) Dictionary keeps growing: support O(L) insertion.
(C) Groups shift between queries (keys un-jam): cannot reuse old signatures.
(D) 26-letter alphabet extended to Unicode / emoji: memory pressure.
"""

NOTES = """## Jammed Keyboard Dictionary Match (Google 2026-04-17)

### 建模：group-id 签名

把 `groups` 转成 `letter_to_gid: dict[str, int]`（26 个字母 O(1) 即可）。
任意字符串 `w` 的**签名**定义为
$\\text{sig}(w) = (g_{w_0}, g_{w_1}, \\dots, g_{w_{n-1}})$
其中 $g_c$ = 字母 $c$ 所属的组编号。两个串在 jammed 键盘上**不可区分**
当且仅当它们签名相等。于是原问题等价于：

> 字典里哪些词与 `typed` 有相同签名？

### 解法 1：Signature Bucket（推荐作为主答案）

预处理：把字典按签名分桶（`dict[tuple[int,...], list[str]]`）。
查询：计算 `sig(typed)`，查桶。

```python
from collections import defaultdict

def build_index(dictionary: list[str], groups: list[set[str]]) -> tuple[dict, dict]:
    letter_to_gid = {c: i for i, g in enumerate(groups) for c in g}
    bucket: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for w in dictionary:
        sig = tuple(letter_to_gid[c] for c in w)
        bucket[sig].append(w)
    return bucket, letter_to_gid

def query(typed: str, bucket, letter_to_gid) -> list[str]:
    sig = tuple(letter_to_gid[c] for c in typed)
    return bucket.get(sig, [])
```

**复杂度**：设 $N$ 字典词数，$L$ 平均词长，$Q$ 查询数。
- 预处理 $O(N L)$ 时间、$O(N L)$ 空间（存签名 + 词）。
- 单次查询 $O(L)$（算签名 + 哈希查桶）。
- 若只要**数量**而不要词本身，空间可压到 $O(N)$（桶值存计数或存 id）。

**要点**：
1. `tuple` 可哈希，直接作 dict key；别用 `list`。
2. 只需签名相等，不用再逐字母 compare —— hash 冲突用 Python dict 自己的
   equality 兜底，面试一般不用担心。
3. 字典可为空、`typed` 含字典外字母需定义行为：通常把外字母映射到
   独立新 gid（或直接 KeyError 然后返回空）。

### 解法 2：Group-keyed Trie（follow-up B 的主力）

把字典插入一棵 trie，但 children 不以字母为 key，而以**组 id** 为 key。
查询时按 `typed` 的组 id 路径下行，叶节点挂所有落在该路径的原词。

```python
class TrieNode:
    __slots__ = ("children", "words")
    def __init__(self) -> None:
        self.children: dict[int, "TrieNode"] = {}
        self.words: list[str] = []

def insert(root: TrieNode, w: str, letter_to_gid: dict[str, int]) -> None:
    node = root
    for c in w:
        gid = letter_to_gid[c]
        node = node.children.setdefault(gid, TrieNode())
    node.words.append(w)

def query_trie(root: TrieNode, typed: str, letter_to_gid) -> list[str]:
    node = root
    for c in typed:
        gid = letter_to_gid[c]
        if gid not in node.children:
            return []
        node = node.children[gid]
    return node.words
```

**复杂度**：
- 插入/查询都是 $O(L)$。
- 空间 $O(\\sum L)$ 最坏；若大量公共前缀则显著少于签名桶。
- **相比签名桶**的优势：支持前缀查询、流式插入、以及在"键盘分组变化"
  下只需重建 `letter_to_gid`（但 trie 结构本身已经烧入旧 gid，必须重建
  trie —— 见 follow-up C）。

### Follow-up 响应

**(A) 多次查询 / 固定字典 / 固定分组**
一次预处理（签名桶或 trie），之后每次查询 $O(L)$。签名桶更简单，面试里
先给它；trie 的价值在 (B)。

**(B) 字典持续增长**
签名桶支持 $O(L)$ 插入（算签名 + append）。trie 同 $O(L)$ 但对长公共
前缀更省内存。无论哪种，都不用重建整个结构。

**(C) 分组变化（某个键修好了 / 新键卡住了）**
旧签名作废。两种策略：
1. **只改几个字母**：遍历受影响字母的倒排索引 (`letter -> word_ids`)，
   只重算这些词的签名；其余桶不动。
2. **大范围改动**：直接从头重建，$O(N L)$。
面试可先问"分组变化频率"再选策略 —— 典型的澄清分支。

**(D) 字母表巨大 / Unicode**
签名桶仍然能用（tuple of int gid），trie 的 `dict` children 也只按实际
出现的 gid 分配，空间主导项是字典本身。若字典大到内存吃不下，
可把签名哈希到 64-bit 整数存桶：`hash(sig)`，面试补一句"哈希冲突用
字典内 equality 兜底"。

### 正确性证明

对字符串 $w$ 和 $t$，"在 jammed 键盘上不可区分" 的等价定义：
$\\forall i. w_i, t_i \\in \\text{same group} \\iff g_{w_i} = g_{t_i}$
即 $\\text{sig}(w) = \\text{sig}(t)$。因此签名相等 $\\iff$ 可行匹配。

长度不等的两串签名不等（tuple 长度不同），自动淘汰，不用额外判 len。

### 常见错误对照

| 错误做法 | 问题 |
|----------|------|
| 用 `set(groups[i])` 作 key | set 不可哈希，需要 `frozenset` 或 gid |
| 把 `typed` 每字母去逐个遍历字典 | $O(N L)$ 每次查询，follow-up A 爆炸 |
| Trie 的 children 用字母而非 gid | 就是普通字典树，无法利用等价组 |
| 忽略 len 不等的早退 | tuple 比较自带，但 follow-up C 按字母重算时容易忘 |
| 签名用字符串拼接 `str(gid)` 无分隔符 | `(1,12)` 与 `(11,2)` 碰撞；要么用 tuple 要么加分隔符 |

### 与相关题的联系

- **LC 249 Group Shifted Strings**：签名 = 相邻差分，结构一样的分桶题。
- **LC 49 Group Anagrams**：签名 = sorted(word) 或字频 tuple。
- **LC 1032 Stream of Characters**：反向 trie 支持流式后缀查询；和 (B) 的
  trie 插入方向不同但数据结构同源。
- 本题可视为"把 anagram 分桶里的 sorted-signature 换成 group-id-signature"
  的一族模板。

### 面试应答 checklist

1. 澄清：分组是否固定？查询多少次？字典规模？字母表？是否要返回词还是
   只要计数？大小写？非字母？
2. 先给**签名桶** $O(NL)$ 预处理 + $O(L)$ 查询。
3. 再给 **trie** 版本，强调流式插入与前缀能力。
4. 回答 follow-up：分组变化 -> 倒排索引只重算受影响的词。
5. 谈 Unicode / 大字母表 -> 签名哈希到 64-bit。
6. 提 anagram / shifted string 作为同族题以秀模板意识。
"""


def verify_examples() -> None:
    """Self-check both algorithms against hand-worked cases."""
    from collections import defaultdict

    groups = [set("abc"), set("def"), set("ghi"), set("jkl"), set("mno"),
              set("pqr"), set("stu"), set("vwx"), set("yz")]
    # 补足剩余字母(刚好覆盖 a-z)
    covered = set().union(*groups)
    assert covered == set("abcdefghijklmnopqrstuvwxyz"), covered

    letter_to_gid = {c: i for i, g in enumerate(groups) for c in g}

    def sig(w: str) -> tuple[int, ...]:
        return tuple(letter_to_gid[c] for c in w)

    dictionary = ["cab", "abc", "bed", "bee", "cad", "dab", "bade", "fad", "fed"]
    typed = "bad"
    bucket: dict = defaultdict(list)
    for w in dictionary:
        bucket[sig(w)].append(w)
    matches = bucket.get(sig(typed), [])
    # typed "bad" -> (0,0,1); check which dict words share that
    expected = [w for w in dictionary if sig(w) == sig(typed)]
    assert sorted(matches) == sorted(expected), (matches, expected)

    # trie alternative
    class TrieNode:
        __slots__ = ("children", "words")
        def __init__(self) -> None:
            self.children = {}
            self.words = []

    root = TrieNode()
    for w in dictionary:
        node = root
        for c in w:
            gid = letter_to_gid[c]
            node = node.children.setdefault(gid, TrieNode())
        node.words.append(w)
    node = root
    ok = True
    for c in typed:
        gid = letter_to_gid[c]
        if gid not in node.children:
            ok = False
            break
        node = node.children[gid]
    trie_matches = node.words if ok else []
    assert sorted(trie_matches) == sorted(expected), (trie_matches, expected)

    # length mismatch auto-rejected
    assert sig("bade") != sig(typed)

    print("algorithm self-checks: all passed [OK]")


def upsert_problem(cur: sqlite3.Cursor) -> int:
    cur.execute(
        "SELECT id FROM problems WHERE leetcode_id IS NULL AND title=?",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(
        ["trie", "hashing", "bucket", "signature", "string"],
        ensure_ascii=False,
    )
    company_json = json.dumps(["Google"], ensure_ascii=False)
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET description=?, notes=?, tags=?, pattern=?, category=?, "
            "company_tags=?, source=?, difficulty=?, priority=? WHERE id=?",
            (DESCRIPTION, NOTES, tags_json, "bucket-trie", "algorithm",
             company_json, SOURCE_BADGE, "medium", 1, pid),
        )
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, description, notes, tags, pattern, "
        "category, company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (TITLE, DESCRIPTION, NOTES, tags_json, "bucket-trie", "algorithm",
         company_json, SOURCE_BADGE, "medium", 1, now),
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
