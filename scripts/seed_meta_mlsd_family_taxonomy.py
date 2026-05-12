"""Seed Meta MLSD Family Taxonomy + 13 Question Cards doc (T-P0-838).

Per T-P0-838 ([Meta-MLSD B]). Target: company_documents row for company_id=31
(Meta) titled '[Meta-MLSD] Family Taxonomy + 13 Question Cards (drawer)'.

This is the cd:// drawer page reached from the Meta MLSD main hub (T-P0-832/840).
Content is the 13-题 family taxonomy summary table + per-question cards
(Q1-Q12 verbatim from source_02_family_taxonomy.md; Q13 Reels is reference-only
linking to sd://meta-reels-golden — the canonical 45-min walkthrough seeded in
T-P0-837).

SOURCE:
  docs/prep/meta_mlsd_2026-05-11/source_02_family_taxonomy.md
    - Lines 1-3: 第一节 family taxonomy 13 行 (题目 / family / unique twist)
    - Lines 8-160: 第三节 Q1-Q12 详细卡片
                   (Twist -> Puzzle pieces -> Anti-patterns -> Strong moment)

DB TARGET: data/mle_prep.db, table=company_documents
  is_golden = 0 (drawer page, NOT the default first page)
  doc_kind  = 'prep_note'
  source_type = 'manual'

Idempotency: sentinel <!-- META_MLSD_FAMILY_TAXONOMY_20260511 --> gates the
write. Second run = 0 writes when content is byte-identical.

Style:
  - Chinese narration + English ML terms (first-occurrence pattern)
  - Strong moment hooks: English verbatim (face-the-interviewer line)
  - Puzzle pieces: compact 2-col markdown table (Piece | Why)
  - Anti-patterns: bullet list with leading X marker (U+274C)
    (U+274C is U+2700-27BF Dingbats; NOT in lint regex ranges -- precedent:
     scripts/seed_meta_reels_golden_sd.py uses the same marker.)
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
SENTINEL = "<!-- META_MLSD_FAMILY_TAXONOMY_20260511 -->"

COMPANY_ID = 31  # Meta
DOC_TITLE = "[Meta-MLSD] Family Taxonomy + 13 Question Cards (drawer)"
DOC_KIND = "prep_note"
SOURCE_TYPE = "manual"
IS_GOLDEN = 0

# X-mark prefix for anti-patterns (Dingbats U+274C, precedent: reels golden SD).
X = "❌"

CONTENT = f"""{SENTINEL}

# Meta MLSD - Family Taxonomy + 13 Question Cards (drawer)

> 30 秒判题型 -> 跳卡片 -> 套 puzzle pieces + 投 strong moment hook -> 按 timing skeleton 走 45 分钟. 金句英文 verbatim, 不 paraphrase.

---

## 1. Family Taxonomy 总表 (30 秒判题)

