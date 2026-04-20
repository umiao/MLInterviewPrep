"""Seed: T-P0-543 -- ML Fundamentals Y-depth Q#21 SFT / RLHF / DPO.

[T-MLF-06a] CALIBRATION BARRIER. Writes the canonical Y-depth golden
answer for Question 21 (SFT / RLHF / DPO objectives) into
framework_nodes.description for the leaf at path
'ml-fundamentals/llm_stats/sft-rlhf-dpo'.

Y-depth = deep expansion. Per the 5-section template locked in T-P0-540
review (cf. scripts/seed_ml_fundamentals_content_cat5.py):

  1. 问题设定       -- rigorous definitions of three objective types.
  2. 推导           -- Bradley-Terry RM loss; PPO with KL-constrained
                       objective; DPO closed-form showing the partition
                       function Z(x) cancellation step-by-step.
  3. 物理意义       -- why ref model stays as KL anchor; reward hacking;
                       why DPO is supervised but still aligned.
  4. 常见追问预判   -- 5+ items (DPO vs IPO vs KTO; beta temperature
                       interpretation; offline vs online; reward
                       overoptimization; iterative DPO).
  5. 参考           -- 2-3 paper refs.

Acronyms first-occurrence expanded in bold **English** (acronym, 中文)
per data/ml_fundamentals_inventory.yaml acronyms_to_expand list:
SFT, RLHF, DPO, PPO, RM, KL, MLE.

Idempotency:
  - Expected description is a single raw-string constant.
  - Second run yields updated=0 skipped=1 conflict=0.
  - SHA-256 of (path, description) captured pre/post for audit.
  - If the existing description is neither the placeholder
    'TODO[MLF-sft-rlhf-dpo]' nor the new content, script aborts
    with [CONFLICT] before any write.

Acceptance:
  - framework_nodes row at path 'ml-fundamentals/llm_stats/sft-rlhf-dpo'
    updated.
  - Description contains KaTeX math ($ or $$) and section headers (## ).
  - Re-run is no-op (updated=0).

Awaiting review barrier: runner MUST stop with status=review (NOT
completed) after this script so the user can read the rendered drawer
and confirm the Y-depth standard before T-P0-544/545 reuse it.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

TARGET_PATH = "ml-fundamentals/llm_stats/sft-rlhf-dpo"
PLACEHOLDER = "TODO[MLF-sft-rlhf-dpo]"


DESC_SFT_RLHF_DPO = r"""# SFT / RLHF / DPO 三种目标函数

## 1. 问题设定

预训练语言模型输出 token 的下一个概率分布 $\pi_\theta(y \mid x)$，但"预测下一个 token"与"对人类有用、诚实、无害"并不直接对齐。对齐的三条主流路线分别对应三种**目标函数**（objective）：

- **Supervised Fine-Tuning** (SFT, 监督微调)：在高质量 `(prompt, response)` 示范数据上做最大似然。
- **Reinforcement Learning from Human Feedback** (RLHF, 基于人类反馈的强化学习)：先从成对偏好 $(y_w \succ y_l \mid x)$ 学一个**Reward Model** (RM, 奖励模型)，再用 **Proximal Policy Optimization** (PPO, 近端策略优化) 在 $\text{RM} - \beta \cdot \text{KL}$ 组合目标上把策略往高奖励推，同时用 **Kullback-Leibler divergence** (KL, KL 散度) 把策略拉回参考模型附近防止跑飞。
- **Direct Preference Optimization** (DPO, 直接偏好优化)：跳过 RM 与 RL，把 KL-约束最优策略的闭式解代回 Bradley-Terry 偏好似然，得到一个**纯监督**的对比似然损失，直接在成对数据上训。

第一次出现的其他缩写：**Maximum Likelihood Estimation** (MLE, 极大似然估计)。

三种方法的输入、训练信号和最终模型如下。

