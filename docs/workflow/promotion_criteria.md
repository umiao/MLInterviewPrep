# Meta-Prep Promotion Criteria (T-P1-801)

The threshold rule for promoting per-company prose patterns into the shared
`meta-prep/*` pillar of the KG.

This document is the locked spec. The thresholds below are the gating
contract for T-P1-803 through T-P1-807 (B3 shared-substrate seeds) and
T-P1-821 (B4-promotion consolidation). Changes to this file require a
new task with explicit user approval -- do not adjust the thresholds
mid-batch without re-running affected B3/B4a steps.

---

## The threshold

A pattern is promoted to a `meta-prep/*` node if and only if **both**
conditions hold:

1. **Frequency**: the pattern appears in **>=3 of 11** P0+P1 companies'
   prose surfaces (S1 prep_notes, S2 notes, S3 company_documents).
2. **De-companiable wording**: the pattern can be rewritten without
   referencing any specific company, team, product, or person while
   preserving its instructional value.

Both conditions are necessary. Frequency without de-companiability
produces a meta-prep node that's actually three companies' opinions
glued together; de-companiability without frequency produces a
single-source generality that belongs in the company's own KG node, not
the shared pillar.

---

## The 11 P0+P1 companies (the denominator)

The denominator is anchored to the 11 companies whose status is
`onsite`, `phone_screen`, or who are explicitly tagged P0/P1 in the
KG-INT B-batch. As of 2026-05-10:

| Status | Companies |
|---|---|
| `onsite` | Google, Uber, Pinterest, Meta |
| `phone_screen` | LinkedIn, DoorDash, Adobe, TikTok, Slack, PARSPEC |
| Explicit P0/P1 | (any company with active onsite-prep work; see audit B1 roll-up) |

Total: 11. The 18 `applied`-status companies (Apple, Nvidia, Reddit,
Salesforce, Microsoft, Instacart, Robinhood, Roblox, Amazon, Coinbase,
Quora, Intuit, Snap, OpenAI, Anthropic, Airbnb, Glean, Netflix) are
**not** part of the denominator. They are processed lightweight via
T-P2-835 (KG-extraction only, no archive, no promotion).

If a company moves from `applied` to `phone_screen` or `onsite` mid-batch,
the denominator updates from 11 to 12 and the threshold from `>=3 of 11`
to `>=3 of 12`. Re-run B3/B4-promotion for that company; do not retroactively
re-evaluate already-promoted patterns -- they meet the OLD threshold and
that's locked.

---

## Frequency: what counts as "appears"

A pattern "appears" in a company iff at least one of:

- A heading or paragraph in S1 prep_notes / S2 notes / S3 company_documents
  contains a meaningful instance of the pattern (not just a passing mention)
- An entry in `framework_node_problems`, `concept_links`, or
  `behavioral_example_company_tags` operationalizes the pattern for that
  company

"Meaningful instance" excludes:

- Single-word mentions in a long bullet list ("...HNSW, IVF, LSH...")
  -- this is taxonomy, not coverage
- Section headings with no body content
- Auto-generated cross-reference tables

The judgment call is "if I deleted this paragraph, would the company's
prep be measurably worse?" If yes, it counts.

---

## De-companiable wording: the rewrite test

A pattern is de-companiable iff its meta-prep version, rewritten without
any company/team/product/person reference, retains:

- The same actionable advice (the *what to do*)
- The same warning signs (the *what to avoid*)
- The same reasoning (the *why this works*)

If de-companying drops any of those three, the pattern is **not**
promotable. It belongs in the company's KG node (as a company-specific
node) or in `concept_links.note` on a per-company link.

### Examples

#### Promotable

> "When the interviewer asks about HNSW, lead with the layered-graph
> structure (top sparse, bottom dense), then explain greedy descent +
> backtracking on each layer. Anchor the recall/latency tradeoff in
> ef_construction and ef_search."

This is de-companiable: drop nothing, just remove the implicit "Pinterest
asks about HNSW because of their pin embedding pipeline" framing if it
exists. Goes to `meta-prep/system-design-must-knows/HNSW`.

#### Not promotable

> "Google's R2 round emphasizes calibration deep-dives because the GMB
> ads team's bidding model has had production calibration drift twice."

The actionable advice (calibration deep-dive) is universal but the
*reason it's emphasized* is Google-specific (the GMB incident). De-companying
loses the "why R2 specifically" signal. Stays in Google's KG node, possibly
as a `concept_links.note` linking the calibration framework_node to
Google's company_id.

#### Edge case: 3+ companies but each with their own framing

If 3+ companies prep "calibration deep-dive" but each frames it for a
different production reason (Google: GMB ads, Pinterest: pin ranking,
Uber: ETA model), the **technique** is promotable to `meta-prep/...`,
but the **company-specific framings** stay as `concept_links.note` on
the per-company links. Two artifacts, not one.

---

## Mechanical scoring (for §2 migration matrix)

When writing the §2 matrix in a B4a archive plan, each candidate row
gets a `[PROMOTION]` flag iff the row would pass both conditions if
the matrix were extended across all 11 companies.

The flag is **prospective** -- it does not require the other companies'
plans to exist yet. T-P1-821 (B4-promotion) consolidates flags across
all B4a plans and applies the actual `>=3 of 11` cut.

A row flagged `[PROMOTION]` should also have a proposed
`meta-prep/*` target node in the "现迁移到" column, even if that node
doesn't exist yet -- it gets created during T-P1-821 if the cut passes.

---

## Anti-patterns

- **One-source promotion**: a pattern from a single company gets
  promoted because "it's universal." Universal-feeling is not the
  threshold; 3+ companies' independent occurrence is. If the user
  writes the pattern fresh in 1 company, that's authorship, not
  internalization -- belongs in that company's KG node.

- **Wording-drift collation**: 3 companies have the pattern but each
  in slightly different wording, and the meta-prep node uses one
  company's wording verbatim. This is "promote by hostage" -- the
  meta-prep node is now company-X-flavoured. Always rewrite into
  neutral wording before promoting.

- **Threshold-relaxation creep**: "this only appears in 2 companies
  but it's clearly important, let's promote it anyway." No. Two-company
  patterns wait for a third occurrence. Premature promotion creates
  meta-prep nodes that get retroactively edited as more companies
  show up with their own framing -- which is exactly the duplication
  problem the protocol is designed to prevent.
