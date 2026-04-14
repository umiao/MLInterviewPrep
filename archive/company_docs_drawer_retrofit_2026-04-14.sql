-- Drawer-link retrofit of 8 company docs (T-P0-193 AC5 via T-P0-197).
-- Generated 2026-04-14. Rerun with retrofit_doc_drawer_links.py is idempotent.
BEGIN TRANSACTION;

-- doc 3 (Uber BPS Phone Screen Prep): lc=13 leetcode=0 custom=0
UPDATE company_documents SET content = '# Uber MLE -- BPS (Behavioral + Problem Solving，行为+问题解决) 面试准备材料

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
| [LC 994](lc://994) (Rotting Oranges) | 多源 BFS | 所有腐烂格子入队，逐层 BFS |
| [LC 1020](lc://1020) (Number of Enclaves) | 边界 BFS/DFS | 从边界开始，标记可达陆地 |
| [LC 1197](lc://1197) (Min Knight Moves) | 网格 BFS | 变体：有限棋盘大小 n |
| [LC 230](lc://230) (Kth Smallest in BST) | 中序遍历 | 迭代 + 递归；变体：第 k 大 |
| [LC 337](lc://337) (House Robber III) | 树形 **DP (Dynamic Programming，动态规划)** (DFS) | 每个节点 rob/not-rob 状态 |
| [LC 549](lc://549) (Longest Consecutive Seq II) | 树 DFS | 追踪递增/递减长度 |
| [LC 987](lc://987) (Vertical Order Traversal) | BFS/DFS + 列追踪 | 按列排序，再按行、值排序 |
| [LC 2791](lc://2791) (Palindrome Paths in Tree) | DFS + 位掩码 XOR | 路径前缀 XOR，计数回文可构成数 |
| 2D Grid Nearest Exit | BFS | 从起点到边界的标准 BFS |
| Lock Combination | 状态空间 BFS | 解锁的最少步数 |
| City Graph BFS Sort | BFS + 排序 | 按距离排序，距离相同按索引 |

### Union Find

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| [LC 547](lc://547) (Number of Provinces) | Union Find / DFS | 邻接矩阵中的连通分量 |
| [LC 1697](lc://1697) (Edge Length Limited Paths) | 离线排序 + UF | 将查询和边一起排序 |
| Rider Connection Log | 带时间戳的 UF | 所有骑手最早连通时间；屏蔽事件需要 BFS 重建 |

### Binary Search

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| [LC 977](lc://977) (Squares of Sorted Array) | 双指针（非 BS，但涉及有序数组） | 从两端比较绝对值 |
| [LC 981](lc://981) (Time Based KV Store) | 时间戳上的二分查找 | Follow-ups：100万+ req/sec、线程安全 |
| Purchase Optimization | 前缀和 + BS | 给定预算下最大可购数量 |
| Elevator Binary Search | 数组跳跃 + BS | 最小起始索引 |
| Max Throughput with Budget | BS on target | 二分答案 |

### Dynamic Programming

| 题目 | 模式 | 关键思路 |
|------|------|----------|
| Jump Game Prime Variant | DP + 素数筛 | 跳 +1 或 +以3结尾的素数 |
| [LC 337](lc://337) (House Robber III) | 树形 DP | 每个节点 rob/not-rob |
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
- [ ] 水准备好，手机静音', updated_at = datetime('now') WHERE id = 3;

-- doc 19 (Adobe MLE Prep: All-in-One (Day 1-8 + Prep Script)): unchanged (stats={'lc': 0, 'leetcode': 0, 'custom': 0})

-- doc 26 ([合集] 算法题解全索引): lc=33 leetcode=0 custom=0
UPDATE company_documents SET content = '# LinkedIn Interview Questions Index

> 本文档汇总LinkedIn面试中所有问到的题目，包含题目描述、解法要点、Follow-up和来源标注。
> 数据来源：一亩三分地面经整理 + LinkedIn seed data (47题)

## 目录

- **Coding** (15 题)
  - Q1: Design a data structure that supports insert, delete, and ge ([LC 380](lc://380), 381)
  - Q2: Given a list of courses and their prerequisites, determine i ([LC 207](lc://207), 210)
  - Q3: Given a binary tree, repeatedly remove all leaf nodes and re ([LC 366](lc://366))
  - Q4: Given a tree, find its centroid using centroid decomposition
  - Q5: Implement a Trie (prefix tree) data structure that supports  ([LC 208](lc://208), 211, 212)
  - Q6: Given a nested list of integers (where each element is eithe ([LC 339](lc://339), 364)
  - Q7: Big data algorithm: Given a range (a, b), find the minimum c
  - Q8: N lockers are initially all closed
  - Q9: Given two Binary Search Trees (BSTs), find the deepest commo
  - Q10: Big data coding: Given a large dataset of elements, apply a 
  - Q11: There are N coins with face values 0, 1, 2, 
  - Q12: Given a string containing digits from 2-9 inclusive, return  ([LC 17](lc://17))
  - Q13: Given a list of non-repetitive positive integers, find and o ([LC 128](lc://128)*)
  - Q14: SQL Problem: Given two tables - table1(user_id, article_id, 
  - Q15: SQL + Python: Given tables video_posts(post_date, memberid, 
- **ML Theory & Coding** (8 题)
  - Q16: Explain the Transformer architecture in detail
  - Q17: You are testing whether changing an email''s headline and con
  - Q18: LinkedIn hypothesizes that video posting features might not 
  - Q19: Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost 
  - Q20: Design and implement a sparse vector and sparse matrix repre ([LC 1573](lc://1573), 311)
  - Q21: Implement weighted random sampling from a multinomial distri
  - Q22: Compare and contrast using open-source software vs building 
  - Q23: Which LinkedIn product do you like most and why? Demonstrate
- **ML System Design** (24 题)
  - Q24: Design a distributed Key-Value Store that supports replicati
  - Q25: Design a metrics monitoring system for a large-scale distrib
  - Q26: Given a LinkedIn webpage showing user profile information, d
  - Q27: Design a system to help LinkedIn recruiters find suitable ca
  - Q28: Design the metrics framework for LinkedIn''s job search and r
  - Q29: Design LinkedIn''s feed ranking system
  - Q30: LinkedIn''s job application rate has been dropping
  - Q31: How would you identify frequent business travelers from Link
  - Q32: Design a recommendation system for LinkedIn Learning
  - Q33: Design a propensity model to predict which LinkedIn users ar
  - Q34: Design a personalized job ranking model for LinkedIn
  - Q35: LinkedIn has 500M+ users
  - Q36: What metrics would you design to measure job quality on Link
  - Q37: How would you identify potential client companies for Linked
  - Q38: Design a keyword search system for LinkedIn that surfaces th
  - Q39: How would you decide which feature to build next for a Linke
  - Q40: Design the metrics for LinkedIn''s profile visit feature
  - Q41: You are launching a new feature on LinkedIn
  - Q42: Design a database schema and system for tracking job applica
  - Q43: Design LinkedIn''s push notification system for improving use
  - Q44: LinkedIn''s job application count has dropped 10% month-over-
  - Q45: You''ve launched a ''Recommended Jobs'' feature on LinkedIn
  - Q46: Design a system to track and analyze application database at
  - Q47: Design a system for LinkedIn keyword search that surfaces th

---

## Coding (15 题)

### Q1. Design a data structure that supports insert, delete, and getRandom operations, ... ([LC 380](lc://380), 381)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: hash-map, array, randomized, design, O(1)-operations

**题目**: Design a data structure that supports insert, delete, and getRandom operations, all in average O(1) time complexity. The insert and delete operations should work with arbitrary values, and getRandom should return a random element with equal probability...

**解答**:

**思路**: 核心是将 hash map 和 dynamic array (动态数组) 结合。HashMap 存储 val -> index 的映射实现 O(1) 查找；数组支持 O(1) 随机访问。删除时将目标元素与数组末尾元素交换，然后 pop 末尾，保持 O(1)。

```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}  # val -> index in list
        self.vals = []

    def insert(self, val: int) -> bool:
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.val_to_idx:
            return False
        idx = self.val_to_idx[val]
        last = self.vals[-1]
        self.vals[idx] = last
        self.val_to_idx[last] = idx
        self.vals.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```

- **Time**: O(1) average for insert/remove/getRandom
- **Space**: O(n)

**Follow-up ([LC 381](lc://381) -- 允许重复)**:
HashMap 存 val -> set of indices。remove 时从 set 中取任一 index，与末尾交换。insert 时直接加入 set。

---

### Q2. Given a list of courses and their prerequisites, determine if it is possible to ... ([LC 207](lc://207), 210)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: topological-sort, graph, BFS, DFS, cycle-detection

**题目**: Given a list of courses and their prerequisites, determine if it is possible to finish all courses (cycle detection in a directed graph). If possible, return a valid order in which to take the courses...

**解答**:

**思路**: 经典的 Topological Sort (拓扑排序) 问题。用 BFS (Breadth-First Search，广度优先搜索) 的 Kahn''s Algorithm: 维护每个节点的 in-degree (入度)，从入度为 0 的节点开始，逐层移除节点并更新邻居入度。如果最终处理的节点数 < 总数，说明存在环。

```python
from collections import deque

def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:
    graph = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    for course, pre in prerequisites:
        graph[pre].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(numCourses) if in_degree[i] == 0)
    count = 0
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        count += 1
        for nei in graph[node]:
            in_degree[nei] -= 1
            if in_degree[nei] == 0:
                queue.append(nei)
    return count == numCourses  # order 即为拓扑排序结果 ([LC 210](lc://210))
```

- **Time**: O(V + E)，V = 课程数，E = 先修关系数
- **Space**: O(V + E)
- **Key Technique**: Kahn''s Algorithm (BFS topological sort) -- 适合检测 DAG (Directed Acyclic Graph，有向无环图) 和输出排序

**Follow-ups**:
- 如果需要返回所有可能的拓扑排序? -> 回溯法枚举所有入度为 0 的选择
- 如何检测具体是哪些课程构成了环? -> DFS 染色法 (white/gray/black)
- 并行执行: 最少需要几个学期? -> [LC 1136](lc://1136), 分层 BFS

---

### Q3. Given a binary tree, repeatedly remove all leaf nodes and return the result of e... ([LC 366](lc://366))

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: binary-tree, DFS, tree-depth, recursion

**题目**: Given a binary tree, repeatedly remove all leaf nodes and return the result of each removal round. In each round, collect all current leaf nodes, remove them from the tree, and repeat until the tree is empty...

**解答**:

**思路**: 不需要真的反复删除叶子。观察规律：一个节点被删除的轮次 = 它在树中的高度 (height)。叶子节点 height=0 第一轮删除，其父节点如果两个子节点都是叶子则 height=1 第二轮删除，以此类推。用 DFS (Depth-First Search，深度优先搜索) 后序遍历计算每个节点高度，按高度分组。

```python
from collections import defaultdict

def findLeaves(root) -> list[list[int]]:
    result = defaultdict(list)

    def dfs(node) -> int:
        if not node:
            return -1
        h = max(dfs(node.left), dfs(node.right)) + 1
        result[h].append(node.val)
        return h

    dfs(root)
    return [result[i] for i in range(len(result))]
```

- **Time**: O(n)，每个节点访问一次
- **Space**: O(n)
- **Key Insight**: 节点的"删除轮次" = 节点高度，避免了 O(n^2) 的模拟删除

**Follow-ups**:
- 如果要求返回每轮移除后的树结构 (而非节点值列表)? -> DFS 中实际断开子节点引用
- 如何用 iterative 方式实现? -> 用 stack 模拟后序遍历

---

### Q4. Given a tree, find its centroid using centroid decomposition

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: tree, centroid-decomposition, advanced-data-structures, divide-and-conquer, graph

**题目**: Given a tree, find its centroid using centroid decomposition. Then support dynamic point activation/deactivation queries: activate or deactivate nodes, and after each operation, find the nearest active node to a given query node...

**解答**:

**思路**: Centroid Decomposition (重心分解) 是树上分治的经典技术。树的 centroid (重心) 是删除后使最大子树最小的节点。递归地找重心、以重心为根分治，构建一棵深度 O(log n) 的 centroid tree。支持高效的路径查询和点激活/查询操作。

```python
def find_centroid(adj: list[list[int]], n: int) -> int:
    """Find centroid of tree with n nodes."""
    subtree_size = [0] * n
    removed = [False] * n

    def get_size(v: int, parent: int) -> int:
        subtree_size[v] = 1
        for u in adj[v]:
            if u != parent and not removed[u]:
                subtree_size[v] += get_size(u, v)
        return subtree_size[v]

    def get_centroid(v: int, parent: int, tree_size: int) -> int:
        for u in adj[v]:
            if u != parent and not removed[u]:
                if subtree_size[u] > tree_size // 2:
                    return get_centroid(u, v, tree_size)
        return v

    def decompose(v: int, parent_centroid: int) -> int:
        size = get_size(v, -1)
        centroid = get_centroid(v, -1, size)
        removed[centroid] = True
        # Process centroid: build centroid tree
        for u in adj[centroid]:
            if not removed[u]:
                child_centroid = decompose(u, centroid)
        return centroid

    return decompose(0, -1)
```

- **Build Time**: O(n log n)
- **Query/Activate**: O(log n) -- 沿 centroid tree 向上遍历 O(log n) 层祖先
- **Space**: O(n log n) for distance caches
- **Key Insight**: 重心分解将任意树变成深度 O(log n) 的平衡结构，使得路径查询从 O(n) 降到 O(log n)

**Follow-ups**:
- 如果树是动态的 (可以加边)? -> Link-Cut Tree
- 如何处理带权边? -> 在 BFS/DFS 预处理时记录距离

---

### Q5. Implement a Trie (prefix tree) data structure that supports insert, search, and ... ([LC 208](lc://208), 211, 212)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: trie, prefix-tree, word-search, DFS, backtracking, autocomplete

**题目**: Implement a Trie (prefix tree) data structure that supports insert, search, and startsWith operations. Then extend it to solve word search problems: given a board of characters and a list of words, find all words that can be formed by sequentially adjacent cells ([LC 212](lc://212))...

**解答**:

**思路**: Trie (前缀树/字典树) 是处理字符串前缀问题的核心数据结构。每个节点代表一个字符，从根到叶的路径构成完整单词。[LC 212](lc://212) Word Search II 将 Trie 与 DFS backtracking (回溯) 结合，在二维网格中高效搜索多个单词。

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, prefix: str) -> TrieNode | None:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

# Word Search II ([LC 212](lc://212)): Trie + DFS backtracking
def findWords(board: list[list[str]], words: list[str]) -> list[str]:
    trie = Trie()
    for w in words:
        trie.insert(w)

    rows, cols = len(board), len(board[0])
    result = set()

    def dfs(r, c, node, path):
        ch = board[r][c]
        if ch not in node.children:
            return
        node = node.children[ch]
        path += ch
        if node.is_end:
            result.add(path)
        board[r][c] = ''#''  # mark visited
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != ''#'':
                dfs(nr, nc, node, path)
        board[r][c] = ch  # restore

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")
    return list(result)
```

- **Trie insert/search**: O(L)，L = 单词长度
- **Word Search II**: O(M*N * 4^L) worst case，Trie 剪枝实际快很多
- **Space**: O(total characters across all words)

**Follow-ups**:
- 如何实现 autocomplete (返回所有匹配前缀的单词)? -> DFS 从前缀节点遍历所有子树
- 如何支持通配符搜索 ([LC 211](lc://211))? -> 遇到 ''.'' 时遍历所有 children
- 如何优化内存? -> Compressed trie (Patricia trie) 合并单链路径

---

### Q6. Given a nested list of integers (where each element is either an integer or a li... ([LC 339](lc://339), 364)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recursion, DFS, BFS, nested-list, weighted-sum

**题目**: Given a nested list of integers (where each element is either an integer or a list of integers, which may itself contain nested lists), compute the weighted sum. In [LC 339](lc://339), deeper elements have higher weight (depth * value)...

**解答**:

**思路**:
- **[LC 339](lc://339) (正向加权)**: depth * value，DFS 递归传入当前深度即可。
- **[LC 364](lc://364) (反向加权)**: 浅层权重更大。技巧：BFS 逐层处理，维护 unweighted 累加和。每深入一层，把 unweighted 再加到 weighted 上。浅层值被累加更多次 (maxDepth 次)，深层值只被累加 1 次。

```python
# [LC 339](lc://339): Nested List Weight Sum (depth * value)
def depthSum(nestedList) -> int:
    def dfs(lst, depth):
        total = 0
        for item in lst:
            if item.isInteger():
                total += item.getInteger() * depth
            else:
                total += dfs(item.getList(), depth + 1)
        return total
    return dfs(nestedList, 1)

# [LC 364](lc://364): Nested List Weight Sum II (reverse weight)
def depthSumInverse(nestedList) -> int:
    weighted, unweighted = 0, 0
    level = nestedList
    while level:
        next_level = []
        for item in level:
            if item.isInteger():
                unweighted += item.getInteger()
            else:
                next_level.extend(item.getList())
        weighted += unweighted  # 浅层值被反复累加
        level = next_level
    return weighted
```

- **Time**: O(n)，n = 所有嵌套元素总数
- **Space**: O(d)，d = 最大嵌套深度
- **Key Trick**: [LC 364](lc://364) 的 BFS 累加技巧避免了先求 maxDepth 再二次遍历

**Follow-ups**:
- 如何实现 NestedInteger 的 flatten iterator ([LC 341](lc://341))? -> 用 stack 惰性展开
- 如果嵌套层数可能很深导致栈溢出? -> 改用显式 stack 迭代

---

### Q7. Big data algorithm: Given a range (a, b), find the minimum convex value within t...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: digit-dp, big-data, number-theory, dynamic-programming, math

**题目**: Big data algorithm: Given a range (a, b), find the minimum convex value within that range. A convex number is one where adjacent digit differences alternate in sign (i.e., digits form a zigzag pattern, each digit is either a local minimum or local maximum compared to its neighbors)...

**解答**:

**思路**: Convex number (凸数) 的相邻数字差值正负交替 (zigzag pattern)。暴力检查每个数是 O((b-a)*D)，当范围很大时不可行。使用 Digit DP (数位 DP，数位动态规划) 逐位构造合法数字，状态包括：当前位、前一位数字、前一个差值方向、是否仍受上界限制。

```python
def count_convex_in_range(a: int, b: int) -> int:
    """Count convex (zigzag) numbers in [a, b]."""
    def count_up_to(n: int) -> int:
        digits = [int(d) for d in str(n)]
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def dp(pos, prev_digit, prev_dir, tight, started):
            # prev_dir: 1=up, -1=down, 0=not set
            if pos == len(digits):
                return 1 if started else 0
            limit = digits[pos] if tight else 9
            count = 0
            for d in range(0, limit + 1):
                if not started and d == 0:
                    count += dp(pos+1, -1, 0, False, False)
                    continue
                new_tight = tight and (d == limit)
                if not started or prev_digit == -1:
                    count += dp(pos+1, d, 0, new_tight, True)
                else:
                    diff = d - prev_digit
                    if diff == 0:
                        continue
                    new_dir = 1 if diff > 0 else -1
                    if prev_dir == 0 or new_dir != prev_dir:
                        count += dp(pos+1, d, new_dir, new_tight, True)
            return count
        return dp(0, -1, 0, True, False)

    return count_up_to(b) - count_up_to(a - 1)
```

- **Digit DP**: O(D * 10 * 3 * 2) states，D = 位数，远快于暴力
- **Key Technique**: Digit DP -- 逐位构建数字，用 tight 标记是否仍受上界约束

**Follow-ups**:
- 如何找 range 内的第 k 个 convex number? -> 二分搜索 + count_convex_up_to
- 如果 digits 可以是任意 base (非十进制)? -> 修改 limit 为 base-1

---

### Q8. N lockers are initially all closed

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: math, number-theory, perfect-squares, factors, brainteaser

**题目**: N lockers are initially all closed. In round n (for n = 1, 2, ..., N), you toggle the state of every locker whose number is a multiple of n...

**解答**:

**思路**: 第 k 个 locker (储物柜) 在第 n 轮被 toggle (切换) 当且仅当 n 是 k 的因子。因此 locker k 最终打开当且仅当 k 有奇数个因子。只有 perfect square (完全平方数) 有奇数个因子 (因为因子配对，只有平方根与自身配对)。

```python
import math

def open_lockers(n: int) -> list[int]:
    """Return list of open lockers after n rounds."""
    # 只有完全平方数编号的 locker 最终打开
    return [i*i for i in range(1, int(math.isqrt(n)) + 1)]

def count_open(n: int) -> int:
    """Count of open lockers = floor(sqrt(n))."""
    return int(math.isqrt(n))
```

- **Answer**: 打开的 locker 编号为 1, 4, 9, 16, ..., 即所有 <= N 的完全平方数
- **数学本质**: 因子个数为奇数 <=> 完全平方数
- **Time**: O(sqrt(n)) 枚举结果，O(1) 计算个数

**Follow-ups**:
- 如果不是从第 1 轮到第 N 轮, 而是只执行第 a 到第 b 轮? -> 统计每个柜子在 [a, b] 范围内的因子个数
- 如果 toggle 改为 "只有当柜子关着才打开"? -> 结果变为所有有因子在操作范围内的柜子都打开

---

### Q9. Given two Binary Search Trees (BSTs), find the deepest common ancestor of a node...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: BST, binary-search-tree, common-ancestor, tree-traversal, set-intersection

**题目**: Given two Binary Search Trees (BSTs), find the deepest common ancestor of a node that exists in both trees. The node must appear in both BSTs, and among all such common nodes, find the one at the greatest depth in either tree...

**解答**:

**思路**: 先找两棵 BST (Binary Search Tree，二叉搜索树) 的公共节点集合，然后找其中最深的。方法一：对 BST1 做中序遍历得排序数组，对 BST2 做中序遍历得排序数组，双指针求交集。方法二：BST1 的值存入 HashSet，遍历 BST2 查找交集并记录深度。

```python
def deepest_common_ancestor(root1, root2) -> int | None:
    """Find deepest node that exists in both BSTs."""
    # Step 1: Collect all values from BST1
    vals1 = set()
    def inorder(node):
        if not node:
            return
        inorder(node.left)
        vals1.add(node.val)
        inorder(node.right)
    inorder(root1)

    # Step 2: Find common nodes with max depth in BST2
    best_val, best_depth = None, -1
    def dfs(node, depth):
        nonlocal best_val, best_depth
        if not node:
            return
        if node.val in vals1 and depth > best_depth:
            best_depth = depth
            best_val = node.val
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)
    dfs(root2, 0)
    return best_val
```

- **Time**: O(n + m)，n, m 分别为两棵树的节点数
- **Space**: O(n)，存储 BST1 的值集合
- **Alternative**: 双指针法对两个排序数组求交集，空间 O(n+m)

**Follow-ups**:
- 如果两棵树非常大, 无法全部载入内存? -> 用 iterator 逐步合并 in-order 序列
- 如果要找 "最深的公共祖先" (LCA of common nodes)? -> 需要在同一棵树上找 LCA

---

### Q10. Big data coding: Given a large dataset of elements, apply a function f to each e...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: sorting, big-data, map-reduce, external-sort, function-mapping, parallel-computing

**题目**: Big data coding: Given a large dataset of elements, apply a function f to each element and return the sorted result efficiently. The function f may not be monotonic...

**解答**:

**思路**: 对大规模数据集应用函数 f 后排序。关键优化取决于 f 的性质：
1. **f 单调递增**: 先排序输入，再 map，结果自动有序。O(n log n)。
2. **f 单调递减**: 先排序输入，map 后反转。O(n log n)。
3. **f 非单调 (一般情况)**: map 后再排序。O(n log n)。无法利用输入顺序。
4. **大数据 (内存放不下)**: External Sort (外部排序) -- 分块读入内存排序，写入临时文件，再多路归并 (k-way merge)。MapReduce 框架天然支持。

```python
import heapq

def map_and_sort(data: list, f) -> list:
    """Apply f to each element and return sorted result."""
    mapped = [f(x) for x in data]  # O(n)
    mapped.sort()                   # O(n log n)
    return mapped

# External sort for big data (conceptual)
def external_sort(input_file: str, output_file: str, chunk_size: int):
    """Sort file too large for memory using external merge sort."""
    # Phase 1: Sort chunks in memory, write to temp files
    temp_files = []
    # ... read chunk_size elements, sort, write to temp file

    # Phase 2: K-way merge using min-heap
    # heapq.merge(*sorted_iterators) for efficient merging
    pass
```

- **General case**: O(n log n) sort + O(n) map
- **Monotonic f**: O(n log n) sort only (利用单调性跳过重新排序)
- **External Sort**: O(n log n) with O(chunk_size) memory，适合数据量 >> 内存

**Follow-ups**:
- 如果 f 是局部单调的 (piecewise monotonic)? -> 分段排序后归并
- 如何处理数据倾斜 (某些 f(x) 值特别集中)? -> 采样估计分布, 动态调整 partition 边界

---

### Q11. There are N coins with face values 0, 1, 2, 

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: dynamic-programming, modular-arithmetic, combinatorics, counting, knapsack

**题目**: There are N coins with face values 0, 1, 2, ..., N-1. You must pick exactly K coins...

**解答**:

**思路**: N 枚硬币面值 0 到 N-1，选恰好 K 枚，求总面值 mod M 的某个值的方案数。经典 knapsack DP (背包动态规划)：dp[i][j][r] = 从前 i 种硬币中选了 j 枚、总面值 mod M 余 r 的方案数。空间优化后只需 dp[j][r]。

```python
def count_ways(n: int, k: int, m: int, target_mod: int) -> int:
    """Count ways to pick exactly k coins from {0..n-1} with sum % m == target_mod."""
    # dp[j][r] = ways to pick j coins with sum % m == r
    dp = [[0] * m for _ in range(k + 1)]
    dp[0][0] = 1  # 0 coins, sum=0

    for coin in range(n):  # coin values 0..n-1
        # Traverse in reverse to avoid reusing same coin
        for j in range(min(k, coin + 1), 0, -1):
            for r in range(m):
                prev_r = (r - coin) % m
                dp[j][r] += dp[j - 1][prev_r]

    return dp[k][target_mod]
```

- **Time**: O(N * K * M)
- **Space**: O(K * M)
- **Key Technique**: Modular knapsack DP，状态压缩到 (选了几枚, 余数)

**Follow-ups**:
- 如果硬币可以重复选取? -> 去掉 j 的逆序遍历 (变为完全背包)
- 如果 M 很大怎么优化? -> NTT (Number Theoretic Transform) 加速多项式乘法

---

### Q12. Given a string containing digits from 2-9 inclusive, return all possible letter ... ([LC 17](lc://17))

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: backtracking, recursion, string, combinations

**题目**: Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent on a phone keypad. Return the answer in any order...

**解答**:

**思路**: Backtracking (回溯)。建立数字到字母的映射表，对每个数字尝试所有可能字母，递归生成组合。

```python
def letterCombinations(digits: str) -> list[str]:
    if not digits:
        return []
    phone = {
        ''2'': ''abc'', ''3'': ''def'', ''4'': ''ghi'', ''5'': ''jkl'',
        ''6'': ''mno'', ''7'': ''pqrs'', ''8'': ''tuv'', ''9'': ''wxyz''
    }
    result = []

    def backtrack(idx: int, path: list[str]):
        if idx == len(digits):
            result.append(''''.join(path))
            return
        for ch in phone[digits[idx]]:
            path.append(ch)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

- **Time**: O(4^N * N)，每个数字最多 4 种选择，生成长度 N 的字符串
- **Space**: O(N) 递归深度 (不含输出)
- **Key Technique**: Backtracking with explicit undo (回溯 + path.pop())

**Follow-ups**:
- 如何只返回在字典中存在的单词? -> 加 Trie 或 set 剪枝
- 如果按 T9 输入法, 需要返回最可能的单词? -> 频率加权 + Trie 前缀搜索

---

### Q13. Given a list of non-repetitive positive integers, find and output all maximal co... ([LC 128](lc://128)*)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: sorting, array, grouping, consecutive-sequence

**题目**: Given a list of non-repetitive positive integers, find and output all maximal consecutive subsequences. A consecutive subsequence is a group of numbers that form a contiguous range (e.g., [1,2,3,4])...

**解答**:

**思路**: 找所有最长连续子序列。两种方法：
1. **排序法**: O(n log n)，排序后线性扫描分组。
2. **HashSet 法**: O(n)，只从序列起点 (num-1 不在 set 中) 开始向右扩展。

```python
def find_consecutive_groups(nums: list[int]) -> list[list[int]]:
    """Find all maximal consecutive subsequences."""
    if not nums:
        return []
    num_set = set(nums)
    groups = []

    for num in num_set:
        if num - 1 not in num_set:  # 只从序列起点开始
            seq = [num]
            cur = num
            while cur + 1 in num_set:
                cur += 1
                seq.append(cur)
            groups.append(seq)

    return groups

# [LC 128](lc://128): Longest Consecutive Sequence
def longestConsecutive(nums: list[int]) -> int:
    num_set = set(nums)
    best = 0
    for num in num_set:
        if num - 1 not in num_set:
            length = 1
            while num + length in num_set:
                length += 1
            best = max(best, length)
    return best
```

- **HashSet**: O(n) time, O(n) space -- 每个元素最多被访问两次 (一次作为起点检查，一次在 while 中)
- **Sort**: O(n log n) time, O(1) extra space
- **Key Insight**: 只从 "起点" 开始扩展，避免重复计算

**Follow-ups**:
- 如何处理有重复元素的情况? -> 先去重 (用 set), 再按相同逻辑处理
- 如果数据是流式到达的? -> 用 Union-Find 动态合并连续区间

---

### Q14. SQL Problem: Given two tables - table1(user_id, article_id, date) recording user...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: SQL, inner-join, group-by, histogram, subquery, data-analysis

**题目**: SQL Problem: Given two tables - table1(user_id, article_id, date) recording user article views, and table2(article_id, article_type) mapping articles to types: (1) Count the number of article types each user viewed on 2019-01-01 using an inner join and group by. (2) Create a histogram showing the distribution of how many article types each user viewed, grouped by the count of article types.

**解题思路**:

**Part 1: 每个用户查看了多少种文章类型**

```sql
-- Part 1: Count distinct article types per user on 2019-01-01
SELECT t1.user_id,
       COUNT(DISTINCT t2.article_type) AS type_count
FROM table1 t1
INNER JOIN table2 t2 ON t1.article_id = t2.article_id
WHERE t1.date = ''2019-01-01''
GROUP BY t1.user_id;
```

**Part 2: 分布直方图** (有多少用户查看了 1 种类型, 多少用户查看了 2 种, ...)

```sql
-- Part 2: Histogram of type counts
WITH user_type_counts AS (
    SELECT t1.user_id,
           COUNT(DISTINCT t2.article_type) AS type_count
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.article_id = t2.article_id
    WHERE t1.date = ''2019-01-01''
    GROUP BY t1.user_id
)
SELECT type_count,
       COUNT(*) AS num_users
FROM user_type_counts
GROUP BY type_count
ORDER BY type_count;
```

**Python 等价实现** (用 pandas):

```python
import pandas as pd

def article_type_histogram(views_df: pd.DataFrame,
                           articles_df: pd.DataFrame) -> pd.DataFrame:
    # Filter date
    daily = views_df[views_df["date"] == "2019-01-01"]
    # Join
    merged = daily.merge(articles_df, on="article_id")
    # Count distinct types per user
    user_types = (merged.groupby("user_id")["article_type"]
                  .nunique().reset_index(name="type_count"))
    # Histogram
    histogram = (user_types.groupby("type_count")
                 .size().reset_index(name="num_users"))
    return histogram
```

**Follow-ups**:
- 如果要看一段时间内的趋势 (每天的直方图)? -> 加 date 维度 GROUP BY
- 如何排除只看了一次的噪声用户? -> 加 HAVING COUNT(*) >= threshold

**解答**:

```sql
-- (1) 每个用户在 2019-01-01 浏览的文章类型数
SELECT t1.user_id,
       COUNT(DISTINCT t2.article_type) AS type_count
FROM table1 t1
INNER JOIN table2 t2 ON t1.article_id = t2.article_id
WHERE t1.date = ''2019-01-01''
GROUP BY t1.user_id;

-- (2) 用户浏览类型数的分布直方图
SELECT type_count, COUNT(*) AS user_count
FROM (
    SELECT t1.user_id,
           COUNT(DISTINCT t2.article_type) AS type_count
    FROM table1 t1
    INNER JOIN table2 t2 ON t1.article_id = t2.article_id
    WHERE t1.date = ''2019-01-01''
    GROUP BY t1.user_id
) sub
GROUP BY type_count
ORDER BY type_count;
```

- **Key SQL Techniques**: INNER JOIN + GROUP BY + COUNT(DISTINCT) 用于分类统计；子查询 (subquery) 实现二次聚合生成 histogram (直方图)
- **注意**: 使用 COUNT(DISTINCT article_type) 而非 COUNT(*)，因为同一用户可能多次浏览同类型文章

---

### Q15. SQL + Python: Given tables video_posts(post_date, memberid, video_length) and me...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: SQL, python, data-analysis, hypothesis-testing, join, aggregation

**题目**: SQL + Python: Given tables video_posts(post_date, memberid, video_length) and members(memberid, country, join_date), analyze video upload patterns. Write SQL queries to: (1) Find average video count and total video length per member segmented by US vs non-US...

**解题思路**:

**Part 1: SQL -- US vs non-US video statistics**

```sql
-- Average video count and total video length per member, segmented by US/non-US
SELECT
    CASE WHEN m.country = ''US'' THEN ''US'' ELSE ''Non-US'' END AS segment,
    COUNT(DISTINCT v.memberid) AS num_members,
    COUNT(*) AS total_videos,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT v.memberid), 2) AS avg_videos_per_member,
    SUM(v.video_length) AS total_video_length,
    ROUND(SUM(v.video_length) * 1.0 / COUNT(DISTINCT v.memberid), 2) AS avg_length_per_member
FROM video_posts v
INNER JOIN members m ON v.memberid = m.memberid
GROUP BY CASE WHEN m.country = ''US'' THEN ''US'' ELSE ''Non-US'' END;
```

**Part 2: Python -- Hypothesis Testing (假设检验)**

检验 US 用户是否比 non-US 上传更多视频:

```python
import pandas as pd
from scipy import stats

def test_video_upload_difference(
    video_posts: pd.DataFrame, members: pd.DataFrame
) -> dict:
    # Merge tables
    merged = video_posts.merge(members, on="memberid")
    merged["is_us"] = merged["country"] == "US"

    # Count videos per member
    per_member = (merged.groupby(["memberid", "is_us"])
                  .size().reset_index(name="video_count"))

    us_counts = per_member[per_member["is_us"]]["video_count"]
    non_us_counts = per_member[~per_member["is_us"]]["video_count"]

    # Two-sample t-test (Welch''s t-test for unequal variances)
    t_stat, p_value = stats.ttest_ind(us_counts, non_us_counts,
                                       equal_var=False)

    return {
        "us_mean": us_counts.mean(),
        "non_us_mean": non_us_counts.mean(),
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant_at_005": p_value < 0.05,
    }
```

**Follow-ups**:
- 如何控制 confounders (如 join_date, country 发展水平)? -> 倾向得分匹配 (Propensity Score Matching, PSM) 或回归分析
- 如果样本量差异很大 (US 远多于 non-US)? -> 使用 bootstrap resampling 或 Mann-Whitney U test

**解答**:

```sql
-- (1) 按 US vs non-US 分段统计每个用户的视频数和总时长
SELECT
    CASE WHEN m.country = ''US'' THEN ''US'' ELSE ''Non-US'' END AS segment,
    COUNT(v.memberid) * 1.0 / COUNT(DISTINCT v.memberid) AS avg_video_count,
    SUM(v.video_length) AS total_video_length,
    COUNT(DISTINCT v.memberid) AS member_count
FROM video_posts v
JOIN members m ON v.memberid = m.memberid
GROUP BY CASE WHEN m.country = ''US'' THEN ''US'' ELSE ''Non-US'' END;

-- (2) 按加入时间队列分析视频上传趋势
SELECT
    DATE_TRUNC(''month'', m.join_date) AS cohort,
    CASE WHEN m.country = ''US'' THEN ''US'' ELSE ''Non-US'' END AS segment,
    COUNT(*) AS video_count
FROM video_posts v
JOIN members m ON v.memberid = m.memberid
GROUP BY cohort, segment
ORDER BY cohort;
```

```python
# Python: Hypothesis testing -- US vs Non-US video upload frequency
from scipy import stats
import pandas as pd

def test_video_upload_difference(df_us: pd.Series, df_non_us: pd.Series):
    """Two-sample t-test for video upload frequency."""
    t_stat, p_value = stats.ttest_ind(df_us, df_non_us, equal_var=False)
    alpha = 0.05
    print(f"t-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")
    if p_value < alpha:
        print("Reject H0: US and non-US upload rates differ significantly")
    else:
        print("Fail to reject H0: No significant difference")
    return t_stat, p_value
```

- **SQL**: JOIN + CASE WHEN 实现分段聚合；DATE_TRUNC 用于队列 (cohort) 分析
- **Python**: Welch''s t-test (不假设方差相等) 检验两组均值差异
- **Follow-up**: 还可以做 Mann-Whitney U test (非参数检验) 如果数据不服从正态分布

---

## ML Theory & Coding (8 题)

### Q16. Explain the Transformer architecture in detail

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: transformer, attention, self-attention, multi-head-attention, positional-encoding, model-validation

**题目**: Explain the Transformer architecture in detail. Describe the encoder and decoder components, self-attention mechanism, multi-head attention, and positional encoding...

**解题思路**:

**核心架构** (来自 "Attention Is All You Need", Vaswani et al. 2017):

**1. Self-Attention (自注意力)**:
- 输入 X 线性映射为 Q (Query), K (Key), V (Value)
- Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
- d_k 是 key 维度, 除以 sqrt(d_k) 防止 softmax 饱和

**2. Multi-Head Attention (MHA，多头注意力)**:
- 将 Q, K, V 分成 h 个 head, 每个 head 独立计算 attention, 最后 concat + linear
- 不同 head 可以关注不同的语义子空间 (如句法关系 vs 语义关系)

**3. Positional Encoding (PE，位置编码)**:
- Transformer 没有 RNN 的序列顺序, 需要显式注入位置信息
- 原始方法: PE(pos, 2i) = sin(pos / 10000^(2i/d)), PE(pos, 2i+1) = cos(...)
- 现代方法: learned positional embeddings 或 RoPE (Rotary Position Embedding)

**4. Encoder**: N 层, 每层 = Multi-Head Self-Attention + FFN (Feed-Forward Network), 每个子层后加 LayerNorm + residual connection。

**5. Decoder**: N 层, 每层 = Masked Self-Attention + Cross-Attention (attend to encoder output) + FFN。Masked attention 防止看到未来 token。

```python
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor, mask=None) -> torch.Tensor:
        B, L, _ = x.shape
        Q = self.W_q(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        scores = Q @ K.transpose(-2, -1) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))
        attn = torch.softmax(scores, dim=-1)
        out = (attn @ V).transpose(1, 2).contiguous().view(B, L, -1)
        return self.W_o(out)
```

**关键面试点**:
- Self-attention 复杂度 O(n^2 * d), n 是序列长度 -- 长文本的瓶颈
- Pre-norm vs Post-norm: 现代实践多用 Pre-norm (LayerNorm 在 attention 之前)
- Decoder-only (GPT) vs Encoder-only (BERT) vs Encoder-Decoder (T5): 不同任务适合不同架构

**Follow-ups**:
- 如何解决 O(n^2) 复杂度? -> Flash Attention, Sparse Attention, Linear Attention
- BERT vs GPT 的核心区别? -> 双向 vs 单向 attention; MLM vs causal LM
- 为什么用 LayerNorm 而非 BatchNorm? -> 序列长度不固定, BN 统计量不稳定

**解答**:

**Transformer 架构核心组件**:

**1. Self-Attention (自注意力机制)**:
- 输入序列中每个 token 计算与其他所有 token 的相关性权重
- 公式: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
- Q (Query), K (Key), V (Value) 分别由输入乘以学习到的权重矩阵得到
- sqrt(d_k) 缩放因子防止点积过大导致 softmax 梯度消失

**2. Multi-Head Attention (多头注意力)**:
- 将 Q, K, V 拆分为 h 个头，每个头独立计算 attention，最后 concat + linear projection
- 好处：不同 head 可以关注不同的语义关系 (syntactic vs semantic)
- MultiHead(Q,K,V) = Concat(head_1, ..., head_h) * W_O

**3. Positional Encoding (位置编码)**:
- Transformer 无内置序列顺序感知 (与 RNN (Recurrent Neural Network，循环神经网络) 不同)
- 使用 sin/cos 函数生成位置编码: PE(pos, 2i) = sin(pos / 10000^(2i/d))
- 可学习位置编码 vs 固定 sinusoidal -- 实践中效果相近

**4. Encoder**: N 层堆叠，每层 = Multi-Head Self-Attention + FFN (Feed-Forward Network，前馈网络) + LayerNorm + Residual Connection
**5. Decoder**: 额外加入 Masked Self-Attention (防止看到未来 token) + Cross-Attention (关注 encoder 输出)

```python
import torch
import torch.nn as nn
import math

class ScaledDotProductAttention(nn.Module):
    def forward(self, Q, K, V, mask=None):
        d_k = Q.size(-1)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float(''-inf''))
        attn = torch.softmax(scores, dim=-1)
        return torch.matmul(attn, V), attn
```

- **Time Complexity**: O(n^2 * d) per layer，n = sequence length, d = dimension
- **Key Trade-off**: Self-attention 是 O(n^2)，限制了长序列处理。改进：Flash Attention, Sparse Attention, Linear Attention

---

### Q17. You are testing whether changing an email''s headline and content affects engagem...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: ab-testing, multivariate-testing, hypothesis-testing, statistics, experiment-design, email-campaign

**题目**: You are testing whether changing an email''s headline and content affects engagement (open rate, click-through rate). How would you design and analyze this experiment? Discuss multivariate testing, hypothesis formulation, significance testing, and potential pitfalls.

**解题思路**:

**实验设计 -- 2x2 Factorial Design (全因子设计)**:
- Factor A: Headline (old vs new)
- Factor B: Content (old vs new)
- 4 组: (old headline, old content), (old, new), (new, old), (new, new)
- 比 A/B test 更优: 可以检测 interaction effect (两个因素组合效应)

**假设检验框架**:
1. H0: 新 headline/content 不影响 CTR (Click-Through Rate，点击率)
2. H1: 至少一个 factor 影响 CTR
3. 显著性水平 alpha = 0.05, 需做 multiple comparison correction

**样本量计算**:

```python
from scipy import stats
import numpy as np

def sample_size_proportion(
    p1: float, p2: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    """Minimum sample size per group for two-proportion z-test."""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    p_bar = (p1 + p2) / 2
    n = ((z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) +
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 /
         (p1 - p2) ** 2)
    return int(np.ceil(n))

# Example: detect CTR change from 5% to 6%
n = sample_size_proportion(0.05, 0.06)
print(f"Need {n} users per group")  # ~4669 per group
```

**分析步骤**:
1. Chi-squared test 或 two-proportion z-test 比较每组 CTR
2. 用 Bonferroni correction 修正多重比较 (4 组有 6 对比较)
3. 用 two-way ANOVA 或 logistic regression 检测 interaction effect

**常见陷阱**:
- **Novelty effect**: 新版本短期 CTR 高是因为新鲜感, 需要足够长的实验周期
- **Network effect**: 如果用户互相影响 (如分享邮件), 需要 cluster-level randomization
- **Multiple metrics**: open rate 和 CTR 是两个指标, 需要调整 alpha (如 alpha/2)
- **Selection bias**: 确保随机分组, 检查 pre-experiment balance

**Follow-ups**:
- 如何在 early stopping 和 statistical validity 之间取平衡? -> Sequential testing (如 O''Brien-Fleming bounds)
- 如果 sample size 不够, 如何提高 power? -> 使用 CUPED (Controlled-experiment Using Pre-Experiment Data) 降低方差

**解答**:

**实验设计**:
- **Factorial Design (析因设计)**: 2 个因子 (headline, content) 各 2 水平 = 2x2 = 4 组
  - Group A: 原 headline + 原 content (control)
  - Group B: 新 headline + 原 content
  - Group C: 原 headline + 新 content
  - Group D: 新 headline + 新 content
- **随机分配**: 用户随机分到 4 组，确保组间基线特征均衡

**Hypothesis (假设)**:
- H0: 新 headline/content 对 open rate 和 CTR (Click-Through Rate，点击率) 无显著影响
- H1: 至少一个因子有显著影响
- 需要检验 main effects (主效应) 和 interaction effect (交互效应)

**Sample Size (样本量)**:
- 使用 power analysis: 设定 alpha=0.05, power=0.80, MDE (Minimum Detectable Effect，最小可检测效果)
- 对于比例数据: n = (Z_alpha/2 + Z_beta)^2 * (p1(1-p1) + p2(1-p2)) / (p1-p2)^2

**Analysis (分析)**:
- Open rate: proportion z-test 或 chi-squared test
- CTR: 同上，但注意 CTR = clicks/opens (条件概率)
- 交互效应: 用 two-way ANOVA (Analysis of Variance，方差分析) 或 logistic regression

**Pitfalls (常见陷阱)**:
1. **Multiple comparisons**: 4 组 = 6 pairs，需要 Bonferroni correction (alpha/6)
2. **Novelty effect**: 新邮件短期内可能因新鲜感而表现好
3. **Email delivery bias**: 不同 headline 可能触发不同的 spam filter 行为
4. **Day-of-week effect**: 确保各组在同一时间段发送
5. **Metric coupling**: open rate 和 CTR 不独立 -- CTR 取决于 opens

---

### Q18. LinkedIn hypothesizes that video posting features might not be catching on inter...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: hypothesis-testing, two-sample-test, t-test, proportion-test, SQL, python

**题目**: LinkedIn hypothesizes that video posting features might not be catching on internationally as well as in the US. Given two tables - video_posts(post_date, memberid, video_length) and members(memberid, country, join_date) - test whether US members upload more videos than non-US members...

**解题思路**:

**Step 1: SQL 数据准备**

```sql
-- Per-member video count, segmented by US/non-US
SELECT m.memberid,
       CASE WHEN m.country = ''US'' THEN 1 ELSE 0 END AS is_us,
       COUNT(v.memberid) AS video_count
FROM members m
LEFT JOIN video_posts v ON m.memberid = v.memberid
GROUP BY m.memberid, is_us;
```

注意用 LEFT JOIN: 没有发过视频的用户 video_count = 0, 不能丢弃他们。

**Step 2: Python 假设检验**

```python
import pandas as pd
from scipy import stats

def test_us_vs_nonus(members_df: pd.DataFrame,
                     videos_df: pd.DataFrame) -> dict:
    # Count videos per member
    video_counts = (videos_df.groupby("memberid")
                    .size().reset_index(name="count"))
    merged = members_df.merge(video_counts, on="memberid", how="left")
    merged["count"] = merged["count"].fillna(0)
    merged["is_us"] = merged["country"] == "US"

    us = merged[merged["is_us"]]["count"]
    non_us = merged[~merged["is_us"]]["count"]

    # Welch''s t-test (unequal variance)
    t_stat, p_value = stats.ttest_ind(us, non_us, equal_var=False)

    # Also test proportion of "active posters" (at least 1 video)
    us_active = (us > 0).sum()
    non_us_active = (non_us > 0).sum()
    # Two-proportion z-test
    count = [us_active, non_us_active]
    nobs = [len(us), len(non_us)]
    z_stat, p_prop = stats.proportions_ztest(count, nobs)

    return {
        "us_mean": us.mean(),
        "non_us_mean": non_us.mean(),
        "t_test_p": p_value,
        "proportion_test_p": p_prop,
    }
```

**关键考虑**:
- **Confounders**: join_date (新用户可能不熟悉功能), 国家的互联网基础设施差异
- **Simpson''s Paradox**: 某些国家用户基数大但活跃度低, 聚合后可能掩盖趋势
- **Practical significance vs Statistical significance**: p < 0.05 不代表差异有业务意义, 需要看 effect size (如 Cohen''s d)

**Follow-ups**:
- 如果发现确实有差距, 如何决定是否值得为国际市场投入优化? -> 估算 ROI: 国际市场用户增长潜力 x 预期 engagement 提升
- 如何排除 join_date 的 confounding effect? -> 按 cohort 分层分析或用回归控制

**解答**:

**Step 1: SQL -- 提取数据**:
```sql
-- 每个用户的视频上传数量，按 US/non-US 分组
SELECT
    m.memberid,
    CASE WHEN m.country = ''US'' THEN ''US'' ELSE ''Non-US'' END AS segment,
    COUNT(v.memberid) AS video_count
FROM members m
LEFT JOIN video_posts v ON m.memberid = v.memberid
GROUP BY m.memberid, segment;
```

**Step 2: Python -- 假设检验**:
```python
from scipy import stats
import numpy as np

# us_counts, non_us_counts: 每个用户的视频上传数量
def test_video_adoption(us_counts: np.ndarray, non_us_counts: np.ndarray):
    # (1) Welch''s t-test (不假设方差相等)
    t_stat, p_val = stats.ttest_ind(us_counts, non_us_counts, equal_var=False)
    print(f"Welch t-test: t={t_stat:.3f}, p={p_val:.4f}")

    # (2) Mann-Whitney U test (非参数，适合偏态分布)
    u_stat, p_val_mw = stats.mannwhitneyu(us_counts, non_us_counts, alternative=''greater'')
    print(f"Mann-Whitney U: U={u_stat:.0f}, p={p_val_mw:.4f}")

    # (3) Effect size (Cohen''s d)
    pooled_std = np.sqrt((us_counts.std()**2 + non_us_counts.std()**2) / 2)
    cohens_d = (us_counts.mean() - non_us_counts.mean()) / pooled_std
    print(f"Cohen''s d = {cohens_d:.3f}")
```

**Key Considerations**:
- **One-sided test**: H1 是 "US > Non-US"，使用 alternative=''greater''
- **Effect size**: 即使统计显著，Cohen''s d 很小说明实际差异不大
- **Confounders**: 加入时间 (join_date)、活跃度等可能混淆因素应控制
- **视频上传为 0 的用户**: LEFT JOIN 确保包含从未上传的用户

---

### Q19. Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: advertising-metrics, CPC, CPM, cost-metrics, product-sense, LinkedIn-ads

**题目**: Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions) metrics. When would you use each? How do you decide which pricing model is better for an advertising campaign on LinkedIn?

**解题思路**:

**CPC (Cost Per Click，每次点击费用)**:
- 广告主按点击付费。CPC = Total Ad Spend / Total Clicks
- 适用场景: 转化导向 (lead generation, job applications, website visits)
- 优点: 只为实际兴趣付费; 缺点: 可能有 click fraud, 高竞争关键词 CPC 很贵

**CPM (Cost Per Mille，每千次展示费用)**:
- 广告主按展示次数付费。CPM = (Total Ad Spend / Total Impressions) * 1000
- 适用场景: 品牌曝光 (brand awareness campaigns)
- 优点: 可预测成本, 适合大量曝光; 缺点: 展示不等于关注, 效果难衡量

**选择框架**:

| 维度 | 选 CPC | 选 CPM |
|------|--------|--------|
| 目标 | Direct response, conversion | Brand awareness, reach |
| 预算 | 按效果付费, 风险低 | 按量付费, 适合大预算 |
| CTR 预期 | CTR 低时 CPC 更划算 | CTR 高时 CPM 更划算 |
| 衡量 | 点击数, 转化率 | 展示数, reach, brand lift |

**Equivalent CPM** (eCPM): 用于跨模型比较。eCPM = CPC * CTR * 1000。

```python
def compare_pricing(cpc: float, cpm: float, expected_ctr: float) -> str:
    """Recommend CPC or CPM based on expected CTR."""
    ecpm_from_cpc = cpc * expected_ctr * 1000
    if ecpm_from_cpc < cpm:
        return f"CPC is cheaper: eCPM=${ecpm_from_cpc:.2f} < CPM=${cpm:.2f}"
    return f"CPM is cheaper: CPM=${cpm:.2f} < eCPM=${ecpm_from_cpc:.2f}"

# Example: CPC=$2, CPM=$10, expected CTR=0.8%
print(compare_pricing(2.0, 10.0, 0.008))
# "CPC is cheaper: eCPM=$16.00 < CPM=$10.00" -> actually CPM is cheaper here
```

**LinkedIn 特有考虑**:
- LinkedIn 用户意图明确 (professional context), CTR 通常高于其他平台
- LinkedIn Ads 还支持 CPS (Cost Per Send, InMail), CPV (Cost Per View, video ads)
- 对于 B2B marketing, CPC 通常更受欢迎因为 lead quality 更可控

**Follow-ups**:
- 如何设计一个 ad auction system 同时支持 CPC 和 CPM bidders? -> 统一用 eCPM 排名
- 如何检测和防止 click fraud? -> 异常检测: 同 IP 高频点击, bot 行为模式识别

**解答**:

**CPC (Cost Per Click，每次点击费用)**:
- 广告主仅在用户点击广告时付费
- CPC = Total Spend / Total Clicks
- **适用场景**: 目标是 conversion (转化) -- 求职申请、注册、下载
- **优势**: 直接衡量用户意图，ROI (Return on Investment，投资回报率) 易计算
- **劣势**: 高竞争行业 CPC 很高；可能遇到 click fraud (点击欺诈)

**CPM (Cost Per Mille，每千次展示费用)**:
- 广告主为每 1000 次广告展示付费，不管是否点击
- CPM = (Total Spend / Total Impressions) * 1000
- **适用场景**: 目标是 brand awareness (品牌知名度) -- 新产品发布、招聘品牌
- **优势**: 确保曝光量，适合 top-of-funnel (漏斗顶部) 营销
- **劣势**: 展示不等于关注，实际效果难衡量

**决策框架**:
| 因素 | 选 CPC | 选 CPM |
|------|--------|--------|
| Campaign Goal | 转化驱动 (求职申请, 注册) | 品牌曝光 |
| Budget | 有限预算，追求效率 | 充足预算，追求覆盖 |
| CTR Expectation | 低 CTR (展示多但点击少) | 高 CTR (CPM 更划算) |
| Measurement | 易衡量 conversion | 需要额外 brand lift study |

**LinkedIn 特有考虑**: LinkedIn 广告的平均 CPC 较高 ($5-8 vs Google $1-2)，因为用户质量高 (professionals)。对于 B2B lead generation (商业线索生成)，CPC 通常更合适。

---

### Q20. Design and implement a sparse vector and sparse matrix representation from scrat... ([LC 1573](lc://1573), 311)

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: sparse-vector, sparse-matrix, data-structures, optimization, hash-map, dot-product

**题目**: Design and implement a sparse vector and sparse matrix representation from scratch. Define the constructor, attributes, and methods...

**解答**:

**思路**: 稀疏数据只存储非零元素。Sparse Vector (稀疏向量) 用 dict {index: value}；Sparse Matrix (稀疏矩阵) 用 dict of dicts 或 CSR (Compressed Sparse Row，压缩行存储) 格式。

```python
class SparseVector:
    """[LC 1573](lc://1573): Dot Product of Two Sparse Vectors."""
    def __init__(self, nums: list[int]):
        self.nonzero = {i: v for i, v in enumerate(nums) if v != 0}

    def dotProduct(self, vec: ''SparseVector'') -> int:
        # 遍历较短的一方，O(min(k1, k2))
        if len(self.nonzero) > len(vec.nonzero):
            return vec.dotProduct(self)
        return sum(
            v * vec.nonzero[i]
            for i, v in self.nonzero.items()
            if i in vec.nonzero
        )

class SparseMatrix:
    """[LC 311](lc://311): Sparse Matrix Multiplication."""
    def __init__(self, mat: list[list[int]]):
        self.rows = len(mat)
        self.cols = len(mat[0]) if mat else 0
        # row -> {col: val} for non-zero entries
        self.data = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if mat[r][c] != 0:
                    self.data.setdefault(r, {})[c] = mat[r][c]

    def multiply(self, other: ''SparseMatrix'') -> list[list[int]]:
        result = [[0] * other.cols for _ in range(self.rows)]
        for r, cols_a in self.data.items():
            for k, val_a in cols_a.items():
                if k in other.data:
                    for c, val_b in other.data[k].items():
                        result[r][c] += val_a * val_b
        return result
```

- **Sparse Vector Dot Product**: O(min(k1, k2))，k = 非零元素数
- **Sparse Matrix Multiply**: O(nnz_A * avg_nnz_per_row_B)，远快于 O(n^3) dense multiplication
- **Key Insight**: 只遍历非零元素，跳过大量零值计算

**Follow-ups**:
- 如何高效实现 transpose? -> 交换 row/col 索引即可, O(nnz)
- 对于超大矩阵如何分布式计算? -> Block partition + MapReduce
- CSR vs COO vs CSC 格式的区别? -> CSR 适合行切片, CSC 适合列切片, COO 适合构建

---

### Q21. Implement weighted random sampling from a multinomial distribution

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: sampling, multinomial, probability, binary-search, alias-method, random

**题目**: Implement weighted random sampling from a multinomial distribution. Given an array of n numbers representing weights/probabilities, write a function to sample an index according to those weights...

**解答**:

**思路**: 三种方法，复杂度递减：

**方法 1: Prefix Sum + Binary Search (前缀和 + 二分搜索)**:
- 构建累积概率数组，每次采样生成 random [0,1)，二分查找落入区间
- Build O(n), Sample O(log n)

**方法 2: Alias Method (别名方法)**:
- 将 n 个不等概率的桶重新分配为 n 个等概率的桶，每个桶最多装 2 种结果
- Build O(n), Sample O(1) -- 最优

```python
import random
import bisect

# Method 1: Prefix Sum + Binary Search
class WeightedSamplerBisect:
    def __init__(self, weights: list[float]):
        total = sum(weights)
        self.cumulative = []
        running = 0.0
        for w in weights:
            running += w / total
            self.cumulative.append(running)

    def sample(self) -> int:
        return bisect.bisect_left(self.cumulative, random.random())

# Method 2: Alias Method (O(1) sampling)
class AliasMethod:
    def __init__(self, weights: list[float]):
        n = len(weights)
        total = sum(weights)
        prob = [w * n / total for w in weights]
        self.alias = list(range(n))
        self.prob = [1.0] * n

        small, large = [], []
        for i, p in enumerate(prob):
            (small if p < 1.0 else large).append(i)

        while small and large:
            s, l = small.pop(), large.pop()
            self.prob[s] = prob[s]
            self.alias[s] = l
            prob[l] -= (1.0 - prob[s])
            (small if prob[l] < 1.0 else large).append(l)

    def sample(self) -> int:
        i = random.randint(0, len(self.prob) - 1)
        return i if random.random() < self.prob[i] else self.alias[i]
```

- **Prefix Sum**: Build O(n), Sample O(log n), Space O(n) -- 简单通用
- **Alias Method**: Build O(n), Sample O(1), Space O(n) -- 高频采样场景最优
- **Follow-up**: Reservoir sampling (蓄水池采样) 用于 streaming data (流式数据)

---

### Q22. Compare and contrast using open-source software vs building your own solution (b...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: open-source, build-vs-buy, engineering-decision, tradeoffs, discussion, software-engineering

**题目**: Compare and contrast using open-source software vs building your own solution (build vs buy). How would you make this decision for a machine learning project at a large company like LinkedIn? Discuss factors like maintainability, customization, security, community support, licensing, and cost.

**解题思路**:

**对比框架**:

| 维度 | Open Source (Buy/Adopt) | Build In-House |
|------|------------------------|----------------|
| **Time to market** | 快 -- 现成可用 | 慢 -- 从零开始 |
| **Customization** | 受限于项目架构 | 完全可控 |
| **Maintenance** | 社区维护, 但可能 abandon | 需要专门团队 |
| **Security** | 代码透明但也暴露攻击面 | 可以做更严格的内部审计 |
| **Cost** | 初始低, 但集成/运维成本可能高 | 初始高, 但长期成本可控 |
| **Licensing** | 需要审查 (GPL vs MIT vs Apache) | 无 license 风险 |
| **Talent** | 更多人熟悉主流 OSS | 需要培训或招聘 |

**决策框架 (Decision Matrix)**:

1. **Core vs Context**: 如果是公司核心竞争力 (如 LinkedIn 的 feed ranking), 自建; 如果是 context (如日志系统), 用 open source。
2. **Differentiation**: 如果需要高度定制且独特, 自建更合适。
3. **Maturity**: 如果 OSS 项目已经成熟稳定 (如 Kafka, Spark), 优先采用。
4. **Team capability**: 团队是否有能力维护自建系统?

**LinkedIn 实际案例**:
- **Adopt**: Kafka (消息队列), Spark (大数据处理), Lucene/Solr (搜索) -- 都是 LinkedIn 先采用后开源的
- **Build**: Voldemort (KV store), Samza (stream processing), Pro-ML (ML platform) -- 核心业务需要高度定制

**推荐回答结构**:
1. 先问清需求: 是否核心功能? 时间线? 团队规模?
2. 列出 Build vs Buy 各 3-4 个优缺点
3. 给出 decision matrix 评分
4. 提出 hybrid approach: 用 OSS 做基础, 在上层自建定制层

**Follow-ups**:
- 如何评估一个 OSS 项目的 health? -> Stars, commit frequency, issue response time, license, backing company
- 如果选了 OSS 后发现不满足需求? -> Fork + maintain internally (如 LinkedIn 对 Kafka 的贡献)

**解答**:

**决策矩阵**:

| 维度 | Open Source (开源) | Build In-House (自研) |
|------|-------------------|----------------------|
| **Time to Market** | 快 -- 现成解决方案 | 慢 -- 需要开发周期 |
| **Customization** | 受限于现有 API | 完全定制 |
| **Maintenance** | 社区维护，但升级可能 break | 团队全权负责 |
| **Security** | 代码公开可审计，但漏洞也公开 | 内部控制，但审计资源有限 |
| **Cost** | 免费但有隐性运维成本 | 高开发成本但长期可控 |
| **Talent** | 降低招聘门槛 (通用技能) | 需要专门人才 |
| **Licensing** | 注意 GPL/AGPL 传染性 | 无许可证风险 |

**LinkedIn/大厂语境下的考量**:
1. **Core vs Context**: 核心竞争力 (ranking, recommendation) 自研；基础设施 (monitoring, logging) 用开源
2. **规模因素**: LinkedIn 规模 (500M+ users) 下，通用开源工具可能性能不足，需要定制
3. **实际案例**: LinkedIn 自研 Voldemort (KV store), Kafka (messaging) 而非用现有方案
4. **ML Frameworks**: 通常用开源 (PyTorch, TensorFlow) + 自研训练/serving infrastructure
5. **决策流程**: 先用开源 PoC (Proof of Concept，概念验证)，验证后再决定是否自研替代

**推荐答题框架**: "对于 [specific ML project]，我会先评估：(1) 是否是核心竞争力，(2) 规模需求是否超出开源能力，(3) 团队维护能力。非核心 + 规模合适 => 开源；核心 + 定制需求高 => 自研。"

---

### Q23. Which LinkedIn product do you like most and why

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: easy
- **Tags**: product-sense, LinkedIn-products, behavioral, product-analysis, discussion

**题目**: Which LinkedIn product do you like most and why? Demonstrate your understanding of LinkedIn''s product ecosystem and your product sense by analyzing a specific feature - its value proposition, target users, key metrics, and potential improvements.

**解题思路 (以 LinkedIn Feed 为例)**:

**1. Product Overview**:
LinkedIn Feed 是用户的主信息流, 通过算法 ranking 展示 connections 的动态、文章、招聘信息和广告。

**2. Value Proposition**:
- 对用户: 获取行业洞察, 保持 professional network 活跃
- 对 LinkedIn: 核心 engagement driver, 广告变现的主渠道
- 对 content creators: 建立 thought leadership, 扩大影响力

**3. Target Users**:
- Job seekers: 关注行业动态和招聘信息
- Professionals: networking 和 knowledge sharing
- Recruiters: 了解候选人动态和市场趋势
- B2B marketers: 内容营销和 lead generation

**4. Key Metrics**:
- **Engagement**: DAU/MAU ratio, time spent in feed, scroll depth
- **Content quality**: Meaningful interactions (comments > reactions > views)
- **Revenue**: Ad revenue per session, CTR on sponsored posts
- **Creator health**: Post frequency, follower growth rate

**5. Potential Improvements**:
- **Content quality filtering**: 减少 engagement bait (如 "agree?" polls), 提高信息质量
- **Topic-based feed**: 允许用户按话题 (ML, product management, etc.) 筛选 feed
- **Better video experience**: 短视频整合, 类似 TikTok 但保持 professional tone
- **AI-powered summaries**: 对长文章提供 AI 摘要, 降低信息消费成本

**回答框架 (STAR-Product)**:
1. **选择**: 说明选了什么产品以及为什么
2. **分析**: 用户是谁, 核心价值, 竞争优势
3. **指标**: 如何衡量成功
4. **改进**: 2-3 个具体改进建议 + 预期影响

**Follow-ups**:
- 如何平衡 content creator 利益和 consumer experience? -> 双边市场平衡, 监控 creator retention 同时优化 consumer engagement
- 如何衡量 "meaningful engagement" vs 浅层互动? -> 基于 comments/shares 而非 likes, 用 time-spent-reading 作为 proxy

**解答**:

**示例回答: LinkedIn Feed Ranking (信息流排序)**

**1. Value Proposition (价值主张)**:
- 将最相关的专业内容推送给用户，提高信息获取效率
- 帮助 content creators 获得精准曝光
- 为 LinkedIn 创造广告收入基础 (feed ads)

**2. Target Users (目标用户)**:
- **Active Professionals**: 寻找行业 insights, job opportunities, networking
- **Content Creators**: 希望建立 professional brand (专业品牌)
- **Recruiters/Sales**: 通过内容触达潜在候选人/客户

**3. Key Metrics (核心指标)**:
- **Engagement**: DAU/MAU ratio, sessions per day, time spent in feed
- **Content Quality**: 有价值互动率 (comments vs likes), share rate
- **Creator Health**: 新 creator 留存率, 内容发布频率
- **Business**: Feed ad CTR, revenue per session, CPM

**4. Potential Improvements (改进方向)**:
- **Content Diversity**: 避免 echo chamber (信息茧房)，引入 exploration-exploitation 平衡
- **Professional Context**: 根据用户当前 career stage 调整内容 (job seeker vs hiring manager)
- **Quality Signal**: 区分 "engagement bait" 和真正有价值的专业内容
- **Cross-format**: 更好地融合 articles, videos, newsletters, polls 的混合排序

**答题技巧**: 选你最熟悉的产品，展示 (1) 对用户需求的深度理解，(2) 数据驱动的思维，(3) 可落地的改进建议。避免泛泛而谈。

---

## ML System Design (24 题)

### Q24. Design a distributed Key-Value Store that supports replication, sharding, and co...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: distributed-systems, key-value-store, replication, sharding, vector-clock, quorum

**题目**: Design a distributed Key-Value Store that supports replication, sharding, and consistency guarantees. Discuss concepts including replica placement, sharding strategies, vector clocks for conflict resolution, and read/write quorum protocols...

**解答**:

**Architecture (架构)**:

**1. Sharding (分片)**:
- **Consistent Hashing (一致性哈希)**: 将 key 映射到 hash ring 上，每个节点负责 ring 上的一段范围。添加/移除节点只影响相邻分片，数据迁移量 O(K/N)
- **Virtual Nodes**: 每个物理节点映射多个虚拟节点，改善负载均衡

**2. Replication (复制)**:
- N 个 replicas per partition (通常 N=3)
- **Replica Placement**: 不同 rack/AZ (Availability Zone，可用区) 部署，容灾

**3. Consistency (一致性)**:
- **Quorum Protocol**: W + R > N 保证强一致性 (W=写入确认数, R=读取节点数, N=副本数)
- 常见配置: N=3, W=2, R=2 (强一致) 或 W=1, R=1 (高可用/最终一致)
- **Vector Clock (向量时钟)**: 每个节点维护一个版本向量，检测并发写入冲突

**4. Conflict Resolution (冲突解决)**:
- Last-Writer-Wins (LWW，最后写入者胜): 简单但可能丢失数据
- Application-level merge: 让应用层决定如何合并冲突 (如 Amazon Dynamo 的 shopping cart)

**5. Failure Handling**:
- **Hinted Handoff**: 目标节点不可用时，写入临时代理节点，恢复后转移
- **Anti-Entropy (反熵)**: 后台 Merkle Tree 比对修复不一致数据

**Key Trade-off**: CAP Theorem (CAP 定理) -- Consistency, Availability, Partition Tolerance 三选二。LinkedIn 的 Voldemort 选择 AP (高可用 + 分区容错)，牺牲强一致性。

**Follow-ups**:
- 如何实现 cross-datacenter replication? -> Async replication + conflict resolution (CRDTs or vector clocks)
- 如何处理 hot keys (某些 key 访问量远超平均)? -> Read replicas, caching layer, key-level load balancing

---

### Q25. Design a metrics monitoring system for a large-scale distributed infrastructure ...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: metrics-monitoring, time-series-db, LSM-tree, indexing, observability, distributed-systems

**题目**: Design a metrics monitoring system for a large-scale distributed infrastructure like LinkedIn. Cover: choice of time-series database vs NoSQL, efficient indexing strategies for time-series data, LSM tree compaction principles, and how to collect system-level and application-level metrics from nodes and containers.

**解题思路**:

**系统架构**:

```
Agents (每台机器) -> Collector/Aggregator -> Message Queue (Kafka)
    -> Stream Processor -> Time-Series DB -> Query Engine -> Dashboard/Alerts
```

**1. Data Collection**:
- **System metrics**: CPU, memory, disk, network (用 node_exporter / collectd)
- **Application metrics**: request latency, error rate, throughput (用 StatsD / Micrometer)
- **Container metrics**: Docker/K8s cgroup stats
- Pull vs Push model: Prometheus 用 pull (主动拉取), StatsD 用 push (应用推送)

**2. 存储选型 -- Time-Series DB (TSDB，时序数据库)**:
- **InfluxDB / TimescaleDB / Prometheus**: 专为时序数据优化
- 优于普通 NoSQL 因为: 高效的时间范围查询, 自动 downsampling, retention policies
- **LSM Tree (Log-Structured Merge Tree)**: 写优化结构。数据先写入内存 MemTable, 满后 flush 到磁盘 SSTable (Sorted String Table), 后台 compaction 合并文件。

**3. Indexing**:
- 按 (metric_name, tags, timestamp) 索引
- Tag-based indexing: 支持按 host, service, region 等维度查询
- Time-partitioned storage: 按时间段分片, 旧数据自动归档/删除

**4. 查询和告警**:
- **Query**: 支持 aggregation (sum, avg, percentile), group by, downsampling
- **Alerting**: 基于阈值或异常检测, 多级告警 (warning -> critical -> page)

**5. Scale 考虑**:
- LinkedIn 规模: 数十万台机器, 每秒数百万 metric data points
- 水平扩展: Kafka 做缓冲, TSDB 分片存储
- Downsampling: 最近 24h 保留秒级数据, 1 周保留分钟级, 1 年保留小时级

**Follow-ups**:
- 如何实现异常检测 (anomaly detection) 而非简单阈值? -> 用 Prophet, ARIMA, 或 isolation forest 检测时序异常
- 如何减少 metric cardinality explosion (tag 组合爆炸)? -> 限制 tag 数量, 预聚合高基数 tags

**解答**:

**Architecture**:

**1. Data Collection Layer (数据采集层)**:
- **Agent-based**: 每台机器运行 metrics agent (类似 Telegraf/collectd)，采集 CPU, memory, disk, network
- **Application SDK**: 业务代码通过 SDK 上报自定义指标 (latency, error rate, throughput)
- **Push vs Pull**: Push (agent 主动发送) 适合短生命周期容器；Pull (Prometheus 模式) 适合稳定服务

**2. Ingestion & Storage (存储层)**:
- **TSDB (Time-Series Database，时序数据库)**: 专为时间序列优化
  - 写入密集: LSM Tree (Log-Structured Merge Tree) 结构，顺序写入 + 后台 compaction
  - 压缩: delta-of-delta encoding (时间戳), gorilla compression (浮点值)
  - 代表: InfluxDB, OpenTSDB, Prometheus
- **LSM Compaction**: MemTable -> L0 SSTable -> L1 -> ... 逐层合并，减少读放大
- **Data Retention**: 高精度数据保留 7 天，降采样 (downsampling) 后保留 1 年

**3. Indexing (索引)**:
- **Tag-based Index**: metric_name + tags (host, service, region) 的倒排索引
- **Time-partitioned**: 按时间分区，查询只扫描相关时间段

**4. Query & Alerting (查询与告警)**:
- **Dashboard**: Grafana 实时可视化
- **Alert Rules**: 基于阈值、趋势、异常检测 (如 3-sigma rule, EWMA (Exponentially Weighted Moving Average，指数加权移动平均))
- **Anomaly Detection**: 使用 ML 模型识别非 threshold-based 的异常模式

**Scalability**: 水平扩展存储节点 + 分片 by metric name hash。LinkedIn 的 inGraphs 系统处理 billions of metrics/day。

---

### Q26. Given a LinkedIn webpage showing user profile information, design a system to cl...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: classification, NLP, feature-engineering, text-classification, user-profiling, LinkedIn-profile

**题目**: Given a LinkedIn webpage showing user profile information, design a system to classify each user into a job category (e.g., software engineer, data scientist, product manager) and extract relevant attributes. How would you approach feature engineering, model selection, and handling edge cases like career changers or multi-role users?

**解题思路**:

**1. Problem Formulation**:
- Multi-class classification (可能 multi-label, 因为一个人可能有多个 role)
- 目标: 输入 profile -> 输出 job category + confidence score

**2. Feature Engineering**:
- **Text features**: headline, summary, job title, skills (TF-IDF (Term Frequency-Inverse Document Frequency) 或 BERT embeddings)
- **Structured features**: industry, company size, years of experience, education, skill endorsement counts
- **Graph features**: connections 的 job category 分布 (homophily -- 同行业的人倾向互相连接)
- **Behavioral features**: 关注的 groups, 点赞的 posts 的 topic 分布

**3. Model Selection**:
- **Baseline**: Logistic Regression / Random Forest on TF-IDF features
- **Production**: Fine-tuned BERT on headline + summary, 加上 structured features 的 MLP 分支
- **Multi-label**: Binary Relevance (每个 category 一个 classifier) 或 multi-label BERT

**4. Training Pipeline**:
- **Labels**: 用现有 standardized title + industry 作为 weak labels, 或 human annotation
- **Data augmentation**: 同义词替换, title 变体 (如 "SWE" = "Software Engineer")
- **Class imbalance**: Focal loss 或 oversampling rare categories

**5. Edge Cases**:
- **Career changers**: 用最近 N 年的 experience 加权, 而非全部历史
- **Multi-role users**: Multi-label 输出 + 每个 label 的 confidence
- **Incomplete profiles**: 缺少 headline/summary 时 fallback 到 skills + industry
- **Freelancers/Consultants**: 用 project descriptions 和 skills 而非 company/title

**6. Serving**:
- 实时: 新注册/更新 profile 时 trigger classification
- 批量: 定期重新分类所有用户 (捕捉 career transitions)

**Follow-ups**:
- 如何处理新兴 job categories (如 "AI Engineer" 几年前不存在)? -> 监控 unclassified rate, 定期用 clustering 发现新类别
- 如何保证 classification 不会产生 bias? -> 审查 demographic parity, 避免用 gender/race-correlated features

**解答**:

**1. Feature Engineering (特征工程)**:
- **Text Features**: title, headline, summary, experience descriptions -> TF-IDF (Term Frequency-Inverse Document Frequency) 或 BERT (Bidirectional Encoder Representations from Transformers) embeddings
- **Structured Features**: industry, skills (endorsed), education (degree, field), years of experience
- **Network Features**: 相似职位的 connections 比例，所在 company 的行业
- **Temporal Features**: 职位变化频率，最近职位的停留时间

**2. Model Architecture**:
- **Baseline**: Multi-class logistic regression / gradient boosted trees (XGBoost) on TF-IDF + structured features
- **Advanced**: Fine-tuned BERT on title + summary text，concat with structured features，feed into MLP (Multi-Layer Perceptron，多层感知机)
- **Label Taxonomy**: ~50-200 标准化职位类别 (可用 O*NET 或 LinkedIn 自有 taxonomy)

**3. Edge Cases (边缘情况)**:
- **Career Changers**: 使用最近的职位 (time-weighted) + skill endorsements 作为更强信号
- **Multi-role Users**: 支持 multi-label classification (每个用户可属于多个类别)，或按 primary/secondary 分类
- **Sparse Profiles**: 只有 title 没有 summary 的用户 -> 用 title 单特征模型作为 fallback

**4. Pipeline**:
- Offline batch: 定期重新分类所有用户 (daily/weekly)
- Online: 新注册用户 real-time 分类 (使用轻量模型)
- Feedback loop: 用户编辑 title/skills 时触发重新分类

**Evaluation**: Precision/Recall per category + macro-averaged F1。对高价值类别 (如 recruiter, executive) 重点关注。

---

### Q27. Design a system to help LinkedIn recruiters find suitable candidates for job ope...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: recommendation-system, ranking, matching, recruiter, talent-search, information-retrieval

**题目**: Design a system to help LinkedIn recruiters find suitable candidates for job openings. Cover the end-to-end pipeline: understanding recruiter intent, candidate retrieval, ranking, matching, and recommendation...

**解题思路**:

**End-to-End Pipeline**:

```
Recruiter Query -> Query Understanding -> Candidate Retrieval
    -> Ranking -> Filtering -> Results + Explanations
```

**1. Query Understanding**:
- 解析 recruiter 输入: job title, skills, location, experience, company preferences
- Query expansion: "ML Engineer" -> also search "Machine Learning Engineer", "AI Engineer"
- Intent classification: 是精确搜索还是探索性搜索

**2. Candidate Retrieval (召回层)**:
- **Inverted index**: 按 skills, title, location 索引
- **Embedding-based retrieval**: 将 job description 和 candidate profile encode 到同一向量空间, 用 ANN (Approximate Nearest Neighbor，近似最近邻) 搜索 (如 FAISS, HNSW)
- 目标: 从 500M+ 用户中快速召回 top-1000 candidates

**3. Ranking (排序层)**:
- **Features**:
  - Relevance: skill match score, title similarity, experience fit
  - Quality: profile completeness, endorsement count, activity level
  - Behavioral: 该候选人对类似 InMail 的历史 response rate
  - Contextual: 是否 open to work, 地理距离
- **Model**: Learning-to-Rank (LambdaMART 或 neural ranking model)
- **Training data**: recruiter click/response as positive, skip as negative

**4. Filtering & Business Rules**:
- 过滤已联系过的候选人
- 排除明确表示不感兴趣的用户
- Diversity: 确保结果不过度集中于某个公司/学校

**5. Metrics**:
- **Offline**: NDCG (Normalized Discounted Cumulative Gain), MRR (Mean Reciprocal Rank)
- **Online**: InMail response rate, time to fill position, recruiter return rate

**Follow-ups**:
- 如何处理 cold-start candidates (新用户, profile 信息少)? -> 用 collaborative filtering (类似用户的行为) + 要求完善 profile
- 如何避免 bias (如偏向某些学校/公司)? -> Fairness constraints on ranking, blind resume features

**解答**:

**End-to-End Pipeline**:

**1. Query Understanding (意图理解)**:
- 解析 recruiter 搜索: job title, skills, location, seniority, company type
- Query expansion: "ML Engineer" -> also search "Machine Learning", "Deep Learning", "AI Engineer"
- 使用 NLP (Natural Language Processing，自然语言处理) 提取结构化 intent

**2. Candidate Retrieval (候选人检索)**:
- **Stage 1 -- Recall (召回)**: 从 500M+ profiles 中快速筛选到 ~10K 候选人
  - Inverted index on skills, title, location
  - Embedding-based ANN (Approximate Nearest Neighbor，近似最近邻) 搜索: FAISS/ScaNN
- **Stage 2 -- Ranking (精排)**: 对 ~10K 候选人用复杂模型排序到 top 100
  - Features: skill match score, experience relevance, location fit, engagement signals (是否活跃求职)

**3. Matching Model**:
- **Two-tower model**: Recruiter intent embedding + Candidate profile embedding，计算 cosine similarity
- **Cross-attention model**: 将 job description 和 candidate profile 联合编码，捕获细粒度匹配
- **Training data**: 历史 InMail 回复 (positive), 查看但未联系 (negative)

**4. Key Features**:
- Skill overlap ratio, title semantic similarity, seniority match
- Candidate responsiveness (InMail 历史回复率)
- Geographic willingness (是否愿意 relocate)
- Network proximity (共同 connections)

**5. Trade-offs**:
- **Precision vs Recall**: Recruiter 宁可少看几个 (high precision) 也不想翻很多不相关的 (low precision)
- **Active vs Passive**: 主动求职者 vs 被动候选人的不同信号
- **Fairness**: 避免性别、年龄、种族偏差 -- 需要 bias audit 和 fairness constraints

---

### Q28. Design the metrics framework for LinkedIn''s job search and ranking module

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, job-search, ranking, CTR, product-metrics, evaluation

**题目**: Design the metrics framework for LinkedIn''s job search and ranking module. What metrics would you track (click-through rate, application rate, time spent, search frequency)? What features matter most for job ranking, and how would you measure the overall health of the job search experience?

**解题思路**:

**Metrics 分层框架**:

**1. North Star Metric (北极星指标)**: Successful job applications per active job seeker per week。衡量 end-to-end 价值。

**2. Primary Metrics**:
- **CTR (Click-Through Rate)**: job card clicks / impressions。衡量排序相关性。
- **Application Rate**: applications / job detail page views。衡量转化效率。
- **Search Success Rate**: % of searches leading to at least 1 click/application。
- **Time to Apply**: 从搜索到提交申请的平均时间。越短越好。

**3. Quality Metrics**:
- **Relevance Score**: 搜索结果与 query 的匹配度 (通过 human evaluation 或 user feedback)
- **Application-to-Interview Ratio**: 申请后获得面试的比例 (需要 recruiter 端数据)
- **Repeat Search Rate**: 高重复率说明搜索结果不满意
- **Zero-result Rate**: 搜索返回 0 结果的比例

**4. Engagement Metrics**:
- **Session depth**: 每次搜索会话浏览几个 job detail pages
- **Saved jobs rate**: 收藏率 (表示意向但未立即申请)
- **Return rate**: 用户多久回来搜索一次

**5. Job Ranking Features (重要性排序)**:
- **Query-job relevance**: title match, skill match, description similarity
- **Personalization**: user''s past applications, saved jobs, profile-job fit
- **Job freshness**: 新发布的 job 优先 (posting date)
- **Job quality signals**: company rating, salary range, application count
- **Geolocation**: distance/commute time

**Guardrail Metrics** (不能变差):
- Revenue per search (ad revenue)
- Job poster satisfaction (post-to-fill rate)
- User diversity (不过度推荐同一类 job)

**Follow-ups**:
- CTR 提升但 application rate 下降怎么办? -> 可能是标题 clickbait 导致; 需要 composite metric
- 如何衡量 job 推荐的 long-term value? -> 跟踪 hired + 6-month retention

**解答**:

**Metrics Hierarchy (指标层次)**:

**North Star Metric**: Qualified Applications per Searcher (每个搜索者的有效申请数)

**1. Funnel Metrics (漏斗指标)**:
- **Search -> Click**: CTR (Click-Through Rate) = clicks / impressions per search
- **Click -> Apply**: Application Rate = applications / job detail views
- **Apply -> Interview**: Response Rate (需要 employer 端数据)
- **Overall**: Search-to-Apply Rate = applications / searches

**2. Engagement Metrics**:
- Search frequency per user per week
- Avg jobs viewed per session
- Time spent on job detail page (区分 reading vs bouncing)
- Save/bookmark rate

**3. Quality Metrics**:
- **Relevance**: Position of clicked job in result list (MRR -- Mean Reciprocal Rank，平均倒数排名)
- **NDCG (Normalized Discounted Cumulative Gain，归一化折损累积增益)**: 评估排序质量
- **Zero-result rate**: 搜索无结果的比例 (越低越好)
- **Pogo-sticking rate**: 点击后快速返回搜索结果的比例 (表示结果不相关)

**4. Health Metrics**:
- DAU/WAU of job search feature
- Searcher retention (7-day, 30-day)
- Job seeker -> applied -> hired 的完整转化率

**Job Ranking Features**: title match, skill overlap, location distance, company size preference, seniority match, salary range, recency of posting, employer responsiveness score

---

### Q29. Design LinkedIn''s feed ranking system

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: feed-ranking, recommendation, features, engagement, content-ranking, multi-objective

**题目**: Design LinkedIn''s feed ranking system. What features would you consider for ranking content in a user''s feed? Cover content features, user features, interaction features, and how you would balance relevance, engagement, and content diversity.

**解题思路**:

**系统架构 (Multi-stage Pipeline)**:

```
Candidate Generation -> First-pass Ranking -> Second-pass Ranking
    -> Diversity/Business Rules -> Final Feed
```

**1. Candidate Generation (召回)**:
- **Network posts**: 1st/2nd degree connections 的动态
- **Topic-based**: 用户关注 topic 的热门内容
- **Collaborative filtering**: 类似用户互动过的内容
- 目标: 从数百万候选 post 中召回 ~1000 个

**2. Feature Categories**:

**Content features**:
- Content type (text, image, video, article, poll)
- Content length, language, hashtags
- Creator credibility (follower count, engagement history)
- Content freshness (posting time)

**User features**:
- Industry, job title, seniority level
- Historical engagement patterns (偏好 video vs text)
- Active time patterns, device type

**Interaction features (user x content)**:
- User-creator relationship (connection degree, interaction history)
- Topic affinity score
- 用户对类似 content 的历史 CTR

**3. Ranking Model**:
- **Multi-objective optimization**: 同时预测多个目标
  - P(click), P(like), P(comment), P(share), P(long_dwell_time)
- Final score = w1*P(click) + w2*P(comment) + w3*P(share) - w4*P(hide)
- Model: GBDT (Gradient Boosted Decision Tree) 或 deep neural network (wide & deep)

**4. Diversity & De-duplication**:
- MMR (Maximal Marginal Relevance): 在 relevance 和 diversity 之间平衡
- 规则: 连续不超过 2 个同一 creator 的 post; 不超过 3 个同类型内容
- Viral content throttling: 防止单条 post 过度曝光

**5. Metrics**:
- **Primary**: time spent, meaningful engagement (comments, shares)
- **Guardrails**: 广告 revenue, creator 发帖频率, misinformation rate

**Follow-ups**:
- 如何处理 cold-start users/content? -> 用 popularity-based ranking + quick exploration (epsilon-greedy)
- 如何避免 filter bubble (信息茧房)? -> 注入 exploration posts, 跨 topic 推荐

**解答**:

**Multi-Stage Ranking Pipeline**:

**Stage 1 -- Candidate Generation (候选生成)**:
- 来源: connections'' posts, followed creators, suggested content, ads
- 从 millions 筛选到 ~1000 candidates

**Stage 2 -- Scoring (打分)**:
- 预测 P(like), P(comment), P(share), P(click), P(hide)
- Final score = weighted combination: w1*P(like) + w2*P(comment) + w3*P(share) - w4*P(hide)

**Feature Categories**:

| 类别 | 特征示例 |
|------|---------|
| **User Features** | industry, seniority, past engagement patterns, active hours |
| **Content Features** | post type (text/image/video/article), length, hashtags, language |
| **Author Features** | follower count, avg engagement rate, connection degree |
| **Context Features** | time of day, device, session depth (第几次刷新) |
| **Cross Features** | user-author industry match, user-topic affinity |

**Diversity & Quality Balance**:
- **MMR (Maximal Marginal Relevance，最大边际相关性)**: 在 relevance 和 diversity 之间 trade-off，避免连续展示同类内容
- **Content type quota**: 每个 feed session 中限制同类型内容比例 (如最多 30% video)
- **Anti-viral**: 对 low-quality viral content (clickbait) 加惩罚项
- **Creator side optimization**: 确保优质创作者获得足够曝光，维护 creator ecosystem

**Model Architecture**: Deep neural network (Wide & Deep 或 DCN (Deep & Cross Network)) with embedding layers for categorical features。LinkedIn 实际使用 multi-objective optimization 同时优化多个 engagement signals。

---

### Q30. LinkedIn''s job application rate has been dropping

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: funnel-analysis, product-analytics, debugging, segmentation, metrics, root-cause-analysis

**题目**: LinkedIn''s job application rate has been dropping. You are given data showing the overall application funnel...

**解题思路**:

**结构化诊断框架 (MECE)**:

**Step 1: 明确问题**
- Application rate = applications / job detail page views? 或 applications / active job seekers?
- Drop 的程度? 是突然下降还是缓慢趋势?
- 时间范围? 某个时间点之后突变可能是 bug 或 product change

**Step 2: Funnel 分析**

```
Search/Browse -> Job Impressions -> Clicks (CTR) -> Detail Page Views
    -> Start Application -> Complete Application (Completion Rate)
```

在每一步检查 drop 发生在哪里:
- CTR 下降? -> 排序/推荐问题
- Detail page -> Start application 下降? -> UI 问题, job quality 问题
- Application completion 下降? -> 流程太长, 技术 bug, external link redirect

**Step 3: 分维度拆解 (Segmentation)**
- **平台**: mobile vs desktop vs app (某个平台可能有 bug)
- **地区**: 特定 country/region 的下降
- **用户类型**: premium vs free, 新用户 vs 老用户
- **Job 类型**: 某个 industry 或 job level 的下降
- **时间**: weekday vs weekend, 是否和节假日相关

**Step 4: 假设生成与验证**

| 假设 | 验证方法 |
|------|---------|
| Recent product change broke something | Check deployment timeline, A/B test results |
| Job quality declined (more spam jobs) | Check job reporting rate, time-to-fill |
| Competitor (Indeed) launched new feature | Check market data, user surveys |
| Seasonal effect (post-hiring season) | YoY comparison |
| External redirect rate increased | Check % of "Apply on company site" vs in-app apply |

**Step 5: 推荐行动**
1. 如果是 bug: hotfix + post-mortem
2. 如果是 job quality: 加强 job posting review + quality signals
3. 如果是 UX 问题: simplify application flow (Easy Apply 推广)
4. 如果是 seasonal: 正常, 但考虑 counter-seasonal promotions

**Follow-ups**:
- 如果 apply rate 下降但 save rate 上升? -> 用户在 browsing 但 not ready to apply; 可能是 job market uncertainty
- 如何区分 supply-side (fewer good jobs) vs demand-side (fewer active seekers) 问题? -> 分别看 new job postings trend 和 active seeker trend

**解答**:

**Structured Investigation Framework (结构化排查框架)**:

**Step 1: Clarify & Scope (澄清)**:
- 定义 "application rate" = applications / job views? or applications / active users?
- 时间范围: 突然下降还是渐进趋势?
- 全局 vs 局部: 所有市场/平台都下降还是某个 segment?

**Step 2: Funnel Decomposition (漏斗分解)**:
```
Job Search -> Job Impression -> Job Click -> Job Detail View -> Apply Click -> Submit Application
```
找到哪一步的转化率下降最大

**Step 3: Segmentation Analysis (分层分析)**:
- **By Platform**: Mobile vs Desktop vs App (例如新版 App 的 apply button 位置变了?)
- **By Geography**: 某个市场的下降可能源于季节性或竞争
- **By User Type**: New vs returning users, premium vs free
- **By Job Type**: 某些行业/职位类型下降更多?
- **By Employer**: 大公司 vs 小公司的 job posting 质量

**Step 4: Hypothesis Generation (假设生成)**:
1. **Product Change**: 近期是否有 UI 改动影响 apply flow?
2. **Supply Side**: Job posting 数量或质量下降? (经济不景气?)
3. **Competition**: 竞品 (Indeed, Glassdoor) 是否推出新功能?
4. **Technical**: 页面加载变慢? Apply button 异常?
5. **External**: 季节性因素 (假期, 毕业季后)?

**Step 5: Validation & Action**:
- A/B test 验证假设
- 如果是 UI 问题: revert 或 fix
- 如果是 supply 问题: 提升 job posting 质量，incentivize employers

---

### Q31. How would you identify frequent business travelers from LinkedIn data

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-engineering, classification, geo-features, user-segmentation, IP-geolocation, VPN

**题目**: How would you identify frequent business travelers from LinkedIn data? What features would you extract (job title, travel frequency, location changes, geo clusters, international company connections, connections distribution)? How would you handle issues with IP address and VPN accuracy for geo-based features?

**解答**:

**Feature Engineering (特征工程)**:

**1. Profile-based Features (静态特征)**:
- Job title keywords: "consultant", "sales director", "regional manager", "field engineer"
- Industry: consulting, enterprise sales, auditing -- 高出差行业
- Company type: 跨国企业, 多 office 公司
- Skills: "business development", "client management"

**2. Behavioral Features (行为特征)**:
- **Login location changes**: 短时间内从不同城市/国家登录 (IP geolocation)
- **Geo clusters**: 过去 90 天 unique 城市数、国家数
- **Session timezone shifts**: 频繁的时区变化
- **Connection distribution**: connections 分布在多个城市/国家的比例
- **Content engagement**: 与 travel/airport/hotel 相关内容的互动

**3. IP & VPN Handling (VPN 处理)**:
- VPN 检测: 已知 VPN IP 范围、数据中心 IP 标记
- 多信号融合: IP location + device GPS (mobile) + timezone + language settings
- 置信度评分: 当多信号一致时高置信，只有 IP 时低置信
- Fallback: 如果 IP 不可靠，更依赖 profile 和 connection 特征

**Model**:
- Binary classification: frequent_traveler = 1/0
- Ground truth: 可以用 self-reported travel frequency (profile survey) 或 expense report data (enterprise partners)
- Gradient boosted trees (XGBoost/LightGBM) 适合 mixed feature types

**Follow-up**: VPN accuracy -- 最好的策略是 ensemble multiple location signals，不过度依赖任何单一来源。对于 mobile 用户，GPS 数据比 IP 更可靠。

---

### Q32. Design a recommendation system for LinkedIn Learning

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recommendation-system, LinkedIn-Learning, ad-targeting, collaborative-filtering, content-based, personalization

**题目**: Design a recommendation system for LinkedIn Learning. Who are the target users? What features would you use for course recommendations? Additionally, how would you approach ad targeting for travel company advertisements on LinkedIn (e.g., recommending ads for travel services to the right audience)?

**解题思路**:

**Part 1: LinkedIn Learning 推荐系统**

**Target Users**: professionals seeking skill development -- job seekers upskilling, employees following learning paths, career changers

**推荐策略 (多路召回)**:
1. **Content-based**: 基于用户 skills gap (profile skills vs desired job requirements) 推荐补齐的课程
2. **Collaborative Filtering (CF，协同过滤)**: 相似用户 (同 title/industry) 学过的课程
3. **Sequential**: 用户刚完成 "Python Basics" -> 推荐 "Advanced Python"
4. **Trending**: 行业内热门课程 (如 AI/ML 课程 in tech industry)

**Features**:
- User: current skills, target role, industry, seniority, past courses, completion rates
- Course: topic tags, difficulty, duration, instructor rating, completion rate
- Cross: user-skill x course-skill overlap, peer completion rate

**Ranking Model**: 预测 P(complete course | user, course), 用 multi-task learning 同时优化 click + start + complete。

**Cold Start**:
- New user: 基于 profile 的 rule-based recommendations + onboarding survey
- New course: 基于 course metadata 的 content-based matching

**Part 2: Travel Ad Targeting**

**Audience Segmentation**:
- 用 Q31 的 frequent traveler identification model
- 加上: 关注旅行相关 pages/groups, 在 travel industry 工作, 高 seniority (更多商务旅行预算)

**Ad Ranking**: eCPM = bid * P(click) * P(convert), 在旅行广告和其他广告间竞价

**Follow-ups**:
- 如何衡量推荐质量? -> 课程完成率, skill assessment improvement, career outcome (如 job change)
- 如何平衡 popular courses 和 niche courses? -> Exploration-exploitation (如 Thompson Sampling)

**解答**:

**Target Users**: (1) 职业转型者 (career changers), (2) 技能提升者 (upskilling), (3) 企业培训学员 (corporate learners), (4) 学生/求职者

**Recommendation Architecture**:

**1. Candidate Generation (候选生成)**:
- **Content-based**: 基于用户 skills gap (profile skills vs desired job skills) 推荐弥补差距的课程
- **Collaborative Filtering (协同过滤)**: "和你相似的人也学了这些课程"
- **Trending**: 行业内热门课程 (trending in your industry)

**2. Features**:
| 类别 | 特征 |
|------|------|
| User | current skills, target role, industry, seniority, learning history |
| Course | topic, difficulty, duration, instructor rating, completion rate |
| Cross | skill-course relevance score, peer enrollment rate |
| Context | time of year (new year resolutions), job market trends |

**3. Ranking Model**:
- Predict P(enroll), P(complete), P(rate_high)
- Score = w1*P(enroll) + w2*P(complete) + w3*P(rate_high)
- 注重 completion 而非仅 enrollment，因为完成课程才有真正价值

**4. Cold Start (冷启动)**:
- 新用户: 基于 profile (title, skills) 推荐入门课程
- 新课程: 基于 content similarity 与热门课程比较

**Ad Targeting (旅行广告)**:
- Audience: 使用 Q31 的 frequent traveler 模型识别目标受众
- Lookalike audience: 找与已知商旅人士行为相似的用户
- Context: 在 travel-related content 旁展示 (contextual targeting)

---

### Q33. Design a propensity model to predict which LinkedIn users are likely to purchase...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: propensity-model, classification, conversion, class-imbalance, feature-selection, premium

**题目**: Design a propensity model to predict which LinkedIn users are likely to purchase LinkedIn Premium or a generative AI subscription. You are given sample data with columns: Date, MemberID, Converted (0/1), and various feature columns...

**解题思路**:

**1. Problem Setup**:
- Binary classification: P(convert to Premium | user features)
- 强 class imbalance: conversion rate 通常 < 5%

**2. Feature Engineering**:

**User profile features**:
- Account age, profile completeness score
- Industry, seniority, company size
- Number of connections, endorsements

**Engagement features**:
- DAU/WAU/MAU classification
- Feature usage: search frequency, InMail usage, profile views received
- Premium feature trial history (有没有用过免费试用)
- Job search activity (高活跃度 = 更可能付费)

**Behavioral signals**:
- Visited Premium page but didn''t convert (high intent)
- Used features that are Premium-gated (如 "Who viewed your profile")
- Email campaign interaction (opened/clicked upgrade emails)

**Temporal features**:
- Day of week, month (季节性: 年初求职季转化率高)
- Days since last login, login frequency trend (上升/下降)

**3. Modeling**:

```python
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, precision_recall_curve

# Handle class imbalance
model = GradientBoostingClassifier(
    n_estimators=200, max_depth=5,
    subsample=0.8, scale_pos_weight=20  # ~1:20 imbalance
)

# Use stratified CV to preserve class ratio
cv = StratifiedKFold(n_splits=5, shuffle=True)
```

**4. Class Imbalance Handling**:
- **Scale pos weight**: 增加正样本权重
- **SMOTE (Synthetic Minority Over-sampling Technique)**: 合成少数类样本
- **Threshold tuning**: 根据 business cost 调整 decision threshold
- **Evaluation**: 用 AUC-ROC (Area Under ROC Curve) + PR-AUC, 不用 accuracy

**5. Deployment**:
- 每日 batch scoring -> 将 top-K high-propensity users 发送 targeted promotion
- Real-time scoring: 用户访问 Premium page 时触发 personalized pricing/offer

**Follow-ups**:
- 如何防止 "已经要买的用户" 浪费促销预算? -> Uplift modeling: 预测促销的增量效果而非绝对转化概率
- Feature importance 如何解释给 business stakeholders? -> SHAP (SHapley Additive exPlanations) values

**解答**:

**1. Problem Framing**:
- Binary classification: Converted = 1 (purchased) / 0 (not purchased)
- Class imbalance: conversion rate 通常 < 5%，需要特殊处理

**2. Feature Engineering**:
- **Engagement**: login frequency, pages viewed, features used, time spent
- **Job-seeking signals**: job searches, applications submitted, profile updates
- **Network**: connection count, InMail usage, group memberships
- **Premium trial**: 是否使用过 free trial, trial 期间的活跃度
- **Temporal**: 注册时长, 最近活跃度变化趋势
- **Device**: mobile vs desktop (mobile 用户更常 convert?)

**3. Class Imbalance Handling (类不平衡处理)**:
- **SMOTE (Synthetic Minority Over-sampling Technique)**: 合成少数类样本
- **Cost-sensitive learning**: 对 positive class 赋予更高权重
- **Threshold tuning**: 调整分类阈值而非使用默认 0.5
- **Evaluation**: 用 AUC-ROC 和 Precision-Recall AUC 而非 accuracy

**4. Model Selection**:
- **Baseline**: Logistic Regression (可解释性强，适合初版)
- **Production**: XGBoost/LightGBM (处理 mixed features 好，支持 feature importance)
- **Feature Selection**: 用 permutation importance 或 SHAP (SHapley Additive exPlanations) values

**5. Deployment**:
- 每日批量预测 all users 的 conversion probability
- 按 propensity score 分桶: high (>0.3), medium (0.1-0.3), low (<0.1)
- High propensity 用户: targeted email campaign, personalized offer
- Medium: show Premium feature highlights in-app
- Evaluation: lift chart, calibration plot, A/B test of targeting strategy

---

### Q34. Design a personalized job ranking model for LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: hard
- **Tags**: job-ranking, learning-to-rank, personalization, features, recommendation, search

**题目**: Design a personalized job ranking model for LinkedIn. How would you rank jobs for an individual user? What features would you use (user personality/preferences, seniority level, search context, keywords, headline, summary, connections at company, skills, endorsements)? Describe the model architecture and training approach.

**解题思路**:

**1. Feature Categories**:

**Query features** (搜索上下文):
- Search keywords, filters (location, remote, salary range)
- Search session context (刚搜了什么, click 了什么)

**User features**:
- Profile: skills, headline, experience, education, seniority
- Preferences: desired job type, location, salary expectation
- Behavioral: 历史 click/apply/save 的 job 的 pattern
- Network: connections at specific companies

**Job features**:
- Title, description, required skills, seniority level
- Company: size, industry, brand strength, Glassdoor rating
- Job metadata: posting date, salary range, remote/hybrid/onsite
- Quality: application count, view-to-apply ratio

**Cross features (user x job)**:
- Skill overlap: user skills vs required skills match ratio
- Title similarity: user''s current/past titles vs job title
- Location match: user location vs job location
- Connection count at company
- Company industry match with user''s industry

**2. Model Architecture**:
- **Learning-to-Rank (LTR)**: LambdaMART (GBDT-based) 或 neural LTR
- **Two-tower model**: user tower + job tower, learned embeddings for retrieval
- **Multi-task**: jointly predict P(click), P(apply), P(qualified)
- Final score = weighted combination, 如 0.3*P(click) + 0.5*P(apply) + 0.2*P(qualified)

**3. Training**:
- **Positive signals**: click, save, apply, get hired
- **Negative signals**: impression without click, quick back from detail page
- **Pairwise loss**: for each query, the applied job should rank higher than clicked-only, which should rank higher than skipped
- **Temporal train/test split**: 用过去数据训练, 未来数据验证

**4. Serving**:
- Two-stage: embedding-based retrieval (ANN search) -> LTR re-ranking
- Real-time feature computation: user features cached, job features pre-computed
- Latency target: < 200ms for full pipeline

**Follow-ups**:
- 如何处理 position bias (用户倾向点击排名靠前的结果)? -> Inverse Propensity Weighting (IPW) 或 randomized experiments
- 如何平衡 relevance 和 diversity? -> DPP (Determinantal Point Process) 或 MMR re-ranking

**解答**:

**1. Feature Categories**:

| Category | Features |
|----------|----------|
| **Query** | search keywords, filters (location, salary, remote) |
| **User** | skills, seniority, industry, past applications, saved jobs |
| **Job** | title, description embedding, company, location, salary range, posting date |
| **Cross** | skill-job match score, title similarity, connections at company, company-user industry match |
| **Context** | device, time of day, session position (first search vs refinement) |

**2. Model Architecture -- LTR (Learning to Rank，学习排序)**:
- **Pointwise**: Predict P(apply | user, job) with binary cross-entropy
- **Pairwise**: 给定 (user, job_a, job_b)，预测哪个 job 更 relevant (如 RankNet, LambdaRank)
- **Listwise**: 直接优化 NDCG (如 LambdaMART)

**推荐**: Two-stage approach
- Stage 1: Lightweight model (logistic regression / small NN) 对 ~1000 candidates 粗排
- Stage 2: Heavy model (deep cross network) 对 top ~100 精排

**3. Training Data**:
- **Positive**: applied jobs, saved jobs, long-viewed jobs (>30s on detail page)
- **Negative**: impressed but not clicked, clicked but quickly bounced
- **Label hierarchy**: apply > save > long_view > click > impression (multi-level relevance)

**4. Evaluation**:
- Offline: NDCG@10, MRR, Precision@5
- Online: Application rate, CTR, search-to-apply conversion, user retention
- A/B test: new model vs current model on random user splits

**5. Personalization Key Insight**: "Connections at company" 是 LinkedIn 独有的强 signal -- 用户更倾向于申请有认识人的公司。

---

### Q35. LinkedIn has 500M+ users

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: user-segmentation, market-sizing, opportunity-sizing, clustering, product-strategy, estimation

**题目**: LinkedIn has 500M+ users. Identify the top 5 user segments, estimate each segment''s market size, and estimate the opportunity sizing for sales professionals specifically...

**解题思路**:

**Top 5 User Segments**:

| Segment | Est. % | Est. Count | Key Needs |
|---------|--------|------------|-----------|
| 1. Job Seekers | 15% | 75M | Job search, resume building, interview prep |
| 2. Passive Professionals | 40% | 200M | Networking, industry news, brand building |
| 3. Recruiters & HR | 5% | 25M | Talent sourcing, employer branding |
| 4. Sales Professionals | 10% | 50M | Lead generation, prospect research, relationship building |
| 5. Content Creators/Educators | 5% | 25M | Audience building, thought leadership |
| (Other: students, inactive) | 25% | 125M | Career exploration, dormant |

**Segmentation Methodology**:
- **Behavioral clustering**: 基于 feature usage patterns (search, post, InMail, apply)
- **K-means / DBSCAN** on behavioral vectors
- **Rule-based overlay**: 结合 job title + industry 标签

**Sales Professionals Opportunity Sizing**:

**TAM (Total Addressable Market)**:
- 50M sales professionals on LinkedIn
- Sales Navigator price: ~$100/month
- TAM = 50M * $100 * 12 = $60B/year

**SAM (Serviceable Addressable Market)**:
- 只考虑 B2B sales (约 60% of sales pros) = 30M
- 其中决策者/heavy users 约 30% = 9M
- SAM = 9M * $100 * 12 = $10.8B/year

**SOM (Serviceable Obtainable Market)**:
- Current Sales Navigator subscribers (公开数据约 500K-1M)
- Short-term target: 3M subscribers (3x growth)
- SOM = 3M * $100 * 12 = $3.6B/year

**Product Strategy for Sales Segment**:
1. **Sales Navigator**: 高级搜索 + lead recommendations + InMail credits
2. **LinkedIn Sales Insights**: 公司级 intent signals
3. **CRM (Customer Relationship Management) integration**: Salesforce/HubSpot sync

**Follow-ups**:
- 如何增加 Sales Navigator 的 stickiness? -> Show ROI metrics (deals closed via LI), team collaboration features
- 如何从 passive professionals 转化为 paying users? -> Surface premium features at "moment of need" (如 profile view spike)

**解答**:

**Top 5 User Segments (用户分层)**:

| Segment | Est. Size | % of Users | Revenue Model |
|---------|-----------|------------|---------------|
| **1. Job Seekers** | ~100M | 20% | Premium Career ($30/mo), job ads |
| **2. Recruiters / HR** | ~25M | 5% | Recruiter Lite/Pro ($100-800/mo), job postings |
| **3. Sales Professionals** | ~50M | 10% | Sales Navigator ($80-135/mo) |
| **4. Content Creators / Influencers** | ~15M | 3% | Premium features, newsletter tools |
| **5. Passive Professionals** | ~310M | 62% | Ad revenue (feed ads, sponsored content) |

**Sales Professional Opportunity Sizing (销售人员机会估算)**:

**TAM (Total Addressable Market，总可寻址市场)**:
- 全球销售从业者 ~50M on LinkedIn
- 潜在 Sales Navigator 用户: ~50M * 有付费意愿比例 (~20%) = 10M
- TAM = 10M * $100/mo * 12 = $12B/year

**SAM (Serviceable Addressable Market，可服务市场)**:
- 英语市场 + 大中型企业: ~3M potential users
- SAM = 3M * $100/mo * 12 = $3.6B/year

**SOM (Serviceable Obtainable Market，可获得市场)**:
- 当前市场份额 ~800K subscribers (公开数据估算)
- SOM = 800K * $100/mo * 12 = ~$960M/year

**Growth Levers**: (1) SMB (Small-Medium Business，中小企业) 市场渗透, (2) 非英语市场扩展, (3) AI-powered features 提升付费转化

---

### Q36. What metrics would you design to measure job quality on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, job-quality, data-analytics, product-metrics, content-quality

**题目**: What metrics would you design to measure job quality on LinkedIn? How would you define a ''high-quality'' job posting, and what data signals would you use to measure and rank job posting quality?

**解题思路**:

**"High Quality" Job Posting 定义**: 准确描述真实岗位, 吸引合格候选人, 并最终导致成功雇佣。

**Quality Signals 分层**:

**1. Content Quality (内容质量)**:
- **Completeness score**: 是否包含 title, description, requirements, salary range, benefits, location
- **Description length**: 太短 (< 100 words) 可能信息不足; 太长 (> 2000 words) 可能噪声多
- **Salary transparency**: 是否公开薪资范围 (强正信号)
- **Spam/scam signals**: 异常薪资承诺, 可疑公司名, 要求预付费用

**2. Engagement Quality (互动质量)**:
- **View-to-apply rate**: 看了 detail page 后申请的比例 (高 = 吸引对的人)
- **Application quality**: 申请者与 requirements 的 match score 分布
- **Quick-exit rate**: 打开 detail page 后秒退的比例 (高 = 标题与内容不匹配)
- **Save/share rate**: 收藏和分享率

**3. Outcome Quality (结果质量)**:
- **Response rate**: recruiter 回复申请者的比例 (低 = 可能是 ghost posting)
- **Time to fill**: 从发布到 filled 的时间
- **Interview rate**: 申请到面试转化率
- **Hire rate**: 最终雇佣率

**4. Poster Quality (发布者质量)**:
- Company verified status
- Company Glassdoor/LinkedIn rating
- Historical posting pattern (频繁发布相同 job = 可疑)

**Composite Job Quality Score**:

```
JQS = w1 * completeness + w2 * engagement_quality
    + w3 * outcome_quality + w4 * poster_quality
```

权重通过 human evaluation + regression 确定。

**应用场景**:
- 搜索排序: 高 JQS 的 job 排名更高
- 内容审核: 低 JQS 的 job 触发人工审核
- Poster feedback: 给雇主展示 job quality dashboard 和改进建议

**Follow-ups**:
- 如何检测 "ghost jobs" (已填但未关闭的岗位)? -> 监控 response rate drop + 时间维度异常
- Job quality 和 diversity 的关系? -> 检查 JQS 是否对某些 industry/location 有 bias

**解答**:

**Job Quality Definition (职位质量定义)**:
高质量 job posting = 信息完整 + 真实有效 + 对求职者有吸引力 + employer 积极响应

**Metrics Framework**:

**1. Posting Completeness (信息完整度)**:
- 必填字段覆盖率: title, company, location, description, requirements, salary range
- Description length & richness: 字数、是否包含 responsibilities/qualifications/benefits
- Score: weighted sum of filled fields (salary range 权重高因为用户最关心)

**2. Engagement Signals (用户参与信号)**:
- CTR: impressions -> clicks ratio (高 CTR = 标题和描述吸引人)
- Apply rate: clicks -> applications ratio
- Save/bookmark rate: 表示用户认为值得考虑
- Time on page: 长停留 = 认真阅读 (区分于快速 bounce)

**3. Employer Responsiveness (雇主响应度)**:
- Response rate: 收到申请后多久回复
- Interview rate: applications -> interviews ratio
- Ghosting rate: 申请后无任何反馈的比例 (越低越好)

**4. Outcome Signals (结果信号)**:
- Hire rate: 该 posting 最终是否成功招到人
- Time to fill: 从发布到招满的时间
- Retention: 通过该 posting 招到的人是否留任 6+ 个月

**5. Negative Signals (负面信号)**:
- Report/flag rate: 用户举报虚假/误导性 posting
- Duplicate detection: 同一 posting 反复发布 (可能是 spam)
- Salary accuracy: 面试后实际薪资与 posting 差异

**Composite Score**: Quality = w1*Completeness + w2*Engagement + w3*Responsiveness - w4*NegativeSignals

---

### Q37. How would you identify potential client companies for LinkedIn''s sales solutions...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: lead-scoring, sales, CRM, propensity-model, B2B, company-scoring

**题目**: How would you identify potential client companies for LinkedIn''s sales solutions (Sales Navigator, advertising, recruiting tools)? What features and metrics would you use to score and prioritize companies, and how would you build a CRM-style scoring model?

**解题思路**:

**1. Target Definition**: 预测 P(company purchases LinkedIn product within next quarter)

**2. Feature Engineering**:

**Company profile features**:
- Size (employee count), industry, revenue, growth rate
- Hiring velocity (job postings per month) -- 高 = potential recruiting tools buyer
- LinkedIn company page engagement (follower count, page activity)

**Historical behavior on LinkedIn**:
- Current product usage (free tier features usage)
- Past sales conversations/demos (CRM data)
- LinkedIn Ads spend history
- Job posting frequency and volume

**Digital signals (intent signals)**:
- Website visits to LinkedIn business solutions pages
- Downloaded whitepapers or attended LinkedIn webinars
- Competitive product usage (using Indeed, Glassdoor more)

**External data**:
- Funding events (newly funded startups need recruiting)
- M&A activity (post-merger companies need employer branding)
- Layoffs (paradoxically, may need outplacement/rebranding)

**3. Lead Scoring Model**:

| Score Tier | Description | Action |
|-----------|-------------|--------|
| A (90-100) | High intent + high value | Immediate sales outreach |
| B (70-89) | High intent or high value | Nurture campaign |
| C (50-69) | Medium signals | Automated marketing |
| D (< 50) | Low probability | No action, periodic re-score |

**Model**:
- Gradient Boosted Trees for conversion prediction
- Separate models per product (Recruiter, Sales Nav, Ads)
- Score = P(convert) * expected_deal_value

**4. Metrics**:
- Lead-to-opportunity conversion rate by score tier
- Sales cycle length
- Revenue per lead
- Model lift over random outreach

**Follow-ups**:
- 如何避免只 target 大公司而忽略 high-growth SMBs? -> 加入 growth rate features, 用 "velocity" 而非 absolute size
- 如何处理 long sales cycles (enterprise deals 可能 6-12 months)? -> Recalibrate labels to use "entered pipeline" as positive signal

**解答**:

**Lead Scoring Model (线索评分模型)**:

**1. Company Features (公司特征)**:
- **Firmographics**: industry, size (employee count), revenue, location, growth rate
- **LinkedIn Presence**: company page followers, content posting frequency, employee profile completeness
- **Hiring Activity**: job postings on LinkedIn, recruiter seat count, InMail volume
- **Current Spend**: 是否已是 LinkedIn 广告客户? 当前 spend level?

**2. Engagement Signals**:
- Company page admin activity (更新频率)
- Employee advocacy: 员工在 LinkedIn 上的活跃度
- Sales Navigator trial usage / demo requests
- Website visits to LinkedIn business solutions pages (if tracking available)

**3. Propensity Model**:
- **Training data**: 历史成交客户 (positive) vs 未成交 leads (negative)
- **Model**: Gradient boosted trees (XGBoost) -- 处理 mixed features 好，可解释
- **Output**: propensity score (0-1) + segment label (hot/warm/cold)

**4. Scoring Framework**:
```
Lead Score = Fit Score (40%) + Engagement Score (30%) + Timing Score (30%)
```
- **Fit Score**: 公司规模、行业、增长率是否匹配目标客户画像
- **Engagement Score**: 与 LinkedIn 产品的互动程度
- **Timing Score**: 是否在采购窗口期 (如 fiscal year start, headcount expansion)

**5. Prioritization**: 按 score 排序分配给 sales team。High score + recent engagement = 优先联系。

---

### Q38. Design a keyword search system for LinkedIn that surfaces the most popular/relev...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: search-ranking, information-retrieval, keyword-search, content-search, relevance, infrastructure-cost

**题目**: Design a keyword search system for LinkedIn that surfaces the most popular/relevant posts. How would you rank search results for content search? Discuss relevance signals, personalization, and cost metrics for search (cost per search, infrastructure cost per query).

**解题思路**:

**系统架构**:

```
Query -> Query Processing -> Index Lookup -> Candidate Retrieval
    -> Relevance Ranking -> Personalization -> Results
```

**1. Query Processing**:
- Tokenization + stemming + stop words removal
- Spell correction (did you mean...?)
- Query expansion: synonyms, abbreviations ("ML" -> "machine learning")
- Intent detection: searching for people vs posts vs jobs vs companies

**2. Indexing (Inverted Index)**:
- 每个 term -> list of (doc_id, tf, position) 用于 matching
- BM25 (Best Matching 25) 作为 base relevance score
- 分 index: posts index, profiles index, jobs index, companies index

**3. Ranking Signals**:

**Relevance signals**:
- BM25 text match score (term frequency, document length normalization)
- Title match boost (query 出现在 post title 权重更高)
- Exact phrase match bonus
- Recency decay (新 post 更相关)

**Popularity signals**:
- Like/comment/share count
- View count
- Author authority (follower count, post history engagement)

**Personalization signals**:
- Connection degree (1st > 2nd > 3rd)
- Industry/topic affinity (用户历史 engagement 的 topic 分布)
- Language match

**4. Cost Metrics**:
- **Cost per search**: infrastructure cost / total search queries
- **Query latency**: P50 < 100ms, P99 < 500ms
- **Index freshness**: new posts indexed within X minutes
- Optimization: tiered caching (hot queries cached), early termination (stop scoring after top-K found)

**5. Architecture for Scale**:
- **Distributed index**: partition by content hash or time range
- **Two-phase ranking**: L1 (fast BM25 on inverted index) -> L2 (neural re-ranker on top-100)
- **Cache**: 热门 queries 缓存 (如 "machine learning", "remote jobs")

**Follow-ups**:
- 如何处理多语言搜索? -> Language-specific tokenizers + cross-lingual embeddings
- 如何平衡 relevance 和 freshness? -> 可配置的 time-decay factor, 或 separate "Top" vs "Recent" tabs

**解答**:

**Architecture**:

**1. Indexing Layer (索引层)**:
- **Inverted Index**: 对所有 posts 的文本内容建立倒排索引 (term -> list of post_ids)
- **Real-time Index**: 新 post 发布后几秒内可搜索 (使用 Lucene/Elasticsearch 的 near-real-time refresh)
- **Field-specific Indexing**: title, body, author_name, hashtags 分别索引，支持 field-weighted scoring

**2. Ranking Signals (排序信号)**:
- **Text Relevance**: BM25 score (term frequency, inverse document frequency, document length normalization)
- **Popularity**: likes, comments, shares, views (time-decayed)
- **Freshness**: 发布时间 decay (recent posts 权重更高)
- **Author Authority**: follower count, engagement rate, topic expertise
- **Personalization**: user-author connection degree, shared industry/skills, past engagement with similar content

**3. Ranking Formula**:
```
Score = w1*BM25(query, post) + w2*Popularity_decay(post) + w3*Freshness(post) + w4*Personalization(user, post)
```
权重通过 LTR (Learning to Rank) 模型从 click-through 数据学习

**4. Cost Metrics (成本指标)**:
- **Cost per search**: infra cost / total searches (target: < $0.001/search)
- **Latency**: P50 < 100ms, P99 < 500ms
- **Infrastructure cost**: compute (CPU for ranking) + storage (index size) + network
- **Optimization**: 分层 ranking (cheap recall -> expensive re-ranking), index caching, query result caching

---

### Q39. How would you decide which feature to build next for a LinkedIn product

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-prioritization, product-sense, decision-framework, impact-estimation, roadmap-planning

**题目**: How would you decide which feature to build next for a LinkedIn product? Describe a feature prioritization framework. What data would you use to support the decision? How would you estimate impact before building?

**解题思路**:

**Feature Prioritization Framework: RICE**

| 维度 | 定义 | 数据来源 |
|------|------|---------|
| **R**each | 影响多少用户 | User analytics, segment sizing |
| **I**mpact | 每个用户的影响程度 (1-3 scale) | User research, competitive analysis |
| **C**onfidence | 对估算的信心 (%, 越高越好) | Past experiment results, market data |
| **E**ffort | 开发成本 (person-months) | Engineering estimation |

RICE Score = (Reach * Impact * Confidence) / Effort

**详细决策流程**:

**Step 1: Gather candidates**
- User research: surveys, interviews, support tickets
- Data analysis: funnel drop-offs, feature usage gaps
- Competitive analysis: 竞品有但我们没有的功能
- Strategy alignment: 与公司 OKR (Objectives and Key Results) 对齐

**Step 2: Impact estimation (before building)**
- **Size the opportunity**: 如果 feature X 将 funnel step Y 的转化率提升 Z%, 影响多少 revenue/engagement
- **Analogy-based**: 类似 feature 在其他产品的效果
- **Survey intent**: "Would you use feature X?" (需要 discount, 实际使用率通常是 stated intent 的 30-50%)

**Step 3: Validate cheaply**
- **Fake door test**: 放一个 feature 按钮, 测量点击量, 不需要真正实现
- **Wizard of Oz**: 人工模拟 feature 效果
- **Prototype test**: 小范围 beta test

**Step 4: Build + A/B test**
- Feature flag 控制, A/B test 验证
- 观察期足够长 (2-4 weeks 避免 novelty effect)
- 看 primary metrics + guardrail metrics

**Example**: 是否 build "Salary Insights" feature?
- Reach: 75M job seekers = high
- Impact: salary is #1 reason for job change = high (3/3)
- Confidence: Glassdoor proves market demand = 80%
- Effort: 3 person-months
- RICE = (75M * 3 * 0.8) / 3 = 60M -> very high priority

**Follow-ups**:
- 如何处理 high-impact but high-risk features? -> 分阶段发布, MVP first, 加 rollback plan
- 如何平衡短期 engagement gains 和长期 user trust? -> 定义 long-term guardrail metrics (如 user trust score, NPS)

**解答**:

**Prioritization Framework: RICE Score**

**R - Reach (影响范围)**: 该 feature 影响多少用户?
- 用 DAU/MAU 中的 eligible users 估算
- Example: "智能求职推荐" 影响所有 active job seekers (~100M)

**I - Impact (影响程度)**: 对每个受影响用户的影响有多大?
- Score 1-3: 1=low (slight improvement), 2=medium (noticeable), 3=high (game-changer)
- 基于 user research, competitive analysis, internal data

**C - Confidence (置信度)**: 估算的可靠程度?
- High (80%): 有 A/B test 数据或 strong analogues
- Medium (50%): user research 支持但无量化数据
- Low (20%): 纯直觉/hypothesis

**E - Effort (工程成本)**: 开发、测试、部署所需人月
- 越低越好 (分母)

**RICE Score = (Reach * Impact * Confidence) / Effort**

**Data Sources for Decision**:
1. **User Research**: surveys, user interviews, usability testing
2. **Competitive Analysis**: 竞品是否已有该功能? 用户反馈?
3. **Internal Data**: 相关功能的 engagement metrics, funnel drop-offs
4. **Market Data**: industry trends, analyst reports

**Impact Estimation Methods**:
- **Historical analogues**: 类似 feature 上线后的 metric lift
- **Fake door test**: 展示 feature 入口但不实现，测量 click rate
- **Limited rollout**: 先对 1% 用户开放，外推全量效果
- **Back-of-envelope**: 估算 funnel 改善 -> 最终 metric 变化

---

### Q40. Design the metrics for LinkedIn''s profile visit feature

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: metrics-design, profile-views, product-metrics, feature-evaluation, engagement

**题目**: Design the metrics for LinkedIn''s profile visit feature. What would you measure to evaluate whether the ''Who Viewed Your Profile'' feature is successful? How would you define and track feature success?

**解题思路**:

**Feature 价值分析**: "Who Viewed Your Profile" (WVYP) 是 LinkedIn 最具特色的功能之一, 驱动用户回访和 Premium 转化。

**Metrics 框架**:

**1. Engagement Metrics (用户参与)**:
- **WVYP page visit rate**: % of DAU who visit WVYP page per day
- **Notification click-through rate**: WVYP notification clicks / notifications sent
- **Profile views per user**: average views received per week (supply metric)
- **View-back rate**: 用户看了 WVYP 后去查看 viewer 的 profile 的比例

**2. Retention Metrics (留存)**:
- **D7/D30 retention lift**: WVYP 使用者 vs 非使用者的留存差异
- **Session frequency**: WVYP 用户的平均 weekly sessions
- **Reactivation rate**: dormant users 因 WVYP notification 回来的比例

**3. Monetization Metrics (变现)**:
- **Premium conversion**: WVYP 是 Premium 的 top 卖点 (full list of viewers)
- **Upsell CTR**: free users 看到 "upgrade to see all viewers" 的转化率
- **Revenue per WVYP session**: 通过 Premium upsell + ads 产生的收入

**4. Quality Metrics (质量)**:
- **Accuracy**: viewer list 的准确性 (privacy settings 可能隐藏部分 viewers)
- **Freshness**: 从 view 发生到出现在列表中的延迟
- **User satisfaction**: NPS for WVYP feature (survey-based)
- **Privacy complaints**: 因 WVYP 导致的 privacy concern reports

**5. Guardrail Metrics (不能变差)**:
- Privacy opt-out rate: 如果增加可见性导致更多人选择匿名浏览
- Harassment reports: 确保不被滥用于 stalking
- Overall session time: WVYP 不应 cannibalize 其他 feature 的使用

**Success Definition**:
Feature is successful if: (1) WVYP daily visits grow YoY, (2) contributes measurably to Premium conversion, (3) privacy metrics remain stable.

**Follow-ups**:
- 如果匿名浏览模式使用率上升导致 WVYP 数据稀疏怎么办? -> 提供 "appear as anonymous" but show industry/role hints
- 如何 A/B test WVYP 的不同版本 (如增加 viewer insights)? -> 注意 network effect: 两组用户的互相查看会交叉

**解答**:

**Feature Value Hypothesis**: "Who Viewed Your Profile" 通过 social curiosity 驱动用户回访和 engagement

**1. Engagement Metrics**:
- **Feature Usage**: DAU of "Who Viewed" page, views per session
- **Notification CTR**: push/email notification about profile views -> click rate
- **Return Visit Rate**: 查看 "Who Viewed" 后 24h 内再次登录的比例
- **Session Depth**: 查看 "Who Viewed" 后是否继续浏览其他页面

**2. Downstream Actions (下游行为)**:
- **Connection Requests**: 查看 viewer profile 后发起 connection request 的比例
- **Profile Updates**: 被浏览后是否更新自己的 profile (motivated by views)
- **InMail Sent**: 是否向 viewer 发送消息
- **Premium Conversion**: "Who Viewed" 是 Premium 的核心卖点 -- 转化率

**3. User Satisfaction**:
- **NPS (Net Promoter Score，净推荐值)**: 对该功能的满意度
- **Privacy Concern Rate**: 因隐私原因关闭可见性的用户比例 (越高 = 功能可能引起不适)

**4. Success Criteria**:
- Primary: Feature DAU 占 total DAU 的 15%+
- Secondary: 使用该功能的用户 7-day retention 比不使用的高 5%+
- Guardrail: Privacy opt-out rate < 10%

**5. Premium Upsell**: 免费用户只看到最近 5 个 viewers，Premium 看到全部 -- 跟踪 upsell conversion rate

---

### Q41. You are launching a new feature on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: feature-launch, product-evaluation, success-metrics, market-estimation, launch-process, user-satisfaction

**题目**: You are launching a new feature on LinkedIn. Walk through the full evaluation process: estimating potential market, determining initial data needs, defining success metrics, pre-launch steps, and post-launch user satisfaction measurement.

**解题思路**:

**Phase 1: Pre-Launch Planning**

**Market Sizing**:
- TAM: 全部 LinkedIn users * feature 的适用比例
- SAM: 活跃用户中符合 target persona 的比例
- Example: 如果 launching "AI Resume Review" -> TAM = 75M job seekers, SAM = 30M active job seekers

**Data Requirements**:
- Baseline metrics: 当前相关 funnel 的转化率
- User research: qualitative interviews + quantitative surveys
- Logging infrastructure: 确保 feature 的所有交互都有 instrumentation

**Success Metrics (定义 before launch)**:
- **Primary**: 1 个核心指标 (如 feature adoption rate within 30 days)
- **Secondary**: engagement depth (如 average sessions using feature per user)
- **Guardrails**: 不能降低的指标 (如 overall app performance, existing feature usage)

**Phase 2: Launch Execution**

1. **Internal dogfooding**: 员工先用 1-2 周
2. **Beta/canary release**: 1-5% of users, monitor crash rate + critical bugs
3. **A/B test**: 10-50% rollout, 收集足够样本量
4. **Full rollout**: 如果 A/B test 显著正向

**Rollout 注意事项**:
- Feature flag 控制, 支持快速 rollback
- Staged rollout by geography/user segment
- On-call 工程师 monitor real-time metrics

**Phase 3: Post-Launch Evaluation**

**Short-term (1-4 weeks)**:
- Adoption rate: % of eligible users who tried feature
- Activation rate: % of users who completed key action (not just opened)
- Bug reports, crash rate, performance metrics

**Medium-term (1-3 months)**:
- Retention: feature usage D7, D30 retention
- Engagement: 是否增加 overall platform engagement
- Cannibalization: 是否减少其他 feature 使用

**User Satisfaction**:
- In-app feedback: thumbs up/down after using feature
- NPS (Net Promoter Score) survey
- Support ticket analysis: 新增 issue categories
- Qualitative: user interviews with power users + churned users

**Follow-ups**:
- 如果 A/B test 不显著怎么办? -> 延长测试期, 或 segment analysis 找 sub-populations where it works
- 如何决定 kill a feature that underperforms? -> Pre-define kill criteria (如 < X% adoption after 3 months)

**解答**:

**Phase 1: Pre-Launch Planning**

**Market Estimation**:
- TAM: 该 feature 的潜在用户群 (e.g., all LinkedIn users, only recruiters, only job seekers)
- SAM: 实际可触达的用户 (active users in target segment)
- Initial target: 1-5% of SAM for MVP (Minimum Viable Product，最小可行产品)

**Data Requirements**:
- 现有数据: user demographics, behavior logs, engagement patterns
- 新增数据: feature-specific event tracking (impressions, clicks, completions)
- Instrumentation plan: 定义所有 tracking events before development

**Success Metrics (OKR 框架)**:
- **Primary metric**: 直接衡量 feature 价值 (e.g., applications submitted, courses completed)
- **Secondary metrics**: engagement (usage frequency, time spent), adoption rate
- **Guardrail metrics**: 确保不伤害其他指标 (overall DAU, other feature usage, page load time)

**Phase 2: Launch Execution**

- **Staged Rollout**: 1% -> 5% -> 25% -> 100%，每阶段监控 guardrail metrics
- **A/B Test Design**: treatment vs control, 确保统计功效 (power >= 80%)
- **Feature Flags**: 随时可回滚 (kill switch)

**Phase 3: Post-Launch Evaluation**

- **Quantitative**: A/B test results, metric dashboards, cohort analysis
- **Qualitative**: in-app survey (NPS), user interviews, support ticket analysis
- **Long-term**: 30/60/90 day retention curves, LTV (Lifetime Value，用户生命周期价值) impact
- **Decision**: Ship (metrics positive), Iterate (metrics neutral), Kill (metrics negative or guardrail violated)

---

### Q42. Design a database schema and system for tracking job applications on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: database-design, schema-design, application-tracking, job-search, data-modeling

**题目**: Design a database schema and system for tracking job applications on LinkedIn. Include attributes for users with applied_job, status, connections at the company, application history, etc...

**解题思路**:

**Core Tables**:

```sql
-- Users (applicant information)
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    headline VARCHAR(500),
    location VARCHAR(255),
    industry VARCHAR(100),
    experience_years INT,
    profile_completeness FLOAT,
    created_at TIMESTAMP
);

-- Jobs
CREATE TABLE jobs (
    job_id BIGINT PRIMARY KEY,
    company_id BIGINT REFERENCES companies(company_id),
    title VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    seniority_level VARCHAR(50),
    employment_type VARCHAR(50),  -- full-time, contract, etc.
    salary_min INT,
    salary_max INT,
    posted_at TIMESTAMP,
    status VARCHAR(20) DEFAULT ''active'',  -- active, closed, filled
    INDEX idx_company (company_id),
    INDEX idx_posted (posted_at)
);

-- Applications (core tracking table)
CREATE TABLE applications (
    application_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT REFERENCES users(user_id),
    job_id BIGINT REFERENCES jobs(job_id),
    status VARCHAR(30) DEFAULT ''submitted'',
    -- submitted -> reviewed -> interviewing -> offered -> hired/rejected
    applied_at TIMESTAMP,
    updated_at TIMESTAMP,
    source VARCHAR(50),  -- search, recommendation, email_alert, easy_apply
    resume_version_id BIGINT,
    cover_letter TEXT,
    INDEX idx_user (user_id),
    INDEX idx_job (job_id),
    INDEX idx_status (status),
    UNIQUE KEY uk_user_job (user_id, job_id)  -- prevent duplicate applications
);

-- Application status history (audit trail)
CREATE TABLE application_status_log (
    log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    application_id BIGINT REFERENCES applications(application_id),
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    changed_at TIMESTAMP,
    changed_by VARCHAR(50)  -- system, recruiter, applicant
);

-- Connections at company (for "X connections work here")
CREATE TABLE user_connections (
    user_id BIGINT,
    connection_id BIGINT,
    company_id BIGINT,
    PRIMARY KEY (user_id, connection_id)
);
```

**Key Design Decisions**:
- **Status as enum string**: 比 int 更可读, 便于调试
- **Separate status log**: 完整审计轨迹, 支持 funnel analysis
- **Source tracking**: 知道用户从哪里来申请, 优化渠道
- **Unique constraint on (user_id, job_id)**: 防止重复申请

**Analytics Queries**:

```sql
-- Application funnel by source
SELECT source,
       COUNT(*) AS total_applications,
       SUM(CASE WHEN status = ''reviewed'' THEN 1 ELSE 0 END) AS reviewed,
       SUM(CASE WHEN status = ''interviewing'' THEN 1 ELSE 0 END) AS interviews,
       SUM(CASE WHEN status = ''hired'' THEN 1 ELSE 0 END) AS hired
FROM applications
WHERE applied_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY source;
```

**Follow-ups**:
- 如何 scale 到每天百万级申请量? -> 分库分表 (shard by user_id), 读写分离, 状态更新用消息队列异步
- 如何实现 "Easy Apply" 的无缝体验? -> 预填充 profile data, 一键提交, 减少 friction

**解答**:

**Schema Design**:

```sql
-- Core tables
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    headline VARCHAR(500),
    location VARCHAR(255),
    industry VARCHAR(100),
    seniority_level VARCHAR(50)
);

CREATE TABLE jobs (
    job_id BIGINT PRIMARY KEY,
    company_id BIGINT,
    title VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    salary_min INT,
    salary_max INT,
    posted_date TIMESTAMP,
    status VARCHAR(20)  -- active/closed/filled
);

CREATE TABLE applications (
    application_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    job_id BIGINT REFERENCES jobs(job_id),
    applied_date TIMESTAMP,
    status VARCHAR(30),  -- submitted/reviewed/interview/offer/rejected/withdrawn
    source VARCHAR(50),  -- search/recommendation/email_alert/referral
    resume_version_id BIGINT,
    cover_letter TEXT,
    UNIQUE(user_id, job_id)
);

CREATE TABLE application_status_history (
    id BIGINT PRIMARY KEY,
    application_id BIGINT REFERENCES applications(application_id),
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    changed_at TIMESTAMP,
    changed_by VARCHAR(20)  -- applicant/employer/system
);

-- Derived/cached for ML features
CREATE TABLE user_company_connections (
    user_id BIGINT,
    company_id BIGINT,
    connection_count INT,
    strongest_connection_degree INT,  -- 1st/2nd/3rd
    PRIMARY KEY(user_id, company_id)
);
```

**Key Design Decisions**:
- **Status History Table**: 记录状态变化轨迹，支持 funnel analysis
- **Source Tracking**: 追踪申请来源，评估各渠道效果
- **Connections Cache**: 预计算用户在目标公司的 connections 数，加速 ranking
- **Indexing**: (user_id, applied_date), (job_id, status), (company_id) 上建索引

---

### Q43. Design LinkedIn''s push notification system for improving user engagement

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: push-notification, engagement, conversion-funnel, personalization, notification-optimization, CPA

**题目**: Design LinkedIn''s push notification system for improving user engagement. Why use push notifications? Which engagement features should you focus on? Discuss time/frequency considerations, conversion funnel (notification -> open -> action), and key metrics (CPA, click notification rate, CVR).

**解题思路**:

**Why Push Notifications**: Re-engage users who are not actively on the platform; drive specific actions (apply, connect, respond).

**1. Notification Types (按优先级)**:
- **Direct actions**: InMail received, connection request, endorsement
- **Social engagement**: likes/comments on your post, someone shared your article
- **Job alerts**: new jobs matching your preferences, application status updates
- **Content**: trending posts in your industry, weekly digest
- **Growth/onboarding**: profile completion reminders, skill assessment invites

**2. Personalization Framework**:

**When to send (时机)**:
- 用户历史活跃时间段 (如每天 8am-9am commute time)
- 时区感知
- 避免 notification fatigue: 每日上限 (如 max 5 push notifications)

**What to send (内容)**:
- 预测 P(open | notification type, user, time)
- 优先发送高价值 notification (direct message > content update)
- Suppress low-value notifications (如 "X liked your comment" -- 可以 batch)

**Who to send (目标)**:
- Segment by engagement level:
  - Active users: 减少 notifications (他们已经在用)
  - At-risk users: 增加 re-engagement notifications
  - Dormant users: 高价值 hook (如 "A recruiter viewed your profile")

**3. Conversion Funnel & Metrics**:

```
Notification Sent -> Delivered -> Opened -> Action Taken -> Conversion
```

| Metric | 定义 | 目标 |
|--------|------|------|
| Delivery Rate | delivered / sent | > 95% |
| Open Rate | opens / delivered | 10-20% |
| CTR (Click-Through Rate) | clicks / opens | 5-15% |
| CVR (Conversion Rate) | conversions / clicks | varies by type |
| CPA (Cost Per Acquisition) | cost / conversions | minimize |
| Unsubscribe Rate | unsubscribes / sent | < 0.1% |

**4. Guardrails**:
- **Notification fatigue**: 监控 disable notification rate
- **User trust**: 不发送 misleading notifications (如 "fake" profile views)
- **Canary rollout**: 新 notification type 先给 1% 用户测试

**Follow-ups**:
- 如何优化 notification 文案? -> A/B test different copy, 用 LLM 生成 personalized text
- 如何处理跨设备 (mobile + desktop) notification? -> De-duplicate, prefer the device user is active on

**解答**:

**Why Push Notifications**: 将离线用户拉回平台，提升 DAU 和 engagement depth

**1. Notification Types (按价值排序)**:
- **Social**: "X viewed your profile", "X connected with you", "X endorsed your skill"
- **Content**: "Trending in your industry", "Your post got 100 likes"
- **Job**: "New jobs matching your preferences", "Your application was viewed"
- **Network**: "X started a new position", "X''s work anniversary"

**2. Personalization Engine**:
- **Content Selection**: 选择对该用户最 relevant 的通知 (based on past engagement)
- **Timing Optimization**: 在用户历史 active 时段发送 (e.g., 早上通勤时间)
- **Frequency Capping**: 每日上限 (e.g., max 5 push notifications/day)
- **Channel Selection**: push vs email vs in-app，根据用户偏好

**3. Conversion Funnel & Metrics**:
```
Notification Sent -> Delivered -> Opened -> Action Taken
```
- **Delivery Rate**: delivered / sent (受 OS, device settings 影响)
- **Open Rate (CTR)**: opened / delivered (target: 10-15%)
- **CVR (Conversion Rate，转化率)**: action / opened (target: 30-50%)
- **CPA (Cost Per Action)**: infrastructure cost / total actions
- **Opt-out Rate**: 退订率 (guardrail: < 0.5% per day)

**4. Anti-Spam & Quality**:
- **Fatigue Model**: 如果用户连续 3 天不 open notifications，降低频率
- **Relevance Score**: 只发送 predicted P(open) > threshold 的通知
- **A/B Test**: 每个通知 type 独立测试 optimal frequency 和 wording

**5. Key Trade-off**: 发送更多通知 -> 短期 DAU 提升，但 long-term opt-out 率上升。用 long-term retention 而非短期 DAU 作为优化目标。

---

### Q44. LinkedIn''s job application count has dropped 10% month-over-month

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: root-cause-analysis, metric-debugging, product-analytics, investigation, problem-solving

**题目**: LinkedIn''s job application count has dropped 10% month-over-month. How would you investigate and diagnose this problem? Walk through a structured approach: supply vs demand analysis, segment analysis, hypothesis generation, and recommended actions.

**解题思路**:

**Step 1: Clarify & Decompose the Metric**

Application Count = Job Seekers * Search Rate * CTR * Application Rate

分解看哪个环节 drop:
- **Job Seekers 下降?** -> Demand-side 问题
- **Job Postings 下降?** -> Supply-side 问题
- **CTR 下降?** -> Ranking/UX 问题
- **Application Rate 下降?** -> Application flow 问题

**Step 2: Supply vs Demand Analysis**

| 维度 | 检查内容 |
|------|---------|
| Supply | Active job postings count, new postings per week, job quality score trend |
| Demand | Active job seekers count, search query volume, DAU of job tab |
| Platform | New user registration, user churn rate |

**Step 3: Segment Analysis (找 isolation)**

```
-- Segment application drop by platform
SELECT platform, month,
       COUNT(*) AS applications,
       LAG(COUNT(*)) OVER (PARTITION BY platform ORDER BY month) AS prev_month
FROM applications
GROUP BY platform, month;
```

检查是否 isolated to:
- **某个平台**: mobile app vs desktop vs mobile web
- **某个地区**: US vs EMEA vs APAC
- **某个 job category**: tech vs non-tech
- **某种用户**: new vs returning, free vs premium
- **某种 apply type**: Easy Apply vs external redirect

**Step 4: Hypothesis Generation**

| 假设 | 验证方法 | 可能原因 |
|------|---------|---------|
| Product bug | Check deployment logs, error rates | 新 release 引入的 bug |
| Seasonal | YoY comparison | 正常季节性波动 |
| External redirect broken | Check redirect success rate | 第三方 ATS link 失效 |
| Application flow friction | A/B test results, funnel analysis | 新增字段导致 abandon |
| Job quality decline | JQS trend, spam rate | 更多低质量 posting |
| Macro economic | Job market data (BLS), competitor data | 经济衰退减少 hiring |

**Step 5: Recommended Actions (根据假设)**

1. **If bug**: Hotfix + rollback
2. **If funnel friction**: Simplify application flow, A/B test removal of unnecessary fields
3. **If supply decline**: Outreach to employers, incentivize job posting
4. **If external factors**: Monitor, prepare messaging to stakeholders
5. **Always**: Set up automated alerts for early detection

**Follow-ups**:
- 如果 10% drop 只发生在 mobile? -> 检查最近 app update, specific device/OS version issues
- 如何区分 "fewer applications per seeker" vs "fewer seekers"? -> Decompose into per-user application rate * user count

**解答**:

**Structured Root-Cause Analysis (结构化根因分析)**:

**Step 1: Metric Decomposition (指标分解)**:
```
Applications = Job Seekers * Searches/Seeker * Jobs_Seen/Search * Apply_Rate
```
哪个因子下降了? 分解后逐一检查。

**Step 2: Supply vs Demand (供给 vs 需求)**:
- **Supply (Job Postings)**: 职位发布总量是否下降? (经济衰退? 季节性?)
- **Demand (Job Seekers)**: 搜索用户数是否下降? 搜索频率是否变化?
- 如果 supply 和 demand 都没变，问题在 conversion (apply rate)

**Step 3: Segmentation (分层分析)**:
- **By Platform**: Mobile/Desktop/App -- 某个平台的 apply flow 是否有 bug?
- **By Region**: US/EU/Asia -- 区域性下降 vs 全局?
- **By Job Category**: Tech/Finance/Healthcare -- 行业特定?
- **By User Segment**: New/Returning, Free/Premium
- **By Employer Segment**: Large/SMB, new/existing employers

**Step 4: Hypothesis Testing**:
1. **Product Bug**: 近期 deploy 是否引入 apply button 异常? -> 检查 error logs
2. **UI Change**: A/B test rollout 是否影响了 apply flow?
3. **Seasonality**: 对比去年同期是否有类似 pattern?
4. **Competition**: 竞品推出新功能抢走用户?
5. **External**: 经济/就业市场变化?

**Step 5: Action Plan**:
- **Quick fix**: 如果是 bug/UI regression -> revert
- **Feature improve**: 如果是 apply flow 摩擦 -> simplify (one-click apply)
- **Supply boost**: 如果是 job posting 下降 -> incentivize employers
- **Monitor**: 设置 alert 当 application count 下降 > 5% week-over-week

---

### Q45. You''ve launched a ''Recommended Jobs'' feature on LinkedIn

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: recommendation-evaluation, metrics-design, AB-testing, feature-evaluation, job-recommendation

**题目**: You''ve launched a ''Recommended Jobs'' feature on LinkedIn. How would you measure its performance? What metrics would you track, and how would you compare it against other job discovery methods (search, email alerts, browsing)?

**解题思路**:

**1. Feature-Specific Metrics**:

**Adoption**:
- % of active users who view recommended jobs section
- Impression count: 每日展示多少 recommended jobs

**Quality**:
- **Recommendation CTR**: clicks on recommended jobs / impressions
- **Application rate**: applications from recommended jobs / clicks
- **Skill match score**: average match between user profile and recommended jobs
- **Diversity**: unique companies/industries in recommendations

**Downstream Impact**:
- **Applications from recommendations**: 占总 applications 的比例
- **Interview rate**: 通过 recommended jobs 申请后获得面试的比例
- **Time to apply**: 从 recommendation 到 application 的时间

**2. Comparison with Other Channels**:

| Metric | Recommended | Search | Email Alerts | Browse |
|--------|-------------|--------|-------------|--------|
| CTR | Measure | Baseline | Baseline | Baseline |
| Apply Rate | Measure | Baseline | Baseline | Baseline |
| Quality Score | Measure | Baseline | Baseline | Baseline |
| Cost per Apply | Measure | Baseline | Baseline | Baseline |

**Attribution model**: 用户可能通过多个渠道看到同一个 job。用 last-touch attribution 或 multi-touch attribution 分配 credit。

**3. A/B Test Design**:
- Control: 无 recommended jobs section
- Treatment: 有 recommended jobs section
- Randomization unit: user-level (不是 session-level)
- Duration: 至少 2-4 weeks (覆盖 weekly cycle)
- Primary metric: total applications per user (not just from recommendations -- 要看 incremental value)

**4. Cannibalization Analysis**:
- Recommendations 是否只是 redirecting 用户从 search 到 recommendations? 而非增加 total applications?
- 检查: control group 的 search applications vs treatment group 的 search applications
- 只有 net positive (total applications increase) 才算真正成功

**5. Long-term Metrics**:
- 3/6/12-month retention of users who engage with recommendations
- Job satisfaction: post-hire surveys for users hired through recommendations
- Model improvement: recommendation quality trend over time (A/B test effect size increasing)

**Follow-ups**:
- 如何处理 cold-start (新用户没有 interaction history)? -> 基于 profile + similar users 的 popularity-based recommendations
- 推荐的 jobs 如何保持 freshness? -> 优先推荐新发布的 jobs, 对已见过的做 de-duplication

**解答**:

**1. Feature-Level Metrics**:
- **Recommendation Quality**: CTR on recommended jobs, apply rate on recommended jobs
- **Coverage**: % of users who receive recommendations, % of jobs that get recommended
- **Diversity**: unique job categories / companies in recommendations per user
- **Freshness**: avg age of recommended jobs (应该优先推荐新发布的)

**2. Comparative Analysis (跨渠道比较)**:

| Channel | CTR | Apply Rate | Quality Signal |
|---------|-----|------------|----------------|
| **Recommended Jobs** | Track | Track | recommendation model quality |
| **Search** | Baseline | Baseline | explicit intent (用户主动搜索) |
| **Email Alerts** | Track | Track | timing + relevance |
| **Browse** | Track | Track | discovery-based |

- **Attribution**: 用户可能先通过 recommendation 看到 job，后来再 search 找到同一 job 申请 -- 需要 attribution model (last-click vs multi-touch)

**3. Incremental Impact**:
- **Key question**: Recommended Jobs 是否带来 incremental applications，还是只是 cannibalize (蚕食) search?
- 方法: A/B test -- treatment group 有 recommendations, control group 没有
- Measure: total applications (not just from recommendation channel)

**4. Long-term Metrics**:
- Job seeker retention: 使用 recommendations 的用户是否更活跃?
- Match quality: 通过 recommendations 申请的 jobs 是否有更高 interview/offer rate?
- User satisfaction: in-app survey on recommendation relevance

**5. Guardrails**:
- 不应降低 search usage (recommendations 补充而非替代 search)
- 不应增加 spam/irrelevant job impressions

---

### Q46. Design a system to track and analyze application database attributes for LinkedI...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: data-pipeline, feature-store, application-data, job-matching, data-engineering, ML-features

**题目**: Design a system to track and analyze application database attributes for LinkedIn users. Given fields like applied_job, application_status, connections_at_company, and application_history, how would you design the data pipeline and use these attributes to improve job search quality and matching?

**解题思路**:

**1. Data Pipeline Architecture**:

```
Application Events -> Event Stream (Kafka) -> Stream Processing (Flink/Spark)
    -> Feature Store -> ML Models + Analytics Dashboard
                   -> Data Warehouse (Offline Analysis)
```

**2. Key Attributes & Schema**:

**User application profile** (每个用户的申请画像):
- `total_applications`: 总申请数
- `application_history`: list of (job_id, timestamp, status, source)
- `success_rate`: applications that reached interview / total applications
- `preferred_industries`: based on application distribution
- `preferred_seniority`: from applied jobs'' levels
- `avg_connections_at_applied_companies`: social signal strength

**3. Feature Engineering for ML Models**:

**Job ranking improvement**:
- `user_apply_rate_for_similar_jobs`: 该用户对类似 jobs 的历史 apply rate
- `job_application_velocity`: job 的申请速度 (快速增长的 job 可能更热门或更好)
- `connections_at_company`: 有 connections 的公司, 用户更可能申请和被录用

**Match quality prediction**:
- `skill_overlap_with_applied_jobs`: 用户 skills vs 成功申请 jobs 的 required skills 的 overlap
- `title_trajectory`: 用户职位变化趋势 (升级 vs 平级 vs 转行)
- `application_to_interview_ratio`: 衡量用户 resume/profile 的匹配质量

**4. Data Pipeline Components**:

**Real-time path** (Kafka + Flink):
- 实时更新 application status
- 实时计算 connections_at_company (当用户查看 job 时)
- Feed real-time features to ranking model

**Batch path** (Spark):
- 每日重新计算 aggregated features (success rate, preference distributions)
- 训练数据生成 for ML model retraining
- Analytics report generation

**Feature Store**:
- Online serving: Redis/Memcached for low-latency feature lookup
- Offline: Hive/Parquet for model training
- Feature versioning: track feature definitions over time

**5. Privacy Considerations**:
- Application data is highly sensitive -- 加密存储, 限制访问
- 不向 employers 暴露用户的其他公司申请信息
- GDPR (General Data Protection Regulation) compliance: 用户有权删除申请数据

**Follow-ups**:
- 如何处理 data skew (少数用户海量申请, 多数用户少量申请)? -> 对 heavy applicants 做 truncation, 或用 log transform 归一化
- 如何用 application outcome data 改进 job quality scoring? -> 申请后面试率高的 job = higher quality

**解答**:

**Data Pipeline Architecture**:

**1. Data Ingestion (数据采集)**:
- **Event Stream**: 每次 application 状态变化生成事件 (Kafka topic: application_events)
- **Fields**: user_id, job_id, timestamp, action (apply/withdraw/status_change), new_status
- **Enrichment**: join with user profile, job posting, company data in real-time (Flink/Spark Streaming)

**2. Feature Engineering Pipeline**:
```
Raw Events -> Feature Store -> ML Models -> Job Ranking
```

| Feature | Computation | Update Frequency |
|---------|-------------|-----------------|
| application_count_30d | COUNT(applications) per user, last 30 days | Daily batch |
| apply_to_response_rate | responses / applications per user | Daily batch |
| connections_at_company | COUNT(connections) at target company | Real-time (connection changes) |
| application_history_embedding | Sequence model on past application patterns | Weekly batch |
| skill_job_match_score | Cosine similarity(user_skills, job_requirements) | On-demand |

**3. Feature Store (特征存储)**:
- **Online Store**: Redis/DynamoDB for real-time serving (low latency features)
- **Offline Store**: Hive/BigQuery for batch training data
- **Feature consistency**: 确保 training 和 serving 使用相同的 feature 计算逻辑

**4. ML Applications**:
- **Job Ranking**: 用 connections_at_company + application_history 作为 personalization features
- **Success Prediction**: 基于历史 apply->interview->offer patterns 预测成功概率
- **Smart Apply**: 推荐 "Easy Apply" vs "Full Application" based on 历史 response rate
- **Notification Trigger**: 当 application_status 变化时触发个性化通知

**5. Data Quality**: schema validation, null rate monitoring, freshness checks (stale data alert)

---

### Q47. Design a system for LinkedIn keyword search that surfaces the most popular posts...

- **Company**: LinkedIn | **Round**: phone_screen | **Difficulty**: medium
- **Tags**: search-ranking, popularity-ranking, sponsored-search, CPC, CPM, auction-design

**题目**: Design a system for LinkedIn keyword search that surfaces the most popular posts and content. How do you define ''popular''? What ranking signals would you use? Discuss cost metrics including CPC (cost per click), cost per 1000 impressions, and cost per keyword for sponsored search results.

**解题思路**:

**1. Defining "Popular"**:

Popularity 不是单一指标, 而是 composite score:
- **Engagement score**: likes * 1 + comments * 3 + shares * 5 + saves * 2 (加权, 高质量互动权重更大)
- **Velocity**: engagement growth rate (近期增长快的 > 总量大但增长停滞的)
- **Author authority**: follower count, post history engagement rate, verified status
- **Reach**: unique views / impressions

**Popularity Decay**: P(t) = engagement_score * decay(age), 用 time-decay function (如 exponential decay 或 power law) 确保新内容有机会被看到。

**2. Organic Ranking Signals**:

| Signal | Weight | 说明 |
|--------|--------|------|
| Text relevance (BM25) | High | Query-content match |
| Popularity score | Medium-High | As defined above |
| Personalization | Medium | User-topic affinity, connection degree |
| Freshness | Medium | Time decay factor |
| Content quality | Medium | Spam score, readability, media richness |

**3. Sponsored Search (Ads Integration)**:

**Ad Auction Design**:
- Advertiser 设置 bid (CPC or CPM) + targeting criteria
- **Ad Rank = bid * quality_score * relevance_score**
- Quality score: historical CTR, landing page quality, ad copy relevance
- 用 **GSP (Generalized Second-Price) Auction**: winner pays 最低能赢的价格 (类似 Google Ads)

**Pricing Models**:

| Model | 公式 | 适用 |
|-------|------|------|
| CPC | Advertiser pays per click | Direct response campaigns |
| CPM | Pay per 1000 impressions | Brand awareness |
| CPK (Cost Per Keyword) | Fixed price for keyword placement | Guaranteed visibility |

**Organic vs Sponsored 混合排序**:
- 用 eCPM 统一比较: organic content 的 eCPM = 0, sponsored content 的 eCPM = bid * P(click)
- 但不能全是 ads: 设定 max ad density (如每 5 个结果最多 1 个 ad)
- 标记 "Sponsored" 以保持用户信任

**4. Cost Metrics for Platform**:
- **Revenue per search**: total ad revenue / total searches
- **Ad load**: % of results that are sponsored
- **User satisfaction trade-off**: 过高 ad load 降低 organic engagement, 需要平衡

**Follow-ups**:
- 如何防止 ad fraud (虚假点击)? -> Click pattern anomaly detection, IP-based filtering, conversion verification
- 如何平衡 high-bidding low-relevance ads vs low-bidding high-relevance ads? -> 强调 quality score 的权重, 使 relevance 成为关键 factor

**解答**:

**1. Popularity Definition (定义 "热门")**:
- **Engagement-weighted score**: Score = w1*likes + w2*comments + w3*shares + w4*clicks
- **Time decay**: 使用 exponential decay -- 1 天前的 engagement 权重 > 7 天前
- **Velocity**: engagement 增长速率 (trending 内容初期增速快)
- **Quality adjustment**: 低质量 viral content (clickbait) 降权

**2. Organic Ranking Signals**:
- **Query Relevance**: BM25 text match + semantic similarity (BERT embeddings)
- **Popularity Score**: 如上定义
- **Author Authority**: follower count, expertise in query topic
- **Personalization**: user-author affinity, industry match
- **Freshness**: 时间衰减，优先展示近期内容

**3. Sponsored Search (付费搜索)**:

**Auction Design (竞价设计)**:
- **Second-price auction**: 竞价者支付第二高出价 + $0.01 (incentive-compatible)
- **Ad Rank = Bid * Quality Score**: quality score 包括 predicted CTR, ad relevance, landing page quality
- 高 quality score 的广告可以用更低的出价获得更高的位置

**Cost Metrics**:
- **CPC (Cost Per Click)**: 广告主每次点击付费。CPC = Total Spend / Clicks。适合 conversion-oriented campaigns
- **CPM (Cost Per Mille)**: 每 1000 次展示的费用。CPM = (Spend / Impressions) * 1000。适合 brand awareness
- **Cost per keyword**: 特定关键词的平均 CPC/CPM。高竞争关键词 ("software engineer jobs") 价格更高

**4. Organic vs Sponsored 混合展示**:
- 明确标记 "Sponsored" / "Promoted"
- Sponsored 结果不超过 total results 的 20% (user experience guardrail)
- 监控 organic CTR 是否因 ads 增多而下降 (cannibalization)

**Revenue Optimization**: Maximize long-term revenue = short-term ad revenue + user retention value。过度广告导致用户流失，long-term 收入下降。

---

## 统计

- **总题数**: 47
- **Coding**: 15 题 (全部含解题思路 + Python 代码)
- **ML Theory & Coding**: 8 题 (全部含详细解答)
- **ML System Design**: 24 题 (全部含系统设计分析)
- **有LeetCode编号的题目**: 8
- **含 Python 代码的题目**: 28
- **含 SQL 代码的题目**: 4
- **含 Follow-up 的题目**: 47
', updated_at = datetime('now') WHERE id = 26;

-- doc 30 (Uber BPS LeetCode Solutions Guide): lc=19 leetcode=0 custom=0
UPDATE company_documents SET content = '# Uber BPS -- LC Problem Solutions

> 所有题解均包含：解题思路、简洁 Python 代码、时间/空间复杂度、边界情况，以及 1point3acres 面经中报告的所有追问变体。
>
> Task: T-P0-242

---

## [LC 230](lc://230): Kth Smallest Element in a BST

> **题目描述** [medium]: Given the root of a binary search tree, and an integer k, return the kth smallest value (1-indexed) of all the values of the nodes in the tree.
 
Example 1:


Input: root = [3,1,4,null,2], k = 1
Output: 1

Example 2:


Input: root = [5,3,6,2,4,null,null,1], k = 3
Output: 3

 
Constraints:

The number of nodes in the tree is n.
1 &lt;= k &lt;= n &lt;= 104
0 &lt;= Node.val &lt;= 104

 
Follow up: If
 
Example 1:

Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1-&gt;4-&gt;5,
  1-&gt;3-&gt;4,
  2-&gt;6
]
merging them into one sorted linked list:
1-&gt;1-&gt;2-&gt;3-&gt;4-&gt;4


**Pattern**: Tree / Inorder Traversal（树 / 中序遍历）

### (a) Iterative Inorder

**中序遍历 (Inorder Traversal)** 在 **BST (Binary Search Tree，二叉搜索树)** 中会按升序访问所有节点，因此第 k 个访问到的节点即为第 k 小元素。迭代版本使用显式栈模拟递归。

```python
def kthSmallest(root, k):
    """Iterative inorder traversal -- stop at kth element."""
    stack = []
    node = root
    count = 0
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.right
```
**Time**: O(H + k)，其中 H 为树高。**Space**: O(H)，栈空间。

### (b) Recursive Inorder

递归版本使用列表作为可变闭包变量传递计数和结果，并在找到第 k 个元素后提前终止。

```python
def kthSmallest(root, k):
    """Recursive inorder with early termination."""
    result = [None]
    count = [0]

    def inorder(node):
        if not node or result[0] is not None:
            return
        inorder(node.left)
        count[0] += 1
        if count[0] == k:
            result[0] = node.val
            return
        inorder(node.right)

    inorder(root)
    return result[0]
```
**Time**: O(H + k)。**Space**: O(H) 递归栈空间。

### (c) VARIANT: Kth Largest

第 k 大变体使用反向中序遍历（右 -> 根 -> 左），将右子树优先访问：

```python
def kthLargest(root, k):
    """Reverse inorder: visit right subtree first."""
    stack = []
    node = root
    count = 0
    while stack or node:
        while node:
            stack.append(node)
            node = node.right  # go right first
        node = stack.pop()
        count += 1
        if count == k:
            return node.val
        node = node.left  # then left
```

### (d) FOLLOW-UP: O(1) Space -- Morris Traversal

**Morris 遍历 (Morris Traversal)** 通过临时修改树的指针来实现 O(1) 空间的中序遍历，遍历结束后完整恢复树的结构。

```python
def kthSmallest_morris(root, k):
    """Morris inorder traversal -- O(1) space, O(n) time."""
    node = root
    count = 0
    while node:
        if not node.left:
            count += 1
            if count == k:
                return node.val
            node = node.right
        else:
            # Find inorder predecessor
            pred = node.left
            while pred.right and pred.right != node:
                pred = pred.right
            if not pred.right:
                # Thread: link predecessor to current
                pred.right = node
                node = node.left
            else:
                # Unthread: predecessor already linked
                pred.right = None
                count += 1
                if count == k:
                    return node.val
                node = node.right
```
**Time**: O(n)。**Space**: O(1)——临时修改树后恢复原结构。

### (e) FOLLOW-UP: Augmented BST (left_count/right_count)

若可修改树结构，为每个节点添加 `left_count`（左子树节点数），可实现 O(H) 的查询：

```python
def kthSmallest_augmented(root, k):
    """O(H) lookup with augmented BST storing subtree sizes."""
    node = root
    while node:
        left_count = node.left_count if hasattr(node, ''left_count'') else 0
        if k == left_count + 1:
            return node.val
        elif k <= left_count:
            node = node.left
        else:
            k -= left_count + 1
            node = node.right
```
**Time**: O(H)。**Space**: O(1)。需要 O(n) 的预处理来计算子树大小。

### (f) FOLLOW-UP: Flatten the Tree

将 BST 通过中序遍历展开为有序数组，再直接按下标查询：

```python
def kthSmallest_flatten(root, k):
    """Flatten BST to sorted list, then O(1) index lookup."""
    vals = []
    def inorder(node):
        if node:
            inorder(node.left)
            vals.append(node.val)
            inorder(node.right)
    inorder(root)
    return vals[k - 1]
```
**Time**: O(n) 预处理，O(1) 单次查询。**Space**: O(n)。

---

## [LC 547](lc://547): Number of Provinces

> **题目描述** [medium]: There are N students in a class. Some of them are friends, while some are not. Their
friendship is transitive in nature. For example, if A is a direct friend of B, and B
is a direct friend of C, then A is an indirect friend of C. And we defined a
friend circle is a group of students who are direct or indirect friends.

Given a N*N matrix M representing the friend relationship between students in
t


**Pattern**: Union Find / DFS（并查集 / 深度优先搜索）

### Union Find

**并查集 (Union Find，UF)** 使用路径压缩与按秩合并优化，将连通分量合并操作接近 O(1) 均摊时间。

```python
def findCircleNum(isConnected):
    """Union Find with path compression and union by rank."""
    n = len(isConnected)
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # path compression
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1

    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                union(i, j)

    return len(set(find(i) for i in range(n)))
```
**Time**: O(n^2 * alpha(n))，其中 alpha 为反阿克曼函数（实际近似常数）。**Space**: O(n)。

### DFS Alternative

**DFS (Depth-First Search，深度优先搜索)** 替代方案：标记已访问节点，每次从未访问节点出发遍历即为一个新省份。

```python
def findCircleNum_dfs(isConnected):
    n = len(isConnected)
    visited = [False] * n
    provinces = 0

    def dfs(city):
        visited[city] = True
        for neighbor in range(n):
            if isConnected[city][neighbor] == 1 and not visited[neighbor]:
                dfs(neighbor)

    for i in range(n):
        if not visited[i]:
            dfs(i)
            provinces += 1
    return provinces
```

---

## [LC 337](lc://337): House Robber III

> **题目描述** [medium]: The thief has found himself a new place for his thievery again. There is only one entrance to
this area, called the "root." Besides the root, each house has one and only one
parent house. After a tour, the smart thief realized that "all houses in this place
forms a binary tree". It will automatically contact the police if two directly-linked
houses were broken into on the same night.

Determine th


**Pattern**: Tree DP（树上动态规划）

**树形 DP (Tree DP，树上动态规划)** 的核心思路：每个节点返回两个状态的最优值——抢当前节点 vs 不抢当前节点，由此避免相邻节点被同时抢劫的非法情况。

```python
def rob(root):
    """Tree DP: each node returns (rob_this, skip_this)."""
    def dfs(node):
        if not node:
            return (0, 0)
        left = dfs(node.left)
        right = dfs(node.right)
        # Rob this node: can''t rob children
        rob_this = node.val + left[1] + right[1]
        # Skip this node: take max of each child
        skip_this = max(left) + max(right)
        return (rob_this, skip_this)

    return max(dfs(root))
```
**Time**: O(n)。**Space**: O(H) 递归栈空间。

---

## [LC 1020](lc://1020): Number of Enclaves

> **题目描述** [medium]: Given a 2D array `A`, each cell is 0 (representing sea) or 1 (representing land)

A move consists of walking from one land square 4-directionally to another land square, or
off the boundary of the grid.

Return the number of land squares in the grid for which we cannot walk off
the boundary of the grid in any number of moves.

Example 1:

Input: [[0,0,0,0],[1,0,1,0],[0,1,1,0],[0,0,0,0]]
Output: 3



**Pattern**: BFS from Border（从边界出发的广度优先搜索）

**BFS (Breadth-First Search，广度优先搜索)** 策略：先将所有与边界相连的陆地格子标记为已访问（即可逃脱），剩余的陆地格子即为"飞地"（enclave）。

```python
from collections import deque

def numEnclaves(grid):
    """BFS from all border land cells, then count remaining land."""
    m, n = len(grid), len(grid[0])
    q = deque()

    # Enqueue all border land cells
    for i in range(m):
        for j in range(n):
            if (i == 0 or i == m - 1 or j == 0 or j == n - 1) and grid[i][j] == 1:
                q.append((i, j))
                grid[i][j] = 0  # mark visited

    # BFS to mark all reachable from border
    while q:
        x, y = q.popleft()
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                grid[nx][ny] = 0
                q.append((nx, ny))

    # Count remaining land cells (enclaves)
    return sum(grid[i][j] for i in range(m) for j in range(n))
```
**Time**: O(m*n)。**Space**: O(m*n) 队列最坏情况。

---

## [LC 994](lc://994): Rotting Oranges

> **题目描述** [medium]: You are given an m x n grid where each cell can have one of three values:

0 representing an empty cell,
1 representing a fresh orange, or
2 representing a rotten orange.

Every minute, any fresh orange that is 4-directionally adjacent to a rotten orange becomes rotten.
Return the minimum number of minutes that must elapse until no cell has a fresh orange. If this is impossible, return -1.
 
Examp


**Pattern**: Multi-source BFS（多源广度优先搜索）

多源 BFS 的关键：将所有初始腐烂橙子同时加入队列，模拟并行扩散过程。按轮次（分钟）扩展边界，每轮处理当前层所有节点。

```python
from collections import deque

def orangesRotting(grid):
    """Multi-source BFS from all initially rotten oranges."""
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    while q:
        minutes += 1
        for _ in range(len(q)):
            x, y = q.popleft()
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                    grid[nx][ny] = 2
                    fresh -= 1
                    q.append((nx, ny))
        if fresh == 0:
            return minutes

    return -1  # some fresh oranges unreachable
```
**Time**: O(m*n)。**Space**: O(m*n)。

---

## [LC 23](lc://23): Merge K Sorted Lists

**Pattern**: Heap（堆）

### Min-Heap Approach

使用**最小堆 (Min-Heap，最小优先队列)** 维护 k 个链表的当前最小节点，每次弹出最小值后将其下一个节点压入堆中。

```python
import heapq

def mergeKLists(lists):
    """Merge k sorted lists using a min-heap."""
    dummy = ListNode(0)
    curr = dummy
    heap = []

    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst.val, i, lst))

    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```
**Time**: O(N log k)，其中 N 为所有节点总数，k 为链表数量。**Space**: O(k)。

### Divide and Conquer

**分治法 (Divide and Conquer，分治)** 替代方案：每轮将链表两两配对合并，共 log k 轮，每轮合并总量为 O(N)。

```python
def mergeKLists_dc(lists):
    """Merge k lists by repeatedly merging pairs."""
    if not lists:
        return None

    def merge2(l1, l2):
        dummy = ListNode(0)
        curr = dummy
        while l1 and l2:
            if l1.val <= l2.val:
                curr.next = l1
                l1 = l1.next
            else:
                curr.next = l2
                l2 = l2.next
            curr = curr.next
        curr.next = l1 or l2
        return dummy.next

    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            l1 = lists[i]
            l2 = lists[i + 1] if i + 1 < len(lists) else None
            merged.append(merge2(l1, l2))
        lists = merged
    return lists[0]
```
**Time**: O(N log k)。**Space**: O(1) 额外空间（原地修改）+ O(log k) 递归栈。

---

## [LC 815](lc://815): Bus Routes

> **题目描述** [hard]: You are given an array routes where routes[i] is a bus route that the ith bus repeats forever. Return the least number of buses you must take to travel from source to target. Return -1 if it is not possible.

### **My Solution: BFS on Routes (有性能隐患)**

```python
class Solution:
    def numBusesToDestination(self, routes, source, target):
        if source == target:
            return 0
        routeData = {i: set(route) for i, route in enumerate(routes)}
        queue = deque()
        visited = set()
        for i in routeData:
            if source in routeData[i]:
                queue.append(i)
                visited.add(i)
        if not queue:
            return -1
        ans = 1
        while queue:
            for _ in range(len(queue)):
                cur = queue.popleft()
                if target in routeData[cur]:
                    return ans
                for key in routeData:  # O(R) per route -- bottleneck!
                    if key not in visited and routeData[key] & routeData[cur]:
                        queue.append(key)
                        visited.add(key)
            ans += 1
        return -1
```
- **问题**: 内层遍历所有路线 O(R)，集合交集 O(S) -> 总 O(R^2 * S)，routes 多时 TLE

### **最优解: BFS on Stops + stop_to_routes 映射**

```python
from collections import deque, defaultdict

class Solution:
    def numBusesToDestination(self, routes, source, target):
        if source == target:
            return 0
        stop_to_routes = defaultdict(set)
        for i, route in enumerate(routes):
            for stop in route:
                stop_to_routes[stop].add(i)

        visited_routes = set()
        visited_stops = set([source])
        queue = deque([source])
        buses = 0

        while queue:
            buses += 1
            for _ in range(len(queue)):
                stop = queue.popleft()
                for route_id in stop_to_routes[stop]:
                    if route_id in visited_routes:
                        continue
                    visited_routes.add(route_id)
                    for next_stop in routes[route_id]:
                        if next_stop == target:
                            return buses
                        if next_stop not in visited_stops:
                            visited_stops.add(next_stop)
                            queue.append(next_stop)
        return -1
```
- 时间: O(R * S)，空间: O(R * S)
- 关键: stop_to_routes 映射避免 O(R^2) 两两比较


## [LC 981](lc://981): Time Based Key-Value Store

> **题目描述** [medium]: Design a time-based key-value data structure that can store multiple values for the same key at different time stamps and retrieve the key&#39;s value at a certain timestamp.

Implement the TimeMap class:


	TimeMap() Initializes the object of the data structure.
	void set(String key, String value, int timestamp) Stores the key key with the value value at the given time timestamp.
...(truncated)


**Pattern**: Binary Search on Timestamps（在时间戳上的二分查找）

**二分查找 (Binary Search，BS)** 应用：每个 key 对应一个按时间戳有序排列的列表（由 set 操作保证单调递增），get 时用 `bisect_right` 找到最大的满足 `timestamp <= 给定值` 的条目。

```python
import bisect

class TimeMap:
    def __init__(self):
        self.store = {}  # key -> [(timestamp, value), ...]

    def set(self, key, value, timestamp):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))

    def get(self, key, timestamp):
        if key not in self.store:
            return ""
        entries = self.store[key]
        # Binary search for largest timestamp <= given timestamp
        idx = bisect.bisect_right(entries, (timestamp, chr(127))) - 1
        if idx < 0:
            return ""
        return entries[idx][1]
```
**Time**: set O(1)，get O(log n)。**Space**: O(n)。

### Follow-ups

**每秒 100 万次以上请求**：按 key 哈希值分片到多台机器。每台机器负责一个 key 子集，使用**一致性哈希 (Consistent Hashing，一致哈希)** 实现均匀分布。

**线程安全**：对每个 key 使用读写锁（多读单写）。多个读操作可并发，写操作独占访问。或使用基于 CAS 的无锁追加列表。

**均摊时间复杂度**：set 的均摊时间为 O(1)（列表追加）。get 为 O(log n) 二分查找。题目保证时间戳单调递增，因此列表始终有序，无需额外排序。

---

## [LC 17](lc://17): Letter Combinations of a Phone Number

> **题目描述** [medium]: Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order.
A mapping of digits to letters (just like on the telephone buttons) is given below. Note that 1 does not map to any letters.

 
Example 1:

Input: digits = "23"
Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]

Example 2:

Input: digits


**Pattern**: Backtracking（回溯）

**回溯 (Backtracking)** 枚举所有可能的字母组合：对每个数字位，依次尝试对应的每个字母，递归到下一位，完成后撤销选择。

```python
def letterCombinations(digits):
    """Backtracking to generate all letter combinations."""
    if not digits:
        return []

    mapping = {
        ''2'': ''abc'', ''3'': ''def'', ''4'': ''ghi'', ''5'': ''jkl'',
        ''6'': ''mno'', ''7'': ''pqrs'', ''8'': ''tuv'', ''9'': ''wxyz''
    }
    result = []

    def backtrack(idx, path):
        if idx == len(digits):
            result.append(''''.join(path))
            return
        for char in mapping[digits[idx]]:
            path.append(char)
            backtrack(idx + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```
**Time**: O(4^n * n)，其中 n 为 digits 长度。**Space**: O(n) 递归深度。

### VARIANT: 10-digit Phone Number

算法不变，但输出规模大幅增加（最多 4^10 ≈ 100 万种组合）。可改用迭代方式或生成器以节省内存：

```python
def letterCombinations_iterative(digits):
    """Iterative BFS-style combination generation."""
    if not digits:
        return []
    mapping = {''2'':''abc'',''3'':''def'',''4'':''ghi'',''5'':''jkl'',
               ''6'':''mno'',''7'':''pqrs'',''8'':''tuv'',''9'':''wxyz''}
    combos = ['''']
    for digit in digits:
        combos = [prev + char for prev in combos for char in mapping[digit]]
    return combos
```

---

## [LC 79](lc://79): Word Search

> **题目描述** [medium]: Given an m x n grid of characters board and a string word, return true if word exists in the grid.
The word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.
 
Example 1:


Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"
Output:


**Pattern**: Backtracking / DFS（回溯 / 深度优先搜索）

### Standard DFS

在网格中搜索单词：对每个起始格子运行 DFS，标记已访问格子（防止重复使用），找到匹配后恢复原值（回溯）。

```python
def exist(board, word):
    """DFS backtracking on grid."""
    m, n = len(board), len(board[0])

    def dfs(i, j, k):
        if k == len(word):
            return True
        if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[k]:
            return False
        temp = board[i][j]
        board[i][j] = ''#''  # mark visited
        for di, dj in [(0,1),(0,-1),(1,0),(-1,0)]:
            if dfs(i+di, j+dj, k+1):
                return True
        board[i][j] = temp  # restore
        return False

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False
```
**Time**: O(m*n*3^L)，其中 L 为单词长度（每步有 3 个方向可选，因为不能回头）。**Space**: O(L)。

### VARIANT: 8 Directions, Straight Line Only

8 方向但必须走直线（不能转弯），无需回溯，直接枚举每个起点和方向即可：

```python
def exist_8dir_straight(board, word):
    """8 directions, must go in straight line (no turning).
    Much simpler -- O(R*C*8*L) enumeration, no backtracking."""
    m, n = len(board), len(board[0])
    L = len(word)
    directions = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    for i in range(m):
        for j in range(n):
            if board[i][j] != word[0]:
                continue
            for di, dj in directions:
                # Check if word fits in this direction
                ei, ej = i + di*(L-1), j + dj*(L-1)
                if ei < 0 or ei >= m or ej < 0 or ej >= n:
                    continue
                match = True
                for k in range(L):
                    if board[i+di*k][j+dj*k] != word[k]:
                        match = False
                        break
                if match:
                    return True
    return False
```
**Time**: O(R*C*8*L)。**Space**: O(1)。

---

## [LC 977](lc://977): Squares of a Sorted Array

> **题目描述** [?]: Given an array of integers `A` sorted in non-decreasing order, return an
array of the squares of each number, also in sorted non-decreasing order.

Example 1:

Input: [-4,-1,0,3,10]
Output: [0,1,9,16,100]

Example 2:

Input: [-7,-3,2,3,11]
Output: [4,9,9,49,121]

Note:

- `1 <= A.length <= 10000`

- `-10000 <= A[i] <= 10000`

- `A` is sorted in non-decreasing order.


**Pattern**: Two Pointers（双指针）

**双指针 (Two Pointers)** 从数组两端向中间移动：绝对值最大的元素在两端，因此每次取两端绝对值较大者的平方，从结果数组末尾向前填充。

```python
def sortedSquares(nums):
    """Two pointers from both ends -- largest absolute values at edges."""
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    pos = n - 1  # fill from the end

    while left <= right:
        if abs(nums[left]) > abs(nums[right]):
            result[pos] = nums[left] ** 2
            left += 1
        else:
            result[pos] = nums[right] ** 2
            right -= 1
        pos -= 1

    return result
```
**Time**: O(n)。**Space**: O(n) 存储结果。

---

## [LC 987](lc://987): Vertical Order Traversal of a Binary Tree

> **题目描述** [hard]: Given a binary tree, return the vertical order traversal of its nodes values.

For each node at position `(X, Y)`, its left and right children respectively will
be at positions `(X-1, Y-1)` and `(X+1, Y-1)`.

Running a vertical line from `X = -infinity` to `X = +infinity`,
whenever the vertical line touches some nodes, we report the values of the nodes in order
from top to bottom (decreasing `Y` c


**Pattern**: BFS/DFS with Column Tracking（带列追踪的 BFS/DFS）

BFS 遍历时记录每个节点的 (行, 列) 坐标，按列分组后对每列内元素先按行、再按值排序。

```python
from collections import defaultdict, deque

def verticalTraversal(root):
    """BFS with (row, col) tracking, sort by col -> row -> value."""
    if not root:
        return []

    col_map = defaultdict(list)
    q = deque([(root, 0, 0)])  # (node, row, col)

    while q:
        node, row, col = q.popleft()
        col_map[col].append((row, node.val))
        if node.left:
            q.append((node.left, row + 1, col - 1))
        if node.right:
            q.append((node.right, row + 1, col + 1))

    result = []
    for col in sorted(col_map):
        # Sort by row first, then by value
        col_map[col].sort()
        result.append([val for _, val in col_map[col]])

    return result
```
**Time**: O(n log n)。**Space**: O(n)。

---

## [LC 1197](lc://1197): Minimum Knight Moves

> **题目描述** [medium]: In an infinite chess board with coordinates from `-infinity` to
`+infinity`, you have a knight at square `[0,
0]`.

A knight has 8 possible moves it can make, as illustrated below. Each move is two
squares in a cardinal direction, then one square in an orthogonal direction.

Return the minimum number of steps needed to move the knight to the square `[x,
y]`.  It is guaranteed the answer exists.

E


**Pattern**: BFS（广度优先搜索）

利用棋盘的对称性将目标映射到第一象限（取绝对值），减少搜索空间。BFS 保证找到的第一条到达目标的路径即为最短路径。

```python
from collections import deque

def minKnightMoves(x, y):
    """BFS from (0,0) to (|x|,|y|). Use symmetry to stay in quadrant I."""
    x, y = abs(x), abs(y)
    if x == 0 and y == 0:
        return 0

    visited = {(0, 0)}
    q = deque([(0, 0, 0)])
    moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

    while q:
        cx, cy, steps = q.popleft()
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) == (x, y):
                return steps + 1
            # Pruning: stay within reasonable bounds
            if (nx, ny) not in visited and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                visited.add((nx, ny))
                q.append((nx, ny, steps + 1))
```
**Time**: O(|x|*|y|) 最坏情况。**Space**: O(|x|*|y|)。

### VARIANT: Finite Board Size n

棋盘大小有限（n x n），BFS 时需检查边界条件，无路可达时返回 -1：

```python
def minKnightMoves_finite(n, x, y):
    """BFS on n x n board."""
    if x == 0 and y == 0:
        return 0
    visited = {(0, 0)}
    q = deque([(0, 0, 0)])
    moves = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
    while q:
        cx, cy, steps = q.popleft()
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) == (x, y):
                return steps + 1
            if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny, steps + 1))
    return -1  # unreachable
```

---

## [LC 1697](lc://1697): Checking Existence of Edge Length Limited Paths

> **题目描述** [hard]: An undirected graph of `n` nodes is defined by `edgeList`,
where `edgeList[i] = [ui, vi, disi]` denotes
an edge between nodes `ui` and `vi` with
distance `disi`. Note that there may be multiple
edges between two nodes.

Given an array `queries`, where `queries[j] = [pj,
qj, limitj]`, your task is to determine for each `queries[j]`
whether there is a path between `pj` and
`qj` such that each edge o


**Pattern**: Offline Queries + Union Find（离线查询 + 并查集）

**离线查询 (Offline Queries)** 技巧：将所有边和查询按权重/限制排序后一起处理。对每个查询，只将权重严格小于限制的边加入并查集，再判断两端点是否连通。

```python
def distanceLimitedPathsExist(n, edgeList, queries):
    """Sort edges and queries by weight/limit. Process offline with UF."""
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1

    # Sort edges by weight
    edgeList.sort(key=lambda e: e[2])

    # Sort queries by limit, keep original index
    indexed_queries = sorted(enumerate(queries), key=lambda x: x[1][2])

    result = [False] * len(queries)
    edge_idx = 0

    for qi, (a, b, limit) in indexed_queries:
        # Add all edges with weight < limit
        while edge_idx < len(edgeList) and edgeList[edge_idx][2] < limit:
            u, v, w = edgeList[edge_idx]
            union(u, v)
            edge_idx += 1
        result[qi] = find(a) == find(b)

    return result
```
**Time**: O((E + Q) log(E + Q) + (E + Q) * alpha(n))。**Space**: O(n + Q)。

### VARIANT: Edge Weight >= k

变体要求路径上所有边权重均不小于 k。将边和查询按权重降序排列，逐步加入满足条件的边：

```python
def pathsWithMinWeight(n, edgeList, queries):
    """All edges on path must have weight >= k."""
    parent = list(range(n))
    rank = [0] * n
    # ... same find/union ...

    edgeList.sort(key=lambda e: -e[2])  # descending by weight
    indexed_queries = sorted(enumerate(queries), key=lambda x: -x[1][2])

    result = [False] * len(queries)
    edge_idx = 0

    for qi, (a, b, k) in indexed_queries:
        while edge_idx < len(edgeList) and edgeList[edge_idx][2] >= k:
            u, v, w = edgeList[edge_idx]
            union(u, v)
            edge_idx += 1
        result[qi] = find(a) == find(b)

    return result
```

---

## [LC 549](lc://549): Binary Tree Longest Consecutive Sequence II

> **题目描述** [medium]: Given a binary tree, you need to find the length of Longest Consecutive Path in Binary
Tree.

Especially, this path can be either increasing or decreasing. For example, [1,2,3,4] and
[4,3,2,1] are both considered valid, but the path [1,2,4,3] is not valid. On the other hand,
the path can be in the child-Parent-child order, where not necessarily be parent-child
order.

Example 1:

Input:
1
/ \
2   


**Pattern**: Tree DP（树上动态规划）

每个节点向上汇报两个值：以该节点为端点的最长递增序列长度和最长递减序列长度。过该节点的最长连续路径 = 递增长度 + 递减长度 - 1（节点本身不重复计数）。

```python
def longestConsecutive(root):
    """DFS tracking increasing and decreasing lengths per node."""
    max_len = [0]

    def dfs(node):
        """Returns (increasing_len, decreasing_len) through this node."""
        if not node:
            return (0, 0)

        inc = dec = 1  # at minimum, the node itself

        if node.left:
            li, ld = dfs(node.left)
            if node.left.val == node.val + 1:
                inc = max(inc, li + 1)
            if node.left.val == node.val - 1:
                dec = max(dec, ld + 1)

        if node.right:
            ri, rd = dfs(node.right)
            if node.right.val == node.val + 1:
                inc = max(inc, ri + 1)
            if node.right.val == node.val - 1:
                dec = max(dec, rd + 1)

        # Path through this node: inc + dec - 1 (don''t double-count node)
        max_len[0] = max(max_len[0], inc + dec - 1)
        return (inc, dec)

    dfs(root)
    return max_len[0]
```
**Time**: O(n)。**Space**: O(H)。

---

## [LC 2503](lc://2503): Maximum Number of Points From Grid Queries

> **题目描述** [hard]: Given an m x n integer matrix grid and an array queries. For each queries[i], start from the top left cell of the matrix and repeatedly visit cells of strictly less value. Return the maximum number of points achievable for each query.


**Pattern**: BFS + Sort Queries（BFS + 排序查询）

将查询按限制值排序，用**最小堆 (Min-Heap)** 维护 BFS 边界。对每个查询，将所有值严格小于限制的可达格子扩展进入已统计点数中，实现增量计算。

```python
import heapq

def maxPoints(grid, queries):
    """Process queries in sorted order. BFS with min-heap for frontier."""
    m, n = len(grid), len(grid[0])

    # Sort queries with original indices
    sorted_q = sorted(enumerate(queries), key=lambda x: x[1])

    result = [0] * len(queries)
    visited = [[False] * n for _ in range(m)]
    heap = [(grid[0][0], 0, 0)]  # (value, row, col)
    visited[0][0] = True
    points = 0

    for qi, limit in sorted_q:
        # Expand BFS frontier: add all cells with value < limit
        while heap and heap[0][0] < limit:
            val, x, y = heapq.heappop(heap)
            points += 1
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < m and 0 <= ny < n and not visited[nx][ny]:
                    visited[nx][ny] = True
                    heapq.heappush(heap, (grid[nx][ny], nx, ny))
        result[qi] = points

    return result
```
**Time**: O(m*n*log(m*n) + Q*log(Q))。**Space**: O(m*n)。

---

## [LC 2858](lc://2858): Minimum Edge Reversals So Every Node Is Reachable

> **题目描述** [hard]: Given a directed tree with n nodes rooted at node 0. Find the minimum number of edge reversals needed so that every node can reach node 0, for each possible root.


**Pattern**: Re-rooting DP（换根动态规划）

**换根 DP (Re-rooting DP)** 分两步：先以节点 0 为根做一次 DFS 得到 dp[0]，再通过第二次 DFS 将根从父节点"移动"到子节点，利用父节点的 dp 值 O(1) 推导子节点的 dp 值。

```python
from collections import defaultdict

def minEdgeReversals(n, edges):
    """Re-rooting DP: DFS from 0, then propagate to all nodes."""
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append((v, 0))  # original direction: cost 0
        graph[v].append((u, 1))  # reversed: cost 1

    dp = [0] * n

    # Step 1: DFS from node 0 to compute dp[0]
    def dfs(node, parent):
        cost = 0
        for neighbor, rev_cost in graph[node]:
            if neighbor != parent:
                cost += rev_cost + dfs(neighbor, node)
        return cost

    dp[0] = dfs(0, -1)

    # Step 2: Re-root to compute dp for all nodes
    def reroot(node, parent):
        for neighbor, rev_cost in graph[node]:
            if neighbor != parent:
                # Moving root from node to neighbor:
                # If edge node->neighbor was original (rev_cost=0): now need to reverse it (+1)
                # If edge was reversed (rev_cost=1): now it''s in correct direction (-1)
                dp[neighbor] = dp[node] + (1 if rev_cost == 0 else -1)
                reroot(neighbor, node)

    reroot(0, -1)
    return dp
```
**Time**: O(n)。**Space**: O(n)。

**1point3acres 面经注意点**：需自行构建邻接表，注意输入可能是 1-indexed。根据题目要求，返回翻转次数最少的节点编号或整个 dp 数组。

---

## [LC 2791](lc://2791): Count Paths That Can Form a Palindrome in a Tree

> **题目描述** [hard]: Given a tree rooted at node 0 with n nodes. Each node has a character value. For each query node, count how many nodes v exist on the path from the query node to root such that the characters can be rearranged to form a palindrome.


**Pattern**: Bitmask XOR + DFS（位掩码异或 + 深度优先搜索）

**关键洞察**：路径 u->v 上的字符集等于从根到 u 的路径字符集 XOR 从根到 v 的路径字符集（公共前缀抵消）。路径可构成回文 = XOR 结果中最多有 1 个 bit 为 1（至多一个字符出现奇数次）。

```python
from collections import defaultdict

def countPalindromePaths(parent, s):
    """DFS with XOR bitmask prefix. Palindrome = at most 1 odd-count char."""
    n = len(parent)
    children = defaultdict(list)
    for i in range(1, n):
        children[parent[i]].append(i)

    # prefix[node] = XOR of character bitmasks from root to node
    prefix = [0] * n
    count = 0

    # Count pairs where prefix[u] XOR prefix[v] has at most 1 bit set
    freq = defaultdict(int)
    freq[0] = 1  # root''s prefix is 0

    def dfs(node):
        nonlocal count
        for child in children[node]:
            bit = 1 << (ord(s[child]) - ord(''a''))
            prefix[child] = prefix[node] ^ bit

            # Count paths ending at child:
            # Case 1: prefix[child] XOR prefix[ancestor] == 0 (all even)
            count += freq[prefix[child]]
            # Case 2: XOR has exactly 1 bit set
            for i in range(26):
                count += freq[prefix[child] ^ (1 << i)]

            freq[prefix[child]] += 1
            dfs(child)

    dfs(0)
    return count
```
**Time**: O(26n)。**Space**: O(n)。

**关键洞察**：路径 u->v 上的字符来自 root->u 的前缀异或 root->v 的前缀。可构成回文意味着至多 1 个字符出现奇数次，即 XOR 结果至多有 1 个 bit 为 1。

---

## [LC 1696](lc://1696): Jump Game VI

> **题目描述** [medium]: You are given a 0-indexed integer array `nums` and an
integer `k`.

You are initially standing at index `0`. In one move, you can jump at most
`k` steps forward without going outside the boundaries of the array. That
is, you can jump from index `i` to any index in the range `[i + 1,
min(n - 1, i + k)]` inclusive.

You want to reach the last index of the array (index `n - 1`). Your
score is the sum


**Pattern**: DP + Sliding Window Max (Deque)（动态规划 + 单调双端队列滑动窗口最大值）

**单调双端队列 (Monotonic Deque)** 维护大小为 k 的窗口内 dp 值的最大值：队列头部始终保存窗口内最大 dp 值的下标，新元素加入前从队尾弹出所有不大于它的元素。

```python
from collections import deque

def maxResult(nums, k):
    """DP with monotonic deque for sliding window maximum."""
    n = len(nums)
    dp = [0] * n
    dp[0] = nums[0]
    dq = deque([0])  # indices of dp values in decreasing order

    for i in range(1, n):
        # Remove elements outside window
        while dq and dq[0] < i - k:
            dq.popleft()

        dp[i] = nums[i] + dp[dq[0]]  # best reachable score

        # Maintain decreasing deque
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)

    return dp[-1]
```
**Time**: O(n)。**Space**: O(k)。

### VARIANT: Jump +1 or +Prime Ending in 3

变体：每步可跳 +1 或 +任意以 3 结尾的素数（3, 13, 23, ...）。先用筛法预计算所有满足条件的素数，再做 DP：

```python
def jumpGamePrime(arr):
    """Jump +1 or +prime ending in 3 (3,13,23,...). Maximize score."""
    n = len(arr)

    # Precompute primes ending in 3 up to n
    def sieve_primes_ending_3(limit):
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return [p for p in range(2, limit + 1) if is_prime[p] and p % 10 == 3]

    primes = sieve_primes_ending_3(n)
    jumps = [1] + primes  # can always jump +1, or +prime ending in 3

    dp = [float(''-inf'')] * n
    dp[0] = arr[0]

    for i in range(1, n):
        for jump in jumps:
            prev = i - jump
            if prev >= 0 and dp[prev] != float(''-inf''):
                dp[i] = max(dp[i], dp[prev] + arr[i])

    return dp[-1] if dp[-1] != float(''-inf'') else -1
```
**Time**: O(n * P)，其中 P 为不超过 n 的以 3 结尾的素数个数。**Space**: O(n)。

---

## Edge Cases & General Tips

### Common Edge Cases to Check（常见边界情况检查）

- 空输入 / 单元素
- 所有元素相同
- 已有序 / 逆序排列
- 树只有左子树或只有右子树
- 图中存在不连通分量
- k = 0 或 k = n

### Complexity Analysis Checklist（复杂度分析清单）

对每个题解，务必说明：
1. 时间复杂度及主导操作的解释
2. 空间复杂度，区分辅助空间与输入空间
3. 若最好/最坏情况差异显著，分别说明', updated_at = datetime('now') WHERE id = 30;

-- doc 31 (Uber BPS Custom Problem Solutions): lc=4 leetcode=0 custom=0
UPDATE company_documents SET content = '# Uber BPS -- 自定义（非 LC）题目解题方案

> Uber 面试专属题目的解答，这些题目没有对应的标准 LeetCode 编号。
> 每题包含：题目描述（根据 1p3a 重构）、解题思路、简洁 Python 代码、
> 时间/空间复杂度、边界情况及延伸问题。
>
> Task: T-P0-243

---

## Table of Contents

1. [Purchase Optimization](#1-purchase-optimization)

> **题目描述**: [1p3a Uber] Given prices array and queries (pos, amount), find max items purchasable starting from pos with given amount. Approach: prefix sum + binary search on prefix array. Multiple 1p3a reports confirm this as a recurring Uber problem.

2. [Customer Revenue & Referral Tracking (OOD)](#2-customer-revenue--referral-tracking-ood)

> **题目描述**: [1p3a Uber] OOD design problem. API: insertNewCustomer(revenue, referrerID) -> customerID, getLowestK(k, minTotalRevenue) -> Set of k customer IDs. Revenue propagates up referral tree. Must handle tree aggregation efficiently. Key: maintain sorted structure for getLowestK queries.

3. [Uber Rider Connection Log (Union Find)](#3-uber-rider-connection-log-union-find)

> **题目描述**: [1p3a Uber] Parse timestamped logs: ''A shared-ride-with B''. Find earliest time all riders connected (transitive). Follow-up: handle ''block'' events (A blocked B). UF cannot handle deletions -- must use BFS/DFS rebuild. Interviewer pushes hard, wants both approaches discussed. Rayin style: push-to-fai

4. [Elevator Binary Search OA](#4-elevator-binary-search-oa)

> **题目描述**: [1p3a Uber] OA problem. Array where each cell has a move distance (positive = forward, negative = backward). Find minimum starting index that never goes out of left boundary. Linear scan: traverse and track when boundary is violated, update answer.

5. [Server Throughput with Heap](#5-server-throughput-with-heap)
6. [Cart & Pricing Engine (OOD)](#6-cart--pricing-engine-ood)
7. [Circular Array Shortest Jump](#7-circular-array-shortest-jump)

> **题目描述**: [1p3a Uber] Given circular array with jump distances, find shortest path from index A to B. arr[i] = exact jump distance (left or right). BFS on indices.

8. [Robot Distance in Grid](#8-robot-distance-in-grid)

> **题目描述**: [1p3a Uber] Grid with robots(O), empty(E), obstacles(X). Given distance array [left, top, bottom, right], find robot matching distances. DP to precompute distances from each cell to nearest obstacle in 4 directions.

9. [Min Operations n to 0](#9-min-operations-n-to-0)

> **题目描述**: [1p3a Uber] Each operation: n += or -= 2^i. Find min operations to reach 0. Optimal: binary/NAF analysis. n%%2==0: shift right. n%%4==3: +1. n%%4==1: -1. Count operations on odd numbers.

10. [Shortest Subarray with k Distinct](#10-shortest-subarray-with-k-distinct)

> **题目描述**: [1p3a Uber] Find shortest subarray containing at least k distinct integers. Standard two-pointer / sliding window with counter. Expand right until >= k distinct, shrink left to minimize length.

11. [Price Discount (Monotonic Stack)](#11-price-discount-monotonic-stack)

> **题目描述**: [1p3a Uber] OA problem. For each i, find first j > i where prices[j] <= prices[i]. If discount exists: final = prices[i] - prices[j]. If no discount: sell at original price. Output: (1) total discounted sum, (2) indices sold at original price (0-based, ascending). Classic monotonic stack application

12. [Balanced Permutation](#12-balanced-permutation)
13. [Elevator/Stairs Energy](#13-elevatorstairs-energy)
14. [N-ary Tree 3-Part](#14-n-ary-tree-3-part)
15. [Max Throughput with Budget](#15-max-throughput-with-budget)

> **题目描述**: [1p3a Uber] Multiple services, each has current throughput and scale cost. Pipeline: service i+1 input comes from service i. Bottleneck = min throughput. Budget constraint. Binary search on target throughput. For each candidate, check if total cost to raise all services to target <= budget.

16. [Parking Lot (OOD)](#16-parking-lot-ood)
17. [Task Assignment to 2 People](#17-task-assignment-to-2-people)

> **题目描述**: [1p3a Uber] n tasks, reward1[i]/reward2[i] per person. Person 1 must do exactly k tasks. Maximize total reward. Greedy: sort by diff(r1 - r2) descending, pick top k for person 1, rest for person 2. Base sum = sum(reward2), add top-k diffs.

18. [Jump Game Prime-Ending Variant](#18-jump-game-prime-ending-variant)
19. [Min Edge Reversal for Optimal Root](#19-min-edge-reversal-for-optimal-root)
20. [Palindrome Paths in Tree](#20-palindrome-paths-in-tree)
21. [Minesweeper Grid Generator](#21-minesweeper-grid-generator)

> **题目描述**: [1p3a Uber] Place N mines randomly on 2D grid. Follow-up: optimize code quality -- remove unnecessary set, reduce variables, simplify logic. Interviewer pushes for cleaner code iteratively. Focus is on code quality, not algorithmic complexity.

22. [2D Grid Nearest Exit (BFS)](#22-2d-grid-nearest-exit-bfs)

> **题目描述**: [1p3a Uber] BFS from starting point to find nearest boundary cell. Standard multi-source BFS variant. Similar to [LC 1926](lc://1926).

23. [Lock Combination BFS](#23-lock-combination-bfs)

> **题目描述**: [1p3a Uber] Tech screening problem. Find minimum steps to unlock. BFS on state space. Similar to [LC 752](lc://752) (Open the Lock).

24. [Non-overlapping Interval Triples](#24-non-overlapping-interval-triples)

> **题目描述**: [1p3a Uber] Count groups of 3 intervals with no pairwise overlap. Sort intervals, enumerate combinations efficiently. Time pressure: 40 min for 2 problems, interviewer moves on quickly.

25. [City Graph BFS Sort](#25-city-graph-bfs-sort)

> **题目描述**: [1p3a Uber] Given city graph + start city, sort cities by distance. Ties: smaller index first. BFS to compute distances, then sort. Time pressure: paired with interval triples in same 40-min session.


---

## 1. Purchase Optimization

**Pattern**: **Prefix Sum（前缀和）** + **Binary Search（二分查找）**

### Problem Statement

给定一个升序排列的价格数组 `prices`，以及一组查询 `(pos, amount)`，
对于每个查询，求从索引 `pos` 开始、预算为 `amount` 时，最多能购买多少件商品。

### Approach

1. 对 prices 排序（若未排序）。
2. 构建前缀和数组：`prefix[i] = prices[0] + prices[1] + ... + prices[i-1]`。
3. 对于每个查询 `(pos, amount)`：二分查找最大的 `end`，使得
   `prefix[end] - prefix[pos] <= amount`。

```python
import bisect
from typing import List, Tuple


def max_items_purchasable(
    prices: List[int], queries: List[Tuple[int, int]]
) -> List[int]:
    """For each (pos, amount), find max items buyable from prices[pos:]."""
    prices.sort()
    n = len(prices)

    # prefix[i] = sum of prices[0..i-1]
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + prices[i]

    results = []
    for pos, amount in queries:
        if pos >= n:
            results.append(0)
            continue
        # Find largest end such that prefix[end] - prefix[pos] <= amount
        # i.e. prefix[end] <= prefix[pos] + amount
        target = prefix[pos] + amount
        end = bisect.bisect_right(prefix, target, lo=pos, hi=n + 1) - 1
        results.append(end - pos)

    return results
```

**时间复杂度**：排序 O(n log n) + 构建前缀和 O(n) + 处理 q 个查询 O(q log n)。
**空间复杂度**：O(n)，用于存储前缀和数组。

### Edge Cases
- `amount` 为 0 -> 返回 0
- `pos` 超出数组范围 -> 返回 0
- 预算足以购买所有剩余商品

### Follow-up: Unsorted Prices

若价格数组未排序，需先排序。若查询需要原始索引，排序前需维护一个索引映射。

---

## 2. Customer Revenue & Referral Tracking (OOD)

**Pattern**: **Object-Oriented Design（面向对象设计）** / **Tree Aggregation（树形聚合）**

### Problem Statement

设计一个系统，支持以下操作：
- `insertNewCustomer(revenue, referrerID)`：添加一位客户，其收入为 revenue，由 referrerID 推荐。收入沿推荐链向上传播。
- `getLowestK(k, minTotalRevenue)`：返回总收入（直接收入 + 所有被推荐人收入之和）超过 minTotalRevenue 的 k 位总收入最低的客户。

### Approach

每个客户记录直接收入和 `total_revenue`（直接 + 子树收入之和）。
插入时，沿推荐链向上传播收入。对于 `getLowestK`，维护一个有序结构或过滤扫描。

```python
import heapq
from typing import List, Optional


class Customer:
    """A customer node in the referral tree."""

    def __init__(self, cid: int, revenue: float, referrer_id: Optional[int]):
        self.cid: int = cid
        self.revenue: float = revenue
        self.total_revenue: float = revenue  # direct + subtree
        self.referrer_id: Optional[int] = referrer_id
        self.referrals: List[int] = []


class ReferralSystem:
    """Referral tracking with upward revenue propagation."""

    def __init__(self) -> None:
        self.customers: dict[int, Customer] = {}
        self._next_id: int = 0

    def insert_new_customer(
        self, revenue: float, referrer_id: Optional[int] = None
    ) -> int:
        """Insert customer and propagate revenue up the referral chain."""
        cid = self._next_id
        self._next_id += 1

        customer = Customer(cid, revenue, referrer_id)
        self.customers[cid] = customer

        if referrer_id is not None and referrer_id in self.customers:
            self.customers[referrer_id].referrals.append(cid)
            # Propagate revenue upward
            current_id = referrer_id
            while current_id is not None:
                self.customers[current_id].total_revenue += revenue
                current_id = self.customers[current_id].referrer_id

        return cid

    def get_lowest_k(self, k: int, min_total_revenue: float) -> List[int]:
        """Return k customers with lowest total_revenue >= min_total_revenue."""
        candidates = [
            (c.total_revenue, c.cid)
            for c in self.customers.values()
            if c.total_revenue >= min_total_revenue
        ]
        # Use heapq.nsmallest for efficiency when k << n
        smallest = heapq.nsmallest(k, candidates)
        return [cid for _, cid in smallest]
```

**时间复杂度**：
- `insert`：O(D)，D 为推荐树的深度（收入向上传播）。
- `getLowestK`：O(n log k)，使用堆选择。

**空间复杂度**：O(n)，存储所有客户。

### Edge Cases
- 无推荐人的客户（根节点）
- 深度较大的推荐链（O(D) 传播）
- k 大于满足条件的客户数量

### Follow-up: Efficient getLowestK

若查询频繁，可维护一个按 total_revenue 索引的有序容器（如 sortedcontainers 的 SortedList）。
插入时：删除旧条目、更新、重新插入，可实现插入 O(log n)、查询 O(k + log n)。

---

## 3. Uber Rider Connection Log (Union Find)

**Pattern**: **Union Find（并查集）** / **Graph Connectivity（图连通性）**

### Problem Statement

给定形如 `"<timestamp> A shared-ride-with B"` 的带时间戳日志，求所有乘客首次全部连通（直接或间接）的最早时间戳。

**延伸问题**：处理 `"<timestamp> A blocked B"`（断开连接）事件。

### Approach -- Part 1: Union Find

按时间顺序处理日志。对每条 `shared-ride-with` 记录，合并两位乘客。
每次合并后检查所有乘客是否已在同一连通分量中。

```python
from typing import List, Optional, Tuple


class UnionFind:
    """Weighted Union-Find with path compression."""

    def __init__(self, n: int):
        self.parent: List[int] = list(range(n))
        self.rank: List[int] = [0] * n
        self.components: int = n

    def find(self, x: int) -> int:
        """Find root with path compression."""
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        """Union by rank. Returns True if a merge occurred."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.components -= 1
        return True


def earliest_full_connection(
    logs: List[Tuple[int, str, str]], n_riders: int
) -> Optional[int]:
    """Find earliest timestamp when all n_riders are connected.

    Args:
        logs: List of (timestamp, rider_a, rider_b) sorted by timestamp.
        n_riders: Total number of distinct riders.

    Returns:
        Earliest timestamp or None if never fully connected.
    """
    rider_to_id: dict[str, int] = {}
    next_id = 0

    def get_id(name: str) -> int:
        nonlocal next_id
        if name not in rider_to_id:
            rider_to_id[name] = next_id
            next_id += 1
        return rider_to_id[name]

    uf = UnionFind(n_riders)

    for timestamp, a, b in logs:
        id_a, id_b = get_id(a), get_id(b)
        uf.union(id_a, id_b)
        if uf.components == 1:
            return timestamp

    return None
```

**时间复杂度**：O(E * alpha(N)) ≈ O(E)，E 为日志条数。
**空间复杂度**：O(N)，用于并查集结构。

### Follow-up: Handling "block" Events (Deletions)

并查集**不支持**删除操作。有两种方案：

**方案 A：离线处理——逆序**

若需要找所有人**最后一次**全部连通的时间，可逆序处理事件：断开变合并，共乘变边。但这改变了问题语义。

**方案 B：使用 BFS/DFS 重建**

对于需要同时处理连接和断开事件的在线场景，维护邻接表。每次事件后运行 **BFS (Breadth-First Search，广度优先搜索)** 或 **DFS (Depth-First Search，深度优先搜索)** 检查连通性。

```python
from collections import defaultdict, deque
from typing import List, Optional, Tuple


def earliest_full_connection_with_blocks(
    logs: List[Tuple[int, str, str, str]], n_riders: int
) -> Optional[int]:
    """Handle both ''connect'' and ''block'' events.

    Args:
        logs: (timestamp, action, rider_a, rider_b) where action is
              ''shared-ride-with'' or ''blocked''.
    """
    graph: dict[str, set[str]] = defaultdict(set)
    all_riders: set[str] = set()

    def is_connected() -> bool:
        if len(all_riders) < n_riders:
            return False
        start = next(iter(all_riders))
        visited: set[str] = set()
        queue = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return len(visited) == len(all_riders)

    for timestamp, action, a, b in logs:
        all_riders.add(a)
        all_riders.add(b)

        if action == "shared-ride-with":
            graph[a].add(b)
            graph[b].add(a)
        elif action == "blocked":
            graph[a].discard(b)
            graph[b].discard(a)

        if is_connected():
            return timestamp

    return None
```

**时间复杂度**：O(E * (V + E))——每次事件后进行 BFS。对于大规模输入，可用 Link-Cut Tree 或 ETT（欧拉回路树）优化至 O(log N) 每次操作。
**空间复杂度**：O(V + E)，用于邻接表。

### Edge Cases
- 只有一位乘客（天然连通）
- 对不存在的连接执行 block 操作（无操作）
- 同一对乘客之间有多条连接

---

## 4. Elevator Binary Search OA

**Pattern**: **Array Simulation（数组模拟）** / Binary Search

### Problem Statement

给定一个数组，每个元素表示移动距离，从索引 `i` 出发，移动到 `i + arr[i]`（或根据规则移动到 `i - arr[i]`）。
求最小的起始索引，使得遍历过程中永远不会越过左边界（索引 < 0）。

### Approach

从每个起始索引模拟路径。若该属性具有单调性（起始索引越大，左侧空间越多），可用记忆化或二分查找提升效率。

```python
from typing import List


def min_starting_index(moves: List[int]) -> int:
    """Find minimum starting index that never goes below 0.

    The array alternates: even indices move right (+moves[i]),
    odd indices move left (-moves[i]).
    """
    n = len(moves)

    def simulate(start: int) -> bool:
        """Return True if starting at ''start'' never goes below 0."""
        pos = start
        visited: set[int] = set()
        while 0 <= pos < n:
            if pos in visited:
                return True  # cycle detected, never exits left
            visited.add(pos)
            pos += moves[pos]  # moves[i] can be negative (left jump)
        return pos >= 0  # exited right or stayed in bounds

    # If monotonic: binary search
    lo, hi = 0, n - 1
    result = n  # no valid start found

    # Linear scan fallback (safe for all cases)
    for i in range(n):
        if simulate(i):
            return i

    return result
```

**时间复杂度**：线性扫描 + 模拟，最坏情况 O(n^2)。
若具有单调性，使用二分查找：O(n log n)。
**空间复杂度**：O(n)，用于 visited 集合。

### Variant: Bidirectional Jumps with Array Values

```python
def min_start_bidirectional(arr: List[int]) -> int:
    """Each position has jump distance. Even-index: right, odd-index: left."""
    n = len(arr)
    for start in range(n):
        pos = start
        steps = 0
        valid = True
        while 0 <= pos < n and steps < 2 * n:
            pos = pos + arr[pos] if pos % 2 == 0 else pos - arr[pos]
            steps += 1
            if pos < 0:
                valid = False
                break
        if valid:
            return start
    return -1
```

### Edge Cases
- 数组长度为 1
- 所有元素为 0（在起点形成无限循环）
- 负数跳跃导致立即越过左边界

---

## 5. Server Throughput with Heap

**Pattern**: **Heap（堆）** / **Greedy Scheduling（贪心调度）**

### Problem Statement

给定 `n` 台服务器及其处理时间，以及传入的请求，最大化吞吐量。
对比递归解法与基于堆的解法。

### Approach: Min-Heap for Earliest Available Server

```python
import heapq
from typing import List, Tuple


def max_throughput_heap(
    servers: List[int], requests: List[Tuple[int, int]]
) -> int:
    """Assign requests to servers to maximize throughput.

    Args:
        servers: Processing time for each server.
        requests: (arrival_time, processing_time) sorted by arrival.

    Returns:
        Number of requests successfully processed.
    """
    # Min-heap: (available_time, server_id)
    heap: List[Tuple[int, int]] = [(0, i) for i in range(len(servers))]
    heapq.heapify(heap)

    processed = 0
    for arrival, duration in requests:
        # Get the server that becomes free earliest
        avail_time, sid = heapq.heappop(heap)
        if avail_time <= arrival:
            # Server is free, assign this request
            new_avail = arrival + duration
            heapq.heappush(heap, (new_avail, sid))
            processed += 1
        else:
            # No server available, put it back and skip request
            heapq.heappush(heap, (avail_time, sid))

    return processed
```

**时间复杂度**：O(R log S)，R 为请求数，S 为服务器数。
**空间复杂度**：O(S)，用于堆。

### Recursive Approach (for comparison)

```python
def max_throughput_recursive(
    servers: List[int],
    requests: List[Tuple[int, int]],
    idx: int = 0,
    avail: List[int] | None = None,
) -> int:
    """Brute force: try assigning each request to each server."""
    if avail is None:
        avail = [0] * len(servers)
    if idx == len(requests):
        return 0

    arrival, duration = requests[idx]
    # Option 1: skip this request
    best = max_throughput_recursive(servers, requests, idx + 1, avail)

    # Option 2: assign to an available server
    for s in range(len(servers)):
        if avail[s] <= arrival:
            old = avail[s]
            avail[s] = arrival + duration
            result = 1 + max_throughput_recursive(
                servers, requests, idx + 1, avail
            )
            best = max(best, result)
            avail[s] = old  # backtrack

    return best
```

**时间复杂度**：O(S^R) 指数级——仅适用于小规模输入。

### Edge Cases
- 所有请求同时到达
- 只有一台服务器
- 处理时间超过请求间隔

---

## 6. Cart & Pricing Engine (OOD)

**Pattern**: **Object-Oriented Design（面向对象设计）** / **Strategy Pattern（策略模式）**

### Problem Statement

为 Uber Eats 购物车系统设计类。需求：
- 商品定制（附加项及额外费用）
- 高峰期价格倍增（Surge Pricing）
- 会员折扣（Uber One）
- 优惠码（固定金额或百分比）
- 小票明细输出

### Design

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass
class AddOn:
    """An item customization (e.g., extra cheese)."""
    name: str
    price: float


@dataclass
class MenuItem:
    """A menu item with optional add-ons."""
    name: str
    base_price: float
    add_ons: List[AddOn] = field(default_factory=list)

    @property
    def total_price(self) -> float:
        return self.base_price + sum(a.price for a in self.add_ons)


@dataclass
class CartItem:
    """An item in the cart with quantity."""
    menu_item: MenuItem
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.menu_item.total_price * self.quantity


# --- Pricing Rules (Strategy Pattern) ---

class PricingRule(ABC):
    """Base class for pricing rules applied to cart total."""

    @abstractmethod
    def apply(self, amount: float) -> float:
        """Return the adjusted amount after applying this rule."""

    @abstractmethod
    def description(self) -> str:
        """Human-readable description for receipt."""


class SurgePricingRule(PricingRule):
    """Multiplier during peak demand."""

    def __init__(self, multiplier: float):
        self.multiplier = multiplier

    def apply(self, amount: float) -> float:
        return amount * self.multiplier

    def description(self) -> str:
        return f"Surge pricing ({self.multiplier}x)"


class MembershipDiscountRule(PricingRule):
    """Flat percentage discount for Uber One members."""

    def __init__(self, discount_pct: float):
        self.discount_pct = discount_pct

    def apply(self, amount: float) -> float:
        return amount * (1 - self.discount_pct / 100)

    def description(self) -> str:
        return f"Uber One discount (-{self.discount_pct}%)"


class PromoCodeType(Enum):
    FLAT = "flat"
    PERCENTAGE = "percentage"


class PromoCodeRule(PricingRule):
    """Promo code: flat amount off or percentage off."""

    def __init__(self, code: str, promo_type: PromoCodeType, value: float):
        self.code = code
        self.promo_type = promo_type
        self.value = value

    def apply(self, amount: float) -> float:
        if self.promo_type == PromoCodeType.FLAT:
            return max(0.0, amount - self.value)
        return amount * (1 - self.value / 100)

    def description(self) -> str:
        if self.promo_type == PromoCodeType.FLAT:
            return f"Promo ''{self.code}'' (-${self.value:.2f})"
        return f"Promo ''{self.code}'' (-{self.value}%)"


# --- Cart ---

class Cart:
    """Shopping cart with pricing engine."""

    def __init__(self) -> None:
        self.items: List[CartItem] = []
        self.pricing_rules: List[PricingRule] = []

    def add_item(self, menu_item: MenuItem, quantity: int = 1) -> None:
        """Add item to cart."""
        self.items.append(CartItem(menu_item, quantity))

    def add_pricing_rule(self, rule: PricingRule) -> None:
        """Add a pricing rule (surge, discount, promo)."""
        self.pricing_rules.append(rule)

    @property
    def subtotal(self) -> float:
        """Raw total before pricing rules."""
        return sum(item.subtotal for item in self.items)

    @property
    def total(self) -> float:
        """Final total after all pricing rules applied in order."""
        amount = self.subtotal
        for rule in self.pricing_rules:
            amount = rule.apply(amount)
        return round(amount, 2)

    def receipt(self) -> str:
        """Generate itemized receipt with pricing breakdown."""
        lines: List[str] = ["=== Receipt ==="]

        for item in self.items:
            base = item.menu_item.base_price
            lines.append(
                f"  {item.menu_item.name} x{item.quantity}"
                f"  ${base:.2f} ea"
            )
            for addon in item.menu_item.add_ons:
                lines.append(f"    + {addon.name}: ${addon.price:.2f}")
            lines.append(f"    Item total: ${item.subtotal:.2f}")

        lines.append(f"\nSubtotal: ${self.subtotal:.2f}")

        amount = self.subtotal
        for rule in self.pricing_rules:
            new_amount = rule.apply(amount)
            diff = new_amount - amount
            sign = "+" if diff >= 0 else ""
            lines.append(f"  {rule.description()}: {sign}${diff:.2f}")
            amount = new_amount

        lines.append(f"\nTotal: ${round(amount, 2):.2f}")
        lines.append("===============")
        return "\n".join(lines)
```

### Usage Example

```python
burger = MenuItem("Burger", 12.99, [AddOn("Extra Cheese", 1.50)])
fries = MenuItem("Fries", 4.99)

cart = Cart()
cart.add_item(burger, 2)
cart.add_item(fries, 1)

cart.add_pricing_rule(SurgePricingRule(1.3))
cart.add_pricing_rule(MembershipDiscountRule(10))
cart.add_pricing_rule(
    PromoCodeRule("SAVE5", PromoCodeType.FLAT, 5.0)
)

print(cart.receipt())
```

**关键设计决策**：
- 策略模式用于定价规则：方便扩展新规则类型
- 规则按顺序应用（高峰倍增 -> 折扣 -> 优惠码）
- `MenuItem.total_price` 包含附加项费用
- 小票展示完整明细

### Follow-up: Rule Ordering and Conflicts

生产环境中，为规则定义 `priority` 字段，应用前按优先级排序。
对于互斥规则（如只能使用一个优惠码），在 `add_pricing_rule` 时进行校验。

---

## 7. Circular Array Shortest Jump

**Pattern**: BFS on Circular Array（循环数组 BFS）

### Problem Statement

给定一个循环整数数组，`arr[i]` 表示索引 `i` 处的跳跃距离，
求从索引 A 到索引 B 的最少跳跃次数。
跳跃支持循环绕回：从索引 `i` 出发，可以跳到 `(i + arr[i]) % n` 或 `(i - arr[i]) % n`。

### Approach

从源节点 A 开始 BFS。每个状态为循环数组中的一个位置。
由于求最短路径，BFS 保证最优性。

```python
from collections import deque
from typing import List


def shortest_jump(arr: List[int], start: int, end: int) -> int:
    """Find minimum jumps from start to end in circular array.

    At each position i, can jump to (i + arr[i]) % n or (i - arr[i]) % n.
    Returns -1 if unreachable.
    """
    n = len(arr)
    if start == end:
        return 0

    visited = [False] * n
    visited[start] = True
    queue: deque[tuple[int, int]] = deque([(start, 0)])

    while queue:
        pos, dist = queue.popleft()
        for nxt in [(pos + arr[pos]) % n, (pos - arr[pos]) % n]:
            if nxt == end:
                return dist + 1
            if not visited[nxt]:
                visited[nxt] = True
                queue.append((nxt, dist + 1))

    return -1
```

**时间复杂度**：O(n)——每个节点最多访问一次。
**空间复杂度**：O(n)，用于 visited 数组和队列。

### Edge Cases
- `start == end` -> 0 次跳跃
- `arr[i] == 0` -> 卡在位置 i（无出边）
- 所有元素相同 -> 规律性跳跃模式

---

## 8. Robot Distance in Grid

**Pattern**: **DP（动态规划）** Precomputation / 4-Direction Obstacle Distance

### Problem Statement

给定一个网格，其中：
- `O` = 机器人
- `E` = 空格
- `X` = 障碍物

以及一个距离数组 `[left, top, bottom, right]`，表示目标机器人到各方向最近障碍物的距离，
找出与之匹配的机器人。

### Approach

用 DP 预计算每个格子在四个方向上到最近障碍物的距离，
然后遍历所有机器人格子，检查其四方向距离是否与查询匹配。

```python
from typing import List, Optional, Tuple

INF = float("inf")


def find_robot(
    grid: List[List[str]], target_dist: Tuple[int, int, int, int]
) -> Optional[Tuple[int, int]]:
    """Find the robot whose distances to nearest obstacle in 4 directions match.

    Args:
        grid: 2D grid with ''O'' (robot), ''E'' (empty), ''X'' (obstacle).
        target_dist: (left, top, bottom, right) distances.

    Returns:
        (row, col) of matching robot, or None.
    """
    if not grid or not grid[0]:
        return None

    rows, cols = len(grid), len(grid[0])

    # Precompute distances to nearest obstacle in 4 directions
    left_dist = [[0] * cols for _ in range(rows)]
    right_dist = [[0] * cols for _ in range(rows)]
    top_dist = [[0] * cols for _ in range(rows)]
    bottom_dist = [[0] * cols for _ in range(rows)]

    # Left: scan each row left-to-right
    for r in range(rows):
        dist = 0
        for c in range(cols):
            if grid[r][c] == "X":
                dist = 0
            else:
                left_dist[r][c] = dist
                dist += 1

    # Right: scan each row right-to-left
    for r in range(rows):
        dist = 0
        for c in range(cols - 1, -1, -1):
            if grid[r][c] == "X":
                dist = 0
            else:
                right_dist[r][c] = dist
                dist += 1

    # Top: scan each column top-to-bottom
    for c in range(cols):
        dist = 0
        for r in range(rows):
            if grid[r][c] == "X":
                dist = 0
            else:
                top_dist[r][c] = dist
                dist += 1

    # Bottom: scan each column bottom-to-top
    for c in range(cols):
        dist = 0
        for r in range(rows - 1, -1, -1):
            if grid[r][c] == "X":
                dist = 0
            else:
                bottom_dist[r][c] = dist
                dist += 1

    # Find robot matching target distances
    t_left, t_top, t_bottom, t_right = target_dist
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "O":
                if (
                    left_dist[r][c] == t_left
                    and top_dist[r][c] == t_top
                    and bottom_dist[r][c] == t_bottom
                    and right_dist[r][c] == t_right
                ):
                    return (r, c)

    return None
```

**时间复杂度**：预计算 O(rows * cols) + 查找 O(rows * cols)。
**空间复杂度**：O(rows * cols)，用于四个方向的距离矩阵。

### Edge Cases
- 机器人在网格边界（到障碍物的距离等于到边界的距离）
- 多个机器人具有相同的距离分布（返回第一个匹配或全部）
- 没有匹配的机器人

### Note on Distance Definition

问题可能将"距离"定义为到最近障碍物的格数，或到边界的格数（将边界视为障碍物）。
请与面试官确认。上述方案将起始列/行的边缘距离视为 0（隐式边界墙）。

---

## 9. Min Operations n to 0

**Pattern**: **Greedy（贪心）** / **NAF (Non-Adjacent Form，非相邻表示法)**

### Problem Statement

给定整数 `n`，使用操作 `n += 2^i` 或 `n -= 2^i`（i 为任意非负整数）将其减至 0。
求最少操作次数。

### Approach

等价于求 `n` 的 **NAF (Non-Adjacent Form，非相邻表示法)**。
核心思路：最少操作次数等于 NAF 中非零数字的个数。基于 `n % 4` 的贪心规则：

- 若 `n % 2 == 0`：除以 2（右移），无需操作
- 若 `n % 4 == 1`：减 1（一次操作）
- 若 `n % 4 == 3`：加 1（一次操作，产生更长的进位，但总操作次数更少）

```python
def min_operations(n: int) -> int:
    """Minimum +/- 2^i operations to reduce n to 0."""
    if n < 0:
        n = -n  # symmetric
    ops = 0
    while n > 0:
        if n % 2 == 0:
            n //= 2
        elif n % 4 == 1:
            n -= 1
            ops += 1
            n //= 2
        else:  # n % 4 == 3
            n += 1
            ops += 1
            n //= 2
    return ops
```

**时间复杂度**：O(log n)——每次迭代至少将 n 减半。
**空间复杂度**：O(1)。

### Proof of Optimality

NAF 在所有有符号二进制表示中，非零数字位数最少。
贪心规则 `n%4==3 -> +1` 可避免相邻的 1 位，这正是 NAF 的构造方式。

### Alternative: Bit Counting

```python
def min_operations_bit(n: int) -> int:
    """Count non-zero digits in NAF representation."""
    ops = 0
    while n:
        if n & 1:
            # Check if we have consecutive 1-bits
            if n & 2:
                n += 1  # NAF: replace trailing 11 with 100 then subtract
            else:
                n -= 1
            ops += 1
        n >>= 1
    return ops
```

### Edge Cases
- n = 0 -> 0 次操作
- n = 1 -> 1 次操作（减去 2^0）
- n 是 2 的幂次 -> 1 次操作
- 大数 n（在 O(log n) 内完成）

---

## 10. Shortest Subarray with k Distinct

**Pattern**: **Sliding Window（滑动窗口）** + Counter（计数器）

### Problem Statement

给定数组 `nums` 和整数 `k`，求包含至少 `k` 个不同元素的最短子数组长度。
若不可能，返回 -1。

### Approach

经典滑动窗口 + 频率计数器。向右扩展直到有 `k` 个不同元素，然后向左收缩以最小化长度。

```python
from collections import defaultdict
from typing import List


def shortest_subarray_k_distinct(nums: List[int], k: int) -> int:
    """Find shortest subarray with at least k distinct elements."""
    n = len(nums)
    if k > n:
        return -1

    counter: dict[int, int] = defaultdict(int)
    distinct = 0
    min_len = n + 1
    left = 0

    for right in range(n):
        if counter[nums[right]] == 0:
            distinct += 1
        counter[nums[right]] += 1

        # Shrink from left while we still have k distinct
        while distinct >= k:
            min_len = min(min_len, right - left + 1)
            counter[nums[left]] -= 1
            if counter[nums[left]] == 0:
                distinct -= 1
            left += 1

    return min_len if min_len <= n else -1
```

**时间复杂度**：O(n)——每个元素进出窗口各一次。
**空间复杂度**：O(k)，用于计数器。

### Edge Cases
- 所有元素相同且 k > 1 -> 返回 -1
- k = 1 -> 返回 1
- 整个数组恰好有 k 个不同元素 -> 返回 n（若无更短子数组）

---

## 11. Price Discount (Monotonic Stack)

**Pattern**: **Monotonic Stack（单调栈）** / Next Smaller Element（下一个更小元素）

### Problem Statement

对于索引 `i` 处价格为 `prices[i]` 的商品，找到第一个 `j > i` 使得 `prices[j] <= prices[i]`。
索引 `i` 处的折扣价为 `prices[i] - prices[j]`。
输出：总折扣后的价格之和，以及以原价出售的商品索引（即找不到 j 的索引）。

### Approach

使用单调栈查找每个索引的"下一个更小或等于"的元素。

```python
from typing import List, Tuple


def price_discount(prices: List[int]) -> Tuple[int, List[int]]:
    """Compute total discounted sum and indices sold at original price.

    For each i, discount = prices[j] where j is first j>i with prices[j] <= prices[i].
    If no such j, item sold at original price.

    Returns:
        (total_sum, original_price_indices)
    """
    n = len(prices)
    discount = [0] * n  # discount applied at each index
    stack: List[int] = []  # monotonic stack of indices

    for i in range(n):
        # Pop all elements where current price <= stack top price
        while stack and prices[i] <= prices[stack[-1]]:
            idx = stack.pop()
            discount[idx] = prices[i]
        stack.append(i)

    # Remaining in stack: no discount (sold at original price)
    original_indices = list(stack)

    total = sum(prices[i] - discount[i] for i in range(n))
    return total, sorted(original_indices)
```

**时间复杂度**：O(n)——每个元素最多入栈和出栈各一次。
**空间复杂度**：O(n)，用于栈和折扣数组。

### Example

```
prices = [8, 4, 6, 2, 3]
Discounts: 8-4=4, 4-2=2, 6-2=4, 2 (original), 3 (original)
Total = 4 + 2 + 4 + 2 + 3 = 15
Original price indices: [3, 4]
```

### Edge Cases
- 所有价格递增 -> 每件商品都被下一件折扣
- 所有价格递减 -> 只有最后一件以原价出售
- 所有价格相同 -> 每件被下一件折扣，最后一件以原价出售

---

## 12. Balanced Permutation

**Pattern**: Tracking Min/Max Positions（追踪最小/最大位置）

### Problem Statement

给定 `1..n` 的一个排列，对每个 `k`（从 1 到 n），检查是否存在一个连续子数组构成 `1..k` 的排列。

### Approach

记录每个值的位置。要使连续子数组构成 `1..k` 的排列，所有值 `1..k` 必须占据连续的索引范围。
随着 k 增大，维护 `min_pos` 和 `max_pos`。若 `max_pos - min_pos + 1 == k`，则满足条件。

```python
from typing import List


def balanced_permutation(perm: List[int]) -> List[bool]:
    """For each k=1..n, check if a contiguous subarray forms perm of 1..k.

    Args:
        perm: A permutation of 1..n (1-indexed values).

    Returns:
        List of booleans, result[k-1] = True if subarray perm of 1..k exists.
    """
    n = len(perm)
    pos = [0] * (n + 1)  # pos[v] = index of value v in perm
    for i, v in enumerate(perm):
        pos[v] = i

    result: List[bool] = []
    min_pos = pos[1]
    max_pos = pos[1]

    for k in range(1, n + 1):
        min_pos = min(min_pos, pos[k])
        max_pos = max(max_pos, pos[k])
        # If the range [min_pos, max_pos] has exactly k elements,
        # and we know values 1..k are all within it, it must be a perm of 1..k
        result.append(max_pos - min_pos + 1 == k)

    return result
```

**时间复杂度**：O(n)。
**空间复杂度**：O(n)，用于位置数组。

### Proof

对于值 `1..k` 所占位置的范围 `max_pos - min_pos + 1`：
- 若范围 == k，则 k 个槽位恰好存放 k 个值，无间隙 -> 连续排列。
- 若范围 > k，则区间内存在不属于 `1..k` 的值 -> 非连续排列。

### Edge Cases
- n = 1 -> 始终为 [True]
- 有序排列 [1,2,3,...,n] -> 全为 True
- 逆序排列 -> 仅 k=1 和 k=n 为 True

---

## 13. Elevator/Stairs Energy

**Pattern**: **Binary Search（二分查找）** on Split Point

### Problem Statement

一个人先乘电梯爬 `mid` 层，再走楼梯爬剩余楼层。
- 电梯：每层增加 `e1` 能量，花费 `t1` 时间。
- 楼梯：每层消耗 `e2` 能量，每层时间 = `ceil(c / 当前能量)`。

求使总时间最小（或使两种策略的时间差最小）的分割点。

### Approach

对分割点 `mid` 进行二分/线性搜索。对每个候选点计算：
1. 电梯阶段（楼层 0..mid）的时间
2. 楼梯阶段（楼层 mid..总层数，与能量相关）的时间

```python
import math
from typing import Tuple


def optimal_split(
    total_floors: int,
    e1: float,
    t1: float,
    e2: float,
    c: float,
    initial_energy: float,
) -> Tuple[int, float]:
    """Find optimal floor to switch from elevator to stairs.

    Args:
        total_floors: Total floors to climb.
        e1: Energy gained per elevator floor.
        t1: Time per elevator floor.
        e2: Energy consumed per stair floor.
        c: Constant for stair time calculation.
        initial_energy: Starting energy.

    Returns:
        (split_floor, total_time)
    """

    def compute_time(split: int) -> float:
        """Total time if taking elevator for first ''split'' floors."""
        # Elevator phase
        elev_time = split * t1
        energy = initial_energy + split * e1

        # Stairs phase
        stairs_floors = total_floors - split
        stair_time = 0.0
        for _ in range(stairs_floors):
            if energy <= 0:
                return float("inf")  # Can''t climb
            stair_time += math.ceil(c / energy)
            energy -= e2

        return elev_time + stair_time

    best_split = 0
    best_time = float("inf")

    # Binary search works if time function is unimodal (valley-shaped)
    # Otherwise, linear scan:
    for split in range(total_floors + 1):
        t = compute_time(split)
        if t < best_time:
            best_time = t
            best_split = split

    return best_split, best_time
```

**时间复杂度**：线性扫描 O(n^2)（每次评估 O(n)，共 n 个候选）。
若时间函数为单峰（谷形），使用三分搜索：O(n log n)。
**空间复杂度**：O(1)。

### Binary Search Optimization (if unimodal)

```python
def optimal_split_binary(
    total_floors: int,
    e1: float, t1: float, e2: float, c: float,
    initial_energy: float,
) -> Tuple[int, float]:
    """Ternary search for minimum on unimodal function."""

    def compute_time(split: int) -> float:
        elev_time = split * t1
        energy = initial_energy + split * e1
        stair_time = 0.0
        for _ in range(total_floors - split):
            if energy <= 0:
                return float("inf")
            stair_time += math.ceil(c / energy)
            energy -= e2
        return elev_time + stair_time

    lo, hi = 0, total_floors
    while hi - lo > 2:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if compute_time(m1) < compute_time(m2):
            hi = m2
        else:
            lo = m1

    best_split = lo
    best_time = compute_time(lo)
    for s in range(lo + 1, hi + 1):
        t = compute_time(s)
        if t < best_time:
            best_time = t
            best_split = s
    return best_split, best_time
```

### Edge Cases
- 0 层 -> 时间为 0
- 楼梯阶段能量耗尽 -> 需要更多电梯楼层
- 全程乘电梯或全程走楼梯可能是最优解

---

## 14. N-ary Tree 3-Part

**Pattern**: Tree DFS（树形深度优先搜索）/ Path Finding（路径查找）

### Problem Statement

给定一棵 N 叉树，实现三个操作：
1. 求所有节点值之和
2. 找出最大路径值（根到叶）
3. 返回最大路径上的节点

### Solution

```python
from typing import List, Optional, Tuple


class NaryNode:
    """N-ary tree node."""

    def __init__(self, val: int, children: Optional[List["NaryNode"]] = None):
        self.val: int = val
        self.children: List["NaryNode"] = children or []


def sum_all(root: Optional[NaryNode]) -> int:
    """Part (a): Sum all node values in the tree."""
    if root is None:
        return 0
    return root.val + sum(sum_all(child) for child in root.children)


def max_path_value(root: Optional[NaryNode]) -> int:
    """Part (b): Find maximum root-to-leaf path sum."""
    if root is None:
        return 0
    if not root.children:
        return root.val
    return root.val + max(max_path_value(c) for c in root.children)


def max_path_nodes(root: Optional[NaryNode]) -> List[int]:
    """Part (c): Return node values on the maximum root-to-leaf path."""
    if root is None:
        return []
    if not root.children:
        return [root.val]

    best_path: List[int] = []
    best_sum = float("-inf")

    for child in root.children:
        child_path = max_path_nodes(child)
        child_sum = sum(child_path)
        if child_sum > best_sum:
            best_sum = child_sum
            best_path = child_path

    return [root.val] + best_path
```

**时间复杂度**：每个操作 O(n)——遍历每个节点一次。
**空间复杂度**：O(h)，h 为树的高度（递归深度）。

### Optimization: Single Pass for All Three

```python
def tree_analysis(
    root: Optional[NaryNode],
) -> Tuple[int, int, List[int]]:
    """Compute all three parts in a single DFS.

    Returns: (total_sum, max_path_value, max_path_nodes)
    """
    if root is None:
        return 0, 0, []

    if not root.children:
        return root.val, root.val, [root.val]

    total = root.val
    best_child_sum = float("-inf")
    best_child_path: List[int] = []

    for child in root.children:
        child_total, child_max, child_path = tree_analysis(child)
        total += child_total
        if child_max > best_child_sum:
            best_child_sum = child_max
            best_child_path = child_path

    return (
        total,
        root.val + best_child_sum,
        [root.val] + best_child_path,
    )
```

### Edge Cases
- 空树（root 为 None）
- 单节点（叶节点即根节点）
- 所有值为负数
- 多条路径具有相同最大和（返回任意一条）

---

## 15. Max Throughput with Budget

**Pattern**: **Binary Search on Answer（二分答案）**

### Problem Statement

给定 `n` 个服务，每个服务有 `current_throughput[i]` 和 `scale_cost[i]`（每单位吞吐量的扩容成本），
以及预算 `B`。在所有服务都达到同一水平的前提下，求可实现的最大吞吐量（瓶颈为最小值）。

### Approach

对目标吞吐量 `T` 进行二分查找。对每个候选 T，计算将所有服务提升至 T 的总成本。
若成本 <= 预算，则 T 可行。

```python
from typing import List


def max_throughput(
    current: List[int], cost: List[int], budget: int
) -> int:
    """Find max throughput achievable within budget.

    Each service i needs (T - current[i]) * cost[i] to reach throughput T.
    Only services below T need scaling.
    """
    n = len(current)

    def feasible(target: int) -> bool:
        total_cost = 0
        for i in range(n):
            if current[i] < target:
                total_cost += (target - current[i]) * cost[i]
                if total_cost > budget:
                    return False
        return True

    lo = min(current)
    hi = max(current) + budget  # upper bound: all budget on cheapest service

    while lo < hi:
        mid = (lo + hi + 1) // 2
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1

    return lo
```

**时间复杂度**：O(n * log(最大吞吐量范围))。
**空间复杂度**：O(1)。

### Edge Cases
- 预算为 0 -> 答案为 min(current)
- 所有服务吞吐量相同 -> 均匀分配预算
- 某个服务扩容成本极高（主导预算分配）
- 大预算 -> 上界计算很重要

### Follow-up: Fractional Throughput

若吞吐量可为非整数，使用浮点数二分查找并设置 epsilon 容差：

```python
def max_throughput_float(
    current: List[float], cost: List[float], budget: float
) -> float:
    """Float version with 1e-6 precision."""
    lo = min(current)
    hi = max(current) + budget

    for _ in range(100):  # enough iterations for double precision
        mid = (lo + hi) / 2
        total = sum(max(0, mid - c) * k for c, k in zip(current, cost))
        if total <= budget:
            lo = mid
        else:
            hi = mid

    return lo
```

---

## 16. Parking Lot (OOD)

**Pattern**: **Object-Oriented Design（面向对象设计）**

### Problem Statement

设计一个停车场系统：
- `park(vehicle)` - 停放一辆车，返回车位 ID 或 -1
- `unpark(spot_id)` - 从车位移走车辆
- `check_car(license_plate)` - 检查某辆车是否已停放，返回车位 ID 或 -1

约束条件：摩托车位只能停摩托车，普通车位可停摩托车和轿车。

### Solution

```python
from enum import Enum
from typing import Dict, Optional


class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"


class Vehicle:
    """A vehicle with type and license plate."""

    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        self.license_plate: str = license_plate
        self.vehicle_type: VehicleType = vehicle_type


class SpotType(Enum):
    MOTORCYCLE = "motorcycle"
    REGULAR = "regular"


class ParkingSpot:
    """A parking spot that may hold a vehicle."""

    def __init__(self, spot_id: int, spot_type: SpotType):
        self.spot_id: int = spot_id
        self.spot_type: SpotType = spot_type
        self.vehicle: Optional[Vehicle] = None

    @property
    def is_available(self) -> bool:
        return self.vehicle is None

    def can_fit(self, vehicle: Vehicle) -> bool:
        """Check if this spot can accommodate the vehicle."""
        if self.spot_type == SpotType.MOTORCYCLE:
            return vehicle.vehicle_type == VehicleType.MOTORCYCLE
        # Regular spots fit both cars and motorcycles
        return True


class ParkingLot:
    """Parking lot with motorcycle and regular spots."""

    def __init__(
        self, num_motorcycle_spots: int, num_regular_spots: int
    ) -> None:
        self.spots: Dict[int, ParkingSpot] = {}
        self.plate_to_spot: Dict[str, int] = {}

        spot_id = 0
        for _ in range(num_motorcycle_spots):
            self.spots[spot_id] = ParkingSpot(spot_id, SpotType.MOTORCYCLE)
            spot_id += 1
        for _ in range(num_regular_spots):
            self.spots[spot_id] = ParkingSpot(spot_id, SpotType.REGULAR)
            spot_id += 1

    def park(self, vehicle: Vehicle) -> int:
        """Park vehicle, return spot ID or -1 if no spot available.

        Strategy: try motorcycle spots first for motorcycles (preserve
        regular spots for cars), then regular spots.
        """
        if vehicle.license_plate in self.plate_to_spot:
            return self.plate_to_spot[vehicle.license_plate]

        # For motorcycles: prefer motorcycle spots first
        preferred_order = (
            [SpotType.MOTORCYCLE, SpotType.REGULAR]
            if vehicle.vehicle_type == VehicleType.MOTORCYCLE
            else [SpotType.REGULAR]
        )

        for pref_type in preferred_order:
            for spot in self.spots.values():
                if (
                    spot.is_available
                    and spot.spot_type == pref_type
                    and spot.can_fit(vehicle)
                ):
                    spot.vehicle = vehicle
                    self.plate_to_spot[vehicle.license_plate] = spot.spot_id
                    return spot.spot_id

        return -1

    def unpark(self, spot_id: int) -> bool:
        """Remove vehicle from spot. Returns True if successful."""
        if spot_id not in self.spots:
            return False
        spot = self.spots[spot_id]
        if spot.vehicle is None:
            return False

        del self.plate_to_spot[spot.vehicle.license_plate]
        spot.vehicle = None
        return True

    def check_car(self, license_plate: str) -> int:
        """Check if car is parked. Return spot ID or -1."""
        return self.plate_to_spot.get(license_plate, -1)
```

**时间复杂度**：
- `park`：O(S)，S 为总车位数（线性扫描可用车位）。
- `unpark`：O(1) 直接访问车位。
- `check_car`：O(1) 哈希查找。

**空间复杂度**：O(S + V)，V 为已停放的车辆数。

### Follow-up: Optimize park() to O(1)

为每种车位类型维护独立的空闲车位队列（deque 或 set）：

```python
from collections import deque


class ParkingLotOptimized:
    """O(1) park/unpark using free-spot queues."""

    def __init__(self, n_moto: int, n_regular: int) -> None:
        self.spots: Dict[int, ParkingSpot] = {}
        self.plate_to_spot: Dict[str, int] = {}
        self.free_motorcycle: deque[int] = deque()
        self.free_regular: deque[int] = deque()

        sid = 0
        for _ in range(n_moto):
            self.spots[sid] = ParkingSpot(sid, SpotType.MOTORCYCLE)
            self.free_motorcycle.append(sid)
            sid += 1
        for _ in range(n_regular):
            self.spots[sid] = ParkingSpot(sid, SpotType.REGULAR)
            self.free_regular.append(sid)
            sid += 1

    def park(self, vehicle: Vehicle) -> int:
        if vehicle.license_plate in self.plate_to_spot:
            return self.plate_to_spot[vehicle.license_plate]

        spot_id = -1
        if vehicle.vehicle_type == VehicleType.MOTORCYCLE:
            if self.free_motorcycle:
                spot_id = self.free_motorcycle.popleft()
            elif self.free_regular:
                spot_id = self.free_regular.popleft()
        else:  # CAR
            if self.free_regular:
                spot_id = self.free_regular.popleft()

        if spot_id == -1:
            return -1

        self.spots[spot_id].vehicle = vehicle
        self.plate_to_spot[vehicle.license_plate] = spot_id
        return spot_id

    def unpark(self, spot_id: int) -> bool:
        if spot_id not in self.spots or self.spots[spot_id].vehicle is None:
            return False
        spot = self.spots[spot_id]
        del self.plate_to_spot[spot.vehicle.license_plate]
        spot.vehicle = None
        if spot.spot_type == SpotType.MOTORCYCLE:
            self.free_motorcycle.append(spot_id)
        else:
            self.free_regular.append(spot_id)
        return True
```

### Edge Cases
- 停放已在停车场的车（幂等操作）
- 对空车位执行 unpark
- 所有车位已满

---

## 17. Task Assignment to 2 People

**Pattern**: **Greedy（贪心）** / Sort by Difference（按差值排序）

### Problem Statement

给定 `n` 个任务，`reward1[i]`（人员 1 完成任务 i 的奖励）和 `reward2[i]`（人员 2 完成任务 i 的奖励）。
人员 1 必须完成恰好 `k` 个任务，人员 2 完成其余任务。求最大总奖励。

### Approach

对每个任务，计算分配给人员 1 的"优势"：`diff[i] = reward1[i] - reward2[i]`。
按 diff 降序排序，将前 k 个任务分配给人员 1，其余分配给人员 2。

```python
from typing import List, Tuple


def max_reward(
    reward1: List[int], reward2: List[int], k: int
) -> Tuple[int, List[int]]:
    """Assign k tasks to person 1, rest to person 2, maximizing total reward.

    Returns: (max_total, list of task indices assigned to person 1)
    """
    n = len(reward1)
    # (advantage of person 1, task index)
    diffs = [(reward1[i] - reward2[i], i) for i in range(n)]
    diffs.sort(reverse=True)

    person1_tasks = [idx for _, idx in diffs[:k]]
    total = 0
    person1_set = set(person1_tasks)
    for i in range(n):
        if i in person1_set:
            total += reward1[i]
        else:
            total += reward2[i]

    return total, sorted(person1_tasks)
```

**时间复杂度**：O(n log n)，用于排序。
**空间复杂度**：O(n)。

### Proof of Correctness

初始时将所有任务分配给人员 2，总奖励 = sum(reward2)。
将任务 i 从人员 2 切换到人员 1，总奖励变化量为 `reward1[i] - reward2[i]`。
为最大化，选取 diff 最大的 k 个任务。

### Edge Cases
- k = 0 -> 所有任务分配给人员 2
- k = n -> 所有任务分配给人员 1
- 所有 diff 相等 -> 任意 k 个任务均可
- 所有 diff 为负 -> 仍需分配 k 个任务给人员 1

---

## 18. Jump Game Prime-Ending Variant

**Pattern**: **DP（动态规划）** / **Sieve of Eratosthenes（埃拉托斯特尼筛法）**

### Problem Statement

类似 [LC 1696](lc://1696)（Jump Game VI），但从位置 `i` 可以跳到 `i+1` 或 `i+p`，
其中 `p` 是末位数字为 3 的质数（3, 13, 23, 43, 53, 73, 83, ...）。
求到达最后一个索引的最小代价。

### Approach

1. 使用**埃拉托斯特尼筛法**预计算所有 <= n 的末位为 3 的质数。
2. 从左到右做 DP：`dp[i]` = 到达索引 `i` 的最小代价。
3. 对每个 `i`：`dp[i] = min(dp[i-1], dp[i-p] for all valid primes p) + cost[i]`。

```python
from typing import List


def sieve_primes_ending_3(limit: int) -> List[int]:
    """Return all primes <= limit that end in digit 3."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [p for p in range(2, limit + 1) if is_prime[p] and p % 10 == 3]


def min_cost_jump(cost: List[int]) -> int:
    """Minimum cost to reach last index.

    From index i, can jump to i+1 or i+p (p = prime ending in 3).
    """
    n = len(cost)
    if n <= 1:
        return cost[0] if cost else 0

    primes = sieve_primes_ending_3(n)

    INF = float("inf")
    dp = [INF] * n
    dp[0] = cost[0]

    for i in range(1, n):
        # Jump +1 from i-1
        dp[i] = dp[i - 1] + cost[i]

        # Jump +p from i-p
        for p in primes:
            if p > i:
                break
            dp[i] = min(dp[i], dp[i - p] + cost[i])

    return dp[n - 1]
```

**时间复杂度**：O(n * P)，P 为 <= n 的末位为 3 的质数个数。
n=10000 时，P 约为 100 个，实际约为 O(100n)。
**空间复杂度**：O(n)（dp 数组）+ O(n)（筛法）。

### Optimization: Deque for Sliding Window Minimum

若需要 O(n) 或 O(n log n)，可使用线段树或单调双端队列处理有效跳跃位置。
但由于 P 较小，O(nP) 方案已足够实用。

### Edge Cases
- n = 1 -> 返回 cost[0]
- 所有代价为负（最大化负数路径）
- 大 n（筛法为 O(n log log n)，可忽略不计）

---

## 19. Min Edge Reversal for Optimal Root

**Pattern**: **Re-rooting DP（换根 DP）**

### Problem Statement

给定一棵有 `n` 个节点的有向树，选择一个根节点，使需要反转的边数（使所有边从根向外指）最少。
返回最少反转次数及对应的根节点编号。

### Approach

1. 构建无向邻接表，记录原始方向。
2. 从节点 0 出发 DFS：统计以 0 为根时所需的反转次数。
3. 换根：将根从父节点移至子节点时，若边为 parent->child（正向），反转次数 += 1；
   若边为 child->parent（反向），反转次数 -= 1。

```python
from collections import defaultdict
from typing import List, Tuple


def min_reversals(n: int, edges: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Find optimal root minimizing edge reversals.

    Args:
        n: Number of nodes.
        edges: Directed edges (u, v) meaning u -> v.

    Returns:
        (min_reversals, optimal_root)
    """
    # Build adjacency: (neighbor, cost_to_reverse)
    # If edge u->v exists, going from u to v costs 0 (correct direction),
    # but going from v to u costs 1 (reversal needed).
    adj: dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v in edges:
        adj[u].append((v, 0))  # original direction: no reversal
        adj[v].append((u, 1))  # reverse direction: needs reversal

    # Step 1: DFS from node 0 to count reversals rooted at 0
    cost_at_0 = 0
    visited = [False] * n

    def dfs(node: int) -> None:
        nonlocal cost_at_0
        visited[node] = True
        for neighbor, cost in adj[node]:
            if not visited[neighbor]:
                cost_at_0 += cost
                dfs(neighbor)

    dfs(0)

    # Step 2: Re-root DP
    result = [0] * n
    result[0] = cost_at_0

    visited = [False] * n

    def reroot(node: int) -> None:
        visited[node] = True
        for neighbor, cost in adj[node]:
            if not visited[neighbor]:
                # Moving root from node to neighbor:
                # cost=0 means edge node->neighbor (forward), now becomes
                # backward, so +1 reversal
                # cost=1 means edge neighbor->node (backward), now becomes
                # forward, so -1 reversal
                result[neighbor] = result[node] + (1 if cost == 0 else -1)
                reroot(neighbor)

    reroot(0)

    min_rev = min(result)
    optimal = result.index(min_rev)
    return min_rev, optimal
```

**时间复杂度**：O(n)——两次 DFS。
**空间复杂度**：O(n)，用于邻接表和结果数组。

### Key Insight

将根从父节点 `p` 移至子节点 `c` 时：
- 若原始边为 `p -> c`（从 p 出发 cost=0）：以 p 为根时方向正确，以 c 为根时方向相反，反转次数 += 1。
- 若原始边为 `c -> p`（从 p 出发 cost=1）：以 p 为根时方向相反，以 c 为根时方向正确，反转次数 -= 1。

### Edge Cases
- 所有边从节点 0 向外指 -> 0 次反转，以 0 为根
- 星形图 -> 取决于边的方向
- 线性链 -> 以一端为根

### Warning: 1-indexed Nodes

若问题使用 1 索引节点，需调整：
```python
visited = [False] * (n + 1)
result = [0] * (n + 1)
```

---

## 20. Palindrome Paths in Tree

**Pattern**: **Bitmask（位掩码）** XOR DFS / Prefix on Tree（树上前缀）

### Problem Statement

给定一棵树，每条边标有一个字符（a-z），统计路径数量，使得路径上的字符可以重新排列成回文串。

### Approach

若字符串可以重排成回文串，则至多有一个字符出现奇数次。
用位掩码表示字符频率（第 i 位 = 字符 i 的频率奇偶性）。
若路径的 XOR 位掩码为 0 或恰好一位为 1，则该路径为回文路径。

从根节点出发用 DFS 维护前缀 XOR。路径 (u, v) 的掩码：`mask(u,v) = prefix[u] XOR prefix[v]`。

```python
from collections import defaultdict
from typing import List, Tuple


def count_palindrome_paths(
    n: int, edges: List[Tuple[int, int, str]]
) -> int:
    """Count paths whose edge labels can form a palindrome.

    Args:
        n: Number of nodes (0-indexed).
        edges: (u, v, char) undirected edges.

    Returns:
        Number of palindrome-formable paths.
    """
    adj: dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v, ch in edges:
        bit = 1 << (ord(ch) - ord("a"))
        adj[u].append((v, bit))
        adj[v].append((u, bit))

    # prefix[node] = XOR of all edge bits from root to node
    prefix = [0] * n
    visited = [False] * n
    count = 0

    # Counter of prefix masks seen so far
    mask_count: dict[int, int] = defaultdict(int)

    def dfs(node: int) -> None:
        nonlocal count
        visited[node] = True

        # Count pairs: path (u, v) has mask prefix[u] ^ prefix[v]
        # Palindrome if mask == 0 or mask has exactly one bit set

        # Case 1: prefix[v] == prefix[node] -> XOR = 0
        count += mask_count[prefix[node]]

        # Case 2: prefix[v] ^ prefix[node] has exactly one bit set
        for bit in range(26):
            target = prefix[node] ^ (1 << bit)
            count += mask_count[target]

        mask_count[prefix[node]] += 1

        for neighbor, bit_mask in adj[node]:
            if not visited[neighbor]:
                prefix[neighbor] = prefix[node] ^ bit_mask
                dfs(neighbor)

    dfs(0)
    return count
```

**时间复杂度**：O(26n) = O(n)。
**空间复杂度**：O(n)，用于前缀数组和掩码计数器。

### Key Insight

- 从根节点出发的前缀 XOR 表示根到节点路径上每个字符的频率奇偶性。
- `prefix[u] XOR prefix[v]` 消除了公共的根到 LCA 部分，只保留 u 到 v 路径的字符频率奇偶性。
- 回文串要求 XOR = 0（全为偶数）或恰好一位为 1（一个奇数字符）。

### Edge Cases
- 单节点（0 条路径）
- 线性树（路径为子路径）
- 所有边标同一字符（所有路径均为回文路径）

---

## 21. Minesweeper Grid Generator

**Pattern**: Random Placement（随机布局）/ Code Quality（代码质量）

### Problem Statement

生成一个 M x N 的扫雷网格，随机放置恰好 K 个地雷。
显示网格时，每个格子显示相邻 8 格中地雷的数量，或用 `*` 表示地雷。

**延伸问题**：迭代改进代码质量——去除不必要的变量、简化逻辑、减少集合使用。

### Solution (Clean Version)

```python
import random
from typing import List


def generate_minesweeper(rows: int, cols: int, mines: int) -> List[List[str]]:
    """Generate a minesweeper grid with random mine placement.

    Args:
        rows, cols: Grid dimensions.
        mines: Number of mines to place.

    Returns:
        Grid where ''*'' = mine, digit = adjacent mine count.
    """
    total = rows * cols
    if mines > total:
        raise ValueError(f"Cannot place {mines} mines on {total}-cell grid")

    # Random mine positions
    positions = random.sample(range(total), mines)
    mine_set = set()
    for pos in positions:
        mine_set.add((pos // cols, pos % cols))

    # Build grid
    grid: List[List[str]] = []
    for r in range(rows):
        row: List[str] = []
        for c in range(cols):
            if (r, c) in mine_set:
                row.append("*")
            else:
                count = sum(
                    1
                    for dr in (-1, 0, 1)
                    for dc in (-1, 0, 1)
                    if (dr or dc)
                    and 0 <= r + dr < rows
                    and 0 <= c + dc < cols
                    and (r + dr, c + dc) in mine_set
                )
                row.append(str(count))
        grid.append(row)

    return grid


def print_grid(grid: List[List[str]]) -> None:
    """Pretty-print a minesweeper grid."""
    for row in grid:
        print(" ".join(row))
```

**时间复杂度**：O(M * N)（每格检查 8 个邻居，O(1)）。
**空间复杂度**：O(M * N)（网格）+ O(K)（地雷集合）。

### Follow-up: Iterative Code Quality Improvement

面试官会要求代码逐步变得更简洁：

**V1（初版）**：使用独立的 `is_mine` 二维数组，显式列出 8 个方向，变量较多。

**V2（简化版）**：用集合内联地雷检查，生成器表达式计算计数。

**V3（极简版）**：
```python
def minesweeper(m: int, n: int, k: int) -> List[List[str]]:
    mines = set(random.sample(range(m * n), k))
    is_mine = lambda r, c: r * n + c in mines

    def count(r: int, c: int) -> str:
        if is_mine(r, c):
            return "*"
        return str(sum(
            is_mine(r + dr, c + dc)
            for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if (dr or dc) and 0 <= r + dr < m and 0 <= c + dc < n
        ))

    return [[count(r, c) for c in range(n)] for r in range(m)]
```

### Edge Cases
- 0 个地雷 -> 全为 0
- 全为地雷 -> 全为星号
- 1x1 网格且有一个地雷

---

## 22. 2D Grid Nearest Exit (BFS)

**Pattern**: **BFS（广度优先搜索）** / Shortest Path（最短路径）

### Problem Statement

给定一个二维网格，包含墙和空格，从起始位置找到最近的出口（开放的边界格子）。
起始位置本身不算出口。

### Solution

```python
from collections import deque
from typing import List, Tuple


def nearest_exit(
    grid: List[List[str]], start: Tuple[int, int]
) -> int:
    """Find minimum steps from start to nearest exit (open boundary cell).

    Args:
        grid: ''.'' = open, ''+'' = wall.
        start: (row, col) starting position.

    Returns:
        Minimum steps to exit, or -1 if impossible.
    """
    rows, cols = len(grid), len(grid[0])
    sr, sc = start

    visited = [[False] * cols for _ in range(rows)]
    visited[sr][sc] = True
    queue: deque[Tuple[int, int, int]] = deque([(sr, sc, 0)])

    while queue:
        r, c, dist = queue.popleft()

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                if grid[nr][nc] == ".":
                    # Check if it''s a boundary cell (exit)
                    if (
                        nr == 0
                        or nr == rows - 1
                        or nc == 0
                        or nc == cols - 1
                    ):
                        return dist + 1
                    visited[nr][nc] = True
                    queue.append((nr, nc, dist + 1))

    return -1
```

**时间复杂度**：O(M * N)——每个格子最多访问一次。
**空间复杂度**：O(M * N)，用于 visited 数组和队列。

### Edge Cases
- 起点在边界（仍需移动到另一个出口）
- 没有可达的出口（被墙包围）
- 多个出口距离相同

---

## 23. Lock Combination BFS

**Pattern**: BFS on State Space（状态空间 BFS）

### Problem Statement

一把锁有 `n` 个转盘，每个转盘有 0-9 十个数字。每次操作可将一个转盘向上或向下转动 1 位。
给定目标组合和一组"死锁"组合（需要避免），求从"0000"到目标的最少操作次数。

### Solution

这本质上是 [LC 752](lc://752)（Open the Lock），Uber 常考：

```python
from collections import deque
from typing import List, Set


def min_moves_to_unlock(
    deadends: List[str], target: str
) -> int:
    """Minimum moves to reach target from ''0000'', avoiding deadends.

    Each move: rotate one wheel +1 or -1.
    """
    dead: Set[str] = set(deadends)
    start = "0000"

    if start in dead or target in dead:
        return -1

    if start == target:
        return 0

    visited: Set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])

    while queue:
        state, moves = queue.popleft()

        for i in range(len(state)):
            digit = int(state[i])
            for delta in (1, -1):
                new_digit = (digit + delta) % 10
                new_state = state[:i] + str(new_digit) + state[i + 1 :]

                if new_state == target:
                    return moves + 1

                if new_state not in visited and new_state not in dead:
                    visited.add(new_state)
                    queue.append((new_state, moves + 1))

    return -1
```

**时间复杂度**：O(10^n * n)，n 为转盘数量。n=4 时：O(40000)。
**空间复杂度**：O(10^n)，用于 visited 集合。

### Optimization: Bidirectional BFS

```python
def min_moves_bidirectional(
    deadends: List[str], target: str
) -> int:
    """Bidirectional BFS for faster convergence."""
    dead = set(deadends)
    start = "0000"
    if start in dead or target in dead:
        return -1
    if start == target:
        return 0

    front: Set[str] = {start}
    back: Set[str] = {target}
    visited: Set[str] = set()
    moves = 0

    while front and back:
        # Always expand the smaller frontier
        if len(front) > len(back):
            front, back = back, front

        next_front: Set[str] = set()
        for state in front:
            for i in range(len(state)):
                digit = int(state[i])
                for delta in (1, -1):
                    new_digit = (digit + delta) % 10
                    ns = state[:i] + str(new_digit) + state[i + 1 :]

                    if ns in back:
                        return moves + 1
                    if ns not in visited and ns not in dead:
                        visited.add(ns)
                        next_front.add(ns)

        front = next_front
        moves += 1

    return -1
```

### Edge Cases
- "0000" 是死锁 -> 返回 -1
- 目标为 "0000" -> 返回 0
- 不存在路径 -> 返回 -1

---

## 24. Non-overlapping Interval Triples

**Pattern**: Sorting（排序）+ Greedy（贪心）/ **DP（动态规划）**

### Problem Statement

给定一组区间 `[start, end]`，统计三个区间构成的组合数量，使得组中任意两个区间互不重叠。

### Approach

按结束时间排序区间。对于每个区间作为"中间"区间，统计在其开始之前结束的区间数（左侧候选）
和在其结束之后开始的区间数（右侧候选）。以该区间为中间的三元组数 = `left * right`。

```python
import bisect
from typing import List, Tuple


def count_non_overlapping_triples(
    intervals: List[Tuple[int, int]]
) -> int:
    """Count groups of 3 pairwise non-overlapping intervals."""
    intervals.sort()
    n = len(intervals)

    # Precompute: ends sorted for binary search
    ends = sorted(e for _, e in intervals)
    starts = sorted(s for s, _ in intervals)

    count = 0

    for i in range(n):
        s, e = intervals[i]

        # Count intervals that end strictly before s (can precede interval i)
        left = bisect.bisect_left(ends, s)

        # Count intervals that start strictly after e (can follow interval i)
        right = n - bisect.bisect_right(starts, e)

        count += left * right

    # Each triple is counted 1 time (middle element is unique)
    # But we need to handle overcounting: if left has 2+ and they overlap each other,
    # we overcounted. For exact count, need more careful approach.
    # The above is an APPROXIMATION. For exact count, use the approach below.

    return count


def count_triples_exact(intervals: List[Tuple[int, int]]) -> int:
    """Exact count using sorted order and DP.

    Sort by end time. For each interval i, count pairs of non-overlapping
    intervals that end before i starts. Then i extends each pair to a triple.
    """
    intervals.sort(key=lambda x: x[1])
    n = len(intervals)
    ends = [e for _, e in intervals]

    # pairs_before[i] = number of non-overlapping pairs among intervals
    # that end before intervals[i] starts
    # singles_before[i] = number of intervals that end before intervals[i] starts

    count = 0
    # For each interval i, find how many intervals end before its start
    # Then from those, how many non-overlapping pairs exist

    # Approach: sweep and maintain count of singles and pairs
    # When processing interval i (sorted by end):
    #   - singles = number of previous intervals that end before start[i]
    #   - pairs = number of non-overlapping pairs among those

    # Prefix approach:
    # singles[i] = number of intervals j < i where end[j] < start[i]
    # For triples: for interval i, count pairs among intervals ending before start[i]

    # Two-pass: first compute singles_before for each interval
    singles = [0] * n
    for i in range(n):
        singles[i] = bisect.bisect_left(ends, intervals[i][0])

    # pairs_ending_before[t] = number of non-overlapping pairs where both
    # intervals end before time t
    # For each interval i (in end-sorted order), it forms pairs with
    # all singles_before[i] intervals before it.
    # pairs_before[i] = sum of singles_before[j] for all j where end[j] < start[i]
    # This requires a Fenwick tree or prefix sum approach.

    # Simpler O(n^2) approach:
    pairs_before = [0] * n
    for i in range(n):
        for j in range(i):
            if ends[j] <= intervals[i][0]:
                pairs_before[i] += 1
            else:
                break  # since sorted by end, can optimize

    # For triples: for each i, count non-overlapping pairs before start[i]
    # A pair (j, k) where j < k, end[j] < start[k], and end[k] < start[i]
    pair_count = [0] * n
    for k in range(n):
        pair_count[k] = singles[k]  # intervals before k that don''t overlap

    # Triple: for each i, sum pair_count[k] for all k where end[k] < start[i]
    # Use prefix sums on pair_count indexed by end time
    for i in range(n):
        s_i = intervals[i][0]
        idx = bisect.bisect_left(ends, s_i)
        count += sum(pair_count[j] for j in range(idx))

    return count
```

### Cleaner O(n log n) Solution

```python
def count_triples_optimal(intervals: List[Tuple[int, int]]) -> int:
    """O(n log n) using Fenwick tree.

    Sort by end time. For each interval i:
      - singles_before[i] = # intervals ending before start[i]
      - For triples, maintain cumulative pair_count.
    """
    intervals.sort(key=lambda x: x[1])
    n = len(intervals)
    ends = [e for _, e in intervals]

    total = 0
    # For each interval as the LAST in a triple:
    # Count non-overlapping pairs that both end before this interval starts.
    # A pair is (j, k) with end[j] < start[k] and end[k] < start[i].
    # For interval k: it can pair with singles_before[k] intervals.
    # Accumulate pair_count as we go.

    cumulative_pairs = 0  # total pairs ending before current consideration
    pair_counts = []  # pair_count[k] for each k in order

    for i in range(n):
        s_i = intervals[i][0]

        # Count pairs that fully precede interval i
        # All intervals k where end[k] < s_i contribute pair_count[k] pairs
        idx = bisect.bisect_left(ends, s_i)
        triple_count = sum(pair_counts[:idx]) if pair_counts else 0
        total += triple_count

        # This interval''s pair count (how many singles precede it)
        my_pairs = bisect.bisect_left(ends, s_i)
        pair_counts.append(my_pairs)

    return total
```

**时间复杂度**：前缀和方法 O(n^2)，使用 Fenwick 树（树状数组）可达 O(n log n)。
**空间复杂度**：O(n)。

### Edge Cases
- 少于 3 个区间 -> 0
- 所有区间重叠 -> 0
- 所有区间互不重叠 -> C(n, 3)

---

## 25. City Graph BFS Sort

**Pattern**: BFS + Custom Sorting（BFS + 自定义排序）

### Problem Statement

给定一个城市图（无向）和起始城市，按城市到起始城市的距离对所有城市排序。
距离相同时，城市编号较小的排在前面。

### Solution

```python
from collections import defaultdict, deque
from typing import List, Tuple


def sort_cities_by_distance(
    n: int, edges: List[Tuple[int, int]], start: int
) -> List[int]:
    """Sort cities by BFS distance from start. Ties: smaller index first.

    Args:
        n: Number of cities (0-indexed).
        edges: Undirected edges (u, v).
        start: Starting city.

    Returns:
        List of city indices sorted by (distance, index).
    """
    adj: dict[int, List[int]] = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # BFS to compute distances
    dist = [-1] * n
    dist[start] = 0
    queue: deque[int] = deque([start])

    while queue:
        node = queue.popleft()
        for neighbor in adj[node]:
            if dist[neighbor] == -1:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)

    # Sort by (distance, index). Unreachable cities get infinite distance.
    INF = n + 1
    cities = list(range(n))
    cities.sort(key=lambda c: (dist[c] if dist[c] != -1 else INF, c))

    return cities
```

**时间复杂度**：O(V + E)（BFS）+ O(V log V)（排序）。
**空间复杂度**：O(V + E)。

### Edge Cases
- 不连通图（不可达城市排在末尾）
- 起始城市孤立
- 完全图（除起点外所有城市距离均为 1）
- 自环（不影响 BFS）

### Follow-up: Weighted Graph

对于有权图，使用 **Dijkstra（迪杰斯特拉算法）** 代替 BFS：

```python
import heapq


def sort_cities_weighted(
    n: int, edges: List[Tuple[int, int, int]], start: int
) -> List[int]:
    """Weighted version using Dijkstra."""
    adj: dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    dist = [float("inf")] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in adj[node]:
            nd = d + weight
            if nd < dist[neighbor]:
                dist[neighbor] = nd
                heapq.heappush(heap, (nd, neighbor))

    cities = list(range(n))
    cities.sort(key=lambda c: (dist[c], c))
    return cities
```

---

## Summary Table

| # | Problem | Pattern | Time | Space |
|---|---------|---------|------|-------|
| 1 | Purchase Optimization | Prefix Sum + Binary Search | O(n log n + q log n) | O(n) |
| 2 | Revenue & Referral (OOD) | Tree Aggregation | O(D) insert, O(n log k) query | O(n) |
| 3 | Rider Connection Log | Union Find + BFS | O(E alpha(N)) / O(E(V+E)) | O(N) |
| 4 | Elevator Binary Search | Simulation | O(n^2) / O(n log n) | O(n) |
| 5 | Server Throughput | Heap Scheduling | O(R log S) | O(S) |
| 6 | Cart & Pricing (OOD) | Strategy Pattern | O(items * rules) | O(items) |
| 7 | Circular Array Jump | BFS | O(n) | O(n) |
| 8 | Robot Distance Grid | DP Precompute | O(M*N) | O(M*N) |
| 9 | Min Ops n->0 | Greedy/NAF | O(log n) | O(1) |
| 10 | Shortest k-Distinct | Sliding Window | O(n) | O(k) |
| 11 | Price Discount | Monotonic Stack | O(n) | O(n) |
| 12 | Balanced Permutation | Min/Max Tracking | O(n) | O(n) |
| 13 | Elevator/Stairs Energy | Binary/Ternary Search | O(n log n) | O(1) |
| 14 | N-ary Tree 3-Part | Tree DFS | O(n) | O(h) |
| 15 | Max Throughput Budget | Binary Search on Answer | O(n log T) | O(1) |
| 16 | Parking Lot (OOD) | OOD + Free Queues | O(1) optimized | O(S) |
| 17 | Task Assignment | Greedy Sort by Diff | O(n log n) | O(n) |
| 18 | Jump Game Prime | DP + Sieve | O(nP) | O(n) |
| 19 | Min Edge Reversal | Re-rooting DP | O(n) | O(n) |
| 20 | Palindrome Paths | Bitmask XOR DFS | O(26n) | O(n) |
| 21 | Minesweeper Generator | Random + Grid | O(M*N) | O(M*N) |
| 22 | Grid Nearest Exit | BFS | O(M*N) | O(M*N) |
| 23 | Lock Combination | BFS State Space | O(10^n * n) | O(10^n) |
| 24 | Non-overlapping Triples | Sort + Prefix Count | O(n^2) / O(n log n) | O(n) |
| 25 | City Graph BFS Sort | BFS + Sort | O(V+E + V log V) | O(V+E) |

---

## Pattern Quick Reference

- **Binary Search**: #1 Purchase Opt, #4 Elevator, #13 Energy, #15 Max Throughput
- **BFS/DFS**: #7 Circular Jump, #22 Grid Exit, #23 Lock, #25 City Sort
- **Union Find**: #3 Rider Connection
- **DP**: #18 Jump Game Prime, #19 Re-rooting, #20 Palindrome Paths
- **Greedy**: #9 Min Ops, #17 Task Assignment
- **Monotonic Stack**: #11 Price Discount
- **Sliding Window**: #10 k-Distinct Subarray
- **Heap**: #5 Server Throughput
- **OOD**: #2 Revenue Tracking, #6 Cart Engine, #16 Parking Lot
- **Grid/Matrix**: #8 Robot Distance, #21 Minesweeper
- **Tree**: #14 N-ary Tree 3-Part
- **Tracking**: #12 Balanced Permutation', updated_at = datetime('now') WHERE id = 31;

-- doc 32 (Uber BPS Pattern Cheat Sheet by Algorithm): lc=57 leetcode=0 custom=0
UPDATE company_documents SET content = '# Uber BPS -- 算法模式速查表

> 按算法模式组织的快速参考。每个部分：何时识别该模式、模板方法、所有使用该模式的 Uber BPS 题目以及复杂度。
>
> 来源：`uber_bps_lc_solutions.md`（19道 **LC (LeetCode)** 题）、`uber_bps_custom_solutions.md`（25道自定义题）
>
> Task: T-P1-247

---

## Table of Contents

1. [BFS / Multi-source BFS](#1-bfs--multi-source-bfs)
2. [DFS / Backtracking](#2-dfs--backtracking)
3. [Tree DP / Tree Traversal](#3-tree-dp--tree-traversal)
4. [Union Find (Disjoint Set)](#4-union-find-disjoint-set)
5. [Binary Search](#5-binary-search)
6. [Dynamic Programming](#6-dynamic-programming)
7. [Greedy](#7-greedy)
8. [Heap (Priority Queue)](#8-heap-priority-queue)
9. [Sliding Window](#9-sliding-window)
10. [Monotonic Stack](#10-monotonic-stack)
11. [Two Pointers](#11-two-pointers)
12. [Object-Oriented Design (OOD)](#12-object-oriented-design-ood)
13. [Grid / Matrix](#13-grid--matrix)
14. [Bitmask Techniques](#14-bitmask-techniques)
15. [Complexity Summary Table](#15-complexity-summary-table)
16. [Pattern Recognition Decision Tree](#16-pattern-recognition-decision-tree)

---

## 1. BFS / Multi-source BFS

### When to recognize（何时识别）

- "最短路径"——无权图或网格
- "最少步数/移动次数"到达目标
- 从多个源头同时扩散/感染
- 逐层探索（距离为 k 的所有节点）
- "最近出口"或"到边界的最短距离"

### Template（模板）

```python
from collections import deque

def bfs(graph, start, target):
    q = deque([(start, 0)])
    visited = {start}
    while q:
        node, dist = q.popleft()
        if node == target:
            return dist
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                q.append((neighbor, dist + 1))
    return -1
```

**多源 BFS (Multi-source BFS)**：在开始之前将所有源节点以距离0入队。

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 994](lc://994) Rotting Oranges | 多源 BFS | 所有腐烂橘子同时开始 | O(mn) | O(mn) |
| [LC 1020](lc://1020) Number of Enclaves | 边界 BFS | 从边界 flood-fill，计数剩余 | O(mn) | O(mn) |
| [LC 1197](lc://1197) Min Knight Moves | 带剪枝的 BFS | 对称性：仅在第一象限工作 | O(xy) | O(xy) |
| [LC 815](lc://815) Bus Routes | 路线图上的 BFS | 节点 = 路线，边 = 共享站点 | O(sum routes) | O(sum routes) |
| [LC 2503](lc://2503) Max Grid Points | BFS + 排序查询 | 按升序处理查询，扩展前沿 | O(mn log mn) | O(mn) |
| Custom #7 Circular Jump | 环形数组 BFS | 取模运算处理环绕 | O(n) | O(n) |
| Custom #22 Grid Nearest Exit | 标准网格 BFS | 从所有出口多源 BFS，找最小值 | O(mn) | O(mn) |
| Custom #23 Lock Combination | 状态空间 BFS | 状态 = 数字组合，10^n 空间 | O(10^n * n) | O(10^n) |
| Custom #25 City Graph BFS Sort | BFS + Dijkstra | 最短路径后按距离排序 | O(V+E + V log V) | O(V+E) |

### Tips（技巧）

- 网格 BFS：4方向 `[(0,1),(0,-1),(1,0),(-1,0)]`，内联检查边界。
- 多源：先将所有源入队，再 BFS -- 得到正确的最小距离。
- 如果图有权重，BFS 不适用 -- 使用 **Dijkstra**（基于堆的 BFS）。

---

## 2. DFS / Backtracking

### When to recognize（何时识别）

- "生成所有组合/排列"
- "是否存在路径"（存在性，非最短）
- "在网格中搜索单词"
- "所有满足约束的有效配置"
- 电话号码字母组合、子集生成

### Template (Backtracking)（回溯模板）

```python
def backtrack(state, choices, result):
    if is_complete(state):
        result.append(state.copy())
        return
    for choice in choices:
        if is_valid(choice, state):
            state.add(choice)
            backtrack(state, choices, result)
            state.remove(choice)  # undo
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 79](lc://79) Word Search | 网格 **DFS (Depth-First Search，深度优先搜索)** + 回溯 | 用 ''#'' 原地标记已访问，恢复 | O(mn * 3^L) | O(L) |
| [LC 79](lc://79) variant: 8-dir straight | 线性扫描，无回溯 | 每个起点一个方向——简单得多 | O(mn * 8 * L) | O(1) |
| [LC 17](lc://17) Letter Combos | 回溯 | 数字映射到字符，枚举 | O(4^n * n) | O(n) |

### Tips（技巧）

- 标记-恢复：原地修改网格（`board[i][j] = ''#''`），DFS 后恢复。
- 提前终止：剪枝无法得到有效结果的分支。
- 对于"计数"问题，返回整数而非收集所有解。

---

## 3. Tree DP / Tree Traversal

### When to recognize（何时识别）

- "树路径上可达的最大/最小值"
- "树形排列的房屋抢劫"（取/跳决策）
- "树中最长连续序列"
- "BST 中第 k 小/大"
- "垂直/层序遍历"
- 每个节点基于子节点的子答案贡献最终答案

### Template (Tree DP)（树形 DP 模板）

```python
def tree_dp(root):
    best = [0]

    def dfs(node):
        if not node:
            return (0, 0)  # (option_a, option_b)
        left = dfs(node.left)
        right = dfs(node.right)
        take = node.val + left[1] + right[1]   # take this node
        skip = max(left) + max(right)           # skip this node
        best[0] = max(best[0], take, skip)
        return (take, skip)

    dfs(root)
    return best[0]
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 230](lc://230) Kth Smallest BST | 中序遍历 | 迭代中序，在第 k 个停止 | O(H+k) | O(H) |
| [LC 230](lc://230) variant: Kth Largest | 反向中序 | Right -> root -> left | O(H+k) | O(H) |
| [LC 230](lc://230) follow-up: Morris | O(1) 空间遍历 | 线索化前驱节点 | O(n) | O(1) |
| [LC 230](lc://230) follow-up: Augmented | 存储子树大小 | 通过 left_count 实现 O(H) 查找 | O(H) | O(1) |
| [LC 337](lc://337) House Robber III | 树形 **DP (Dynamic Programming，动态规划)** (取/跳) | 每个节点返回 (rob, skip) 对 | O(n) | O(H) |
| [LC 549](lc://549) Longest Consecutive II | 树形 DP (递增/递减) | 同时追踪递增和递减长度 | O(n) | O(H) |
| [LC 987](lc://987) Vertical Traversal | **BFS (Breadth-First Search，广度优先搜索)** + 列追踪 | 按 (col, row, val) 排序 | O(n log n) | O(n) |
| Custom #14 N-ary Tree 3-Part | DFS 子树操作 | N叉树上的序列化、LCA、子树求和 | O(n) | O(H) |

### Tips（技巧）

- **BST (Binary Search Tree，二叉搜索树)** 性质：中序 = 有序。用此性质解第 k 小元素。
- 树形 DP 签名：`dfs(node) -> tuple`。元组捕获所有需要的状态。
- "经过节点的路径" = 左贡献 + 右贡献 + 节点值。
- Morris 遍历：O(1) 空间但修改/恢复树——面试中需提及。

---

## 4. Union Find (Disjoint Set)（并查集）

### When to recognize（何时识别）

- "连通分量数"
- "节点是否在同一组？"
- "随时间合并组"（在线连通性）
- "离线处理按权重/限制排序的查询"
- "省份/朋友圈/岛屿计数"

### Template（模板）

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 547](lc://547) Number of Provinces | 基础 UF 或 DFS | 计数不同的根 | O(n^2 alpha(n)) | O(n) |
| [LC 1697](lc://1697) Edge Length Limited | 离线查询 + **UF (Union Find，并查集)** | 按权重排序边和查询 | O((E+Q) log) | O(n+Q) |
| [LC 1697](lc://1697) variant: weight >= k | 反向排序 | 按降序处理边权重 | O((E+Q) log) | O(n+Q) |
| Custom #3 Rider Connection | UF + BFS 重建 | UF 处理连接，BFS 处理屏蔽事件 | O(E alpha(N)) | O(N) |

### Tips（技巧）

- **离线查询技巧**：将边和查询一起排序，同步遍历。
- 路径压缩 + 按秩合并 = 每次操作近 O(1)（摊销）。
- 对于"撤销"操作（屏蔽/断开），UF 不支持撤销——使用 BFS 重建或离线逆序处理。
- 计数分量：`len(set(find(i) for i in range(n)))`。

---

## 5. Binary Search（二分查找）

### When to recognize（何时识别）

- "某值的最小/最大"且可行性具有单调性
- "在有序数组中搜索"或"有序 + 旋转"
- "前缀和 + 区间查询"
- "二分答案"（参数化搜索）
- "找阈值/边界"

### Template (Binary Search on Answer)（二分答案模板）

```python
def binary_search_on_answer(lo, hi, is_feasible):
    while lo < hi:
        mid = (lo + hi) // 2
        if is_feasible(mid):
            hi = mid      # try smaller (minimize)
        else:
            lo = mid + 1  # need larger
    return lo
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 981](lc://981) TimeMap | 时间戳上的 **BS (Binary Search，二分查找)** | 在有序时间戳列表上 bisect_right | O(log n) get | O(n) |
| [LC 977](lc://977) Squares Sorted (related) | 有序输入 | 双指针比 BS 更好 | O(n) | O(n) |
| Custom #1 Purchase Optimization | 前缀和 + BS | 在前缀和上二分查找预算 | O(n log n + q log n) | O(n) |
| Custom #4 Elevator BS | 模拟 + BS | 二分查找最优楼层 | O(n log n) | O(n) |
| Custom #13 Elevator/Stairs Energy | 三分/二分查找 | 单峰函数——三分查找 | O(n log n) | O(1) |
| Custom #15 Max Throughput Budget | 二分答案 | "能否在预算 B 下达到吞吐量 T？" | O(n log T) | O(1) |

### Tips（技巧）

- **前缀和 + 二分查找**：用于"预算内最大数量"的经典组合。
- **二分答案**：定义 `is_feasible(x)` 并二分查找 min/max x。
- **三分查找**：用于单峰函数（一个峰/谷）。
- 始终验证：`lo` 还是 `hi` 给出答案？Off-by-one 是 BS 的头号 bug。

---

## 6. Dynamic Programming（动态规划）

### When to recognize（何时识别）

- "每步有选择的最大/最小得分"
- "到达目标的方式数"
- "能否到达终点？"（可变跳跃）
- 重叠子问题 + 最优子结构
- 树上"换根"（计算每个根的答案）

### Template (Re-rooting DP)（换根 DP 模板）

```python
def rerooting_dp(n, adj):
    dp = [0] * n
    # Step 1: DFS from node 0 to compute dp[0]
    def dfs(node, parent):
        cost = 0
        for neighbor, edge_cost in adj[node]:
            if neighbor != parent:
                cost += edge_cost + dfs(neighbor, node)
        return cost
    dp[0] = dfs(0, -1)

    # Step 2: Propagate to all nodes
    def reroot(node, parent):
        for neighbor, edge_cost in adj[node]:
            if neighbor != parent:
                dp[neighbor] = dp[node] + delta(edge_cost)
                reroot(neighbor, node)
    reroot(0, -1)
    return dp
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 1696](lc://1696) Jump Game VI | DP + 单调双端队列 | 滑动窗口最大值实现 O(n) DP 转移 | O(n) | O(k) |
| [LC 1696](lc://1696) variant: prime jumps | DP + 筛法 | 预计算以3结尾的素数作为跳跃大小 | O(n*P) | O(n) |
| [LC 2858](lc://2858) Min Edge Reversals | 换根 DP | 计算根0，每条边 +1/-1 传播 | O(n) | O(n) |
| Custom #8 Robot Distance Grid | DP 预计算 | 通过网格 DP 预计算距离 | O(mn) | O(mn) |
| Custom #18 Jump Game Prime | DP + 筛法 | 跳 +1 或 +以3结尾的素数 | O(n*P) | O(n) |
| Custom #19 Min Edge Reversal | 换根 DP | 同 [LC 2858](lc://2858) | O(n) | O(n) |
| Custom #24 Non-overlapping Triples | 排序 + DP/前缀 | 排序区间，前缀计数实现不重叠 | O(n^2) | O(n) |

### Tips（技巧）

- **换根 DP**：两遍（根0的 DFS，然后传播）。关键：用 O(1) 转移从 dp[parent] 表达 dp[child]。
- **单调双端队列 DP**：当转移为 `dp[i] = max(dp[j] for j in window) + cost` 时使用双端队列。
- **DP + 筛法**：预计算素数一次，用作跳跃表。
- 注意边反转问题中的1-indexed 输入。

---

## 7. Greedy（贪心）

### When to recognize（何时识别）

- "最少操作次数"且有明确的局部最优选择
- "分配任务以最小化总成本"
- 排序 + 贪心选择给出最优解
- 每个选择独立（无未来后悔）

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #9 Min Ops n->0 | 贪心/NAF | 使用最大负斐波那契数幂 / 特殊移动 | O(log n) | O(1) |
| Custom #17 Task Assignment | 按差值排序 | 按 cost_A - cost_B 排序，最优分配 | O(n log n) | O(n) |

### Tips（技巧）

- **交换论证**：通过证明任何交换都会使结果变差来证明贪心最优。
- **按 X - Y 排序**：用于双选择分配的经典方法（如 A 和 B 的成本差）。
- 如果贪心不明显有效，那它可能就不行——改试 DP。

---

## 8. Heap (Priority Queue，优先队列)

### When to recognize（何时识别）

- "K 个最大/最小元素"
- "合并 K 个有序流"
- "调度作业以最大化吞吐量"
- "按优先级处理项目"
- 流数据中需要运行中的 top-k 或 min/max

### Template（模板）

```python
import heapq

# Min-heap (default in Python)
heapq.heappush(heap, item)
heapq.heappop(heap)           # smallest item

# Max-heap: negate values
heapq.heappush(heap, -item)
-heapq.heappop(heap)          # largest item
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 23](lc://23) Merge K Sorted Lists | k 个头节点的最小堆 | 弹出最小值，推入其下一个 | O(N log k) | O(k) |
| [LC 23](lc://23) variant: divide & conquer | 两两合并 | 反复合并对 | O(N log k) | O(1) |
| Custom #5 Server Throughput | 调度堆 | 将请求分配给最早空闲的服务器 | O(R log S) | O(S) |

### Tips（技巧）

- Python `heapq` 只有最小堆。最大堆用取负值或元组 `(-priority, item)`。
- "合并 K 个有序"任何东西：大小为 K 的堆，弹出-推入模式。
- 调度：堆存储 (end_time, server_id)，弹出最早空闲的。

---

## 9. Sliding Window（滑动窗口）

### When to recognize（何时识别）

- "具有性质 X 的最短/最长子数组"
- "最多 K 个不同元素"
- "和在范围内"
- 连续子数组/子串约束
- 问题中出现"窗口"关键词

### Template（模板）

```python
def sliding_window(arr, k):
    counts = {}
    left = 0
    best = float(''inf'')
    for right in range(len(arr)):
        # Expand: add arr[right]
        counts[arr[right]] = counts.get(arr[right], 0) + 1
        # Shrink while constraint violated
        while len(counts) > k:  # example constraint
            counts[arr[left]] -= 1
            if counts[arr[left]] == 0:
                del counts[arr[left]]
            left += 1
        best = min(best, right - left + 1)
    return best
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #10 Shortest k-Distinct | 达到 k 个不同时收缩 | 追踪字符计数，收缩找最小长度 | O(n) | O(k) |
| [LC 1696](lc://1696) (双端队列方面) | 滑动窗口最大值 | 单调双端队列维护窗口内最大值 | O(n) | O(k) |

### Tips（技巧）

- **双指针不变式**：维护窗口 [left, right]，其中性质成立。
- 扩展 right，收缩 left。在每个有效窗口时更新答案。
- "恰好 K 个不同"用 `atMost(K) - atMost(K-1)` 技巧。

---

## 10. Monotonic Stack（单调栈）

### When to recognize（何时识别）

- "下一个更大/更小元素"
- "价格折扣：最近的未来更低价格"
- "股票跨度"问题
- "直方图中最大矩形"系列
- 按顺序处理元素，维护递增/递减性质

### Template（模板）

```python
def next_smaller(prices):
    n = len(prices)
    result = [0] * n
    stack = []  # indices, maintaining increasing values
    for i in range(n):
        while stack and prices[stack[-1]] >= prices[i]:
            idx = stack.pop()
            result[idx] = prices[i]  # prices[i] is next smaller
        stack.append(i)
    return result
```

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #11 Price Discount | 下一个更小元素 | 为每个价格找最近的未来折扣 | O(n) | O(n) |

### Tips（技巧）

- 栈存储索引（不是值）——可以计算距离和访问值。
- **递增栈**：找下一个更小。**递减栈**：找下一个更大。
- 从左到右处理找"下一个"元素，从右到左处理找"前一个"元素。

---

## 11. Two Pointers（双指针）

### When to recognize（何时识别）

- 有序数组操作（合并、去重）
- "有序数组的平方"
- "盛最多水的容器" / "接雨水"
- 从两端向内比较

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 977](lc://977) Squares of Sorted Array | 从两端双指针 | 最大绝对值在边缘 | O(n) | O(n) |

### Tips（技巧）

- 当数组有序且需要对变换产生有序输出时，考虑从两端双指针。
- 从末尾填充结果数组（先放最大值），避免移位。

---

## 12. Object-Oriented Design (OOD，面向对象设计)

### When to recognize（何时识别）

- "设计一个系统"（停车场、购物车、收入追踪器）
- "实现一个具有这些操作的类"
- 面试官询问可扩展性、**SOLID** 原则
- 多种实体类型交互

### Design Checklist（设计清单）

1. **明确需求**：哪些操作？什么规模？
2. **识别实体**：问题中的名词 = 类
3. **定义接口**：每个类暴露哪些方法？
4. **选择模式**：可互换算法用 **Strategy Pattern（策略模式）**，事件用 **Observer Pattern（观察者模式）**
5. **优化**：识别最重要的 O(1) 操作

### Uber BPS Problems

| 题目 | 设计模式 | 关键思路 | 优化操作 |
|------|----------|----------|----------|
| Custom #2 Revenue & Referral | 树形聚合 | 推荐树 + 收入汇总 | O(D) 插入 |
| Custom #6 Cart & Pricing Engine | Strategy Pattern | 加价/会员/优惠作为可插拔规则 | O(items * rules) |
| Custom #16 Parking Lot | **OOD (Object-Oriented Design，面向对象设计)** + 空闲队列 | 按大小的最小堆或队列实现 O(1) 停车 | O(1) 停车/取车 |

### Tips（技巧）

- **从简单开始**：先写基础类，面试官问"如果需要添加 X 呢？"时再加模式。
- **Strategy Pattern**：当定价/评分规则变化时使用。每个规则是实现公共接口的类。
- **O(1) 优化**：停车场用按车辆大小的空闲车位队列。
- 始终讨论权衡："Strategy 更可扩展但增加了间接层。"

---

## 13. Grid / Matrix（网格/矩阵）

### When to recognize（何时识别）

- 2D 棋盘/地图问题
- "放置地雷"、"计数邻居"
- 机器人移动、距离计算
- 洪水填充、连通区域

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| Custom #8 Robot Distance | 网格 DP | 从源点预计算所有距离 | O(mn) | O(mn) |
| Custom #21 Minesweeper | 随机放置 + 计数 | 随机放置地雷，计算邻居计数 | O(mn) | O(mn) |

### Tips（技巧）

- 4方向：`[(0,1),(0,-1),(1,0),(-1,0)]`。8方向：加对角线。
- 边界检查：`0 <= nx < m and 0 <= ny < n`。
- 原地标记（`grid[i][j] = -1`）节省空间但修改输入——面试中需提及。

---

## 14. Bitmask Techniques（位掩码技术）

### When to recognize（何时识别）

- "回文可构成"（偶/奇字符计数）
- 按字符/元素的布尔标志进行状态追踪
- XOR 用于切换/取消操作
- 小字母表（26个字母可放入32位整数）

### Uber BPS Problems

| 题目 | 变体 | 关键思路 | 时间 | 空间 |
|------|------|----------|------|------|
| [LC 2791](lc://2791) Palindrome Paths | XOR 前缀位掩码 | 路径 u->v 回文当且仅当 XOR 最多1位为1 | O(26n) | O(n) |
| Custom #20 Palindrome Paths | 相同技术 | 路径上字符奇偶性的位掩码 | O(26n) | O(n) |

### Tips（技巧）

- **XOR 前缀**：`prefix[v] = prefix[parent] ^ (1 << char)`。路径 u-v = `prefix[u] ^ prefix[v]`。
- **最多1位为1**：检查 `x == 0` 或 `x & (x-1) == 0`。
- **26位掩码**：每个字母一位，追踪奇偶性。XOR 切换奇偶性。

---

## 15. Complexity Summary Table（复杂度汇总表）

### LC Problems

| LC # | 题目 | 模式 | 时间 | 空间 |
|------|------|------|------|------|
| 17 | Letter Combinations | 回溯 | O(4^n * n) | O(n) |
| 23 | Merge K Sorted Lists | 堆 | O(N log k) | O(k) |
| 79 | Word Search | DFS 回溯 | O(mn * 3^L) | O(L) |
| 230 | Kth Smallest BST | 中序遍历 | O(H + k) | O(H) |
| 337 | House Robber III | 树形 DP | O(n) | O(H) |
| 547 | Number of Provinces | Union Find / DFS | O(n^2 alpha) | O(n) |
| 549 | Longest Consecutive II | 树形 DP | O(n) | O(H) |
| 815 | Bus Routes | 路线 BFS | O(sum routes) | O(sum routes) |
| 977 | Squares Sorted Array | 双指针 | O(n) | O(n) |
| 981 | Time Based KV Store | 二分查找 | O(log n) get | O(n) |
| 987 | Vertical Traversal | BFS + 排序 | O(n log n) | O(n) |
| 994 | Rotting Oranges | 多源 BFS | O(mn) | O(mn) |
| 1020 | Number of Enclaves | 边界 BFS | O(mn) | O(mn) |
| 1197 | Min Knight Moves | BFS | O(xy) | O(xy) |
| 1696 | Jump Game VI | DP + 单调双端队列 | O(n) | O(k) |
| 1697 | Edge Length Limited | UF + 离线查询 | O((E+Q) log) | O(n+Q) |
| 2503 | Max Grid Points | BFS + 排序查询 | O(mn log mn) | O(mn) |
| 2791 | Palindrome Paths Tree | 位掩码 XOR DFS | O(26n) | O(n) |
| 2858 | Min Edge Reversals | 换根 DP | O(n) | O(n) |

### Custom Problems

| # | 题目 | 模式 | 时间 | 空间 |
|---|------|------|------|------|
| 1 | Purchase Optimization | 前缀和 + BS | O(n log n + q log n) | O(n) |
| 2 | Revenue & Referral | OOD / 树 | O(D) 插入 | O(n) |
| 3 | Rider Connection | Union Find + BFS | O(E alpha(N)) | O(N) |
| 4 | Elevator BS | 二分查找 | O(n log n) | O(n) |
| 5 | Server Throughput | 堆调度 | O(R log S) | O(S) |
| 6 | Cart & Pricing | OOD Strategy | O(items * rules) | O(items) |
| 7 | Circular Jump | BFS | O(n) | O(n) |
| 8 | Robot Distance | 网格 DP | O(mn) | O(mn) |
| 9 | Min Ops n->0 | 贪心 | O(log n) | O(1) |
| 10 | k-Distinct Subarray | 滑动窗口 | O(n) | O(k) |
| 11 | Price Discount | 单调栈 | O(n) | O(n) |
| 12 | Balanced Permutation | Min/Max 追踪 | O(n) | O(n) |
| 13 | Elevator/Stairs Energy | 三分查找 | O(n log n) | O(1) |
| 14 | N-ary Tree 3-Part | 树 DFS | O(n) | O(H) |
| 15 | Max Throughput Budget | 二分答案 | O(n log T) | O(1) |
| 16 | Parking Lot | OOD | O(1) 停车 | O(S) |
| 17 | Task Assignment | 贪心排序 | O(n log n) | O(n) |
| 18 | Jump Game Prime | DP + 筛法 | O(n*P) | O(n) |
| 19 | Min Edge Reversal | 换根 DP | O(n) | O(n) |
| 20 | Palindrome Paths | 位掩码 XOR DFS | O(26n) | O(n) |
| 21 | Minesweeper | 网格随机 | O(mn) | O(mn) |
| 22 | Grid Nearest Exit | BFS | O(mn) | O(mn) |
| 23 | Lock Combination | BFS 状态空间 | O(10^n * n) | O(10^n) |
| 24 | Non-overlapping Triples | 排序 + 前缀 | O(n^2) | O(n) |
| 25 | City Graph Sort | BFS + Dijkstra | O(V+E + V log V) | O(V+E) |

---

## 16. Pattern Recognition Decision Tree（模式识别决策树）

使用此流程图从问题关键词识别正确模式：

```
是设计问题吗？（类、实体、操作）
  是 -> OOD (#2, #6, #16)

是在树上吗？
  是 -> 是 BST 的第 k 小/搜索？
           是 -> 中序遍历 ([LC 230](lc://230))
         是"取或跳"节点决策？
           是 -> 树形 DP ([LC 337](lc://337), [LC 549](lc://549))
         是"所有根的最优解"？
           是 -> 换根 DP ([LC 2858](lc://2858), #19)
         是"回文路径"？
           是 -> 位掩码 XOR ([LC 2791](lc://2791), #20)
         其他 -> 树 DFS (#14)

是在图上吗？
  是 -> 无权"最短路径"？
           是 -> BFS ([LC 994](lc://994), [LC 1197](lc://1197), #22, #23)
         "连通分量"或"同一组"？
           是 -> Union Find ([LC 547](lc://547), [LC 1697](lc://1697), #3)
         "公交线路数/换乘"？
           是 -> 路线图 BFS ([LC 815](lc://815))

是在网格上吗？
  是 -> "最短距离 / 最近"？
           是 -> BFS ([LC 1020](lc://1020), #22)
         "查找单词 / 路径是否存在"？
           是 -> DFS 回溯 ([LC 79](lc://79))
         "预计算距离"？
           是 -> 网格 DP (#8)
         "生成棋盘"？
           是 -> 随机 + 计数 (#21)

是数组问题吗？
  是 -> "有序 + 搜索/查询"？
           是 -> 二分查找 ([LC 981](lc://981), #1, #4, #15)
         "具有 K 个不同元素的子数组 / 和约束"？
           是 -> 滑动窗口 (#10)
         "下一个更大/更小元素"？
           是 -> 单调栈 (#11)
         "跳跃的最大得分"？
           是 -> DP ([LC 1696](lc://1696), #18)
         "有序 + 变换"？
           是 -> 双指针 ([LC 977](lc://977))
         "分配以最小化成本"？
           是 -> 贪心排序 (#17)
         "合并 K 个有序"？
           是 -> 堆 ([LC 23](lc://23))
         "调度请求"？
           是 -> 堆 (#5)

是"生成所有组合"？
  是 -> 回溯 ([LC 17](lc://17))

是"有可行性检查的最小化/最大化"？
  是 -> 二分答案 (#13, #15)
```

### Quick Pattern Signals（快速模式信号）

| 问题中的信号 | 模式 | 示例 |
|-------------|------|------|
| "最短路径"、"最少步数" | BFS | [LC 994](lc://994), [LC 1197](lc://1197) |
| "连通分量"、"同一组" | Union Find | [LC 547](lc://547), [LC 1697](lc://1697) |
| "BST 中第 k 小/大" | 中序遍历 | [LC 230](lc://230) |
| "树上取或跳" | 树形 DP | [LC 337](lc://337) |
| "所有根最优" | 换根 DP | [LC 2858](lc://2858) |
| "回文路径 + 树" | 位掩码 XOR | [LC 2791](lc://2791) |
| "有序 + 预算/区间查询" | 前缀和 + BS | Custom #1 |
| "能否达到 X？"（单调性） | 二分答案 | Custom #15 |
| "下一个更小/更大" | 单调栈 | Custom #11 |
| "子数组中 K 个不同" | 滑动窗口 | Custom #10 |
| "合并 K 个有序流" | 堆 | [LC 23](lc://23) |
| "分配任务，最小化成本" | 按差值贪心排序 | Custom #17 |
| "设计停车/购物车/追踪器" | OOD | Custom #2, #6, #16 |
| "生成所有组合" | 回溯 | [LC 17](lc://17) |
| "网格中搜索单词" | DFS + 回溯 | [LC 79](lc://79) |', updated_at = datetime('now') WHERE id = 32;

-- doc 35 (Uber BPS Timed Mock Interview Sets): lc=3 leetcode=0 custom=0
UPDATE company_documents SET content = '# Uber BPS -- Timed Mock Interview Problem Sets（限时模拟面试题组）

> 3组限时模拟题，模拟 **BPS (Behavioral + Problem Solving，行为+问题解决)** 面试中45分钟的编程部分。
> 每组：1道 medium（20分钟）+ 1道 medium-hard（20分钟）+ follow-up（5分钟）。
>
> **使用方法**：设定计时器。打开 HackerRank 或空白编辑器。时间结束前不要查看答案。
> 每组完成后，在 `uber_bps_lc_solutions.md` 和 `uber_bps_custom_solutions.md` 中复习解法。
>
> Task: T-P2-248

---

## Set 1: Tree Traversal + Union Find

**考察模式**：**BST (Binary Search Tree，二叉搜索树)** 中序遍历、**UF (Union Find，并查集)** 事件处理

**目标时间**：共45分钟

---

### Problem 1A: Kth Smallest in BST (Medium, 20 min)

**来源**：[LC 230](lc://230) 变体

给定一棵 BST 的根节点和整数 `k`，返回第 k 小的元素。

```
Input: root = [5, 3, 6, 2, 4, null, null, 1], k = 3
Output: 3
```

**要求**：
1. 使用迭代中序遍历实现（不使用递归）。
2. 说明时间和空间复杂度。

**Follow-up A**（面试官提示，+3分钟）：
> "现在找第 k **大**的元素。"

期望：反向中序遍历（right -> node -> left）。复杂度相同。

**Follow-up B**（面试官提示，+2分钟）：
> "如果这棵 BST 频繁修改（插入/删除），且 `kthSmallest` 被频繁调用，如何优化？"

期望：为每个节点增加 `left_count`（左子树大小）。O(H) 查找，无需完整遍历。需讨论权衡：每次插入/删除需要 O(H) 维护计数。

**评分标准**：
- [ ] 干净的迭代中序遍历：2分
- [ ] 在第 k 个元素处正确提前终止：1分
- [ ] 复杂度分析（O(H+k) 时间，O(H) 空间）：1分
- [ ] Follow-up A（反向中序遍历）：1分
- [ ] Follow-up B（增强型 BST）：1分

---

### Problem 1B: Rider Connection Log（骑手连接日志）(Medium-Hard, 20 min)

**来源**：Custom #3

给定带时间戳的骑手交互日志，找到所有骑手最早全部连通（直接或传递）的时间。

```
Input:
  n_riders = 4
  logs = [
    (1, "Alice", "Bob"),       # timestamp 1: Alice shared ride with Bob
    (2, "Charlie", "Dave"),    # timestamp 2: Charlie shared ride with Dave
    (5, "Bob", "Charlie"),     # timestamp 5: Bob shared ride with Charlie
  ]
Output: 5  # At timestamp 5, all 4 riders are in one connected component
```

**要求**：
1. 实现带路径压缩和按秩合并的 Union Find。
2. 按时间顺序处理日志。当 `components == 1` 时返回最早时间戳，若永远不完全连通则返回 `None`。
3. 说明时间和空间复杂度。

**Follow-up**（面试官提示，+5分钟）：
> "现在日志还可以包含''屏蔽''事件：`(7, ''blocked'', ''Alice'', ''Bob'')`。如何处理断开连接？"

期望方案：Union Find 不支持删除操作。改用邻接表 + **BFS (Breadth-First Search，广度优先搜索)** / **DFS (Depth-First Search，深度优先搜索)** 连通性检查。讨论权衡：UF 每次查询 O(alpha(N))，但不支持删除；BFS 重建每次事件 O(V+E)，但支持删除。提到离线逆序处理作为替代方案（如果所有事件已知）。

**评分标准**：
- [ ] 正确的 UnionFind 类（带压缩的 find、按秩合并的 union）：2分
- [ ] 正确的连通分量计数和提前返回：1分
- [ ] 处理骑手名字到 ID 的映射：1分
- [ ] 复杂度分析（O(E * alpha(N)) 时间，O(N) 空间）：1分
- [ ] Follow-up：BFS 重建方案及权衡讨论：2分

---

### Set 1 Debrief Checklist（复盘清单）

完成 Set 1 后回顾：
- [ ] 编码前是否解释了思路？
- [ ] 是否编写并运行了测试用例？
- [ ] 是否对每种方案说明了复杂度？
- [ ] 是否处理了边界情况（空树、k=1、单个骑手）？
- [ ] 总时间：______ / 45分钟

---

## Set 2: Multi-source BFS + Prefix Sum Binary Search

**考察模式**：网格 BFS、**前缀和 (Prefix Sum)** + **BS (Binary Search，二分查找)**

**目标时间**：共45分钟

---

### Problem 2A: Rotting Oranges（腐烂的橘子）(Medium, 20 min)

**来源**：[LC 994](lc://994)

有一个 `m x n` 的网格，每个格子是：
- `0` = 空格
- `1` = 新鲜橘子
- `2` = 腐烂橘子

每分钟，与腐烂橘子相邻（4个方向）的新鲜橘子会变腐烂。返回所有新鲜橘子都腐烂的最少分钟数，如果不可能则返回 `-1`。

```
Input: grid = [[2,1,1],[1,1,0],[0,1,1]]
Output: 4
```

**要求**：
1. 使用多源 BFS（先将所有腐烂橘子入队）。
2. 追踪新鲜橘子计数；BFS 完成后若 fresh > 0 则返回 -1。
3. 说明时间和空间复杂度。

**Follow-up A**（面试官提示，+3分钟）：
> "如果腐烂橘子也能对角线传播（8个方向）呢？"

期望：在方向数组中添加4个对角方向。BFS 逻辑不变。时间仍为 O(mn)。

**Follow-up B**（面试官提示，+2分钟）：
> "如果某些格子是墙（值为3）会阻挡传播呢？"

期望：在 BFS 邻居检查中跳过值为3的格子。复杂度不变。说明：墙可能造成不可达的新鲜橘子，因此 -1 的情况更常见。

**评分标准**：
- [ ] 正确的多源 BFS 初始化：2分
- [ ] 正确的分钟计数（逐层 BFS）：1分
- [ ] 处理 fresh == 0 的边界情况（返回0）：1分
- [ ] 不可达时返回 -1：1分
- [ ] 复杂度分析（O(mn) 时间和空间）：1分

---

### Problem 2B: Purchase Optimization（采购优化）(Medium-Hard, 20 min)

**来源**：Custom #1

给定一个商品 `prices` 列表（可能未排序）和一系列查询 `(start_pos, budget)`，对每个查询找出从索引 `start_pos` 开始、在给定预算内最多能买多少件商品。商品必须按最便宜的顺序购买。

```
Input:
  prices = [10, 5, 20, 15, 3]
  queries = [(0, 25), (2, 40), (0, 100)]
Output: [3, 2, 5]
  # Query 1: sorted = [3,5,10,15,20], from pos 0 with budget 25: buy 3+5+10=18, can''t add 15 -> 3 items
  # Query 2: from pos 2 with budget 40: buy 10+15=25, can''t add 20 -> wait, pos 2 in sorted -> 10,15,20 -> 10+15=25 <= 40, +20=45 > 40 -> 2 items
  # Query 3: from pos 0, budget 100: buy all 5 items (3+5+10+15+20=53 <= 100) -> 5
```

**要求**：
1. 先对价格排序。
2. 构建前缀和数组。
3. 对每个查询，二分查找最大可购买数量。
4. 说明时间和空间复杂度。

**Follow-up**（面试官提示，+5分钟）：
> "如果每件商品有''类别''，且每个类别最多买2件呢？"

期望讨论：前缀和 + 二分查找不再适用，因为约束是按类别而非全局的。需要贪心方法：遍历排序后的价格，维护类别计数，跳过超过类别限制的商品。每次查询时间变为 O(n) 而非 O(log n)。或者，预计算每种类别限制约束下的"过滤前缀和"。

**评分标准**：
- [ ] 正确的排序 + 前缀和构建：1分
- [ ] 正确的二分查找（bisect_right on prefix sum）：2分
- [ ] 处理边界情况（pos 越界、budget 为0）：1分
- [ ] 复杂度分析（O(n log n + q log n) 时间，O(n) 空间）：1分
- [ ] Follow-up：识别 BS 失效，提出贪心替代方案：2分

---

### Set 2 Debrief Checklist（复盘清单）

完成 Set 2 后回顾：
- [ ] 编码前是否确认了约束条件（网格大小、价格范围）？
- [ ] 是否主动用边界情况测试（全部腐烂、无新鲜、空网格）？
- [ ] 前缀和索引是否正确处理（off-by-one）？
- [ ] 选择方案前是否讨论了多种方案？
- [ ] 总时间：______ / 45分钟

---

## Set 3: Graph Components + OOD

**考察模式**：**UF (Union Find，并查集)** / DFS 连通性、**OOD (Object-Oriented Design，面向对象设计)** Strategy 模式

**目标时间**：共45分钟

---

### Problem 3A: Number of Provinces（省份数量）(Medium, 20 min)

**来源**：[LC 547](lc://547)

有 `n` 个城市。`isConnected[i][j] = 1` 表示城市 `i` 和城市 `j` 直接相连。省份是一组直接或间接相连的城市。返回省份数量。

```
Input: isConnected = [[1,1,0],[1,1,0],[0,0,1]]
Output: 2
```

**要求**：
1. 使用 Union Find 或 DFS 实现（选择一种，准备好讨论另一种）。
2. 说明时间和空间复杂度。
3. 用示例输入演示你的解法。

**Follow-up A**（面试官提示，+3分钟）：
> "给定一系列新建的城市间道路，如何高效追踪每条道路建成后的省份数？"

期望：Union Find 非常适合在线连通性问题。初始 n 个分量，每次合并减少1（若未已连通）。每条道路 O(alpha(n))。DFS 每次需要完整重新遍历——效率差很多。

**Follow-up B**（面试官提示，+2分钟）：
> "如果某些道路是单向的（有向），你的方案还有效吗？"

期望：不行。Union Find 假设无向边。对于有向图，需要用 **Tarjan** 或 **Kosaraju** 算法求**SCC (Strongly Connected Components，强连通分量)**。需提到弱连通分量和强连通分量的区别。

**评分标准**：
- [ ] 正确的 UF 或 DFS 实现：2分
- [ ] 正确的省份计数：1分
- [ ] 复杂度分析（O(n^2 * alpha(n)) UF 或 O(n^2) DFS）：1分
- [ ] Follow-up A：在线 UF 优于 DFS：1分
- [ ] Follow-up B：有向图意识（SCC）：1分

---

### Problem 3B: Cart & Pricing Engine（购物车定价引擎）(Medium-Hard, 20 min)

**来源**：Custom #6

设计一个 Uber Eats 购物车系统，需要以下功能：
1. **菜单项**：含基础价格和可选附加项（如"Extra cheese +$1.50"）
2. **高峰加价**：高峰时段的乘数（如1.3倍）
3. **会员折扣**：如 Uber One 享9折
4. **优惠码**：固定金额或百分比折扣
5. **收据生成**：显示逐项明细

**要求**：
1. 设计类结构。画出/描述类之间的关系。
2. 实现核心类：`MenuItem`、`CartItem`、`Cart`，以及至少两条定价规则。
3. 定价规则应以可配置顺序应用（**Strategy Pattern，策略模式**）。
4. 展示一个生成收据的使用示例。

```
Example usage:
  cart = Cart()
  burger = MenuItem("Burger", 12.00, add_ons=[AddOn("Extra cheese", 1.50)])
  cart.add_item(burger, quantity=2)
  cart.add_pricing_rule(SurgePricingRule(1.3))
  cart.add_pricing_rule(MembershipDiscountRule(10))
  print(cart.receipt())

Expected receipt:
  === Receipt ===
  Burger (+ Extra cheese) x2    $27.00
  Subtotal:                     $27.00
  Surge pricing (1.3x):        $35.10
  Uber One discount (-10%):    $31.59
  Total:                        $31.59
```

**Follow-up**（面试官提示，+5分钟）：
> "如何添加一条最大折扣上限为$15的规则？它应该放在定价管道的哪个位置？"

期望：创建 `MaxDiscountCapRule`，比较当前金额与 `(subtotal - max_discount)`，取较大值。应在所有折扣之后**最后**应用。讨论：规则顺序很重要——上限必须是后处理步骤，不能和折扣交错。

**评分标准**：
- [ ] 干净的类设计（MenuItem, CartItem, Cart）：2分
- [ ] 定价规则的 Strategy Pattern（ABC + 具体实现）：2分
- [ ] 正确的带定价明细的收据：1分
- [ ] 可扩展性讨论（添加新规则无需修改 Cart）：1分
- [ ] Follow-up：最大折扣上限及顺序合理性：1分

---

### Set 3 Debrief Checklist（复盘清单）

完成 Set 3 后回顾：
- [ ] Problem 3A 是否讨论了 UF 与 DFS 的权衡？
- [ ] Problem 3B 是否画了类图或描述了类关系？
- [ ] 是否解释了为什么用 Strategy Pattern 而非 if/else 链？
- [ ] 是否用给定示例测试了 OOD 代码？
- [ ] 总时间：______ / 45分钟

---

## Overall Practice Schedule（整体练习计划）

| 日期 | 题组 | 完成后重点复习内容 |
|------|------|--------------------|
| Day 1 | Set 1 | BST 遍历变体、Union Find 模板 |
| Day 2 | Set 2 | BFS 模式、前缀和 + 二分查找 |
| Day 3 | Set 3 | 图连通性、OOD / Strategy Pattern |
| Day 4 | 最弱题组 | 重做得分最低的那组 |

### Scoring Guide（评分指南）

| 分数 | 水平 | 行动 |
|------|------|------|
| 10-12 / 12 每组 | 优秀 | BPS 准备就绪。专注提速。 |
| 7-9 / 12 每组 | 良好 | 复习 follow-up 模式。练习口头表达权衡分析。 |
| 4-6 / 12 每组 | 需提高 | 在 `uber_bps_pattern_cheatsheet.md` 中重新学习该模式，从头重做。 |
| < 4 / 12 每组 | 存在差距 | 用3-5道类似 **LC (LeetCode)** 题目练习该模式后再重试。 |

### Time Management Tips（时间管理技巧）

- **0-2分钟**：明确问题。复述约束条件。询问边界情况。
- **2-5分钟**：讨论2种方案。选择一种。说明复杂度。
- **5-18分钟**：编码。边写边说。在线处理边界情况。
- **18-20分钟**：用给定示例 + 1个边界情况测试。修复 bug。
- **Follow-ups**：大声思考。先说关键洞察，不用写完整代码。

> **黄金法则**：如果实现过程中卡住超过3分钟，退后一步重新审视方案。一个错误算法写得再完美也得0分。一个正确算法有小 bug 仍然得分不错。', updated_at = datetime('now') WHERE id = 35;

-- doc 47 (Pinterest LC Must-Do: Review & Index): lc=18 leetcode=0 custom=7
UPDATE company_documents SET content = '# Pinterest LC Must-Do -- Review & Index

> 14 LeetCode problems from Pinterest prep list. This doc is an **index + pattern review**.
> Each entry links back to the problem''s full solution notes in the problems DB.

## Quick Status

> Click a problem title to open its description + solution notes in a side drawer.

| # | LC | Title | Difficulty | Pattern | Status | Notes |
|---|-----|-------|-----------|---------|--------|-------|
| 1 | 332 | [Reconstruct Itinerary](lc://332) | Hard | Hierholzer (Eulerian Path) | Done | Written |
| 2 | 465 | [Optimal Account Balancing](lc://465) | Hard | Bitmask DP (zero-sum partition) | Done | Written |
| 3 | 815 | [Bus Routes](lc://815) | Hard | BFS on route graph | Done | Written |
| 4 | 322 | [Coin Change](lc://322) | Medium | DP (unbounded knapsack) | Done | Written |
| 5 | 282 | [Expression Add Operators](lc://282) | Hard | Backtracking + `prev` trick | Done | Written |
| 6 | 1055 | [Shortest Way to Form String](lc://1055) | Medium | Greedy / DP | Done | Written |
| 7 | 311 | [Sparse Matrix Multiplication](lc://311) | Medium | Hash-map compression | Done | Written |
| 8 | 2402 | [Meeting Rooms III](lc://2402) | Hard | Two-heap simulation | Done | Written |
| 9 | 1110 | [Delete Nodes And Return Forest](lc://1110) | Medium | DFS + `is_root` flag | Done | Written |
| 10 | 1244 | [Design A Leaderboard](lc://1244) | Medium | Sorted map / heap | Done | Written |
| 11 | 410 | [Split Array Largest Sum](lc://410) | Hard | Binary search on answer / DP | Done | Written |
| 12 | 43 | [Multiply Strings](lc://43) | Medium | Simulation on digit arrays | Done | Written |
| 13 | 642 | [Design Search Autocomplete System](lc://642) | Hard | Trie + heap | Done | Written |
| 14 | 1723 | [Find Minimum Time to Finish All Jobs](lc://1723) | Hard | Binary search + backtracking | Done | Written |

**Progress**: 14/14 done | **Notes written**: 14/14 (全部含中文 + code review)

---

## Pattern Clusters (for review)

Group problems by core technique so similar traps/tricks reinforce each other.

### Cluster A: Graph / Eulerian / BFS
- [**LC 332** Reconstruct Itinerary](lc://332) -- Hierholzer''s algorithm, post-order append + reverse
- [**LC 815** Bus Routes](lc://815) -- BFS on *route* graph (nodes = routes, not stops)
- [**LC 465** Optimal Account Balancing](lc://465) -- partition graph into zero-sum components (bitmask DP)

### Cluster B: Backtracking / DFS with Carried State
- [**LC 282** Expression Add Operators](lc://282) -- `prev` trick for `*` precedence
- [**LC 1110** Delete Nodes And Return Forest](lc://1110) -- `is_root` flag carried down, None returned up
- [**LC 1723** Find Minimum Time to Finish All Jobs](lc://1723) -- backtrack + binary search on answer

### Cluster C: DP on Subsets / Indices
- [**LC 322** Coin Change](lc://322) -- classic unbounded knapsack 1D DP
- [**LC 410** Split Array Largest Sum](lc://410) -- binary search on answer OR DP on (i, k)
- [**LC 1055** Shortest Way to Form String](lc://1055) -- greedy two-pointer per chunk

### Cluster D: Heap / Simulation / Design
- [**LC 2402** Meeting Rooms III](lc://2402) -- two-heap (free + busy) with tuple tiebreak
- [**LC 1244** Design A Leaderboard](lc://1244) -- hash map + on-demand sort (or sorted structure)
- [**LC 642** Design Search Autocomplete](lc://642) -- Trie + heap/top-k
- [**LC 311** Sparse Matrix Multiplication](lc://311) -- hash-map representation

### Cluster E: String / Arithmetic Simulation
- [**LC 43** Multiply Strings](lc://43) -- digit-by-digit simulation, index arithmetic `(i+j)` and `(i+j+1)`

---

## Core Patterns Cheat Sheet

### Hierholzer''s Algorithm ([LC 332](lc://332))
```
build graph, min-heap neighbors (lex order)
dfs(u): while graph[u]: dfs(heappop(graph[u]))
        route.append(u)    # post-order
return route[::-1]
```
Key insight: append **after** all out-edges exhausted. Dead-ends end up at tail of reversed = correct order.

### `prev` Trick for Operator Precedence ([LC 282](lc://282))
```
dfs(i, expr, cur, prev):
  +: new_cur = cur + x,             new_prev = x
  -: new_cur = cur - x,             new_prev = -x
  *: new_cur = cur - prev + prev*x, new_prev = prev*x
```
Invariant: `cur` is current expression value; `prev` is last additive term (signed). Multiplication rewrites last term: "undo prev, apply prev*x."

### `is_root` Flag ([LC 1110](lc://1110))
```
dfs(node, is_root):
  deleted = node.val in to_delete
  if is_root and not deleted: forest.append(node)
  node.left  = dfs(node.left,  deleted)    # child''s is_root = my deleted status
  node.right = dfs(node.right, deleted)
  return None if deleted else node         # parent auto-unlinks
```
Principle: "carry ancestor state DOWN via params, signal unlink UP via return."

### Bitmask DP on Zero-Sum Partitions ([LC 465](lc://465))
```
dp[mask] = max zero-sum subgroups partitioning mask
for mask where subset_sum[mask] == 0:
  enumerate submasks sub (via sub = (sub-1) & mask)
  if subset_sum[sub] == 0 and dp[mask^sub] >= 0:
    dp[mask] = max(dp[mask], 1 + dp[mask^sub])
answer = n - dp[(1<<n) - 1]
```
**Critical**: use `(sub-1) & mask` for O(3^n), NOT `range(mask+1)` which is O(4^n).

### Two-Heap Resource Simulation ([LC 2402](lc://2402))
```
free = min-heap of room IDs
busy = min-heap of (end_time, room_id)
for meeting (start, end):
  release: while busy and busy[0][0] <= start: move to free
  assign:  if free: pop; else: delay via busy
```
Tiebreak via tuple `(end, room_id)` -- automatic.

---

## Common Traps Across the Set

1. **Leading zeros in string numbers** ([LC 43](lc://43), 282): `break` not `continue` once `s[0]==''0''` with `len > 1`.
2. **Submask enumeration** ([LC 465](lc://465), 698, 473): `sub = (sub-1) & mask` for O(3^n); `range(mask+1)` is O(4^n) but often still AC due to guards.
3. **Heap tuple tiebreak** ([LC 2402](lc://2402), 1882, 1834): `(end, room)` gives "earliest end, then lowest ID" automatically.
4. **Post-order vs carry-down state** ([LC 1110](lc://1110) vs [LC 332](lc://332)): choose based on "does decision depend on ancestors or descendants?"
5. **Eval in expression problems** ([LC 282](lc://282)): never use `eval()` in interviews; use `prev` trick.

---

## Daily Review Template

Pick 1-2 problems, spend 20 min each:
1. **Re-solve from scratch** (no notes) -- this surfaces what you actually remember.
2. **Compare to notes** -- any delta is a learning signal.
3. **State the pattern in one sentence** -- forces compression.
4. **Identify 2 related problems** -- tests transfer.

If stuck >10 min, read notes and mark for re-review tomorrow.

---

## Links

- Full problem notes: accessible via `/problems/<id>` in this UI; content is in `problems.notes` column.
- Recruiter call prep: [Pinterest Senior MLE -- Recruiter Call Prep](./docs) (separate doc id=39).
- Source: user-provided 2026-04-12 via Discord.

---

## Pinterest Expansion (2025-11 Dump) -- New LC Set

Additional LC problems surfaced from the Pinterest 2025-11 Discord dump.
These are *not* part of the original 14-problem must-do list but appeared in
recent onsite reports; each is tagged `Pinterest` in the problems DB.

| # | LC | Title | Difficulty | Pattern | Notes |
|---|-----|-------|-----------|---------|-------|
| 1 | 84   | [Largest Rectangle in Histogram](lc://84)    | Hard   | Monotonic stack            | Foundation for skyline/histogram-style problems |
| 2 | 392  | [Is Subsequence](lc://392)                   | Easy   | Two-pointer                | Warmup; often asked as lead-in before [LC 1055](lc://1055) |
| 3 | 1526 | [Minimum Number of Increments on Subarrays](lc://1526) | Hard   | Greedy on diffs            | One-pass: sum of positive first-diffs |
| 4 | 1564 | [Put Boxes Into Warehouse I](lc://1564)      | Medium | Greedy + prefix-min        | Sort boxes desc; scan warehouse |
| 5 | 1580 | [Put Boxes Into Warehouse II](lc://1580)     | Hard   | Two-pointer from both ends | Generalizes 1564 (warehouse has no height monotonicity) |
| 6 | 3229 | [Min Operations to Make Array Equal to Target](lc://3229) | Hard   | Greedy on diffs (signed)   | Variant of 1526; handles sign changes |
| 7 | 1851 | [Minimum Interval to Include Each Query](lc://1851) | Hard   | Offline sort + min-heap    | Best match for reported 「寻找餐馆区间」; see [investigation note](./pinterest/lc_investigation_restaurant_intervals.md) |

**Cluster F: Monotonic Stack / Histogram** -- [LC 84](lc://84)

**Cluster G: Greedy on Differences** -- [LC 1526](lc://1526), [LC 3229](lc://3229)

**Cluster H: Warehouse / Box Packing (Greedy)** -- [LC 1564](lc://1564), [LC 1580](lc://1580)

**Cluster I: Interval Queries (Offline Sort + Heap)** -- [LC 1851](lc://1851)

---

## Custom Coding Problems (Pinterest-Specific)

Problems reported onsite without a direct LeetCode equivalent. Full write-ups
live under `problems.notes` in the problems DB; search by title.

| # | Title | Core Pattern | Notes |
|---|-------|--------------|-------|
| 1 | [Escape Room Game State (rooms + people)](db://1068) | BFS / state machine | Multi-actor graph traversal |
| 2 | [Lighthouse 2D Light Propagation (beam + mirrors + splitters)](db://1071) | Grid simulation + recursion | Branching on splitters; cycle detection |
| 3 | [Prefix-Match First-Word-Index (sorted dictionary)](db://1072) | Binary search / Trie | `bisect_left` on sorted dict is the clean O(log n) |
| 4 | [Grant Access / Permission Propagation on a DAG](db://1075) | BFS/DFS on DAG | Topological traversal; avoid re-visit |
| 5 | [Pin Connectivity on a Pinterest Relationship Graph](db://1076) | Union-Find | Component queries over streaming edges |
| 6 | [round() from scratch (string input, no float)](db://1073) | String/digit arithmetic | No `float()`; handle banker''s vs half-up explicitly |
| 7 | [round by precision p (string s, precision p)](db://1074) | String/digit arithmetic | Generalizes #6; align to p-th digit before rounding |
| 8 | [LC 332 -- Loop follow-up](lc://332) addendum | Graph + loop detection | Variant: detect if itinerary must revisit a ticket |

---

## System Design (SD) Modules

Each Pinterest-flavored SD write-up lives in `docs/pinterest/`. These are
multi-section documents with: problem framing, metrics, data/feature, model
architecture, training, serving, online eval, failure modes.

| # | Topic | File | Linked LC / Custom |
|---|-------|------|--------------------|
| 1 | Ad CTR Prediction                        | [system_design_ad_ctr.md](./pinterest/system_design_ad_ctr.md)                   | -- |
| 2 | User & Item Embeddings                    | [system_design_embeddings.md](./pinterest/system_design_embeddings.md)           | -- |
| 3 | Personalized Chat Bot Recommending Pins   | [system_design_chatbot_pins.md](./pinterest/system_design_chatbot_pins.md)       | -- |
| 4 | Pin Ranking                               | [system_design_pin_ranking.md](./pinterest/system_design_pin_ranking.md)         | [LC 1244 Leaderboard](lc://1244) (score-store analog) |
| 5 | Pins Search                               | [system_design_pins_search.md](./pinterest/system_design_pins_search.md)         | [LC 642 Autocomplete](lc://642), [LC 392 Is Subsequence](lc://392) |
| 6 | Notification Recommendation               | [system_design_notification_reco.md](./pinterest/system_design_notification_reco.md) | -- |
| 7 | Catalog Bulk Update                       | [system_design_catalog_bulk_update.md](./pinterest/system_design_catalog_bulk_update.md) | [LC 1526/3229 (batch-diff updates)](lc://1526) |

---

## BQ (Behavioral)

- **Pinterest BQ Question Map (2025-11)**: [bq_question_map.md](./pinterest/bq_question_map.md) -- maps the 5 reported BQ prompts to 2-3 best-fit EX-XX stories each with 1-sentence angles.

---

## LC <-> SD Cross-Links

Quick lookup: when a SD interview trends toward algorithm-style sub-questions,
these LC problems are the closest patterns.

| SD Module | Most Relevant LC / Pattern |
|-----------|----------------------------|
| Pin Ranking / Leaderboard      | [LC 1244 Design A Leaderboard](lc://1244), [LC 2402 Meeting Rooms III](lc://2402) (heap tiebreak) |
| Pins Search / Autocomplete     | [LC 642 Autocomplete](lc://642), [LC 1055 Shortest Way to Form String](lc://1055), [LC 392 Is Subsequence](lc://392) |
| Embeddings / Retrieval         | [LC 311 Sparse Matrix Multiplication](lc://311) (approx kNN warmup) |
| Catalog Bulk Update            | [LC 1526](lc://1526), [LC 3229](lc://3229) (diff-based minimum ops) |
| Ad CTR                         | [LC 322 Coin Change](lc://322) (budget DP analog for pacing) |
| Chat Bot Pins Reco             | [LC 282 Expression Add Operators](lc://282) (prompt-parse style backtrack) |
| Warehouse / Inventory Layout   | [LC 1564](lc://1564), [LC 1580](lc://1580) |

---

*Last enriched: 2026-04-13 (T-P2-413).*
', updated_at = datetime('now') WHERE id = 47;

COMMIT;
