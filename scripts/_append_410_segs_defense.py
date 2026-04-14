"""Append the segs=1 vs usedCnt=0 correctness defense to LC 410 notes.
Captures the Discord follow-up discussion 2026-04-13."""
import sqlite3

APPENDIX = r'''

---

### 深入点 #2：为什么 `segs = 1` 起步是正确的（对质疑的回应）

常见疑问："如果默认从 1 开始，全 0 数组不就算错了吗？用了 0 段应该是 0。"

**简短回答**：在 LC 410 的约束下，`segs = 1` 起步永远正确，`usedCnt = 0` 只是"靠不等式侥幸过题"。

#### 核心论点：只要 `nums` 非空，答案就 >= 1 段

LC 410 明确约束 `1 <= nums.length <= 1000`。非空数组必须被装进**至少一个 subarray**，所以 "0 段" 永远不是合法答案。

`segs = 1` 不是"默认认为用了 1 段"，而是 **"一进入循环就已经隐式开了第一段（还没放任何元素）"**。这是 loop invariant 的初始化而不是"预先加账"。

#### Corner-case 对照表

| 输入 | 正确答案 | `segs=1` 版 | `usedCnt=0` 版 |
|------|---------|------------|----------------|
| `nums=[0,0,0], k=1, cap=0` | 1 段 | 返回 True（`1 <= 1`）✓ | 返回 True（`0 <= 1`），但语义算的是"0 段"❌ |
| `nums=[0], k=1` | 1 段 | 返回 True ✓ | 巧合 True（靠 `0 <= k`）|
| `nums=[]`（题目不允许）| 0 段 | 需 `if not nums: return 0` 特判 | 自然返回 0 |
| 一般情况 | >= 1 段 | 完全正确 | 完全正确 |

#### "usedCnt=0 在全 0 时 AC" 不是正确，是运气

`usedCnt = 0` 的逻辑只在两种情况下 +1：
1. 遇到 `v > curBox` 开新段
2. 循环结束时 `curBox < upperbound`（"有东西消耗了容量"）

全 0 时两个条件都不触发 → `usedCnt = 0`。此时**真实答案是 1 段**，但返回 `0 <= k = True` **仅因为 k >= 1 时不等式恒成立**。这是用错误的 usedCnt 过了不等式，不是逻辑正确。

#### 什么场景会坏？

如果题目变体为 **"minimize #segments such that each seg >= threshold"**（最大化段数 / 精确段数），feasibility 函数需要**段数的精确值**，不再是 "<= k" 形式。这时 `usedCnt = 0` 会直接算错。

`segs = 1` 的写法在段数语义精确对齐，改编到同骨架变体时不需要重审正确性。

#### 空数组兜底的不对称

仔细看：**`usedCnt = 0` 只在空数组时"正确"（返回 0）**，但这种情况 LC 410 根本不给。代价是**常规非空数组时语义错（多算 1）**，靠不等式救回来。

**`segs = 1`** 在空数组时"错 1"（需要特判），但常规非空时**每一步都和真值对齐**。哪个更值得？在 "1 <= nums.length" 的题目里，后者压倒性胜出。

#### 结论

- `segs = 1` 起步：**语义精确**，robust 到各种变体
- `usedCnt = 0` 起步：**靠不等式侥幸**，在 LC 410 原题 AC，但迁移到变体题会坏

推荐 canonical `segs = 1` 写法，这是风格偏好的**技术原因**（不是单纯美观）。
'''

conn = sqlite3.connect("data/mle_prep.db")
row = conn.execute("SELECT notes FROM problems WHERE leetcode_id = 410").fetchone()
new_notes = row[0] + APPENDIX
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 410", (new_notes,))
conn.commit()
print(f"[OK] LC 410 notes extended: {len(row[0])} -> {len(new_notes)} chars")
conn.close()
