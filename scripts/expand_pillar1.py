"""Expand Pillar 1 nodes that are below 4K chars to meet the threshold."""
import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "mle_prep.db")

# Additional content to append to each node that's too short
# These expansions add ML context, deeper explanations, and more interview tips

EXPANSIONS = {}

EXPANSIONS[44] = r"""

## ML Application Context
在机器学习工程中，数组和字符串操作是日常工作的基础：

### NumPy/PyTorch 中的数组操作
数组操作与张量操作有直接的对应关系。面试中常见的数组题目可以帮助理解底层的张量运算：
- **切片和索引**：NumPy 的高级索引（fancy indexing）允许使用数组作为索引，这在特征选择和数据采样中非常常用
- **向量化操作**：将 Python for 循环转化为 NumPy/PyTorch 的向量化操作可获得 100-1000 倍的加速。面试中如果你的解法涉及嵌套循环，面试官可能会追问如何向量化
- **内存布局**：C-contiguous（行优先）vs Fortran-contiguous（列优先）影响矩阵运算的缓存效率。`np.ascontiguousarray()` 确保内存连续

### 文本处理与 NLP
字符串操作在 NLP 预处理管道中至关重要：
- **分词 (Tokenization)**：将文本拆分为 tokens，涉及大量字符串操作
- **正则表达式**：清洗文本数据、提取模式、规范化格式
- **编码处理**：UTF-8 编码在多语言 NLP 中是必须理解的概念

### 面试策略提示
- 当看到"子数组"关键词时，优先考虑滑动窗口或前缀和
- 当看到"排序数组"时，优先考虑二分查找或双指针
- 当需要 $$O(1)$$ 空间时，考虑原地操作（读写指针模式）
- 当问题涉及"连续"子序列时，滑动窗口通常是最优解法
- 面试开始时花 1-2 分钟确认输入约束（数组是否已排序、是否有重复、数值范围等）
"""

EXPANSIONS[46] = r"""

## ML Application Context
栈和队列在 ML 系统中有重要应用：

### 计算图与自动微分
深度学习框架中的自动微分使用栈来管理计算图的反向传播顺序。每个操作被压入栈中，反向传播时按 LIFO 顺序弹出并计算梯度。

### 数据管道中的队列
- **数据加载**：PyTorch 的 `DataLoader` 使用多进程队列将预处理后的 batch 传递给训练循环
- **请求队列**：ML 推理服务使用队列管理传入的推理请求，实现负载均衡和批量推理
- **消息队列**：Kafka、RabbitMQ 等消息队列在 ML 管道中用于解耦数据生产者和消费者

### Beam Search 中的优先队列
在序列生成任务（机器翻译、文本生成）中，**Beam Search（束搜索）** 使用优先队列维护 top-k 候选序列。每一步扩展所有候选，保留得分最高的 k 个。

### 面试策略提示
- 看到"括号匹配"或"嵌套结构"立即想到栈
- 看到"滑动窗口最大/最小值"立即想到单调 deque
- 单调栈问题的本质是：对于每个元素，找到它之前/之后的第一个更大/更小元素
- Min Stack 的变体可能要求同时支持 getMax -- 使用两个辅助栈
- 在实现计算器时，注意运算符优先级和括号的嵌套处理
"""

EXPANSIONS[47] = r"""

## ML Application Context
虽然链表在 ML 中不常直接使用，但相关概念有重要应用：

### LRU Cache 在 ML 系统中的应用
**LRU Cache（最近最少使用缓存）** 是链表最实用的应用，在 ML 系统中广泛使用：
- **特征缓存**：缓存最近查询的特征向量，避免重复从数据库获取
- **模型缓存**：在多模型服务中，缓存最近使用的模型权重
- **Embedding 缓存**：缓存高频查询的 embedding 向量，减少计算开销
- Python 的 `functools.lru_cache` 底层使用双向链表 + 字典实现

### 内存管理
操作系统的空闲内存块管理使用链表。理解链表有助于理解 GPU 内存分配器的工作原理（如 PyTorch 的 CUDA 缓存分配器）。

### 面试策略提示
- 链表题几乎总是可以用哑节点简化 -- 养成习惯
- 反转链表是很多高级链表题的子操作（如 K 个一组反转）
- 快慢指针的核心思想：利用速度差来确定相对位置
- 面试中画图至关重要 -- 指针操作的顺序稍有不当就会导致丢失节点
- 链表题的常见追问：能否原地操作？能否用 $$O(1)$$ 空间？
- 合并 K 个有序链表是分治思想在链表上的经典应用
"""

