# Framework Content Template

Standard structure for all framework leaf-topic prep docs.
Each topic's `description` field follows this template rendered as Markdown + KaTeX.

---

## Template Structure

```markdown
# {Topic Title}

## Overview
Brief 2-3 sentence summary of the topic and why it matters for MLE interviews.

## Core Concepts

### {Concept 1}
Explanation with mathematical formulation where applicable.

$$
\text{LaTeX formula here}
$$

Key properties:
- Property 1
- Property 2

### {Concept 2}
...

## Implementation

```python
# Concise, interview-ready code snippet
def example():
    pass
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Pattern 1 | Scenario | Insight |
| Pattern 2 | Scenario | Insight |

### Common Interview Questions
- [ ] Question 1
- [ ] Question 2
- [ ] Question 3

## Comparisons

| Aspect | Method A | Method B |
|--------|----------|----------|
| Complexity | O(...) | O(...) |
| Pros | ... | ... |
| Cons | ... | ... |

## Key Takeaways

- [ ] Takeaway 1
- [ ] Takeaway 2
- [ ] Takeaway 3
```

---

## Guidelines

1. **Depth**: Target senior MLE level -- assume familiarity with basics, focus on nuance and trade-offs.
2. **Math**: Use KaTeX-compatible LaTeX. Inline: `$...$`, block: `$$...$$`.
3. **Code**: Python only. Keep snippets short (< 30 lines), focused on the core idea.
4. **Checkboxes**: Use `- [ ]` for items the user should self-assess during review.
5. **Tables**: Use for comparisons and pattern catalogs -- interviewers love structured answers.
6. **No emoji**: Use text markers only.
