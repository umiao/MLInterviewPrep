"""One-off: add Pinterest company tag and solution note to LC 1055."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

NOTE = """## Shortest Way to Form String

### 思路
贪心 + 二分查找。核心观察：要用 source 的子序列拼出 target，就尽量在一次子序列里“吃掉”target 中尽可能多的字符，吃不下了再开新的一份 source。

具体做法：
1. **预处理**：对 target 中出现过的每个字符 c，记录它在 source 中所有出现位置，存成 `preprocessDict[c] = [i1, i2, ...]`（有序）。
2. **无解判定**：如果 target 中某个字符在 source 中完全不存在（`preprocessDict[c]` 为空列表），直接返回 -1。
3. **贪心扫描**：维护 source 中的当前指针 curPos。对 target 中的每个字符 c，二分查找 `preprocessDict[c]` 中 ≥ curPos 的第一个位置 nextPos：
   - 找得到：curPos = nextPos + 1，继续下一个字符。
   - 找不到（nextPos == -1）：说明当前这一份 source 子序列已经用完了，需要开新的一份。ans += 1，curPos 重置为 0，再重新二分一次（这次一定能找到，因为字符存在于 source 中）。
4. 最终答案是 `ans + 1`（循环结束时最后一份子序列还没算进去）。

### 关键技巧
- 预处理每个字符的位置列表 + 二分查找，将每次“在 source[curPos:] 中找下一个 c”的复杂度从 O(n) 降到 O(log n)。
- 只为 target 中出现过的字符建立位置列表，避免浪费空间。
- 用“找不到就开新子序列、ans += 1、curPos 归零”的模式替代显式的两层循环，代码更干净。

### 核心代码
```python
class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        ans = 0
        nSource = len(source)
        nTarget = len(target)
        preprocessDict = dict()
        for c in target:
            if c not in preprocessDict:
                preprocessDict[c] = []
        for i, char in enumerate(source):
            if char in preprocessDict:
                preprocessDict[char].append(i)
        def _findNext(char, pos):
            indexList = preprocessDict[char]
            beg, end = 0, len(indexList)
            while beg < end:
                mid = beg + (end - beg) // 2
                if indexList[mid] < pos:
                    beg = mid + 1
                else:
                    end = mid
            mid = beg + (end - beg) // 2
            return indexList[mid] if mid < len(indexList) else -1
        curPos = 0
        for c in target:
            if not preprocessDict[c]:
                return -1
            nextPos = _findNext(c, curPos)
            if nextPos == -1:
                ans += 1
                curPos = 0
                nextPos = _findNext(c, curPos)
            curPos = nextPos + 1
        return ans + 1
```

### 注意点
- `_findNext` 使用的是标准的 lower_bound 二分：找第一个 ≥ pos 的位置。注意最后重新赋值 `mid = beg + (end - beg) // 2` 其实等同于 `mid = beg`，返回 `indexList[beg]`（越界则 -1）。
- 返回 `ans + 1` 而不是 `ans`：循环体内只有在“当前子序列用完、需要开新的”才 ans += 1，循环结束时最后一份仍未计入。
- 无解判定要放在循环里每个字符都检查一次（或循环前对所有字符一次性判断），不能漏。
- 字符完全不在 source 中时要提前返回 -1，避免在空列表上二分。

### 复杂度
- 预处理：O(|source| + |target|)
- 主循环：对 target 每个字符做一次 O(log |source|) 的二分，共 O(|target| · log |source|)
- 总时间：O((|source| + |target|) + |target| · log |source|)
- 空间：O(|source|)（preprocessDict 存储 source 中字符的位置）

### 另一种思路（未实现）
也可以换成“预处理每个位置 + 每个字符的下一次出现位置”的 DP 表：`nextPos[i][c]` 表示 source 中从位置 i 开始，字符 c 下一次出现的下标（不存在则 -1）。这样查询时就是 O(1) 而不是 O(log n)。如果一开始在位置 0 就拿不到某个字符的下一次出现位置（即 `nextPos[0][c] == -1`），说明 source 中根本没有这个字符，直接返回 -1。整体时间复杂度 O(|source| · 字符集大小 + |target|)，空间 O(|source| · 字符集大小)。
"""


def main() -> None:
    con = sqlite3.connect(str(DB_PATH))
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, company_tags, notes FROM problems WHERE leetcode_id = 1055"
        )
        row = cur.fetchone()
        if row is None:
            raise SystemExit("LC 1055 not found")
        pid, company_tags_raw, existing_notes = row

        # Ensure Pinterest tag present (idempotent)
        tags = json.loads(company_tags_raw) if company_tags_raw else []
        if "Pinterest" not in tags:
            tags.append("Pinterest")
        new_tags = json.dumps(tags, ensure_ascii=False)

        cur.execute(
            "UPDATE problems "
            "SET company_tags = ?, notes = ?, is_completed = 1 "
            "WHERE id = ?",
            (new_tags, NOTE, pid),
        )
        con.commit()
        print(f"[DONE] Updated problem id={pid} (LC 1055)")
        print(f"  company_tags: {tags}")
        print(f"  notes length: {len(NOTE)}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
