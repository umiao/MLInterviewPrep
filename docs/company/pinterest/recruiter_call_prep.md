# Pinterest Senior ML Engineer -- 面试准备笔记

> **2026-04-08 Recruiter Call 总结**
>
> 与 Pinterest recruiter David 通话完毕，面试结构及准备要点整理如下。

---

## 基本信息

- **职级**: Senior Level
- **薪资**: ~$500K/年 TC
- **招聘模式**: 统招，HC 有限（目前约 5 个）
- **注意**: 需要 Team Match，HC 竞争激烈

---

## 面试结构总览

### Phone Screen (60 分钟)

| 环节 | 内容 | 时间分配（预估） |
|------|------|----------------|
| Intro & ML Project Discussion | 自我介绍 + 深入讨论一个 ML 项目 | ~10-15 min |
| ML Fundamentals | 3 道随机 ML 基础问题 | ~15-20 min |
| Coding Challenge | 1 道编程题（LeetCode 风格） | ~25-30 min |

### Virtual Onsite (5 轮，各 60 分钟)

| 轮次 | 类型 | 重点 |
|------|------|------|
| 1 | LeetCode Coding | 数据结构 & 算法 |
| 2 | LeetCode Coding | 数据结构 & 算法 |
| 3 | ML Deep Dive | ML 理论 & 实践 |
| 4 | ML System Modeling | ML 系统设计 |
| 5 | Behavioral Questions (BQ) | 行为面试 |

---

## 面试环境

- 视频: **Google Meet**
- 编码: **CoderPad**（无编译器，语法不用 100% 精确）
- 推荐语言: **Python / Java / C++**（面试官最熟悉这三种）
- 需要: 稳定网络 + 电脑

---

## Phone Screen 准备要点

### 1. ML Project Discussion（开场）

- 准备 **一个你最熟悉的 ML 项目**，能深入细节讨论
- 要点覆盖:
  - 项目背景 & 业务目标
  - ML 方法选择及原因
  - 你的具体贡献和角色
  - 数据处理、特征工程
  - 模型训练、评估指标
  - 上线部署 & 效果
  - 遇到的挑战 & 如何解决

### 2. ML Fundamentals (3 道随机题)

重点复习领域（来自官方 Prep Guide）:
- **Logistic Regression** -- 原理、损失函数、梯度
- **Variance / Bias Tradeoff** -- 欠拟合 vs 过拟合
- **Regularization** -- L1 vs L2，为什么有效，如何选择
- **Decision Trees** -- 分裂标准、剪枝、ensemble 方法（RF, GBDT, XGBoost）
- **Convex Functions** -- 为什么凸优化重要，非凸怎么办
- **Model Evaluation** -- precision/recall/F1, AUC-ROC, cross-validation

### 3. Coding Challenge

- 难度: **LeetCode Medium ~ Hard**
- 可能有 **follow-up 问题**、新增需求、edge cases

---

## Coding 面试方法论 (CTCI 7 步法)

### Gayle Laakmann McDowell 的解题框架

```
1. Listen    -> 仔细听题，所有信息都有用
2. Example   -> 用例子理解题目，避免特殊 case
3. Brute Force -> 先说暴力解法 + 复杂度，不急着写代码
4. Optimize  -> 用 BUD 优化或其他策略
5. Walk Through -> 确认最优解的每个细节
6. Implement -> 写干净、模块化的代码
7. Test      -> 分层测试: 概念 -> 特殊代码 -> 热点 -> 小 case -> 边界
```

### BUD 优化法

- **B**ottlenecks -- 找到时间瓶颈
- **U**nnecessary Work -- 去掉多余计算
- **D**uplicated Work -- 消除重复计算

### 5 种优化思路

1. **BUD** -- 瓶颈、多余、重复
2. **DIY** -- 手动做一遍，逆向工程思路
3. **Simplify & Generalize** -- 先解简化版
4. **Base Case & Build** -- 从 base case 递推
5. **Data Structure Brainstorm** -- 尝试不同数据结构

### Best Conceivable Runtime (BCR)

- 理论下界，比如两个集合求交集不可能低于 O(|A|+|B|)
- 如果你的解已经达到 BCR，就不需要再优化了

### 绝对不要做的事

- 忽略题目给的信息（信息都是有用的）
- 纯在脑子里想，不用例子
- 迷糊的时候硬写代码（停下来想清楚）
- 没得到面试官认可就开始写代码

---

## Coding 面试核心 Checklist

来自 David (Recruiter) 的建议:

