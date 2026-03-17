"""Seed Pillar 8 (Behavioral & Leadership) framework node descriptions.

Usage:
    python scripts/seed_pillar8_content.py

Populates the `description` field for all 13 Pillar 8 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== COMMON QUESTION CATEGORIES =====

CONTENT["pillar8.common_questions.technical_leadership"] = r"""# Technical Leadership

## Overview
Technical leadership questions assess your ability to drive technical direction, make architectural decisions, and guide teams through complex ML engineering challenges. For senior MLE roles, interviewers expect evidence that you have owned technical strategy -- not just executed tasks -- and can articulate how your decisions shaped outcomes at the team or org level.

## Core Concepts

### Defining Technical Vision
Technical leaders set direction by identifying the highest-leverage problems and proposing solutions that balance short-term delivery with long-term scalability. In ML, this often means choosing between building custom infrastructure vs. adopting managed services, deciding when to invest in data quality vs. model complexity, or determining the right level of automation for ML pipelines.

Key elements:
- Translating business objectives into technical roadmaps
- Evaluating build-vs-buy tradeoffs for ML infrastructure
- Establishing team coding standards, review processes, and testing norms
- Creating alignment across data scientists, ML engineers, and platform teams

### Decision-Making Under Uncertainty
Senior MLEs regularly make high-stakes decisions with incomplete information: should you retrain the model now or wait for more labeled data? Should you invest in a new feature store or extend the existing one? Strong answers demonstrate a structured approach -- gathering signal, consulting stakeholders, defining reversibility, and setting clear success criteria before committing.

### Growing Others
Technical leadership extends beyond personal contribution. Interviewers look for evidence that you have raised the bar for your team -- through code reviews, design docs, mentoring junior engineers, or establishing best practices that outlive your direct involvement.

## STAR Templates

### Template 1: Leading a Model Architecture Migration
- **Situation**: Describe the legacy system (e.g., batch scoring pipeline with growing latency) and the business pressure driving change.
- **Task**: Emphasize your ownership of the technical direction -- you were responsible for evaluating options and building consensus, not just implementing a pre-decided plan.
- **Action**: Detail the evaluation process (benchmarking alternatives, writing an RFC, gathering feedback from stakeholders), the migration strategy (phased rollout, shadow scoring), and how you handled risks (rollback plan, monitoring).
- **Result**: Quantify impact -- latency reduction, throughput improvement, cost savings. Also mention team outcomes: "The architecture I designed is now the standard for three other teams."

### Template 2: Establishing ML Engineering Standards
- **Situation**: Team had inconsistent model evaluation practices, leading to production incidents.
- **Task**: You took ownership of defining and implementing team-wide standards.
- **Action**: Drafted an evaluation checklist, introduced automated validation in CI, ran a workshop on proper offline-online metric alignment.
- **Result**: Reduced production model rollbacks by X%, decreased time-to-deploy for new models by Y days.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Vision | "How do you decide the technical direction for your team?" | Show structured evaluation, not just intuition |
| Influence | "Tell me about a time you changed your team's technical approach." | Emphasize evidence-based persuasion and stakeholder buy-in |
| Ownership | "Describe a technical decision you made that had lasting impact." | Focus on decisions that scaled beyond your immediate work |
| Growth | "How have you helped others become better engineers?" | Concrete examples: review practices, design doc culture, pairing |

### Common Interview Questions
- [ ] Describe a time you set the technical direction for a project.
- [ ] Tell me about a difficult technical decision you made with incomplete information.
- [ ] How do you balance technical debt against feature delivery?
- [ ] Give an example of a technical standard you introduced that your team adopted.
- [ ] How do you handle disagreements about technical approach with senior colleagues?

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Scope | "I built the model" | "I designed the architecture, got buy-in, and led the migration across two teams" |
| Decision process | "I chose TensorFlow because I know it best" | "I evaluated three frameworks against our latency and team skill constraints, documented tradeoffs in an RFC" |
| Impact framing | "It worked well" | "Reduced inference latency by 40%, adopted as the standard pattern for 3 other services" |
| Team dimension | No mention of others | "Mentored two junior engineers through the migration; both now own subsystems independently" |

## Key Takeaways
- [ ] Always frame yourself as the driver of technical direction, not just a participant
- [ ] Show structured decision-making: criteria, evaluation, stakeholder alignment
- [ ] Quantify both system outcomes (latency, cost) and team outcomes (adoption, standards)
- [ ] Demonstrate that your leadership had lasting impact beyond the immediate project
- [ ] Include how you handled disagreement or resistance to your technical vision
"""

CONTENT["pillar8.common_questions.influence_without_authority"] = r"""# Influence Without Authority

## Overview
Influence without authority is one of the most critical behavioral competencies for senior MLEs. ML projects inherently span organizational boundaries -- you need data from the data engineering team, compute from the platform team, buy-in from product managers, and cooperation from downstream services. Interviewers assess whether you can drive outcomes when you have no direct reporting authority over the people whose help you need.

## Core Concepts

### Building Credibility First
Influence starts with trust. Before you can persuade others to change their priorities, you need a track record of delivering value and demonstrating competence. In ML contexts, this often means showing quick wins -- a prototype that demonstrates potential, an analysis that surfaces a problem nobody else noticed, or a fix to a shared system that benefits multiple teams.

### The Pull Model of Persuasion
Rather than pushing your agenda, effective influencers create conditions where others want to participate:
- Frame requests in terms of the other team's goals and metrics
- Make the cost of inaction visible with data
- Reduce the burden on collaborators by doing upfront work (draft designs, prototypes)
- Build coalitions by getting early buy-in from key stakeholders

### Navigating Organizational Dynamics
Senior MLEs must understand the incentive structures of partner teams. The data engineering team is measured on pipeline reliability, not model accuracy. The product team cares about user metrics, not technical elegance. Effective influence means translating your ML needs into the language of each stakeholder's priorities.

### Escalation as a Last Resort
Sometimes alignment cannot be achieved through persuasion alone. Strong answers show you know when and how to escalate -- bringing data to a shared manager, proposing a joint OKR, or creating a formal cross-team charter -- without damaging relationships.

## STAR Templates

### Template 1: Securing Data Pipeline Priority
- **Situation**: Your model needed a new feature pipeline, but the data engineering team had a full roadmap with no capacity for your request.
- **Task**: Get the pipeline built within your project timeline without having authority over the data team's priorities.
- **Action**: Built a prototype using a manual data extraction to demonstrate the model's potential impact (e.g., +5% conversion). Presented the results to both teams' leadership in a joint meeting. Offered to handle the model-side integration work to minimize the data team's scope. Proposed a phased approach where the first phase required minimal data team effort.
- **Result**: Data team allocated one engineer for two sprints. The feature pipeline shipped on time and the model improvement delivered $X in incremental revenue.

### Template 2: Aligning Product and ML on Metric Definition
- **Situation**: Product team wanted to optimize for click-through rate; your analysis showed this would increase low-quality engagement and hurt long-term retention.
- **Task**: Convince the product team to adopt a composite metric without undermining their ownership of product direction.
- **Action**: Ran an offline analysis showing the correlation between CTR-optimized recommendations and user churn. Proposed a composite metric that balanced engagement and retention. Built a dashboard that made the tradeoff visible in real time. Facilitated a workshop where both teams agreed on the new metric.
- **Result**: Team adopted the composite metric. Six-month retention improved by X% while engagement remained within acceptable bounds.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Cross-team | "Tell me about a time you needed another team to change their priorities for you." | Show empathy for their constraints, not just your needs |
| Persuasion | "How did you convince stakeholders who initially disagreed with your approach?" | Lead with data and shared incentives |
| Coalition | "Describe a time you built alignment across multiple teams." | Show the sequence: 1-on-1 buy-in before group decisions |
| Conflict | "What do you do when you cannot get agreement?" | Escalation with data, not authority |

### Common Interview Questions
- [ ] Tell me about a time you influenced a team you had no authority over.
- [ ] Describe a situation where you had to get buy-in from a skeptical stakeholder.
- [ ] How do you handle it when a partner team deprioritizes your request?
- [ ] Give an example of building a cross-team coalition for an ML initiative.
- [ ] Tell me about a time you changed someone's mind using data.

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Approach | "I asked my manager to talk to their manager" | "I built a prototype showing $X impact, then presented it in their team meeting" |
| Framing | "I told them we needed the data" | "I showed how the new pipeline would reduce their on-call load by 30%" |
| Empathy | No mention of the other team's constraints | "I understood they were in a code freeze, so I proposed a phased approach" |
| Outcome | "They eventually agreed" | "We co-authored a design doc and delivered jointly, which became a template for future cross-team projects" |

## Key Takeaways
- [ ] Always frame requests in terms of the other party's goals and metrics
- [ ] Build credibility through quick wins before making large asks
- [ ] Use data to make the cost of inaction visible
- [ ] Show that you reduced the burden on collaborators, not just demanded their time
- [ ] Demonstrate relationship preservation -- influence is a long game
"""

CONTENT["pillar8.common_questions.conflict_resolution"] = r"""# Conflict Resolution

## Overview
Conflict is inevitable in ML teams -- disagreements about model architecture, data quality standards, deployment timelines, and prioritization are part of daily work. Senior MLE interviews probe how you navigate these tensions constructively. The best answers show that you can disagree respectfully, seek to understand opposing viewpoints, and drive toward resolution without damaging relationships or team cohesion.

