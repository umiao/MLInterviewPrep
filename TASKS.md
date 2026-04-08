# Task Backlog

<!-- Auto-generated from .claude/tasks.db. Do not edit directly. -->
<!-- Use: python .claude/hooks/task_db.py --help -->

## In Progress

## Active Tasks

### P0 -- Must Have (core functionality)

### P1 -- Should Have (agentic intelligence)

#### T-P1-311: SD Prep: Design Dropbox/Google Drive
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design Dropbox/Google Drive (slug=interview-cloud-storage)
Key concepts: Block-level chunking + dedup + delta sync, conflict resolution, metadata DB, sync notification, storage optimization, offline editing

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_cloud_storage.py with the seed script.
3. Create SystemDesign record: slug='interview-cloud-storage', title='Design Dropbox/Google Drive', display_order=113.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-cloud-storage.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

#### T-P1-312: SD Prep: Design a Price Drop Tracker (CamelCamelCamel)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design a Price Drop Tracker (CamelCamelCamel) (slug=interview-price-drop-tracker)
Key concepts: Scraping pipeline, price history time-series, alert system, anti-scraping, product matching/dedup, scale to millions of products

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_price_tracker.py with the seed script.
3. Create SystemDesign record: slug='interview-price-drop-tracker', title='Design a Price Drop Tracker (CamelCamelCamel)', display_order=114.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-price-drop-tracker.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

#### T-P1-313: SD Prep: Design an Online Judge (Leetcode)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design an Online Judge (Leetcode) (slug=interview-online-judge)
Key concepts: Code sandbox (Docker/gVisor), queue-based submission, test case runner, judge verdicts, anti-cheat MOSS, multi-language runtime

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_online_judge.py with the seed script.
3. Create SystemDesign record: slug='interview-online-judge', title='Design an Online Judge (Leetcode)', display_order=115.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-online-judge.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

#### T-P1-314: SD Prep: Design Ticketmaster / Hotel Reservation
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design Ticketmaster / Hotel Reservation (slug=interview-ticket-reservation)
Key concepts: Seat map inventory, distributed locking for concurrent booking, payment hold TTL, overbooking, waitlist, flash sale virtual queue, idempotency

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_ticket_reservation.py with the seed script.
3. Create SystemDesign record: slug='interview-ticket-reservation', title='Design Ticketmaster / Hotel Reservation', display_order=116.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-ticket-reservation.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

#### T-P1-315: SD Prep: Design a Web Crawler
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design a Web Crawler (slug=interview-web-crawler)
Key concepts: URL frontier priority queue, distributed crawling consistent hashing, Bloom filter dedup (10B URLs ~1.2GB), robots.txt, 10K hacked machines variant = distributed hash map

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_web_crawler.py with the seed script.
3. Create SystemDesign record: slug='interview-web-crawler', title='Design a Web Crawler', display_order=117.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-web-crawler.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

#### T-P1-316: SD Prep: Design an Auction System (eBay)
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design an Auction System (eBay) (slug=interview-auction-system)
Key concepts: Real-time bidding WebSocket, bid ordering monotonic timestamps, auction state machine, sniping protection soft close, payment escrow, reserve price

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_auction_system.py with the seed script.
3. Create SystemDesign record: slug='interview-auction-system', title='Design an Auction System (eBay)', display_order=118.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-auction-system.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

#### T-P1-317: SD Prep: Design a Distributed Cache
- **Priority**: P1
- **Complexity**: M
- **Depends on**: None
- **Description**: LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-use expansion (e.g., CDN (Content Delivery Network)), (2) API/code examples, (3) formulas, (4) proper nouns (Redis, Kafka, etc.). All discussion, explanation, analysis, Q&A dialogue should be fluent Chinese to ensure readability.

CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

STANDARD SYSTEM DESIGN INTERVIEW FLOW -- each section maps to a phase:

=== SECTION: overview ===
Phase 1: Requirements Clarification (5 min in interview)

Structure the overview as:
1. **Problem Statement**: 1-2 sentence description of what we are building
2. **Functional Requirements (FR)**: 3-5 core features the system MUST support
   - Example (URL Shortener): shorten URL, redirect, custom alias, expiration
3. **Non-Functional Requirements (NFR)**:
   - Availability target (99.9%? 99.99%?)
   - Latency target (P99 < Xms for reads, < Yms for writes)
   - Consistency model (strong? eventual? where does it matter?)
   - Scalability target (DAU, QPS, storage growth rate)
   - Durability (data loss tolerance)
