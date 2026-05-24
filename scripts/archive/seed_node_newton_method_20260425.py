"""Seed: Newton's Method & Numerical Iteration framework node + LC links.

Inserts a new depth=2 leaf under pillar7.calculus_optimization (id=40):

  pillar7.calculus_optimization.newton_method  (depth=2)

Source content is the user-authored 6-section thinking framework
(`从快速开方到牛顿法的思维框架`) plus a short interview-prep tail
(section 7: failure modes + answer script). Size deliberately kept under
sibling average (multivariable=6472, chain_rule=7031, convex_opt=7926)
because the topic scope is narrower; user explicit ask: "avoid over-expansion".

Also wires 2 LC problems to this node via problems.framework_node_id:
  - LC 69 Sqrt(x)               (problems.id=272) -- canonical entry point
  - LC 367 Valid Perfect Square (problems.id=655) -- methodology mirror

Idempotent:
  1. Node insert: SKIP if path+title match; CONFLICT if title differs.
  2. Description: writes once when row does not yet exist; on second run
     the row already matches and no UPDATE happens.
  3. LC FK: SKIP if problems.framework_node_id already points at the new
     node; UPDATE if currently NULL; CONFLICT if pointing elsewhere.

Ad-hoc hotfix-style task (no task_db ticket): user-authored content drop
on 2026-04-25.

Usage:
    python scripts/seed_node_newton_method_20260425.py [--dry-run] [--db PATH]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "data" / "mle_prep.db"

PARENT_PATH = "pillar7.calculus_optimization"
NEW_PATH = f"{PARENT_PATH}.newton_method"
NEW_TITLE = "Newton's Method & Numerical Iteration (牛顿法与数值迭代)"
NEW_DEPTH = 2
NEW_IMPORTANCE = 0.7

LINKED_LC_PROBLEMS = (
    # (problem_id, lc_number, title for log only)
    (272, 69,  "Sqrt(x)"),
    (655, 367, "Valid Perfect Square"),
)

DESCRIPTION = """# 从快速开方到牛顿法的思维框架

## 一、起点：开方为什么不该用二分

二分搜索（**Binary Search**）每步只多 1 bit 精度，对 double（53 bit 尾数）要 50+ 步。问题在于它没用到函数的任何分析性质，只用了 "单调"。光滑函数应该有更好的办法——我们手里有 $f$ 和 $f'$ 的解析形式，没理由只挑大小。

## 二、牛顿法的推导：一阶 Taylor 展开

