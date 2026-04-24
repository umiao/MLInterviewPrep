# SD-YT-01: YouTube/Netflix Video Streaming expansion (2026-04-24)

**Task**: T-P1-602 [SD-YT-01]
**Target row**: `system_designs` id=21 slug=`interview-video-streaming`
**Seed script**: `scripts/seed_sd_youtube_content_pipeline_expand_20260421.py`
**DB backup suffix**: `_pre_expand_sd21`

## Scope

Fold 8 traditional-SD expansions into existing sections of id=21 (additive
only -- no section deletion, no numbered-list renumbering of existing sections).
Source: user-provided Discord attachment spec (Discord msg 1496318022804308119)
distilled into 8 expansion targets in the task description.

## What was added (section-by-section)

### architecture (3855 -> 7770 chars, +3915)

1. **#### 1. Upload Service** -- 2 new bullets:
   - *Chunked Upload Mechanics*: 10-50 MB chunks -> edge server ->
     GCS/Colossus blob -> Pub/Sub `video-ingest` topic -> stateless
     FFmpeg worker pool on thousands of instances; each chunk idempotent
   - *Pub/Sub vs Kafka* tradeoff in GCP ecosystem

2. **#### 2. Transcoding Pipeline** -- 3 new blocks:
   - *Transcoding Tier Policy*: H.264-for-all / VP9-for-hot /
     AV1-for-head+4K/8K with cost-amortization rationale
     (tail saves, head goes aggressive)
   - *Encoding Ladder*: 9-rung resolution pyramid
     (144p/240p/360p/480p/720p/1080p/1440p/2160p/4320p) with
     per-rung multi-bitrate tiers (720p @ 1.5/2.5/4 Mbps example)
   - *VCU / Argos ASIC callout*: Google self-designed video coding
     unit, 7-20x throughput vs NVENC GPU at same power, cites
     Ranganathan et al. ASPLOS 2021 paper

3. **#### 3. Video Storage** -- Storage & Metadata Split:
   - Blob on **Colossus** (GFS successor, RS 6,3 erasure coding)
   - Metadata on **Bigtable** (sparse columnar, auto-sharded by `video_id`)
   - Full-text on **Elasticsearch**
   - Content ID fingerprint on independent **Bigtable** table
     (Chromaprint 128-bit + pHash 60-bit)

4. **#### 4. CDN & Playback Service** -- Google Global Cache:
   - ISP-rack embedding layer (same shape as Netflix Open Connect Appliance)
   - RTT < 5 ms, 70%+ reduction in origin traffic, settlement-free peering
   - Forms `ISP rack -> regional Shield -> Origin (Colossus)` 3-layer CDN

5. **NEW #### 7. Content-to-Feature Bridge** -- multimodal pipeline:
   - Video-BERT frame embedding (every 2s, 512-dim)
   - ASR (Whisper/USM) + OCR + audio fingerprint + topic classifier
     + thumbnail CTR scorer
   - **Explicit bridge**: outputs feed BOTH Elasticsearch search index
     AND recommendation retrieval/ranking (framework node id=198)
   - Design principle: content understanding is platform capability,
     not per-vertical -- shared by search + reco

### tradeoffs (2282 -> 2523 chars, +241)

6. **Key Design Decisions table** -- 1 new row:
   - *分段协议 (Segment Protocol)*: HLS 6-10 s vs DASH 1-5 s
   - Decision: generate both; DASH shorter segments reduce rebuffering
     up to 30% on mobile; LL-DASH brings live latency to ~3 s

## AC grep verification (post-run, from seed script output)

| marker | actual | required |
|--------|--------|----------|
| VCU | 5x | >=1 |
| Colossus | 3x | >=1 |
| Bigtable | 3x | >=2 |
| Pub/Sub | 2x | >=1 |
| chunked | 3x | >=2 |
| Google Global Cache | 1x | >=1 |

## Size delta

- Core 7 sections before: 21417 chars
- Core 7 sections after: 25573 chars (+4156)
- Target range: 25000-30000 chars (AC met)

## Existing sections preserved (invariant check)

All existing `#### 1`-`#### 6` headings preserved; `####
数据库选择与理由 (Database Choices)` table intact; `### 通信模式
(Communication Patterns)` intact; `### 关键设计决策` table rows
(转码策略 / CDN 架构 / 视频编码 / 元数据存储 / 观看计数) all intact;
`### 一致性 vs 可用性`, `### 成本 vs 性能权衡`, `### 复杂度 vs
简洁度`, `### 10x / 100x 规模变化` all intact.

## Idempotency

- Marker strings for state detection: `Google Global Cache` in
  architecture AND `DASH 1-5 s` in tradeoffs.
- 2nd run: `[SKIP] sd21 already expanded` (full no-op).
- Anchor-based single-occurrence replacement: if anchor string fails
  to match (upstream drift) or matches >1x, script raises instead of
  half-applying.

## Manual smoke test (deferred -- not run in this session)

- Route: `/system-design/interview-video-streaming` (frontend id=21 slug)
- Expected: new subsections render markdown properly; sections 1-6
  show their new bullets; section 7 Content-to-Feature Bridge renders
  as fresh subsection between 观看计数 (#6) and 数据库选择与理由;
  tradeoffs table shows 6 rows (added 分段协议).
- Skipped here because the task is DB-content-only; all added content
  uses existing markdown constructs (bullets, tables, bold, inline
  code) already rendered by the app.

## Links

- framework node id=198 (Real-Time Recommendation): bridge target
  cited in new #### 7 subsection.
- DB backup: `data/mle_prep.db.bak.20260424_121805_pre_expand_sd21`
- Follow-up task: T-P1-603 [SD-YT-02] (framework_nodes id=198 expansion)
  -- intentionally scoped separately; this task did NOT edit id=198.
