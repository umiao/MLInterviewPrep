# Google SWE III (AI/ML) -- 面试准备笔记

> **2026-04-08 Recruiter Call 总结**
>
> 与 Google recruiter 通话完毕，面试结构已确认，关键要点整理如下。

---

## 面试结构

### 第一轮 | 虚拟面试 (~2 小时)

| 类型 | 时长 | 重点 |
|------|------|------|
| ML Domain Interview | 45 min | ML paradigm、模型迭代经验、数据分析与处理、ML+产品洞察 |
| Googleyness & Leadership (G&L) | 45 min | 行为面试、领导力、跨团队影响力、用户优先思维 |

### 第二轮 | 现场 Onsite (~1.5 小时)

| 类型 | 时长 | 重点 |
|------|------|------|
| CS Fundamentals / Coding / DS&A (x2) | 各 45 min | 数据结构、算法、编码能力 |

> 注意: Coding 轮直接移到 physical onsite，跳过虚拟 coding 环节。

---

## Recruiter Call 关键要点

### ML Domain Interview -- 考察方向

1. **ML Paradigm 与迭代经验**
   - 展示实际迭代 ML 模型的经验
   - 说明何时以及为何切换 paradigm（如 pointwise -> pairwise -> listwise）
   - 讨论真实的模型迭代周期案例

2. **数据分析与处理**
   - 如何处理数据质量、特征工程、数据管道设计
   - 展示对数据分布、偏差、采样问题的理解

3. **ML + 产品洞察**
   - "现有的 ranking 系统可能有什么问题？你会如何改进？"
   - 思考 objective function 的局限性（如 proxy metric != 真实用户价值）
   - 参考: 我的 Ranking-as-Allocation 工作（多目标优化与曝光分配）
   - 参考: NDCG proxy challenge 故事 (BLOG-01 behavioral example)

4. **Modeling 基础知识**
   - 基础: loss functions、regularization、evaluation metrics、bias-variance tradeoff
   - 准备好 ML system design 相关问题

### Googleyness & Leadership -- 考察方向

1. **影响多个团队的 Leadership**
   - 工作影响力超出直属团队的故事
   - 跨职能协作案例
   - 参考 BQ 故事: Module Proliferation Escalation、Search Diversity Intent Collapse

2. **用户优先 (User-First) 思维**
   - 产品思维: 这如何改善用户体验？
   - 展示用户同理心和以用户为中心的决策

3. **Googleyness 特质**
   - 做正确的事、适应模糊性、协作精神、智识谦逊
   - 享受乐趣、尊重地 push back、关心团队

---

## 面试环境与工具

- 虚拟面试通过 **Google Meet** 进行
- 编码使用 **VIP (Virtual Interview Platform)** -- 实时协作白板，支持语法高亮
- **没有 IDE 或编译器** -- 代码需要逻辑上能编译通过
- Systems Design 可能用到 **Google Drawings** 画图
- 现场面试提供 Chromebook 和/或白板
- 建议使用耳机/免提设备，方便边说边写

---

## 面试核心原则

1. **Think out loud** -- 说出思考过程，展示解题思路
2. **确认假设** -- 对问题有任何假设，主动和面试官沟通确认
3. **接受提示** -- 面试官给 hint 是在帮你，积极调整方向
4. **写真实代码** -- 不要伪代码，代码应该能在编译器中运行
5. **简历全覆盖** -- 技术和非技术面试官都可能问简历上任何内容

---

## 准备清单

### ML Domain 准备

- [ ] 复习 ML 基础: loss functions、regularization、bias-variance、evaluation metrics
- [ ] 准备 2-3 个 ML 迭代故事（用数据驱动的模型改进周期）
- [ ] 准备"现有 ranking 有什么问题"分析（objective limitation、多目标 tradeoff）
- [ ] 复习 system design 模块: ranking-as-allocation、LLM orchestration、PBE pipeline
- [ ] 练习 ML system design: 特征工程、模型选择、online/offline evaluation
- [ ] 复习数据处理 pattern: 缺失数据处理、feature drift、数据质量

