"""[META-ANC-4] Sparse Matrix Ops drawer (Meta AI-Native Coding).

Inserts ONE problems row that becomes the db://<id> drawer for the Sparse
Matrix Operations Meta AI-Native Coding question. Distills the COO/CSR/CSC
storage trio + sparse-vector double-pointer dot product + sub-cubic matmul
landscape (Strassen / Coppersmith-Winograd / Alman-VW 2024) plus the BLAS
GEMM industry-reality counterpoint into a single description.

Idempotency key: (source='Meta-AI-Native-Coding-2026-05-01',
pattern='sparse_format_dot_product'). The pattern column is the STABLE
SLUG -- never rewritten. The title may evolve. A sentinel HTML comment
<!-- ANC_SLUG: meta_anc_sparse_matrix_ops --> is embedded at the top
of the description for grep-based discovery.

Plus a problem_company_tags row linking the inserted problem to the Meta
company row (id resolved by name lookup, asserted == 31).

Source: docs/staging/sources/meta_ai_native_coding_2026_05_01.md
(Section 4 first half, lines 235-265).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.company_tags import ProblemCompanyTag  # noqa: E402
from src.backend.models.problem import Problem  # noqa: E402

SLUG = "meta_anc_sparse_matrix_ops"
SOURCE = "Meta-AI-Native-Coding-2026-05-01"
PATTERN = "sparse_format_dot_product"
TITLE = "Meta AI-Native Coding - Sparse Matrix Ops (COO/CSR/CSC + double-pointer dot + subcubic matmul)"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
DESCRIPTION_SOURCE = "manual"
SENTINEL = f"<!-- ANC_SLUG: {SLUG} -->"

REQUIRED_KEYWORDS = [
    "COO",
    "CSR",
    "CSC",
    "双指针",
    "Strassen",
    "BLAS",
]

DESCRIPTION = SENTINEL + r"""

# Sparse Matrix Ops -- Meta AI-Native Coding (COO/CSR/CSC + 双指针 dot + 亚立方 matmul)

> **题型**: 实现稀疏向量点积 / 稀疏矩阵乘法；让 AI 对比三种存储格式在乘法运算中的性能差异。
> **场景**: Meta AI-Native Coding MLE / 实习向；这道题的差异化得分点是"让 NNZ 取代维度成为复杂度主导项"的洞察 + "理论复杂度 != 实际性能"的工业界反差。
> **AI 协同**: 让 AI 生成各格式的 toy benchmark 并对比性能差异，自己掌握选型逻辑（构建期 COO，运算期 CSR/CSC）。

---

## 1. 核心思路一句话

稀疏向量 / 矩阵运算的核心是**让 NNZ (非零元个数) 取代维度成为复杂度主导项**。做点积或乘法时，先比较两边稀疏度，**找更稀疏的一方作为入口和瓶颈**，把它转成坐标形式 (COO 三元组)，然后永远遍历稀疏的那一方，对稠密的一方用哈希 / 二分定位即可。

**反直觉点**: 同样是 $n \times n$ 矩阵，dense 是 $O(n^2)$ 元素，但稀疏可能只有 $O(n)$ 非零元——所以**复杂度主导项不是 $n$ 而是 $\text{nnz}$**。考官想听到的是这一句"NNZ 取代维度"，而不是直接套 $O(n^3)$。

---

## 2. 三种存储格式对照表

| 格式 | 数据结构 | 构建成本 | 行访问 | 列访问 | 友好场景 | 工业惯例 |
|------|----------|----------|--------|--------|----------|----------|
| **COO** (Coordinate) | 三元组 `(row, col, val)` 列表 | 最快 (直接 append) | 慢 (要扫全表) | 慢 (要扫全表) | 增量构建期 | 数据进来时先攒成 COO |
| **CSR** (Compressed Sparse Row) | `row_ptr` + `col_idx` + `val` | 需要按行排序 | 快 (`row_ptr` 直接定位) | 慢 | SpMV ($Av$, 按行归约) | 运算期 `.tocsr()` |
| **CSC** (Compressed Sparse Column) | `col_ptr` + `row_idx` + `val` | 需要按列排序 | 慢 | 快 (`col_ptr` 直接定位) | SpMV^T ($A^Tv$), 取列 | 运算期 `.tocsc()` |

**SciPy 设计哲学**: 构建期用 COO -> 一次性 `.tocsr()` / `.tocsc()` 转格式 -> 运算期用压缩格式。这个 pipeline 是面试金句——比"我用 dict-of-dict"高一个等级。

