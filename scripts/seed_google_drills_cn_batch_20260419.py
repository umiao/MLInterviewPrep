"""Batch-upgrade 5 Google R1 drill docs (55, 56, 60, 64, 67) to >=50% CN prose.

Per task T-P2-533. Uniform Chinese-prose uplift pass:
- Prose: CN-ify English phrases that still leaked through prior batches
- Formulas / code / pseudocode / table cells: untouched
- Section headings: untouched (English)
- Idempotent: per-doc sentinel `<!-- CN_BATCH_20260419 -->` skips re-application

Already-passing docs (61, 62, 63, 65, 68, 69, 72) are declared in PASSING_DOCS
and verified post-run only (no content edits).

Verification: every one of the 12 drill docs must report prose_cjk >= 0.50
after this script runs.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- CN_BATCH_20260419 -->"

# Docs the batch rewrites (were below 50% prose_cjk at start of T-P2-533)
REWRITE_IDS = [55, 56, 60, 64, 67]

# Docs already above 50% -- do not touch, but verify post-run
PASSING_IDS = [61, 62, 63, 65, 68, 69, 72]

ALL_DRILL_IDS = sorted(REWRITE_IDS + PASSING_IDS)


def prose_only(content: str) -> str:
    p = re.sub(r"\$\$.*?\$\$", "", content, flags=re.DOTALL)
    p = re.sub(r"\$[^\$\n]*?\$", "", p)
    p = re.sub(r"```.*?```", "", p, flags=re.DOTALL)
    p = re.sub(r"`[^`]*`", "", p)
    p = re.sub(r"^\|.*$", "", p, flags=re.MULTILINE)
    p = re.sub(r"^#+\s.*$", "", p, flags=re.MULTILINE)
    p = re.sub(r"<!--.*?-->", "", p, flags=re.DOTALL)
    return p


def cjk_ratio(content: str) -> tuple[float, int, int]:
    prose = prose_only(content)
    cjk = sum(1 for c in prose if "\u4e00" <= c <= "\u9fff")
    latin = sum(1 for c in prose if c.isalpha() and ord(c) < 128)
    total = cjk + latin
    return (cjk / total if total else 0.0, cjk, latin)


# -----------------------------------------------------------------------------
# Per-doc prose substitutions. Each pair is (old, new) applied via str.replace
# ONCE on the whole content. Substitution texts are crafted to land ONLY in
# prose segments; they do not collide with formula bodies, code fences,
# headings, table cells, or HTML comments.
# -----------------------------------------------------------------------------

SUBS: dict[int, list[tuple[str, str]]] = {}

# ---- DOC 55: Regularization Deep Dive -------------------------------------
SUBS[55] = [
    (
        "本 drill 服务 Google R1 面试的**口述练习**：L1 / L2 几何推导、KKT、soft-thresholding、Bayesian prior、AdamW 等核心内容已固化到 canonical hub。此处只保留 **drill-specific** 的战术要点——dropout、early stopping、data augmentation、以及 7 法全景表与 30 秒口述自测。",
        "本训练面向 Google R1 面试的**口述演练**：L1 / L2 几何推导、KKT 条件、软阈值 (soft-thresholding)、贝叶斯先验 (Bayesian prior)、AdamW 等核心推导均已固化到规范总库 (canonical hub)。此处仅保留**针对本训练独有**的战术要点——**Dropout** (丢弃)、**Early Stopping** (早停)、**Data Augmentation** (数据增广) 三法细节，加 7 法全景表与 30 秒口述自测。",
    ),
    (
        "- Canonical hub: [Regularization](/framework/195)（务必先过一遍）\n- 神经网络训练循环（forward / backward pass）\n- 随机采样与蒙特卡洛的基本直觉",
        "- 规范总库入口：[Regularization](/framework/195)（务必先过一遍）\n- 神经网络训练循环：前向传播 (forward pass) 与反向传播 (backward pass)\n- 随机采样与蒙特卡洛方法的基本直觉",
    ),
    (
        "训练阶段：每次前向把每个单元以概率 $p$ 置零。推理阶段：启用全部单元，activation 乘以 $(1-p)$；或训练时用 **inverted dropout** 直接除以 $(1-p)$，推理不变。",
        "训练阶段：每次前向传播将每个神经单元以概率 $p$ 随机置零。推理阶段：启用全部单元，将激活值乘以 $(1-p)$ 以补偿期望；或训练时采用**反向丢弃** (Inverted Dropout) 的写法直接除以 $(1-p)$，推理阶段保持不变。",
    ),
    (
        "**集成视角（Srivastava 2014）**：$n$ 个单元 -> $2^n$ 个 thinned networks。平均预测近似等于一个指数级 ensemble 的平均。",
        "**集成视角（Srivastava 2014）**：$n$ 个单元对应 $2^n$ 个稀疏子网 (thinned networks)。训练时每步等价于采样出一个子网络做前向，推理时的平均预测近似等于这一指数级集成 (ensemble) 的均值。",
    ),
    (
        "**Bayesian 视角（Gal & Ghahramani 2016）**：推理时**保持 dropout 开启**，做 $T$ 次 forward，得到预测均值与不确定性。MC Dropout 的方差估计：",
        "**贝叶斯视角（Gal & Ghahramani 2016）**：推理时**保持 Dropout 处于开启状态**，重复进行 $T$ 次前向传播，得到预测均值与模型不确定性。**蒙特卡洛 Dropout** (MC Dropout) 的方差估计写作：",
    ),
    (
        '**口述捷径**："Dropout 是 $2^n$ 子网络的廉价集成；推理时不关它还能免费拿到不确定性。"',
        '**口述捷径**："Dropout 相当于 $2^n$ 个子网络的廉价集成；推理时不关掉它，还能顺带免费拿到模型不确定性估计。"',
    ),
    (
        "从 $w=0$ 起，小学习率的 GD 在权重空间画一条轨迹；**停得早就等于限制 $\\|w\\|$ 的增长**。$T$ 步 x 学习率 $\\eta$ x 梯度上界 $G_{\\max}$：",
        "从 $w=0$ 出发，采用小学习率的梯度下降 (Gradient Descent, GD) 在权重空间描出一条轨迹；**提早停止训练即等于限制 $\\|w\\|$ 的增长上界**。总共 $T$ 步、学习率为 $\\eta$、梯度模上界记为 $G_{\\max}$，则有：",
    ),
    (
        "Bishop (1995) / Sjoberg & Ljung (1995) 证明：在二次损失下，early stopping 的第 $T$ 步等价于 L2 正则 $\\lambda_{\\text{eff}} \\propto 1/(\\eta T)$。",
        "Bishop (1995) 与 Sjoberg-Ljung (1995) 已证明：在二次损失下，提前停止 (Early Stopping) 执行到第 $T$ 步时等价于一个强度为 $\\lambda_{\\text{eff}} \\propto 1/(\\eta T)$ 的 L2 正则。",
    ),
    (
        '**口述捷径**："Early stopping = 隐式 L2；步数少 = 范数小 = 正则强。免费但把优化和正则耦合在一起。"',
        '**口述捷径**："提前停止等同于隐式 L2 正则；步数越少对应权重范数越小、正则越强。好处是零额外开销，代价是把优化与正则两件事耦合到了一起。"',
    ),
    (
        "ERM 最小化的是**训练点上的平均损失**；数据增广把每个点替换为一个**邻域（vicinity）**。形式化（Chapelle 等 2000）：",
        "**经验风险最小化** (Empirical Risk Minimization, ERM) 最小化的是**训练样本点上的平均损失**；数据增广把每个训练点替换为一个**邻域** (vicinity)。形式化表述 (Chapelle 等 2000)：",
    ),
    (
        "vicinity 分布 $\\nu$ 编码领域先验：图像用 flip / crop，NLP 用 synonym replacement，Mixup 用插值。**正则化效果**：模型必须在邻域内都对，决策边界被平滑，variance 下降而 bias 不变（只要 augmentation 保标签）。",
        "邻域分布 $\\nu$ 编码领域先验：图像任务用翻转 (flip) 与裁剪 (crop)，自然语言处理 (NLP) 用同义词替换 (synonym replacement)，Mixup 则在样本对之间做插值。**正则化效果**：模型必须在整个邻域内都保持正确，决策边界被自然平滑，方差 (variance) 下降而偏差 (bias) 保持不变——前提是增广操作不会破坏标签语义。",
    ),
    (
        '**口述捷径**："Augmentation 就是在邻域上训练，不是在点上。数学上是 VRM——vicinity kernel 取代 ERM 里的 Dirac delta。"',
        '**口述捷径**："数据增广就是在邻域上训练，不是在孤立的样本点上。形式化表述即**邻域风险最小化** (Vicinal Risk Minimization, VRM)——用邻域核 (vicinity kernel) 取代 ERM 里的 Dirac delta 点测度。"',
    ),
    (
        '"Adam 的 $v_t$ 把 L2 梯度按历史自适应地缩小，所以正则强度不均匀；AdamW 把 decay 挪到 Adam 步之外，所有参数均匀 $(1-\\eta\\lambda)$。transformer 用 AdamW。"',
        '"Adam 的二阶动量 $v_t$ 会把 L2 梯度按历史自适应地缩小，导致每个参数的正则强度不均匀；AdamW 将权重衰减 (weight decay) 挪到 Adam 主步之外，所有参数都乘以统一的 $(1-\\eta\\lambda)$。Transformer 类架构默认采用 AdamW。"',
    ),
    (
        "- [ ] L1 稀疏的三层解释（几何 / 代数 / Bayesian）--- 指向 canonical §1/§5",
        "- [ ] L1 稀疏的三层解释（几何直觉、代数 KKT、贝叶斯先验）——详见规范总库 §1/§5",
    ),
    (
        "- [ ] L2 闭式解 $(X^\\top X+\\lambda I)^{-1}X^\\top y$ 与逐奇异值收缩 --- canonical §3",
        "- [ ] L2 闭式解 $(X^\\top X+\\lambda I)^{-1}X^\\top y$ 与逐奇异值收缩的推导——详见规范总库 §3",
    ),
    (
        "- [ ] Ridge vs Lasso 的 bias 谁更大？两者都 biased，L1 还额外把系数压到 0",
        "- [ ] 岭回归 (Ridge) 与 套索回归 (Lasso) 哪个偏差更大？两者均是有偏估计；L1 额外把部分系数精确压缩至 0",
    ),
    (
        "- [ ] Dropout = $2^n$ ensemble + MC Dropout uncertainty",
        "- [ ] Dropout 等价于 $2^n$ 子网集成，叠加 MC Dropout 不确定性估计",
    ),
    (
        "- [ ] Early stopping 是隐式 L2，$\\lambda\\propto 1/(\\eta T)$",
        "- [ ] 提前停止等同于隐式 L2 正则，有效强度 $\\lambda\\propto 1/(\\eta T)$",
    ),
    (
        "- [ ] AdamW 的一句话解释（$v_t$ 吞 L2；decay 解耦）",
        "- [ ] AdamW 的一句话解释：$v_t$ 会吞掉裸 L2；AdamW 把权重衰减从自适应步里解耦出来",
    ),
    (
        "- [ ] Data aug = VRM，vicinity kernel 取代 Dirac delta",
        "- [ ] 数据增广即 VRM，用邻域核取代 Dirac delta 点测度",
    ),
    (
        "- [ ] James-Stein：$p\\ge 3$ 时收缩估计严格优于 OLS",
        "- [ ] James-Stein 估计：在维度 $p\\ge 3$ 时，收缩估计严格优于普通最小二乘 (OLS)",
    ),
    (
        '**面试口吻收尾**："L1 / L2 的推导我画图+写 KKT+ Bayesian 三条线都能走；dropout 我用 ensemble 和 MC 两种解释；AdamW 我能说清 $v_t$ 吞 L2 这个技术细节。"',
        '**面试口吻收尾**："L1 / L2 的推导我几何画图、代数 KKT、贝叶斯先验三条路线都能走；Dropout 我用集成视角与 MC 不确定性两种解释；AdamW 这块我能说清 $v_t$ 吞掉裸 L2 这个技术细节。"',
    ),
]

# ---- DOC 56: Bias-Variance + Overfitting Diagnosis ----------------------
SUBS[56] = [
    (
        "口述战术速查。完整推导、正则理论和 double-descent 讨论都在 canonical hub。\n本文件只保留 Google R1 drill 需要的面：诊断对照表、集成方差公式、学习曲线形状、以及口述捷径。",
        "口述战术速查表。完整推导、正则理论与**双下降** (double-descent) 的讨论都放在规范总库 (canonical hub)。\n本文档只保留 Google R1 训练所需的几块：诊断对照表、集成方差公式、学习曲线形状，以及各节末尾的口述捷径。",
    ),
    (
        "复杂度-误差关系驱动所有诊断（推导见 canonical hub，这里只背一句结论）：\n\n> 模型复杂度 up  =>  Bias down、Variance up。",
        "模型复杂度与误差的关系是所有诊断动作的出发点（完整推导见规范总库，这里只记一句结论）：\n\n> 模型复杂度上升，偏差下降、方差上升。",
    ),
    (
        '**口述捷径**："Underfit 两端都高，bias 主导；overfit 是 train/test gap，variance 主导；leakage 是 test 比 train 还好，哪里一定出错了。"',
        '**口述捷径**："欠拟合是训练与测试误差两端都高，偏差主导；过拟合是训练-测试误差 gap 大，方差主导；数据泄漏是测试比训练还好，说明某处流程一定出了错。"',
    ),
    (
        "$B$ 个模型平均、两两相关系数为 $\\rho$ 时的方差：",
        "对 $B$ 个子模型做平均、两两相关系数为 $\\rho$ 时，集成方差为：",
    ),
    (
        "Bagging 的方差下限是 $\\rho\\sigma^2$。**Random Forest (随机森林)** 在每次分裂时随机选特征子集（分类常取 $m=\\sqrt{p}$、回归取 $m=p/3$）把 $\\rho$ 压低——$\\rho$ 越小、下限越低。",
        "装袋法 (Bagging) 的方差下限是 $\\rho\\sigma^2$。**随机森林** (Random Forest, RF) 在每次节点分裂时随机选取特征子集（分类常取 $m=\\sqrt{p}$、回归常取 $m=p/3$），以此把子树相关系数 $\\rho$ 压低——$\\rho$ 越小，这个下限越低。",
    ),
    (
        '**口述捷径**："Bagging 方差下限 = rho 乘 sigma 方；RF 用随机特征把 rho 压低，下限就更低。"',
        '**口述捷径**："装袋法的方差下限等于相关系数 $\\rho$ 乘以单树方差 $\\sigma^2$；随机森林靠随机特征子集把 $\\rho$ 进一步压低，整体方差下限也随之更低。"',
    ),
    (
        "**RF (Random Forest)** 和 **GBDT (Gradient Boosted Decision Trees)** 从 bias-variance 权衡的两端进攻：",
        "**随机森林** (Random Forest, RF) 与**梯度提升决策树** (Gradient Boosted Decision Trees, GBDT) 从偏差-方差权衡的两端同时进攻：",
    ),
    (
        "RF：$f(x) = \\frac{1}{B}\\sum_{b=1}^{B} T_b(x)$（深树平均）\n\nGBDT：$f(x) = \\sum_{m=1}^{M} \\eta\\,h_m(x)$（浅树在残差上累加）",
        "随机森林：$f(x) = \\frac{1}{B}\\sum_{b=1}^{B} T_b(x)$（对深树做平均）\n\n梯度提升决策树：$f(x) = \\sum_{m=1}^{M} \\eta\\,h_m(x)$（浅树在残差上逐步累加）",
    ),
    (
        '**口述捷径**："RF 是深树平均，主打降 variance；GBDT 是浅树串行堆，主打降 bias。入口相反，目的地相同。"',
        '**口述捷径**："随机森林是深树做平均，主打降方差；梯度提升决策树是浅树顺序堆叠，主打降偏差。两者入口完全相反，终点却是同一个。"',
    ),
    (
        "把训练误差和验证误差画在同一张图上，横轴是训练集大小。曲线形状直接给出诊断：",
        "把训练误差和验证误差画在同一张图上，横轴取训练集大小。两条曲线的形状直接给出诊断结论：",
    ),
    (
        "经验法则：\n\n- Train-val gap 大 => variance 问题。加数据或加正则。\n- 两条曲线都高位平台 => bias 问题。加特征或加容量。\n- Train 误差 = 0 => 记忆化红灯。加正则。\n- 曲线收敛到的水平可近似看作当前模型类下的 irreducible error。",
        "经验法则：\n\n- 训练误差与验证误差之间 gap 大，属于方差问题，处置为加数据或加正则。\n- 两条曲线都在高位形成平台，属于偏差问题，处置为加特征或加容量。\n- 训练误差等于 0，属于记忆化红灯，处置为加正则。\n- 两条曲线最终收敛到的水平，可近似视为当前模型族下的不可约误差 (irreducible error)。",
    ),
    (
        '**口述捷径**："Gap 大 = variance，加数据；两端都高 = bias，加容量；train=0、val 高 = 记忆化，加正则。"',
        '**口述捷径**："训练-验证 gap 大等于方差问题，处置是加数据；两端都偏高等于偏差问题，处置是加容量；训练误差为零、验证偏高等于记忆化，处置是加正则。"',
    ),
    (
        "- [ ] 背 $E_D[(y - \\hat{f})^2] = \\text{Bias}^2 + \\text{Var} + \\sigma^2$",
        "- [ ] 背出分解式 $E_D[(y - \\hat{f})^2] = \\text{Bias}^2 + \\text{Var} + \\sigma^2$",
    ),
    (
        "- [ ] 一句话说清三项各代表什么",
        "- [ ] 用一句话说清楚三项（偏差平方、方差、不可约噪声）各代表什么",
    ),
    (
        "- [ ] 复杂度 up => bias down、variance up（嘴上说一遍）",
        "- [ ] 复杂度上升对应偏差下降、方差上升（请在嘴上过一遍）",
    ),
    (
        "- [ ] Underfit 两端高；overfit 是 train/test 的 gap",
        "- [ ] 欠拟合是训练与测试两端误差都高；过拟合是训练与测试之间 gap 大",
    ),
    (
        "- [ ] Bagging 方差 = $\\rho\\sigma^2 + (1-\\rho)\\sigma^2/B$，下限 $\\rho\\sigma^2$",
        "- [ ] 装袋法方差 $= \\rho\\sigma^2 + (1-\\rho)\\sigma^2/B$，其下限为 $\\rho\\sigma^2$",
    ),
    (
        "- [ ] RF 用随机特征降 rho；GBDT 顺序地降 bias",
        "- [ ] 随机森林用随机特征子集把 $\\rho$ 压下来；梯度提升决策树靠顺序拟合残差把偏差压下来",
    ),
    (
        "- [ ] RF = 深树平均；GBDT = 浅树堆叠",
        "- [ ] 一句话对比：随机森林是深树做平均，梯度提升决策树是浅树做顺序堆叠",
    ),
    (
        "- [ ] 学习曲线：大 gap = variance；都高 = bias；train=0 = 记忆化",
        "- [ ] 学习曲线口诀：gap 大等于方差问题；两端都高等于偏差问题；训练误差归零等于记忆化",
    ),
]

# ---- DOC 60: LambdaRank / LambdaMART Drill -------------------------------
SUBS[60] = [
    (
        "- 有监督学习、cross-entropy 损失、sigmoid 梯度\n- Gradient Boosted Decision Trees（MART / XGBoost / LightGBM）\n- NDCG / DCG 定义（见 google_ndcg_map_mrr_drill.md 配套文档）",
        "- 有监督学习基础、交叉熵 (cross-entropy) 损失、sigmoid 函数的梯度\n- **梯度提升决策树** (Gradient Boosted Decision Trees, GBDT) 家族：MART / XGBoost / LightGBM\n- **归一化折损累计增益** (NDCG) 与**折损累计增益** (DCG) 的定义（见配套文档 google_ndcg_map_mrr_drill.md）",
    ),
    (
        "场景：query $q$ 有若干候选文档；带标签对 $(i,j)$ 满足 $y_i > y_j$。模型给出标量分数 $s_i = f(x_i)$、$s_j = f(x_j)$。目标：把 $s_i$ 推到 $s_j$ 上面。",
        "场景：一个查询 (query) $q$ 对应若干候选文档；对每个带标签的文档对 $(i,j)$ 满足 $y_i > y_j$。模型给出标量分数 $s_i = f(x_i)$ 与 $s_j = f(x_j)$。目标是把 $s_i$ 推到 $s_j$ 上方。",
    ),
    (
        "用分数差的 sigmoid 建模成对偏好：",
        "用分数差的 sigmoid 函数建模成对偏好：",
    ),
    (
        "交叉熵目标为 1（$i$ 应排在 $j$ 前面），所以损失是：",
        "将交叉熵的真实目标设为 1 （即 $i$ 理应排在 $j$ 前面），因此成对损失写作：",
    ),
    (
        "梯度（白板上一定写得出来）：\n\n对称：$s_i$ 抬、$s_j$ 压，幅度相同。",
        "梯度推导（白板上一定要能写出来）：\n\n梯度关于分数差是对称的：把 $s_i$ 向上推、把 $s_j$ 向下压，两者幅度完全一致。",
    ),
    (
        '**口述捷径**："RankNet = 对分数差的 logistic loss。梯度大小是 $1 - P_{ij}$：模型错得越离谱（$P_{ij}\\to 0$）梯度越大；模型对了就自动消失。"',
        '**口述捷径**："RankNet 就是对分数差 $s_i - s_j$ 取 logistic 损失。梯度幅度等于 $1 - P_{ij}$：模型错得越离谱（$P_{ij}\\to 0$）梯度越大；模型排对了梯度自动消失。"',
    ),
    (
        "**致命缺陷**：每对误排权重一样。交换位置 1 和位置 2 的代价等于交换位置 99 和 100，但顶部那对对用户伤害大得多。",
        "**致命缺陷**：每一对误排的权重完全相同。交换位次 1 与 2 的代价等于交换位次 99 与 100，但顶部那对误排对用户体验的伤害显然大得多。",
    ),
    (
        "诀窍：不对 NDCG 求导（argsort 是离散的），而是把 RankNet 每对的梯度乘以交换两个文档位置所造成的 $|\\Delta\\mathrm{NDCG}_{ij}|$。",
        "关键诀窍：不直接对 NDCG 求导（排序 argsort 是离散的、无梯度），而是把 RankNet 每对梯度乘以交换两个文档位置所带来的 $|\\Delta\\mathrm{NDCG}_{ij}|$ 变化量。",
    ),
    (
        "Lambda 梯度 = RankNet 方向乘交换幅度：",
        "**Lambda 伪梯度**等于 RankNet 梯度方向乘以交换带来的 NDCG 变化幅度：",
    ),
    (
        "交换后只有两个位置的 DCG 变化：",
        "位置交换后，只有两个位置上的 DCG 发生变化：",
    ),
    (
        "逐文档聚合——每个 doc 对它参与的所有对求和：\n\n$doc\\ i$ 的伪梯度。$\\lambda_i$ 为负表示分数要推高。",
        "再按文档逐个聚合——每个文档 $i$ 对所有参与的文档对求和：\n\n$\\lambda_i$ 是文档 $i$ 的聚合伪梯度。当 $\\lambda_i$ 为负时意味着该文档分数应被推高。",
    ),
    (
        "**LambdaMART** = 把 $(\\lambda_i, w_i)$ 作为 (gradient, hessian) 塞给 MART。Hessian 近似 $w_{ij} = P_{ij}(1 - P_{ij}) \\cdot |\\Delta\\mathrm{NDCG}_{ij}|$。树分裂和叶子值的算法与普通 XGBoost 完全一样——只是梯度来源换成了 LambdaRank。",
        "**LambdaMART** 做的事情是把 $(\\lambda_i, w_i)$ 作为 (梯度, 海森) 送给 MART (Multiple Additive Regression Trees)。海森近似取 $w_{ij} = P_{ij}(1 - P_{ij}) \\cdot |\\Delta\\mathrm{NDCG}_{ij}|$。树的分裂规则和叶子值计算与普通 XGBoost 完全一致——唯一区别是梯度来源换成了 LambdaRank 的伪梯度。",
    ),
    (
        "**为什么容量自动集中在 top**：位置 1 附近 $1/\\log_2(p+1)\\approx 1$，位置 100 附近只有 $\\approx 0.14$，所以同样的 label swap 在顶部产生 7 倍大的 $|\\Delta\\mathrm{NDCG}|$。**自调节收敛**：排序接近理想时 $(1 - P_{ij})$ 和 $|\\Delta\\mathrm{NDCG}_{ij}|$ 都在缩小，更新自然消失。",
        "**为什么模型容量会自动集中在头部**：位置 1 附近的位置折扣 $1/\\log_2(p+1)\\approx 1$，位置 100 附近只有约 $0.14$，因此同样的标签交换 (label swap) 在头部会产生 7 倍大小的 $|\\Delta\\mathrm{NDCG}|$。**自调节收敛特性**：当排序接近理想排序时，$(1 - P_{ij})$ 与 $|\\Delta\\mathrm{NDCG}_{ij}|$ 两者都在缩小，权重更新量自然随之衰减。",
    ),
    (
        '**口述捷径**："LambdaRank = RankNet 梯度乘以交换的 $|\\Delta\\mathrm{NDCG}|$。顶部误排的 $\\Delta\\mathrm{NDCG}$ 大、梯度占主导。LambdaMART 就是把这个伪梯度塞进 GBDT。"',
        '**口述捷径**："LambdaRank 的本质是 RankNet 梯度乘以交换导致的 $|\\Delta\\mathrm{NDCG}|$。头部误排对应的 $\\Delta\\mathrm{NDCG}$ 大、梯度占主导。LambdaMART 就是把这个伪梯度塞进梯度提升决策树里训练。"',
    ),
    (
        '三种 **LTR** 范式差在"损失的单位"：',
        '**学习排序** (Learning to Rank, LTR) 三种范式的差别在于"损失函数作用的单位"：',
    ),
    (
        "决策规则：\n\n- 如果标签本身是标量概率（click / order），从 pointwise BCE 入手。便宜、可在 doc 上并行、给的分数可校准、可直接用来 bidding 和卡阈值。\n\n- 如果只在乎排序（召回任务、候选再排），pairwise 是最小代价的升级，教模型相对偏好。\n\n- 如果有分级相关性标签且 NDCG 是头条指标，就上 listwise——生产用 LambdaMART（GBDT 栈），神经网络栈用 ListNet 或 ApproxNDCG。这类损失天生就是位置感知的。\n\n- 多任务排序场景（DoorDash / eBay feed、Etsy search）里，pointwise MTL head（pClick、pOrder、pGMV）通常线性融合成分数；纯 listwise 反而少见，因为下游 bidding 需要可校准 head。",
        "决策规则：\n\n- 若标签本身就是标量概率（点击 click、下单 order），首选逐点 BCE。它便宜、可在文档维度并行、给出的分数可校准，可直接用于出价 (bidding) 与阈值卡位。\n\n- 若只在乎排序（召回任务、候选重排），成对 (pairwise) 方法是代价最小的升级，它教会模型相对偏好关系。\n\n- 若存在分级相关性标签且 NDCG 是头条指标，则上列表级 (listwise) 方法——生产环境用 LambdaMART（跑在梯度提升决策树栈上），神经网络栈用 ListNet 或 ApproxNDCG。这类损失天生具备位置感知性。\n\n- 多任务排序场景（DoorDash / eBay feed、Etsy 搜索）里，逐点多任务学习 (MTL) 头 (pClick、pOrder、pGMV) 通常线性融合为最终分数；纯 listwise 反而少见，因为下游出价系统需要可校准的逐点头。",
    ),
    (
        '**口述捷径**："Pointwise 用来当可校准的 head，pairwise 用来学相对顺序，listwise（LambdaMART）用在分级 NDCG 是目标的场景。ListNet 的 softmax 是神经 ranker 不用 GBDT 时的 listwise 光滑选项。"',
        '**口述捷径**："逐点方法用作可校准的预测头，成对方法用来学相对顺序，列表级方法（如 LambdaMART）用在分级 NDCG 是目标的场景。ListNet 的 softmax 损失则是神经排序器不上梯度提升决策树栈时的列表级光滑替代。"',
    ),
    (
        'Google 面试官爱追问："为什么你选 NDCG？凭什么它就是对的目标？" 最好答案是 Sale-NDCG 反面教材，因为它说明你懂 NDCG 的失败模式，而不只是公式。',
        'Google 面试官常追问："为什么你选 NDCG？凭什么它就是对的目标函数？" 最佳答法是 Sale-NDCG 反面教材，这能证明你真正理解 NDCG 的失败模式，而不仅仅会背公式。',
    ),
    (
        "30 秒故事脚本：\n\n- 团队优化的是 Sale NDCG = 用 purchase conversion 加权的 NDCG。标准选择，跑了几年都挺好。\n\n- 发现系统性偏差：便宜 item 的 conversion 更高，所以 Sale NDCG 把 \\$5 的配件排到 \\$100 的项链前面。局部指标在涨，平台 GMB (Gross Merchandise Bought) 却平稳没动。\n\n- 根因：Sale NDCG 的 gain = $2^y - 1$ 不含 item value。LambdaMART 在忠实地优化一个**错配**的代理目标。\n\n- 修复：把排序重新表述成资源分配问题——分别预测 pClick、pOrder、预期每曝光收入（pointwise MTL、BCE / 回归 head），再按 GMB-bid 分数 $w_1 \\cdot \\text{pClick} + w_2 \\cdot \\text{pOrder} + w_3 \\cdot \\text{pOrder} \\cdot \\text{value} - w_4 \\cdot \\text{risk}$ 分槽位。这就是 Ranking-as-Allocation。\n\n- 结果：首次 A/B +1% GMB，这个分配 primitive 还推广到了 Ads、Monetization、promo 模块。",
        "30 秒故事脚本：\n\n- 团队优化的是 Sale NDCG，即用购买转化率 (purchase conversion) 加权的 NDCG。这是当时的标准选择，跑了几年都没问题。\n\n- 后来发现系统性偏差：廉价商品的转化率更高，因此 Sale NDCG 会把 \\$5 的配件排到 \\$100 的项链前面。局部指标持续上涨，平台**商品总交易额** (Gross Merchandise Bought, GMB) 却一直没动。\n\n- 根因分析：Sale NDCG 的收益 $2^y - 1$ 并不包含商品价值 (item value)。LambdaMART 在忠实地优化一个**目标错配**的代理指标。\n\n- 修复方案：把排序重新表述为资源分配问题——分别预测点击概率 (pClick)、下单概率 (pOrder)、单次曝光预期收入，采用逐点多任务架构（BCE 或回归头），再按出价分数 $w_1 \\cdot \\text{pClick} + w_2 \\cdot \\text{pOrder} + w_3 \\cdot \\text{pOrder} \\cdot \\text{value} - w_4 \\cdot \\text{risk}$ 分配槽位。这一范式即**排序即分配** (Ranking-as-Allocation)。\n\n- 结果：首次 A/B 实验便收获 +1% GMB，这一分配原语后来也推广到了广告、变现、促销模块。",
    ),
    (
        "**为什么这个故事在 Google ranking 岗上打得响**：\n\n- 显示你理解 NDCG 是代理、不是业务目标。LambdaMART 把 NDCG 优化满格也照样可能伤 GMB。\n\n- 展示对 pointwise MTL + score fusion 模式的熟练度——这种模式主宰了现代电商排序（DoorDash 第三节的 fusion score 结构上完全一样）。\n\n- 给了通往 calibration 的桥：GMB bidding 一旦 pClick / pOrder 校准失灵就崩——自然接回 calibration drill（T-P0-417）。",
        "**为什么这个故事在 Google 排序岗上非常加分**：\n\n- 它证明你理解 NDCG 只是代理指标、不是业务目标。即使 LambdaMART 把 NDCG 优化到满格，仍然可能损伤 GMB。\n\n- 它展示了对**逐点多任务 + 分数融合** (pointwise MTL + score fusion) 这一模式的熟练度——这种模式主宰了现代电商排序（DoorDash 第三节的融合分数在结构上完全一致）。\n\n- 它给出了通往校准 (calibration) 议题的桥梁：GMB 出价一旦 pClick / pOrder 校准失灵就会崩——自然接回校准训练（T-P0-417）。",
    ),
    (
        '**口述捷径**："NDCG 是代理。Sale NDCG 忽略 item value——便宜 item 在排名上压过贵 item。修复是 Ranking-as-Allocation：校准的 MTL head 融合成 GMB bid 分数。第一次实验就 +1% GMB。"',
        '**口述捷径**："NDCG 只是代理指标。Sale NDCG 忽略了商品价值——廉价商品在排名上会压过昂贵商品。修复方案就是排序即分配：用校准后的多任务头融合成 GMB 出价分数。第一次 A/B 实验就拿到了 +1% GMB。"',
    ),
    (
        "- [ ] 背 RankNet 损失：$\\log(1 + \\exp(-(s_i - s_j)))$",
        "- [ ] 背出 RankNet 损失：$\\log(1 + \\exp(-(s_i - s_j)))$",
    ),
    (
        "- [ ] 说出 RankNet 梯度 $\\partial L / \\partial s_i = -(1 - P_{ij})$",
        "- [ ] 说出 RankNet 梯度：$\\partial L / \\partial s_i = -(1 - P_{ij})$",
    ),
    (
        "- [ ] 说出 RankNet 的致命缺陷（所有对权重一样）",
        "- [ ] 说出 RankNet 的致命缺陷（所有文档对的权重完全相同）",
    ),
    (
        "- [ ] 背 $\\lambda_{ij} = -(1 - P_{ij}) \\cdot |\\Delta\\mathrm{NDCG}_{ij}|$",
        "- [ ] 背出 Lambda 伪梯度：$\\lambda_{ij} = -(1 - P_{ij}) \\cdot |\\Delta\\mathrm{NDCG}_{ij}|$",
    ),
    (
        "- [ ] 解释为什么 $|\\Delta\\mathrm{NDCG}|$ 把容量压到顶部（$1/\\log_2$ 折扣在顶部大）",
        "- [ ] 解释为什么 $|\\Delta\\mathrm{NDCG}|$ 会把模型容量压到头部（$1/\\log_2$ 折扣在头部更大）",
    ),
    (
        "- [ ] LambdaMART = $(\\lambda_i, w_i)$ 作为 (gradient, hessian) 喂给 GBDT",
        "- [ ] LambdaMART 即把 $(\\lambda_i, w_i)$ 作为 (梯度, 海森) 喂给梯度提升决策树",
    ),
    (
        "- [ ] Pointwise BCE -- 什么时候用（可校准的 click / order head、MTL）",
        "- [ ] 逐点 BCE 何时使用：需要可校准的点击、下单预测头、多任务学习场景",
    ),
    (
        "- [ ] Pairwise RankNet -- 什么时候用（只要顺序、无分级标签）",
        "- [ ] 成对 RankNet 何时使用：只关心相对顺序、没有分级标签的场景",
    ),
    (
        "- [ ] Listwise (ListNet / LambdaMART) -- 什么时候用（分级标签、NDCG 目标）",
        "- [ ] 列表级方法 (ListNet / LambdaMART) 何时使用：有分级相关性标签且 NDCG 是目标",
    ),
    (
        "- [ ] Sale NDCG 故事：便宜 item 压过贵 item -> Ranking-as-Allocation -> +1% GMB",
        "- [ ] Sale NDCG 故事主线：廉价商品压过高价商品 -> 排序即分配 -> 实验 +1% GMB",
    ),
    (
        "- [ ] 通往 calibration 的桥：GMB bidding 需要可校准的 pClick / pOrder",
        "- [ ] 通往校准议题的桥梁：GMB 出价需要可校准的 pClick 与 pOrder 概率",
    ),
]

# ---- DOC 64: Two-Tower Retrieval Deep Dive -------------------------------
SUBS[64] = [
    (
        "- 方程级别的 InfoNCE / contrastive loss\n- Sampled softmax + popularity bias 修正\n- Dense vector retrieval，cosine / dot-product 相似度\n- LTR 指标：NDCG、recall@K、MRR\n- ANN（approximate nearest neighbor）的高层认识",
        "- 方程级别的 **InfoNCE** 与对比损失 (contrastive loss)\n- 采样 softmax 与流行度偏差 (popularity bias) 修正\n- 稠密向量检索 (dense vector retrieval)：余弦 (cosine) 与点积 (dot-product) 相似度\n- 学习排序 (LTR) 指标：NDCG、recall@K、MRR\n- 近似最近邻 (Approximate Nearest Neighbor, ANN) 的高层认识",
    ),
    (
        "Staging-11 单独覆盖 **InfoNCE** 本身——损失、temperature、梯度。应付 ML 基础题够用了，但应付不了系统设计题。**Google R1 L5/L6 ranking 会问：\"十亿文档、10ms SLA，给我走一下召回阶段。\"** 有趣的回答都在架构层面：**Two-Tower** 分解本身、如何挖负样本而不毒害模型、什么 ANN 索引匹配你的更新频率、以及为什么你的 offline recall@1000 涨 3 点、online NDCG 却跌。",
        "Staging-11 已经单独覆盖 **InfoNCE** 本身——损失形式、温度 (temperature)、梯度推导。应付机器学习基础题已经够用，但应付不了系统设计题。**Google R1 L5/L6 ranking 会问：\"十亿级文档语料、10 毫秒 SLA，请把召回阶段从头走一遍给我看。\"** 有价值的回答都发生在架构层面：**双塔** (Two-Tower) 分解本身、如何挖掘负样本又不毒害模型、哪种 **ANN** 索引匹配你的更新频率、以及为什么你的线下 recall@1000 涨了 3 个点、线上 NDCG 反而下跌。",
    ),
    (
        "这个 drill 覆盖上面四个系统级关注点。串起它们的线是**解耦**：query 和 doc 靠点积打分、没有 cross-attention——换来离线建索引，同时禁掉任何跨 $(q, d)$ 边界的特征。栈里每一个 tradeoff 都从这**一个约束**推出来。",
        "本训练覆盖上述四个系统级关注点。贯穿它们的主线是**解耦** (decoupling)：查询 (query) 与文档 (doc) 只靠点积打分、没有跨塔注意力 (cross-attention)——换取离线建索引的能力，代价是禁掉任何跨越 $(q, d)$ 边界的特征。整个栈里的每一个取舍都可以从这**一个约束**推导出来。",
    ),
    (
        '**口述捷径**："**Two-tower** = dot product = 离线索引。其他一切——负样本挖掘、**HNSW** vs IVF、线下-线上 gap——都是这句首话的二阶后果。"',
        '**口述捷径**："**双塔** = 点积打分 = 支持离线建索引。其他一切——负样本挖掘、**HNSW** vs **IVF**、线下-线上指标 gap——都只是第一句话的二阶推论。"',
    ),
    (
        "规范架构：query 塔把（用户特征、上下文、文本）映到 $u \\in \\mathbb{R}^d$；item 塔把（item 特征、文本、metadata）映到 $v \\in \\mathbb{R}^d$。打分是纯内积：",
        "规范架构：查询塔把（用户特征、上下文、查询文本）映射到 $u \\in \\mathbb{R}^d$；物品塔把（物品特征、文本、元数据 metadata）映射到 $v \\in \\mathbb{R}^d$。打分纯粹走内积：",
    ),
    (
        "双塔打分：独立算出的 query 和 doc embedding 的点积：",
        "双塔打分：独立计算出的查询向量与文档向量的点积：",
    ),
    (
        "**关键性质**：$v_\\phi(d)$ **只依赖** $d$，永远看不到 query。这一个约束就是让十亿级召回成为可能的原因。具体三条：",
        "**关键性质**：$v_\\phi(d)$ **只依赖于** $d$，永远不会看到查询 $q$。正是这一个约束让十亿级召回变得可行。具体分三条：",
    ),
    (
        "1. **离线预计算 (Offline precomputation)**：每个 doc 的 $v$ 在每次 corpus snapshot 时计算一次，而不是每次 query 计算一次。对一个 $10^9$-doc 索引、1B 参数的塔，这就是 10ms SLA 和 10 分钟 SLA 的差距。",
        "1. **离线预计算** (Offline precomputation)：每个文档的 $v$ 在每次语料 (corpus) 快照时计算一次，而不是每次查询都重新计算。对一个 $10^9$ 文档索引、参数量 10 亿的塔而言，这就是 10 毫秒 SLA 与 10 分钟 SLA 的差别。",
    ),
    (
        "2. **ANN 索引构建 (ANN index build)**：所有 $v$ 固定后，在其上建向量索引（HNSW 或 **IVF-PQ**）。在线服务变成 encode(q) -> **ANN** search——$O(\\log N)$ 甚至更好，而不是 $O(N)$。",
        "2. **ANN 索引构建** (ANN index build)：所有 $v$ 固定之后，在这些向量上构建近似最近邻索引（HNSW 或 **IVF-PQ**）。在线服务路径变为：查询编码 `encode(q)` -> **近似最近邻** 搜索 (ANN search)，复杂度降到 $O(\\log N)$ 甚至更优，而不是 $O(N)$。",
    ),
    (
        "3. **实时 query 特征免费 (Fresh query features are free)**：$u_\\theta$ 每次请求重新计算，所以实时上下文（位置、session、时段）不额外掏钱。这就是双塔在上下文敏感检索里统治力的根源（DoorDash、YouTube 首页 feed、Pinterest homefeed）。",
        "3. **实时查询特征零成本** (Fresh query features are free)：$u_\\theta$ 在每次请求时重新计算，因此实时上下文（位置、会话 session、时段）不需要额外花费。这正是双塔在上下文敏感检索中占据统治地位的根源（DoorDash 商家召回、YouTube 首页 feed、Pinterest homefeed 都是如此）。",
    ),
    (
        "**代价是表达能力**。cross-encoder 能对 $(q, d)$ token 做联合注意力，学到\"query 词 A 与 doc 词 B 的交互\"；双塔学不了。任何**跨 $(q, d)$ 边界**的特征——\"q 里多少词出现在 d\"、\"$(q, d)$ 对的历史 CTR\"——都必须活在 reranker 里，不能在 retriever 里。标准生产模式是 retrieval (双塔) -> rerank (top-K 候选上的 cross-encoder)：",
        "**代价是表达能力**。跨塔编码器 (cross-encoder) 能对 $(q, d)$ 的 token 做联合注意力，学到\"查询词 A 与文档词 B 的交互\"这类信号；双塔学不了。任何**跨越 $(q, d)$ 边界**的特征——\"查询中有多少词出现在文档里\"、\"$(q, d)$ 对的历史点击率 (CTR)\"——都必须放在重排器 (reranker) 里，不能放进召回器 (retriever)。标准生产模式是：检索阶段用双塔 -> 重排阶段在 top-K 候选上用跨塔编码器。",
    ),
    (
        "两阶段 pipeline：廉价点积召回喂昂贵 cross-attention rerank：",
        "两阶段流水线：廉价点积召回把候选送给昂贵的跨塔注意力重排：",
    ),
    (
        "口述答案里要提的系统影响：\n\n- **索引刷新延迟 (Index refresh latency)**：换 item 塔要**重新编码整个 corpus**——留几小时的 rebuild 时间。孪生查询（\"同一 item 有多套 metadata\"）要版本化。\n\n- **无 late interaction**：ColBERT 等模型用 per-token late interaction 放松双塔，内存大约 10 倍以换召回提升。能承担就上；Google 的规模往往不行。\n\n- **User 塔必须纯净**：不能有任何依赖候选 doc 的特征。审稿人会死咬这条——如果你说\"user embedding 里放了 top-candidate 信号\"，你就破了解耦、失去了离线索引。",
        "口述答案里必须提到的几个系统影响：\n\n- **索引刷新延迟** (Index refresh latency)：更换物品塔意味着**需要对整个语料重新编码**——预留几小时的重建时间。孪生查询（即\"同一物品有多套元数据\"的情况）必须做版本化。\n\n- **没有后期交互** (late interaction)：ColBERT 等模型用逐 token 后期交互放松双塔约束，内存代价约 10 倍，换来召回提升。有预算能承担就上；Google 的规模通常承担不起。\n\n- **用户塔必须纯净**：不能包含任何依赖候选文档的特征。面试评审者会死咬这一条——如果你说\"用户向量里加了头部候选的信号\"，就破坏了解耦、失去了离线索引的能力。",
    ),
    (
        '**口述捷径**："两塔意味着 $v$ 不知道 $q$，所以 $v$ 可预计算，所以 $v$ 上的 ANN 索引给你亚毫秒召回。架构代价是没有 cross-attention——所以我们**永远**加一个 reranker。"',
        '**口述捷径**："双塔意味着 $v$ 不知道 $q$，所以 $v$ 可离线预计算，所以在 $v$ 上建近似最近邻索引就能拿到亚毫秒级召回。架构代价是没有跨塔注意力——因此我们**永远**会在其后再加一个重排器。"',
    ),
    (
        "双塔用 **InfoNCE** 训练就是小负样本集上的纯 softmax；模型质量**被负样本分布支配**。全 corpus softmax 不可行，生产系统都从四种策略里挑（通常混合）。",
        "双塔用 **InfoNCE** 训练就是在小负样本集上做纯 softmax；模型质量**被负样本分布支配**。全语料 softmax 不可行，生产系统都从以下四种策略里选（通常混合使用）。",
    ),
    (
        "InfoNCE over $K$ negatives：这 $K$ 负样本的分布选择是主导的设计变量：",
        "在 $K$ 个负样本上的 InfoNCE 损失：这 $K$ 个负样本的分布选择才是主导性的设计变量：",
    ),
    (
        "**(a) Random negatives**：从 corpus 均匀抽 $K$ 个 item。便宜、相对 corpus 先验无偏。*失败模式*：大多数随机 item **琐碎地是负的**——\"query = 披萨\" vs \"doc = 电钻\"根本不是难题。模型学会粗粒度主题，**却从不学到真正驱动用户满意度的同主题细区分**。",
        "**(a) 随机负样本** (Random negatives)：从语料里均匀抽样 $K$ 个物品。成本低，对语料先验而言无偏。*失败模式*：大多数随机物品**过于容易被判负**——\"查询=披萨\" 对 \"文档=电钻\" 根本不是难题。模型只学到粗粒度主题，**却从未学到真正驱动用户满意度的同主题细粒度区分**。",
    ),
    (
        "**(b) In-batch negatives**：把同一 minibatch 里其他行的正样本当本行的负样本。$K = \\text{batch\\_size} - 1$ 白送，不多做 forward。*失败模式*：**popularity bias (流行度偏差)**——高频 item **同时**按频次出现在正样本和负样本里。梯度**过度惩罚**流行 item，把它们从高频 query 那里**挤走**。教科书修法是 sampled-softmax **logit correction**：",
        "**(b) 批内负样本** (In-batch negatives)：把同一小批次 (minibatch) 里其他行的正样本当作本行的负样本。这样 $K = \\text{batch\\_size} - 1$ 白送，不必额外跑前向。*失败模式*：**流行度偏差** (popularity bias)——高频物品**同时**按频次出现在正样本与负样本里。梯度**过度惩罚**热门物品，把它们从高频查询的结果中**挤走**。教科书修法是采样 softmax 的 **logit 修正** (logit correction)：",
    ),
    (
        "流行度修正 logit：减去 log 采样概率，恢复\"全 corpus 无偏 softmax\"（Bengio-Senecal 2008, YouTube DNN）：",
        "流行度修正后的 logit：减去 log 采样概率，以恢复到\"全语料无偏 softmax\"的等价形式 (Bengio-Senecal 2008, YouTube DNN)：",
    ),
    (
        "不修正的话，in-batch negatives 会让索引系统性偏向**不利于头部分布**——而头部正是 reranker 最依赖的部分。",
        "不做这项修正，批内负样本会让索引系统性地**压制头部分布**——而头部正是重排器最依赖的那部分流量。",
    ),
    (
        "**(c) Hard negatives**：训练步 $t$ 用当前模型跑一次 ANN，把 top-K **未被点击**的 item 当 $t+1$ 步的负样本。把决策边界**锐化到真正重要的 margin 附近**。*失败模式 1*：**false negatives (假负样本)**——用户没点不是因为 item 不相关，而是**没看到**（折叠下、下一页）。训练把相关 item 推离 query。*失败模式 2*：**自我强化循环 (self-reinforcing loop)**——从当前模型挖出的 hard negative 编码了当前模型的偏差；用它们训练反而**收紧**这些偏差而不是纠正。**标准缓解：从上一版本的 snapshot 里挖，而不是 live 模型**。",
        "**(c) 困难负样本** (Hard negatives)：在训练步 $t$ 用当前模型跑一次近似最近邻搜索，把 top-K 中**用户没有点击**的物品作为第 $t+1$ 步的负样本。目的是把决策边界**锐化到真正重要的 margin 附近**。*失败模式 1*：**假负样本** (false negatives)——用户没点不是因为物品不相关，而是**根本没看到**（折叠以下、下一页）。训练反而把相关物品推离了查询。*失败模式 2*：**自我强化循环** (self-reinforcing loop)——从当前模型挖出的困难负样本编码了当前模型的偏差；用它们训练反而**固化**这些偏差而非纠正。**标准缓解方案：从上一版模型快照 (snapshot) 里挖掘，而不是从在线模型 (live model) 里挖**。",
    ),
    (
        "**(d) Mixed / curriculum**：生产默认——比如 50% in-batch、30% random、20% hard。比例是值得 sweep 的超参。*失败模式*：混合比例常常**一次选定后再也不调**——即使 corpus 或 query 分布迁移了。",
        "**(d) 混合与课程学习** (Mixed / curriculum)：生产环境的默认做法——例如 50% 批内、30% 随机、20% 困难。混合比例是值得做超参扫描 (sweep) 的维度。*失败模式*：混合比例常常**定好之后就再也没有重新调过**——即使语料或查询分布发生了漂移。",
    ),
    (
        "**贯穿的坑：positive-only bias (只看正样本偏差)**。训练对来自点击；点击只在 impression 过的 item 上发生。$\\pi_0$ 从不展示的 item 既不是正样本也不是 hard negative——它们**对训练不可见**。这和 **IPS**（见 IPS drill, T-P0-418）为评估解决的 selection bias 是同一个问题，它**对召回训练同样重要**：你学不会召回你从未 log 过的东西。",
        "**贯穿四者的大坑：仅正样本偏差** (positive-only bias)。训练样本对来自用户点击；点击只发生在曾被曝光 (impression) 的物品上。从未被当前策略 $\\pi_0$ 展示过的物品既不是正样本也不是困难负样本——它们对训练**根本不可见**。这和 **逆倾向评分** (IPS，见 IPS drill, T-P0-418) 为评估阶段解决的选择偏差是同一个问题，且对召回训练**同等重要**：你学不会召回那些你从未记录过 (log) 的东西。",
    ),
    (
        '**口述捷径**："Random 无偏但太易；in-batch 便宜但流行度偏（减 $\\log p_j$）；hard 锐利但有 false negative 和自我强化（从 snapshot 挖）。三者混。Positive selection bias 是混合救不了的那条。"',
        '**口述捷径**："随机负样本无偏但过于容易；批内便宜但有流行度偏（需要减去 $\\log p_j$）；困难负样本锐利但会遇到假负样本与自我强化（从模型快照中挖掘）。生产里三者混用。仅正样本的选择偏差则是混用也救不了的那条。"',
    ),
    (
        "两大生产 ANN 索引有**正交的失败模式**；选哪一个是**系统设计决策，不是调参**。一张速查表：",
        "两大生产级近似最近邻索引具有**正交的失败模式**；选择哪一个属于**系统设计决策，不是超参调优**。一张速查表总结：",
    ),
    (
        "**选 HNSW**：corpus 能全塞内存（$d=128$ 下 $10^8$ 向量以下），延迟 SLA 紧（1ms 以下），item 按增量更新（开店 / 关店、商品上下架）。典型场景：DoorDash 商家召回、Pinterest 指定 board 上的 pin 召回。",
        "**选 HNSW 的条件**：语料能全部塞进内存（$d=128$ 时约 $10^8$ 向量以下），延迟 SLA 紧张（低于 1 毫秒），物品按增量更新（开店 / 关店、商品上下架）。典型场景：DoorDash 商家召回、Pinterest 指定画板 (board) 上的 pin 召回。",
    ),
    (
        "**选 IVF-PQ**：corpus 是 $10^9+$ 向量、内存是绑定约束，更新按 batch（日级或周级 rebuild 可接受），且能接受 90-92% 召回——靠 rerank 阶段补。典型场景：YouTube 视频 corpus、Google Web 索引的召回 cell。",
        "**选 IVF-PQ 的条件**：语料规模达 $10^9$+ 向量、内存是核心约束，更新按批次 (batch) 进行（日级或周级重建可以接受），且能接受 90-92% 的召回——剩余 gap 靠重排阶段补。典型场景：YouTube 视频语料、Google Web 索引中的召回单元 (cell)。",
    ),
    (
        "**选 Flat**：你在 debug、为 recall 测量做 ground truth、或 corpus 在 $10^5$ 以下且不关心延迟。**永远别上 prod**。",
        "**选 Flat 的条件**：你在做调试 (debug)、为召回率测量提供真值 (ground truth)、或语料规模在 $10^5$ 以下且不关心延迟。**永远不要上生产**。",
    ),
    (
        "**混合 (Hybrid)**：很多系统外层用 IVF-PQ（粗 cell 路由），cell 内用 HNSW（被选中 cell 的细搜索）。Faiss 复合索引开箱就支持。",
        "**混合索引** (Hybrid)：很多系统外层用 IVF-PQ 做粗单元 (cell) 路由，单元内部用 HNSW 做细搜索。Faiss 的复合索引开箱即支持这种组合。",
    ),
    (
        "两个索引都暴露 recall / latency 旋钮——HNSW 的 `ef_search`、IVF-PQ 的 `nprobe`。面试官会压你怎么调：\n\n- **召回目标要比下游需要的高一截**——比如 reranker 见 top-100、你要 95% 有效召回，就把 ANN 调到 recall@1000 = 97-98%，给 rerank 留 headroom。\n\n- **永远 over-retrieve**：向 ANN 要 top-(K * 2-5)，让 reranker 剪枝。边际延迟成本几乎持平；召回提升显著，因为 ANN 的 2-5% 漏检与 rerank 误差**不相关**。\n\n- **召回要对照 ground-truth Flat 报**，不是对照训练标签——你要把**索引近似误差**和**模型质量误差**分开。",
        "两种索引都暴露召回/延迟旋钮——HNSW 的 `ef_search`、IVF-PQ 的 `nprobe`。面试官会追问你怎么调：\n\n- **召回目标要比下游需求留出一截冗余**——比如重排器只看 top-100、希望达到 95% 有效召回，就把近似最近邻索引调到 recall@1000 = 97-98%，给重排留出余量 (headroom)。\n\n- **一定要做过召回** (over-retrieve)：向近似最近邻索引要 top-$K \\times 2 \\sim 5$，交给重排做剪枝。边际延迟成本几乎持平；召回提升却很明显，因为 2-5% 的索引漏检与重排误差**不相关**。\n\n- **召回数字要对照 Flat 真值来报**，而不是对照训练标签——目的是把**索引近似误差**与**模型质量误差**分开度量。",
    ),
    (
        '**口述捷径**："HNSW 用于内存里亚毫秒；IVF-PQ 用于十亿级 + batch 更新。Over-retrieve 2-5x，让 reranker 收尾。对照 ground-truth Flat 调 `ef_search` / `nprobe`，不是训练标签。"',
        '**口述捷径**："HNSW 用于内存内亚毫秒场景；IVF-PQ 用于十亿级 + 批式更新。过召回 2-5 倍，让重排收尾。对照 Flat 真值来调 `ef_search` 与 `nprobe`，而不是对照训练标签。"',
    ),
    (
        "Google R1 面试官在找的失败模式：**\"我们上线了 v2，offline recall@1000 涨 3 点，online NDCG 跌 0.5 点、流量回到 baseline。\"** 这不是测量误差，是 **Training-Serving Skew (TSS)** + **5 个具体来源**。**能把 5 条都说出来就是 senior 级答案**。",
        "Google R1 面试官追问的正是这个失败模式：**\"我们上线了 v2，线下 recall@1000 涨 3 个点，线上 NDCG 跌 0.5 个点、流量回到基线 (baseline)。\"** 这不是测量误差，而是**训练-服务偏移** (Training-Serving Skew, TSS) 加上 **5 个具体来源**。**能把这 5 条都说清楚就是 senior 级答案**。",
    ),
    (
        "**Source 1: ANN 近似偏差 (ANN approximation skew)**。离线 recall 一般对照 Flat (exact) top-K 评；在线服务用 HNSW 或 IVF-PQ，漏检率 3-10%。离线数字**不反映用户实际看到的**。*诊断*：把 \"index recall\" = recall(ANN top-K, Flat top-K) 作为独立指标；不信任任何没把**模型召回**和**索引召回**分开的数字。",
        "**来源 1：近似最近邻近似偏差** (ANN approximation skew)。线下 recall 通常对照 Flat (精确) top-K 评估；线上服务用 HNSW 或 IVF-PQ，漏检率在 3-10%。线下数字**并不反映用户真正看到的结果**。*诊断手段*：把\"索引召回\" = recall(ANN top-K, Flat top-K) 单独作为一项指标；不要相信任何没有把**模型召回**与**索引召回**拆开度量的数字。",
    ),
    (
        "**Source 2: 特征偏差 (Feature skew)**。query 塔用的特征（session 历史、位置、实时上下文）离线（从日志去重回填）和在线（流式、新鲜、带时钟偏差）**计算方式不同**。*诊断*：拿 held-out 的已 log query 分别跑离线和在线 pipeline，比较两条分数分布。KL 散度超过约 0.05 就是冒烟枪。",
        "**来源 2：特征偏差** (Feature skew)。查询塔使用的特征（会话 session 历史、位置、实时上下文）在线下（从日志去重回填）与线上（流式、新鲜、带时钟偏差）**计算方式不同**。*诊断手段*：拿留出 (held-out) 的已记录查询分别跑线下与线上流水线，比较两条分数分布。KL 散度超过约 0.05 就是冒烟枪 (smoking gun)。",
    ),
    (
        "**Source 3: 奖励错配 (Reward misalignment)**。离线 recall 把\"相关 = 用户点击\"；在线 NDCG 用等级标签或另一个 reward model。以**点击正样本召回**为目标训的 retriever 可能召回标题党、压过真正带来满意度的 item——online NDCG 跌而 recall@1000 涨。*诊断*：离线 recall 评估用**和在线指标同一套 relevance 函数**，不用\"是否点击\"。",
        "**来源 3：奖励错配** (Reward misalignment)。线下 recall 把\"相关 = 用户点击\"；线上 NDCG 使用分级标签或另一个奖励模型 (reward model)。以**点击正样本召回**为训练目标的召回器，可能会召回标题党内容、压过真正带来用户满意度的物品——线上 NDCG 下跌而 recall@1000 反而上涨。*诊断手段*：线下 recall 评估必须**使用与线上指标完全相同的相关性函数**，而不是\"是否点击\"。",
    ),
    (
        "**Source 4: Rerank 反转 (Rerank inversion)**。retrieval 按点积排；生产列表按 cross-encoder rerank。换了 retriever 后候选集可能一样但**顺序变了**——reranker 的校准基于旧 retriever 的分数分布训练，分布一动 ranker 校准就破（见 T-P0-417 Calibration drill）。*诊断*：每次换 retriever 都要**重训 rerank 或 temperature 重校准**；离线评估整**完整 pipeline (retrieve + rerank)**，不是单独 retrieval。",
        "**来源 4：重排反转** (Rerank inversion)。召回按点积排序；生产列表按跨塔编码器重排。换了召回器之后候选集可能不变但**顺序已经变了**——重排器的校准是基于旧召回器的分数分布训练的，分布一旦漂移重排校准就破（见 T-P0-417 校准训练）。*诊断手段*：每次更换召回器都必须**重训重排或者重新做温度校准**；线下评估必须对**整条完整流水线（召回 + 重排）**进行，而不是只评单独的召回。",
    ),
    (
        "**Source 5: 流行度漂移 (Popularity drift)**。离线训练负样本从历史 corpus 分布抽；在线活跃候选集偏向更新、更流行的 item。如果 in-batch logit correction 用错了 $p_j$ 分布，**头部 item 会在线上被过度压制**。*诊断*：监控头/尾召回分解。如果头部 recall 跌了、尾部涨了，流行度修正过火了。",
        "**来源 5：流行度漂移** (Popularity drift)。线下训练负样本从历史语料分布采样；线上活跃候选集更偏向于更新的、更热门的物品。如果批内 logit 修正用了错误的 $p_j$ 分布，**头部物品会在线上被过度压制**。*诊断手段*：监控头部与尾部召回的分解。如果头部 recall 下跌、尾部上涨，说明流行度修正过头了。",
    ),
    (
        "经典的全栈无偏评估做法：\n\n去偏离线 NDCG via IPS（见 T-P0-418 drill）：把 selection 和 position bias 除掉，让离线和在线可比：",
        "经典的全栈无偏评估做法：\n\n用逆倾向评分 (IPS) 做去偏离线 NDCG（见 T-P0-418 训练）：把选择偏差与位置偏差都除掉，让线下与线上指标可比：",
    ),
    (
        '**口述捷径**："五种偏移：索引召回 vs Flat、特征新鲜度、reward 函数、rerank 校准、流行度漂移。上线前每一个都做针对性离线诊断。Offline recall@K 单独不是 ship gate；debiased offline NDCG 更接近，仍然要小 A/B 兜底。"',
        '**口述捷径**："五种偏移：索引召回 vs Flat、特征新鲜度、奖励函数、重排校准、流行度漂移。上线前每一条都需要做针对性线下诊断。线下 recall@K 单独不是上线门槛；去偏后的线下 NDCG 更接近真实，但仍然需要小流量 A/B 做最后兜底。"',
    ),
    (
        "面试官爱听的具体数字：\n\n- 典型 embedding 维度 $d$：64-256。$d$ 超过约 256 召回几乎不涨、ANN 延迟却线性增。\n\n- HNSW 内存：约 $(4d + 8M)$ 字节 / 向量，$M$ 是图度数（典型 $M=16$）。$d=128, M=16$：每向量约 640 字节。$10^8$ 向量 -> 64 GB RAM——这就是 HNSW 单机顶格的地方。\n\n- IVF-PQ PQ 压缩后内存：每向量 8-16 字节。$10^9$ 向量 -> 8-16 GB。这就是为什么 web 规模只能 IVF-PQ。\n\n- Batch size 8192 的 in-batch negatives：每正样本白送 $K=8191$ 个负样本。这是为什么双塔训练能容易扩到超大 batch——**有效 $K$ 随 batch 长，item 塔却不多 forward 一次**。\n\n- Temperature $\\tau$：典型 0.05-0.1。太小（< 0.01）-> 梯度集中在最近负样本，训练不稳。太大（> 0.5）-> 损失几乎均匀，模型学得慢。\n\n- Rebuild 节奏：HNSW 秒级接受写入；IVF-PQ 一般日级 rebuild。若任务要\"分钟级 fresh\"，HNSW 或分层索引**必选**。",
        "面试官偏爱的具体数字：\n\n- 典型嵌入 (embedding) 维度 $d$：64 至 256。一旦 $d$ 超过约 256，召回几乎不再提升，但近似最近邻延迟线性增长。\n\n- HNSW 内存估算：约 $(4d + 8M)$ 字节 / 向量，$M$ 是图的度数（典型值 $M=16$）。取 $d=128, M=16$：每向量约 640 字节。$10^8$ 向量 -> 64 GB 内存——这就是 HNSW 单机的规模上限。\n\n- IVF-PQ 压缩后内存：每向量 8-16 字节。$10^9$ 向量 -> 8-16 GB。这就是为什么网页级 (web scale) 规模只能选 IVF-PQ。\n\n- 批大小 (batch size) 8192 的批内负样本：每条正样本白送 $K=8191$ 个负样本。这是双塔训练能轻松扩展到超大 batch 的根本原因——**有效 $K$ 随 batch 线性增长，物品塔却不必多跑一次前向**。\n\n- 温度 $\\tau$ 典型值 0.05-0.1。过小（< 0.01） -> 梯度过度集中于最近的负样本，训练不稳。过大（> 0.5） -> 损失几乎均匀，模型学习很慢。\n\n- 重建 (rebuild) 节奏：HNSW 支持秒级写入；IVF-PQ 一般日级重建。若任务需要\"分钟级新鲜度\"，则 HNSW 或分层索引是**必选项**。",
    ),
    (
        "- [ ] 双塔架构：独立 $u_\\theta(q), v_\\phi(d)$，score = $u \\cdot v$\n- [ ] 解耦 -> 离线预计算 + ANN 索引（这就是全部收益）\n- [ ] 代价：无 cross-attention -> 跨特征必须活在 reranker\n- [ ] 负样本：(a) random、(b) in-batch（修正 $-\\log p_j$）、(c) hard（从 snapshot 挖）、(d) 混合\n- [ ] In-batch 流行度偏差 用 sampled-softmax log 修正\n- [ ] Hard-negative 失败模式：false negatives + 自我强化循环\n- [ ] HNSW：图、亚毫秒、增量、占内存、$\\le 10^8$ 规模\n- [ ] IVF-PQ：粗桶 + PQ 压缩、省内存、batch rebuild、$10^9+$ 规模\n- [ ] Over-retrieve 2-5x 喂 rerank；按 Flat ground truth 调 `ef_search` / `nprobe`\n- [ ] 五种 **TSS** 来源：索引召回、特征偏差、reward 函数、rerank 校准、流行度漂移\n- [ ] Offline recall@K 单独不是 ship gate；debiased NDCG + 小 A/B 兜底",
        "- [ ] 双塔架构：独立的 $u_\\theta(q), v_\\phi(d)$ 两塔，打分 $= u \\cdot v$\n- [ ] 解耦带来离线预计算与近似最近邻索引（这就是全部的核心收益）\n- [ ] 代价是没有跨塔注意力，因此跨特征必须放进重排器里\n- [ ] 四种负样本：随机负样本、批内负样本（需修正 $-\\log p_j$）、困难负样本（必须从模型快照挖掘）、混合负样本\n- [ ] 批内流行度偏差用采样 softmax 的 log 修正公式处理\n- [ ] 困难负样本的失败模式：假负样本加自我强化循环\n- [ ] HNSW：图结构、亚毫秒延迟、支持增量、内存占用高、规模上限 $\\le 10^8$\n- [ ] IVF-PQ：粗桶 + 乘积量化压缩、内存友好、需批式重建、规模能到 $10^9$ 以上\n- [ ] 过召回 2-5 倍喂给重排；按 Flat 真值调 `ef_search` 与 `nprobe`\n- [ ] 五种训练-服务偏移来源：索引召回、特征偏差、奖励函数、重排校准、流行度漂移\n- [ ] 单独的线下 recall@K 不是上线门槛；去偏后的 NDCG 加小流量 A/B 做最终兜底",
    ),
]

# ---- DOC 67: A/B Test Rigor Drill ----------------------------------------
SUBS[67] = [
    (
        "- **MDE (Minimum Detectable Effect，最小可检测效应)**：给定 $\\alpha, \\beta$ 下实验有 power 检测到的最小真实 delta\n- **SRM (Sample Ratio Mismatch，样本比不匹配)**：对 arm 尺寸做卡方检验；指向 randomization 或 logging bug，不是 treatment 效应\n- **CUPED (Controlled-experiment Using Pre-Experiment Data，用实验前数据做受控实验)**：用 pre-period 协变量回归做方差缩减；把 $n$ 砍到 $n \\cdot (1 - \\rho^2)$\n- **OEC (Overall Evaluation Criterion，总评估指标)**：事先声明的**唯一**主指标；guardrails 另外监控、另外做 FDR 控制\n- **GMB (Google Merchant Bidding，Google 购物广告)**：付费购物渠道，bid = target_ROAS * 预测价值；Etsy 大量使用",
        "- **最小可检测效应** (Minimum Detectable Effect, MDE)：给定显著性 $\\alpha$ 与第二类错误率 $\\beta$ 时，实验在该 power 下能检测到的最小真实效应差 delta\n- **样本比不匹配** (Sample Ratio Mismatch, SRM)：对分流臂 (arm) 的样本量做卡方检验；触发时意味着随机化或日志 bug，而非处理效应\n- **用实验前数据做受控实验** (Controlled-experiment Using Pre-Experiment Data, CUPED)：用实验前协变量做回归以缩减方差；把所需样本量压到 $n \\cdot (1 - \\rho^2)$\n- **总评估指标** (Overall Evaluation Criterion, OEC)：事先声明的**唯一**主指标；护栏指标 (guardrails) 另行监控并做错误发现率 (FDR) 控制\n- **Google 购物广告** (Google Merchant Bidding, GMB)：付费购物渠道，出价 = target_ROAS × 预测价值；Etsy 大量使用",
    ),
    (
        "大多数 A/B 灾难不是模型 bug——是**实验卫生**失败：under-powered 上线被报\"flat\"、peeking 把 Type I 吹涨、treatment 效应被 novelty 混淆。这个 rigor drill 就是**每次上线必过的五道独立检查**。",
        "大多数 A/B 灾难并不是模型 bug——而是**实验卫生**失败：功效不足 (under-powered) 的上线被报告为\"flat\"、中途偷看 (peeking) 把第一类错误吹涨、处理效应被新奇性 (novelty) 混淆。这个严谨性 (rigor) 训练就是**每次上线必须过的五道独立检查**。",
    ),
    (
        "**心智顺序**：(1) 上线前算 sample size，(2) 看业务指标前先 **SRM**，(3) 分析时上 **CUPED** / 方差缩减，(4) 结论冻结前做 novelty washout，(5) 对历史踩过的坑做模式匹配。",
        "**操作顺序**：(1) 上线前先算样本量 (sample size)，(2) 看业务指标前先跑 **SRM** 检查，(3) 分析阶段上 **CUPED** / 方差缩减，(4) 冻结结论前完成新奇效应洗期 (novelty washout)，(5) 对历史踩过的已知坑做模式匹配。",
    ),
    (
        '**口述捷径**："开始前 power 足够、看指标前 SRM、分析时 CUPED、相信 lift 前 washout、永远看看你是不是踩了见过的坑。"',
        '**口述捷径**："实验开始前确保功效足够、看指标之前先跑 SRM、分析时做 CUPED 方差缩减、在相信 lift 之前做 novelty 洗期、永远回头看看你是不是踩到了历史见过的坑。"',
    ),
    (
        "对均值相等的双边检验，总 variance 为 $\\sigma^2$、目标 lift 为 $\\delta$，每 arm 样本量：",
        "对均值相等假设的双边检验，总方差为 $\\sigma^2$、目标 lift 为 $\\delta$ 时，每个分流臂所需样本量为：",
    ),
    (
        "**推导草图**：在 $H_0$ 下检验统计量 $\\sim N(0, 1)$；在 $H_1$ 下 $\\sim N(\\delta / \\text{SE}, 1)$，其中 $\\text{SE} = \\sqrt{2 \\sigma^2 / n}$。在双边 $\\alpha$ 下拒绝 $H_0$ 要求 $|T| > z_{\\alpha/2}$；在 $H_1$ 下达到 power $1 - \\beta$ 要求 $\\delta / \\text{SE} \\ge z_{\\alpha/2} + z_{\\beta}$。解 $n$ 得公式。**两个 $z$ 分位数相加**是因为它们衡量**同一方向上**的临界位置和拒绝尾。",
        "**推导草图**：在原假设 $H_0$ 下检验统计量服从 $N(0, 1)$；在备择假设 $H_1$ 下服从 $N(\\delta / \\text{SE}, 1)$，其中标准误 $\\text{SE} = \\sqrt{2 \\sigma^2 / n}$。在双边显著性 $\\alpha$ 下拒绝 $H_0$ 要求 $|T| > z_{\\alpha/2}$；在 $H_1$ 下达到 power $1 - \\beta$ 要求 $\\delta / \\text{SE} \\ge z_{\\alpha/2} + z_{\\beta}$。解 $n$ 即得公式。**两个 $z$ 分位数相加**的原因在于它们衡量的都是**同方向上**的临界位置与拒绝尾距离。",
    ),
    (
        "power 条件解出 $n$ 就是 sample-size 公式：",
        "从功效条件中解出 $n$，即得样本量公式：",
    ),
    (
        "**典型分位数**：$\\alpha = 0.05$ 双边、power = 0.80：$z_{\\alpha/2} = 1.96, z_{\\beta} = 0.84$，$(1.96 + 0.84)^2 \\approx 7.84$。",
        "**典型分位数**：显著性 $\\alpha = 0.05$ 双边、功效 power = 0.80 对应 $z_{\\alpha/2} = 1.96, z_{\\beta} = 0.84$，平方和 $(1.96 + 0.84)^2 \\approx 7.84$。",
    ),
    (
        "**数值锚点**：$\\sigma = 12$ USD/user 收入、$\\delta = 0.20$ USD（$\\approx 4\\%$ lift on 5 USD baseline） => $n = 2 \\cdot 144 \\cdot 7.84 / 0.04 \\approx 56{,}448$ /arm。用 CUPED 把 $\\sigma$ 砍半 => $n$ 降到约 14,000——**最大的单一杠杆**。",
        "**数值锚点**：用户收入标准差 $\\sigma = 12$ 美元、目标 $\\delta = 0.20$ 美元（相当于 5 美元基线上约 4% lift），则 $n = 2 \\cdot 144 \\cdot 7.84 / 0.04 \\approx 56{,}448$ / 每臂。如果上 CUPED 把 $\\sigma$ 砍半，则 $n$ 降到约 14,000——这是**最大的单一杠杆**。",
    ),
    (
        "**比例指标**（CTR / CVR）baseline 为 $p$，代入 $\\sigma^2 = p(1-p)$。$p = 2\\%$、相对 **MDE** 10%（$\\delta = 0.002$）下 $n \\approx 80{,}600$ /arm（pooled variance）。",
        "**比例类指标**（点击率 CTR / 转化率 CVR）基线为 $p$ 时，代入 $\\sigma^2 = p(1-p)$。取 $p = 2\\%$、相对 **MDE** 10%（即 $\\delta = 0.002$）时，$n \\approx 80{,}600$ / 每臂（pooled 方差）。",
    ),
    (
        '**口述捷径**："$n$ 规模随 $\\sigma^2 / \\delta^2$——MDE 减半，$n$ 翻 4 倍；$\\sigma$ 减半，$n$ 减半。公式背下：$2 \\sigma^2 (z_{\\alpha/2} + z_\\beta)^2 / \\delta^2$。"',
        '**口述捷径**："样本量规模随 $\\sigma^2 / \\delta^2$ 变化——最小可检测效应减半，样本量翻 4 倍；方差减半，样本量减半。核心公式必背：$n = 2 \\sigma^2 (z_{\\alpha/2} + z_\\beta)^2 / \\delta^2$。"',
    ),
    (
        "**SRM = Sample Ratio Mismatch**：用卡方检验观测到的 arm 尺寸是否匹配设计分配（如 50/50 或 90/10）。",
        "**样本比不匹配** (SRM = Sample Ratio Mismatch)：用卡方检验 (chi-square test) 判断观测到的分流臂样本量是否符合设计分配（如 50/50 或 90/10）。",
    ),
    (
        "对比观测 arm 数 $N_k$ 与期望 $E_k$ 的卡方统计量：",
        "对比观测到的每臂样本量 $N_k$ 与期望值 $E_k$ 的卡方统计量：",
    ),
    (
        "**关键框架**：SRM 是**随机化诊断 (randomization diagnostic)**，**不是结果指标**。它不告诉你 treatment 有没有用。它告诉你**随机化、logging、过滤 pipeline 是否可信**。SRM 触发意味着你看到的是 pipeline bug，而不是 hypothesis test。",
        "**关键心智框架**：SRM 是一个**随机化诊断** (randomization diagnostic)，**不是结果指标**。它不告诉你处理组是否有效。它告诉你**随机化、日志、过滤流水线是否可信**。SRM 一旦触发，你看到的就是一个流水线 bug，而不是假设检验的结果。",
    ),
    (
        "**SRM 触发的常见根因**：\n\n- Bot / crawler 过滤**跨 arm 非对称**（某 arm 缓存方式不同、某 arm 被 pre-roll 过滤漏掉）\n\n- Redirect 或 feature-flag 代码在某 arm 抛异常、用户被**静默丢失**\n\n- Logging 被某变体**延迟或丢失**（例如 treatment 触发一个新信标而该信标在 Safari 里失败）\n\n- Trigger 条件依赖**只在某 arm 里计算**的特征（post-treatment filtering）",
        "**SRM 触发的常见根因**：\n\n- 爬虫 (bot / crawler) 过滤**在两臂上不对称**（某臂缓存策略不同、某臂被预热过滤漏掉）\n\n- 跳转 (redirect) 或特性开关 (feature-flag) 代码在某一臂抛异常，用户被**静默丢失**\n\n- 日志对某一变体**延迟或丢失**（例如处理组触发了一个新信标、而该信标在 Safari 里失败）\n\n- 触发条件 (trigger) 依赖**只在某一臂里计算**的特征（即处理后过滤 post-treatment filtering）",
    ),
    (
        "**互联网规模下**，1M 用户的 49.4 / 50.6 就能跑出卡方 $p < 0.001$——SRM **非常敏感**。信任告警：SRM 触发**作废**所有下游指标。",
        "**在互联网级规模下**，100 万用户的 49.4 / 50.6 分布就足以跑出卡方 $p < 0.001$——SRM **极其敏感**。务必信任这个告警：一旦 SRM 触发，**所有下游指标全部作废**。",
    ),
    (
        "**操作规则**：在生成任何 lift 报告**之前**，在 pipeline 内跑 SRM。如果 SRM 失败，把实验 gate 到\"阻塞-调查中\"——**不要用眼瞟 OEC**；那个数字已被造成偏移的原因污染。",
        "**操作规则**：在生成任何 lift 报告**之前**，务必先在流水线里跑 SRM。如果 SRM 失败，把实验置为\"阻塞-调查中\" (blocked-investigating) 状态——**不要用眼瞟总评估指标**；那个数字已经被造成偏移的同一个原因污染。",
    ),
    (
        '**口述捷径**："SRM 是 arm 尺寸的卡方检验。管道健康检查，不是 treatment 结果。触发 => pipeline bug，不是 flat/lift。永远先于任何业务指标跑。"',
        '**口述捷径**："SRM 是对分流臂样本量的卡方检验。属于流水线健康检查，不是处理结果。触发等于存在流水线 bug，不是 flat 或 lift。永远优先于任何业务指标运行。"',
    ),
    (
        "**CUPED (Deng et al. 2013, Microsoft)** 是方差缩减的主力。选一个**实验开始前**测量的协变量 $X_{\\text{pre}}$（比如同一用户实验开始前 14 天的 revenue）。把 $Y$ 对 $X_{\\text{pre}}$ 回归得到 $\\theta$，再分析残差：",
        "**CUPED 方法** (Deng 等 2013, Microsoft) 是方差缩减的主力。选取一个**实验开始前**测量的协变量 $X_{\\text{pre}}$（例如同一用户在实验开始前 14 天的收入）。把 $Y$ 对 $X_{\\text{pre}}$ 做最小二乘回归得到系数 $\\theta$，然后分析调整后的残差：",
    ),
    (
        "调整后的指标：减去 pre-period 协变量的 OLS 预测：",
        "调整后的指标：从原指标中减去实验前协变量的 OLS 预测值：",
    ),
    (
        "**残差方差被 pre-post 相关系数 $\\rho$ 的平方砍掉**：",
        "**残差方差被实验前-实验后相关系数 $\\rho$ 的平方砍掉**：",
    ),
    (
        "因为随机分配保证了 $\\mathbb{E}[X_{\\text{pre}} \\mid \\text{treatment}] = \\mathbb{E}[X_{\\text{pre}} \\mid \\text{control}]$，减去 $\\theta \\cdot (X_{\\text{pre}} - \\bar{X})$ **不会偏估 treatment 效应**。它只是重新分解方差：**同一用户跨期共有的随机噪声被吸进协变量**。",
        "由于随机分配保证了 $\\mathbb{E}[X_{\\text{pre}} \\mid \\text{处理}] = \\mathbb{E}[X_{\\text{pre}} \\mid \\text{对照}]$，减去 $\\theta \\cdot (X_{\\text{pre}} - \\bar{X})$ **并不会给处理效应引入偏差**。它只是重新分解方差：**同一用户跨期共享的随机噪声被吸收进协变量里**。",
    ),
    (
        "**样本量按同一因子下降**：$n_{\\text{CUPED}} = n \\cdot (1 - \\rho^2)$。同用户 pre/post 的典型 $\\rho$：0.5 => 样本减 25%；0.7 => 减 51%。**Ads / revenue 类指标常能打到 $\\rho = 0.6 \\sim 0.8$**，因为重度用户在两个窗口都占优。",
        "**样本量按同一因子下降**：$n_{\\text{CUPED}} = n \\cdot (1 - \\rho^2)$。同一用户实验前后的典型相关系数：$\\rho = 0.5$ 对应样本量减少 25%；$\\rho = 0.7$ 对应减少 51%。**广告或收入类指标经常能打到 $\\rho = 0.6 \\sim 0.8$**，因为重度用户在实验前后两个窗口里都占主导。",
    ),
    (
        "**踩坑点**：协变量**必须只用 pre-period 数据**、**绝不能被 treatment 污染**。如果 $X_{\\text{pre}}$ 偷偷包含了实验开始当天，它就变成 post-treatment，CUPED 会让估计有偏。**安全规则：在 randomization 时刻冻结 $X_{\\text{pre}}$、存下来、永不重算**。",
        "**踩坑点**：协变量**必须完全取自实验前时段的数据**、**绝不能被处理变量污染**。如果 $X_{\\text{pre}}$ 偷偷包含了实验开始当天的数据，它就变成了处理后变量，CUPED 会让估计产生偏差。**安全规则**：在随机化 (randomization) 时刻冻结 $X_{\\text{pre}}$、存档、之后永不重新计算。",
    ),
    (
        "**Type I 不变**：因为 $\\theta$ 在 pooled 数据上拟合、treatment 与 $X_{\\text{pre}}$ 期望下正交，$\\mathbb{E}[Y_{\\text{CUPED}} \\mid \\text{treat}] = \\mathbb{E}[Y_{\\text{CUPED}} \\mid \\text{control}]$ 的检验 Type I 不变。**方差缩减是免费的 power 提升**。",
        "**第一类错误率不变**：因为系数 $\\theta$ 在合并 (pooled) 数据上拟合、处理变量与 $X_{\\text{pre}}$ 在期望下正交，所以关于 $\\mathbb{E}[Y_{\\text{CUPED}} \\mid \\text{处理}] = \\mathbb{E}[Y_{\\text{CUPED}} \\mid \\text{对照}]$ 的检验保持第一类错误率不变。**方差缩减等于免费的功效提升**。",
    ),
    (
        '**口述捷释**："CUPED 减去 $\\theta$ 乘以 pre-period 协变量残差。方差降 $1 - \\rho^2$、样本降同一因子。只用 pre-period、在 randomization 时冻结。免费 power，无 bias，Type I 不变。"',
        '**口述捷径**："CUPED 的本质是减去 $\\theta$ 乘以实验前协变量残差。方差下降因子 $1 - \\rho^2$，样本量下降同一因子。协变量仅用实验前、并在随机化时冻结。属于免费的 power 提升、不引入偏差、第一类错误率保持不变。"',
    ),
    (
        "任何 UX 变化的前几天都会出现**两种相反**的时间偏差：\n\n- **Novelty (新奇效应)**：用户点新东西是**因为它新**（第 1-3 天 CTR 高估、第 7 天衰减）。常见于视觉改版、新角标位置、新推荐位。\n\n- **Primacy (首因效应)**：用户忽视或抵抗新东西——因为不熟悉、或隐藏了他们依赖的功能（第 1-3 天参与度压低、第 7 天恢复）。常见于布局重排、按钮移除、tab 改名。",
        "任何用户体验 (UX) 变化的最初几天都会出现**两种相反**的时间偏差：\n\n- **新奇效应** (Novelty)：用户点新东西是**因为它新** （前 1-3 天点击率高估、第 7 天左右衰减）。常见于视觉改版、新角标位置、新推荐位。\n\n- **首因效应** (Primacy)：用户忽视或抵抗新东西——或是因为不熟悉、或是隐藏了他们依赖的功能（前 1-3 天参与度被压低、第 7 天左右恢复）。常见于布局重排、按钮移除、标签页 (tab) 改名。",
    ),
    (
        "两种效应都在**相近的 3-7 天时间尺度**上衰减。**一周 washout** 意味着：开始实验，**忽略前 7 天**做点估计，从稳定尾部读 lift。或者画 7 天滚动 lift 曲线，只信任**平台期**。",
        "两种效应都在**相近的 3-7 天时间尺度**上衰减。**一周洗期** (washout) 的操作含义是：开始实验后，**忽略前 7 天数据**再做点估计，从稳定尾部读取 lift。或者画出 7 天滚动 lift 曲线，只信任曲线进入**平台期**之后的读数。",
    ),
    (
        "Washout 分析：在 novelty 窗口后 ($T \\ge 14$) 平均 lift：",
        "洗期分析：在新奇窗口之后（即要求 $T \\ge 14$）计算平均 lift：",
    ),
    (
        "**为什么偏偏是一周**：产品使用周期**以周为单位**（工作日 vs 周末、发薪日、邮寄时间）。短于 7 天的窗口还携带 day-of-week 混淆，所以 7 天**一招处理 novelty + 周期性**。",
        "**为什么恰好取一周**：产品使用周期**本身以周为单位**（工作日 vs 周末、发薪日、邮寄时间）。短于 7 天的窗口还会带有星期几 (day-of-week) 混淆，所以取 7 天可以**一招同时处理新奇效应与周期性**。",
    ),
    (
        "**失败模式**：把第 3 天的 lift 当作定论。如果 novelty 是 +5%、真实效应是 0%，第 3 天说\"上线\"、第 2 个月说\"指标怎么回来了？\"。广告排序上线的事后分析里**常见 novelty 没 washout** 导致的回溯。",
        "**失败模式**：把第 3 天的 lift 当作最终结论。如果新奇效应贡献了 +5%、而真实效应其实是 0%，第 3 天拍板\"上线\"、第二个月又发出\"指标怎么掉回去了？\"。广告排序上线事后分析中**经常见到未做新奇洗期**导致的回滚。",
    ),
    (
        "配套：**Cohort 新鲜度检验**——按\"本实验内首次暴露\" vs \"已在前置重叠实验里暴露过\"分组。如果 novelty 真的存在，新 cohort 的 gap 最大。",
        "配套诊断：**队列 (cohort) 新鲜度检验**——按\"本实验内首次暴露\"与\"已在前置重叠实验里暴露过\"分组。若新奇效应真的存在，新队列的 gap 最大。",
    ),
    (
        '**口述捷径**："Novelty = 早期正向偏；primacy = 早期负向偏；两者都 3-7 天衰减。跑至少 14 天，lift 从第 8 天起读。7 天同时吞掉 day-of-week 混淆。"',
        '**口述捷径**："新奇效应是早期正向偏，首因效应是早期负向偏，两者都在 3-7 天内衰减。实验至少跑 14 天，lift 从第 8 天起读。7 天窗口能同时吞掉星期几的混淆因子。"',
    ),
    (
        "现实世界的复合陷阱，来自 Etsy Google Merchant Bidding (GMB) 实验。一次 bid multiplier 变化 A/B 跨合格 campaign 测试。**观察到的 lift 看起来又大又 stat-sig；上线被三次独立的 rigor 检查连续挡下**。",
        "现实世界的复合陷阱，来自 Etsy 的 Google 购物广告 (GMB) 实验。一次出价倍数 (bid multiplier) 变更的 A/B 跨合格广告活动 (campaign) 测试。**观察到的 lift 看起来既大又显著 (stat-sig)；但上线被三道独立的严谨性检查连续挡下**。",
    ),
    (
        "**Trap 1: Unit-of-analysis mismatch (分析单位错配)**。Randomization 在 **campaign 级**，但指标（revenue per impression）在 **impression 级**聚合。方差按\"impression i.i.d.\"计算——系统性**低估** SE，因为同 campaign 内 impression 相关。**名义 $p = 0.02$ 在正确的 cluster-robust SE 下塌到 $p = 0.15$**。",
        "**陷阱 1：分析单位错配** (Unit-of-analysis mismatch)。随机化发生在**广告活动级别**，但指标（每次曝光收入 revenue per impression）却在**曝光 impression 级别**聚合。方差按\"曝光独立同分布\"计算——从而系统性**低估**标准误 (SE)，因为同一广告活动内的曝光是相关的。**名义 $p = 0.02$ 在正确的簇稳健标准误 (cluster-robust SE) 下会塌到 $p = 0.15$**。",
    ),
    (
        "Design effect：cluster size $m$、intra-cluster 相关 $\\rho_{\\text{icc}}$ 膨胀方差：",
        "设计效应 (design effect)：簇大小 $m$、簇内相关系数 $\\rho_{\\text{icc}}$ 共同使方差膨胀：",
    ),
    (
        "**Trap 2: 拍卖密度不对称造成的 SRM**。Treatment 因为 multiplier 更高**赢更多拍卖**，所以 treatment campaign 在同窗口里**服务了更多 impression**。这看起来像 SRM（campaign 级 50/50 没问题、impression 级 53/47 报警）。**但这不是 bug——是 treatment 效应泄漏进了分配比例**。教训：**SRM 必须在 randomization 单位（campaign）上跑，不是 analysis 单位（impression）**，否则正当的赢会看起来像 pipeline 失败。",
        "**陷阱 2：拍卖密度不对称引发的 SRM**。处理组因为出价倍数更高**赢得了更多拍卖**，因此处理组广告活动在同一窗口内**服务了更多曝光**。看上去像是 SRM（活动级别 50/50 没问题、曝光级别 53/47 报警）。**但这其实不是 bug——而是处理效应泄漏进了分配比例**。教训：**SRM 必须在随机化单位（广告活动）上运行，而不是在分析单位（曝光）上运行**，否则一个正当的拍卖胜利会被误认为流水线失败。",
    ),
    (
        "**Trap 3: 出价曲线里的 novelty**。第 1-4 天显示 +8% revenue lift——因为 Google smart-bidding 系统还没**重新校准竞争响应**。第 10 天 lift 稳定在 +1.5%——竞品 bid 已调整。**把第 4 天数字当上线定论 = 三倍计了这个过渡性优势**。",
        "**陷阱 3：出价曲线里的新奇效应**。前 1-4 天显示 +8% 的收入 lift——因为 Google 智能出价 (smart-bidding) 系统还没有**针对新的竞争响应重新校准**。第 10 天 lift 稳定在 +1.5%——对手的出价已经调整过来。**把第 4 天的数字当作上线结论，等于把这个过渡性优势放大了三倍**。",
    ),
    (
        "**结果**：ship 决策翻为\"iterate\"。14 天 washout + cluster-robust SE + campaign-level SRM 后的最终读数：lift = +1.1%, $p = 0.08$，$\\alpha = 0.05$ 下**不 stat-sig**。加宽合格范围 + CUPED on pre-period GMV 增加 power，下季度成功检测到稳健的 +0.9% lift。",
        "**最终结果**：上线决策被翻为\"迭代\" (iterate)。在 14 天洗期、簇稳健标准误、广告活动级别 SRM 全部过关后，最终读数为：lift = +1.1%, $p = 0.08$，在 $\\alpha = 0.05$ 下**并不显著**。通过放宽合格范围加上在实验前商品交易额 (GMV) 上做 CUPED 来提升 power，下一季度成功检测到稳健的 +0.9% lift。",
    ),
    (
        "**要点模式**：在 bidding / auction 实验里盯紧 (a) randomization 单位与 analysis 单位的相关、(b) treatment 效应泄漏进分配比例、(c) novelty 不光来自用户、还来自周边拍卖生态。**广告平台是对抗系统——竞品在几天内响应你的 treatment，而不是瞬间**。",
        "**要点模式**：在出价 / 拍卖类实验里必须盯紧 (a) 随机化单位与分析单位之间的相关性、(b) 处理效应泄漏进分配比例、(c) 新奇效应不仅来自用户、还来自周边拍卖生态。**广告平台本质上是一个对抗系统——竞品会在几天内响应你的处理，而不是瞬时**。",
    ),
    (
        '**口述捷径**："Etsy GMB 我见过复合陷阱——impression 级 SE 低估、拍卖密度触发 SRM、拍卖级 novelty。用 campaign 级 cluster-robust SE、campaign 级 SRM、14 天 washout 修掉。把 $p=0.02$ 的 ship 翻成 $p=0.08$ 的 iterate。"',
        '**口述捷径**："Etsy GMB 案例里我见过三重复合陷阱——曝光级标准误低估、拍卖密度触发 SRM、拍卖级别的新奇效应。修复办法是活动级簇稳健标准误、活动级 SRM、14 天洗期。最终把 $p=0.02$ 的上线翻成了 $p=0.08$ 的迭代。"',
    ),
    (
        "**顺序关键**：上线前算样本量、出指标前跑 SRM、分析时做方差缩减、结论前 washout、前后做模式匹配。",
        "**顺序至关重要**：上线前算样本量、出指标前跑 SRM、分析阶段做方差缩减、结论前做洗期、前后都做已知坑位模式匹配。",
    ),
    (
        "背几个锚点、30 秒内估出 $n$：",
        "背几个常用锚点数字，就可以在 30 秒内估算出 $n$：",
    ),
    (
        "- [ ] 样本量公式：$n = 2 \\sigma^2 (z_{\\alpha/2} + z_\\beta)^2 / \\delta^2$\n- [ ] 两个 $z$ 分位数相加是因为衡量的都是**同方向**的距离\n- [ ] SRM = arm 尺寸卡方；随机化健康，不是结果\n- [ ] SRM 在 randomization 单位上跑，不在 analysis 单位\n- [ ] CUPED = $Y - \\theta (X_{\\text{pre}} - \\bar{X})$；方差降 $(1 - \\rho^2)$\n- [ ] CUPED 协变量**严格 pre-treatment**、randomization 时冻结\n- [ ] Novelty = 早期正偏、Primacy = 早期负偏\n- [ ] 一周 washout 同时吞 novelty 和 day-of-week 周期\n- [ ] **永远声明分析单位和 randomization 单位**\n- [ ] Etsy GMB 陷阱 = cluster SE + 拍卖密度 SRM + 拍卖 novelty",
        "- [ ] 样本量公式：$n = 2 \\sigma^2 (z_{\\alpha/2} + z_\\beta)^2 / \\delta^2$\n- [ ] 两个 $z$ 分位数相加，原因在于它们衡量的都是**同方向**的距离\n- [ ] SRM 等于分流臂样本量的卡方检验；测的是随机化是否健康，不是结果\n- [ ] SRM 必须在随机化单位上运行，不是在分析单位上运行\n- [ ] CUPED 公式：$Y - \\theta (X_{\\text{pre}} - \\bar{X})$；方差下降因子为 $(1 - \\rho^2)$\n- [ ] CUPED 协变量**严格只取实验前数据**、且在随机化时刻冻结\n- [ ] 新奇效应等于早期正向偏差、首因效应等于早期负向偏差\n- [ ] 一周洗期能同时吞掉新奇效应与星期几周期\n- [ ] **永远要显式声明分析单位和随机化单位两者**\n- [ ] Etsy GMB 案例的三重陷阱等于簇稳健标准误、拍卖密度触发的 SRM、拍卖层面的新奇效应",
    ),
]


# -----------------------------------------------------------------------------
# Apply substitutions + seed
# -----------------------------------------------------------------------------

def apply_subs(content: str, subs: list[tuple[str, str]]) -> tuple[str, int, list[str]]:
    """Apply each (old, new) once. Return (new_content, applied_count, missed)."""
    out = content
    applied = 0
    missed: list[str] = []
    for old, new in subs:
        if old in out:
            out = out.replace(old, new, 1)
            applied += 1
        else:
            missed.append(old[:60])
    return out, applied, missed


def seed_one(conn: sqlite3.Connection, did: int) -> str:
    row = conn.execute(
        "SELECT content FROM company_documents WHERE id=?", (did,)
    ).fetchone()
    if row is None:
        return f"[MISSING] doc {did}"
    current = row[0]

    if SENTINEL in current:
        ratio, _, _ = cjk_ratio(current)
        return f"[UNCHANGED] doc {did} (sentinel present, prose_cjk={ratio:.1%})"

    subs = SUBS.get(did, [])
    new_content, applied, missed = apply_subs(current, subs)

    # Prepend sentinel (once) to top of content if not already present
    if SENTINEL not in new_content:
        lines = new_content.splitlines(keepends=True)
        # Insert sentinel after any existing leading HTML comments on lines 0..2
        insert_at = 0
        for i, ln in enumerate(lines[:3]):
            if ln.strip().startswith("<!--") and ln.strip().endswith("-->"):
                insert_at = i + 1
        lines.insert(insert_at, SENTINEL + "\n")
        new_content = "".join(lines)

    ratio, cjk, latin = cjk_ratio(new_content)
    if ratio < 0.50:
        missed_report = "; ".join(missed) if missed else "(all subs applied)"
        return (
            f"[FAIL] doc {did} post-rewrite prose_cjk={ratio:.1%} (cjk={cjk}, latin={latin}) "
            f"-- need >=50%. applied={applied}/{len(subs)}. missed: {missed_report}"
        )

    # Compare to current -- identical means already seeded to identical bytes
    if new_content == current:
        return f"[UNCHANGED] doc {did} (identical bytes)"

    h_before = hashlib.sha256(current.encode("utf-8")).hexdigest()[:12]
    h_after = hashlib.sha256(new_content.encode("utf-8")).hexdigest()[:12]
    conn.execute(
        "UPDATE company_documents SET content=? WHERE id=?",
        (new_content, did),
    )
    conn.commit()
    return (
        f"[UPDATED] doc {did} prose_cjk={ratio:.1%} (applied={applied}/{len(subs)}) "
        f"{h_before}->{h_after}"
    )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not DB_PATH.exists():
        print(f"[ERROR] DB not found: {DB_PATH}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(str(DB_PATH))
    try:
        print(f"[BEGIN] T-P2-533 CN-batch against {DB_PATH}")
        for did in REWRITE_IDS:
            print(seed_one(conn, did))

        print("\n[VERIFY] all 12 drill docs post-run:")
        any_fail = False
        for did in ALL_DRILL_IDS:
            row = conn.execute(
                "SELECT title, content FROM company_documents WHERE id=?", (did,)
            ).fetchone()
            if row is None:
                print(f"[MISSING] doc {did}")
                any_fail = True
                continue
            title, content = row
            ratio, cjk, latin = cjk_ratio(content)
            status = "[PASS]" if ratio >= 0.50 else "[FAIL]"
            print(f"{status} doc {did}: prose_cjk={ratio:.1%} cjk={cjk} latin={latin} ({title[:60]})")
            if ratio < 0.50:
                any_fail = True

        if any_fail:
            print("\n[FAIL] at least one drill doc is below 50% CN prose")
            return 1
        print("\n[OK] all 12 drill docs pass >=50% CN prose")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