EXPANSIONS[48] = r"""

## ML Application Context
树结构在 ML 中有广泛的应用：

### 决策树与集成学习
- **Decision Tree（决策树）** 的每次分裂本质上是 BST 的插入操作
- **Random Forest（随机森林）** 和 **XGBoost** 等集成方法构建大量决策树
- 理解树的遍历有助于理解特征重要性计算（通过遍历所有树的分裂节点统计）

### 语法树与 NLP
- **AST (Abstract Syntax Tree，抽象语法树)** 在代码分析中使用树结构表示程序的层次结构
- NLP 中的 **Parse Tree（解析树）** 表示句子的语法结构
- **Tree-LSTM** 和 **Tree Transformer** 直接在树结构上进行编码

### 层次聚类
**Hierarchical Clustering（层次聚类）** 构建一棵树（称为 dendrogram），表示数据点之间的聚类层次关系。自底向上（凝聚）或自顶向下（分裂）构建。

### 面试策略提示
- 树问题的第一反应应该是递归 -- 确定基本情况和递推关系
- 如果面试官要求迭代解法，用栈模拟递归
- BST 的中序遍历给出排序序列 -- 这个性质可以解决很多 BST 问题
- "树的直径"和"最大路径和"是两个看似相似但解法不同的经典问题
- 序列化/反序列化是系统设计面试中也可能出现的树问题
"""

EXPANSIONS[50] = r"""

## ML Application Context
Trie 在 ML 和 NLP 系统中有重要应用：

### 分词器 (Tokenizer)
现代 NLP 模型使用 **BPE (Byte Pair Encoding，字节对编码)** 分词器，其底层词汇表查找可以用 Trie 优化：
- 给定一段文本，快速找到最长匹配的 token
- 词汇表通常包含 30K-100K 个 token，Trie 的前缀搜索比逐个匹配高效得多

### 自动补全系统
搜索引擎和输入法的自动补全功能是 Trie 的经典应用场景：
- 用户输入前缀时，Trie 快速返回所有匹配的候选词
- 结合频率信息和用户历史进行排序
- ML 模型可以在 Trie 的基础上进行个性化排序

### IP 路由与特征前缀匹配
网络路由使用 Trie（通常是压缩 Trie / 基数树）进行最长前缀匹配。类似地，在特征工程中，可以使用 Trie 对分类特征进行前缀分组。

### 面试策略提示
- Trie 的核心优势在于前缀查询 -- 如果问题涉及"前缀"关键词，优先考虑 Trie
- Word Search II 是 Trie 的高频面试题 -- 构建 Trie 后在网格上 DFS
- 位运算 Trie 求最大异或对是一个高级技巧，但出现频率在增加
- 在实际系统中，Trie 通常与其他数据结构结合使用（如 Trie + 堆实现 top-k 自动补全）
- 面试中提到 Trie 的压缩变体（Radix Tree）会加分
"""

EXPANSIONS[51] = r"""

## ML Application Context
Union-Find 在 ML 中有多个重要应用：

### 实体消解 (Entity Resolution)
在数据清洗和知识图谱构建中，**Entity Resolution（实体消解）** 需要将引用同一实体的不同记录合并。Union-Find 是实现这一功能的高效方法：
- 当发现两条记录引用同一实体时，执行 union 操作
- 最终，同一分量中的所有记录被认为是同一实体

### 图像分割
在计算机视觉中，基于像素相似度的图像分割可以使用 Union-Find：
- 将相似的相邻像素合并到同一分量
- 最终的分量对应图像中的不同区域/物体

### 聚类算法
**Single-Linkage Clustering（单链接聚类）** 和 Kruskal 算法有相同的结构：
- 按距离排序所有点对
- 依次合并最近的点对
- Union-Find 跟踪当前的聚类状态

### 面试策略提示
- Union-Find 的模板非常固定 -- 背熟模板后可以快速应用到各种问题
- 路径压缩和按秩合并必须同时实现才能获得最优性能
- 区分 Union-Find 和 BFS/DFS 的适用场景：Union-Find 适合动态连通性查询，BFS/DFS 适合路径搜索
- 带权 Union-Find 可以解决方程式问题（如 Evaluate Division）-- 这是一个高级但值得掌握的变体
- 面试中常见的陷阱：忘记返回 union 是否成功（影响环检测和分量计数）
"""

