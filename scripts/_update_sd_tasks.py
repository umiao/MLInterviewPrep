"""Update all 20 SD interview prep tasks with enhanced section guide."""
import json
import subprocess
import sys
from pathlib import Path

PROJ_ROOT = str(Path(__file__).resolve().parent.parent)

ENHANCED_SECTION_GUIDE = r"""CRITICAL SAFETY RULES: (1) NEVER run any eBay module seed script. (2) All content in Chinese with English terms preserved bold + first-use explanation. (3) Seed script = source of truth. (4) Formulas: use \mid not |, single-line $$ blocks, blank lines between $$. (5) Read scripts/content_module_arbitration.py as REFERENCE for Chinese style.

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
Include a 3-minute elevator pitch version too."""

# Task IDs and their original descriptions (we prepend the enhanced guide)
TASK_IDS = [
    "T-P0-298", "T-P0-299", "T-P0-300", "T-P0-301", "T-P0-302",
    "T-P0-303", "T-P0-304", "T-P0-305", "T-P0-306",
    "T-P1-307", "T-P1-308", "T-P1-309", "T-P1-310", "T-P1-311",
    "T-P1-312", "T-P1-313", "T-P1-314", "T-P1-315", "T-P1-316", "T-P1-317",
]

# Read each task's current description, extract TOPIC + STEPS + AC, replace guide
import sqlite3

conn = sqlite3.connect(str(Path(PROJ_ROOT) / ".claude" / "tasks.db"))
c = conn.cursor()

for tid in TASK_IDS:
    c.execute("SELECT description FROM tasks WHERE id = ?", (tid,))
    row = c.fetchone()
    if not row:
        print(f"[SKIP] {tid} not found")
        continue
    old_desc = row[0]

    # Extract TOPIC line onwards
    topic_idx = old_desc.find("TOPIC:")
    if topic_idx < 0:
        print(f"[SKIP] {tid} no TOPIC found")
        continue
    topic_section = old_desc[topic_idx:]

    new_desc = f"{ENHANCED_SECTION_GUIDE}\n\n{topic_section}"

    cmd = [
        sys.executable, ".claude/hooks/task_db.py", "update", tid,
        "--description", new_desc,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJ_ROOT, encoding="utf-8")
    try:
        data = json.loads(r.stdout.strip())
        print(f"[OK] {tid}: updated ({len(new_desc)} chars)")
    except Exception:
        print(f"[ERR] {tid}: {r.stdout[:60]} | {r.stderr[:60]}")

conn.close()
