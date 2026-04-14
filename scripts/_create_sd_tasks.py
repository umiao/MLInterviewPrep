"""Create 20 individual SD interview prep tasks in task_db."""
import json
import subprocess
import sys
from pathlib import Path

PROJ_ROOT = str(Path(__file__).resolve().parent.parent)

SAFETY = (
    "CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. "
    "(2) All content in Chinese with English terms preserved bold + first-use explanation. "
    "(3) Seed script = source of truth. (4) Formulas: use \\mid not |, single-line $$ blocks, "
    "blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for "
    "Chinese style and depth."
)

SECTION_GUIDE = (
    "Each topic is a new SystemDesign DB record. 8 sections adapted for interview prep:\n"
    "- overview: Problem definition + 5-8 Clarification Questions to ask interviewer (with WHY each matters). Simulate clarify strategy.\n"
    "- architecture: High-level design + core components\n"
    "- dataflow: Read/write paths + API design (REST endpoints)\n"
    "- formulas: Capacity estimation (QPS, storage, bandwidth) + core algorithm math\n"
    "- production_constraints: Scale numbers, bottlenecks, SLA targets\n"
    "- tradeoffs: 3-5 key design decisions Option A vs B vs Our Choice\n"
    "- defense: 4-5 interviewer follow-up Q&A (acknowledge-mitigate-data)\n"
    "- verbal_outline: 1h interview time allocation + step-by-step outline"
)

TOPICS = [
    ("P0", "M", "interview-url-shortener", "url_shortener", "Design a URL Shortener", 100,
     "Hash vs counter ID, Base62 encoding, 301 vs 302 redirect, read-heavy caching, analytics, expiration/TTL"),
    ("P0", "M", "interview-rate-limiter", "rate_limiter", "Design a Rate Limiter", 101,
     "Token bucket vs sliding window vs fixed window, distributed rate limiting with Redis, race conditions, rule engine, HTTP 429"),
    ("P0", "M", "interview-notification-system", "notification", "Design a Notification System", 102,
     "Push (APNs/FCM) / SMS / Email, priority queue, template engine, retry with exponential backoff + DLQ, user preferences, rate limiting per user"),
    ("P0", "M", "interview-ride-sharing", "ride_sharing", "Design a Ride-sharing System (Uber)", 103,
     "CRITICAL FOR UBER INTERVIEW. Matching algorithm, surge pricing, real-time location (WebSocket, 3-5s), geospatial indexing (Geohash/S2/H3), ETA prediction, trip state machine, payment"),
    ("P0", "M", "interview-proximity-service", "proximity_service", "Design a Proximity Service (Yelp)", 104,
     "Geohash vs QuadTree vs R-Tree, nearby search within radius, business CRUD + search, caching hot areas, read-heavy 99:1"),
    ("P0", "M", "interview-game-leaderboard", "game_leaderboard", "Design a Real-time Game Leaderboard", 105,
     "Redis Sorted Set (ZADD/ZRANK/ZRANGE), top-K, rank lookup, relative ranking, sharding for millions, daily/weekly/all-time"),
    ("P0", "M", "interview-news-feed", "news_feed", "Design a News Feed (Instagram)", 106,
     "Fan-out on write vs read (hybrid), celebrity problem, ranking (EdgeRank), media CDN, feed cache invalidation, cursor pagination"),
    ("P0", "M", "interview-chat-system", "chat_system", "Design a Chat System (Messenger/WhatsApp)", 107,
     "WebSocket management, message delivery at-least-once + dedup, online presence heartbeat, group chat, message storage, E2E encryption, read receipts"),
    ("P0", "M", "interview-live-comments", "live_comments", "Design Facebook Live Comments", 108,
     "Real-time streaming WebSocket/SSE, comment ordering, high write throughput 100K+/sec, moderation pipeline, millions concurrent viewers"),
    ("P1", "M", "interview-search-autocomplete", "search_autocomplete", "Design Search Autocomplete", 109,
     "Trie (compressed), top-K suggestions, data collection pipeline, ranking (frequency + personalization + trending), multi-level caching"),
    ("P1", "M", "interview-top-k-heavy-hitters", "top_k", "Design Top-K Heavy Hitters", 110,
     "Count-Min Sketch, Space-Saving algorithm, MapReduce, streaming vs batch, approximate vs exact, multi-level aggregation"),
    ("P1", "M", "interview-ad-click-aggregator", "ad_click", "Design an Ad Click Aggregator", 111,
     "Kafka + Flink streaming, exactly-once counting, time-window aggregation, late events + watermarks, lambda architecture, click fraud detection"),
    ("P1", "M", "interview-video-streaming", "video_streaming", "Design YouTube/Netflix Video Streaming", 112,
     "Upload + transcoding pipeline, adaptive bitrate HLS/DASH, CDN edge caching, metadata service, view counting, copyright detection"),
    ("P1", "M", "interview-cloud-storage", "cloud_storage", "Design Dropbox/Google Drive", 113,
     "Block-level chunking + dedup + delta sync, conflict resolution, metadata DB, sync notification, storage optimization, offline editing"),
    ("P1", "M", "interview-price-drop-tracker", "price_tracker", "Design a Price Drop Tracker (CamelCamelCamel)", 114,
     "Scraping pipeline, price history time-series, alert system, anti-scraping, product matching/dedup, scale to millions of products"),
    ("P1", "M", "interview-online-judge", "online_judge", "Design an Online Judge (Leetcode)", 115,
     "Code sandbox (Docker/gVisor), queue-based submission, test case runner, judge verdicts, anti-cheat MOSS, multi-language runtime"),
    ("P1", "M", "interview-ticket-reservation", "ticket_reservation", "Design Ticketmaster / Hotel Reservation", 116,
     "Seat map inventory, distributed locking for concurrent booking, payment hold TTL, overbooking, waitlist, flash sale virtual queue, idempotency"),
    ("P1", "M", "interview-web-crawler", "web_crawler", "Design a Web Crawler", 117,
     "URL frontier priority queue, distributed crawling consistent hashing, Bloom filter dedup (10B URLs ~1.2GB), robots.txt, 10K hacked machines variant = distributed hash map"),
    ("P1", "M", "interview-auction-system", "auction_system", "Design an Auction System (eBay)", 118,
     "Real-time bidding WebSocket, bid ordering monotonic timestamps, auction state machine, sniping protection soft close, payment escrow, reserve price"),
    ("P1", "M", "interview-distributed-cache", "distributed_cache", "Design a Distributed Cache", 119,
     "Consistent hashing virtual nodes, LRU/LFU/TTL eviction, cache-aside vs write-through vs write-behind, stampede prevention, hot key, invalidation"),
]


