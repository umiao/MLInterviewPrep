# Uber Virtual Onsite (VO) 完整准备指南

## 一、VO概览

| Round | 类型 | 时长 | 评估重点 |
|-------|------|------|----------|
| 1 | Coding: Algorithms & Data Structures | 60 min | 通用算法，Big-O分析，代码质量，可测试性 |
| 2 | Coding: Depth in Specialization (ML) | 60 min | ML方向深度coding，模拟实际工作场景 |
| 3 | Design & Architecture (New Problem) | 60 min | 从零构建大规模系统，trade-off分析 |
| 4 | Behavioral: Collaboration & Leadership | 60 min | 协作/信任/多元视角/conviction |

---

## 二、通用面试技巧 (适用所有轮次)

### 核心原则：Think Out Loud

> "Our engineers are evaluating not only your technical abilities but also how you approach problems."

- [ ] **主动clarify** -- 问题故意underspecified，面试官在考察你能否identify gaps并提问
- [ ] **先说思路再写代码** -- 描述你打算如何tackle每个部分
- [ ] **不要silent coding** -- 始终让面试官知道你在想什么
- [ ] **假设要验证** -- 如果需要assume，先和面试官确认
- [ ] **听hints** -- 面试官可能在引导你，不要错过提示
- [ ] **Brute force可以起步** -- 但必须说明你知道这不是最优解，然后优化
- [ ] **寻找多种解法** -- 先想几种方案，比较后选最佳

### 面试官评估视角

面试官在看:
1. 是否认真听题并理解？
2. 是否在开始前问了正确的clarifying questions？(**非常重要**)
3. 是否灵活、有创造力、愿意尝试新方法？
4. 能否从简单问题上升到更复杂的问题解决？
5. 代码是否可以被debug和测试？

---

## 三、Round 1: Algorithms & Data Structures

### 考察范围
- [ ] **Big-O分析** -- 时间和空间复杂度分析
- [ ] **排序与哈希** -- 常见排序算法、hash table应用
- [ ] **大数据处理** -- 处理大量数据的优雅高效方案
- [ ] **问题分解** -- 将大问题拆解为可管理的子问题
- [ ] **代码质量** -- idiomatic code，正确使用数据结构
- [ ] **可测试性** -- 代码可debug，能识别需要测试的场景

### CS基础复习清单
- [ ] Arrays, Linked Lists, Stacks, Queues
- [ ] Hash Tables, Hash Maps
- [ ] Trees (BST, Trie, Heap)
- [ ] Graphs (BFS, DFS, Topological Sort)
- [ ] Dynamic Programming
- [ ] Sliding Window, Two Pointers
- [ ] Binary Search及其变种
- [ ] Greedy Algorithms
- [ ] Union Find

