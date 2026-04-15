"""One-shot: create Pinterest Sketch/Streaming theory 1-pager and ingest to DB.

T-P0-436 deliverable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_note_builder import FormulaBlock, StudyNoteBuilder

COMPANY_ID = 29
DOC_TITLE = "Pinterest Sketch/Streaming Theory 1-Pager"


def build_note() -> StudyNoteBuilder:
    """Build the sketch/streaming theory study note."""
    b = StudyNoteBuilder()

    b.set_title("Sketch & Streaming Algorithms -- Pinterest Prep")

    b.add_prerequisites([
        "Hash functions and collision analysis",
        "Heap-based top-K (LC 703/973/378)",
        "Probability basics (expectation, variance, Markov/Chebyshev bounds)",
    ])

    b.add_term("CMS", "Count-Min Sketch",
               "Sub-linear frequency estimator using multiple hash functions")
    b.add_term("HLL", "HyperLogLog",
               "Cardinality estimator using leading-zero statistics")
    b.add_term("SS", "Space-Saving (Misra-Gries variant)",
               "Deterministic heavy-hitter detection with O(1/e) counters")

    # --- Section 1: Count-Min Sketch ---
    b.add_section("1. Count-Min Sketch (CMS)", [
        "**What**: A probabilistic data structure for point frequency queries on a stream.",
        "**Structure**: d independent hash functions, each mapping to a row of w counters "
        "(d x w matrix). On `update(item, count)`: increment `table[i][h_i(item)]` for "
        "each row i.",
        "**Query**: Return the minimum across all d rows:",
        FormulaBlock(
            latex=r"\hat{f}(x) = \min_{i=1}^{d} \; \text{table}[i][h_i(x)]",
            explanation="Frequency estimate (always overestimates, never underestimates):",
        ),
        "**Error bound**: With w = ceil(e/epsilon) and d = ceil(ln(1/delta)):",
        FormulaBlock(
            latex=r"\hat{f}(x) \leq f(x) + \varepsilon \|a\|_1 \quad "
                  r"\text{with probability} \geq 1-\delta",
        ),
        "**Why overestimate-only**: Hash collisions can only add counts, never subtract. "
        "Taking the min across rows minimizes collision impact.",
        "**Use case**: Top-K heavy hitters in real-time streams. "
        "Pinterest trending pins: CMS tracks pin impression frequencies, "
        "a min-heap of size K maintains the current top-K. "
        "Update: increment CMS, if new estimate > heap minimum, replace.",
        "**Space**: O(w * d) = O((1/epsilon) * ln(1/delta)) -- sub-linear in stream size.",
    ])

    # --- Section 2: Space-Saving ---
    b.add_section("2. Space-Saving / Misra-Gries", [
        "**What**: Deterministic algorithm for finding all items with frequency > n/k "
        "using at most k-1 counters. The Space-Saving variant (Metwally 2005) refines "
        "replacement strategy.",
        "**Algorithm (Misra-Gries)**:\n"
        "1. Maintain at most k-1 (item, count) pairs.\n"
        "2. On new item: if item tracked, increment; if slots available, add with count 1; "
        "else decrement ALL counters by 1 and remove zeros.",
        "**Space-Saving twist**: Instead of decrement-all, evict the item with the "
        "smallest count and replace it with the new item, setting count = (evicted count + 1). "
        "This gives tighter estimates than Misra-Gries.",
        "**Guarantee**: Any item with true frequency > n/k will appear in the final set. "
        "False positives possible, false negatives impossible for heavy hitters.",
        "**Space**: O(1/epsilon) counters -- more space-efficient than CMS for the same "
        "error guarantee because it avoids the d-row overhead.",
        "**CMS vs Space-Saving**:\n"
        "- CMS: simpler, parallelizable (merge = element-wise add), but more space.\n"
        "- Space-Saving: tighter bounds, less space, but harder to merge across shards.",
    ])

    # --- Section 3: Reservoir Sampling ---
    b.add_section("3. Reservoir Sampling (LC 382/398)", [
        "**What**: Select k items uniformly at random from a stream of unknown length N, "
        "using O(k) memory.",
        "**Algorithm (Vitter's R)**:\n"
        "1. Fill reservoir with first k items.\n"
        "2. For the i-th item (i > k): generate j = random(1, i). "
        "If j <= k, replace reservoir[j] with the new item.",
        "**Proof sketch**: Each of the N items has exactly k/N probability of being in "
        "the final reservoir (induction on i).",
        "**Weighted variant (LC 528 / A-ES)**: Use key = random^(1/weight); keep top-k keys. "
        "Items with higher weight are exponentially more likely to survive.",
        "**Pinterest application**: Ad impression sampling for offline analysis -- "
        "maintaining a fair sample of user-ad interactions from a massive event stream "
        "without knowing total volume in advance.",
        "**Complexity**: O(k) space, O(1) per element (amortized).",
    ])

    # --- Section 4: HyperLogLog ---
    b.add_section("4. HyperLogLog (HLL)", [
        "**What**: Estimates the number of distinct elements (cardinality) in a stream "
        "using O(m) = O(1/epsilon^2) registers.",
        "**Mechanism**:\n"
        "1. Hash each item to a uniform bit string.\n"
        "2. Use first p bits to select one of m = 2^p registers.\n"
        "3. Count leading zeros in remaining bits; store max per register.",
        FormulaBlock(
            latex=r"\hat{n} = \alpha_m \cdot m^2 \cdot \left(\sum_{j=1}^{m} 2^{-M[j]}\right)^{-1}",
            explanation="Harmonic-mean estimator across registers:",
        ),
        "**Accuracy**: Standard error ~ 1.04 / sqrt(m). "
        "With 2^14 = 16384 registers (12 KB), relative error ~ 0.81%.",
        "**Not top-K but frequently co-asked**: Interviewers testing streaming knowledge "
        "often ask HLL alongside CMS. Key distinction: HLL estimates cardinality (how many "
        "distinct?), CMS estimates frequency (how often each?).",
        "**Pinterest application**: Counting unique pinners who saw a campaign -- "
        "exact `COUNT(DISTINCT user_id)` over billions of events is expensive; "
        "HLL gives ~1% error in 12 KB.",
    ])

    # --- Comparison table ---
    b.add_comparison_table(
        headers=["Algorithm", "Answers", "Space", "Mergeable?", "Error Type"],
        rows=[
            ["CMS", "Point frequency", "O(1/e * ln(1/d))", "Yes (add)", "Overestimate"],
            ["Space-Saving", "Heavy hitters (freq > n/k)", "O(1/e)", "Hard", "Over+Under"],
            ["Reservoir", "Uniform sample of k", "O(k)", "No", "Sampling variance"],
            ["HLL", "Distinct count", "O(1/e^2)", "Yes (max)", "Relative ~1%"],
        ],
        title="Streaming Algorithms Comparison",
    )

    # --- Interview bridge ---
    b.add_section("Interview Bridge: Pinterest Real-Time Top-K Trending Pins", [
        "**Setup**: \"How would you find trending pins in real time at Pinterest scale?\"",
        "**Answer skeleton**:\n"
        "1. Naive: Global min-heap of size K tracking exact counts -- "
        "doesn't scale because maintaining exact per-pin counts requires O(N) space "
        "where N is the pin vocabulary.\n"
        "2. Better: **CMS + min-heap**. CMS estimates frequency in sub-linear space; "
        "min-heap of size K maintains the current top-K pins by estimated frequency. "
        "On each event, update CMS, compare estimate with heap minimum, swap if larger.\n"
        "3. Distributed: Shard by hash(pin_id), each shard runs local CMS + heap, "
        "periodically merge top-K lists (CMS is mergeable via element-wise addition).\n"
        "4. Decay: Apply exponential time decay to counts (multiply all counters by "
        "decay factor on each window tick) to capture recency, not just all-time volume.",
        "**Follow-up hooks**:\n"
        "- \"What if you need exact top-K?\" -- Space-Saving gives deterministic guarantees "
        "for heavy hitters but is harder to distribute.\n"
        "- \"How do you handle bursty traffic?\" -- Sliding window CMS or decaying counters.\n"
        "- \"How do you evaluate accuracy?\" -- Sample ground truth on a subset, "
        "measure precision@K and recall@K of the approximate top-K vs exact.",
    ])

    return b


def main() -> None:
    """Build note, save to file and DB."""
    builder = build_note()
    content = builder.build()

    # Save to docs/
    doc_path = Path(__file__).resolve().parent.parent / "docs" / "pinterest_sketch_streaming_1pager.md"
    doc_path.write_text(content, encoding="utf-8")
    print(f"[DONE] Wrote {doc_path.name} ({len(content)} chars)")

    # Ingest to DB
    db_path = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    builder.save_to_db(COMPANY_ID, DOC_TITLE, db_path=db_path)


if __name__ == "__main__":
    main()
