# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""
Translate company_documents id=4 (DoorDash Project Deep Dive) to Chinese.
Following chinese_conversion_spec.md rules.
"""

import io
import re
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = "data/mle_prep.db"

CHINESE_CONTENT = r"""# DoorDash Round 1 -- 项目深度剖析准备材料

> **项目**: Diversity / Intent-Aware Ranking（多样性/意图感知排序）
> **角色**: Tech Lead / 发起人
> **目标级别**: L6 Staff
> **面试形式**: 45分钟深度剖析 + Q&A

---

## 1. Problem Statement（~5分钟）

### Target Users
- **买家**：在大型电商平台上搜索宽泛、多意图查询词（如"pokemon"、"calvin klein"）的用户
- **卖家**：长尾意图细分领域中被 base ranker 系统性低曝光的商家

### Core Insight
**LTR (Learning to Rank，学习排序)** 排序模型**系统性地将多意图查询折叠到主导意图**。`pokemon` → 几乎全部是 TCG 卡牌，但用户实际购买分布约为 ~50% 游戏/玩具/手办。根本原因：pairwise/pointwise 排序采用**独立性假设** —— 每个商品独立打分，不感知页面上其他商品的存在。

> **LTR (Learning to Rank，学习排序)**：一种 ML 框架，通过学习打分函数按相关性对商品排序；标准变体包括 pointwise、pairwise 和 listwise。

### My Role
- **完全自主发起**：在 Hacker Week 期间分析了弃用率最高的查询词，发现了系统性意图折叠模式
- 获得 Hacker Week 奖项；当原团队的职责范围不涵盖排序优化时，主动转组以获得完整 ownership
- 驱动项目从发现 → 上线 → 跨垂类框架复用，历时多年

### Expected Outcome
一个生产级、可复用的分配原语，将搜索结果多样性校准至用户需求分布 —— 在保持相关性质量的同时提升 **GMB (Gross Merchandise Bought，商品购买总额)**。

---

## 2. Solutions Explored（~5分钟）

### Alternatives Considered

| 方案 | 拒绝原因 |
|------|----------|
| **xQuAD / IA-Select** | 需要逐查询意图标注 —— 成本高，不可扩展 |
| **DPP (Determinantal Point Process，行列式点过程)**：使用核矩阵进行集合感知优化以选择多样化子集 | 高 QPS 下延迟不可接受；多样性-相关性权衡是隐式的且难以调优 |
| **Neural holistic ranking**（神经整体排序） | 完整集合优化 —— 理论最优但推理开销阻碍生产部署 |
| **Rule-based dedup**（基于规则的去重） | 无法捕捉意图级别的需求分布；粒度太粗 |

### Decision Framework
1. 必须是 **O(L) 单次遍历重排序**（生产延迟约束）
2. 必须保持**意图内排序不变**（同一意图类别内不降低相关性）
3. 必须通过可解释的旋钮**可调优**（不是黑盒核函数）
4. 单意图查询必须**优雅降级**回 base ranker

### Convergence
选择了**软配额执行 + 基于赤字的提升** —— 通过注入页面级意图覆盖信号来近似整体排序，避免真正集合优化的指数级复杂度。

---

## 3. Technical Deep Dive（~20分钟）

### Decision 1: Cheap Intent-Coverage Proxy Instead of Holistic Ranking

**问题**：神经整体排序解决了独立性假设问题，但延迟不可接受。

**方案**：不做真正的集合优化，而是让排序器"看到"当前页面的意图覆盖状态：
- 计算 **deficit（赤字）** = 每个意图 facet 相对于目标需求分布的欠表示程度
- 对每个 facet 的 leading item 施加有界的加法提升
- 单次遍历重排序取 top-k

> **Deficit（赤字）**：`max{0, k · p*(a|c) - μ_a(c)}` —— facet `a` 在 cohort `c` 中目标曝光量（来自需求分布）与 base ranker 下预期曝光量之间的差距。