## Core Concepts

### Types of Conflict in ML Teams
Understanding the nature of the conflict determines the resolution strategy:

| Conflict Type | Example | Resolution Approach |
|--------------|---------|-------------------|
| Technical disagreement | "Should we use a transformer or gradient-boosted model?" | Data-driven evaluation with clear criteria |
| Priority conflict | "Should we fix model drift or build a new feature?" | Align on business impact and urgency |
| Process conflict | "How much testing is enough before deployment?" | Establish shared standards with concrete thresholds |
| Interpersonal tension | "Colleague dismisses suggestions in reviews" | Direct conversation, focus on behavior not character |
| Cross-team friction | "Data team ships schema changes without notice" | Formalize contracts and communication protocols |

### The Disagree-and-Commit Framework
A mature approach to conflict involves three phases:
1. **Advocate clearly**: State your position with supporting evidence. "I believe approach A is better because [data/analysis]."
2. **Listen actively**: Understand the other perspective fully before responding. Restate their argument to confirm understanding.
3. **Commit fully**: Once a decision is made (even if it is not your preferred option), execute with full effort. Do not undermine the chosen direction.

### Separating People from Problems
Effective conflict resolution addresses the technical or process issue without making it personal. Phrases that help:
- "I see this differently because..." (not "You're wrong because...")
- "Help me understand the reasoning behind..." (not "That doesn't make sense")
- "What would we need to see to change our approach?" (establishes objective criteria)

### When to Escalate
Escalation is appropriate when: the disagreement involves a decision with irreversible consequences, the team is stuck in a loop, or the conflict involves a values violation (e.g., shipping a model you believe is harmful). Escalation is not appropriate as a first resort or as a way to "win" an argument.

## STAR Templates

### Template 1: Technical Architecture Disagreement
- **Situation**: You and a senior colleague disagreed on whether to build a real-time feature store or extend the existing batch pipeline for a recommendation system.
- **Task**: Resolve the disagreement and move the project forward without creating a rift on the team.
- **Action**: Proposed a structured evaluation: both parties wrote one-page design docs. Defined evaluation criteria together (latency, cost, maintenance burden, time-to-ship). Ran a benchmark on a representative workload. Facilitated a team review where both designs were presented against the agreed criteria.
- **Result**: The data showed the batch approach met latency requirements at 40% lower cost. Your colleague agreed, and the team shipped in 3 weeks. The evaluation template became a team standard for future architecture decisions.

### Template 2: Resolving a Cross-Team Data Quality Dispute
- **Situation**: Your model's accuracy dropped after an upstream team changed their data schema without notification. The upstream team maintained the change was correct and your model should adapt.
- **Task**: Resolve the immediate production issue and establish processes to prevent recurrence.
- **Action**: First, fixed the immediate issue with a data validation layer. Then met with the upstream team to understand their change rationale. Proposed a schema change notification protocol and a shared data contract. Created automated compatibility tests that both teams run before deploying changes.
- **Result**: Model accuracy restored within 24 hours. The data contract process was adopted org-wide and prevented 3 similar incidents in the following quarter.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Technical disagreement | "Tell me about a time you disagreed with a colleague on a technical approach." | Show data-driven resolution, not hierarchy |
| Interpersonal | "Describe a difficult working relationship and how you handled it." | Focus on behavior change, not blame |
| Escalation | "When have you had to escalate a disagreement?" | Show it was a last resort with clear justification |
| Team dynamics | "How do you handle it when your team cannot reach consensus?" | Demonstrate a structured decision-making process |

### Common Interview Questions
- [ ] Tell me about a time you had a significant disagreement with a colleague.
- [ ] Describe a situation where you had to push back on a decision from a more senior person.
- [ ] How do you handle it when you believe a team decision is wrong?
- [ ] Tell me about a conflict that made your team stronger.
- [ ] Give an example of a time you compromised on a technical decision.

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Tone | "I was right and eventually proved it" | "We had different perspectives; here is how we found the best path forward" |
| Process | "I just kept arguing my point" | "We defined objective criteria and let the data decide" |
| Relationship | No mention of the relationship afterward | "We built a stronger working relationship and collaborated on two more projects" |
| Learning | "I would do the same thing again" | "I learned to surface disagreements earlier and propose evaluation frameworks upfront" |

## Key Takeaways
- [ ] Frame conflicts as shared problems, not personal battles
- [ ] Always propose a structured evaluation process rather than arguing from opinion
- [ ] Show that you can disagree and commit -- executing fully on decisions you did not prefer
- [ ] Demonstrate that conflicts led to better processes or stronger relationships
- [ ] Include what you learned and would do differently next time
"""

CONTENT["pillar8.common_questions.ambiguity"] = r"""# Handling Ambiguity

## Overview
ML projects are inherently ambiguous: requirements are often vague ("make recommendations better"), success metrics are unclear, data is messy, and the feasibility of a given approach is unknown until you try it. Senior MLE interviews test your ability to make progress in the face of uncertainty -- structuring ambiguous problems, making reasonable assumptions, and iterating toward clarity without waiting for perfect information.

## Core Concepts

### Structuring Ambiguous Problems
The first step in handling ambiguity is decomposition. Break a vague objective into concrete sub-questions:

| Vague Objective | Structured Sub-Questions |
|----------------|------------------------|
| "Improve search quality" | What metric defines quality? What are the top failure modes? Which user segments are most affected? What is the current baseline? |
| "Build an ML pipeline" | What is the input data source? What latency is required? What is the expected throughput? Who are the consumers? |
| "Reduce model bias" | Bias with respect to which attributes? What fairness metric is appropriate? What is the acceptable accuracy tradeoff? |

### The Assumption-Driven Approach
When information is missing, explicitly state your assumptions and validate them incrementally:
1. List what you know and what you do not know
2. Make explicit assumptions for each unknown
3. Identify which assumptions carry the most risk
4. Design experiments or prototypes to validate the riskiest assumptions first
5. Iterate: update assumptions as you learn

### Minimum Viable Experiments
Rather than building a complete solution under uncertainty, design small experiments that reduce the biggest unknowns:
- Build a simple baseline model to establish feasibility before investing in complex architectures
- Use a sample of data to validate data quality assumptions before building a full pipeline
- Deploy a shadow model to measure real-world performance before committing to a full launch

### Communicating Under Uncertainty
Senior MLEs must communicate uncertainty clearly to stakeholders:
- "Based on our current data, I estimate X with confidence level Y"
- "We have two viable approaches; here is the experiment that will tell us which to pursue"
- "I recommend we invest one sprint in a prototype before committing to the full roadmap"

## STAR Templates

### Template 1: Scoping an Undefined ML Project
- **Situation**: Product leadership said "we need personalization" with no further specification -- no defined metrics, no target user segment, no data inventory.
- **Task**: Transform this vague directive into a concrete, executable project plan.
- **Action**: Conducted stakeholder interviews to understand the business goal (increase user engagement). Analyzed existing data to identify what personalization signals were available. Defined three candidate approaches with increasing complexity. Proposed a two-week proof-of-concept using the simplest approach to validate feasibility. Presented a decision framework: if the POC showed >X% lift, invest in the full solution; otherwise, revisit the problem framing.
- **Result**: POC showed a 12% engagement lift with a simple collaborative filtering approach. Secured headcount for two additional engineers. Full system launched in Q2 and delivered 18% engagement improvement.

### Template 2: Navigating Conflicting Requirements
- **Situation**: Three stakeholders wanted different things from the same model: marketing wanted interpretability, product wanted accuracy, and legal wanted fairness guarantees.
- **Task**: Find a path forward that satisfied the core needs of all stakeholders.
- **Action**: Mapped each stakeholder's requirement to a concrete metric. Identified which requirements were truly in tension vs. which were compatible. Built a Pareto frontier showing the accuracy-fairness tradeoff. Proposed a solution that met the fairness threshold, provided feature importance explanations, and achieved 95% of the maximum possible accuracy. Presented the tradeoff analysis to all stakeholders in a joint meeting.
- **Result**: All three stakeholders agreed on the proposed approach. The explicit tradeoff framework became the standard process for resolving multi-stakeholder conflicts on future ML projects.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Scoping | "Tell me about a time you started a project with unclear requirements." | Show how you created structure from chaos |
| Assumptions | "How do you make decisions when you do not have enough data?" | Demonstrate explicit assumption-making and validation |
| Pivoting | "Describe a time you had to change direction mid-project." | Show adaptability while maintaining momentum |
| Communication | "How do you communicate uncertainty to non-technical stakeholders?" | Use concrete frameworks, not vague hedging |

### Common Interview Questions
- [ ] Tell me about a time you had to make progress without clear direction.
- [ ] Describe a project where the requirements changed significantly mid-stream.
- [ ] How do you prioritize when everything seems equally important and urgent?
- [ ] Give an example of a time you made a decision with incomplete information.
- [ ] Tell me about a time you had to convince stakeholders to accept uncertainty.

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Initial response | "I waited for clearer requirements" | "I identified the top three unknowns and designed experiments to resolve them" |
| Assumptions | Implicit or unstated | "I explicitly assumed X, validated it with Y, and adjusted when Z" |
| Communication | "I told them it was hard to say" | "I presented three scenarios with probability estimates and recommended a path" |
| Iteration | Built the whole thing, then discovered it was wrong | "Two-week POC confirmed feasibility before we committed the full team" |

