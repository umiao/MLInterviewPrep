"""T-P1-455: Cold-Start Strategies framework node + Pinterest company doc.

Adds the missing 'Cold Start' depth-2 framework_node under
pillar4.recommender_systems (sibling of CF / Content-Based / Deep Reco) and
seeds a Pinterest company_document covering Pin/user/creator cold-start
playbooks. Pyramid mid: covers the five canonical strategies + Pinterest
specifics, defers full meta-learning + bandit derivations to other docs.

Idempotent: re-runs UPDATE the framework_node description and upsert the
company_document by (company_id, title).

Usage::

    python scripts/seed_pinterest_recsys_cold_start_20260416.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from study_note_builder import FormulaBlock, StudyNoteBuilder  # noqa: E402

DB_PATH = ROOT / "data" / "mle_prep.db"

PINTEREST_COMPANY_ID = 29
DOC_TITLE = "Pinterest Cold-Start Strategies (Pin / User / Creator)"

NODE_PARENT_ID = 21  # pillar4.recommender_systems
NODE_PATH = "pillar4.recommender_systems.cold_start"
NODE_TITLE = "Cold Start"
NODE_DEPTH = 2
NODE_IMPORTANCE = 0.85
NODE_PRIORITY = "P1"
NODE_STATUS = "not_started"
NODE_ESTIMATED_HOURS = 3.0
NODE_RELEVANT_COMPANIES = "Pinterest, TikTok, YouTube, Spotify, Netflix"


# ==========================================================================
# Framework node description (>= 3500 bytes target)
# ==========================================================================

NODE_DESCRIPTION = """# Cold Start

## Overview

**Cold-Start Problem（冷启动问题）** 是推荐系统的核心痛点之一：当**新用户、新物品、或新创作者**进入系统时，缺少历史交互信号，**Collaborative Filtering（协同过滤）** 直接失效——矩阵分解学不到 embedding，CF 邻居为空，深度模型缺监督。资深MLE必须掌握五类应对策略并理解何时混合使用。

冷启动可细分为三种场景：(1) **User cold-start（用户冷启动）**：新注册用户无历史交互；(2) **Item cold-start（物品冷启动）**：新上架物品无人点击；(3) **System cold-start（系统冷启动）**：新业务上线、整张交互矩阵稀疏。Pinterest 的 Pin 流每天新增数百万张，**Pin cold-start** 是日常生产问题，不是边角案例。

## Five Canonical Strategies

### 1. Content-Based First-Shot（基于内容的首发）

利用物品/用户的**侧信息（side information）**——文本、图像、地理、人口学——直接计算相似度，不依赖任何交互历史。Pinterest 的天然优势在于每张 Pin 都自带**图像 + 文本（标题、描述、Board 上下文）**，新 Pin 一上传就能立即过视觉塔（ResNet-50 / EfficientNet）+ 文本塔（BERT 系）得到 embedding，直接进入 ANN 索引，**完全跳过冷启动阶段**。

公式上，新物品 $$j$$ 与已有用户 $$u$$ 的得分：

$$
\\text{score}(u, j) = \\cos(\\mathbf{u}_{\\text{profile}}, \\mathbf{x}_j^{\\text{content}})
$$

这是 Pinterest、YouTube Shorts、TikTok 处理新内容的默认主路径。

### 2. Cross-Domain / Demographic Transfer（跨域 / 人口学迁移）

新用户没有交互，但有**注册信号**：年龄段、性别、地理位置、设备、注册渠道。把已有用户按这些特征聚类，新用户继承同簇用户的偏好分布作为先验。**Bayesian 框架**下，这是给新用户 embedding 一个**信息先验**而非零向量。Pinterest 实战：注册时强制选 "感兴趣的话题"（cooking / fashion / DIY），这本身就是显式 demographic transfer。

### 3. Meta-Learning（元学习，MAML 系）

把 "从少量交互快速学到用户偏好" 显式建模成一个学习问题：训练一个**初始化参数 $$\\theta_0$$**，使得在新用户上只需 $$k$$ 步梯度下降就能达到合理性能。**MAML（Model-Agnostic Meta-Learning）** 的内外循环优化：