4. **Clarification Questions to Ask Interviewer** (5-8 questions with WHY):
   Each question formatted as: "Q: [question] -- WHY: [what design decision this affects]"
   Example: "Q: Do we need analytics on click counts? -- WHY: This determines whether we need a separate analytics pipeline or can piggyback on the redirect service"
5. **Out of Scope**: Explicitly state what we are NOT designing (prevents scope creep)

=== SECTION: architecture ===
Phase 2: High-Level Design (10 min)
- Component diagram (described in markdown, not image)
- Core services and their responsibilities
- Database choices with justification (SQL vs NoSQL vs both)
- Communication patterns (sync REST, async message queue, WebSocket)
- Data partitioning strategy if relevant

=== SECTION: dataflow ===
Phase 3: API Design + Data Flow (5 min)
- REST API endpoints: method, path, request body, response, status codes
- Core data models (key tables/collections with fields)
- Read path: step-by-step from client request to response
- Write path: step-by-step from client write to durable storage
- Include async paths (queues, background jobs) if relevant

=== SECTION: formulas ===
Phase 4: Back-of-Envelope Estimation + Core Algorithms (5 min)
MUST include a complete capacity estimation:
- DAU -> QPS (read QPS, write QPS, peak multiplier 2-5x)
- Storage: per-record size x records/day x retention period
- Bandwidth: QPS x average response size
- Memory (cache): hot data percentage x total data size
- Example calculation with concrete numbers (not just formulas)
Also include any core algorithm math (hashing, data structures, etc.)

=== SECTION: production_constraints ===
Phase 5: Deep Dive - Scale & Reliability (part of 25 min deep dive)
- Concrete scale numbers (users, QPS, storage, servers)
- Single point of failure analysis
- Multi-datacenter / cross-region considerations:
  - Active-active vs active-passive
  - Data replication strategy (sync vs async)
  - DNS-based routing / GeoDNS
  - Conflict resolution for multi-master
- High concurrency handling:
  - Connection pooling
  - Rate limiting
  - Circuit breaker pattern
  - Graceful degradation under load
- Monitoring & alerting: key metrics to watch

=== SECTION: tradeoffs ===
Phase 6: Trade-off Discussion (10 min)
- 3-5 key design decisions in table format:
  | Decision | Option A | Option B | Our Choice & Why |
- At least ONE decision about:
  - Consistency vs availability (CAP theorem application)
  - Cost vs performance
  - Complexity vs simplicity
- Include "what would change at 10x / 100x scale"

=== SECTION: defense ===
Interviewer Follow-up Q&A
- 4-5 tough questions the interviewer might ask
- Format: Q -> Acknowledge limitation -> Mitigation -> Data/evidence
- Include at least one question about:
  - Failure scenario ("What if X goes down?")
  - Scale challenge ("What if traffic 10x overnight?")
  - Data consistency ("What if two users do X simultaneously?")

=== SECTION: verbal_outline ===
1-Hour Interview Pacing Guide
- 0-5 min: Requirements clarification (FR, NFR, clarifying questions)
- 5-15 min: High-level architecture (draw components, justify DB choice)
- 15-40 min: Deep dive (pick 2-3 most interesting components, go deep)
- 40-50 min: Trade-offs and scaling discussion
- 50-55 min: Wrap-up (what would you improve? monitoring? what did you skip?)
- 55-60 min: Questions for interviewer
Include a 3-minute elevator pitch version too.

TOPIC: Design a Distributed Cache (slug=interview-distributed-cache)
Key concepts: Consistent hashing virtual nodes, LRU/LFU/TTL eviction, cache-aside vs write-through vs write-behind, stampede prevention, hot key, invalidation

STEPS:
1. Read scripts/content_module_arbitration.py as REFERENCE.
2. Create scripts/content_interview_distributed_cache.py with the seed script.
3. Create SystemDesign record: slug='interview-distributed-cache', title='Design a Distributed Cache', display_order=119.
4. Run seed script to populate all 8 sections.
5. Update SystemDesignList.tsx INTERVIEW_TOPICS: change matching topic to link to /system-design/interview-distributed-cache.
6. Verify: all 8 sections in DB, Chinese chars present, no bare | in math, TypeScript compiles.

