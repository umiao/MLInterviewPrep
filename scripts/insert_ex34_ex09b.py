"""Insert EX-34 (BBE seller-level vs listing-level risk policy) and EX-09B
(conversational search privacy proxy item cut). Tag to themes and create
question_example_links.

EX-34 fills the long-standing gap that COM-5 'feedback you disagreed with' had
no story where the user actually disagreed and was vindicated.

EX-09B is the privacy-cut of EX-09 (same project, different lens), following
the EX-33/EX-33B pattern. Per the user's clarifications:
  - co-developed (not solo)
  - privacy explicitly listed as a technical advantage in design doc
  - PII / NSFW are illustrative not exhaustive examples of sensitive types
  - query rewrite was the natural first direction because of pre-existing
    query clustering / autocomplete techniques; the LLM angle added
    world-knowledge value
"""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "mle_prep.db"

# ============================================================================
# EX-34
# ============================================================================

EX34 = {
    "example_id": "EX-34",
    "title": "BBE Risk Policy: Seller-Level vs Listing-Level — Disagreeing with a Principal Researcher on Absolutism as Lazy Non-Action",
    "source_project": "eBay BBE (Buyer Bad Experience) — risk policy enforcement granularity",
    "situation": (
        "On the BBE (Buyer Bad Experience) project, the team faced a policy choice that looked "
        "like an engineering question but was really about new-seller and small-seller "
        "fairness: when a bad-experience risk signal fired, should we enforce at SELLER level "
        "(restrict the seller account as an entity) or at LISTING level (act on the specific "
        "flagged listing)? A principal researcher held a hard preference for seller-level "
        "absolutism — clean, executable, broad-coverage. In practice that absolutism meant a "
        "new or small seller with even a few risk-flagged listings would get their entire "
        "account suppressed and lose marketplace visibility, while large sellers could "
        "absorb individual flags and use their PR / appeals channels to recover quickly."
    ),
    "task": (
        "Decide whether to accept seller-level absolutism as the team default or build a more "
        "granular (listing-level) enforcement path, and surface the fairness / marketplace-"
        "health argument behind that architectural choice so it could not be dismissed as "
        "implementation preference."
    ),
    "action": (
        "(1) Engaged the principal researcher directly at the first-principles level rather "
        "than going around him or escalating. The implicit assumption inside seller-level "
        "enforcement is 'if a seller has any bad listing, the seller as an entity is risky' "
        "— I argued that assumption breaks for new and small sellers who have small samples, "
        "limited remediation resources, and no appeals leverage. They get locked into entity-"
        "level labels precisely because they are small, while large sellers escape via PR.\n\n"
        "(2) Pulled the data. I segmented current seller-level enforcement triggers by seller "
        "tier (new / small / mid / large) and showed the false-positive rate on new and "
        "small sellers was disproportionately higher. The absolute punishment they absorbed "
        "was disproportionate to the actual risk signal.\n\n"
        "(3) Reframed the question from 'how clean is this enforcement' to 'are we taking "
        "reasonable responsibility for new and small sellers'. Marketplace trust is not "
        "built on whether large sellers get punished cleanly; it is built on whether small "
        "sellers feel they were treated fairly. A policy that pushes all enforcement onto "
        "entity-level absolutism is in fact LAZY NON-ACTION dressed up as rigor — it pushes "
        "the engineering responsibility of 'making nuanced judgments' onto 'replacing "
        "judgment with a blanket rule'.\n\n"
        "(4) Proposed a listing-level enforcement path with a seller-level escalation: "
        "decide risk at listing granularity; only escalate to entity-level if a seller "
        "accumulates a threshold of flagged listings; on first flag, give the seller "
        "actionable feedback so they can remediate before any enforcement compounds. This "
        "protects buyers without destroying small-seller listing lifecycles on a first "
        "small offense.\n\n"
        "(5) Engaged the principal researcher's UNDERLYING concern, not just his stated "
        "position. What he actually cared about was enforcement consistency and audit "
        "simplicity. I wrote the listing-level + cumulative-escalation mechanism as an "
        "explicit auditable state machine, so enforcement consistency was actually BETTER "
        "than pure seller-level (every action now had a traceable trigger trail). His real "
        "concern got honored, not dismissed."
    ),
    "result": (
        "Listing-level enforcement was adopted as the default; seller-level escalation was "
        "preserved as the cumulative trigger. Two outcomes: (a) new-seller and small-seller "
        "false-positive punishment dropped substantially; their listing lifecycles moved "
        "closer to large-seller actuals. (b) The relationship with the principal researcher "
        "actually improved, because his audit-consistency concern was honored as a first-"
        "class part of the mechanism rather than dismissed.\n\n"
        "The lesson I take out of this and use as a recurring smell test: ABSOLUTISM IS OFTEN "
        "NOT RIGOR — IT IS LAZY NON-ACTION IN DISGUISE. Pushing 'make a nuanced judgment' "
        "onto 'replace judgment with a blanket rule' substantively damages marketplace value "
        "and trust, because it externalizes the cost onto the participants who can least "
        "absorb it (in our case, new and small sellers). I now ask, every time I see an "
        "entity-level absolutism in any policy or system: 'is this absolutism really required, "
        "or is it a way to avoid doing the engineering of nuanced judgment?'"
    ),
    "evidence_quotes": [
        "Absolutism is often not rigor — it is lazy non-action in disguise.",
        "Marketplace trust is not built on whether large sellers get punished cleanly; it is built on whether small sellers feel they were treated fairly.",
        "I disagreed with seller-level absolutism as the implementation; I never disagreed with enforcement consistency as the goal — and I proved that by making consistency strictly better in the listing-level mechanism.",
        "New and small sellers get locked into entity-level labels precisely because they are small. Large sellers escape via PR. That is reverse unfairness baked into the policy.",
        "I trigger an absolutism smell test now: every time I see an entity-level blanket rule, I ask whether it is really required or whether it is a way to avoid doing the engineering of nuanced judgment.",
    ],
    "principle_tags": [
        "have_backbone_disagree_and_commit",
        "fairness_for_new_and_small_sellers",
        "two_sided_marketplace_responsibility",
        "absolutism_smell_test",
        "engage_with_underlying_concern",
        "data_driven",
        "ownership",
    ],
    "risk_statement": (
        "Principal researchers are usually right; the largest narration risk in this story "
        "is sounding like 'I overrode an expert'. State the disagreement precisely: I did "
        "not disagree with enforcement consistency (his goal), I disagreed with seller-level "
        "absolutism (his implementation), and I proved consistency was strictly better in "
        "the listing-level mechanism. Avoid sounding anti-large-seller — the fairness frame "
        "is about disproportionate punishment of new and small sellers, NOT about benefits "
        "to large sellers.\n\n"
        "NARRATION-RISK GUARD: do not let the 'absolutism is lazy non-action' line read as a "
        "moral judgment on the principal researcher personally. He was honestly chasing audit "
        "simplicity, which is a legitimate concern. The lesson is about a CLASS of policy "
        "design failure, not about him."
    ),
    "analogy": (
        "Absolute standards are like a kitchen cleaver — clean, executable, broad-use. But if "
        "the cleaver is the only tool you reach for, you have given up on being a cook."
    ),
    "tech_terms": {
        "BBE (Buyer Bad Experience)": "eBay program to identify and reduce buyer-side bad experiences (defects, complaints, returns) at scale via risk policies and seller behavior signals",
        "Seller-level enforcement": "applying a risk policy decision to the seller account as a whole (suppress visibility, restrict listing privileges, etc.)",
        "Listing-level enforcement": "applying a risk policy decision only to the specific listing(s) flagged by risk signals, leaving the rest of the seller's catalog intact",
        "Cumulative escalation": "a policy pattern where individual listing-level actions accumulate into seller-level action only when a threshold is crossed, preserving individual-action proportionality while still allowing entity-level escalation when warranted",
        "False-positive rate by segment": "evaluation of how often a risk policy mis-flags non-risky behavior, broken down by seller tier (new / small / mid / large) to surface fairness imbalances that aggregate metrics hide",
    },
}

