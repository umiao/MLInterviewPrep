# System Design Fundamentals: Data-Intensive Applications (DDIA Ch1-9)

## Overview

Designing Data-Intensive Applications (DDIA) Part I covers the foundational building blocks of modern data systems. For MLE interviews, these chapters provide the vocabulary and mental models for discussing system trade-offs: why one storage engine over another, how to choose between data models, and what encoding format to use for inter-service communication. Mastering these fundamentals is prerequisite for tackling distributed systems design questions.

## Core Concepts

### Three Pillars of Data Systems

Every data system is evaluated along three dimensions:

**Reliability** -- the system continues to work correctly even when things go wrong.
- Fault $\ne$ failure: a fault is one component deviating from spec; a failure is the whole system stopping service
- Hardware faults: hard disks have MTTF of 10-50 years; on a 10,000-disk cluster, expect ~1 disk failure per day
- Software faults: correlated failures (bugs, resource exhaustion, cascading failures) are harder to anticipate than hardware faults
- Human error: causes ~75% of outages vs 10-25% from hardware
- Mitigation: redundancy (RAID, dual power), process isolation, crash-and-restart design, monitoring/telemetry, sandbox environments, gradual rollouts

**Scalability** -- the system can handle growth in data volume, traffic, or complexity.
- Describe load with specific parameters: requests/second, read/write ratio, simultaneously active users, cache hit rate
- Use percentiles (p50, p95, p99) rather than averages for response time -- tail latencies directly impact user experience
- Latency vs response time: latency = time waiting to be handled; response time = full client-observed time including network and queueing delays
- Head-of-line blocking: a few slow requests hold up all subsequent requests in the queue
- Scaling up (vertical) vs scaling out (horizontal) -- horizontal is usually inevitable at scale
- Tip: keep the database on a single node as long as possible; distributing stateful data is complex

**Maintainability** -- the system remains easy to work with over time.
- Operability: monitoring, automation, self-healing, good defaults, predictable behavior
- Simplicity: reduce state space explosion, tight coupling, tangled dependencies via good abstractions
- Evolvability (extensibility): design for unanticipated use cases, requirement changes, platform migrations

### Data Models

Choosing the right data model is one of the most impactful design decisions.

**Relational Model**:
- Data organized into relations (tables) with unordered tuples (rows)
- Strong support for joins, many-to-many relationships, and ACID guarantees
- Query optimizer built once benefits all applications
- Schema-on-write: enforced structure at write time (like static typing)
- Denormalization can reduce joins but requires extra work to maintain consistency

**Document Model** (NoSQL):
- Self-contained records (JSON/BSON/XML) retrieved by identifier
- Better for: high write throughput, flexible schemas, self-contained objects with few cross-references
- Schema-on-read: structure is implicit, interpreted at read time (like dynamic typing)
- Weakness: poor join support, cannot directly reference nested items, struggles with deep nesting
- Data locality advantage: entire document stored contiguously (fewer disk seeks)

**Graph Model**:
- Vertices (nodes) and edges (relationships) with properties (key-value pairs)
- Ideal when relationships are as important as the entities themselves (social networks, knowledge graphs)
- Any two vertices can be linked; labels enable multiple relationship types in one graph
- Query languages: Cypher (property graphs), SPARQL (triple-stores/RDF), Datalog (recursive rules)
- Recursive traversal is natural in graph DBs but requires complex recursive CTEs in SQL

**When to use each**:
- Relational: structured data with many-to-many relationships, need for joins and ACID
- Document: self-contained records, flexible schema, high write throughput, one-to-many dominant
- Graph: highly interconnected data, relationship-centric queries, variable-depth traversal

### Storage Engines: LSM-Tree vs B-Tree

The two dominant storage engine architectures have fundamentally different write/read trade-offs.