| 方法 | 训练数据 | 训练信号 | 最终产物 | 训练阶段 |
|------|----------|----------|----------|----------|
| SFT | `(x, y)` 单条示范 | 每 token 交叉熵 | $\pi_{\text{SFT}}$ | Stage 1（RLHF 的起点） |
| RLHF | 偏好对 $(x, y_w, y_l)$ + SFT 模型 | RM 得分 $-\beta\,\text{KL}$ | $\pi_{\text{RLHF}}$ | Stage 2（RM → PPO） |
| DPO | 偏好对 $(x, y_w, y_l)$ + SFT 参考 | 对比对数似然（偏好数据直接喂） | $\pi_{\text{DPO}}$ | 替代 Stage 2（单阶段） |

## 2. 推导

### 2.1 SFT：示范数据上的 MLE

给定示范数据集 $\mathcal{D}_{\text{SFT}} = \{(x_i, y_i)\}$，把 $y_i = (y_{i,1}, \ldots, y_{i,T})$ 展开成 token 序列，目标是最大化示范序列的对数似然：

$$\mathcal{L}_{\text{SFT}}(\theta) = -\,\mathbb{E}_{(x, y) \sim \mathcal{D}_{\text{SFT}}} \left[ \sum_{t=1}^{T} \log \pi_\theta(y_t \mid x, y_{<t}) \right]$$

这就是预训练的交叉熵目标限制在示范分布上。简单、稳定，问题是**只能克隆示范**：示范里没出现过的好答案、被示范作者偶尔写歪的糟答案，SFT 一视同仁地拟合。SFT 的上限等于示范的上限；要超越示范就需要偏好信号。

### 2.2 RLHF Stage A：Bradley-Terry 奖励模型

人类对成对回答 $(y_w, y_l \mid x)$ 给出"$y_w$ 优于 $y_l$"的偏好标签。假设偏好由一个隐奖励 $r^\star(x, y)$ 驱动，**Bradley-Terry**（1952）偏好模型写作：

$$P(y_w \succ y_l \mid x) = \sigma\!\big(r^\star(x, y_w) - r^\star(x, y_l)\big)$$

$\sigma(z) = 1/(1 + e^{-z})$ 是 logistic sigmoid。用参数化 $r_\phi$ 来逼近 $r^\star$，最大化偏好似然等价于最小化：

$$\mathcal{L}_{\text{RM}}(\phi) = -\,\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}_{\text{pref}}} \left[ \log \sigma\!\big(r_\phi(x, y_w) - r_\phi(x, y_l)\big) \right]$$

**要点**：(i) 标注者只需比大小，不需要打绝对分，降低标注噪声。(ii) 损失只依赖**差值** $r_\phi(x, y_w) - r_\phi(x, y_l)$——对任意函数 $c(x)$，$r_\phi(x, y) + c(x)$ 给出同样的 loss。也就是说 RM 的 $x$-条件常数不可辨识（这个不可辨识性正是下文 DPO 推导里 $Z(x)$ 能消掉的根本原因）。

### 2.3 RLHF Stage B：PPO 在 KL-约束下最大化 RM

有了 $r_\phi$，下一步是训 $\pi_\theta$ 使其高分。朴素 RL 目标 $\mathbb{E}[r_\phi(x, y)]$ 会被 **reward hacking**（奖励劫持）破坏：$\pi_\theta$ 学会钻 RM 的漏洞输出高分但糟糕的答案。解决：加一个以 $\pi_{\text{ref}}$ 为锚的 KL 惩罚，$\pi_{\text{ref}}$ 通常就是 SFT 模型：

$$\max_{\pi_\theta}\; \mathbb{E}_{x \sim \mathcal{D}}\,\mathbb{E}_{y \sim \pi_\theta(\cdot \mid x)} \Big[\, r_\phi(x, y) \,\Big] - \beta\, \mathrm{KL}\!\big(\pi_\theta(\cdot \mid x)\,\|\,\pi_{\text{ref}}(\cdot \mid x)\big)$$

