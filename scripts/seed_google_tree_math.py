"""Seed Google coding prep for T-P2-210: Tree/Trie level-order + Math expressions.

(1) LC 102 / 103 / 107 level-order family + Trie BFS-level traversal variant.
(2) Math expression: LC 770 Basic Calculator IV (poly + vars) and LC 772
    Basic Calculator III (mul/div + parens). LC 224 already has full notes
    so we skip it (cross-referenced from 772).

Idempotent: re-running updates in place via marked sections. Chinese prose;
code + complexity English per feedback_lc_notes_chinese.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SOURCE_BADGE = "Google 2026-04-17 prep"
MARKER = "## Google 2026-04-17 prep"


def merge_json_tag(existing: str | None, tag: str) -> str:
    tags = json.loads(existing) if existing else []
    if tag not in tags:
        tags.append(tag)
    return json.dumps(tags, ensure_ascii=False)


def merge_source(existing: str | None, new: str) -> str:
    if not existing:
        return new
    parts = [s.strip() for s in existing.split(",") if s.strip()]
    if new not in parts:
        parts.append(new)
    return ", ".join(parts)


def append_notes(existing: str | None, addendum: str) -> str:
    if existing and MARKER in existing:
        idx = existing.index(MARKER)
        head = existing[:idx].rstrip()
        if head.endswith("---"):
            head = head[:-3].rstrip()
        if not head:
            return addendum
        return head + "\n\n---\n\n" + addendum
    if not existing:
        return addendum
    return existing.rstrip() + "\n\n---\n\n" + addendum


# ---------------------------------------------------------------------------
# LC 102 / 103 / 107 shared addendum: level order family + Trie BFS variant
# ---------------------------------------------------------------------------

LEVEL_ORDER_NOTES = MARKER + """: 层序遍历家族 + Trie BFS 变体

### 模板：一次 BFS 分层

核心是"**当前层的 size 先锁定**"，这样可以在一次 while 里吐出一层完整的
节点列表：

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    q = deque([root])
    out = []
    while q:
        n = len(q)
        level = []
        for _ in range(n):
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.append(level)
    return out
