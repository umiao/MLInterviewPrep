"""Seed: T-P0-510 -- Populate id=18 System Design Framework with canonical L5 paradigm.

Writes the L5 (Senior/E5/IC5) ML System Design paradigm as the description of
framework_node id=18 (path='pillar3.design_framework'), which is the meta-reference
every concrete design problem (89-97, 198, future) must link back to.

Safety:
  1. Timestamped .bak snapshot of mle_prep.db before touching the row.
  2. Archives old description (originally NULL) into
     framework_nodes_description_history so the prior state is recoverable.
  3. Idempotent: if the DB row already matches the new description
     (identical SHA-256), exits fast without re-archiving or re-writing.
  4. Post-update structural guards: length in [6500, 8500], starts with
     expected title, contains Appendix A + all 6 stage headings +
     pass-bar checklist + L5-L6 delta.
"""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
NODE_ID = 18
TITLE_GUARD = "# ML System Design Framework"

# Length window: Part A ~5-7K + Part B ~1-1.5K = 6500-8500 target.
# Allow the Appendix A.1 (T-P0-514) suffix to push up to ~12100.
LEN_MIN = 6500
LEN_MAX = 12100

NEW_DESCRIPTION = """# ML System Design Framework (L5 \u901a\u8fc7\u8303\u5f0f)

> \u672c\u6587\u662f Pillar 3 \u6240\u6709\u5177\u4f53\u8bbe\u8ba1\u9898\u7684**\u552f\u4e00\u6e90\u5934 (single source of truth)**\u3002\u6bcf\u9053\u5b50\u9898\uff0889-97 / 198 / \u65b0\u589e\uff09\u5fc5\u987b\u6309\u672b\u5c3e **Appendix A \u00b7 Unified Template Skeleton** \u7684\u9aa8\u67b6\u7ec4\u7ec7\u63cf\u8ff0\u3002

## Prerequisites \u2014 L5 vs L4 \u4e09\u4ef6\u4e8b

L5 \u548c L4 \u7684\u5dee\u5f02\u4e0d\u5728\"\u66f4\u591a\u6280\u672f\u70b9\"\uff0c\u800c\u5728**\u5224\u65ad\u6df1\u5ea6**\u3002\u9762\u8bd5\u5b98\u770b\u4e09\u4ef6\u4e8b\uff1a

1. **Scale awareness (\u89c4\u6a21\u610f\u8bc6)**\uff1a\u6bcf\u4e2a\u67b6\u6784\u51b3\u7b56\u80cc\u540e\u90fd\u80fd\u7ed9\u51fa**\u5177\u4f53\u6570\u5b57** (QPS / storage / latency budget)\uff0c\u800c\u4e0d\u662f\"\u9ad8\u53ef\u7528\"\u3001\"\u53ef\u6269\u5c55\"\u8fd9\u7c7b\u7a7a\u8bdd\u3002
2. **Tradeoff articulation (\u6743\u8861\u660e\u786e\u8868\u8fbe)**\uff1a\u9009\u4e86 A \u4e0d\u9009 B \u65f6\uff0c\u4e3b\u52a8\u8bf4\u51fa B \u7684\u7f3a\u70b9\u548c\u5207\u6362 B \u7684\u89e6\u53d1\u6761\u4ef6\u3002
3. **Failure thinking (\u5931\u6548\u601d\u7ef4)**\uff1a\u81f3\u5c11\u4e3b\u52a8\u63d0\u51fa\u4e00\u4e2a**\u964d\u7ea7\u7b56\u7565** (graceful degradation)\uff0c\u800c\u4e0d\u662f\u7b49\u9762\u8bd5\u5b98\u8ffd\u95ee\u3002

\u4e09\u8005\u7f3a\u4e00\u5c31\u662f L4\uff1b\u4e09\u8005\u5168\u5177\u4e14\u81ea\u7136\u6d41\u9732\uff0c\u662f L5\u3002

## Time Budget \u2014 60 \u5206\u949f\u8282\u594f

| Stage | \u65f6\u957f | \u7d2f\u8ba1 | \u4ea7\u7269 |
|---|---|---|---|
| 1. Requirements Clarification | 5m | 0-5 | \u529f\u80fd\u5217\u8868 + \u5173\u952e\u6570\u5b57 |
| 2. Capacity Estimation | 5m | 5-10 | QPS / Storage / Bandwidth |
| 3. High-Level Architecture | 15m | 10-25 | \u670d\u52a1\u62d3\u6251 + \u6570\u636e\u6d41 + \u5b58\u50a8\u9009\u578b |
| 4. Deep Dive | 25m | 25-50 | 2-3 \u4e2a\u6df1\u6316\u8bdd\u9898 |
| 5. Reliability & Monitoring | 5m | 50-55 | \u5931\u6548\u57df + SLO |
| 6. Summary | 5m | 55-60 | tradeoff \u56de\u6536 + \u672a\u8986\u76d6\u70b9 |

**\u8282\u594f\u4e22\u5931\u4fe1\u53f7** (pace-loss signals)\uff1a10 \u5206\u949f\u65f6\u8fd8\u5728\u95ee\u529f\u80fd \u2192 \u9700\u5f3a\u5236\u622a\u65ad\u8fdb\u5165 Stage 2\uff1b25 \u5206\u949f\u65f6\u67b6\u6784\u8fd8\u6ca1\u753b\u5b8c \u2192 \u653e\u5f03\u67d0\u4e2a\u975e\u6838\u5fc3\u670d\u52a1\uff1bDeep Dive \u5355\u8bdd\u9898\u8d85\u8fc7 15 \u5206\u949f \u2192 \u4e3b\u52a8\u5207\u6362\u3002

## Stage 1: Requirements Clarification (5m)

\u4ea7\u7269 = \u4e09\u4efd\u6e05\u5355\uff1a

- **Functional requirements (\u529f\u80fd\u9700\u6c42)**\uff1a\u7528\u6237\u80fd\u505a\u4ec0\u4e48\u3001\u7cfb\u7edf\u8f93\u51fa\u4ec0\u4e48\u3002
- **Non-functional requirements (\u975e\u529f\u80fd\u9700\u6c42)**\uff1alatency / throughput / availability / consistency \u56db\u8f74\u53ca\u5176\u6570\u5b57\u3002
- **Out-of-scope (\u6392\u9664\u9879)**\uff1a\u660e\u786e\u8bf4\u51fa\u672c\u8f6e\u4e0d\u8bbe\u8ba1\u7684\u90e8\u5206\uff08\u5982 payment / auth\uff09\u3002

**\u5fc5\u95ee\u4e94\u95ee\u8868** (mandatory Qs)\uff1a

| # | Question | \u76ee\u7684 |
|---|---|---|
| 1 | \u7528\u6237\u91cf\u7ea7\uff1fDAU / MAU\uff1f | \u9a71\u52a8 capacity \u7ae0 |
| 2 | \u8bfb\u591a\u5199\u591a\uff1f\u5177\u4f53\u6bd4\u4f8b\uff1f | \u51b3\u5b9a\u7f13\u5b58\u548c\u4e3b\u5e93\u9009\u578b |
| 3 | \u5b9e\u65f6\u6027\u8981\u6c42\uff1f\u79d2\u7ea7\u8fd8\u662f\u5206\u949f\u7ea7\uff1f | \u51b3\u5b9a sync / async\u3001\u662f\u5426\u5f15\u5165\u6d88\u606f\u961f\u5217 |
| 4 | \u4e00\u81f4\u6027\u8981\u6c42\uff1fstrong vs eventual\uff1f | \u51b3\u5b9a\u662f\u5426\u9700 transaction / leader election |
| 5 | \u5730\u57df\u8303\u56f4\uff1f\u5355 region \u8fd8\u662f\u5168\u7403\uff1f | \u51b3\u5b9a\u591a\u6d3b / CDN / \u6570\u636e\u5408\u89c4 |

**Common pit**\uff1a\u5168\u90e8\u95ee\u5b8c\u4e94\u95ee\u624d\u8bf4 \"Let me start designing\" \u2014\u2014 \u9519\u3002\u6b63\u786e\u505a\u6cd5\u662f\u95ee 2-3 \u4e2a\u6700\u5173\u952e\u7684\uff08\u901a\u5e38\u662f Q1/Q2/Q3\uff09\u5c31\u8fdb\u5165\u6d41\u6c34\u8d26\u4f30\u7b97\uff0c\u5269\u4e0b\u7684\u8fb9\u8bbe\u8ba1\u8fb9\u786e\u8ba4\u3002

## Stage 2: Capacity Estimation (5m)

\u56fa\u5b9a\u8ba1\u7b97\u94fe\uff1a

```
DAU \u2192 per-user-ops/day \u2192 QPS (avg & peak) \u2192 Storage/day \u2192 Bandwidth
```

**\u793a\u4f8b\u63a8\u5bfc** (\u4ee5 Rec System \u4e3a\u4f8b)\uff1a

- DAU = 100M\uff0c\u4eba\u5747 50 \u6b21\u63a8\u8350\u8bf7\u6c42/\u5929 \u2192 50 \u00d7 10^8 / 86400 \u2248 **58K QPS avg**\uff0c\u5cf0\u503c 3x \u2248 **175K QPS peak**\u3002
- \u6bcf\u6b21\u8bf7\u6c42 log \u5927\u5c0f 1KB \u2192 \u6bcf\u5929 **5TB** \u65e5\u5fd7\u2192 \u9a71\u52a8\u51b7\u5b58\u5206\u5c42\u3002
- \u6bcf\u6b21\u8bf7\u6c42\u8fd4\u56de 20 \u6761\u5019\u9009\u00d71KB \u2192 peak \u5916\u7f51\u5e26\u5bbd **3.5GB/s** \u2192 \u9a71\u52a8 CDN / edge cache \u9009\u578b\u3002

**\u5173\u952e\u53e5\u5f0f**\uff1a\u6bcf\u7b97\u51fa\u4e00\u4e2a\u6570\u5b57\uff0c\u8981\u660e\u786e\u8bf4\uff1a**\u8fd9\u4e2a\u6570\u5b57\u9a71\u52a8\u4e86\u4e0b\u6e38\u54ea\u4e2a\u67b6\u6784\u51b3\u7b56**\u3002\u7eaf\u7b97\u6570\u4e0d\u7ed1\u5b9a\u51b3\u7b56 = L4\u3002

**\u5bf9\u9f50\u57fa\u51c6** (benchmarks to remember)\uff1a

- HDD seek 10ms / SSD 0.1ms / memory 100ns / network round-trip same-DC 0.5ms, cross-region 150ms\u3002
- MySQL single instance ~10K QPS write, ~30K QPS read; Redis ~100K QPS; Kafka single partition ~10MB/s\u3002

**Pitfalls**\uff1aQPS \u53ea\u7b97\u5747\u503c\u4e0d\u7b97\u5cf0\u503c\uff1b\u5b58\u50a8\u53ea\u7b97\u539f\u6587\u4e0d\u7b97 index / replica\uff1b\u5e26\u5bbd\u53ea\u7b97\u51fa\u4e0d\u7b97\u5165\u3002

## Stage 3: High-Level Architecture (15m) \u2014 PASS/FAIL DIVIDER

**\u4e09\u5c42\u7eaa\u5f8b** (3-layer discipline)\uff1aclient \u2192 gateway/\u7f51\u5173 \u2192 \u540e\u7aef\u670d\u52a1\u5c42 \u2192 \u5b58\u50a8\u5c42\u3002\u6bcf\u5c42\u5206\u522b\u56de\u7b54\uff1a\u8fd9\u5c42\u89e3\u51b3\u4ec0\u4e48 / \u53ef\u7528\u4ec0\u4e48\u7ec4\u4ef6 / \u4e3a\u4ec0\u4e48\u8fd9\u6837\u9009\u3002

**\u670d\u52a1\u62c6\u5206\uff1a\u6309 read/write + SLA \u5207\uff0c\u4e0d\u6309\u6a21\u5757\u5207** (\u8fd9\u662f L5 \u5173\u952e\u7eaa\u5f8b)\u3002\u4f8b\u5982\u6253\u8f66\u7cfb\u7edf\uff1a

| Service | \u8bfb\u5199\u7c7b\u578b | SLA | \u5b58\u50a8 | \u4e3a\u4ec0\u4e48\u72ec\u7acb |
|---|---|---|---|---|
| Location Service | \u9ad8\u5199\u9ad8\u8bfb | 200ms | Redis Geo | QPS \u91cf\u7ea7\u548c\u5b58\u50a8\u72b6\u6001\u4e0d\u540c |
| Matching Service | \u8bfb\u5bc6\u96c6\u578b | 500ms | in-memory + Redis | \u8ba1\u7b97\u5bc6\u96c6 |
| Trip Service | \u5f3a\u4e00\u81f4\u5199 | 1s | MySQL | \u4e8b\u52a1\u6027 |
| Payment | \u5f3a\u4e00\u81f4\u5199 | 2s | MySQL + WAL | \u9700 ACID + \u5ba1\u8ba1 |

**\u5b58\u50a8\u9009\u578b\u8868** (storage selection)\uff1a

| \u9700\u6c42 | \u9009\u578b | \u7406\u7531 |
|---|---|---|
| Key-Value \u9ad8 QPS | Redis / Memcached | in-memory \u5ef6\u8fdf\u4f4e |
| \u7ed3\u6784\u5316 + \u4e8b\u52a1 | MySQL / PostgreSQL | ACID |
| \u5927\u5bb9\u91cf + \u4f4e QPS | HDFS / S3 | \u5355\u4f4d\u5b58\u50a8\u6210\u672c\u4f4e |
| \u5730\u7406\u67e5\u8be2 | Redis Geo / PostGIS | GEOHASH / R-tree \u7d22\u5f15 |
| \u5168\u6587\u68c0\u7d22 | Elasticsearch | \u5012\u6392\u7d22\u5f15 |
| \u65f6\u5e8f / \u65e5\u5fd7 | Kafka + ClickHouse | \u6279\u91cf\u5199\u5165 + \u5217\u5b58 |
| \u5f3a\u4e00\u81f4 + \u5206\u5e03\u5f0f | Spanner / TiDB | Paxos/Raft |

\u8fc7\u4e86\u8fd9\u4e00\u6b65 = \u9762\u8bd5\u8fc7\u534a\uff1b\u8fd9\u4e00\u6b65\u6df7\u4e71 = \u76f4\u63a5 L4 fail\u3002

## Stage 4: Deep Dive (25m) \u2014 RATING DETERMINER

\u9762\u8bd5\u5b98\u901a\u5e38\u4f1a\u6307\u5b9a 2-3 \u4e2a topic\uff1a\u201clet\u2019s go deeper on X\u201d\u3002\u6bcf\u4e2a topic \u7528**5-step \u7ed3\u6784**\uff1a

1. **Essence (\u95ee\u9898\u672c\u8d28)**\uff1a\u4e00\u53e5\u8bdd\u8bb2\u6e05\u6838\u5fc3\u77db\u76fe\u3002
2. **Options (\u9009\u9879\u7a77\u4e3e)**\uff1a\u81f3\u5c11 2-3 \u4e2a\u5019\u9009\u65b9\u6848\u3002
3. **Pick + Why (\u9009\u4e00\u4e2a + \u7406\u7531)**\uff1a\u914d\u5177\u4f53\u6570\u5b57\u53ca tradeoff\u3002
4. **Scale-out (\u6269\u5c55\u5230 10x)**\uff1a10x \u6d41\u91cf\u65f6\u8fd9\u4e2a\u65b9\u6848\u600e\u4e48\u53d8\u3002
5. **Edges (\u8fb9\u754c + \u5931\u6548)**\uff1a\u8fb9\u754c\u6761\u4ef6\u3001\u4e00\u81f4\u6027\u95ee\u9898\u3001\u964d\u7ea7\u65b9\u6848\u3002

**Reusable playbooks** (\u5feb\u901f\u53d6\u7528\u8bdd\u672f)\uff1a

- **CAS (Compare-And-Swap, \u539f\u5b50\u6bd4\u8f83\u4ea4\u6362)**\uff1a\u6d3b\u52a8\u4e0b\u5355\u9632\u91cd / \u9ad8\u5e76\u53d1\u6263\u5e93\u5b58\u3002
- **Geospatial (\u5730\u7406\u7d22\u5f15)**\uff1aGeohash \u6216 H3 \u5206\u683c\uff1b\u9644\u8fd1\u67e5\u8be2\u7528\u5e73\u65b9\u8fd1\u4f3c + \u5345\u7406\u62d2\u7b5b\u3002
- **WebSocket fanout**\uff1a\u957f\u8fde\u63a5 push\uff1b\u5206\u5e03\u5f0f\u4f1a\u8bdd\u5b58\u50a8\u7528 Redis\uff08\u56e0\u4e3a in-memory + \u8de8\u8282\u70b9\u5171\u4eab + \u4e9a\u6beb\u79d2\uff09\uff1b\u6d88\u8d39\u7aef\u964d\u7ea7\u4e3a long-polling\u3002
- **Pub/sub fanout**\uff1a\u5199\u6269\u6563 vs \u8bfb\u6269\u6563\uff1bKafka consumer group\uff1b\u53cc\u5199\u4f4e\u4e00\u81f4\u6027\u8d85\u7ea7\u7528\u6237\u3002
- **Hotspot mitigation (\u70ed\u70b9\u7f13\u89e3)**\uff1a\u672c\u5730\u4e8c\u7ea7\u7f13\u5b58\uff1bkey \u52a0\u540e\u7f00\u6253\u6563\uff1b\u589e\u52a0\u526f\u672c\u7684\u53ea\u8bfb\u526f\u672c\u3002

\u6bcf\u4e2a deep dive **\u5fc5\u987b**\u6709\u4f2a\u4ee3\u7801\u3001SQL\u3001\u6216\u6570\u636e\u7ed3\u6784\u9aa8\u67b6\uff0c\u8ba9\u9762\u8bd5\u5b98\u770b\u5230\u4f60\u4e0d\u505c\u5728\u201c\u53e3\u5934\u8c08\u5175\u201d\u3002

## Stage 5: Reliability & Monitoring (5m)

**\u56db\u5c42\u5931\u6548\u57df** (4-layer failure domain)\uff1a

| Layer | \u5931\u6548\u6837\u4f8b | \u9632\u62a4\u624b\u6bb5 |
|---|---|---|
| Infrastructure | \u673a\u67b6/\u673a\u623f\u65ad\u7535 | \u591a AZ / \u591a region |
| Service | \u5355\u4e2a\u670d\u52a1\u5d29\u6e83 | \u7194\u65ad / \u9650\u6d41 / \u8d85\u65f6 |
| Dependency | \u4e0b\u6e38 API / DB \u538b\u529b | \u7f13\u5b58\u517c\u964d\u7ea7 |
| Data | \u810f\u6570\u636e / \u70ed\u70b9 / \u4e0d\u4e00\u81f4 | idempotency key / \u5bf9\u8d26 |

**\u964d\u7ea7\u8868** (graceful degradation)\uff1a

| \u573a\u666f | \u6b63\u5e38 | \u964d\u7ea7 |
|---|---|---|
| \u63a8\u8350\u6a21\u578b\u8d85\u65f6 | \u4e2a\u6027\u5316 ranking | \u8fd4\u56de\u5168\u5c40\u70ed\u699c |
| \u5730\u7406\u7f13\u5b58\u65ad\u8fde | Redis GEO | \u964d\u7ea7\u4e3a\u5185\u5b58 LRU + \u5bbd\u534a\u5f84\u5019\u9009 |
| \u652f\u4ed8\u7ec4\u4ef6\u5931\u6548 | \u540c\u6b65\u6263\u6b3e | \u6539\u4e3a\u5f02\u6b65 + \u4e8b\u540e\u5bf9\u8d26 |

**SLO \u5fc5\u987b\u540c\u65f6\u542b**\uff1a\u6280\u672f\u6307\u6807 (p50/p95/p99 latency\u3001availability\u3001error rate) **\u548c**\u4e1a\u52a1\u6307\u6807\uff08CTR\u3001GMV\u3001\u76d1\u7ba1\u62a5\u544a\u51c6\u65f6\u7387\uff09\u3002\u7eaf\u6280\u672f\u6307\u6807\u7684 dashboard = L4\u3002

## Stage 6: Summary (5m)

\u6536\u5c3e\u6a21\u677f\uff1a\u201c\u6211\u505a\u7684\u4e09\u4e2a\u6700\u5927\u6743\u8861\u662f X\u3001Y\u3001Z\uff1b\u5982\u679c\u518d\u7ed9\u6211 30 \u5206\u949f\uff0c\u6211\u4f1a\u6DF1\u6316 A \u548c B\uff1b\u8fd9\u4e2a\u8bbe\u8ba1\u7684\u663e\u8457\u7f3a\u70b9\u662f C\uff0c\u7f13\u89e3\u8def\u5f84\u662f D\u3002\u201d

\u4e3b\u52a8\u70b9\u51fa\u7f3a\u70b9 \u2192 \u9762\u8bd5\u5b98\u77e5\u9053\u4f60\u6709\u81ea\u6211\u610f\u8bc6 \u2192 \u4e0d\u4f1a\u518d\u6263\u6761\u3002

## L5 Pass-Bar Checklist (7 \u7c7b\u00d7~35 \u9879)

1. **Requirements**\uff1a\u529f\u80fd/\u975e\u529f\u80fd/\u6392\u9664\u9879\u5404\u6709\u3001\u5173\u952e\u6570\u5b57\u786e\u8ba4\u3001out-of-scope \u4e3b\u52a8\u58f0\u660e\u3002
2. **Capacity**\uff1aQPS avg + peak\u3001\u5b58\u50a8/\u5929\u3001\u5e26\u5bbd\u5747\u7ed9\u51fa + **\u7ed1\u5b9a\u51b3\u7b56**\u3002
3. **Architecture**\uff1a\u56fe\u793a\u6e05\u6670\u3001\u670d\u52a1\u6309 read/write+SLA \u5207\u3001\u5b58\u50a8\u9009\u578b\u6709\u7406\u7531\u3001\u6570\u636e\u6d41\u7f16\u53f7\u3002
4. **Deep Dive**\uff1a\u81f3\u5c11 2 \u4e2a\u3001\u6309 5-step \u7ed3\u6784\u3001\u542b\u4f2a\u4ee3\u7801/SQL\u3001\u6709 tradeoff \u6bd4\u8f83\u3002
5. **Reliability**\uff1a4 \u5c42\u5931\u6548\u57df\u3001\u964d\u7ea7\u7b56\u7565\u3001\u7194\u65ad/\u9650\u6d41\u3001\u591a AZ/region\u3002
6. **Monitoring**\uff1aSLI/SLO\u3001\u6280\u672f\u6307\u6807 + \u4e1a\u52a1\u6307\u6807\u3001\u544a\u8b66\u5206\u7ea7\u3001\u6545\u969c\u6f14\u7ec3\u3002
7. **Communication**\uff1a\u8282\u594f\u63a7\u5236\u3001tradeoff \u4e3b\u52a8\u8868\u8fbe\u3001\u7f3a\u70b9\u4e3b\u52a8\u63d0\u3001\u672a\u8986\u76d6\u9762\u660e\u786e\u3002

\u82e5\u4e03\u7c7b\u90fd\u90fd\u5f88\u786c \u2192 strong L5\uff1b\u67d0\u4e00\u7c7b\u660e\u663e\u5f31 \u2192 lean L4\uff1b\u4e24\u7c7b\u4ee5\u4e0a\u5f31 \u2192 L4 fail\u3002

## L5 \u2192 L6 Delta Table

| \u7ef4\u5ea6 | L5 | L6 |
|---|---|---|
| \u8303\u56f4 | \u5355\u4e2a\u7cfb\u7edf\u7684\u5b8c\u6574\u8bbe\u8ba1 | \u8de8\u7cfb\u7edf\u7684\u884c\u4e1a\u65b9\u6848\uff08platform\uff09 |
| \u51b3\u7b56 | \u6709\u6570\u5b57 + tradeoff | \u80fd\u63a8\u52a8\u4e1a\u52a1\u4fa7\u89c6\u89d2\uff08build vs buy\uff09 |
| \u5931\u6548 | \u542b\u964d\u7ea7 | \u542b\u6f14\u7ec3\u8ba1\u5212\u3001\u5e74\u5ea6\u5bb9\u91cf\u89c4\u5212 |
| \u521b\u65b0 | \u7528\u6210\u719f\u7ec4\u4ef6 | \u80fd\u63d0\u51fa\u65b0\u62bd\u8c61\uff08custom protocol / novel data model\uff09 |
| \u5f71\u54cd | team / org | company / industry |

## Tactics \u2014 \u4e09\u4ef6\u5b9e\u7528\u5668

**\u9762\u8bd5\u524d\u51c6\u5907\u5217\u8868**\uff1a(1) \u519b\u5907 5 \u4e2a\u9ad8\u9891\u9898\u6a21\u7248\u7b54\u6848\u3002(2) \u80cc\u719f 20 \u4e2a\u57fa\u51c6\u6570\u5b57\u3002(3) \u51c6\u5907 3 \u4e2a\u7ecf\u5178\u5931\u6548\u6545\u4e8b\u4e3a reliability \u7ae0\u4f9b\u7d20\u6750\u3002

**\u9762\u8bd5\u4e2d 3 \u6761\u7eaa\u5f8b**\uff1a(1) \u5148\u8bb2\u65b9\u6848\u5185\u5bb9\u518d\u8bb2\u540d\u8bcd \u2014\u2014 \u9762\u8bd5\u5b98\u77e5\u9053\u4f60\u61c2\u539f\u7406\u800c\u4e0d\u662f\u8bb0\u4e86\u5355\u8bcd\u3002(2) \u4e3b\u52a8\u7ed9\u51fa tradeoff \u2014\u2014 \u4e0d\u8981\u7b49\u9762\u8bd5\u5b98\u8ffd\u95ee\u3002(3) 5 \u5206\u949f\u627e\u4e0d\u5230\u7b54\u6848 \u2192 \u4e3b\u52a8\u8bf4\u201c\u6211\u5148\u6302\u7740\u8fd9\u4e2a\uff0c\u5148\u628a\u4e3b\u7ebf\u8df0\u901a\u201d\u3002

**3 \u53e5\u6551\u573a\u8bdd\u672f**\uff1a(a) \u201cLet me list 2-3 options and pick after comparing.\u201d (b) \u201cWhat\u2019s your latency budget for this step? I want to pick between X and Y.\u201d (c) \u201cA weakness of this design is W; the mitigation would be M \u2014\u2014 happy to go deeper if you\u2019d like.\u201d

## Appendix A \u00b7 Unified Template Skeleton

\u4efb\u4f55 Pillar 3 \u4e0b\u9762\u7684\u5177\u4f53\u8bbe\u8ba1\u9898\uff0889-97 + 198 + \u672a\u6765\u65b0\u9898\uff09\uff0c\u63cf\u8ff0\u90fd MUST \u6309\u5982\u4e0b\u9aa8\u67b6\u7ec4\u7ec7\u3002

### Required Sections\uff08\u6309\u987a\u5e8f\u51fa\u73b0\uff09

1. `# <Problem Title>`
2. `> <one-line positioning: what kind of system this is>`
3. `## Prerequisites` \u2014 \u5fc5\u987b include `\u2192 \u53c2\u89c1 [id=18 System Design Framework](/kg?node=n18)` \u4e00\u884c
4. `## 1. Requirements Clarification` \u2014 functional / non-functional\uff08\u542b\u5177\u4f53\u6570\u5b57\uff09 / out-of-scope
5. `## 2. Capacity Estimation` \u2014 DAU\u2192QPS\u2192Storage\u2192Bandwidth \u81f3\u5c11\u4e09\u6b65\uff0c\u5e76\u660e\u786e\u201c\u8fd9\u4e2a\u6570\u5b57\u9a71\u52a8\u4e86\u54ea\u4e2a\u67b6\u6784\u51b3\u7b56\u201d
6. `## 3. High-Level Architecture` \u2014 3-5 \u4e2a\u670d\u52a1\uff08\u6309 read/write + SLA \u5207\uff0c\u4e0d\u6309\u6a21\u5757\u5207\uff09\u3001\u7f16\u53f7\u6570\u636e\u6d41\u3001\u5b58\u50a8\u9009\u578b\u8868
7. `## 4. Deep Dives` \u2014 \u81f3\u5c11 2 \u4e2a\u6df1\u6316\u8bdd\u9898\uff0c\u6bcf\u4e2a\u6309 5-step \u7ed3\u6784\uff08essence / options / pick+why / scale-out / edges\uff09
8. `## 5. Reliability & Monitoring` \u2014 4 \u5c42 failure domain + \u964d\u7ea7\u8868 + SLO\uff08\u542b\u4e1a\u52a1\u6307\u6807\uff09
9. `## 6. Summary & Tradeoffs` \u2014 \u6838\u5fc3\u51b3\u7b56 + tradeoff + \u672a\u8986\u76d6\u70b9
10. `## Interview Q&A` \u2014 \u4fdd\u7559/\u6269\u5c55\u73b0\u6709 Q&A
11. `## Self-Check` \u2014 \u5bf9\u7167 id=18 pass-bar checklist \u7684 7 \u7c7b\u522b\u81ea\u6211\u6253\u5206

### Optional Sections\uff08\u4f5c\u4e3a Section 4 \u7684 nested deep-dive\uff09

- **ML-Domain Content**\uff1a\u5177\u4f53\u6a21\u578b\u3001\u516c\u5f0f\u3001\u6570\u636e\u96c6\u7b49\u2014\u2014\u73b0\u6709 9 \u9898\u7684 \u201cCore Concepts / Implementation / Interview Patterns / Comparisons / Key Takeaways / Advanced Topics\u201d \u5f52\u5230\u6b64\u5904\uff0c\u4f5c\u4e3a\u540c\u5c42 `###` \u5b50\u6a21\u5757\u3002

### Quality Gates \u2014 \u6bcf\u9053\u9898\u63cf\u8ff0\u5fc5\u987b\u6ee1\u8db3

- [ ] \u63cf\u8ff0\u957f\u5ea6 \u2265 8000 \u5b57\u7b26\uff08L5 \u6df1\u5ea6\u8981\u6c42\uff09
- [ ] Section 2 \u7ed9\u51fa\u81f3\u5c11 2 \u4e2a\u5177\u4f53\u6570\u5b57 + \u8bf4\u660e\u5b83\u9a71\u52a8\u4e86\u54ea\u4e2a\u51b3\u7b56
- [ ] Section 3 \u8868\u683c\u6216\u5217\u8868\u660e\u786e\u5217\u51fa\u670d\u52a1\u53ca\u5176 SLA
- [ ] Section 4 \u81f3\u5c11 2 \u4e2a deep dive\uff0c\u6bcf\u4e2a\u81f3\u5c11\u5305\u542b\u4e00\u6bb5\u4f2a\u4ee3\u7801\u6216 SQL
- [ ] Section 5 \u542b\u81f3\u5c11 3 \u6761\u5177\u4f53 SLO\uff08\u4e0d\u662f\u6cdb\u6cdb\u201c\u9ad8\u53ef\u7528\u201d\uff09
- [ ] Self-Check \u6bb5\u6309 id=18 \u7684 7 \u8282 checklist \u9010\u9879\u6253\u52fe
"""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def backup_db() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = DB_PATH.with_suffix(f".db.bak.{stamp}")
    shutil.copy2(DB_PATH, dst)
    print(f"[INFO] DB backup -> {dst.name}")
    return dst