$\beta > 0$ 是 KL 温度（KL 惩罚强度），经验值 $0.01$–$0.1$。这个目标只有期望里的 $\pi_\theta$ 可导，离散 token 采样不可导——所以用 PPO（on-policy 策略梯度，裁剪重要度比 $r_t(\theta) = \pi_\theta / \pi_{\text{old}}$）在线优化。InstructGPT / ChatGPT / Claude 早期训练栈就是这条路线。

工程复杂度：需要同时常驻 policy、reference、reward、critic 四个模型（前三个 forward-only，critic 与 policy 同训），显存与工程负担重。

### 2.4 DPO：把闭式解代回偏好似然，$Z(x)$ 消掉

DPO 的关键是先**解析求解** Stage B 的 KL-约束最大化问题，再用这个最优策略作为 RM 的桥梁，省掉 RM 和 PPO 两段流水线。

**Step 1：KL-约束最优策略的闭式解。** Stage B 的目标等价于对每个 $x$ 独立求解：

$$\max_{\pi}\; \mathbb{E}_{y \sim \pi(\cdot \mid x)}[r(x, y)] - \beta\, \mathrm{KL}\!\big(\pi(\cdot \mid x)\,\|\,\pi_{\text{ref}}(\cdot \mid x)\big)$$

对 $\pi(y \mid x)$ 做变分，配合约束 $\sum_y \pi(y \mid x) = 1$（拉格朗日乘子 $\lambda(x)$），或者直接把 KL 展开为 $\mathbb{E}_\pi[\log \pi - \log \pi_{\text{ref}}]$，得最优性条件 $\log \pi^\star = \frac{1}{\beta} r + \log \pi_{\text{ref}} - \text{const}(x)$，指数化并归一化：

$$\boxed{\; \pi^\star(y \mid x) \;=\; \frac{1}{Z(x)}\,\pi_{\text{ref}}(y \mid x)\,\exp\!\left(\frac{1}{\beta}\, r(x, y)\right) \;}$$

其中 $Z(x) = \sum_{y} \pi_{\text{ref}}(y \mid x)\,\exp(r(x, y)/\beta)$ 是归一化常数，俗称**配分函数**（partition function）。问题：$Z(x)$ 要对整个生成空间求和，**完全不可计算**——这正是 PPO 必须放弃闭式解用采样估计梯度的原因。

**Step 2：反解 $r$，$Z(x)$ 只出现一次。** 取对数：

$$\log \pi^\star(y \mid x) = \log \pi_{\text{ref}}(y \mid x) + \frac{1}{\beta}\,r(x, y) - \log Z(x)$$

反解 $r$：

$$r(x, y) = \beta\,\big(\log \pi^\star(y \mid x) - \log \pi_{\text{ref}}(y \mid x)\big) + \beta \log Z(x)$$

注意 $\beta \log Z(x)$ 是一个**只依赖 $x$ 的常数**。

**Step 3：代入 Bradley-Terry，常数相减消掉。** Bradley-Terry 偏好损失依赖的是**差值** $r(x, y_w) - r(x, y_l)$：

$$r(x, y_w) - r(x, y_l) = \beta\,\big(\log \pi^\star(y_w \mid x) - \log \pi_{\text{ref}}(y_w \mid x)\big) - \beta\,\big(\log \pi^\star(y_l \mid x) - \log \pi_{\text{ref}}(y_l \mid x)\big) + \underbrace{\beta \log Z(x) - \beta \log Z(x)}_{= 0}$$

$$\boxed{\;\; r(x, y_w) - r(x, y_l) \;=\; \beta\,\log \frac{\pi^\star(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta\,\log \frac{\pi^\star(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)} \;\;}$$

$Z(x)$ 对 $y_w, y_l$ 都一样，在差值里干净消掉——不可辨识性恰好是我们的朋友。

**Step 4：把 $\pi^\star$ 换成待优化 $\pi_\theta$，得到 DPO 损失。**

$$\mathcal{L}_{\text{DPO}}(\theta) = -\,\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}_{\text{pref}}} \left[ \log \sigma\!\left(\beta\,\log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta\,\log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\right) \right]$$