EXPANSIONS[52] = r"""

## ML Application Context
二分查找在 ML 中有多种应用：

### 超参数调优
**Binary Search on Answer（二分答案）** 的思想可以应用于超参数搜索：
- 对学习率进行二分搜索：如果当前学习率导致发散则降低，如果收敛太慢则增加
- 阈值优化：在 ROC 曲线上二分搜索最优分类阈值

### 分位数计算与百分位特征
在特征工程中，计算数据的分位数（如中位数、P95、P99）时，二分查找在排序数据上的效率是 $$O(\log n)$$。Python 的 `np.percentile` 和 `np.quantile` 底层使用类似的分区技术。

### 模型选择中的单调性
许多模型选择问题具有单调性质：增加模型复杂度（如树的深度、特征数量）通常先减少后增加验证集误差。这种 U 形曲线上的最优点可以用类似二分搜索的方法找到（三分搜索）。

### 面试策略提示
- 看到"最小化最大值"或"最大化最小值"时，立即考虑二分答案
- 二分查找的核心难点是边界条件 -- 建议选择一种固定模板并坚持使用
- `bisect_left` 和 `bisect_right` 在面试中可以直接使用，无需手写
- 旋转排序数组是二分查找的变体中最常考的 -- 关键是判断哪一半是有序的
- Median of Two Sorted Arrays 是二分查找的最难应用之一，需要专门准备
"""

EXPANSIONS[53] = r"""

## ML Application Context
BFS 和 DFS 在 ML 系统中有广泛应用：

### 图神经网络 (GNN)
**GNN (Graph Neural Network，图神经网络)** 的消息传递机制本质上是 BFS 的变体：
- 每一层聚合邻居的特征，对应 BFS 的一层
- K 层 GNN 等价于 K 跳的 BFS 邻域聚合
- **GraphSAGE** 使用采样的 BFS 邻居来减少计算量

### ML 管道中的依赖解析
ML 训练和推理管道中的任务依赖关系形成 DAG：
- 使用拓扑排序确定任务执行顺序
- Apache Airflow、Kubeflow Pipelines 等工具使用 DAG 来编排 ML 工作流
- 检测循环依赖（环检测）是管道验证的关键步骤

### 知识图谱遍历
在基于知识图谱的推荐和问答系统中：
- BFS 用于发现多跳关系（如"用户购买了X -> X的类似商品 -> 推荐"）
- DFS 用于发现深层路径和推理链

### 面试策略提示
- BFS 的关键细节：在入队时标记 visited，而非出队时 -- 这避免了重复入队
- 多源 BFS 是一个强大的模式 -- 将所有源点同时入队，逐层扩展
- 拓扑排序推荐使用 Kahn's 算法（BFS + 入度），代码更直观
- 网格问题中 BFS/DFS 的选择：最短路径用 BFS，路径枚举用 DFS
- 环检测的三色标记法（白/灰/黑）是理解 DFS 状态的最佳方式
"""

EXPANSIONS[54] = r"""

## ML Application Context
动态规划在 ML 中有深层次的应用：

### 序列模型与 Viterbi 算法
**Viterbi Algorithm（维特比算法）** 是 DP 在 ML 中最经典的应用：
- 在 **HMM (Hidden Markov Model，隐马尔可夫模型)** 中，Viterbi 算法用 DP 找到最可能的隐状态序列
- 在 **CRF (Conditional Random Field，条件随机场)** 中，Viterbi 用于序列标注的解码
- 时间复杂度 $$O(T \cdot S^2)$$，其中 $T$ 是序列长度，$S$ 是状态数

### CTC Loss
**CTC (Connectionist Temporal Classification)** 损失在语音识别中使用 DP 来计算所有可能对齐的概率总和，避免了需要预先对齐的问题。

### Beam Search 与 DP
**Beam Search（束搜索）** 可以看作带剪枝的 DP：每一步只保留 top-k 个候选状态，在效率和最优性之间权衡。

### 面试策略提示
- DP 问题的第一步永远是定义状态 -- 如果状态定义不清晰，后面一切都会出错
- 先写自顶向下（记忆化递归），确认正确后再转换为自底向上
- 空间优化是面试加分项：如果 `dp[i]` 仅依赖 `dp[i-1]`，可以用两个变量替代整个数组
- 背包问题的变体非常多 -- 分清楚 0/1 背包和完全背包的区别（内层循环方向）
- 编辑距离是面试必会题目，也是 NLP 中字符串相似度度量的基础
"""

