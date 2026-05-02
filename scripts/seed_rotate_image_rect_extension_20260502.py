"""Seed: T-P0-691 [MLI-E1] -- Rotate Image rectangular n*m generalization.

APPENDS a rectangular n*m extension section to ``problems.id=73``
(Rotate Image, LC 48). The existing square-only content is PRESERVED
verbatim -- this script only adds an append-block guarded by sentinel
``<!-- ROTATE_IMAGE_RECT_20260502 -->`` so a second run is a 0-write
no-op.

Why this extension matters (from the original task brief):
- LC 48 is square-only, but the natural follow-up "what if the matrix is
  n*m?" exposes a deep gap. 180-degree rotation generalizes trivially via
  the involution (i, j) <-> (n-1-i, m-1-j); 90-degree rotation in the
  rectangular case has NO simple in-place D_4 decomposition because the
  output shape m*n != input shape n*m. The interview-acceptable answer is
  O(nm) auxiliary; the theoretical O(1) auxiliary algorithm is
  Cate-Twigg 1977 (ACM TOMS Algorithm 513), which uses the multiplicative
  group structure sigma(k) = k * n mod (N - 1) to enumerate cycle leaders
  in-place. FFTW's in-place transpose is a descendant.

Style anchors (per task spec):
1. problems.id=73 existing notes -- match its Chinese-prose voice.
2. problems.id=1064 K-Means -- canonical SECTION baseline.
3. scripts/seed_geometric_median_20260502.py (T-P0-690) -- direct UPSERT
   template (sentinel-guarded append, 0-write second run).

Technical content (verified during planning, all citations real):
- D_4 dihedral group (8 elements: 4 rotations + 4 reflections).
  Decompositions used in the square case:
      R_90  = H circ T = T circ V
      R_180 = H circ V = V circ H
      R_270 = V circ T = T circ H
  where T = transpose (along main diagonal), H = horizontal flip (mirror
  left-right), V = vertical flip (mirror up-down).
- TETRAHEDRAL-GROUP WARNING (motivated): the original brief used
  "tetrahedral group" (sihuanti qun, A_4 / S_4) when meaning dihedral D_4
  -- a real terminology slip. A_4 (order 12) and S_4 (order 24) are the
  rotation/full symmetry groups of the regular tetrahedron and have NO
  direct relation to matrix rotation. Without this framing the warning
  feels abstract; with it, it documents a concrete pedagogical pitfall.
- Cate, E. G. & Twigg, D. W. (1977). "Algorithm 513: Analysis of
  in-situ transposition", ACM Transactions on Mathematical Software
  3(1):104-110. The first practical O(1)-extra-space rectangular
  in-place transpose. Built on Brenner (1973) "Algorithm 467: Matrix
  transposition in place" (Comm. ACM 16(11):692-694). FFTW's source
  ships an in-place transpose in this lineage.

Idempotency:
- Sentinel <!-- ROTATE_IMAGE_RECT_20260502 --> at the head of the
  appended block. If present, second run is a 0-write skip.
- Canonical key: problems.id = 73 (LC 48 = "Rotate Image"). The script
  asserts leetcode_id = 48 before writing as a sanity check.
- Existing square-case content is preserved byte-for-byte (no edit to the
  pre-sentinel substring).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

PROBLEM_ID = 73
EXPECTED_LEETCODE_ID = 48
SENTINEL = "<!-- ROTATE_IMAGE_RECT_20260502 -->"

APPEND_BLOCK = "\n\n" + SENTINEL + r"""

---

## 推广: n*m 长方矩阵旋转 (rectangular case)

### 题目推广

LC 48 给的是 n*n 方阵原地旋转 90 度. 一个非常自然 (面试常追问) 的推广是:

> 给一个 n 行 m 列的整数矩阵, 顺时针旋转 90 度. 旋转后形状变成 m*n.

**核心挑战 (in-place 语义在长方下的微妙)**:

- 当 $n = m$ (方阵) 时, 输出形状和输入形状一致 (n*n -> n*n), "原地"
  含义清晰: 同一块 $n^2$ 内存就够.
- 当 $n \ne m$ 时, 输入是 $n \times m$, 输出是 $m \times n$. 即便元素总数
  相同 ($N = nm$), **行列长度变了**, "原地" 不再是 "在同一块二维数组上写
  回", 而是 "在同一块**线性**内存上重排". 这就是为什么 LC 48 把题目限定
  为方阵 -- 长方版本的 in-place 旋转在工程上更接近**矩阵转置**, 而不是
  方阵 D_4 群里的几何操作.

### 解法层次

按 "面试要写的代码" -> "面试要说出来但不写的特殊情形" -> "理论上能做到但
工业级才实现的极限" 三层组织.

#### 层 1 (主答案): 开 m*n 辅助, $O(nm)$ 时间 / $O(nm)$ 额外空间

```python
def rotate_rect(matrix: list[list[int]]) -> list[list[int]]:
    # Clockwise 90 degrees, returns a new m*n matrix.
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    out = [[0] * n for _ in range(m)]
    for i in range(n):
        for j in range(m):
            # (i, j) in n*m  ->  (j, n-1-i) in m*n
            out[j][n - 1 - i] = matrix[i][j]
    return out
```