REQUIRED_MARKERS = (
    "## Prerequisites \u2014 L5 vs L4",
    "## Time Budget",
    "## Stage 1: Requirements Clarification",
    "## Stage 2: Capacity Estimation",
    "## Stage 3: High-Level Architecture",
    "## Stage 4: Deep Dive",
    "## Stage 5: Reliability & Monitoring",
    "## Stage 6: Summary",
    "## L5 Pass-Bar Checklist",
    "## L5 \u2192 L6 Delta Table",
    "## Tactics",
    "## Appendix A \u00b7 Unified Template Skeleton",
    "### Required Sections",
    "### Quality Gates",
)


def validate(desc: str) -> list[str]:
    problems: list[str] = []
    n = len(desc)
    if n < LEN_MIN or n > LEN_MAX:
        problems.append(f"length {n} outside window [{LEN_MIN}, {LEN_MAX}]")
    if not desc.startswith(TITLE_GUARD):
        problems.append(f"description does not start with {TITLE_GUARD!r}")
    for marker in REQUIRED_MARKERS:
        if marker not in desc:
            problems.append(f"missing marker: {marker!r}")
    return problems


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] Database not found: {DB_PATH}")
        return 1

    problems = validate(NEW_DESCRIPTION)
    if problems:
        print("[FAIL] Embedded content failed self-validation:")
        for p in problems:
            print(f"  - {p}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()
        if not row:
            print(f"[FAIL] framework_node id={NODE_ID} not found")
            return 1
        old_desc = row[0]

        new_hash = sha256(NEW_DESCRIPTION)
        old_hash = sha256(old_desc) if old_desc is not None else None

        if old_hash == new_hash:
            print(f"[SKIP] Node {NODE_ID} already at target hash {new_hash[:12]}")
            print(f"[PASS] Current length = {len(NEW_DESCRIPTION)} chars")
            return 0

        # Tolerate later appendix suffixes (e.g. T-P0-514 Appendix A.1):
        # if current DB desc starts with our canonical body, leave DB alone.
        if old_desc is not None and old_desc.startswith(NEW_DESCRIPTION):
            print(f"[SKIP] Node {NODE_ID} already contains this body as prefix; "
                  f"a later seed has appended suffixes (len={len(old_desc)})")
            return 0

        print(
            f"[INFO] Char length: "
            f"{len(old_desc) if old_desc is not None else 'NULL'} "
            f"-> {len(NEW_DESCRIPTION)}"
        )
        print(f"[INFO] Old hash: {old_hash[:12] if old_hash else 'NULL'}")
        print(f"[INFO] New hash: {new_hash[:12]}")

        backup_db()

        # Archive old description first (even if NULL -- recoverability).
        conn.execute(
            "INSERT INTO framework_nodes_description_history(node_id, description) "
            "VALUES (?, ?)",
            (NODE_ID, old_desc),
        )
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (NEW_DESCRIPTION, NODE_ID),
        )
        conn.commit()

        check = conn.execute(
            "SELECT description FROM framework_nodes WHERE id = ?", (NODE_ID,)
        ).fetchone()[0]
        post = validate(check)
        if post:
            print("[FAIL] Post-update validation failed:")
            for p in post:
                print(f"  - {p}")
            return 1

        hist_rows = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes_description_history WHERE node_id = ?",
            (NODE_ID,),
        ).fetchone()[0]
        print(f"[PASS] Node {NODE_ID} updated; length now {len(check)} chars; "
              f"history rows for this node = {hist_rows}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
