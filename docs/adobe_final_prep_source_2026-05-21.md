# Adobe 面试复习笔记: 统计学 & RAG 工程

> **Source**: 用户 2026-05-21 提供的复习笔记 (Adobe Senior MLE final loop 当日提供)
> **用途**: 作为 MLI Adobe final round prep page 的内容源
> **执行参考**: 见 task `[Adobe] Final round prep page: Stats + RAG` (P1)
> **风格**: 中文叙述 + 英文术语 (首次出现展开 `**English** (acronym, 中文)`),per [[feedback_content_style_cn_en]]
> **数学**: 单 `$` 或 `$$` 均可,per [[feedback_math_formatting]];使用 `StudyNoteBuilder` 见现有 `seed_adobe_day1_chinese.py` 模板

---

## Part 1 · 统计学

### 1. 描述性统计

**Q1. 样本均值、方差、标准差公式?**

- 样本均值: $\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i$
- 样本方差 (无偏): $s^2 = \frac{1}{n-1}\sum_{i=1}^{n}(x_i - \bar{x})^2$
- 样本标准差: $s = \sqrt{s^2}$

**为什么 n−1(Bessel's correction)?** 用 $\bar{x}$ 估计 $\mu$ 时占用了一个自由度,分母用 $n$ 会低估总体方差。除以 $n-1$ 让估计量无偏。

**Q2. 标准误 (SE) 和标准差 (SD) 的区别?**

- SD 描述**单个观测值**的离散程度
- SE 描述**统计量本身**的不确定性
- 均值的标准误: $SE_{\bar{x}} = \frac{s}{\sqrt{n}}$(样本量 $n$ 越大,$\bar{x}$ 越精确)

**Q3. 95% 置信区间什么意思?最常见的误解?**

- 公式(均值,大样本): $\bar{x} \pm z_{\alpha/2} \cdot \frac{s}{\sqrt{n}}$,其中 $z_{0.025} = 1.96$
- 小样本 (n < 30 且 σ 未知) 用 t: $\bar{x} \pm t_{\alpha/2,\, n-1} \cdot \frac{s}{\sqrt{n}}$
- 比例的 Wald CI: $\hat{p} \pm z_{\alpha/2}\sqrt{\frac{\hat{p}(1-\hat{p})}{n}}$
- 极端比例 (p 接近 0 或 1) 用 **Wilson 区间** 更稳

**误解**: "真实参数有 95% 概率落在这个区间里" [FAIL]

**正确**: 在重复实验意义下,构造的 CI 中有 95% 会包含真实参数。**真实参数是固定的,区间才是随机的**。

---

### 2. 概率分布

**Q4. 二项分布 (Binomial) 关键公式?**

$$P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}$$

- $E[X] = np$
- $Var[X] = np(1-p)$
- 当 $np \geq 5$ 且 $n(1-p) \geq 5$,可用正态近似 $N(np,\, np(1-p))$

**Q5. 正态分布 PDF 和重要性质?**

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

- 68/95/99.7 法则(1σ / 2σ / 3σ)
- 线性组合仍正态: $aX + bY \sim N(a\mu_X + b\mu_Y,\, a^2\sigma_X^2 + b^2\sigma_Y^2)$(X, Y 独立)

**Q6. 中心极限定理 (CLT) 是什么?**

任意分布(方差有限)的样本均值,当 $n$ 足够大时,分布近似为:

$$\bar{X} \sim N\left(\mu,\, \frac{\sigma^2}{n}\right)$$

经验阈值 $n \geq 30$。极偏分布需要更大 n。这是 A/B test 用 z-test 的理论基础。

**Q7. 常见分布速查?**

