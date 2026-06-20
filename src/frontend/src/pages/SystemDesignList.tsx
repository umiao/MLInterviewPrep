import { useState, useMemo, useEffect } from "react";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type {
  SystemDesignSummary,
  SystemDesignCheatSheet,
} from "../types/system-design";
import ImageLightbox from "../components/ui/ImageLightbox";
import CheatSheetCard from "../components/CheatSheetCard";

const EBAY_NARRATIVE = `My core work at eBay has been systematically transforming search ranking from independent pointwise scoring into page-level resource allocation. Starting with the data foundation (PBE Pipeline for unbiased training data), I built the allocation framework (Ranking-as-Allocation with diversity constraints), extended it to multi-module page composition (Module Arbitration marketplace), and most recently brought GenAI into the production search path (LLM Artifact Orchestration). Each project builds on the last -- together they represent a complete evolution from 'rank items by relevance score' to 'optimize the entire user experience as a constrained allocation problem.'`;

const READING_ORDER =
  "Interview reading order: PBE Pipeline -> Ranking-as-Allocation -> Module Arbitration -> LLM Orchestration";

type Difficulty = "Easy" | "Medium" | "Hard";

interface TopicMeta {
  description: string;
  difficulty: Difficulty;
  tags: string[];
  category: string;
}

const CATEGORY_ORDER = [
  "Core Infrastructure",
  "Social & Real-time",
  "Location & Geo",
  "Search & Data",
  "Storage & Media",
  "Recommendation & ML",
  "Trust & Safety",
  "Specialized",
];

const PINTEREST_CATEGORY_ORDER = ["Pinterest"];