$$
\\theta_0 \\leftarrow \\theta_0 - \\beta \\nabla_{\\theta_0} \\sum_{u \\in \\text{tasks}} \\mathcal{L}_u(\\theta_0 - \\alpha \\nabla_\\theta \\mathcal{L}_u(\\theta_0))
$$

**实践成本**：训练复杂、超参敏感、生产部署罕见；面试上知道概念 + 能说"工业界常用 fine-tune 替代"即可。

### 4. Contextual Bandits（上下文老虎机，explore/exploit）

冷启动本质是 explore/exploit 权衡：要给新物品**主动曝光**才能拿到反馈。**LinUCB / Thompson Sampling** 把推荐看作多臂赌博机，每个 arm（物品 / 候选 embedding）维护一个不确定性估计，置信上界（UCB）大的 arm 优先曝光。**LinUCB 的得分公式**：

$$
\\text{score}(a) = \\hat{\\mu}_a + \\alpha \\sqrt{\\mathbf{x}_a^T A_a^{-1} \\mathbf{x}_a}
$$

其中第二项是探索奖励，$$\\alpha$$ 控制探索强度。Pinterest 内部用 bandit 给新 Pin 做 "首批曝光预算"——每张新 Pin 强制曝光 $$N$$ 次以收集 CTR 信号，再交给排序模型。

### 5. Popularity / Trending Baseline Fallback（热门 / 趋势兜底）

最后一道防线：什么都不知道时，推**全局热门**或**当前 trending**。简单但极有效，CTR 通常比随机高 5-10x，是任何冷启动管线的兜底层。**注意**：直接推全局热门会有 popularity bias，新创作者永远进不了 top；解法是分桶推（按 category trending）+ 给新内容固定曝光配额 + `1/(1 + log(impressions))` 给老热门降权。

## 评估指标与陷阱

冷启动效果**不能只看 CTR**——cold-start 阶段样本少，CTR 方差巨大且容易被探索/利用比例污染。常用评估组合：(a) **覆盖率（coverage）**：新 Pin / 新 Creator 在前 N 天能被曝光给多少独立用户；(b) **进入主流通道时间（time-to-converge）**：新 Pin 累积到 1000 impressions 的中位时间；(c) **新用户 7/14/30 天留存**：Onboarding + 冷启动管线的核心 KPI；(d) **长期 CTR 偏置（popularity bias）**：新内容在 top-100 trending 中的占比，避免老热门垄断。

**典型陷阱**：(1) 用 random A/B 评估冷启动会低估真实效果——bandit 探索本身收益滞后，需用 **interleave + IPS（inverse propensity scoring）** 做反事实评估；(2) 直接对比"新策略 vs 老策略"在新用户群上的指标会被 selection bias 污染——新用户进入实验组的时刻不可控；(3) cold-start regularizer 调过头会**永久压制大用户**的体验，需用 stratified evaluation 同时看新老用户分桶指标。

## Pinterest 三场景速查

| 场景 | 主策略 | 兜底 | 关键 KPI |
| --- | --- | --- | --- |
| **Pin cold-start** | Content-based 视觉 + 文本塔 embedding 直接进 ANN | Category trending | 新 Pin 进 ANN 后首日 impressions |
| **User cold-start** | 注册时显式选话题 + demographic transfer | Editorial / 全局热门 | 注册后 7 天留存 |
| **Creator cold-start** | 给新 Board / 新 Creator 固定曝光配额 + bandit 探索 | 同 category top creator | 新 Creator 30 天 follower 增长 |

## When to Mix vs Pick One

冷启动几乎从不 "用一种"——**生产管线是分阶段串联**：(a) 0 交互时走 content-based + popularity 兜底；(b) 1~10 交互时叠加 demographic + bandit 探索；(c) 10~100 交互时切换到主排序模型 + 在 loss 加 cold-start regularizer；(d) >100 交互时进入正常 CF / 深度模型。**Pinterest 实战**：Home feed 排序模型对每个候选的特征里显式加 "is_new_pin / is_new_user / interaction_count" 作为 gating 信号，让模型自己学不同冷启动阶段的权重组合。

