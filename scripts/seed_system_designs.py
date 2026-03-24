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