EX34_THEMES = ["conflict_disagreement", "ownership_accountability", "leadership_direction"]

EX34_LINKS = [
    ("COM-5",  "Direct fit -- this is the gap-filler. Story where I disagreed with a principal researcher on a hard policy constraint and was vindicated, but did so by honoring his underlying audit-consistency concern rather than dismissing it."),
    ("LDR-3",  "Tough call as a leader: choosing to engage the principal researcher in first-principles disagreement rather than escalate, knowing the social cost. Frame the 'tough' part as the relational risk, not the technical complexity."),
    ("IMP-11", "Ethical dilemma framing: the choice between absolute enforcement (cleaner audit) and proportional fairness (right thing for new/small sellers). The lesson is that absolutism dressed as rigor is itself an ethical failure when it externalizes cost onto those least able to absorb it."),
    ("IMP-13", "Tough ethical decision: disagreeing with a principal researcher on a fairness-laden policy choice. The 'tough' is in the willingness to surface the fairness frame at all when the team default was absolutism."),
    ("IMP-15", "Advocated for responsible practices: pushed for listing-level enforcement specifically because seller-level absolutism externalized cost onto new and small sellers. Use the 'absolutism smell test' line."),
    ("COM-2",  "Persuaded the principal researcher (and downstream the team) to change direction by reframing the question and honoring his underlying concern. Use this for the 'persuade by translation' pattern, not the 'persuade by force' pattern."),
]

