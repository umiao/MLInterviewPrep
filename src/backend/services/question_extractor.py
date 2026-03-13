"""LLM-based interview question extractor."""
from src.backend.services.llm_service import LLMService

EXTRACT_PROMPT = """
Given this interview experience post, extract ALL interview questions mentioned.

For EACH question, provide:
1. company: the company name
2. role: the role (MLE, Applied Scientist, etc.)
3. level: seniority level if mentioned
4. round: which interview round (phone, onsite coding, ML design, behavioral)
5. question_text: the actual question (preserve technical details)
6. question_type: one of [coding, ml_theory, ml_system_design, ml_coding, behavioral, general_system_design]
7. tags: relevant topic tags

Return JSON array. If no clear questions found, return [].
Example:
[
  {
    "company": "Google",
    "role": "MLE",
    "level": "L5",
    "round": "onsite_ml_design",
    "question_text": "Design a real-time spam detection system for Gmail",
    "question_type": "ml_system_design",
    "tags": ["spam_detection", "real_time", "text_classification", "gmail"]
  }
]
"""


def extract_questions(
    llm_service: LLMService,
    text: str,
    source_context: dict | None = None,
) -> list[dict]:
    """Extract interview questions from text using LLM.

    Args:
        llm_service: LLM service instance.
        text: Interview experience text.
        source_context: Optional context like {"company": "Google", "role": "MLE"}.

    Returns:
        List of extracted question dicts.
    """
    user_message = ""
    if source_context:
        company = source_context.get("company", "Unknown")
        role = source_context.get("role", "Unknown")
        user_message = (
            f"Context: This post is likely about {company} {role} interviews.\n\n"
        )
    user_message += text

    result = llm_service.chat(
        system_prompt=EXTRACT_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        response_format="json",
    )

    if isinstance(result, dict) and "error" in result:
        return []

    if not isinstance(result, list):
        return []

    # Filter to only questions with required fields
    valid = []
    for q in result:
        if isinstance(q, dict) and q.get("question_text") and q.get("question_type"):
            valid.append(q)
    return valid