| 分布 | 场景 | 期望 |
|---|---|---|
| Bernoulli | 单次二元事件 | $p$ |
| Binomial | n 次独立 Bernoulli | $np$ |
| Poisson $\lambda$ | 稀有事件计数 | $\lambda$ |
| Exponential $\lambda$ | 事件间隔时间 | $1/\lambda$ |
| Beta $(\alpha,\beta)$ | 比例的先验 (Bayesian) | $\alpha/(\alpha+\beta)$ |
| Geometric | 直到首次成功的尝试数 | $1/p$ |

---

### 3. 假设检验

**Q8. p-value 严格定义?**

$$p = P(\text{观察到当前或更极端的数据} \mid H_0\text{ 为真})$$

**绝不等于** $P(H_0 \mid \text{data})$。

**Q9. p-value 五大常见误解?**

1. **p < 0.05 ≠ 效果重要** — 统计显著与实际显著不同。n 极大时几乎任何差异都显著
2. **p ≥ 0.05 ≠ H₀ 为真** — "absence of evidence is not evidence of absence"
3. **p-value 不告诉你效果大小** — 必须配合 effect size 和 CI
4. **多次测试不调整** → α 膨胀
5. **p-hacking**: 反复看数据、改变停止规则会让 p 失效

**Q10. Type I / Type II / Power 的定义?**

|  | $H_0$ 真 | $H_1$ 真 |
|---|---|---|
| 拒绝 $H_0$ | Type I (α) [FAIL] | 正确  (Power) |
| 不拒绝 $H_0$ | 正确  | Type II (β) [FAIL] |

- α = Type I 错误率 (常取 0.05)
- β = Type II 错误率
- **Power = 1 − β** = 在 $H_1$ 真时成功检出的概率 (常要求 0.8)

**影响 Power 的因素**: 样本量 ↑、effect size ↑、方差 ↓、α ↑ → Power ↑

**Q11. A/B test 样本量公式(两比例)?**

每组样本量(标准近似):

$$n = \frac{(z_{\alpha/2} + z_\beta)^2 \cdot [p_1(1-p_1) + p_2(1-p_2)]}{(p_1 - p_2)^2}$$

**数值例子**: baseline CTR = 5%, MDE (绝对) = 0.5%, α=0.05 (双尾), power=0.8

- $z_{0.025} = 1.96$, $z_{0.20} = 0.84$
- 分子: $(1.96+0.84)^2 \cdot (0.05 \cdot 0.95 + 0.055 \cdot 0.945) = 7.84 \cdot 0.0995 \approx 0.780$
- 分母: $(0.005)^2 = 2.5 \times 10^{-5}$
- $n \approx 31{,}200$ 每组

**两均值版本**: $n = \dfrac{2(z_{\alpha/2}+z_\beta)^2 \sigma^2}{\delta^2}$ 每组

**Q12. 单尾 vs 双尾?**

- 双尾: 你只关心"有没有差异" → 默认选这个
- 单尾: 你**事先**有方向假设(且对反方向不感兴趣) → 临界值变小,更易显著
- [WARN] 业务上**几乎都用双尾**,因为反方向的结果你不可能忽略

**Q13. t-test vs z-test 怎么选?**

- z-test: σ 已知,或 n 大(一般 ≥ 30)
- t-test: σ 未知,小样本
- 实务中 A/B test 几乎都是大样本,两者几乎等价

**Q14. 多重比较问题?**

做 $m$ 个独立检验,假设全部 $H_0$ 真,至少一个 false positive 的概率:

$$P(\text{至少 1 FP}) = 1 - (1-\alpha)^m \xrightarrow{m=20,\alpha=0.05} 0.64$$

**修正方法**:

| 方法 | 思路 | 特点 |
|---|---|---|
| Bonferroni | $\alpha_{adj} = \alpha/m$ | 保守,控制 FWER |
| Holm-Bonferroni | 排序后逐步 | 比 Bonferroni 强 |
| Benjamini-Hochberg (BH) | 控制 FDR(错误发现比例期望) | 大规模检验首选 |