要解 $f(x) = 0$。在当前点 $x_n$ 做一阶 **Taylor expansion**：
$$f(x) \\approx f(x_n) + f'(x_n)(x - x_n)$$
真实零点未知，但切线的零点可以直接解出。令上式为 0：
$$x_{n+1} = x_n - \\frac{f(x_n)}{f'(x_n)}$$
几何意义：在 $(x_n, f(x_n))$ 画切线，取切线与 x 轴的交点作为新估计。

代入开方 $\\sqrt a$，取 $f(x) = x^2 - a$：
$$x_{n+1} = \\frac{1}{2}\\left(x_n + \\frac{a}{x_n}\\right) \\qquad (\\text{Heron 公式})$$

这是**二阶收敛**（**quadratic convergence**）——每步精度位数翻倍。直观看：$x_n$ 偏大则 $a/x_n$ 偏小，取算术平均向真值靠拢。任意正初值都收敛（**AM-GM** 保证从第一步起 $\\geq \\sqrt a$，之后单调下降），但好初值能省几步。

## 三、和相关思想的关系

- **Taylor expansion**：牛顿法就是用一阶 Taylor。用二阶就得到三阶收敛的 **Halley's method**。阶数越高常数越大，工程上一阶通常够用。
- **Gradient Descent**：形式相似但目标不同——梯度下降找极小值、步长人定；牛顿法找零点、"步长" $1/f'(x_n)$ 由函数本身提供。最小化 $g$ 等价于解 $g'(x)=0$，对它套牛顿就是优化里的 **Newton's method for optimization**（用 **Hessian** 作自适应步长）。这也解释了为什么牛顿法在 ML 优化里被称作 "二阶方法"。

## 四、推广到一般问题：反函数策略

要算 $y = g(a)$，若 $g$ 难算而反函数 $f = g^{-1}$ 易算，**不要逼近 $g$，去解方程 $f(y) = a$**。

- **$\\sqrt a$**：解 $y^2 = a$。$f, f'$ 都是乘法，硬件最便宜的运算。
- **$\\log a$**：解 $e^y = a$。把难算的 log 换成易算的 exp，且 $f' = f$ 可复用，每步基本 "免费" 拿到导数值。
- **矩阵求逆（matrix inversion）**：迭代 $X_{n+1} = X_n(2I - A X_n)$，每步两次矩阵乘代替一次 $O(n^3)$ 求逆，在并行硬件上反而更快。

适用条件：(1) 反函数便宜；(2) 导数好算（最好能复用 $f$ 的值）；(3) 有便宜的初值来源（**浮点位表示**是金矿——直接位运算就能拿到很好的 $\\sqrt{}$ 初值，著名例子 Quake III 的 fast inverse sqrt）；(4) 单步代价低于直接求解。

## 五、与多项式逼近的分工

不是对立而是互补，构成现代库函数（**libm**）的两层结构：

1. **Range reduction（范围归约）**：用代数恒等式把自变量压到小区间。例如 $\\log a = \\log m + e \\cdot \\log 2$，先把 $a$ 拆成 $m \\cdot 2^e$，只需在 $m \\in [1,2)$ 上算 $\\log m$。
2. **核心逼近**：小区间上用 **minimax polynomial**（流水线友好、定步数、无分支）或 Newton 迭代（任意精度、有自然反函数时）。

## 六、方法论收束

**用便宜的方向逼近昂贵的方向**。问 $g$ 的反函数是不是更便宜——是，就改写成解 $f(y) = a$ 让牛顿法处理。再问能否先用代数结构把问题归约到小区间——能，就先归约再迭代。

牛顿法只是这条原则最常见的实现。同一精神也出现在 **EM algorithm**（易算下界代替难算似然）、**dual methods**（对偶问题代替原问题）等地方——都是同一种算法品味。

## 七、面试串讲与失败模式

**收敛性陷阱**：牛顿法**不保证全局收敛**——若初值落在 $f'(x) = 0$ 附近，或 $f$ 不光滑、有多根、震荡区域，迭代可能发散或在两根间反弹。开方之所以 "任意正初值都收敛"，是因为 $f(x)=x^2-a$ 在 $x>0$ 上严格凸 + $f'>0$，"二阶收敛 + AM-GM 单调下降" 三件套同时成立——这是特例，不是通则。

工程实现常用 "**hybrid bisection-Newton**"：先二分到候选区间确保不发散，再牛顿精修。Brent 方法是这条思路的成熟实现。

**面试答题脚本**：(1) 先报二分基线 + $O(\\log(1/\\epsilon))$ 复杂度；(2) 主动指出 "二分没用 $f$ 的解析信息，只用了单调性"，引出 "是否能用斜率"；(3) 推导牛顿公式 + 给出 Heron 形式 + 5-7 步内收敛到 double 精度；(4) 给收敛阶 + 至少一种失败模式（多根 / 不光滑 / 初值差）；(5) 若被追问，扩到反函数策略（log / 矩阵求逆）展示视野。

**LC 串讲入口**：
- LC 69 Sqrt(x) 是 Newton 思路最标准的展示题——二分要 30+ 次，Newton 5-7 步整数精度即收敛。
- LC 367 Valid Perfect Square 同型，用 Newton 展现 "主动用 $f'$ 信息" 的 L5 signal 而非默认二分。
"""


def upsert_node(
    conn: sqlite3.Connection,
    *,
    parent_id: int,
    path: str,
    depth: int,
    title: str,
    description: str,
    importance: float,
) -> tuple[str, int]:
    """Insert framework node if absent; SKIP if exact match; refuse on conflict.

    Args:
        conn: Open SQLite connection.
        parent_id: framework_nodes.id of the parent.
        path: Dot-delimited unique path (e.g. ``pillar7.calculus_optimization.newton_method``).
        depth: Hierarchy depth (root=0).
        title: Display title (must be stable across reruns).
        description: Markdown body for the node drawer.
        importance: Float in [0,1]; higher = more interview-relevant.

    Returns:
        Tuple ``(action, node_id)`` where action is ``"INSERTED"`` or
        ``"SKIPPED"``.

    Raises:
        RuntimeError: When ``path`` exists with a different title.
    """
    existing = conn.execute(
        "SELECT id, title FROM framework_nodes WHERE path = ?", (path,)
    ).fetchone()
    if existing is not None:
        node_id, existing_title = existing
        if existing_title != title:
            raise RuntimeError(
                f"[CONFLICT] path={path!r} exists with title={existing_title!r}, "
                f"refusing to overwrite with {title!r}"
            )
        return "SKIPPED", node_id

    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, depth, title, description,
         importance, "P1", "not_started", 0.0),
    )
    return "INSERTED", cur.lastrowid


def link_problem(
    conn: sqlite3.Connection,
    *,
    problem_id: int,
    target_node_id: int,
    log_label: str,
) -> str:
    """Set problems.framework_node_id idempotently.

    Returns one of: ``"LINKED"`` (was NULL, now set), ``"SKIPPED"`` (already
    pointed at target), ``"CONFLICT"`` (points at a different node, manual
    review needed).
    """
    row = conn.execute(
        "SELECT framework_node_id FROM problems WHERE id = ?", (problem_id,)
    ).fetchone()
    if row is None:
        raise RuntimeError(f"problems.id={problem_id} not found ({log_label})")
    current = row[0]
    if current == target_node_id:
        return "SKIPPED"
    if current is not None:
        return "CONFLICT"
    conn.execute(
        "UPDATE problems SET framework_node_id = ? WHERE id = ?",
        (target_node_id, problem_id),
    )
    return "LINKED"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Roll back at the end so DB is untouched.")
    parser.add_argument("--db", default=str(DEFAULT_DB),
                        help=f"Path to SQLite DB (default: {DEFAULT_DB})")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[FAIL] DB not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    try:
        parent = conn.execute(
            "SELECT id FROM framework_nodes WHERE path = ?", (PARENT_PATH,)
        ).fetchone()
        if parent is None:
            raise RuntimeError(
                f"Parent path {PARENT_PATH!r} missing -- expected pillar7 to exist"
            )
        parent_id = parent[0]

        action, node_id = upsert_node(
            conn,
            parent_id=parent_id,
            path=NEW_PATH,
            depth=NEW_DEPTH,
            title=NEW_TITLE,
            description=DESCRIPTION,
            importance=NEW_IMPORTANCE,
        )
        print(f"[{action}] node id={node_id} path={NEW_PATH} "
              f"len(desc)={len(DESCRIPTION)}")

        # Wire LC problems
        link_counts = {"LINKED": 0, "SKIPPED": 0, "CONFLICT": 0}
        for problem_id, lc_number, title in LINKED_LC_PROBLEMS:
            result = link_problem(
                conn,
                problem_id=problem_id,
                target_node_id=node_id,
                log_label=f"LC {lc_number} {title}",
            )
            link_counts[result] += 1
            print(f"[{result}] LC {lc_number:<4} ({title}) -> framework_node id={node_id}")

        if args.dry_run:
            conn.rollback()
            print("[DRY-RUN] rolled back")
        else:
            conn.commit()
            print("[COMMIT] committed")

        print(f"[SUMMARY] node={action} "
              f"links_linked={link_counts['LINKED']} "
              f"links_skipped={link_counts['SKIPPED']} "
              f"links_conflict={link_counts['CONFLICT']}")
        if link_counts["CONFLICT"] > 0:
            print("[WARN] one or more LC problems already point at a different "
                  "framework_node -- manual reconciliation needed")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