## Key Takeaways
- [ ] Decompose vague objectives into concrete, answerable sub-questions
- [ ] Make assumptions explicit and validate the riskiest ones first
- [ ] Use minimum viable experiments to reduce uncertainty before committing resources
- [ ] Communicate uncertainty with frameworks and data, not vague hedging
- [ ] Show that you create clarity for your team, not just tolerate ambiguity
"""

CONTENT["pillar8.common_questions.failure_learning"] = r"""# Failure & Learning

## Overview
Failure stories are among the most revealing behavioral questions in senior MLE interviews. Every experienced engineer has failures; what distinguishes strong candidates is how they respond to failure -- their self-awareness, accountability, systematic root cause analysis, and ability to implement lasting improvements. Interviewers use these questions to assess maturity, resilience, and growth mindset.

## Core Concepts

### Why Interviewers Ask About Failure
Failure questions test multiple dimensions simultaneously:
- **Self-awareness**: Can you identify your own role in a failure, or do you externalize blame?
- **Accountability**: Do you own the outcome, even when external factors contributed?
- **Analytical rigor**: Do you conduct structured root cause analysis or rely on surface-level explanations?
- **Growth**: Did the failure lead to concrete, lasting improvements?
- **Judgment**: Was the risk reasonable given what you knew at the time?

### Choosing the Right Failure Story
Not all failures are equal for interview purposes:

| Good Failure Story | Poor Failure Story |
|-------------------|-------------------|
| Meaningful stakes (production impact, missed deadline) | Trivial mistake with no consequences |
| You had significant ownership | You were a minor contributor |
| Clear root cause you can articulate | Vague or entirely external cause |
| Led to concrete systemic improvements | Led to no change |
| Demonstrates technical depth | Purely interpersonal or political |

### The Root Cause Analysis Framework
Structure your failure analysis:
1. **What happened**: Factual description of the failure and its impact
2. **Why it happened**: Chain of causes, going at least two levels deep (not just "the test missed it" but "we had no integration tests because we prioritized speed over coverage")
3. **Your role**: What you specifically did or failed to do
4. **Immediate response**: How you contained the damage
5. **Systemic fix**: What you changed to prevent recurrence
6. **Validation**: How you know the fix works

### Framing Failure Constructively
The goal is not to minimize the failure or to be self-flagellating. Show:
- Proportionate accountability (not "it was all my fault" or "it was all their fault")
- Technical depth in understanding the root cause
- Initiative in driving improvements
- Evidence that the lesson stuck

## STAR Templates