AC:
- All 8 sections filled (Chinese, 10K+ chars)
- Clarification Questions in overview (5-8 with reasoning)
- Capacity estimation in formulas
- 1h interview outline in verbal_outline
- SystemDesignList.tsx updated
- Seed script = source of truth
- No bare | in math, TypeScript clean

### P2 -- Nice to Have

#### T-P2-318: SD Prep: Update landing page with all topics + category grouping
- **Priority**: P2
- **Complexity**: M
- **Depends on**: None
- **Description**: After all 20 content tasks are done, update SystemDesignList.tsx Interview Prep tab:

1. Replace hardcoded INTERVIEW_TOPICS with dynamic DB fetch (display_order >= 100)
2. Group by category: Core Infrastructure, Social & Real-time, Location & Geo, Search & Data, Storage & Media, Specialized
3. Each card links to /system-design/{slug} (no Coming Soon)
4. Difficulty badge + key tags per card
5. TypeScript clean

AC: All 20 topics shown as clickable cards, grouped by category, no Coming Soon, TypeScript clean

### P3 -- Stretch Goals

## Blocked

#### T-P1-184: [SYNC] helixos: Fix broken hooks -- use absolute Python path + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: All hooks in helixos settings.json use bare python which resolves to the Windows Store stub (exit 49) on this machine. MLInterviewPrep already has the fix applied.

Actions needed:
1. Copy .claude/hooks/setup_python_env.sh from MLInterviewPrep to helixos (writes Anaconda to CLAUDE_ENV_FILE)
2. Update helixos .claude/settings.json: replace all python with /c/Anaconda/python.exe in ALL hook commands
3. Add SessionStart hook entry for setup_python_env.sh

BLOCKED: Claude Code file permissions block writes to helixos .claude/hooks/ directory from MLInterviewPrep session. Must be done from a helixos session or manually.

#### T-P1-238: [SYNC] Fix helixos: replace bare python with absolute path in settings.json hooks
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/settings.json uses bare `python` for all hook commands (plan_mode_hook, block_dangerous, commit_msg_guard, secret_guard, tasks_md_guard, file_watch_warn, yaml_validate, lint_check, test_check, archive_check, session_context). Per CLAUDE.md Prohibited Actions: bare python resolves to Windows Store stub (exit code 49) and hooks silently fail. Fix: replace all `python "$CLAUDE_PROJECT_DIR/..."` with `/c/Anaconda/python.exe "$CLAUDE_PROJECT_DIR/..."`. Source: MLInterviewPrep settings.json (already fixed). Also add setup_python_env.sh as first SessionStart hook (bash "$CLAUDE_PROJECT_DIR/.claude/hooks/setup_python_env.sh") -- MLInterviewPrep has this, helixos does not. Copy setup_python_env.sh from MLInterviewPrep if not present.

#### T-P1-254: [SYNC] helixos: Fix bare python in settings.json + add setup_python_env.sh
- **Priority**: P1
- **Complexity**: S
- **Depends on**: None
- **Description**: CRITICAL: helixos settings.json uses bare python for ALL hook commands. On Windows, bare python resolves to the AppData Store stub (exit code 49), silently breaking all hooks. Fix: (1) Replace all bare python with /c/Anaconda/python.exe in settings.json. (2) Add setup_python_env.sh SessionStart hook (copy from MLInterviewPrep) to inject Anaconda into PATH for Bash tool calls via CLAUDE_ENV_FILE. CLAUDE.md already documents this prohibition (added 2026-03-21 via propagation) but the fix was never applied. This is the same root cause as MLInterviewPrep lesson [2026-03-20] #bash-tool #path.

#### T-P2-187: [SYNC] Add setup_python_env.sh + absolute Python path to helixos and template
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep has: (1) setup_python_env.sh SessionStart hook that writes Anaconda to CLAUDE_ENV_FILE, (2) /c/Anaconda/python.exe absolute paths in all settings.json hook commands. helixos and claude-code-project-template both use bare python in settings.json and have no setup_python_env.sh. Per LESSONS.md: Bash tool runs non-login shells, .bashrc not sourced, bare python resolves to Windows Store stub. Source: MLInterviewPrep/.claude/hooks/setup_python_env.sh and settings.json. Action: copy setup_python_env.sh to helixos and template, update settings.json hook commands to use absolute path.