/** Client-side metadata for each interview topic, keyed by slug. */
const TOPIC_META: Record<string, TopicMeta> = {
  "interview-url-shortener": {
    description:
      "TinyURL-style service: hash/encode long URLs, redirect, analytics, expiration. Focus on hashing strategy, collision handling, and read-heavy scaling.",
    difficulty: "Easy",
    tags: ["Hashing", "Database", "Caching"],
    category: "Core Infrastructure",
  },
  "interview-rate-limiter": {
    description:
      "API gateway rate limiting: token bucket, sliding window, distributed counters. Focus on accuracy vs performance trade-offs and distributed coordination.",
    difficulty: "Medium",
    tags: ["Distributed Systems", "Redis", "API Gateway"],
    category: "Core Infrastructure",
  },
  "interview-distributed-cache": {
    description:
      "Consistent hashing with virtual nodes, LRU/LFU/TinyLFU eviction, cache-aside vs write-through vs write-behind, stampede prevention (singleflight), hot key mitigation (L1 + key replication), CDC-driven invalidation, Bloom Filter for penetration defense.",
    difficulty: "Hard",
    tags: ["Consistent Hashing", "Caching", "Distributed Systems"],
    category: "Core Infrastructure",
  },
  "interview-notification-system": {
    description:
      "Multi-channel notifications: push, SMS, email. Priority queues, rate limiting per user, template rendering, delivery tracking and retry logic.",
    difficulty: "Medium",
    tags: ["Message Queue", "Priority", "Multi-channel"],
    category: "Core Infrastructure",
  },
  "interview-news-feed": {
    description:
      "Social media feed generation: fan-out on write vs read (hybrid model), celebrity problem, ML ranking (EdgeRank), media CDN, feed cache invalidation, cursor pagination.",
    difficulty: "Hard",
    tags: ["Fan-out", "Ranking", "Caching"],
    category: "Social & Real-time",
  },
  "interview-chat-system": {
    description:
      "Real-time messaging: WebSocket connections, message delivery guarantees, group chat, online presence. Focus on connection management and message ordering.",
    difficulty: "Medium",
    tags: ["WebSocket", "Message Queue", "Presence"],
    category: "Social & Real-time",
  },
  "interview-live-comments": {
    description:
      "Real-time comment streaming for live video: Fan-out Tree for millions of concurrent viewers, comment sampling, SSE/WebSocket, pre-moderation pipeline, reaction aggregation.",
    difficulty: "Hard",
    tags: ["Fan-out", "SSE", "Real-time", "Moderation"],
    category: "Social & Real-time",
  },
  "interview-game-leaderboard": {
    description:
      "Redis Sorted Set leaderboard: ZADD/ZREVRANK/ZREVRANGE, Top-K, rank lookup, relative ranking, Kafka peak shaving, score-range sharding for 50M+ players, daily/weekly/season boards.",
    difficulty: "Medium",
    tags: ["Redis", "Sorted Set", "Real-time"],
    category: "Social & Real-time",
  },
  "interview-ride-sharing": {
    description:
      "Real-time driver matching, location tracking, surge pricing, trip lifecycle. Focus on geospatial indexing, high-throughput location updates, and supply-demand balancing.",
    difficulty: "Hard",
    tags: ["Geospatial", "WebSocket", "Real-time"],
    category: "Location & Geo",
  },
  "interview-proximity-service": {
    description:
      "Nearby search: Geohash vs QuadTree vs R-Tree, radius queries, business CRUD + filtering, multi-level caching for 99:1 read-heavy workload.",
    difficulty: "Medium",
    tags: ["Geospatial", "Caching", "Read-heavy"],
    category: "Location & Geo",
  },
  "interview-search-autocomplete": {
    description:
      "Typeahead suggestion: trie data structure, top-K frequent queries, real-time updates. Focus on latency requirements and data freshness.",
    difficulty: "Medium",
    tags: ["Trie", "Caching", "Ranking"],
    category: "Search & Data",
  },
  "interview-top-k-heavy-hitters": {
    description:
      "Count-Min Sketch + Min-Heap streaming Top-K: three-layer aggregation (local -> partition -> global), Lambda Architecture with hourly batch calibration, multi-window CMS additivity.",
    difficulty: "Hard",
    tags: ["Streaming", "Probabilistic DS", "MapReduce"],
    category: "Search & Data",
  },
  "interview-ad-click-aggregator": {
    description:
      "Lambda Architecture for ad billing: Kafka + Flink exactly-once aggregation, two-level dedup (Bloom Filter + RocksDB), real-time fraud detection, ClickHouse OLAP, batch billing reconciliation.",
    difficulty: "Hard",
    tags: ["Streaming", "Exactly-Once", "Fraud Detection"],
    category: "Search & Data",
  },
  "interview-web-crawler": {
    description:
      "Distributed web crawler: URL frontier, politeness, dedup, content extraction. Focus on scale, distributed coordination, and fault tolerance.",
    difficulty: "Medium",
    tags: ["Distributed Systems", "Queue", "Dedup"],
    category: "Search & Data",
  },
  "interview-video-streaming": {
    description:
      "Upload + transcoding pipeline (DAG parallel GPU transcode), ABR adaptive bitrate (HLS/DASH), three-layer CDN caching (Edge 200+ POP -> Shield -> Origin S3), multi-CDN failover, viral video handling.",
    difficulty: "Hard",
    tags: ["CDN", "Video", "Transcoding"],
    category: "Storage & Media",
  },
  "interview-cloud-storage": {
    description:
      "Block-level chunking (CDC/Rabin Fingerprint) + dedup + delta sync, conflict resolution (version vector + conflict copy), metadata DB (MySQL sharded), WebSocket sync notification, tiered storage optimization, offline editing.",
    difficulty: "Hard",
    tags: ["Storage", "Sync", "Dedup"],
    category: "Storage & Media",
  },
  "interview-price-drop-tracker": {
    description:
      "Scraping pipeline (proxy rotation, anti-scraping, golden tests), TimescaleDB price history (downsampling, continuous aggregates), event-driven alert evaluation (Kafka + rule engine + cooldown), Z-Score anomaly detection, dynamic scrape priority.",
    difficulty: "Medium",
    tags: ["Scraping", "Time-Series", "Alerts"],
    category: "Specialized",
  },
  "interview-online-judge": {
    description:
      "Code sandbox (gVisor/Docker + cgroups + seccomp), queue-based submission pipeline (RabbitMQ), test case runner with early termination, judge verdicts state machine, MOSS plagiarism detection (Winnowing), multi-language runtime, contest leaderboard (Redis Sorted Set).",
    difficulty: "Hard",
    tags: ["Sandbox", "Queue", "Security"],
    category: "Specialized",
  },
  "interview-ticket-reservation": {
    description:
      "Seat inventory with distributed locking (SELECT FOR UPDATE SKIP LOCKED), payment hold TTL, virtual queue for flash sales, overbooking probability model, idempotent payment, waitlist notification.",
    difficulty: "Hard",
    tags: ["Concurrency", "Locking", "Queue"],
    category: "Specialized",
  },
  "interview-auction-system": {
    description:
      "Real-time bidding via WebSocket, bid ordering with monotonic timestamps, auction state machine, sniping protection (soft close), proxy bidding engine, payment escrow, reserve price, hot auction isolation via Kafka serialization.",
    difficulty: "Hard",
    tags: ["Real-time", "Concurrency", "WebSocket"],
    category: "Specialized",
  },
  "interview-harmful-content-detection": {
    description:
      "Multi-modal (text+image+video) classifier with hybrid fast-path + human-review pipeline. 5B+ posts/day at 100ms p99. Per-policy precision/recall thresholds (hate-speech vs CSAM), distilled model for throughput, active-learning loop, region-specific rule engine (GDPR vs US). Metric: prevalence + appeal rate.",
    difficulty: "Hard",
    tags: ["Multi-modal", "ML Serving", "Trust & Safety"],
    category: "Trust & Safety",
  },
  "interview-fb-post-privacy": {
    description:
      "Audience-visibility at scale: 3B users x 100B posts, p99 < 5ms. Hybrid materialize/filter strategy split by author follower count, bitmap/set membership in TAO/Redis, CDC + Tombstone for privacy-edit propagation, Custom List lazy recompute. Access-control problem, not ML.",
    difficulty: "Hard",
    tags: ["Access Control", "TAO", "Materialization"],
    category: "Social & Real-time",
  },
  "interview-spotify-audio-streaming": {
    description:
      "Audio-specific differences from video streaming: 3-tier codec ladder (96/160/320 kbps), gapless playback with prefetch+crossfade, file-level DRM (not per-segment), Discover Weekly = CF + audio embedding (CNN on raw waveform). Offline download = force 320kbps. Anti-fraud: device fingerprint + 30s play threshold.",
    difficulty: "Hard",
    tags: ["CDN", "Audio", "Recommendations"],
    category: "Storage & Media",
  },
  "interview-recommendation-system": {
    description:
      "Three-stage funnel: Retrieval (10B->1K via 5-path multi-source) -> Ranking (DLRM + MMoE 4-8 experts + DCN-v2, multi-task CTR/retention/save/share) -> Rerank (MMR/DPP diversity + creator pacing + IPS position-bias). Two-tower DSSM ANN via HNSW/Faiss-IVF; user-item fully decoupled. Cold start: content embedding for items, demographic prior for users.",
    difficulty: "Hard",
    tags: ["Two-Tower", "DLRM", "MMoE", "Multi-task"],
    category: "Recommendation & ML",
  },
  "meta-reels-golden": {
    description:
      "Meta MLSD canonical Reels golden 45min walkthrough: pacing + 4 strong moments + multimodal lifecycle + DLRM + multi-task heads + IPS-vs-exploration + watch-ratio retention metric",
    difficulty: "Hard",
    tags: ["Meta", "MLSD", "Reels", "Multimodal", "DLRM"],
    category: "ML System Design",
  },
  "meta-top3-comments-golden": {
    description:
      "Meta MLSD Top-3 Comments selection golden 45min walkthrough: intra-item ranking + set selection + 3 unique twists (comment≠item / time-bias / community health) + MMOE + shallow bias tower + shadow logging + list-level A/B",
    difficulty: "Hard",
    tags: ["Meta", "MLSD", "Top-K", "Selection Bias", "List-level"],
    category: "ML System Design",
  },
  "pinterest-system-design-concepts": {
    description:
      "Pinterest 核心概念与术语 deep-dive 索引: 多任务排序架构 (MMoE/PLE/DLRM/DCN-v2)、检索与 ANN (HNSW/IVF/Faiss)、LTR 方法、评估指标、纠偏与 LLM 微调、基础设施与业务 KPI、Pinterest 专属系统 (PinSAGE/SearchSAGE/Catalog)。",
    difficulty: "Hard",
    tags: ["Concepts", "Glossary", "Index"],
    category: "Pinterest",
  },
  "pinterest-ad-ctr": {
    description:
      "Pinterest ad CTR prediction: feature engineering for pins/users/context, GBDT vs deep model tradeoffs, calibration, online learning loop, exploration via Thompson sampling.",
    difficulty: "Hard",
    tags: ["CTR", "Ads", "GBDT"],
    category: "Pinterest",
  },
  "pinterest-embeddings": {
    description:
      "Pinterest user & pin embeddings: PinSAGE graph neural net, two-tower retrieval, embedding refresh cadence, ANN serving infrastructure, A/B evaluation of embedding quality.",
    difficulty: "Hard",
    tags: ["Embeddings", "GNN", "Two-Tower"],
    category: "Pinterest",
  },
  "pinterest-chatbot-pins": {
    description:
      "Pinterest personalized chat bot for pin discovery: LLM-driven pin retrieval, multi-turn context, RAG over pin metadata, latency budget, hallucination mitigation, evaluation harness.",
    difficulty: "Hard",
    tags: ["LLM", "RAG", "Chatbot"],
    category: "Pinterest",
  },
  "pinterest-pin-ranking": {
    description:
      "Pinterest home/topic feed ranking: multi-objective ranking (engagement + retention + creator diversity), MMoE/PLE multi-task, position-bias correction, cold-start strategies.",
    difficulty: "Hard",
    tags: ["Ranking", "Multi-task", "MMoE"],
    category: "Pinterest",
  },
  "pinterest-pins-search": {
    description:
      "Pinterest pins search engine: query understanding, dense + lexical retrieval hybrid, image-text cross-modal, learning-to-rank, query rewriting and intent classification.",
    difficulty: "Hard",
    tags: ["Search", "Cross-modal", "LTR"],
    category: "Pinterest",
  },
  "pinterest-notification-reco": {
    description:
      "Pinterest notification recommendation: which pin/topic to push to which user when. Frequency capping, fatigue modeling, downstream engagement attribution, multi-channel arbitration (push/email/in-app).",
    difficulty: "Medium",
    tags: ["Notifications", "Recommendation", "Frequency Cap"],
    category: "Pinterest",
  },
  "pinterest-catalog-bulk-update": {
    description:
      "Pinterest catalog bulk update at 500M records: scaling Solr/ElasticSearch ingestion, idempotent upsert, partial-update vs full-rebuild tradeoffs, indexing latency SLAs, dead-letter handling.",
    difficulty: "Medium",
    tags: ["Bulk Ingest", "Solr", "Indexing"],
    category: "Pinterest",
  },
};

