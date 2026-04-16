"""Seed: Google R1 Feature Drift Monitoring drill note (company_id=3).

Covers T-P1-422 AC:
 (1) PSI = sum (a - e) * ln(a / e), 0.1 warn / 0.25 critical,
 (2) KL asymmetric / unbounded vs JS symmetric / bounded,
 (3) KS for continuous features (no binning),
 (4) Concept drift P(y|x) vs covariate shift P(x) vs label shift P(y),
 (5) Per-feature + per-segment alerting, not aggregate-only.

Each section is a 30-60 second oral answer for Google R1 prep.
Mirrors the format of seed_google_ab_test_rigor_drill.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 3  # Google
DOC_TITLE = (
    "Feature Drift Drill: PSI / KL / JS / KS + Concept vs Covariate Shift "
    "(Google R1 Prep)"
)


def build_note() -> StudyNoteBuilder:
    """Build the feature drift monitoring drill study note."""
    b = StudyNoteBuilder()
    b.set_title(
        "Feature Drift Drill -- PSI / KL / JS / KS + Concept vs Covariate Shift"
    )

    b.add_prerequisites([
        "Probability distributions, expectation, and log-likelihood",
        "Empirical CDF and order statistics",
        "Hypothesis testing: null distribution, p-value, critical value",
        "Train-serve skew and the role of feature pipelines in production ML",
    ])

    b.add_term("PSI", "Population Stability Index",
               "Binned distribution-shift score; 0.1 warn, 0.25 critical, widely used in credit / ads")
    b.add_term("KL", "Kullback-Leibler divergence",
               "Asymmetric, unbounded information gain of q relative to reference p")
    b.add_term("JS", "Jensen-Shannon divergence",
               "Symmetric, bounded smoothing of KL around the midpoint distribution m = (p+q)/2")
    b.add_term("KS", "Kolmogorov-Smirnov test",
               "Max vertical gap between empirical CDFs; continuous, non-parametric, no binning required")
    b.add_term("ICC", "Intra-Cluster Correlation",
               "Fraction of total variance attributable to clusters; inflates SE when ignored")

    # --- Section 0: Framing ---
    b.add_section("0. Why Drift Monitoring Matters (The Framing)", [
        "Production ML degrades silently. A model trained on Q1 data and "
        "served through Q4 will lose AUC as user behavior, upstream feature "
        "pipelines, and labeling conventions all move. Drift monitoring is "
        "the early-warning layer that flags degradation BEFORE the business "
        "metric takes a hit.",
        "Three distinct shifts, each with a different fix:",
        "- Covariate shift: P(x) changes, P(y|x) stable -> re-weight training "
        "or re-sample, no relabeling needed",
        "- Concept drift: P(y|x) changes, P(x) may or may not change -> must "
        "retrain with fresh labels; re-weighting will NOT help",
        "- Label / prior shift: P(y) changes, P(x|y) stable -> recalibrate "
        "the output probabilities (Saerens / BBSE)",
        "Mental order of checks: (1) compute PSI per feature daily, "
        "(2) alert at 0.1 / 0.25 thresholds, (3) for continuous features use "
        "KS, (4) for multi-dimensional distributions use KL or JS, "
        "(5) attribute drift type (covariate vs concept vs label) before "
        "deciding to retrain.",
        "Oral shortcut: 'PSI is the daily workhorse. KL / JS compare "
        "distributions when you need information-theoretic framing. KS "
        "handles continuous without binning. Covariate shift = inputs moved, "
        "concept drift = input-output relationship moved. Always alert per "
        "feature and per segment, never just aggregate.'",
    ])

    # --- AC (1): PSI ---
    b.add_section("1. PSI -- The Binned Drift Workhorse", [
        "PSI compares two distributions over the SAME bin edges: the "
        "reference (training) distribution `e` and the current (serving) "
        "distribution `a`, expressed as proportions summing to 1.",
        FormulaBlock(
            latex=(
                r"\mathrm{PSI} = \sum_{i=1}^{K} (a_i - e_i) \cdot "
                r"\ln\!\left(\frac{a_i}{e_i}\right)"
            ),
            explanation=(
                "Binned distribution-shift score over K bins, reference e_i and actual a_i:"
            ),
        ),
        "Each bin contributes `(a_i - e_i) * ln(a_i / e_i)`. The sign of "
        "the contribution is ALWAYS non-negative because `(a - e)` and "
        "`ln(a / e)` have the same sign (both positive when a > e, both "
        "negative when a < e). PSI is therefore a distance-like quantity, "
        "though not a proper metric.",
        "Industry-standard thresholds (originating from credit-scoring, "
        "widely adopted in ads / search ranking):",
        "- PSI < 0.1 -- no significant shift, continue monitoring",
        "- 0.1 <= PSI < 0.25 -- moderate shift, investigate and consider retraining",
        "- PSI >= 0.25 -- significant shift, model likely degraded, retrain",
        "Bin-count sensitivity: use equal-frequency bins computed on the "
        "reference period (typically 10 bins). Fixing bin edges on the "
        "reference is critical -- if you re-bin every day using current "
        "data, you lose the anchor and the score drifts trivially. Also "
        "clip empty bins to a small epsilon (e.g., 1e-4) to avoid "
        "ln(0) blowups.",
        "Numerical anchor: suppose reference `e = [0.2, 0.3, 0.3, 0.2]` "
        "and actual `a = [0.1, 0.2, 0.4, 0.3]`. "
        "Contribution_1 = (0.1 - 0.2) * ln(0.1 / 0.2) = -0.1 * (-0.693) = 0.0693. "
        "Contribution_2 = (0.2 - 0.3) * ln(0.2 / 0.3) = -0.1 * (-0.405) = 0.0405. "
        "Contribution_3 = (0.4 - 0.3) * ln(0.4 / 0.3) = 0.1 * 0.288 = 0.0288. "
        "Contribution_4 = (0.3 - 0.2) * ln(0.3 / 0.2) = 0.1 * 0.405 = 0.0405. "
        "PSI = 0.0693 + 0.0405 + 0.0288 + 0.0405 = 0.179 -- in the WARN band.",
        "Oral shortcut: 'PSI = sum (a - e) ln(a / e). 0.1 warn, 0.25 critical. "
        "Equal-frequency bins fixed on reference, epsilon-clip zeros, alert "
        "per feature. Symmetric in a / e swap because both factors flip sign.'",
    ])

    # --- AC (2): KL vs JS ---
    b.add_section("2. KL vs JS -- Information-Theoretic Distribution Distance", [
        "KL divergence measures the expected extra bits to encode samples "
        "from p using a code optimized for q. It is the information-theory "
        "cousin of PSI (PSI ~ symmetrized KL on binned distributions):",
        FormulaBlock(
            latex=(
                r"D_{\mathrm{KL}}(p \,\|\, q) = \sum_{x} p(x) \cdot "
                r"\ln\!\left(\frac{p(x)}{q(x)}\right)"
            ),
            explanation="KL divergence of q from p (expectation under p):",
        ),
        "Critical properties of KL:",
        "- **Asymmetric**: D_KL(p || q) != D_KL(q || p) in general. The "
        "direction matters -- `p || q` is 'how wasteful is q as a code for "
        "p?'",
        "- **Unbounded**: if q(x) = 0 for some x with p(x) > 0, KL blows up "
        "to infinity. Any zero in the denominator makes KL undefined. "
        "Practical workaround: add-epsilon smoothing, but this hides the "
        "exact pathology.",
        "- **Non-metric**: fails the triangle inequality.",
        "JS divergence symmetrizes KL around the midpoint m = (p + q) / 2:",
        FormulaBlock(
            latex=(
                r"D_{\mathrm{JS}}(p, q) = \tfrac{1}{2} D_{\mathrm{KL}}(p \,\|\, m) + "
                r"\tfrac{1}{2} D_{\mathrm{KL}}(q \,\|\, m), \quad m = \tfrac{1}{2}(p + q)"
            ),
            explanation="JS divergence: average KL from each distribution to the midpoint:",
        ),
        "Critical properties of JS:",
        "- **Symmetric**: D_JS(p, q) = D_JS(q, p) by construction",
        "- **Bounded**: 0 <= D_JS <= ln(2) in nats (or 1 in bits). "
        "Boundedness is what makes JS safe for alerting thresholds; KL "
        "requires log-scale axes to visualize.",
        "- **Square-root is a metric**: sqrt(D_JS) satisfies triangle "
        "inequality (Endres-Schindelin 2003), which matters for clustering "
        "drift fingerprints.",
        "When to use which in production:",
        "- Use **PSI** for binned single-feature daily dashboards (history "
        "of thresholds, easy triage)",
        "- Use **KL** when you have a natural reference / target ordering "
        "(e.g., model predictions vs true label distribution)",
        "- Use **JS** when you need a symmetric bounded score for alerting "
        "at multiple time windows, especially for text / embedding "
        "distributions",
        "Oral shortcut: 'KL is asymmetric, unbounded, blows up on zero "
        "support. JS is symmetric, bounded by ln 2, sqrt(JS) is a metric. "
        "PSI is a binned cousin of symmetrized KL with fixed thresholds. "
        "Pick by whether you need ordering (KL), a metric (JS), or "
        "standardized thresholds (PSI).'",
    ])

    # --- AC (3): KS for continuous features ---
    b.add_section("3. KS Test -- Continuous Features Without Binning", [
        "Binning a continuous feature throws away information and makes the "
        "PSI score sensitive to the bin grid. The Kolmogorov-Smirnov test "
        "avoids binning entirely by comparing empirical CDFs:",
        FormulaBlock(
            latex=(
                r"D_{\mathrm{KS}} = \sup_{x} \bigl|F_1(x) - F_2(x)\bigr|"
            ),
            explanation=(
                "KS statistic: maximum vertical gap between empirical CDFs of two samples:"
            ),
        ),
        "Under the null hypothesis (same distribution), the scaled statistic "
        "has a known distribution (Kolmogorov distribution). For two samples "
        "of sizes n1 and n2, reject H0 at level alpha when:",
        FormulaBlock(
            latex=(
                r"D_{\mathrm{KS}} > c(\alpha) \cdot \sqrt{\frac{n_1 + n_2}{n_1 \cdot n_2}}, "
                r"\quad c(0.05) \approx 1.36"
            ),
            explanation=(
                "Two-sample KS critical value at alpha = 0.05 with the classic 1.36 constant:"
            ),
        ),
        "Properties:",
        "- **Non-parametric**: no distributional assumption beyond "
        "continuity",
        "- **No binning**: uses order statistics directly",
        "- **Most sensitive near the median**: CDF gap is maximized where "
        "density is highest. A tail-only shift of rare events is under-"
        "powered. For tail drift, use Anderson-Darling or split by quantile "
        "and run KS per segment.",
        "Practical pitfalls:",
        "- At Internet scale (n >> 1e6) KS is hyper-sensitive -- even "
        "cosmetically small shifts trigger rejection. Either use effect-"
        "size thresholds (D > 0.05) instead of p-values, or downsample to a "
        "fixed reference size.",
        "- KS is a univariate test. For multivariate drift use per-feature "
        "KS plus a MMD (Maximum Mean Discrepancy) or a domain classifier "
        "(train a binary classifier to distinguish reference vs current; "
        "AUC > 0.6 is a drift signal).",
        "Oral shortcut: 'KS = sup gap between two empirical CDFs. No binning, "
        "non-parametric, single number per feature. Critical value about "
        "1.36 * sqrt((n1+n2)/(n1 n2)) at alpha 0.05. Tail-weak; switch to "
        "AD or quantile-split if the tail matters.'",
    ])

    # --- AC (4): Concept drift vs covariate shift vs label shift ---
    b.add_section("4. Concept Drift vs Covariate Shift vs Label Shift", [
        "Drift type determines the fix. Getting the type wrong wastes weeks: "
        "retraining on stale labels when the problem is concept drift, or "
        "recalibrating when the problem is actually covariate shift.",
        "Factorize the joint distribution two ways:",
        FormulaBlock(
            latex=(
                r"P(x, y) = P(y \mid x) \cdot P(x) = P(x \mid y) \cdot P(y)"
            ),
            explanation="Two factorizations of the joint, each isolates a shift type:",
        ),
        "- **Covariate shift**: P(x) changes, P(y|x) is stable. Classic "
        "example: user demographics shift after a new market launch but the "
        "same input-to-label relation still holds. Fix: importance "
        "re-weighting w(x) = P_target(x) / P_source(x), or re-sample training "
        "data to match the new P(x). No new labels needed.",
        "- **Concept drift**: P(y|x) changes, P(x) may or may not change. "
        "Classic example: spam filters -- adversaries adapt and the same "
        "input features start mapping to different labels. Fix: relabel and "
        "retrain with fresh data. Re-weighting the SAME labels will make "
        "things worse because the labels themselves are now wrong.",
        "- **Label / prior shift**: P(y) changes, P(x|y) stable. Classic "
        "example: disease prevalence shifts across hospitals but the "
        "symptom-to-disease generative model is stable. Fix: recalibrate "
        "via Saerens-Latinne-Decaestecker EM or BBSE (black-box shift "
        "estimation). No retraining needed if the model is probabilistic.",
        "Diagnostic flow:",
        "- Step 1: is P(x) drifting? Run PSI / KS per feature.",
        "- Step 2: is P(y) drifting? Compare recent label distribution to "
        "training (if labels are available -- often delayed).",
        "- Step 3: is P(y|x) drifting? Compare model accuracy on a fresh "
        "small labeled slice. If accuracy drops WITHOUT P(x) drift, that is "
        "concept drift.",
        "Canonical trap: you see P(x) drift, assume covariate shift, "
        "re-weight. Online metric does not recover. The real cause was "
        "concept drift that happened to co-occur with covariate shift. "
        "Always check labels (step 3) before blaming P(x) alone.",
        FormulaBlock(
            latex=(
                r"w(x) = \frac{P_{\text{target}}(x)}{P_{\text{source}}(x)}, \quad "
                r"\mathbb{E}_{\text{target}}[\ell(f(x), y)] = "
                r"\mathbb{E}_{\text{source}}\bigl[w(x) \cdot \ell(f(x), y)\bigr]"
            ),
            explanation=(
                "Importance-weighting identity: only valid under covariate shift, NOT concept drift:"
            ),
        ),
        "Oral shortcut: 'Three shifts: P(x) covariate, P(y|x) concept, P(y) "
        "label. Covariate -> re-weight by P_target / P_source. Concept -> "
        "relabel and retrain. Label -> recalibrate. P(x) drift is necessary "
        "but NOT sufficient for covariate shift; always check label "
        "accuracy.'",
    ])

    # --- AC (5): Per-feature / per-segment alerting ---
    b.add_section("5. Per-Feature and Per-Segment Alerting", [
        "Aggregate drift scores are a classic false-negative trap. A model "
        "with 500 features can have 5 features blown wide open while the "
        "mean PSI looks fine. The fix is dimensional alerting.",
        "Alert-axis checklist:",
        "- **Per feature**: one PSI / KS per feature, rank by score, alert "
        "top-K. A single feature with PSI > 0.25 triggers investigation "
        "even if the model-level aggregate is calm.",
        "- **Per segment**: split by device, country, user cohort, "
        "day-of-week. Drift often concentrates in one segment (e.g., iOS 17 "
        "rollout changes screen-time distribution for iOS users only).",
        "- **Per time window**: compute PSI on daily, 7-day, and 30-day "
        "windows. Fast 1-day spikes are often pipeline bugs; slow 30-day "
        "trends are real population shift.",
        "- **Per feature family**: cluster correlated features (e.g., all "
        "engagement counters) so a bug in one pipeline shows as one "
        "cluster-level alert, not 50 noisy feature-level alerts.",
        "Multiple-testing correction: with 500 features and alpha=0.05 you "
        "expect 25 false positives per day. Apply Benjamini-Hochberg FDR "
        "control on the daily p-values, or use a higher threshold (alpha / "
        "K) if you need strict Bonferroni. For effect-size gates (PSI > "
        "0.25), FDR is moot -- the threshold IS the multiple-testing "
        "control.",
        FormulaBlock(
            latex=(
                r"\mathrm{FDR}_{\text{BH}}\!: \text{ reject } H_{(k)} \text{ if } "
                r"p_{(k)} \le \frac{k}{K} \cdot \alpha"
            ),
            explanation=(
                "Benjamini-Hochberg step-up on sorted p-values p_(1) <= ... <= p_(K):"
            ),
        ),
        "Alert fatigue countermeasures:",
        "- **Hierarchy of severity**: only page on critical (PSI > 0.25 + "
        "segment-correlated + feature is high-importance in the SHAP "
        "ranking). Everything else goes to a dashboard, not a pager.",
        "- **Suppression window**: if a feature is already firing, "
        "suppress duplicates for 24 hours to avoid slack-storming the team.",
        "- **Auto-triage**: a feature whose drift is explained by an "
        "upstream pipeline config bump should auto-link to the deploy "
        "timeline (Grafana annotation) so the on-call sees cause-and-effect "
        "at a glance.",
        "Oral shortcut: 'Never trust a single aggregate drift number. Alert "
        "per feature, per segment, per time window. FDR-correct daily "
        "p-values or use effect-size gates like PSI > 0.25. Page only on "
        "high-importance features; dashboard everything else.'",
    ])

    # --- Section 6: Comparison table ---
    b.add_section("6. Drift Metrics at a Glance", [
        "Pick the metric by feature type, desired symmetry, and the question "
        "you are asking.",
    ])

    b.add_comparison_table(
        headers=["Metric", "Feature type", "Symmetric?", "Bounded?",
                 "Thresholds", "When to use"],
        rows=[
            ["PSI", "Binned (cat or numeric)", "Yes (de facto)",
             "No (but finite)", "0.1 / 0.25",
             "Daily single-feature dashboards"],
            ["KL", "Binned", "No", "No",
             "Application-specific", "Reference vs current with natural ordering"],
            ["JS", "Binned", "Yes", "Yes (<= ln 2)",
             "~0.05 warn, ~0.1 critical", "Symmetric alerting, embeddings"],
            ["KS", "Continuous", "Yes", "Yes (<= 1)",
             "D > 0.05 or p<alpha", "Continuous features without binning"],
            ["MMD", "Any (kernel)", "Yes", "Yes",
             "Domain-specific", "Multivariate / embeddings"],
            ["Domain classifier AUC", "Any", "Yes", "Yes (<= 1)",
             "AUC > 0.6", "High-dimensional covariate shift"],
        ],
        title="Feature drift metrics comparison",
    )

    b.add_section("7. Three Shifts and Their Fixes", [
        "The fix depends entirely on WHICH distribution moved. Misdiagnosing "
        "the shift type is the single most common production failure.",
    ])

    b.add_comparison_table(
        headers=["Shift", "What moves", "What stays", "Fix", "Relabel?"],
        rows=[
            ["Covariate", "P(x)", "P(y|x)",
             "Importance re-weighting w(x) = P_target / P_source", "No"],
            ["Concept", "P(y|x)", "P(x) may move or not",
             "Retrain with fresh labels", "Yes"],
            ["Label / Prior", "P(y)", "P(x|y)",
             "Recalibrate (Saerens EM / BBSE)", "No"],
        ],
        title="Three drift types vs remediation",
    )

    # --- Summary checklist ---
    b.add_checklist("2-Minute Oral Self-Check", [
        "PSI = sum (a - e) * ln(a / e), bin-wise sum, K bins",
        "PSI thresholds: 0.1 warn, 0.25 critical (credit-scoring heritage)",
        "Equal-frequency bins fixed on reference; epsilon-clip zeros",
        "KL is asymmetric and unbounded; JS is symmetric and bounded by ln 2",
        "sqrt(JS) is a proper metric (triangle inequality holds)",
        "KS = sup |F1 - F2|, non-parametric, no binning, weak in tails",
        "KS critical value ~ 1.36 * sqrt((n1+n2)/(n1*n2)) at alpha=0.05",
        "Covariate shift = P(x) moves, P(y|x) stable -> re-weight",
        "Concept drift = P(y|x) moves -> relabel and retrain",
        "Label shift = P(y) moves, P(x|y) stable -> recalibrate",
        "Alert per feature, per segment, per time window -- never aggregate only",
        "FDR-correct p-values OR rely on effect-size gates like PSI > 0.25",
    ])

    return b


def main() -> None:
    """Build and save the feature drift drill note."""
    b = build_note()
    content = b.build()

    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    out_path = docs_dir / "google_feature_drift_drill.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {out_path} ({len(content)} chars)")

    doc_id = b.save_to_db(company_id=COMPANY_ID, doc_title=DOC_TITLE)
    print(f"[DONE] DB document id={doc_id}")


if __name__ == "__main__":
    main()