EXPANSIONS[55] = r"""

## ML Application Context
贪心算法在 ML 中有多种应用：

### 特征选择
**Forward Feature Selection（前向特征选择）** 使用贪心策略：
- 每一步添加能够最大改善模型性能的一个特征
- 虽然不保证找到全局最优特征子集，但计算效率远高于穷举搜索
- 类似地，**Backward Elimination（后向消除）** 每步移除一个对模型贡献最小的特征

### Huffman 编码与数据压缩
**Huffman Coding（霍夫曼编码）** 是贪心算法的经典应用，在数据压缩中广泛使用：
- 为频率高的符号分配短编码，频率低的分配长编码
- 这是一种最优前缀编码方案
- 原理与信息论中的信息熵直接相关

### 语言模型中的贪心解码
在序列生成中，**Greedy Decoding（贪心解码）** 每一步选择概率最高的 token：
- 优点：速度快、实现简单
- 缺点：可能错过全局最优序列
- Beam Search 通过保留多个候选来改善贪心解码的质量

### 面试策略提示
- 贪心题的难点不在于编码，而在于证明正确性 -- 准备好交换论证（exchange argument）
- 区间调度问题是贪心的经典题型：最大不重叠区间按结束时间排序，最少会议室用堆
- 如果想到贪心解法但无法证明正确性，尝试找反例。找不到反例不代表贪心正确
- 面试中如果贪心失败，通常可以用 DP 解决 -- 这是一个常见的"降级"策略
- Task Scheduler 和 Candy 是两道需要仔细分析的贪心题，值得反复练习
"""

EXPANSIONS[56] = r"""

## ML Application Context
回溯法在 ML 中有多种应用：

### AutoML 与超参数搜索
**Grid Search（网格搜索）** 本质上是一种系统化的回溯搜索，遍历所有超参数组合。更智能的搜索方法（如基于约束的搜索）使用剪枝策略来减少搜索空间。

### 组合特征选择
当特征之间存在依赖或约束时，特征选择问题可以建模为约束满足问题，使用回溯法求解：
- 例如，某些特征不能同时选择（互斥约束）
- 或者某些特征必须一起选择（共现约束）

### Beam Search 变体
NLP 中的 **Constrained Beam Search（约束束搜索）** 在生成过程中添加约束（如必须包含某些词），本质上是带剪枝的回溯搜索。

### 面试策略提示
- 回溯模板是通用的：选择 -> 递归 -> 撤销。关键在于如何定义"选择"和"约束"
- 处理重复的标准方法：排序 + 跳过相邻重复。这在 Subsets II 和 Permutations II 中是必需的
- N 皇后问题的优化：用集合（而非数组）跟踪已使用的列和对角线，将约束检查从 $$O(n)$$ 降到 $$O(1)$$
- 回溯 vs DFS 的区别：回溯关注的是"构建解"并在不可行时撤销；DFS 关注的是"遍历图/树"
- 面试中在回溯题上常见的时间压力 -- 快速写出模板然后专注于问题特定的逻辑
"""