### 关联资源
- **Pattern Cheat Sheet by Algorithm** (已有doc)
- **LeetCode Solutions Guide** (已有doc)
- **Custom Problem Solutions** (已有doc)
- **Timed Mock Interview Sets** (已有doc)
- [Uber LeetCode题目列表 (Reddit)](https://www.reddit.com/r/leetcode/comments/13842cs/list_of_questions_uber/) -- **必须全部完成**

---

## 四、Round 2: Coding Depth in ML

### 考察范围
> "This interview assesses depth in your chosen area of specialization via writing code that solves a problem that would be similar to what you would do in the job."

- [ ] **ML算法从零实现** -- 不依赖sklearn，手写核心算法
- [ ] **数据处理pipeline** -- feature engineering, data cleaning
- [ ] **模型评估** -- metrics选择、cross-validation、overfitting诊断
- [ ] **Optimization** -- gradient descent变种、learning rate调度
- [ ] **实际场景问题** -- 推荐系统、ranking、分类、回归等Uber场景

### ML Coding准备清单
- [ ] Linear Regression (from scratch)
- [ ] Logistic Regression (from scratch)
- [ ] Decision Tree / Random Forest逻辑
- [ ] KNN实现
- [ ] K-Means Clustering
- [ ] Gradient Descent (SGD, Mini-batch)
- [ ] Cross-Validation实现
- [ ] Feature Selection / Importance
- [ ] Precision/Recall/F1/AUC计算
- [ ] Bias-Variance Tradeoff理解

### 关联资源
- **ML Fundamentals From-Scratch 完整指南** (已有doc, 8大主题)
- **KNN & ML Fundamentals Review** (已有doc)

---

## 五、Round 3: Design & Architecture (New Problem)

### HR文件关键要求

> "System design assesses a candidate's ability to combine knowledge, theory, experience, and judgment toward solving a real-world engineering problem with significant ambiguity."

### 核心框架 (STEP 1-2-3-4)

**Step 1: Clarify & Scope (5-10 min)**
- [ ] 问题故意underspecified -- 你需要probe找到问题边界
- [ ] 确认functional requirements
- [ ] 确认non-functional requirements (scale, latency, availability)
- [ ] 明确read/write比例、QPS估算

**Step 2: High-Level Design (15-20 min)**
- [ ] 画出核心components和数据流
- [ ] 识别关键services和它们的职责
- [ ] Database选型和schema设计(**不要说"用标准数据库查"**)
- [ ] API设计

**Step 3: Deep Dive (20-25 min)**
- [ ] 选择1-2个关键component深入讨论
- [ ] 数据分区/sharding策略
- [ ] Caching策略
- [ ] 一致性 vs 可用性的trade-off

**Step 4: Failure & Scale (5-10 min)**
- [ ] **Failure Recovery** -- Uber大规模场景下故障频繁，如何检测和防御？
- [ ] 单点故障消除
- [ ] 监控和alerting

### 关键提醒

> **"We are interested in seeing that you know the implications of the various tradeoffs you make -- we want to see a coherent design rather than evaluating what specific tradeoff is 'correct.'"**

- **不要说用现成产品** -- "use a standard database and do queries" 不是他们想听的
- **重点是trade-off awareness** -- 解释为什么选A而不是B，implications是什么
- **从零构建** -- 展示你理解底层原理

### System Design常见主题
- [ ] URL Shortener
- [ ] Ride-sharing system (Uber核心!)
- [ ] Real-time location tracking
- [ ] Notification system
- [ ] Rate limiter
- [ ] Search autocomplete
- [ ] News feed / Timeline
- [ ] Chat system
- [ ] Distributed cache

### 关联资源
- **Design & Architecture Prep** (已有doc)
- [System Design Interview - GitHub](https://github.com/checkcheckzz/system-design-interview)
- [Uber Engineering Blog](https://www.uber.com/blog/engineering/) -- **TODO: follow并学习**

---

## 六、Round 4: Behavioral (Collaboration & Leadership)

### Uber考察的3个核心维度

**1. 信任与协作 (Trust & Collaboration)**
> "Build and sustain trusting, collaborative, and strategic relationships within and across teams or orgs, working with integrity."

- [ ] 准备故事: 跨团队合作达成共同目标
- [ ] 准备故事: 建立信任的具体行为
- 推荐BQ: BLOG-01 (Brand Recall协作), BLOG-03 (跨组边界防御), EX-06 (平台化200M+)

**2. 尊重与多元视角 (Respect & Diverse Perspectives)**
> "Treat others with respect, embrace diverse perspectives and encourage cooperation at all levels, leading by example."

- [ ] 准备故事: 接受不同意见并从中学习
- [ ] 准备故事: 以身作则带领团队
- 推荐BQ: EX-17 (senior IC反馈), EX-13 (署名争议), BLOG-02 (Code Review标准)

**3. Conviction与执行 (Conviction & Commitment)**
> "As a leader having conviction is expected and healthy debates encouraged; when an outcome has been decided they embrace the decision 100%."

- [ ] 准备故事: 坚持己见并推动变革
- [ ] 准备故事: 决定后全力执行(disagree and commit)
- 推荐BQ: BLOG-04 (目标追踪改革), EX-01 (intent collapse发现), EX-02 (主动转team)

### STAR方法提醒
- **S**ituation: 简洁设定背景(2-3句)
- **T**ask: 你的具体角色和目标
- **A**ction: 你做了什么(重点!)，不是团队做了什么
- **R**esult: 量化结果 + 长期影响

### Behavioral准备清单
- [ ] 每个维度至少准备2个故事
- [ ] 每个故事控制在2-3分钟
- [ ] 练习用英文流畅讲述
- [ ] 准备follow-up问题的回答
- [ ] 确保故事展示你的个人贡献(不是团队的)

---

## 七、重要链接汇总

| 资源 | 说明 | 优先级 |
|------|------|--------|
| [Uber ML/AI Interview Guide](https://www.uber.com/us/en/careers/ml-ai-interview-guide/) | 官方面试指南 | **必读** |
| [Reddit Uber LeetCode List](https://www.reddit.com/r/leetcode/comments/13842cs/list_of_questions_uber/) | 历年Uber算法题 | **必做** |
| [System Design Interview - GitHub](https://github.com/checkcheckzz/system-design-interview) | 系统设计资源集 | 推荐 |
| [Interviewing.io](https://interviewing.io/) | Mock interview平台 | 推荐 |
| [Uber Engineering Blog](https://www.uber.com/blog/engineering/) | 了解Uber技术栈 | 推荐 |

---

## 八、VO总体Checklist

### 面试前
- [ ] 确认面试schedule (4轮的具体时间和顺序)
- [ ] 测试Zoom连接和设备
- [ ] 准备好IDE/编辑器环境
- [ ] 复习所有prep documents
- [ ] Reddit Uber LeetCode list全部完成
- [ ] 至少做2次完整mock interview

### 每轮面试中
- [ ] 先clarify再动手
- [ ] Think out loud
- [ ] 管理时间(不要卡在一个点上太久)
- [ ] 如果卡住就说出来，请求hint

### 面试后
- [ ] 记录每轮的题目和表现
- [ ] 总结可以改进的地方
