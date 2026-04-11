"""One-off v2: rewrite LC 1055 note with cleaned greedy+bisect code and a full DP alternative."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTE = """## Shortest Way to Form String

### 思路
贪心 + 二分查找。核心观察：要用 source 的子序列拼出 target，就尽量在一次子序列里"吃掉"target 中尽可能多的字符，吃不下了再开新的一份 source。

具体做法：
1. **预处理**：对 source 中的每个字符，记录它出现的所有下标（有序），存成 `preprocessDict[c] = [i1, i2, ...]`。
2. **无解判定**：如果 target 中存在任何字符不在 source 的字符集里，直接返回 -1。
3. **贪心扫描**：维护 source 中的当前指针 curPos。对 target 中的每个字符 c，二分查找 `preprocessDict[c]` 中 ≥ curPos 的第一个位置 nextPos：
   - 找得到：curPos = nextPos + 1，继续下一个字符。
   - 找不到：说明当前这一份 source 子序列已经用完了，需要开新的一份。ans += 1，curPos 重置为 0，再重新二分一次（这次一定能找到，因为字符存在于 source 中）。
4. 最终答案是 `ans + 1`：ans 统计的是"开了多少次新子序列"（wrap 次数），而最初在进行中的那一份还没计入，所以 +1。

### 关键技巧
- 预处理每个字符的位置列表 + 二分查找，将"在 source[curPos:] 中找下一个 c"的复杂度从 O(n) 降到 O(log n)。
- 用 `collections.defaultdict(list)` + `bisect.bisect_left` 替代手写字典初始化和手写二分，代码更干净、更不容易写错。
- 用 `set(target) - set(source)` 一次性做无解判定，避免每个字符都在循环里检查。
- 用"找不到就 wrap、ans += 1、curPos 归零"的模式替代显式的两层循环。

### 核心代码
```python
import bisect
from collections import defaultdict


class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        # 无解早返回：target 中只要有一个字符不在 source 里就直接 -1
        if set(target) - set(source):
            return -1

        # 预处理：每个字符在 source 中的所有位置（有序）
        preprocessDict: dict[str, list[int]] = defaultdict(list)
        for i, ch in enumerate(source):
            preprocessDict[ch].append(i)

        def _findNext(char: str, pos: int) -> int:
            # lower_bound: source 中 >= pos 的第一个 char 位置，找不到返回 -1
            indexList = preprocessDict[char]
            idx = bisect.bisect_left(indexList, pos)
            return indexList[idx] if idx < len(indexList) else -1

        ans = 0  # 已经"用完"的 source 子序列份数（wrap 次数）
        curPos = 0
        for c in target:
            nextPos = _findNext(c, curPos)
            if nextPos == -1:
                # 当前这一份 source 已经走到头了，开新的一份
                ans += 1
                curPos = 0
                nextPos = _findNext(c, 0)  # 既然 c 在 source 中，这次一定找得到
            curPos = nextPos + 1

        # ans 统计的是 wrap 次数；循环结束时还有一份"进行中"的子序列未计入，所以 +1
        return ans + 1
```

### 注意点
- `bisect.bisect_left` 返回的就是标准 lower_bound 下标（>= pos 的第一个位置）。越界时返回 len(indexList)，所以要判断 idx < len(indexList)。
- 返回 `ans + 1` 而不是 `ans`：循环体内只有在"当前子序列用完、需要开新的"才 ans += 1，循环结束时最后一份仍未计入。
- `set(target) - set(source)` 的判定要放在循环之前，否则主循环里仍需处理 `preprocessDict[c]` 为空的情况。
- 字符完全不在 source 中时要提前返回 -1，避免在空列表上二分。

### 清理说明（相比原始版本）
- 删除了未使用的 `nSource`、`nTarget` 局部变量。
- `_findNext` 的原版在 `while beg < end` 结束后又算了一次 `mid = beg + (end - beg) // 2`（此时 beg == end，相当于 mid = beg），属于死代码。简化为直接返回 `indexList[beg]`；更进一步直接用 `bisect.bisect_left`。
- 用 `collections.defaultdict(list)` 替代"先建空列表再 append"的两次遍历，只扫一次 source。
- 用 `set(target) - set(source)` 一次性完成无解判定，取代循环内的 per-char 空列表检查。
- 在 `ans + 1` 处加注释解释 ans 的语义（wrap 次数）以及 +1 的来源。