def main():
    results = []
    for priority, complexity, slug, slug_short, title, order, details in TOPICS:
        steps = (
            f"STEPS:\n"
            f"1. Read scripts/content_module_arbitration.py as REFERENCE.\n"
            f"2. Create scripts/content_interview_{slug_short}.py with the seed script.\n"
            f"3. Create SystemDesign record: slug='{slug}', title='{title}', display_order={order}.\n"
            f"4. Run seed script to populate all 8 sections.\n"
            f"5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/{slug}.\n"
            f"6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.\n\n"
            f"AC:\n"
            f"- All 8 sections filled (Chinese, 10K+ chars)\n"
            f"- Clarification Questions in overview (5-8 with reasoning)\n"
            f"- Capacity estimation in formulas\n"
            f"- 1h interview outline in verbal_outline\n"
            f"- SystemDesignList.tsx updated\n"
            f"- Seed script = source of truth\n"
            f"- No bare | in math, TypeScript clean"
        )

        desc = f"{SAFETY}\n\n{SECTION_GUIDE}\n\nTOPIC: {title} (slug={slug})\nKey concepts: {details}\n\n{steps}"

        cmd = [
            sys.executable, ".claude/hooks/task_db.py", "add",
            "--title", f"SD Prep: {title}",
            "--priority", priority,
            "--complexity", complexity,
            "--description", desc,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJ_ROOT, encoding="utf-8")
        try:
            data = json.loads(r.stdout.strip())
            results.append(f"{data['id']} [{priority}/{complexity}] {title}")
        except Exception:
            results.append(f"ERROR: {r.stdout[:80]} | {r.stderr[:80]}")

    for line in results:
        print(line)


if __name__ == "__main__":
    main()
