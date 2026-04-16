"""Idempotent: mark LC 895 complete and attach Chinese solution notes.

LC 895 Maximum Frequency Stack -- 频次分组 + 组内栈序的 canonical 题。
属于 stateful_ds_design 家族，与 LC 716 Max Stack / LC 1429 First Unique Number
属于同一思路谱系（多结构组合维护 O(1) 查询）。

Run: python scripts/_update_lc895_notes.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
LC_ID = 895
PATTERN = "hash map + stack"
SENTINEL = "<!-- LC895_NOTES -->"

NOTES = """<!-- LC895_NOTES -->
## 题目定位
**stateful_ds_design 家族** -- FreqStack 是"频次分组 + 组内栈序"的 canonical 题。
- `push(val)`：入栈。
- `pop()`：弹出**当前频次最高**的元素；若多个并列最高，弹出**最近 push** 的那一个。
- 全部要求 $O(1)$。

考点不是数据结构本身，而是"如何用两层结构同时编码两种顺序：频次顺序（外层）+ 入栈顺序（内层）"。

## 核心洞察（必背）
**同一个 `val` 在所有 $\\le \\text{freq}(val)$ 的 group 里都保留一份副本**。
- 第一次 push(5)：freq[5]=1，groups[1].append(5)。
- 第二次 push(5)：freq[5]=2，groups[2].append(5)。**注意 groups[1] 里那个 5 没有删掉**。
- pop()：从 groups[max_freq] 弹出 5，freq[5] 回到 1。下一次 pop 如果 max_freq 仍是 2 就继续在 2 里弹，如果 2 空了 max_freq 减到 1，groups[1] 里还有 5（也还有别的元素），按入栈顺序继续弹。

**为什么 pop 时只在 max_freq 那一层弹、不去清理低层？**
因为低层的副本本来就代表"那个 val 在低频时期的存在"，未来 max_freq 降下来时它仍然是"低频期里入栈的元素之一"，按 LIFO 出栈本来就是正确语义。这套结构把"频次回退"自动映射成"回到上一层 stack"，无需任何 cross-layer 删除。这是这道题最巧的地方。

## Python 代码（面试可直接默写）
```python
from collections import defaultdict

class FreqStack:
    def __init__(self):
        self.freq = defaultdict(int)            # val -> current freq
        self.groups = defaultdict(list)         # freq -> stack of vals
        self.max_freq = 0

    def push(self, val: int) -> None:
        self.freq[val] += 1
        f = self.freq[val]
        if f > self.max_freq:
            self.max_freq = f
        self.groups[f].append(val)              # O(1)

    def pop(self) -> int:
        v = self.groups[self.max_freq].pop()    # O(1)
        self.freq[v] -= 1
        if not self.groups[self.max_freq]:
            self.max_freq -= 1
        return v
```

## 走查示例
push 序列：`5, 7, 5, 7, 4`，然后 pop 四次。

| 步骤 | freq | groups | max_freq |
| --- | --- | --- | --- |
| push 5 | {5:1} | {1:[5]} | 1 |
| push 7 | {5:1,7:1} | {1:[5,7]} | 1 |
| push 5 | {5:2,7:1} | {1:[5,7], 2:[5]} | 2 |
| push 7 | {5:2,7:2} | {1:[5,7], 2:[5,7]} | 2 |
| push 4 | {5:2,7:2,4:1} | {1:[5,7,4], 2:[5,7]} | 2 |
| pop -> 7 | {5:2,7:1,4:1} | {1:[5,7,4], 2:[5]} | 2 |
| pop -> 5 | {5:1,7:1,4:1} | {1:[5,7,4], 2:[]} | 1 |
| pop -> 4 | {5:1,7:1,4:0} | {1:[5,7]} | 1 |
| pop -> 7 | {5:1,7:0,4:0} | {1:[5]} | 1 |

输出序列 `7, 5, 4, 7` -- 注意第二次 pop 的 5 和 7 同为 freq=2，**按入栈先后**先弹 7 再弹 5；之后回落到 freq=1 层，按 LIFO 弹 4，再弹 7（5 还在底）。

> 题目给的 expected 顺序是 `5,7,5,4`，那是**输入顺序**；这里的 `7,5,4,7` 是 4 次 pop 的输出顺序。两者不要混。

