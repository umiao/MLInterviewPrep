"""Polish Pinterest custom problem notes (1068, 1071–1076) per user feedback 2026-04-15.

Fixes:
- Drop awkward calque "物化 (materialize)" in favor of natural Chinese ("展开缓存", "预计算闭包").
- Remove duplicated English+Chinese parallel sections (1071, 1073) — keep one Chinese-primary narrative
  per feedback_lc_notes_chinese.md (prose Chinese, code/algorithm names/complexity English).
- Normalize code blocks: 4-space indent, consistent docstring style, strip unused type-hint noise.
- Tighten problem descriptions for fluency.
- Preserve 45-sec 口播 scripts where present / add where useful.

Idempotent: re-running overwrites notes + descriptions to canonical versions.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# ------------------------------------------------------------------ 1068 ---
DESC_1068 = """[Pinterest coding 2026-11] 设计一个逃脱房间游戏的状态管理器。

初始化 `Game(rooms, people)`，`rooms` 是按前进顺序排列的房间号列表，`people` 是初始玩家列表（全部起始于 rooms[0]）。支持三个操作：

- `proceedToNextRoom(pid)` — 玩家 pid 前进到下一个房间。玩家可以乱序前进（谁先解谜谁先走）。O(1)。
- `getPeople(roomId)` — 返回 `roomId` 中的玩家列表，按进入该房间的时间顺序。O(k)。
- `getTop(K)` — 返回前 K 名玩家：房号越靠后越领先；同房内按进入时间先后排序。O(R + K)。

*题面整理 2026-04-15。*"""

NOTES_1068 = """## Escape Room Game State (Pinterest 2025-11)

三个操作：
- `proceedToNextRoom(pid)` — 玩家 pid 前进一房，O(1)
- `getPeople(roomId)` — 按入房顺序返回房内玩家，O(k)
- `getTop(K)` — 按 (房号降序, 同房入房序) 返回前 K 名，O(R + K)

### 数据结构
- **每房一个双向链表（DLL）**：O(1) 尾部 append、O(1) 按节点指针 unlink。
- **全局 `pid → Node` 哈希**：O(1) 定位某人当前节点。
- **`pid → next_idx`**：预存前进序列中下一位的下标，避免每次 O(R) 扫描。

**为什么必须用 DLL**：玩家不按 FIFO 离开（先解谜者先走），要从队列中间 O(1) 摘除。`list.remove` 和 `collections.deque` 的中间删除都是 O(k)。Node 里反存 `room_id`，unlink 时才知道属于哪个房间的链表。

### Code

```python
class _Node:
    __slots__ = ('pid', 'room_id', 'prev', 'next')
    def __init__(self, pid, room_id):
        self.pid, self.room_id = pid, room_id
        self.prev = self.next = None

class _DLL:
    __slots__ = ('head', 'tail', 'size')
    def __init__(self):
        self.head = self.tail = None
        self.size = 0

    def append(self, node):
        node.prev, node.next = self.tail, None
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self.size += 1

    def unlink(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = node.next = None
        self.size -= 1

    def iter_forward(self):
        cur = self.head
        while cur:
            yield cur
            cur = cur.next


class Game:
    def __init__(self, rooms, people):
        self._order = list(rooms)
        self._order_desc = list(reversed(rooms))
        self._rooms = {rid: _DLL() for rid in rooms}
        self._people = {}
        self._next_idx = {}
        start = rooms[0]
        for pid in people:
            node = _Node(pid, start)
            self._rooms[start].append(node)
            self._people[pid] = node
            self._next_idx[pid] = 1 if len(rooms) > 1 else -1

    def proceedToNextRoom(self, pid):
        node = self._people[pid]
        nxt = self._next_idx[pid]
        if nxt == -1:
            return  # already final
        self._rooms[node.room_id].unlink(node)
        new_room = self._order[nxt]
        node.room_id = new_room
        self._rooms[new_room].append(node)
        self._next_idx[pid] = nxt + 1 if nxt + 1 < len(self._order) else -1

    def getPeople(self, roomId):
        dll = self._rooms.get(roomId)
        return [n.pid for n in dll.iter_forward()] if dll else []

    def getTop(self, K):
        out = []
        for rid in self._order_desc:
            for n in self._rooms[rid].iter_forward():
                out.append(n.pid)
                if len(out) == K:
                    return out
        return out
```

### 复杂度

| Op | Time |
|----|------|
| `__init__` | O(R + N) |
| `proceedToNextRoom` | O(1) |
| `getPeople(roomId)` | O(k) |
| `getTop(K)` | O(R + K) |

### 陷阱
1. Node 里要反存 `room_id`，unlink 时才能定位所属链表。
2. `_next_idx` 预存，避免每次 `rooms.index(current)` 的 O(R) 扫描。
3. 终点房用 `-1` 哨兵，`proceedToNextRoom` 直接 no-op。

