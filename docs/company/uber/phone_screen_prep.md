# Uber MLE -- BPS (Behavioral + Problem Solving，行为+问题解决) 面试准备材料

> **阶段**：BPS 面试（在 Recruiter Screen 之后）
>
> **形式**：1小时 HackerRank 共享屏幕。综合编程、**D&A (Design & Architecture，设计与架构)** 和 ML 基础。
>
> **招聘方确认的结构**：5分钟介绍，40-50分钟编程 + D&A，5分钟 Q&A。

---

## 1. BPS Format Overview

BPS 取代了之前的两轮电话面试。它是一个单场1小时的面试，综合评估编程能力、系统思维和沟通表达。

| 环节 | 时长 | 重点 |
|------|------|------|
| 介绍 & 热身 | ~5分钟 | 简短自我介绍，面试官介绍面试形式 |
| 编程 + D&A | ~40-50分钟 | 在 HackerRank 上做算法题 + 设计/架构讨论 |
| Q&A | ~5分钟 | 你向面试官提问 |

**Uber 在 BPS 中评估什么：**
- **技术能力** -- 能否在时间压力下干净地解决算法问题？
- **沟通** -- 是否解释了思路？能否引导对话节奏？
- **设计与架构** -- 能否用高层次图表讨论过去的复杂项目？
- **ML 基础** -- **KNN (K-Nearest Neighbors，K近邻)** 、偏差-方差、模型评估基础

**BPS 之后的面试流程：**

| 阶段 | 重点 |
|------|------|
| Recruiter Screen | 背景匹配、动机、流程安排 |
| **BPS** | 编程 + D&A + ML 基础（当前阶段） |
| Virtual Onsite (4轮) | Coding & Data、Applied ML、System Design、Behavioral |

---

## 2. Time Allocation Strategy (1hr)

> 最大的错误是把整个小时都花在编码上。合理分配时间。

| 阶段 | 时间 | 做什么 |
|------|------|--------|
| **介绍** | 0:00-0:05 | 60秒自我介绍。面试官设定背景。 |
| **Problem 1** | 0:05-0:25 | 明确问题 -> 讨论方案 -> 编码 -> 测试。约20分钟。 |
| **Follow-ups / Problem 2** | 0:25-0:40 | 变体、优化，或第二道题。 |
| **D&A 讨论** | 0:40-0:50 | 过去复杂项目的讲解，配合图表。 |
| **ML 基础** | 0:50-0:55 | KNN、评估指标、偏差-方差快速问答。 |
| **你的提问** | 0:55-1:00 | 1-2个准备好的反向提问。 |

**来自一亩三分地的面经要点：**
- 部分 BPS 面试编程比重大（两道 LC 题 + follow-ups）
- 其他混合案例分析（UberEats 指标评估、特征评估）和较轻的编码（pandas、fizzbuzz）
- D&A 部分可能穿插在编码讨论中，也可能单独进行
- 面试官可能在第一道题之前先简单聊聊简历

---

## 3. Problem-Solving Approach

**不要直接跳入编码。** 面试官评估的是你的思维过程。

1. **明确目标** -- 复述问题，确认约束条件和边界情况
2. **探索多种方案** -- 在高层次讨论2-3种可能的解法
3. **分析权衡** -- 比较时间/空间复杂度、可读性、边界情况处理
4. **提出并论证选择** -- 解释为什么这个方案最适合
5. **干净地编码** -- 用清晰的结构和有意义的变量名实现
6. **主动测试** -- 在运行之前自己走一遍测试用例

**主动引导节奏。** 不要等面试官提示每一步——主动推进对话。

---

## 4. Problem Categorization by Pattern

来自 Uber BPS 面试的题目，按算法模式分类以便针对性练习。

