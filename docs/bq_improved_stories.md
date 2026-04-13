# BQ Interview Stories -- Improved & Interview-Ready

## Improvement Criteria Applied

Every story below has been reviewed and improved per these criteria:

| # | Criterion | What It Means |
|---|-----------|---------------|
| 1 | **Risk & Consequence First** | Every story explicitly states what was at risk and the severe consequences if not addressed |
| 2 | **Result = Impact-Driven Recovery** | Result leads with how the project was saved and what success was achieved -- never ends abruptly after describing a process |
| 3 | **Technical Terms Concise** | All domain terms (MRR, GMB, LTR, NDCG, etc.) get a one-line plain-English definition on first use |
| 4 | **Audience-Friendly Examples** | Uses concrete, relatable analogies assuming no tech background |
| 5 | **Situation = One Sentence** | Maximum brevity for context-setting |
| 6 | **Action = Bullet Points** | Structured for interviewer note-taking |
| 7 | **Domain Knowledge Depth** | Each story demonstrates deep expertise and context |

---

## STORY 1: Search Diversity -- Intent Collapse (EX-01)

**Situation:** During Hacker Week, I discovered that our search ranking system was silently failing half its users. Multi-intent queries like "pokemon" returned 90%+ trading cards, even though purchase data showed half the buyers actually wanted games, toys, or figures. Standard metrics looked healthy because the dominant-intent users were satisfied -- the problem was invisible.

> **Terms:** *LTR (Learning to Rank)* = ML model that scores and orders search results. *Pairwise LTR* = scores each item independently, which can cause all top results to cluster around one type. *GMB (Gross Merchandise Bought)* = total dollar value of purchases, the key business metric. *Intent collapse* = when a ranking system converges on a single interpretation of an ambiguous query, crowding out other valid intents.

**Risk if not addressed:** Half of users on multi-intent queries were completely unserved -- they saw irrelevant results and abandoned. This was invisible to standard metrics because the dominant-intent users masked the missing ones. Without intervention, the organization would continue optimizing a broken system that looked healthy.

> **Simple analogy:** A restaurant menu only shows steak dishes because steak is the top seller. Vegetarian customers leave immediately -- but the restaurant thinks business is great because steak lovers are happy. They're losing half their potential customers and don't even know it, because they only measure satisfaction of people who stayed.

**Task:** No one had assigned this. I had one week to validate the problem, pinpoint the root cause, and build a working prototype that proved it was fixable.

**Action:**
- Analyzed abandoned-query logs and found a systematic pattern: hundreds of high-volume queries suffered the same "intent collapse," where one product type crowded out everything else
- Diagnosed the root cause -- our ranking model scored each item in isolation, so it had no mechanism to reason about diversity across the full results page. The highest-scoring items all looked alike.
- Built an end-to-end diversity-blending prototype in one week -- data pipeline, blending algorithm, and experiment framework -- and validated with purchase data that it surfaced previously invisible user intents

**Result:** This self-initiated project proved clear revenue improvement potential and grew into a multi-year initiative with **200M+ annualized impact** across multiple product verticals. The core insight -- that item-level scoring creates page-level homogeneity -- fundamentally changed how the organization approached ranking optimization. The methodology was also published as a full research paper at **SIGIR**, a premier information retrieval conference.

> **Memory anchor:** "Standard metrics said everything was fine -- because they only measured the users who stayed."

---

## STORY 2: Overcoming Organizational Resistance via Strategic Team Transfer (EX-02)

**Situation:** After winning Hacker Week, my diversity ranking project stalled because my manager believed our team's mission was relevance filtering, not ranking optimization -- no experiment slots were allocated and the work was considered out-of-scope.

**Risk if not addressed:** A validated project with demonstrated GMB improvement potential would die due to organizational misalignment. The 200M+ opportunity would remain untapped, and users on multi-intent queries would continue seeing homogeneous results indefinitely.

**Action:**
- Attempted to reframe the project within the existing team's charter -- this failed because the team's OKRs were fundamentally about relevance thresholds, not ranking quality
- Recognized the core issue: the project was a ranking problem being housed in a relevance team
- Made the deliberate decision to transfer to the Final Ranking team, reframing diversity as a ranking allocation problem to align with their charter
- Acknowledged my own gap: I should have translated the business case into the team's OKR language earlier and found a ranking team sponsor sooner

**Result:** The transfer gave me complete ownership and resources. The first experiment delivered **+1% GMB**, and the allocation framework was subsequently reused across multiple verticals for **200M+ annualized impact**. Key lesson: "the problem follows the person" -- proactively seek the right organizational home rather than accepting structural constraints.

---

## STORY 3: Challenging the Industry-Standard Ranking Metric (EX-03)

**Situation:** Our search ranking team was optimizing Sale NDCG -- an industry-standard metric -- but I discovered it systematically prioritized cheap items over expensive ones, causing a \$100 necklace to rank below \$5 accessories despite generating far more marketplace value.

> **Terms:** *NDCG (Normalized Discounted Cumulative Gain)* = standard metric for ranking quality, measures how well the "best" results appear at the top. *Sale NDCG* = NDCG weighted by whether users bought the item. *Calibration* = whether the model's predicted probabilities match actual outcomes.

**Risk if not addressed:** Optimizing the wrong metric meant the entire ranking system was systematically undervaluing high-margin products. Every model improvement would push rankings further in the wrong direction -- making cheap, high-conversion items dominate while suppressing the products that actually drove marketplace revenue.

> **Simple analogy:** Imagine a real estate agent who ranks listings by "likelihood of getting a viewing" instead of "expected commission." Studio apartments would always rank first because they're easy to show, while luxury homes get buried -- even though one luxury sale generates more commission than ten studio viewings.

**Action:**
- Analyzed the relationship between item price and ranking position; demonstrated that Sale NDCG's conversion-rate weighting created systematic price bias
- Proposed GMB (price x sale probability) as the correct optimization target -- this directly measures marketplace value, not just conversion likelihood
- Discovered a deeper calibration trap: the model's group-level probabilities looked correct, but individual item scores were insensitive to item-level differences, causing price alone to dominate
- Designed a BM25-inspired price transformation with log scaling and per-tranche soft caps -- chosen for interpretability and cost control over theoretical optimality

**Result:** Switching to GMB proxy fundamentally improved ranking behavior. High-quality, authenticated listings saw significant GMB uplift, and the insight that **"proxy selection is the most underestimated ML decision"** became a guiding principle for the entire team's future work.

---

