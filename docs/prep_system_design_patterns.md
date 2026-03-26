# System Design Practical Patterns (Alex Xu SD Interview)

## Overview

Alex Xu's System Design Interview series distills practical patterns for designing large-scale systems. Unlike DDIA's theoretical foundations, this material focuses on the interview process itself: the 4-step framework, back-of-envelope estimation, scaling recipes, and concrete design walkthroughs (rate limiters, news feeds, chat systems, autocomplete, video pipelines, cloud storage). Mastering these patterns lets you structure any system design answer with confidence.

## Core Concepts

### The 4-Step System Design Framework

Every system design interview follows this structure:

| Step | Time | Goal |
|------|------|------|
| 1. Clarify requirements | 3-10 min | Scope features, users, scale, tech constraints |
| 2. High-level design | 10-15 min | Box diagram, API sketch, data flow, back-of-envelope |
| 3. Deep dive | 10-25 min | Drill into 1-2 critical components the interviewer cares about |
| 4. Wrap up | 3-5 min | Bottlenecks, improvements, error handling, next scale curve |

Key behaviors:
- Never jump straight to a solution -- ask clarifying questions first
- Draw box diagrams: clients, load balancer, API servers, caches, databases, message queues, CDN
- Treat the interviewer as a teammate; propose alternatives, solicit feedback early
- Prioritize deep-dive topics that demonstrate your strongest skills

### Back-of-Envelope Estimation

**Powers of two (byte units)**:

| Symbol | Power | Approximate |
|--------|-------|-------------|
| KB | $2^{10}$ | 1 thousand bytes |
| MB | $2^{20}$ | 1 million bytes |
| GB | $2^{30}$ | 1 billion bytes |
| TB | $2^{40}$ | 1 trillion bytes |
| PB | $2^{50}$ | 1 quadrillion bytes |

**Common latency numbers**:

| Operation | Time |
|-----------|------|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 100 ns |
| Main memory reference | 100 ns |
| Compress 1 KB (Zippy) | 10 us |
| Send 2 KB over 1 Gbps network | 20 us |
| Read 1 MB sequentially from memory | 250 us |
| Round trip within same datacenter | 500 us |
| Disk seek | 10 ms |
| Read 1 MB sequentially from network | 10 ms |
| Read 1 MB sequentially from disk | 30 ms |
| Send packet CA to Netherlands and back | 150 ms |

Rules of thumb: avoid disk seeks; simple compression is fast; compress before sending over network; cross-datacenter roundtrips are expensive.

**Availability SLA nines**:

| Availability | Downtime/year |
|-------------|---------------|
| 99% (two nines) | 3.65 days |
| 99.9% | 8.77 hours |
| 99.99% | 52.6 minutes |
| 99.999% | 5.26 minutes |

**Estimation recipe** (Twitter example):
- 300M MAU, 50% DAU = 150M DAU
- 2 tweets/user/day: QPS = $150M \times 2 / 86400 \approx 3500$; Peak QPS $\approx 7000$
- 10% tweets have media (1 MB avg): daily storage = $150M \times 2 \times 0.1 \times 1\text{MB} = 30\text{TB/day}$
- 5-year storage: $\approx 55\text{PB}$

### Scaling Ladder: Zero to Millions

The canonical progression for scaling a web application:

1. **Single server** -- web + DB + cache on one machine
2. **Separate database** -- move DB to its own server (first scaling step)
3. **Load balancer** -- distribute traffic across multiple web servers; use private IPs
4. **Database replication** -- master (writes) + slaves (reads); higher read-to-write ratio means more slaves
5. **Cache layer** -- read-through cache (check cache first, fall back to DB); Redis or Memcached with LRU/LFU eviction
6. **CDN** -- geographically dispersed servers for static assets; pay-per-transfer, set TTL, invalidate via API or object versioning
7. **Stateless web tier** -- store session data in shared persistent storage (Redis/NoSQL); enables auto-scaling
8. **Multiple data centers** -- geoDNS routing; replicate data across regions; challenges: traffic redirection, data sync, consistent deployment
9. **Message queues** -- decouple producers/consumers for independent scaling; durable, asynchronous
10. **Database sharding** -- split data across servers by shard key; use consistent hashing to minimize reshuffling

