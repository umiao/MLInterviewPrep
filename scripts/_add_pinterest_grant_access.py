"""Add Pinterest Grant Access / Permission Propagation custom problem to mle_prep.db.

Source: Pinterest coding round 2025-11 (non-LC, recurring).
Resources form a DAG (parent -> child). When a user is granted access to a
node, the grant propagates to ALL descendants. Support:
  - grant(user, node)
  - revoke(user, node)  (follow-up)
  - hasAccess(user, node)  -- true iff some ancestor-or-self of node was granted
                              to the user AND that grant was not revoked along
                              the relevant path.

Canonical lean answer: store grants per (user, node); for hasAccess, walk the
ancestor closure (BFS/DFS upward) and check any ancestor has a grant. With
caching and reverse-adjacency, amortized near-O(ancestors visited).

Idempotent: if a row with this title already exists, updates notes only.

Task: T-P1-400
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

TITLE = "Grant Access / Permission Propagation on a DAG"
SOURCE = "pinterest_interview,custom"
COMPANY_TAGS = json.dumps(["Pinterest"])
TAGS = json.dumps(["Graph", "DAG", "BFS", "DFS", "Design", "Permissions"])
PATTERN = "Ancestor-closure search on DAG (optionally memoized)"
DIFFICULTY = "medium"
CATEGORY = "algorithm"
PRIORITY = 2  # P1

DESCRIPTION = """\
[Pinterest coding 2025-11] A company organizes resources (folders, documents,
projects) as a directed acyclic graph where an edge parent -> child means the
child is contained under / inherits from the parent. An admin can grant a user
access to a single node; the grant PROPAGATES to every descendant of that node.

Design a PermissionSystem with:
  - addEdge(parent, child)      -- build the DAG (no cycles).
  - grant(user, node)           -- give user access at `node` (and all descendants).
  - hasAccess(user, node)       -- return True iff user has a grant at `node`
                                   OR at any ancestor-or-self of `node`.

Follow-ups discussed:
  (a) revoke(user, node) -- how propagation interacts with conflicting grants.
  (b) Multiple inheritance: a node may have many parents (true DAG, not tree).
  (c) Scale: millions of nodes, millions of grants, very skewed query pattern
      -- when to memoize vs when to precompute closure.
  (d) Groups: user -> group -> node grants (two-layer DAG).
"""

SOLUTION_TAG = "[Pinterest Grant-Access Canonical Solution]"

NOTES = SOLUTION_TAG + r"""

## Problem (Pinterest 2025-11)

Resources form a DAG. A grant at node `N` for user `U` gives `U` access to
`N` and every descendant of `N`. Implement:

- `addEdge(parent, child)`
- `grant(user, node)`
- `hasAccess(user, node) -> bool`

## Canonical Solution -- Upward Ancestor Walk (recommended)

**Storage**:
  - `children: node -> set[node]`  (forward edges, used only for traversals if
    you choose the downward strategy; not strictly needed by this solution).
  - `parents:  node -> set[node]`  (reverse edges, used by hasAccess).
  - `grants:   user -> set[node]`  (explicit grants only, not the closure).

**hasAccess(user, node)**: BFS/DFS upward from `node` through `parents`. Return
True the moment we hit any node in `grants[user]`. Otherwise return False after
exhausting the ancestor closure.

```python
from collections import defaultdict, deque

class PermissionSystem:
    def __init__(self) -> None:
        self.children: dict[str, set[str]] = defaultdict(set)
        self.parents:  dict[str, set[str]] = defaultdict(set)
        self.grants:   dict[str, set[str]] = defaultdict(set)

    def add_edge(self, parent: str, child: str) -> None:
        self.children[parent].add(child)
        self.parents[child].add(parent)

    def grant(self, user: str, node: str) -> None:
        self.grants[user].add(node)

    def has_access(self, user: str, node: str) -> bool:
        g = self.grants.get(user)
        if not g:
            return False
        if node in g:
            return True
        seen = {node}
        q = deque([node])
        while q:
            cur = q.popleft()
            for p in self.parents.get(cur, ()):
                if p in g:
                    return True
                if p not in seen:
                    seen.add(p)
                    q.append(p)
        return False
```

Complexity per `has_access`: O(A) where A is the size of the ancestor closure
of `node`. `grant` is O(1). `add_edge` is O(1).

## Alternative 1 -- Downward propagation on grant (materialize closure)

