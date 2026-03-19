"""Seed companies from the application tracking spreadsheet.

Idempotent: skips companies that already exist (case-insensitive match).
"""

import sys
from datetime import date
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402

COMPANIES: list[dict] = [
    {
        "name": "Google",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- Software Engineer, AI/ML, Google Ads\n"
            "- Software Engineer III, AI/ML, GenAI - Mountain View\n"
            "- Software Engineer III, Google Research, AI/ML\n"
            "\n"
            "Note: 3 jobs in 30-day window reached. Resets 4/4."
        ),
    },
    {
        "name": "Airbnb",
        "status": "applied",
        "notes": (
            "Position: Senior Machine Learning Engineer, "
            "Listing and Host Tools Data and AI\n"
            "Status: Referral completed"
        ),
    },
    {
        "name": "Uber",
        "status": "applied",
        "notes": (
            "Position: Machine Learning Engineer - Ranking & Recommendations"
        ),
    },
    {
        "name": "Netflix",
        "status": "applied",
        "notes": (
            "Position: Machine Learning Engineer (L4) - Production Science"
        ),
    },
    {
        "name": "Glean",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- Machine Learning Engineer, Search Quality\n"
            "- Machine Learning Engineer, Enterprise Brain"
        ),
    },
    {
        "name": "Apple",
        "status": "applied",
        "notes": (
            "Position: Machine Learning Engineer, Siri Core Modeling"
        ),
    },
    {
        "name": "Nvidia",
        "status": "applied",
        "notes": (
            "Position: Senior GenAI Algorithms Engineer - "
            "Post-Training Optimizations"
        ),
    },
    {
        "name": "Reddit",
        "status": "applied",
        "notes": "Position: Senior ML Engineer",
    },
    {
        "name": "Salesforce",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- AI Engineer, Agent Systems\n"
            "- Lead Machine Learning Engineer, LLM Infrastructure"
        ),
    },
    {
        "name": "Microsoft",
        "status": "applied",
        "notes": "2 positions (details TBD)",
    },
    {
        "name": "Instacart",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- Senior Machine Learning Engineer II, AI Special Projects\n"
            "- Senior Machine Learning Engineer II, Growth Modeling"
        ),
    },
    {
        "name": "Robinhood",
        "status": "applied",
        "notes": (
            "Position: Senior Machine Learning Engineer, Agentic"
        ),
    },
    {
        "name": "Roblox",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- Senior Machine Learning Engineer, Ads\n"
            "- Sr Machine Learning Engineer - Safety Experience"
        ),
    },
    {
        "name": "Amazon",
        "status": "applied",
        "notes": (
            "Position: Applied Scientist, Delivery Foundation Model"
        ),
    },
    {
        "name": "Coinbase",
        "status": "applied",
        "notes": (
            "Position: Senior Software Engineer "
            "(AI Platform - AI Acceleration)"
        ),
    },
    {
        "name": "Quora",
        "status": "applied",
        "notes": (
            "Position: Senior Machine Learning Engineer, Ranking (Remote)"
        ),
    },
    {
        "name": "Intuit",
        "status": "applied",
        "notes": "Position: Senior AI Scientist",
    },
    {
        "name": "Snap",
        "status": "applied",
        "notes": "Position: Machine Learning Engineer, Level 4",
    },
    {
        "name": "OpenAI",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- Research Engineer, Retrieval & Search, Applied Engineering\n"
            "- Research Engineer, Applied AI Engineering\n"
            "- Research Engineer, Notifications\n"
            "- Software Engineer, Youth Well-Being"
        ),
    },
    {
        "name": "Anthropic",
        "status": "applied",
        "notes": (
            "Positions applied:\n"
            "- Software Engineer, Growth\n"
            "- Machine Learning Systems Engineer, Research Tools"
        ),
    },
]


def seed_companies() -> None:
    """Insert companies into the database, skipping existing ones."""
    init_db()
    db = SessionLocal()
    try:
        # Get existing company names (case-insensitive)
        existing = {
            c.name.lower()
            for c in db.query(Company).all()
        }

        added = 0
        skipped = 0
        for data in COMPANIES:
            if data["name"].lower() in existing:
                print(f"  SKIP (exists): {data['name']}")
                skipped += 1
                continue

            company = Company(
                name=data["name"],
                status=data["status"],
                applied_at=date.today(),
                notes=data.get("notes"),
            )
            db.add(company)
            added += 1
            print(f"  ADD: {data['name']}")

        db.commit()
        print(f"\nDone: {added} added, {skipped} skipped")
    finally:
        db.close()


if __name__ == "__main__":
    seed_companies()