**Cache considerations**: use for read-heavy, write-infrequent data; set expiration policies; keep cache and DB in sync; overprovision memory; use eviction policies (LRU, LFU, FIFO).

**Sharding challenges**: celebrity/hotspot keys (dedicate shards), cross-shard joins (denormalize), resharding (consistent hashing with virtual nodes).

### Rate Limiting Algorithms

| Algorithm | Mechanism | Pros | Cons | Parameters |
|-----------|-----------|------|------|------------|
| Token bucket | Refill tokens at fixed rate; each request consumes one token | Simple, memory-efficient, allows short bursts | Needs tuning of two params | Bucket capacity, refill rate |
| Leaking bucket | FIFO queue with constant outflow rate | Stable output rate, memory-efficient | Burst traffic fills queue with old requests | Bucket capacity, outflow rate |
| Fixed window counter | Count requests per fixed time window | Simple, memory-efficient | Boundary burst problem -- can allow 2x quota at window edges | Window size, max count |
| Sliding window log | Track timestamps of each request in sorted set | Precise, no boundary burst | High memory (stores every timestamp) | Window size, max count |
| Sliding window counter | Weighted average of current + previous window counts | Memory-efficient, smooths spikes | Approximate (soft enforcement) | Window size, max count |

**Architecture**: Client -> Rate limiter middleware -> API servers. Counter stored in Redis (INCR + EXPIRE). Return HTTP 429 with headers: `X-Ratelimit-Remaining`, `X-Ratelimit-Limit`, `X-Ratelimit-Retry-After`.

**Distributed challenges**:
- Race condition: concurrent reads produce stale counter. Fix with Redis Lua scripts (atomic ZINCRBY) or sorted sets
- Synchronization: multiple rate limiters need shared state; use centralized Redis, avoid sticky sessions (not scalable)

### Consistent Hashing

Map both servers and keys onto a hash ring (range $[0, 2^{160}-1]$). A key is assigned to the first server found clockwise.

**Virtual nodes**: map each physical server to multiple positions on the ring. Benefits:
- Even distribution regardless of server count
- Adding/removing a server only affects neighboring keys
- Heterogeneous capacity: more virtual nodes for more powerful servers

Used in: Amazon Dynamo, Apache Cassandra, Discord, CDN systems.

### Fanout Strategies (News Feed)

| Strategy | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| Fanout on write (push) | Pre-compute feed at publish time; write to all followers' caches | Fast reads, real-time delivery | Slow for users with many followers (hotkey); wastes resources for inactive users |
| Fanout on read (pull) | Compute feed on demand when user loads page | No hotkey problem; saves resources for inactive users | Slow reads |
| Hybrid | Push for normal users; pull for celebrities | Best of both worlds | More complex |

**News feed cache hierarchy** (5 tiers):
1. News Feed (post IDs)
2. Content (hot cache + normal)
3. Social Graph (follower/following)
4. Actions (likes, replies)
5. Counters (like count, reply count)

### Unique ID Generation in Distributed Systems

| Approach | Bits | Pros | Cons |
|----------|------|------|------|
| Multi-master replication | N/A | Simple | IDs not time-sorted; hard to scale across DCs |
| UUID | 128 | No coordination; easy to scale | Not 64-bit; not time-sorted; non-numeric |
| Ticket server (centralized auto-increment) | 64 | Simple, numeric | Single point of failure |
| Twitter Snowflake | 64 | Time-sorted, scalable, numeric | Clock sync needed |