EXPANSIONS[57] = r"""

## ML Application Context
图算法在 ML 中有广泛且深入的应用：

### 图神经网络 (GNN) 消息传递
GNN 的消息传递可以看作图上的迭代松弛操作：
- **GCN (Graph Convolutional Network，图卷积网络)**：类似于在图上做"扩散"操作
- **GAT (Graph Attention Network，图注意力网络)**：在消息传递中引入注意力机制
- 消息传递的层数类似于 BFS 的层数（k 层 GNN 聚合 k 跳邻居的信息）

### 计算图优化
深度学习框架将模型表示为计算图，使用拓扑排序确定前向传播的顺序。反向传播则沿着反向拓扑序执行。图优化（如算子融合、内存优化）也依赖图算法。

### 推荐系统中的网络分析
- **二部图匹配**：用户-商品交互形成二部图，图算法用于发现社区和相似用户
- **PageRank**：最初用于网页排序，现在也用于知识图谱中的实体重要性排序
- **最短路径**：在知识图谱中发现实体之间的关系链

### 面试策略提示
- Dijkstra 面试实现要点：使用懒删除（弹出时检查是否过期）而非 decrease-key
- Bellman-Ford 变体："最多 K 站"问题需要在每轮之间复制距离数组，否则可能使用同一轮的更新
- 面试开始时一定要确认：有向还是无向？有权还是无权？是否可能有负权重？
- Floyd-Warshall 虽然是 $$O(V^3)$$，但在小图上非常实用且代码简洁
"""

EXPANSIONS[58] = r"""

## ML Application Context
分治法在 ML 中有重要的应用：

### 数据并行训练
**Data Parallel Training（数据并行训练）** 是分治思想的直接应用：
- **Divide**：将训练 batch 分割到多个 GPU
- **Conquer**：每个 GPU 独立计算梯度
- **Combine**：通过 All-Reduce 操作聚合所有 GPU 的梯度
- 这种方式可以线性地扩展训练吞吐量

### MapReduce 与分布式特征工程
**MapReduce** 框架遵循分治模式：
- **Map**：将数据分片，在每个分片上独立计算
- **Reduce**：合并所有分片的结果
- 在大规模特征工程中（如计算数十亿用户的特征统计），MapReduce 是标准的处理模式

### 决策树的递归分裂
决策树的构建过程是分治法的经典应用：
- **Divide**：根据最优分裂点将数据分为两个子集
- **Conquer**：在每个子集上递归构建子树
- **Combine**：将子树连接到当前节点

### 面试策略提示
- Master Theorem 是分析分治算法复杂度的最重要工具 -- 面试中可能直接被问到
- 归并排序的"合并"步骤是一个可复用的模式：逆序对计数本质上是在合并时额外计数
- Quick Select 的随机化很重要 -- 不随机化主元最坏情况是 $$O(n^2)$$
- 链表排序用归并排序（而非快排），因为链表不支持随机访问
- Median of Two Sorted Arrays 是分治的巅峰题目之一 -- 需要深入理解二分的变体
"""

EXPANSIONS[59] = r"""

## ML Application Context
矩阵和张量操作是 ML 的计算核心：

### GPU 加速与 CUDA
理解矩阵操作对 GPU 编程至关重要：
- GPU 的并行架构天然适合矩阵运算（SIMT 模型）
- **Tiling（分块）** 技术将大矩阵分成小块以充分利用共享内存
- 矩阵乘法的理论复杂度是 $$O(n^3)$$，但通过优化的 BLAS 库（如 cuBLAS）可以接近硬件峰值 FLOPS
- **Tensor Core** 在现代 GPU 上提供专用的矩阵乘法硬件，支持混合精度计算

### 注意力机制的矩阵解释
**Self-Attention（自注意力）** 的核心是一系列矩阵操作：
- 计算注意力分数：$$QK^T$$ 是一个矩阵乘法，产生 $$(seq, seq)$$ 的注意力矩阵
- 加权求和：注意力权重乘以 V 矩阵
- **Flash Attention** 优化通过分块计算减少了对 HBM 的访问，将注意力的内存复杂度从 $$O(n^2)$$ 降低到 $$O(n)$$

### 面试中的实战建议
- 面试中最常被要求从零实现的操作：softmax、注意力、batch norm、cosine similarity
- 数值稳定性是关键考点：softmax 减最大值、log-sum-exp 技巧
- 广播规则必须熟练 -- 维度不匹配是最常见的运行时错误来源
- einsum 的符号表示法简洁强大，面试中提到会加分
"""