**权衡**：近似解，但复杂度为 O(L)，对比集合优化的指数级复杂度。

**Pokemon 示例（详细推演）**：
- Base ranker top-60：~40 张 TCG 卡牌、~8 个游戏、~12 个玩具
- **All-touch attribution（全触点归因）** 目标：50% 卡牌 / 30% 游戏 / 20% 玩具
- `deficit(games) = max{0, 60 × 0.3 - 8} = 10` → 被 τ 截断
- 一个得分 0.6 的游戏商品可以跃升到第15个 TCG 卡牌（得分 0.85）之前，但**无法**超过 top-1 TCG 卡牌（得分 0.95）
- 结果：TCG 仍占据第1位，但第2-10位包含了游戏/玩具/手办

---

### Decision 2: Three-Tier Storage/Compute Tradeoff for Intent Distribution

| 层级 | 方法 | 使用场景 |
|------|------|----------|
| **Full** | 完整用户会话的全触点归因 | 资源充足时 |
| **Compressed** | Top-K 类别频率分布 | 存储受限时 |
| **Minimal** | **Dirichlet smoothing（狄利克雷平滑）** → 仅存储页面熵；通过 temperature scaling（温度缩放，Boltzmann/Gibbs 变换）恢复 | 极致压缩时 |

> **Dirichlet smoothing（狄利克雷平滑）**：向观测频率添加伪计数（α），防止零概率 facet 并向均匀分布正则化。等价于以 Dirichlet 先验做 **MAP (Maximum A Posteriori，最大后验概率)** 估计。

> **Temperature scaling（温度缩放）**：对 base ranker 分数的单参数变换，以匹配目标熵。当 base ranker 的 facet 排序稳定（~95% top-facet 重叠率）时效果良好；当分数平坦时退化 → 回退到完整分布。

**Facet 选择**：探索了完整 facet 发现方案；最终选定 **brand × category** —— 在电商场景下性能足够且复杂度可控。

---

### Decision 3: Soft-Quota Instead of Hard-Quota Enforcement

**硬配额的问题**：行为突变、不可控的相关性损失、难以调优。

**软配额设计**：
- 离线计算每个 facet、每个 cohort 的 deficit
- 映射为有界提升量：`φ(a|c) = min(deficit, τ)`
- 仅对每个 facet 的 **leading item** 施加加法提升：`s'_i = s_i + Δ · φ(f(i)|c(q))`
- 单次遍历重排序取 top-k

> **Soft-quota（软配额）**：不强制每个类别的硬性位置限制，而是施加一个连续的、有界的分数提升，提升幅度与该 facet 的欠表示程度成正比。

**Safety Knobs（安全旋钮）**：

| 旋钮 | 作用 |
|------|------|
| **τ** | 每个 facet 的提升上限 —— 防止失控提升 |
| **Δ** | 全局强度旋钮（Δ→∞ 退化为硬配额） |
| **K** | 每个 facet 的商品上限 —— 限制同 facet 重复 |
| **L** | 前缀长度 —— 限定最坏情况下的相关性损失 |

**安全保证**：意图内排序**严格保持不变**。被提升的商品始终是该 facet 中 base ranker 排名最高的商品。

---

### Decision 4: Cohorting and Backoff Strategy

- 查询 → cohort 映射使用 embedding / 垂类 / 类别 / 频率信号
- 分层回退：query-level → category-level → global target
- 确保稀疏/长尾查询的鲁棒性（deficit 自然趋近于零）

> **Long-tail defense（长尾防御，by construction）**：低频查询的召回集较小 → facet 较少 → deficit 较小 → 提升量接近零 → 系统自动退化为 base ranker。

---

## 4. Measuring Success（~8分钟）