```

**复杂度**：时间 $O(N)$，空间 $O(W)$，其中 $W$ 是最大层宽（完全二叉树 $W=N/2$）。

### LC 102 (原题)

直接套上面模板即可，返回 `out`。

### LC 103 Zigzag

两种常用写法：
1. **布尔翻转 + deque 反转**：维护 `ltr: bool`，每层结束后 `ltr = not ltr`，
   if not ltr: `level.reverse()`。代码最短。
2. **双端插入 appendleft**：`level` 本身用 deque；偶数层 `appendleft`，
   奇数层 `append`。避免一次 reverse 的 $O(W)$，但常数在 Python 里差不多。

```python
from collections import deque
def zigzag(root):
    if not root: return []
    q = deque([root]); out = []; ltr = True
    while q:
        n = len(q); level = deque()
        for _ in range(n):
            node = q.popleft()
            (level.append if ltr else level.appendleft)(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.append(list(level)); ltr = not ltr
    return out
```

### LC 107 Bottom-up level order

最快写法：正常层序 + `return out[::-1]`。
若严格追求 **O(1) 额外翻转成本**：用 `collections.deque` + `appendleft(level)`，
一次性把每层插到前面。两种写法渐进相同。

### 与 DFS 的等价

层序也可用递归 DFS + 层深度参数完成：维护 `out: list[list[int]]`，递归中
`if depth == len(out): out.append([]); out[depth].append(node.val)`。
**面试时先给 BFS 版本**——更直观、也自然承接"按层输出"的后续问题
（LC 199 右视图、LC 515 每层最大值、LC 637 每层均值）。

### Trie 的 BFS 层序变体

Trie 是多叉树（children 按 26 字母或 gid 建索引），层序一样套模板，只是
子节点枚举改成遍历 `children.values()`：

```python
def trie_level_order(root):
    q = deque([root]); out = []
    while q:
        n = len(q); level = []
        for _ in range(n):
            node = q.popleft()
            level.append(node.val if hasattr(node,'val') else None)
            for child in node.children.values():
                q.append(child)
        out.append(level)
    return out
```

**场景**：
- **按前缀长度分层展示词典**（debug / 可视化）。
- **Bloomlier 查询**：给定 query，BFS 收集距离 ≤ k 的近邻节点（编辑距离 trie）。
- **同族题 LC 1032 Stream of Characters**：反向 trie + 在线流式扫描；层序
  用于预处理 fail-link（Aho-Corasick 的 BFS 构建）。

### 易错点对照

| 错误 | 问题 |
|------|------|
| while q: for node in q: ... q.clear() | 一次性扫整个队列但还在往 q 加 children，混层 |
| 没锁 n = len(q) | 本层加的新孩子会被当作本层节点 |
| DFS 返回时忘 depth | 深度误当成层号，会错分层 |
| Zigzag 用 reverse() 原地翻转 vs 返回值 | `list.reverse()` 返回 None，容易 bug |

### 复杂度汇总

| 题 | 时间 | 空间 |
|----|------|------|
| 102 / 103 / 107 | $O(N)$ | $O(W)$ |
| Trie 层序 | $O(V+E)$ = $O(\\Sigma L)$ | $O(W_{\\text{trie}})$ |

其中 $\\Sigma L$ 是字典总字符数。
"""


# ---------------------------------------------------------------------------
# LC 772 Basic Calculator III — mul/div + parens
# ---------------------------------------------------------------------------

LC772_NOTES = MARKER + """: Basic Calculator III（mul/div + parens）

### 与 LC 224 / 227 的关系

| 题 | 支持运算 | 核心技巧 |
|----|---------|---------|
| 224 | `+ - ( )` | 栈存符号，遇 `(` 压栈，遇 `)` 弹栈 |
| 227 | `+ - * /` 无括号 | prev + cur 合并，乘除立即算 |
| 772 | `+ - * / ( )` 全部 | 224 递归 + 227 合并；两层叠加 |

### 主解：递归下降 + 栈合并

遇 `(` 就把剩余串丢给递归；返回时把括号值当一个数继续 227 的合并逻辑。

```python
def calculate(s: str) -> int:
    s = s.replace(" ", "")
    i = 0
    def helper() -> int:
        nonlocal i
        stack, num, op = [], 0, '+'
        while i < len(s):
            c = s[i]
            if c.isdigit():
                num = num*10 + int(c)
            if c == '(':
                i += 1
                num = helper()
            if (not c.isdigit() and c != '(') or i == len(s)-1:
                if op == '+': stack.append(num)
                elif op == '-': stack.append(-num)
                elif op == '*': stack.append(stack.pop()*num)
                elif op == '/': stack.append(int(stack.pop()/num))  # 向 0 取整
                num, op = 0, c
            i += 1
            if c == ')': break
        return sum(stack)
    return helper()
```

**关键陷阱**：
1. Python `//` 对负数向下取整，LC 要求**向 0 取整** -> 用 `int(a/b)` 或
   `a // b if a*b >= 0 else -(-a // b)`。
2. 单目负号 `-(3+4)`：预处理把行首或 `(` 后的 `-` 换成 `0-`，或在 helper
   里把 `stack` 初始压 0。
3. 长串数字要 `num = num*10 + int(c)` 累加，不能只看当前字符。
4. `i` 必须是共享指针（`nonlocal`），让递归返回后主调知道吃到哪里了。

### 复杂度

- 时间 $O(n)$，每个字符被访问常数次（helper 深度有限）。
- 空间 $O(n)$（递归栈 + 合并栈，最坏是全嵌套括号）。

### 替代：Shunting-yard + 后缀求值

Dijkstra 双栈法：一个 operand 栈、一个 operator 栈，按优先级收敛。
LC 224/227/772 可用**统一模板**实现；代码略长但可扩展到 LC 770（符号）。
面试若时间紧先给递归版，再口头补 shunting-yard。

### Follow-ups

- 加 `^` 幂运算 -> 改优先级表，右结合（$2^{3^2}=2^9$）。
- 支持变量赋值 `a=3+4; b=a*2` -> 加符号表。
- 浮点 + 科学计数 -> 词法扫描独立成 tokenizer。
- **LC 770 Basic Calculator IV** = 772 再加"变量未知"，answer 变成
  多项式展开（见 770 笔记）。
"""


# ---------------------------------------------------------------------------
# LC 770 Basic Calculator IV — polynomial over symbolic vars
# ---------------------------------------------------------------------------

LC770_TITLE = "Basic Calculator IV"
LC770_URL = "https://leetcode.com/problems/basic-calculator-iv/"
LC770_DESC = """Evaluate an expression with `+ - * ( )` plus free variables
and a partial substitution mapping. Return the simplified polynomial as
a list of terms sorted by (-degree, lex).

Example:
- expr = "e + 8 - a + 5", evalvars = ["e"], evalnums = [1]
  -> ["-1*a", "14"]
- expr = "(e + 8) * (e - 8)", evalvars = [], evalnums = []
  -> ["1*e*e", "-64"]

Follow-up chain:
(A) Add `/` division -> rational polynomials, no longer term-list form.
(B) Evaluate many different substitutions -> precompute Poly once,
    substitute lazily.
(C) Very long expressions -> tokenizer + shunting-yard beats recursion.
"""

LC770_NOTES = """## LC 770 Basic Calculator IV (Google 2026-04-17 prep)

### 模型：多项式 as Counter[tuple[str,...]]

一个项是**变量的排序 tuple** + 一个整数系数。整张多项式是
`Counter[tuple[str,...], int]`：

- 常数 5 -> `{(): 5}`
- `3*a*b` -> `{('a','b'): 3}`
- `a*a - 4` -> `{('a','a'): 1, (): -4}`

为什么排序：`a*b` 与 `b*a` 必须合并，`sorted(vars)` 作为 key 保证唯一。

### 算子

```python
from collections import Counter
from itertools import product as iproduct

Poly = Counter  # alias

def poly_add(p, q, sign=1):
    out = Counter(p)
    for k, v in q.items():
        out[k] += sign*v
        if out[k] == 0: del out[k]
    return out

def poly_mul(p, q):
    out = Counter()
    for (kp, vp), (kq, vq) in iproduct(p.items(), q.items()):
        key = tuple(sorted(kp + kq))
        out[key] += vp*vq
    return out

def poly_eval(p, env):
    # env: dict[str, int]; 代入已知变量，保留未知
    out = Counter()
    for vars_tuple, coef in p.items():
        unknown = []
        c = coef
        for v in vars_tuple:
            if v in env: c *= env[v]
            else: unknown.append(v)
        key = tuple(sorted(unknown))
        out[key] += c
        if out[key] == 0: del out[key]
    return out
```

### 解析：递归下降 + shunting-yard 双栈都可

**递归**最短：和 LC 772 同骨架，只是 `num` 从 int 升级成 Poly。
单 token 构造 Poly 的规则：
- 数字 token `"5"` -> `{(): 5}`
- 变量 token `"a"` -> `{('a',): 1}`（若 `a in env` 则直接变成 `{(): env[a]}`）

`+ -` 用 `poly_add(p, q, +1/-1)`；`*` 用 `poly_mul`；`(` 递归。

### 输出格式

把最终 Poly 按要求排序：

```python
def format_poly(p):
    items = [(vars_tuple, coef) for vars_tuple, coef in p.items() if coef]
    items.sort(key=lambda t: (-len(t[0]), t[0]))  # 先按次数降序，再字典序
    out = []
    for vars_tuple, coef in items:
        if vars_tuple:
            out.append("*".join([str(coef), *vars_tuple]))
        else:
            out.append(str(coef))
    return out
```

### 复杂度

设 tokens 数 $T$，最终多项式项数 $M$，最高次数 $D$。
- `poly_add`：$O(M)$。
- `poly_mul`：$O(M_p \\cdot M_q)$，每次合并还要 `sorted` 一个长度 $D$ 的 tuple，
  实际 $O(M_p M_q \\cdot D \\log D)$。
- 整体对嵌套乘法可爆到 $O(M^2 D \\log D)$；LC 数据范围允许。

### 易错点

| 错误 | 问题 |
|------|------|
| 用 `dict` 不删零项 | 输出时多了 "0*a" 垃圾项 |
| 变量 tuple 未排序 | `(a,b)` 与 `(b,a)` 成两个项无法合并 |
| 代入 env 后没重排 | `a*b` where `a=2` -> key 应变成 `(b,)` |
| 单目负号漏处理 | `-(a+1)` 结果错，参照 772 的 "(0-" 预处理 |
| 整数溢出 | Python 无忧；C++ 需 int64 |

### Follow-ups

- **(A) `/` 除法**：结果是有理函数，term-list 不够，需 `(分子 Poly, 分母 Poly)`
  + gcd。面试通常只问"能否扩展"，口述即可。
- **(B) 多次 eval**：先解析一次成 Poly，每次只跑 `poly_eval(env)` 即 $O(M \\cdot D)$。
- **(C) 超长表达式**：改 shunting-yard，递归深度限制消失。

### 交叉引用

- **LC 224/227/772**：同系列，数字不带变量。
- **LC 282 Expression Add Operators**：插运算符后枚举，不走 Poly 路。
- **LC 150 Evaluate RPN**：若输入已是后缀表达式，直接栈 + Poly 运算符。
"""


# ---------------------------------------------------------------------------
# LC 103 / 107 standalone notes (short since they share 102 template)
# ---------------------------------------------------------------------------

LC103_NOTES = MARKER + """: Zigzag Level Order

见 LC 102 笔记的"LC 103 Zigzag" 小节。核心：BFS 模板基础上每层加一个
`ltr` 布尔翻转；要么 `level.reverse()`，要么用 `deque` 两头插。

```python
from collections import deque
def zigzagLevelOrder(root):
    if not root: return []
    q = deque([root]); out = []; ltr = True
    while q:
        n = len(q); level = deque()
        for _ in range(n):
            node = q.popleft()
            (level.append if ltr else level.appendleft)(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.append(list(level)); ltr = not ltr
    return out
```

**复杂度** $O(N)$ 时间 / $O(W)$ 空间。
"""


LC107_NOTES = MARKER + """: Level Order II (bottom-up)

标准 BFS 完成后反转整体：`return out[::-1]`。或用 `collections.deque`
+ `appendleft(level)` 一次插到前面。两者渐进相同。

```python
def levelOrderBottom(root):
    if not root: return []
    from collections import deque
    q = deque([root]); out = deque()
    while q:
        n = len(q); level = []
        for _ in range(n):
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.appendleft(level)
    return list(out)
```

**复杂度** $O(N)$ 时间 / $O(W)$ 空间。与 LC 102 完全同源，注意面试考官
可能用 107 作热身题再跳到 103 或 199。
"""


def update_lc(cur: sqlite3.Cursor, lc_id: int, new_notes: str, tag: str) -> None:
    cur.execute(
        "SELECT id, notes, tags, source FROM problems WHERE leetcode_id=?",
        (lc_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"LC {lc_id} missing from DB")
    pid, notes, tags, source = row
    merged_notes = append_notes(notes, new_notes)
    merged_tags = merge_json_tag(tags, tag)
    merged_source = merge_source(source, SOURCE_BADGE)
    cur.execute(
        "UPDATE problems SET notes=?, tags=?, source=? WHERE id=?",
        (merged_notes, merged_tags, merged_source, pid),
    )
    print(f"  LC {lc_id}: notes {len(notes or '')} -> {len(merged_notes)}")


def upsert_lc770(cur: sqlite3.Cursor) -> int:
    cur.execute("SELECT id, notes FROM problems WHERE leetcode_id=770")
    row = cur.fetchone()
    now = datetime.now().isoformat(timespec="seconds")
    tags_json = json.dumps(
        ["stack", "recursion", "polynomial", "math", "string"],
        ensure_ascii=False,
    )
    company_json = json.dumps(["Google"], ensure_ascii=False)
    if row is not None:
        pid = row[0]
        cur.execute(
            "UPDATE problems SET title=?, url=?, description=?, notes=?, tags=?, "
            "pattern=?, category=?, company_tags=?, source=?, difficulty=?, priority=? "
            "WHERE id=?",
            (LC770_TITLE, LC770_URL, LC770_DESC, LC770_NOTES, tags_json,
             "expression-parser", "algorithm", company_json, SOURCE_BADGE,
             "hard", 1, pid),
        )
        print(f"  LC 770: UPDATE pid={pid} notes_len={len(LC770_NOTES)}")
        return pid
    cur.execute(
        "INSERT INTO problems (leetcode_id, title, url, description, notes, tags, pattern, "
        "category, company_tags, source, difficulty, priority, is_completed, created_at) "
        "VALUES (770, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (LC770_TITLE, LC770_URL, LC770_DESC, LC770_NOTES, tags_json,
         "expression-parser", "algorithm", company_json, SOURCE_BADGE,
         "hard", 1, now),
    )
    pid = cur.lastrowid
    print(f"  LC 770: INSERT pid={pid} notes_len={len(LC770_NOTES)}")
    return pid


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    print("updating LC 102 / 103 / 107 / 772 / 770...")
    update_lc(cur, 102, LEVEL_ORDER_NOTES, "bfs")
    update_lc(cur, 103, LC103_NOTES, "bfs")
    update_lc(cur, 107, LC107_NOTES, "bfs")
    update_lc(cur, 772, LC772_NOTES, "stack")
    upsert_lc770(cur)
    conn.commit()
    conn.close()
    print("done")


if __name__ == "__main__":
    main()