EXPANSIONS[60] = r"""

## ML Application Context
从零实现 ML 算法是面试中区分候选人水平的关键环节：

### 面试深度追问方向
面试官在你完成基本实现后，通常会沿以下方向追问：
- **正则化**："如何添加 L1/L2 正则化？" -- 在损失函数中添加惩罚项，相应修改梯度
- **Mini-batch**："如何将批量梯度下降改为 mini-batch？" -- 每次迭代随机采样一个子集计算梯度
- **早停 (Early Stopping)**："如何决定何时停止训练？" -- 监控验证集损失，连续若干轮不下降时停止
- **特征缩放**："为什么需要标准化特征？" -- 梯度下降对特征尺度敏感，未缩放的特征导致收敛慢
- **初始化**："权重初始化为什么重要？" -- 影响梯度的流动，错误的初始化导致梯度消失/爆炸

### K-Means++ 初始化详解
标准 K-Means 使用随机初始化，容易收敛到局部最优。**K-Means++ 初始化** 通过以下步骤改善：
1. 随机选择第一个质心
2. 对于每个后续质心，以与最近已选质心的距离的平方成正比的概率选择
3. 这保证了初始质心之间的良好分散性
"""

EXPANSIONS[62] = r"""

## ML Application Context
采样算法在 ML 中有广泛的应用：

### Mini-batch SGD 中的数据采样
每个训练迭代从数据集中均匀随机采样一个 mini-batch，这是最基本的采样应用。高级变体包括：
- **Stratified Sampling（分层采样）**：确保每个 mini-batch 中各类别的比例与总体一致
- **Curriculum Learning（课程学习）**：根据样本难度进行非均匀采样，先学简单后学难
- **Hard Negative Mining（困难负样本挖掘）**：优先采样模型预测错误的负样本

### Word2Vec 中的 Negative Sampling
**Negative Sampling（负采样）** 是加权采样的直接应用：
- 将 softmax 近似为多个二分类问题
- 负样本按词频的 3/4 次方进行加权采样
- 这大幅减少了训练中 softmax 的计算开销

### 多臂老虎机中的 Thompson Sampling
**Thompson Sampling** 从每个臂的后验分布中采样一个值，然后选择采样值最高的臂：
- 自然地平衡了探索与利用（exploration vs exploitation）
- 在推荐系统和在线广告中广泛使用

### 面试策略提示
- 蓄水池采样的证明是面试高频问题 -- 通过归纳法证明每个元素被选中的概率相等
- Fisher-Yates 洗牌的正确性依赖于"每个位置与后续随机位置交换" -- 错误的变体（如与任意位置交换）不保证均匀性
- 重要性采样的主要风险是高方差 -- 当提议分布与目标分布差异大时，少数样本的权重会非常大
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.text_factory = str
    cur = conn.cursor()

    for node_id, extra_content in EXPANSIONS.items():
        # Read current content
        cur.execute("SELECT description FROM framework_nodes WHERE id=?", (node_id,))
        row = cur.fetchone()
        current = row[0] if row else ""

        # Append expansion
        new_content = current + extra_content
        cur.execute("UPDATE framework_nodes SET description=? WHERE id=?",
                    (new_content, node_id))
        print(f"Node {node_id}: expanded from {len(current)} to {len(new_content)} chars")

    conn.commit()

    # Final verification
    print("\n=== FINAL VERIFICATION ===")
    all_ok = True
    for node_id in range(44, 64):
        cur.execute("SELECT description FROM framework_nodes WHERE id=?", (node_id,))
        row = cur.fetchone()
        desc = row[0] if row else ""
        desc_len = len(desc)

        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', desc))

        code_blocks = re.findall(r'```[\s\S]*?```', desc)
        formula_in_code = False
        for block in code_blocks:
            if '$$' in block:
                formula_in_code = True

        min_size = 4000
        size_ok = desc_len >= min_size

        status = "OK" if (has_chinese and not formula_in_code and size_ok) else "FAIL"
        if status == "FAIL":
            all_ok = False
        issues = []
        if not has_chinese:
            issues.append("no Chinese")
        if formula_in_code:
            issues.append("formula in code block")
        if not size_ok:
            issues.append(f"too short ({desc_len} < {min_size})")

        issue_str = f" [{', '.join(issues)}]" if issues else ""
        print(f"Node {node_id}: {status} ({desc_len} chars){issue_str}")

    conn.close()
    print(f"\nOverall: {'ALL PASSED' if all_ok else 'SOME FAILED'}")


if __name__ == "__main__":
    main()
