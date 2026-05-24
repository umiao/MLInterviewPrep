# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Append a Chinese 'Weight-Based Derivation & On-the-Fly Mnemonic' section
to LC 43 notes, incorporating user's insight from Discord 2026-04-13."""
import sqlite3

APPENDIX = r'''

---

### 临场推导 `ansArr[i + j + 1]` 的三种视角

常见的心理卡点：为什么两位相乘的结果写到 `ansArr[i + j + 1]`，不是 `ansArr[i + j]` 或别的？下面三种推导从严谨到"拍脑袋"，按你的节奏选一个。

#### 视角 A: 权重代数 (最严谨)

把下标翻译成 **10 的幂次**：

| 实体 | 权重 |
|------|------|
| `num1[i]`（从左数第 i 位） | `10^(m-1-i)` |
| `num2[j]` | `10^(n-1-j)` |
| `ansArr[k]`（长度 m+n） | `10^(m+n-1-k)` |

乘积权重相加：
```
(m-1-i) + (n-1-j) = (m+n-2) - (i+j)
```

令结果权重等于 `ansArr[k]` 的权重：
```
(m+n-1-k) = (m+n-2) - (i+j)
=> k = i + j + 1
```

**一次代数就把下标敲死**。面试写给面试官看很稳。

#### 视角 B: 位数上界 + 对齐 (直觉最强)

1. **上界事实**：m 位 × n 位 ≤ **m+n 位**（证明：`10^m · 10^n = 10^(m+n)`，所以两个 <= 10^m 和 <= 10^n 的数相乘 <= 10^(m+n)）。
2. 留长度 `m+n` 的数组。
3. `num1[i]` 是从高到低第 `i+1` 位，贡献应该落在结果的"中间偏左还是偏右"？
4. **用两个极端锚点秒验**（你自己写的方法，很好）：
   - **最低位相乘**：`i=m-1, j=n-1` → 应落在 `ansArr` 最右 = 下标 `m+n-1`。`i+j+1 = m+n-1` [Y]
   - **最高位相乘**：`i=0, j=0` → 应落在 `ansArr[1]`（留 `[0]` 给进位）。`i+j+1 = 1` [Y]
5. 两个锚点都对上 `i+j+1`，这公式就记住了。

**为什么是 `i+j+1` 而不是 `i+j`**：`i+j` 的最大值 = `(m-1)+(n-1) = m+n-2`，对应 ansArr 下标 `m+n-2`（倒数第二位），不是最后一位。差 1 的修正来自我们留了 `ansArr[0]` 给最终进位。

#### 视角 C: 一句话口诀 (临场最快)

> **"从左数下标越小，越靠高位 —— 所以结果里 `i+j` 小的也在左边；`+1` 是为最前面的进位预留一位。"**

临场如果你信得过自己的 trial-and-error：
1. 写 `ansArr[i + j] += x * y`
2. 做一遍 `"99" * "99"` = `9801` 的手算，发现溢出/对不上
3. 改成 `i + j + 1`，留 `ansArr[0]` 给最终进位

实战里**算一次 `99 * 99`** 比推权重代数快得多 —— 是 "small-case validation" 这个通用 trick 的具体应用。

### 为什么要从低位到高位做乘法？

你代码里 `for i in range(m-1, -1, -1)` 是从低位扫的。原因：

1. **低位在右，下标大**：从 `m-1` 往 0 扫等同于从个位扫到最高位，**自然顺序**。
2. **进位方向**：低位的进位向高位传递。如果从高位开始扫，每次遇到进位要回头改前面的位，代码复杂；从低位起所有进位都向"尚未处理的高位"传递，一次过。

但 `ansArr[i + j + 1]` 这一步**本身不涉及进位**——它只是把 `x * y` 累加到正确的位置。进位统一在第二个 for 循环（`ansArr[i - 1] += ansArr[i] // 10`）里处理。**这两件事解耦**，所以两个循环可以独立推导。

### 总结：三种视角怎么选

- **笔试 / OA**：视角 C 口诀 + `99 * 99` 手算 30 秒定下标。
- **面试白板**：视角 B 两锚点验证，边说边写，让面试官知道你是"推"出来的不是"背"出来的。
- **写题解 / 博客**：视角 A 权重代数严谨好看。

**三个视角指向同一个事实**：`i + j + 1` = 两位相乘权重之和在 `ansArr` 里对应的下标，偏移 `+1` 是为最终进位留的 `ansArr[0]`。
'''

conn = sqlite3.connect("data/mle_prep.db")
row = conn.execute("SELECT notes FROM problems WHERE leetcode_id = 43").fetchone()
new_notes = row[0] + APPENDIX
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 43", (new_notes,))
conn.commit()
print(f"[OK] LC 43 notes extended: {len(row[0])} -> {len(new_notes)} chars")
conn.close()