## STORY 4: MRR Paradox -- When a "Worse" Metric Means Better Outcomes (EX-04)

**Situation:** After launching our diversity experiment, MRR decreased while GMB and purchase rate both increased, causing stakeholder alarm since MRR was the established ranking quality metric.

> **Terms:** *MRR (Mean Reciprocal Rank)* = measures how quickly users find the first relevant result (higher = users click sooner). *GMB* = total purchase value. *Abandonment rate* = percentage of users who leave without engaging.

**Risk if not addressed:** If stakeholders rejected the experiment based on MRR decline alone, we would roll back a change that was actually generating more revenue and serving more users. The team would revert to optimizing a metric that systematically failed half the user base on multi-intent queries.

> **Simple analogy:** Imagine a bookstore rearranges shelves so mystery fans find mysteries slightly slower, but sci-fi fans -- who previously couldn't find anything -- now find great books. Total book sales go up, but the "average time to first purchase" metric gets worse. Killing the rearrangement because of one metric would sacrifice the real business improvement.

**Action:**
- Presented GMB + purchase data proving more items were being sold -- the business outcome was unambiguously positive
- Explained MRR's theoretical limitation: it assumes users have a single intent, so for "pokemon" where 50% want cards and 50% want games, giving all top slots to cards maximizes MRR but fails half the users
- Used abandonment rate decrease as UX guardrail evidence -- users were staying longer and buying more
- Delivered the key reframe: "We slightly reduced ranking efficiency for dominant-intent users, but awakened minority-intent users who were completely unserved -- the marketplace is net positive"

**Result:** Leadership accepted the new framing and adjusted team OKRs to incorporate abandonment data alongside traditional metrics. This was a **fundamental shift** in how the organization evaluated ranking quality -- moving from single-intent proxy metrics to holistic marketplace health indicators.

---

## STORY 5: Relevance Filtering -- Deployment Feasibility (EX-05)

**Situation:** As tech lead and sole MLE on a relevance filtering project, my team spent two months building a high-accuracy XGBoost model with thousands of trees. At deployment time, we discovered the model added +10% latency overhead -- completely unacceptable against our <=1% budget.

> **Terms:** *XGBoost* = ML model that stacks many decision trees in sequence. *Latency* = response time; in search, every millisecond affects user experience. *Early exit* = stop evaluating trees once accuracy converges. *Cheap rejection* = lightweight model filters out easy cases before the expensive model runs. *Silent failure* = system produces wrong results without any error signal.

**Risk if not addressed:** Two months of model development work would be wasted with no fallback. More dangerously, if the silent failures had reached production undetected, the system would have returned degraded search results with no alerts -- monitoring would show everything normal while users experienced broken relevance.

> **Simple analogy:** Designed a perfect sports car, then discovered it doesn't fit through the factory door. Realized 80% of deliveries only need a bicycle -- only 20% actually require the truck. But then found the truck was driving through toll gates where the scanner silently truncated its cargo manifest because it was too long.

**Task:** Find a model architecture that met the strict <=1% latency constraint while maintaining acceptable filtering accuracy -- and ensure it actually worked end-to-end in production.

**Action:**
- **Beat 1 -- Tried three paths, two died.** Early exit (truncate at ~600 trees), feature-pruned small model, cheap rejection. Feature-pruned lost too much accuracy. Early exit alone landed right at the latency boundary with no margin.
- **Beat 2 -- Key insight: most requests don't need the big model.** 80%+ of candidate items were obviously irrelevant. Cheap rejection + early exit cut computation by an order of magnitude. The reframe: not "how do we shrink the big model" but "most requests don't deserve the big model at all."
- **Beat 3 -- Silent failures.** In prod load testing, CI pipeline started producing wrong results with no errors. Traced to: (1) serialized model's JSON exceeded downstream field length limit, (2) request URLs ballooned past 16,384 chars -- 8x the 2,048 standard. System silently truncated data.

**Result:** Shipped meeting <=1% latency. GMB on null/low-intent queries improved **+4-6%**. Cheap rejection + early exit pattern reused for two other deployments. Established new team standard: **end-to-end payload stress test before every launch** -- verifying model outputs are received intact at every downstream stage.

> **Memory anchor:** "The real constraints aren't just model performance vs. complexity -- they're the coupling between the model and every system it touches."

---

## STORY 6: Building a Reusable Allocation Framework -- 200M+ Impact (EX-06)

**Situation:** Our initial diversity experiment showed +1% GMB, but I recognized the real opportunity was much larger -- other teams had similar under-exposure problems (authenticated listings, C2C new listings) that the same framework could solve.

**Risk if not addressed:** Without a reusable framework, each team would build ad-hoc solutions to the same allocation problem -- duplicating effort, creating inconsistencies, and leaving most of the value on the table. The +1% GMB from one vertical was a fraction of the total addressable opportunity.

> **Simple analogy:** Imagine you build a custom irrigation system for one field, and it works great. But you notice all neighboring fields have the same dry-soil problem. You could build a custom system for each field, or you could build a portable irrigation platform that any farmer can plug into. The platform approach requires more upfront investment but multiplies the value across every field.

**Action:**
- Designed the diversity solution not as a one-off fix but as a reusable allocation primitive: caching tables, deficit calculation pipeline, and uplift mechanism where new use cases only need to plug in a target distribution
- Made a key architectural decision: unified GMB bidding dimension replacing the old LTR "scoring" paradigm with an ads-style "bidding + allocation" paradigm
- This meant any ranking module (organic, carousel, ads) could compete in the same framework, eliminating the module proliferation problem

**Result:** The framework was reused for authenticated listings, C2C new listings, and other verticals -- each reuse delivered **+0.6%+ independent GMB gain**. Annualized total impact: **200M+**. The lesson: **platform primitive value far exceeds single optimization -- invest in hard infrastructure first.**

---

## STORY 7: Exposing the Self-Fulfilling Prophecy in Our Dataset (EX-07)

**Situation:** Our team debated for months whether relevance filtering actually helped, but I discovered the evaluation itself was fundamentally flawed -- we were testing models on a dataset that only contained converted results, creating a self-fulfilling prophecy where the existing system always appeared unbeatable.

> **Terms:** *Survivorship bias* = only looking at data from things that "survived" (here: items users clicked/bought), ignoring everything else. *IID (Independent and Identically Distributed)* = assumption that training and test data come from the same distribution.

**Risk if not addressed:** The team would continue wasting effort trying different models on a biased dataset -- every experiment would confirm the status quo, and the actual relevance problems (users seeing irrelevant results and abandoning) would never be addressed. The existing ranking and retrieval systems would continuously amplify their own bias.

