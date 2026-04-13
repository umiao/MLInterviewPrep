"""Rework EX-33 (MoE Paradigm Shift) per T-P0-386.

Lead Result with the 200M GMB number; keep honest negative result framing
but let the downstream win close the arc. Sharpen Action ownership ("we" -> "I"
where ambiguous). Add STORY 33 to docs/bq_improved_stories.md.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "mle_prep.db"
STORIES_MD = ROOT / "docs" / "bq_improved_stories.md"

NEW_RESULT = (
    "The downstream Allocation direction that emerged from this failure later shipped "
    "**200M+ in annualized GMB** -- the paradigm reframe, not the MoE project itself, "
    "was the real business outcome. MoE was officially deprecated and did not ship, "
    "and that honest negative result was the chip that made the reframe credible. "
    "Three org-level follow-throughs: (1) the team was renamed from \"ranking modeling\" "
    "to \"policy learning\" and eventually to \"Allocation team\", reflecting the full "
    "paradigm shift; (2) allocation policy became the team's new main line of work, "
    "with multiple downstream initiatives (authenticated listings, C2C new listings, "
    "diversity framework reuse) shipping under the new paradigm; (3) leadership adopted "
    "the allocation framing as the default planning question -- \"what user problem are "
    "we solving and is a ranker the right tool for it\" replaced \"how do we train a "
    "better ranker\". That mental-model change is irreversible, and the 200M GMB figure "
    "is its downstream receipt."
)

NEW_ACTION = (
    "(1) Framing decision at project launch - \"start test\", not \"test and launch\". "
    "Against org convention, I labeled the project scope as \"start test\" rather than "
    "\"test and launch\" (my manager signed off, but the framing was mine to propose and own). "
    "Convention would have allowed me to wrap a failure as \"carry over to next quarter\", "
    "which protects the IC's track record but destroys the credibility of any paradigm-level "
    "signal the project produces. I gave up that protection on purpose - a wrapped success "
    "cannot convince anyone, and if I wanted this project to function as a paradigm test, "
    "the result had to be credible either way.\n\n"
    "(2) Moment of realization mid-execution. While adding a new expert to handle abandonment "
    "and exploration, I noticed that it and the conversion expert were frequently co-activated "
    "but contributed in opposite directions. I first attributed this to under-training and "
    "added more training rounds, but the behavior stayed. Then I realized it was structural - "
    "these two goal sets were orthogonal to conversion in a way that a single item-level "
    "ranker could not reconcile. More disturbing was a second finding: by our org's launch "
    "criteria (MRR up, revenue neutral) this expert was actually launchable, yet users were "
    "not being served better and homogeneity had gotten worse. That gap made me first question "
    "MRR itself as a self-fulfilling prophecy - the ranker training objective and the metric "
    "shared the same assumptions, so a \"win\" on the metric did not independently validate "
    "user outcome.\n\n"
    "(3) Converting failure into a reframe proposal. I wrote a detailed proposal arguing three "
    "things: (a) the ranker architecture cannot handle goals that are structurally orthogonal "
    "to conversion, such as diversity, abandonment, and exploration; (b) the org's metric "
    "system was masking this blind spot; (c) the right direction was to make the business "
    "tradeoff explicit as an allocation policy, letting the model unleash its power inside a "
    "defined policy frame, instead of asking the ranker to carry both optimization and "
    "tradeoff on the same head. I drove the proposal through the review cycle personally; "
    "the several-quarter pre-work from me, senior ICs, and my manager had prepared the org "
    "psychologically, and MoE's negative result was the last undeniable empirical chip."
)

STORY_33_MD = """## STORY 33: MoE Paradigm Shift -- Honest Negative Result, 200M+ Downstream (EX-33)

**Situation:** In the eBay search org, the dominant paradigm was pairwise distributed ranking -- each item scored independently and then sorted. The industry had moved toward whole-page optimization and reranking, and several senior ICs, my manager, and I had been flagging the gap for several quarters. The org agreed at the abstract level but had no concrete path forward.

**Risk if not addressed:** A ranker-centric paradigm cannot reconcile goals that are structurally orthogonal to conversion (diversity, abandonment, exploration). Without an empirical test the org could not reject, the paradigm would persist -- and every subsequent ranker upgrade would inherit the same blind spot.

> **Simple analogy:** You suspect the entire blueprint of a factory is wrong, but everyone keeps asking for a better machine on the same assembly line. The only way to prove the blueprint is the problem is to build the most sophisticated machine possible *on that exact line* -- and let its honest failure show that the line itself has to change.

**Action:**
- **Framing at project launch -- "start test", not "test and launch".** Leadership assigned me the high-visibility MoE + neural-ranking project (~80 GPU nodes, nearly all org-wide headroom). I labeled the scope as "start test" against org convention. That gave up my carry-over protection on purpose: a wrapped success cannot convince anyone, and I wanted the result to be credible either way.
- **Mid-execution realization.** Adding an expert for abandonment/exploration, I saw it co-activate with the conversion expert in opposite directions -- structural, not a training-rounds problem. A second finding: by launch criteria (MRR up, revenue neutral) the expert was launchable, yet homogeneity got worse. That made me question MRR as a self-fulfilling prophecy -- training objective and metric shared the same assumptions.
- **Converting failure into a reframe proposal.** I wrote a proposal arguing: (a) the ranker architecture cannot carry goals structurally orthogonal to conversion; (b) the metric system was masking it; (c) the right move was to make the tradeoff explicit as an **allocation policy**, letting the model work inside a defined frame. I drove it through the review cycle personally.

**Result:** The MoE direction was **officially deprecated** and did not ship -- a credibly honest negative result. But the downstream Allocation direction that emerged from it later shipped **200M+ in annualized GMB**, and three org-level follow-throughs locked in the reframe: (1) the team was **renamed** from "ranking modeling" -> "policy learning" -> **"Allocation team"**; (2) allocation policy became the team's new main line of work, with multiple downstream initiatives (authenticated listings, C2C new listings, diversity framework reuse) shipping under it; (3) leadership's default planning question shifted from "how do we train a better ranker" to "what user problem are we solving and is a ranker the right tool for it". **That mental-model change is irreversible, and the 200M GMB is its downstream receipt.**

---

"""


def main() -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute(
        "UPDATE behavioral_examples SET action = ?, result = ? WHERE example_id = ?",
        (NEW_ACTION, NEW_RESULT, "EX-33"),
    )
    assert cur.rowcount == 1, f"expected 1 row updated, got {cur.rowcount}"
    con.commit()
    con.close()
    print(f"[DB] EX-33 updated: action={len(NEW_ACTION)} chars, result={len(NEW_RESULT)} chars")

    text = STORIES_MD.read_text(encoding="utf-8")
    if "## STORY 33:" in text:
        print("[MD] STORY 33 already present -- skipping insert")
        return
    anchor = "## EXISTING ANSWERS (COL-1 through COL-4) -- Improved"
    assert anchor in text, "anchor not found in stories file"
    new_text = text.replace(anchor, STORY_33_MD + anchor, 1)
    STORIES_MD.write_text(new_text, encoding="utf-8")
    print(f"[MD] STORY 33 inserted before '{anchor}'")


if __name__ == "__main__":
    main()
