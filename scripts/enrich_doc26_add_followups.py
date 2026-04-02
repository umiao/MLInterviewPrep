"""Add follow-ups to doc#26 questions missing them.

Task: T-P0-262 (supplement)
"""
import io
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# (unique_anchor_text, replacement_with_followup_appended)
# Each anchor is the last meaningful line before "---" for that question.
INSERTIONS = [
    # Q3
    (
        "- **Key Insight**: 节点的\"删除轮次\" = 节点高度，避免了 O(n^2) 的模拟删除\n\n---\n\n### Q4.",
        "- **Key Insight**: 节点的\"删除轮次\" = 节点高度，避免了 O(n^2) 的模拟删除\n\n**Follow-ups**:\n- 如果要求返回每轮移除后的树结构 (而非节点值列表)? -> DFS 中实际断开子节点引用\n- 如何用 iterative 方式实现? -> 用 stack 模拟后序遍历\n\n---\n\n### Q4.",
    ),
    # Q4
    (
        "- **Key Insight**: 重心分解将任意树变成深度 O(log n) 的平衡结构，使得路径查询从 O(n) 降到 O(log n)\n\n---\n\n### Q5.",
        "- **Key Insight**: 重心分解将任意树变成深度 O(log n) 的平衡结构，使得路径查询从 O(n) 降到 O(log n)\n\n**Follow-ups**:\n- 如果树是动态的 (可以加边)? -> Link-Cut Tree\n- 如何处理带权边? -> 在 BFS/DFS 预处理时记录距离\n\n---\n\n### Q5.",
    ),
    # Q5
    (
        "- **Space**: O(total characters across all words)\n\n---\n\n### Q6.",
        "- **Space**: O(total characters across all words)\n\n**Follow-ups**:\n- 如何实现 autocomplete (返回所有匹配前缀的单词)? -> DFS 从前缀节点遍历所有子树\n- 如何支持通配符搜索 (LC 211)? -> 遇到 '.' 时遍历所有 children\n- 如何优化内存? -> Compressed trie (Patricia trie) 合并单链路径\n\n---\n\n### Q6.",
    ),
    # Q6
    (
        "- **Key Trick**: LC 364 的 BFS 累加技巧避免了先求 maxDepth 再二次遍历\n\n---\n\n### Q7.",
        "- **Key Trick**: LC 364 的 BFS 累加技巧避免了先求 maxDepth 再二次遍历\n\n**Follow-ups**:\n- 如何实现 NestedInteger 的 flatten iterator (LC 341)? -> 用 stack 惰性展开\n- 如果嵌套层数可能很深导致栈溢出? -> 改用显式 stack 迭代\n\n---\n\n### Q7.",
    ),
    # Q7
    (
        "- **Key Technique**: Digit DP -- 逐位构建数字，用 tight 标记是否仍受上界约束\n\n---\n\n### Q8.",
        "- **Key Technique**: Digit DP -- 逐位构建数字，用 tight 标记是否仍受上界约束\n\n**Follow-ups**:\n- 如何找 range 内的第 k 个 convex number? -> 二分搜索 + count_convex_up_to\n- 如果 digits 可以是任意 base (非十进制)? -> 修改 limit 为 base-1\n\n---\n\n### Q8.",
    ),
    # Q8
    (
        "- **Time**: O(sqrt(n)) 枚举结果，O(1) 计算个数\n\n---\n\n### Q9.",
        "- **Time**: O(sqrt(n)) 枚举结果，O(1) 计算个数\n\n**Follow-ups**:\n- 如果不是从第 1 轮到第 N 轮, 而是只执行第 a 到第 b 轮? -> 统计每个柜子在 [a, b] 范围内的因子个数\n- 如果 toggle 改为 \"只有当柜子关着才打开\"? -> 结果变为所有有因子在操作范围内的柜子都打开\n\n---\n\n### Q9.",
    ),
    # Q9
    (
        "- **Alternative**: 双指针法对两个排序数组求交集，空间 O(n+m)\n\n---\n\n### Q10.",
        "- **Alternative**: 双指针法对两个排序数组求交集，空间 O(n+m)\n\n**Follow-ups**:\n- 如果两棵树非常大, 无法全部载入内存? -> 用 iterator 逐步合并 in-order 序列\n- 如果要找 \"最深的公共祖先\" (LCA of common nodes)? -> 需要在同一棵树上找 LCA\n\n---\n\n### Q10.",
    ),
    # Q10
    (
        "- **External Sort**: O(n log n) with O(chunk_size) memory，适合数据量 >> 内存\n\n---\n\n### Q11.",
        "- **External Sort**: O(n log n) with O(chunk_size) memory，适合数据量 >> 内存\n\n**Follow-ups**:\n- 如果 f 是局部单调的 (piecewise monotonic)? -> 分段排序后归并\n- 如何处理数据倾斜 (某些 f(x) 值特别集中)? -> 采样估计分布, 动态调整 partition 边界\n\n---\n\n### Q11.",
    ),
    # Q11
    (
        "- **Key Technique**: Modular knapsack DP，状态压缩到 (选了几枚, 余数)\n\n---\n\n### Q12.",
        "- **Key Technique**: Modular knapsack DP，状态压缩到 (选了几枚, 余数)\n\n**Follow-ups**:\n- 如果硬币可以重复选取? -> 去掉 j 的逆序遍历 (变为完全背包)\n- 如果 M 很大怎么优化? -> NTT (Number Theoretic Transform) 加速多项式乘法\n\n---\n\n### Q12.",
    ),
    # Q12
    (
        "- **Key Technique**: Backtracking with explicit undo (回溯 + path.pop())\n\n---\n\n### Q13.",
        "- **Key Technique**: Backtracking with explicit undo (回溯 + path.pop())\n\n**Follow-ups**:\n- 如何只返回在字典中存在的单词? -> 加 Trie 或 set 剪枝\n- 如果按 T9 输入法, 需要返回最可能的单词? -> 频率加权 + Trie 前缀搜索\n\n---\n\n### Q13.",
    ),
    # Q13
    (
        "- **Key Insight**: 只从 \"起点\" 开始扩展，避免重复计算\n\n---\n\n### Q14.",
        "- **Key Insight**: 只从 \"起点\" 开始扩展，避免重复计算\n\n**Follow-ups**:\n- 如何处理有重复元素的情况? -> 先去重 (用 set), 再按相同逻辑处理\n- 如果数据是流式到达的? -> 用 Union-Find 动态合并连续区间\n\n---\n\n### Q14.",
    ),
    # Q20
    (
        "- **Key Insight**: 只遍历非零元素，跳过大量零值计算\n\n---\n\n### Q21.",
        "- **Key Insight**: 只遍历非零元素，跳过大量零值计算\n\n**Follow-ups**:\n- 如何高效实现 transpose? -> 交换 row/col 索引即可, O(nnz)\n- 对于超大矩阵如何分布式计算? -> Block partition + MapReduce\n- CSR vs COO vs CSC 格式的区别? -> CSR 适合行切片, CSC 适合列切片, COO 适合构建\n\n---\n\n### Q21.",
    ),
    # Q24
    (
        "**Key Trade-off**: CAP Theorem (CAP 定理) -- Consistency, Availability, Partition Tolerance 三选二。LinkedIn 的 Voldemort 选择 AP (高可用 + 分区容错)，牺牲强一致性。\n\n---\n\n### Q25.",
        "**Key Trade-off**: CAP Theorem (CAP 定理) -- Consistency, Availability, Partition Tolerance 三选二。LinkedIn 的 Voldemort 选择 AP (高可用 + 分区容错)，牺牲强一致性。\n\n**Follow-ups**:\n- 如何实现 cross-datacenter replication? -> Async replication + conflict resolution (CRDTs or vector clocks)\n- 如何处理 hot keys (某些 key 访问量远超平均)? -> Read replicas, caching layer, key-level load balancing\n\n---\n\n### Q25.",
    ),
]


def main() -> None:
    """Add missing follow-ups."""
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=26")
    content = cur.fetchone()[0]
    original_len = len(content)

    applied = 0
    for old, new in INSERTIONS:
        if old in content:
            content = content.replace(old, new)
            applied += 1
        else:
            print(f"SKIP: {old[:80]!r}")

    print(f"Applied {applied}/{len(INSERTIONS)} follow-up insertions")
    print(f"Size: {original_len}c -> {len(content)}c (+{len(content) - original_len}c)")

    followups = content.count("**Follow-up")
    print(f"Total follow-up sections: {followups}")

    cur.execute("UPDATE company_documents SET content=? WHERE id=26", (content,))
    conn.commit()
    conn.close()
    print("Database updated.")


if __name__ == "__main__":
    main()
