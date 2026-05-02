"""Backfill cheat_sheet column for the 7 eBay system designs (id=1..7).

Targets (display_order 1-7, all currently empty on cheat_sheet):
  id=1 module-arbitration
  id=2 llm-orchestration
  id=3 pbe-pipeline
  id=4 ranking-allocation
  id=5 database-comparison
  id=6 distributed-task-queue
  id=7 vibe-code-engineering-patterns

(id=8 ml-system-design-patterns already DONE via 2026-05-01 extraction.)

Idempotent: rewrites only the cheat_sheet column for the 7 target slugs;
all other columns are left untouched.

Style (per project memory feedback_content_style_cn_en + reference rows):
  - Markdown table with 8-12 rows.
  - Columns: 'Item' / 'Number / Decision'.
  - Chinese narration + English technical-term expansion on first use.
  - 250-700 chars (compact flash card).
  - Numbers / decisions sourced from each row's existing overview /
    production_constraints / tradeoffs columns -- no new content invented.

Part of T-P2-683 (batch 1 of ~3-4); subsequent batches handle the 19
interview SDs and 5 old Pinterest SDs.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.system_design import SystemDesign  # noqa: E402

CHEAT_SHEETS: dict[str, str] = {
    "module-arbitration": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 规模 | 50K QPS 峰值, 5 亿曝光/天, 2000 万点击/天 |
| 模块注册表 | ~200 模块, 每市场 ~50 活跃 |
| 候选模块/查询 | 15-30（Stage 1 裁剪）, K=48 槽位 |
| 探索策略 | **TS (Thompson Sampling)** > UCB（非平稳奖励） |
| 优化范围 | 整页 **LP (Linear Programming)**（贪心忽略跨模块交互） |
| Stage 1 延迟 | <20ms（选择 + 异步内容获取 50ms timeout） |
| Stage 2 延迟 | <10ms（LP 求解 ~5ms + 组合） |
| 端到端 P99 | <150ms 总 SRP, 仲裁占 ~30ms |
| 质量门控 | 混合（硬阈值挡最差 + 软惩罚保探索） |
| 冷启动 | 上下文 bandits + 模块类型相似性先验 |
| 业务影响 | +4% 页面级 GMV, 12 -> 200+ 模块类型 |
""",

    "llm-orchestration": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| LLM 角色 | 代理模式（Artifact Generator）, 不直接检索 |
| 模型 | 微调 7B, **INT8** 量化（~7GB VRAM/GPU） |
| GPU 集群 | 4 个 A10 Pod, batch=16, 目标 70% 利用率 |
| 吞吐 | ~8K 推理/秒, 成本 ~$8K/月（vs GPT-4 $50K/月） |
| LLM 延迟 | P50 35ms, P99 65ms, timeout 80ms |
| 端到端搜索 | P99 200ms（含 LLM）vs 80ms（不含, +40ms） |
| 回退率 | ~2%（超时或低置信度回退纯 Cassini） |
| 意图准确率 | 92%（vs GPT-4 96%）, 1 万人工标注/月 |
| 格式错误率 | 0.01%（Outlines 约束解码）vs 3.2% 无约束 |
| 训练数据 | 5000 万查询-制品-参与度三元组, 2 周窗口 |
| 蒸馏周期 | 全量微调季度, LoRA 适配月度 |
""",

    "pbe-pipeline": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 核心问题 | Click 仅 2-5% **CTR**, 95% 曝光无信号 + 位置偏差 |
| 信号升级 | Viewport 曝光 + 停留时长 + 交互深度 |
| 曝光量 | 5 亿/天, 20 亿视口事件 |
| Stream 1 | Sojourner ~200K 事件/秒 峰值 |
| Stream 2 | Kafka ~50K 特征更新/秒 |
| Spark Join | 5 分钟微批, 端到端 5 分钟（离线训练可接受） |
| 归因批量 | 500 节点 Spark, ~4 小时/天 |
| 训练数据 | ~2TB/天快照, 30 天保留 |
| 客户端开销 | sendBeacon 异步 0ms, IntersectionObserver <5ms/页 |
| **IPW (Inverse Propensity Weighting)** | 月度位置随机化实验, ~0.1% 查询参与 |
| 模型重训 | 主排序日, 实验模型周, 14 天归因窗口 |
""",

    "ranking-allocation": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 范式 | 排序 = 分配 K=48 槽位约束优化（非逐点评分） |