# ============================================================================
# EX-09B
# ============================================================================

EX09B = {
    "example_id": "EX-09B",
    "title": "Conversational Search Privacy: Proxy Item Generation Eliminates Raw Query Leakage Risk (Privacy-Cut of EX-09)",
    "source_project": "Conversational Search with LLM (privacy-cut, same project as EX-09)",
    "situation": (
        "On our LLM-powered conversational search project, the natural first design direction "
        "was query rewrite -- not because it was naive, but because the team already had "
        "mature prior art in query clustering and autocomplete; introducing the LLM into "
        "this path looked like an incremental upgrade that added world-knowledge value to a "
        "well-understood pipeline. That natural choice carried an implicit privacy cost: the "
        "user's raw conversational input -- including potentially sensitive types like PII "
        "and NSFW content as outstanding (but not exhaustive) examples -- would have to flow "
        "through the LLM context and be persisted in pipeline logs, training data collection, "
        "and downstream evaluation systems. This privacy / leakage risk was implicitly "
        "accepted in design; nobody had flagged it as a blocker because the team's focus was "
        "on delivering the feature."
    ),
    "task": (
        "Find a design path that delivered the conversational search capability AND did not "
        "let user raw conversational queries flow into any downstream persistence path -- "
        "before that implicit risk became an actual leakage incident."
    ),
    "action": (
        "(1) Surfaced the privacy concern explicitly in the design discussion. The query "
        "rewrite path implicitly accepted that raw user dialogue would be persisted "
        "downstream; that risk had not been processed in any prior doc or design review. "
        "I named it as a blocker, not a side concern.\n\n"
        "(2) Challenged the query-rewrite default. The team's prior art (query clustering, "
        "autocomplete) had legitimized the rewrite framing, but the question I asked was: "
        "can we deliver conversational understanding WITHOUT the raw query needing to enter "
        "the retrieval index, the eval pipeline, or any training-data path?\n\n"
        "(3) Co-developed the proxy-item path with the team. Instead of rewriting the "
        "conversational query into a search query, use the LLM to generate proxy items -- "
        "synthetic representative items that match the conversational intent -- and use "
        "those proxy items as the retrieval seed. The raw conversational query never enters "
        "retrieval, eval, or training. This was a TEAM design decision, not a solo proposal; "
        "the privacy framing was the connective tissue that let the team commit to the new "
        "path.\n\n"
        "(4) Validated proxy items capture conversational intent semantically (this overlaps "
        "with the EX-09 retrieval-breakthrough work).\n\n"
        "(5) Wrote the privacy benefit explicitly into the design doc as one of the listed "
        "technical advantages of the proxy-item path. Not just in my head, not just in "
        "discussion -- pinned in the architectural artifact so future review and audit "
        "could not lose it."
    ),
    "result": (
        "The proxy-item path shipped. User raw conversational queries -- including any PII / "
        "NSFW / other sensitive content -- never persist outside the immediate request "
        "handling path. The retrieval / breakthrough side effect (which is the EX-09 "
        "main-line frame) is a real benefit, but the IRREDUCIBLE reason proxy items had to "
        "be the chosen path, the reason it could not be query-rewrite-with-redaction, was "
        "the privacy property: query rewrite would have left the raw query persisted "
        "somewhere in the system; proxy item makes that persistence structurally "
        "impossible.\n\n"
        "Lesson I carry forward: ELIMINATE, DON'T MITIGATE. Good privacy design makes the "
        "sensitive data structurally absent from the path, not encrypted-in-place. Mitigation "
        "is fragile because it depends on every downstream consumer behaving correctly; "
        "elimination is robust because the data is not there to leak."
    ),
    "evidence_quotes": [
        "We almost defaulted into accepting that raw user dialogue would flow into downstream logs and training data -- proxy item turned that risk from 'accepted' into 'eliminated'.",
        "The proxy-item path has a retrieval upside, but privacy is the irreducible reason it had to be the chosen path.",
        "Eliminate, don't mitigate. Good privacy design makes the sensitive data structurally absent from the path, not encrypted-in-place.",
        "Query rewrite was the natural first direction -- we had query clustering and autocomplete as prior art, so introducing the LLM looked like a clean incremental upgrade. That naturalness was exactly what made the privacy cost invisible.",
    ],
    "principle_tags": [
        "privacy_by_design",
        "eliminate_not_mitigate",
        "cross_functional",
        "design_doc_as_artifact",
        "innovation",
        "responsible_ai",
        "challenge_the_default_framing",
    ],
    "risk_statement": (
        "This story is the PRIVACY-CUT of the same project that EX-09 covers as an "
        "innovation / retrieval breakthrough. The two cuts must NEVER be combined in a "
        "single answer -- combining the privacy framing with the retrieval-breakthrough tail "
        "makes the privacy benefit sound like a post-hoc bonus rather than the irreducible "
        "reason the path was chosen. Same pattern as EX-33 / EX-33B (both are framings of "
        "the MoE-to-allocation project).\n\n"
        "USAGE RULE: For privacy / security / responsible-AI / 'privacy concern in your "
        "projects' questions (e.g. IMP-14), use the EX-09B framing and stop the story at "
        "'eliminate don't mitigate'. Do NOT mention the retrieval performance benefit -- "
        "that belongs to EX-09. For innovation / breakthrough questions, use EX-09 and do "
        "NOT mention privacy.\n\n"
        "NARRATION-RISK GUARD: This was a CO-DEVELOPED team design decision, not a solo "
        "proposal. Frame it as 'I surfaced the concern and helped the team find a path that "
        "honored it', not as 'I single-handedly designed proxy items'. Overclaiming on the "
        "design contribution would be inaccurate to the actual collaboration."
    ),
    "analogy": (
        "Good privacy design is not putting the user's raw query into a locked safe -- it is "
        "designing the system so the raw query never needs to leave the user's session in the "
        "first place."
    ),
    "tech_terms": {
        "Query rewrite": "transforming a user's natural-language query into a structured search query that the existing retrieval system can consume; well-understood prior art via query clustering and autocomplete",
        "Proxy item generation": "using an LLM to generate synthetic items representative of the user's conversational intent, then using those items (not the raw query) as the retrieval seed -- structurally removes the raw query from any downstream path",
        "Eliminate-not-mitigate (privacy)": "design principle: rather than reducing the chance of sensitive data leaking, design the system so the sensitive data structurally cannot reach the path where leakage would occur",
        "Design-doc-as-artifact": "writing architectural decisions and their rationales (including non-functional concerns like privacy) into a versioned design doc, so the rationale is preserved for future review and audit instead of living only in chat history",
    },
}

