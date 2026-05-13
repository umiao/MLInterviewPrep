# Source 05 — Bias Tower / Train-Serve Skew / Shadow Feature Logging 深版

**Provenance**: Verbatim from user-authored Discord message 1503874418529669201
(2026-05-12, channel #ml-interview-prep). 8-section thinking framework on
排序模型 debias (popularity / position / selection bias 的工业级解法), 与
特征训练/服务一致性 (train-serve skew 与 shadow feature logging) 的耦合.

**Fusion / 引用关系**:

- 本文件是 fr-node `meta-prep/system-design-must-knows/popularity-bias-debiasing`
  (`framework_nodes.id=266`) 的 **canonical 深版 source-of-truth**.
- T-P0-853 (sd://meta-top3-comments-golden, Top-3 Comments Golden Answer)
  已经把本文件的 **简版** 切片嵌进 system_designs row 的 3 列:
  - `architecture` 末尾: Bias Tower 简版 3-句 digest (节一+二+三 浓缩) + anchor
    sentence `深入见 fr-node meta-prep/system-design-must-knows/popularity-bias-debiasing`
  - `production_constraints` 末尾: Shadow Logging + Train-Serve Skew 简版
    (节五+六 4-来源 + 2-件套 核心句) + 同样 anchor sentence
  - `cheat_sheet` 末尾: Design Doc 强调话术 4 句金句 (节八 verbatim)
- T-P0-855..858 (cd94..cd97 drawer retrofits) 把 source_04 加进 4 个 Meta
  company_document drawers 的 fr-node link block; 它们也会捎带 anchor 到
  本 fr-node, 由 reader 进一步 drill-down 深版.
- 因此本 source_05 文件 + seeded fr-node 266 description = 整条 anchor chain
  的 **terminal** (终点深读), 链头是 sd-card 简版, 链中是 cd-drawer 简版, 链尾是
  本节 8 章深版.

**Idempotent rebuild**: `python scripts/seed_bias_tower_debiasing_node.py`
sentinel UPSERT by `framework_nodes.path = 'meta-prep/system-design-must-knows/popularity-bias-debiasing'`.
重跑无副作用; 首次跑 description 从 710B (短版, 由 `seed_meta_prep_sd_must_knows.py` 写入)
更新为 ~6.5KB (本深版 8-章). 之后所有再跑 = SKIP.

---

## 一、Shallow Bias Tower (YouTube 2019)

**架构**

- 双塔加性结构: `logit = main_tower(content, user, ctx) + bias_tower(bias_features)`
- 主塔深 (MMoE)，偏差塔浅 (1-2 层 / 线性)
- 偏差塔输入只放 bias 类特征: position、device、slot type、isAds 等

**为什么浅**

- 容量瓶颈 -> 只吸收加性偏置，吃不下 content 信号
- 防止 position 抢梯度，逼主塔学真实相关性

**核心归纳偏置**

- 加性可分: relevance + bias，提供可识别性
- 主塔输出天然独立于 position，干净的反事实表达

---

## 二、Mask-at-Inference

- 训练: bias tower 喂真实 position
- 推理: 屏蔽 bias 项
- 两种等价实现:
  - 把 bias term 整个置 0 (最干净)
  - position 设为固定参考值 (如 1)，bias term 变常数，不影响排序
- 配套训练技巧: 训练时对 position 做 feature dropout，让模型对缺失鲁棒

---

## 三、Bias Tower vs. 直接当 Feature

| 维度       | Bias Tower             | 拼进主塔                    |
|------------|------------------------|-----------------------------|
| 分解结构   | 加性可分               | content x position 纠缠     |
| 推理 mask  | 良定义                 | 分布外、表示被污染          |
| 梯度竞争   | 主塔学相关性           | position 抢信号             |
| 可识别性   | 强先验                 | 解不唯一                    |

理论等价的前提 (即用工程隐式重建 bias tower): position 随机分布 + dropout + 正则 +
大容量。做齐这些 = 手工搭 bias tower。

---

## 四、isAds 的判断标准

- 想要 反事实「若为 organic 的相关性」-> 当 bias 处理
- 想要 事实预测 P(click | 当前真实身份) -> 当 context feature

判断点: ads 与 organic 是否只是 logit 加性偏移 (-> bias) 还是有真 interaction (-> feature)。

---

## 五、Train/Serve Skew

**常见来源**

- 训练/服务代码路径不一致 (Python vs C++)
- Time travel: 训练特征泄漏未来
- 数据源 / 默认值 / null 处理漂移
- bias 特征训练用真实值、serving 用 mask，分布不匹配

后果: 离线指标好、线上掉点

---

## 六、Shadow Feature Logging

做法: serving 时把模型实际看到的 feature_vector 原样落盘，事后 join label 作为训练样本。

**保证**

- 训练/服务特征 100% 一致 (同一份代码算的)
- Point-in-time 正确，无未来泄漏
- bias 特征 (position / device) 忠实记录，bias tower 训练分布对齐

**工程要点**

- 采样要无偏，避免引入新 bias
- 异步队列 (Kafka / Pub-Sub)，不阻塞 serving
- 流式 label joiner (Flink / Beam) 按 request_id 关联行为
- 持续监控 logged 特征分布 vs serving 实时分布 -> 主动告警 skew

---

## 七、整体设计内在逻辑链

- 隐式反馈 -> 选择偏差 -> 需 debias
- 模型层: shallow bias tower 剥离 position bias
- 推理层: mask-at-inference 实现反事实预测
- 数据层: shadow logging 消除 train/serve skew，保证 1-3 真正生效

口诀: **架构纠偏 (bias tower) + 推理纠偏 (mask) + 数据纠偏 (shadow log)，三层缺一不可。**

---

## 八、Design Doc 强调话术

1. 「采用加性 shallow bias tower，结构性强制 relevance / bias 分解」
2. 「Mask-at-inference 提供干净的反事实排序信号」
3. 「Shadow feature logging 保证 bias 特征训练/服务分布一致，避免 debias 机制被 skew 破坏」
4. 「离线 AUC 可能持平甚至微跌，业务指标 (多样性 / 留存 / 新内容曝光) 为真实评估目标」
