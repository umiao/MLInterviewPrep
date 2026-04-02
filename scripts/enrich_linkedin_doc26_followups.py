"""Add missing follow-ups to doc#26 questions that were already enriched.

Task: T-P0-262 (supplement)
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# Each entry: (unique_before_string, follow_up_text_to_insert_before_separator)
# We insert follow-ups BEFORE the "---" line that separates questions.

FOLLOWUP_INSERTIONS = [
    # Q2 - Course Schedule
    (
        "- **Key Technique**: Kahn's Algorithm (BFS topological sort) -- 适合检测 DAG (Directed Acyclic Graph，有向无环图) 和输出排序\n\n---\n\n### Q3.",
        "- **Key Technique**: Kahn's Algorithm (BFS topological sort) -- 适合检测 DAG (Directed Acyclic Graph，有向无环图) 和输出排序\n\n**Follow-ups**:\n- 如果需要返回所有可能的拓扑排序? -> 回溯法枚举所有入度为 0 的选择\n- 如何检测具体是哪些课程构成了环? -> DFS 染色法 (white/gray/black)\n- 并行执行: 最少需要几个学期? -> LC 1136, 分层 BFS\n\n---\n\n### Q3.",
    ),
    # Q3 - Find Leaves of Binary Tree
    (
        "每个节点的 \"removal round\" 等于该节点在树中的高度（叶子高度为 0）。无需真正删除节点，只需 DFS 计算每个节点的 height 并按 height 分组。\n\n```python",
        "每个节点的 \"removal round\" 等于该节点在树中的高度（叶子高度为 0）。无需真正删除节点，只需 DFS 计算每个节点的 height 并按 height 分组。\n\n```python",
    ),
    # Q4 - Centroid Decomposition
    (
        "分治树深度 O(log n)，支持高效路径查询。\n\n---\n\n### Q5.",
        "分治树深度 O(log n)，支持高效路径查询。\n\n**Follow-ups**:\n- 如果树是动态的 (可以加边)? -> Link-Cut Tree\n- 如何处理带权边? -> 在 BFS/DFS 预处理时记录距离\n\n---\n\n### Q5.",
    ),
    # Q5 - Trie
    (
        "Trie 剪枝使实际效率远高于最坏情况。\n\n---\n\n### Q6.",
        "Trie 剪枝使实际效率远高于最坏情况。\n\n**Follow-ups**:\n- 如何实现 autocomplete (返回所有匹配前缀的单词)? -> DFS 从前缀节点遍历所有子树\n- 如何支持通配符搜索 (LC 211)? -> 遇到 '.' 时遍历所有 children\n- 如何优化内存? -> Compressed trie (Patricia trie) 合并单链路径\n\n---\n\n### Q6.",
    ),
    # Q6 - Nested List Weight Sum
    (
        "depth * val 直接递归即可。\n\n---\n\n### Q7.",
        "depth * val 直接递归即可。\n\n**Follow-ups**:\n- 如何实现 NestedInteger 的 flatten iterator (LC 341)? -> 用 stack 惰性展开\n- 如果嵌套层数可能很深导致栈溢出? -> 改用显式 stack 迭代\n\n---\n\n### Q7.",
    ),
    # Q7 - Convex Number / Digit DP
    (
        "Digit DP 可高效统计大范围内的 convex numbers 数量。\n\n---\n\n### Q8.",
        "Digit DP 可高效统计大范围内的 convex numbers 数量。\n\n**Follow-ups**:\n- 如何找 range 内的第 k 个 convex number? -> 二分搜索 + count_convex_up_to\n- 如果 digits 可以是任意 base (非十进制)? -> 修改 limit 为 base-1\n\n---\n\n### Q8.",
    ),
    # Q8 - N Lockers
    (
        "最终打开的 locker 编号恰好是 1 到 N 中的所有完全平方数。\n\n---\n\n### Q9.",
        "最终打开的 locker 编号恰好是 1 到 N 中的所有完全平方数。\n\n**Follow-ups**:\n- 如果不是从第 1 轮到第 N 轮, 而是只执行第 a 到第 b 轮? -> 统计每个柜子在 [a, b] 范围内的因子个数\n- 如果 toggle 改为 \"只有当柜子关着才打开\"? -> 结果变为所有有因子在操作范围内的柜子都打开\n\n---\n\n### Q9.",
    ),
    # Q9 - BST Common Node
    (
        "BST 的中序遍历天然有序，利用排序性质可以用双指针高效求交集。\n\n---\n\n### Q10.",
        "BST 的中序遍历天然有序，利用排序性质可以用双指针高效求交集。\n\n**Follow-ups**:\n- 如果两棵树非常大, 无法全部载入内存? -> 用 iterator 逐步合并 in-order 序列\n- 如果要找 \"最深的公共祖先\" (LCA of common nodes)? -> 不同问题, 需要在同一棵树上找 LCA\n\n---\n\n### Q10.",
    ),
    # Q10 - Big Data Sort
    (
        "对于大数据，使用 MapReduce 或 external sort 进行分布式排序。\n\n---\n\n### Q11.",
        "对于大数据，使用 MapReduce 或 external sort 进行分布式排序。\n\n**Follow-ups**:\n- 如果 f 是局部单调的 (piecewise monotonic)? -> 分段排序后归并\n- 如何处理数据倾斜 (某些 f(x) 值特别集中)? -> 采样估计分布, 动态调整 partition 边界\n\n---\n\n### Q11.",
    ),
    # Q11 - Coins Modular Sum
    (
        "类似 0-1 knapsack，关键在于跟踪 sum mod M。\n\n---\n\n### Q12.",
        "类似 0-1 knapsack，关键在于跟踪 sum mod M。\n\n**Follow-ups**:\n- 如果硬币可以重复选取? -> 去掉 j 的逆序遍历 (变为完全背包)\n- 如果 M 很大怎么优化? -> NTT (Number Theoretic Transform) 加速多项式乘法\n\n---\n\n### Q12.",
    ),
    # Q12 - Letter Combinations
    (
        "也可以用 `itertools.product` 实现 iterative 版本。\n\n---\n\n### Q13.",
        "也可以用 `itertools.product` 实现 iterative 版本。\n\n**Follow-ups**:\n- 如何只返回在字典中存在的单词? -> 加 Trie 或 set 剪枝\n- 如果按 T9 输入法, 需要返回最可能的单词? -> 频率加权 + Trie 前缀搜索\n\n---\n\n### Q13.",
    ),
    # Q13 - Consecutive Sequence
    (
        "利用 hash set 实现 O(n) 时间查找最长连续子序列。\n\n---\n\n### Q14.",
        "利用 hash set 实现 O(n) 时间查找最长连续子序列。\n\n**Follow-ups**:\n- 如何处理有重复元素的情况? -> 先去重 (用 set), 再按相同逻辑处理\n- 如果数据是流式到达的? -> 用 Union-Find 动态合并连续区间\n\n---\n\n### Q14.",
    ),
    # Q20 - Sparse Vector/Matrix
    (
        "稀疏矩阵乘法的关键优化：只遍历 A 的非零元素，对 B 的对应行做乘加。\n\n---\n\n### Q21.",
        "稀疏矩阵乘法的关键优化：只遍历 A 的非零元素，对 B 的对应行做乘加。\n\n**Follow-ups**:\n- 如何高效实现 transpose? -> 交换 row/col 索引即可, O(nnz)\n- 对于超大矩阵如何分布式计算? -> Block partition + MapReduce\n- CSR vs COO vs CSC 格式的区别和适用场景? -> CSR 适合行切片, CSC 适合列切片, COO 适合构建\n\n---\n\n### Q21.",
    ),
    # Q24 - Distributed KV Store
    (
        "最终一致性通过 anti-entropy 和 read repair 保证。\n\n---\n\n### Q25.",
        "最终一致性通过 anti-entropy 和 read repair 保证。\n\n**Follow-ups**:\n- 如何实现 cross-datacenter replication? -> Async replication + conflict resolution (CRDTs or vector clocks)\n- 如何处理 hot keys (某些 key 访问量远超平均)? -> Read replicas, caching layer, key-level load balancing\n\n---\n\n### Q25.",
    ),
]


def main() -> None:
    """Add missing follow-ups."""
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=26")
    content = cur.fetchone()[0]
    original_len = len(content)

    applied = 0
    for old, new in FOLLOWUP_INSERTIONS:
        if old in content:
            content = content.replace(old, new)
            applied += 1
        else:
            # Show first 60 chars of old for debugging
            print(f"SKIP (not found): {old[:60]!r}")

    print(f"Applied {applied}/{len(FOLLOWUP_INSERTIONS)} follow-up insertions")
    print(f"Size: {original_len}c -> {len(content)}c (+{len(content) - original_len}c)")

    # Count follow-ups now
    followups = content.count("**Follow-up")
    print(f"Total follow-up sections: {followups}")

    cur.execute("UPDATE company_documents SET content=? WHERE id=26", (content,))
    conn.commit()
    conn.close()
    print("Database updated.")


if __name__ == "__main__":
    main()
