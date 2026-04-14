"""Append a 'Code Review of Your Solution' section to LC 410 notes, analyzing
the user's curBox-based variant submitted via Discord 2026-04-13."""
import sqlite3

APPENDIX = r'''

---

### Code Review: 你的 `curBox` 写法

```python
def verify(upperbound):
    curBox = upperbound
    usedCnt = 0
    for v in nums:
        if v > upperbound:
            return False
        if v > curBox:
            curBox = upperbound
            usedCnt += 1
        curBox -= v
    if curBox < upperbound:
        usedCnt += 1
    return usedCnt <= k
```

**核心结论**：**逻辑正确**，跑得过 LC。但有 4 处可以改进。

#### 1. `if v > upperbound: return False` 是冗余的

你的二分初值 `beg = max(nums)`，循环不变式保证 `mid >= max(nums) >= v`，这个判断永远不会触发。删掉让意图更清晰。

（留着也可以作为 defensive check，但习惯上我们靠 `lo = max(nums)` 的 invariant 而不是运行时判断。）

#### 2. `usedCnt` 的计数逻辑不标准

你的做法：usedCnt 从 0 开始；每开一个**新**（第二个及以后的）box 才 +1；最后再看 `curBox < upperbound` 决定是否额外 +1。等价于"先假设没开任何 box，之后算总消耗"。

canonical 的写法直接 `segs = 1` 起步（已经默认开一个），遇到装不下就 +1。Trace 上更直观：

```python
segs, cur = 1, 0
for x in nums:
    if cur + x > cap:
        segs += 1
        cur = x
    else:
        cur += x
return segs <= k
```

读者一眼就能对上 "共用了 segs 段" 的语义，不需要去证明最后那个 `if curBox < upperbound` 的等价性。

#### 3. 没有提前终止

当 `usedCnt` 已经 > k 时，后面的遍历是浪费。canonical 版每次开新段就检查 `if segs > k: return False`，n=1000 * 30 轮二分下省下 O(n·log S) 级别的无效工作。

#### 4. 二分出口后的冗余语句

```python
while beg < end:
    ...
mid = beg + (end - beg) // 2
return mid
```

循环退出时 `beg == end`，最后一行再算 `mid = ...` 完全多余，直接 `return beg`（或 `end`，都行）。一行比三行安全，更能传达 "loop invariant 保证答案就是 lo" 的意图。

#### 5. 全零 corner case 的语义漏洞（正确性 OK 但值得知道）

`nums = [0, 0, 0], k = 1`:
- `beg = max(nums) = 0`, `end = sum(nums) = 0` → 循环不进入 → `return 0` [Y]

`nums = [0, 0, 0, 5, 0], k = 3`:
- `beg = 5, end = 5` → `return 5` [Y]

但你的 `verify` 在 `cap = 0`, `nums = [0, 0, 0]` 时：
- 每轮 `v=0`，`v > curBox` 是 `0 > 0` = False → 不开新段
- 循环后 `curBox == upperbound`（都是 0）→ 不 +1
- 返回 `0 <= k` = True（正确！）

但语义上说 "我用了 0 个段装完了"，实际上数组总得占**至少 1 段**。这里只是因为 `0 <= k` 恒成立所以 AC；canonical 版的 `segs = 1` 起步会返回 `1 <= k` 也 AC，但更符合直觉。

#### 改进后的完整版

```python
class Solution:
    def splitArray(self, nums: List[int], k: int) -> int:
        def feasible(cap: int) -> bool:
            segs, cur = 1, 0
            for x in nums:
                if cur + x > cap:
                    segs += 1
                    if segs > k:
                        return False
                    cur = x
                else:
                    cur += x
            return True

        lo, hi = max(nums), sum(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if feasible(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
```

差异对比表：

| 项 | 你的 | 改进 |
|----|------|------|
| `v > upperbound` 兜底 | 有（死代码）| 删 |
| 计数初值 | `usedCnt = 0` + 末尾补 | `segs = 1` 起 |
| 提前终止 | 无 | `segs > k` 即退 |
| 循环后 | `mid = ...; return mid` | `return lo` |
| 变量名 | `curBox / upperbound` | `cur / cap`（更短更通用）|

**面试建议**：你的版本能 AC，但 code review 时面试官会指出上述 4 点。先用 canonical 模板（更容易被"秒认"），代码写完后主动提 trade-off 说明你知道还有其他等价写法。
'''

conn = sqlite3.connect("data/mle_prep.db")
row = conn.execute("SELECT notes FROM problems WHERE leetcode_id = 410").fetchone()
new_notes = row[0] + APPENDIX
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 410", (new_notes,))
conn.commit()
print(f"[OK] LC 410 notes extended: {len(row[0])} -> {len(new_notes)} chars")
conn.close()