### Experiment Design
- **Paired replay protocol（配对回放协议）**：相同的日志前缀，同时运行对照组/实验组，使用 per-query ΔH 配合分位数分层
- **Debiased curve（去偏曲线）**：A/B lift 减去 A/A lift 以消除分桶漂移
- **机制证据**：独立 holdout 集上 **JSD (Jensen-Shannon Divergence，Jensen-Shannon 散度)** 到目标分布的距离下降 **43.5%**，确认了从需求校准 → 业务收益的因果链

> **JSD (Jensen-Shannon Divergence，Jensen-Shannon 散度)**：两个概率分布之间的对称距离度量；此处用于量化结果页面意图分布与用户需求分布的匹配程度。

### Metrics Table

| 指标 | 基线 | 目标 | 结果 | 备注 |
|------|------|------|------|------|
| **GMB (Gross Merchandise Bought，商品购买总额)** | — | 正向提升 | **+~1%** | 统计显著；首次实验 |
| **Abandonment rate（弃用率）** | — | 下降 | **-0.3%** | 统计显著 |
| **MRR (Mean Reciprocal Rank，平均倒数排名)** | — | 监控 | 下降 | 重新定义：不是有效的页面级指标（见下文） |
| **框架复用 GMB** | — | 每个垂类正向提升 | **+0.6%+每个** | 认证商品、C2C 新商品列表 |
| **年化影响** | — | — | **200M+** | 跨多个垂类累计 |

> **GMB**：购买商品的总金额；主要业务指标。
> **MRR**：第一个相关结果排名位置的倒数；隐式假设单一意图。

### MRR Reframe
MRR 下降约1%，因为它衡量的是在**单意图假设**下"第一个相关结果出现在哪里"。当用户有混合意图时，将所有顶部位置给主导意图最大化 MRR，但**让一半用户失望**。证据：
- GMB 上升 → 更多商品被售出（如果效率真正下降这不可能发生）
- 弃用率下降 → 之前找不到东西的用户现在开始参与（"从零开始的增量 GMB"）
- 结论：MRR 下降 = 主导意图用户的效率降低，但**唤醒了少数意图用户** —— 净正市场结果

### Counter-Intuitive Findings
1. MRR 下降 + GMB 上升 → **直接推翻**了"pairwise LTR = 页面级最优"
2. 顶部漏斗查询（vintage、fashion）：多样性提供知识/灵感价值 —— 无法用页内 last-touch 指标衡量
3. 框架的最大价值不是多样性本身，而是一个**可复用的分配原语** —— 每次复用带来 0.6%+ 独立 GMB 增益

---

## 5. Key Learnings（~5分钟）

### If I Did It Again
- 更早建立自己的**监控管线**（GMB 漂移 / 多样性 / 相关性定期审查）—— 用数据主动产生洞察，而不是等实验 slot
- 更早构建**完整因果故事**（DS + 日志 + 数据管线），以降低利益相关者说服成本
- 更主动地**寻求资源和赞助**，而不是等待自上而下的优先级认可

### How This Changed My Thinking
- 从"做更好的排序" → **"质疑页面级最优性的定义"**
- 技术约束（延迟）迫使产生更优雅的代理方案 —— **约束是创新之源**
- 框架的真正价值在于**可复用性**，而非单次实验结果
- 对于顶部漏斗查询，**归因模型的选择本身就是一个业务价值判断** —— 灵感驱动的搜索无法用页内指标衡量

---

## Q&A Prep -- 16个挑战性问题防御

### Challenge 1: JSD drop ≠ GMB increase (causality)
**防御**：JSD 是**机制验证**，不是因果证明。它确认系统在做我们设计的事情 —— 如果 JSD 没有下降但 GMB 上升了，那反而是坏信号（存在未知混淆因素）。真正的因果证据是**三角验证**：GMB 上升 + JSD 下降 + 弃用率下降。三个独立信号指向同一方向。

