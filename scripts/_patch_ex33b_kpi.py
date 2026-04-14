"""One-shot patch: fix EX-33B KPI references.

User correction:
- The real KPIs were BI (Business Impact) and GMB (Gross Merchandise Bookings).
- MRR was the metric I had been leaning on, but I later realized it is NOT a
  real KPI -- it is a self-fulfilling proxy because the ranker training objective
  and MRR share the same assumptions.

Also adds BI/GMB to tech_terms and a one-line quote about metric vs KPI.
Idempotent: re-running detects already-patched state and exits cleanly.
"""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "mle_prep.db"

OLD_ACTION_CHUNK = (
    "by our launch criteria (MRR up, revenue neutral) the expert was "
    "technically 'launchable' on paper, but users were not being served better and "
    "homogeneity was getting worse"
)
NEW_ACTION_CHUNK = (
    "the expert was technically passing the metric I had been leaning on (MRR up), but "
    "the actual business KPIs we cared about - BI and GMB - were either flat or being "
    "hurt by the new expert. That gap forced me to question whether MRR was even a "
    "meaningful KPI in the first place: the ranker training objective and MRR shared "
    "the same assumptions, so an 'MRR win' was a self-fulfilling prophecy that did not "
    "independently validate user outcome. Users were not being served better and "
    "homogeneity was getting worse"
)

OLD_RESULT_CHUNK = "There was no rescue and no silver lining I could honestly offer."
NEW_RESULT_CHUNK = (
    "There was no rescue and no silver lining I could honestly offer. The cleanest "
    "one-line postmortem I now give: I was optimizing MRR while the team's real KPIs "
    "- BI and GMB - were the ones telling the truth, and I learned the hard way that "
    "a metric is not the same thing as a KPI."
)

NEW_QUOTE = (
    "A metric is not the same thing as a KPI. I was winning on MRR while BI and GMB "
    "- the actual business KPIs - were telling me the opposite."
)

NEW_TECH_TERMS = {
    "BI (Business Impact)": (
        "a top-line KPI used by the search org to measure real business outcome "
        "(revenue / margin level), independent of model-side proxy metrics"
    ),
    "GMB (Gross Merchandise Bookings)": (
        "top-line KPI capturing total booked merchandise value across the "
        "marketplace; one of the two real launch KPIs in this story"
    ),
    "MRR (Mean Reciprocal Rank)": (
        "position-weighted retrieval metric. In this project I initially treated "
        "it as a launch criterion, but later realized it is a self-fulfilling proxy "
        "(the ranker training objective and MRR share the same assumptions) and not "
        "a real KPI."
    ),
}


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    c.execute(
        "SELECT action, result, evidence_quotes, tech_terms "
        "FROM behavioral_examples WHERE example_id='EX-33B'"
    )
    row = c.fetchone()
    if not row:
        raise SystemExit("EX-33B not found")
    action, result, quotes_json, tech_json = row

    changed = False

    if OLD_ACTION_CHUNK in action:
        action = action.replace(OLD_ACTION_CHUNK, NEW_ACTION_CHUNK)
        changed = True
        print("[patch] action chunk replaced")
    elif "BI and GMB" in action:
        print("[skip] action already patched")
    else:
        raise SystemExit("action chunk neither old nor patched -- aborting")

    if OLD_RESULT_CHUNK in result and "metric is not the same thing as a KPI" not in result:
        result = result.replace(OLD_RESULT_CHUNK, NEW_RESULT_CHUNK)
        changed = True
        print("[patch] result postmortem appended")
    elif "metric is not the same thing as a KPI" in result:
        print("[skip] result already patched")
    else:
        raise SystemExit("result chunk neither old nor patched -- aborting")

    quotes = json.loads(quotes_json)
    if NEW_QUOTE not in quotes:
        quotes.append(NEW_QUOTE)
        changed = True
        print("[patch] new quote appended")
    else:
        print("[skip] quote already present")

    tech = json.loads(tech_json)
    for k, v in NEW_TECH_TERMS.items():
        if tech.get(k) != v:
            tech[k] = v
            changed = True
    print("[patch] tech_terms updated (BI / GMB / MRR)")

    if changed:
        c.execute(
            "UPDATE behavioral_examples SET action=?, result=?, evidence_quotes=?, tech_terms=? "
            "WHERE example_id='EX-33B'",
            (action, result, json.dumps(quotes, ensure_ascii=False), json.dumps(tech, ensure_ascii=False)),
        )
        conn.commit()
        print("[ok] EX-33B updated")
    else:
        print("[ok] no changes needed")

    # verify
    c.execute("SELECT action, result, evidence_quotes, tech_terms FROM behavioral_examples WHERE example_id='EX-33B'")
    a, r, q, t = c.fetchone()
    print()
    print("BI in action:", "BI" in a)
    print("GMB in action:", "GMB" in a)
    print("'metric is not the same thing as a KPI' in result:", "metric is not the same thing as a KPI" in r)
    print("quote count:", len(json.loads(q)))
    print("BI in tech_terms:", "BI (Business Impact)" in json.loads(t))
    print("GMB in tech_terms:", "GMB (Gross Merchandise Bookings)" in json.loads(t))


if __name__ == "__main__":
    main()
