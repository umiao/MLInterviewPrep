"""Insert EX-33B (failure-cut of MoE project) and link it to the failure cluster questions.

EX-33B is a separate framing of the same project as EX-33. EX-33 frames it as a
paradigm shift / influence-without-authority story with a 200M+ tail. EX-33B
frames the SAME work as a clean failure story stopping at the moment of
realization, with no rescue. The two must never be combined in a single answer.

This script is idempotent: re-running will not duplicate the example or links.
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "mle_prep.db"

EXAMPLE_ID = "EX-33B"
TITLE = "MoE Over-Iteration: A Model Believer's Humility Lesson on Problem Formulation"
SOURCE_PROJECT = "eBay search - ranking to allocation paradigm (failure-cut)"

SITUATION = (
    "At eBay search I was a strong believer in the model-side narrative: the industry "
    "had moved toward whole-page optimization, neural ranking, and MoE architectures, "
    "and I shared the assumption that increasingly sophisticated rankers would unlock "
    "the diversity, abandonment, and exploration problems we were stuck on. Leadership "
    "assigned me ownership of a high-visibility project to migrate search from boosting "
    "to neural ranking + MoE, consuming ~80 GPU nodes -- nearly all the org-wide "
    "headroom. From day one I framed this in my head as 'the model architecture upgrade "
    "that finally lets us solve everything.'"
)

TASK = (
    "Deliver a working MoE ranker that integrated multiple expert heads (conversion, "
    "abandonment, exploration) and demonstrated improvement on our org's launch "
    "criteria. My personal stake was even higher than the project scope: I had been "
    "advocating internally that model-side sophistication was the right answer, and "
    "this project was implicitly the proof."
)

ACTION = (
    "(1) First wall - bias in expert routing. Initial training showed the gating "
    "network was collapsing onto the conversion expert and ignoring the others. I "
    "treated this as a technical bug: re-balanced training data, added auxiliary "
    "losses to encourage expert diversification, retrained. Bias reduced.\n\n"
    "(2) Second wall - degraded MoE router behavior. After the bias fix, the router "
    "started oscillating - co-activating experts that were pulling in opposite "
    "directions. I again treated it as a tuning problem: more training rounds, "
    "careful warmup schedules, auxiliary load-balancing terms. The oscillation "
    "calmed down on the surface.\n\n"
    "(3) Third wall - generating a new orthogonal expert. I noticed that abandonment "
    "and exploration signals were structurally different from conversion, so I "
    "designed and trained a dedicated orthogonal expert for them. This was the most "
    "'I'm finally cracking it' moment of the project for me - architecturally clean, "
    "theoretically motivated.\n\n"
    "(4) The realization. With all three fixes in place and the system technically "
    "working, I looked at the eval and saw something I could not engineer my way out "
    "of: the new expert was structurally in conflict with our existing core KPI "
    "metrics. Worse, by our launch criteria (MRR up, revenue neutral) the expert was "
    "technically 'launchable' on paper, but users were not being served better and "
    "homogeneity was getting worse. The system was tech-unblocked but business-"
    "unlaunchable. I had spent the budget, the GPU headroom, and my own credibility "
    "chasing increasingly sophisticated model-side fixes for a problem that was not "
    "a model problem in the first place -- it was a problem-formulation problem. "
    "The ranker architecture, no matter how fancy, could not reconcile goals that "
    "were structurally orthogonal to conversion on a single item-level head.\n\n"
    "(5) What I did with the realization. I stopped iterating. I did not try to "
    "wrap it as a partial win or carry it over to the next quarter. I wrote up the "
    "technical state honestly -- what worked, what did not, and crucially why no "
    "amount of further model iteration would fix it -- and surfaced it to my "
    "manager and the senior ICs."
)

RESULT = (
    "The MoE direction did not launch. Technically the system was complete; "
    "business-wise the direction was wrong from day one because we had been asking "
    "the wrong question. I had burned ~80 GPU nodes of org-wide headroom, several "
    "quarters of my own time, and the implicit credibility I had built advocating "
    "for the model-side narrative. There was no rescue and no silver lining I could "
    "honestly offer.\n\n"
    "The lesson I took out of it -- and the reason I tell this story -- is respect "
    "for problem formulation over model sophistication. Specifically:\n"
    "- Before reaching for a more sophisticated model, I now force myself to ask "
    "'is the thing I am trying to optimize even the right objective, or am I about "
    "to spend a quarter making a wrong objective more efficient?'\n"
    "- I stopped treating 'the model is technically working' as evidence the project "
    "is on track. Tech-unblocked is not business-launchable, and a working model "
    "that optimizes a misaligned objective is worse than no model, because it spends "
    "real resources and sets a misleading anchor for the team.\n"
    "- When I see myself fixing one technical wall after another in quick succession "
    "(bias -> router -> new expert), I treat that as a smell that the problem might "
    "not be where I think it is, and I force a step back to re-question the "
    "formulation, not just the next layer of fix.\n"
    "- I also became much more careful about advocating for a paradigm I have "
    "personal investment in. Being a model believer is fine; being a model believer "
    "who refuses to look at non-model explanations is how you burn 80 GPUs."
)

EVIDENCE_QUOTES = [
    "The system was tech-unblocked but business-unlaunchable.",
    "I was fixing one wall after another -- bias, router, orthogonal expert -- and that pattern itself should have told me the problem was not where I was looking.",
    "No amount of further model iteration would fix it, because the problem was not a model problem.",
    "Tech-unblocked is not business-launchable. A working model that optimizes a misaligned objective is worse than no model.",
    "Being a model believer is fine; being a model believer who refuses to look at non-model explanations is how you burn 80 GPUs.",
]

PRINCIPLE_TAGS = [
    "failure",
    "humility",
    "problem_formulation",
    "model_believer_blind_spot",
    "dive_deep",
    "learn_and_be_curious",
    "ownership",
    "bias_for_action_correction",
]

RISK_STATEMENT = (
    "This is a clean failure story with NO rescue. Do not append the EX-33 paradigm-"
    "shift / 200M+ tail under any circumstance -- that ending belongs to a different "
    "framing of the same project (EX-33) and using both endings simultaneously will "
    "make the interviewer feel the failure is being laundered.\n\n"
    "TEMPORAL POV PRINCIPLE: This is not fabrication. It is an honest account from a "
    "specific moment in the project's life. At that moment -- before the org-level "
    "paradigm shift happened -- the neural-combiner / architecture-innovation "
    "iteration WAS a failure, full stop. We cannot retroactively use future success "
    "to whitewash that moment's lesson. Different project phases warrant different "
    "POVs, and a faithful narration of one phase does not require disclosing the "
    "other.\n\n"
    "USAGE RULE: For failure / mistake / setback / 'what would you do differently' "
    "questions, stop the story at the lesson, not at the org reframe. If the "
    "interviewer follows up with 'what happened to the team / project after that,' "
    "then and only then it is acceptable to briefly mention 'the org eventually used "
    "those negative findings to reframe the problem as an allocation problem, but "
    "that's a separate story about org-level paradigm shift, not about what I "
    "personally learned from this failure.'"
)

ANALOGY = (
    "I kept patching leaks on a boat that was pointed at the wrong harbor. Each "
    "patch worked. The boat still arrived nowhere we wanted to be."
)

TECH_TERMS = {
    "MoE (Mixture of Experts)": "ranker architecture that routes inputs to specialized sub-networks ('experts') combined via a gating mechanism",
    "Neural ranking": "deep-model-based item scoring that replaces handcrafted boosting and tree-based rankers",
    "Expert routing": "the gating-network decision that decides which expert handles a given query/item",
    "MRR (Mean Reciprocal Rank)": "position-weighted retrieval metric; here it acted as a self-fulfilling prophecy because the ranker and the metric shared the same assumptions",
    "Item-level ranker": "a ranker that scores candidates one at a time, independent of the rest of the page",
    "Allocation policy": "explicit policy that decides how candidates are distributed across business goals, making tradeoffs visible at the page level",
}

QUESTION_LINKS = [
    ("OWN-1",  "Direct ownership of failure: I owned the 80 GPUs, the credibility, and the call to stop iterating rather than wrap it as a partial win."),
    ("ADP-15", "The biggest lesson from this failed project IS the entire point of this story-cut: respect for problem formulation over model sophistication."),
    ("ADP-12", "What I would do differently: question the problem formulation BEFORE reaching for the next model-side fix, especially when fixing one wall just exposes the next."),
    ("ADP-18", "Frame as: 'I assumed model sophistication was the answer when the actual constraint was business problem formulation.' Recent enough to feel current; concrete enough to be specific."),
    ("OWN-11", "Ownership of a challenging situation, but lean on the 'taking responsibility for STOPPING' angle, not the 'taking responsibility for shipping' angle."),
    ("EXE-9",  "Use only if interviewer accepts a personal-recovery framing rather than project-recovery. The project did not recover; my judgment did. If they want a project bounce-back story, prefer EX-15 or EX-16."),
]


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 1. Upsert example
    c.execute("SELECT id FROM behavioral_examples WHERE example_id=?", (EXAMPLE_ID,))
    existing = c.fetchone()
    if existing:
        print(f"[update] {EXAMPLE_ID} already exists (id={existing[0]}), updating fields")
        c.execute(
            """
            UPDATE behavioral_examples
            SET title=?, source_project=?, situation=?, task=?, action=?, result=?,
                evidence_quotes=?, principle_tags=?, risk_statement=?, analogy=?, tech_terms=?
            WHERE example_id=?
            """,
            (
                TITLE, SOURCE_PROJECT, SITUATION, TASK, ACTION, RESULT,
                json.dumps(EVIDENCE_QUOTES, ensure_ascii=False),
                json.dumps(PRINCIPLE_TAGS, ensure_ascii=False),
                RISK_STATEMENT, ANALOGY,
                json.dumps(TECH_TERMS, ensure_ascii=False),
                EXAMPLE_ID,
            ),
        )
        example_db_id = existing[0]
    else:
        c.execute(
            """
            INSERT INTO behavioral_examples
            (example_id, title, source_project, situation, task, action, result,
             evidence_quotes, principle_tags, risk_statement, analogy, tech_terms)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                EXAMPLE_ID, TITLE, SOURCE_PROJECT, SITUATION, TASK, ACTION, RESULT,
                json.dumps(EVIDENCE_QUOTES, ensure_ascii=False),
                json.dumps(PRINCIPLE_TAGS, ensure_ascii=False),
                RISK_STATEMENT, ANALOGY,
                json.dumps(TECH_TERMS, ensure_ascii=False),
            ),
        )
        example_db_id = c.lastrowid
        print(f"[insert] {EXAMPLE_ID} created with db id={example_db_id}")

    # 2. Upsert question links
    inserted = 0
    updated = 0
    for qid_str, note in QUESTION_LINKS:
        c.execute("SELECT id FROM behavioral_questions WHERE question_id=?", (qid_str,))
        q_row = c.fetchone()
        if not q_row:
            print(f"[warn] question {qid_str} not found, skipping")
            continue
        question_db_id = q_row[0]

        c.execute(
            "SELECT id FROM question_example_links WHERE question_id=? AND example_id=?",
            (question_db_id, example_db_id),
        )
        existing_link = c.fetchone()
        if existing_link:
            c.execute(
                "UPDATE question_example_links SET relevance_note=? WHERE id=?",
                (note, existing_link[0]),
            )
            updated += 1
        else:
            c.execute(
                "INSERT INTO question_example_links (question_id, example_id, relevance_note) VALUES (?,?,?)",
                (question_db_id, example_db_id, note),
            )
            inserted += 1

    conn.commit()
    print(f"[links] inserted={inserted} updated={updated}")

    # 3. Verify
    c.execute("SELECT example_id, title FROM behavioral_examples WHERE example_id=?", (EXAMPLE_ID,))
    print("[verify-example]", c.fetchone())
    c.execute(
        """
        SELECT q.question_id, l.relevance_note
        FROM question_example_links l
        JOIN behavioral_questions q ON q.id = l.question_id
        WHERE l.example_id = ?
        ORDER BY q.question_id
        """,
        (example_db_id,),
    )
    print("[verify-links]")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1][:80]}...")

    conn.close()


if __name__ == "__main__":
    main()
