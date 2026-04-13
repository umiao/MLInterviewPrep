"""Rewrite Adobe Day 2 (RLHF/DPO/Distillation) in Chinese.

Incorporates user's comprehensive supplement covering:
- RLHF 3-stage pipeline with full math (SFT, RM, PPO)
- DPO 4-step derivation (Z(x) cancellation)
- PPO clip mechanism + 4-model GPU analysis
- DPO vs RLHF multi-dimensional comparison
- GRPO/RLAIF/KTO/SimPO/IPO/ORPO variants
- LLM distillation (dark knowledge, temperature, T-squared correction)
- 70B->7B recipe + memory estimation
- 5 error corrections, 5 Q&As with answers, formula cheat sheet
"""
import importlib.util
import sqlite3
import sys
from pathlib import Path

# Import StudyNoteBuilder from scripts/study_note_builder.py
_BUILDER_PATH = Path(__file__).resolve().parent / "study_note_builder.py"
_spec = importlib.util.spec_from_file_location("study_note_builder", _BUILDER_PATH)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["study_note_builder"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
StudyNoteBuilder = _mod.StudyNoteBuilder
FormulaBlock = _mod.FormulaBlock

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
DOC_ID = 12  # Adobe Prep Day2
COMPANY_ID = 23


def build_day2_chinese() -> StudyNoteBuilder:
    b = StudyNoteBuilder()
    b.set_title("RLHF / DPO Alignment + LLM Distillation (Adobe Prep Day 2)")

    b.add_prerequisites([
        "语言模型预训练 (next-token prediction, cross-entropy loss)",
        "基础强化学习 (policy, reward, objective functions)",
        "概率基础 (sigmoid, KL divergence, softmax)",
    ])

    # Register terms
    b.add_term("RLHF", "Reinforcement Learning from Human Feedback",
               "三阶段 pipeline (SFT -> Reward Model -> PPO)，将 LLM 对齐到人类偏好")
    b.add_term("DPO", "Direct Preference Optimization",
               "消除 reward model 和 RL 循环，用分类损失直接优化偏好")
    b.add_term("SFT", "Supervised Fine-Tuning",
               "在高质量示范数据上微调预训练模型")
    b.add_term("PPO", "Proximal Policy Optimization",
               "RLHF Stage 3 使用的 RL 算法，通过 clipped surrogate objective 保持更新稳定")
    b.add_term("Bradley-Terry", "Bradley-Terry Model",
               "偏好模型: P(A > B) = sigmoid(score_A - score_B)")
    b.add_term("KL Divergence", "Kullback-Leibler Divergence",
               "衡量两个概率分布差异的度量，用作 RLHF 中的正则化项")
    b.add_term("Reward Hacking", "Reward Hacking",
               "策略利用 reward model 的缺陷，生成高分但无意义的输出")
    b.add_term("Knowledge Distillation", "Knowledge Distillation",
               "将大 teacher 模型的知识通过 soft targets 转移到小 student 模型")
    b.add_term("Dark Knowledge", "Dark Knowledge",
               "高温 soft probability 分布中揭示的类间关系")

    # ===== Section 1: RLHF Three-Stage Pipeline =====
    b.add_section("1. RLHF: 三阶段 Pipeline", [
        "### 宏观图景",
        "",
        "预训练 LLM 只是一个\"下一个 token 预测器\"，不知道什么是有帮助的、安全的、诚实的回答。"
        "RLHF 的目标是把它变成一个**对齐的助手**。",
        "",
        "```\nPretrained LLM -> [Stage 1: SFT] -> [Stage 2: Reward Model] -> [Stage 3: PPO] -> Aligned Model\n```",
        "",
        "### Stage 1: Supervised Fine-Tuning (SFT)",
        "",
        "**目标:** 教模型回答问题的格式和风格。",
        "",
        "**输入数据:** (prompt, 人工编写的理想回答) 对",
        "",
        FormulaBlock(
            latex=r"L_{\text{SFT}} = -\mathbb{E}_{(x,y) \sim D_{\text{demo}}} \left[ \sum_t \log \pi_{\text{SFT}}(y_t \mid x, y_{<t}) \right]",
            explanation="**损失函数:** 标准 next-token cross-entropy",
        ),
        "**直觉:** SFT 不改变算法，只改变数据 -- 用高质量示范数据微调，让模型学会\"收到指令后应该输出什么样的格式和内容\"。",
        "",
        "**输出:** $\\pi_{\\text{SFT}}$ (SFT 策略)，作为后续阶段的起点。",
        "",
        "---",
        "",
        "### Stage 2: Reward Model Training",
        "",
        "**目标:** 训练一个\"裁判\"来评估回答质量。",
        "",
        "**核心问题:** 无法用公式定义\"好的回答\"，但人类可以轻松比较两个回答。",
        "",
        "**输入数据:** (prompt x, winner $y_w$, loser $y_l$)，人类标注 $y_w \\succ y_l$",
        "",
        FormulaBlock(
            latex=r"P(y_w \succ y_l \mid x) = \sigma\bigl( r_\phi(x, y_w) - r_\phi(x, y_l) \bigr)",
            explanation="**Bradley-Terry 偏好模型:**",
        ),
        "- $r_\\phi$: 打分函数，输入 (prompt, response)，输出标量分数",
        "- $\\sigma$: sigmoid 函数",
        "- **关键洞察: 只有分数的差值有意义**，绝对值无所谓 (r=5 vs r=3 等价于 r=105 vs r=103)",
        "",
        FormulaBlock(
            latex=r"L_{\text{RM}} = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma\bigl( r_\phi(x, y_w) - r_\phi(x, y_l) \bigr) \right]",
            explanation="**损失函数:** 最大化观察到的偏好的对数似然",
        ),
        "**架构实现:** 将 SFT 模型的 LM head (输出词表大小向量) 替换为 scalar head (输出一个数字)。",
        "",
        "---",
        "",
        "### Stage 3: PPO Optimization",
        "",
        "**目标:** 用裁判的分数指导模型生成更好的回答，同时不跑太偏。",
        "",
        FormulaBlock(
            latex=r"\max_{\pi_\theta} \; \mathbb{E}_{x \sim D,\; y \sim \pi_\theta(\cdot|x)} \left[ r_\phi(x, y) - \beta \cdot D_{\text{KL}}\bigl( \pi_\theta(\cdot|x) \,\|\, \pi_{\text{SFT}}(\cdot|x) \bigr) \right]",
            explanation="**RLHF 优化目标:**",
        ),
        "两部分之间存在**张力**:",
        "",
        "| 项 | 作用 | 没有它会怎样 |\n"
        "| --- | --- | --- |\n"
        "| $r_\\phi(x, y)$ | 最大化 reward，让模型追求高分 | 模型不更新 |\n"
        "| $-\\beta \\cdot D_{\\text{KL}}$ | 约束策略不离 $\\pi_{\\text{SFT}}$ 太远 | Reward hacking: 生成高分但无意义的 gibberish |",
        "",
        "**$\\beta$ 的权衡:**",
        "- $\\beta$ 太小 -> 容易 reward hacking",
        "- $\\beta$ 太大 -> 模型几乎不更新，等同于 SFT",
        "",
        "#### Reward Hacking 的直觉",
        "",
        "Reward model 是从有限数据训练的近似函数，必然有\"盲区\"。没有 KL 约束，策略模型会通过梯度下降找到这些盲区"
        " -- 生成人类看来是胡言乱语、但 reward model 给出异常高分的输出。",
        "",
        "**类比:** KL 惩罚就像\"你的答案不能跟正常学生差太远\"，防止模型找到考官的评分漏洞。",
        "",
        "#### PPO Clip 机制",
        "",
        FormulaBlock(
            latex=r"L_{\text{PPO}} = \mathbb{E}_t \left[ \min\!\left( \frac{\pi_\theta}{\pi_{\text{old}}} \cdot A_t, \;\; \text{clip}\!\left(\frac{\pi_\theta}{\pi_{\text{old}}},\, 1{-}\varepsilon,\, 1{+}\varepsilon\right) \cdot A_t \right) \right]",
            explanation="PPO 使用 clipped surrogate objective 限制每步更新幅度:",
        ),
        "| 符号 | 含义 |\n"
        "| --- | --- |\n"
        "| $\\pi_\\theta / \\pi_{\\text{old}}$ | 概率比: 当前策略 vs 上一轮策略在该动作上的概率比 |\n"
        "| $A_t$ | 优势函数: 该动作比平均水平好多少 (>0 好, <0 差) |\n"
        "| $\\varepsilon \\approx 0.2$ | Clip 范围，限制概率比在 [0.8, 1.2] |",
        "",
        "**min 的作用:**",
        "- $A_t > 0$ (好动作): 想增加概率，但 clip 限制增幅不超过 $1+\\varepsilon$",
        "- $A_t < 0$ (坏动作): 想降低概率，但 clip 限制降幅不超过 $1-\\varepsilon$",
        "- **本质: 每步更新不要太大，保持训练稳定**",
        "",
        "#### PPO 阶段需要 4 个模型",
        "",
        "| 模型 | 角色 | 状态 |\n"
        "| --- | --- | --- |\n"
        "| Policy model ($\\pi_\\theta$) | 正在被训练的策略 | 训练中 |\n"
        "| Reference model ($\\pi_{\\text{SFT}}$) | 计算 KL 散度的基准 | 冻结 |\n"
        "| Reward model ($r_\\phi$) | 给生成的回答打分 | 冻结 |\n"
        "| Value model | 估计状态价值，计算 advantage $A_t$ | 训练中 |",
        "",
        "> 这就是 RLHF GPU 内存需求极高的原因。7B 模型 x 4 = 56GB 参数 (FP16)，加上优化器和激活值更多。",
        "",
        "---",
        "",
        "### 三阶段数据流总结",
        "",
        "| Stage | 输入数据 | 损失函数 | 训练的模型 | 输出 |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| 1 SFT | (prompt, 示范回答) | Cross-Entropy | 预训练 LLM | $\\pi_{\\text{SFT}}$ |\n"
        "| 2 RM | (prompt, $y_w \\succ y_l$) | Bradley-Terry NLL | SFT + scalar head | $r_\\phi$ |\n"
        "| 3 PPO | 在线生成 + RM 打分 | Reward - $\\beta \\cdot$ KL (PPO clip) | 策略 $\\pi_\\theta$ | Aligned model |",
        "",
        "**关键特征: Stage 3 是 online 的** -- 策略不断生成新回答，RM 不断评分，策略不断更新。",
    ])

    # ===== Section 2: DPO =====
    b.add_section("2. DPO: Direct Preference Optimization", [
        "### 动机",
        "",
        "RLHF 的痛点: 4 个模型同时在 GPU、训练不稳定 (PPO 超参多)、reward hacking 风险。",
        "",
        "**DPO 的核心问题:** 能否跳过 reward model 和 RL，直接从偏好数据优化策略？",
        "",
        "答案: 可以，且推导是精确的代数变换，无任何近似。",
        "",
        "---",
        "",
        "### 完整推导 (四步)",
        "",
        "#### 第一步: 求 RLHF 目标的最优策略 (闭式解)",
        "",
        "RLHF 目标展开 KL 散度后:",
        "",
        FormulaBlock(
            latex=r"\max_\pi \; \mathbb{E}_{y \sim \pi} \left[ r(x,y) - \beta \cdot \log \pi(y|x) + \beta \cdot \log \pi_{\text{ref}}(y|x) \right]",
            explanation="",
        ),
        "这是带熵正则化的优化问题，用拉格朗日乘子法 (约束 $\\sum_y \\pi(y|x) = 1$) 求解，闭式解为:",
        "",
        FormulaBlock(
            latex=r"\pi^*(y|x) = \pi_{\text{ref}}(y|x) \cdot \frac{\exp\bigl( r(x,y) / \beta \bigr)}{Z(x)}",
            explanation="",
        ),
        "其中 $Z(x) = \\sum_y \\pi_{\\text{ref}}(y|x) \\cdot \\exp(r(x,y)/\\beta)$ 是归一化常数。",
        "",
        "**直觉:** $\\pi_{\\text{ref}}$ 是基础分布，reward 高的 y 被 $\\exp(r/\\beta)$ 放大概率，$Z(x)$ 确保概率和为 1。",
        "",
        "- $\\beta$ 大 -> $r/\\beta$ 小 -> $\\pi^* \\approx \\pi_{\\text{ref}}$ (保守)",
        "- $\\beta$ 小 -> $r/\\beta$ 大 -> $\\pi^*$ 激进追求高 reward",
        "",
        "#### 第二步: 反解出 reward",
        "",
        "对闭式解两边取 log 并移项:",
        "",
        FormulaBlock(
            latex=r"r(x,y) = \beta \cdot \log \frac{\pi^*(y|x)}{\pi_{\text{ref}}(y|x)} + \beta \cdot \log Z(x)",
            explanation="",
        ),
        "**意义:** reward 可用\"策略与参考策略的对数概率比\"表达。$\\beta \\cdot \\log Z(x)$ 是只依赖 prompt x 的常数项。",
        "",
        "#### 第三步: 代入 Bradley-Terry，Z(x) 消掉",
        "",
        "将 reward 表达式代入 $P(y_w \\succ y_l) = \\sigma(r(y_w) - r(y_l))$:",
        "",
        "```\nr(y_w) - r(y_l) = beta * log(pi*/pi_ref)(y_w) + beta * log Z(x)\n"
        "                 - beta * log(pi*/pi_ref)(y_l) - beta * log Z(x)\n```",
        "",
        "**$+\\beta \\cdot \\log Z(x)$ 和 $-\\beta \\cdot \\log Z(x)$ 完美对消!**",
        "",
        "$Z(x)$ 消掉的原因: 它只依赖于 prompt x，对同一 x 下的 $y_w$ 和 $y_l$ 是同一个常数，差值中自然消失。",
        "",
        FormulaBlock(
            latex=r"P(y_w \succ y_l) = \sigma\!\left( \beta \cdot \left[ \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right] \right)",
            explanation="结果:",
        ),
        "#### 第四步: 取负对数似然 -> DPO Loss",
        "",
        FormulaBlock(
            latex=r"L_{\text{DPO}} = -\mathbb{E} \left[ \log \sigma\!\left( \beta \cdot \left( \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)} \right) \right) \right]",
            explanation="",
        ),
        "**简记:** 定义 $\\Delta(y) = \\log \\pi_\\theta(y|x) - \\log \\pi_{\\text{ref}}(y|x)$，则:",
        "",
        FormulaBlock(
            latex=r"L_{\text{DPO}} = -\mathbb{E} \left[ \log \sigma\bigl( \beta \cdot ( \Delta(y_w) - \Delta(y_l) ) \bigr) \right]",
            explanation="",
        ),
        "> 与 $L_{\\text{RM}} = -\\mathbb{E}[\\log \\sigma(r(y_w) - r(y_l))]$ 形式几乎一样! 只是把显式 reward score 替换为隐式 log-probability ratio。",
        "",
        "---",
        "",
        "### DPO 梯度直觉",
        "",
        "DPO 梯度同时做两件事:",
        "",
        "- **推高 $\\pi_\\theta(y_w|x)$** (让 winner 更可能)",
        "- **压低 $\\pi_\\theta(y_l|x)$** (让 loser 更不可能)",
        "",
        "梯度大小是**自适应的**:",
        "",
        "| 当前模型状态 | $\\sigma$ 输入 | 梯度大小 | 含义 |\n"
        "| --- | --- | --- | --- |\n"
        "| 已正确偏好 $y_w$ ($\\Delta(y_w) >> \\Delta(y_l)$) | 大正数 -> $\\sigma \\approx 1$ | 很小 | 已经学对，无需大幅调整 |\n"
        "| 错误偏好 $y_l$ ($\\Delta(y_l) > \\Delta(y_w)$) | 负数 -> $\\sigma << 1$ | 很大 | 判断错误，需强力纠正 |",
        "",
        "> 这与交叉熵行为一致 -- 对错误预测惩罚更重，这也是 DPO 比 PPO 稳定得多的原因。",
        "",
        "---",
        "",
        "### 隐式 Reward Model",
        "",
        "**常见误解:** \"DPO 完全没有 reward model\"",
        "",
        "**纠正:** DPO 有**隐式** reward model，训练完后可提取:",
        "",
        FormulaBlock(
            latex=r"r(x, y) = \beta \cdot \log \frac{\pi_\theta(y|x)}{\pi_{\text{ref}}(y|x)}",
            explanation="",
        ),
        "DPO 训练出的策略**同时也是一个 reward model** -- 优雅的副产品。",
    ])

    # ===== Section 3: DPO vs RLHF =====
    b.add_section("3. DPO vs RLHF 对比", [
        "### Pipeline 对比",
        "",
        "```\nRLHF:  Pretrained -> SFT -> Reward Model -> PPO -> Aligned\n"
        "       [3 stages]   [4 models at train time]\n\n"
        "DPO:   Pretrained -> SFT -> DPO Loss -> Aligned\n"
        "       [2 stages]   [2 models at train time]\n```",
        "",
        "### 数据流对比",
        "",
        "- **RLHF:** 偏好数据 -> 训练显式 RM -> RM 给 PPO **在线**生成的回答打分 -> 更新策略",
        "- **DPO:** 偏好数据 -> 直接用偏好数据上的分类损失更新策略 (**离线**，固定数据集)",
        "",
        "### 多维度对比",
        "",
        "| 维度 | RLHF (PPO) | DPO |\n"
        "| --- | --- | --- |\n"
        "| Pipeline 复杂度 | 3 stages, 4 models | 2 stages, 2 models |\n"
        "| GPU 内存 | 极高 | 中等 |\n"
        "| 训练稳定性 | 脆弱 (RL 超参敏感) | 稳定 (类交叉熵损失) |\n"
        "| 超参数 | PPO clip, LRs, GAE lambda, KL coeff | 基本只有 $\\beta$ |\n"
        "| Reward hacking 风险 | 较高 (显式 RM 可被利用) | 较低 (无显式 RM) |\n"
        "| 在线探索 | PPO 生成新轨迹 | 离线，固定数据集 |\n"
        "| 迭代改进 | 容易 (重新生成、重新排序) | 较难 (需要新偏好数据) |\n"
        "| 性能上限 | 更高 (好 RM + 充足算力) | 对多数任务可比 |\n"
        "| 工业应用 | OpenAI (GPT-4 早期), Anthropic | Meta (Llama 2+), 大部分开源模型 |",
        "",
        "### 选择指南",
        "",
        "- **选 DPO:** 算力有限、需要简单 pipeline、单轮对齐、已有离线偏好数据",
        "- **选 RLHF:** 大算力预算、需要迭代自我改进、需要在线探索、reward model 还有其他用途 (过滤、排序)",
    ])

    # ===== Section 4: Variants =====
    b.add_section("4. 变体与扩展", [
        "### RLHF 变体",
        "",
        "| 方法 | 核心思想 | 重要程度 |\n"
        "| --- | --- | --- |\n"
        "| **GRPO** | 去掉 value model: 同一 prompt 生成一组回答，用组内 reward 均值作 baseline 计算 advantage。DeepSeek 采用 | 高 |\n"
        "| **RLAIF** (Constitutional AI) | 用 AI 代替人类生成偏好标注，基于预定义\"宪法原则\"。解决标注成本和可扩展性问题。Anthropic 提出 | 高 |\n"
        "| **RAFT** | 用 RM 筛选高分回答做 SFT，完全跳过 RL，RM 当筛选器而非优化信号 | 中 |\n"
        "| **ReMax** | REINFORCE + baseline 替代 PPO，降低实现复杂度 | 低 |",
        "",
        "### DPO 变体",
        "",
        "| 方法 | 核心改进 | 解决的问题 |\n"
        "| --- | --- | --- |\n"
        "| **KTO** | 用 binary (好/差) 标签替代成对比较 | 实际中常只有 unpaired 反馈，无成对数据 |\n"
        "| **SimPO** | 去掉 reference model，用序列长度归一化 log-prob 替代 | 2 个模型 -> 1 个模型 |\n"
        "| **IPO** | log-sigmoid -> squared hinge loss | 防止在偏好数据上过拟合 |\n"
        "| **ORPO** | SFT + 偏好优化合并为一个阶段 | 连 Stage 1 都省了 |",
    ])

    # ===== Section 5: LLM Distillation =====
    b.add_section("5. LLM 知识蒸馏 (Distillation)", [
        "### 动机",
        "",
        "与 RLHF/DPO 方向不同:",
        "",
        "- **RLHF/DPO** 解决\"方向\"问题 -> 让模型的行为**对齐**人类偏好",
        "- **Distillation** 解决\"效率\"问题 -> 在保持能力的前提下**压缩**模型",
        "",
        "实际工业流程中两者经常组合: 先对齐大模型，再蒸馏成小模型部署。",
        "",
        "---",
        "",
        "### Dark Knowledge (核心直觉)",
        "",
        "以图像分类为例，teacher 对一张猫的图片输出:",
        "",
        "```\ncat: 90%,  dog: 8%,  car: 2%\n```",
        "",
        "| 目标类型 | student 学到的信息 |\n"
        "| --- | --- |\n"
        "| Hard label (cat=1, 其余=0) | \"这是猫\" -- 仅此而已 |\n"
        "| Soft label (90/8/2) | \"这是猫，而且猫和狗在视觉上相似(8%)，猫和车完全不像(2%)\" |",
        "",
        "**类间关系**就是 dark knowledge -- 隐藏在 soft probability 中、hard label 永远无法传达的信息。",
        "",
        "---",
        "",
        "### Temperature 的作用",
        "",
        FormulaBlock(
            latex=r"p_i^{(T)} = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}",
            explanation="",
        ),
        "| T 值 | 分布特征 | 效果 |\n"
        "| --- | --- | --- |\n"
        "| T = 1 | 尖锐: top class ~99%，其余 ~0% | Dark knowledge 被\"淹没\" |\n"
        "| T = 2~10 | 平滑: 类间差异被放大 | 最优范围，充分传递 dark knowledge |\n"
        "| T -> inf | 趋近均匀分布 | 判别信息丢失，反而变差 |",
        "",
        "> **常见误解:** \"T 越高越好\" -> 错! 最优 T 通常在 2-10，需在验证集上调优。",
        "",
        "---",
        "",
        "### 蒸馏损失函数",
        "",
        FormulaBlock(
            latex=r"L_{\text{KD}} = \alpha \cdot T^2 \cdot D_{\text{KL}}\bigl( p_{\text{teacher}}^{(T)} \,\|\, p_{\text{student}}^{(T)} \bigr) + (1-\alpha) \cdot L_{\text{CE}}(y,\, p_{\text{student}}^{(1)})",
            explanation="",
        ),
        "| 项 | 作用 | 参数说明 |\n"
        "| --- | --- | --- |\n"
        "| Soft target loss | 让 student 匹配 teacher 的 soft 分布 -> dark knowledge 传递通道 | T: 温度; $T^2$ 补偿高温下梯度幅度缩小 |\n"
        "| Hard target loss | 标准交叉熵，保证不偏离正确答案 | 用 T=1 的正常 softmax |\n"
        "| $\\alpha$ | 两项权重 | 通常 0.5~0.9，soft target 权重更大 |",
        "",
        "**$T^2$ 校正因子的原因:** 温度升高后 softmax 变平坦，梯度幅度缩小。$T^2$ 补偿这个缩小，保持梯度量级稳定。",
        "",
        "---",
        "",
        "### LLM 特有的蒸馏策略",
        "",
        "| 策略 | 原理 | 适用场景 |\n"
        "| --- | --- | --- |\n"
        "| **Sequence-level KD** | Teacher 生成回答 -> student 做 SFT。最常用，不需对齐词表 | Alpaca, Vicuna 等开源模型 |\n"
        "| **Logit distillation** | 逐 token 匹配 teacher/student 输出分布。效果最好，但需共享词表 | 同架构族蒸馏 |\n"
        "| **Feature distillation** | 匹配中间层 hidden states (如 teacher 第 60 层 -> student 第 24 层) | 需设计层对应关系 |\n"
        "| **Step-by-step distillation** | Teacher 生成推理链，student 学推理过程 + 最终答案 | 数学、代码任务 |",
        "",
        "---",
        "",
        "### 70B -> 7B 实际方案",
        "",
        "#### 架构选择",
        "",
        "| 维度 | 决策 |\n"
        "| --- | --- |\n"
        "| Tokenizer & 词表 | 保持相同 (logit KD 的前提) |\n"
        "| 层数 | 减少: 80 -> 32 |\n"
        "| Hidden dim | 减少: 8192 -> 4096 |\n"
        "| 注意力头数 | 相应减少 |\n"
        "| 上下文长度 | 保持 |",
        "",
        "#### 训练配方",
        "",
        "- 用 teacher 对海量 prompt 生成高质量回答",
        "- 混合目标训练: logit KD + sequence-level KD",
        "- 数据量: 通常比标准预训练多 **10-50x** tokens",
        "",
        "#### 内存估算",
        "",
        "| 组件 | 参数量 | FP16 内存 | 含优化器 |\n"
        "| --- | --- | --- | --- |\n"
        "| 70B teacher (推理) | 70B | ~140 GB | N/A (冻结) |\n"
        "| 7B student (训练) | 7B | ~14 GB | ~56 GB (AdamW 4x) |\n"
        "| **总计最低** | -- | -- | **~196 GB (约 3x A100 80GB)** |",
        "",
        "#### 质量衡量指标",
        "",
        "| 指标 | 含义 | 目标 |\n"
        "| --- | --- | --- |\n"
        "| Perplexity gap | Student PPL 与 teacher PPL 的差距 | 越小越好 |\n"
        "| Task accuracy retention | 保留了 teacher 多少准确率 | > 90% |\n"
        "| Latency speedup | 推理 FLOPs 比 | 70B/7B 约 10x |\n"
        "| KL divergence | 在 held-out 数据上的分布相似度 | 越小越好 |",
    ])

    # ===== Section 6: Error Corrections =====
    b.add_section("6. 常见误解纠正", [
        "| # | 误解 | 纠正 |\n"
        "| --- | --- | --- |\n"
        "| 1 | \"DPO 完全没有 reward model\" | DPO 有**隐式** RM: $r(x,y) = \\beta \\cdot \\log(\\pi_\\theta / \\pi_{\\text{ref}})$。关键是不需要**单独训练**一个 RM |\n"
        "| 2 | \"RLHF 需要数百万偏好标注\" | RM 通常用 50K-500K 对比对。InstructGPT 用了 ~33K prompt + ~40K 对比 |\n"
        "| 3 | \"KL 惩罚只是防遗忘\" | **主要目的是防 reward hacking**，防遗忘是次要收益 |\n"
        "| 4 | \"蒸馏只能用相同架构\" | 跨架构蒸馏可行 (如 GPT -> encoder-decoder)。logit KD 需共享词表，sequence-level KD 无此限制 |\n"
        "| 5 | \"温度越高蒸馏效果越好\" | 最优 T 在 [2, 10]。太高分布趋近均匀，判别信息丢失 |",
    ])

    # ===== Section 7: Self-Check =====
    b.add_section("7. Self-Check Questions + 参考答案", [
        "### Q1: 画出 RLHF 三阶段 pipeline，每阶段说出输入数据、损失函数、训练的模型",
        "",
        "- [ ] **Q1:** 画出 RLHF 三阶段 pipeline，每阶段说出输入数据、损失函数、训练的模型",
        "",
        "> **Stage 1 SFT:** 输入 (prompt, 示范回答)，损失 cross-entropy，训练预训练 LLM -> $\\pi_{\\text{SFT}}$。"
        " **Stage 2 RM:** 输入 (prompt, $y_w \\succ y_l$)，损失 Bradley-Terry NLL，训练 SFT+scalar head -> $r_\\phi$。"
        " **Stage 3 PPO:** 输入在线生成 + RM 打分，目标 max E[r - $\\beta$ KL]，训练 $\\pi_\\theta$ (需 4 个模型同时在 GPU)。",
        "",
        "### Q2: 默写 DPO loss，解释 Z(x) 为何消掉",
        "",
        "- [ ] **Q2:** 默写 DPO loss，解释 Z(x) 为何消掉",
        "",
        "> $L_{\\text{DPO}} = -\\mathbb{E}[\\log \\sigma(\\beta \\cdot (\\log(\\pi_\\theta(y_w|x)/\\pi_{\\text{ref}}(y_w|x)) - \\log(\\pi_\\theta(y_l|x)/\\pi_{\\text{ref}}(y_l|x))))]$。"
        " Z(x) 消掉的原因: 从最优策略反解 reward 得到 $r = \\beta \\cdot \\log(\\pi/\\pi_{\\text{ref}}) + \\beta \\cdot \\log Z(x)$。"
        " 代入 Bradley-Terry 需要 $r(y_w) - r(y_l)$，$\\beta \\cdot \\log Z(x)$ 只依赖 prompt x，是常数，做差时一正一负抵消。",
        "",
        "### Q3: 70B teacher -> 7B student 蒸馏方案",
        "",
        "- [ ] **Q3:** 70B teacher -> 7B student 蒸馏方案",
        "",
        "> 损失 $L_{\\text{KD}} = \\alpha \\cdot T^2 \\cdot KL + (1-\\alpha) \\cdot CE$; 温度 T=2~10 调优; 保持词表，减层数/hidden_dim;"
        " 数据量 10-50x 标准预训练; 需 ~196GB 显存 (约 3x A100 80GB); 目标 accuracy retention > 90%。",
        "",
        "### Q4: 5 维度对比 DPO vs RLHF",
        "",
        "- [ ] **Q4:** 5 维度对比 DPO vs RLHF",
        "",
        "> 计算成本 DPO 低 (2 vs 4 模型); 稳定性 DPO 优 (分类损失 vs RL); 性能上限 RLHF 高 (在线探索);"
        " 数据 DPO 只需离线偏好对，RLHF Stage 3 在线生成; 在线探索 RLHF 有 DPO 无 -- 这是最根本区别。",
        "",
        "### Q5: Reward hacking 是什么，KL 惩罚如何防止?",
        "",
        "- [ ] **Q5:** Reward hacking 是什么，KL 惩罚如何防止?",
        "",
        "> 策略利用 RM 缺陷生成高分但无意义输出。KL 惩罚约束策略不离 $\\pi_{\\text{SFT}}$ 太远，"
        " $\\pi_{\\text{SFT}}$ 生成\"正常自然语言\"，即使 RM 对 gibberish 给高分，KL 惩罚也会因偏离太远而惩罚策略。"
        " 与 Diffusion 中 CFG guidance scale 的类比: 都在控制 **质量/对齐 vs 多样性/自然度** 的 trade-off。",
    ])

    # ===== Section 8: Formula Cheat Sheet =====
    b.add_section("8. 公式速查卡", [
        "```\nRLHF Pipeline:  Pretrained -> SFT -> Reward Model -> PPO -> Aligned Model\n\n"
        "SFT Loss:       L = -E[ sum_t log pi(y_t | x, y_{<t}) ]\n\n"
        "RM Loss:        L = -E[ log sigma( r(y_w) - r(y_l) ) ]               (Bradley-Terry)\n\n"
        "RLHF Obj:       max E[ r(x,y) - beta * KL(pi || pi_ref) ]\n\n"
        "Optimal Policy: pi*(y|x) = pi_ref(y|x) * exp(r(x,y)/beta) / Z(x)\n\n"
        "Implicit RM:    r(x,y) = beta * log( pi(y|x) / pi_ref(y|x) )\n\n"
        "DPO Loss:       L = -E[ log sigma( beta * (log(pi/pi_ref)(y_w) - log(pi/pi_ref)(y_l)) ) ]\n\n"
        "PPO Clip:       L = E[ min( (pi/pi_old)*A,  clip(pi/pi_old, 1-eps, 1+eps)*A ) ]\n\n"
        "KD Loss:        L = alpha*T^2*KL(p_teacher^T || p_student^T) + (1-alpha)*CE(y, p_student^1)\n\n"
        "Temperature:    p_i^(T) = exp(z_i/T) / sum(exp(z_j/T))               (T>1 = softer)\n```",
    ])

    return b


def main() -> None:
    builder = build_day2_chinese()
    content = builder.build()
    print(f"Generated content: {len(content)} chars")

    # Validate
    warnings = builder.validate(content)
    if warnings:
        print(f"WARNINGS: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("Validation: PASS (0 warnings)")

    # Save to DB -- update existing doc id=12
    db_path = str(DB_PATH)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get old length for comparison
    cur.execute("SELECT LENGTH(content) FROM company_documents WHERE id=?", (DOC_ID,))
    old_len = cur.fetchone()[0]

    # Update content and title
    new_title = "Adobe Prep Day2: RLHF/DPO Alignment + LLM Distillation"
    cur.execute(
        "UPDATE company_documents SET content=?, title=? WHERE id=?",
        (content, new_title, DOC_ID),
    )
    conn.commit()

    # Verify
    cur.execute("SELECT LENGTH(content) FROM company_documents WHERE id=?", (DOC_ID,))
    new_len = cur.fetchone()[0]
    print(f"Updated doc id={DOC_ID}: {old_len} -> {new_len} chars ({new_len - old_len:+d})")

    # Verify tables render (no blank lines between table rows)
    lines = content.split("\n")
    table_issues = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and i + 1 < len(lines):
            next_line = lines[i + 1]
            if next_line.strip() == "" and i + 2 < len(lines) and lines[i + 2].strip().startswith("|"):
                table_issues += 1
    print(f"Table rendering check: {table_issues} blank-line issues")

    # Count formulas
    formula_count = content.count("$$")
    print(f"Formula blocks: {formula_count // 2} (double-dollar pairs)")

    # Count checklist items
    checklist_count = content.count("- [ ]")
    print(f"Checklist items: {checklist_count}")

    # Count blockquote answers
    answer_count = len([l for l in lines if l.strip().startswith(">")])
    print(f"Blockquote answers: {answer_count}")

    conn.close()


if __name__ == "__main__":
    main()
