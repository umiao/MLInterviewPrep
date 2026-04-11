"""Populate EX-30 (Hash Misdesign) in place + insert EX-33 (MoE->Allocation).

See T-P1-357 for the full spec. Pre-approved English STAR content below.
Idempotent: re-running is a no-op for the INSERT path and re-applies the
UPDATE path (writes are identical).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# ---------------------------------------------------------------------------
# EX-30 - Hash Capability Misdesign (pure-failure story, overwrite placeholder)
# ---------------------------------------------------------------------------

EX30_TITLE = "Hash Capability Misdesign - Expert Frame Blind Spot"
EX30_SOURCE_PROJECT = "eBay search - diversity/hash features"

EX30_PRINCIPLE_TAGS = [
    "failure",
    "learning",
    "expert_blind_spot",
    "cross_functional",
    "humility",
    "consulted_prior_art",
]

EX30_ANALOGY = (
    "Shipping a hash function turned out to be shipping an analytical "
    "artifact - I optimized the math-object standard and ignored who "
    "the real consumer was."
)

EX30_TECH_TERMS = {
    "Hash function": "deterministic mapping from a variable-length input to a fixed-size bucket identifier",
    "Prime multiplication": "large-prime-based hashing trick that yields good uniformity and high-bit mixing",
    "Entropy metric": "information-theoretic measure of distribution spread used here as a diversity signal",
    "Diversity metric": "feature-level measure of how spread out a result set is across facets",
    "SQL/Hive": "offline analytical query layer over the event data warehouse used by DS teams",
    "Stable ID": "a persistent, human-traceable identifier attached to each bucket so downstream analysis can join on it",
    "Analytical pipeline": "the DS/product workflow that turns raw event data into launch-decision evidence",
}

EX30_SITUATION = (
    "At eBay search I was in an unusually high-momentum collaboration with a "
    "PM, shipping a series of diversity-related features and metrics with "
    "almost no friction. I personally had a feeling of invincibility - needs "
    "identified, design fast, ship faster, PM driving launch, and the loop "
    "turned fast enough that I stopped looking for blockers. I was the deep-"
    "expertise IC on hash and diversity inside our group."
)

EX30_TASK = (
    "PM and I identified a new capability need: compute facet hash and "
    "entropy-based diversity metric on the real-time page-rendering path, "
    "as the foundation for a new round of diversity experiments. As the "
    "hash-domain IC, I owned the design."
)

EX30_ACTION = (
    "(1) Wrong first decision - elegant but single-framed design. I designed "
    "a math-elegant real-time hash: large-prime multiplication plus high-bit "
    "extraction. Uniformity was good, performance was high, extension was "
    "clean. I shipped it as an optional feature. My team's internal testing "
    "all passed and I was confident in the quality. Looking back, the root "
    "cause was not technical - I evaluated \"good\" by the hash-as-math-"
    "object standard (quality, uniformity, performance), and I never asked "
    "a more basic question: who outside my team will consume this, and what "
    "will they use it for.\n\n"
    "(2) Failure surfaces. Weeks after launch, confusion began escalating "
    "back from two or three downstream teams - mostly data science and "
    "analytics/product. They were stuck preparing launch analysis. My hash "
    "was implicit at the SQL/Hive layer with no stable identity, so DS "
    "could not track \"which bucket corresponds to which facet\" in their "
    "analytical queries, and they could not build explainable launch-"
    "decision support on top of it. The moment that escalation landed back "
    "on my desk was when this failure became real for me. I realized I had "
    "not shipped a hash function - I had shipped an analytical artifact, "
    "and I had designed it with zero analytical-consumer perspective.\n\n"
    "(3) Wrong second decision - sunk-cost rescue attempt. My first "
    "instinct was to propose a \"correct\" fix: modify search lower infra "
    "so hash became a first-class operator, plus matching changes to the "
    "data pipeline, the A/B test platform, and Hive SQL, so my elegant "
    "hash could be properly tracked end-to-end. I quickly realized this "
    "was a cross-four-team, multi-quarter infra change. The proposal did "
    "not go through. Looking back that is the right outcome, because it "
    "was using larger infra investment to rescue a framing error rather "
    "than admitting the framing itself was wrong.\n\n"
    "(4) Right third decision - consult and adopt prior art. I went to "
    "the indexing team and asked how their analytics pipeline adaptively "
    "absorbs new features and metrics. The answer was humbling: they "
    "already had a mature practice I had no idea existed. I followed "
    "their work. The final solution was an explicit cache of diversity "
    "aspect plus stable ID assignment. By my hash-expert standard this "
    "was \"worse\" - lower efficiency, no elegant scaling, zero math "
    "beauty. By the cross-functional standard it was \"better\", because "
    "it served what DS actually needed: traceable, explainable, auditable."
)

EX30_RESULT = (
    "Downstream confusion was resolved and launch analysis could proceed. "
    "But I have to be honest: this is not a happy ending. Two or three "
    "downstream teams had several weeks of analysis time burned by my "
    "design choice. My proposed infra rescue was rejected. The fix was "
    "not something I cleverly invented - it came from asking someone "
    "else who had the answer the whole time. The reputational cost was "
    "real: as the hash-domain expert, I shipped something in my own "
    "domain that confused the downstream consumers of my own work."
)

EX30_RISK_STATEMENT = (
    "Cost was externalized to two or three downstream DS/product teams "
    "whose analysis time was burned. Personal reputational cost inside "
    "my own expert domain. The failure was unambiguous: no ship of the "
    "original design, proposed rescue rejected, final fix sourced from "
    "prior art I had simply never asked about. Use this story for "
    "failure-type questions; it does not have a success-tail to soften it."
)

EX30_EVIDENCE_QUOTES = [
    "I had a feeling of invincibility - the collaboration loop was so smooth I stopped looking for blockers.",
    "The escalation landed on my desk and I realized I had not shipped a hash function, I had shipped an analytical artifact.",
    "Expertise had taught me to design first. I should have asked first.",
]

# EX-30 existing links get real relevance notes (5 rows from T-P0-351 preserved).
EX30_EXISTING_LINK_NOTES: dict[str, str] = {
    "OWN-1": (
        "Clean ownership-of-failure narrative: I owned the hash design, "
        "the failure was attributable to my framing, and I narrate the "
        "cost to downstream teams without deflecting."
    ),
    "OWN-8": (
        "Moving-fast-and-made-a-mistake fit: the smooth PM collaboration "
        "loop removed friction, which is precisely what let me ship a "
        "design without consumer audit."
    ),
    "ADP-5": (
        "Handling-a-mistake arc: escalation landed, I proposed a wrong "
        "rescue, then adopted prior art from the indexing team - a "
        "three-stage response to the mistake."
    ),
    "ADP-18": (
        "Recent-mistake-and-lesson framing: the lesson is a mental-model "
        "shift (ask who the consumer is before designing), not a "
        "tactical fix, and it is transferable."
    ),
    "EXE-2": (
        "Setback-in-timelines fit: downstream DS analysis was blocked, "
        "forcing a mid-flight pivot from my elegant design to a cached "
        "stable-ID solution borrowed from indexing."
    ),
}

# EX-30 gets 1 new link: ADP-15.
EX30_NEW_LINK: tuple[str, str] = (
    "ADP-15",
    "The cleanest unambiguous failure in my story pool; no success-tail, "
    "clear mental-model lesson (expert frame blind spot).",
)

# EX-30 theme tags (slug list).
EX30_THEME_SLUGS = [
    "failure_setback",
    "mentoring_coaching",
    "scope_creep_ambiguous",
    "conflict_disagreement",
]

# ---------------------------------------------------------------------------
# EX-33 - MoE -> Allocation Paradigm Shift (new row)
# ---------------------------------------------------------------------------

EX33_EXAMPLE_ID = "EX-33"
EX33_TITLE = "MoE -> Allocation Paradigm Shift - Org-Level Reframe via Honest Negative Result"
EX33_SOURCE_PROJECT = "eBay search - ranking to allocation paradigm"

EX33_PRINCIPLE_TAGS = [
    "organizational_change",
    "long_term_bet",
    "influence_without_authority",
    "calculated_risk",
    "paradigm_shift",
    "evidence_based_advocacy",
    "coalition_building",
]

EX33_ANALOGY = (
    "A wrapped success cannot convince anyone. A credibly honest negative "
    "result was the last chip that flipped the org's paradigm."
)

EX33_TECH_TERMS = {
    "MoE (Mixture of Experts)": "ranker architecture that routes inputs to specialized sub-networks ('experts') combined via a gating mechanism",
    "Neural ranking": "deep-model-based item scoring that replaces handcrafted boosting and tree-based rankers",
    "Pairwise ranking": "training scheme that scores each item independently and sorts, optimizing pairwise preference",
    "Whole-page optimization": "optimizing the full result page jointly rather than ranking items in isolation",
    "Reranking": "second-stage reorder of a candidate set produced by a base ranker, typically under page-level constraints",
    "Allocation policy": "explicit policy that decides how candidates are distributed across business goals, making tradeoffs visible at the page level",
    "Expert routing": "the gating-network decision that decides which expert handles a given query/item",
    "Item-level ranker": "a ranker that scores candidates one at a time, independent of the rest of the page",
    "MRR (Mean Reciprocal Rank)": "position-weighted retrieval metric that became a self-fulfilling prophecy because the ranker and the metric shared the same assumptions",
}

EX33_SITUATION = (
    "In the eBay search org, the dominant paradigm was pairwise distributed "
    "ranking - each item scored independently and then sorted. The industry "
    "had moved toward whole-page optimization and reranking, and several "
    "senior ICs, my manager, and I had been calling out this gap for "
    "several quarters. The org agreed with the direction at the abstract "
    "level, but nobody had a concrete path. It was a shared-vision, "
    "no-path situation."
)

EX33_TASK = (
    "Leadership assigned me ownership of a high-visibility project: migrate "
    "search from boosting to neural ranking plus MoE, consuming about 80 "
    "GPU nodes, which was nearly all the org-wide headroom, shared with "
    "the cross-org AI intake. On the surface this was a ranker upgrade. "
    "In my head it was also a critical empirical test of the ranker-"
    "centric paradigm itself: if even the most sophisticated ranker "
    "architecture could not solve the diversity and discovery problems we "
    "were seeing, that would be the strongest possible evidence for "
    "reframing the paradigm."
)

EX33_ACTION = (
    "(1) Framing decision at project launch - \"start test\", not "
    "\"test and launch\". Against org convention, my manager and I labeled "
    "the project scope as \"start test\" rather than \"test and launch\". "
    "Convention would have allowed us to wrap a failure as \"carry over to "
    "next quarter\", which protects the IC's track record but destroys the "
    "credibility of any paradigm-level signal the project produces. I gave "
    "up that protection on purpose - a wrapped success cannot convince "
    "anyone, and if I wanted this project to function as a paradigm test, "
    "the result had to be credible either way.\n\n"
    "(2) Moment of realization mid-execution. While adding a new expert "
    "to handle abandonment and exploration, I noticed that it and the "
    "conversion expert were frequently co-activated but contributed in "
    "opposite directions. I first attributed this to under-training and "
    "added more training rounds, but the behavior stayed. Then I realized "
    "it was structural - these two goal sets were orthogonal to conversion "
    "in a way that a single item-level ranker could not reconcile. More "
    "disturbing was a second finding: by our org's launch criteria (MRR "
    "up, revenue neutral) this expert was actually launchable, yet users "
    "were not being served better and homogeneity had gotten worse. That "
    "gap made me first question MRR itself as a self-fulfilling prophecy "
    "- the ranker training objective and the metric shared the same "
    "assumptions, so a \"win\" on the metric did not independently "
    "validate user outcome.\n\n"
    "(3) Converting failure into a reframe proposal. I wrote a detailed "
    "proposal arguing three things: (a) the ranker architecture cannot "
    "handle goals that are structurally orthogonal to conversion, such as "
    "diversity, abandonment, and exploration; (b) the org's metric system "
    "was masking this blind spot; (c) the right direction was to make the "
    "business tradeoff explicit as an allocation policy, letting the model "
    "unleash its power inside a defined policy frame, instead of asking "
    "the ranker to carry both optimization and tradeoff on the same head. "
    "The proposal was accepted because the several-quarter pre-work from "
    "me, the senior ICs, and my manager had prepared the org "
    "psychologically. MoE's negative result was the last undeniable "
    "empirical chip."
)

EX33_RESULT = (
    "The MoE direction was officially deprecated and did not ship. But "
    "three org-level outcomes followed. First, the team was renamed from "
    "\"ranking modeling\" to \"policy learning\" and eventually to the "
    "\"Allocation team\", reflecting the full paradigm shift. Second, "
    "allocation policy became the team's new main line of work. Third, "
    "that new direction later shipped over 200M in annualized GMB. The "
    "outcome I care about most is not the GMB number: it is that the "
    "org's default planning question shifted from \"how do we train a "
    "better ranker\" to \"what user problem are we solving and is a "
    "ranker the right tool for it\". That mental-model change is "
    "irreversible."
)

EX33_RISK_STATEMENT = (
    "I staked my personal track record as collateral when I refused the "
    "carry-over convention. If MoE had been wrapped, the failure would "
    "have been invisible but so would the paradigm lesson. Real costs "
    "were personal (no carry-over protection for my record), team "
    "(mindset adjustment away from \"we are launching something\"), and "
    "political (signaling to leadership that a top-down strategic project "
    "might not work). DO NOT use this story for pure-failure questions - "
    "the 200M+ tail will make the interviewer feel the story is a "
    "disguised success, which backfires. For failure questions use EX-30 "
    "instead."
)

EX33_EVIDENCE_QUOTES = [
    "A wrapped success cannot convince anyone. A credibly honest negative result was the last undeniable empirical chip.",
    "I used 'start test' framing instead of 'test and launch', which gave up my carry-over protection on purpose.",
    "MRR was a self-fulfilling prophecy because the ranker's training objective and the evaluation metric shared the same assumptions.",
    "Alt framing B (Influence Without Authority): coalition + risk-taking + opponents-language + evidence-based advocacy over several quarters.",
    "Alt framing C (Calculated Risk): short-term personal cost traded for long-term organizational value; used my track record as collateral for a paradigm bet.",
]

# EX-33 links: (question_id, relevance_note)
EX33_LINKS: list[tuple[str, str]] = [
    ("OWN-6", "Bold risk at work - 'start test' framing staked my personal track record on a paradigm bet with no carry-over protection."),
    ("PS-6", "Calculated risk - short-term personal cost (no carry-over cover) traded for long-term org value (paradigm shift + 200M+ GMB tail)."),
    ("OWN-10", "Long-term impact demonstration - multi-quarter paradigm push across the org, not a single-quarter ship."),
    ("IMP-10", "Long-term impact example - the full Allocation policy 200M+ GMB arc and team rename from ranking to allocation."),
    ("IMP-9", "Short-term vs long-term tradeoff - forgoing carry-over protection and a 'launchable' MoE expert for long-term paradigm credibility."),
    ("INN-6", "New process/strategy with major improvement - the allocation policy proposal replaced ranker-centric planning as the team's main line."),
    ("INN-8", "Questioned a traditional approach - pairwise distributed ranking - and proposed reranking + allocation policy as the replacement paradigm."),
    ("COM-2", "Persuade others to change direction - core influence-without-authority match; convinced the org to deprecate a top-down strategic project."),
    ("COL-5", "Align teams/stakeholders on shared goal - coalition building over several quarters with senior ICs and my manager before the empirical chip landed."),
    ("IMP-4", "Improved a process/system adding significant value - paradigm shift yielded 200M+ annualized GMB and a durable mental-model change."),
    ("INN-1", "Identified an opportunity for improvement - recognized the paradigm gap between pairwise ranking and the industry's whole-page direction."),
    ("OWN-9", "Innovate without all the information - ran an 80-GPU empirical test as the way forward under strategic uncertainty; the negative result was the signal."),
]

# EX-33 theme tags (slug list).
EX33_THEME_SLUGS = [
    "leadership_direction",
    "ownership_accountability",
    "prioritization_tradeoffs",
    "technical_problem_solving",
    "failure_setback",
    "ambiguity_uncertainty",
]


def populate(db_path: Path = DB_PATH) -> dict[str, int]:
    """Run all EX-30 and EX-33 population writes in one transaction."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        now = datetime.utcnow().isoformat(sep=" ")

        # ------------------- EX-30 UPDATE -------------------
        ex30_row = cur.execute(
            "SELECT id FROM behavioral_examples WHERE example_id = 'EX-30'"
        ).fetchone()
        if ex30_row is None:
            raise RuntimeError("EX-30 placeholder row missing - run _seed_failure_placeholders first")
        ex30_db_id = ex30_row["id"]

        cur.execute(
            """
            UPDATE behavioral_examples
               SET title = ?,
                   source_project = ?,
                   situation = ?,
                   task = ?,
                   action = ?,
                   result = ?,
                   evidence_quotes = ?,
                   principle_tags = ?,
                   risk_statement = ?,
                   analogy = ?,
                   tech_terms = ?
             WHERE id = ?
            """,
            (
                EX30_TITLE,
                EX30_SOURCE_PROJECT,
                EX30_SITUATION,
                EX30_TASK,
                EX30_ACTION,
                EX30_RESULT,
                json.dumps(EX30_EVIDENCE_QUOTES, ensure_ascii=False),
                json.dumps(EX30_PRINCIPLE_TAGS, ensure_ascii=False),
                EX30_RISK_STATEMENT,
                EX30_ANALOGY,
                json.dumps(EX30_TECH_TERMS, ensure_ascii=False),
                ex30_db_id,
            ),
        )

        # Update existing link relevance notes.
        updated_links = 0
        for qid_str, note in EX30_EXISTING_LINK_NOTES.items():
            q_row = cur.execute(
                "SELECT id FROM behavioral_questions WHERE question_id = ?",
                (qid_str,),
            ).fetchone()
            if q_row is None:
                raise RuntimeError(f"question {qid_str} not found for EX-30 existing link update")
            cur.execute(
                """
                UPDATE question_example_links
                   SET relevance_note = ?
                 WHERE question_id = ? AND example_id = ?
                """,
                (note, q_row["id"], ex30_db_id),
            )
            updated_links += cur.rowcount

        # Add new EX-30 link (ADP-15) if not present.
        new_qid_str, new_note = EX30_NEW_LINK
        q_row = cur.execute(
            "SELECT id FROM behavioral_questions WHERE question_id = ?",
            (new_qid_str,),
        ).fetchone()
        if q_row is None:
            raise RuntimeError(f"question {new_qid_str} not found for EX-30 new link")
        existing = cur.execute(
            "SELECT id FROM question_example_links WHERE question_id = ? AND example_id = ?",
            (q_row["id"], ex30_db_id),
        ).fetchone()
        inserted_ex30_links = 0
        if existing is None:
            cur.execute(
                """
                INSERT INTO question_example_links (question_id, example_id, relevance_note, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (q_row["id"], ex30_db_id, new_note, now),
            )
            inserted_ex30_links = 1
        else:
            cur.execute(
                """
                UPDATE question_example_links
                   SET relevance_note = ?
                 WHERE id = ?
                """,
                (new_note, existing["id"]),
            )

        # EX-30 theme tags.
        ex30_theme_inserts = 0
        for slug in EX30_THEME_SLUGS:
            theme_row = cur.execute(
                "SELECT id FROM behavioral_themes WHERE slug = ?",
                (slug,),
            ).fetchone()
            if theme_row is None:
                raise RuntimeError(f"theme '{slug}' not found in behavioral_themes")
            existing_tag = cur.execute(
                "SELECT 1 FROM example_theme_tags WHERE example_id = ? AND theme_id = ?",
                (ex30_db_id, theme_row["id"]),
            ).fetchone()
            if existing_tag is None:
                cur.execute(
                    """
                    INSERT INTO example_theme_tags (example_id, theme_id, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (ex30_db_id, theme_row["id"], now),
                )
                ex30_theme_inserts += 1

        # ------------------- EX-33 INSERT -------------------
        ex33_row = cur.execute(
            "SELECT id FROM behavioral_examples WHERE example_id = ?",
            (EX33_EXAMPLE_ID,),
        ).fetchone()
        inserted_ex33 = 0
        if ex33_row is None:
            cur.execute(
                """
                INSERT INTO behavioral_examples (
                    example_id, title, source_project,
                    situation, task, action, result,
                    evidence_quotes, principle_tags,
                    risk_statement, analogy, tech_terms,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    EX33_EXAMPLE_ID,
                    EX33_TITLE,
                    EX33_SOURCE_PROJECT,
                    EX33_SITUATION,
                    EX33_TASK,
                    EX33_ACTION,
                    EX33_RESULT,
                    json.dumps(EX33_EVIDENCE_QUOTES, ensure_ascii=False),
                    json.dumps(EX33_PRINCIPLE_TAGS, ensure_ascii=False),
                    EX33_RISK_STATEMENT,
                    EX33_ANALOGY,
                    json.dumps(EX33_TECH_TERMS, ensure_ascii=False),
                    now,
                ),
            )
            inserted_ex33 = 1
            ex33_db_id = cur.lastrowid
        else:
            ex33_db_id = ex33_row["id"]
            cur.execute(
                """
                UPDATE behavioral_examples
                   SET title = ?,
                       source_project = ?,
                       situation = ?,
                       task = ?,
                       action = ?,
                       result = ?,
                       evidence_quotes = ?,
                       principle_tags = ?,
                       risk_statement = ?,
                       analogy = ?,
                       tech_terms = ?
                 WHERE id = ?
                """,
                (
                    EX33_TITLE,
                    EX33_SOURCE_PROJECT,
                    EX33_SITUATION,
                    EX33_TASK,
                    EX33_ACTION,
                    EX33_RESULT,
                    json.dumps(EX33_EVIDENCE_QUOTES, ensure_ascii=False),
                    json.dumps(EX33_PRINCIPLE_TAGS, ensure_ascii=False),
                    EX33_RISK_STATEMENT,
                    EX33_ANALOGY,
                    json.dumps(EX33_TECH_TERMS, ensure_ascii=False),
                    ex33_db_id,
                ),
            )

        # EX-33 links.
        inserted_ex33_links = 0
        for qid_str, note in EX33_LINKS:
            q_row = cur.execute(
                "SELECT id FROM behavioral_questions WHERE question_id = ?",
                (qid_str,),
            ).fetchone()
            if q_row is None:
                raise RuntimeError(f"question {qid_str} not found for EX-33 link")
            existing = cur.execute(
                "SELECT id FROM question_example_links WHERE question_id = ? AND example_id = ?",
                (q_row["id"], ex33_db_id),
            ).fetchone()
            if existing is None:
                cur.execute(
                    """
                    INSERT INTO question_example_links (question_id, example_id, relevance_note, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (q_row["id"], ex33_db_id, note, now),
                )
                inserted_ex33_links += 1
            else:
                cur.execute(
                    """
                    UPDATE question_example_links
                       SET relevance_note = ?
                     WHERE id = ?
                    """,
                    (note, existing["id"]),
                )

        # EX-33 theme tags.
        ex33_theme_inserts = 0
        for slug in EX33_THEME_SLUGS:
            theme_row = cur.execute(
                "SELECT id FROM behavioral_themes WHERE slug = ?",
                (slug,),
            ).fetchone()
            if theme_row is None:
                raise RuntimeError(f"theme '{slug}' not found in behavioral_themes")
            existing_tag = cur.execute(
                "SELECT 1 FROM example_theme_tags WHERE example_id = ? AND theme_id = ?",
                (ex33_db_id, theme_row["id"]),
            ).fetchone()
            if existing_tag is None:
                cur.execute(
                    """
                    INSERT INTO example_theme_tags (example_id, theme_id, created_at)
                    VALUES (?, ?, ?)
                    """,
                    (ex33_db_id, theme_row["id"], now),
                )
                ex33_theme_inserts += 1

        conn.commit()
        return {
            "ex30_existing_links_updated": updated_links,
            "ex30_new_links_inserted": inserted_ex30_links,
            "ex30_theme_tags_inserted": ex30_theme_inserts,
            "ex33_inserted": inserted_ex33,
            "ex33_links_inserted": inserted_ex33_links,
            "ex33_theme_tags_inserted": ex33_theme_inserts,
        }
    finally:
        conn.close()


def main() -> None:
    result = populate()
    print("[populate_hash_and_moe] " + " ".join(f"{k}={v}" for k, v in result.items()))


if __name__ == "__main__":
    main()