形式上是一个**标准对比对数似然**，和 RM 训练长得几乎一样——区别只在于 logit 的参数化换成了 $\beta \log (\pi_\theta / \pi_{\text{ref}})$。工程上：只需要 $\pi_\theta$ 和 $\pi_{\text{ref}}$ 两个模型（后者 forward-only），显存减半；没有采样、没有 critic、没有 clip，稳定性直逼 SFT。

## 3. 物理意义

### 3.1 $\pi_{\text{ref}}$ 为什么必须留作 KL 锚

$\pi_{\text{ref}}$ 同时扮演两个角色：**分布支撑**和**正则化锚**。第一，RLHF/DPO 要学的策略通过 $\pi^\star \propto \pi_{\text{ref}} \cdot \exp(r/\beta)$ 参数化——$\pi_{\text{ref}}$ 给出基础概率质量，偏好信号只能**重新调整**这个质量而不是凭空创造。第二，KL 项把 $\pi_\theta$ 拉回 $\pi_{\text{ref}}$ 附近，防止 reward hacking；$\pi_{\text{ref}}$ 质量越好，最终对齐后的模型质量越好。所以对齐流水线的惯例是：预训练 → SFT（得到 $\pi_{\text{SFT}}$）→ 用 $\pi_{\text{SFT}}$ 作 $\pi_{\text{ref}}$ 做 RLHF / DPO。跳过 SFT 直接从 base model 做 DPO 通常效果很差——$\pi_{\text{ref}}$ 本身没指令跟随能力，DPO 也救不回来。

### 3.2 reward hacking 是什么

RM 是**有限偏好数据**上学出来的**有限容量代理**，它和真实人类偏好 $r^\star$ 有误差。PPO 的梯度沿 $\nabla r_\phi$ 爬山，一旦某类输出能骗到 $r_\phi$ 高分但实际差（比如学会插入"作为大模型，我认为…"这类套话，或者学会特定的标点/格式触发 RM 的假相关性），策略会迅速扑过去。表现：RM 得分持续升、真实人类评分停滞甚至下降——Gao 2023 *Scaling Laws for Reward Model Overoptimization* 给出经验曲线，真实奖励 vs 代理奖励呈倒 U 形。缓解：增大 $\beta$ 让 KL 把策略拉回 $\pi_{\text{ref}}$、扩大偏好数据、早停、RM 集成。

### 3.3 DPO 为什么"长得像监督学习但仍是对齐"

DPO 的损失是标准二元交叉熵的形式，训练像 SFT 一样稳，这经常让人误以为它"只是 SFT 的变种"。但关键在于它对比的**对象不是示范 vs 非示范**，而是**同一 prompt 下的 $y_w$ vs $y_l$**，而且 logit 被定义为 $\beta \log (\pi_\theta / \pi_{\text{ref}})$——这个量可证明等价于 RLHF 在 KL-约束下最优策略对应的隐奖励差。DPO 理论上**等价于**先训一个 RM 再用 PPO 优化（在数据 $\to \infty$、优化完美的极限下），但工程上把两阶段合成一阶段。所以 DPO 不是一个"更好 SFT"，它是一个把 RLHF 闭式化、数值化的实现。

## 4. 常见追问预判

### 4.1 $\beta$ 的物理含义与取值

$\beta$ 是 KL 温度（temperature）。$\beta \to \infty$：KL 权重无穷大，策略锁死在 $\pi_{\text{ref}}$，偏好信号被忽略；$\beta \to 0$：KL 失效，退化为纯 RM 最大化，reward hacking 爆炸。经验值 $\beta \in [0.01, 0.5]$，DPO 原论文默认 $0.1$。在 DPO 损失里 $\beta$ 同时出现在 logit 和隐含温度里，调大会让 loss 对 $\pi_\theta / \pi_{\text{ref}}$ 比值的变化更敏感——**DPO 的 $\beta$ 既控正则也控梯度 scale**。实操：从 $0.1$ 起调，大模型 / 高质量偏好数据可以到 $0.01$–$0.05$；数据噪声大要调大 $\beta$ 防过拟合到噪声偏好对。