**Snowflake ID structure** (64 bits):
- 1 bit: sign (always 0)
- 41 bits: timestamp (ms since epoch) -- supports ~69 years
- 5 bits: datacenter ID (32 datacenters)
- 5 bits: machine ID (32 machines per DC)
- 12 bits: sequence number (4096 IDs per ms per machine)

### URL Shortener Design

**Estimation**: 100M URLs/day; write QPS $\approx 1160$; read $\approx 10\times$ write; 10 years $\approx 365$B records; storage $\approx 365$ TB.

**Hash value space**: characters from $[0\text{-}9, a\text{-}z, A\text{-}Z]$ = 62 chars. Need $n$ where $62^n \ge 365B$; $n=7$ suffices.

**Two approaches**:
1. **Hash + collision resolution**: Apply CRC32/MD5/SHA-1, take first 7 chars. On collision, append predefined string and retry. Use Bloom filter to speed up existence checks.
2. **Base-62 conversion**: Convert unique numeric ID to base-62 string. Fixed-length not guaranteed but deterministic. Security concern: next URL is predictable.

**Redirect codes**: 301 (permanent -- browser caches, reduces server load) vs 302 (temporary -- enables click tracking and analytics).

### Chat System Design

**Protocol selection for message delivery**:

| Protocol | Direction | Behavior |
|----------|-----------|----------|
| HTTP (sender side) | Client -> server | Standard request/response with keep-alive |
| Polling | Client -> server | Periodic checks; simple but wasteful |
| Long polling | Client -> server | Hold connection until message or timeout; drawback: sender/receiver may hit different servers |
| WebSocket | Bidirectional | Persistent, full-duplex; starts as HTTP then upgrades; works through firewalls on port 80/443 |

**Architecture components**:
- Stateless services: login, signup, profiles -- behind load balancer
- Stateful service: chat server maintaining WebSocket connections -- use service discovery (e.g., ZooKeeper) to assign clients
- KV store (HBase, Cassandra) for chat history: low latency, horizontal scaling, handles long-tail data well
- Presence servers: online/offline status with heartbeat mechanism

**Message flow (1-on-1)**: User A sends message -> chat server gets message ID from generator -> stores in KV store -> if User B online, forward via B's chat server; if offline, push notification.

**Group chat**: copy message to each member's sync queue (works for small groups; WeChat limits to 500 members).

**Multi-device sync**: each device maintains `cur_max_message_id`; fetch new messages with ID > local max.

**Online presence**: heartbeat-based detection avoids toggling on transient disconnects. Use pub/sub for status fanout to friends. For large groups, fetch status on-demand only.

### Autocomplete System (Trie)

**Data structure**: prefix tree where each node stores a character (26 children for lowercase). Augmented with frequency counts and cached top-K results at each node.

**Complexity after optimization**:
- Find prefix: $O(1)$ (bounded prefix length, e.g., 50 chars)
- Retrieve top-K from cache: $O(1)$
- Cache miss fallback: $O(c \log c)$ where $c$ = number of children

**Data pipeline**:
```
Analytics Logs -> Aggregators -> Aggregated Records -> Workers -> Trie DB -> Trie Cache
```
- Trie rebuilt weekly (or shorter intervals for real-time needs like Twitter)
- Trie DB options: document store (MongoDB -- serialized trie) or KV store (prefix as key)

**Query optimization**:
- AJAX requests (no full page refresh)
- Browser caching (1-hour TTL for suggestions)
- Data sampling (log only a fraction of queries)

**Scaling**: shard by first character; use historical distribution for smarter sharding (e.g., combine u-z into one shard).

### Video Streaming Pipeline (YouTube)

**Upload flow**: Client -> Load Balancer -> API Servers -> Original Blob Storage -> Transcoding Servers -> Transcoded Storage -> CDN.

**Transcoding pipeline (DAG-based)**:
1. **Preprocessor**: split video into GoP (Group of Pictures) chunks; generate DAG config; cache in temp storage
2. **DAG Scheduler**: split DAG into stages; enqueue tasks to resource manager
3. **Resource Manager**: task queue + worker queue + running queue + task scheduler (picks optimal task-worker pairs)
4. **Task Workers**: specialized workers for encoding, thumbnails, watermarks, merging