### 追问
- **getTop 降到 O(K)**：再维护一个"非空房间"的房号降序 DLL，append / unlink 时同步更新。
- **玩家可跳过某些房间**：把 `_next_idx` 换成每人自己的剩余房间序列列表，仍然 O(1)。

### 45 秒口播
> "核心是每房一个双向链表加全局 pid→Node 哈希。必须用双向链表是因为玩家不按 FIFO 离开——先解谜者先走——要从队列中间 O(1) 摘除，list 和 deque 的中间删都做不到。Node 反存 room_id 让 unlink 能找到所属链表。proceedToNextRoom 就是 O(1) 的 unlink 旧房加 append 新房尾部；入房尾部保证同房内入房顺序正确。getTop 按房号倒序扫链表正向累计到 K，O(R + K)；若要 O(K) 可以再维护一个非空房间的房号降序链表。关键冗余是 pid→Node 让定位 O(1)，next_idx 预存前进下标避免每次扫 rooms。"
"""

# ------------------------------------------------------------------ 1071 ---
DESC_1071 = """[Pinterest coding 2026-11] 二维网格上的光束传播模拟。灯塔从某个方向发射光束，光束按格子前进并与网格内容发生交互：

- `.`  空格子       — 方向不变继续前进
- `/`  镜子         — `(dr, dc) → (-dc, -dr)`，如向右入射反射成向上
- `\\`  镜子         — `(dr, dc) → ( dc,  dr)`，如向右入射反射成向下
- `|`  分束器       — 水平入射分成上 + 下两束；垂直入射直穿
- `-`  分束器       — 垂直入射分成左 + 右两束；水平入射直穿

统计光束离开网格或循环终止前被照亮的**不同格子数**。

**常见追问**：
(a) 多个灯塔同时发射：取所有被照亮集合的并集。
(b) 最佳放置：枚举每个边界格作为光源，报告最大照亮数（朴素 `O(N·M·(N+M))`）。
(c) 循环检测：由 `(格子, 方向)` 的 visited 集合天然保证终止。

*题面整理 2026-04-15。*"""

NOTES_1071 = """## Lighthouse 2D Beam Propagation (Pinterest 2025-11)

### 核心洞察：状态 = (格子, 方向)
光束在同一 `(r, c, dr, dc)` 会产生完全相同的未来轨迹。visited 集合必须以四元组为 key，不是 `(r, c)`——否则镜子互反（如两面 `/\\` 相对）会死循环。终止由状态有限（最多 `4·R·C` 个）保证。

照亮格子数 = `len({(r, c) for (r, c, _, _) in visited})`。

### 镜面变换公式（考前背诵）

| 格子 | 变换 | 推导 |
|------|------|------|
| `/`  | `(dr, dc) → (-dc, -dr)` | `/` 是反对角，交换并取反 |
| `\\` | `(dr, dc) → ( dc,  dr)` | `\\` 是主对角，直接交换 |

分束器只在**垂直于自身方向**入射时分光：`|` 分上下（当 `dr == 0`），`-` 分左右（当 `dc == 0`）；其余情况按 `.` 处理。这是最容易写反的地方。

### Code

```python
from collections import deque

def energized(grid, start):
    \"\"\"start = (r0, c0, dr, dc); 返回照亮的不同格子数。\"\"\"
    R, C = len(grid), len(grid[0])
    visited = set()
    q = deque([start])

    while q:
        r, c, dr, dc = q.popleft()
        if not (0 <= r < R and 0 <= c < C):
            continue
        if (r, c, dr, dc) in visited:
            continue
        visited.add((r, c, dr, dc))
        ch = grid[r][c]

        if ch == '.':
            nxts = [(dr, dc)]
        elif ch == '/':
            nxts = [(-dc, -dr)]
        elif ch == '\\\\':
            nxts = [(dc, dr)]
        elif ch == '|':
            nxts = [(-1, 0), (1, 0)] if dr == 0 else [(dr, dc)]
        elif ch == '-':
            nxts = [(0, -1), (0, 1)] if dc == 0 else [(dr, dc)]
        else:
            nxts = []  # 墙 / 未知字符:吸收

        for ndr, ndc in nxts:
            q.append((r + ndr, c + ndc, ndr, ndc))

    return len({(r, c) for (r, c, _, _) in visited})


def best_placement(grid):
    \"\"\"枚举所有边界入口方向,返回最大照亮数。\"\"\"
    R, C = len(grid), len(grid[0])
    best = 0
    for r in range(R):
        best = max(best, energized(grid, (r, 0, 0, 1)))
        best = max(best, energized(grid, (r, C - 1, 0, -1)))
    for c in range(C):
        best = max(best, energized(grid, (0, c, 1, 0)))
        best = max(best, energized(grid, (R - 1, c, -1, 0)))
    return best
```

### 复杂度
- 单束 `energized`：每个 `(r, c, dr, dc)` 至多入队一次，共 `4·R·C` 个状态，时空 `O(R·C)`。
- `best_placement` 暴力枚举：`O((R + C)·R·C)`，面试规模 `R, C ≤ 200` 内绰绰有余。