## Pinterest 公司文档

详细 5 策略 + 三场景 playbook + 面试 QA 见 **company_documents `Pinterest Cold-Start Strategies`**（含 Pinterest ItemSage 双塔在新 Pin 上的发挥、注册 onboarding 流的 demographic transfer、新 Creator 曝光配额的工程实现细节）。
"""


# ==========================================================================
# Pinterest company doc content (target <= 2000 words)
# ==========================================================================

def build_cold_start_doc() -> str:
    b = StudyNoteBuilder()
    b.set_title("Pinterest Cold-Start Strategies (Pin / User / Creator) -- 1-Pager")

    b.add_prerequisites([
        "推荐系统基础：CF / 矩阵分解 / Two-Tower 架构",
        "Pinterest 双塔与 ItemSage 视觉+文本对齐（参见 `[Pinterest-CV]` CNN Foundation 文档）",
        "Bayesian 先验直觉：信息先验 vs 零向量初始化",
        "基础 explore/exploit：epsilon-greedy / UCB",
    ])

    b.add_term("Cold-Start", "Cold-Start Problem",
        "新用户/新物品/新系统缺历史交互，CF 失效；推荐系统的核心痛点之一")
    b.add_term("ItemSage", "Pinterest's Multimodal Item Embedding",
        "Pinterest 内部视觉塔 + 文本塔统一对齐到同一空间的 Pin embedding 系统")
    b.add_term("MAML", "Model-Agnostic Meta-Learning",
        "训练初始参数让新任务/新用户只需少量梯度步即可适应")
    b.add_term("LinUCB", "Linear Upper Confidence Bound",
        "线性奖励假设下的 contextual bandit；arm 得分 = 期望 + 置信上界")
    b.add_term("Onboarding", "Onboarding Topic Picker",
        "Pinterest 注册时强制选 5+ 话题；显式 demographic + interest 信号")

    # ----------------------------------------------------------------------
    b.add_section("1. 三类冷启动场景速查", [
        (
            "**Pinterest 的冷启动不是边角问题**——日均新增数百万 Pin、几十万新用户、"
            "数千新 Creator。三类场景需要分别设计：\n\n"
            "- **Pin cold-start（物品冷启动）**：新 Pin 上传，无 impression / save / click。"
            "Pinterest 的天然优势：每 Pin 自带图像 + 标题 + 描述 + Board 上下文 -> "
            "直接过 **ItemSage** 双塔 -> embedding 进 ANN 索引 -> 立刻可被召回。\n"
            "- **User cold-start（用户冷启动）**：新注册，无 home feed 交互。"
            "Pinterest 的解法：**Onboarding Topic Picker**（强制选 5+ 话题）+ "
            "demographic transfer（年龄/地理/设备）。\n"
            "- **Creator cold-start（创作者冷启动）**：新 Board / 新 Creator，跟随者为 0。"
            "解法：给新 Creator 固定曝光配额 + bandit 探索找早期粉丝。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_section("2. 五种策略 + Pinterest 落地", [
        (
            "**(1) Content-Based First-Shot（首推路径）**\n\n"
            "Pinterest 是图像-文本平台，content side info 极其丰富。"
            "新 Pin 一旦上传，**5 分钟内**走完：(a) 视觉塔（ResNet-50 蒸馏版 / "
            "EfficientNet-B3）抽 256 维视觉 embedding；(b) 文本塔（distilBERT）"
            "处理标题/描述/OCR 文本；(c) ItemSage 把两者投影到统一 1024 维空间；"
            "(d) embedding 写入 HNSW / FAISS 索引。\n\n"
            "**为什么这条路在 Pinterest 比在 Netflix / 电商更有效**：Pin 的视觉信号"
            "对用户 retention 几乎是充分统计——\"这张图是不是我的菜\"在 200ms "
            "内就能判断。新闻 / 电商缺这种纯视觉判别力。"
        ),
        (
            "**(2) Cross-Domain / Demographic Transfer（先验注入）**\n\n"
            "新用户在注册流提供：年龄段、性别（可选）、地理（IP 推断）、设备、语言、"
            "注册渠道（搜索来源、社交分享）。把已有用户按这些维度做 K-means 聚类，"
            "新用户继承同簇 centroid embedding 作为初始 user embedding。\n\n"
            "**Pinterest Onboarding Topic Picker** 是显式版本：注册流强制选 5+ 话题"
            "（cooking / fashion / DIY / travel ...）-> 把这 5 个话题的 average embedding "
            "作为 user embedding 初始化。30 秒内拿到的信号 = 自然滚动 home feed 1-2 周的"
            "等价信息量；这是 Pinterest 留存数据公开归因到 Onboarding 的核心理由。"
        ),
        FormulaBlock(
            latex=(
                r"\mathbf{u}_{\text{init}} = \frac{1}{|T|} \sum_{t \in T} \mathbf{e}_t"
                r" + \beta \cdot \mathbf{c}_{\text{demo}}"
            ),
            explanation=(
                "**用户冷启动初始化公式**：$T$ 是用户在 Onboarding 选的话题集合，"
                "$\\mathbf{e}_t$ 是话题 embedding，$\\mathbf{c}_{\\text{demo}}$ 是该用户"
                "demographic 簇 centroid，$\\beta$ 是 demographic 权重（实战 0.1~0.3）。"
            ),
        ),
        (
            "**(3) Meta-Learning（MAML 系，工业界谨慎使用）**\n\n"
            "理论很优雅：训练一个 $\\theta_0$ 让任意新用户只需 5~10 步 fine-tune 就能学到偏好。"
            "**实战为什么少见**：(a) 训练成本巨大（双层优化）；(b) 超参敏感、不稳定；"
            "(c) 推断时还要做 per-user fine-tune，工程复杂；(d) 简单的 fine-tune "
            "往往效果接近。**面试要点**：知道概念，能解释 inner/outer loop，能说"
            "\"工业界更常用基于先验初始化 + 少量 transfer learning，不直接上 MAML\"。"
        ),
        (
            "**(4) Contextual Bandits（新 Pin / 新 Creator 探索预算）**\n\n"
            "新 Pin 的 ItemSage embedding 只是\"图文相似性\"——和真实 CTR 的相关性"
            "在 0.4~0.6 之间，需要少量真实曝光来校准。**Pinterest bandit 的工程化做法**："
            "(a) 每张新 Pin 给固定曝光预算 $N=200~500$ impressions；"
            "(b) 这些曝光从随机用户里抽，但 over-sample 同 category 的活跃用户；"
            "(c) 收集 CTR 后更新 LinUCB 后验，决定是否继续推；"
            "(d) 累计 1000+ impressions 后切到主排序模型。\n\n"
            "**Creator 冷启动同理**：新 Creator 的 first 10 Pins 享受额外曝光配额，"
            "防止 popularity bias 把新人永久压在尾部。"
        ),
        FormulaBlock(
            latex=(
                r"\text{LinUCB}(a, x) = x^T \hat{\theta}_a + "
                r"\alpha \sqrt{x^T A_a^{-1} x}"
            ),
            explanation=(
                "**LinUCB 评分**：$x$ 是 context 向量（用户 + 物品特征），"
                "$\\hat{\\theta}_a$ 是 arm $a$ 的线性权重 MLE，"
                "第二项是置信上界（不确定性奖励）；$\\alpha$ 控制探索强度，"
                "实战 0.5~2.0，对新 Pin 阶段调高。"
            ),
        ),
        (
            "**(5) Popularity / Trending Baseline（兜底层）**\n\n"
            "什么都不知道时（用户拒绝 Onboarding、Pin 内容抽 embedding 失败、模型超时），"
            "**全局 trending Pins** 是兜底选择。CTR 通常比纯随机高 5-10x。\n\n"
            "**关键陷阱**：直接推全局 trending 会强化 popularity bias，"
            "新 Creator 永远挤不进。**Pinterest 解法**：(a) 按 category 分桶 trending，"
            "保证每类话题都有候选；(b) trending 集合里强制保留 ~10% 新 Pins（freshness 配额）；"
            "(c) 用 `1/(1 + log(impressions))` 给老热门降权，让上升期 Pin 优先。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_comparison_table(
        headers=["策略", "用户冷启动", "Pin 冷启动", "Creator 冷启动", "工程成本"],
        rows=[
            ["**Content-based**", "弱", "**主路径**（ItemSage 双塔）", "弱", "低（已有塔）"],
            ["**Demographic transfer**", "**主路径**（Onboarding）", "弱", "中", "低"],
            ["**Meta-Learning (MAML)**", "可选，少见", "弱", "弱", "**高**"],
            ["**Contextual Bandit**", "弱", "中（新 Pin 曝光预算）", "**主路径**（探索预算）", "中"],
            ["**Popularity fallback**", "兜底", "兜底", "兜底（同 category top）", "极低"],
        ],
        title="3. Pinterest 三场景 x 五策略的适配矩阵",
    )

    # ----------------------------------------------------------------------
    b.add_section("4. 生产管线：阶段串联（不是 pick-one）", [
        (
            "Pinterest 实战的冷启动**从不只用一种策略**——是**按交互量分阶段串联**：\n\n"
            "- **0 交互**（注册首日）：Onboarding topics + demographic transfer + "
            "trending 兜底；用户 embedding 完全靠先验。\n"
            "- **1~10 交互**：开始拼接真实信号（save / hide / 长按），"
            "bandit 给 home feed 加 explore 比例 ~20%；用户 embedding = "
            "0.5 * Onboarding init + 0.5 * 实时学习的 embedding。\n"
            "- **10~100 交互**：主排序模型上线，但 loss 加 cold-start regularizer "
            "（对 interaction_count < 100 的样本调高 sample weight）；explore 降到 ~10%。\n"
            "- **>100 交互**：完全切到正常 ranking model，explore 降到 ~5% baseline。"
        ),
        (
            "**关键工程实现**：home feed 排序模型的特征里显式包含 "
            "`is_new_user`（< 7 天）、`is_new_pin`（< 24h）、`interaction_count_bucket`，"
            "让模型自己学不同冷启动阶段的权重组合，而不是硬编码 if-else 切换策略。"
        ),
    ])

    # ----------------------------------------------------------------------
    b.add_interview_qa(
        "Pinterest 一个新 Pin 上传，怎么让它有机会被推荐？",
        (
            "**3 步回答**：\n"
            "  1. **Content-based 首发**：上传后 5 分钟内过 ItemSage 双塔（视觉塔 ResNet-50 / "
            "EfficientNet + 文本塔 distilBERT）-> 1024 维 embedding -> 写入 HNSW "
            "ANN 索引 -> 立刻可被任意候选检索。\n"
            "  2. **Bandit 曝光预算**：给新 Pin 200-500 impressions 的 LinUCB 探索预算，"
            "over-sample 同 category 活跃用户，收集真实 CTR 信号。\n"
            "  3. **切换主排序**：累计 1000+ impressions 后特征里 `is_new_pin=False`，"
            "进入正常 ranking 模型；同时 freshness 配额保证 trending 集合里"
            "始终有 ~10% 新 Pins。\n\n"
            "**加分**：主动提 popularity bias 风险 + 三种解法（category 分桶、freshness 配额、"
            "log-impressions 降权）；提 ItemSage 双塔的 contrastive loss 训练（对 cold-start "
            "embedding 质量是充分条件）。"
        ),
    )
    b.add_interview_qa(
        "新用户注册第一次打开 Pinterest，home feed 怎么生成？",
        (
            "**核心**：纯靠先验，没有真实交互信号。\n"
            "  1. **Onboarding topics**（最强信号）：用户必须选 5+ 话题，"
            "把这些话题 embedding 平均作为 user embedding 初始化；30 秒拿到的"
            "信息量 ~ 自然滚动 1-2 周。\n"
            "  2. **Demographic transfer**：地理（IP）+ 设备 + 注册渠道 -> 找最近的 K 个"
            "已有用户簇，继承簇 centroid 偏好分布作为补充先验。\n"
            "  3. **Bandit 高 explore**：home feed 用 epsilon-greedy 或 LinUCB，"
            "explore 比例 ~20%（vs 老用户 ~5%），快速探索用户真实兴趣。\n"
            "  4. **Trending 兜底**：模型超时或所有候选不足时退化到 category trending。\n\n"
            "**加分**：提 7 天留存是这个流程的核心 KPI，Onboarding topic picker 的"
            "AB 测试历史显示对留存有 5-10% 提升；提 \"continuous onboarding\"——"
            "前 7 天每次会话末尾轻量再问一两个偏好问题。"
        ),
    )
    b.add_interview_qa(
        "为什么 Pinterest 的 cold-start 比 Netflix 简单？",
        (
            "**根本原因**：Pin 的视觉信号是用户决策的近似充分统计——"
            "200ms 看一眼图就能判断 \"是不是我的菜\"，content-based embedding "
            "和真实偏好的相关性可达 0.6+。\n\n"
            "Netflix 不行：电影封面图诱惑力 vs 真实观看后评分 几乎不相关，"
            "必须靠交互信号慢慢学。所以 Netflix 重 demographic transfer + "
            "强制评分若干部已看过的电影；Pinterest 重 content embedding + 视觉塔。\n\n"
            "**反向论证**：Spotify 的歌曲 cold-start 用音频频谱嵌入，也走 content-based "
            "首发路径——同样因为 30 秒试听是近似充分统计。**信号充分性 = "
            "content-based 路径有效性**。"
        ),
    )
    b.add_interview_qa(
        "MAML / 元学习在工业界推荐系统真的用吗？",
        (
            "**诚实答案**：罕见。学术论文很多，生产部署极少，原因：\n"
            "  1. **训练成本**：双层优化把训练时间放大 5-10x，需要海量任务采样。\n"
            "  2. **超参敏感**：内循环步长、外循环步长、任务采样策略全部影响收敛。\n"
            "  3. **推断复杂**：每个新用户要做 per-user fine-tune，工程系统不接受。\n"
            "  4. **简单替代足够好**：基于话题 embedding 平均 + demographic transfer + "
            "正常 ranking 模型，效果通常接近 MAML，工程成本低 10x。\n\n"
            "**面试加分回答**：\"知道 MAML 概念，能解释 inner/outer loop 优化的含义，"
            "但工业界更常用 Onboarding 显式收集偏好 + 先验初始化 + 标准 fine-tune；"
            "MAML 是 nice to know 但不是 must have。\""
        ),
    )

    # ----------------------------------------------------------------------
    b.add_checklist("Pinterest Cold-Start Self-Check", [
        "能列出三类冷启动场景（user / pin / creator）+ 各自主策略",
        "能默写 5 种策略 + 适配矩阵（content-based / demographic / MAML / bandit / trending）",
        "能解释 Pinterest 为什么 content-based 首发特别有效（视觉信号充分性）",
        "能讲清楚 Onboarding Topic Picker 的信号量等价 1-2 周自然滚动",
        "能讲 LinUCB 公式 + 新 Pin 曝光预算的工程实现（200-500 impressions）",
        "能讲 popularity bias 三种解法（category 分桶、freshness 配额、log 降权）",
        "能讲生产管线 4 阶段切换（0 / 1-10 / 10-100 / >100 交互）",
        "能对比 Pinterest vs Netflix 的 cold-start 难度差异（信号充分性视角）",
        "能诚实评价 MAML 在工业界少见的 4 个原因",
    ])

    return b.build()


# ==========================================================================
# DB helpers
# ==========================================================================

def upsert_framework_node(conn: sqlite3.Connection) -> tuple[int, str, int]:
    """Upsert framework_node by path. Returns (node_id, action, desc_length)."""
    row = conn.execute(
        "SELECT id FROM framework_nodes WHERE path = ?", (NODE_PATH,)
    ).fetchone()
    if row:
        node_id = row[0]
        conn.execute(
            "UPDATE framework_nodes SET parent_id = ?, depth = ?, title = ?, "
            "description = ?, importance = ?, priority = ?, status = ?, "
            "estimated_hours = ?, relevant_companies = ? WHERE id = ?",
            (
                NODE_PARENT_ID, NODE_DEPTH, NODE_TITLE, NODE_DESCRIPTION,
                NODE_IMPORTANCE, NODE_PRIORITY, NODE_STATUS,
                NODE_ESTIMATED_HOURS, NODE_RELEVANT_COMPANIES, node_id,
            ),
        )
        action = "UPDATED"
    else:
        cur = conn.execute(
            "INSERT INTO framework_nodes "
            "(parent_id, path, depth, title, description, importance, "
            "priority, status, estimated_hours, relevant_companies, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (
                NODE_PARENT_ID, NODE_PATH, NODE_DEPTH, NODE_TITLE,
                NODE_DESCRIPTION, NODE_IMPORTANCE, NODE_PRIORITY, NODE_STATUS,
                NODE_ESTIMATED_HOURS, NODE_RELEVANT_COMPANIES,
            ),
        )
        node_id = cur.lastrowid
        action = "INSERTED"
    new_len = conn.execute(
        "SELECT length(description) FROM framework_nodes WHERE id = ?", (node_id,)
    ).fetchone()[0]
    return node_id, action, new_len


def upsert_company_document(
    conn: sqlite3.Connection,
    company_id: int,
    title: str,
    content: str,
    doc_kind: str = "prep_note",
    source_type: str = "manual",
) -> tuple[int, str, int]:
    """Insert or update company_document by (company_id, title)."""
    row = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (company_id, title),
    ).fetchone()
    if row:
        doc_id = row[0]
        conn.execute(
            "UPDATE company_documents SET content = ?, doc_kind = ?, "
            "source_type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (content, doc_kind, source_type, doc_id),
        )
        action = "UPDATED"
    else:
        cur = conn.execute(
            "INSERT INTO company_documents "
            "(company_id, title, content, source_type, doc_kind) "
            "VALUES (?, ?, ?, ?, ?)",
            (company_id, title, content, source_type, doc_kind),
        )
        doc_id = cur.lastrowid
        action = "INSERTED"
    new_len = conn.execute(
        "SELECT length(content) FROM company_documents WHERE id = ?", (doc_id,)
    ).fetchone()[0]
    return doc_id, action, new_len


# ==========================================================================
# Main
# ==========================================================================

def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    desc_bytes = len(NODE_DESCRIPTION.encode("utf-8"))
    desc_chars = len(NODE_DESCRIPTION)
    print(f"[BUILT] cold_start node description: {desc_chars} chars / {desc_bytes} bytes")
    if desc_bytes < 3500:
        print(f"[FAIL] node description {desc_bytes} bytes < 3500 byte AC minimum")
        sys.exit(1)

    content = build_cold_start_doc()
    warns = StudyNoteBuilder.validate(content)
    for w in warns:
        print(f"[WARN] {w}")
    doc_chars = len(content)
    doc_bytes = len(content.encode("utf-8"))
    word_estimate_en = doc_chars // 6  # rough English-equivalent word count
    print(f"[BUILT] cold_start doc: {doc_chars} chars / {doc_bytes} bytes / ~{word_estimate_en} EN-equivalent words")
    if doc_chars > 13000:
        print(f"[WARN] doc {doc_chars} chars may exceed 2000 word AC")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        nid, naction, nlen = upsert_framework_node(conn)
        print(f"[{naction}] framework_node id={nid} path={NODE_PATH} desc_len={nlen}")

        did, daction, dlen = upsert_company_document(
            conn, PINTEREST_COMPANY_ID, DOC_TITLE, content
        )
        print(f"[{daction}] company_document id={did} title='{DOC_TITLE}' content_len={dlen}")

        conn.commit()
    finally:
        conn.close()

    print("[DONE] Pinterest cold-start seed complete")


if __name__ == "__main__":
    main()
