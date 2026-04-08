import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type { SystemDesignSummary } from "../types/system-design";
import ImageLightbox from "../components/ui/ImageLightbox";

const EBAY_NARRATIVE = `My core work at eBay has been systematically transforming search ranking from independent pointwise scoring into page-level resource allocation. Starting with the data foundation (PBE Pipeline for unbiased training data), I built the allocation framework (Ranking-as-Allocation with diversity constraints), extended it to multi-module page composition (Module Arbitration marketplace), and most recently brought GenAI into the production search path (LLM Artifact Orchestration). Each project builds on the last -- together they represent a complete evolution from 'rank items by relevance score' to 'optimize the entire user experience as a constrained allocation problem.'`;

const READING_ORDER =
  "Interview reading order: PBE Pipeline -> Ranking-as-Allocation -> Module Arbitration -> LLM Orchestration";

interface InterviewTopic {
  title: string;
  slug?: string;
  description: string;
  difficulty: "Easy" | "Medium" | "Hard";
  tags: string[];
}

const INTERVIEW_TOPICS: InterviewTopic[] = [
  {
    title: "Design a URL Shortener",
    slug: "interview-url-shortener",
    description:
      "TinyURL-style service: hash/encode long URLs, redirect, analytics, expiration. Focus on hashing strategy, collision handling, and read-heavy scaling.",
    difficulty: "Easy",
    tags: ["Hashing", "Database", "Caching"],
  },
  {
    title: "Design a Rate Limiter",
    slug: "interview-rate-limiter",
    description:
      "API gateway rate limiting: token bucket, sliding window, distributed counters. Focus on accuracy vs performance trade-offs and distributed coordination.",
    difficulty: "Medium",
    tags: ["Distributed Systems", "Redis", "API Gateway"],
  },
  {
    title: "Design a News Feed",
    slug: "interview-news-feed",
    description:
      "Social media feed generation: fan-out on write vs read (hybrid model), celebrity problem, ML ranking (EdgeRank), media CDN, feed cache invalidation, cursor pagination.",
    difficulty: "Hard",
    tags: ["Fan-out", "Ranking", "Caching"],
  },
  {
    title: "Design a Chat System",
    slug: "interview-chat-system",
    description:
      "Real-time messaging: WebSocket connections, message delivery guarantees, group chat, online presence. Focus on connection management and message ordering.",
    difficulty: "Medium",
    tags: ["WebSocket", "Message Queue", "Presence"],
  },
  {
    title: "Design a Real-time Game Leaderboard",
    slug: "interview-game-leaderboard",
    description:
      "Redis Sorted Set leaderboard: ZADD/ZREVRANK/ZREVRANGE, Top-K, rank lookup, relative ranking, Kafka peak shaving, score-range sharding for 50M+ players, daily/weekly/season boards.",
    difficulty: "Medium",
    tags: ["Redis", "Sorted Set", "Real-time"],
  },
  {
    title: "Design a Key-Value Store",
    description:
      "Distributed KV store: consistent hashing, replication, conflict resolution. Focus on CAP trade-offs, partitioning strategy, and failure handling.",
    difficulty: "Hard",
    tags: ["Distributed Systems", "Consistency", "Replication"],
  },
  {
    title: "Design a Notification System",
    slug: "interview-notification-system",
    description:
      "Multi-channel notifications: push, SMS, email. Priority queues, rate limiting per user, template rendering, delivery tracking and retry logic.",
    difficulty: "Medium",
    tags: ["Message Queue", "Priority", "Multi-channel"],
  },
  {
    title: "Design a Ride-sharing System (Uber)",
    slug: "interview-ride-sharing",
    description:
      "Real-time driver matching, location tracking, surge pricing, trip lifecycle. Focus on geospatial indexing, high-throughput location updates, and supply-demand balancing.",
    difficulty: "Hard",
    tags: ["Geospatial", "WebSocket", "Real-time"],
  },
  {
    title: "Design a Proximity Service (Yelp)",
    slug: "interview-proximity-service",
    description:
      "Nearby search: Geohash vs QuadTree vs R-Tree, radius queries, business CRUD + filtering, multi-level caching for 99:1 read-heavy workload.",
    difficulty: "Medium",
    tags: ["Geospatial", "Caching", "Read-heavy"],
  },
  {
    title: "Design a Web Crawler",
    slug: "interview-web-crawler",
    description:
      "Distributed web crawler: URL frontier, politeness, dedup, content extraction. Focus on scale, distributed coordination, and fault tolerance.",
    difficulty: "Medium",
    tags: ["Distributed Systems", "Queue", "Dedup"],
  },
  {
    title: "Design Facebook Live Comments",
    slug: "interview-live-comments",
    description:
      "Real-time comment streaming for live video: Fan-out Tree for millions of concurrent viewers, comment sampling, SSE/WebSocket, pre-moderation pipeline, reaction aggregation.",
    difficulty: "Hard",
    tags: ["Fan-out", "SSE", "Real-time", "Moderation"],
  },
  {
    title: "Design a Search Autocomplete",
    slug: "interview-search-autocomplete",
    description:
      "Typeahead suggestion: trie data structure, top-K frequent queries, real-time updates. Focus on latency requirements and data freshness.",
    difficulty: "Medium",
    tags: ["Trie", "Caching", "Ranking"],
  },
  {
    title: "Design Top-K Heavy Hitters",
    slug: "interview-top-k-heavy-hitters",
    description:
      "Count-Min Sketch + Min-Heap streaming Top-K: three-layer aggregation (local -> partition -> global), Lambda Architecture with hourly batch calibration, multi-window CMS additivity.",
    difficulty: "Hard",
    tags: ["Streaming", "Probabilistic DS", "MapReduce"],
  },
  {
    title: "Design an Ad Click Aggregator",
    slug: "interview-ad-click-aggregator",
    description:
      "Lambda Architecture for ad billing: Kafka + Flink exactly-once aggregation, two-level dedup (Bloom Filter + RocksDB), real-time fraud detection, ClickHouse OLAP, batch billing reconciliation.",
    difficulty: "Hard",
    tags: ["Streaming", "Exactly-Once", "Fraud Detection"],
  },
  {
    title: "Design YouTube/Netflix Video Streaming",
    slug: "interview-video-streaming",
    description:
      "Upload + transcoding pipeline (DAG parallel GPU transcode), ABR adaptive bitrate (HLS/DASH), three-layer CDN caching (Edge 200+ POP -> Shield -> Origin S3), multi-CDN failover, viral video handling.",
    difficulty: "Hard",
    tags: ["CDN", "Video", "Transcoding"],
  },
  {
    title: "Design Dropbox/Google Drive",
    slug: "interview-cloud-storage",
    description:
      "Block-level chunking (CDC/Rabin Fingerprint) + dedup + delta sync, conflict resolution (version vector + conflict copy), metadata DB (MySQL sharded), WebSocket sync notification, tiered storage optimization, offline editing.",
    difficulty: "Hard",
    tags: ["Storage", "Sync", "Dedup"],
  },
  {
    title: "Design a Price Drop Tracker (CamelCamelCamel)",
    slug: "interview-price-drop-tracker",
    description:
      "Scraping pipeline (proxy rotation, anti-scraping, golden tests), TimescaleDB price history (downsampling, continuous aggregates), event-driven alert evaluation (Kafka + rule engine + cooldown), Z-Score anomaly detection, dynamic scrape priority.",
    difficulty: "Medium",
    tags: ["Scraping", "Time-Series", "Alerts"],
  },
  {
    title: "Design an Online Judge (LeetCode)",
    slug: "interview-online-judge",
    description:
      "Code sandbox (gVisor/Docker + cgroups + seccomp), queue-based submission pipeline (RabbitMQ), test case runner with early termination, judge verdicts state machine, MOSS plagiarism detection (Winnowing), multi-language runtime, contest leaderboard (Redis Sorted Set).",
    difficulty: "Hard",
    tags: ["Sandbox", "Queue", "Security"],
  },
  {
    title: "Design Ticketmaster / Hotel Reservation",
    slug: "interview-ticket-reservation",
    description:
      "Seat inventory with distributed locking (SELECT FOR UPDATE SKIP LOCKED), payment hold TTL, virtual queue for flash sales, overbooking probability model, idempotent payment, waitlist notification.",
    difficulty: "Hard",
    tags: ["Concurrency", "Locking", "Queue"],
  },
  {
    title: "Design an Auction System (eBay)",
    slug: "interview-auction-system",
    description:
      "Real-time bidding via WebSocket, bid ordering with monotonic timestamps, auction state machine, sniping protection (soft close), proxy bidding engine, payment escrow, reserve price, hot auction isolation via Kafka serialization.",
    difficulty: "Hard",
    tags: ["Real-time", "Concurrency", "WebSocket"],
  },
  {
    title: "Design a Distributed Cache",
    slug: "interview-distributed-cache",
    description:
      "Consistent hashing with virtual nodes, LRU/LFU/TinyLFU eviction, cache-aside vs write-through vs write-behind, stampede prevention (singleflight), hot key mitigation (L1 + key replication), CDC-driven invalidation, Bloom Filter for penetration defense.",
    difficulty: "Hard",
    tags: ["Consistent Hashing", "Caching", "Distributed Systems"],
  },
];

