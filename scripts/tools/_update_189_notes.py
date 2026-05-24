# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-shot: write LC 189 Rotate Array solution notes into problems.notes + mark completed."""
import sqlite3

NOTES = r'''# LeetCode 189. Rotate Array — 题解

## 题目

给定长度为 `n` 的数组 `nums`，将其向右旋转 `k` 步。要求 **O(n) 时间，O(1) 额外空间**。

```
[1,2,3,4,5,6,7], k=3  →  [5,6,7,1,2,3,4]
```

---

## 方法一：三次反转（推荐）

### 代数推导

把数组看成两段拼接 `[A | B]`，其中 `|A| = n-k`、`|B| = k`。目标是得到 `[B | A]`。

反转操作 `rev` 满足两条性质：

1. `rev² = id`（对合）
2. `rev(X · Y) = rev(Y) · rev(X)`（**反同态**，与矩阵转置 `(AB)ᵀ = BᵀAᵀ` 完全同构）

直接套第二条：

```
rev( rev(A) · rev(B) ) = rev(rev(B)) · rev(rev(A)) = B · A   ✓
```

所以做法天然就是：**反 A、反 B、再整体反**（或者反过来：先整体反，再分别反两段）。

### 代码

```python
def rotate(nums: list[int], k: int) -> None:
    n = len(nums)
    k %= n
    def rev(l: int, r: int) -> None:
        while l < r:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1
            r -= 1
    rev(0, n - 1)      # 整体反
    rev(0, k - 1)      # 反前 k 个
    rev(k, n - 1)      # 反后 n-k 个
```

**复杂度**：每个位置被访问常数次，时间 O(n)，额外空间 O(1)。

---

## 方法二：循环替换（cyclic replacements）

### 思路

位置 `i` 上的元素最终要去 `(i + k) % n`。从某个起点不停跳，会形成长度为 `n / gcd(n, k)` 的循环；总共有 `gcd(n, k)` 个独立循环，各自处理一遍。

实现要点：
- 用 `prev` 暂存即将被覆盖的值，swap 后继续；
- 用全局计数器 `count` 累计到 `n` 即停，避免显式算 `gcd`。

### 代码

```python
def rotate(nums: list[int], k: int) -> None:
    n = len(nums)
    k %= n
    count = 0
    start = 0
    while count < n:
        current, prev = start, nums[start]
        while True:
            nxt = (current + k) % n
            nums[nxt], prev = prev, nums[nxt]
            current = nxt
            count += 1
            if current == start:
                break
        start += 1
```

**复杂度**：每个元素恰好被搬一次，时间 O(n)，额外空间 O(1)。

---

## 两种方法的对比

| | 三次反转 | 循环替换 |
|---|---|---|
| 代码量 | 极短，几乎不会写错 | 双重循环，边界易错 |
| 实际操作次数 | 每个位置被读写 ~2 次 | 每个位置恰好 1 次 |
| 思维难度 | 需要先看出代数恒等式 | 需要理解置换的循环分解 |
| 适用场景 | 首选答案 | 展示对群论 / 置换结构的理解 |

---

## 为什么三次反转"自然"——结构视角

### 代数：involutive monoid

`(Σ*, ·, rev)` 是一个带对合的幺半群（involutive monoid）。这种结构里，`rev` 扮演的角色和矩阵转置完全一致：

| 矩阵 | 序列 |
|---|---|
| `transpose` | `reverse` |
| `(AB)ᵀ = BᵀAᵀ` | `rev(AB) = rev(B) rev(A)` |
| 90° 旋转 = transpose ∘ flip | 数组旋转 = `rev ∘ (rev ⊗ rev)` |
| `D₄` 作用在方阵上 | involutive monoid 作用在序列上 |

> 一句话：方阵旋转用 transpose + flip，数组旋转用 rev + 子段 rev。**同一个抽象骨架**。

### 几何：二面体群

`D_n` 里有个标准事实：

> 任意两个反射的复合是一个旋转，旋转角度 = 两反射轴夹角的 2 倍。

`rev_all`（整段反转）就是 `D_n` 里的一个反射。要旋转 `k`，还需要"第二个反射"——它对应的反射轴在 `k/2` 处。这个反射在数组上没法一步做出来，但 `rev(0..k-1) ∘ rev(k..n-1)` 恰好等于它（两个不交子段的反转拼出一个完整反射）。所以：

```
rotate(k) = rev_all  ∘  [ rev(0..k-1) ∘ rev(k..n-1) ]
            └─反射₁─┘    └────── 反射₂ ──────┘
```

二面体群里"旋转 = 两反射复合"，落在数组上就是**三次反转**。

---

## 一句话总结

- **代数视角**：`rev` 是对合反同态，三次反转就是 `rev(rev(A)·rev(B)) = B·A` 的展开。
- **几何视角**：`D_n` 中旋转 = 两反射复合；其中一个反射要用两次子段反转拼出来，总数为 3。
- **工程视角**：写它，别想太多。
'''

conn = sqlite3.connect("data/mle_prep.db")
cur = conn.execute(
    "UPDATE problems SET notes = ?, is_completed = 1 WHERE leetcode_id = 189",
    (NOTES,),
)
conn.commit()
print(f"[OK] LC 189 notes updated ({len(NOTES)} chars), rows={cur.rowcount}, is_completed=1")
conn.close()