#### T-P2-207: [SYNC] Remove deprecated stop-cache from helixos test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: helixos/.claude/hooks/test_check.py still imports and uses check_stop_cache/write_stop_cache from hook_utils. MLInterviewPrep already removed the cache in T-P2-188 (commit abf6543), per the lesson that stop caches can produce false passes when files change between sessions.

Action: Update helixos/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove check_stop_cache/write_stop_cache import and usage. Run tests after to confirm hook still works.

Source: MLInterviewPrep/.claude/hooks/test_check.py (current, cache-free version).

#### T-P2-208: [SYNC] Remove deprecated stop-cache from template test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: claude-code-project-template/.claude/hooks/test_check.py still uses check_stop_cache/write_stop_cache from hook_utils. The lesson [2026-03-18] established that stop caches cause false PASS results when files change between sessions. MLInterviewPrep already fixed this.

Action: Update template/.claude/hooks/test_check.py to match MLInterviewPrep version -- remove cache import and usage. The template is the reference baseline, so it should have the best-known version of all hooks.

Source: MLInterviewPrep/.claude/hooks/test_check.py.

#### T-P2-239: [SYNC] Propagate session_context.py improvements from MLInterviewPrep to helixos
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: MLInterviewPrep session_context.py has two improvements over helixos version: (1) Extracted _get_completed_task_ids() as a named helper function instead of inline code. (2) Added fresh-clone DB missing warning: if .claude/tasks.db is missing but TASKS.md has tasks, warn user to run `python .claude/hooks/task_db.py import`. Apply both changes to helixos/.claude/hooks/session_context.py.

#### T-P2-255: [DEBT] helixos: Remove deprecated stop cache usage from test_check.py
- **Priority**: P2
- **Complexity**: S
- **Depends on**: None
- **Description**: test_check.py imports check_stop_cache and write_stop_cache from hook_utils and uses them to skip re-running tests in the same session. These deprecated caching functions were removed from the hook architecture (LESSONS.md lesson [2026-03-18]: removed lint cache so every Stop hook runs fresh). The caching logic means test failures can be silently skipped if tests passed earlier in the same session. Fix: Remove the cache check/write calls from test_check.py so tests always run fresh on Stop. Keep check_stop_cache/write_stop_cache in hook_utils.py only if other hooks still use them.

## Completed Tasks

> 270 completed tasks archived to [archive/completed_tasks.md](archive/completed_tasks.md).

- [x] **2026-04-08** -- T-P2-287: System design formula audit: all modules. CRITICAL SAFETY RULES: (1) NEVER run any module seed script unless fixing that specific module. (2) NEVER overwrite Chin
- [x] **2026-04-08** -- T-P2-286: System design depth: ml-system-design-patterns expansion. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_ml_system_design_patterns.py
- [x] **2026-04-08** -- T-P2-285: System design depth: vibe-code-engineering restructure. CRITICAL SAFETY RULES: (1) NEVER run any other module seed script. Only run scripts/content_vibe_code_engineering.py. (2
- [x] **2026-04-08** -- T-P2-279: [SYNC] Propagate DB-only content recovery lesson to template. Propagate MLInterviewPrep LESSONS.md entry [2026-04-08] to claude-code-project-template/LESSONS.md.
- [x] **2026-04-08** -- T-P2-278: [SYNC] Propagate SQLite naive-datetime timezone lesson to helixos. Propagate MLInterviewPrep LESSONS.md entry [2026-04-07] to helixos/LESSONS.md.
- [x] **2026-04-08** -- T-P1-310: SD Prep: Design YouTube/Netflix Video Streaming. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-309: SD Prep: Design an Ad Click Aggregator. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-308: SD Prep: Design Top-K Heavy Hitters. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P1-307: SD Prep: Design Search Autocomplete. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-306: SD Prep: Design Facebook Live Comments. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-305: SD Prep: Design a Chat System (Messenger/WhatsApp). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-304: SD Prep: Design a News Feed (Instagram). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-303: SD Prep: Design a Real-time Game Leaderboard. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-302: SD Prep: Design a Proximity Service (Yelp). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-301: SD Prep: Design a Ride-sharing System (Uber). LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-300: SD Prep: Design a Notification System. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-299: SD Prep: Design a Rate Limiter. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
- [x] **2026-04-08** -- T-P0-298: SD Prep: Design a URL Shortener. LANGUAGE RULE: All narrative content MUST be in Chinese. Only preserve English for: (1) technical acronyms with first-us