## 复杂度
- `push`：$O(1)$（两个 dict 写入）。
- `pop`：$O(1)$（list.pop() 是尾弹）。
- 空间：$O(N)$，其中 $N$ 是 push 总次数 -- 每次 push 在 groups 里多占 1 个 slot；副本数等于 push 次数，不会爆。

## 易错点
1. **不要用 heap (freq, neg_seq, val)**：这种解法是 $O(\\log n)$，面试官点名要 $O(1)$ 时给 heap 答案就掉分。heap 只在"freq 不是单调递增、需要任意优先级"时才必要；这题 freq 严格 +1 且我们能维护 max_freq 局部变量，无需 heap。
2. **max_freq 的递减只在当前层空了之后**：`if not self.groups[self.max_freq]: self.max_freq -= 1`。不要写成 "freq[v] -= 1 后看 freq[v] 决定" -- freq[v] 是单个 val 的频次，max_freq 是全局最大频次，二者不一定同步。
3. **defaultdict(list) 不要换成 dict**：换成 dict 后 `groups[f].append(val)` 会 KeyError。如果一定要 dict，写 `groups.setdefault(f, []).append(val)`。
4. **push 和 pop 的对偶性**：push 把 val 放入 `freq[val]` 那一层；pop 总是从 `max_freq` 那一层取。两者层号不同 -- 这是为什么不需要"先找该 val 当前在哪一层" -- pop 只看 max_freq。

## Follow-up 追问指针
- **LC 716 Max Stack**：同家族的另一种 stateful 栈变体 -- push/pop/top + 还要 popMax。常见做法是双向链表 + TreeMap (Java) 或 SortedList (Python)，思想同样是"一个结构维主序，另一个结构维次序"。
- **LC 1429 First Unique Number**：流式数据上"首个不重复元素" -- 用双向链表 + hashmap 维护 freq=1 子集。同样是"频次状态 + 顺序结构"的组合。
- **如果改成 popMin（弹最低频）怎么办？**：维护 `min_freq` 不再像 max_freq 那样"自然单调下降"，需要 SortedList 或者 lazy delete。这是为什么这道题原版只问 max -- max_freq 单调维护是 $O(1)$ 的关键前提。
- **并发场景**：FreqStack 上加锁是简单解；要 lock-free 的话，groups[f].append 可以用 CAS，但 max_freq 的 read-modify-write 仍需要原子操作或 single-writer 模型。

## 一句话 pitch（面试 45 秒）
> 维护两个 dict：`freq[val]` 记当前频次，`groups[f]` 是频次为 f 的元素栈，外加 `max_freq` 缓存全局最高频次。push 时 freq 自增，把 val 放到对应频次的 group 里（注意低频 group 里它的副本还在）；pop 时直接从 max_freq 那个 group 尾部弹，freq 回退；如果当前 group 空了 max_freq 减一。低层副本天然代表"低频时期的存在"，pop 不需要跨层清理。push 和 pop 都是 $O(1)$，空间 $O(N)$。如果面试官问"为什么不用 heap"，答 heap 是 $O(\\log n)$，这里 freq 严格 +1 + max 单调，所以根本不需要优先队列。
"""


def main() -> None:
    """Attach notes and mark LC 895 as completed; idempotent via sentinel."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT id, notes, is_completed, family, pattern "
            "FROM problems WHERE leetcode_id = ?",
            (LC_ID,),
        ).fetchone()
        if row is None:
            raise SystemExit(f"LC {LC_ID} not in problems table")
        pid, existing_notes, _done, _fam, pat = row

        if existing_notes and SENTINEL in existing_notes:
            print(f"[UNCHANGED] LC {LC_ID} id={pid} (sentinel present)")
            return

        fields: dict[str, str | int] = {
            "notes": NOTES,
            "is_completed": 1,
        }
        if not pat:
            fields["pattern"] = PATTERN

        sets = ", ".join(f"{k} = ?" for k in fields)
        conn.execute(
            f"UPDATE problems SET {sets} WHERE id = ?",
            (*fields.values(), pid),
        )
        conn.commit()
        print(
            f"[UPDATED] LC {LC_ID} id={pid} "
            f"notes_len={len(NOTES)} fields={list(fields)}"
        )


if __name__ == "__main__":
    main()