### BFS / DFS（最高频）

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| LC 994 (Rotting Oranges) | 多源 BFS | 所有腐烂格子入队，逐层 BFS |
| LC 1020 (Number of Enclaves) | 边界 BFS/DFS | 从边界开始，标记可达陆地 |
| LC 1197 (Min Knight Moves) | 网格 BFS | 变体：有限棋盘大小 n |
| LC 230 (Kth Smallest in BST) | 中序遍历 | 迭代 + 递归；变体：第 k 大 |
| LC 337 (House Robber III) | 树形 **DP (Dynamic Programming，动态规划)** (DFS) | 每个节点 rob/not-rob 状态 |
| LC 549 (Longest Consecutive Seq II) | 树 DFS | 追踪递增/递减长度 |
| LC 987 (Vertical Order Traversal) | BFS/DFS + 列追踪 | 按列排序，再按行、值排序 |
| LC 2791 (Palindrome Paths in Tree) | DFS + 位掩码 XOR | 路径前缀 XOR，计数回文可构成数 |
| 2D Grid Nearest Exit | BFS | 从起点到边界的标准 BFS |
| Lock Combination | 状态空间 BFS | 解锁的最少步数 |
| City Graph BFS Sort | BFS + 排序 | 按距离排序，距离相同按索引 |

### Union Find

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| LC 547 (Number of Provinces) | Union Find / DFS | 邻接矩阵中的连通分量 |
| LC 1697 (Edge Length Limited Paths) | 离线排序 + UF | 将查询和边一起排序 |
| Rider Connection Log | 带时间戳的 UF | 所有骑手最早连通时间；屏蔽事件需要 BFS 重建 |

### Binary Search

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| LC 977 (Squares of Sorted Array) | 双指针（非 BS，但涉及有序数组） | 从两端比较绝对值 |
| LC 981 (Time Based KV Store) | 时间戳上的二分查找 | Follow-ups：100万+ req/sec、线程安全 |
| Purchase Optimization | 前缀和 + BS | 给定预算下最大可购数量 |
| Elevator Binary Search | 数组跳跃 + BS | 最小起始索引 |
| Max Throughput with Budget | BS on target | 二分答案 |

### Dynamic Programming

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| Jump Game Prime Variant | DP + 素数筛 | 跳 +1 或 +以3结尾的素数 |
| LC 337 (House Robber III) | 树形 DP | 每个节点 rob/not-rob |
| Non-overlapping Interval Triples | 排序 + DP/贪心 | 计数有效三元组 |
| Balanced Permutation | 追踪 min/max 位置 | 随 k 增大检查子数组排列 |

### Monotonic Stack（单调栈）

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| Price Discount | 单调栈 | 每个价格的下一个更小元素 |

### Sliding Window（滑动窗口）

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| Shortest Subarray with k Distinct | 双指针 + 计数器 | 标准滑动窗口最小化 |

### OOD (Object-Oriented Design，面向对象设计)

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| Cart & Pricing Engine | Strategy Pattern（策略模式） | 商品定制、加价、折扣、优惠 |
| Parking Lot | 类层次结构 | 摩托车 vs 普通车位约束 |
| Customer Revenue & Referral | 树形聚合 | 收入沿推荐树向上传播 |

### Greedy / Math（贪心/数学）

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| Min Operations n->0 | 二进制/NAF 分析 | n%4==1 -> -1, n%4==3 -> +1 |
| Task Assignment to 2 People | 按奖励差排序 | k 个任务的贪心分配 |
| Elevator/Stairs Energy | BS on split point | 最小化时间差 |

---

## 5. D&A (Design & Architecture) Prep

D&A 环节要求你讨论过去的复杂项目。面试官希望看到你画出高层次图表并解释系统流程。

### What to prepare

准备1-2个项目，能在8-10分钟内配合图表完整讲解。

**Project 1: Ranking-as-Allocation Framework（排序即分配框架）**

图表要素：
- Query -> Retrieval（基于 embedding / 规则）-> 候选集
- 候选集 -> Pointwise scoring -> 会话级分配层
- 分配层：多目标约束（曝光、转化、风险）
- 后期 re-ranking，**MoE (Mixture of Experts，混合专家)** 架构
- **A/B** 实验框架 + 诊断工具

关键讨论点：
- 为什么用会话级分配而非 pointwise 排序
- 多目标权衡：如何平衡竞争性业务指标
- MoE 架构：何时以及为什么优于单模型
- 生产考量：延迟预算、渐进式发布

**Project 2: LLM-Based Evaluation Pipeline（基于LLM的评估流水线）**

图表要素：
- 数据管道：采样查询 -> 检索搜索结果 -> 与标签配对
- **LLM (Large Language Model，大语言模型)** 推理：提示工程 -> 校准 -> 批量异步服务
- 评估：与人工评审的一致性指标 -> 仪表板
- 推广：全组织集成，用于 Search & Ads 实验

