"""Seed interview events into the timeline.

Idempotent: skips events that already exist (matched by company_name + scheduled_at).
"""
import requests

API_BASE = "http://localhost:8000/api"

EVENTS = [
    {
        "company_name": "DoorDash",
        "event_type": "technical",
        "title": "ML Project Deep Dive",
        "description": "First round - ML deep dive on past projects and technical depth",
        "scheduled_at": "2026-03-26T13:00:00",
        "duration_minutes": 45,
        "status": "upcoming",
    },
    {
        "company_name": "Uber",
        "event_type": "hr_call",
        "title": "HR Talk with Jaclyn",
        "description": "HR screening call",
        "scheduled_at": "2026-03-23T11:10:00",
        "duration_minutes": 30,
        "status": "upcoming",
    },
    {
        "company_name": "Adobe",
        "event_type": "phone_screen",
        "title": "Phone Screen",
        "description": "Adobe phone screen - exact time TBD, week of March 30 - April 3 2026",
        "scheduled_at": "2026-03-30T09:00:00",
        "duration_minutes": 60,
        "status": "upcoming",
    },
    {
        "company_name": "Unknown Fintech",
        "event_type": "hr_call",
        "title": "HR Call with Maddie Gore",
        "description": "HR phone screen - recruiter Maddie Gore (She/Her). Company name TBD. Slot confirmed 2026-04-28 09:00 AM PT (between Uber final day 1 Apr 27 and day 2 Apr 29).",
        "scheduled_at": "2026-04-28T09:00:00",
        "duration_minutes": 30,
        "status": "upcoming",
    },
]


def main() -> None:
    """Seed interview events, skipping duplicates."""
    # Fetch existing events
    resp = requests.get(f"{API_BASE}/timeline/events", timeout=10)
    resp.raise_for_status()
    existing = resp.json()

    # Build set of (company_name, scheduled_at) for dedup
    existing_keys = {
        (e["company_name"], e["scheduled_at"]) for e in existing
    }

    created = 0
    skipped = 0
    for event in EVENTS:
        # Normalize key: API may return ISO with timezone suffix
        key = (event["company_name"], event["scheduled_at"])
        # Check both with and without timezone suffix
        if key in existing_keys or any(
            e["company_name"] == event["company_name"]
            and e["scheduled_at"].startswith(event["scheduled_at"][:16])
            for e in existing
        ):
            print(f"  SKIP  {event['company_name']} - {event['title']} (already exists)")
            skipped += 1
            continue

        r = requests.post(
            f"{API_BASE}/timeline/events",
            json=event,
            timeout=10,
        )
        r.raise_for_status()
        print(f"  CREATED  {event['company_name']} - {event['title']} (id={r.json()['id']})")
        created += 1

    print(f"\nDone: {created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()
