"""One-shot: write LC 1110 solution notes into problems.notes."""
import sqlite3

NOTES = r'''## LC 1110 - Delete Nodes And Return Forest (DFS + "is_root" Flag)

> Pinterest must-do list. See [Pinterest Prep Notes](../docs/pinterest_recruiter_call_prep.md#pinterest-lc-%E5%BF%85%E5%88%B7%E9%A2%98%E5%88%97%E8%A1%A8-14-%E9%A2%98)

### Problem Recap
Given a binary tree and a `to_delete` list of values. Delete those nodes. The remaining nodes form a forest. Return the list of roots of each tree in the forest (each unique tree listed once, root order doesn't matter).

### Key Insight: Who Becomes a Forest Root?

A node becomes a forest root **iff**:
1. It is NOT in `to_delete`, AND
2. Its parent IS in `to_delete` (or it was the original tree root).

So we need to pass down one bit of info during DFS: "is my parent deleted?" (equivalently "am I a potential root?"). That's the `is_root` flag.

### Canonical Solution

```python
class Solution:
    def delNodes(self, root: "TreeNode", to_delete: list[int]) -> list["TreeNode"]:
        to_delete = set(to_delete)
        forest = []

        def dfs(node: "TreeNode | None", is_root: bool) -> "TreeNode | None":
            if node is None:
                return None
            deleted = node.val in to_delete
            if is_root and not deleted:
                forest.append(node)
            # Children's "is_root" = whether THIS node is deleted
            node.left = dfs(node.left, deleted)
            node.right = dfs(node.right, deleted)
            # Return None if this node is deleted (parent will unlink)
            return None if deleted else node

        dfs(root, True)
        return forest
```

**Why this is clean**:
- **Single pass**, O(n) time, O(h) space (recursion).
- Unlinking is handled by the return value: parent writes `node.left = dfs(...)`, which is `None` if the child was deleted.
- The `is_root` flag elegantly captures both "original root" and "parent was deleted" cases.

### Your Solution: Review

Your post-order approach is **correct**. Walkthrough of your logic:
1. Recurse into subtrees first.
2. If current node is in `to_delete`, append its non-deleted children to `ret`.
3. Unlink deleted children (`root.left = None` / `root.right = None`).
4. After the traversal, check the original root separately.

**What's awkward about it**:

| Issue | Your code | Canonical |
|-------|-----------|-----------|
| Special-case original root | `if root.val not in to_delete: ret.append(root)` after traversal | Handled uniformly via `is_root=True` initial call |
| Two passes over children | First check deletion + append to `ret`, then separately nullify | Single return-based unlinking |
| Double `in to_delete` check | Checked 4+ times per node (child-check for ret + child-check for nullify) | Once per node |
| Rebuilding parent name `root` | You shadow the outer `root` inside `traverse(root)`, then use it outside -- works but confusing | Use `node` inside, `root` as outer handle |

**Your code is O(n) but with a constant factor penalty** (redundant set lookups and two-phase child handling). Functionally fine, stylistically noisier than needed.

### "Carry state down" vs "handle on the way up"

This problem showcases a general recursion design principle:

- Your version: do all the work **on the way up** (post-order). Requires reasoning about each node's parent AFTER the fact (hence the special case for root).
- Canonical version: carry state **down** via `is_root` argument, return unlinking info **up**. Most tree-DFS problems are cleaner this way when the decision depends on ancestor state.

If in an interview the question includes "parent constraints" (e.g., "count nodes whose parent satisfies X"), immediately consider passing a parent-state argument down rather than trying to peek back up.

### Traps & Edge Cases

1. **`to_delete` is a list, convert to set**: O(1) lookups. You do this correctly.
2. **Original root may be deleted**: your separate `if root.val not in to_delete` check handles it; the canonical version handles it via `is_root=True`.
3. **Empty tree (`root is None`)**: canonical handles via initial None check; your code crashes on `root.val` at the final line. Small bug: add `if root is None: return []` at the top.
4. **Values are unique**: problem guarantees this (1 <= val <= 1000 and all distinct). So matching by value is safe. If values weren't unique, you'd need to match by node identity.

### Complexity

- **Time**: O(n + k) where n = tree size, k = len(to_delete). Building the set is O(k); traversal is O(n) with O(1) membership checks.
- **Space**: O(h + k) where h = tree height (recursion stack) + set.

### Pattern Recognition

Cue: "delete nodes from a tree, return components/forest" -> DFS with `is_root` flag, return `None` to signal unlink.

Related:
- LC 814 Binary Tree Pruning (same "return None to unlink" pattern)
- LC 669 Trim a BST (same return-based unlink, BST-aware)
- LC 1325 Delete Leaves With a Given Value (post-order deletion)

### Summary

Your solution works but the canonical `dfs(node, is_root)` with return-based unlinking is noticeably cleaner:
- One pass, no post-hoc special case for the original root
- Return `None` from the recursive call to let parents unlink automatically
- One membership check per node instead of 2-4

Commit the canonical form to muscle memory -- the `is_root`/`is_X` flag-carrying pattern generalizes to many ancestor-dependent tree problems.
'''

conn = sqlite3.connect("data/mle_prep.db")
conn.execute("UPDATE problems SET notes = ? WHERE leetcode_id = 1110", (NOTES,))
conn.commit()
print(f"[OK] LC 1110 notes updated ({len(NOTES)} chars)")
conn.close()
