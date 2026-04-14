"""Split data_analysis from Technical Depth into its own QuickIndex family.

Updates T-P1-361 task description so the autonomous session generates 7 cluster
families instead of 6, with Data and Decisions as its own group containing the
single data_analysis theme. Per user direction (item f).
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / ".claude" / "tasks.db"

OLD = "{ id: 'technical',  label: 'Technical Depth',         theme_slugs: ['technical_problem_solving', 'code_quality_tech_debt', 'data_analysis'] },"
NEW = (
    "{ id: 'technical',  label: 'Technical Depth',         theme_slugs: ['technical_problem_solving', 'code_quality_tech_debt'] },\n"
    "         { id: 'data',       label: 'Data and Decisions',      theme_slugs: ['data_analysis'] },"
)


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()
    c.execute("SELECT description FROM tasks WHERE id='T-P1-361'")
    desc = c.fetchone()[0]

    if NEW.split("\n")[1].strip() in desc:
        print("[skip] data family split already applied")
        return

    if OLD not in desc:
        # show what we have so we can debug
        for line in desc.splitlines():
            if "technical" in line.lower() and "label" in line.lower():
                print("FOUND:", repr(line))
        raise SystemExit("OLD line not found verbatim — task description has drifted")

    desc = desc.replace(OLD, NEW)
    desc = desc.replace("all 6 family headings", "all 7 family headings")
    desc = desc.replace("6 family groups", "7 family groups")
    desc = desc.replace("6 cluster family", "7 cluster family")

    c.execute(
        "UPDATE tasks SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id='T-P1-361'",
        (desc,),
    )
    conn.commit()
    print(f"[ok] updated, new len: {len(desc)}")
    print("contains 'Data and Decisions':", "Data and Decisions" in desc)
    print("contains old grouping (should be False):", "'technical_problem_solving', 'code_quality_tech_debt', 'data_analysis'" in desc)
    conn.close()


if __name__ == "__main__":
    main()