### 陷阱
1. **起点本身要算照亮**：把 `(r0, c0, dr, dc)` 直接入队，不要退一步再入。
2. **同一格子多方向经过要各进 visited 一次**，最后统计亮格时再去重到 `(r, c)`。
3. **分束器在起点立即分光**是自然行为（`ch == '|'` 检查先于入队邻居）。

### 追问

| 变体 | 对应写法 |
|------|---------|
| 多灯塔求并集 | 多个 source 跑 BFS 合并 visited |
| 最佳起点放哪 | `best_placement` 枚举边界 |
| 只问是否存在环 | 相同 visited 集合中重复 `(r,c,dr,dc)` 即有环 |
| "Lighthouse with radius R" | 改 BFS 为 step ≤ R 的扩散 |

### 45 秒口播
> "关键是状态必须是 (格子, 方向) 四元组，不是 (格子)——镜子互反会让光束绕圈，方向才是区分同一格不同未来的维度，4·R·C 个状态保证 BFS 终止。镜子 `/` 的变换是 (dr,dc)→(-dc,-dr)，反对角；`\\` 是 (dr,dc)→(dc,dr)，主对角。分束器只在垂直入射时分光。起点本身算照亮，出格直接丢弃。照亮格子数是 visited 去掉方向维度的 set 大小。时空 O(R·C)。"
"""

# ------------------------------------------------------------------ 1072 ---
DESC_1072 = """[Pinterest coding 2026-11] 给一个单词列表（常说已按字典序排好）和一组查询前缀，对每个前缀返回列表中**以该前缀开头的第一个单词的下标**；没有匹配返回 `-1`。

**例**：
```
words    = ['a', 'apple', 'appz', 'b']
prefixes = ['ap']
output   = [1]        # 'apple' 是第一个以 'ap' 开头的单词
```

**标准 follow-up**：
(a) 单词表固定、前缀查询大量：预处理 Trie，每次查询 `O(|prefix|)`。
(b) 单词未排序：用 Trie 或排序后记原下标。
(c) 返回所有匹配下标而非第一个：Trie 节点上挂下标列表。

*题面整理 2026-04-15。*"""

NOTES_1072 = """## Prefix-Match First-Word-Index (Pinterest 2025-11)

### 解法 1：Trie + `min_index`（推荐，通用）

把每个 word 插入 Trie，在**插入路径上的每个节点**都更新 `min_index = min(min_index, word_index)`。查询时按 prefix 字符逐步走到末尾节点，读取 `min_index` 即为答案；中途走不下去返回 `-1`。不依赖输入是否有序。预处理 `O(Σ|w|)`，单次查询 `O(|prefix|)`。

```python
class TrieNode:
    __slots__ = ("children", "min_index")
    def __init__(self):
        self.children = {}
        self.min_index = -1


class PrefixIndex:
    def __init__(self, words):
        self.root = TrieNode()
        for i, w in enumerate(words):
            node = self.root
            for ch in w:
                nxt = node.children.get(ch)
                if nxt is None:
                    nxt = TrieNode()
                    node.children[ch] = nxt
                node = nxt
                if node.min_index == -1 or i < node.min_index:
                    node.min_index = i

    def first_index(self, prefix):
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return -1
        return node.min_index


def solve(words, prefixes):
    idx = PrefixIndex(words)
    return [idx.first_index(p) for p in prefixes]
```

**`min_index` 更新时机最关键**：必须在走到的**每一层**都更新，不能只在终止节点更新；否则查询 "ap" 时读到的只是"以 'ap' 结尾"的最小下标，会漏掉 "apple / append" 这类更长词。

### 解法 2：`bisect_left`（仅当 words 有序）

若 `words` 按字典序排好，所有以 `prefix` 开头的词构成连续区间。`bisect_left(words, prefix)` 返回最左候选位置，再验证是否真以 prefix 开头（例 `words=['a','az','b']`，`prefix='ap'`：`bisect_left → 1` 指到 `'az'`，但不以 `'ap'` 开头，应返回 `-1`）。

```python
from bisect import bisect_left

def solve_sorted(words, prefixes):
    out = []
    for p in prefixes:
        i = bisect_left(words, p)
        out.append(i if i < len(words) and words[i].startswith(p) else -1)
    return out
```

### 复杂度对比

| 方案 | Build | Query | Space | 需要有序? |
|------|-------|-------|-------|----------|
| Trie | `O(Σ\\|w\\|)` | `O(\\|prefix\\|)` | `O(Σ\\|w\\|)` | 否 |
| Bisect | `O(N log N)`（若需排序）| `O(\\|prefix\\| + log N)` | `O(1)` | 是 |

**面试策略**：先给 Trie（通用稳健），再提"如果词表已有序，可以零预处理用 `bisect_left`，单次 `O(log N + |prefix|)`"。