### 4.2 DPO vs IPO vs KTO —— 偏好损失的选择

- **Identity Preference Optimization** (IPO, Azar 2023)：指出 DPO 在标注有噪声且偏好强度差不多的对上会过度推挤（logit 差值无界增长），改用 MSE 的对比损失 $\big(\log(\pi_\theta/\pi_{\text{ref}})_{y_w} - \log(\pi_\theta/\pi_{\text{ref}})_{y_l} - \tau\big)^2$ 把 margin clip 住，更稳但拟合偏好的能力稍弱。
- **Kahneman-Tversky Optimization** (KTO, Ethayarajh 2024)：基于前景理论的非对称损失，只需要**单侧**二元反馈（"好 / 不好"，不需要成对），和 Kahneman-Tversky 的 loss aversion 一致。当偏好对数据稀缺、但单边 thumbs up/down 数据多（产品日志里更常见）时优于 DPO。
- 还有 **SimPO**（无 $\pi_{\text{ref}}$，用 length-normalized log-prob）、**ORPO**（把 SFT 和偏好合成单阶段）等。选择经验：数据干净的成对偏好用 DPO，噪声大用 IPO，只有单边反馈用 KTO。

### 4.3 offline DPO vs online DPO / Iterative DPO

原始 DPO 是 **offline**：用**固定的** $(x, y_w, y_l)$ 数据集训一遍，$y_w, y_l$ 一般由早期 SFT 模型采样、由人类（或 GPT-4）标注。问题：数据分布固定，策略越训越跑偏离训练数据分布，梯度信号变差。

**Iterative DPO** / **Online DPO**：训一轮 DPO → 用新策略重新采样 $(y_1, y_2)$ → 用 RM 或人类打新偏好 → 再训一轮。LLaMA-3 指令模型的对齐就是多轮 iterative DPO + 少量 RM + 拒绝采样。这部分把 DPO 从纯离线监督推回"半在线"，理论上趋近 PPO 的效果但工程简单得多。

### 4.4 reward over-optimization 与 KL 预算

PPO 训练中常见的现象：RM 得分一路涨但真实评估打平甚至下降。两种诊断手段：

- **KL budget**：监控 $\mathrm{KL}(\pi_\theta \,\|\, \pi_{\text{ref}})$。经验上 $\mathrm{KL} > 20$–$50$ nats 后真实质量开始掉，InstructGPT 论文画过这条曲线。
- **Goldilocks region**：BoN（Best-of-$N$ 从 $\pi_{\text{ref}}$ 采样 $N$ 条选最高 RM 得分）与 RL 的比较，二者都在中等 KL 处达到真实奖励峰值，更大的 KL 偏差换来的都是 RM 上的"虚高"。

DPO 同样会 over-optimize，但因为 $\beta$ 直接 baked-in，显式调大 $\beta$ 是最直接的缓解手段；再配合早停 + 留一个 held-out 偏好验证集。

### 4.5 为什么不能跳过 SFT 直接 DPO

理论上 DPO 只需要偏好数据 + $\pi_{\text{ref}}$。但若 $\pi_{\text{ref}}$ 是 base model（未经 SFT 的 pretrain checkpoint），它几乎不能生成 instruction-following 风格的文本——偏好对里的 $y_w$ 通常是指令跟随的优质回答，而 $\pi_{\text{ref}}(y_w \mid x)$ 极低，DPO 的 logit $\beta \log (\pi_\theta/\pi_{\text{ref}})$ 在 $y_w$ 上要把概率推得非常大才能区分，数值不稳且难以训练。实操流程恒定为 "Pretrain → SFT → DPO"；跳过 SFT 只适用于 $\pi_{\text{ref}}$ 已经足够 instruction-tuned 的场景。