**FWER vs FDR**: FWER 控制"任何一个误拒"的概率;FDR 控制"误拒占所有拒绝中的比例"。基因组学、广告 metric 海量比较时用 FDR。

---

### 4. 方差缩减 (Variance Reduction)

**Q15. CUPED 原理?**

**目的**: 用实验前数据(pre-period covariate)抵消用户基线差异,减小指标方差,从而用更小样本量获得同等 power。

**公式**:

$$Y^{\text{cuped}} = Y - \theta(X - E[X])$$

最优 $\theta = \dfrac{\text{Cov}(Y, X)}{\text{Var}(X)}$(其实就是 $Y$ 对 $X$ 的回归斜率)

**方差缩减比例**:

$$\text{Var}(Y^{\text{cuped}}) = \text{Var}(Y)(1 - \rho^2)$$

其中 $\rho$ 是 $Y$ 和 $X$ 的相关系数。如果用户实验前后行为相关性 $\rho=0.7$,方差降 51%,等价于 ~2 倍样本量。

**关键约束**: $X$ 必须**与处理变量独立**(用 pre-period 数据保证)。否则会引入偏差。

**Q16. 其他方差缩减手段?**

- **分层抽样 (Stratification)**: 按用户类型分层后取均值
- **回归调整 (Regression adjustment)**: ANCOVA, CUPED 的更一般形式
- **配对实验 (Paired design)**: 同一用户 before/after

---

### 5. 回归分析

**Q17. OLS 公式和假设?**

模型: $y = X\beta + \epsilon$, $\epsilon \sim N(0, \sigma^2 I)$

闭式解: $\hat{\beta} = (X^TX)^{-1}X^Ty$

**Gauss-Markov 假设 (LINE)**:

- **L**inearity: $y$ 与 $X$ 的关系是线性的
- **I**ndependence: $\epsilon_i$ 独立
- **N**ormality of residuals (只为做推断,不为估计)
- **E**qual variance (homoscedasticity)
- 加: 无完美多重共线性 ($X^TX$ 可逆)

**Q18. 怎么解释回归系数?**

$\beta_j$: **其他变量不变**时, $x_j$ 每增加 1 单位, $y$ 平均增加 $\beta_j$ 单位。

[WARN] 是**条件**关系而非边际关系,**不是因果**。

**标准化系数** (z-score 化输入): 可跨变量比较"哪个特征影响更大"。

**Q19. R² 公式和陷阱?**

$$R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$$

$$\bar{R}^2 = 1 - \frac{(1-R^2)(n-1)}{n - p - 1}$$

**陷阱**:
- $R^2$ 高 ≠ 模型好(可能过拟合)
- $R^2$ 低 ≠ 模型差(噪声数据本就上限低)
- 加任何特征 $R^2$ 都不会下降 → 必须看 adjusted $R^2$ 或 hold-out

**Q20. Logistic regression?**

$$P(y=1|x) = \sigma(x^T\beta) = \frac{1}{1 + e^{-x^T\beta}}$$

Log-odds 形式(最容易解释):

$$\log\frac{p}{1-p} = x^T\beta$$

**系数解释**: $x_j$ 增加 1 → log-odds 增加 $\beta_j$ → **odds 乘以 $e^{\beta_j}$**

损失(cross-entropy / log-loss):

$$L = -\frac{1}{n}\sum[y_i \log \hat{p}_i + (1-y_i)\log(1-\hat{p}_i)]$$

无闭式解,用 IRLS 或梯度下降求 MLE。

**Q21. 多重共线性 (Multicollinearity)?**

- 检测: VIF $= 1/(1 - R_j^2)$,VIF > 10 通常视为严重
- 后果: 系数不稳、SE 膨胀(但预测仍可能 OK)
- 处理: 删除冗余特征、PCA、Ridge 回归

---

### 6. CI vs PI(置信区间 vs 预测区间)

**Q22. 区别?**

