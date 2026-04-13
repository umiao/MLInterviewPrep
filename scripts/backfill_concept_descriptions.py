"""Backfill short Chinese descriptions for non-LC problems (T-P1-183).

Targets 26 problems where leetcode_id IS NULL and description IS NULL/empty:
- 24 Uber 1point3acres custom problems (algorithm category)
- 1 ML coding problem (K-Means)
- 1 system design problem (Driver Queue)

Convention: Chinese prose; algorithm names, data structures, and formulas in
English. 1-2 short paragraphs per entry. Sets description_source='manual'.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"

# Descriptions keyed by problem id. Each is 1-2 Chinese paragraphs; English
# reserved for algorithm/data-structure names and API signatures.
DESCRIPTIONS: dict[int, str] = {
    1031: (
        "**Purchase Optimization (Uber 1p3a)**: 给定升序排列的价格数组 `prices` 以及若干查询 "
        "`(pos, amount)`，对每个查询返回从下标 `pos` 开始、预算 `amount` 内最多可购买的物品数量。\n\n"
        "标准做法: 前缀和 + 二分查找。预处理 `prefix[i] = sum(prices[0..i-1])`，每次查询用 "
        "`bisect_right` 找到最大的 `end`，使 `prefix[end] - prefix[pos] <= amount`。"
        "时间 O((n + q) log n)，空间 O(n)。"
    ),
    1032: (
        "**Customer Revenue & Referral Tracking (Uber 1p3a, OOD)**: 设计推荐系统，支持 "
        "`insertNewCustomer(revenue, referrerID)` 与 `getLowestK(k, minTotalRevenue)` 两个 API。"
        "新用户 revenue 需沿 referral 树向上传播，汇总到所有祖先的 `total_revenue`。\n\n"
        "关键设计: 每个 `Customer` 节点保存 direct revenue 与 subtree total；插入时沿父指针上溯传播；"
        "查询使用 `heapq.nsmallest` 或 SortedList 获得满足 `total_revenue >= minTotalRevenue` 的最小 k 个。"
        "插入 O(D)，查询 O(n log k) 或 O(k + log n)。"
    ),
    1033: (
        "**Uber Rider Connection Log (Union Find)**: 给定按时间戳排序的日志 "
        "`<timestamp> A shared-ride-with B`，求所有乘客第一次全部互相连通（直接或传递）的最早时间戳。\n\n"
        "主解法: Union Find with path compression，每条日志执行 `union`，当 `components == 1` 时返回当前时间戳；"
        "均摊 O(E·α(N))。Follow-up 引入 `blocked` 事件（删除边），UF 无法支持删除；"
        "改用邻接表 + BFS/DFS 在每次事件后重判连通性，或升级到 Link-Cut Tree / Euler Tour Trees 做 O(log N)。"
    ),
    1034: (
        "**Elevator Binary Search OA (Uber 1p3a)**: 给定 `moves` 数组，每个位置表示跳跃距离（偶数下标向右、"
        "奇数下标向左，或正负号决定方向）。找到最小起点 `start`，使模拟过程中位置不会越过左边界 (index < 0)。\n\n"
        "做法: 对每个候选 start 模拟跳跃路径，用 `visited` 集合检测环；若单调，则可在起点上做二分。"
        "朴素线性扫描 O(n²) worst case，单调性下 O(n log n)。"
    ),
    1035: (
        "**Server Throughput with Heap (Uber 1p3a OA)**: 给定 `n` 台服务器与按到达时间排序的请求 "
        "`(arrival, duration)`。每台服务器可并发处理一个请求，请求到达时若有空闲服务器则分配并计数，"
        "否则丢弃。最大化被成功处理的请求数。\n\n"
        "做法: Min-heap of `(available_time, server_id)`。"
        "每个请求弹出堆顶服务器，若 `available_time <= arrival` 则占用并以 `arrival + duration` 重入堆，"
        "否则原样放回并跳过该请求。时间 O(R log S)，空间 O(S)。递归暴力解法 O(S^R) 仅用于教学对比。"
    ),
    1036: (
        "**Cart & Pricing Engine OOD (Uber Eats)**: 设计购物车与计价引擎，支持菜品自定义 (add-ons 如 "
        "'Extra Cheese')、surge pricing 乘数、membership 折扣 (Uber One: 免配送 + 5% off)、"
        "promo codes（固定额或百分比）以及详细收据 (Base/Add-ons/Fees/Discounts)。\n\n"
        "关键模式: Strategy pattern 为每类定价规则建独立类；`PricingEngine` 按顺序应用策略链，"
        "保留中间小计以便输出 receipt breakdown。多条独立定价规则需能组合叠加，测试覆盖边界（负总价截断、"
        "百分比与固定额混用、membership 与 promo 互斥与否）。"
    ),
    1037: (
        "**Circular Array Shortest Jump (Uber 1p3a)**: 给定循环数组，`arr[i]` 表示从位置 i 可跳的**精确**距离"
        "（左右任选其一）。求从下标 A 到 B 的最短跳跃步数。\n\n"
        "做法: BFS on indices，每个节点有两个邻居 `(i + arr[i]) mod n` 与 `(i - arr[i]) mod n`；"
        "首次访问 B 的层数即答案。时间/空间 O(n)。"
    ),
    1038: (
        "**Robot Distance in Grid (Uber 1p3a)**: 网格中 `O` 为机器人、`E` 为空、`X` 为障碍。"
        "给定目标机器人到最近障碍的四方向距离 `[left, top, bottom, right]`，找出匹配该距离向量的机器人。\n\n"
        "做法: DP 预计算每个 cell 到四个方向最近障碍的距离（四次线性扫描），然后遍历所有 robot cell 比较四元组。"
        "预处理 O(R·C)，查询 O(1)。"
    ),
    1039: (
        "**Min Operations n to 0 (Uber 1p3a)**: 每次操作可令 `n += 2^i` 或 `n -= 2^i`（任意 i >= 0），"
        "求将 n 变为 0 的最少操作次数。\n\n"
        "关键洞察: 答案等于 n 的 Non-Adjacent Form (NAF) 中非零位个数。贪心规则: 若 `n % 2 == 0` 则右移；"
        "若 `n % 4 == 1` 则减 1；若 `n % 4 == 3` 则加 1（制造更长 carry 以减少总操作数）。时间 O(log n)。"
    ),
    1040: (
        "**Shortest Subarray with k Distinct (Uber 1p3a)**: 给定数组 `nums` 与整数 k，"
        "求包含至少 k 个不同元素的最短子数组长度；若不存在返回 -1。\n\n"
        "做法: Sliding window + 频次计数器。右指针扩张直到窗内 distinct >= k，再收缩左指针直到 distinct 恰好下降，"
        "记录最短长度。时间 O(n)，空间 O(k)。"
    ),
    1041: (
        "**Price Discount (Monotonic Stack, Uber 1p3a OA)**: 对每个下标 i，找到第一个 j > i 使 "
        "`prices[j] <= prices[i]`；若存在，第 i 件的成交价为 `prices[i] - prices[j]`，否则按原价卖出。"
        "输出 (1) 总成交额，(2) 按原价卖出的下标列表（升序）。\n\n"
        "做法: 经典 next smaller or equal element 问题，使用单调递增栈从右向左扫描，或从左向右边扫边弹栈结算。"
        "时间 O(n)，空间 O(n)。"
    ),
    1042: (
        "**Balanced Permutation Check (Uber 1p3a)**: 给定 `1..n` 的排列，对每个 k ∈ [1, n] 判定前 k 位是否构成 "
        "`1..k` 的排列；将结果按顺序拼成二进制串返回。\n\n"
        "做法: 线性扫描并维护 `min_pos` 与 `max_pos`。处理 k 时更新 `max_pos = max(max_pos, pos[k])`、"
        "`min_pos = min(min_pos, pos[k])`，若 `max_pos - min_pos + 1 == k` 则第 k 位为 '1'。时间 O(n)。"
    ),
    1043: (
        "**Elevator/Stairs Energy Optimization (Uber 1p3a)**: 总共 c 层，前 x 层乘电梯（每层耗时 t1、获得 e1 能量）、"
        "剩余 c - x 层走楼梯（每层消耗 e2，耗时 `ceil(c / energy)`，能量不能为负）。"
        "最小化电梯与楼梯两段耗时之差。\n\n"
        "做法: 对分割点 x 做二分搜索（基于差值单调性），可行性检查中验证能量非负约束与耗时差。"
        "时间 O(log c · check_cost)。"
    ),
    1044: (
        "**N-ary Tree 3-part Problem (Uber 1p3a)**: 给定 N-ary tree，实现三个操作: "
        "(a) 求所有节点值之和；(b) 求 root-to-leaf 最大路径和；(c) 返回最大路径上的节点序列。\n\n"
        "做法: 自定义 `NaryNode` 类，三个独立 DFS 遍历。(b) 与 (c) 可合并为一次 post-order DFS，"
        "向上传递 `(max_sum_from_here, best_child_path)`。整体 O(N)。"
    ),
    1045: (
        "**Max Throughput with Budget (Uber 1p3a)**: `n` 个流水线服务，各有 `current_throughput[i]` 与 "
        "`scale_cost[i]`（每单位吞吐扩容成本）。瓶颈吞吐为所有服务最小值。"
        "在总预算 B 内最大化瓶颈吞吐。\n\n"
        "做法: Binary search on answer。对候选吞吐 T，累加 `max(0, T - current[i]) * scale_cost[i]`，"
        "若 <= B 则 T 可行。时间 O(n log (max_throughput))。"
    ),
    1046: (
        "**Parking Lot OOD (Uber 1p3a)**: 设计停车场系统，支持 `park(vehicle)`、`unpark(spot_id)`、"
        "`check_car(license_plate)`。约束: motorcycle 专用位只接受摩托车，regular 位同时接受摩托车与普通汽车。\n\n"
        "类层次: `VehicleType` enum, `Vehicle` 基类 + 子类, `Spot` + `SpotType`, `ParkingLot` 管理分配。"
        "维护两张 map: `spot_id -> Vehicle`、`license_plate -> spot_id`，实现 O(1) 查询；"
        "分配策略可用两个空闲队列/位图分别管理 motorcycle-only 与 regular 位。"
    ),
    1047: (
        "**Task Assignment to 2 People (Uber 1p3a)**: n 个任务，`reward1[i]` / `reward2[i]` 分别为由 person 1 / 2 "
        "执行的收益。person 1 必须恰好执行 k 个任务，其余归 person 2。最大化总收益。\n\n"
        "做法: 贪心。计算 `diff[i] = reward1[i] - reward2[i]`，按降序排序，前 k 个分给 person 1。"
        "总收益 = `sum(reward2) + sum(top-k diffs)`。时间 O(n log n)。"
    ),
    1048: (
        "**Minesweeper Grid Generator (Uber 1p3a)**: 在 M × N 网格上随机放置恰好 K 个地雷，"
        "输出网格中每个非雷 cell 显示其 8-邻居的地雷数，雷本身显示为 `*`。\n\n"
        "Follow-up 强调代码质量: 避免不必要的 set、缩减变量、简化逻辑。"
        "常见洁净实现: 用 `random.sample(range(M*N), K)` 选出一维索引，直接二次遍历计数邻居。"
        "时间 O(M·N)。面试官关注迭代式代码质量改进而非算法复杂度。"
    ),
    1049: (
        "**2D Grid Nearest Exit (BFS, Uber 1p3a)**: 给定含墙与通路的 2D 网格和起点，"
        "求到达任意边界空 cell 的最短步数（起点本身不算出口）。\n\n"
        "做法: 标准多源/单源 BFS，从起点出发逐层扩展，第一次到达边界 cell 的层数即为答案；"
        "若不可达返回 -1。与 LC 1926 同型。时间/空间 O(R·C)。"
    ),
    1050: (
        "**Lock Combination BFS (Uber 1p3a)**: 类 LC 752 Open the Lock。四轮盘（或 n 位）密码锁，"
        "每步旋转一个轮盘 +1 或 -1（10 进制循环），给定 `deadends` 黑名单和 `target`，求从 `\"0000\"` 到 target 的最少步数。\n\n"
        "做法: 状态空间 BFS，visited 集合避免重复；可选双向 BFS 将状态数从 O(10^n) 降到 O(10^(n/2))。"
        "每个状态有 2n 个邻居。"
    ),
    1051: (
        "**Non-overlapping Interval Triples (Uber 1p3a)**: 给定区间列表 `[start, end]`，"
        "统计三元组数量，使三个区间两两不重叠。\n\n"
        "做法: 排序 + 计数。按 end 排序，枚举中间区间 m：用 bisect 在 end 数组上找到左侧结束早于 `m.start` 的区间数 L，"
        "在 start 数组上找到右侧开始晚于 `m.end` 的区间数 R，累加 `L * R`。时间 O(n log n)。"
    ),
    1052: (
        "**City Graph BFS Sort (Uber 1p3a)**: 给定无向城市图与起点，按到起点的 BFS 距离升序排序所有城市；"
        "距离相同则下标小者在前。\n\n"
        "做法: 从起点做 BFS 得到 `dist[i]`，然后按 `(dist[i], i)` 升序排序。时间 O(V + E + V log V)。"
        "面试场景中与 Non-overlapping Interval Triples 同场 40 分钟，考察时间管理。"
    ),
    1053: (
        "**Balls Attraction Union Find (Uber 1p3a)**: 2D 平面若干球体，若两球距离 < d 则相互吸引并合并；"
        "每个时间步只能主动触发一个球启动吸引（连锁反应）。求使所有球合并所需最少时间步数。\n\n"
        "做法: Union Find 预先连接所有距离 < d 的球对，最终连通分量数即为答案（每个分量需一次独立触发）。"
        "球对枚举 O(n²)，UF 操作近似 O(1)。"
    ),
    1054: (
        "**Layers and Energy Adventure (Uber 1p3a)**: `layers[i]` 表示通过第 i 层消耗的能量，"
        "`energy[i]` 表示进入第 i 层所需最低剩余能量，初始能量 K。从层 i 出发: 消耗 `layers[i]`，"
        "若剩余 >= `energy[i]` 则通过。返回 `score[i]` = 从第 i 层出发可连续通过的最大层数。\n\n"
        "做法: Prefix sum + sliding window / two pointers。维护窗口 [l, r] 累积消耗，"
        "在消耗超限或 energy 检查失败时收缩左端；对每个起点输出最大连续通过层数。时间 O(n)。"
    ),
    1055: (
        "**Driver Queue System Design (Uber 1p3a)**: 设计内部 API，给定 pickup area 返回司机队列。"
        "司机进入该区域时加入队列，离开时从队列中移除。核心需求: 低延迟查询、地理围栏 (geofence) 归属变更、"
        "队列公平性（FIFO + priority boost）。\n\n"
        "系统设计要点: geohash / S2 cell 索引做区域归属，driver location stream 经 Kafka 入 stateful 流处理"
        "(Flink/KStreams) 维护每区 active queue；API 层从 Redis sorted set 按进入时间读取。"
        "讨论一致性 (at-least-once vs exactly-once)、热点区 sharding、driver churn 导致的抖动平滑。"
        "面试反馈强调对话交互 (clarifying questions、trade-off)，不要直接给答案。"
    ),
    1064: (
        "**K-Means Pure Python Implementation (K-Means++)**: 从零实现 K-Means 聚类，"
        "使用 K-Means++ 初始化以降低坏初值概率；支持 4 种停止条件（max iterations、centroid 移动 < 阈值、"
        "labels 无变化、SSE 收敛）与空 cluster 处理（重新从最远点初始化）。\n\n"
        "核心步骤: (1) K-Means++ 按距离平方加权采样初始 centroid；"
        "(2) Assignment step 计算每点到所有 centroid 的欧氏距离并取 argmin；"
        "(3) Update step 按均值更新 centroid；(4) 检查任一停止条件。复杂度 O(n·k·d·iter)。"
        "关键 ML 讨论点: K 选择 (elbow、silhouette)、初始化敏感性、对异常点不鲁棒、"
        "与 Gaussian Mixture / spectral clustering 的区别。"
    ),
}


def main() -> None:
    missing = set()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        rows = cur.execute(
            "SELECT id, title FROM problems WHERE leetcode_id IS NULL "
            "AND (description IS NULL OR TRIM(description)='') "
            "ORDER BY id"
        ).fetchall()
        target_ids = {r[0] for r in rows}
        print(f"Targets in DB: {len(target_ids)}")

        provided = set(DESCRIPTIONS.keys())
        missing_in_script = target_ids - provided
        extra_in_script = provided - target_ids
        if missing_in_script:
            print(f"WARNING: no description for ids: {sorted(missing_in_script)}")
            missing.update(missing_in_script)
        if extra_in_script:
            print(f"Note: script has descriptions for ids not needing backfill: {sorted(extra_in_script)}")

        updated = 0
        for pid, desc in DESCRIPTIONS.items():
            if pid not in target_ids:
                continue
            cur.execute(
                "UPDATE problems SET description=?, description_source='manual' "
                "WHERE id=?",
                (desc, pid),
            )
            updated += cur.rowcount
        conn.commit()
        print(f"Updated {updated} problems.")

        remaining = cur.execute(
            "SELECT COUNT(*) FROM problems WHERE leetcode_id IS NULL "
            "AND (description IS NULL OR TRIM(description)='')"
        ).fetchone()[0]
        print(f"Remaining NULL/empty concept descriptions: {remaining}")
    finally:
        conn.close()

    if missing:
        raise SystemExit(f"Missing descriptions for: {sorted(missing)}")


if __name__ == "__main__":
    main()