### 边界
1. **空前缀**：任何字符串都以空串开头，返回 `0`。Trie 的 `root.min_index` 被所有词累积更新为 0；`bisect_left(words, '')` 也返回 0。
2. **前缀比所有词都长**：Trie 走偏返回 `-1`；bisect 候选不以 prefix 开头，验证失败返回 `-1`。
3. **重复词**：Trie 天然取 min；`bisect_left` 返回最左出现位置。

### 追问
- **返回所有匹配下标**：Trie 节点挂 `list[int]`；或 `bisect_left` + `bisect_right` 取区间。
- **流式新增**：Trie 直接插入并更新 `min_index`；bisect 需要维护有序结构（`SortedList` / 平衡树）。

### 45 秒口播
> "两种方案：Trie 是通用解——每个 word 逐字符插入，**每经过一个节点就更新该节点的 min_index**，查询时沿 prefix 走到末端读 min_index 即可。关键陷阱：min_index 要在每一层都更新，只在终止节点更新会漏掉更长的词。如果 words 已排序，可以零预处理用 bisect_left 找最左候选，再验证是否真以 prefix 开头。Trie 预处理 O(Σ|w|)、查询 O(|prefix|)；bisect 无预处理、查询 O(log N + |prefix|)。面试先 Trie 再提 bisect。"
"""

# ------------------------------------------------------------------ 1073 ---
DESC_1073 = """[Pinterest coding 2026-11] 实现 `my_round(s: str) -> int`，把字符串 `s` 表示的十进制数按**四舍五入到最近整数**返回，**不能调用 `float(s)`**。`float()` 对极长输入（如 400 位数字）会悄悄溢出成 `inf`，且二进制浮点带来的舍入偏差（例如 `float('2.675')` 实际是 `2.6749999...`，与十进制 half-up 不一致）必须避免。

**Half-up 规则**（负数向远离 0 方向舍入）：
```
'2.4'   -> 2
'2.5'   -> 3
'-2.5'  -> -3
'9.5'   -> 10          # 进位传播
'-.2'   -> 0           # 无整数部分
'2.'    -> 2           # 无小数部分
'  +3 ' -> 3           # 允许空白 + 显式正负号
```

**非法输入**（`""`, `"."`, `"1.2.3"`, `"abc"`）→ `ValueError`。

**Follow-up (T-P1-403)**：推广到"保留 p 位小数"的精度舍入（见 1074），复用同一套解析 + 进位机制，只是把进位起点从个位换到第 p 位。

*题面整理 2026-04-15。*"""

NOTES_1073 = """## round() from scratch (Pinterest 2025-11)

### 为什么不能用 `float()`
1. **溢出**：`float("1" + "0"*400)` → `inf`。字符串解析保持任意精度（Python int 是大整数）。
2. **二进制伪像**：`float("2.675")` 实际是 `2.6749999...`，原生 `round` 会给 `2.67` 而非 `2.68`。十进制字符串处理绕过这个问题。
3. **面试意图**：考察**解析 + 进位链**的手感，不是库函数调用。

### 状态机四段解析
`s` 结构：`[空白][符号][整数位].[小数位][空白]`。任何其它字符 → `ValueError`。整数位和小数位**各自可空，但不能同时为空**（`"."` 非法；`"2."` 和 `".2"` 合法）。

### 半进位判定只看 `frac[0]`
个位的四舍五入只看第一个小数位，后续位不影响决策。进位链从最低位往前传；若传到最高位还有进位，在最前面插入一个 `"1"`（对应 `99 → 100`）。

### Code

```python
def my_round(s: str) -> int:
    s = s.strip()
    if not s:
        raise ValueError("empty string")

    i, n = 0, len(s)
    neg = False
    if s[i] in "+-":
        neg = s[i] == "-"
        i += 1

    int_part = ""
    while i < n and s[i].isdigit():
        int_part += s[i]
        i += 1

    frac_part = ""
    if i < n and s[i] == ".":
        i += 1
        while i < n and s[i].isdigit():
            frac_part += s[i]
            i += 1

    if i != n:
        raise ValueError(f"unexpected char at {i}: {s!r}")
    if not int_part and not frac_part:
        raise ValueError(f"no digits in {s!r}")
    if not int_part:
        int_part = "0"

    round_up = len(frac_part) > 0 and frac_part[0] >= "5"
    digits = list(int_part)
    if round_up:
        j = len(digits) - 1
        carry = 1
        while j >= 0 and carry:
            d = int(digits[j]) + carry
            if d == 10:
                digits[j] = "0"
                carry = 1
            else:
                digits[j] = str(d)
                carry = 0
            j -= 1
        if carry:
            digits.insert(0, "1")

    mag = int("".join(digits))
    return -mag if (neg and mag != 0) else mag
```

### 复杂度
`O(|s|)` 时间，`O(|s|)` 空间。

### 边界 matrix