### G&L 准备

- [ ] 准备 Top 20 行为面试问题，每题 3 个不同的 STAR 回答
- [ ] 准备跨团队 leadership 故事:
  - Module Proliferation -> VP Escalation（跨组织影响）
  - Search Diversity -> Intent Collapse Discovery（改变研究员与工程师的协作方式）
  - LLM Eval Pipeline -> 全组织采用（影响评估标准）
- [ ] 准备 user-first 故事:
  - Seller Risk Modeling Fairness（用户保护的伦理决策）
  - Ranking-as-Allocation（平衡买家/卖家曝光）
- [ ] 了解 Google 文化和价值观（Googleyness 维度）

### Coding 准备

- [ ] 限时练习: 每题 45 分钟
- [ ] 重点方向: 数据结构、算法、复杂度分析、边界条件
- [ ] 复习 Blind 75 + 额外 medium/hard 题目
- [ ] 在纯文本编辑器中练习（没有 IDE 自动补全）

### 通用准备

- [ ] 观看 L4 SWE Expectations 视频
- [ ] 观看 Example Coding Interview 视频
- [ ] 阅读 Interview Prep Guide (careers.google.com)
- [ ] 通读简历 -- 准备每段经历的 deep dive
- [ ] 练习自我介绍 (60-90 秒)

---

## 自我介绍草稿 (60-90 秒)

I'm a Machine Learning Engineer at eBay on the Search Science, Ranking & Monetization team, where I've spent the past three years building large-scale ranking and relevance systems serving millions of queries daily.

One highlight is designing eBay's Ranking-as-Allocation framework that reframes search ranking as a resource allocation problem -- enabling precise multi-objective control over exposure, conversion, and risk at site scale. I also built an end-to-end LLM-based evaluation pipeline that achieved human-comparable agreement while reducing cost by 94% and latency by 90%, now adopted org-wide for Search & Ads experiments.

I'm now looking for my next challenge in AI/ML at Google, where I can apply my experience in ranking optimization, ML system design, and LLM applications to products at even greater scale. Google's focus on ML-driven product intelligence and the opportunity to work across teams on foundational ML infrastructure is exactly the kind of impact I want to make.

---

## 面试流程时间线

| 阶段 | 预计时间 |
|------|---------|
| 第一轮虚拟面试 (ML Domain + G&L) | ~2 小时 |
| 第二轮现场面试 (Coding x2) | ~1.5 小时 |
| 面试反馈收集 | 7-10 个工作日 |
| 最终审批与初始 Offer | 时间不定 |
| **总计（面试到 Offer）** | **约 4-6 周** |

---

## 推荐准备资源

### 阅读材料
- Google Testing Blog: https://testing.googleblog.com/
- Tech Dev Guide: https://techdevguide.withgoogle.com/
- Interview Prep Guide: https://careers.google.com/how-we-hire/interview/

### 视频资源
- How We Hire: https://www.youtube.com/watch?v=k-baHBzWe4k
- Prepare for Coding Interview: https://www.youtube.com/watch?v=6ZZX9iIgFoo
- Example Coding Interview: https://www.youtube.com/watch?v=XKu_SEDAykw
- Interview Tips from SWEs: https://www.youtube.com/watch?v=XOtrOSatBoY
- Life at Google Interviews: https://www.youtube.com/playlist?list=PLllx_3tLoo4c_aR8RKOOnizL5LiUH02YF

---

## 与现有准备材料的交叉引用

| 方向 | 已有材料 |
|------|---------|
| ML 基础 | Pillar 2 (ML Fundamentals & Theory) -- 192 个 framework nodes |
| ML System Design | 28 个 system design 模块 (ranking-as-allocation、LLM orchestration 等) |
| 行为面试/STAR | 数据库中 29 个打磨好的行为面试案例, `docs/bq_improved_stories.md` |
| Coding | 数据库中 1058 道题目, Blind 75 解答 |
| Leadership 故事 | BLOG-01 (两部分: Influence + Deep Dive)、Module Proliferation、Search Diversity |