| | 描述对象 | 公式 (回归预测点 $x_0$) |
|---|---|---|
| CI | **均值**的不确定性 | $\hat{y}_0 \pm t \cdot \sigma\sqrt{\frac{1}{n} + \frac{(x_0-\bar{x})^2}{S_{xx}}}$ |
| PI | **单个新观测**的不确定性 | $\hat{y}_0 \pm t \cdot \sigma\sqrt{1 + \frac{1}{n} + \frac{(x_0-\bar{x})^2}{S_{xx}}}$ |

PI 比 CI 多了"$+1$"项(个体随机误差),所以**总是更宽**。

---

### 7. Bias-Variance Tradeoff

**Q23. 分解公式?**

$$E[(\hat{f}(x) - y)^2] = \underbrace{(E[\hat{f}(x)] - f(x))^2}_{\text{bias}^2} + \underbrace{\text{Var}(\hat{f}(x))}_{\text{variance}} + \underbrace{\sigma^2}_{\text{irreducible}}$$

- High bias = underfit(模型太简单)
- High variance = overfit(模型太复杂、数据不够)
- L1/L2 正则化、bagging 降 variance;boosting 降 bias

---

### 8. 不平衡分类: AUC vs PR-AUC

**Q24. 为什么不平衡数据要看 PR-AUC?**

- **ROC-AUC**: TPR vs FPR;与类别比例**无关**
- **PR-AUC**: Precision vs Recall;**对正类比例敏感**

**反直觉例子**: 1% 正例,模型 TPR=0.9, FPR=0.05 → 看似不错。但:

- TP = 0.9 × 100 = 90
- FP = 0.05 × 9900 = 495
- Precision = 90 / (90+495) = **15%**

ROC 看起来漂亮(AUC 可能 0.95+),实际预测 100 个正例只对 15 个。**当你关心正类预测的可信度时,用 PR-AUC**。

**经验规则**: 极不平衡(如 < 5% 正例)、欺诈检测、点击预测 → PR-AUC 主导。

---

### 9. 缺失值处理

**Q25. 缺失机制三类?**

- **MCAR** (Missing Completely at Random): 缺失与任何变量无关 → 删除安全
- **MAR** (Missing at Random): 缺失依赖**观测到的**其他变量 → 可建模填补
- **MNAR** (Missing Not at Random): 缺失依赖**未观测的值本身** → 最棘手(如高收入者不报收入)

**Q26. 常用方法及陷阱?**

| 方法 | 优点 | 陷阱 |
|---|---|---|
| 删除(listwise) | 简单 | 损失数据,仅 MCAR 无偏 |
| 均值/中位数填补 | 简单 | 低估方差、削弱相关性 |
| 回归填补 | 利用相关 | 低估方差(确定性预测) |
| Multiple Imputation (MICE) | 反映不确定性 | 实现复杂 |
| 加 missing indicator | 保留"缺失"信息 | 共线性风险 |
| Tree-based 原生处理 | XGBoost/LightGBM 直接支持 | 无 |

**Q27. EM 算法在缺失值上怎么用?**

E-step: 用当前参数估计填补缺失值(条件期望);M-step: 用填补后的完整数据更新参数。迭代直到收敛。

---

### 10. 没实验也能做因果推断

**Q28. 主要方法对比?**

| 方法 | 核心假设 | 适用 |
|---|---|---|
| **DiD** (Difference-in-Differences) | 平行趋势 (parallel trends) | 政策/特性 rollout 前后对比 |
| **RDD** (Regression Discontinuity) | 阈值附近其他变量连续 | 有 cutoff 的场景 (e.g. 资格分数线) |
| **IV** (Instrumental Variable) | $Z$ 影响 $T$ 但不直接影响 $Y$ | 有外生变量时 |
| **PSM** (Propensity Score Matching) | 可观测变量上无未观测混淆 | 观察数据对比 |
| **Synthetic Control** | 加权 control 单元 → 反事实 | 单一处理单元 (e.g. 一个城市) |
| **Doubly Robust** | 结合 outcome 模型 + propensity | 任一模型正确就一致 |