**坐标推导**: 顺时针 90 度的几何映射是 $(i, j) \to (j, n - 1 - i)$. 在
方阵下行列等长, 可以直接覆盖原数组; 在长方下输出维度变成 $m \times n$,
所以必须开新数组. **这是面试的标准答卷.**

**复杂度**: 时间 $\Theta(nm)$, 空间 $\Theta(nm)$ (输出本身).

#### 层 2 (特殊情形): 几个允许 $O(1)$ 额外空间的子问题

这些子问题应该**口头说出来**, 让面试官知道你看到了结构, 但**不必写完代码**
(除非被追问).

**(a) 任意形状的 180 度旋转: $O(1)$ 额外空间, 单遍**

180 度旋转的映射是 $(i, j) \leftrightarrow (n-1-i, m-1-j)$. 它是一个
**对合 (involution)**: 应用两次回到自身, 所以可以两两配对地原地交换.

```python
def rotate_180_inplace(matrix: list[list[int]]) -> None:
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    half = (n * m) // 2
    for k in range(half):
        i1, j1 = divmod(k, m)
        i2, j2 = n - 1 - i1, m - 1 - j1
        matrix[i1][j1], matrix[i2][j2] = matrix[i2][j2], matrix[i1][j1]
    # If n*m is odd, the center cell is its own image (no-op).
```

**关键**: 180 度的输出形状和输入形状相同 ($n \times m$ 还是 $n \times m$),
所以"原地"语义和方阵版本一样干净.

**(b) 方阵 90 度: $O(1)$ 额外空间, $H \circ T$ 分解 (LC 48 主解)**

方阵下 (n = m) 的主解就是题面给的 transpose + 行翻转:

$$R_{90} = H \circ T$$

其中 $T$ (转置) 是关于主对角线的对合, 在上三角原地交换; $H$ (水平翻转)
是每行内的对合, 头尾对换. 两个对合都是 $O(1)$ 额外空间, 合起来仍然是
$O(1)$. **必须 n = m**, 否则转置后形状变成 m*n 已经"飞出"了原数组.

#### 层 3 (理论极限): 长方 90 度的 $O(1)$ 额外空间

**这一层是面试不写, 但应该知道存在并能 cite 出处的内容.**

长方 90 度旋转 $\Leftrightarrow$ 长方原地转置 + 行翻转 (或列翻转, 取决于
方向). 长方 in-place 转置的 $O(1)$-辅助算法是经典数值线性代数问题:

- **Brenner (1973)**, "Algorithm 467: Matrix transposition in place",
  Communications of the ACM 16(11), 692-694. 第一个实用 in-place 长方
  转置算法.
- **Cate & Twigg (1977)**, "Algorithm 513: Analysis of in-situ
  transposition", ACM Transactions on Mathematical Software 3(1),
  104-110. 用乘法群 $\sigma(k) = kn \bmod (N - 1)$ 的循环结构枚举 cycle
  leaders, 给出严格的循环长度分析.
- **FFTW 的 in-place transpose** (`fftw3/rdft/`) 实现自此一脉. 工业级
  代码, 加 SIMD / cache blocking 后比 "开新数组" 还快.

**核心思路**: 把 $n \times m$ 矩阵看作长度 $N = nm$ 的一维数组 (row-major).
位置 $k = im + j$ 在转置后应去到 $k' = jn + i$. 数学上 $k \to kn \bmod
(N - 1)$ 是 $\mathbb{Z}_{N-1}^*$ 的一个置换 (假设 $\gcd(n, N-1) = 1$),
循环结构由 $n$ 在该群的阶决定. **沿每个循环依次搬一个 buffer 元素**:
$O(N)$ 时间, **$O(1)$ 额外空间** (一个临时变量).

**为什么不写**: cycle-leader 枚举要么需要预知所有循环 (查表), 要么需要
"已搬过" 标记位 (恢复 $O(1)$ 空间不平凡), 实现细节远超白板范围. 面试官
听到 "Cate-Twigg 1977 / FFTW" 已经是满分答卷.

### 群论补丁: $D_4$ 与方阵旋转的关系

(原 LC 48 笔记里的 $D_4$ 引用在这里被推广)

方阵 $n = m$ 时, **8 个 $D_4$ 元素** (4 旋转 + 4 反射) 都是 $n \times n$
矩阵到自身的对合或周期性变换, 全都可以原地实现:

| 元素 | 形式 | 几何 | 阶 (期周) | 原地? |
|------|------|------|----------|--------|
| $e$ | 恒等 | -- | 1 | trivially |
| $R_{90}$ | $H \circ T$ | 顺时针 90度 | 4 | 是 (T + H 各 $O(1)$) |
| $R_{180}$ | $H \circ V$ | 180度 | 2 | 是 (involution) |
| $R_{270}$ | $V \circ T$ | 逆时针 90度 | 4 | 是 (T + V 各 $O(1)$) |
| $H$ | 行翻转 | 水平镜像 | 2 | 是 (involution) |
| $V$ | 列翻转 | 垂直镜像 | 2 | 是 (involution) |
| $T$ | 主对角对合 | 转置 | 2 | 是 (involution) |
| $T'$ | 副对角对合 | 反对角转置 | 2 | 是 (involution) |

