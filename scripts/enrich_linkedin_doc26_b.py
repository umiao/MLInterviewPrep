"""Enrich LinkedIn doc#26 (Question Index) -- ML Theory Q16-Q23.

Task: T-P0-262 (Part 2/4)
Adds comprehensive solutions for all 8 ML theory & coding questions.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"


def get_content(conn: sqlite3.Connection) -> str:
    """Read doc#26 content."""
    cur = conn.cursor()
    cur.execute("SELECT content FROM company_documents WHERE id=26")
    row = cur.fetchone()
    if not row:
        print("ERROR: doc#26 not found")
        sys.exit(1)
    return row[0]


def enrich(content: str) -> str:
    """Apply enrichments to ML Theory questions Q16-Q23."""

    # ── Q16: Transformer Architecture ──
    content = content.replace(
        """**题目**: Explain the Transformer architecture in detail. Describe the encoder and decoder components, self-attention mechanism, multi-head attention, and positional encoding...

---

### Q17.""",
        """**题目**: Explain the Transformer architecture in detail. Describe the encoder and decoder components, self-attention mechanism, multi-head attention, and positional encoding...

**解答**:

**Transformer 架构核心组件**:

**1. Self-Attention (自注意力机制)**:
- 输入序列中每个 token 计算与其他所有 token 的相关性权重
- 公式: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
- Q (Query), K (Key), V (Value) 分别由输入乘以学习到的权重矩阵得到
- sqrt(d_k) 缩放因子防止点积过大导致 softmax 梯度消失

**2. Multi-Head Attention (多头注意力)**:
- 将 Q, K, V 拆分为 h 个头，每个头独立计算 attention，最后 concat + linear projection
- 好处：不同 head 可以关注不同的语义关系 (syntactic vs semantic)
- MultiHead(Q,K,V) = Concat(head_1, ..., head_h) * W_O

**3. Positional Encoding (位置编码)**:
- Transformer 无内置序列顺序感知 (与 RNN (Recurrent Neural Network，循环神经网络) 不同)
- 使用 sin/cos 函数生成位置编码: PE(pos, 2i) = sin(pos / 10000^(2i/d))
- 可学习位置编码 vs 固定 sinusoidal -- 实践中效果相近

**4. Encoder**: N 层堆叠，每层 = Multi-Head Self-Attention + FFN (Feed-Forward Network，前馈网络) + LayerNorm + Residual Connection
**5. Decoder**: 额外加入 Masked Self-Attention (防止看到未来 token) + Cross-Attention (关注 encoder 输出)

```python
import torch
import torch.nn as nn
import math

class ScaledDotProductAttention(nn.Module):
    def forward(self, Q, K, V, mask=None):
        d_k = Q.size(-1)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attn = torch.softmax(scores, dim=-1)
        return torch.matmul(attn, V), attn
```

- **Time Complexity**: O(n^2 * d) per layer，n = sequence length, d = dimension
- **Key Trade-off**: Self-attention 是 O(n^2)，限制了长序列处理。改进：Flash Attention, Sparse Attention, Linear Attention

---

### Q17."""
    )

    # ── Q17: A/B Testing Email Campaign ──
    content = content.replace(
        """**题目**: You are testing whether changing an email's headline and content affects engagement (open rate, click-through rate). How would you design and analyze this experiment? Discuss multivariate testing, hypothesis formulation, significance testing, and potential pitfalls.

---

### Q18.""",
        """**题目**: You are testing whether changing an email's headline and content affects engagement (open rate, click-through rate). How would you design and analyze this experiment? Discuss multivariate testing, hypothesis formulation, significance testing, and potential pitfalls.

**解答**:

**实验设计**:
- **Factorial Design (析因设计)**: 2 个因子 (headline, content) 各 2 水平 = 2x2 = 4 组
  - Group A: 原 headline + 原 content (control)
  - Group B: 新 headline + 原 content
  - Group C: 原 headline + 新 content
  - Group D: 新 headline + 新 content
- **随机分配**: 用户随机分到 4 组，确保组间基线特征均衡

**Hypothesis (假设)**:
- H0: 新 headline/content 对 open rate 和 CTR (Click-Through Rate，点击率) 无显著影响
- H1: 至少一个因子有显著影响
- 需要检验 main effects (主效应) 和 interaction effect (交互效应)

**Sample Size (样本量)**:
- 使用 power analysis: 设定 alpha=0.05, power=0.80, MDE (Minimum Detectable Effect，最小可检测效果)
- 对于比例数据: n = (Z_alpha/2 + Z_beta)^2 * (p1(1-p1) + p2(1-p2)) / (p1-p2)^2

**Analysis (分析)**:
- Open rate: proportion z-test 或 chi-squared test
- CTR: 同上，但注意 CTR = clicks/opens (条件概率)
- 交互效应: 用 two-way ANOVA (Analysis of Variance，方差分析) 或 logistic regression

**Pitfalls (常见陷阱)**:
1. **Multiple comparisons**: 4 组 = 6 pairs，需要 Bonferroni correction (alpha/6)
2. **Novelty effect**: 新邮件短期内可能因新鲜感而表现好
3. **Email delivery bias**: 不同 headline 可能触发不同的 spam filter 行为
4. **Day-of-week effect**: 确保各组在同一时间段发送
5. **Metric coupling**: open rate 和 CTR 不独立 -- CTR 取决于 opens

---

### Q18."""
    )

    # ── Q18: Video Posting US vs Non-US ──
    content = content.replace(
        """**题目**: LinkedIn hypothesizes that video posting features might not be catching on internationally as well as in the US. Given two tables - video_posts(post_date, memberid, video_length) and members(memberid, country, join_date) - test whether US members upload more videos than non-US members...

---

### Q19.""",
        """**题目**: LinkedIn hypothesizes that video posting features might not be catching on internationally as well as in the US. Given two tables - video_posts(post_date, memberid, video_length) and members(memberid, country, join_date) - test whether US members upload more videos than non-US members...

**解答**:

**Step 1: SQL -- 提取数据**:
```sql
-- 每个用户的视频上传数量，按 US/non-US 分组
SELECT
    m.memberid,
    CASE WHEN m.country = 'US' THEN 'US' ELSE 'Non-US' END AS segment,
    COUNT(v.memberid) AS video_count
FROM members m
LEFT JOIN video_posts v ON m.memberid = v.memberid
GROUP BY m.memberid, segment;
```

**Step 2: Python -- 假设检验**:
```python
from scipy import stats
import numpy as np

# us_counts, non_us_counts: 每个用户的视频上传数量
def test_video_adoption(us_counts: np.ndarray, non_us_counts: np.ndarray):
    # (1) Welch's t-test (不假设方差相等)
    t_stat, p_val = stats.ttest_ind(us_counts, non_us_counts, equal_var=False)
    print(f"Welch t-test: t={t_stat:.3f}, p={p_val:.4f}")

    # (2) Mann-Whitney U test (非参数，适合偏态分布)
    u_stat, p_val_mw = stats.mannwhitneyu(us_counts, non_us_counts, alternative='greater')
    print(f"Mann-Whitney U: U={u_stat:.0f}, p={p_val_mw:.4f}")

    # (3) Effect size (Cohen's d)
    pooled_std = np.sqrt((us_counts.std()**2 + non_us_counts.std()**2) / 2)
    cohens_d = (us_counts.mean() - non_us_counts.mean()) / pooled_std
    print(f"Cohen's d = {cohens_d:.3f}")
```

**Key Considerations**:
- **One-sided test**: H1 是 "US > Non-US"，使用 alternative='greater'
- **Effect size**: 即使统计显著，Cohen's d 很小说明实际差异不大
- **Confounders**: 加入时间 (join_date)、活跃度等可能混淆因素应控制
- **视频上传为 0 的用户**: LEFT JOIN 确保包含从未上传的用户

---

### Q19."""
    )

    # ── Q19: CPC vs CPM ──
    content = content.replace(
        """**题目**: Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions) metrics. When would you use each? How do you decide which pricing model is better for an advertising campaign on LinkedIn?

---

### Q20.""",
        """**题目**: Explain CPC (Cost Per Click) and CPM (Cost Per Mille / Cost Per 1000 Impressions) metrics. When would you use each? How do you decide which pricing model is better for an advertising campaign on LinkedIn?

**解答**:

**CPC (Cost Per Click，每次点击费用)**:
- 广告主仅在用户点击广告时付费
- CPC = Total Spend / Total Clicks
- **适用场景**: 目标是 conversion (转化) -- 求职申请、注册、下载
- **优势**: 直接衡量用户意图，ROI (Return on Investment，投资回报率) 易计算
- **劣势**: 高竞争行业 CPC 很高；可能遇到 click fraud (点击欺诈)

**CPM (Cost Per Mille，每千次展示费用)**:
- 广告主为每 1000 次广告展示付费，不管是否点击
- CPM = (Total Spend / Total Impressions) * 1000
- **适用场景**: 目标是 brand awareness (品牌知名度) -- 新产品发布、招聘品牌
- **优势**: 确保曝光量，适合 top-of-funnel (漏斗顶部) 营销
- **劣势**: 展示不等于关注，实际效果难衡量

**决策框架**:
| 因素 | 选 CPC | 选 CPM |
|------|--------|--------|
| Campaign Goal | 转化驱动 (求职申请, 注册) | 品牌曝光 |
| Budget | 有限预算，追求效率 | 充足预算，追求覆盖 |
| CTR Expectation | 低 CTR (展示多但点击少) | 高 CTR (CPM 更划算) |
| Measurement | 易衡量 conversion | 需要额外 brand lift study |

**LinkedIn 特有考虑**: LinkedIn 广告的平均 CPC 较高 ($5-8 vs Google $1-2)，因为用户质量高 (professionals)。对于 B2B lead generation (商业线索生成)，CPC 通常更合适。

---

### Q20."""
    )

    # ── Q20: Sparse Vector/Matrix (LC 1573, 311) ──
    content = content.replace(
        """**解法要点**:
- Space: O(k) where k = number of non-zero elements
- \"\"\"Compute dot product. O(min(k1, k2)) time.\"\"\"
- Space: O(nnz) where nnz = number of non-zero elements
- \"\"\"Multiply two sparse matrices. O(nnz_A * nnz_B / cols_A) average.\"\"\"

---

### Q21.""",
        """**解答**:

**思路**: 稀疏数据只存储非零元素。Sparse Vector (稀疏向量) 用 dict {index: value}；Sparse Matrix (稀疏矩阵) 用 dict of dicts 或 CSR (Compressed Sparse Row，压缩行存储) 格式。

```python
class SparseVector:
    \"\"\"LC 1573: Dot Product of Two Sparse Vectors.\"\"\"
    def __init__(self, nums: list[int]):
        self.nonzero = {i: v for i, v in enumerate(nums) if v != 0}

    def dotProduct(self, vec: 'SparseVector') -> int:
        # 遍历较短的一方，O(min(k1, k2))
        if len(self.nonzero) > len(vec.nonzero):
            return vec.dotProduct(self)
        return sum(
            v * vec.nonzero[i]
            for i, v in self.nonzero.items()
            if i in vec.nonzero
        )

class SparseMatrix:
    \"\"\"LC 311: Sparse Matrix Multiplication.\"\"\"
    def __init__(self, mat: list[list[int]]):
        self.rows = len(mat)
        self.cols = len(mat[0]) if mat else 0
        # row -> {col: val} for non-zero entries
        self.data = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if mat[r][c] != 0:
                    self.data.setdefault(r, {})[c] = mat[r][c]

    def multiply(self, other: 'SparseMatrix') -> list[list[int]]:
        result = [[0] * other.cols for _ in range(self.rows)]
        for r, cols_a in self.data.items():
            for k, val_a in cols_a.items():
                if k in other.data:
                    for c, val_b in other.data[k].items():
                        result[r][c] += val_a * val_b
        return result
```

- **Sparse Vector Dot Product**: O(min(k1, k2))，k = 非零元素数
- **Sparse Matrix Multiply**: O(nnz_A * avg_nnz_per_row_B)，远快于 O(n^3) dense multiplication
- **Key Insight**: 只遍历非零元素，跳过大量零值计算

---

### Q21."""
    )

    # ── Q21: Weighted Random Sampling ──
    content = content.replace(
        """**解法要点**:
- Build: O(n), Sample: O(log n), Space: O(n)
- O(1) sampling after O(n) preprocessing.
- \"\"\"Alias method for O(1) weighted sampling.
- Build: O(n), Sample: O(1), Space: O(n)

---

### Q22.""",
        """**解答**:

**思路**: 三种方法，复杂度递减：

**方法 1: Prefix Sum + Binary Search (前缀和 + 二分搜索)**:
- 构建累积概率数组，每次采样生成 random [0,1)，二分查找落入区间
- Build O(n), Sample O(log n)

**方法 2: Alias Method (别名方法)**:
- 将 n 个不等概率的桶重新分配为 n 个等概率的桶，每个桶最多装 2 种结果
- Build O(n), Sample O(1) -- 最优

```python
import random
import bisect

# Method 1: Prefix Sum + Binary Search
class WeightedSamplerBisect:
    def __init__(self, weights: list[float]):
        total = sum(weights)
        self.cumulative = []
        running = 0.0
        for w in weights:
            running += w / total
            self.cumulative.append(running)

    def sample(self) -> int:
        return bisect.bisect_left(self.cumulative, random.random())

# Method 2: Alias Method (O(1) sampling)
class AliasMethod:
    def __init__(self, weights: list[float]):
        n = len(weights)
        total = sum(weights)
        prob = [w * n / total for w in weights]
        self.alias = list(range(n))
        self.prob = [1.0] * n

        small, large = [], []
        for i, p in enumerate(prob):
            (small if p < 1.0 else large).append(i)

        while small and large:
            s, l = small.pop(), large.pop()
            self.prob[s] = prob[s]
            self.alias[s] = l
            prob[l] -= (1.0 - prob[s])
            (small if prob[l] < 1.0 else large).append(l)

    def sample(self) -> int:
        i = random.randint(0, len(self.prob) - 1)
        return i if random.random() < self.prob[i] else self.alias[i]
```

- **Prefix Sum**: Build O(n), Sample O(log n), Space O(n) -- 简单通用
- **Alias Method**: Build O(n), Sample O(1), Space O(n) -- 高频采样场景最优
- **Follow-up**: Reservoir sampling (蓄水池采样) 用于 streaming data (流式数据)

---

### Q22."""
    )

    # ── Q22: Open Source vs Build ──
    content = content.replace(
        """**题目**: Compare and contrast using open-source software vs building your own solution (build vs buy). How would you make this decision for a machine learning project at a large company like LinkedIn? Discuss factors like maintainability, customization, security, community support, licensing, and cost.

---

### Q23.""",
        """**题目**: Compare and contrast using open-source software vs building your own solution (build vs buy). How would you make this decision for a machine learning project at a large company like LinkedIn? Discuss factors like maintainability, customization, security, community support, licensing, and cost.

**解答**:

**决策矩阵**:

| 维度 | Open Source (开源) | Build In-House (自研) |
|------|-------------------|----------------------|
| **Time to Market** | 快 -- 现成解决方案 | 慢 -- 需要开发周期 |
| **Customization** | 受限于现有 API | 完全定制 |
| **Maintenance** | 社区维护，但升级可能 break | 团队全权负责 |
| **Security** | 代码公开可审计，但漏洞也公开 | 内部控制，但审计资源有限 |
| **Cost** | 免费但有隐性运维成本 | 高开发成本但长期可控 |
| **Talent** | 降低招聘门槛 (通用技能) | 需要专门人才 |
| **Licensing** | 注意 GPL/AGPL 传染性 | 无许可证风险 |

**LinkedIn/大厂语境下的考量**:
1. **Core vs Context**: 核心竞争力 (ranking, recommendation) 自研；基础设施 (monitoring, logging) 用开源
2. **规模因素**: LinkedIn 规模 (500M+ users) 下，通用开源工具可能性能不足，需要定制
3. **实际案例**: LinkedIn 自研 Voldemort (KV store), Kafka (messaging) 而非用现有方案
4. **ML Frameworks**: 通常用开源 (PyTorch, TensorFlow) + 自研训练/serving infrastructure
5. **决策流程**: 先用开源 PoC (Proof of Concept，概念验证)，验证后再决定是否自研替代

**推荐答题框架**: "对于 [specific ML project]，我会先评估：(1) 是否是核心竞争力，(2) 规模需求是否超出开源能力，(3) 团队维护能力。非核心 + 规模合适 => 开源；核心 + 定制需求高 => 自研。"

---

### Q23."""
    )

    # ── Q23: LinkedIn Product Sense ──
    content = content.replace(
        """**题目**: Which LinkedIn product do you like most and why? Demonstrate your understanding of LinkedIn's product ecosystem and your product sense by analyzing a specific feature - its value proposition, target users, key metrics, and potential improvements.

---""",
        """**题目**: Which LinkedIn product do you like most and why? Demonstrate your understanding of LinkedIn's product ecosystem and your product sense by analyzing a specific feature - its value proposition, target users, key metrics, and potential improvements.

**解答**:

**示例回答: LinkedIn Feed Ranking (信息流排序)**

**1. Value Proposition (价值主张)**:
- 将最相关的专业内容推送给用户，提高信息获取效率
- 帮助 content creators 获得精准曝光
- 为 LinkedIn 创造广告收入基础 (feed ads)

**2. Target Users (目标用户)**:
- **Active Professionals**: 寻找行业 insights, job opportunities, networking
- **Content Creators**: 希望建立 professional brand (专业品牌)
- **Recruiters/Sales**: 通过内容触达潜在候选人/客户

**3. Key Metrics (核心指标)**:
- **Engagement**: DAU/MAU ratio, sessions per day, time spent in feed
- **Content Quality**: 有价值互动率 (comments vs likes), share rate
- **Creator Health**: 新 creator 留存率, 内容发布频率
- **Business**: Feed ad CTR, revenue per session, CPM

**4. Potential Improvements (改进方向)**:
- **Content Diversity**: 避免 echo chamber (信息茧房)，引入 exploration-exploitation 平衡
- **Professional Context**: 根据用户当前 career stage 调整内容 (job seeker vs hiring manager)
- **Quality Signal**: 区分 "engagement bait" 和真正有价值的专业内容
- **Cross-format**: 更好地融合 articles, videos, newsletters, polls 的混合排序

**答题技巧**: 选你最熟悉的产品，展示 (1) 对用户需求的深度理解，(2) 数据驱动的思维，(3) 可落地的改进建议。避免泛泛而谈。

---"""
    )

    return content


def main() -> None:
    """Apply enrichments and save."""
    conn = sqlite3.connect(str(DB_PATH))
    content = get_content(conn)
    original_len = len(content)

    enriched = enrich(content)

    if enriched == content:
        print("WARNING: No changes applied -- check markers")
        conn.close()
        sys.exit(1)

    conn.execute(
        "UPDATE company_documents SET content=? WHERE id=26",
        (enriched,),
    )
    conn.commit()
    new_len = len(enriched)
    print(f"OK: doc#26 enriched {original_len}c -> {new_len}c (+{new_len - original_len}c)")
    print("ML Theory Q16-Q23: all 8 questions enriched with full solutions")
    conn.close()


if __name__ == "__main__":
    main()
