"""Seed: Google R1 IPS / counterfactual eval / debiased NDCG drill (company_id=3).

Covers T-P0-418 AC:
 (1) IPS reweighting by 1/P(shown),
 (2) Examination hypothesis P(click) = P(exam) * P(rel),
 (3) SNIPS self-normalized estimator + bias/variance tradeoff,
 (4) One-line SIGIR paper contribution + one-line biggest limitation,
 (5) How propensity is estimated (result randomization, EM, intervention
     harvesting, position bias model fit).

Each section is a 30-60 second oral answer for Google R1 staging.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = (
    "IPS / Counterfactual Eval / Debiased NDCG Drill "
    "(Google R1 Prep, SIGIR talking points)"
)


def build_note() -> StudyNoteBuilder:
    """Build the IPS / counterfactual eval drill study note."""
    b = StudyNoteBuilder()
    b.set_title(
        "IPS / Counterfactual Eval / Debiased NDCG Drill "
        "-- SIGIR Paper Talking Points"
    )

    b.add_prerequisites([
        "Learning to rank: NDCG, DCG, relevance grades",
        "Logged bandit / off-policy evaluation basics",
        "Click models at a high level (PBM, cascade)",
        "Importance sampling / Horvitz-Thompson estimator",
    ])

    b.add_term("IPS", "Inverse Propensity Scoring",
               "Reweight each logged observation by 1 / P(shown) to un-bias the estimate of a counterfactual policy")
    b.add_term("PBM", "Position-Based Model",
               "Click factorizes into examination and relevance: P(click|q,d,k) = P(exam|k) * P(rel|q,d)")
    b.add_term("SNIPS", "Self-Normalized IPS",
               "Divide the IPS weighted sum by the sum of weights; biased but much lower variance than vanilla IPS")
    b.add_term("CEM", "Counterfactual Evaluation Metric",
               "Any estimator that answers 'what would metric X be under policy pi?' using only logs from policy pi0")
    b.add_term("NDCG", "Normalized Discounted Cumulative Gain",
               "Position-discounted relevance sum normalized by the ideal ranking; standard LTR metric")
    b.add_term("DCG", "Discounted Cumulative Gain",
               "Un-normalized relevance sum with logarithmic position discount")

    # --- Section 0: Framing ---
    b.add_section("0. Why Counterfactual Eval (The Framing)", [
        "In production ranking, users only click results that were shown to them. "
        "Training on clicks directly learns to reproduce the logging policy, not "
        "the true relevance. A/B tests are the gold standard but slow, expensive, "
        "and unsafe for bad candidates. Counterfactual evaluation asks: 'given "
        "logs from policy pi0, what would NDCG be if we deployed policy pi?' -- "
        "without running a live test.",
        FormulaBlock(
            latex=(
                r"V(\pi) = \mathbb{E}_{(q,\mathbf{d}) \sim \pi_0}\Bigl["
                r"\tfrac{\pi(\mathbf{d}\mid q)}{\pi_0(\mathbf{d}\mid q)} \cdot r(q,\mathbf{d})\Bigr]"
            ),
            explanation="Off-policy value: reweight logged rewards by the policy ratio (Horvitz-Thompson):",
        ),
        "Two biases make naive click-based eval wrong: (i) **position bias** "
        "-- top results are examined far more often, so clicks overstate their "
        "relevance; (ii) **selection bias** -- pi0 never showed most (q,d) "
        "pairs, so clicks are only observed on a biased subset.",
        "Oral shortcut: 'Naive clicks confound relevance with what pi0 chose "
        "to show and where. IPS pulls the policy out by reweighting with "
        "1/P(shown); examination models pull position out by factoring "
        "click = exam * rel.'",
    ])

    # --- AC (1): IPS reweighting by 1/P(shown) ---
    b.add_section("1. IPS Reweighting by 1/P(shown)", [
        "**IPS** is the Horvitz-Thompson trick applied to logged interactions. "
        "For each (query, document) pair in the log, divide the observed reward "
        "(click or graded relevance signal) by the probability that pi0 would "
        "have shown that document at that position:",
        FormulaBlock(
            latex=(
                r"\hat{V}_{\text{IPS}}(\pi) = \frac{1}{N} \sum_{i=1}^{N} "
                r"\frac{\mathbb{1}[d_i \in \pi(q_i)]}{p_i} \cdot c_i"
            ),
            explanation="IPS estimator: indicator that the new policy shows d_i, divided by the shown-probability p_i:",
        ),
        "Here c_i is the observed click (or relevance judgment), and p_i = "
        "P(d_i shown at position k_i under pi0). When p_i is correct, the "
        "estimator is unbiased -- E[IPS] = V(pi). That property requires full "
        "support: every action pi might take must have nonzero propensity under "
        "pi0 (overlap condition). If pi0 never shows d at position 1, no amount "
        "of reweighting can tell you what would happen if pi did.",
        "Practical form for ranking: instead of a joint propensity over the "
        "whole list, the **PBM** factorization lets us use per-position "
        "propensities p_k -- much easier to estimate.",
        FormulaBlock(
            latex=(
                r"\hat{\Delta}(\pi) = \sum_{q,d} "
                r"\frac{c_{q,d}}{p_{k_0(q,d)}} \cdot "
                r"\mathrm{rel\text{-}gain}_\pi(q,d)"
            ),
            explanation="Per-position IPS: only the position propensity enters, because we assume click = exam_k * rel:",
        ),
        "Pitfall: tiny p_i (near zero) -- a single logged click is divided by "
        "1e-4 and swamps the sum. Variance blows up faster than bias shrinks. "
        "Standard mitigation: **propensity clipping** p_i <- max(p_i, tau) "
        "with tau ~ 0.01 to 0.05; this trades a small bias for a large "
        "variance reduction.",
        "Oral shortcut: 'IPS = 1/P(shown) weighting. Unbiased under overlap, "
        "but variance explodes at small propensities. Clip at tau to keep "
        "variance sane.'",
    ])

    # --- AC (2): Examination hypothesis ---
    b.add_section("2. Examination Hypothesis -- Click = Exam * Relevance", [
        "The examination hypothesis (Richardson 2007, Chapelle-Zhang 2009) says "
        "a user clicks iff they examine and the result is relevant. The classic "
        "**PBM** form assumes examination depends only on position, not on "
        "content:",
        FormulaBlock(
            latex=(
                r"\Pr(C = 1 \mid q, d, k) = \underbrace{\Pr(E = 1 \mid k)}_{\text{position bias}} "
                r"\cdot \underbrace{\Pr(R = 1 \mid q, d)}_{\text{relevance}}"
            ),
            explanation="PBM: click factorizes into examination (position-only) and relevance (query-doc-only):",
        ),
        "This is the foundational assumption that makes debiased LTR tractable. "
        "Two immediate consequences: (i) p_k = P(exam | position k) plays the "
        "role of the propensity and only depends on position; (ii) the counterfactual "
        "click rate at a different position is recoverable by multiplying "
        "relevance by the new position's examination probability.",
        "Compare to cascade (Craswell 2008): users examine top-down and stop "
        "at the first click -- examination at position k depends on earlier "
        "results, breaking position-only factorization. PBM is wrong in detail "
        "(examination interacts with snippet, freshness, SERP layout) but "
        "right enough to carry debiased LTR in practice.",
        "Oral shortcut: 'Examination hypothesis: click = P(exam at position) * "
        "P(rel | q,d). Under PBM, position is the only confound; that is the "
        "one assumption that makes per-position IPS valid.'",
    ])

    # --- AC (5): Propensity estimation ---
    b.add_section("3. Propensity Estimation -- Where Does P(shown) Come From?", [
        "The IPS estimator is only as good as the propensity. Four standard "
        "ways to estimate position-examination propensity p_k in production:",
        "**(a) Result randomization (RandPair, Joachims 2017)**: for a small "
        "slice of traffic, swap the document at position 1 with the document at "
        "position k. Because relevance is held constant across the swap, the "
        "ratio of click-through rates directly estimates the examination ratio "
        "p_k / p_1. Cheapest ground truth; costs a small amount of user experience.",
        FormulaBlock(
            latex=(
                r"\frac{p_k}{p_1} = "
                r"\frac{\mathrm{CTR}(d \text{ swapped to position } k)}{\mathrm{CTR}(d \text{ at position } 1)}"
            ),
            explanation="RandPair estimator: CTR ratio under swap identifies the relative examination:",
        ),
        "**(b) Intervention harvesting (Agarwal 2019)**: if the logging policy "
        "already varies position for the same (q,d) across impressions "
        "(re-rankings, refreshes, personalization flips), harvest these "
        "natural interventions instead of injecting new swaps. Zero UX cost, "
        "but needs a diverse enough logging policy.",
        "**(c) EM on PBM (Wang 2018, Regression-EM)**: jointly estimate "
        "relevance R(q,d) and examination p_k by alternating: E-step compute "
        "P(exam | click, q, d, k), M-step update the position table and the "
        "relevance model. Cheap, biased if PBM is wrong, and brittle to "
        "clickbait / snippet effects.",
        "**(d) Inverse propensity model (click-through rate fit)**: fit a "
        "parametric or nonparametric p_k curve from logs under the assumption "
        "that the top positions of an unbiased policy satisfy p_1 ~ 1. Simple "
        "and the default baseline when nothing better is available.",
        "Sanity-check curve: p_k typically drops to 0.3-0.5 at k=3 and below "
        "0.1 past k=10 for desktop web SERP; mobile is steeper. Always "
        "report propensity error bars and the clipping tau used -- both "
        "are first-class knobs that reviewers will press on.",
        "Oral shortcut: 'Propensity comes from randomization when you can "
        "afford it, intervention harvesting when logs are diverse, EM when "
        "you cannot randomize, and a parametric p_k fit as a last resort.'",
    ])

    # --- AC (3): SNIPS ---
    b.add_section("4. SNIPS -- Self-Normalized IPS (Bias/Variance Tradeoff)", [
        "Vanilla IPS is unbiased but high-variance. **SNIPS** (Swaminathan-Joachims "
        "2015) divides by the sum of weights instead of N, trading a small bias "
        "for a large variance reduction:",
        FormulaBlock(
            latex=(
                r"\hat{V}_{\text{SNIPS}}(\pi) = "
                r"\frac{\sum_{i=1}^{N} w_i \, c_i}{\sum_{i=1}^{N} w_i}, "
                r"\quad w_i = \frac{\mathbb{1}[d_i \in \pi(q_i)]}{p_i}"
            ),
            explanation="SNIPS estimator: the IPS ratio with normalization by the sum of importance weights:",
        ),
        "Why it helps: if a single log has an absurdly small p_i, both "
        "numerator (w_i * c_i) and denominator (w_i) blow up together, so the "
        "ratio stays stable. SNIPS is no longer unbiased (bias O(1/N)) but "
        "the MSE is almost always lower than vanilla IPS on real-world "
        "propensity distributions with heavy tails.",
        "The bias/variance tradeoff in one line:",
        FormulaBlock(
            latex=(
                r"\mathrm{MSE}(\hat{V}) = \underbrace{\bigl(\mathbb{E}[\hat{V}] - V\bigr)^2}_{\text{bias}^2} + "
                r"\underbrace{\mathrm{Var}(\hat{V})}_{\text{variance}}"
            ),
            explanation="MSE decomposition: SNIPS adds bias^2 of order 1/N but kills variance from rare small propensities:",
        ),
        "Practical ladder (increasing bias, decreasing variance):",
        "1. Vanilla IPS -- unbiased, high variance, unusable with small p_i.",
        "2. Clipped IPS -- clip p_i at tau; small bias, big variance drop.",
        "3. **SNIPS** -- self-normalize; small bias, often best on real logs.",
        "4. Doubly robust (DR) -- combine SNIPS with a reward model; "
        "variance further reduced, and unbiased if either propensity or "
        "reward model is correct.",
        "Oral shortcut: 'SNIPS divides IPS by the sum of weights; biased by "
        "1/N but variance is bounded and MSE is typically lower. It is the "
        "first thing to reach for after vanilla IPS blows up.'",
    ])

    # --- Comparison table: estimator families ---
    b.add_section("5. Estimator Ladder at a Glance", [
        "Pick by the shape of your propensity distribution and whether you can "
        "afford a reward model:",
    ])

    b.add_comparison_table(
        headers=["", "Naive CTR", "IPS", "Clipped IPS", "SNIPS", "DR"],
        rows=[
            ["Unbiased?", "No", "Yes (under overlap)", "No (tau bias)", "No (O(1/N))", "Yes if either model correct"],
            ["Variance", "Low", "Very high", "Moderate", "Low", "Lowest"],
            ["Needs propensity", "No", "Yes", "Yes", "Yes", "Yes"],
            ["Needs reward model", "No", "No", "No", "No", "Yes"],
            ["Fails when", "Always (biased by policy)", "Small p_i in tail", "Over-clip destroys signal", "Heavy skew of w_i", "Both models misspecified"],
            ["Typical LTR use", "Baseline only", "Rare", "Production", "Production", "Production + reward model"],
        ],
        title="IPS / SNIPS / DR Estimator Comparison",
    )

    # --- Debiased NDCG ---
    b.add_section("6. Debiased NDCG (PBM-IPS NDCG)", [
        "Standard NDCG assumes the labels are known everywhere. In production "
        "we only have clicks at the positions pi0 chose. Debiased NDCG replaces "
        "the per-document relevance estimate with its IPS-corrected version:",
        FormulaBlock(
            latex=(
                r"\widehat{\mathrm{DCG}}(\pi) = \sum_{k=1}^{K} "
                r"\frac{1}{\log_2(k+1)} \cdot "
                r"\frac{c_{\pi_0(k)}}{p_{k_0(d)}}"
            ),
            explanation="IPS-DCG: weight each observed click by 1 / P(examined at its logged position):",
        ),
        "Interpretation: each click 'pays for' all the positions where the "
        "document would have been examined but was not, under the re-ranked "
        "policy. Under PBM and correct p_k, this is an unbiased estimate of "
        "DCG under pi. Divide by the ideal-list DCG in the usual way to get "
        "debiased NDCG.",
        "Known failure modes:",
        "1. Misspecified position model (cascade, not PBM) -> systematic "
        "mis-weighting that neither clipping nor SNIPS fixes.",
        "2. Trust bias -- users click because they trust rank 1, not because "
        "the doc is relevant; propensity model absorbs some of this but not "
        "all.",
        "3. Presentation effects (snippet quality, thumbnails, ads above) "
        "-- violate position-only examination.",
        "4. Long-tail queries -- propensity variance dominates; report confidence "
        "intervals and do stratified analysis.",
        "Oral shortcut: 'Debiased NDCG = replace each per-position gain by "
        "click / p_k, then normalize by ideal DCG. Unbiased under PBM, and "
        "that one assumption is the thing a Google reviewer presses on.'",
    ])

    # --- AC (4): SIGIR paper contribution + limitation ---
    b.add_section("7. SIGIR Paper: Contribution + Biggest Limitation", [
        "Interviewer favorite: a one-sentence contribution and a one-sentence "
        "limitation. Both should be testable and non-defensive. Template:",
        "**Contribution (one line)**: 'We showed that [specific technique] "
        "reduces [bias source] on [benchmark / production slice] by [X%], "
        "measured by [metric] -- under [assumption A].'",
        "Example concrete form: 'We introduced a lightweight propensity "
        "estimator using intervention harvesting on existing production "
        "reranks, recovering p_k within 3% of RandPair on the top-5 "
        "positions without any new randomized traffic, which enabled "
        "unbiased NDCG eval on our full logged traffic.'",
        "**Limitation (one line)**: 'The approach assumes [assumption]; when "
        "[concrete violation], the estimator is biased by approximately [Y%], "
        "and we believe [mitigation / future work].'",
        "Example concrete form: 'Our method assumes PBM (position-only "
        "examination); on mobile infinite-scroll SERPs the cascade component "
        "dominates and our position propensity is biased by an estimated "
        "10-15% in the tail -- a cascade extension or a DR overlay would "
        "address it.'",
        "Ladder of answer quality -- press yourself upward:",
        "1. Hedge ('it worked well'). Weak -- zero information.",
        "2. Metric + delta ('improved NDCG@10 by 2 points'). OK.",
        "3. Metric + delta + regime ('improved NDCG@10 by 2 points on "
        "mid-tail queries under PBM'). Good.",
        "4. Metric + delta + regime + honest limit ('+2 NDCG on mid-tail "
        "under PBM; tail queries still have 3% CI, mobile cascade not "
        "addressed'). Senior-level.",
        "Oral shortcut: 'Contribution = specific technique + specific delta "
        "+ specific assumption. Limitation = the assumption's sharp edge + "
        "magnitude + direction of bias + planned mitigation.'",
    ])

    # --- Numerical sanity check ---
    b.add_section("8. Numerical Sanity Check (Small p_k Blowup)", [
        "Position propensities: p_1 = 1.0, p_2 = 0.5, p_10 = 0.05. A single "
        "click observed at position 10 contributes 1 / 0.05 = 20 to the IPS "
        "sum. If only 100 impressions were logged at position 10 with a "
        "single click, the IPS estimate for that position is 20 / 100 = "
        "0.20 -- but its standard error is roughly sqrt(Var) / N ~ 20 / "
        "sqrt(100) = 2.0. The point estimate is swamped by noise.",
        "Clipping at tau = 0.1 replaces 0.05 with 0.10, shrinking the single "
        "click's weight from 20 to 10. Point estimate biased low by ~2x at "
        "that position; but variance drops by 4x. SNIPS would normalize by "
        "the sum of weights across all positions, so a dominant position-1 "
        "bucket (weight 1.0) prevents the position-10 tail from dominating "
        "the final estimate.",
        "Takeaway: the propensity tail is where estimators fall over. "
        "Always plot the weight distribution (histogram of 1/p_i on the log "
        "scale) before trusting any number.",
    ])

    # --- Summary checklist ---
    b.add_checklist("2-Minute Oral Self-Check", [
        "State the goal: estimate V(pi) from logs of pi0 without A/B testing",
        "Write IPS = (1/N) sum 1[d in pi]/p * c; unbiased under overlap",
        "Examination hypothesis: P(click | q, d, k) = P(exam | k) * P(rel | q, d)",
        "Name 4 ways to estimate p_k: RandPair, intervention harvesting, EM, parametric fit",
        "SNIPS = IPS / sum(w); biased O(1/N) but lower variance on heavy tails",
        "Bias/variance ladder: naive < IPS < clipped IPS < SNIPS < DR",
        "Debiased NDCG: replace per-position gain by click / p_k then normalize",
        "SIGIR contribution: technique + delta + assumption + regime",
        "SIGIR limitation: assumption's sharp edge + magnitude + mitigation",
        "Pitfall: small p_k causes variance blowup; always report clipping tau",
    ])

    return b


def main() -> None:
    """Build and save the IPS / counterfactual eval drill note."""
    b = build_note()
    content = b.build()

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_ips_counterfactual_drill.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