**长方 $n \ne m$ 时**, $D_4$ 群作用**部分破坏**:

- $R_{180}$, $H$, $V$ 仍保形状 ($n \times m$ -> $n \times m$), 仍可
  $O(1)$ 原地.
- $R_{90}$, $R_{270}$, $T$, $T'$ 都把形状换成 $m \times n$, 不能在原
  $n \times m$ 数组里完成 -- 必须开辅助或用层 3 的 cycle-leader 算法.

### 警示: $D_4$ 不是 "四面体群"

**这是一个非常常见的术语滑步, 必须明确**: 二面体群 $D_4$ (order 8) 是
正方形的对称群 -- 是**这道题需要的群**. 它和 "四面体群" $A_4$ / $S_4$
(order 12 / 24) 完全无关:

- $A_4$ (alternating group) -- 正四面体的旋转对称群, 12 阶, 偶置换.
- $S_4$ (symmetric group) -- 正四面体的全对称群 (含反射), 24 阶, 任意置换.
- $D_4$ (dihedral group) -- 正方形的对称群, 8 阶, 4 旋转 + 4 反射.

中文里 "二面体" 和 "四面体" 一字之差, 群论里不是同一个对象. 写 LC 48 解
答时如果说 "本质是四面体群", 听起来很玄但其实**指错了对象**, 几何意义和
矩阵旋转对不上号. 正确的表述是: **方阵 90 度旋转的 in-place 实现, 利用
了二面体群 $D_4$ 在 8 个对合 / 周期性变换里的结构, 把一次旋转分解成两
次对合**.

### 复杂度下界表 (informal)

| 输入形状 + 旋转 | 时间下界 | $O(1)$ 额外空间可达? | 怎么达到 |
|------|---------|---------|--------|
| 任意 $n \times m$, **180 度** | $\Theta(nm)$ | **是** | 单遍对合两两交换 |
| 方阵 $n \times n$, **90 / 270 度** | $\Theta(n^2) = \Theta(nm)$ | **是** | $D_4$ 分解 ($H \circ T$ 等), 两次对合 |
| 长方 $n \times m, n \ne m$, **90 / 270 度** | $\Theta(nm)$ | **理论是** (Cate-Twigg 1977), 工业 $\Theta(nm)$ 辅助 | cycle-leader / FFTW; 面试不写 |

时间下界 $\Theta(nm)$ 对所有版本都 tight: 输出每个元素都至少要被写一次,
所以任何正确算法都至少 $\Omega(nm)$.

### 面试可达的最优 (收口)

- **方阵 90 度 + 任意形状 180 度**: 白板上能写完, $O(1)$ 额外空间.
- **长方 90 度**: **面试答案是 $O(nm)$ 额外空间** (开 $m \times n$ 新
  数组). 理论 $O(1)$ 存在 (Cate-Twigg 1977 / Brenner 1973 / FFTW),
  但只在工业级 BLAS / FFT 库里实现, **白板写不出来也不该写**. 能 cite
  出处 + 解释思路 (cycle leaders on $\sigma(k) = kn \bmod (N-1)$) 就是
  这道题的天花板答卷.
- **更广的角度**: $D_4$ (二面体群, 不是四面体群) 给方阵的 8 个变换都
  提供 $O(1)$ 原地实现; 长方下只有 $\{e, H, V, R_{180}\}$ 这 4 个保形
  状的元素仍能 $O(1)$ 原地, 其余 4 个换形状的需要落到层 3.
"""


def main() -> int:
    """Append rectangular extension section to problems.id=73 notes."""
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT id, leetcode_id, title, notes "
            "FROM problems WHERE id = ?",
            (PROBLEM_ID,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] problems.id={PROBLEM_ID} not found")
            return 1

        pid, leetcode_id, title, old_notes = row
        old_notes = old_notes or ""

        if leetcode_id != EXPECTED_LEETCODE_ID:
            print(
                f"[FAIL] problems.id={pid} has leetcode_id={leetcode_id}, "
                f"expected {EXPECTED_LEETCODE_ID}. Aborting to avoid editing "
                f"the wrong row."
            )
            return 1

        if SENTINEL in old_notes:
            print(
                f"[SKIP] id={pid} '{title}' already has sentinel "
                f"{SENTINEL} (notes={len(old_notes)} chars, no write)"
            )
            return 0

        new_notes = old_notes.rstrip() + APPEND_BLOCK
        conn.execute(
            "UPDATE problems SET notes = ? WHERE id = ?",
            (new_notes, pid),
        )
        conn.commit()
        print(
            f"[APPEND] id={pid} '{title}' (LC {leetcode_id}) "
            f"+ rectangular extension, notes "
            f"{len(old_notes)} -> {len(new_notes)} chars"
        )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