> **Simple analogy:** Imagine testing whether a new restaurant menu is better by only surveying customers who already ate there. The existing menu always "wins" because you're only asking people who liked the food enough to stay. You'd never discover that 40% of potential customers looked at the menu, saw nothing appealing, and walked away -- because those people aren't in your survey.

**Action:**
- Identified three root issues: (1) pairwise dataset formulation was structurally biased, (2) most negative examples were dropped (survivorship bias), (3) non-purchase user value (browsing, inspiration, knowledge-seeking) was completely ignored
- Demonstrated that XGBoost's unbiased fitting on the accepted dataset was nearly unbeatable -- but this had nothing to do with model quality; it was an artifact of the dataset itself
- Through cross-functional alignment, advocated for fixing the problem at the source (dataset and problem formulation) rather than trying different models on flawed data

**Result:** Successfully convinced stakeholders to shift focus from model optimization to **problem formulation correctness** -- the actual bottleneck. This prevented further wasted engineering cycles on a self-fulfilling evaluation loop and redirected effort toward building an unbiased evaluation framework.

---

## STORY 8: Escalating Production Degradation to VP (EX-08)

**Situation:** I noticed our search production baseline was mysteriously degrading over months, but no one else saw the problem because they were using the latest production as their control group -- masking the cumulative decline.

**Risk if not addressed:** Every team was independently launching new modules (carousels, widgets) that each passed individual A/B tests but collectively degraded the user experience. Without intervention, the cumulative degradation would continue invisibly -- each new launch would look fine in isolation while the overall product quality steadily eroded. This is the "boiling frog" problem at production scale.

> **Simple analogy:** Imagine a shared office where every team adds their own poster to the walls. Each poster individually looks fine and passes a "does this poster look good?" check. But after six months, the walls are so cluttered that nobody can find anything. No single poster is the problem, but the accumulation is. And if you only compare against "how the walls looked yesterday," the problem is invisible.

**Action:**
- Compared current production against baseline from months earlier and confirmed significant GMB regression that was invisible in recent A/B tests
- Traced the cause: too many independently-launched modules, each occupying 4-6x the space of regular listings, crowding out organic results
- Quantified the cumulative impact with data showing the gap between historical and current baselines
- Escalated the finding to VP with clear evidence that independent A/B testing could not capture interaction effects between modules

**Result:** The VP-level escalation triggered a thorough investigation and ultimately led to the creation of a **dedicated module arbitration system and team** to manage it. This was the organizational genesis of the allocation framework that later produced **200M+ annualized impact**. The core insight -- that independent testing creates a blind spot for interaction effects -- became a standard consideration in the team's experiment design process.

---

## STORY 9: Conversational Search -- Proxy Item Breakthrough (EX-09)

**Situation:** In our LLM-powered conversational search project, query rewrites generated by the LLM consistently failed to find relevant results because the LLM's "world knowledge" didn't match our search engine's tokenizer and parser behavior -- plausible-sounding queries returned irrelevant or empty results.

> **Terms:** *ANN (Approximate Nearest Neighbor)* = fast similarity search using vector embeddings. *Tokenizer/Parser* = system that breaks text into searchable components. *Proxy item* = a representative example used as a search anchor instead of keywords.

**Risk if not addressed:** The entire conversational search project was blocked. Without a way to bridge LLM output and the existing search infrastructure, the project would fail -- wasting the investment in LLM integration and missing the competitive opportunity to offer conversational shopping experiences.

> **Simple analogy:** Imagine you hire a brilliant translator who speaks perfect French, but your store catalog is indexed in a dialect the translator doesn't know. Instead of trying to teach the translator the dialect (expensive, slow), you give the translator sample products from the catalog and say "find me more things like this." The translator doesn't need to speak the dialect -- the catalog's own similarity search does the matching.

**Action:**
- Diagnosed the root cause: the LLM generated semantically correct queries, but the search engine's word segmentation and keyword interpretation mangled them into irrelevant results
- Instead of fixing LLM query generation or retraining the search engine (both expensive, slow), discovered the proxy item approach: have the LLM generate descriptions of ideal items for each sub-intent, then use these as proxy items for ANN-based retrieval
- This maximally leveraged existing infrastructure (embedding search, retrieval pipelines) with zero changes to the search engine
- Each sub-intent got its own candidate stream with embedding distance for relevance scoring

**Result:** The proxy item approach delivered strong results and was the **fastest path to unblocking experimentation**. It demonstrated maximum reuse of existing infrastructure while elegantly solving the LLM-search adaptation gap -- a solution that would have taken months via the alternatives.

---

## STORY 10: Designing Rigorous Experiment Evaluation for SIGIR Publication (EX-10)

**Situation:** Standard A/B testing had systematic biases -- bucketing drift, on-policy replay limitations, and no way to separate real effects from confounds -- threatening the validity of both our production decisions and a planned SIGIR academic paper.

> **Terms:** *Bucketing drift* = users in A/B test groups change behavior over time, introducing noise. *On-policy replay* = evaluating a new policy using data from the old policy, which can be misleading. *SIGIR* = top-tier academic conference in information retrieval.

**Risk if not addressed:** Production decisions worth millions in GMB were being made on unreliable experiment data. Additionally, if the evaluation methodology didn't meet academic rigor, the SIGIR submission would be rejected -- wasting months of research work and missing the opportunity to establish the team's credibility in the academic community.

**Action:**
- Designed a paired replay protocol: same logged prefix, simultaneous control/treatment evaluation for fair comparison
- Built quantile stratification to ensure fairness across query types (head vs. tail queries have very different behavior)
- Discovered bucketing drift through personal monitoring pipeline and designed a debiased curve (A/B lift minus A/A lift) to remove it
- Established three-angle causal verification: GMB rise + JSD distance decrease (diversity mechanism working) + abandonment decrease (UX guardrail)

**Result:** The framework supported multiple rounds of experiments across different time windows and user cohorts, all showing consistent results. It was **rigorous enough for SIGIR publication** while being practical enough for daily production iteration. The three-angle verification approach became the team's standard for making causal claims about ranking changes.

---

## STORY 11: Mentoring an Intern on Goal Communication (EX-11 / Story A)

**Situation:** A PhD intern had many long-open backlog tasks and peers perceived his work as "all self-learning with no deadlines" -- but upon investigation, his actual progress was solid; the problem was purely in how he communicated it.

