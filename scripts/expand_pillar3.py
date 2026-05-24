"""Expand Pillar 3 nodes (89-107) to meet 5500+ char requirement.

This script:
1. Runs the existing translate_pillar3.py to apply base Chinese translations
2. Appends additional content to each node to reach 5500+ chars
3. Verifies all nodes meet the requirements
"""
import importlib.util
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "mle_prep.db")

# Load base translations
spec = importlib.util.spec_from_file_location(
    "translate_pillar3",
    os.path.join(BASE_DIR, "translate_pillar3.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Additional content for each node to reach 5500+ chars
EXPANSIONS = {}

EXPANSIONS[89] = r"""

## Advanced Topics

### Hybrid Retrieval Architecture

**Hybrid Retrieval（混合检索）** 是当前搜索系统的最佳实践，同时利用稀疏和稠密信号。通过 **RRF (Reciprocal Rank Fusion，倒数排名融合)** 合并两路结果：

$$\text{RRF}(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$

其中 $$r(d)$$ 为文档 $$d$$ 在排序 $$r$$ 中的排名，$$k$$ 为平滑常数（通常取 60）。混合检索通常比单独使用任一方法在 NDCG 上提升 5-15%。

### Query Rewriting with LLM

利用 **LLM (Large Language Model，大语言模型)** 进行查询改写是近年来的重要创新。LLM 可以理解用户的模糊意图并生成更适合检索的查询表达。这种方法不需要修改索引，是提升搜索质量的低成本高收益方案。同时，基于 LLM 的查询理解可以实现更复杂的意图解析，如多轮对话式搜索中的指代消解和上下文理解。

### Distributed Index Architecture

工业级搜索系统采用 **Sharding（分片）** + **Replication（副本）** 的分布式架构。索引按文档 ID 哈希或按主题进行分片，每个分片有多个副本保证高可用。查询执行采用 **Scatter-Gather（分发-汇聚）** 模式，将请求扇出到所有分片并行处理后合并结果。**Tiered Index（分层索引）** 策略将热门文档放入内存层，长尾文档放在磁盘层，优化整体资源利用率和查询尾部延迟。索引更新时使用 **Canary Query（金丝雀查询）** 机制进行质量回归检测，确保新索引不会导致搜索质量下降。
"""

EXPANSIONS[90] = r"""

## Advanced Topics

### Feedback Loop & Data Flywheel

**Data Flywheel（数据飞轮）** 是推荐系统持续改进的核心机制：用户行为数据训练模型 -> 更好的推荐吸引更多交互 -> 更多数据进一步提升模型。但需要警惕 **Filter Bubble（过滤气泡）** 效应：系统只推荐用户已知喜好的内容，导致信息茧房。解决方案包括引入多样性约束、探索机制（如 epsilon-greedy 或 Thompson Sampling）和内容新鲜度加分。

### Real-time Recommendation Architecture

现代推荐系统采用实时架构：用户行为通过 **Kafka** 流入实时特征计算管道（Flink/Spark Streaming），更新用户画像和近期行为序列。推理服务在毫秒级返回个性化推荐结果。这要求模型支持 **Incremental Update（增量更新）** 或 **Online Learning（在线学习）**，以捕获用户最新兴趣变化。实时推荐架构的关键组件包括实时特征存储（Redis/DynamoDB）、在线推理服务（TF Serving/Triton）和实时日志采集管道。

### Diversity & Exploration

推荐系统的多样性控制是工程与产品的核心课题：

| 策略 | 方法 | 目标 |
|------|------|------|
| **MMR (Maximal Marginal Relevance，最大边际相关性)** | 贪心选择兼顾相关性和多样性的结果 | 避免结果同质化 |
| **DPP (Determinantal Point Process，行列式点过程)** | 基于核矩阵的概率多样性采样 | 保证子集多样性 |
| **Slot-based Diversity（插槽多样性）** | 在结果列表中预留固定位置给不同品类 | 保证品类覆盖 |
| **Exploration（探索）** | Bandit 算法为新内容分配曝光 | 发现新兴趣 |

### Evaluation Beyond Accuracy

推荐系统的评估需要超越准确性指标，关注用户长期价值：**Serendipity（惊喜度）** 衡量推荐结果中用户意想不到但喜欢的比例；**Coverage（覆盖率）** 衡量被推荐过的物品占总物品的比例；**Fairness（公平性）** 确保不同创作者和供给方获得合理的曝光机会。长期指标如用户留存率、生态健康度比短期 CTR 更重要，但测量周期更长。
"""

EXPANSIONS[91] = r"""

## Advanced Topics

### Attribution Modeling

**Attribution（归因）** 是广告系统的关键问题：用户在多个广告触点之间转化时，如何将转化价值分配给各个触点？

| 归因模型 | 原理 | 优缺点 |
|----------|------|--------|
| **Last-click（末次点击）** | 全部归因于最后一次点击 | 简单但忽略上游触点的贡献 |
| **First-click（首次点击）** | 全部归因于首次点击 | 简单但忽略下游触点的转化作用 |
| **Linear（线性归因）** | 均匀分配给所有触点 | 公平但不区分触点重要性 |
| **Data-driven（数据驱动）** | 基于 Shapley Value 或 ML 模型 | 最准确但计算复杂 |

### Creative Optimization

**Creative Optimization（广告创意优化）** 使用 ML 自动选择最优的广告素材组合：标题、图片、CTA 按钮等元素通过 **Multi-Armed Bandit（多臂老虎机）** 策略动态分配流量，快速找到 CTR 最高的创意版本。大规模创意优化需要处理 **Combinatorial Exploration（组合探索）** 问题，因为元素组合数呈指数增长。

### Privacy-Preserving Ads

随着隐私法规（GDPR、CCPA）和浏览器限制（第三方 Cookie 消亡），广告系统面临重大转型。**Privacy Sandbox** 等新技术通过 **Federated Learning（联邦学习）** 和 **Differential Privacy（差分隐私）** 在保护用户隐私的同时维持广告效果。**On-device Learning（端上学习）** 在用户设备上进行个性化推理，避免个人数据传输到服务器，是隐私保护广告的重要方向。

### Real-time Bidding Pipeline

实时竞价管道的延迟预算通常仅有 50-100ms，需要在此时间内完成特征提取、CTR/CVR 预估、出价计算和预算校验。系统设计需要高度优化的推理服务（模型量化、特征缓存）和分层降级策略（当某个模型超时时回退到简单模型或历史统计值）。广告系统的可靠性直接关系到收入，因此需要完善的容灾和降级机制。
"""

EXPANSIONS[92] = r"""

## Advanced Topics

### Multi-Objective Optimization

市场平台的优化目标往往相互矛盾，需要 **Multi-Objective Optimization（多目标优化）**：

$$\min_\theta \left[\text{ETA Error}(\theta), -\text{GMV}(\theta), \text{Wait Time}(\theta)\right]$$

通过 **Pareto Front（帕累托前沿）** 寻找无法同时改善所有目标的最优解集。实际系统中通常将次要目标转化为约束条件，在约束范围内优化主要目标。

### Simulation Environment

由于线上实验成本高且风险大，市场平台广泛使用 **Simulation（仿真）** 环境评估算法变更。仿真器模拟供需时空分布、用户行为模式、交通状况和天气影响，支持离线策略评估和参数搜索。高保真仿真器的校准本身就是一个 ML 问题，需要用历史数据训练环境模型。

### Pricing Strategy Design

动态定价策略需要考虑多个维度：**Price Elasticity（价格弹性）** 模型估计需求对价格的敏感度 $$\epsilon = \frac{\partial \ln Q}{\partial \ln P}$$；**Competitive Pricing（竞争定价）** 考虑竞对的定价策略；**Fairness Constraints（公平性约束）** 避免对特定地区或人群的价格歧视。Uber 的 Surge Pricing 曾因在紧急事件期间大幅涨价而遭受公关危机，说明定价策略不仅是技术问题，还涉及社会责任和品牌影响。

### Order Batching & Routing

**Order Batching（订单合并）** 在外卖配送场景中将多个顺路订单分配给同一骑手，提高配送效率。这是 NP-hard 的 **VRP (Vehicle Routing Problem，车辆路径问题)** 变种，工业系统通常采用贪心启发式算法结合 ML 预测（ETA、用户容忍度）来近似求解。关键约束包括餐品保温时间、骑手负载上限和用户期望送达时间。实际系统还需要处理实时订单插入和路径重规划问题。
"""

EXPANSIONS[93] = r"""

## Advanced Topics

### LLM Fine-tuning Strategies

大模型的微调策略选择对系统效果和成本有重大影响：

| 策略 | 训练成本 | 效果 | 适用场景 |
|------|----------|------|----------|
| **Full Fine-tuning（全量微调）** | 极高 | 最好 | 有大量标注数据，需要深度定制 |
| **LoRA (Low-Rank Adaptation，低秩适应)** | 低（仅训练 0.1% 参数） | 接近全量微调 | 资源受限，快速实验 |
| **Prefix Tuning（前缀调优）** | 低 | 中等 | 多任务共享基座模型 |
| **RLHF (Reinforcement Learning from Human Feedback，基于人类反馈的强化学习)** | 高 | 对齐人类偏好 | 对话系统、安全对齐 |

### Evaluation of LLM Systems

LLM 系统的评估是一个开放性挑战，传统 NLP 指标（BLEU、ROUGE）无法充分衡量生成质量：

- **LLM-as-Judge（LLM 作为评判者）**：使用强大的 LLM（如 GPT-4）评估其他模型的输出质量
- **Chatbot Arena / Elo Rating**：通过人类盲评打分建立模型排名
- **Red Teaming（红队测试）**：系统性地尝试让模型产生有害输出，评估安全性边界
- **Domain-specific Benchmarks（领域基准测试）**：针对特定应用场景设计的评估集

### Hallucination Mitigation

**Hallucination（幻觉）** 是 LLM 系统的核心挑战。缓解策略包括：RAG 提供事实依据、**Self-consistency（自洽性检查）** 多次采样取一致答案、**Fact-checking Pipeline（事实核查管道）** 对生成内容进行后验证、以及在 prompt 中明确要求模型在不确定时说"不知道"。工业系统通常将多种策略组合使用，并通过置信度分数决定是否需要人工审核。
"""

EXPANSIONS[94] = r"""

## Advanced Topics

### Multi-Sensor Fusion

自动驾驶等高级 CV 应用需要 **Multi-Sensor Fusion（多传感器融合）**：

| 传感器 | 优势 | 劣势 | 数据格式 |
|--------|------|------|----------|
| **Camera（摄像头）** | 颜色、纹理、语义丰富 | 受光照影响大 | 2D 图像 |
| **LiDAR（激光雷达）** | 精确 3D 距离测量 | 昂贵、点云稀疏 | 3D 点云 |
| **Radar（毫米波雷达）** | 全天候、测速准确 | 分辨率低 | 距离-速度图 |

融合策略分为 **Early Fusion（前融合）**（特征级拼接）、**Late Fusion（后融合）**（决策级融合）和 **Mid Fusion（中融合）**（中间层交互），BEVFusion 等方法在统一的 **BEV (Bird's Eye View，鸟瞰图)** 空间进行多模态融合。

### Data Flywheel for CV

**Data Flywheel（数据飞轮）** 是 CV 系统持续改进的核心机制：部署模型到生产环境 -> 自动收集模型预测困难或不确定的样本 -> 人工标注这些困难样本 -> 加入训练集重新训练 -> 部署更强的模型。Tesla 的自动驾驶系统通过全球车队持续收集数据就是数据飞轮的典型案例。关键技术包括 **Active Learning（主动学习）** 选择最有价值的样本进行标注，以及 **Auto-labeling（自动标注）** 用强模型给弱模型生成伪标签。

### Edge Deployment Optimization

CV 模型在边缘设备（手机、摄像头、车载芯片）上部署需要深度优化。**MobileNet** 使用 **Depthwise Separable Convolution（深度可分离卷积）** 将标准卷积的计算量减少约 $$8\text{-}9\times$$。**NAS (Neural Architecture Search，神经架构搜索)** 可以自动设计在特定硬件约束下最优的模型架构，EfficientNet 就是 NAS 发现的高效架构。部署工具链（TensorRT、CoreML、ONNX Runtime）提供了量化、图优化和硬件特化的推理加速。
"""

EXPANSIONS[95] = r"""

## Advanced Topics

### Explainability in Fraud Detection

反欺诈系统需要 **Explainability（可解释性）**，因为误杀正常用户会直接影响用户体验和客户关系。常用解释方法包括：**SHAP (SHapley Additive exPlanations，Shapley 加性解释)** 计算每个特征对预测的边际贡献；基于规则的解释将 ML 分数转化为人类可读的风险因素；**Counterfactual Explanation（反事实解释）** 告诉用户"如果XX条件不满足，交易就会通过"。

### Adaptive Risk Thresholds

反欺诈系统的风险阈值不应静态，而应根据业务场景动态调整。高价值交易需要更严格的阈值（误杀成本低于放行欺诈的损失），小额交易可以放宽以减少用户摩擦。**Risk-based Authentication（基于风险的认证）** 根据风险分数决定认证强度：低风险直接放行，中风险要求短信验证码，高风险要求人脸识别或人工审核。

### Anti-Money Laundering

**AML (Anti-Money Laundering，反洗钱)** 是金融欺诈检测的重要分支。洗钱者通过多层账户间的小额转账模糊资金来源。**Graph-based（基于图的）** 分析特别适合检测这类模式：将账户构建为节点、转账为边的有向图，通过社区发现和异常子图检测识别可疑的资金流动网络。
"""

EXPANSIONS[96] = r"""

## Advanced Topics

### GPU Cluster Management

大规模 ML 训练和推理需要高效的 GPU 集群管理。关键技术包括：

- **Gang Scheduling（组调度）**：确保分布式训练的所有 GPU 同时分配，避免资源碎片化
- **Preemption（抢占）**：高优先级任务可以抢占低优先级任务的 GPU，被抢占的任务从 checkpoint 恢复
- **MIG (Multi-Instance GPU，多实例 GPU)**：将单块 A100 GPU 切分为多个小实例，提高利用率
- **Spot/Preemptible Instances（抢占式实例）**：使用云厂商的低价实例进行可中断的训练任务，节省 60-80% 成本

### Experiment Tracking & Reproducibility

**Experiment Tracking（实验追踪）** 系统需要记录每次实验的完整信息：代码版本（git commit）、数据版本（数据集哈希）、超参数配置、训练曲线和最终指标。**MLflow**、**Weights & Biases** 和 **Neptune** 是常用的实验追踪工具。可复现性要求还包括随机种子固定、确定性训练模式以及环境依赖锁定。

### Continuous Training Pipeline

**Continuous Training（持续训练）** 管道自动化模型更新流程：监控数据分布变化 -> 触发重训练 -> 自动评估新模型 -> 通过质量门控后自动部署。**Shadow Mode（影子模式）** 让新模型先在生产流量上并行运行但不影响用户，与旧模型对比一段时间后再切换。**Automatic Rollback（自动回滚）** 在新模型上线后持续监控关键指标，一旦检测到退化立即回滚到上一版本。
"""

EXPANSIONS[97] = r"""

## Advanced Topics

### Diffusion Model Architecture Evolution

扩散模型的架构经历了重要演进：从最初的 **U-Net** 到 **DiT (Diffusion Transformer，扩散 Transformer)**。DiT 用 Transformer 替代 U-Net 中的卷积层，在大规模训练时表现更好。**Stable Diffusion 3** 和 **FLUX** 采用的 **MM-DiT (Multi-Modal DiT，多模态扩散 Transformer)** 将文本和图像 token 在同一 Transformer 中处理，实现更好的文本-图像对齐。

### Video Generation Challenges

**Text-to-Video（文本生成视频）** 面临独特的技术挑战：

- **Temporal Consistency（时序一致性）**：相邻帧之间需要保持视觉连贯性，避免闪烁和形态突变
- **Long-range Dependency（长程依赖）**：视频中的对象和场景需要在整个时间跨度内保持一致
- **Computational Cost（计算成本）**：视频的 token 数量远超图像（时间 x 空间），推理成本极高
- **Motion Quality（运动质量）**：生成自然、物理合理的运动模式需要模型理解物理规律

Sora 等系统使用 **Spacetime Patches（时空分块）** 将视频表示为 3D token 序列，通过 Transformer 建模时空关系。

### Content Safety Pipeline

生成式 AI 的内容安全管道是产品化的关键环节：**Input Filter（输入过滤）** 检测和拒绝有害 prompt；**Output Filter（输出过滤）** 对生成内容进行 NSFW 检测、版权检查和事实性验证；**Watermarking（水印）** 在生成内容中嵌入不可见标记追踪来源。

### Cost Optimization for Generative AI

生成式 AI 推理成本远高于判别式模型。优化策略包括：**Caching（缓存）** 对相似 prompt 复用结果；**Model Cascade（模型级联）** 简单请求用小模型、复杂请求用大模型；**Quantization（量化）** INT8/INT4 降低精度；**Batching（批处理）** 合并请求提高 GPU 利用率。综合使用可降低推理成本 5-10 倍。
"""

EXPANSIONS[98] = r"""

## Advanced Topics

### Feature Engineering for Two-Tower

双塔模型的特征工程决定了模型的上限：

**User Tower 特征设计**：
- **ID Embedding**：用户 ID 的可学习嵌入，捕获个体偏好
- **Behavioral Sequence（行为序列）**：最近 N 次交互的物品 ID 序列，通过 Transformer 或 Attention Pooling 编码
- **User Profile（用户画像）**：人口统计特征（年龄、性别、地域）、注册时长、活跃度
- **Context Features（上下文特征）**：当前时间、设备类型、所在页面

**Item Tower 特征设计**：
- **ID Embedding**：物品 ID 的可学习嵌入
- **Content Features（内容特征）**：标题文本嵌入、图片 CNN 特征、品类和标签
- **Statistical Features（统计特征）**：历史点击率、平均观看时长、最近 7 天的互动数

### Addressing Representation Bottleneck

双塔模型的核心限制是 **Representation Bottleneck（表示瓶颈）**：用户和物品的所有信息被压缩为固定维度的向量，信息损失不可避免。缓解策略包括：

- **Multi-vector Representation（多向量表示）**：如 **ColBERT** 为每个 token 生成独立向量
- **Mixture of Logits（混合 Logit）**：使用多组嵌入的加权组合增加表达能力
- **Cross-feature in Late Stage（后续阶段引入交叉特征）**：在精排阶段使用交叉编码器
- **Larger Embedding Dimension（更大的嵌入维度）**：从 64 增加到 256，但需权衡 ANN 检索速度

### Production Deployment Patterns

工业部署需要考虑：索引的增量更新（新物品快速编码并加入 ANN 索引）、模型版本管理（新旧模型嵌入空间不兼容时需全量重建索引）、以及冷启动处理（新用户特征不完整时降级到热门推荐）。
"""

EXPANSIONS[99] = r"""

## Advanced Topics

### Cascade Effect & Error Propagation

多阶段系统的核心风险是 **Cascade Error（级联误差）**：前序阶段的遗漏无法被后续阶段弥补。因此：

- 召回阶段的 **Recall@K** 必须严格监控，目标通常 > 95%
- 多路召回策略通过冗余降低单路召回遗漏的风险
- 定期对精排结果进行反向分析：检查精排 top-10 中各路召回的贡献比例
- **全量评估**：定期对全量物品跑精排模型，检查是否有被召回遗漏的高分物品

### Distillation Across Stages

**Cross-stage Distillation（跨阶段蒸馏）** 是优化多阶段系统的有效方法：用精排模型的打分结果作为粗排模型的训练标签，使粗排逼近精排的排序能力。这比让粗排直接学习用户行为标签更有效，因为精排已经融合了更丰富的特征和更复杂的建模能力。

### Listwise Re-ranking

传统重排将每个物品独立打分，忽略了物品间关系。**Listwise Re-ranking（列表级重排）** 考虑整个推荐列表的全局质量，使用 Transformer 自回归生成推荐列表，每一步选择都考虑已选物品。**PRM (Personalized Re-ranking Model，个性化重排模型)** 在阿里巴巴的推荐系统中取得了显著效果。

### Online-Offline Consistency

确保在线系统行为与离线评估一致是重要的工程挑战。**Feature Logging（特征日志）** 记录每次在线请求使用的特征值，用于离线回放和模型训练，确保训练数据与在线推理完全一致。
"""

EXPANSIONS[100] = r"""

## Advanced Topics

### Hybrid Index Strategies

工业系统通常组合使用多种 ANN 算法。**IVF + HNSW** 组合将 IVF 的粗量化与 HNSW 的图搜索结合：先用 IVF 缩小搜索范围，再在每个聚类内用 HNSW 精确搜索。**IVF + PQ** 组合是内存受限场景的首选：IVF 缩小范围，PQ 压缩向量存储，两者配合可在单机上索引十亿级向量。

### Vector Database Architecture

**Vector Database（向量数据库）** 在 ANN 索引基础上增加了数据库功能：

- **Metadata Filtering（元数据过滤）**：向量检索的同时支持属性过滤（如"只搜索最近 7 天的文档"）
- **Multi-tenancy（多租户）**：不同用户/应用共享同一集群，数据隔离
- **Distributed Sharding（分布式分片）**：向量索引分布到多个节点，支持水平扩展
- **Consistency Model（一致性模型）**：写入后多久可读（最终一致 vs 强一致）

主流选择包括 **Milvus**（开源分布式）、**Pinecone**（全托管）、**Weaviate**（开源，支持混合检索）和 **Qdrant**（Rust 实现，高性能）。

### Dimension Reduction & Quantization

当嵌入维度过高时，可以通过降维和量化减少开销：**PCA（主成分分析）** 线性降维保留方差最大的方向；**Random Projection（随机投影）** 利用 Johnson-Lindenstrauss 引理保证降维后距离近似保持；**Scalar Quantization（标量量化）** 将 float32 量化为 int8，存储减少 4x；**Binary Quantization（二值量化）** 每维 1 bit，通过 Hamming 距离加速检索。
"""

EXPANSIONS[101] = r"""

## Advanced Topics

### Feature Store Anti-Patterns

常见的 Feature Store 反模式：

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| **训练时自行计算特征** | 训练-推理偏差 | 统一使用 Feature Store 的特征定义 |
| **在线存储保存历史版本** | 存储爆炸 | 在线只存最新值，历史存离线 |
| **未做 Point-in-time Join** | 标签泄露 | 严格按事件时间关联特征 |
| **特征定义散落各处** | 重复开发、不一致 | 集中的 Feature Registry |

### Feature Monitoring & Quality

特征质量监控是 Feature Store 的重要功能：

- **Distribution Monitoring（分布监控）**：使用 **KS Test（KS 检验）** 或 **PSI (Population Stability Index，群体稳定性指标)** 检测特征分布偏移
- **Freshness Monitoring（新鲜度监控）**：监控在线特征的更新延迟，确保满足 SLA
- **Completeness Monitoring（完整性监控）**：监控特征的缺失率和空值比例
- **Schema Validation（模式验证）**：确保特征值的类型和范围符合定义

当特征质量异常时，系统应自动降级到备用特征或默认值而非使用错误的特征值进行推理。

### Feature Store at Scale

超大规模 Feature Store 的工程挑战包括：热点特征的多级缓存策略、跨团队的特征复用和发现机制、按使用量的成本分摊、以及敏感特征的访问权限控制和审计日志。特征复用率是衡量 Feature Store 价值的核心指标。
"""

EXPANSIONS[102] = r"""

## Advanced Topics

### Multi-Modal Embeddings

**Multi-Modal Embeddings（多模态嵌入）** 将不同模态的数据映射到同一向量空间：

- **CLIP (Contrastive Language-Image Pre-training，对比语言-图像预训练)**：将文本和图像编码到共享空间，支持零样本图像分类和跨模态检索
- **ImageBind**：Meta 提出，将 6 种模态统一到一个嵌入空间
- **Embedding as Feature（嵌入作为特征）**：将预训练嵌入作为下游模型的输入特征，是迁移学习最常用的方式

### Embedding Compression

大规模嵌入表的压缩对工业系统至关重要：

| 压缩方法 | 压缩比 | 精度影响 | 适用场景 |
|----------|--------|----------|----------|
| **Mixed-dimension Embedding（混合维度嵌入）** | 2-4x | 低 | 热门物品高维、冷门物品低维 |
| **Hash Embedding（哈希嵌入）** | 5-10x | 中 | 减少嵌入表行数 |
| **Product Quantization（乘积量化）** | 8-32x | 中 | 向量检索场景 |
| **Knowledge Distillation（知识蒸馏）** | 定制 | 低 | 将大嵌入表蒸馏到小嵌入表 |

### Domain-Specific Embedding Training

不同领域需要定制化的嵌入训练策略：搜索领域关注查询-文档的语义匹配，训练数据来自点击日志；推荐领域关注用户-物品的兴趣匹配，训练数据来自行为序列；代码领域关注函数-描述的对应关系，需要理解代码语义。通用预训练嵌入可以作为起点，但在特定领域任务上通常不如领域定制化嵌入效果好。
"""

EXPANSIONS[103] = r"""

## Advanced Topics

### Complex Event Processing

**CEP (Complex Event Processing，复杂事件处理)** 在实时特征计算中检测跨多个事件的复杂模式：

- **Sequence Pattern（序列模式）**：检测用户在特定时间内依次执行的操作序列
- **Aggregation Pattern（聚合模式）**：计算时间窗口内的统计指标
- **Correlation Pattern（关联模式）**：检测多个用户/设备之间的关联行为

### Backfill Strategy

**Backfill（回填）** 是实时特征系统的重要运维操作：当特征计算逻辑变更或修复 bug 时，需要重新计算历史时间段的特征值。回填策略需要在不影响在线服务的前提下，使用离线计算引擎重放历史事件流。关键挑战包括保证回填结果与实时计算的一致性、处理回填期间新到达的事件、以及控制对在线存储的写入压力。

### State Management

流式特征计算的状态管理是核心工程挑战。有状态算子（如窗口聚合）需要在节点故障时恢复状态。**Flink** 通过 **Checkpoint（检查点）** 和 **Savepoint（保存点）** 机制实现 exactly-once 状态恢复。状态大小管理也很重要——窗口过大会导致状态膨胀，需要 TTL 清理过期状态。
"""

EXPANSIONS[104] = r"""

## Advanced Topics

### Variance Reduction Techniques

除 CUPED 外，还有多种方差缩减技术：

- **Stratified Sampling（分层采样）**：按用户属性分层后在层内随机分配
- **CUPAC (Control Using Predictions As Covariates，使用预测作为协变量的控制)**：用 ML 模型的预测值作为协变量进一步缩减方差
- **Delta Method（Delta 方法）**：对比率型指标（如 Revenue/User）精确计算方差
- **Trimming（截尾处理）**：去除极端值减少方差，但需验证截尾不引入偏差

### Interaction Effects & Mutual Exclusion

当多个实验同时运行时需要处理 **Interaction Effects（交互效应）**：**Mutual Exclusion Layer（互斥层）** 确保同一用户在同一层内只参与一个实验；**Orthogonal Layer（正交层）** 使不同层的实验独立随机化；**Holdout Group（保留组）** 保留部分用户不参与任何实验作为长期基准。

### Long-term Effect Measurement

A/B 测试通常衡量短期效果（1-2 周），但 ML 模型变更可能有长期影响。**Holdback Experiment（保留实验）** 将部分用户长期保持旧版本持续比较；**Switchback Experiment（切换实验）** 在市场平台中交替使用新旧策略；**Regression Discontinuity（断点回归）** 利用阈值附近的自然分割进行准实验设计。

### Bayesian A/B Testing

**Bayesian A/B Testing（贝叶斯 A/B 测试）** 提供更直观的概率解释。优势包括：自然支持随时停止（无 peeking 问题）、结果直接表述为"B 优于 A 的概率为 X%"、可以融入先验知识。
"""

EXPANSIONS[105] = r"""

## Advanced Topics

### Bayesian Optimization

**Bayesian Optimization（贝叶斯优化）** 是探索利用思想在连续空间中的应用：

$$x_{t+1} = \arg\max_x \alpha(x | \mathcal{D}_{1:t})$$

其中 $$\alpha$$ 为 **Acquisition Function（采集函数）**（如 Expected Improvement、UCB），**Gaussian Process（高斯过程）** 作为替代模型建模目标函数的不确定性。贝叶斯优化在 ML 超参数调优中广泛应用：**Optuna**、**Hyperopt** 等工具通过贝叶斯优化高效搜索超参数空间。

### Contextual Bandits in Practice

工业级 Contextual Bandit 系统的实际挑战包括：高维动作空间需要结合检索系统缩小范围、用户偏好的非平稳性需要适应分布偏移、以及 **Off-policy Evaluation (OPE，离策略评估)** 使用 IPS 或 Doubly Robust 估计器评估新策略效果。
"""

EXPANSIONS[106] = r"""

## Advanced Topics

### Distillation for LLM Compression

**LLM 蒸馏** 是当前模型压缩的热点方向。典型流程：使用大型教师模型在大量无标签数据上生成高质量标注，然后用这些标注训练较小的学生模型。关键技术包括：

- **Data Curation（数据策展）**：选择多样化的、有代表性的训练样本
- **Progressive Distillation（渐进蒸馏）**：逐步减小学生模型大小
- **Task-specific Distillation（任务特定蒸馏）**：针对特定下游任务蒸馏
- **Synthetic Data Generation（合成数据生成）**：教师模型生成大量高质量训练数据

### Distillation in Ranking Systems

排序系统中的蒸馏是多阶段排序架构的核心优化手段。通过 pairwise 排序蒸馏，粗排模型可以学习到精排模型的排序偏好，而非直接从用户行为标签学习。这显著提升了粗排与精排的一致性。

### Practical Tips

蒸馏的实践经验：温度过低（< 2）时软标签接近硬标签，蒸馏效果有限；温度过高（> 20）时分布过于均匀，信息量不足，通常 $$T \in [4, 10]$$ 效果最好。当数据充足时 $$\alpha$$ 可设较小（如 0.1）更多依赖软标签；数据少时 $$\alpha$$ 设较大（如 0.5）硬标签提供更强监督。使用多个教师模型的平均输出作为软标签比单一教师效果更好。
"""

EXPANSIONS[107] = ""  # Already passes at 5535 chars


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA encoding = 'UTF-8'")
    cur = conn.cursor()

    # Step 1: Apply base translations
    for node_id in sorted(mod.NODES.keys()):
        desc = mod.NODES[node_id]
        cur.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (desc, node_id),
        )
    conn.commit()
    print("Base translations applied.")

    # Step 2: Apply expansions
    for node_id, expansion in EXPANSIONS.items():
        if not expansion:
            continue
        cur.execute(
            "SELECT description FROM framework_nodes WHERE id = ?",
            (node_id,),
        )
        current = cur.fetchone()[0]
        new_desc = current + expansion
        cur.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (new_desc, node_id),
        )
    conn.commit()
    print("Expansions applied.")

    # Step 3: Verify
    print("\n=== Verification ===")
    all_pass = True
    for node_id in range(89, 108):
        cur.execute(
            "SELECT LENGTH(description) FROM framework_nodes WHERE id = ?",
            (node_id,),
        )
        length = cur.fetchone()[0]
        cur.execute(
            "SELECT description FROM framework_nodes WHERE id = ?",
            (node_id,),
        )
        text = cur.fetchone()[0]
        has_chinese = any("\u4e00" <= c <= "\u9fff" for c in text)
        status = "PASS" if length >= 5500 and has_chinese else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(
            f"Node {node_id}: length={length}, has_chinese={has_chinese}, {status}"
        )

    conn.close()
    print(f"\nAll passed: {all_pass}")


if __name__ == "__main__":
    main()
