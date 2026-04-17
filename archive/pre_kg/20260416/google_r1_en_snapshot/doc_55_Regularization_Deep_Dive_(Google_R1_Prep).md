<!-- KG_P2_02_REGULARIZATION_20260416 -->

# Regularization Deep Dive -- Google R1 Prep (Drill)

> **正典** [Regularization (pillar2.regularization.regularization_canonical_hub)](/framework/195)

本 drill 服务 Google R1 面试的**口述练习**：L1 / L2 几何推导、KKT、soft-thresholding、Bayesian prior、AdamW 等核心内容已固化到 canonical hub。此处只保留 **drill-specific** 的战术要点——dropout、early stopping、data augmentation、以及 7 法全景表与 30 秒口述自测。

## Prerequisites

- Canonical hub: [Regularization](/framework/195)（务必先过一遍）
- 神经网络训练循环（forward / backward pass）
- 随机采样与蒙特卡洛的基本直觉

## 1. Dropout -- Bayesian Approximation & Ensemble View

训练阶段：每次前向把每个单元以概率 $p$ 置零。推理阶段：启用全部单元，activation 乘以 $(1-p)$；或训练时用 **inverted dropout** 直接除以 $(1-p)$，推理不变。

**集成视角（Srivastava 2014）**：$n$ 个单元 -> $2^n$ 个 thinned networks。平均预测近似等于一个指数级 ensemble 的平均。

**Bayesian 视角（Gal & Ghahramani 2016）**：推理时**保持 dropout 开启**，做 $T$ 次 forward，得到预测均值与不确定性。MC Dropout 的方差估计：

$$\mathrm{Var}[y^*] \approx \frac{1}{T}\sum_{t=1}^{T} f_{\theta_t}(x^*)^2 - \left(\frac{1}{T}\sum_{t=1}^{T} f_{\theta_t}(x^*)\right)^2$$

**口述捷径**：“Dropout 是 $2^n$ 子网络的廉价集成；推理时不关它还能免费拿到不确定性。”

## 2. Early Stopping -- Implicit L2

从 $w=0$ 起，小学习率的 GD 在权重空间画一条轨迹；**停得早就等于限制 $\|w\|$ 的增长**。$T$ 步 × 学习率 $\eta$ × 梯度上界 $G_{\max}$：

$$\|w_T\| \le \eta \cdot T \cdot G_{\max}$$

Bishop (1995) / Sjoberg & Ljung (1995) 证明：在二次损失下，early stopping 的第 $T$ 步等价于 L2 正则 $\lambda_{\text{eff}} \propto 1/(\eta T)$。

**口述捷径**：“Early stopping = 隐式 L2；步数少 = 范数小 = 正则强。免费但把优化和正则耦合在一起。”

## 3. Data Augmentation -- Vicinal Risk Minimization

ERM 最小化的是**训练点上的平均损失**；数据增广把每个点替换为一个**邻域（vicinity）**。形式化（Chapelle 等 2000）：

$$R_{\text{VRM}} = \frac{1}{n}\sum_{i=1}^{n} \mathbb{E}_{x' \sim \nu(x_i)}[\ell(f(x'), y_i)]$$

vicinity 分布 $\nu$ 编码领域先验：图像用 flip / crop，NLP 用 synonym replacement，Mixup 用插值。**正则化效果**：模型必须在邻域内都对，决策边界被平滑，variance 下降而 bias 不变（只要 augmentation 保标签）。

**口述捷径**：“Augmentation 就是在邻域上训练，不是在点上。数学上是 VRM——vicinity kernel 取代 ERM 里的 Dirac delta。”

## 4. AdamW in One Breath（canonical 已详述，此处仅口述）

> **正典** [Regularization §7 AdamW](/framework/195)

"Adam 的 $v_t$ 把 L2 梯度按历史自适应地缩小，所以正则强度不均匀；AdamW 把 decay 挪到 Adam 步之外，所有参数均匀 $(1-\eta\lambda)$。transformer 用 AdamW。"

## 5. 7-Method Regularization Panorama

| Method | What It Constrains | Oral 10-Second Pitch |
| --- | --- | --- |
| L1 | 激活的特征数 | 菱形顶点在坐标轴 => 稀疏 |
| L2 / Ridge | 权重整体幅度 | 圆面光滑；闭式 $(X'X+\lambda I)^{-1} X'y$ |
| Elastic Net | 相关特征组 | L2 绑定整组，L1 删除整组 |
| Dropout | 隐层共适应 | $2^n$ 子网集成；MC 拿不确定性 |
| Early Stopping | 原点出发的轨迹长度 | 隐式 L2；$\lambda \sim 1/(\eta T)$；最便宜 |
| AdamW | 各参数统一幅度 | decoupled decay；Adam+L2 非 AdamW |
| Data Aug / VRM | 决策边界光滑度 | 在邻域上训练而非点上 |

## 6. 30-Second Oral Self-Check

- [ ] L1 稀疏的三层解释（几何 / 代数 / Bayesian）--- 指向 canonical §1/§5
- [ ] L2 闭式解 $(X^\top X+\lambda I)^{-1}X^\top y$ 与逐奇异值收缩 --- canonical §3
- [ ] Ridge vs Lasso 的 bias 谁更大？两者都 biased，L1 还额外把系数压到 0
- [ ] Dropout = $2^n$ ensemble + MC Dropout uncertainty
- [ ] Early stopping 是隐式 L2，$\lambda\propto 1/(\eta T)$
- [ ] AdamW 的一句话解释（$v_t$ 吞 L2；decay 解耦）
- [ ] Data aug = VRM，vicinity kernel 取代 Dirac delta
- [ ] James-Stein：$p\ge 3$ 时收缩估计严格优于 OLS

**面试口吻收尾**："L1 / L2 的推导我画图+写 KKT+ Bayesian 三条线都能走；dropout 我用 ensemble 和 MC 两种解释；AdamW 我能说清 $v_t$ 吞 L2 这个技术细节。"