On `grant(user, node)`, BFS downward from `node` and insert every descendant
into `access[user]`. `has_access` becomes O(1) set lookup.

Pros: instant queries. Cons: every grant touches the whole descendant subtree;
revocation is painful because another grant at an intermediate ancestor may
still legitimately cover the same nodes. Memory blows up if many users each get
grants on large subtrees. Good choice ONLY if grants are rare and queries dominate.

## Alternative 2 -- Memoized upward walk

Cache `has_access(user, node)` results. Invalidate on any new `grant(user, *)`.
In steady state with grant-rare / query-heavy workloads, per-query cost
approaches O(1) after warm-up.

## Follow-up (a) -- Revocation

Naive "remove from grants" is wrong under propagation. If user was granted at
parent `P` and explicitly revoked at child `C`, but `C`'s sibling `D` should
still inherit from `P`, a pure set representation cannot express the "deny at
C" exception.

Two clean models:

1. **Explicit deny list**: add `denies: user -> set[node]`. `has_access`
   walks upward; if we hit a `deny` first we return False, if we hit a `grant`
   first we return True (shortest-ancestor-wins). This is the UNIX-style ACL
   closest-ancestor rule. Requires defining a tie-break (typically deny wins
   at the same node).

2. **Effective-access recomputation**: on revoke, recompute the user's access
   set from scratch using the grant+deny list. Simpler semantics, more work
   per revoke.

Clarify with the interviewer which semantics they want before coding -- this
is THE key design question and they often have a preference.

## Follow-up (b) -- True DAG (multiple parents)

The code above already handles multi-parent: `parents[c]` is a set, and the
BFS visits each ancestor once via `seen`. No change needed. Confirm with the
interviewer that "access via ANY path from any granted ancestor" is the rule
(almost always yes for permissions; rarely they want "access via ALL paths",
which is a different problem).

## Follow-up (c) -- Scale

| Pattern                       | Best strategy                          |
|-------------------------------|----------------------------------------|
| Grants rare, queries frequent | Alt 2 memoized upward, or Alt 1 closure|
| Grants frequent, queries rare | Canonical upward walk (no materialize) |
| Both frequent                 | Canonical + LRU cache, invalidate smart|
| Read-heavy + bounded depth    | Alt 1 + versioned snapshots            |

## Follow-up (d) -- Groups (two-layer DAG)

Add `group_members: group -> set[user]` and allow `grant(group, node)`.
`has_access(user, node)` becomes: user is granted directly, OR any group
containing the user is granted at an ancestor-or-self of `node`.

Model it as a single larger DAG: virtual edges `user -> group`. Then
`has_access(principal, node)` walks upward from `node` AND sideways from the
user through group membership. Both closures are small in practice; union
them lazily during the BFS.

## Edge Cases

1. Grant at `node` itself -- `has_access(user, node)` must return True (the
   `node in g` short-circuit handles this).
2. Node with no parents and no direct grant -- return False (loop exits with
   empty queue).
3. Multiple grants on the same ancestor chain -- idempotent under set storage.
4. Unknown node id in `has_access` -- return False (empty `parents` lookup).
5. Grants for a user with no grants yet -- `grants.get(user)` is None/empty,
   short-circuit to False.

## Chinese Notes (中文解析)

**题意**: 资源之间是有向无环图 (DAG), parent -> child 表示 child 继承 parent。
给用户在某节点 `N` 授权 = 该用户获得 `N` 及其**所有后代**的访问权限。实现:

- `addEdge(parent, child)` 建图
- `grant(user, node)` 记录一次授权
- `hasAccess(user, node)` 判断访问权

**核心观察**: 授权一次影响可能非常多的后代, 若在 `grant` 时把所有后代都写入访问
集合, 写放大严重且难以处理撤销。相反, 查询时从 `node` **反向 BFS/DFS 向上**走,
只要碰到任何 `grants[user]` 里的节点就说明有权, 最坏 O(祖先闭包大小)。

**为什么反向走更好**:
- 授权通常少, 查询多。但单次授权影响的**后代**可能非常多, 而单次查询对应的
  **祖先**一般较少 (树/DAG 的深度远小于节点总数)。
- 撤销语义 (follow-up a) 也更自然: 反向走时, 谁离 `node` 更近, 谁说了算, 天然
  契合 "就近祖先胜出" 的 ACL 语义。