| 输入 | 输出 | 说明 |
|------|------|------|
| `"2.5"` | `3` | half-up |
| `"-2.5"` | `-3` | half away from zero（符号最后施加） |
| `"9.5"` | `10` | 进位传播 |
| `"99.5"` | `100` | 进位扩到新最高位 |
| `"-.5"` | `-1` | 空整数补 `"0"` 后再走常规流程 |
| `"2."` | `2` | 空小数部分直接截断 |
| `" +3 "` | `3` | trim 空白，接受 `+` |
| `""` / `"."` / `"1.2.3"` / `"1e2"` | raise | 非法 |

**符号最后施加**：永远先算幅值再加符号，避免 `-0` 和负数进位的两套写法。

### 陷阱
- `"-.5"` 容易误返回 `0`：整数部分为空时不能早退，要先补 `"0"`。
- 进位链处理要有"传到顶还要进一位"的兜底（`digits.insert(0, "1")`）。
- 避免返回 `-0`：`neg and mag != 0` 条件判断。

### 追问
- **任意精度 p**（见 1074）：进位起点从 ones 改为 `frac[p-1]` 所在位，其余逻辑不变。
- **科学计数法** `"1.5e2"`：多加一段指数解析，把小数点左右移 e 位。
- **流式输入**：逐字符状态机，空间 `O(1)` 附加。

### 45 秒口播
> "不能用 float：长输入会溢出成 inf，二进制浮点对 2.675 这种半进位会给错方向。解法是**状态机解析**四段——空白、符号、整数位、小数位——任何非法字符抛错。半进位判定只看小数第一位；第一位 ≥ 5 就从最低位开始进位链，传到顶还有进位就在最前面插一个 1。符号最后施加，避免 `-0`。整数和小数各自可空但不能同空，`-.5` 这种要把空整数补 0 再走常规。O(|s|) 时间空间。推广到 1074 的任意精度 p 时，只需把进位起点从个位换到第 p 位。"
"""

# ------------------------------------------------------------------ 1074 ---
DESC_1074 = """[Pinterest coding 2026-11, T-P1-402 的 follow-up] 实现 `round_by_precision(s: str, p: str) -> str`，把字符串 `s` 表示的十进制数**四舍五入到 `p` 的最近倍数**。`p` 以字符串形式给出、保证是 10 的整数幂（如 `'100'`, `'10'`, `'1'`, `'0.1'`, `'0.01'`）。返回同样是字符串。**不能用 `float()`**（溢出 + 二进制伪像两个坑）。

**例**：
```
s='12567',    p='100'  -> '12600'
s='1234.678', p='0.1'  -> '1234.7'
s='1234.678', p='0.01' -> '1234.68'
s='99.5',     p='1'    -> '100'
s='-0.05',    p='0.1'  -> '-0.1'   # half away from zero
s='49',       p='100'  -> '0'
s='50',       p='100'  -> '100'
```

Half-up 规则（远离 0）。进位传播可能跨越小数点（例 `'9.99'` at `p='0.1'` → `'10.0'`）。

*题面整理 2026-04-15。*"""

NOTES_1074 = """## Round by Precision p (Pinterest 2025-11 follow-up)

### 核心观察：`p = 10^k`
`p` 保证是 10 的整数幂，找到 `p` 中 `'1'` 相对小数点的偏移就得到 `k`：
- `p='100'` → `k=2`（舍到百位）
- `p='1'`   → `k=0`（舍到整数，即 1073 的特例）
- `p='0.1'` → `k=-1`（保留 1 位小数）
- `p='0.01'`→ `k=-2`（保留 2 位小数）

### 算法步骤
1. **解析** `s` 为 `(sign, int_digits, frac_digits)`，同 1073 的状态机。
2. **解析** `p` 得到 `k`。
3. **定位舍入位**：把所有数字拼成一条，令 `dot_pos` 为首个小数位的下标，则第一个被丢弃的位置 `cut = dot_pos - k`。
4. **半进位判定**：`digits[cut] >= '5'` → 对 `digits[:cut]` 最低位加 1；否则截断。
5. **进位传播**：从 `cut - 1` 向高位循环 `+1`，处理 `10` 进位；可能需要在最前面插入新的 `"1"`（如 `9.99` at `p=0.1` → `10.0`）。
6. **重组**：按 `k` 切回整数/小数部分；清理前导零（保留单个 `'0'`）；负零归正；拼回符号。

### 关键边界

| 输入 | 说明 |
|------|------|
| `s='49', p='100'` | 低于半进位阈值 → `'0'` |
| `s='50', p='100'` | 恰好半进位 → `'100'` |
| `s='-0.05', p='0.1'` | 远离零 → `'-0.1'` |
| `s='9.99', p='0.1'` | 进位跨越小数点 → `'10.0'` |
| `s='0.005', p='0.01'` | 末位半进位 → `'0.01'` |

**结果必须保留 `p` 暗示的尾零**（`1234.7` 而不是 `1234.700`，但 `'100'` 而非 `'1e2'`）。

### 面试模板