const DIFFICULTY_COLORS: Record<InterviewTopic["difficulty"], string> = {
  Easy: "bg-green-100 text-green-700",
  Medium: "bg-yellow-100 text-yellow-700",
  Hard: "bg-red-100 text-red-700",
};

type Tab = "interview" | "ebay";

export default function SystemDesignList() {
  const navigate = useNavigate();
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

  const sorted = [...modules].sort(
    (a, b) => a.display_order - b.display_order,
  );

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
          onClick={() => switchTab("ebay")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "ebay"
              ? "border-blue-500 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
          }`}
        >
          eBay Projects
        </button>
      </div>

      {/* Interview Prep tab */}
      {activeTab === "interview" && (
        <div>
          <p className="text-sm text-gray-600 mb-6">
            Common system design interview questions. Content coming soon -- use
            these as a checklist to guide your preparation.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {INTERVIEW_TOPICS.map((topic) => (
              <div
                key={topic.title}
                className={`bg-white rounded-lg border border-gray-200 px-4 py-3 ${topic.slug ? "cursor-pointer hover:border-blue-400 hover:shadow-md transition-all" : "opacity-80"}`}
                onClick={
                  topic.slug
                    ? () => navigate(`/system-design/${topic.slug}`)
                    : undefined
                }
              >
                <div className="flex items-center justify-between mb-1">
                  <h2 className="text-base font-semibold text-gray-800">
                    {topic.title}
                  </h2>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded ${DIFFICULTY_COLORS[topic.difficulty]}`}
                  >
                    {topic.difficulty}
                  </span>
                </div>
                <p className="text-sm text-gray-500 mb-2">
                  {topic.description}
                </p>
                <div className="flex flex-wrap gap-1">
                  {topic.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                {!topic.slug && (
                  <p className="text-xs text-gray-400 mt-2 italic">
                    Coming Soon
                  </p>
                )}
              </div>
            ))}
          </div>
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
          {!isLoading && !error && sorted.length === 0 && (
            <div className="text-gray-400 py-12 text-center">
              No system design modules yet.
            </div>
          )}

          {/* 2x2 card grid */}
          {!isLoading && sorted.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {sorted.map((mod) => (
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
    </div>
  );
}
