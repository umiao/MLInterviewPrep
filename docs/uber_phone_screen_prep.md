# Uber MLE -- Phone Screen Prep Materials

> **Stage**: Technical Phone Screen (after Recruiter Screen)
>
> **Format**: 2 rounds, each 1hr on HackerRank. NOT ML-specific -- general software engineering coding.

---

## 1. MLE Interview Process Overview

For Machine Learning Engineer roles, Uber typically runs:

| Stage | Focus |
|-------|-------|
| Recruiter Screen | Background fit, motivation, logistics |
| Technical Screen | Coding ability, ML fundamentals (YOU ARE HERE) |
| Final Loop (4-5 rounds) | See below |

**Final Loop Rounds:**
1. **Coding & Data** -- Algorithm implementation, data manipulation
2. **Applied ML** -- Model selection, feature engineering, evaluation metrics, trade-offs
3. **System Design** -- End-to-end ML system architecture (training, serving, monitoring)
4. **Product & Collaboration** -- Translating business problems to ML solutions, cross-functional communication
5. **Behavioral** -- Cultural norm alignment, leadership, conflict resolution

**What Uber evaluates:**
- **Production Ownership** -- Systems that work under latency constraints and data imperfections
- **Trade-off Reasoning** -- Accuracy vs latency vs cost vs marketplace stability
- **Operational Maturity** -- Model drift, monitoring, debugging, graceful degradation
- **Cross-functional Communication** -- Explaining technical decisions to non-technical stakeholders

---

## 2. Process Structure

> **Evaluation pillars**: Technical competence + Communication + Problem solving. The key is finding the right balance across all three -- pure coding speed without explanation is not enough.

| Stage | Format | Duration |
|-------|--------|----------|
| Phone Screen 1 | HackerRank coding | 1 hr |
| Phone Screen 2 | HackerRank coding | 1 hr |
| Virtual Onsite (4 rounds) | System design, ML, behavioral, team match | 4 x 1 hr |

Total timeline: ~4-5 weeks from first phone screen to final decision. The Team VO round determines which specific team you match with.

---

## 3. Problem-Solving Approach

**Do NOT jump straight into coding.** The interviewer is evaluating your thought process as much as the solution itself.

1. **Clarify the objective** -- Restate the problem, confirm constraints and edge cases
2. **Explore multiple approaches** -- Discuss 2-3 possible solutions at a high level
3. **Analyze tradeoffs** -- Compare time/space complexity, readability, edge case handling
4. **Propose and justify your choice** -- Explain why this approach fits best
5. **Code it cleanly** -- Then implement with clear structure

**Anticipate and lead the cadence.** Don't wait for the interviewer to prompt each step -- drive the conversation forward. Show you can structure your own thinking.

---

## 4. Content Areas

| Area | Details | Priority |
|------|---------|----------|
| **DSA fundamentals** | Arrays, strings, trees, graphs, hash maps | High |
| **Dynamic Programming** | DP is explicitly possible -- practice common patterns (knapsack, LIS, grid paths) | High |
| **ML algorithm coding** | KNN implementation, possibly ANN (approximate nearest neighbor) | Medium-High |
| **Syntax fluency** | Write clean Python without constantly looking up API -- interviewer notices hesitation | High |
| **Edge/corner cases** | Proactively identify: empty input, single element, overflow, duplicates | High |
| **Test case generation** | Demonstrate ability to create your own test cases -- don't just rely on provided examples | High |
| **Complexity analysis** | State time and space complexity for every approach discussed | High |

---

## 5. Communication and Style

**Coding style matters:**
- Clean, readable code with meaningful variable names
- Modular structure (helper functions where appropriate)
- Be prepared to defend your solution choices

**Adaptability:**
- If the interviewer suggests a different direction, pivot gracefully
- Show you can incorporate feedback in real-time -- this signals coachability

**Pacing (critical):**
- Do NOT spend the entire hour on coding
- Reserve ~10+ minutes for experience discussion or follow-up questions
- Reserve ~5 minutes at the end for your own questions
- Rough allocation: ~5 min problem understanding, ~35-40 min coding + discussion, ~10 min experience, ~5 min your questions

---

## 6. Phone Screen Checklist

- [ ] Practice 5+ HackerRank medium problems (DSA focus, timed 35-40 min each)
- [ ] Practice 2-3 DP problems (tabulation + memoization approaches)
- [ ] Implement KNN from scratch (distance metrics, k selection, edge cases)
- [ ] Review ANN concepts (locality-sensitive hashing, tree-based approaches)
- [ ] Practice talking through solutions aloud while coding
- [ ] Do at least 2 mock interviews with the "clarify -> explore -> tradeoff -> code" flow
- [ ] Prepare 2-3 concise experience talking points (~2 min each) for the non-coding portion
- [ ] Review Python standard library: collections, heapq, bisect, itertools