关键讨论点：
- 为什么用 LLM-as-judge：成本降低94%，延迟降低90%
- 校准方法论：如何确保可靠性
- 失败模式和防护措施
- 这如何加速实验速度

### D&A tips from 1p3a reports（一亩三分地面经中的 D&A 技巧）

- 面试官可能要求你在 HackerRank 共享编辑器上画高层次图表
- 预期 follow-up 如"为什么选 X 而不是 Y？"和"如果重来你会怎么做？"
- 一则面经指出面试官对"花了两周做的"不满意——强调决策为什么复杂，而非只是花了多少时间
- "多对话，不要只给答案"——与面试官的问题互动

---

## 6. ML Fundamentals Review

招聘方明确提到 KNN 和 ML 基础。准备好快速问答。

### KNN (K-Nearest Neighbors，K近邻)

| 主题 | 要点 |
|------|------|
| 算法 | 存储所有训练数据。对新数据点：计算与所有点的距离，找 k 个最近邻，投票（分类）或平均（回归）。 |
| 距离度量 | **Euclidean (L2)**、**Manhattan (L1)**、**Cosine similarity（余弦相似度）**。选择取决于数据特性。 |
| k 值选择 | 小 k = 过拟合（噪声敏感），大 k = 欠拟合（过度平滑）。使用交叉验证确定。 |
| 加权 KNN | 按 1/distance 加权——距离越近的邻居影响越大。 |
| 优化 | **KD-tree**（低维）、**Ball tree**（较高维）、**LSH (Locality-Sensitive Hashing，局部敏感哈希)**（近似，极高维）。 |
| 维度灾难 | 维度增加时距离趋于收敛——KNN 变得无意义。 |
| 特征缩放 | 必须归一化/标准化特征；KNN 对距离敏感。 |
| 类别特征 | **Hamming distance（汉明距离）**，或编码后使用标准距离。 |
| 优缺点 | 无训练阶段、可解释、非参数。推理慢、内存占用大、对无关特征敏感。 |

### Core ML Concepts

| 概念 | 快速回答 |
|------|----------|
| 偏差-方差权衡 | 高偏差 = 欠拟合（模型太简单）。高方差 = 过拟合（模型太复杂）。目标：最小化总误差 = bias^2 + variance + 不可约噪声。 |
| 过拟合 | 模型记住训练数据，在未见数据上失败。标志：训练准确率 >> 验证准确率。对策：更多数据、正则化、更简单模型、dropout、早停。 |
| 交叉验证 | k-fold：将数据分成 k 份，用 k-1 份训练、1份验证，轮换。给出稳健的泛化估计。不平衡类别用分层 **CV (Cross-Validation，交叉验证)**。 |
| Precision vs Recall | Precision = TP/(TP+FP) -- 预测为正的中有多少正确？Recall = TP/(TP+FN) -- 实际为正的中有多少被找到？**F1** = 调和平均。 |
| **ROC-AUC** | 绘制不同阈值下的 **TPR (True Positive Rate)** vs **FPR (False Positive Rate)**。**AUC (Area Under Curve，曲线下面积)** = 模型将随机正样本排在随机负样本前面的概率。0.5 = 随机，1.0 = 完美。 |
| 正则化 | **L1 (Lasso)**：稀疏特征，特征选择。**L2 (Ridge)**：小权重，防止大系数。**Elastic Net**：两者结合。 |
| 梯度下降 | 沿负梯度方向更新权重。学习率控制步长。变体：**SGD (Stochastic Gradient Descent，随机梯度下降)**、mini-batch、**Adam (Adaptive Moment Estimation)**（自适应）。 |
| 决策树 | 按信息增益（ID3/C4.5）或 **Gini Impurity（基尼不纯度）** 减少量（CART）分裂。易过拟合——使用剪枝或集成。 |
| Random Forest | Bagging + 特征子采样。比单棵树降低方差。 |
| Boosting | 序列集成：每个模型纠正前一个的错误。**AdaBoost**、**GBDT (Gradient Boosted Decision Trees，梯度提升决策树)**、**XGBoost**。降低偏差。 |

---

## 7. HackerRank Tips

BPS 编码在 HackerRank 上进行，需共享屏幕。

### Before the interview（面试前准备）