### 4.6 DPO 的等价性结论究竟有多强

严格表述：在 (i) Bradley-Terry 偏好模型正确、(ii) RM 函数类足够表达、(iii) 优化到最优的假设下，DPO 的最优解 $\pi_\theta^\star$ 等于 RLHF 的最优解 $\pi^\star$。现实中三个假设都不严格成立：人类偏好并非纯 Bradley-Terry（有 ties、有 ordering intransitivity）、$\pi_\theta$ 受容量和优化限制、数据也有限。因此**实证比较**（LLaMA-2 RLHF vs LLaMA-3 iterative DPO vs Claude's constitutional AI 等）才是判据，而非理论等价性。

## 5. 参考

- Rafailov et al. 2023, *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* —— DPO 原论文，上面 §2.4 的推导严格按照这篇的 Lemma 1 + Theorem 1。
- Christiano et al. 2017, *Deep Reinforcement Learning from Human Preferences* + Ouyang et al. 2022, *Training language models to follow instructions with human feedback* (InstructGPT) —— Bradley-Terry RM + PPO 这条路线的正典。
- Azar et al. 2023, *A General Theoretical Paradigm to Understand Learning from Human Preferences* (IPO) 与 Ethayarajh et al. 2024, *KTO: Model Alignment as Prospect Theoretic Optimization* —— DPO 的主要变体与改良。
- Gao et al. 2023, *Scaling Laws for Reward Model Overoptimization* —— reward hacking / over-optimization 的经验曲线与 KL budget 分析。
"""


def sha256_of_description(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) pair of the target leaf."""
    h = hashlib.sha256()
    row = conn.execute(
        "SELECT description FROM framework_nodes WHERE path = ?", (TARGET_PATH,)
    ).fetchone()
    h.update(TARGET_PATH.encode("utf-8"))
    h.update(b"\x00")
    h.update((row[0] or "").encode("utf-8"))
    h.update(b"\x00")
    return h.hexdigest()


def validate_content(path: str, content: str) -> None:
    """AC: description must contain KaTeX math + at least one section header."""
    if "$" not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no $...$ math delimiter found")
    if "## " not in content:
        raise RuntimeError(f"[AC-FAIL] {path}: no '## ' section header found")


def main() -> int:
    """Update the single Q#21 leaf with the Y-depth golden answer (idempotent)."""
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    validate_content(TARGET_PATH, DESC_SFT_RLHF_DPO)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_description(conn)
        print(f"[PRE]  sha256={pre_hash}")

        row = conn.execute(
            "SELECT id, description FROM framework_nodes WHERE path = ?",
            (TARGET_PATH,),
        ).fetchone()
        if row is None:
            print(f"[FAIL] missing node at path={TARGET_PATH}")
            return 1
        node_id, current = row

        if current == DESC_SFT_RLHF_DPO:
            print(f"[SKIP]   id={node_id} path={TARGET_PATH} (already up-to-date)")
            counts = {"UPDATED": 0, "SKIPPED": 1}
        elif current != PLACEHOLDER:
            preview = (current or "")[:80].replace("\n", " ")
            raise RuntimeError(
                f"[CONFLICT] path={TARGET_PATH}: existing description neither "
                f"placeholder nor expected new content. current[:80]={preview!r}"
            )
        else:
            conn.execute(
                "UPDATE framework_nodes SET description = ? WHERE id = ?",
                (DESC_SFT_RLHF_DPO, node_id),
            )
            conn.commit()
            counts = {"UPDATED": 1, "SKIPPED": 0}
            print(
                f"[UPDATE] id={node_id} path={TARGET_PATH} "
                f"len={len(DESC_SFT_RLHF_DPO)} (was {len(current)})"
            )

        post_hash = sha256_of_description(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    total = counts["UPDATED"] + counts["SKIPPED"]
    print(
        f"[SUMMARY] updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total={total} (expected 1)"
    )
    if total != 1:
        print("[FAIL] expected to touch exactly 1 leaf")
        return 1
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