**经典搭配**: $C = A \times B$ 的稀疏实现，**A 用 CSR (取行)**, **B 用 CSC (取列)**, 每个 $C_{ij}$ 归约成"行 i 与列 j 的稀疏向量点积"。

---

## 3. 核心 idiom: 稀疏向量点积 (双指针)

### 3.1 排序输入版 -- $O(\text{nnz}_1 + \text{nnz}_2)$

```python
def sparse_dot(v1, v2):
    # v1, v2: List[(idx, val)]，按 idx 升序排列
    i, j, res = 0, 0, 0.0
    while i < len(v1) and j < len(v2):
        if v1[i][0] == v2[j][0]:
            res += v1[i][1] * v2[j][1]
            i += 1
            j += 1
        elif v1[i][0] < v2[j][0]:
            i += 1
        else:
            j += 1
    return res
```

**为什么是 双指针 而非 hash**: 输入已排序时，双指针 cache 友好、常数小、零额外内存；hash 表有 hash 计算 + 装载因子开销。**有序假设是关键**——这是 LeetCode 1570 的标准答案。

### 3.2 一稀一稠版 (一边 nnz 远小于另一边) -- $O(\text{nnz}_{\text{small}})$

```python
def sparse_dot_asym(sparse, dense):
    # sparse: dict {idx: val}，dense: list (full vector)
    return sum(v * dense[i] for i, v in sparse.items())
```

只遍历稀疏端，对稠密端做 $O(1)$ 索引。**复杂度只跟稀疏一方的 NNZ 有关**——这是工业界 SpMV 的核心优化。

### 3.3 未排序版 -- 哈希查表 $O(\text{nnz}_1 + \text{nnz}_2)$

```python
def sparse_dot_unsorted(v1, v2):
    # v1, v2: List[(idx, val)]，未排序
    table = {idx: val for idx, val in v1}
    return sum(val * table.get(idx, 0.0) for idx, val in v2)
```

输入无序就丢一边进哈希、遍历另一边查表，期望 $O(\text{nnz}_1 + \text{nnz}_2)$。**面试金句**: "如果允许排序就用 双指针 (cache 友好)；不允许预处理就用 hash (常数大但简单)。"

---

## 4. 矩阵乘法 < $O(n^3)$ 的主流算法谱系

| 算法 | 复杂度 | 原理 | 实战意义 |
|------|--------|------|----------|
| **朴素三重循环** | $O(n^3)$ | 三层 for | BLAS GEMM 的真实底层 |
| **Strassen** (1969) | $O(n^{2.807})$ | 分治: 把 $2 \times 2$ 分块乘法的 8 次子乘法重组为 **7 次子乘法 + 18 次加法**，递归下去 | 大矩阵理论上更快，但数值不稳 + 常数大，实际很少用 |
| **Coppersmith-Winograd 系列** | $\sim O(n^{2.37})$ | 借助张量秩 (tensor rank) 上界构造的递归方案 | **常数极大，只有理论意义**，从未进入生产 |
| **当前最优 (Alman-VW, 2024)** | $\sim O(n^{2.371})$ | 同系列改进 | 同上，纯理论 |

**记忆口诀**: $n^3 \to n^{2.807}$ (Strassen) $\to n^{2.37}$ (CW) $\to n^{2.371}$ (Alman-VW 2024)。**指数 2.37x 是当前最好的渐近界**，但工业界**没人用**——这是反差点。

---

## 5. 工业界反差: 为什么 BLAS 仍然是 $O(n^3)$？

考官最爱的 follow-up: "Strassen 复杂度更低，为什么 NumPy / PyTorch / cuBLAS 都不用？"

### 标准答案三段论

1. **常数因子**: Strassen 的隐藏常数 (18 次加法 + 递归开销 + 临时矩阵分配) 在 $n < 1024$ 时**比朴素三重循环还慢**。
2. **数值稳定性**: Strassen 的减法步骤会放大舍入误差 (catastrophic cancellation)，浮点累积误差 $O(n^{\log_2 7})$ 而朴素只有 $O(n)$。
3. **硬件优化路径**: BLAS 的 GEMM 仍是朴素 $O(n^3)$ 三重循环，但靠 **cache blocking** + **SIMD/AVX** + **多线程** + **GPU 张量核** 把常数压到极致——比 Strassen 快、数值更稳定。

**金句**: "**理论复杂度 != 实际性能**"。这一句是 senior signal——展示你知道渐近分析 vs 工程实现的差距。

### 何时 Strassen 真的有用