```python
def round_by_precision(s: str, p: str) -> str:
    sign, int_digs, frac_digs = _parse_decimal(s)      # 非法输入抛 ValueError
    k = _precision_exponent(p)                          # p = 10**k
    digits = list(int_digs or '0') + list(frac_digs)
    dot_pos = len(int_digs or '0')                      # digits[dot_pos] 是首个小数位
    cut = dot_pos - k                                   # 首个被丢弃的位
    if cut <= 0:
        return _format_zero(sign, k)
    round_up = cut < len(digits) and digits[cut] >= '5'
    kept = digits[:cut]
    if round_up:
        kept = _increment(kept)                         # 可能在最前面多出 '1'
    return _reassemble(sign, kept, k)
```

辅助函数 `_parse_decimal` / `_precision_exponent` / `_increment` / `_reassemble` 在白板上分别实现即可；核心思想是"**把十进制数当成数字串做定点运算**"。

### 与 1073 的关系
1073 是本题 `p='1'` (`k=0`) 的特例。先掌握 1073 的状态机 + 进位链，本题只需要再加一层"按 `k` 定位 `cut`"的索引计算。面试时主动澄清 tie-break 语义：half-away-from-zero 还是 banker's rounding。

### 复杂度
`O(n)` 时间空间，`n = len(s)`。

### 45 秒口播
> "`p` 是 10 的整数幂，找 `p` 里 `'1'` 相对小数点的偏移就得到 `k`。先按 1073 的状态机解析 `s`，得到整数位和小数位；把两段拼成一条数字串，记 `dot_pos` 为首个小数位下标，第一个被丢弃的位就是 `cut = dot_pos - k`。半进位只看 `digits[cut]` 是否 ≥ 5；要进位就从 `cut - 1` 向前传，传到顶还有进位就在最前面插 `'1'`。最后按 `k` 切回整数/小数、清前导零、处理负零、加回符号。1073 是 `k=0` 的特例；1074 只多一层按 `k` 定位 `cut` 的索引计算。O(n) 时间空间。"
"""

# ------------------------------------------------------------------ 1075 ---
DESC_1075 = """[Pinterest coding 2026-11] 某公司把资源（文件夹、文档、项目）组织为一个**有向无环图 (DAG)**，边 `parent → child` 代表 child 被 parent 包含 / 继承自 parent。管理员可以把某用户的权限授予单个节点；该授权**自动继承到该节点的所有后代**。

设计 `PermissionSystem`：
- `addEdge(parent, child)` — 搭建 DAG（保证无环）。
- `grant(user, node)` — 给用户在 `node` 上授权（自动对所有后代生效）。
- `hasAccess(user, node)` — 当且仅当用户在 `node` **自身或任一祖先**上有授权时返回 `True`。

**讨论过的 follow-up**：
(a) `revoke(user, node)` 如何与冲突授权交互。
(b) 多继承：一个节点可能有多个父亲（真 DAG，不是树）。
(c) 规模：百万级节点和授权、查询极度倾斜——何时缓存、何时预计算闭包。
(d) 组概念：`user → group → node` 形成两层 DAG。

*题面整理 2026-04-15。*"""

NOTES_1075 = """## Grant Access on DAG (Pinterest 2025-11)

### 推荐方案：查询时向上走（reverse BFS）

**存储**：
- `parents: node → set[node]` — 反向边，供 `has_access` 用
- `children: node → set[node]` — 正向边（本方案不必用，留作扩展）
- `grants: user → set[node]` — 只记显式授权，不预计算闭包

**`has_access(user, node)`**：从 `node` 沿 `parents` 反向 BFS，一旦撞上 `grants[user]` 里的节点就返回 `True`；走完祖先闭包仍无则 `False`。

```python
from collections import defaultdict, deque

class PermissionSystem:
    def __init__(self):
        self.children = defaultdict(set)
        self.parents  = defaultdict(set)
        self.grants   = defaultdict(set)

    def add_edge(self, parent, child):
        self.children[parent].add(child)
        self.parents[child].add(parent)

    def grant(self, user, node):
        self.grants[user].add(node)

    def has_access(self, user, node):
        g = self.grants.get(user)
        if not g:
            return False
        if node in g:
            return True
        seen = {node}
        q = deque([node])
        while q:
            cur = q.popleft()
            for p in self.parents.get(cur, ()):
                if p in g:
                    return True
                if p not in seen:
                    seen.add(p)
                    q.append(p)
        return False
```

`has_access` 复杂度 `O(A)`（A = node 的祖先闭包大小）；`grant` / `add_edge` 均 `O(1)`。

**为什么反向走更合适**：单次授权影响的**后代**可能极多，而单次查询对应的**祖先**通常较少（DAG 深度 ≪ 节点数）。此外"近祖先优先"的 ACL 语义（见 revoke 追问）天然契合反向走。

### 备选 1：授权时下传（预计算闭包）
在 `grant(user, node)` 时 BFS 下传，把所有后代写入 `access[user]`。查询 `O(1)`。优点：查询极快；缺点：单次授权写放大大，撤销时因为祖先可能还有合法授权，直接删集合会误杀。**只适合授权极稀少 + 查询极多**的场景。

