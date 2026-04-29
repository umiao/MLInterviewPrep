"""Strengthen id=33 'Uber BPS Design & Architecture Prep' with 10 audit-discovered gaps.

T-P1-631 ([UBER-VO-4]): Adds delta-only paragraphs covering the 10 search/rec
strengthening keywords identified in the T-P0-628 audit -- training-serving
skew, graceful degradation, hard filter vs soft feature, two-tower / MMoE /
DIN, H3 vs geohash, position bias, online learning vs batch retraining,
off-policy evaluation, cluster-randomized A/B, three-time-scale architecture.

Anchor stability invariant (LOCKED): MUST NOT modify any existing H1/H2/H3
heading TEXT. New content lives under brand-new H3 subsections (5.6 - 5.9)
inserted before '## 6. Common D&A Follow-up Questions'. This keeps the
``db://33#section-5-1-driver-maps`` style anchor links from T-P0-632 stable.

Idempotent via sentinel HTML comment markers ``<!-- T-P1-631:STRENGTHEN BEGIN/END -->``.
Re-running with unchanged block content yields content_hash unchanged.

Source TXT line ranges cited in HTML comments under each subsection for
traceability back to the audit-input txt files.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "mle_prep.db"

COMPANY_ID = 5  # Uber
TARGET_DOC_TITLE = "Uber BPS Design & Architecture Prep"
SENTINEL_KEY = "STRENGTHEN"


def compute_hash(content: str) -> str:
    """SHA-256 over UTF-8 bytes -- used as the idempotency key."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def render_strengthen_block() -> str:
    """Four new H3 subsections (5.6 - 5.9) covering the 10 keyword gaps.

    Each sub-block leads with the keyword bolded so regex audit matches both
    the canonical keyword phrase and the deeper trade-off discussion.
    """
    return (
        "### 5.6 训练-服务一致性 (Training-Serving Skew 三层防御)\n"
        "\n"
        "<!-- source: audit_uber_search_rec_gap.txt L1-L48 (T-P0-628) -->\n"
        "\n"
        "**Training-serving skew (训练-服务特征分布不一致)** 是搜索/推荐生产系统最常见、"
        "也最隐蔽的故障类别. 离线 AUC 漂亮上线却看不到效果, 多半是这个问题. "
        "Uber 的 Michelangelo 平台围绕此提供了三层防御:\n"
        "\n"
        "1. **Feature Snapshot at Serving Time (服务时特征快照)**: 模型推断时, 把"
        "全部特征值连同 prediction 一起异步落盘到 Kafka -> Hive. 训练数据"
        "直接读快照, 而不是 join 历史维度表. 这样从根本上消除了特征语义/取值范围"
        "在训练-服务之间漂移的可能.\n"
        "2. **Feature Store (Michelangelo Palette)**: 单一 source-of-truth 的"
        "特征定义+计算+取数库. 离线 batch + 在线 low-latency lookup 共享同一份"
        "特征 spec, 由同一份代码生成. 避免了\"一个特征两份实现\"的经典反模式.\n"
        "3. **Feature Monitoring (KL/PSI 监控)**: 对每个 production 特征"
        "持续计算分布漂移指标 -- **KL divergence (相对熵)** 或 **PSI (Population "
        "Stability Index, 分布稳定指数)**. PSI > 0.25 触发告警, 超过 0.5 自动"
        "回滚或触发再训练. 既能抓住上游数据 schema 变更, 也能抓住用户分布的"
        "缓慢漂移.\n"
        "\n"
        "**Trade-off**: 三层防御都不便宜. Snapshot 让训练数据存储 ~3x 膨胀; "
        "Feature Store 增加一次 RPC; Monitoring 需要额外计算资源. Uber 的判断是: "
        "搜索/推荐排序模型每个百分点的 AUC 都直接换算成营收, 三层防御的工程成本"
        "在 ROI 上是显然划算的.\n"
        "\n"
        "### 5.7 排序模型核心栈 (Two-tower / MMoE / DIN)\n"
        "\n"
        "<!-- source: audit_uber_search_rec_gap.txt L52-L138 (T-P0-628) -->\n"
        "\n"
        "工业界搜索/推荐排序的事实标准是\"召回-粗排-精排-重排\"漏斗. "
        "Staff 候选必须能讲清楚每一阶段的 SOTA 模型选型与权衡:\n"
        "\n"
        "**Two-tower model (双塔模型, 召回阶段)**: User tower + Item tower 各自"
        "独立编码, 最后用点积/余弦计算相似度. 优势: Item embedding 可全量预计算"
        "并存入 ANN 索引 (FAISS / ScaNN), 在线只过 User tower + ANN 查询, P99 < 5ms. "
        "代价: User-Item 交叉特征只能在最后一层交互, 表达力弱于 cross-network. "
        "因此 two-tower 用于召回, 不用于精排.\n"
        "\n"
        "**MMoE (Multi-gate Mixture-of-Experts, 多门控混合专家, 多任务排序)**: "
        "每个任务 (CTR / CVR / Watch-time / Bookmark) 有独立的 gate 网络, "
        "对共享的 expert 池进行加权融合. 相比 shared-bottom 多任务架构, MMoE 在"
        "任务相关性低时能避免负迁移; 相比每任务一个独立模型, 又能共享底层表征. "
        "Uber Eats 用 MMoE 同时建模点击/下单/评分.\n"
        "\n"
        "**DIN (Deep Interest Network, 深度兴趣网络, 注意力建模历史行为)**: "
        "针对 candidate item, 对用户历史行为序列做 target-attention -- "
        "与候选商品相关的历史行为权重高, 不相关的权重接近零. 解决了\"用户买过"
        "尿布也买过相机, 平均池化后两个兴趣相互稀释\"的问题. 阿里淘宝原创, "
        "已成为推荐系统标配. 进阶版 DIEN 进一步建模兴趣演化的时序结构.\n"
        "\n"
        "**Trade-off (整体栈选型)**: Two-tower + MMoE + DIN 构成\"召回侧高吞吐 "
        "+ 排序侧多目标 + 用户兴趣精细建模\"的现代栈. 但每一项都引入工程复杂度: "
        "Two-tower 需要 ANN 基础设施; MMoE 需要多任务标签同时可得; DIN 需要"
        "用户行为序列存储. 早期阶段可只上 Two-tower 召回 + LR 精排, 后续逐步迭代.\n"
        "\n"
        "### 5.8 实验评估 (Position Bias / Off-Policy / Cluster A/B / Online vs Batch)\n"
        "\n"
        "<!-- source: audit_uber_search_rec_gap.txt L142-L240 (T-P0-628) -->\n"
        "\n"
        "**Position bias (位置偏差)** 是搜索/推荐离线训练的头号陷阱. 用户点击"
        "排第 1 位的结果不一定因为它最相关, 而可能仅因为它在第 1 位. 直接用"
        "点击日志训练 CTR 模型, 模型会学到\"把任何东西放在第 1 位都能拿点击\". "
        "经典缓解方案: Google 2019 paper 提出的 **shallow-tower trick** -- 训练时"
        "把 position 作为特征喂入一个轻量子网络, 服务时把 position 特征置零, "
        "等价于把模型 debias 后的部分留下来打分. 另一条路是 **IPS "
        "(Inverse Propensity Score, 逆倾向加权)**: 对每条样本按 1/P(被展示在该位置) "
        "加权, 数学上等价于反事实期望.\n"
        "\n"
        "**Off-policy evaluation (离线策略评估)**: 新策略上线前, 用旧策略收集的"
        "日志数据估计新策略的指标. 朴素方法 IPS 在 propensity 接近 0 时方差爆炸; "
        "工业界常用 **DR estimator (Doubly Robust, 双重稳健估计)** -- 用一个"
        "回归模型 m(x) 估计 reward, 然后 DR = m(x) + IPS * (r - m(x)). 只要 m 或"
        "倾向估计有一个准, DR 就无偏. Uber 用 DR 做 marketplace 策略 (派单/定价) "
        "的 offline-only 评估, 减少需要上线 A/B 的策略数量.\n"
        "\n"
        "**Cluster-randomized A/B testing (按聚类随机化的对照实验)**: 在"
        "marketplace (Rides / Eats / Marketplace 整体) 场景下, 标准的"
        "user-level A/B 不成立, 因为 treatment 用户的行为会通过供给侧"
        "(司机被占用, 餐厅产能被占用) 影响 control 用户 -- 这就是 **interference "
        "(实验组互相干扰)**. 解决方案: 按地理 cell (H3) 或时间窗口 cluster "
        "随机化, 让 cluster 内全部用户同处一个 arm, cluster 之间相互独立. "
        "代价: 单位实验功效降低, 需要更长 (4-8 周) 的实验时长达到显著性.\n"
        "\n"
        "**Online learning vs Batch retraining (在线学习 vs 批量再训练)**: "
        "Batch 再训练 (每天/每周全量训练一次) 是默认方案 -- 简单稳定可回滚, "
        "但对热点事件 / 突发流行的反应延迟天级. **Online learning (在线学习)** "
        "用流式样本以小步长更新模型, 反应分钟级, 但容易被噪声/对抗样本污染, "
        "且回滚困难 (没有 well-defined snapshot). Uber 在 Eats 推荐用混合架构: "
        "底层 embedding 与多任务塔每天 batch 重训, 顶层 ranker 头部用 online "
        "学习实时跟新热点.\n"
        "\n"
        "### 5.9 系统韧性与时尺度架构 (Graceful Degradation / Three-Time-Scale / Hard Filter / H3)\n"
        "\n"
        "<!-- source: audit_uber_search_rec_gap.txt L244-L340 (T-P0-628) -->\n"
        "\n"
        "**Graceful degradation (优雅降级)**: 生产搜索/推荐系统的下游依赖 "
        "(特征服务 / 模型服务 / 召回索引) 任一抖动都不应该让用户看到空结果. "
        "Uber 的标准做法: (a) 每一层 RPC 设硬 timeout (~10ms 召回 / ~30ms 排序); "
        "(b) 超时走 fallback (e.g. 个性化召回失败 -> 退回热门召回); "
        "(c) 把\"is-fallback\"作为一个 boolean 特征喂给上层, 让排序层知道当前"
        "结果是降级版本, 可以采用更保守的 ranking; (d) 最终兜底是预计算的"
        "全局 popularity 列表 -- 永远不会返回空.\n"
        "\n"
        "**Hard filter vs Soft feature (硬过滤 vs 软特征)**: 物品的可用性/新鲜度"
        "约束有两种处理路径. **Hard filter** (硬过滤): 在召回阶段直接过滤掉"
        "缺货/过期 item, 后续打分排序看不到它们. 优势: 绝对不会把不可买的东西"
        "推到用户面前 (避免 dead-click); 劣势: 短期不可用 (e.g. 餐厅打烊 1h) "
        "也被过滤, 缺乏个性化弹性. **Soft feature** (软特征): 把可用性/新鲜度"
        "作为特征喂入排序模型, 让模型学习权衡. 工业界常见: hard filter 用于"
        "强约束 (永久缺货/合规黑名单), soft feature 用于弹性约束 (临时打烊/"
        "库存紧张). Uber Eats 餐厅推荐两者结合.\n"
        "\n"
        "**Three-time-scale architecture (三时尺度架构: Offline / Near-line / Online)**: "
        "现代搜索/推荐系统是三个时间尺度的组合. **Offline** (离线, 小时-天级): "
        "特征工程, 模型训练, 全量 embedding 重计算. **Near-line** (近线, 秒-分钟级): "
        "Streaming 计算用户实时 session 特征 (最近点击的 K 件), Kafka -> Flink -> "
        "online feature store. **Online** (在线, 毫秒级): 模型推断, ANN 召回, "
        "ranking. 三层都要在 latency / freshness / cost 之间权衡: offline 最便宜"
        "但最旧, online 最新但最贵.\n"
        "\n"
        "**H3 vs geohash (地理空间索引深化, 补充 §5.1)**: "
        "三个核心差异决定了 Uber 选择 **H3 hexagonal grid (六边形网格)** 而非"
        "geohash: (1) **邻接均匀**: 六边形每个 cell 有且仅有 6 个等距邻居, "
        "geohash 的方块在边和角的邻居距离不一致, 在拼接\"附近 cell\"时引入"
        "数学上的不对称; (2) **面积均匀**: H3 每个 resolution 下的 cell 面积"
        "差异 < 2x, geohash 在高纬地区面积明显缩小, 极地附近退化严重; "
        "(3) **多分辨率**: H3 16 个 resolution 层级 (从全球 ~4km^2 到 ~1m^2) "
        "之间是确定性父子关系, 适合多尺度聚合. 综合起来 H3 在 Uber 的"
        "supply/demand 热力图, 派单匹配, ETA 估算等场景下是更好的选择.\n"
        "\n"
        "---\n"
    )