### Challenge 2: Paired replay counterfactual validity
**防御**：on-policy 日志前缀是一个固有局限。我们的缓解措施是跨独立维度的三角验证：(1) 多个时间窗口结果一致，(2) 用户群体分层（查询频率、使用时长）lift 方向稳定，(3) 去偏曲线（A/B - A/A）。不是完美的反事实，但在生产约束下是最强可行的验证。

### Challenge 3: Abandonment attribution decomposition
**防御**：我们没有完全分解"未点击即弃用"vs"点击后弃用" —— 长期归因窗口有成熟度问题（跨会话灵感购买）。弃用率下降是**一阶收益**，独立于机制。结合 GMB 上升，这排除了纯粹的"参与度技巧" —— 用户在购买，不仅仅是浏览。

### Challenge 4: MRR decline debugging depth
**防御**：MRR 衡量的是单意图假设下第一个相关结果的排名。在多意图场景下，相关性是**以意图为条件的** —— 一个 pokemon 游戏对游戏寻求者是 0.95，对卡牌寻求者是 0.3。GMB 上升 + 弃用率下降 = 之前找不到东西的增量用户正在转化。这就是字面意义上的"从零创造价值"。

### Challenge 5: Target distribution on-policy bias
**防御**：on-policy 偏差是真实存在的，我们承认这一点。两个防御：(1) **requery signal（重查询信号）** —— 找不到想要内容的用户会添加限定词（"pokemon games"），暴露被压制的意图，(2) **用户多样性** —— 不同用户以不同方式克服排序偏差，在聚合层面稀释了 on-policy 污染。on-policy 分布是**下界** —— 真正被压制的意图更大，意味着我们的效果被低估了。

### Challenge 6: Deficit online/offline mismatch
**防御**：离线 deficit 使用历史召回分布；在线召回是动态的。我们接受这个近似因为：(1) 目标是方向性修正，不是精确分布匹配，(2) 安全旋钮（τ、K、L）提供硬性上界，防止过时 deficit 导致过度提升，(3) 在线实时 deficit 计算会增加不可接受的延迟。

### Challenge 7: Additive uplift score-scale assumption
**防御**：加法提升假设跨查询/垂类的分数范围可比。Δ 通过离线网格搜索**逐 cohort 校准**，确保有效提升量在每个 cohort 分数分布的目标范围内。统一设置优于逐垂类模型，原因是工程可维护性、冷启动规避和跨垂类信号保留。

### Challenge 8: Leading-item-only recall gap
**防御**：这是有意的**问题分解**决策。排序在召回集内分配；创造库存是检索的工作。当某个 facet 的 leading item 质量低于相关性阈值时，提升量被安全旋钮 L 截断。这为检索团队生成了**可操作的积压信号**：持续被截断的 facet = 需要修复的检索缺口。

### Challenge 9: Manager resistance vs. priority
**防御**：两个因素同时存在。相关性团队的职责范围是相关性兜底 —— 排序优化不在范围内。不管业务案例多强，实验 slot 不会分配给范围外的工作。我的 Hacker Week demo 在一周内证明了技术可行性。我没有及早做到的是：将业务案例翻译成团队的 OKR 语言。最终解决方案：**转组** —— 问题跟随人走。

### Challenge 10: Framework reuse attribution
**防御**：其他 MLE 使用了我的**生产级基础设施**（缓存表、deficit 管线、提升机制）并接入新的目标分布。他们没有从研究代码重建。类比：如果你构建了广告竞价系统，有人添加了新的出价策略，你拥有竞价基础设施。我拥有**分配原语**；复用者拥有垂类特定策略。

### Challenge 11: Experiment design ownership
**防御**：配对回放协议、分位数分层和去偏曲线都是**我独立设计的**。动机：(1) 生产快速迭代需求，(2) SIGIR 论文的学术严谨性。去偏曲线是在我通过个人监控管线发现分桶漂移后添加的 —— 不是标准团队工作流。