EX09B_THEMES = ["process_systems", "ownership_accountability", "technical_problem_solving"]

EX09B_LINKS = [
    ("IMP-14", "Direct fit -- the gap-filler for the privacy/security question. Use the EX-09B (privacy-cut) framing and stop at 'eliminate don't mitigate'. Do NOT use EX-20 (Seller Risk Modeling Fairness) for this question -- that one is fairness, not privacy."),
    ("IMP-12", "Responsible innovation framing: the proxy-item path was chosen because the team committed to a privacy-by-design property even though query-rewrite would have shipped sooner. Use the 'naturalness made the privacy cost invisible' line."),
    ("IMP-15", "Advocated for responsible practices in product design: explicitly named the leakage risk inside an LLM project where the team was focused on feature delivery, and helped the team co-develop an architectural alternative that honored the concern."),
    ("PS-1",  "Difficult technical decision: rejecting the natural query-rewrite path (which had clear prior art and incremental LLM upside) in favor of co-developing proxy item generation, on the basis of an irreducible privacy property."),
    ("INN-4", "Innovative solution context: the proxy-item path was a non-obvious architectural alternative that the team had to design from scratch; the privacy concern was the forcing function that motivated the innovation. Use this only when you also want the innovation framing -- otherwise prefer EX-09 main-line."),
]


