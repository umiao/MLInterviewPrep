# Meta-Prompt: ML Implementation 笔记精简改写

> **用法**：在新对话里贴这份文档，然后贴你的草稿，要求 Claude "按此规范改写"。改写完逐条对照"验收清单"自检。

---

## 总体哲学

**前压信息密度，后做极简切分**。开头 6 行 TL;DR 必须独立完成"复述算法"任务；中段把代码切成自然组件，每段前置散文讲 *why*，代码本体只保留锚点注释；末尾对比/追问用表格和 cheat sheet 压到极限。

**Why 在散文里，What 在代码里**——这是整个改写的轴心原则。算法动机、几何直觉、对比理由都该在 code block **之前**的散文里讲完，code block 内部只剩 shape 标注、锚点、边界 case。如果你发现自己在写 inline 多行注释解释数学，那段注释应该被提炼成 1-2 行散文挪到代码上方。

**删除（不要犹豫）**：
- 论文引用、年份、作者名
- "何时还会选用 X" 这类教学性 stretch 段落
- "关键要点" 段（一定和 intro 重复）
- 完整数学证明（保留结论公式即可）
- 教学性长注释（"为什么这么做"那种）

**保留（不要妥协）**：
- 30 秒内能讲完、面试官会追问的细节
- 失败模式（empty cluster、NaN、numerical overflow、奇异矩阵）
- 时间/空间复杂度
- 同类算法的对比要点（一句话级别）
- 数值稳定性 trick（如果是该算法的灵魂）

---

## 标准骨架

每份笔记**按此顺序**，无例外：

1. **TL;DR**（5-7 行 blockquote）— 算法定位、核心循环编号步骤、边界条件、空/退化情况、复杂度
2. **实现**（5-8 个 section）— 每 section 一个 code block，前置 1-2 行散文
3. **变体对比表**（如有变体）— 表格 + 1 句总结
4. **面试追问 Cheat Sheet**— 每问 `> **Q: ...**` 引导，下面 1-3 行 bullet

---

## Section 切分规则

按"**独立可白板**"的颗粒度切。一段代码独立讲完一个 step 就切。

**典型边界**：
- `__init__` → 单独一段（标题 "Class skeleton"）
- 每个独立的 helper 一段（init / E-step / M-step / objective / utility）
- 多个变体（如 vanilla vs ++）**同一 section 内**用 `**加粗小标题**` 区分，**不要**拆成两个 section
- 主循环单独一段，inline 用 `# Criterion N` 或 `# Step N` 作锚点
- predict / inference 单独一段（即使只有 1-2 行）

**反例**：把 helper 全塞进一个超长 class block。这破坏了"白板时只贴一段"的诉求。

---

## Inline 注释规范

**允许**：
- shape: `# (n, k)`
- 锚点: `# Criterion 2: max iter`
- 边界 case: `# else: empty cluster fallback`
- 数值稳定性 hint: `# avoid log(0)`

**禁止**：
- 算法解释（应在散文）
- 多行段落（>1 行）
- 中英混排长句
- 重复散文已讲过的 why

---

## Shape-per-line decomposition

每个产生形状变化的 numpy 操作单独一行，配 `# (shape)` 注释。禁止把 3+ 步链式操作压缩到一个表达式（典型反例：`np.array([... for c in centers]).T`）。"一次只算一个 vector" 是默认姿态——`(d,)` → `(n, d)` broadcast → `(n,)` → list of K → `(k, n)` → `.T` → `(n, k)` → argmin → `(n,)` 应该是 7 行 7 个 shape 注释，不是一行链式。

目标：白板时读者按行追形状变化，不需要心算 numpy 隐式 broadcast / axis 推导。

---

## 表格与对比

变体对比**强制用表格**，不要写成散文段落。

- 列数 ≤ 5，每格 ≤ 12 字
- 表头按算法选：选择方式 / 失败模式 / 实践默认值 / 理论保证 / 复杂度
- 表格下方**必须**一句话总结，给出"两者本质差异"或"何时偏好哪个"

---

## 追问 Cheat Sheet 格式

```markdown
> **Q: 问题文本**

- **术语**：1 行机制 + 半行局限。
```

每个问题 1-3 个 bullet，每 bullet ≤ 2 行。**如果某条追问需要展开到一整段，说明它不该出现在 cheat sheet 里**——要么提升到正文 section，要么删除。

---

## 排版细节

- 数学：`$$...$$`（所有公式，包括 inline 的复杂度）
- 关键术语首次出现：`**bold**`
- 算法名 / library 名 / 变量名：`` `inline code` ``
- 章节分隔：`---`
- 引用 / Q&A：`> blockquote`
- 列表：`-`（统一，不混用 `*`）
- 不用 emoji
- TL;DR 用 blockquote 包裹，每行用 `>` 起头

---

## End-to-end test block

每份笔记末尾必须以 `## End-to-end test` 章节收尾（visible，不要折叠），位置在完整实现之后（main loop / predict 之类全部讲完）。约束：

- ≤ 10 行
- 用 `np.random.rand` / `np.random.randn` + 命名常量 `N, D`（和 `K` 如适用）
- instantiate class → `fit()` → 可选 `predict()` → assert output shape
- < 1s 内跑完，无外部依赖
- 改写时 autonomous session 必须真正执行此块（捕获 stdout 验证无异常），不止静态检查

---

## 验收清单

改写完成前**逐条自检**：