- [ ] **问清楚需求** -- 不要假设，主动问 clarifying questions
- [ ] **合适的数据结构 & 算法** -- 能说明选择理由
- [ ] **时间空间复杂度** -- 每个解法都要能分析
- [ ] **不纠结语法** -- CoderPad 没有编译器
- [ ] **争取最优解** -- 从暴力开始逐步优化
- [ ] **处理 corner/edge cases** -- 空输入、越界、重复等
- [ ] **防御性编码** -- 错误检查、无效输入处理、异常抛出
- [ ] **验证代码** -- 用测试用例 walk through，找 bug
- [ ] **Think out loud** -- 全程解释逻辑，接受面试官 hint
- [ ] **准备 follow-up** -- 新需求、edge case 变体、优化要求

---

## 准备清单

### 需要立即行动

- [ ] 回复 David: 提供 **3+ 个可用时间段**（周一至周五，10AM-5PM PST）
- [ ] 发送 **最新简历** 给 David（面试官会提前看）
- [ ] 准备好 **一个 ML 项目** 的深度讨论

### 准备计划

- [ ] 复习 ML Fundamentals（Logistic Regression, Regularization, Decision Trees, Bias-Variance, Convex Optimization, Model Evaluation）
- [ ] LeetCode 刷题（Medium-Hard），每题 45-60 分钟计时
- [ ] 练习 CTCI 7 步法，形成肌肉记忆
- [ ] 熟悉 CoderPad 环境
- [ ] 浏览 Pinterest Engineering Blog，了解他们的 ML 系统和产品
- [ ] 阅读 Patrick Halina's Blog 面试技巧
- [ ] 准备 BQ 故事（VO 阶段用）

---

## 推荐准备资源

### 刷题平台

- LeetCode: https://leetcode.com/ (Medium to Hard)
- HackerEarth: https://www.hackerearth.com/
- CareerCup: https://www.careercup.com/
- GeeksforGeeks: https://www.geeksforgeeks.org/
- TopCoder: https://www.topcoder.com/

### Pinterest 相关

- Pinterest Engineering Blog: https://medium.com/pinterest-engineering
- Pinterest Publications: https://labs.pinterest.com/publications
- Pinterest Open Source (GitHub): https://github.com/pinterest
- Pinterest Tech Stack: https://stackshare.io/pinterest/pinterest
- Pinterest Careers & Life: https://www.pinterestcareers.com/
- PinFlex (混合办公): https://www.pinterestcareers.com/pinflex/
- Patrick Halina's Blog: https://www.patrickhalina.com/ (Pinterest ML Manager 的面试技巧)

---

## 关于 Pinterest

**Mission**: Bring everyone the inspiration to create a life they love

**Core Values**:
- Put Pinners First
- Aim for Extraordinary
- Create Belonging
- Act as One
- Win or Learn

---

## Pinterest LC 必刷题列表 (14 题)

| # | LC | Title | Difficulty | Status |
|---|-----|-------|-----------|--------|
| 1 | 332 | Reconstruct Itinerary | Hard | TODO |
| 2 | 465 | Optimal Account Balancing | Hard | Done |
| 3 | 815 | Bus Routes | Hard | Done |
| 4 | 322 | Coin Change | Medium | Done |
| 5 | 282 | Expression Add Operators | Hard | TODO |
| 6 | 1055 | Shortest Way to Form String | Medium | Done |
| 7 | 311 | Sparse Matrix Multiplication | Medium | Done |
| 8 | 2402 | Meeting Rooms III | Hard | TODO |
| 9 | 1110 | Delete Nodes And Return Forest | Medium | TODO |
| 10 | 1244 | Design A Leaderboard | Medium | Done |
| 11 | 410 | Split Array Largest Sum | Hard | TODO |
| 12 | 43 | Multiply Strings | Medium | TODO |
| 13 | 642 | Design Search Autocomplete System | Hard | TODO |
| 14 | 1723 | Find Minimum Time to Finish All Jobs | Hard | TODO |

**Progress**: 6/14 completed | **TODO**: 8 remaining (5 Hard, 3 Medium)

---

## 与现有准备材料的交叉引用

| 方向 | 已有材料 |
|------|---------|
| ML 基础 | Pillar 2 (ML Fundamentals & Theory) -- 192 个 framework nodes |
| ML System Design | 28 个 system design 模块 |
| 行为面试/STAR | 数据库中 29 个打磨好的行为面试案例, `docs/bq_improved_stories.md` |
| Coding | 数据库中 1058 道题目, Blind 75 解答 |
| ML Project Deep Dive | Ranking-as-Allocation, LLM Eval Pipeline, Search Diversity |