### Challenge 12: Seller-side impact
**防御**：多样性混合有意压缩主导意图头部卖家的曝光 —— 这是**设计预期行为**。业务正当性：(1) 策略数据显示卖家的首次成功交易具有**非线性终身价值** —— 多样性为长尾卖家提供曝光是一种平台投资，(2) 平台定位需要市场活力，而非头部卖家集中。

### Challenge 13: 200M+ calculation method
**防御**：标准 A/B lift 外推：实验组 vs 对照组的人均 GMB 差异 × 年化 GMV。每个垂类的实验运行在独立流量上（不相交的用户群体），因此加法外推在方法论上是站得住脚的。200M+ 是业务影响的**数量级估计**，不是实际入账收入。

### Challenge 14: Leadership mindset change evidence
**防御**：三种互补证据：(1) 运营信号（弃用率、相关性工单、商家投诉），(2) 意图-购买集中度对齐（页面展示分布与购买分布之间的 JSD），(3) 跨多季度累计改善。关键转折点：当弃用率被纳入团队 OKR —— 一旦指标进入问责体系，叙事就会跟随。

### Challenge 15: What I'd do differently (technical)
**防御**：更早投资 **all-touch attribution label pipeline（全触点归因标签管线）** —— 早期使用 last-touch，切换到 all-touch 后发现目标分布发生了显著变化（浪费了时间）。如果资源允许，设计一个小规模的**随机化召回实验**（即使只有1%流量）来限定 on-policy 偏差。更早进行 **per-cohort score normalization（逐 cohort 分数归一化）** 以获得更一致的软配额行为。

### Challenge 16: Bounding on-policy bias
**防御**：随机化排序会直接损害用户体验和短期 GMB —— 无法通过保障审查。替代方案：使用 **requery behavior as revealed preference（重查询行为作为显示偏好）** —— 当用户添加产品类型限定词时，暴露了未被满足的意图。衡量实验组 vs 对照组的意图揭示性重查询频率。工业因果标准：**通过三角验证实现帕累托改进**，而非完整因果识别。诚实的科学。

---

## Key Numbers Quick Reference

| 数字 | 代表含义 |
|------|----------|
| **+~1%** | GMB 提升（首次实验，统计显著） |
| **-0.3%** | 弃用率降低 |
| **+0.6%+** | 框架复用时每个垂类的 GMB 提升 |
| **200M+** | 跨垂类年化影响（数量级估计） |
| **43.5%** | 独立 holdout 集上 JSD 到目标分布距离的降低 |
| **~95%** | base ranker 排序稳定时的 top-facet 重叠率（temperature scaling） |
| **~87%** | 跨 cohort 平均 top-facet 重叠率 |
| **0.0%** | 意图内排序违反率（对比 MMR baseline 的 28.1%） |
| **+0.39%** | 延迟均值增加（对比 MMR 的 +0.82%） |
| **+17.4%** | 类别覆盖增加（适度的、需求校准的 —— 对比 MMR 的 +78.8%） |

---

## Paper Comparison: Soft-Quota vs. MMR Baseline

| 指标 | Soft-Quota (Ours) | MMR Baseline |
|------|-------------------|-------------|
| 延迟均值 | +0.39% | +0.82% |
| 延迟 P95 | +0.24% | +0.57% |
| 意图内排序违反 | **0.0%** | 28.1% |
| Overlap@60 | 91.9% | 87.1% |
| MRR-sale@60 | -0.64% | -1.1% |
| 类别覆盖 | +17.4% | +78.8% |
| Shannon entropy | +12.1% | +37.4% |

**核心洞察**：适度的、需求校准的多样性（+17.4% 覆盖）在 GMB 上优于最大多样性（+78.8%）—— 我们不是在最大化多样性，而是在**将多样性对齐到用户需求**。

---

## Expression Style Reminders

### Say This, Not That