- [ ] TL;DR ≤ 7 行，但读完就能复述算法骨架
- [ ] 没有论文引用 / 年份 / 作者名
- [ ] intro 和 "关键要点" 没有重复内容（后者已删除）
- [ ] 每个 code block 前面有散文，散文不重复 inline 注释能讲的事
- [ ] inline 注释只剩 shape / 锚点 / 边界 case
- [ ] 变体对比是**表格 + 一句话**，不是散文
- [ ] 追问 cheat sheet 每条 ≤ 3 bullet，每 bullet ≤ 2 行
- [ ] 所有公式用 `$$...$$`
- [ ] 所有 shape-changing numpy 操作单独成行，配 `# (shape)` 注释
- [ ] `## End-to-end test` 章节存在且执行通过（autonomous session 实跑过）
- [ ] **总篇幅比原版短至少 30%**（如果不短，几乎肯定是没删够）

---

## 4 道题的具体锚点

### Linear Regression (closed-form lstsq + GD)

两种方法天然是对比表（不是两份独立代码）。

- **对比维度**：复杂度（$$O(d^3)$$ vs $$O(n \cdot d \cdot T)$$）、数值稳定性（QR / SVD vs learning rate 调参）、可扩展性（$$d$$ 大时 GD 优）
- **追问重灾区**：正则化的闭式解差异（Ridge 有 $$(X^TX + \lambda I)^{-1}$$，Lasso 没闭式）、共线性 → 用 SVD / 伪逆、normal equation 何时奇异
- **不要保留**：完整的最小二乘推导（保留 $$\hat\beta = (X^TX)^{-1}X^Ty$$ 一行结论即可）
- **e2e block**：`(N, D)` 输入，连续 `y` 形如 `(N,)`，assert 预测 shape 为 `(N,)`

### KNN (KNN + Weighted)

没有训练循环，全部重点在 inference 阶段的 distance + weighting。

- **结构特殊点**：`fit()` 几乎只是 store data，主代码在 `predict()` —— 把 predict 拆成 distance 计算 / top-K 选取 / 投票 三段
- **变体表**：uniform vs distance-weighted（$$w_i = 1/d_i$$ 或 $$1/d_i^2$$）
- **追问重灾区**：K 选择（奇数避免 tie）、curse of dimensionality（高维下距离趋同）、KD-tree / Ball tree 加速（建议提一下复杂度 $$O(\log n)$$ 查询）、分类 vs 回归 weighting 差异
- **e2e block**：`(N, D)` 训练 + 离散 `y` 形如 `(N,)`，对一小批 `(M, D)` query 调用 `predict`，assert 输出 shape 为 `(M,)`

### Logistic Regression (Sigmoid + Stable BCE + GD)

**这道题的灵魂是数值稳定性**——必须单独成一个 section（不要塞进 BCE 计算的注释里）。

- **TL;DR 强制提到**：stable BCE via `np.logaddexp` 或 `log1p(exp(-|z|))`
- **独立 section "Numerical stability"**：这是**少数值得保留数学推导**的地方，写出 $$\log(1 + e^z)$$ 在 $$z$$ 大时溢出的问题，以及 $$\max(z, 0) + \log(1 + e^{-|z|})$$ 这个等价形式
- **追问重灾区**：为什么 LR 没闭式解（sigmoid 非线性 → 似然非二次）、softmax 推广、class imbalance（class weight / focal loss）、L1/L2 正则的几何含义
- **e2e block**：`(N, D)` + 二元 `y ∈ {0, 1}` 形如 `(N,)`，`fit` 后 `predict_proba` assert 输出 ∈ `[0, 1]` 且 shape 为 `(N,)`

### Geometric Median (Weiszfeld + Vardi-Zhang 1999)

⚠️ 标题里就带了 "1999"——按删除原则**改成 "Vardi-Zhang variant"**，年份和论文引用全部去掉。

- **核心公式**：Weiszfeld iteration $$x_{t+1} = \frac{\sum w_i x_i}{\sum w_i}, \quad w_i = \frac{1}{\|x_i - x_t\|}$$
- **Vardi-Zhang 修复了什么**：iterate 落在某个 data point 上时 $$w_i \to \infty$$ 的退化（实现要点：检测命中并切换更新公式）
- **变体表**：原版 Weiszfeld vs Vardi-Zhang，列"退化处理 / 收敛性 / 实现复杂度"
- **追问重灾区**：与 mean / coordinate-wise median 的差异（$$L_2$$ 鲁棒中心 vs $$L_1$$ 逐维 median）、为什么 GM 没有闭式解（一阶条件含 $$x$$ 的 norm）、收敛性（目标函数凸 + Lipschitz → Weiszfeld 几乎处处收敛）
- **e2e block**：`(N, D)` 输入点云，`fit` 后 assert 估计 median 形如 `(D,)`，与 `np.mean` 对比展示鲁棒差异

---

## 元判断：什么时候偏离上述规则

规则是默认值，不是教条。**偏离的合法理由只有两个**：

1. **该算法的灵魂在某个非典型位置**（如 LR 的数值稳定性配独立 section）—— 这种情况要在 TL;DR 里显式提到
2. **某个追问点是该算法**专属高频问，且 1-2 行答不完 —— 提升到正文 section，不要硬塞 cheat sheet

除此之外的偏离基本都是没删够。**当你犹豫某段要不要留，默认删**。