- [ ] 熟悉 HackerRank IDE（在 hackerrank.com/test 测试）
- [ ] 将首选语言设为 Python 3
- [ ] 了解快捷键：运行（Ctrl+Enter）、提交
- [ ] 练习在没有本地 IDE 自动补全的情况下写代码

### During the interview（面试中）

| 技巧 | 原因 |
|------|------|
| **频繁运行代码** | 面经确认面试官期望你运行和调试。不要提交未测试的代码。 |
| **编写自己的测试用例** | 在自定义输入框中添加边界情况。展示严谨性。 |
| **用 print 语句调试** | 如果卡住，加 print 追踪执行。最终提交前删除。 |
| **先用注释写思路** | 在注释中写伪代码，然后填充代码。面试官能看到你的思考过程。 |
| **屏幕共享礼仪** | 关闭不必要的标签页。只保留 HackerRank + 空白记事本。不要偷看答案。 |
| **边写边说** | 解说你在做什么："现在我在处理...的边界情况" |
| **不要恐慌 follow-ups** | Follow-ups 是预期的（变体、优化、复杂度）。大声思考。 |
| **时间意识** | 如果卡住超过5分钟，讨论你已尝试的内容并请求提示。比沉默挣扎好。 |

### Common HackerRank gotchas（常见HackerRank坑）

- 输入解析：使用 `input().split()` 或 `sys.stdin` 处理大输入
- Python 递归限制：大图 DFS 时使用 `sys.setrecursionlimit(10000)`
- 输出格式：精确匹配期望输出（末尾换行、空格）
- 可用集合：`from collections import defaultdict, deque, Counter`
- Heapq：`import heapq` -- Python 只有最小堆；最大堆用取负值

---

## 8. Content Areas Summary

| 领域 | 详情 | 优先级 |
|------|------|--------|
| **BFS/DFS** | 图遍历、树题、网格搜索——Uber BPS 中最高频模式 | 最高 |
| **Union Find** | 连通分量、离线排序边查询 | 高 |
| **Binary Search** | 二分答案、基于时间的查找、有序数组操作 | 高 |
| **Dynamic Programming** | 树形 DP、跳跃游戏变体、区间问题 | 高 |
| **OOD** | 购物车/定价、停车场、推荐树——干净的类设计 | 中高 |
| **ML 基础** | KNN 实现、偏差-方差、评估指标、CV | 中高 |
| **D&A 项目讨论** | 高层次图表、权衡推理、设计决策 | 中高 |
| **语法流利度** | 不用 IDE 自动补全写干净的 Python；面试官注意到犹豫 | 高 |
| **边界情况** | 主动识别：空输入、单元素、溢出、重复 | 高 |
| **复杂度分析** | 对讨论的每种方案说明时间和空间复杂度 | 高 |

---

## 9. BPS Checklist（BPS 检查清单）

### Coding prep（编程准备）
- [ ] 每种高频模式（BFS/DFS、UF、BS、DP）练习5+道题
- [ ] 至少在 HackerRank 上做3道题（不是本地 IDE）
- [ ] 练习2-3道 OOD 题（类设计、Strategy Pattern）
- [ ] 计时：medium 20分钟，medium-hard 25分钟

### ML prep（ML 准备）
- [ ] 从零实现 KNN（距离度量、k 值选择、加权）
- [ ] 复习 **ANN (Approximate Nearest Neighbors，近似最近邻)** 概念（LSH、KD-tree、Ball tree）
- [ ] 快速问答：偏差-方差、precision-recall、ROC-AUC、正则化

### D&A prep（D&A 准备）
- [ ] 准备2个项目讲解，配合图表（各8-10分钟）
- [ ] 练习口头表达权衡决策
- [ ] 准备应对"为什么选 X 而不是 Y"的 follow-ups

### Communication prep（沟通准备）
- [ ] 练习边编码边口述解法
- [ ] 至少做2次模拟面试，按"明确问题 -> 探索方案 -> 权衡分析 -> 编码"流程
- [ ] 练习引导对话——不要等面试官提示

### Logistics（后勤准备）
- [ ] 测试 HackerRank IDE 和屏幕共享设置
- [ ] 准备安静环境 + 有线耳机
- [ ] 准备好本文档 + 简历以便快速查阅
- [ ] 水准备好，手机静音