**LSM-Tree (Log-Structured Merge-Tree)**:
- Write path: writes go to in-memory **memtable** (red-black/AVL tree, sorted by key) -> when memtable exceeds threshold, flush to disk as immutable **SSTable** (Sorted String Table) -> background compaction merges SSTables
- Read path: check memtable first, then SSTables in reverse chronological order
- Crash recovery: Write-Ahead Log (WAL) records every write before memtable insertion
- Optimization: Bloom filters to avoid unnecessary SSTable reads; sparse indexes for range lookups
- Compaction strategies:
  - **Size-tiered**: each tier has N SSTables of similar size; when full, compact and promote to next tier (results in large SSTables at deeper levels)
  - **Leveled**: each level has a size cap with globally ordered SSTables; exceeding the limit triggers merge with next level (better read performance, more write amplification)
- Used by: LevelDB, RocksDB, Cassandra, Lucene (term dictionary)

**B-Tree**:
- Standard index in almost all relational databases
- Fixed-size pages (typically 4KB), organized as a balanced tree with branching factor of several hundred
- Depth of $O(\log n)$: a 4-level tree with branching factor 500 stores up to 256 TB
- Updates are in-place: find the leaf page, overwrite it
- Page splits: when a page overflows, split into two half-full pages and update parent references
- Crash recovery: WAL (redo log) records every modification before applying to pages
- Concurrency: requires lightweight locks (latches) for thread safety
- Optimization: copy-on-write scheme (write to new location, update parent pointers); key abbreviation for higher branching factor

**Comparison**:

| Aspect | LSM-Tree | B-Tree |
|--------|----------|--------|
| Write performance | Faster (sequential writes) | Slower (random writes, WAL + page) |
| Read performance | Slower (check multiple SSTables) | Faster (single tree traversal) |
| Write amplification | Compaction rewrites data | WAL + page write (+ splits) |
| Space efficiency | May have redundant entries until compaction | Some fragmentation from splits |
| Disk I/O pattern | Sequential (good for HDD and SSD) | Random (better with SSD) |
| Concurrency | Simple (single writer thread for log) | Complex (page-level locking) |
| Predictability | High-percentile latency can spike during compaction | More predictable latency |
| Best for | Write-heavy workloads | Read-heavy workloads |

### Indexes and Specialized Structures

**Secondary indexes**: map non-unique keys to row identifiers (list of IDs or unique composite keys). Essential for joins.

**Clustered vs non-clustered index**:
- Heap file: rows stored separately, index holds references (avoids duplication across multiple indexes)
- Clustered index: stores the actual row data within the index (e.g., MySQL InnoDB primary key)
- Covering index: stores some columns within the index to avoid heap file lookups for specific queries
- Trade-off: clustered/covering indexes speed up reads but increase storage and write overhead

**Multi-column indexes**:
- Concatenated index: combines multiple columns in fixed order (limited flexibility)
- R-tree: generalization of B-tree for multi-dimensional data (geospatial queries)
  - Uses Minimal Bounding Rectangles (MBR) for space division
  - Variants: R*-tree (re-insertion for less overlap), R+-tree (no overlap, objects in multiple leaves)

**Full-text search**: Lucene uses SSTable-like structures with finite state automaton (trie-like) in-memory index; supports fuzzy matching via edit distance.

**In-memory databases** (Redis, Memcached): faster not because they avoid disk reads (OS page cache handles that) but because they skip encoding overhead. Can support data structures (priority queues, sets) hard to implement on disk.

### OLTP vs OLAP

| Aspect | OLTP | OLAP |
|--------|------|------|
| Read pattern | Small number of records by key | Aggregate over many records |
| Write pattern | Random-access, low-latency from user input | Bulk import or event stream |
| Primary users | End users via web apps | Internal analysts for decision support |
| Data represents | Latest state of data | History of events |
| Dataset size | GB to TB | TB to PB |
| Bottleneck | Disk seek time | Disk bandwidth (scan throughput) |

**Data Warehouse**: separate read-only copy of OLTP data, optimized for analytics. ETL (Extract-Transform-Load) pipeline feeds data in.

**Star Schema** (dimensional modeling):
- Central **fact table**: each row = one event (e.g., a sale), with foreign keys to dimension tables and metric columns
- **Dimension tables**: who, what, where, when, how, why (e.g., product, store, date, customer)
- Snowflake schema: dimensions further normalized into sub-dimensions (more normalized, more joins)