| 不要这样说 | 改为这样说 |
|------------|------------|
| "这不是大问题" | 直接陈述失败模式及其防御 |
| "我们不关心 top-3 低相关性" | "意图内排序严格保持不变；被提升的商品始终是其 facet 中 base ranker 排名最高的，这是结构性保证" |
| "你可以用 MI 或 L2 或其他指标" | 选定**一个**（论文公式6：deficit），并为之负责 |
| "按我们的定义不存在相关性问题" | "相关性在我们的框架中是二元兜底决策" + 逐意图 MRR 重定义 |

### Anecdote Usage Rules
- **Pokemon TCG 卡牌** → 问题陈述开场 + deficit 推演
- **Calvin Klein** → 意图折叠的普遍性（内衣 + 香水折叠，缺失服装/配饰/鞋类）
- **Pikachu 滑板** → 留给"你如何定义相关性"或"相关性兜底如何工作"的问题
- **永远不要**用轶事回答纯技术问题（如帕累托最优性）—— 看起来像在回避

### Single-Intent Query Defense (Automatic)
当被问到"你的系统是否过度多样化窄查询如'iphone 15 pro max case'？"时：
- all-touch attribution 显示目标 95%+ 集中在手机壳上
- Dirichlet smoothing → 熵保持非常低
- 其他 facet 的 deficit ≈ 0 → uplift ≈ 0
- 系统**自动退化为 base ranker** —— 通过数学，而非分类器

### Pareto / Operating Point Standard Answer
1. **经验层面**：没有在全站 A/B 上做完整网格搜索（成本不可承受）；使用了大量抓取 + 人工/LLM 对搜索结果质量的判断
2. **在线验证**：多次 A/B 测试确认业务指标净正向
3. **前瞻性**：当前策略是全局的；进一步推进需要细分级别的差异化 —— 不同用户群体有不同的多样性-相关性前沿
"""


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Read current content for verification
    cur.execute("SELECT length(content) FROM company_documents WHERE id=4")
    old_len = cur.fetchone()[0]
    print(f"Original content length: {old_len}")

    # Update with Chinese content
    cur.execute(
        "UPDATE company_documents SET content = ? WHERE id = 4",
        (CHINESE_CONTENT.strip(),),
    )
    conn.commit()

    # Verify
    cur.execute("SELECT content FROM company_documents WHERE id=4")
    new_content = cur.fetchone()[0]
    new_len = len(new_content)
    print(f"New content length: {new_len}")

    # Validation checks

    # Check 1: Has Chinese characters
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", new_content))
    print(f"Chinese characters: {chinese_chars}")
    assert chinese_chars > 500, f"Too few Chinese characters: {chinese_chars}"

    # Check 2: No formulas in code blocks
    code_blocks = re.findall(r"```[\s\S]*?```", new_content)
    for i, block in enumerate(code_blocks):
        assert "$$" not in block, f"Formula inside code block {i}!"
    print(f"Code blocks checked: {len(code_blocks)} (no formulas inside)")

    # Check 3: English headings preserved
    headings = re.findall(r"^##+ .+$", new_content, re.MULTILINE)
    print(f"Headings found: {len(headings)}")
    for h in headings[:10]:
        print(f"  {h}")

    # Check 4: Bold terms with Chinese expansion
    bold_terms = re.findall(r"\*\*[A-Z].*?[）)].*?\*\*", new_content)
    print(f"Bold terms with Chinese expansion: {len(bold_terms)}")
    for t in bold_terms[:10]:
        print(f"  {t}")

    # Check 5: Key numbers preserved
    for num in ["+~1%", "-0.3%", "+0.6%", "200M+", "43.5%", "0.0%"]:
        assert num in new_content, f"Missing key number: {num}"
    print("All key numbers preserved")

    # Check 6: Tables preserved
    table_rows = re.findall(r"^\|.+\|$", new_content, re.MULTILINE)
    print(f"Table rows: {len(table_rows)}")

    print("\n[DONE] All validation checks passed!")
    conn.close()


if __name__ == "__main__":
    main()