### 复杂度
- 预处理：O(|source| + |target|)
- 主循环：对 target 每个字符做一次 O(log |source|) 的二分，共 O(|target| · log |source|)
- 总时间：O((|source| + |target|) + |target| · log |source|)
- 空间：O(|source|)（preprocessDict 存储 source 中每个字符的位置列表）

### 另一种思路：DP 预处理 next 表
换成"预处理每个位置 + 每个字符的下一次出现位置"的 DP 表：`nxt[i][c]` 表示 source 中从位置 i 开始（含 i）字符 c 下一次出现的下标，不存在则 -1。这样主循环里每次查询就是 O(1)，不再需要二分。

**状态定义**
- `nxt` 是一张 (n+1) × 26 的表，n = len(source)。
- `nxt[n][c] = -1` 对所有字符（边界：source 之外当然找不到任何字符）。
- 逆序填表：`nxt[i][c] = i if source[i] == c else nxt[i+1][c]`。

**主循环**
和贪心版几乎一样，只是把 `_findNext(c, curPos)` 换成 `nxt[curPos][c]`：
- 若 `nxt[curPos][c] == -1`：wrap（ans += 1，curPos = 0），再查一次 `nxt[0][c]`。
- 否则 curPos = `nxt[curPos][c] + 1`。
- 无解判定：`nxt[0][c] == -1` 说明 source 中根本没有字符 c，返回 -1。

```python
class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        n = len(source)
        A = ord('a')

        # nxt[i][c] = source 中从位置 i 开始（含 i）字符 c 下一次出现的下标；-1 表示不存在
        nxt = [[-1] * 26 for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            # 先继承 i+1 行
            for c in range(26):
                nxt[i][c] = nxt[i + 1][c]
            # 再用当前字符覆盖
            nxt[i][ord(source[i]) - A] = i

        # 无解早返回：target 中存在 source 里没有的字符
        for ch in set(target):
            if nxt[0][ord(ch) - A] == -1:
                return -1

        ans = 0  # wrap 次数
        curPos = 0
        for ch in target:
            c = ord(ch) - A
            if curPos == n or nxt[curPos][c] == -1:
                # 当前这一份 source 走到头了，开新的一份
                ans += 1
                curPos = 0
            # 此时一定找得到（已经做过全局无解判定）
            curPos = nxt[curPos][c] + 1

        # ans 是 wrap 次数，最后一份进行中的子序列还要 +1
        return ans + 1
```

**复杂度**
- 预处理：O(26 · n)
- 主循环：O(|target|)
- 总时间：O(26 · |source| + |target|)
- 空间：O(26 · |source|)

**什么时候选 DP 版本？**
- target 远长于 source 且字符集小（26）时，DP 版本比贪心+二分更快：每次查询 O(1) vs O(log n)。
- 面试里两种都写得出来最好：贪心+二分体现对 lower_bound 的掌握，DP 体现对 next 表 / 后缀状态的思维。
- 如果字符集很大（比如 Unicode），DP 的 O(|Σ|·n) 空间就不划算了，这时贪心+二分更通用。
"""


def main() -> None:
    """Update LC 1055 notes column with the cleaned + DP version (idempotent)."""
    con = sqlite3.connect(str(DB_PATH))
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, notes FROM problems WHERE leetcode_id = 1055"
        )
        row = cur.fetchone()
        if row is None:
            raise SystemExit("LC 1055 not found")
        pid, existing_notes = row

        if existing_notes == NOTE:
            print(f"[SKIP] problem id={pid} (LC 1055) notes already up to date")
            return

        cur.execute(
            "UPDATE problems SET notes = ?, is_completed = 1 WHERE id = ?",
            (NOTE, pid),
        )
        con.commit()
        print(f"[DONE] Updated problem id={pid} (LC 1055)")
        print(f"  notes length: {len(NOTE)}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
