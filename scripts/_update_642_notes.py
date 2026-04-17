"""One-shot: write LC 642 solution notes in Chinese."""
import sqlite3

NOTES = r'''## LC 642 - Design Search Autocomplete System (Trie + Heap)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/company/pinterest/recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### 核心重述 (THE Key Insight)

在线搜索自动补全：给定历史句子 `sentences[]` 与对应热度 `times[]`，支持流式 `input(c)`：
- `c` 是字母、空格或 `'#'`。
- `'#'` 表示当前句子输入结束，把它累计到词频表里（新句子热度为 1，已有句子 `+=1`），返回 `[]`。
- 否则返回 Top 3 按 `(热度降序, 字典序升序)` 排序的、以当前前缀开头的历史句子。

**核心洞察**：
1. **Trie 按前缀分组**：把每个句子挂到 trie 路径上，并在每个节点缓存 "从该节点出发能到达的所有完整句子 → 热度" 的字典。
2. **在输入流中增量维护当前指针**：`input` 按字符流进入，只要维护一个"当前所在 trie 节点" `cur`，每进一个字符就下移一步，无需每次从根重走。
3. **Top 3 排序规则**：主键热度降序，次键字典序升序（注意空格 `' '` 在 ASCII 中 < 字母，所以字典序要直接用字符串比较即可正确处理）。

### Approach A: Trie + 节点缓存句子表 (推荐)

每个 trie 节点存 `counts: Dict[str, int]`，记录"经过该节点的所有完整句子及其热度"。`input('#')` 时沿刚才的路径每个节点都 `counts[sentence] += 1`。

```python
class TrieNode:
    __slots__ = ("children", "counts")
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.counts: dict[str, int] = {}  # sentence -> hot

class AutocompleteSystem:
    def __init__(self, sentences: list[str], times: list[int]):
        self.root = TrieNode()
        self.cur = self.root
        self.buf: list[str] = []
        self.dead = False  # 当前前缀已无匹配，后续字符直接返回 []
        for s, t in zip(sentences, times):
            self._insert(s, t)

    def _insert(self, sentence: str, hot: int) -> None:
        node = self.root
        for ch in sentence:
            node = node.children.setdefault(ch, TrieNode())
            node.counts[sentence] = node.counts.get(sentence, 0) + hot

    def input(self, c: str) -> list[str]:
        if c == "#":
            sentence = "".join(self.buf)
            self._insert(sentence, 1)
            self.buf.clear()
            self.cur = self.root
            self.dead = False
            return []
        self.buf.append(c)
        if self.dead:
            return []
        nxt = self.cur.children.get(c)
        if nxt is None:
            self.cur = self.root  # 任意占位，反正 dead 了
            self.dead = True
            return []
        self.cur = nxt
        # Top 3: (-hot, sentence) 升序
        items = self.cur.counts.items()
        top = sorted(items, key=lambda kv: (-kv[1], kv[0]))[:3]
        return [s for s, _ in top]
```

**复杂度**：
- `_insert`：O(L) 时间，L 是句子长度，每个节点写一次 `counts`。
- `input(c)` (非 `#`)：匹配 O(1)，排序 O(k log k)，k = 该节点 `counts` 大小。Top-3 可用 `heapq.nsmallest(3, items, key=...)` 得到 O(k) + O(3 log k)，常数更小。
- 空间：O(总字符数)，每个节点的 `counts` 累计起来是 Σ L_i。

### Approach B: Trie + 只在叶节点存计数 + DFS 收集

节点只在句子结束处记 `count`。`input` 到达 `cur` 后，DFS 整棵子树收集所有 `count > 0` 的句子再排序。空间更省（不重复存句子），但每次查询耗时 = O(子树节点数 + k log k)。前缀短时代价大。工业上多用 Approach A 的缓存版。

### Approach C: 直接线性扫描词频表

维护 `dict[sentence -> count]`，每次 `input` 扫所有 key 判前缀。代码 10 行就写完，适合面试"先 brute"。复杂度 O(N·L)，N = 历史句子数。能过 LC 数据，但面试官问"如何扩展到百万句子" 就得切到 trie。

### Code Review 要点 (常见失误)

- **`'#'` 分支要重置 `buf` 和 `cur`**，否则下一句的前缀会接着上一个算。
- **新句子热度是 1，不是 0**。`_insert` 里必须 `+= hot` 而非 `= hot`：已有句子 `'#'` 时要在旧热度基础上 +1（共享 trie 节点）。
- **`dead` 标志**：一旦某个字符不在当前节点的 children 中，后续所有字符（直到 `'#'`）都应返回 `[]`，但 `buf` 还要继续累积（`'#'` 时把这个新句子热度 1 插入）。漏掉 `dead` 会让后续 `input` 触发 KeyError 或误命中其他子树。
- **排序次键是字典序升序，不是降序**。`key=(-hot, sentence)` 中 `sentence` 不加负号。
- **空格参与比较**：句子含 `' '` (ASCII 32) < 字母，直接字符串比较即可，别手动跳过。
- **热度相同取前 3 要稳定按字母序**，不能依赖 dict 插入序。
- **重复插入同一句子**：`'#'` 时该句子已存在，走到每个节点 `counts[sentence]` 都要 `+= 1`，与首次插入共用 `_insert` 逻辑即可。
- **Trie 节点 `__slots__`**：用 `__slots__` 省内存，节点数量可能很大 (题目约束 sentences 最长 100，总字符百万级)。

### 识别模板 (When to Use This Pattern)

- "流式前缀匹配 / 自动补全 / 搜索框下拉框"。
- 查询按前缀 + Top-K 排序 (热度、字母序)，插入/更新频繁 → Trie + 节点缓存是标准答案。
- 同族：LC 208 Implement Trie、LC 211 Add and Search Word、LC 677 Map Sum Pairs、LC 1268 Search Suggestions System、LC 212 Word Search II。

### 面试叙述模板 (Talking Points)

1. "我维护一棵 trie，每个节点缓存一个 `sentence -> hotness` 字典，表示所有经过这个节点的完整句子。"
2. "流式输入维护 `cur` 指针 + `buf` 缓冲。普通字符下移一步，返回当前节点 `counts` 按 `(-hot, sentence)` 排序的前 3。"
3. "`'#'` 时把 buf 里的句子 `+=1` 插回 trie (新句从 1 开始)，清 buf，cur 回 root。"
4. "匹配失败我用 `dead` 标志短路，避免重复查找，但继续累积 buf 为将来插入做准备。"
5. "复杂度：插入 O(L)，查询 O(k log k)，k 是当前节点的句子数。如果 k 很大可用 heap 做 nsmallest 到 O(k)。"
6. 扩展："如果 sentences 上亿条，可以分布式 sharding 按前缀 hash，或者用 FST / DAWG 压缩 trie。"

### 为什么不用 HashMap + 全量扫描

- 句子数 N、平均长度 L，每次 `input` 非 `#` 都扫全表 → O(N·L)。LC 642 数据小能过，工业场景 (Google Suggest、淘宝搜索框) 百万级 QPS + 亿级语料必爆。
- Trie 把"前缀分组"的开销从查询时摊到插入时，换来查询 O(k log k)，k ≪ N。

### Complexity Summary

| Approach | Insert | Query (input c) | Space |
|----------|--------|-----------------|-------|
| Trie + 节点 counts (A) | O(L) | O(k log k)，k=子树句子数 | O(Σ L) 放大常数 |
| Trie + 叶 count + DFS (B) | O(L) | O(子树节点数 + k log k) | O(Σ L) 最省 |
| HashMap 线扫 (C) | O(1) | O(N·L) | O(N·L) |
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 642", (NOTES,))
conn.commit()
cur = conn.execute("SELECT length(notes) FROM problems WHERE leetcode_id = 642")
print(f"[OK] LC 642 notes updated ({cur.fetchone()[0]} chars)")
conn.close()
