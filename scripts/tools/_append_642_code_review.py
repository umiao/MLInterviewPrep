# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Append a 'Code Review of Your Solution' section to LC 642 notes,
analyzing user's submitted Trie + cursor + dead-flag design."""
import sqlite3

APPENDIX = r'''

---

### Code Review：你的 Trie + cursor 写法

**总评**：结构整体正确，核心优化（incremental cursor + dead flag）都到位，属于"能 AC 且时间常数小"的实现。但在 **API 清晰度 + 职责耦合 + 一处潜在 bug** 上有改进空间。下面按严重程度排序。

#### 1. `Trie.match(word, startNode)` 的双模 API 令人困惑

你的 `match` 同时承担两种职责：
- 从 root 走完整 word（模式 A，但实际没人用）
- 从 cursor 走增量字符（模式 B，`AutocompleteSystem.input` 只用这个）

两种模式共享一个函数，参数名还叫 `word`（其实传进来是单字符），读者必须追到 caller 才理解。**拆成两个方法更清晰**：

```python
class Trie:
    def advance(self, ch: str) -> list[tuple[str, int]]:
        """从当前 cursor 消费一个字符，返回该前缀的 top-3 建议。"""
        if self.dead:
            return []
        if ch not in self.cursor.children:
            self.dead = True
            return []
        self.cursor = self.cursor.children[ch]
        return self._top3_under(self.cursor)

    def reset(self) -> None:
        self.cursor = self.root
        self.dead = False
```

职责单一，调用方只需 `trie.advance(ch)`，不用关心 cursor / dead 内部状态。

#### 2. `dead` 状态泄漏到 `AutocompleteSystem`

你的 `input` 里：
```python
if self.Trie.dead:
    return []
ans = self.Trie.match(c, startNode=self.Trie.curNode)
```

`AutocompleteSystem` 正在读 `Trie` 的私有状态 `dead` —— 违反封装。`match` 内部其实也检查了 dead（返回 `[]`），所以外层这个 `if self.Trie.dead` **是冗余的**。删掉它，或者让 `advance` 自己处理。

#### 3. `TrieNode.trie = defaultdict(TrieNode)` 的隐式副作用

在 `insert` 里 `curNode.trie[char]` 利用 defaultdict 自动创建子节点 —— 很顺手。但在 `match` 之外的地方如果你误写 `curNode.trie[char]` 做查询，会**静默创建一个空节点**，后续 DFS 会遍历到它导致幽灵结果。

**建议**：insert 里继续用 defaultdict 的自动创建；match 和 DFS 里严格用 `in` 检查 + `children.get()`，或者干脆把 `trie` 换成普通 dict + insert 里显式 `setdefault`：

```python
class TrieNode:
    __slots__ = ("children", "word", "freq")
    def __init__(self):
        self.children = {}
        self.word = ""
        self.freq = 0

def insert(self, word, freq):
    node = self.root
    for ch in word:
        node = node.children.setdefault(ch, TrieNode())
    node.word = word
    node.freq += freq
```

显式构造让"哪里会创建新节点"一目了然。`__slots__` 顺带省内存。

#### 4. 双重返回信号：`self.dead = True` + `return []`

同一次 match 失败同时写两处状态：`self.curNode = curNode; self.dead = True; return []`。调用方有两种检查方式（看返回值 或 看 dead flag），容易出现"两处不一致"的 bug。

**简化**：dead flag 就够了（用于下一次 input 提前退出），不需要 match 返回 `[]` 作为额外信号；或者反过来，用返回值，删掉 dead。任选其一别两者都要。

#### 5. `heapq.nsmallest(3, ans, key=...)` vs `sorted(...)[:3]`

你写的：
```python
return heapq.nsmallest(3, ans, key=lambda x: (-x[1], x[0]))
```

`nsmallest(K, n_items)` 是 O(N log K)，当 N 大 K 小时比 `sorted(...)[:K]` 的 O(N log N) 快。在这题里 N 是所有以当前前缀为起点的完整句子数，往往 N 很小（十几个），所以两种写法实际无差。

但你的写法**语义更好看**：明确说"取 top 3"，而不是"全部排序再切片"。保留。

#### 6. 性能进阶：每个节点预存 top-3（scale-up 优化）

目前 `_top3_under(node)` 每次调用都 DFS 整个子树。若 `sentences` 里有百万级句子，每次 input 就是一次 O(subtree_size) 操作，慢。

**优化**：insert 时自底向上维护每个节点的 `top3: list[(freq, word)]`。input 时直接读 `cursor.top3`，O(3)。代价：insert 从 O(L) 变 O(L · K · log K)，对这题 K=3 可忽略。

面试时可以提这个作为 "如果数据规模上升到 1M 句子，怎么优化读路径" 的答法，加分项。

#### 改进后的完整版（参考）

```python
class TrieNode:
    __slots__ = ("children", "word", "freq")
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.word: str = ""
        self.freq: int = 0

class AutocompleteSystem:
    def __init__(self, sentences: list[str], times: list[int]):
        self.root = TrieNode()
        for s, t in zip(sentences, times):
            self._insert(s, t)
        self.cursor: TrieNode | None = self.root
        self.buf: list[str] = []

    def _insert(self, word: str, freq: int) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.word = word
        node.freq += freq

    def _collect(self, node: TrieNode) -> list[tuple[str, int]]:
        out = []
        stack = [node]
        while stack:
            u = stack.pop()
            if u.word:
                out.append((u.word, u.freq))
            stack.extend(u.children.values())
        return out

    def input(self, c: str) -> list[str]:
        if c == "#":
            self._insert("".join(self.buf), 1)
            self.buf.clear()
            self.cursor = self.root
            return []
        self.buf.append(c)
        if self.cursor is None:
            return []
        self.cursor = self.cursor.children.get(c)
        if self.cursor is None:
            return []
        cands = self._collect(self.cursor)
        top3 = heapq.nsmallest(3, cands, key=lambda p: (-p[1], p[0]))
        return [w for w, _ in top3]
```

关键差异：
- 没有独立的 `Trie` 类 —— `AutocompleteSystem` 直接管理 trie（单一类，职责明确）
- `cursor = None` 代替 `dead` flag，用 Python 的 `Optional` 自然表达
- 用**迭代 DFS**（`stack`）代替递归，避免深度大时 RecursionError
- `collect` 和 `top-k` 分离，逻辑阶梯更清晰

### 总结

| 方面 | 你的 | 改进 |
|------|------|------|
| API 清晰度 | `match(word, startNode)` 双模 | `advance(ch)` 单模 |
| 封装 | `input` 读 `Trie.dead` | `cursor = None` 或 advance 自处理 |
| 自动创建子节点 | `defaultdict(TrieNode)` 全程 | insert 里 `setdefault`，查询用 `get` |
| 返回信号 | dead flag + `[]` 双重 | 只用一种 |
| 递归 DFS | 可能栈溢出 | 迭代 stack 版 |
| 规模扩展 | 每次 full DFS 子树 | 每节点预存 top-3 |

**你的版本能 AC 没问题**，以上是往 "production-ready / 面试白板优雅度" 方向的改进建议。
'''

conn = sqlite3.connect("data/mle_prep.db")
row = conn.execute("SELECT notes FROM problems WHERE leetcode_id = 642").fetchone()
new_notes = row[0] + APPENDIX
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 642", (new_notes,))
conn.commit()
print(f"[OK] LC 642 notes extended: {len(row[0])} -> {len(new_notes)} chars")
conn.close()