### Template 1: Production Model Failure
- **Situation**: Deployed a model update that caused a 15% drop in conversion rate due to a feature distribution shift you did not detect in offline evaluation.
- **Task**: Diagnose the issue, restore service quality, and prevent recurrence.
- **Action**: Identified the root cause within 4 hours (a feature's distribution in the serving path diverged from training data due to a logging change). Rolled back to the previous model version. Conducted a post-mortem with the team. Implemented three systemic changes: (1) distribution drift monitoring on all input features, (2) a mandatory shadow-scoring period before full deployment, (3) automated rollback triggers based on real-time metric degradation.
- **Result**: Service restored within 6 hours. The monitoring system caught two similar issues in the next quarter before they reached production. Post-mortem process adopted team-wide.

### Template 2: Underestimating Project Complexity
- **Situation**: Estimated a model migration would take 4 weeks; it took 12 weeks and required descoping features.
- **Task**: Deliver the migration while managing stakeholder expectations and identifying what went wrong in the estimate.
- **Action**: After week 4, recognized the estimate was wrong and immediately communicated the revised timeline with a clear explanation. Identified three causes: (1) underestimated data migration complexity, (2) did not account for downstream consumer changes, (3) assumed a library compatibility that did not hold. Proposed a phased delivery plan to ship core functionality first. After completion, documented an estimation checklist that included data migration, downstream dependencies, and library compatibility verification.
- **Result**: Core functionality shipped in week 8; full migration in week 12. The estimation checklist reduced estimation errors by approximately 40% on subsequent projects (based on planned-vs-actual tracking).

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Direct failure | "Tell me about your biggest professional failure." | Choose a meaningful failure with a strong learning arc |
| Mistake | "Describe a time you made a mistake that affected your team." | Show accountability and systemic response |
| Missed goal | "Tell me about a time you did not meet a deadline or target." | Emphasize communication and recovery, not excuses |
| Risk assessment | "Describe a time you took a risk that did not pay off." | Show the risk was calculated and the learning was valuable |

### Common Interview Questions
- [ ] Tell me about a time you failed. What did you learn?
- [ ] Describe a production incident you were responsible for.
- [ ] What is the biggest mistake you have made in your career?
- [ ] Tell me about a project that did not go as planned.
- [ ] Describe a time you received critical feedback. How did you respond?

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Accountability | "The data team gave us bad data" | "I should have validated the data pipeline before training; I assumed consistency without checking" |
| Depth | "The model did not work" | "The model failed because feature X had a 30% distribution shift between offline evaluation and production serving" |
| Response | "We fixed it" | "I implemented automated drift detection, shadow scoring, and rollback triggers" |
| Learning | "I learned to be more careful" | "I created a deployment checklist that the team still uses; it has caught 3 similar issues since" |
| Proportionality | Excessively self-blaming or excessively deflecting | Balanced: acknowledges own role while noting systemic factors |

## Key Takeaways
- [ ] Choose failures with real stakes where you had meaningful ownership
- [ ] Go at least two levels deep on root cause analysis
- [ ] Show immediate damage control AND lasting systemic improvements
- [ ] Demonstrate proportionate accountability -- neither deflecting nor excessively self-blaming
- [ ] Quantify the impact of both the failure and the improvements that followed
"""

CONTENT["pillar8.common_questions.impact"] = r"""# Impact Stories

## Overview
Impact questions are the backbone of senior MLE interviews. Every behavioral round includes some form of "Tell me about your most impactful project." These questions assess your ability to identify high-leverage opportunities, execute on them, and articulate the value you created in concrete, measurable terms. The strength of your impact stories often determines the hiring committee's confidence in your seniority level.

## Core Concepts

### The Impact Hierarchy
Not all impact is equal. Structure your stories to show the highest level of impact you genuinely drove:

| Impact Level | Example | Signal |
|-------------|---------|--------|
| Task execution | "I trained a model that achieved X accuracy" | IC-level |
| System improvement | "I redesigned the pipeline, reducing latency by 50%" | Senior IC |
| Team enablement | "I built a framework that let 5 teams deploy models 3x faster" | Staff-level |
| Org-level change | "I established the ML platform strategy that serves 20 teams" | Principal-level |

### Quantification Discipline
Vague impact claims are the most common weakness in behavioral interviews. Every impact story needs numbers:
- Revenue or cost: "$X in incremental revenue", "reduced compute cost by $Y/month"
- Scale: "serving 10M requests/day", "processing 500GB daily"
- Efficiency: "reduced model deployment time from 2 weeks to 2 hours"
- Quality: "improved precision from 72% to 89%", "reduced false positive rate by 60%"
- Scope: "adopted by 5 teams across 3 organizations"

If you do not have exact numbers, use reasonable estimates with clear methodology: "Based on A/B test results showing X% lift on Y metric, across Z users, the estimated annualized impact was approximately $N."

### Attribution Clarity
Senior MLE interviews require you to clearly distinguish your contributions from the team's work. This is not about taking sole credit -- it is about showing what you specifically drove vs. what was a team effort:
- "I designed the architecture and led the implementation; two other engineers built the data pipeline and monitoring"
- "I identified the opportunity through exploratory analysis, proposed the project, and drove the technical execution"
- "This was a team effort; my specific contributions were X, Y, and Z"

### Connecting Technical Work to Business Outcomes
The strongest impact stories draw a clear line from technical decisions to business results:
- "I chose to use a two-tower retrieval model instead of a single-tower approach because it allowed us to pre-compute item embeddings, reducing serving latency from 200ms to 15ms, which improved conversion rate by 3%."
- "I implemented online learning for the fraud model, reducing detection delay from 24 hours to 15 minutes, which prevented an estimated $2M in annual fraud losses."

## STAR Templates

### Template 1: High-Impact Model Improvement
- **Situation**: The recommendation system had not been updated in 18 months and engagement metrics had plateaued.
- **Task**: Identify the highest-leverage improvement opportunity and deliver measurable business impact.
- **Action**: Analyzed failure modes in the existing system and identified that cold-start users (40% of traffic) received poor recommendations. Designed a hybrid model combining collaborative filtering for warm users with a content-based approach for cold-start users. Built an A/B testing framework to measure impact rigorously. Coordinated with the product team to define success criteria before launch.
- **Result**: 8% improvement in engagement for cold-start users, 3% overall engagement lift. Estimated $4M annualized revenue impact based on engagement-to-revenue correlation. Approach was extended to two other product surfaces.

### Template 2: Infrastructure Impact
- **Situation**: ML teams spent 40% of engineering time on deployment and operational tasks instead of model development.
- **Task**: Build shared infrastructure to reduce operational overhead across all ML teams.
- **Action**: Interviewed 8 ML teams to identify common pain points. Designed and built a model serving framework with automated canary deployment, rollback, and monitoring. Created self-service onboarding documentation and ran hands-on workshops for each team.
- **Result**: Reduced model deployment time from an average of 10 days to 4 hours. Freed up approximately 2,500 engineering hours per quarter across the org. Five teams migrated within the first quarter.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Greatest hit | "What is your most impactful project?" | Choose the story with the clearest quantified business outcome |
| Technical depth | "Walk me through a technical decision that drove significant impact." | Show the causal chain from technical choice to business result |
| Scope | "Tell me about something you built that others use." | Emphasize breadth of adoption and enablement |
| Initiative | "Describe a time you identified an opportunity nobody else saw." | Show proactive problem identification, not just execution |

### Common Interview Questions
- [ ] Tell me about your most impactful project in the last two years.
- [ ] Describe a time you significantly improved an ML system.
- [ ] What is the most valuable thing you have built?
- [ ] Tell me about a time you went above and beyond your core responsibilities.
- [ ] How do you decide what to work on to maximize impact?

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Metrics | "The model was very accurate" | "Improved precision from 72% to 89%, reducing false alerts by 60% and saving the ops team 15 hours/week" |
| Attribution | "We built a great system" | "I designed the architecture and led the implementation; I also identified the original opportunity through exploratory analysis" |
| Business link | "The model performed well in offline evaluation" | "The A/B test showed a 3% conversion lift, translating to approximately $4M annualized revenue" |
| Scope | "I improved my team's model" | "I built a reusable framework that 5 teams adopted, collectively improving their deployment velocity by 3x" |

## Key Takeaways
- [ ] Every impact story must have concrete, quantified outcomes
- [ ] Draw a clear causal chain from your technical decisions to business results
- [ ] Be explicit about your individual contribution vs. the team's work
- [ ] Show the highest level of impact appropriate to your target seniority
- [ ] Include how you identified the opportunity, not just how you executed
"""

CONTENT["pillar8.common_questions.mentorship"] = r"""# Mentorship

## Overview
Mentorship questions assess a senior MLE's ability to develop others and multiply their impact through people, not just code. At the senior level and above, interviewers expect you to have actively helped others grow -- whether through formal mentorship, code reviews, onboarding, or creating learning resources. These stories demonstrate that you can scale your impact beyond your individual output.

## Core Concepts

### Mentorship vs. Management
Mentorship is influence without authority applied to someone's professional growth. Unlike management, it does not come with reporting authority, performance reviews, or hiring/firing decisions. This distinction matters in interviews:

| Aspect | Mentorship | Management |
|--------|-----------|------------|
| Authority | None -- influence-based | Direct reporting line |
| Focus | Long-term growth and skills | Short-term delivery and performance |
| Structure | Flexible, mentee-driven | Regular 1:1s, formal reviews |
| Success metric | Mentee's independence and capability growth | Team output and goal attainment |

### Effective Mentorship Patterns for MLEs
- **Code review as teaching**: Using reviews not just to catch bugs but to explain design principles, suggest better patterns, and share context about why decisions were made
- **Pairing on hard problems**: Working through debugging sessions, design decisions, or unfamiliar codebases together rather than just providing the answer
- **Structured onboarding**: Creating onboarding plans, starter tasks of graduated difficulty, and documentation that helps new team members become productive faster
- **Stretch assignments**: Identifying opportunities for mentees to grow by taking on challenges slightly beyond their current level, with your guidance as a safety net
- **Knowledge sharing**: Writing design docs, running tech talks, or creating internal courses that benefit the broader team

### Measuring Mentorship Impact
Interviewers want to see that your mentorship produced measurable results:
- Mentee promoted or took on significantly more responsibility
- Mentee became independent in an area where they previously needed heavy guidance
- Onboarding time reduced for new team members
- Team velocity or code quality improved as a result of your teaching
- Knowledge sharing led to wider adoption of best practices

### Common Mentorship Challenges
- Mentee who is resistant to feedback
- Balancing mentorship time with your own deliverables
- Mentee who wants answers rather than guidance
- Mentoring across skill gaps (e.g., ML for a software engineer, or systems for a data scientist)

## STAR Templates

### Template 1: Developing a Junior MLE
- **Situation**: A junior engineer joined the team with strong software engineering skills but no ML experience. The team needed them to contribute to model development within 3 months.
- **Task**: Accelerate the junior engineer's growth in ML while maintaining your own project commitments.
- **Action**: Created a structured 12-week onboarding plan with weekly milestones. Started with pair programming on model evaluation scripts, graduated to independent feature engineering tasks, then to owning a small model improvement end-to-end. Held weekly 30-minute 1:1s focused on their growth goals. Used code reviews as teaching moments, always explaining the "why" behind suggestions. Identified a starter project (improving data validation for the training pipeline) that was valuable to the team and appropriate for their skill level.
- **Result**: Within 3 months, the engineer independently shipped a feature engineering improvement that lifted model accuracy by 2%. Within 6 months, they owned a full model refresh project. They were promoted to MLE II within a year. The onboarding plan was adopted as the team standard for all new ML hires.

### Template 2: Scaling Knowledge Through Documentation and Teaching
- **Situation**: The team's ML deployment process was tribal knowledge held by two senior engineers. New team members took 4-6 weeks to learn the deployment process, and mistakes were common.
- **Task**: Make the deployment process accessible and reduce onboarding friction.
- **Action**: Documented the complete deployment process with step-by-step guides and common pitfalls. Created a "deployment dojo" -- a series of three hands-on workshops where engineers practiced deploying a toy model through the full pipeline. Built automated checks that caught common mistakes before they reached production. Established a buddy system where each new engineer was paired with an experienced deployer for their first two deployments.
- **Result**: Onboarding time for the deployment process dropped from 4-6 weeks to 1 week. Deployment errors by new team members decreased by 80%. The workshop format was adopted by two other teams.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Direct mentorship | "Tell me about a time you mentored someone." | Show structured approach and measurable growth |
| Teaching | "How do you help others learn new skills?" | Demonstrate patience, graduated difficulty, and empowerment |
| Scaling | "How do you share knowledge across your team?" | Show systems and processes, not just 1:1 effort |
| Challenge | "Tell me about a difficult mentorship situation." | Show adaptability and persistence |

### Common Interview Questions
- [ ] Describe a time you helped someone grow in their career.
- [ ] How do you onboard new team members?
- [ ] Tell me about a time you gave difficult feedback.
- [ ] How do you balance mentoring others with your own work?
- [ ] Describe a time someone you mentored exceeded your expectations.

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Approach | "I answered their questions when they asked" | "I created a structured onboarding plan with weekly milestones and regular check-ins" |
| Focus | "I told them what to do" | "I guided them to discover the solution through targeted questions and pair programming" |
| Impact | "They seemed more confident" | "They independently shipped a model improvement within 3 months and were promoted within a year" |
| Scale | "I helped one person" | "I created onboarding materials and workshops that the whole team now uses" |

## Key Takeaways
- [ ] Show structured, intentional mentorship -- not just ad-hoc help
- [ ] Quantify mentorship outcomes: promotions, independence gained, onboarding time reduced
- [ ] Demonstrate that you empower others rather than create dependence
- [ ] Include examples of scaling your knowledge through documentation, workshops, or processes
- [ ] Show how you balanced mentorship responsibilities with your own technical deliverables
"""

CONTENT["pillar8.common_questions.cross_functional"] = r"""# Cross-functional Collaboration

## Overview
ML projects are inherently cross-functional. A recommendation model touches product management (what to optimize), data engineering (feature pipelines), backend engineering (serving infrastructure), design (how results are presented), and business teams (success metrics). Senior MLE interviews assess your ability to work effectively across these boundaries -- translating between technical and non-technical contexts, aligning diverse stakeholders, and delivering integrated solutions.

## Core Concepts

### The MLE as a Bridge
Senior MLEs often serve as the translation layer between technical and business teams. This requires:
- **Technical-to-business translation**: Explaining model behavior, uncertainty, and limitations in terms stakeholders can act on
- **Business-to-technical translation**: Converting product requirements into concrete ML problem formulations
- **Cross-team coordination**: Aligning timelines, interfaces, and dependencies across data, platform, and product teams

### Common Cross-Functional Interfaces for MLEs

| Partner Team | What They Need From You | What You Need From Them |
|-------------|----------------------|------------------------|
| Product Management | Model capabilities, timelines, tradeoffs | Clear success metrics, user context, prioritization |
| Data Engineering | Feature requirements, SLAs, data contracts | Reliable data pipelines, schema stability |
| Backend Engineering | Model serving requirements, latency budgets | Serving infrastructure, API contracts |
| Design/UX | Explanation of model outputs, confidence scores | User research on how recommendations are perceived |
| Business/Analytics | Model performance reports, A/B test results | Business context, revenue attribution |

### Communication Strategies
- **Shared artifacts**: Design docs, data contracts, and API specifications that create a single source of truth across teams
- **Regular syncs**: Cross-team standups or weekly syncs for projects with active dependencies
- **Demos over documents**: Showing working prototypes is more effective than written descriptions for non-technical stakeholders
- **Explicit tradeoff framing**: "We can have X or Y but not both; here is the data to help decide" is more productive than "we need more time"

### Managing Cross-Team Dependencies
ML projects often sit on the critical path of multiple teams' deliverables. Effective dependency management includes:
- Identifying dependencies early and building buffer into timelines
- Creating clear interface contracts (API schemas, data formats, SLAs) before implementation begins
- Having fallback plans when dependencies slip
- Over-communicating status changes, especially delays

## STAR Templates

### Template 1: End-to-End ML Feature Launch
- **Situation**: Launching a new ML-powered feature required coordination across ML, backend, frontend, product, and data teams -- five teams total with different priorities and timelines.
- **Task**: Serve as the technical lead coordinating the ML aspects across all teams to deliver the feature on schedule.
- **Action**: Created a shared project tracker with clear milestones and owners for each team. Defined interface contracts (API schemas, data formats) upfront in a joint design review. Established a weekly cross-team sync to surface blockers early. When the data team's pipeline was delayed by two weeks, proposed an interim solution using cached features that allowed ML development to continue. Ran a joint demo at each milestone to keep all teams aligned on progress and remaining work.
- **Result**: Feature launched on time despite the data pipeline delay. The cross-team coordination template (project tracker, interface contracts, weekly sync) was adopted as the standard process for cross-functional ML launches.

### Template 2: Aligning ML and Product on Metrics
- **Situation**: The product team measured success by click-through rate while the ML team optimized for engagement time. This misalignment caused confusion in A/B test interpretation and conflicting priorities.
- **Task**: Align both teams on a unified success metric and measurement framework.
- **Action**: Analyzed the correlation between CTR and engagement time across user segments. Found that CTR optimization led to clickbait-style results that hurt long-term engagement. Proposed a composite metric that weighted both short-term clicks and 7-day retention. Built a dashboard that showed both metrics side by side for every experiment. Facilitated a workshop where product and ML teams jointly defined the new metric and its thresholds.
- **Result**: Teams adopted the composite metric. Model improvements that scored well on the composite metric showed a 15% improvement in 30-day retention compared to CTR-only optimization. The metric definition process was adopted by three other product areas.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Coordination | "Tell me about a project involving multiple teams." | Show how you created alignment and managed dependencies |
| Translation | "How do you explain ML concepts to non-technical stakeholders?" | Demonstrate clarity without condescension |
| Dependency | "Describe a time a dependency from another team was delayed." | Show proactive mitigation, not just waiting |
| Alignment | "Tell me about a time teams had conflicting goals." | Demonstrate finding shared objectives |

### Common Interview Questions
- [ ] Describe a project where you worked closely with non-ML teams.
- [ ] How do you communicate model limitations to product managers?
- [ ] Tell me about a time you had to align multiple stakeholders with different priorities.
- [ ] Describe a cross-team dependency that became a risk. How did you handle it?
- [ ] How do you ensure that ML and product teams are measuring success the same way?

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Scope | "I built the model and handed it off" | "I coordinated across 5 teams, defining interfaces and managing dependencies end-to-end" |
| Communication | "I explained the technical details" | "I translated model behavior into product implications using demos and shared dashboards" |
| Dependencies | "The other team was late so we were late" | "When the dependency slipped, I proposed an interim solution that kept us on track" |
| Alignment | "Everyone agreed eventually" | "I facilitated a joint workshop where we defined shared metrics and success criteria" |

## Key Takeaways
- [ ] Position yourself as the bridge between technical and business teams
- [ ] Show that you proactively manage dependencies rather than passively waiting
- [ ] Demonstrate communication strategies tailored to different audiences
- [ ] Include examples of creating shared artifacts (design docs, dashboards, contracts) that aligned teams
- [ ] Quantify the coordination outcomes, not just the technical outcomes
"""

CONTENT["pillar8.common_questions.prioritization"] = r"""# Prioritization

## Overview
Prioritization is a defining skill for senior MLEs. With more potential projects than available time, interviewers want to see that you can systematically evaluate opportunities, make defensible tradeoff decisions, and say "no" to good ideas in favor of great ones. This is especially challenging in ML, where the expected value of a project is often uncertain until significant exploration has been done.

## Core Concepts

### Prioritization Frameworks for ML Work

**Impact vs. Effort Matrix**

| | Low Effort | High Effort |
|--|-----------|-------------|
| **High Impact** | Do first (quick wins) | Plan and invest (strategic bets) |
| **Low Impact** | Do if time permits (nice to have) | Avoid (resource traps) |

**ICE Scoring (Impact, Confidence, Ease)**
- Impact: How much will this move the target metric?
- Confidence: How sure are you about the expected impact?
- Ease: How much effort is required to deliver?
- Score = Impact x Confidence x Ease (each rated 1-10)

**RICE Scoring (Reach, Impact, Confidence, Effort)**
Similar to ICE but adds Reach -- how many users or use cases does this affect? Useful for platform and infrastructure work.

### ML-Specific Prioritization Challenges
- **Uncertain returns**: Unlike product features, ML improvements often have unknown payoff until experimentation is done. You must decide how much to invest in exploration vs. exploitation.
- **Compounding infrastructure debt**: Skipping monitoring, testing, or pipeline improvements saves time now but compounds into production incidents later.
- **Research vs. engineering tradeoffs**: Should you explore a novel architecture or optimize the existing system? The answer depends on where you are on the diminishing returns curve.
- **Urgent vs. important**: Production model drift demands immediate attention but may crowd out higher-value long-term projects.

### The Portfolio Approach
Senior MLEs manage their work as a portfolio:
- **70% high-confidence incremental improvements**: Feature engineering, hyperparameter tuning, data quality fixes with predictable returns
- **20% medium-confidence architectural changes**: Model architecture upgrades, pipeline redesigns with estimated but uncertain returns
- **10% exploratory bets**: Novel approaches, research-inspired ideas with high potential but low certainty

### Saying No Effectively
A critical prioritization skill is declining work without damaging relationships:
- "This is a great idea, but given our current priorities, it would delay X by Y weeks. Can we revisit next quarter?"
- "I can do a lightweight version of this in Z days. Would that meet your immediate need?"
- "Let me show you the current priority stack. Where would you rank this relative to the existing commitments?"

## STAR Templates

### Template 1: Reprioritizing After a Production Incident
- **Situation**: Your team had a full roadmap of model improvements when a production model started showing significant accuracy degradation due to data drift. At the same time, a partner team was waiting on a feature you had committed to delivering.
- **Task**: Decide how to allocate the team's limited capacity across the incident, the committed feature, and the planned roadmap.
- **Action**: Assessed the production impact (estimated revenue loss per day from the drift). Evaluated the partner team's timeline flexibility. Made the call to: (1) assign yourself and one engineer to the production issue (highest urgency), (2) communicate a one-week delay to the partner team with a clear explanation and revised timeline, (3) pause the lowest-priority roadmap item to create capacity. Documented the decision rationale and shared it with all stakeholders within two hours of the incident.
- **Result**: Production issue resolved in 3 days, limiting revenue impact to approximately $50K vs. the estimated $200K if left unaddressed for the original planned fix date. Partner team feature delivered one week late but with full quality. The prioritization framework used for the decision was adopted as a team playbook for future incidents.

### Template 2: Choosing Between ML Projects
- **Situation**: Had three potential projects for the quarter: (A) retraining the core ranking model with new features (estimated +2% revenue, high confidence), (B) building a new personalization system for a growing user segment (estimated +5% revenue, low confidence), (C) migrating the serving infrastructure to reduce costs by 30%.
- **Task**: Recommend and justify the optimal allocation of a 4-person team for the quarter.
- **Action**: Built a quantified comparison using ICE scoring. Estimated the expected value of each project accounting for uncertainty. Proposed splitting the team: 2 engineers on project A (high confidence, ships in 6 weeks), 1 engineer on a 3-week spike for project B to validate the feasibility estimate, and 1 engineer on project C (independent workstream with guaranteed savings). Presented the analysis to leadership with clear decision criteria and contingency plans.
- **Result**: Project A delivered +2.3% revenue lift. The Project B spike showed the personalization system was feasible but needed a different data source than initially assumed -- saving the team from a potentially wasted full-quarter investment. Project C delivered 28% cost reduction. Total quarter impact exceeded what any single project would have delivered.

## Interview Patterns

| Question Type | Example Question | Key Insight |
|--------------|-----------------|-------------|
| Tradeoffs | "How do you decide what to work on?" | Show a systematic framework, not just intuition |
| Saying no | "Tell me about a time you had to decline a request." | Demonstrate diplomacy and alternative solutions |
| Urgency | "How do you handle competing urgent requests?" | Show rapid triage with clear criteria |
| Strategic | "How do you balance short-term wins vs. long-term investments?" | Demonstrate portfolio thinking |

### Common Interview Questions
- [ ] How do you prioritize when you have more work than capacity?
- [ ] Tell me about a time you had to choose between two important projects.
- [ ] Describe a time you said no to a stakeholder request. How did you handle it?
- [ ] How do you decide when to invest in infrastructure vs. features?
- [ ] Tell me about a time you reprioritized your work based on new information.

## Comparisons

| Aspect | Weak Answer | Strong Answer |
|--------|------------|---------------|
| Framework | "I worked on what seemed most important" | "I scored each project on impact, confidence, and effort, then presented the analysis to stakeholders" |
| Saying no | "I told them we could not do it" | "I explained the tradeoff, offered a lightweight alternative, and proposed revisiting next quarter" |
| Adaptability | "I stuck to the original plan" | "When the production incident hit, I reassessed priorities within 2 hours and communicated revised timelines to all stakeholders" |
| Scope | "I focused on my own work" | "I prioritized across the team's full portfolio, balancing incremental wins, strategic bets, and infrastructure investments" |

## Key Takeaways
- [ ] Use a structured prioritization framework (ICE, RICE, impact/effort matrix) rather than intuition alone
- [ ] Show that you consider uncertainty and confidence, not just expected impact
- [ ] Demonstrate the ability to say no diplomatically while offering alternatives
- [ ] Include examples of adapting priorities in response to new information
- [ ] Frame prioritization as a team and portfolio problem, not just a personal task list
"""

# ===== STAR FRAMEWORK =====

CONTENT["pillar8.star_framework"] = r"""# STAR Framework & Quantification

## Overview
The STAR framework (Situation, Task, Action, Result) is the universal structure for behavioral interview answers. For senior MLE candidates, mastering STAR is not just about telling coherent stories -- it is about calibrating depth, quantifying impact precisely, and demonstrating the seniority signals that hiring committees look for. This guide covers both the mechanics of STAR and the quantification discipline that separates strong from average answers.

## Core Concepts

### The STAR Structure

| Component | Purpose | Time Allocation | Common Mistake |
|-----------|---------|----------------|----------------|
| Situation | Set context; establish stakes | 15-20% of answer | Too long; irrelevant details |
| Task | Clarify YOUR responsibility | 10-15% of answer | Confusing team's task with your task |
| Action | Show what YOU did and how | 40-50% of answer | Too vague; listing activities without depth |
| Result | Prove impact with evidence | 20-25% of answer | No quantification; vague "it went well" |

### Situation: Setting the Stage
Keep it concise. Include only what the interviewer needs to understand the challenge:
- Company context (scale, domain) if relevant
- The specific problem or opportunity
- Why it mattered (stakes)
- Timeline constraints if applicable

Bad: "So at my company, which is a mid-size e-commerce startup founded in 2018, we have about 200 engineers and our ML team was formed in 2020..." (too much irrelevant context)

Good: "Our recommendation system served 10M daily active users but had not been updated in 18 months. Engagement metrics had plateaued and the VP of Product flagged it as a top-3 priority for Q3." (concise, establishes scale and stakes)

### Task: Clarifying Your Role
This is where many candidates fail. Clearly separate your responsibility from the team's:
- "I was the technical lead responsible for..."
- "My specific role was to..."
- "I owned the decision on..."

Avoid: "We needed to..." (ambiguous ownership)

### Action: The Core of Your Answer
This should be the longest section. Include:
- Your reasoning process (why you chose this approach)
- Technical depth appropriate to the audience
- How you handled obstacles or pivots
- How you involved or influenced others

Structure complex actions chronologically or by theme:
"First, I... Then, I... When [obstacle] arose, I..."

### Result: Quantified Impact
Every result should include numbers. If you do not have exact metrics, estimate responsibly:
- "Based on the A/B test, the model improvement drove a 3% lift in conversion, which translated to approximately $2M annualized revenue."
- "Deployment time dropped from 2 weeks to 4 hours -- measured across the 5 teams that adopted the framework."
- "The oncall incident rate decreased from 3 per week to 1 per month after the monitoring system was in place."

### Quantification Strategies

| Type of Impact | How to Quantify | Example |
|---------------|----------------|---------|
| Revenue | A/B test lift x user base x revenue/user | "+3% conversion = ~$2M/year" |
| Efficiency | Time saved x frequency x people affected | "2 hours saved per deploy x 50 deploys/quarter x 5 teams" |
| Quality | Error rate reduction, precision/recall improvement | "False positive rate dropped from 12% to 3%" |
| Scale | Requests served, data processed, users affected | "Serving 10M predictions/day at p99 latency of 50ms" |
| Reliability | Incident reduction, uptime improvement | "Reduced production incidents from 3/week to 1/month" |
| Adoption | Teams onboarded, engineers using the tool | "Adopted by 8 teams; 40 engineers use it weekly" |

### When You Do Not Have Exact Numbers
Use estimation with transparency:
- "I do not have the exact revenue figure, but based on the 5% engagement lift across 2M users, the estimated impact was in the range of $500K-$1M annually."
- "While I cannot share the exact metrics due to confidentiality, the improvement was in the range of a double-digit percentage lift in the target metric."

## STAR Templates

### Template 1: Model Performance Improvement
- **Situation**: [Scale of system, current performance, business context] -- keep to 2-3 sentences
- **Task**: [Your specific ownership] -- 1 sentence
- **Action**: [Analysis of the problem] -> [Technical approach with reasoning] -> [Implementation details] -> [How you handled obstacles] -- 4-6 sentences
- **Result**: [Metric improvement with numbers] -> [Business impact] -> [Broader adoption or lasting change] -- 2-3 sentences

### Template 2: Infrastructure or Platform Story
- **Situation**: [Pain point, who was affected, scale of the problem]
- **Task**: [Your ownership of the solution]
- **Action**: [Requirements gathering] -> [Design decisions with tradeoffs] -> [Implementation and rollout strategy] -> [Stakeholder management]
- **Result**: [Efficiency gains with numbers] -> [Adoption metrics] -> [Ongoing impact]

## Interview Patterns

| Question Type | STAR Emphasis | Timing Target |
|--------------|--------------|---------------|
| "Tell me about a time..." | Full STAR | 3-5 minutes |
| "What is your biggest accomplishment?" | Heavy on Result quantification | 4-5 minutes |
| "Describe a challenge..." | Heavy on Action (problem-solving process) | 3-4 minutes |
| "How did you handle..." | Heavy on Action (interpersonal approach) | 2-3 minutes |
| Follow-up: "What would you do differently?" | Reflection beyond STAR | 1 minute |

### Common Interview Questions
- [ ] Walk me through a project you are most proud of.
- [ ] Tell me about a time you had to make a difficult technical decision.
- [ ] Describe a situation where you had to influence others.
- [ ] Give an example of a time you dealt with ambiguity.
- [ ] Tell me about a time something went wrong. What did you do?

## Comparisons

| Aspect | Weak STAR | Strong STAR |
|--------|----------|-------------|
| Situation | 2 minutes of background | 30 seconds of relevant context |
| Task | "We needed to improve the model" | "I owned the technical direction for the ranking model refresh" |
| Action | "I trained a new model" | "I analyzed failure modes, identified cold-start as the key gap, designed a hybrid architecture, and ran a rigorous A/B test" |
| Result | "It worked better" | "8% engagement lift for cold-start users, ~$4M annualized revenue, approach adopted by 2 other teams" |
| Timing | 8+ minutes, meandering | 3-4 minutes, structured |

## Key Takeaways
- [ ] Spend 40-50% of your answer on Action -- this is where seniority signals live
- [ ] Every Result must include at least one concrete number
- [ ] Clearly separate your contribution from the team's work in the Task section
- [ ] Keep Situation concise -- only include context the interviewer needs to understand the challenge
- [ ] Prepare 5-7 STAR stories that cover different competencies and can be adapted to various questions
- [ ] Practice timing: a strong STAR answer takes 3-5 minutes, not 8-10
"""

# ===== COMPANY-SPECIFIC BEHAVIORAL =====

CONTENT["pillar8.company_specific.google"] = r"""# Google (Googleyness)

## Overview
Google's behavioral interviews evaluate "Googleyness" -- a set of cultural attributes that predict success at Google beyond raw technical ability. For senior MLE candidates, Googleyness questions probe how you navigate ambiguity, collaborate across teams, challenge the status quo constructively, and prioritize user impact. Understanding what Google specifically looks for allows you to select and frame your stories for maximum alignment.

## Core Concepts

### What is Googleyness?
Googleyness is Google's shorthand for cultural fit and behavioral competencies. While the exact rubric evolves, the core dimensions assessed in interviews are:

| Dimension | What Google Looks For | MLE Signal |
|-----------|---------------------|------------|
| Doing the right thing | Ethical decision-making, user-first thinking | Considering fairness, bias, and user impact in model design |
| Thriving in ambiguity | Comfort with undefined problems, iterative approach | Scoping ML problems, designing experiments under uncertainty |
| Valuing feedback | Seeking and incorporating feedback, intellectual humility | Iterating on models based on review feedback, updating assumptions |
| Challenging the status quo | Questioning existing approaches constructively | Proposing better architectures, identifying technical debt |
| Working collaboratively | Effective cross-functional partnerships | Working with product, data, and platform teams |
| Putting the user first | Decisions anchored in user impact | Optimizing for user experience, not just model metrics |

### Google's Leadership Competencies for Senior Roles
At L5+ (senior), Google also evaluates:
- **Cognitive ability**: Structured problem-solving, learning from experience
- **Leadership**: Emergent leadership, driving direction without formal authority
- **Role-related knowledge**: Deep ML expertise applied in practical contexts

### How Googleyness Is Evaluated
Each interviewer in Google's behavioral round scores on specific Googleyness dimensions. The hiring committee reviews these scores alongside technical assessments. A strong Googleyness signal can compensate for a borderline technical performance; a weak signal is a red flag even with strong technical skills.

## STAR Templates

### Template 1: Challenging the Status Quo
- **Situation**: Your team had been using a rule-based system for content moderation that required constant manual tuning. Everyone accepted it as "good enough" because it had been in place for years.
- **Task**: You believed an ML approach would be significantly better but needed to convince the team to invest in the migration.
- **Action**: Built a proof-of-concept ML model on a weekend using existing labeled data from the rule system's audit logs. The POC showed 30% higher precision at the same recall level. Presented the results in a team meeting with a clear migration plan that minimized risk (shadow mode first, gradual rollover). Addressed concerns about model interpretability by adding explanation features.
- **Result**: Team approved the migration. Production ML system reduced manual moderation workload by 60% while improving precision by 25%. The approach of using existing rule audit logs as training data was adopted by two other safety teams.

### Template 2: Putting the User First
- **Situation**: The ranking model optimization was showing strong offline metrics improvements, but user research revealed that the optimized results felt "samey" -- users were seeing less diverse content.
- **Task**: Balance model metric optimization with user experience quality.
- **Action**: Proposed and implemented a diversity-aware reranking layer that ensured content variety while preserving relevance. Designed an A/B test that measured both engagement metrics and a new diversity score. Collaborated with UX researchers to define what "good diversity" meant for different user segments. Ran the experiment for 4 weeks to capture long-term engagement effects.
- **Result**: The diversity-aware model showed a slight engagement dip in week 1 but a 7% improvement in 4-week retention. This became the default approach for all ranking models, with the explicit principle: "optimize for long-term user value, not short-term engagement."

## Interview Patterns

| Googleyness Dimension | Example Question | What They Want to Hear |
|----------------------|-----------------|----------------------|
| Ambiguity | "Tell me about a time you navigated an unclear situation." | Structured decomposition, iterative progress |
| Feedback | "Describe a time you received tough feedback. How did you respond?" | Openness, concrete changes made |
| Challenge status quo | "Tell me about a time you improved a process or system." | Initiative, data-driven proposal, measured impact |
| Collaboration | "Describe your most effective cross-team project." | Inclusive approach, shared credit, joint success |
| User focus | "Tell me about a decision where you prioritized user impact over other metrics." | Willingness to make harder choices for users |
| Ethics | "Describe a time you raised a concern about a technical approach." | Courage to speak up, constructive framing |

### Common Interview Questions
- [ ] Tell me about a time you went beyond your job description to improve something.
- [ ] Describe a situation where you had to balance multiple stakeholders' needs.
- [ ] How do you handle disagreements with teammates?
- [ ] Tell me about a time you advocated for the user when it was not the easy path.
- [ ] Describe a time you took initiative on something that was not assigned to you.
- [ ] How do you approach learning something completely new?

## Comparisons

| Aspect | Does Not Show Googleyness | Shows Googleyness |
|--------|--------------------------|-------------------|
| Initiative | "I was assigned to improve the model" | "I noticed the model had a fairness gap and proposed a project to address it" |
| Feedback | "I disagreed with the review comments" | "The review highlighted a blind spot in my approach; I redesigned the evaluation to address it" |
| User focus | "We optimized for CTR as requested" | "I pushed back on pure CTR optimization because user research showed it hurt long-term satisfaction" |
| Collaboration | "I built the model and gave it to the team" | "I paired with the product team on metric definition and with infra on serving requirements" |

## Key Takeaways
- [ ] Google values initiative and constructive dissent -- show times you improved things without being asked
- [ ] Always connect your actions to user impact, even for infrastructure work
- [ ] Demonstrate intellectual humility -- show how feedback changed your approach
- [ ] Frame collaboration as genuine partnership, not just coordination
- [ ] Show comfort with ambiguity through structured decomposition, not just tolerance
- [ ] Prepare stories that show ethical reasoning in technical decisions
"""

CONTENT["pillar8.company_specific.amazon_lp"] = r"""# Amazon Leadership Principles

## Overview
Amazon's behavioral interviews are structured entirely around their 16 Leadership Principles (LPs). Every interviewer is assigned specific LPs to evaluate, and they use the STAR method to probe for evidence of each principle. For senior MLE candidates, Amazon expects strong signals on at least 10-12 LPs, with particular emphasis on Ownership, Dive Deep, Bias for Action, and Earn Trust. Understanding the LPs and mapping your MLE experiences to them is essential preparation.

## Core Concepts

### The 16 Leadership Principles

| # | Principle | Core Idea | MLE Application |
|---|-----------|-----------|-----------------|
| 1 | Customer Obsession | Start with customer, work backward | Optimize for user experience, not just model metrics |
| 2 | Ownership | Think long-term, act on behalf of the entire company | Own the full ML lifecycle, not just model training |
| 3 | Invent and Simplify | Seek simplification, expect innovation | Propose simpler model architectures that are easier to maintain |
| 4 | Are Right, A Lot | Strong judgment, seek diverse perspectives | Data-driven technical decisions, openness to being wrong |
| 5 | Learn and Be Curious | Never stop learning | Stay current with ML research, explore new techniques |
| 6 | Hire and Develop the Best | Raise the bar for talent | Mentor junior MLEs, improve hiring processes |
| 7 | Insist on the Highest Standards | Relentlessly high standards | Rigorous model evaluation, production monitoring |
| 8 | Think Big | Create bold vision | Propose transformative ML capabilities, not just incremental improvements |
| 9 | Bias for Action | Speed matters, calculated risk-taking | Ship MVPs quickly, iterate with data |
| 10 | Frugality | Do more with less | Optimize compute costs, use efficient architectures |
| 11 | Earn Trust | Listen, speak candidly, be self-critical | Transparent about model limitations, honest about tradeoffs |
| 12 | Dive Deep | Stay connected to details, audit frequently | Debug production issues at the data level, understand feature distributions |
| 13 | Have Backbone; Disagree and Commit | Challenge respectfully, commit fully | Push back on bad metrics, support team decisions once made |
| 14 | Deliver Results | Focus on key inputs, deliver with quality | Ship models that drive measurable business impact |
| 15 | Strive to be Earth's Best Employer | Work environment, development | Foster inclusive team culture, support growth |
| 16 | Success and Scale Bring Broad Responsibility | Start with customer impact on society | Consider model fairness, environmental impact of training |

### Amazon's Interview Structure
- Typically 4-5 behavioral rounds (1 hour each for senior roles)
- Each interviewer covers 2-3 LPs
- Interviewers use "Tell me about a time when..." questions and drill down with follow-ups
- They score each LP on a bar-raiser scale
- A "bar raiser" interviewer ensures consistent hiring standards across all rounds

### Mapping MLE Stories to LPs
The key to Amazon interviews is having 8-10 strong stories that can each be mapped to 2-3 LPs. For example:

**Story: "Led migration from batch to real-time ML serving"**
- Ownership: Owned the full migration end-to-end
- Bias for Action: Proposed and started the migration when metrics showed the need, without waiting for a mandate
- Dive Deep: Debugged a latency issue that traced to an inefficient feature lookup at the database level
- Deliver Results: Reduced serving latency by 80%, improving user satisfaction scores by 15%
- Frugality: Designed the new system to use spot instances, reducing compute costs by 40%

## STAR Templates

### Template 1: Ownership + Dive Deep + Deliver Results
- **Situation**: Production recommendation model accuracy dropped 5% over two months with no obvious cause.
- **Task**: As the model owner, diagnose and fix the degradation.
- **Action**: (Dive Deep) Analyzed feature distributions over time and found a subtle data drift in user engagement signals caused by a UI change that altered how users interacted with the product. (Ownership) Took responsibility for the full fix -- not just the model retrain but also establishing monitoring for this class of drift. (Deliver Results) Implemented feature drift detection, retrained the model with drift-adjusted features, and deployed within one sprint.
- **Result**: Model accuracy restored and exceeded previous levels by 2%. Drift monitoring caught two similar issues in the following quarter before they impacted production. Total time from detection to fix: 8 days.

### Template 2: Customer Obsession + Have Backbone + Invent and Simplify
- **Situation**: Product team requested a complex deep learning model for a feature with limited training data (10K examples).
- **Task**: Deliver the best solution for the customer, even if it was not what was requested.
- **Action**: (Have Backbone) Presented data showing that a deep learning model would overfit on the available data, with analysis of the learning curve showing no improvement beyond a gradient-boosted model. (Customer Obsession) Framed the argument in terms of customer impact: "Users will get worse recommendations if we overfit." (Invent and Simplify) Proposed a simpler gradient-boosted model with carefully engineered features that could be served at 10x lower latency.
- **Result**: The simpler model outperformed the deep learning prototype by 8% on the held-out set. Serving cost was 90% lower. Product team adopted the "right-size the model" principle for future projects.

## Interview Patterns

| LP | Common Question | What To Emphasize |
|----|----------------|-------------------|
| Customer Obsession | "Tell me about a time you went above and beyond for a customer." | Understanding the real customer need behind the request |
| Ownership | "Tell me about a time you took on something outside your area." | End-to-end responsibility, long-term thinking |
| Bias for Action | "Tell me about a time you made a decision with incomplete data." | Speed of action with calculated risk, not recklessness |
| Dive Deep | "Tell me about a time you found a root cause others missed." | Technical depth, data-level investigation |
| Earn Trust | "Tell me about a time you had to deliver difficult news." | Honesty, transparency about limitations |
| Disagree and Commit | "Tell me about a time you disagreed with your manager." | Respectful challenge with data, full commitment afterward |
| Frugality | "Tell me about a time you did more with less." | Creative resource optimization, not just cost cutting |

### Common Interview Questions
- [ ] Tell me about a time you took ownership of a problem outside your team's scope.
- [ ] Describe a situation where you had to make a quick decision with limited information.
- [ ] Tell me about a time you simplified a complex system.
- [ ] Describe a time you disagreed with a team decision but committed to it anyway.
- [ ] Tell me about a time you failed to meet a deadline. What happened?
- [ ] How have you raised the bar for your team?

## Comparisons

| Aspect | Below the Bar | At/Above the Bar |
|--------|--------------|-----------------|
| Ownership | "That was the data team's responsibility" | "I owned the full pipeline from data ingestion to model serving, including the handoff points" |
| Dive Deep | "The model accuracy dropped so I retrained it" | "I traced the accuracy drop to a 15% distribution shift in feature X caused by a UI change deployed 3 weeks prior" |
| Bias for Action | "I waited for the team to decide" | "I built a prototype over the weekend to validate the approach before the Monday planning meeting" |
| Earn Trust | "The model is performing well" | "The model improved recall by 20% but precision dropped 3% -- here is the tradeoff analysis and my recommendation" |

## Key Takeaways
- [ ] Prepare 8-10 stories that each map to 2-3 LPs, covering at least 12 of the 16 principles
- [ ] For senior roles, emphasize Ownership, Dive Deep, Bias for Action, and Earn Trust
- [ ] Always quantify results -- Amazon is extremely data-driven in evaluation
- [ ] Show end-to-end ownership, not just your slice of the work
- [ ] Practice the "drill-down" -- Amazon interviewers will ask 3-4 follow-up questions on each story
- [ ] Have a failure story ready that shows Earn Trust (honest self-assessment) and Learn and Be Curious (what you improved)
"""

CONTENT["pillar8.company_specific.airbnb_values"] = r"""# Airbnb Core Values

## Overview
Airbnb's behavioral interviews are structured around their core values: Champion the Mission, Be a Host, Embrace the Adventure, and Be a Cereal Entrepreneur. For senior MLE candidates, Airbnb places particular emphasis on mission alignment, intellectual curiosity, and collaborative problem-solving. Understanding Airbnb's unique culture -- which emphasizes belonging, craftsmanship, and cross-functional partnership -- allows you to frame your MLE experiences in the language that resonates with their hiring committees.

## Core Concepts

### Airbnb's Core Values

| Value | Core Idea | MLE Application |
|-------|-----------|-----------------|
| Champion the Mission | Passionate about Airbnb's mission of belonging; put the mission first | Frame ML work in terms of user belonging and host/guest experience |
| Be a Host | Caring, present, making others feel welcome | Collaborative, inclusive team behavior; user empathy in model design |
| Embrace the Adventure | Curious, optimistic, driven by growth | Exploring novel ML approaches, learning from failure, intellectual curiosity |
| Be a Cereal Entrepreneur | Resourceful, creative, scrappy problem-solving | Building effective ML solutions with constraints, creative data sourcing |

### What Makes Airbnb Interviews Different
- **Mission alignment is genuine**: Airbnb interviewers can tell the difference between rehearsed mission statements and authentic connection. If you have personal stories about travel, hosting, or belonging, use them.
- **Craftsmanship matters**: Airbnb values quality and attention to detail. Show that you care about the craft of ML engineering, not just shipping fast.
- **Cross-functional emphasis**: Airbnb's product development is highly collaborative. They want to see deep partnership with product, design, and data science.
- **Belonging focus**: Many ML applications at Airbnb directly affect user belonging (search ranking, pricing, trust and safety). Show awareness of how ML decisions affect diverse user populations.

### Airbnb's Interview Process for ML
- Typically includes a behavioral "core values" round
- Interviewers explicitly map questions to specific values
- Culture fit is weighted heavily -- a strong technical performance with poor culture fit is a decline
- Cross-functional references (from product managers, designers) carry significant weight

### Mapping MLE Experiences to Airbnb Values

**Champion the Mission:**
- ML work that directly improves user experience (search ranking, recommendation quality)
- Fairness and inclusion considerations in model design
- Times you prioritized user impact over technical elegance

**Be a Host:**
- Onboarding new team members, creating inclusive team culture
- Making technical concepts accessible to non-technical partners
- Going out of your way to help a colleague or partner team

**Embrace the Adventure:**
- Exploring novel ML techniques, learning new domains
- Taking on a challenging project outside your comfort zone
- How you responded to failure with curiosity rather than defensiveness

**Be a Cereal Entrepreneur:**
- Building ML solutions with limited data, compute, or team resources
- Creative approaches to data collection or labeling
- Scrappy prototypes that proved value before full investment

## STAR Templates

### Template 1: Champion the Mission + Be a Host
- **Situation**: The search ranking model optimized for booking conversion but user research showed that guests from certain demographics consistently saw less diverse listing results, potentially affecting their sense of belonging on the platform.
- **Task**: Address the fairness gap in search results without significantly impacting overall conversion.
- **Action**: Collaborated with the user research team to quantify the disparity. Designed a fairness-aware ranking component that ensured diverse representation across listing types, price ranges, and neighborhoods. Worked closely with the trust and safety team to define appropriate fairness metrics. Ran an A/B test measuring both conversion and diversity metrics. Presented the tradeoff analysis to product leadership with a clear recommendation.
- **Result**: Implemented a ranking adjustment that improved result diversity by 35% with only a 0.5% conversion impact. User satisfaction surveys from affected demographics improved by 12%. The fairness evaluation framework became a standard part of the model development process.

### Template 2: Embrace the Adventure + Be a Cereal Entrepreneur
- **Situation**: The team needed a real-time pricing suggestion model for hosts, but the available training data was sparse (many listings had fewer than 10 bookings) and the compute budget was limited.
- **Task**: Build an effective pricing model under severe data and resource constraints.
- **Action**: Instead of building a large deep learning model (which the data could not support), researched and applied a hierarchical Bayesian approach that shared information across similar listings. Used creative feature engineering -- public data sources for local events, seasonality patterns from aggregated market data, and geographic clustering to pool information across sparse listings. Built the entire pipeline to run on a single GPU instance to stay within budget. Prototyped in a Jupyter notebook first (1 week) before investing in production infrastructure.
- **Result**: The model provided pricing suggestions within 5% of optimal for 80% of listings, even those with minimal booking history. Host adoption of pricing suggestions increased from 20% to 55%. The hierarchical approach became the standard for all sparse-data ML problems at the company.

## Interview Patterns

| Airbnb Value | Example Question | What To Emphasize |
|-------------|-----------------|-------------------|
| Champion the Mission | "Why do you want to work at Airbnb?" | Authentic connection to belonging, travel, or community |
| Champion the Mission | "Tell me about a time you put users first." | Sacrificing short-term metrics for long-term user value |
| Be a Host | "Describe how you have made a teammate feel supported." | Specific actions, not just intentions |
| Be a Host | "How do you collaborate with non-technical partners?" | Empathy, accessibility, shared vocabulary |
| Embrace the Adventure | "Tell me about a time you took a risk." | Intellectual curiosity, growth from the experience |
| Embrace the Adventure | "Describe a time you learned something completely new." | Enthusiasm for learning, not just competence |
| Be a Cereal Entrepreneur | "Tell me about a time you built something with limited resources." | Creativity, scrappiness, maximum impact per unit effort |

### Common Interview Questions
- [ ] Why Airbnb? What about our mission resonates with you?
- [ ] Tell me about a time you went above and beyond to help a colleague or user.
- [ ] Describe a project where you had to be creative with limited resources.
- [ ] How do you approach learning in a new domain?
- [ ] Tell me about a time you considered the broader impact of your technical work.
- [ ] Describe your most effective cross-functional partnership.
- [ ] Tell me about a time you championed an unpopular but important idea.

## Comparisons

| Aspect | Does Not Show Airbnb Values | Shows Airbnb Values |
|--------|---------------------------|---------------------|
| Mission | "I want to work at Airbnb because it is a top tech company" | "I have been a host for 3 years; I have seen firsthand how the platform creates belonging, and I want to use ML to make that experience better for everyone" |
| Hosting | "I onboarded the new engineer by giving them documentation" | "I created a personalized onboarding plan, paired with them daily for the first week, and checked in on how included they felt on the team" |
| Adventure | "I used the same model architecture I always use" | "I explored a novel hierarchical approach I read about in a recent paper because it seemed well-suited to our sparse data problem" |
| Entrepreneurship | "We needed more data so I asked for a bigger labeling budget" | "I created a semi-supervised approach using existing interaction data as weak labels, avoiding the need for additional labeling budget entirely" |

## Key Takeaways
- [ ] Prepare an authentic "Why Airbnb?" story that connects to belonging, travel, or community
- [ ] Frame ML work in terms of user impact and fairness, not just metric optimization
- [ ] Show genuine collaboration and empathy in cross-functional stories
- [ ] Demonstrate intellectual curiosity and willingness to explore unfamiliar approaches
- [ ] Include examples of resourceful, creative problem-solving under constraints
- [ ] Show awareness of how ML decisions affect diverse user populations
- [ ] Airbnb values craftsmanship -- show you care about the quality of your work, not just shipping fast
"""

# ---------------------------------------------------------------------------
# Main: Write content to database
# ---------------------------------------------------------------------------


def main() -> None:
    """Populate framework_nodes with Pillar 8 content."""
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
