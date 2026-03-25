# Story L: Delegation Decision -- Hashing Experiment Platform

**Source**: Discord message 1486229408619696324
**Example ID**: EX-22
**Task**: T-P0-48
**Date imported**: 2026-03-24

## Raw Story

Building seller group testing for an experiment platform. Had a working hash
approach (sellerID * prime, take high bits) but researcher preferred standard
hash. Key delegation moment: recognized "only I find it intuitive" is a risk
for team maintenance. Actively chose to hand decision authority to researcher
while defining an acceptance framework (uniformity, performance, latency).
Researcher found MurmurHash, discovered existing dedupe hash had ItemID
distribution issue, built reusable library.

Result: better than original approach, researcher gained ownership.

Thesis: delegation is not "I can't so you do it" -- it is recognizing the right
person owning the decision produces better results.

## Cross-References

- LDR-6: Delegate vs handle yourself -- chose to delegate hashing decision
- LDR-8: Trust someone else for key decision -- handed algorithm choice to researcher
- LDR-9: Quality while delegating -- defined acceptance framework (uniformity, performance, latency)
- LDR-7: Empowered team member -- researcher gained ownership, discovered issues, built library
- PS-5: Multiple options choose one -- custom prime hash vs standard hash vs MurmurHash