const DIFFICULTY_COLORS: Record<Difficulty, string> = {
  Easy: "bg-green-100 text-green-700",
  Medium: "bg-yellow-100 text-yellow-700",
  Hard: "bg-red-100 text-red-700",
};

type Tab =
  | "interview"
  | "ml-mlsd"
  | "ebay"
  | "pinterest"
  | "ml-infra-llm"
  | "cheatsheet";

/**
 * Short category badge for a cheat-sheet row, derived from the same
 * display_order bands the rest of this page partitions tabs by. Keeps the
 * badge consistent with tab membership without needing a DB `category` column
 * (category is a frontend-only concept here -- see TOPIC_META).
 */
function cheatSheetCategory(item: SystemDesignCheatSheet): string {
  if (item.display_order < 100) return "eBay";
  if (item.display_order >= 130 && item.display_order < 199) return "ML MLSD";
  if (item.display_order >= 199 && item.display_order < 300) return "Pinterest";
  if (item.display_order >= 300 && item.display_order < 400) return "ML Infra";
  if (item.slug.includes("uber")) return "Uber";
  return "Generic";
}

export default function SystemDesignList() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = (searchParams.get("tab") as Tab) || "interview";
  const [activeTab, setActiveTab] = useState<Tab>(initialTab);

  const {
    data: modules = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["system-designs"],
    queryFn: () => api.get<SystemDesignSummary[]>("/system-designs"),
  });

  // eBay projects: display_order < 100
  const ebayModules = useMemo(
    () =>
      [...modules]
        .filter((m) => m.display_order < 100)
        .sort((a, b) => a.display_order - b.display_order),
    [modules],
  );

  // Interview topics: display_order in [100, 130), grouped by category.
  // Range bumped from [100, 199) to [100, 130) in T-P0-860 to carve out
  // [130, 199) for the ML System Design tab (Meta MLSD golden walkthroughs).
  // Pinterest 199-206 (concept index doc at 199; SD docs at 200..206) is a
  // separate tab to avoid interleaving with general interview prep.
  const interviewTopics = useMemo(() => {
    const topics = modules.filter(
      (m) => m.display_order >= 100 && m.display_order < 130,
    );
    const grouped: Record<string, SystemDesignSummary[]> = {};
    for (const cat of CATEGORY_ORDER) {
      grouped[cat] = [];
    }
    for (const topic of topics) {
      const meta = TOPIC_META[topic.slug];
      const cat = meta?.category ?? "Specialized";
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(topic);
    }
    for (const cat of Object.keys(grouped)) {
      grouped[cat].sort((a, b) => a.display_order - b.display_order);
    }
    return grouped;
  }, [modules]);

  // Pinterest topics: display_order in [199, 300) (concept index doc at 199; 7
  // SD docs at 200..206), separate section sorted at bottom. Upper bound 300
  // added in T-P1-908 to carve out [300, 400) for the ML Infra · LLM tab so
  // the new band does NOT leak into the Pinterest tab.
  const pinterestTopics = useMemo(() => {
    const topics = modules.filter(
      (m) => m.display_order >= 199 && m.display_order < 300,
    );
    const grouped: Record<string, SystemDesignSummary[]> = {};
    for (const cat of PINTEREST_CATEGORY_ORDER) {
      grouped[cat] = [];
    }
    for (const topic of topics) {
      const meta = TOPIC_META[topic.slug];
      const cat = meta?.category ?? "Pinterest";
      if (!grouped[cat]) grouped[cat] = [];
      grouped[cat].push(topic);
    }
    for (const cat of Object.keys(grouped)) {
      grouped[cat].sort((a, b) => a.display_order - b.display_order);
    }
    return grouped;
  }, [modules]);

  // ML System Design modules: display_order in [130, 199) -- Meta MLSD golden
  // walkthroughs (Reels at 130, Top-3 Comments at 131, room for future
  // additions up to 198). Flat card list, no category subdivision.
  const mlMlsdModules = useMemo(
    () =>
      [...modules]
        .filter((m) => m.display_order >= 130 && m.display_order < 199)
        .sort((a, b) => a.display_order - b.display_order),
    [modules],
  );

  // ML Infra · LLM modules: display_order in [300, 400) -- Anthropic
  // ML-Infra LLM system-design problems (carved out in T-P1-908). Flat card
  // list, no category subdivision, mirroring the ml-mlsd render.
  const mlInfraModules = useMemo(
    () =>
      [...modules]
        .filter((m) => m.display_order >= 300 && m.display_order < 400)
        .sort((a, b) => a.display_order - b.display_order),
    [modules],
  );

  const interviewCount = useMemo(
    () => modules.filter((m) => m.display_order >= 100 && m.display_order < 130).length,
    [modules],
  );
  const mlMlsdCount = useMemo(
    () => modules.filter((m) => m.display_order >= 130 && m.display_order < 199).length,
    [modules],
  );
  const pinterestCount = useMemo(
    () =>
      modules.filter((m) => m.display_order >= 199 && m.display_order < 300)
        .length,
    [modules],
  );
  const mlInfraCount = useMemo(
    () =>
      modules.filter((m) => m.display_order >= 300 && m.display_order < 400)
        .length,
    [modules],
  );

  // Cheat Sheet tab: all modules with their one-pager `cheat_sheet`, fetched
  // from the dedicated aggregate endpoint (separate from the summary list so
  // the markdown payload only loads when this tab is used).
  const {
    data: cheatSheets = [],
    isLoading: cheatSheetsLoading,
    error: cheatSheetsError,
  } = useQuery({
    queryKey: ["system-design-cheat-sheets"],
    queryFn: () =>
      api.get<SystemDesignCheatSheet[]>("/system-designs/cheat-sheets"),
  });

  const cheatSheetItems = useMemo(
    () =>
      [...cheatSheets].sort((a, b) => a.display_order - b.display_order),
    [cheatSheets],
  );

  // Deep-link support: when landing on ?tab=cheatsheet#<slug> (or jumping via
  // the TOC), scroll the matching card into view once data has rendered.
  useEffect(() => {
    if (activeTab !== "cheatsheet" || cheatSheetItems.length === 0) return;
    const slug = location.hash.replace(/^#/, "");
    if (!slug) return;
    const el = document.getElementById(slug);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [activeTab, cheatSheetItems, location.hash]);

  const scrollToCard = (slug: string) => {
    const el = document.getElementById(slug);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    // Keep the URL shareable (?tab=cheatsheet#<slug>) without a full reload.
    navigate({ search: "?tab=cheatsheet", hash: slug }, { replace: true });
  };

  const switchTab = (tab: Tab) => {
    setActiveTab(tab);
    setSearchParams(tab === "interview" ? {} : { tab });
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">System Design</h1>

      {/* Tab navigation */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => switchTab("interview")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "interview"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          Interview Prep
        </button>
        <button
          onClick={() => switchTab("ml-mlsd")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "ml-mlsd"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          ML System Design
        </button>
        <button
          onClick={() => switchTab("ebay")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "ebay"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          eBay Projects
        </button>
        <button
          onClick={() => switchTab("pinterest")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "pinterest"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          Pinterest
        </button>
        <button
          onClick={() => switchTab("ml-infra-llm")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "ml-infra-llm"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          ML Infra · LLM
        </button>
        <button
          onClick={() => switchTab("cheatsheet")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "cheatsheet"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          Cheat Sheet
        </button>
      </div>

      {/* Interview Prep tab */}
      {activeTab === "interview" && (
        <div>
          <p className="text-sm text-gray-600 mb-6">
            {interviewCount} system design interview questions, grouped by
            category (ML System Design and Pinterest in their own tabs).
            Click any topic for the full study guide.
          </p>

          {isLoading && (
            <div className="text-gray-500 py-12 text-center">Loading...</div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
              {error instanceof Error
                ? error.message
                : "Failed to load topics"}
            </div>
          )}

          {!isLoading &&
            !error &&
            CATEGORY_ORDER.map((category) => {
              const topics = interviewTopics[category];
              if (!topics || topics.length === 0) return null;
              return (
                <div key={category} className="mb-8">
                  <h2 className="text-lg font-semibold text-gray-700 mb-3 border-b border-gray-100 pb-1">
                    {category}
                  </h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {topics.map((topic) => {
                      const meta = TOPIC_META[topic.slug];
                      const difficulty = meta?.difficulty ?? "Medium";
                      const tags = meta?.tags ?? [];
                      const description =
                        meta?.description ?? topic.subtitle ?? "";
                      return (
                        <div
                          key={topic.slug}
                          className="bg-white rounded-lg border border-gray-200 px-4 py-3 cursor-pointer hover:border-blue-400 hover:shadow-md transition-all"
                          onClick={() =>
                            navigate(`/system-design/${topic.slug}`)
                          }
                        >
                          <div className="flex items-center justify-between mb-1">
                            <h3 className="text-base font-semibold text-gray-800">
                              {topic.title}
                            </h3>
                            <span
                              className={`text-xs font-medium px-2 py-0.5 rounded shrink-0 ml-2 ${DIFFICULTY_COLORS[difficulty]}`}
                            >
                              {difficulty}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mb-2">
                            {description}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {tags.map((tag) => (
                              <span
                                key={tag}
                                className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* ML System Design tab -- Meta MLSD golden walkthroughs (do 130..198).
          Flat card grid (no category subdivision); two cards initially:
          Reels Golden (130) and Top-3 Comments Golden (131). */}
      {activeTab === "ml-mlsd" && (
        <div>
          <p className="text-sm text-gray-600 mb-6">
            {mlMlsdCount} Meta MLSD golden walkthroughs (45min full-set
            simulations). Reels = cross-item engagement framing; Top-3 Comments
            = intra-item ranking + set selection family.
          </p>

          {isLoading && (
            <div className="text-gray-500 py-12 text-center">Loading...</div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
              {error instanceof Error
                ? error.message
                : "Failed to load topics"}
            </div>
          )}

          {!isLoading && !error && mlMlsdModules.length === 0 && (
            <div className="text-gray-400 py-12 text-center">
              No ML System Design modules yet.
            </div>
          )}

          {!isLoading && !error && mlMlsdModules.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {mlMlsdModules.map((topic) => {
                const meta = TOPIC_META[topic.slug];
                const difficulty = meta?.difficulty ?? "Medium";
                const tags = meta?.tags ?? [];
                const description =
                  meta?.description ?? topic.subtitle ?? "";
                return (
                  <div
                    key={topic.slug}
                    className="bg-white rounded-lg border border-gray-200 px-4 py-3 cursor-pointer hover:border-blue-400 hover:shadow-md transition-all"
                    onClick={() =>
                      navigate(`/system-design/${topic.slug}`)
                    }
                  >
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="text-base font-semibold text-gray-800">
                        {topic.title}
                      </h3>
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded shrink-0 ml-2 ${DIFFICULTY_COLORS[difficulty]}`}
                      >
                        {difficulty}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-2">{description}</p>
                    <div className="flex flex-wrap gap-1">
                      {tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* eBay Projects tab */}
      {activeTab === "ebay" && (
        <div>
          <blockquote className="border-l-4 border-blue-400 bg-blue-50 rounded-r-lg px-5 py-4 mb-2 text-sm text-gray-700 leading-relaxed italic">
            {EBAY_NARRATIVE}
          </blockquote>
          <p className="text-xs text-gray-400 mb-8">{READING_ORDER}</p>

          {/* Error state */}
          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
              {error instanceof Error
                ? error.message
                : "Failed to load modules"}
            </div>
          )}

          {/* Loading state */}
          {isLoading && (
            <div className="text-gray-500 py-12 text-center">Loading...</div>
          )}

          {/* Empty state */}
          {!isLoading && !error && ebayModules.length === 0 && (
            <div className="text-gray-400 py-12 text-center">
              No system design modules yet.
            </div>
          )}

          {/* 2x2 card grid */}
          {!isLoading && ebayModules.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {ebayModules.map((mod) => (
                <button
                  key={mod.id}
                  onClick={() => navigate(`/system-design/${mod.slug}`)}
                  className="text-left bg-white rounded-lg shadow hover:shadow-md transition-shadow border border-gray-200 overflow-hidden"
                >
                  {mod.diagram_filename && (
                    <div
                      className="w-full bg-gray-50 flex items-center justify-center"
                      style={{ height: 200 }}
                    >
                      <ImageLightbox
                        src={`/static/system-designs/${mod.diagram_filename}`}
                        alt={`${mod.title} diagram`}
                        className="max-h-full max-w-full object-contain"
                      />
                    </div>
                  )}
                  <div className="px-4 py-3">
                    <h2 className="text-lg font-semibold text-gray-800">
                      {mod.title}
                    </h2>
                    {mod.subtitle && (
                      <p className="text-sm text-gray-500 mt-1">
                        {mod.subtitle}
                      </p>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Pinterest tab — separated from general interview prep so it doesn't
          interfere with the main study list. Sorted at display_order 199+
          (concept index doc at 199; 7 SD docs at 200..206). */}
      {activeTab === "pinterest" && (
        <div>
          <p className="text-sm text-gray-600 mb-6">
            {pinterestCount} Pinterest-specific system design modules (former
            interviewer cycle prep). Kept separate from general interview prep.
          </p>

          {isLoading && (
            <div className="text-gray-500 py-12 text-center">Loading...</div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
              {error instanceof Error
                ? error.message
                : "Failed to load topics"}
            </div>
          )}

          {!isLoading &&
            !error &&
            PINTEREST_CATEGORY_ORDER.map((category) => {
              const topics = pinterestTopics[category];
              if (!topics || topics.length === 0) return null;
              return (
                <div key={category} className="mb-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {topics.map((topic) => {
                      const meta = TOPIC_META[topic.slug];
                      const difficulty = meta?.difficulty ?? "Medium";
                      const tags = meta?.tags ?? [];
                      const description =
                        meta?.description ?? topic.subtitle ?? "";
                      return (
                        <div
                          key={topic.slug}
                          className="bg-white rounded-lg border border-gray-200 px-4 py-3 cursor-pointer hover:border-blue-400 hover:shadow-md transition-all"
                          onClick={() =>
                            navigate(`/system-design/${topic.slug}`)
                          }
                        >
                          <div className="flex items-center justify-between mb-1">
                            <h3 className="text-base font-semibold text-gray-800">
                              {topic.title}
                            </h3>
                            <span
                              className={`text-xs font-medium px-2 py-0.5 rounded shrink-0 ml-2 ${DIFFICULTY_COLORS[difficulty]}`}
                            >
                              {difficulty}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 mb-2">
                            {description}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {tags.map((tag) => (
                              <span
                                key={tag}
                                className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* ML Infra · LLM tab -- Anthropic ML-Infra LLM system-design problems
          (display_order 300..399). Flat card grid (no category subdivision),
          mirroring the ml-mlsd render. */}
      {activeTab === "ml-infra-llm" && (
        <div>
          <p className="text-sm text-gray-600 mb-6">
            {mlInfraCount} ML Infra · LLM system-design problems (Anthropic-style
            LLM infrastructure deep-dives). Kept separate from general interview
            prep.
          </p>

          {isLoading && (
            <div className="text-gray-500 py-12 text-center">Loading...</div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
              {error instanceof Error
                ? error.message
                : "Failed to load topics"}
            </div>
          )}

          {!isLoading && !error && mlInfraModules.length === 0 && (
            <div className="text-gray-400 py-12 text-center">
              No ML Infra · LLM modules yet.
            </div>
          )}

          {!isLoading && !error && mlInfraModules.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {mlInfraModules.map((topic) => {
                const meta = TOPIC_META[topic.slug];
                const difficulty = meta?.difficulty ?? "Medium";
                const tags = meta?.tags ?? [];
                const description =
                  meta?.description ?? topic.subtitle ?? "";
                return (
                  <div
                    key={topic.slug}
                    className="bg-white rounded-lg border border-gray-200 px-4 py-3 cursor-pointer hover:border-blue-400 hover:shadow-md transition-all"
                    onClick={() =>
                      navigate(`/system-design/${topic.slug}`)
                    }
                  >
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="text-base font-semibold text-gray-800">
                        {topic.title}
                      </h3>
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded shrink-0 ml-2 ${DIFFICULTY_COLORS[difficulty]}`}
                      >
                        {difficulty}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-2">{description}</p>
                    <div className="flex flex-wrap gap-1">
                      {tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Cheat Sheet tab -- vertically-stacked one-pager per module (NOT a
          grid), sorted by display_order, with a desktop sticky TOC sidebar for
          quick jumps. Deep-linkable via ?tab=cheatsheet#<slug>. */}
      {activeTab === "cheatsheet" && (
        <div>
          <p className="text-sm text-gray-600 mb-6">
            One-pager cheat sheets for all {cheatSheetItems.length} system-design
            modules, in study order. Use the sidebar to jump; click "Full design
            -&gt;" for the complete write-up.
          </p>

          {cheatSheetsLoading && (
            <div className="text-gray-500 py-12 text-center">Loading...</div>
          )}

          {cheatSheetsError && (
            <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4">
              {cheatSheetsError instanceof Error
                ? cheatSheetsError.message
                : "Failed to load cheat sheets"}
            </div>
          )}

          {!cheatSheetsLoading &&
            !cheatSheetsError &&
            cheatSheetItems.length === 0 && (
              <div className="text-gray-400 py-12 text-center">
                No cheat sheets yet.
              </div>
            )}

          {!cheatSheetsLoading &&
            !cheatSheetsError &&
            cheatSheetItems.length > 0 && (
              <div className="lg:flex lg:gap-6 lg:items-start">
                {/* Desktop-only sticky TOC sidebar */}
                <aside className="hidden lg:block lg:w-56 shrink-0">
                  <nav className="sticky top-6 max-h-[calc(100vh-3rem)] overflow-y-auto border-r border-gray-100 pr-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">
                      Cheat Sheets
                    </p>
                    <ul className="space-y-1">
                      {cheatSheetItems.map((item) => (
                        <li key={item.slug}>
                          <a
                            href={`#${item.slug}`}
                            onClick={(e) => {
                              e.preventDefault();
                              scrollToCard(item.slug);
                            }}
                            className="block text-sm text-gray-600 hover:text-blue-600 truncate py-0.5"
                            title={item.title}
                          >
                            {item.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </nav>
                </aside>

                {/* Stacked one-pager cards */}
                <div className="flex-1 min-w-0 space-y-6">
                  {cheatSheetItems.map((item) => (
                    <CheatSheetCard
                      key={item.slug}
                      item={item}
                      category={cheatSheetCategory(item)}
                    />
                  ))}
                </div>
              </div>
            )}
        </div>
      )}
    </div>
  );
}