**Streaming protocols**: MPEG-DASH, Apple HLS, Microsoft Smooth Streaming, Adobe HDS.

**Optimizations**:
- Parallel chunk upload (resumable)
- Pre-signed upload URLs for security (S3 pre-signed / Azure Shared Access Signature)
- Decouple pipeline stages with message queues for parallelism
- DRM + AES encryption + visual watermarking for content protection
- CDN cost optimization: popular videos on CDN, others on high-capacity storage servers; encode less popular content on demand

### Cloud Storage Design (Google Drive)

**Block-level sync**: split files into blocks (max 4 MB each), each with a unique hash. Only sync modified blocks (**delta sync**). Compress (gzip/bzip2), encrypt, then upload.

**Architecture components**:
- Block servers: split, compress, encrypt, upload blocks to cloud storage
- Cloud storage: S3 or equivalent, replicated across regions
- Metadata DB: relational (for ACID strong consistency) -- stores users, files, blocks, versions
- Notification service: long polling (server does not need to receive from clients; updates infrequent)
- Offline backup queue: queue changes for offline clients to sync later
- Cold storage: inactive data moved to cheaper storage (S3 Glacier)

**Conflict resolution**: first processed version wins; later version flagged as conflict for user to merge or overwrite.

**Save storage**: deduplicate blocks by hash; limit version count; keep valuable versions only; weight recent versions higher.

### Real-World Case Studies Summary

| System | Key Patterns |
|--------|-------------|
| Facebook (TAO) | Multi-layer caching; denormalization for cold data; graph-aware cache with leader/follower; remote markers for read-after-write consistency |
| Facebook (Memcache) | Consistent hashing; UDP for gets / TCP for updates; leases to prevent thundering herds and stale sets; pool separation for hot/cold keys; slab allocator with adaptive sizing |
| Facebook (Haystack) | Store multiple images in single large file; metadata in memory; append-only writes; write-caching strategy (cache recent uploads, not CDN misses) |
| Netflix | Hybrid recommendation (RBM + SVD++); A/B testing platform; React + Node.js + Cassandra + EC2 + Open Connect CDN |
| Amazon (Dynamo) | Consistent hashing with virtual nodes; vector clocks for versioning; sloppy quorum with hinted handoff; Merkle trees for anti-entropy; gossip protocol for failure detection; read-time conflict resolution |
| Google (GFS/BigTable) | 64 MB chunks replicated 3x; MapReduce for parallel processing; BigTable as sorted-string tables on GFS; locality groups for co-located data |
| Google Drive | Differential synchronization; locking vs event-passing vs OT trade-offs |

## Implementation

### Back-of-Envelope Estimation Framework

```python
def estimate_system_requirements(
    total_users: int,
    dau_fraction: float,
    actions_per_day: int,
    avg_payload_bytes: int,
    media_fraction: float = 0.0,
    avg_media_bytes: int = 0,
    retention_years: int = 5,
) -> dict:
    """Quick estimation for system design interviews."""
    dau = total_users * dau_fraction
    # QPS
    qps = dau * actions_per_day / 86400
    peak_qps = qps * 2
    # Storage per day
    text_storage_day = dau * actions_per_day * avg_payload_bytes
    media_storage_day = dau * actions_per_day * media_fraction * avg_media_bytes
    total_storage_day = text_storage_day + media_storage_day
    total_storage = total_storage_day * 365 * retention_years
    return {
        "dau": dau,
        "qps": round(qps),
        "peak_qps": round(peak_qps),
        "storage_per_day_gb": round(total_storage_day / 1e9, 1),
        "total_storage_tb": round(total_storage / 1e12, 1),
    }

# Example: Twitter
print(estimate_system_requirements(
    total_users=300_000_000, dau_fraction=0.5,
    actions_per_day=2, avg_payload_bytes=280,
    media_fraction=0.1, avg_media_bytes=1_000_000,
    retention_years=5,
))
# {'dau': 150000000, 'qps': 3472, 'peak_qps': 6944,
#  'storage_per_day_gb': 30.1, 'total_storage_tb': 54893.2}
```

