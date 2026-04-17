# Pinterest LC 调研笔记：「寻找餐馆区间」

> 来源：Pinterest 2025-11 面经 dump。原题名「寻找餐馆区间」，无 LC 编号。
> 本文档记录候选对照、判定与结论。

## 候选对照

面经候选：LC 1779 / 2563 / 1094 / 1851。

| LC | 英文标题 | 难度 | 核心套路 | 与「餐馆区间」契合度 |
|----|----------|------|----------|----------------------|
| 1779 | Find Nearest Point That Has the Same X or Y Coordinate | Easy | 遍历 + 曼哈顿距离 | 低：关键词「寻找」对上但不涉及「区间」 |
| 2563 | Count the Number of Fair Pairs | Medium | 排序 + 二分 (lower/upper bound) | 中：有「区间」（sum ∈ [lo, hi]）但与「餐馆」无主题联系 |
| 1094 | Car Pooling | Medium | 差分数组 / 扫描线 | 中：区间是「上下车」主题，硬凑为「接送餐」可通 |
| **1851** | **Minimum Interval to Include Each Query** | **Hard** | **离线排序 + 小顶堆（按右端踢出）** | **高：题面天然讲「对每个查询点找最小覆盖区间」，常见主题改写为「对每个用户位置找覆盖该点的最小配送半径的餐馆」** |

## 判定

选 **LC 1851 — Minimum Interval to Include Each Query**。

### 依据

1. **关键词「区间」（intervals）**：1851 的输入就是 `intervals = [[li, ri], ...]`；1779 完全没有区间，1094 与 2563 的「区间」是次要概念。
2. **「寻找」语义**：1851 要求对每个 query 点**寻找**最小覆盖区间，动词与题名完全对齐；1094「合并容量」、2563「计数配对」语义不匹配。
3. **「餐馆」主题改写自然**：Pinterest 面试常把经典 interval 题包装成本地生活 / LBS 场景 — 例如「给定餐馆的服务半径区间集合与一批用户坐标，对每个用户找能覆盖他且服务半径最小的餐馆」。
4. **难度级别**：Pinterest Must-Do 榜单偏 Hard，1851 符合（1094/2563 偏 Medium 不够分量，1779 是 Easy 明显不符）。

### 模式速记（留给后续详细解题笔记）

- 离线算法：把 queries 排序，把 intervals 按左端点排序。
- 用小顶堆，堆序键为**区间长度**；堆元素携带右端点。
- 遍历有序 query q：把所有 `l ≤ q` 的区间 push 入堆；弹出堆顶中 `r < q` 的无效项；堆顶即答案（若空则 -1）。
- 复杂度：O((n + m) log n)。

## 落库动作

- 数据库 `problems` 表已存在 LC 1851（id=144，pattern='interval'，company_tags=[]）。
- 本任务执行：追加 `Pinterest` 到 company_tags。
- 后续任务（不在本任务范围）：补写完整解题笔记 + 加入 Pinterest LC Must-Do 索引表。

## 若结论有误

若 onsite 真题其实是 1094（差分/扫描线）或 2563（排序+二分），两者模式都在已有 Pinterest Must-Do 周边套路内（410 split array、2402 meeting rooms III 皆属区间/堆家族），复习互相迁移成本低。1851 是目前最稳的第一选择。