| QPS | 峰值 ~50K（与 Module Arbitration 共享 Cassini） |
| 候选集 | QN 检索后 50-200 / 查询 |
| 重排延迟 | <3ms（贪心带约束惩罚, $O(K \\cdot N)$ ~9.6K 次） |
| **MUS (Model-Unified Score)** 校准 | <1ms, 每模型 $\\mu, \\sigma$ 每小时刷新 |
| **ORC** 总预算 | 端到端 <15ms |
| 硬约束 | 卖家上限 3 件/查询 + 类目下限 + 品牌安全 + 法规 |
| 软约束 | 4 维（卖家/类目/价格分桶/状况） + 长尾卖家配额 |
| 分段预算 | ~2000 段（意图 × 用户层级）, 每晚 Spark 调整 |
| 闭环收敛 | 学习率 $\\eta=0.1$, 截断 $[b^{\\min}, b^{\\max}]$, 3-7 天稳定 |
| 业务影响 | +3.5% 页面购买率, +2.8% 会话继续率, 推广 3 个垂类 |
""",

    "database-comparison": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 选型框架 | 约束满足: 数据模型 + 一致性 + 规模 + 延迟 + 运维 + 成本 |
| **AP (Availability + Partition)** 系统 | Cassandra / ScyllaDB / DynamoDB |
| **CP (Consistency + Partition)** 系统 | HBase / CockroachDB / TiDB |
| 混合 | MongoDB（可配置一致性, 文档模型） |
| Cassandra 延迟 | p50 1-2ms 读, JVM **GC** 致 p99.9 100ms+ 飙升 |
| ScyllaDB | C++ shard-per-core, 无 GC, p99 2-5ms 读 |
| DynamoDB | 全托管, **DAX** 缓存读 <1ms, 热分区是首要陷阱 |
| HBase 痛点 | ZooKeeper + HDFS + Region 分裂, 高运维成本 |
| 共识写延迟 | CockroachDB / TiDB Raft 写 p99 15-40ms |
| 成本盈亏点 | DynamoDB <100 万请求/天, 自建 Cassandra >1000 万/天 |
| 自建规模 | 最少 3-9 节点（RF=3 多机架）, $5K-$50K/月 |
""",

    "distributed-task-queue": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 核心契约 | Producer / Broker / Worker / Result Backend 四角色解耦 |
| 投递语义 | At-least-once + 幂等 Consumer = Effectively-once |
| Redis 吞吐 | 100K-500K msg/sec 内存型, RDB 丢 60s, AOF-everysec 丢 1s |
| RabbitMQ | 持久化 ~5K-10K msg/sec, quorum 队列 Raft 共识 |
| SQS Standard | ~3K/API call, 批 10/call 多调用方实际无限 |
| SQS FIFO | 300 msg/sec/group, 批 + 多 group 可达 3K |
| Kafka | 100K-2M msg/sec/分区, **acks=all + ISR** 复制 |
| 端到端延迟 | Redis 1-5ms, Kafka 5-20ms, SQS 50-200ms |
| 幂等键 | task_id + 状态机表（pending/running/done） |
| 重试策略 | 指数退避 + jitter + 最大次数后 **DLQ (Dead Letter Queue)** |
| 监控告警 | 队列深度 >10K 警告 / >100K 严重, DLQ >0 即告警 |
""",

    "vibe-code-engineering-patterns": """\
**速查表 (Cheat Sheet) — 30s flash review**

| Item | Number / Decision |
|---|---|
| 范式 | 约束驱动设计（平台限制 -> 架构优势, 而非对抗） |
| Fixture 集 | 5-10 页/数据源, 选择器覆盖率 >=90% |
| OP 长度门禁 | 50-200 字符（过滤短 OP + 长垃圾） |
| 字段精确率 | F1 >=95%, 标题 100% Precision（错比缺更糟） |
| 零结果容忍 | 0（静默空提取 = 数据质量退化首因） |
| 幂等性 | DB 唯一索引 (seed_id, post_url), 重跑不重复 |
| 爬取 QPS | 1-5/站点, --limit 50-200, flock 防重叠 |
| Cron 会话作用域 | 7 天过期, **YAML** 配置是持久 SoT |
| 密钥 hook | Write-time <10ms, Pre-commit <500ms, Cron 兜底每小时 |
| 检测召回 | >=99% 召回率, 误报 <=2%（超 2% 开发者禁用 hook） |
| AI 层 | 3s timeout, **Fail-open** 放行 + 记录, 不阻断 |
""",
}

TARGET_SLUGS = list(CHEAT_SHEETS.keys())


def main() -> None:
    """UPSERT cheat_sheet for the 7 eBay system designs."""
    init_db()
    db = SessionLocal()
    chinese_pattern = re.compile(r"[一-鿿]")
    failed: list[str] = []
    try:
        for slug in TARGET_SLUGS:
            row = db.query(SystemDesign).filter(SystemDesign.slug == slug).first()
            if row is None:
                print(f"[ERROR] slug not found: {slug}")
                failed.append(slug)
                continue

            new = CHEAT_SHEETS[slug]
            old = row.cheat_sheet or ""
            action = "NOOP" if old == new else ("INSERT" if not old else "UPDATE")
            row.cheat_sheet = new

            char_len = len(new)
            has_cn = bool(chinese_pattern.search(new))
            warn = ""
            if not has_cn:
                warn += " [WARN: no CN chars]"
            if char_len < 250 or char_len > 700:
                warn += f" [WARN: len {char_len} outside 250-700]"

            print(f"[{action}] {slug}: cheat_sheet={char_len} chars{warn}")

        db.commit()
        if failed:
            print(f"[FAIL] {len(failed)} slug(s) not found: {failed}")
            sys.exit(1)
        print(f"[DONE] cheat_sheet patched for {len(TARGET_SLUGS)} eBay SDs.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