| # | 题目 | Family | 核心 unique twist |
| - | --- | --- | --- |
| 1 | Top 3 comments extraction | Intra-item ranking | 候选池极小, top slot 影响下游对话质量 |
| 2 | Video-to-video search | Pure retrieval (no query) | "相似" 无法被 query 定义, 多 facet |
| 3 | Friend recommendation | Graph-native | 图结构是 retrieval 本身, reciprocity 决定 label |
| 4 | Ads recommendation | Auction-mediated | 要 calibrated probability, 多 stakeholder |
| 5 | Event recommendation | Sparse + temporal | 双重 cold-start, 事件会过期 |
| 6 | Location recommendation | Context-dominant | POI 稳定, user intent 在 request time 才出现 |
| 7 | Weapon ad classifier | Adversarial classification | Attack 模式演化, cost asymmetric |
| 8 | Yelp restaurant | Aspect-rich | Review text 是主导信号, aspect 级匹配 |
| 9 | FB News Feed | Heterogeneous ranking | 多内容类型, 社交图权重, MSI 而非 engagement |
| 10 | IG Story | Time-bounded sequential | 24h 过期, author-tray 而非 item ranking |
| 11 | Spotify music | Audio + session | 音频 embedding + session 连续性 + relisten 正向 |
| 12 | Predict event attendance | Prediction-as-feature | 必须先问 "下游谁用这个 prediction" |
| 13 | Reels | Session-continuous ranking | 见 golden example: [sd://meta-reels-golden](sd://meta-reels-golden) |

---

## 2. Per-Question Cards (Q1-Q13)

每卡: Twist -> Puzzle Pieces -> Anti-patterns -> Strong Moment (英文 verbatim).

### Q1. Top 3 Comments Extraction

**Unique Twist**: 这是 **intra-item ranking**, 不是 cross-item. 候选池只有几十到几千, position 0 comment 是下游 conversation 种子 — 比 user engagement 更深远.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Single-stage ranking (跳过 retrieval) | N 小, retrieval 没必要 |
| Quality-weighted score | representativeness 比 raw likes 重要 |
| Time-normalized engagement label | 否则早 commenter 自动赢 |
| Author authority feature | verified / 历史质量是稳定信号 |
| Diversity constraint | 不要 3 条同一作者 / 情感倾向 |
| Adversarial-aware (first-poster gaming) | 抢沙发 attack, 要 detect |

**Anti-patterns**:
- {X} 套两阶段 retrieval+ranking (N 太小)
- {X} 用 raw like count 当 label
- {X} 只优化 selected comment engagement, 不想下游

**Strong Moment**: "The comment at position 0 isn't just a ranked result—it becomes the seed of the conversation that the next thousand viewers see. So we're optimizing downstream conversation quality, not just the engagement of the selected comments."

### Q2. Video-to-Video Search (no text)

**Unique Twist**: 没 text query, "相似" 本身需被定义. 视觉 / 音频 / 用途相似是三 axis, 不重合.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Per-modality encoder (visual / audio / OCR) | 各 modality 独立 embedding |
| L2-normalize per modality before fusion | 否则一个 modality 会 dominate |
| Multi-facet retrieval (每 facet 各一批) | user intent 不可知, 先 cover 多 axis |
| Learned fusion weights from click/dwell | 用户点哪个 facet -> learn weight |
| Single-stage (query 是 video) | 没有 user side, 不需 two-tower |
| Cold-start friendly (content-only) | 新 video 上传即可索引 |

**Anti-patterns**:
- {X} 单一 fused embedding 不 normalize
- {X} 强行套 two-tower with user side
- {X} 假装 query intent 已知

**Strong Moment**: "'Similar' is undefined here—it could mean visually similar, audio-similar, or intent-similar, and these pull in different directions. I'd treat this as multi-facet retrieval and let user interaction learn which axis matters in their session."

### Q3. Friend Recommendation (Meta 产品名 **PYMK** = People You May Know)

**Unique Twist**: 图结构是 retrieval 本身, 不是 feature. **Reciprocity** (双向接受) 才是真 positive; dismissal 是异常强负信号.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Graph traversal retrieval (2-hop) | 候选 = extended network |
| Graph features (mutual friends, communities) | 图结构 native signal |
| Reciprocity-aware label (accept = positive) | 单向 send 不可靠 |
| Negative signal from dismissal | 已 ignore 不再推, 强 signal |
| Privacy hard filters (block, restricted) | 红线, 不 ML soft-handle |
| Entity overlap cold-start (school/work) | 新账号没 graph |

**Anti-patterns**:
- {X} 两塔走 user embedding similarity (忽略图)
- {X} send-request 当 positive (接收方 ignore 你 +1)
- {X} 把 dismissal 当 "待会再试" neutral

**Strong Moment**: "The strongest signal in this domain is actually the negative—a user dismissing a PYMK suggestion is a far more reliable label than them sending a friend request, because the request can be one-sided while dismissal is unambiguous."

### Q4. Ads Recommendation

**Unique Twist**: 输出必须是 **calibrated probability**, 不是 ordinal score — auction 的 bid x pCTR 要求 calibration. 多 stakeholder, conversion 有延迟.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Logloss + calibration (不 pairwise) | pairwise 破坏 calibration |
| Multi-task: pCTR + pConversion + pQuality | 不同目标分头再合 |
| Final score = bid x pCTR x pConversion x quality | Auction 输入 |
| Delayed feedback model (windowed labels) | 购买可能 7 天后发生 |
| Counterfactual / IPS replay before A/B | A/B 会影响 advertiser bidding |
| Pacing & budget 在 ML 之外 | ML 出 probability, pacing 是下游 |

**Anti-patterns**:
- {X} 用 NDCG / pairwise loss
- {X} 所有 conversion 当 same-day
- {X} 把 advertiser 当 static (他们 react 你的模型)
- {X} pacing/budget 塞进 ML loss

**Strong Moment**: "Ads ranking isn't really ranking—it's calibrated probability estimation feeding an auction. The moment you switch to a pairwise loss for NDCG gains, you've broken the auction economics."

### Q5. Event Recommendation

**Unique Twist**: 双 cold-start (event 一直新+死, user RSVP 极低), geo+time 是硬约束不是 feature, conversion 高成本.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Content-based retrieval 主导 | per-user 太稀疏, CF 不够 |
| Hard filter: geo + time + capacity | 不能跨地理硬推 |
| Multi-label: click / RSVP / attend | click=noise, RSVP=intent, attend=truth |
| Friend-going 作强 feature | strong signal, 小心 selection bias |
| Cold-start ramp (quality-gated burst) | 新 event 需要 exposure 启动 |
| Time-decay calibration | 下游可能用 prob 决定 notify |

**Anti-patterns**:
- {X} 纯 CF 套 user-item matrix
- {X} soft-filter 地理位置
- {X} 用 click 当主 label
- {X} 忽略 capacity / fully booked event

**Strong Moment**: "A typical user might RSVP to 3 events a year. Per-user history is too sparse for collaborative filtering to be the primary lever—content embedding over event metadata has to do most of the work, with social signals (friends attending) as the strongest personalization input."

### Q6. Personalized Location Recommendation

**Unique Twist**: POI 长期稳定, user intent 在 request time 才浮现. 同店 9am 是答案 9pm 不是. Context 是主导 intent disambiguator, 不是普通 feature.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Heavy context (time, weather, calendar, party) | 决定当下 intent |
| POI embedding 稳定 + offline precompute | POI 变化慢 |
| Real-time user signal (location, queries) | momentary intent |
| Intent classification as intermediate task | "吃饭 vs 咖啡 vs activity" 后再 rank |
| Diversity in re-ranking | 不要 5 个都 cafe |
| Distance + travel-time feature | walking vs driving 体验不同 |

**Anti-patterns**:
- {X} 把 context 当一般 feature (它是主信号)
- {X} 静态 user preference profile (intent 是 momentary)
- {X} 优化 click 而非 visit / booking

**Strong Moment**: "The user at 9am and the same user at 9pm have completely different intents—context isn't one feature among many, it's the primary disambiguator. Without it, we're just recommending the user's average preference, which is no one's actual preference at any moment."

### Q7. Weapon Ad Classifier

**Unique Twist**: **Adversarial** (主动 evade) + 极端 class imbalance (~0.1% pos) + multimodal + cost asymmetric (FN >> FP).

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Multimodal input (image + text + landing page) | 单 modality 漏 image weapons |
| LLM-as-teacher -> distilled student | Teacher 离线 bulk, student 在线 serve |
| Active learning loop | 静态数据集 3 个月失效 |
| Class imbalance: focal loss / cascade | naive 学不到 0.1% positive |
| Asymmetric threshold + human review | FN=违规, FP=ad 错拒 |
| Adversarial augmentation | 模型要 robust to obfuscation |

**Anti-patterns**:
- {X} 对称 thresholding (FN 和 FP 不等价)
- {X} 静态 training set
- {X} 单模态 (text-only 漏 image weapons)
- {X} 直接用 LLM serve (latency / cost)

**Strong Moment**: "The training set you ship today is broken in three months because attackers evolve. The real system isn't the model—it's the active learning loop. The model is just the current snapshot of an ongoing arms race."

### Q8. Yelp Restaurant Recommendation

**Unique Twist**: Review text 是 **dominant signal**. Aspect-level matching (quiet / vegan / romantic) 超过 rating matching 上限.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Aspect extraction from reviews (LLM-based) | "适合约会" 是 review-only signal |
| User aspect preference from review history | 用户写过 review 暴露偏好 |
| Aspect-level matching (非 embedding cosine) | 比 rating-CF 丰富一个量级 |
| Geo + open-now hard filter | 不能 soft handle |
| Time-of-day relevance | 早 vs 晚 relevance 不同 |
| Photo / recent visit signal | 高时效, 反映 current quality |

**Anti-patterns**:
- {X} 纯 rating-based CF (上限低)
- {X} 忽略 review text
- {X} 静态 "good restaurant" 排序

**Strong Moment**: "Rating-based CF has a hard ceiling because two 4-star restaurants can be completely different experiences. The lift comes from aspect-level matching—extracting 'is this place quiet, group-friendly, vegan-OK' from reviews and matching to the user's expressed preferences in their own review history."

### Q9. FB News Feed

**Unique Twist**: 内容类型异构 (status / photo / video / link / milestone), 社交图权重显著, Meta 显式从 engagement 转向 **MSI** (Meaningful Social Interactions).

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Multi-source CG (friends / groups / pages) | 不同 source 不同 retrieval |
| Cross-source ranking | 最后合一个 feed 要互比 |
| Multi-task heads weighted toward MSI | close-friend comment >> page like |
| Diversity across content type + source | 不要刷屏同一 publisher |
| Integrity downranking (misinfo / clickbait) | well-being signal, soft filter |
| Reverse-chronology for close friends | 不能埋掉重要 update |

**Anti-patterns**:
- {X} 单 ranking head on raw engagement
- {X} 套 Reels 的 session-continuous (feed 是 pull-based)
- {X} 忽略 well-being / integrity

**Strong Moment**: "Meta explicitly moved from engagement optimization to MSI—a like from a stranger is worth less than a comment from a close friend. The label hierarchy isn't a nice-to-have, it's the platform's stated objective. Any design that flattens this back to 'predict click' is fighting the company's own product direction."

### Q10. IG Story Recommendation

**Unique Twist**: 24h 硬过期 + ranking unit is **author-tray, not story** — 按作者顺序刷, 改变整个 architecture.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Author-tray level ranking | 用户按 author 浏览 |
| Recency 作硬过滤 (24h) | 不是 feature, 是 eligibility |
| Skip-to-next-author 作负 label | story 特有 implicit negative |
| Close-friends signal 异常强 | story 比 feed 更亲密 |
| Within-tray story sequence model | author 多 story 内部顺序 |
| Cold-start every day | 没有跨日 reuse |

**Anti-patterns**:
- {X} 套 item-level ranking (granularity 错)
- {X} 把 recency 当 feature (它是硬 filter)
- {X} 忽略 "close friends" 隐式权重

**Strong Moment**: "The unit of ranking here isn't story, it's author-tray. Users consume by author, not by individual story—you watch all of Alice's stories then jump to Bob's. This changes the entire architecture: a story-level deep model is solving the wrong granularity problem."

### Q11. Spotify Music Recommendation

**Unique Twist**: 音频 embedding + session 连续性 (mood 不能跳) + **relisten 是正向** (跟视频相反).

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Audio embedding from spectrogram | 内容理解, metadata 不够 |
| Metadata features (genre / artist / era) | 互补稳定信号 |
| Session context (当前 mood) | 不能摇滚突跳古典 |
| Sequential model (next-song given playlist) | session-aware 必须 |
| Repeat consumption as positive | 100 遍同歌 = 极爱 |
| Cold-start via audio embedding | 新 artist 直接可索引 |

**Anti-patterns**:
- {X} 忽略 within-session mood 连续性
- {X} 把 relisten 当疲劳信号 (错, 是正向)
- {X} 纯 CF (audio 是实打实 lift)

**Strong Moment**: "Music has one feature that distinguishes it from almost every other recommendation domain: relisten is positive, not redundant. A user playing the same song 50 times is a five-star signal, not a saturation signal. This inverts the deduplication logic you'd use for video or articles."

### Q12. Predict If User Attends FB Event

**Unique Twist**: 这是 **prediction-as-feature** — 先问 "谁消费 prediction", 否则 design 走偏. 上次答烂大概率在此.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Step 0: clarify downstream consumer | ranking? notify? capacity? 决定一切 |
| Label: RSVP vs actual attendance | 不同 target, 不同 model |
| Time-to-event feature | 1 月 vs 1 天预测机制不同 |
| Social context (friends going, host) | 强 signal |
| Calibrated probability | 不是 ranking score |
| Cold-start for new event types | 演唱会 vs 婚礼 vs meetup |

**Anti-patterns**:
- {X} 不问 "谁用预测" 就 design (上次失败原因)
- {X} 单 label (RSVP vs attend 是不同问题)
- {X} 静态 prediction (随临近变化)
- {X} 纯 binary 不想下游 calibration

**Strong Moment** (这一句话救场): "Before designing this, the most important question is: who consumes the prediction? If it's recommendation ranking, we need calibrated probability for every (user, event) pair. If it's notification gating, we only score the events the user has been recommended. If it's host-side capacity planning, we aggregate. The architecture differs significantly. My default assumption is recommendation ranking—is that the intended use?"

### Q13. Reels Homefeed

**Unique Twist**: Reels homefeed 是无显式 query intent 的 user-conditioned ranking, 内容是多模态 UGC, 主信号是 watch-completion-ratio 而非秒数, slate-level 上有 session fatigue, 平台层有 creator marketplace 长尾保护, 整个 logged data 受 feedback loop 污染.

**Puzzle Pieces**:

| Piece | Why |
| --- | --- |
| Hybrid serving (active 离线 batch + fresh 在线 incremental, blend at retrieval) | freshness vs latency 双重 trade-off |
| Multi-modal encoders (visual / audio / text) + 融合 | UGC metadata 不可信 |
| 2-tower (user side ≠ optional) | no explicit query, user 本身就是 query |
| Multi-task heads (click + completion + watch-time, completion-ratio weighted) | 短视频 watch-time 用绝对秒数会偏向长视频 |
| Slate-level reranking (MMR / DPP) + session metrics | 单点最优 ≠ session 最优 |
| IPS + exploration policy + counterfactual replay (= 第 10 积木) | logged data 严重有偏 |

**Anti-patterns**:
- {X} 用绝对 watch-time 当 label (短视频被打低)
- {X} 单 tower content-only retrieval (忽略 user query nature)
- {X} 套 search results page 的 query-intent 思路
- {X} 忽略 creator 长尾保护 (marketplace supply 死亡螺旋)
- {X} 每个 item 独立 score (忽略 session fatigue)

**Strong Moment**: "Reels homefeed 不是 search results — 用户没有显式 query, user 表征本身就是 query. 这把 retrieval 强制推向 user-conditioned 2-tower, serving 上 active user 走离线 batch cache 但还要并行跑 online incremental 把 fresh content 拉进来. 这是 cold-start 和 freshness 两个问题同时被同一架构解掉."

→ 完整方法论 derivation: [cd://96](cd://96) (Twist 挖掘方法论 section) | 实战 45min 8 段台词 verbatim: [sd://meta-reels-golden](sd://meta-reels-golden)

---

## 3. 如何使用这本 drawer

30 秒看 Section 1 判 family -> 跳对应 Q 卡片 -> 套 Puzzle Pieces + 投 Strong Moment 英文 verbatim -> 按 [sd://meta-reels-golden](sd://meta-reels-golden) timing skeleton 走 45 分钟.
"""


def sha256_bytes(text: str) -> str:
    """Return SHA-256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_content(content: str) -> None:
    """Cheap structural checks on the content payload (mirrors task spec validation)."""
    if SENTINEL not in content:
        raise RuntimeError("sentinel missing")

    # Length bounds: 9000-14000 chars original; 14200 (2026-05-12) for PYMK
    # acronym; 15700 (T-P0-848) for Q13 Reels stub -> full card promotion
    # (Unique Twist + Puzzle Pieces + Anti-patterns + Strong Moment + dual
    # pointer to cd://96 + sd://meta-reels-golden).
    n = len(content)
    if not (9000 <= n <= 15700):
        raise RuntimeError(f"content length {n} not in [9000, 15700]")

    # Section markers
    for marker in (
        "# Meta MLSD - Family Taxonomy",
        "## 1. Family Taxonomy",
        "## 2. Per-Question Cards",
        "## 3. 如何使用这本 drawer",
    ):
        if marker not in content:
            raise RuntimeError(f"section marker missing: {marker!r}")

    # Q13 Reels golden link (sd) + methodology dual-pointer (cd://96, T-P0-848)
    if "sd://meta-reels-golden" not in content:
        raise RuntimeError("sd://meta-reels-golden link missing")
    if "cd://96" not in content:
        raise RuntimeError("cd://96 methodology dual-pointer missing")

    # 13 '### Q' headers (Q1-Q13; Q13 promoted from h4 stub to full h3 card
    # in T-P0-848). Exact '### Q1.'..'### Q13.' pattern matches.
    q_top_headers = sum(
        1
        for i in range(1, 14)
        if f"### Q{i}." in content
    )
    if q_top_headers != 13:
        raise RuntimeError(
            f"expected 13 top-level Q1-Q13 headers, got {q_top_headers}"
        )

    # 'Strong Moment' >= 13 (one per Q1-Q13).
    sm_count = content.count("**Strong Moment**")
    if sm_count < 13:
        raise RuntimeError(
            f"expected >=13 '**Strong Moment**' markers, got {sm_count}"
        )

    # Taxonomy table: 13 data rows + header + separator >= 15 lines starting with '|'
    table_lines = [
        ln for ln in content.splitlines()
        if ln.lstrip().startswith("|")
    ]
    if len(table_lines) < 15:
        raise RuntimeError(
            f"taxonomy table too short: {len(table_lines)} lines starting with '|'; "
            f"need >=15 (header + sep + 13 data rows + per-card puzzle tables)"
        )
    # Also explicit check: 13 numbered rows '| 1 |' .. '| 13 |' in Section 1
    for i in range(1, 14):
        if f"| {i} |" not in content:
            raise RuntimeError(f"taxonomy row '| {i} |' missing")

    # T-P0-848: cd:// now permitted (Q13 card cross-refs cd://96 methodology
    # section). db:// / lc:// still forbidden.
    for scheme in ("db://", "lc://"):
        if scheme in content:
            raise RuntimeError(
                f"forbidden URI scheme {scheme!r} present"
            )

    # Self-link exclusion: Q13 body must NOT reference cd://94 (this doc).
    if "cd://94" in content:
        raise RuntimeError("self-link cd://94 must not appear in this doc")


def main() -> int:
    """Upsert the Meta MLSD Family Taxonomy + Q-cards doc (idempotent)."""
    if not DB_PATH.exists():
        print(f"[ERROR] db not found: {DB_PATH}")
        return 1

    validate_content(CONTENT)
    print(f"[OK] content validated: len={len(CONTENT)}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        row = conn.execute(
            "SELECT name FROM companies WHERE id = ?", (COMPANY_ID,)
        ).fetchone()
        if row is None:
            print(f"[ERROR] company_id={COMPANY_ID} not found")
            return 1
        print(f"[OK] target company: id={COMPANY_ID} name={row[0]!r}")

        cur = conn.execute(
            "SELECT id, content FROM company_documents "
            "WHERE company_id = ? AND title = ?",
            (COMPANY_ID, DOC_TITLE),
        )
        existing = cur.fetchone()

        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        new_hash = sha256_bytes(CONTENT)

        if existing is None:
            conn.execute(
                "INSERT INTO company_documents "
                "(company_id, title, content, source_type, doc_kind, "
                "is_golden, content_hash, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    COMPANY_ID,
                    DOC_TITLE,
                    CONTENT,
                    SOURCE_TYPE,
                    DOC_KIND,
                    IS_GOLDEN,
                    new_hash,
                    now,
                    now,
                ),
            )
            conn.commit()
            new_id = conn.execute(
                "SELECT id FROM company_documents "
                "WHERE company_id = ? AND title = ?",
                (COMPANY_ID, DOC_TITLE),
            ).fetchone()[0]
            print(
                f"[INSERT] id={new_id} len={len(CONTENT)} "
                f"hash={new_hash[:12]}..."
            )
        else:
            existing_id, existing_content = existing
            if SENTINEL in existing_content and existing_content == CONTENT:
                print(
                    f"[UNCHANGED] id={existing_id} sentinel present + "
                    f"content byte-identical; 0 writes"
                )
            else:
                conn.execute(
                    "UPDATE company_documents "
                    "SET content = ?, content_hash = ?, updated_at = ? "
                    "WHERE id = ?",
                    (CONTENT, new_hash, now, existing_id),
                )
                conn.commit()
                old_len = len(existing_content)
                print(
                    f"[UPDATE] id={existing_id} old_len={old_len} "
                    f"new_len={len(CONTENT)} delta={len(CONTENT) - old_len:+d}"
                )

        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