**Column-Oriented Storage**:
- Store all values from each column together instead of row-by-row
- Advantage: only load columns needed for a query (fact tables often have 100+ columns but queries touch few)
- Column compression: **bitmap encoding** (one bit per possible value per row) + **run-length encoding** for sorted columns
- Sort order: sorting by a meaningful column acts as an indexing mechanism and improves compression
- Vectorized processing: compressed column chunks fit in CPU L1 cache, enabling tight loops with SIMD instructions
- Write optimization: use LSM-tree approach (accumulate in memory, batch-write sorted segments)
- **Materialized views**: pre-computed aggregates written to disk (vs virtual views which are stored queries). Higher write cost but faster reads. Data cubes (OLAP cubes) are a common form.

### Encoding and Schema Evolution

When systems evolve, old and new code coexist during rolling upgrades. Encoding formats must support:
- **Backward compatibility**: newer code reads data written by older code (easier)
- **Forward compatibility**: older code reads data written by newer code (harder -- must ignore unknown fields)

**JSON/XML**: human-readable but ambiguous types (no int/float distinction in JSON), no binary string support, verbose. MessagePack provides binary JSON encoding (~18% smaller).

**Protocol Buffers (protobuf)**:
- Schema required: fields identified by numeric **tag** (not name) + type
- Variable-length integers: top bit indicates continuation
- `repeated` marker for arrays (no dedicated list type)
- Compatibility rules: new fields must be optional with defaults; never delete required fields; never reuse deleted tag numbers
- Best for: statically-typed languages (Java, C++, C#) with code generation

**Apache Thrift**: similar to protobuf with BinaryProtocol and CompactProtocol formats; has dedicated list type.

**Avro**:
- No tag numbers -- relies on matching **writer's schema** and **reader's schema** field by field
- Schema resolution: reader translates writer's schema to reader's schema at decode time
- Schema evolution: can only add/remove fields that have default values; union types for nullable fields
- Schema distribution: embedded in file header (Hadoop object container files), negotiated per connection, or versioned in a registry
- Best for: dynamically-typed languages (Python, Ruby, JS), Hadoop ecosystems, schema-heavy workflows

| Aspect | JSON/XML | Protocol Buffers | Avro |
|--------|----------|-----------------|------|
| Human readable | Yes | No (binary) | No (binary) |
| Schema required | No (optional) | Yes (field tags) | Yes (writer + reader) |
| Type safety | Weak | Strong | Strong |
| Field identification | By name | By tag number | By schema position |
| Backward compat | Manual | Tag-based (safe) | Schema resolution |
| Forward compat | Manual | Ignore unknown tags | Schema resolution |
| Best use case | APIs, config | Internal services (static langs) | Data files, Hadoop |

### Communication: REST vs RPC vs Message Passing

**REST (Representational State Transfer)**:
- Design philosophy built on HTTP: URLs identify resources, HTTP verbs for operations
- Advantages: simple debugging (curl/browser), universal language support, vast ecosystem (caches, LBs, proxies, monitoring)
- API description: OpenAPI/Swagger for documentation and code generation
- Best for: public APIs, cross-organization communication

**RPC (Remote Procedure Call)**:
- Makes remote calls look like local function calls (location transparency)
- Fundamental problems: unpredictable network (timeouts, retries), no guaranteed delivery, variable latency, encoding overhead across languages
- Must design for **idempotence** to handle retries safely
- Evolvability: servers updated first, then clients; often maintain multiple API versions via URL/header/API key
- Modern RPC: gRPC (protobuf), Thrift -- use futures/promises for async, provide service discovery
- Best for: internal services within same organization/data center

**Asynchronous Message Passing**:
- Intermediate message broker (queue) between sender and receiver
- One-way: sender does not expect a reply, just sends and moves on
- Advantages: buffer for reliability, automatic redelivery to crashed consumers, decouples sender from receiver (no need to know IP/port), fan-out to multiple recipients
- Implementations: RabbitMQ, ActiveMQ, Apache Kafka, NATS
- No enforced data model -- messages are byte sequences with metadata

**Actor Model** (Akka, Orleans, Erlang OTP):
- Programming model for concurrency: logic encapsulated in actors with private state
- Actors communicate via asynchronous messages (no shared state, no locks)
- Distributed actor frameworks extend this across nodes transparently
- Better location transparency than RPC: messages already assumed to be possibly lost
- Serialization format determines compatibility (default Java serialization in Akka lacks compatibility; use protobuf instead)

| Aspect | REST | RPC | Message Passing |
|--------|------|-----|-----------------|
| Protocol | HTTP | Custom binary (gRPC, Thrift) | Broker-specific |
| Coupling | Loose | Tight (interface contract) | Very loose |
| Communication | Synchronous | Synchronous (modern: async futures) | Asynchronous |
| Discovery | URL-based | Service registry | Broker handles routing |
| Debugging | Easy (browser, curl) | Hard (binary, tooling needed) | Medium (broker UI) |
| Best for | Public APIs | Internal high-perf services | Event-driven, decoupled systems |

## Implementation

### Choosing a Storage Engine (Decision Framework)

```python
def choose_storage_engine(
    write_ratio: float,  # fraction of operations that are writes
    read_latency_p99_ms: float,  # required p99 read latency
    data_size_tb: float,
    query_pattern: str,  # "point", "range", "full_scan"
) -> str:
    """Guide for storage engine selection in system design interviews."""
    # Write-heavy with relaxed read latency -> LSM-tree
    if write_ratio > 0.7 and read_latency_p99_ms > 50:
        return "LSM-tree (e.g., RocksDB, Cassandra)"

    # Read-heavy with strict latency requirements -> B-tree
    if write_ratio < 0.3 and read_latency_p99_ms < 10:
        return "B-tree (e.g., PostgreSQL, MySQL InnoDB)"

    # Analytical full scans over large data -> columnar
    if query_pattern == "full_scan" and data_size_tb > 1:
        return "Column-oriented (e.g., Parquet, ClickHouse)"

    # Small dataset fitting in memory -> in-memory
    if data_size_tb < 0.05:
        return "In-memory (e.g., Redis, Memcached)"

    return "B-tree (safe default for mixed workloads)"
```

### Back-of-Envelope: Estimating Storage Engine Capacity

```python
def btree_capacity(
    page_size_kb: int = 4,
    branching_factor: int = 500,
    levels: int = 4,
) -> str:
    """Estimate B-tree storage capacity."""
    # Each level multiplies capacity by branching factor
    # Level 1: 1 root page -> Level 2: 500 pages -> ...
    total_leaves = branching_factor ** (levels - 1)
    total_size_bytes = total_leaves * page_size_kb * 1024
    total_size_tb = total_size_bytes / (1024 ** 4)
    return f"{levels}-level B-tree, BF={branching_factor}: ~{total_size_tb:.0f} TB"
    # 4-level, BF=500: ~256 TB
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| "Three pillars" framing | Opening any system design answer | Reliability, scalability, maintainability -- show you think beyond features |
| Percentiles over averages | Discussing SLOs/SLAs | p99 captures tail latency that averages hide; tail latency affects power users most |
| LSM vs B-tree trade-off | Storage engine selection | Write-heavy -> LSM; read-heavy -> B-tree; know compaction cost |
| Data model selection | Schema design discussion | Relational for joins, document for flexibility, graph for relationships |
| Star schema | Data warehouse design | Fact table (events) + dimension tables (context); explain snowflake as normalized variant |
| Column storage justification | Analytical query optimization | Only load needed columns; bitmap + RLE compression; vectorized processing |
| Encoding compatibility | API versioning / microservices | Backward + forward compat; protobuf tags; Avro schema resolution |
| REST vs RPC | Service communication | REST for public + debugging; RPC for internal + performance; message queues for decoupling |

### Common Interview Questions

- [ ] "What are the three pillars of a reliable data system?"
- [ ] "Explain LSM-tree vs B-tree: when would you choose each?"
- [ ] "Relational vs document database: trade-offs?"
- [ ] "What is a star schema and when would you use it?"
- [ ] "Column-oriented vs row-oriented storage: why does it matter for analytics?"
- [ ] "How do Protocol Buffers achieve backward/forward compatibility?"
- [ ] "REST vs RPC: when would you use each?"
- [ ] "What are the advantages of asynchronous message passing over direct RPC?"
- [ ] "Explain the difference between OLTP and OLAP systems."
- [ ] "How does a write-ahead log (WAL) ensure crash recovery?"

## Comparisons

### Data Model Comparison

| Aspect | Relational | Document (NoSQL) | Graph |
|--------|-----------|-----------------|-------|
| Structure | Tables with rows | Self-contained JSON/BSON docs | Vertices + edges |
| Schema | Schema-on-write (enforced) | Schema-on-read (flexible) | Schema-optional |
| Relationships | JOINs (many-to-many) | Embedded or references (one-to-many) | Native traversal |
| Query language | SQL (declarative) | Document-specific APIs | Cypher, SPARQL, Gremlin |
| Scalability | Vertical (typically) | Horizontal (sharding) | Varies |
| Best for | Structured data, complex queries | Flexible schemas, high write throughput | Relationship-heavy data |
| Weakness | Schema rigidity, ORM mismatch | Poor joins, deep nesting issues | Less mature tooling |

### Storage Engine Comparison

| Aspect | LSM-Tree | B-Tree | Column Store |
|--------|----------|--------|-------------|
| Write speed | Fast (sequential) | Moderate (random I/O) | Slow (batch-oriented) |
| Read speed | Moderate (multiple levels) | Fast (single traversal) | Fast for scans, slow for point |
| Space efficiency | Redundancy until compaction | Some page fragmentation | Excellent (compression) |
| Write amplification | Compaction overhead | WAL + page rewrites | Batch write only |
| Use case | Write-heavy (logs, time-series) | Mixed OLTP workloads | OLAP / analytics |
| Examples | RocksDB, LevelDB, Cassandra | PostgreSQL, MySQL, SQLite | Parquet, ClickHouse, Redshift |

### Encoding Format Comparison

| Aspect | JSON | Protocol Buffers | Avro | Thrift |
|--------|------|-----------------|------|--------|
| Format | Text | Binary | Binary | Binary |
| Schema | Optional | Required (.proto) | Required (.avsc) | Required (.thrift) |
| Field ID | By name | By tag number | By position | By tag number |
| Compat model | Manual | Tag-based | Schema resolution | Tag-based |
| Null handling | Native null | Default values | Union types | Optional fields |
| Code generation | No | Yes (static langs) | Optional | Yes (static langs) |
| Size efficiency | Low | High | High | High |

### Communication Pattern Comparison

| Aspect | REST | RPC (gRPC) | Message Queue | Actor Model |
|--------|------|-----------|---------------|-------------|
| Paradigm | Resource-oriented | Function call | Event-driven | Message-driven |
| Coupling | Loose | Tight | Very loose | Loose |
| Sync/Async | Sync (HTTP) | Sync + async (streams) | Async | Async |
| Failure handling | HTTP status codes | Error codes + retries | Redelivery, dead letter | Supervision trees |
| Scalability | Stateless, cacheable | Service mesh | Partitioned consumers | Location-transparent |
| Debugging | Easy (curl, browser) | Tooling required | Broker dashboards | Framework-specific |

## Key Takeaways

- [ ] Data systems are evaluated on reliability (fault tolerance), scalability (handle growth), and maintainability (easy to evolve)
- [ ] Use percentiles (p50/p95/p99) for performance metrics, never averages -- tail latencies are what page oncall
- [ ] Choose data models by relationship complexity: relational for many-to-many, document for self-contained objects, graph for relationship-first queries
- [ ] LSM-trees optimize writes (sequential I/O, compaction); B-trees optimize reads (single-path lookup, in-place updates)
- [ ] OLTP (row-store, point queries, low latency) vs OLAP (column-store, scan queries, high throughput) -- always separate them
- [ ] Star schema: fact table (events with metrics) surrounded by dimension tables (context) -- the foundation of data warehouse design
- [ ] Schema evolution requires backward + forward compatibility: use protobuf tags or Avro schema resolution, never break existing consumers
- [ ] REST for public APIs and debugging; RPC for internal high-performance services; message queues for decoupled event-driven systems