**撤销 (follow-up a) 的正确做法**: 单纯从 grants 集合里删节点会误杀 -- 因为
父节点的另一次授权可能还在生效。正确的建模是引入显式 deny 集合, 查询时向上走
直到先命中 grant 或 deny; 或者在 revoke 时按 grant + deny 重新算一次有效集合。
这个 trade-off 一定要在面试时**主动澄清**, 直接套其中一种写法大概率被追问。

**真 DAG (多父) follow-up**: 上面的代码 `parents[c]` 用 `set`, BFS 配合 `seen`
已经天然处理多父, 不用改代码。只需口头确认 "任一路径上有祖先被授权就算有权",
这是 99% 场景的语义。

**组授权 (follow-up d)**: 再加一层 `group_members`, 查询时把 user 所属的 group
也并入 BFS 起点集合, 仍是一个 BFS。

**规模 (follow-up c)**:
- 授权少 + 查询多: `has_access` 做 memoize, 下次授权时把该 user 的缓存全清。
- 授权多 + 查询少: 直接向上走, 不预处理。
- 两者都多: 分桶缓存 + 按 user 级粒度失效。
- 树深度有界的场景 (比如 folder ≤ 20 层): 向上走代价可控, 永远 O(深度)。

**面试交付节奏**:
1. 画 DAG, 说清楚 "授权在 node, 所有后代继承";
2. 先问澄清: 有没有组? 要不要撤销? 多父 DAG 还是严格树?
3. 给出反向 BFS 方案, 说复杂度;
4. 讨论 grant 时预展开 vs 查询时反向走的 trade-off;
5. 写撤销时引入 deny 集合 + 最近祖先胜;
6. 收尾: 缓存 / 规模讨论。

## Self-Test (smoke)

```python
ps = PermissionSystem()
# Tree:
#       root
#      /    \
#    eng    mkt
#    / \     |
#   be  fe  blog
#   |
#  api
for p, c in [
    ("root", "eng"), ("root", "mkt"),
    ("eng", "be"), ("eng", "fe"), ("mkt", "blog"),
    ("be", "api"),
]:
    ps.add_edge(p, c)

ps.grant("alice", "eng")
assert ps.has_access("alice", "eng")   is True   # grant on self
assert ps.has_access("alice", "api")   is True   # deep descendant
assert ps.has_access("alice", "fe")    is True
assert ps.has_access("alice", "blog")  is False  # different subtree
assert ps.has_access("alice", "root")  is False  # ancestor, not descendant
assert ps.has_access("bob",   "api")   is False  # no grants at all

# Multi-parent (DAG): 'shared' has two parents; grant on either grants shared.
ps.add_edge("fe", "shared")
ps.add_edge("blog", "shared")
ps.grant("carol", "mkt")
assert ps.has_access("carol", "shared") is True   # via blog -> mkt
assert ps.has_access("carol", "fe")     is False  # fe's ancestors: eng, root
```
"""


def upsert() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id, notes FROM problems WHERE title = ? AND leetcode_id IS NULL",
        (TITLE,),
    )
    row = cur.fetchone()
    now = datetime.now(UTC).isoformat()

    if row is None:
        cur.execute("SELECT MAX(id) FROM problems")
        next_id = (cur.fetchone()[0] or 0) + 1
        cur.execute(
            """
            INSERT INTO problems (
                id, leetcode_id, title, url, difficulty, tags, pattern,
                category, source, company_tags, priority, is_completed,
                comfort_level, created_at, description, notes
            ) VALUES (?, NULL, ?, NULL, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)
            """,
            (
                next_id,
                TITLE,
                DIFFICULTY,
                TAGS,
                PATTERN,
                CATEGORY,
                SOURCE,
                COMPANY_TAGS,
                PRIORITY,
                now,
                DESCRIPTION,
                NOTES,
            ),
        )
        print(f"[INSERT] id={next_id} title={TITLE!r}")
    else:
        pid, existing_notes = row
        if existing_notes and SOLUTION_TAG in existing_notes:
            print(f"[SKIP] id={pid} already has canonical solution")
        else:
            merged = (existing_notes + "\n\n---\n\n" + NOTES) if existing_notes else NOTES
            cur.execute(
                "UPDATE problems SET notes = ?, description = ? WHERE id = ?",
                (merged, DESCRIPTION, pid),
            )
            print(f"[UPDATE] id={pid} notes appended")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    upsert()