def upsert_block(content: str, key: str, body: str, anchor_pattern: str,
                 mode: str) -> str:
    """Idempotent insert-or-replace of a sentinel-bracketed block.

    If sentinel pair exists, replace its body. Otherwise locate the anchor
    regex (first match) and inject the block ``mode``-relative to it.
    ``mode`` is one of ``"before"`` or ``"after"``.
    """
    begin = f"<!-- T-P1-631:{key} BEGIN -->"
    end = f"<!-- T-P1-631:{key} END -->"
    new_block = f"{begin}\n{body}{end}\n"

    sentinel_re = re.compile(
        re.escape(begin) + r".*?" + re.escape(end) + r"\n?",
        re.DOTALL,
    )
    if sentinel_re.search(content):
        return sentinel_re.sub(new_block, content, count=1)

    m = re.search(anchor_pattern, content)
    if not m:
        raise SystemExit(
            f"[ERROR] anchor pattern {anchor_pattern!r} not found for key {key!r}"
        )
    if mode == "before":
        return content[: m.start()] + new_block + "\n" + content[m.start():]
    if mode == "after":
        return content[: m.end()] + "\n" + new_block + content[m.end():]
    raise SystemExit(f"[ERROR] unknown mode {mode!r} for key {key!r}")


def patch_content(original: str) -> str:
    """Insert the strengthen block before '## 6. Common D&A Follow-up Questions'."""
    return upsert_block(
        original,
        key=SENTINEL_KEY,
        body=render_strengthen_block(),
        anchor_pattern=r"## 6\. Common D&A Follow-up Questions",
        mode="before",
    )


def main() -> int:
    """Read id=33, patch via sentinel UPSERT, write back if changed."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, content, content_hash FROM company_documents "
        "WHERE company_id = ? AND title = ?",
        (COMPANY_ID, TARGET_DOC_TITLE),
    )
    row = cursor.fetchone()
    if row is None:
        raise SystemExit(
            f"[ERROR] target doc not found: company_id={COMPANY_ID} "
            f"title={TARGET_DOC_TITLE!r}"
        )
    doc_id, original, old_hash = row

    new_content = patch_content(original)
    new_hash = compute_hash(new_content)

    if new_hash == old_hash:
        print(f"[NOOP]   doc_id={doc_id} content_hash unchanged "
              f"({new_hash[:12]}) -- idempotent re-run")
        conn.close()
        return 0

    cursor.execute(
        "UPDATE company_documents SET "
        "content = ?, content_hash = ?, updated_at = datetime('now') "
        "WHERE id = ?",
        (new_content, new_hash, doc_id),
    )
    conn.commit()
    print(f"[UPDATE] doc_id={doc_id} chars={len(new_content)} "
          f"old={old_hash[:12] if old_hash else 'NULL'} new={new_hash[:12]}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