### 备选 2：反向走 + memo
对 `has_access(user, node)` 做记忆化，遇到 `grant(user, *)` 就把该 user 的缓存全清。稳态下"授权少查询多"时接近 `O(1)`。

### 追问

**(a) revoke**：从 `grants` 集合里直接删节点**错误**——别处的授权可能仍通过其它祖先生效。两种干净建模：
1. **显式 deny 集合** `denies: user → set[node]`。反向 BFS 时谁先命中谁胜出（近祖先优先）；同节点上通常 deny 胜。UNIX / AD 的 closest-ancestor ACL 就是这套。
2. **有效访问重算**：revoke 时重新从 `grants` + `denies` 推一遍。语义更直观，revoke 更重。

面试要先问清楚语义，默认一种大概率会被追问 trade-off。

**(b) 真 DAG（多父）**：`parents[c]` 已是 `set`，配合 `seen` 天然支持多父。需口头确认语义是"任一路径存在被授权祖先即有权"（通常是）。"全部路径都要被授权"是另一类问题（反向多源可达性）。

**(c) 规模 trade-off**：

| 模式 | 最佳策略 |
|------|---------|
| 授权少、查询多 | Memo 反向走 / 预计算闭包 |
| 授权多、查询少 | 反向走，不预处理 |
| 两者都多 | 反向走 + LRU，按 user 粒度失效 |
| 读多 + 深度有界 | 预计算闭包 + 版本化快照 |

**(d) 组授权**：加 `group_members: group → set[user]`，允许 `grant(group, node)`。`has_access(user, node)` 变为：user 被直接授权，或**包含 user 的任一 group** 在 `node` 或其祖先被授权。等价于从 `node` 向上走 + 从 user 向旁经 group 扩展，两个闭包都小，BFS 惰性 union 即可。

### 陷阱
1. `node` 自身被授权 → `node in g` 短路返回 `True`。
2. 未见过的节点 → `parents.get(cur, ())` 空集合，安全返回 `False`。
3. 同祖先链多次授权 → set 天然幂等。

### 面试交付节奏
1. 画 DAG，讲清"授权在 node，所有后代继承"；
2. 澄清 follow-up：有组吗？支持 revoke 吗？树还是 DAG？
3. 给反向 BFS + 复杂度分析；
4. 对比"查询时走" vs "授权时下传"的 trade-off；
5. 写撤销：引入 deny、近祖先优先；
6. 规模讨论 + 缓存策略收尾。

### 45 秒口播
> "推荐查询时从 node 向上反向 BFS 找祖先里有没有被授权。存 parents 反向边和 grants: user→set[node]。理由：授权影响的后代往往极多，但查询对应的祖先闭包一般很小（DAG 深度远小于节点数）；而且近祖先优先的 ACL 语义天然契合反向走。复杂度 has_access O(祖先闭包大小)，grant 和 add_edge O(1)。备选是授权时下传预计算闭包，查询 O(1) 但 revoke 会误杀，只适合授权稀少。revoke 干净做法是加 deny 集合、近祖先胜。真 DAG 多父由 parents 的 set + seen 天然支持。规模上授权少查询多时加 memo；组授权加一层 group_members，BFS 同时走祖先链和 user→group 扩展。"
"""

# ------------------------------------------------------------------ 1076 ---
DESC_1076 = """[Pinterest coding 2026-11] Pinterest 后端存一张异构无向关系图，节点包括 pin、board、user。两节点间有边表示直接关系，例如：
- pin P 被保存到 board B         (pin-board 边)
- user U 关注 board B            (user-board 边)
- board B1 由 board B2 克隆      (board-board 边)

设计 `ConnectivityService`：
- `addEdge(a, b)` — 记录一条新关系边（无向）。
- `areConnected(a, b)` — 当且仅当 `a` 和 `b` 在关系图的**同一连通分量**中返回 `True`。

**讨论过的 follow-up**：
(a) `componentSize(x)` 与 `countComponents()` 摊还 `O(1)`。
(b) 允许删边：语义如何变（Union-Find 单独不够用了）。
(c) `a` 到 `b` 的**最短跳数**，不仅是连通性。
(d) 规模：数十亿条边流式进入；分片 worker；最终一致性。

*题面整理 2026-04-15。*"""

NOTES_1076 = """## Pin Connectivity (Pinterest 2025-11)

### 推荐方案：Union-Find (DSU)

**数据**：
- `parent: dict[node, node]` — DSU 森林的父指针
- `rank:   dict[node, int]`  — 树高上界（按秩合并用）
- `size:   dict[node, int]`  — 以该节点为根时的分量大小（`component_size` 用）
- `_components: int` — 当前连通分量数（`count_components` 用）

**find(x)**：沿 `parent` 爬到根，回程**路径压缩**（经过的节点全部重指到根）。
**union(a, b)**：按秩合并（矮树挂高树下）；同步累加 `size`、减少 `_components`。
**are_connected(a, b)**：`find(a) == find(b)`。