### Rate Limiter Decision Framework

```python
def choose_rate_limiter(
    needs_burst_tolerance: bool,
    memory_constrained: bool,
    strict_enforcement: bool,
) -> str:
    """Select rate limiting algorithm based on requirements."""
    if strict_enforcement and not memory_constrained:
        return "sliding_window_log"  # Precise, high memory
    if needs_burst_tolerance and memory_constrained:
        return "token_bucket"  # Allows bursts, low memory
    if not needs_burst_tolerance:
        return "leaking_bucket"  # Constant output rate
    return "sliding_window_counter"  # Good balance

# Interview quick-reference:
# - API gateway default: token bucket (most flexible)
# - DDoS protection: leaking bucket (constant rate)
# - Billing/quota: sliding window log (precise)
# - General purpose: sliding window counter (good enough)
```

### System Design Answer Template

```python
DESIGN_TEMPLATE = {
    "step_1_clarify": [
        "What features are in scope?",
        "Web, mobile, or both?",
        "How many users / what scale?",
        "What are the most important qualities? (latency, consistency, availability)",
        "Existing tech stack or greenfield?",
    ],
    "step_2_high_level": [
        "API design (REST endpoints with params)",
        "Data model (tables, key fields, relationships)",
        "Box diagram: client -> LB -> web servers -> cache/DB -> MQ -> workers",
        "Back-of-envelope: QPS, storage, bandwidth",
    ],
    "step_3_deep_dive_candidates": [
        "Scaling bottleneck (DB sharding, cache strategy)",
        "Data consistency model (strong vs eventual)",
        "Specific algorithm (rate limiting, consistent hashing, fanout)",
        "Failure handling and retry mechanisms",
        "Security (auth, DRM, pre-signed URLs)",
    ],
    "step_4_wrap_up": [
        "Identify remaining bottlenecks",
        "Error cases and monitoring",
        "How to handle 10x growth",
        "Rollout strategy",
    ],
}
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| "Walk through designing X" | Any system design question | Follow the 4-step framework; never jump to solution |
| Estimate storage/QPS | Opening of every design | Use powers of 2; DAU -> QPS -> storage -> bandwidth |
| Scaling ladder | "How to scale from 1 to 1M users?" | Follow the 10-step progression: single server -> sharding |
| Rate limiter design | "Protect API from abuse" | Token bucket for flexibility; Redis for distributed counting |
| Fanout on write vs read | News feed, timeline, notification | Push for most users, pull for celebrities (hybrid) |
| Consistent hashing | "How to partition data?" | Virtual nodes for even distribution; minimal reshuffling |
| WebSocket vs long polling | Real-time messaging | WebSocket for bidirectional; long polling for server-push only |
| Trie with top-K cache | Autocomplete, typeahead | O(1) lookup after caching top results at each node |
| DAG pipeline | Video/audio processing | Split into stages; message queues between stages for parallelism |
| Block-level sync | File storage, cloud drive | Hash each block; delta sync only modified blocks |
| Pre-signed URLs | Secure file upload | Client gets time-limited upload URL from server |
| Snowflake ID | Distributed unique IDs | 64-bit: timestamp + DC + machine + sequence |

### Common Interview Questions

- [ ] Walk me through designing a notification system for 10M users
- [ ] How would you estimate the storage needed for a URL shortener serving 100M URLs/day?
- [ ] Design a rate limiter -- which algorithm and why?
- [ ] Fanout on write vs read: when would you choose each?
- [ ] How does consistent hashing handle adding/removing servers?
- [ ] Design a chat system supporting 50M DAU with 1-on-1 and group chat
- [ ] Design a search autocomplete system for 10M DAU
- [ ] How would you design the video upload and transcoding pipeline for YouTube?
- [ ] Design a cloud storage system like Google Drive with file versioning
- [ ] How would you handle the celebrity/hotspot problem in news feed fanout?
- [ ] Compare HTTP polling, long polling, and WebSocket for real-time communication
- [ ] How does the Twitter Snowflake ID scheme ensure uniqueness and time-ordering?

## Comparisons

### Communication Protocols for Real-Time Systems

| Aspect | HTTP Polling | Long Polling | WebSocket |
|--------|-------------|-------------|-----------|
| Direction | Client -> Server | Client -> Server | Bidirectional |
| Connection | New per request | Held until response/timeout | Persistent |
| Latency | High (polling interval) | Medium (timeout delay) | Low (instant) |
| Server resources | Wasted on empty responses | Moderate (held connections) | Efficient per connection |
| Use case | Simple status checks | Server-push only (cloud storage notifications) | Chat, gaming, real-time collaboration |

### Hash Function Approaches for URL Shortening

| Aspect | Hash + Collision Resolution | Base-62 Conversion |
|--------|----------------------------|-------------------|
| URL length | Fixed (7 chars) | Variable |
| Collision handling | Append + retry; Bloom filter | None (unique ID input) |
| Dependency | Hash function only | Needs unique ID generator |
| Predictability | Not predictable | Next URL guessable |
| Performance | Fast but collision retry possible | Always O(1) |

### Cache Eviction Policies

| Policy | Mechanism | Best For |
|--------|-----------|----------|
| LRU (Least Recently Used) | Evict least recently accessed item | General purpose; temporal locality |
| LFU (Least Frequently Used) | Evict item with lowest access count | Frequency-skewed access patterns |
| FIFO (First In First Out) | Evict oldest item | Simple; when age matters more than access pattern |

### Scaling Strategies

| Aspect | Vertical (Scale Up) | Horizontal (Scale Out) |
|--------|---------------------|----------------------|
| Mechanism | Upgrade CPU, RAM, disk | Add more servers |
| Simplicity | Simple | Complex (distributed systems) |
| Cost curve | Exponential at high end | Linear |
| Failure mode | Single point of failure | Tolerant (redundancy) |
| Hard limit | Hardware ceiling | Practically unlimited |
| Data consistency | Trivial (single node) | Requires distributed protocols |

### Database Replication Models

| Aspect | Master-Slave | Multi-Master |
|--------|-------------|-------------|
| Write target | Master only | Any master |
| Read scaling | Add slaves | Add any node |
| Consistency | Strong (single writer) | Eventual (conflict resolution needed) |
| Failover | Elect new master | Automatic |
| Use case | Read-heavy workloads | Multi-region writes |

## Key Takeaways

- [ ] The 4-step framework (clarify, high-level, deep dive, wrap up) structures any system design answer and prevents the most common mistake: jumping into implementation
- [ ] Back-of-envelope estimation is a skill, not a formula -- practice converting DAU to QPS to storage to bandwidth until it is automatic
- [ ] The scaling ladder (single server -> sharding) is a progression, not a menu -- each step addresses a specific bottleneck of the previous
- [ ] Token bucket is the most versatile rate limiting algorithm (allows bursts, simple, memory-efficient) -- default to it unless you need strict precision
- [ ] Hybrid fanout (push for normal users, pull for celebrities) is almost always the right answer for social feed systems
- [ ] WebSocket is the go-to for bidirectional real-time communication; long polling is acceptable for server-push-only scenarios
- [ ] Trie with cached top-K at each node transforms autocomplete from O(n) to O(1) -- a classic interview optimization story
- [ ] Block-level delta sync (hash each block, only transfer changed blocks) is the key insight for cloud storage efficiency
- [ ] For distributed unique IDs, the Snowflake approach (timestamp + DC + machine + sequence in 64 bits) is the industry standard answer
