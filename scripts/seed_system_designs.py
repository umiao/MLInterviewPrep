"""Seed script for system design modules.

Inserts 7 system design case study modules with metadata.
Idempotent: upserts by slug (if exists, updates title/subtitle/diagram/order
and content sections).
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work when run as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.backend.database import SessionLocal, init_db
from src.backend.models.system_design import SystemDesign

# Module seed data: slug, title, subtitle, diagram_filename, display_order
MODULES: list[dict[str, str | int]] = [
    {
        "slug": "module-arbitration",
        "title": "Module Arbitration: Content Marketplace for eBay SRP",
        "subtitle": (
            "Two-stage offline value estimation + online runtime arbitration "
            "for whole-page optimization"
        ),
        "diagram_filename": "module_arbitration.png",
        "display_order": 1,
    },
    {
        "slug": "llm-orchestration",
        "title": "LLM-Generated Artifact Orchestration for Structured Search",
        "subtitle": (
            "Production-ready architecture for structured conversational search "
            "with online inference + offline learning"
        ),
        "diagram_filename": "llm_orchestration.png",
        "display_order": 2,
    },
    {
        "slug": "pbe-pipeline",
        "title": "Product-Based Experience Logging & Dataset Pipeline",
        "subtitle": (
            "End-to-end PBE optimization: trackable IDs, viewport logging, "
            "attribution, training-data materialization"
        ),
        "diagram_filename": "pbe_pipeline.png",
        "display_order": 3,
    },
    {
        "slug": "ranking-allocation",
        "title": "Ranking-as-Allocation: Diversity Allotment Policy Framework",
        "subtitle": (
            "Diversity allotment policy with online serving + nearline "
            "closed-loop policy management"
        ),
        "diagram_filename": "ranking_allocation.png",
        "display_order": 4,
    },
    {
        "slug": "database-comparison",
        "title": "Database Systems Comparison: Cassandra & Distributed Storage",
        "subtitle": (
            "Architecture comparison across Cassandra, HBase, DynamoDB, ScyllaDB, "
            "CockroachDB -- CAP trade-offs, consistency models, and selection criteria"
        ),
        "diagram_filename": "database_comparison.png",
        "display_order": 5,
    },
    {
        "slug": "distributed-task-queue",
        "title": "Distributed Task Queue: Failure Modes, Idempotency & Exactly-Once",
        "subtitle": (
            "Deep failure analysis across 7 scenarios -- worker crash, dual execution, "
            "poison pill, broker restart -- with idempotency and fencing token solutions"
        ),
        "diagram_filename": "distributed_task_queue.png",
        "display_order": 6,
    },
    {
        "slug": "vibe-code-engineering-patterns",
        "title": "Vibe Code Engineering Patterns: Data Extraction, Scraping & Secret Detection",
        "subtitle": (
            "Cross-domain engineering lessons from building data extraction pipelines, "
            "scraping orchestration systems, and multi-layer secret detection"
        ),
        "diagram_filename": "vibe_code_engineering.png",
        "display_order": 7,
        "overview": (
            "## Vibe Code Engineering Lessons\n\n"
            "This module consolidates design takeaways from three production engineering "
            "projects:\n\n"
            "1. **Data Extraction Pipeline** -- 3-layer decomposition (extract/store/serve), "
            "fixture-driven selector design, format locking, structured vs flat storage\n"
            "2. **Scraping Orchestration** -- GitOps config/state separation, self-adaptive "
            "pagination, batch control at execution boundary, early auth failure detection\n"
            "3. **Secret Detection System** -- 7-layer defense-in-depth, regex vs AI detection "
            "boundary, confidence tiering, detection paradox, escape valve design\n\n"
            "The unifying theme: **constraint-driven design** -- turning platform limitations "
            "and operational realities into architectural advantages rather than fighting them."
        ),
        "architecture": (
            "## Cross-Domain Architecture Patterns\n\n"
            "### Extract-Store-Serve 3-Layer Decomposition\n"
            "Standard pattern for data pipeline enhancement tasks. Each layer is independently "
            "testable and rollable-back. The extraction layer should always return structured "
            "data (dict/list) even if persistence is flat text.\n\n"
            "### GitOps for Scraping: Declarative Config + Stateless Execution\n"
            "When the scheduler is session-scoped (e.g., CronCreate with 7-day expiry), "
            "treat cron as a disposable worker and YAML config as the single persistent "
            "source of truth. Principle: turn platform constraints into design advantages "
            "instead of working around them.\n\n"
            "### Phase Separation with Differentiated Scheduling\n"
            "Phase A (discovery/links) vs Phase B (materialization/content) -- independent "
            "scaling and retry. Map to cron: high-frequency drain (B, every 4h) + low-frequency "
            "discover (A, daily). This is the standard architecture for any production crawler.\n\n"
            "### 7-Layer Defense-in-Depth (Secret Detection)\n"
            "```\n"
            "Write-time hook       <- fastest feedback, but bypassable\n"
            "Pre-commit hook       <- second gate, but --no-verify\n"
            "Periodic scan (cron)  <- catch-all, but has time window\n"
            "CI/CD scan            <- server-enforced, not bypassable\n"
            "History scan (trufflehog) <- handles legacy exposure\n"
            "```\n"
            "Each layer has known weaknesses; value comes from combination. No single "
            "layer is 100% effective.\n\n"
            "### Single Source of Truth for Detection Logic\n"
            "Hooks (real-time) and scanners (batch) must share the same core detector module "
            "(`core/detector.py`). Maintaining separate regex lists guarantees pattern drift."
        ),
        "dataflow": (
            "## Extraction, Orchestration & Detection Flows\n\n"
            "### Data Extraction Flow\n"
            "1. Collect 5-10 real pages as fixtures\n"
            "2. Design CSS selectors driven by fixture coverage (not speculation)\n"
            "3. Extract to structured format (dict/list)\n"
            "4. Serialize to text using locked format templates (constants, not ad-hoc)\n"
            "5. Persist with quality gate on OP length (not full text length)\n"
            "6. Alert on zero-result extraction (never silently produce empty data)\n\n"
            "### Scraping Orchestration Flow\n"
            "1. YAML declares 'what I want' (seeds, selectors, target forums)\n"
            "2. DB tracks 'current state' (progress, last page, timestamps)\n"
            "3. CLI dispatches: `fetch --limit N` with batch control as first-class param\n"
            "4. Discovery scans until N consecutive pages with no new links (adaptive stop)\n"
            "5. File lock (flock) prevents cron overlap\n"
            "6. Cookie/auth validated within first 3 requests (fail-fast)\n\n"
            "### Secret Detection Flow\n"
            "1. Regex layer scans for known-format secrets (AKIA*, Discord tokens, DB URIs)\n"
            "2. AI layer receives redacted content (regex hits replaced with [REDACTED])\n"
            "3. AI flags suspicious patterns regex missed (spliced keys, comment passwords)\n"
            "4. Confidence scoring routes to block / warn / log\n"
            "5. Hourly cron sweep catches anything hooks missed\n"
            "6. CI pipeline provides server-side enforcement"
        ),
        "formulas": (
            "## Quality Metrics & Confidence Tiers\n\n"
            "### Extraction Quality Gate\n"
            "- Gate on **OP body length**, not total post length\n"
            "- Rationale: prevents 'short OP + long garbage replies' passing quality check\n"
            "- Known limitation: short OP + high-quality replies will be rejected (document "
            "explicitly)\n\n"
            "### Secret Detection Confidence Tiers\n\n"
            "| Confidence | Threshold | Action | Example |\n"
            "|------------|-----------|--------|---------|\n"
            "| High | > 0.9 | Block | `AKIA[0-9A-Z]{16}` full match |\n"
            "| Medium | 0.6 - 0.9 | Warn, allow | Possible JWT but wrong length |\n"
            "| Low | < 0.6 | Log only | Random base64 string |\n\n"
            "### Content Validity Check\n"
            "- HTTP 200 is not success -- validate payload has minimum content length\n"
            "- Match against known empty-page / login-wall patterns\n"
            "- Idempotency requires DB-level unique index on `(seed_id, post_url)`, "
            "not just code-level checks"
        ),
        "production_constraints": (
            "## Production Constraints\n\n"
            "### CSS Selector Stability\n"
            "- Template-based forums (Discuz etc.) use class names like `.plc.cl` that are "
            "not semantic contracts -- they drift across themes and versions\n"
            "- Never design selectors speculatively; collect 5-10 real fixture pages and "
            "drive selector design by coverage\n"
            "- Zero-result extraction must trigger explicit alert/exception\n\n"
            "### Cron Overlap Prevention\n"
            "- Any scheduled job must answer: 'what if the previous run hasn't finished?'\n"
            "- File locks (flock) are sufficient; no need for DB-level locking\n"
            "- Session-scoped cron (CronCreate) expires after 7 days -- design accordingly\n\n"
            "### Client-Side Security Limits\n"
            "- `git commit --no-verify` bypasses all pre-commit hooks\n"
            "- Client-side protection is a gentleman's agreement; the real gate is server-side\n"
            "- Phased approach: local hooks (now) -> CI scan (medium-term) -> server hooks "
            "(long-term)\n\n"
            "### Config File Safety\n"
            "- YAML typos (e.g., `strat_page` instead of `start_page`) are silently ignored\n"
            "- Any human-written config needs schema validation (Pydantic/dataclass with "
            "strict parsing, reject unknown fields)"
        ),
        "tradeoffs": (
            "## Trade-off Analysis\n\n"
            "### Structured Storage vs Flat JSON\n"
            "- Extraction layer: always return structured data (near-zero cost)\n"
            "- Persistence layer: structured columns only if there is a concrete near-term "
            "consumer, not 'might be useful later'\n"
            "- If data can be re-extracted from source, storing redundant structure has low ROI\n"
            "- Schema evolution: `nullable=True` + consumer-side fallback to old field is the "
            "safest progressive migration\n\n"
            "### Fail-Open AI Detection vs Fail-Closed\n"
            "- AI detection must be fail-open (pass through on failure)\n"
            "- Reason: non-deterministic + unpredictable latency. Blocking authority belongs "
            "only to deterministic systems\n"
            "- If AI blocks: occasional false positives -> developers disable the entire hook "
            "-> defense collapses\n"
            "- AI's role: signal enhancer, not gatekeeper\n\n"
            "### Config vs State Separation\n"
            "- If a field's value updates at runtime, it does not belong in config files\n"
            "- YAML = 'what I want' (declarative), DB = 'what's happening now' (runtime)\n"
            "- Mixing config and state is one of the most common sources of system rot\n"
            "- Anti-pattern: `start_page` appearing in both YAML and DB -> state drift\n\n"
            "### Full-Block vs Confidence-Graded Security\n"
            "- All-or-nothing blocking is not sustainable in engineering practice\n"
            "- Developers interrupted by false positives will `--no-verify` or delete hooks\n"
            "- Graded response (block/warn/log) preserves developer goodwill while "
            "maintaining coverage"
        ),
        "defense": (
            "## Defense Patterns & Adversarial Thinking\n\n"
            "### Fixture-Driven Validation (3-Things Rule)\n"
            "If you could only change three things:\n"
            "1. **Remove `start_page` from config, runtime state lives in DB only** -- "
            "eliminates state drift risk\n"
            "2. **Add YAML schema validation** -- prevents silent config errors\n"
            "3. **Promote `fetch --limit` to CLI first-class param** -- puts safety valve "
            "at the closest point to danger\n\n"
            "### The Detection Paradox\n"
            "AI semantic detection sends file contents to external API. If the file contains "
            "secrets (which is exactly what you're detecting), you leak them during detection.\n"
            "**Solution:** Regex-redact known secrets first (`[REDACTED]`), then send to AI "
            "to find what regex missed.\n\n"
            "### Escape Valve Design\n"
            "Any blocking mechanism must have a controlled exemption path, otherwise users "
            "find uncontrolled bypasses:\n"
            "- File-level: `# secret-guard: ignore-next-line`\n"
            "- Operation-level: env var + confirmation prompt + audit log\n"
            "- **Absolute prohibition:** silent exemptions (bypasses with no logging)\n\n"
            "### Review Methodology\n"
            "- Distinguish **correctness risks** (selector failure -> silent errors) from "
            "**extensibility suggestions** (add JSON column). Former must block; latter is advisory.\n"
            "- Beware absolute claims in reviews ('100% will regret this') -- they package "
            "preference as fact\n"
            "- Most valuable review feedback: not 'what to add' but 'where will it fail silently'\n\n"
            "### Detection vs Remediation\n"
            "Finding a secret is just the start. Full loop:\n"
            "```\n"
            "Detect -> Alert -> Remediation guide -> Key rotation -> Access log audit -> Close\n"
            "```\n"
            "Minimum viable: scan results include text remediation guidance "
            "(e.g., 'AWS Key found -> go to IAM console, Deactivate + Rotate')."
        ),
        "verbal_outline": (
            "## Verbal Outline: Vibe Code Engineering Patterns\n\n"
            "### 3-Minute Version\n"
            "This module covers engineering patterns from three domains: data extraction, "
            "scraping orchestration, and secret detection.\n\n"
            "**Key insight:** Constraint-driven design. In all three projects, the winning "
            "pattern was embracing platform limitations rather than fighting them -- "
            "session-scoped cron becomes GitOps, client-side bypass becomes defense-in-depth, "
            "AI non-determinism becomes fail-open signal enhancement.\n\n"
            "**Three patterns that transfer everywhere:**\n"
            "1. Batch control at the execution boundary (CLI), not orchestration layer\n"
            "2. Strict config/state separation -- if it updates at runtime, it's not config\n"
            "3. Confidence tiering for any blocking system -- graded response preserves "
            "user compliance\n\n"
            "### 10-Minute Version\n"
            "Expand each domain:\n\n"
            "**Data Extraction** (2 min): 3-layer decomposition, fixture-driven selector "
            "design over speculation, format locking for downstream consistency, quality "
            "gates on OP length not total length.\n\n"
            "**Scraping Orchestration** (3 min): GitOps config (YAML) + stateless execution. "
            "Phase A/B separation with differentiated cron frequency. Adaptive pagination "
            "stop (consecutive empty pages, not hard limit). Auth validation fail-fast "
            "within 3 requests. Flock for overlap prevention.\n\n"
            "**Secret Detection** (3 min): 7-layer defense-in-depth where each layer has "
            "known gaps. Regex for known formats (high-confidence block), AI for fuzzy "
            "patterns (fail-open enhance). The detection paradox: redact before sending "
            "to AI. Escape valve design: controlled exemption > uncontrolled bypass. "
            "Full remediation loop from detection through key rotation.\n\n"
            "**Cross-cutting** (2 min): Review methodology -- block on correctness risks, "
            "advise on extensibility. Schema validation as defensive minimum for any "
            "human-written config. Idempotency enforced at DB level, not code level."
        ),
    },
    {
        "slug": "ml-system-design-patterns",
        "title": "ML System Design Interview Patterns: Framework, Defense & Production Signals",
        "subtitle": (
            "Interview-ready patterns: 6-section answer template, 3-layer defense Q&A "
            "(L1 clarify, L2 challenge, L3 breaks-when = Staff+ signal), production "
            "constraint vocabulary, meta-narrative framing, and state machine design lessons"
        ),
        "diagram_filename": "ml_system_design_patterns.png",
        "display_order": 8,
        "overview": (
            "## ML System Design Interview Patterns\n\n"
            "This module consolidates interview preparation patterns from two sources:\n\n"
            "1. **System Design Interview Framework** -- 6-section answer template, "
            "3-layer defense Q&A structure, meta-narrative framing for multi-project "
            "stories, production constraint vocabulary (QPS/latency/cost), and "
            "technical decision speed-reference (Thompson Sampling vs UCB, pointwise "
            "ranking vs page-level allocation, IPW position bias correction)\n"
            "2. **Framework Engineering Patterns** -- state machine design (priority-driven "
            "status derivation), upward propagation with cycle detection, timestamp "
            "immutability, and defensive programming principles\n\n"
            "The unifying theme: **structured preparation beats memorization**. "
            "Interviews reward the ability to navigate decision spaces under pressure, "
            "not the ability to recite architecture diagrams. Every pattern here is "
            "designed to be deployable in a 45-minute system design round."
        ),
        "architecture": (
            "## Interview Answer Architecture: The 6-Section Template\n\n"
            "The 6-section template is itself an interview answer framework:\n\n"
            "```\n"
            "Overview       -> Why this system exists (motivation + business value)\n"
            "Architecture   -> How it works (components + responsibilities)\n"
            "Dataflow       -> How data flows (end-to-end pipeline)\n"
            "Formulas       -> Core algorithms (whiteboard-derivable)\n"
            "Tradeoffs      -> Why this choice over alternatives (decision ability)\n"
            "Defense        -> How to respond under challenge (high-pressure Q&A)\n"
            "```\n\n"
            "**Key insight**: Preparing system design is not 'memorize the architecture "
            "diagram' -- it is internalizing the option space and selection rationale "
            "at every decision point.\n\n"
            "## State Machine Architecture: Priority-Driven Status Derivation\n\n"
            "When parent status must be derived from children:\n\n"
            "```\n"
            "ALL mastered       -> mastered\n"
            "ANY in_progress    -> in_progress\n"
            "ANY review         -> review\n"
            "ALL not_started    -> not_started\n"
            "else               -> in_progress  (fallback)\n"
            "```\n\n"
            "**Why not combinatorial**: `[mastered, review]` is semantically ambiguous. "
            "Priority model eliminates ambiguity. Adding new states is O(1) insertion "
            "into the priority chain, not exponential combination growth.\n\n"
            "### Upward Propagation Pattern\n"
            "- `progress_pct` = importance-weighted average of children\n"
            "- Each parent layer calls `_derive_status` on update\n"
            "- Visited set prevents cycles; cycle detection logs critical + halts "
            "propagation (does not raise to user)\n\n"
            "### Trigger Completeness Checklist\n"
            "All events that change parent-child relationships must trigger propagation:\n"
            "- Status change | Progress change | Study log creation | **Child add/remove**\n"
            "- Missing any trigger = parent permanently stuck in stale state"
        ),
        "dataflow": (
            "## Meta-Narrative: Framing Multiple Projects\n\n"
            "When presenting 4+ projects, the interviewer's first question is typically "
            "'tell me about your work.' You need a 30-second unifying framework, then "
            "expand on demand.\n\n"
            "**Example narrative arc**:\n"
            "> 'My core work is evolving pointwise ranking into page-level allocation'\n\n"
            "Without this frame, 4 projects sound disconnected. With it, each project "
            "becomes a chapter in a coherent story.\n\n"
            "## Technical Decision Quick-Reference\n\n"
            "| Decision Point | Choice | Core Rationale | Common Pitfall |\n"
            "|----------------|--------|----------------|----------------|\n"
            "| Thompson Sampling vs UCB | TS | Better under non-stationary rewards; UCB too conservative | Vanilla TS assumes stationary -> need sliding window posterior |\n"
            "| LLM direct vs Proxy mode | Proxy (LLM generates artifact -> engine executes) | Hallucination, latency, inventory freshness | Underestimating fallback path importance |\n"
            "| Click-only vs Viewport exposure | Viewport | Click is sparse (2-5% CTR) + severe position bias | IntersectionObserver edge cases (background tabs, fast scroll) |\n"
            "| Pointwise ranking vs Allocation | Allocation | Pointwise ignores page-level composition effects | LP solver must stay <5ms or degrade to greedy |\n"
            "| Hard vs Soft constraints (diversity) | Hybrid | Hard for compliance floor, soft for experience tuning | Pure soft can be fully violated; pure hard too rigid |\n"
            "| IPW position debiasing vs None | IPW | Position 1 CTR is 5-10x Position 10 | IPW weights require randomization experiment, not guesswork |\n"
            "| Policy update frequency | Daily batch | Avoids intra-day oscillation; allows overnight analysis | Real-time looks 'advanced' but risk far exceeds benefit |\n"
            "| MUS score normalization vs Raw | Normalized | Multi-model scores are not comparable | Normalization assumes approx-normal distribution -- must verify |"
        ),
        "formulas": (
            "## State Machine Formulas & Timestamp Rules\n\n"
            "### Priority-Driven Status Derivation\n"
            "```\n"
            "priority_chain = [mastered, in_progress, review, not_started]\n"
            "derive_status(children):\n"
            "  if ALL children.status == mastered: return mastered\n"
            "  for status in [in_progress, review]:\n"
            "    if ANY child.status == status: return status\n"
            "  if ALL children.status == not_started: return not_started\n"
            "  return in_progress  # fallback for mixed states\n"
            "```\n\n"
            "### Timestamp Immutability Rule\n"
            "```\n"
            "started_at:    set once on first activity, NEVER cleared\n"
            "completed_at:  set once on completion, NEVER cleared on rollback\n"
            "```\n"
            "**Rationale**: `completed_at` records 'this event happened', not 'current "
            "state is mastered'. Clearing it on rollback destroys history. Timestamps "
            "are event logs, not state fields.\n\n"
            "### Progress Aggregation\n"
            "```\n"
            "parent.progress_pct = sum(child.importance * child.progress_pct) \n"
            "                    / sum(child.importance)\n"
            "```\n"
            "Importance-weighted average preserves relative significance across "
            "heterogeneous subtopics."
        ),
        "production_constraints": (
            "## Production Constraint Vocabulary\n\n"
            "Every system design answer must be able to cite concrete numbers for:\n\n"
            "```\n"
            "QPS / throughput\n"
            "Latency budget (P50 / P99)\n"
            "Data scale (daily increment / total volume)\n"
            "Candidate set size\n"
            "Cost (monthly infra order of magnitude)\n"
            "Failure mode & fallback\n"
            "```\n\n"
            "**Critical signal**: Describing algorithms eloquently but unable to state "
            "latency numbers -> interviewer concludes 'never shipped to production'.\n\n"
            "## Engineering Process Constraints\n\n"
            "### Idempotent Seed/Migration Scripts\n"
            "- `upsert by slug`, not `insert` -- reruns must be safe\n"
            "- Any batch write endpoint defaults to `skip existing`, with explicit "
            "`force` flag to overwrite\n"
            "- DB-level unique index enforces idempotency, not just code-level checks\n\n"
            "### List API Hygiene\n"
            "- `GET /collection` returns summary fields only, never full content\n"
            "- Detail content fetched on demand via `GET /collection/:id`\n"
            "- Seems obvious but frequently forgotten in rapid development\n\n"
            "### Migration Ordering\n"
            "- Backend schema -> migration -> frontend display\n"
            "- Prevents UI from briefly showing dirty/missing data during deploy\n\n"
            "### Cycle Detection in Hierarchical Data\n"
            "- Visited set prevents infinite propagation loops\n"
            "- But cycle existence itself signals data corruption\n"
            "- Log critical on detection; do NOT silently skip"
        ),
        "tradeoffs": (
            "## Trade-off Analysis\n\n"
            "### Fixed Columns vs JSON for Content Storage\n"
            "| Approach | Pros | Cons |\n"
            "|----------|------|------|\n"
            "| Fixed columns (6 Text) | Direct query, partial update, type-safe | Migration needed to add fields |\n"
            "| JSON column | Flexible schema, nested structures | Complex parsing, read-modify-write for partial updates |\n\n"
            "**Decision rule**: If section count/structure is fixed -> fixed columns. "
            "JSON only when structure genuinely varies at runtime. Do not sacrifice "
            "current simplicity for hypothetical future flexibility (YAGNI).\n\n"
            "### Independent Table vs Reusing Existing Tree Structure\n"
            "System design case studies are self-contained -- they are not hierarchical "
            "knowledge nodes. Data model should reflect domain semantics, not be "
            "force-fit into existing structures for reuse.\n\n"
            "### Static Files vs DB Blob vs Object Storage (Images)\n"
            "- Few images (<10), no user upload, no access control -> static files "
            "served by Vite\n"
            "- Threshold for migration: user-uploaded or frequently-changing images\n\n"
            "### Combinatorial vs Priority-Chain State Machines\n"
            "- Combinatorial: exponential edge cases per new state\n"
            "- Priority chain: linear complexity, deterministic, easy to extend\n"
            "- Use priority chain unless state semantics genuinely require "
            "combination-specific behavior\n\n"
            "### Defensive Code: Silent Skip vs Crash vs Log+Continue\n"
            "- Silent skip: most dangerous bug-hiding pattern\n"
            "- Crash (raise): blocks user on infrastructure errors\n"
            "- **Log critical + continue**: defensive code prevents crash, alert "
            "surfaces the underlying data issue\n\n"
            "### Feature Completeness: Show Degraded vs Hide Entirely\n"
            "- 'Degraded display' requires complete data pipeline\n"
            "- If data pipeline is broken, ANY display is misleading\n"
            "- Better to hide feature entirely than show fake/stale data\n\n"
            "### Multi-Layer API Fallback vs Manual Backfill\n"
            "For small data gaps (e.g., 5 missing descriptions), manual backfill "
            "is more economical than maintaining multi-layer scraping pipelines. "
            "Fallback layer count correlates linearly with maintenance cost."
        ),
        "defense": (
            "## Defense Patterns: 3-Layer Interview Q&A Structure\n\n"
            "### The L1-L2-L3 Framework\n"
            "```\n"
            "L1 Clarification:  'Why X?'              -> Explain your choice\n"
            "L2 Challenge:      'Why not Y?'           -> Compare alternatives\n"
            "L3 Attack:         'X breaks when ___'    -> Acknowledge limits + show mitigation\n"
            "```\n\n"
            "**L3 is the Staff+ signal.** Most candidates prepare only to L1. "
            "Comfortable L3 responses demonstrate deep understanding of design "
            "boundaries.\n\n"
            "### Defending Specific Decisions\n\n"
            "**Thompson Sampling choice**:\n"
            "- L1: 'TS handles non-stationary reward distributions better than UCB'\n"
            "- L2: 'UCB's confidence bound is overly conservative in our setting "
            "-- exploration budget is wasted on clearly suboptimal arms'\n"
            "- L3: 'Vanilla TS assumes stationarity. We use sliding-window posterior "
            "reset to handle distribution shift. Trade-off: window size is a "
            "hyperparameter that needs tuning per domain.'\n\n"
            "**Viewport over click-only**:\n"
            "- L1: 'Click is sparse (2-5% CTR) and heavily position-biased'\n"
            "- L2: 'IPW corrects position bias but amplifies variance on sparse clicks'\n"
            "- L3: 'IntersectionObserver has edge cases -- background tabs, fast scroll. "
            "We define minimum dwell time threshold and exclude background-tab events.'\n\n"
            "**Allocation over pointwise ranking**:\n"
            "- L1: 'Pointwise scoring ignores page-level composition effects'\n"
            "- L2: 'Listwise approaches are expensive. Allocation via LP captures "
            "diversity and business constraints jointly.'\n"
            "- L3: 'LP solver must stay under 5ms. When candidate set is too large, "
            "we pre-filter with pointwise scores then run allocation on top-K. "
            "This is a principled degradation, not an abandonment of allocation.'\n\n"
            "### Defensive Programming in Practice\n\n"
            "**Propagation trigger exhaustiveness**:\n"
            "- Challenge: 'What if a child is removed?'\n"
            "- Defense: 'All operations that change parent-child relationships must "
            "trigger propagation. We enumerate: status change, progress change, "
            "study log creation, child add, child remove. Missing any one = parent "
            "permanently stuck in stale state.'\n\n"
            "**Timestamp immutability**:\n"
            "- Challenge: 'User un-masters a topic -- clear completed_at?'\n"
            "- Defense: 'Never. completed_at records an event (\"this was completed\"), "
            "not current state. Clearing it destroys history. Status rollback changes "
            "status field; timestamps remain as audit trail.'\n\n"
            "**Cycle detection**:\n"
            "- Challenge: 'What if the hierarchy has a cycle?'\n"
            "- Defense: 'Visited set halts propagation. But the cycle itself is data "
            "corruption -- we log critical, not silently skip. Defensive code prevents "
            "crash; alerting surfaces the real problem.'"
        ),
        "verbal_outline": (
            "## Verbal Outline: ML System Design Interview Patterns\n\n"
            "### 3-Minute Version\n"
            "This module covers two areas: interview-specific patterns and engineering "
            "design patterns that transfer to any system design discussion.\n\n"
            "**Interview patterns**: The 6-section template structures any answer "
            "(overview, architecture, dataflow, formulas, tradeoffs, defense). "
            "The 3-layer defense framework (clarify, challenge, breaks-when) is the "
            "key differentiator -- L3 responses are the Staff+ signal. Meta-narrative "
            "framing connects multiple projects into a coherent 30-second story.\n\n"
            "**Engineering patterns**: Priority-driven state machines over combinatorial "
            "approaches. Timestamp immutability (event logs, not state fields). "
            "Trigger completeness for hierarchical propagation.\n\n"
            "**Production credibility**: Always be ready with QPS, latency P50/P99, "
            "data scale, and cost numbers. Without these, the interviewer assumes "
            "you have never shipped.\n\n"
            "### 10-Minute Version\n"
            "Expand each area:\n\n"
            "**6-Section Template** (2 min): Walk through each section's purpose. "
            "Overview = why (motivation), Architecture = how (components), "
            "Dataflow = data movement, Formulas = whiteboard math, "
            "Tradeoffs = decision rationale, Defense = adversarial Q&A.\n\n"
            "**3-Layer Defense** (3 min): L1 = explain choice. L2 = compare to "
            "alternative the interviewer will name. L3 = acknowledge where your "
            "design breaks and show mitigation. Demonstrate with TS vs UCB: L1 "
            "non-stationary advantage, L2 UCB's wasted exploration budget, L3 "
            "sliding-window posterior trade-off.\n\n"
            "**Technical Decisions** (2 min): Quick-fire through the decision table. "
            "Viewport over clicks (sparse + biased), allocation over pointwise "
            "(composition effects), hybrid constraints (hard floor + soft tuning), "
            "IPW (5-10x position bias), daily batch policy (avoid oscillation).\n\n"
            "**State Machine Patterns** (2 min): Priority chain eliminates "
            "combinatorial explosion. Timestamp immutability preserves audit trail. "
            "Propagation triggers must be exhaustively enumerated -- missing 'child "
            "remove' is the classic bug.\n\n"
            "**Production Constraints** (1 min): The constraint vocabulary checklist "
            "(QPS, latency, scale, cost, failure mode). Idempotent migrations. "
            "List API hygiene. Deploy ordering (backend -> migration -> frontend)."
        ),
    },
]


def seed_system_designs() -> dict[str, int]:
    """Insert or update system design modules.

    Returns:
        Dict with counts of inserted and updated records.
    """
    init_db()
    db = SessionLocal()
    inserted = 0
    updated = 0

    try:
        for data in MODULES:
            existing = (
                db.query(SystemDesign)
                .filter(SystemDesign.slug == data["slug"])
                .first()
            )
            # Content section keys (optional per module)
            content_keys = [
                "overview", "architecture", "dataflow", "formulas",
                "production_constraints", "tradeoffs", "defense",
                "verbal_outline",
            ]

            if existing:
                existing.title = data["title"]
                existing.subtitle = data["subtitle"]
                existing.diagram_filename = data["diagram_filename"]
                existing.display_order = data["display_order"]
                for key in content_keys:
                    if key in data:
                        setattr(existing, key, data[key])
                updated += 1
            else:
                kwargs = {
                    "slug": data["slug"],
                    "title": data["title"],
                    "subtitle": data["subtitle"],
                    "diagram_filename": data["diagram_filename"],
                    "display_order": data["display_order"],
                }
                for key in content_keys:
                    if key in data:
                        kwargs[key] = data[key]
                module = SystemDesign(**kwargs)
                db.add(module)
                inserted += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {"inserted": inserted, "updated": updated}


if __name__ == "__main__":
    result = seed_system_designs()
    print(
        f"Seed complete: {result['inserted']} inserted, "
        f"{result['updated']} updated."
    )