```python
class ConnectivityService:
    def __init__(self):
        self.parent = {}
        self.rank   = {}
        self.size   = {}
        self._components = 0

    def _ensure(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x]   = 0
            self.size[x]   = 1
            self._components += 1

    def find(self, x):
        self._ensure(x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def add_edge(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra]  += self.size[rb]
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self._components -= 1

    def are_connected(self, a, b):
        return self.find(a) == self.find(b)

    def component_size(self, x):
        return self.size[self.find(x)]

    def count_components(self):
        return self._components
```

复杂度：`add_edge` / `are_connected` 均摊接近 `O(α(N))`（反 Ackermann，近似常数）；空间 `O(N)`。

### 为什么不直接用邻接表 + BFS/DFS
- BFS/DFS 每次查询 `O(V+E)`，查询一多就顶不住。
- 除非题目**明确要求支持删边**或**要返回最短路径**，否则首选 DSU。

### 实现要点
1. `find` 必须路径压缩，否则退化成链表 `O(N)`。
2. `union` 按秩（或按大小）合并，否则单独路径压缩达不到 α 复杂度。
3. `size[root]` 与全局 `_components` 同步更新，`component_size` / `count_components` 都 `O(1)`。

### 追问

**(a) componentSize / countComponents**：上面已覆盖，`size` 挂根，`_components` 每次成功 union 减 1。

**(b) 边删除**：DSU **不支持**高效 un-merge。方案：
1. **离线技巧**（Link-Cut Tree / 欧拉序）：若能看到完整 edge 流，把查询反向、删除变插入。仅适合离线/批处理。
2. **在线动态连通性**（Holm / Lichtenberg / Thorup）：支持 insert + delete + query，摊还 `O(log^2 N)`。实现复杂，面试只需提存在、不要白板写。
3. **回退邻接表 + BFS**：规模小时最简单。

先澄清**是否需要删除**再选方案。

**(c) 最短跳数**：DSU 不提供距离。需要就走 BFS；静态图重复查询可预计算多源 BFS 树或双向 BFS。Pinterest 规模下精确全对距离不可行，工程上用随机游走 / 图嵌入（PinSage）做近似。

**(d) 规模**：
- 按 `hash(node)` 分 shard，每 worker 一份本地 DSU。
- 跨 shard union 走两阶段协调：双方本地 `find`，再由 leader 合并；用**全局 component UUID** 保证任一 shard 的 `find` 返回同一 id。
- **最终一致性**：边可能乱序到达，union 可结合可交换，乱序不影响最终分区。
- **读多写少**：把分区快照成 `node → component_id` 扁平 map，push 到 KV 缓存，查询变缓存 `O(1)`。

### 陷阱
1. 自环 `add_edge(a, a)` — 必须 no-op；DSU 通过 `ra == rb` 早退。
2. 查询未见过节点 — `_ensure` 创建单点分量；`are_connected(x, x) == True`。
3. 重复边 — 第二次调用 no-op。
4. 异构节点类型（`pin 123` vs `board 123`）— 用 tagged key `("pin", 123)` 避免 id 撞车。

### 面试交付节奏
1. 画两三条边的样例讲清"连通"语义；
2. 澄清：删边吗？要距离吗？要 `componentSize` 吗？
3. 给 DSU，写代码，讲路径压缩 + 按秩；
4. 讨论邻接表 + BFS 的适用场景 + 删边追问；
5. 聊分片 DSU + KV 缓存；
6. 收尾：对比 PinSage / 随机游走（Pinterest 上下文加分）。

### 45 秒口播
> "连通性查询首选 Union-Find：parent 指针 + 按秩合并 + 路径压缩，均摊 α(N) ≈ O(1)。顺便维护 size 挂根和全局 _components，component_size 和 count_components 都是 O(1)。自环和重复边用 ra==rb 早退 no-op。异构节点用 tagged key 避免 id 撞车。若题目要求删边，DSU 不够用——离线可以反向处理把删变插，在线要 Holm 等动态连通算法（O(log²N)，面试只提不写）；规模小直接退到邻接表 + BFS。最短距离走 BFS。Pinterest 规模下用 hash(node) 分 shard，跨 shard 合并走全局 component UUID；读多写少时把 node→component_id 推到 KV 缓存。"
"""

# -----------------------------------------------------------------------------

UPDATES = [
    (1068, DESC_1068, NOTES_1068),
    (1071, DESC_1071, NOTES_1071),
    (1072, DESC_1072, NOTES_1072),
    (1073, DESC_1073, NOTES_1073),
    (1074, DESC_1074, NOTES_1074),
    (1075, DESC_1075, NOTES_1075),
    (1076, DESC_1076, NOTES_1076),
]

def main():
    conn = sqlite3.connect(DB)
    for pid, desc, notes in UPDATES:
        n = conn.execute(
            "UPDATE problems SET description = ?, notes = ? WHERE id = ?",
            (desc, notes, pid),
        ).rowcount
        print(f"Problem {pid}: updated {n} row(s), desc={len(desc)}B notes={len(notes)}B")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