只有在 $n > 几千$ 且数值精度要求不高的特殊场景 (例如 GPU 上的极大矩阵乘法库 cuTLASS) 才会用 Strassen 变体——而且通常是**混合策略**: 顶层 Strassen 分治到 $n < 128$ 就切回朴素 GEMM。

---

## 6. 高频 follow-up

### Q1: 稀疏未排序怎么办？
丢一边进哈希表 `{idx: val}`，遍历另一边查表，期望 $O(\text{nnz}_1 + \text{nnz}_2)$。详见 §3.3。

### Q2: 稀疏矩阵转置 $A \to A^T$ 要不要真做？
**不需要真做**——CSR 和 CSC 互为转置，**换个视角读就行**，$O(1)$。读 CSR 为 CSC 就是 $A$ 看成 $A^T$。**这是面试金句级洞察**。

### Q3: CSR x CSC 经典搭配怎么算？
$C_{ij} = \langle A[i, :], B[:, j] \rangle$，A 取行 (CSR 友好) + B 取列 (CSC 友好)，每个 $C_{ij}$ 归约成"行 i 的稀疏向量与列 j 的稀疏向量做点积"——直接调 §3 的双指针 idiom。整体复杂度 $O(\sum_i \sum_j (\text{nnz}_{A,i} + \text{nnz}_{B,j}))$，远低于 $O(n^3)$。

### Q4: 稀疏度阈值是多少？
经验法则: NNZ / total < 5% 才值得用稀疏格式。**否则 dense + BLAS 反而更快** (cache 友好 + SIMD)。这又是"理论 != 实际"的体现。

### Q5: 为什么 SciPy 不让你直接 COO 做乘法？
COO 的 `__mul__` 内部会自动 `.tocsr()` 再算——因为 COO 行 / 列访问都是 $O(\text{nnz})$ 扫全表，乘法实际上**必须**走压缩格式。这是工业 API 强制的最佳实践。

---

## 7. AI 协同分工对照表

| 让 AI 做 | 自己做更快 / 更靠谱 |
|----------|---------------------|
| 生成 COO/CSR/CSC 的 toy benchmark 代码 | **选型逻辑**: 构建期 COO -> 运算期 CSR/CSC |
| 对比三种格式在 SpMV 上的性能数字 | "**理论复杂度 != 实际性能**"金句的口头表述 |
| 实现 双指针 稀疏点积模板 | 何时双指针 vs hash 的 trade-off 判断 |
| 列出 Strassen / CW / Alman-VW 复杂度数 | "为什么 BLAS 仍是 $O(n^3)$"三段论 (常数 / 数值稳定 / 硬件优化) |
| 写 unit test 覆盖 (空向量 / 单元素 / 全相同 idx / 完全不重叠) | 稀疏度阈值的工程经验 (<5% 才值得稀疏) |

**底线**: AI 帮你打代码 + 列公式，**判断 (该用什么格式 / 阈值 / 何时切回 dense)** 必须自己讲。这是这道题的 senior signal。

---

## 8. 三句金句 (面试用来秀洞察)

1. **格式选型金句**: "**构建期用 COO，运算期 .tocsr() / .tocsc()**——SciPy 就是这么设计的。"
2. **复杂度反差金句**: "BLAS 的 GEMM 仍是 $O(n^3)$ 三重循环，但靠 **cache blocking + SIMD + 多线程**把常数压到极致——**理论复杂度 != 实际性能**。"
3. **转置零成本金句**: "稀疏矩阵转置不用真做——CSR 和 CSC 互为转置，**换个视角读就行**，$O(1)$。"

讲这三句的时候放慢节奏——它们值的分比闷头打代码多。

---

## 9. 一图流总结

```
输入 nnz 取代 n 成主导项
        |
        v
构建期: COO 三元组 (append-friendly)
        |
        v (一次性 .tocsr() / .tocsc())
运算期: CSR (取行/SpMV) / CSC (取列/SpMV^T)
        |
        v
点积: 双指针 (有序) / hash (无序) / 一稀一稠 (遍历稀疏端 + 索引稠密端)
        |
        v
矩阵乘: A=CSR, B=CSC -> 每个 C[i,j] 归约成稀疏点积
        |
        v
理论亚立方: Strassen (2.807) / CW (2.37) / Alman-VW 2024 (2.371)
工业反差: BLAS GEMM 仍 O(n^3)，靠 cache+SIMD+并行常数压到极致
```