def upsert_example(c: sqlite3.Cursor, ex: dict) -> int:
    c.execute("SELECT id FROM behavioral_examples WHERE example_id=?", (ex["example_id"],))
    row = c.fetchone()
    if row:
        c.execute(
            """UPDATE behavioral_examples SET title=?, source_project=?, situation=?, task=?,
               action=?, result=?, evidence_quotes=?, principle_tags=?, risk_statement=?,
               analogy=?, tech_terms=? WHERE example_id=?""",
            (
                ex["title"], ex["source_project"], ex["situation"], ex["task"],
                ex["action"], ex["result"],
                json.dumps(ex["evidence_quotes"], ensure_ascii=False),
                json.dumps(ex["principle_tags"], ensure_ascii=False),
                ex["risk_statement"], ex["analogy"],
                json.dumps(ex["tech_terms"], ensure_ascii=False),
                ex["example_id"],
            ),
        )
        print(f"[update] {ex['example_id']} (db id={row[0]})")
        return row[0]
    c.execute(
        """INSERT INTO behavioral_examples
           (example_id, title, source_project, situation, task, action, result,
            evidence_quotes, principle_tags, risk_statement, analogy, tech_terms)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            ex["example_id"], ex["title"], ex["source_project"], ex["situation"],
            ex["task"], ex["action"], ex["result"],
            json.dumps(ex["evidence_quotes"], ensure_ascii=False),
            json.dumps(ex["principle_tags"], ensure_ascii=False),
            ex["risk_statement"], ex["analogy"],
            json.dumps(ex["tech_terms"], ensure_ascii=False),
        ),
    )
    new_id = c.lastrowid
    print(f"[insert] {ex['example_id']} (db id={new_id})")
    return new_id


def tag_themes(c: sqlite3.Cursor, ex_db_id: int, theme_slugs: list[str]) -> None:
    for slug in theme_slugs:
        c.execute("SELECT id FROM behavioral_themes WHERE slug=?", (slug,))
        row = c.fetchone()
        if not row:
            print(f"  [warn] theme {slug} not found, skipping")
            continue
        theme_id = row[0]
        c.execute("SELECT 1 FROM example_theme_tags WHERE example_id=? AND theme_id=?", (ex_db_id, theme_id))
        if c.fetchone():
            continue
        c.execute("INSERT INTO example_theme_tags (example_id, theme_id) VALUES (?, ?)", (ex_db_id, theme_id))
        print(f"  tagged -> {slug}")


def add_links(c: sqlite3.Cursor, ex_db_id: int, links: list[tuple[str, str]]) -> None:
    for qid_str, note in links:
        c.execute("SELECT id FROM behavioral_questions WHERE question_id=?", (qid_str,))
        row = c.fetchone()
        if not row:
            print(f"  [warn] question {qid_str} not found, skipping")
            continue
        q_db_id = row[0]
        c.execute("SELECT id FROM question_example_links WHERE question_id=? AND example_id=?", (q_db_id, ex_db_id))
        existing = c.fetchone()
        if existing:
            c.execute("UPDATE question_example_links SET relevance_note=? WHERE id=?", (note, existing[0]))
            print(f"  link updated: {qid_str}")
        else:
            c.execute(
                "INSERT INTO question_example_links (question_id, example_id, relevance_note) VALUES (?,?,?)",
                (q_db_id, ex_db_id, note),
            )
            print(f"  link inserted: {qid_str}")


def main() -> None:
    conn = sqlite3.connect(str(DB))
    c = conn.cursor()

    ex34_id = upsert_example(c, EX34)
    tag_themes(c, ex34_id, EX34_THEMES)
    add_links(c, ex34_id, EX34_LINKS)

    ex09b_id = upsert_example(c, EX09B)
    tag_themes(c, ex09b_id, EX09B_THEMES)
    add_links(c, ex09b_id, EX09B_LINKS)

    conn.commit()

    # final read-back
    print()
    print("=== final state ===")
    for eid in ("EX-34", "EX-09B"):
        c.execute(
            """SELECT e.example_id, e.title, GROUP_CONCAT(DISTINCT bt.slug)
               FROM behavioral_examples e
               LEFT JOIN example_theme_tags ett ON ett.example_id = e.id
               LEFT JOIN behavioral_themes bt ON bt.id = ett.theme_id
               WHERE e.example_id=? GROUP BY e.id""",
            (eid,),
        )
        r = c.fetchone()
        print(f"  {r[0]}: {r[1][:70]}")
        print(f"    themes: {r[2]}")
        c.execute(
            """SELECT q.question_id FROM question_example_links qel
               JOIN behavioral_questions q ON q.id = qel.question_id
               JOIN behavioral_examples e ON e.id = qel.example_id
               WHERE e.example_id=? ORDER BY q.question_id""",
            (eid,),
        )
        qs = [r[0] for r in c.fetchall()]
        print(f"    linked questions ({len(qs)}): {qs}")
    conn.close()


if __name__ == "__main__":
    main()