**Risk if not addressed:** Without intervention, the intern would receive a negative performance evaluation despite doing good work, potentially losing his return offer. The perception gap would also undermine the team's confidence in hosting PhD interns, threatening the pipeline for future research talent.

**Action:**
- Raised the issue in weekly 1:1, framed positively: "how to better showcase your contributions" rather than "you're doing it wrong"
- Taught the distinction between what leaders want to see (visibility, roadmap, confidence level) vs. raw technical details
- Shared practical rule: every update should cover goals, current progress, and confidence on completion -- not implementation details
- Coached on phased deliverables with verifiable milestones instead of overly aggressive multi-week goals

**Result:** The intern **significantly improved** his goal communication, effectively showcased his contributions, and **received a return offer**. The coaching framework (goals-progress-confidence) became my standard approach for onboarding new researchers, bridging the academia-to-industry communication gap.

---

## STORY 12: Transitioning PhD Interns from Notebooks to Production (EX-12 / Story B)

**Situation:** PhD interns were keeping GPU instances running 24/7 to avoid resource reclamation, causing burnout risk, because they were only comfortable with Jupyter notebooks and struggled to adapt to the production environment.

**Risk if not addressed:** Interns were burning out from an unsustainable work pattern (working late nights to keep instances alive). Beyond the immediate wellbeing concern, the research team couldn't effectively contribute to production projects, creating a bottleneck where only full-time engineers could ship models -- severely limiting the team's research-to-production throughput.

