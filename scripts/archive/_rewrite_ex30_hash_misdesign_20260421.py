"""Rewrite EX-30 (Hash Capability Misdesign).

Replaces situation/task/action/result/risk_statement on
behavioral_examples.example_id='EX-30' with the user's structurally
deeper version (Discord msg 1496053306517094611 attachment +
1496054494696575056 confirm).

Why the rewrite: existing v1 was already labeled "the cluster's gold
standard, needs no additional guard" by NRG-v1, but it ran 2429 chars
of Action with 4 numbered sub-decisions (over-structured) and missed
two L5-level signals: (1) structural recognition that "fundamental
but not yet integrated" is a red flag rather than a neutral state,
(2) the experiment-level confounding tease as probe-bait. New version
tightens Action to ~1100 chars while introducing both signals, and
crystallizes the kill-line lesson "Domain depth is not design
authority. The authority belongs to whoever consumes the output."

NRG-v2 replaces NRG-v1 with 4 pacing beats + most-dangerous-probe
direction inline + reference to separate prep-notes file
`docs/behavioral_prep_notes/EX-30_probe_qa.md` (full 5 anticipated
probes + answer directions + delivery cues, kept in user's original
CN-EN mix per their explicit ask "中英混合也不需要去多改").

Idempotent: situation startswith "At eBay Search, I was the IC owning
hash design in our diversity team" indicates rewrite is already
applied.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "mle_prep.db"
EXAMPLE_ID = "EX-30"

IDEMPOTENT_MARKER = "At eBay Search, I was the IC owning hash design in our diversity team"

# Combined Situation & Task per user's framing.
NEW_SITUATION = (
    "At eBay Search, I was the IC owning hash design in our diversity "
    "team. We were in a high-velocity loop with our PM, shipping "
    "diversity features that moved GMV and engagement, with winning "
    "metrics landing both offline and online."
)

NEW_TASK = (
    "The next step was a real-time facet hash plus entropy-based "
    "diversity metric, meant to unblock a strategic push: running "
    "rigorous tests from seller and advertiser angles, not just "
    "buyer-perceived experience. I owned the design."
)

NEW_ACTION = (
    "I designed a hash that was mathematically elegant. Prime "
    "multiplication, high-bit extraction. Uniformity, performance, "
    "extensibility all clean. Our internal bar was met. I shipped it.\n\n"
    "Weeks later, tickets came back through analytics. Two or three "
    "downstream DS teams were blocked on launch analysis. Our hash was "
    "implicit at the SQL layer with no stable identity, so they could "
    "not trace which bucket mapped to which facet.\n\n"
    "My first instinct was to fix it with more engineering. I proposed "
    "making the hash a first-class operator in our lower search infra, "
    "with matching changes to the data pipeline and A/B platform. It "
    "would have been a four-team, multi-quarter investment.\n\n"
    "It was rejected. And this is where I stopped.\n\n"
    "I realized the rescue was self-centered. Other teams had high-"
    "priority projects running. I was asking them to absorb cost so my "
    "original design could survive. The metric win was already real. "
    "The elegance was not worth the shared cost.\n\n"
    "I went to the indexing team and asked how their pipeline absorbs "
    "new analytical features. They had a mature practice I had never "
    "asked about: explicit aspect cache with stable ID assignment. By "
    "my hash-expert standard, it was worse. By the DS consumer "
    "standard, it was traceable and auditable. I adopted it."
)

NEW_RESULT = (
    "DS unblocked within the next sprint. Launch analysis resumed. The "
    "metric wins held.\n\n"
    "Structurally, I now treat \"fundamental but not yet integrated\" "
    "as a red flag, not a neutral state. An orphan capability will "
    "leak into its consumers somehow -- I have seen this later show up "
    "as experiment-level confounding in adjacent work.\n\n"
    "The lesson: **Domain depth is not design authority. The authority "
    "belongs to whoever consumes the output.**"
)

NEW_RISK = (
    "The surface cost was already paid: two or three downstream DS "
    "teams lost weeks of launch-analysis time, and my proposed rescue "
    "was rejected. The deeper structural risk is that when a team "
    "treats unintegrated capability as an acceptable long-term state, "
    "cost migrates silently to downstream consumers and to adjacent "
    "experiments. The orphan doesn't sit still -- it leaks into "
    "experiment confounders, into ad-hoc query workarounds, into "
    "mental-model drift across the org. By the time you notice, the "
    "cost is already distributed and unrecoverable. It is not a ticket "
    "problem. It is structural debt that compounds.\n\n"
    "<!-- NRG-v2 --> NARRATION GUARD: Pace four high-signal beats -- "
    "pause between \"It was rejected.\" and \"And this is where I "
    "stopped.\" (let rejection land before the resolution); slow down "
    "on \"By my hash-expert standard, it was worse. By the DS consumer "
    "standard, it was traceable and auditable.\" (parallel structure "
    "carries the lesson); end the lesson \"Domain depth is not design "
    "authority\" without softening -- no \"so I learned that...\" tail; "
    "deliver Risk-if-not-addressed segment slowly and steadily, this "
    "is where individual failure abstracts into structural risk (the "
    "L5-bar tell). Most dangerous probe likely to come: \"Why didn't "
    "you ask the indexing team before you designed this?\" -- answer "
    "direct, name the frame error (saw hash as math object, not as "
    "analytical artifact in someone else's decision path), do not "
    "deflect. Full set of 5 anticipated probes + answer directions + "
    "delivery cues lives in `docs/behavioral_prep_notes/"
    "EX-30_probe_qa.md` (kept in user's original CN-EN mix for "
    "delivery prep)."
)


def main() -> int:
    if not DB.exists():
        print(f"[FAIL] db not found: {DB}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    row = conn.execute(
        "SELECT id, title, situation FROM behavioral_examples "
        "WHERE example_id = ?",
        (EXAMPLE_ID,),
    ).fetchone()
    if row is None:
        print(f"[FAIL] {EXAMPLE_ID} not found", file=sys.stderr)
        conn.close()
        return 2

    row_id, title, current_situation = row

    if current_situation and current_situation.startswith(IDEMPOTENT_MARKER):
        print(f"[SKIP] {EXAMPLE_ID} already rewritten")
        conn.close()
        return 0

    conn.close()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DB.with_name(f"{DB.name}.bak.{ts}_pre_ex30_rewrite")
    shutil.copy2(DB, backup)
    print(f"[BACKUP] {backup.name}")

    conn = sqlite3.connect(str(DB))
    before = conn.execute(
        "SELECT length(situation), length(task), length(action), "
        "length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (row_id,),
    ).fetchone()

    conn.execute(
        "UPDATE behavioral_examples "
        "SET situation = ?, task = ?, action = ?, result = ?, "
        "risk_statement = ? "
        "WHERE id = ?",
        (NEW_SITUATION, NEW_TASK, NEW_ACTION, NEW_RESULT, NEW_RISK, row_id),
    )
    conn.commit()

    after = conn.execute(
        "SELECT length(situation), length(task), length(action), "
        "length(result), length(risk_statement) "
        "FROM behavioral_examples WHERE id = ?",
        (row_id,),
    ).fetchone()
    conn.close()

    fields = ["situation", "task", "action", "result", "risk_statement"]
    print(f"[OK] {EXAMPLE_ID} (id={row_id}) '{title}' rewritten:")
    for f, b, a in zip(fields, before, after, strict=False):
        sign = "+" if a >= b else ""
        print(f"  {f:<16} {b:>5} -> {a:>5} chars ({sign}{a - b})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
