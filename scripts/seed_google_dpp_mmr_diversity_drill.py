"""Seed: Google R1 Multi-objective ranking drill (company_id=3).

Covers T-P0-420 AC:
 (1) MMR = lambda * rel - (1 - lambda) * max_sim -- greedy re-rank with a
     single tunable knob, O(k * |C|) complexity, the industry workhorse.
 (2) DPP via det(L_S): diagonal L_ii = quality, off-diagonal L_ij = similarity,
     so one determinant encodes relevance AND repulsion in one score.
 (3) Intent collapse as the real failure mode MMR/DPP attack: greedy blend
     of heterogeneous objectives starves entire intents. Platform fix =
     allocation primitive (module arbitration / slot budgets), not
     scalarization.
 (4) Diversity is ORTHOGONAL to uncertainty weighting / GradNorm / Pareto:
     MTL balances LOSS terms during training; DPP/MMR balances the SLATE at
     serving. They can and should coexist. Interviewers press on this.
 (5) Etsy GMB diversity story: 'bidding reranker maxes click-weighted GMB'
     trap (relevance collapse onto a few sellers), and the two-knob fix.
     Ref: docs/doordash_ml_domain_ranking.md section 5; docs/doordash_ml_domain_search.md
     section 6.2-6.3; docs/pinterest/system_design_pin_ranking.md.

Staging context: pillar-5 / doordash MO drill covers scalarization + MGDA +
uncertainty weighting but does NOT cover slate-level diversity. Google R1 for
ranking roles (Etsy-style GMB, Pinterest home feed, DoorDash home) always
presses on diversity as a separate axis.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3
DOC_TITLE = (
    "Multi-Objective Ranking: DPP / MMR + Etsy Diversity Playbook "
    "(Google R1 Prep)"
)


def build_note() -> StudyNoteBuilder:
    """Build the DPP/MMR diversity drill note."""
    b = StudyNoteBuilder()
    b.set_title(
        "Multi-Objective Ranking -- DPP / MMR + Etsy Diversity "
        "(Google R1 Prep)"
    )

    b.add_prerequisites([
        "Scalarized multi-task ranking loss: L = sum_k w_k L_k",
        "Uncertainty weighting (Kendall 2018) and GradNorm (Chen 2018) at the equation level",
        "Pareto optimization / MGDA / PCGrad at a conceptual level",
        "Cosine similarity and dot-product scoring in embedding space",
        "Two-tower retrieval + cross-encoder reranker pipeline",
    ])

    b.add_term(
        "MMR",
        "Maximal Marginal Relevance",
        "Greedy slate selection: at each slot pick the item that maximizes lambda * relevance minus (1 - lambda) * max similarity to already-picked items",
    )
    b.add_term(
        "DPP",
        "Determinantal Point Process",
        "Probabilistic model over subsets: P(S) proportional to det(L_S); diagonal encodes quality, off-diagonal encodes similarity, so the determinant jointly scores relevance AND diversity",
    )
    b.add_term(
        "MTL",
        "Multi-Task Learning",
        "Training a shared-parameter model against multiple loss heads (click, purchase, dwell); distinct from slate-level diversity, which is a SERVING-time decoupled concern",
    )
    b.add_term(
        "Intent Collapse",
        "Intent Collapse Failure Mode",
        "A scalarized ranker pushes a single dominant intent (e.g. GMB-maxing sellers) into every slot; users with minority intents see no relevant items even though the average NDCG looks healthy",
    )
    b.add_term(
        "Allocation Primitive",
        "Slot-Budget Allocation Primitive",
        "Platform-level mechanism that reserves a fixed share of slate slots per module / intent / business rule, so module arbitration replaces scalar-weight horse-trading",
    )
    b.add_term(
        "GMB",
        "Gross Merchandise Bookings",
        "Etsy's commerce north-star metric; bidding-reranker optimization against GMB is the classic intent-collapse trap because high-GMB sellers dominate the slate",
    )
    b.add_term(
        "MGDA",
        "Multiple Gradient Descent Algorithm",
        "Pareto-optimization method that finds a gradient direction non-increasing for all task losses; orthogonal to slate diversity -- MGDA balances TRAINING, DPP/MMR balances SERVING",
    )

    # --- Section 0: Framing ---
    b.add_section("0. Framing -- Where Diversity Fits in the MO Stack", [
        "Staging-5 and the DoorDash MO drill cover scalarization "
        "(L = sum w_k L_k), **Uncertainty Weighting**, **GradNorm**, and "
        "**MGDA**. Those are all TRAINING-TIME tools: they set how multiple "
        "loss terms share gradient updates. Google R1 for ranking roles "
        "(Etsy/Pinterest/DoorDash/YouTube home) presses on a second axis "
        "that those tools do not touch: **the composition of the final "
        "slate**. Even with perfectly balanced training losses, a greedy "
        "top-K sort can return a slate that is 9 near-duplicate sellers "
        "plus 1 outlier.",
        "This drill covers the four questions that always land in that "
        "conversation: (1) the **MMR** closed form and why it is the "
        "industry default, (2) the **DPP** determinant and why it matters "
        "theoretically even though MMR ships, (3) the **Intent Collapse** "
        "failure mode and why the fix is a slot-level **Allocation "
        "Primitive** rather than yet-another scalar weight, and (4) why "
        "DPP/MMR are orthogonal to MTL loss-balancing -- both MUST coexist "
        "in a production stack.",
        "Oral shortcut: 'MTL balances the LOSS; diversity balances the "
        "SLATE. They run at different layers -- training vs reranker "
        "serving -- so they compose. MMR is the scalar-knob industry "
        "default; DPP is the cleaner math; intent collapse is the failure "
        "scalarization cannot solve, which is why platforms ship slot "
        "budgets.'",
    ])

    # --- AC (1): MMR ---
    b.add_section("1. MMR -- The Industry Workhorse (One Knob, Greedy, O(k|C|))", [
        "**MMR** is a **greedy re-ranker**. Given a candidate set C of size "
        "N (usually the top-200 from L2 heavy rank) and a target slate "
        "size k (usually 20), iteratively pick the item that maximizes:",
        FormulaBlock(
            latex=(
                r"\mathrm{MMR}(d_i) = \lambda \cdot \mathrm{rel}(d_i, q) "
                r"- (1 - \lambda) \cdot \max_{d_j \in S} "
                r"\mathrm{sim}(d_i, d_j)"
            ),
            explanation="MMR score for candidate d_i given already-selected set S; lambda is the single tunable knob (relevance vs repulsion):",
        ),
        "Where rel(d, q) is the L2 ranker score (or any scalarized utility) "
        "and sim(d_i, d_j) is cosine similarity in an embedding space "
        "(PinSage, item2vec, topic one-hot overlap -- choice of space is a "
        "system design decision). Terms:",
        "- **lambda = 1**: pure relevance, no diversity -- equivalent to "
        "`argsort(rel)[:k]`. Produces duplicate-heavy slates.",
        "- **lambda = 0**: pure repulsion -- picks items maximally "
        "different from already-picked, totally ignoring query. Produces "
        "random-looking slates.",
        "- **lambda ~ 0.7**: industry default in feed-ranking papers and "
        "DoorDash / Pinterest re-rankers. Tuned per surface via A/B.",
        "**Complexity**: at slot t of k, pick over |C| - t candidates, "
        "each paired against t already-selected items. Total O(k * |C|) "
        "similarity lookups -- if sim is a precomputed cache or "
        "low-dimensional dot product, this is microseconds. That is why "
        "MMR fits in a 15ms re-rank budget while **DPP** inference does "
        "not.",
        "**Why MMR ships and DPP usually does not**:",
        "- Latency: O(k * |C|) vs DPP's O(k * |C|^2) or greedy-MAP's "
        "O(k^2 * |C|).",
        "- Explainability: `lambda` is one number; PMs tune it; A/B tests "
        "are one-dimensional.",
        "- Determinism: greedy MMR is trivially deterministic given the "
        "candidate order; DPP's stochastic sampling is harder to debug "
        "and replay.",
        "- Feature-plug-in: MMR's `sim` takes any similarity function --- "
        "topic Jaccard, cosine, even a learned pairwise penalty head. "
        "DPP's kernel **L** has to be PSD, which rules out several "
        "natural choices.",
        "**Practical pitfalls interviewers probe**:",
        "- **Scale mismatch**: rel(d, q) from a BCE logit vs sim in [0, 1]. "
        "If rel is unbounded and sim is bounded, the effective lambda "
        "collapses to 1. Fix: min-max normalize rel per request, or "
        "map rel through a sigmoid.",
        "- **Similarity space choice leaks the failure mode**: if sim is "
        "title-text cosine, the ranker diversifies titles but not "
        "sellers; GMB-heavy accounts still dominate. Use a "
        "COMPOSITE similarity: max(title_cos, seller_id_one_hot, "
        "category_match).",
        "- **Business-rule ordering**: MMR is usually followed by "
        "ads-insertion, policy-dedup, and freshness boost. The ordering "
        "matters -- if ads go in after MMR, they consume diversity slots "
        "you already earned. Canonical order: `rank -> MMR -> rules`.",
        "Oral shortcut: 'Greedy O(k|C|) with one lambda knob, sim must "
        "be cheap and expressive. Tune lambda ~ 0.7 on offline NDCG vs "
        "slate entropy, A/B the pair. Industry ships MMR over DPP "
        "because of latency and PM tunability.'",
    ])

    # --- AC (2): DPP ---
    b.add_section("2. DPP -- One Determinant Encodes Relevance AND Repulsion", [
        "**DPP** places a probability on every subset S of the candidate "
        "set, with probability proportional to a matrix determinant:",
        FormulaBlock(
            latex=(
                r"P(S) \propto \det(L_S), "
                r"\quad L_{ii} = q_i^2, "
                r"\quad L_{ij} = q_i \cdot \phi_i^\top \phi_j \cdot q_j"
            ),
            explanation="L is the N x N DPP kernel: diagonal is per-item quality (squared), off-diagonal is quality-weighted embedding similarity. One determinant encodes both:",
        ),
        "The trick is that det(L_S) = prod of eigenvalues of L_S, and "
        "near-duplicate items drive one eigenvalue toward zero, "
        "driving the determinant toward zero. Concretely:",
        "- Diagonal L_ii is **relevance**: high-quality item -> large "
        "diagonal entry -> larger determinant.",
        "- Off-diagonal L_ij is **similarity**: two similar items -> "
        "large off-diagonal -> the matrix becomes near-singular -> "
        "smaller determinant.",
        "- So MAP inference argmax_S det(L_S) subject to |S| = k jointly "
        "picks high-quality AND diverse items -- with NO lambda knob. "
        "That is the advertised win over MMR.",
        "**MAP inference is NP-hard**; the standard approximation is "
        "**greedy MAP** (Chen et al. 2018, Gong et al. 2014):",
        FormulaBlock(
            latex=(
                r"d^* = \arg\max_{d_i \in C \setminus S} "
                r"\log \det(L_{S \cup \{d_i\}}) - \log \det(L_S)"
            ),
            explanation="Greedy MAP: at each step pick the candidate whose addition increases log det by the most. Runs in O(k^2 |C|) with the Cholesky-update trick:",
        ),
        "Because det is submodular in S (a standard result for PSD "
        "kernels), greedy MAP achieves a (1 - 1/e) approximation of the "
        "true optimum -- the same guarantee as greedy submodular max.",
        "**Why DPP is a more honest model than MMR**:",
        "- MMR's `max sim` penalty only considers the closest already-"
        "picked item; DPP considers the whole subset jointly through "
        "the determinant. At k=20, the 5th item onward benefits from "
        "the full-spectrum view.",
        "- DPP naturally spreads across clusters: if the candidate set "
        "has 3 intents with near-equal quality, DPP tends to spread the "
        "slate across all 3, whereas MMR can pile into the highest-"
        "relevance intent until lambda is tuned very aggressively.",
        "- Quality and diversity are **not** two separate objectives "
        "with a mixing weight -- they are two ways the same matrix is "
        "parametrized. That is the 'mathematically cleaner' claim.",
        "**Why DPP rarely ships in practice (the interviewer will ask)**:",
        "- **Kernel design is load-bearing**: you must choose phi and "
        "the quality q_i. Production teams have many noisy quality "
        "heads (CTR, CVR, dwell) and multiple natural similarity spaces; "
        "there is no obvious single kernel.",
        "- **Latency**: even greedy MAP's O(k^2 |C|) + Cholesky "
        "factorization is 5-20x MMR at production k = 20, |C| = 200. "
        "Most feed surfaces cannot afford it in a 15ms rerank budget.",
        "- **Interpretability / A/B test dimensionality**: tuning DPP "
        "means re-learning the kernel rather than moving a single knob. "
        "PMs hate that.",
        "- **Stochastic inference**: if you use sampling (k-DPP) for "
        "exploration, two calls with the same input can return "
        "different slates -- hard to audit.",
        "- **Where DPP does ship**: email digests (latency budget in "
        "seconds, re-tuning is rare), YouTube related-videos research "
        "prototypes, academic benchmarks. Airbnb's 2021 'diversity via "
        "DPP' paper is the canonical industry reference but the "
        "deployment was offline re-ranking, not online serving.",
        "Oral shortcut: 'det(L_S) -- diagonal = quality squared, "
        "off-diagonal = quality-weighted similarity. One matrix, two "
        "meanings. Greedy MAP is O(k^2 |C|) with (1-1/e) guarantee. "
        "Production still ships MMR because kernel design and latency "
        "are worse than a one-knob greedy.'",
    ])

    # --- AC (3): Intent collapse ---
    b.add_section(
        "3. Intent Collapse -- Why Platforms Replace Scalarization with Allocation",
        [
            "Neither **MMR** nor **DPP** solves the **Intent Collapse** "
            "problem when it bites hard. Intent collapse is the failure "
            "mode where a scalarized utility score systematically "
            "starves a whole class of user intents, and it is the "
            "diversity question Google R1 really cares about.",
            "**The failure in concrete terms** (Etsy GMB-optimized "
            "reranker, 2019-2021 era): the production ranker is trained "
            "to predict click-weighted GMB. It learns that 'expensive "
            "high-quality-photo sellers with many reviews' maximize "
            "expected GMB per impression. The top-200 candidate set, "
            "fed to MMR, is already saturated with those sellers; MMR's "
            "sim penalty diversifies IMAGES (different product photos) "
            "but the underlying seller concentration is preserved. "
            "Users who came with a **minority intent** ('budget gift "
            "under 20 USD', 'vintage-specific', 'independent artist') see "
            "no relevant items. Their CTR silently tanks. Aggregate "
            "NDCG looks fine because the MAJORITY intent is still well "
            "served, but long-tail retention degrades over months.",
            "**Why scalar weights cannot fix this**: the issue is not "
            "that one of the K loss weights is mis-tuned. Any "
            "combination w_click L_click + w_GMB L_GMB + w_relevance "
            "L_relevance trains a single utility function. Minority "
            "intents have small support in training data, so they "
            "contribute less to any loss term. Cranking w_relevance "
            "up does not help because the very notion of 'relevance' "
            "is majority-aligned -- the model has no channel for "
            "'this user's intent is unusual'. Even **Uncertainty "
            "Weighting** and **GradNorm** do not fix it; they balance "
            "tasks but still produce a single scalar per (q, d).",
            "**The production fix = Allocation Primitive**. Instead of "
            "one scalarized ranker, the platform breaks the slate into "
            "**module slots** where each module is responsible for a "
            "different intent or business goal, and a SLOT BUDGET "
            "determines how many slots each module owns. Module "
            "arbitration decides per-slot winners with simple rules "
            "(e.g., 'ads own slots 3 and 7; new-seller-boost owns 1 "
            "slot; budget-intent module owns up to 2 slots if the "
            "user's query signals budget intent; the rest of the slate "
            "goes to the base ranker').",
            FormulaBlock(
                latex=(
                    r"\text{slate} = \bigcup_{m \in \mathcal{M}} "
                    r"\mathrm{topK}_m\bigl(c_m \cdot \mathrm{budget}(m, q)\bigr)"
                ),
                explanation="Allocation primitive: the slate is a union of per-module top-K, each module produces up to budget(m, q) slots for query q, merged via a fixed arbitration policy:",
            ),
            "**Why this is structurally better than scalarization**:",
            "- **Minority intents get guaranteed real estate**: the "
            "budget is not competing against majority signal in a loss "
            "function, it is reserved upfront.",
            "- **Module accountability**: each module has its own loss, "
            "its own team, its own A/B test. A regression in one "
            "module does not contaminate the entire slate.",
            "- **Business rules become first-class**: ads insertion, "
            "cold-start boost, policy slots are the same primitive as "
            "ML modules, not bolted on.",
            "- **It composes with DPP/MMR, not replaces them**: inside "
            "a module with multiple items, MMR still diversifies the "
            "items that module fills.",
            "**Platform examples**:",
            "- Facebook News Feed's 'mixer' layer arbitrates among "
            "posts, stories, ads, groups.",
            "- YouTube home page slot budgets for short-form, "
            "long-form, Live, subscriptions.",
            "- Pinterest home feed's 'candidate sources' pattern: "
            "Board-Follow, Interest, Topic, Search-interest are "
            "separate modules, each with quota.",
            "- DoorDash home: 'for you', 'new on DoorDash', 'value', "
            "'cuisines' carousels are module slots -- the scalar "
            "ranker operates INSIDE each carousel, not across them.",
            "- Etsy post-2022 diversity overhaul: explicit seller-"
            "diversity budget, minority-intent pipes, MMR only "
            "operates within-module.",
            "Oral shortcut: 'Scalarization cannot solve minority-intent "
            "starvation -- the signal is too small to matter in the "
            "loss. The platform fix is an ALLOCATION PRIMITIVE: module "
            "slot budgets with arbitration, and MMR/DPP run INSIDE "
            "each module. This is what senior-level ranking interviews "
            "want you to name.'",
        ],
    )

    # --- AC (4): Orthogonality ---
    b.add_section(
        "4. Orthogonality with Uncertainty Weighting / GradNorm / Pareto",
        [
            "A load-bearing Google R1 gotcha: candidates conflate "
            "training-time MTL balancing with serving-time slate "
            "diversity. They are ORTHOGONAL axes; production stacks "
            "apply BOTH.",
        ],
    )

    b.add_comparison_table(
        headers=["Axis", "Training-time MTL balancing", "Serving-time slate diversity"],
        rows=[
            [
                "Tools",
                "Scalarization, Uncertainty Weighting, GradNorm, MGDA, PCGrad",
                "MMR, DPP, allocation primitive, slot budgets",
            ],
            [
                "What it balances",
                "Gradient contributions of different LOSS heads (click, purchase, dwell)",
                "Composition of the final SLATE presented to the user (item diversity, intent coverage)",
            ],
            [
                "Layer",
                "Shared-parameter tower during training",
                "Post-ranker reranker in the serving path",
            ],
            [
                "Per-request cost",
                "Zero at serving time (weights are baked into the model)",
                "Dominant rerank latency (~1-15ms at k=20, |C|=200)",
            ],
            [
                "Failure mode it fixes",
                "Loss-scale imbalance, gradient dominance by one task",
                "Duplicate-heavy slates, intent collapse, position-biased near-identicals",
            ],
            [
                "Failure mode it does NOT fix",
                "Slate-level duplication, minority-intent coverage",
                "Training-time gradient conflict among heads",
            ],
            [
                "A/B test surface",
                "Offline NDCG / ROC-AUC, rarely visible online as diversity",
                "Slate entropy, intent coverage@k, long-tail retention",
            ],
        ],
        title="Training-time MTL vs Serving-time Slate Diversity (Orthogonal Axes)",
    )

    b.add_section("4.1 Canonical Production Composition", [
        "The full stack looks like this:",
        "1. **Training**: Shared MMoE tower with K heads (click, purchase, "
        "dwell, hide). Losses balanced by **Uncertainty Weighting** at "
        "initialization and **GradNorm** during training. Offline "
        "Pareto sweep to pick the shipping scalar weights.",
        "2. **Inference**: Single forward pass emits K scores per (q, d). "
        "A fixed linear combination utility = sum_k w_k * score_k "
        "produces a scalar relevance.",
        "3. **Retrieval -> L1 -> L2 heavy rank**: produces top-200 "
        "by `utility`.",
        "4. **Slate diversity**: Allocation primitive splits 20 slots "
        "among modules; WITHIN each module, MMR re-ranks using the "
        "utility score + a composite similarity (title, seller, "
        "category).",
        "5. **Business rules**: Ads insertion, policy filter, freshness "
        "boost applied LAST so they do not consume diversity slots.",
        "Every stage has its own A/B surface. A regression in any "
        "single stage should be catchable from that stage's metrics.",
        "**Interview trap the interviewer will set**: 'you can just add "
        "a diversity loss term to the MTL training, right? Then you "
        "don't need MMR at serving.' Answer: NO -- a diversity term in "
        "the per-item loss has no access to the slate context. "
        "Slate-level metrics (pairwise cosine sum across the slate, "
        "intent coverage) are non-decomposable. You CAN train a "
        "reranker end-to-end on slate-level rewards (listwise RL, "
        "e.g. SlateQ), but you cannot replace the slate-level mechanism "
        "with a pointwise loss.",
        "Oral shortcut: 'MTL balances LOSS GRADIENTS during training. "
        "DPP/MMR/allocation balances SLATE COMPOSITION at serving. "
        "Different layer, different metric, different owner. A "
        "production stack ships all three: Uncertainty Weighting + "
        "GradNorm at training, plus allocation + MMR at serving.'",
    ])

    # --- Section 5: Etsy story ---
    b.add_section("5. Etsy GMB Diversity War Story -- The Two-Knob Fix", [
        "Google R1 asks: 'give me a concrete diversity trap you have "
        "seen or studied.' Canonical answer: **Etsy GMB-bidding "
        "reranker, 2019-2021**.",
        "**Setup**: Etsy's production reranker predicted "
        "click-weighted **GMB** contribution for each listing. The "
        "model was well calibrated (temperature-scaled), MTL-balanced "
        "via Uncertainty Weighting, and A/B tested via GMV-per-"
        "session. MMR diversified titles with lambda ~ 0.6.",
        "**The symptom**: aggregate GMV-per-session held or rose in "
        "every A/B, but quarterly seller retention at the tail "
        "degraded, and long-tail return-user CTR dropped. Post-hoc "
        "analysis showed: the top-1% sellers captured 40%+ of "
        "impressions on reranked slates; minority intents "
        "('under 15 USD gift', 'vintage', 'personalized') were served "
        "generic top-tier sellers instead of intent-matched "
        "minority-seller listings.",
        "**Why MMR failed to catch it**: the title-cosine similarity "
        "space had high intra-slate entropy (different products) but "
        "low seller entropy (same handful of stores). MMR was "
        "diversifying the surface signal, not the latent concentration.",
        "**The fix (two knobs)**:",
        "1. **Composite similarity**: sim(d_i, d_j) = "
        "max(title_cos, 1 if seller_id_i == seller_id_j else 0, "
        "1 if category_i == category_j else 0). This immediately "
        "suppressed same-seller clumping inside MMR.",
        "2. **Allocation primitive**: reserve 2-4 slots out of 20 for "
        "'minority-intent' and 'long-tail-seller' modules with their "
        "OWN ranker, not competing with GMB. Module budgets tuned per "
        "query-intent class (budget / vintage / personalized).",
        "**Result**: aggregate GMV was flat in A/B (the two modules "
        "displaced some high-GMB but not high-margin listings), but "
        "seller-diversity metrics (Gini, top-1% share) dropped "
        "materially, and 90-day return-user CTR for minority intents "
        "rose 5-8%. This is the shape of fixes Google R1 wants to "
        "hear about: not 'we tuned lambda', but 'we changed the "
        "SIMILARITY space AND added a slot budget'.",
        "**Variant traps on other platforms**:",
        "- **Pinterest creator-concentration**: same pattern with "
        "creators instead of sellers; fix is MMR-penalty on "
        "creator_id plus creator-freshness slots.",
        "- **DoorDash merchant-concentration on 'For You' carousel**: "
        "top-20 merchants dominate; fix is per-merchant cap (max 2 "
        "slots per merchant per slate).",
        "- **YouTube uploader-concentration on home**: enforced slot "
        "budget per channel plus diversity loss in ranker (one of "
        "the few places a diversity LOSS term helps -- because the "
        "slate size is large and slate-level A/B is well-established).",
        "Oral shortcut: 'Etsy 2020: GMB-reranker -> seller collapse. "
        "MMR diversified titles not sellers because the similarity "
        "space was wrong. Fix was composite similarity (title OR "
        "seller OR category) PLUS an allocation primitive reserving "
        "slots for minority intents. That is the senior-diff: know "
        "which knob was wrong and why scalarization could not have "
        "caught it.'",
    ])

    # --- Section 6: Numerical sanity check ---
    b.add_section("6. Numerical Sanity Check -- Scales Interviewers Expect", [
        "Concrete numbers for system-design oral exams:",
        "- **Candidate set size** |C| out of L2 heavy rank: 100-500 "
        "is typical; 200 is the usual default.",
        "- **Slate size** k: home feed 20-25, email digest 10, "
        "search results 10-50.",
        "- **MMR latency budget**: ~1-2ms at k=20, |C|=200 if sim "
        "is a cached cosine. DPP greedy-MAP: 10-20ms at same scale. "
        "That 5-10x multiplier is why MMR ships.",
        "- **Lambda tuning range**: 0.5 to 0.8 covers 95% of "
        "production deployments. Start at 0.7, A/B +/- 0.1.",
        "- **Allocation budgets**: typical home feed reserves 15-25% "
        "of slots for non-base-ranker modules (ads 10-15%, cold start "
        "2-5%, minority intent 5-10%). The base ranker keeps 75-85%.",
        "- **Slate entropy target**: operational metric is Shannon "
        "entropy of category distribution across the slate. Home feed "
        "targets >= 2.5 nats at k=20 (equivalent to ~12 roughly "
        "equally represented categories).",
        "- **Gini for seller concentration**: pre-fix Etsy Gini ~0.85 "
        "on top-100 impressions; post-fix target <= 0.6. Gini 0.9+ "
        "is the usual alert threshold.",
        "- **DPP kernel dimension**: phi dim 32-64 is typical; "
        "anything above 128 blows latency because Cholesky is "
        "O(k^2 d).",
    ])

    # --- Section 7: Self-check ---
    b.add_checklist("2-Minute Oral Self-Check", [
        "MMR closed form: lambda * rel - (1 - lambda) * max sim, greedy O(k|C|)",
        "lambda knob: 0 = pure repulsion, 1 = pure relevance, default ~0.7",
        "DPP: P(S) proportional to det(L_S); diagonal = quality^2, off-diagonal = similarity",
        "Greedy MAP is O(k^2 |C|), submodular, (1 - 1/e) approximation",
        "MMR ships over DPP due to latency, PM tunability, similarity-flexibility",
        "Intent collapse: scalarization starves minority intents regardless of weight tuning",
        "Fix = allocation primitive (slot budgets + module arbitration)",
        "MTL balances LOSS at training; DPP/MMR balances SLATE at serving -- orthogonal",
        "Production stack uses BOTH (Uncertainty + GradNorm + allocation + MMR)",
        "Etsy 2020 GMB story: composite similarity + slot budget, not just lambda tune",
        "A slate-level diversity loss term in the pointwise ranker does NOT replace MMR",
    ])

    return b


def main() -> None:
    """Build and save the DPP/MMR diversity drill note."""
    b = build_note()
    content = b.build()

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_dpp_mmr_diversity_drill.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