> **Simple analogy:** It's like researchers who can only cook in their home kitchen. When they come to a restaurant kitchen with industrial equipment, they're overwhelmed and start doing things that waste resources (leaving all burners on 24/7 because they're afraid of re-lighting them). Instead of expecting them to figure it out alone, I built them a "recipe template" that works specifically in our kitchen.

**Action:**
- **I directly addressed the unhealthy pattern** with the interns: explained that resources should only be allocated during active job runs, not kept alive continuously
- **I diagnosed the real barriers** blocking their production migration: no in-memory data review capability, need for more tests, high cost of single-run failures, dependency management complexity
- **I built the notebook-to-production checklist and template class** -- loads raw logging data -> generates dataset -> runs a simple LR model, covering the full production workflow in one reusable example
- **I ran the first review pass** personally with each intern, walking them through the migration despite early resistance; once the first two interns shipped successfully, the rest self-adopted
- **I briefed HR and the University partnership team** on the outcome so the checklist could feed back into the academic->industry transition program

**Result:** **6 interns across my org adopted the checklist**, and the outcome was cited by the HR + University partnership team as input for iterating on the academic-to-industry onboarding program. Interns stopped the unsustainable 24/7 pattern and shipped production code independently. The template became a **reusable onboarding resource for the entire research team**, enabling any new researcher to go from notebook prototype to production-ready code without 1:1 engineer handholding.

---

## STORY 13: Resolving an Authorship Dispute and Establishing Norms (EX-13 / Story C)

**Situation:** A colleague who had written less than one page of an incomplete manuscript (then abandoned the project) demanded first authorship after my intern and I completed a solid 5-page paper, claiming his contribution was "project initiative."

**Risk if not addressed:** Accepting "gift authorship" would set a toxic precedent -- anyone who briefly touched a project could claim credit for others' work. This would demoralize the intern who did substantial work, discourage future collaboration, and undermine the integrity of the team's publications.

**Action:**
- Had multiple private conversations articulating the principle: authorship should reflect actual contribution to the manuscript, not project initiation
- Stated clearly that "authorship as gift" was unacceptable and would not be the norm
- Intern prepared supporting materials: academic ethics guidelines, conference submission requirements for author declarations
- When working-level discussion failed to resolve it, brought both managers in for mediation

**Result:** Management **agreed with the contribution-based position**. The team established a lasting norm: first authorship goes to whoever made the single largest contribution; if contributions are comparable, rotate. This rule was applied to all subsequent publications -- **no further authorship disputes arose**. The intern felt validated, and the team gained a clear, fair framework for collaboration.

---

## STORY 14: From Vague AI Mandate to Production LLM-as-Judge (EX-14 / Story D)

**Situation:** In 2023, leadership wanted to "upgrade to GenAI" for expert-like search experiences, but assigned me to explore independently with only a sandbox and API credits -- no clear requirements, no precedent for LLM in our production system.

> **Terms:** *LLM-as-Judge* = using a large language model to evaluate/label data quality instead of human annotators. *QPS* = queries per second. *Krippendorff's alpha* = statistical measure of inter-rater agreement.

**Risk if not addressed:** Without a pragmatic direction, the exploration would devolve into an unfocused demo that leadership would eventually deprioritize. The org would miss the GenAI wave, and the backlog of severe relevance issues (incorrectly labeled data, inconsistent quality assessments) would continue accumulating without a scalable solution.

> **Simple analogy:** Leadership said "use AI to make our store smarter." Instead of trying to replace the entire store with a robot (impossible given our infrastructure), I found that the most impactful use was hiring an AI "quality inspector" -- it couldn't run the store, but it could reliably identify which products were mislabeled, something our human team couldn't scale to handle.

**Action:**
- Conducted a 1-week feasibility study: LLM couldn't plug into indexing pipeline, couldn't read inventory, cost analysis showed only ~tens of QPS vs. 40K peak, latency prohibitive for real-time use
- Convinced manager to pivot: instead of chasing agentic search, find the highest-value low-hanging fruit to build organizational confidence in AI
- Deep-dived into the backlog of severe relevance issues; discovered LLM-as-Judge could effectively identify, classify, and label difficult samples that humans struggled with
- Overcame multiple obstacles: human annotators themselves disagreed significantly (making AI-human agreement a flawed metric), LLM instruction-following was immature (JSON failures, NSFW policy blocks), offline comparison initially showed no improvement (diagnosed as dataset quality issue, not model quality)

**Result:** The LLM-as-Judge approach **won across multiple relevance metrics, delivered GMB improvement, and increased user engagement**. It became **production infrastructure adopted by the ads team and other groups** for measuring the impact of their changes on user experience -- scaling from a solo exploration into org-wide measurement infrastructure.

---

## STORY 15: Model Deprecation Incident -- From Implicit Dependencies to Explicit Contracts (EX-15 / Story E)

**Situation:** During on-call, I followed proper process to deprecate old models (confirmed with manager and teammates), but immediately received incident tickets -- query understanding and marketplace teams had been running undocumented tests on those models. Root cause: these teams had "informal stakeholder" relationships -- real production dependencies that existed outside any documented ownership or communication channel.

**Risk if not addressed:** Other teams' experiments and test pipelines were broken, affecting their ability to validate ongoing work. Without resolution, this incident would erode cross-team trust. More fundamentally, without systemic changes, the same class of incident would recur -- "informal stakeholder" relationships had no discovery mechanism, so the next deprecation would hit the same blind spot.

**Action:**
- I owned the gap personally even though I had followed process: **I should have checked downstream consumer Slack channels** and pinged query-understanding + marketplace leads directly before deprecating, not just confirmed internally
- I spent **2 focused days** on redeployment and cleanup to unblock every affected team, working directly with their on-calls so attribution was clear -- nobody left guessing who was doing what
- Shifted from defensive ("I followed process") to constructive ("the process has a gap"): the real problem was the absence of a discovery mechanism for implicit cross-team dependencies
- Led discussions with cross-org teams to surface all "informal stakeholder" relationships -- mapping undocumented dependencies on shared models
- Proposed systematic improvements: regular cross-team alignment mechanism, safety knobs for staged deprecation, advance deprecation warnings with archival alerts
- Head of Engineering asked me to present a formal RCA and lead follow-up investigation, which uncovered and cleaned up additional instances of the same pattern across the organization
- Pushed a **post-mortem attribution norm** -- explicit, blameless ownership of who-did-what across affected teams -- so future incidents wouldn't leak trust the way this one initially did

**Result:** **2-day fix turnaround with zero user-facing production impact** -- all affected teams unblocked and **cross-team trust fully restored**, validated by query-understanding and marketplace leads signing off on the post-mortem. RCA went beyond the single incident: identified and resolved more undocumented cross-team dependencies of the same type. Established **new cross-team communication norms for model lifecycle management** and a **post-mortem attribution norm** now referenced by other on-call teams. Core lesson (reinforced later by EX-16): **the most dangerous dependencies are not the complex ones, but the undocumented implicit ones** -- and when they break, the real recovery work is cross-team trust and clean attribution, not just the redeployment.

---

## STORY 16: Cross-Datacenter Deployment Incident -- Architectural Mismatch Discovery (EX-16 / Story F)

**Situation:** I proactively took on latency optimization without budgeted infra support to unblock my team. Initial version was approved and deployed. When iterating on the same feature/factor name, I hit undocumented "tribal knowledge": the search backend was statically compiled C++ -- any inconsistent definitions across datacenters would cause system panic. Rolled out to the second datacenter's preprod environment; error rate spiked and alerts fired.

> **Terms:** *Statically compiled* = code is frozen at build time; changing a definition in one place without rebuilding everywhere causes incompatibility. *Dynamically linked* = code loads definitions at runtime, allowing independent updates.

**Risk if not addressed:** Preprod caught the failure before customer impact, but the root cause would have been identical in prod. More importantly, this was not just "I didn't ask the right person" -- the deployment model (DC-by-DC, assuming loose coupling between DCs) was fundamentally mismatched with the system's actual coupling structure (static compilation creating implicit strong coupling across DCs). Anyone making similar changes would hit the same trap.

**Action:**
- I drove the RCA end-to-end while the backend team handled the force-merge rollback mechanics -- my contribution was diagnosis, cross-team coordination, and the post-incident architectural fix, not the rollback itself
- Blast radius contained to **~6-hour deployment delay blocking two dependent launches in preprod**; no customer impact because DC-by-DC caught it before full rollout. I was under significant pressure as the incident owner -- **called in twice to present RCA to the Head of Engineering**, first for immediate-cause analysis, then for the systemic architectural findings
- Diagnosed the root cause as an **architectural mismatch** -- DC-by-DC rollout assumes each DC is independently servable, but static compilation silently violated that assumption by requiring bit-consistent definitions across all DCs. Named the counterintuitive finding: DC-by-DC actually saved us (full rollout would have meant org-wide spike with no healthy DC to fall back to)
- Established new practice: counterpart team's tech lead must be an explicit approver (enforced via CODEOWNERS) for cross-DC shared artifact changes -- not just meeting the generic "2 approvers" policy
- Personally led the follow-up audit that uncovered **additional implicit-coupling sites** across the science stack, and drove the fix-forward plan rather than handing it off

**Result:** **6-hour deployment delay blocking 2 dependent launches; presented RCA to Head of Engineering twice; drove follow-up cleanup of additional implicit-coupling sites discovered during the audit**, and **led the migration of the science team's factors and models from statically compiled artifacts to the new declarative artifactory system** -- dynamically loaded, version-checked resources that eliminated the exact class of risk at its source. MTTR-to-systemic-fix (not just incident closure): the declarative artifactory migration was the durable deliverable that made the class of incident architecturally impossible going forward. Core lesson (same pattern as EX-15): **the most dangerous dependencies are the undocumented implicit ones**. In EX-15 it was undocumented cross-team stakeholder relationships; here it was an architectural mismatch between deployment assumptions and system coupling. Both required the same response: make implicit contracts explicit, then build mechanisms so the system enforces them rather than relying on tribal knowledge.

---

## STORY 17: Turning Harsh Feedback into Professional Respect (EX-17 / Story G)

**Situation:** A senior IC gave me harsh feedback -- saying I "lacked basic engineering quality" -- after a researcher I was supporting made late naming changes that broke a build on a PR I had verified, and the senior IC refused to review any more of my code.

**Risk if not addressed:** My professional credibility was damaged with a key senior engineer. If left unaddressed, this would limit my ability to get code reviewed and merged, slow down my team's delivery, and potentially affect my performance evaluation. The underlying process gap (unclear ownership of researcher-contributed code) would continue causing similar incidents.

**Action:**
- Shared the feedback with my manager, who expressed understanding and support
- Recognized the lesson: when you put your name on a PR, you're accountable for its quality -- regardless of who contributed the code
- Developed a clear policy for engineer-researcher collaboration: PRs must be engineer-owned (aligned with existing org policy), meaning the engineer is responsible for all changes before merge
- Proactively reached out to the senior IC to explain the full context (researcher's late changes broke a verified PR) and shared my concrete improvement plan

**Result:** **Built mutual respect** with the senior IC and became good professional friends. We both became known in the org for rigorous checklist adherence and fast response times. The engineer-researcher collaboration policy prevented similar incidents for the team going forward.

---

## STORY 18: Pushing Back on Unreasonable Scope (EX-18 / Story H)

**Situation:** As the sole engineer on the team handling 2-3 business projects, my director also required me to explore distributed training migration across three different technology stacks (Ray, Google/AWS providers, K8s) -- a scope that was impossible for one engineer in one quarter.

**Risk if not addressed:** Attempting to complete an impossible scope would result in either burnout or shallow, useless design docs that couldn't actually drive decisions. Meanwhile, the 2-3 actual business projects would suffer from divided attention. The root cause -- manager and director couldn't align on a preferred tech stack -- would remain unresolved while I absorbed all the downstream pressure.

> **Simple analogy:** Imagine your boss asks you to simultaneously test-drive a Toyota, a BMW, and a Tesla, write detailed comparison reports on each, AND continue doing your regular job. The real problem isn't that you're not working hard enough -- it's that your bosses can't agree on which car to buy, and they're using your labor as a substitute for making a decision.

**Action:**
- Recognized this was fundamentally a multi-manager "route dispute" -- each leader preferred a different tech stack and couldn't convince the other
- Proactively discussed with manager and reached alignment on the real issue: expecting one engineer to resolve a leadership alignment problem through exhaustive exploration was unreasonable
- Shifted approach: instead of trying to complete all explorations, provided analysis of pros/cons, required resources, and realistic timelines for each path -- let leaders make the decision with full information
- Explicitly corrected the director's expectation of "executable migration plan for next quarter"

**Result:** Leadership **accepted the analysis** and deprioritized distributed training, removing it from the next quarter's roadmap. This freed me to focus on the business projects that actually needed attention. The analysis also documented why distributed training isn't always better -- especially for tree-based models where parallelization bottlenecks are well-known and no widely-adopted solutions exist.

---

## STORY 19: Explaining A/B Test Confounders to Non-Technical PMs (EX-19 / Story J)

**Situation:** PMs wanted to run seller conversion tests using our existing buyer-based A/B platform, but I identified a critical confounder: treated and untreated sellers' products could appear on the same search results page, invalidating any comparison.

> **Terms:** *Confounder* = a hidden variable that makes experimental results misleading. *A/B test* = comparing two versions (A and B) to see which performs better. *Buyer-exposure-based* = experiment groups are defined by which buyer sees which version.

**Risk if not addressed:** Running the test with the confounder would produce invalid results that leadership would act on -- potentially launching a policy change based on meaningless data, or worse, killing a good policy because the test showed no effect. Millions in seller conversion optimization would be misdirected.

> **Simple analogy:** Imagine testing two fertilizers by randomly treating half the plants in a shared garden bed. The treated plants' roots share soil with untreated plants, so nutrients leak between groups. You can't tell which fertilizer works because they're contaminating each other. The solution: test on separate plots (time-separated in our case) so there's no cross-contamination.

**Action:**
- Tried slides first but found concrete examples most effective for PM audience
- Used relatable analogy: "If we're both sellers and the system randomly gives us different treatments, but our products appear on the same page, neither comparison is valid -- all qualified sellers on a page should receive the same treatment"
- Worked through the problem to find a compromise: instead of buyer-ID-based splits (which couldn't avoid the same-page contamination), run different treatments by time-of-day or day-of-week with 100% traffic

**Result:** PM **acknowledged the problem's validity** and agreed to implement time-based experiment design. This saved the team from launching tests that would have produced misleading results, and established a workable methodology for seller-side testing that the team continued to use.

---

## STORY 20: Seller Risk Fairness -- Ethical Escalation (EX-20 / Story K)

**Situation:** While reviewing risk guardrails, I discovered our seller risk model systematically penalized new sellers -- they received high risk scores with zero transaction history, creating a vicious cycle where they could never build a reputation.

**Risk if not addressed:** New sellers were trapped in a catch-22: they couldn't build a reputation because the risk model prevented them from getting visibility, and they couldn't lower their risk score without transactions. This violated marketplace fairness principles, could constitute legal risk (blanket penalties against new sellers), and directly undermined the company's strategic push into recommerce -- which depended on attracting new sellers.

> **Simple analogy:** Imagine a credit system that gives every new immigrant a score of zero and requires a credit history to improve it. They can't get credit without a score, and can't get a score without credit. The system appears neutral but is systematically unfair to newcomers. The fix isn't to remove all risk checks -- it's to evaluate newcomers on what they CAN demonstrate (listing quality, identity verification) rather than what they can't (transaction history).

**Action:**
- Phase 1: Raised the issue at design review. Principal researcher argued buyer complaints were rising and the seller bar needed to be higher. Understood his concern but believed the framing ignored the fairness problem
- Phase 2: Conducted deep research using PayPal and other industry cases to demonstrate that the tradeoff (false-positive blocking vs. fraud prevention) is inherently part of compliance. Researched platform liability legal framework; found no evidence supporting blanket new-seller penalties, which could actually constitute a bigger legal risk
- Phase 3: After working-level persuasion failed, aligned with manager and escalated to senior director with full research package

**Result:** Leadership reviewed both perspectives, **collaborated with legal department**, and confirmed the precision modeling direction -- evaluating sellers through listing quality cross-modeling rather than blanket penalties. This aligned with the company's strategic recommerce push. Key principle: **"Escalation goal is not 'let me win' but ensuring the decision is made with full information."**

---

## STORY 21: Tech Debt Balance -- Shipping Without Waiting for Infrastructure (EX-21 / Story L)

**Situation:** Features I was building required the team's new declarative artifactory system, but that system was repeatedly delayed with no clear timeline -- blocking feature delivery that the business needed now.

> **Terms:** *Declarative system* = specify WHAT you want (a JSON config), and the system figures out HOW to deploy it. *Imperative system* = manually specify every step (build Scala/C++ code, deploy to each server). *Parity test* = proves two systems produce identical output.

**Risk if not addressed:** Feature delivery would be blocked indefinitely -- possibly for a year or more -- waiting for infrastructure that was beyond my team's control. The business impact (relevance improvements for classification and real-time fixes) would remain unrealized, and the team's credibility for delivering on its roadmap would erode.

> **Simple analogy:** Imagine you need a new highway to deliver goods to a city, but the highway won't be built for a year. Instead of waiting, you discover that the highway's planned route follows existing back roads. You can pave and use those back roads now, and when the highway is finally built, merging onto it is trivial because you're already on the right path. The key insight is understanding which part of the highway is "essential route" (the roads themselves) versus "nice-to-have infrastructure" (the on-ramps, signage, toll booths).

**Action:**
- Deep research revealed the declarative system's architectural essence: the core value is generating a JSON ranking rule expression; the blockers were peripheral infrastructure (storage, versioning, deployment) -- not the expression generation itself
- Designed approach using an internal caching system for storage, injecting named expressions as parameters into the search engine
- Built parity tests proving hand-generated expressions were **identical** to what the declarative system's profiling layer would generate -- hard evidence, not promises
- Demoed equivalence to the team; declarative team had no objections because the proof was mechanical

**Result:** Feature **shipped on time** with business win, rather than being blocked for a year. When the declarative system finally became ready, migration was smooth -- the core expression implementation was already consistent, requiring only storage/versioning migration. The interim solution effectively became **early validation for the declarative system itself**. Key thesis: tech debt isn't a "fast vs. clean" binary -- it's whether you understand the architectural boundary between core and peripheral.

---

## STORY 22: Delegation -- Hashing Algorithm Decision (EX-22 / Story M)

**Situation:** I had a working custom hash approach for our experiment platform's seller group testing, but a collaborating researcher preferred standard hash functions -- and I recognized that "only I find my approach intuitive" was itself a maintenance risk.

**Risk if not addressed:** Using a custom algorithm that only one person understands creates high bus-factor risk. If I left the team or was unavailable, no one could debug or modify the hashing logic. Additionally, by insisting on my own solution, I would miss the opportunity to develop the researcher's ownership and potentially discover issues that a fresh perspective might catch.

**Action:**
- Made a deliberate decision to hand decision authority to the researcher -- not because my solution was wrong, but because team maintainability matters more than personal preference
- Defined a clear acceptance framework: the chosen algorithm must demonstrate (1) uniform distribution across groups, (2) acceptable performance benchmarks, (3) within latency budget
- Shifted my role from "solution designer" to "requirements definer and quality gatekeeper"
- Let the researcher explore freely within the framework

**Result:** The researcher found MurmurHash -- **superior to my original approach**. During evaluation, they discovered that the team's existing dedupe hash had a latent ItemID distribution non-uniformity bug that my custom approach would never have caught. They built a **reusable hashing library** adopted by multiple teams. The outcome was strictly better: better algorithm, latent bug found, reusable artifact created, and the researcher gained deep ownership. Key thesis: **delegation is not "I can't so you do it" -- it's recognizing the right person owning the decision produces better results.**

---

## STORY 23: NYC C2C Policy Launch -- Leading a 30-Person Urgent Project (EX-23 / Story N)

**Situation:** Our NYC C2C business had been declining for weeks as competitors captured market share, and the VP demanded a test within 2 weeks and a launch proposal within 1 month -- with 30+ people across the org needing to coordinate.

**Risk if not addressed:** Continued market share loss to competitors with every week of delay. The VP's urgency reflected real business risk: the C2C market has strong network effects, meaning lost sellers attract fewer buyers, which drives away more sellers. Without rapid action, the decline could become self-reinforcing and irreversible.

**Action:**
- Inventoried all workstreams, identified the critical path, and organized work so 30+ people didn't block each other
- After test launch, discovered control effectiveness was below expectations. Team suspected Kafka logging fluctuation, but while fixing logging I continued digging deeper
- Discovered root cause: upstream web gateway team had silently "fixed" an incident by overwriting our control property -- causing silent test failure that would have invalidated all results
- Found a deeper structural issue: multiple policies that tested successfully independently **competed for the same top slots** when launched simultaneously -- their effects would cancel each other out
- Convinced VP in weekly meeting to limit scope to highest-ROI policies rather than combo-launching everything

**Result:** Project **delivered within the VP's deadline**. More critically, I prevented the team from making a costly mistake: blindly combo-launching all policies would have shown disappointing results (policies canceling each other), potentially killing good individual policies based on a flawed combined test. The scope adjustment ensured the **highest-impact policies launched cleanly**, and the allocation insight became the team's framework for future ranking strategy.

---

## STORY 24: Communicating the Allocation Problem to a VP (EX-24 / Story O)

**Situation:** During the C2C project, I needed to convince the VP that simultaneously launching all successful test policies -- which seemed like the obvious "maximize impact" move -- would actually produce worse results than launching them selectively.

**Risk if not addressed:** The VP was about to authorize a combo-launch that would produce disappointing results. If the combined test showed weak performance (because policies competed for the same slots), leadership might conclude that none of the individual policies were worth pursuing -- killing initiatives that were actually effective when deployed strategically.

> **Simple analogy:** Imagine you tested three billboards individually on the same highway and each doubled sales for the advertised product. The VP says "great, put all three up at once for triple the effect!" But there's only room for one billboard at the best location. The three billboards compete for attention -- you don't get 3x, you get maybe 1.2x, and the VP thinks billboards don't work.

**Action:**
- Used conclusion-first communication: told the VP three things upfront: (1) we're overestimating the achievable combined effect, (2) we're underestimating the impact on default ranking, (3) this isn't an execution problem -- it's a structural one
- Explained in VP-accessible terms: each policy performs well independently because it monopolizes top positions, but when launched simultaneously they compete for the same positions -- no free lunch
- Framed it as an allocation problem: ranking is fundamentally about distributing limited positions, not adding independent improvements
- Recommended limiting scope to highest-ROI policies first

**Result:** VP **accepted the analysis** and adjusted project direction. The allocation framing became the **team's mental model** for thinking about ranking strategy going forward -- a lasting impact beyond the immediate project decision.

---

## EXISTING ANSWERS (COL-1 through COL-4) -- Improved

### COL-1: Disagreeing with a Teammate on Brand Recall Implementation

**Situation:** A teammate proposed a compound-key lookup table for brand recall that would require a separate query per brand, risking significant latency increase on a system handling thousands of QPS.

> **Terms:** *Query rewrite* = transforming a user's search query before executing it. *Latency* = response time added by each additional system call. *GMV* = Gross Merchandise Value, total transaction amount.

**Risk if not addressed:** Each additional query would add latency; analysis showed >15% increase. On a high-traffic search system, this would degrade user experience across all brand queries, potentially dropping conversion rates below the acceptable launch threshold.

**Action:**
- Conducted latency analysis showing the multi-query approach would exceed the <3% latency increase launch criterion
- Listened to teammate's precision concerns and addressed them directly
- Proposed query rewrite as alternative: achieves the same recall objective with a single query, eliminating the latency penalty
- Facilitated data-driven team discussion that balanced accuracy and performance

**Result:** Team aligned on the query rewrite approach. **Delivered the project on time**, achieving recall objectives while meeting GMV and latency launch criteria (<3% increase). Reinforced the value of data-driven technical decision-making.

---

### COL-2: Aligning on Code Review Standards

**Situation:** Before we aligned on shared standards, **~80% of changes on our team required custom deployment paths** to bypass the standard review queue -- reviewer bandwidth was a bottleneck, and urgent requests kept pulling multiple teams in. Repetitive review requests for tests already covered by existing policy were compounding the delay.

**Risk if not addressed:** A persistent 80% bypass rate meant the standard review process was effectively non-functional, eroding the quality gate it was meant to provide. Unresolved friction would also slow delivery velocity and push engineers to avoid PR submission altogether.

**Action:**
- I initiated a direct 1:1 conversation to understand his review standards and share my testing approach
- I walked him through which tests were already covered by existing policy, addressing his specific concerns with concrete evidence
- **I proposed the shared review checklist** and volunteered to draft the initial version; discussed it with the project lead to get buy-in
- **I documented the tradeoff** (standard-review throughput vs. custom-deployment risk) in the review doc so the team had a single source of truth

**Result:** **Cut custom-deployment rate from ~80% to ~50%, even as business-driven urgent-request volume kept rising.** Reviews became smoother, the project stayed on schedule, and the checklist + tradeoff doc became a durable artifact the team used for subsequent review disagreements without interpersonal friction.

---

### COL-3: Cross-Org Boundary Defense via LLM Relevance Pipeline

**Situation:** In 2024, I was assigned to collaborate with the ads team on relevance evaluation. Early on, the collaboration turned into a boundary conflict -- they gave me their data and hypotheses, asking me to optimize their pass-through rate from a relevance perspective. This fundamentally contradicted our org's principle: relevance standards are absolute quality thresholds, not tunable dials to let a target percentage of results through.

**Risk if not addressed:** If we caved on the boundary, relevance becomes a tunable dial for every team with a pass-through target -- the org's quality standard erodes. If we just said no without addressing the root cause, the ads team would keep escalating or work around us, and both teams waste cycles in an adversarial loop.

**Task:** Hold our data and policy boundary (senior director mandate) without blowing up the cross-org relationship, while finding a solution that addressed the ads team's legitimate underlying need.

**Action:**
- Flagged the situation to my manager immediately; agreed to hold the line but not escalate the conflict
- Instead of just saying no, dug into WHY they kept asking. Through multiple conversations, discovered their real pain point: they didn't trust the relevance model's judgment on every case, and click/purchase signals were too noisy to validate A/B tests. They needed a stronger, explainable relevance signal as a guardrail.
- Proposed a deal: we won't open our policy or model internals, but I'll build an LLM-based judgment pipeline that embeds our rules and outputs detailed reasoning for each decision -- e.g., why a golf bag passes but a golf-themed poker deck gets rejected. They get interpretable signals; we keep our abstraction boundary intact.

**Result:** Built the pipeline over Q2-Q3 2024. Produces **~18K high-quality labeled judgments/day at ~\$500** (vs \$0.30-0.80/label for human annotation). Validated at near-parity with human judgment. Integrated into internal search scraping system as standard relevance signal. Launched across ads and organic results, contributing to **1.5% GMB lift**. Relevance filtering works in tandem with ranking, preventing reward hacking and protecting customer experience.

---

### COL-4: Goal Tracking Reform -- Honest Metrics Over Cosmetic Delivery

**Situation:** Our team's goal tracking system was quietly rewarding failure. Teams would rename unfinished goals, re-scope deliverables mid-cycle, and roll them over -- so on paper, delivery rates looked healthy, but actual velocity was declining quarter over quarter.

**Risk if not addressed:** Without fixing this, the team would continue optimizing for cosmetic delivery rates -- renaming failures as successes -- while real velocity declined. Leadership would make prioritization decisions based on inflated data, and teams would lose the habit of honest estimation.

**Task:** As a stakeholder who reviewed these updates weekly, I took it on myself to fix how we set, tracked, and evaluated goals -- so that our metrics reflected reality instead of masking it.

**Action:**
- Diagnosed the root cause: updates filled with jargon that blocked peer review, progress never mapped back to prior commitments, and "delivery" often just meant renaming an old goal
- Proposed locking goal scope after kickoff and requiring peer confidence estimates against the original timeline -- not the reshuffled version
- Manager pushed back, worried this would strain partner-team relationships. She challenged me to design a proposal the whole group could accept
- Key insight: reframed goal-setting itself -- for high-uncertainty projects, teams commit to "develop and AB-test N features" rather than "make all AB tests succeed." Preserved accountability without punishing honest exploration
- Brought the revised proposal to Senior Director's office hours and secured top-down support, including an explicit no-blame policy for goals that failed under the new honest-reporting standard

**Result:** Short-term delivery rates dropped -- **which was exactly the proof the system was working**, because previously hidden problems were now surfacing. At the VP prioritization level, macro velocity improved: eliminated the cycle of disguised rollover goals and teams started setting commitments they could actually keep. **Framework later adopted by other orgs under Search.**

---

## Technical Term Quick Reference

| Term | One-Line Definition |
|------|-------------------|
| **LTR** | Learning to Rank -- ML model that scores/orders search results |
| **Pairwise LTR** | Scores each item independently; can't reason about page-level diversity |
| **GMB** | Gross Merchandise Bought -- total dollar value of purchases |
| **MRR** | Mean Reciprocal Rank -- how quickly users find the first relevant result |
| **NDCG** | Normalized Discounted Cumulative Gain -- standard ranking quality metric |
| **A/B Test** | Comparing two versions on different user groups to see which performs better |
| **Confounder** | Hidden variable that makes experiment results misleading |
| **Calibration** | Whether predicted probabilities match actual outcomes |
| **QPS** | Queries Per Second -- system throughput capacity |
| **Latency** | Response time; in search, milliseconds matter for user retention |
| **XGBoost** | Popular ML model using many decision trees in sequence |
| **ANN** | Approximate Nearest Neighbor -- fast similarity search using embeddings |
| **LLM-as-Judge** | Using an LLM to evaluate/label data quality instead of human annotators |
| **Proxy Item** | Representative example used as a search anchor instead of keywords |
| **Tokenizer** | System that breaks text into searchable components |
| **Bucketing Drift** | A/B test groups changing behavior over time, introducing noise |
| **Survivorship Bias** | Only looking at data from things that "survived," ignoring everything else |
| **Bus Factor** | Number of people who could leave before a system becomes unmaintainable |
| **MurmurHash** | Fast, well-distributed, non-cryptographic hash function |
| **Tech Debt** | Shortcuts in code/architecture that cost more to fix later |
| **Declarative System** | Specify WHAT you want; system handles HOW |