**记住**: 这道题的差异化签名是 (1) 让 NNZ 取代维度的洞察，(2) 构建/运算分离的 COO -> CSR 流水线，(3) 理论复杂度 != 实际性能的工业反差。三件事都讲到位 = senior signal。
"""


def _normalize(text: str) -> str:
    """Semantic normalization for NOOP comparison.

    Strip per-line trailing whitespace, force LF line endings, collapse
    3+ blank lines down to 2. Forbids accidental [UPDATED] reports caused
    by trailing-whitespace drift or platform line-ending differences.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _assert_required_keywords(description: str) -> None:
    """Abort if any REQUIRED-KEYWORD is missing from the description."""
    for kw in REQUIRED_KEYWORDS:
        if kw not in description:
            raise RuntimeError(
                f"[META-ANC-4] missing keyword {kw!r} -- regenerate"
            )


def _assert_no_emoji(description: str) -> None:
    """Project rule: no emoji characters in content."""
    for ch in description:
        cp = ord(ch)
        if (
            0x1F300 <= cp <= 0x1FAFF
            or 0x1F000 <= cp <= 0x1F2FF
            or 0x2600 <= cp <= 0x27BF
        ):
            raise RuntimeError(
                f"[META-ANC-4] emoji character U+{cp:04X} found at "
                f"position {description.index(ch)}"
            )


def upsert_meta_anc_sparse_matrix_ops() -> int:
    """Insert or update the Sparse Matrix Ops drawer; return problems.id."""
    init_db()
    db = SessionLocal()

    if SENTINEL not in DESCRIPTION:
        raise RuntimeError(f"[META-ANC-4] sentinel missing: {SENTINEL!r}")
    _assert_required_keywords(DESCRIPTION)
    _assert_no_emoji(DESCRIPTION)

    try:
        company_id = (
            db.query(Company).filter(Company.name == "Meta").one().id
        )
        if company_id != 31:
            raise RuntimeError(
                f"[META-ANC-4] expected Meta company_id=31, got {company_id}"
            )
        print(f"[OK] target company: id={company_id} name='Meta'")

        existing = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .first()
        )

        normalized_new = _normalize(DESCRIPTION)

        if existing is None:
            problem = Problem(
                title=TITLE,
                description=DESCRIPTION,
                difficulty=DIFFICULTY,
                pattern=PATTERN,
                category=CATEGORY,
                source=SOURCE,
                description_source=DESCRIPTION_SOURCE,
                is_completed=False,
                comfort_level=0,
            )
            db.add(problem)
            db.flush()
            pid = int(problem.id)
            print(
                f"[INSERT] problems id={pid} title={TITLE!r} "
                f"len={len(DESCRIPTION)}"
            )
        else:
            pid = int(existing.id)
            normalized_old = _normalize(existing.description or "")
            if normalized_old == normalized_new:
                print(
                    f"[NOOP] problems id={pid} description "
                    f"semantically identical (len={len(DESCRIPTION)})"
                )
            else:
                old_len = len(existing.description or "")
                existing.description = DESCRIPTION
                existing.title = TITLE
                existing.difficulty = DIFFICULTY
                existing.category = CATEGORY
                existing.description_source = DESCRIPTION_SOURCE
                print(
                    f"[UPDATED] problems id={pid} old_len={old_len} "
                    f"new_len={len(DESCRIPTION)} "
                    f"delta={len(DESCRIPTION) - old_len:+d}"
                )

        existing_tag = (
            db.query(ProblemCompanyTag)
            .filter(
                ProblemCompanyTag.problem_id == pid,
                ProblemCompanyTag.company_id == company_id,
            )
            .first()
        )
        if existing_tag is None:
            tag = ProblemCompanyTag(
                problem_id=pid,
                company_id=company_id,
                relevance="core",
                source="manual",
                notes="Meta AI-Native Coding 2026-05-01 inventory",
            )
            db.add(tag)
            print(
                f"[INSERT] problem_company_tags problem_id={pid} "
                f"company_id={company_id} relevance=core"
            )
        else:
            print(
                f"[NOOP] problem_company_tags problem_id={pid} "
                f"company_id={company_id} already present"
            )

        db.commit()

        final = (
            db.query(Problem)
            .filter(Problem.source == SOURCE, Problem.pattern == PATTERN)
            .one()
        )
        print(
            f"[VERIFY] problems id={final.id} pattern={final.pattern!r} "
            f"source={final.source!r} desc_len="
            f"{len(final.description or '')}"
        )
        return int(final.id)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upsert_meta_anc_sparse_matrix_ops()
