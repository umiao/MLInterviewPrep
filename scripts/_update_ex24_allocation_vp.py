"""Update EX-24 Allocation-to-VP story: add avoided-cost metric + top-10/30 deliverable.

Touches docs/bq_behavioral_examples.json and data/mle_prep.db (behavioral_examples).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs" / "bq_behavioral_examples.json"
DB_PATH = ROOT / "data" / "mle_prep.db"

NEW_ACTION = (
    "Communication strategy: conclusion first, then expand. Told the VP three "
    "things upfront: (1) we are overestimating the achievable combined effect, "
    "(2) we are underestimating impact on default ranking, (3) this is not an "
    "execution problem but a structural one. Explained in VP-accessible terms: "
    "each policy performs well independently because it monopolizes top slots, "
    "but when launched simultaneously they compete --- no free lunch. Brought a "
    "concrete deliverable I had been iterating on: a top-10 and top-30 "
    "slot-distribution analysis, framed as 'you can bias toward any ONE of the "
    "priorities you want, but not all simultaneously --- slots are a finite "
    "resource'. That turned an abstract argument into a decision aid the VP "
    "could act on in the meeting. Recommended limiting scope to the "
    "highest-ROI adjustments first and sequencing the rest."
)

NEW_RESULT = (
    "Avoided an estimated 2-3 weeks of debugging + reverse-test data collection "
    "that a combo-launch would have burned for an outcome already predictable "
    "from the slot-distribution analysis. VP adopted the slot-as-finite-resource "
    "framing and adjusted project direction on the spot. The allocation framing "
    "became the team-wide mental model for ranking strategy going forward --- it "
    "spread because it combined near-real-time deployment capability, "
    "authenticity as a root-cause diagnosis (not a post-hoc narrative), "
    "long-term business value, and a clean fit with the broader C2C strategy, "
    "not just because the VP endorsed it once."
)

NEW_EVIDENCE = [
    "Conclusion first, then expand: overestimating effect, underestimating default ranking impact, structural not execution problem",
    "Tangible deliverable: top-10 / top-30 slot-distribution analysis framing slots as a finite resource",
    "Avoided ~2-3 weeks of debugging + reverse-test collection by preventing the combo-launch",
    "Allocation framing adopted team-wide because of near-real-time deployment, authenticity, long-term business value, and C2C-strategy fit",
]


def update_json() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    examples = data["examples"]
    target = None
    for e in examples:
        if e.get("id") == "EX-24":
            target = e
            break
    assert target is not None, "EX-24 not found in JSON"
    target["action"] = NEW_ACTION
    target["result"] = NEW_RESULT
    target["evidence_quotes"] = NEW_EVIDENCE
    JSON_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[JSON] EX-24 updated. action={len(NEW_ACTION)} result={len(NEW_RESULT)}")


def update_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE behavioral_examples SET action=?, result=?, evidence_quotes=? WHERE example_id=?",
            (NEW_ACTION, NEW_RESULT, json.dumps(NEW_EVIDENCE, ensure_ascii=False), "EX-24"),
        )
        conn.commit()
        cur.execute(
            "SELECT length(action), length(result) FROM behavioral_examples WHERE example_id=?",
            ("EX-24",),
        )
        row = cur.fetchone()
        print(f"[DB] EX-24 updated. action={row[0]} result={row[1]}")
    finally:
        conn.close()


if __name__ == "__main__":
    update_json()
    update_db()