**Q29. 混淆变量 (Confounder) 是什么?**

同时影响处理 $T$ 和结果 $Y$ 的变量。不控制就会让相关性 ≠ 因果。

> 例: "冰淇淋销量"和"溺水"高度相关 → 共同混淆是"夏季"。

**Q30. Simpson 悖论 (Simpson's Paradox)?**

聚合数据上的相关方向,可能在分组数据上**整体反转**。

> UC Berkeley 男女录取经典案例:聚合看男生录取率高,按系分组看女生录取率高(女生更多申请竞争激烈的系)。

---

### 11. 概率应用题(高频)

**Q31. Bayes 定理 (贝叶斯)**

$$P(A|B) = \frac{P(B|A)P(A)}{P(B)}$$

**经典疾病检测题**: 患病率 1%,检测敏感度 99% (TPR),特异度 95% ($1-\text{FPR}$)。检测阳性,实际患病的概率?

$$P(D|+) = \frac{P(+|D)P(D)}{P(+|D)P(D) + P(+|\neg D)P(\neg D)}$$

$$= \frac{0.99 \times 0.01}{0.99 \times 0.01 + 0.05 \times 0.99} = \frac{0.0099}{0.0594} \approx 16.7\%$$

**直觉**: 真实患者 99 个 vs 误检的 495 个,后者远多于前者 → **base rate fallacy**。

**Q32. 蓄水池抽样 (Reservoir Sampling)?**

从流式数据中均匀采样 $k$ 个,不知道总长。第 $i$ 个元素($i > k$)以 $k/i$ 概率替换池中随机一个。每个元素最终被选中的概率为 $k/n$。

**Q33. 生日问题**

23 人中至少两人同生日的概率 > 50%。

$$P(\text{至少两人同}) = 1 - \frac{365!/(365-n)!}{365^n}$$

直觉: 配对数 $\binom{23}{2} = 253$,比看起来多得多。

---

## Part 2 · RAG 全栈

### 1. Chunking 策略

**Q34. 主流切块方式?**

| 策略 | 描述 | 适用 |
|---|---|---|
| Fixed-size | 固定 token 数(512)+ overlap(10–20%) | 通用 baseline |
| Sentence-aware | 不在句中切 | 短问答 |
| Recursive | 按段落 → 句 → 词层级回退 | LangChain 默认 |
| Semantic chunking | 用 embedding 相似度找断点 | 主题切换明显的文档 |
| Document structure | 按 heading(markdown/HTML) | 技术文档、wiki |
| Hierarchical (parent-child) | 检索小块、返回大块上下文 | 长文档 QA |
| Code-aware | 用 AST 按函数/类切 | 代码库 |
| Table-aware | 整张表/按行切 + 表头保留 | 财报、技术规格 |

**Q35. Chunk size 怎么选?**

- 太小:单块语义不完整,retrieve 时召回散乱
- 太大:embedding 被噪声稀释,精度下降;上下文窗口浪费
- 经验起点:**256–512 token,50–100 overlap**
- **必须**通过 retrieval recall/MRR 在 golden set 上调优,不能拍脑袋

**Q36. 怎么衡量 chunking 效果?**

构建 (query, gold chunk_id) 数据集,对比不同 chunking 策略下 Recall@k、MRR、NDCG。同时**端到端**看 answer correctness,因为 retrieval 好不代表生成好。

---

### 2. Embedding 模型选型

**Q37. 选 embedding 看什么?**

- **任务类型**: asymmetric (query 短/doc 长) vs symmetric — 选对应训练的模型(如 BGE 有专门 query prefix)
- **领域**: 通用 / 代码 (CodeBERT, text-embedding) / 多语言 (BGE-M3, multilingual-e5) / 医疗 (BioBERT)
- **维度 vs 性能**: 768 / 1024 / 3072;Matryoshka 嵌入可截断
- **context length**: 短文 512 vs 长文 8k(jina, voyage-large)
- **MTEB 榜单**: 但**不要直接信榜单分数**,必须在自己数据上验证
- **成本**: 自部署开源 (bge, e5, gte) vs API (OpenAI, Cohere, Voyage)

**Q38. 怎么验证 embedding 在你的数据上好不好?**

1. 人工标注 200–500 条 (query, relevant_doc) 对
2. 用 LLM 合成数据补充(对每篇文档生成假设性问题)
3. 算 Recall@10, MRR, NDCG@10
4. 对比 2–3 个候选 embedding 在同一索引上的表现
5. [WARN] 不要只看 cosine 平均值,要看排序质量

**Q39. 常用模型一览(2024–2025)**

| 模型 | 维度 | 特点 |
|---|---|---|
| OpenAI text-embedding-3-large | 3072 (可裁) | 通用强,闭源 |
| Voyage-3 | 1024 | 检索质量顶尖 |
| Cohere embed-v3 | 1024 | 多语言,便宜 |
| BGE-M3 | 1024 | 开源、多语、long doc |
| E5-mistral-7b-instruct | 4096 | 大但贵 |
| Nomic embed | 768 | 开源轻量 |

---

### 3. 向量数据库 (Vector DB)

**Q40. 主流向量库对比?**

| 库 | 优点 | 缺点 |
|---|---|---|
| **pgvector** | 同库 SQL filter, ACID, 运维简单 | 大规模慢 (>10M) |
| **Pinecone** | Fully managed, 快 | 贵, vendor lock-in |
| **Weaviate** | Hybrid search 原生, 模块化 | 资源占用大 |
| **Qdrant** | Rust, 强大 filtering | 生态较新 |
| **Milvus** | 超大规模 (10B+) | 复杂运维 |
| **FAISS** | 库不是服务, 极快 | 无持久化/分布式 |

**选型决策树**:
- < 1M 向量 + 已有 Postgres → **pgvector**
- 不想运维 → **Pinecone**
- 需要复杂 metadata filtering → **Qdrant / Weaviate**
- 需要 hybrid (BM25 + dense) → **Weaviate / Elasticsearch + vectors**
- 单机 prototype → **FAISS / Chroma**

**Q41. 索引类型?**

| 索引 | 原理 | 内存 | 速度 |
|---|---|---|---|
| Flat (brute force) | 全量计算 | 高 | 慢但 100% recall |
| HNSW | 多层图, 贪心搜索 | 高 | 最常用, 快 |
| IVF | 先聚类再搜对应簇 | 中 | 快, 略损 recall |
| IVF + PQ (Product Quantization) | 聚类+量化压缩 | 低 | 大规模首选 |

**关键参数 (HNSW)**: `M` (连接数, 越大召回越好但内存大), `ef_construction` (建索引质量), `ef_search` (查询时召回 vs 速度 trade-off)。

---

### 4. Re-ranker(重排)

**Q42. 为什么要重排?**

- Bi-encoder(embedding 模型)独立编码 query 和 doc,速度快但语义匹配粗
- Cross-encoder 把 query 和 doc **拼起来一起进 Transformer**,语义对齐更细,但 N 倍慢
- **两阶段**: bi-encoder 召回 top-100,cross-encoder 重排 top-10

**Q43. 常用 re-ranker?**

- **Cohere Rerank v3**: API, 强大稳定
- **bge-reranker-large / v2-m3**: 开源
- **jina-reranker-v2**: 多语言
- **LLM-as-reranker**: 用 GPT-4o/Claude 给候选打分(成本高,质量上限高)

**Q44. ColBERT 和 cross-encoder 区别?**

ColBERT 是 **late-interaction**: 每个 token 单独 embed, 查询时用 MaxSim 算交互。介于 bi-encoder(快但粗)和 cross-encoder(精但慢)之间。

---

### 5. Query Rewriting / Transformation

**Q45. 常用技术?**

- **HyDE** (Hypothetical Document Embeddings): 让 LLM 写一个**假设性答案**,对这个假答案做 embedding 检索。对长尾、抽象 query 提升明显
- **Multi-query**: 让 LLM 生成 3–5 个改写, 取检索结果并集 → 提升 recall
- **Query decomposition**: 复杂问题拆成子问题分别检索(如多跳问答)
- **Step-back prompting**: 先抽象出上位概念再检索("这个 API 怎么用" → "API 文档结构")
- **历史改写**: 多轮对话中把指代消解掉 ("它有什么参数" → "X 函数有什么参数")

---

### 6. Guardrails(护栏)

**Q46. RAG 系统四层护栏?**

1. **输入层**:
   - Prompt injection 检测 (Llama Guard, Lakera, NeMo Guardrails)
   - PII 检测/脱敏 (Presidio)
   - 主题分类(拒绝 off-topic)

2. **检索层**:
   - Metadata 过滤(user role / ACL)
   - 检索结果数量上限
   - 拒绝低置信检索(top score 阈值)

3. **生成层**:
   - System prompt 强约束("only answer based on provided context")
   - Citation enforcement(强制引用 chunk_id)
   - Faithfulness check(生成内容是否真的来自 retrieved doc)

4. **输出层**:
   - Toxicity / 不当内容(Perspective API)
   - PII 泄漏检查
   - Hallucination 检测(NLI 模型验证 claim ⊂ context)

**Q47. Prompt injection 怎么防?**

- 用 system prompt 和 user input **严格分离**
- 检测明显 injection 模式("ignore previous instructions")
- 用 LLM-as-judge 检测意图
- 文档内容也可能含 injection(**indirect prompt injection**)→ 必须 sanitize 检索结果

---

### 7. RAG Evaluation

**Q48. Retrieval 怎么评?**

构建 golden set: `(query, relevant_chunk_ids)`

- **Recall@k**: 召回到的相关 chunk 占全部相关 chunk 的比例
- **Precision@k**: top-k 中相关 chunk 的比例
- **MRR (Mean Reciprocal Rank)**: $\frac{1}{|Q|}\sum \frac{1}{\text{rank of first relevant}}$
- **NDCG@k**: 有分级相关性时用(很相关 = 3, 相关 = 1, 不相关 = 0)

**Q49. End-to-end 怎么评?(RAGAS 框架)**

- **Faithfulness**: 生成的每个 claim 是否能在 retrieved context 中找到支持
- **Answer Relevance**: 答案是否回答了 query
- **Context Precision**: top-k 中真正用上的比例
- **Context Recall**: 回答 ground truth 所需的信息有多少在 context 里
- **Answer Correctness**: 与参考答案对比(语义+事实)

**Q50. 怎么构建 golden dataset?**

- **冷启动**: 用 GPT-4o/Claude 对每篇 doc 生成 3–5 个问题 + 答案 → 人工筛选
- **生产数据**: 收集线上 query, 让标注员标 relevant chunks
- **持续迭代**: 把 bad case (用户点踩、低 confidence) 加入 eval set

---

## 面试小贴士

**统计题被问到时常见陷阱**:
- 公式说出来 + **直觉解释** + 一个**反例或边界 case**,三件套别忘
- 不要装懂 — 不会就说"我不确定,但我会这样推导..."
- A/B test 题永远先问 metric, baseline, MDE, α/β 五要素

**RAG 题被问到时**:
- 永远先问业务场景(短问答 vs 长文档总结 vs 代码搜索完全不同方案)
- 给具体的**调参经验**(chunk size 我从 256 试到 1024)会比说"看情况"显得专业得多
- 谈到 evaluation 是大加分项 — 多数候选人只会说 "用 LLM 评"
