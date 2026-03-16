"""Integration test: scraper pipeline.

Full journey: create seed URL -> paste text -> verify questions extracted
and stored -> analyze question -> verify analysis stored.
Also covers deduplication, filtering, update, and edge cases.
"""

import json
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_EXPERIENCE = (
    "I interviewed at Google for MLE L5 position last month. "
    "The onsite had 4 rounds:\n"
    "1. Coding: Given a binary tree, find the maximum path sum\n"
    "2. ML Design: Design a recommendation system for YouTube\n"
    "3. ML Theory: Explain the bias-variance tradeoff and how it "
    "applies to ensemble methods\n"
    "4. Behavioral: Tell me about a time you had to convince stakeholders"
)

EXTRACTED_QUESTIONS_RESPONSE = [
    {
        "company": "Google",
        "role": "MLE",
        "level": "L5",
        "round": "onsite_coding",
        "question_text": "Given a binary tree, find the maximum path sum",
        "question_type": "coding",
        "tags": ["binary_tree", "dfs", "dynamic_programming"],
    },
    {
        "company": "Google",
        "role": "MLE",
        "level": "L5",
        "round": "onsite_ml_design",
        "question_text": "Design a recommendation system for YouTube",
        "question_type": "ml_system_design",
        "tags": ["recommendation", "youtube", "collaborative_filtering"],
    },
    {
        "company": "Google",
        "role": "MLE",
        "level": "L5",
        "round": "onsite_ml_theory",
        "question_text": (
            "Explain the bias-variance tradeoff and how it applies "
            "to ensemble methods"
        ),
        "question_type": "ml_theory",
        "tags": ["bias_variance", "ensemble"],
    },
    {
        "company": "Google",
        "role": "MLE",
        "level": "L5",
        "round": "behavioral",
        "question_text": (
            "Tell me about a time you had to convince stakeholders"
        ),
        "question_type": "behavioral",
        "tags": ["leadership", "communication"],
    },
]

ANALYSIS_RESPONSE = {
    "solution_approach": "Use DFS with global max tracking",
    "key_concepts": ["tree traversal", "dynamic programming", "recursion"],
    "difficulty": "hard",
    "related_patterns": ["binary_tree", "dfs"],
    "suggested_study": "Review tree DP patterns and path sum variants",
}


def _create_seed(client, **overrides):
    """Create a seed URL and return (response, id)."""
    payload = {
        "url": "https://teamblind.com/post/google-mle-interview-123",
        "source_site": "blind",
        "company": "Google",
        "role_filter": "MLE",
    }
    payload.update(overrides)
    resp = client.post("/api/scraper/seeds", json=payload)
    return resp, resp.json().get("id") if resp.status_code == 201 else None


def _paste_text(client, mock_llm, text=SAMPLE_EXPERIENCE, **overrides):
    """Paste experience text with mocked LLM and return response."""
    payload = {"text": text}
    payload.update(overrides)
    with patch(
        "src.backend.routers.scraper.LLMService", return_value=mock_llm
    ):
        resp = client.post("/api/scraper/paste", json=payload)
    return resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestScraperPipelineHappyPath:
    """End-to-end: seed -> paste -> extract -> analyze."""

    def test_full_pipeline(self, test_client, mock_llm):
        """Complete pipeline: create seed, paste text, verify extraction,
        analyze question, verify analysis stored."""

        # Configure mock to return extracted questions
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE

        # 1. Create seed URL
        resp, seed_id = _create_seed(test_client)
        assert resp.status_code == 201
        seed = resp.json()
        assert seed["url"] == (
            "https://teamblind.com/post/google-mle-interview-123"
        )
        assert seed["source_site"] == "blind"
        assert seed["company"] == "Google"
        assert seed["is_active"] is True

        # 2. Verify seed appears in list
        resp = test_client.get("/api/scraper/seeds")
        assert resp.status_code == 200
        seeds = resp.json()
        assert len(seeds) == 1
        assert seeds[0]["id"] == seed_id

        # 3. Paste interview experience text
        resp = _paste_text(
            test_client, mock_llm,
            company="Google", role="MLE",
        )
        assert resp.status_code == 200
        paste_result = resp.json()
        assert paste_result["was_duplicate"] is False
        assert paste_result["questions_count"] == 4
        assert len(paste_result["questions"]) == 4

        # Verify question details
        q_texts = [q["question_text"] for q in paste_result["questions"]]
        assert "Design a recommendation system for YouTube" in q_texts

        # 4. Verify questions accessible via list endpoint
        resp = test_client.get("/api/questions")
        assert resp.status_code == 200
        questions = resp.json()
        assert len(questions) == 4

        # Verify fields were properly stored
        coding_q = next(
            q for q in questions
            if q["question_type"] == "coding"
        )
        assert coding_q["company"] == "Google"
        assert coding_q["role"] == "MLE"
        assert coding_q["is_reviewed"] is False

        # 5. Analyze a question via LLM
        mock_llm.chat.return_value = ANALYSIS_RESPONSE
        q_id = coding_q["id"]
        with patch(
            "src.backend.routers.scraper.LLMService", return_value=mock_llm
        ):
            resp = test_client.post(f"/api/questions/{q_id}/analyze")
        assert resp.status_code == 200
        analysis = resp.json()
        assert analysis["difficulty"] == "hard"
        assert "tree traversal" in analysis["key_concepts"]

        # 6. Verify analysis stored in question notes
        resp = test_client.get("/api/questions", params={"search": "binary tree"})
        assert resp.status_code == 200
        updated_q = resp.json()
        assert len(updated_q) == 1
        notes = json.loads(updated_q[0]["notes"])
        assert notes["difficulty"] == "hard"
        assert notes["solution_approach"] == "Use DFS with global max tracking"


class TestSeedURLManagement:
    """Seed URL creation, listing, and dedup."""

    def test_create_seed_url(self, test_client):
        """Create seed URL with all fields."""
        resp, seed_id = _create_seed(test_client)
        assert resp.status_code == 201
        assert seed_id is not None
        seed = resp.json()
        assert seed["role_filter"] == "MLE"
        assert seed["check_interval_hours"] == 24

    def test_duplicate_seed_url_rejected(self, test_client):
        """Creating duplicate seed URL returns 409."""
        resp1, _ = _create_seed(test_client)
        assert resp1.status_code == 201

        resp2, _ = _create_seed(test_client)
        assert resp2.status_code == 409

    def test_list_seeds_filter_by_source(self, test_client):
        """Filter seeds by source_site."""
        _create_seed(test_client, url="https://blind.com/a", source_site="blind")
        _create_seed(
            test_client,
            url="https://leetcode.com/discuss/b",
            source_site="leetcode_discuss",
        )

        resp = test_client.get(
            "/api/scraper/seeds", params={"source_site": "blind"}
        )
        assert resp.status_code == 200
        seeds = resp.json()
        assert len(seeds) == 1
        assert seeds[0]["source_site"] == "blind"

    def test_list_seeds_filter_by_active(self, test_client):
        """Filter seeds by is_active (all default True)."""
        _create_seed(test_client)

        resp = test_client.get(
            "/api/scraper/seeds", params={"is_active": True}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp = test_client.get(
            "/api/scraper/seeds", params={"is_active": False}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0


class TestPasteExtraction:
    """Paste text extraction and deduplication."""

    def test_paste_extracts_questions(self, test_client, mock_llm):
        """Paste text extracts questions via LLM."""
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE

        resp = _paste_text(test_client, mock_llm)
        assert resp.status_code == 200
        result = resp.json()
        assert result["questions_count"] == 4
        assert result["was_duplicate"] is False

    def test_paste_duplicate_returns_cached(self, test_client, mock_llm):
        """Pasting same text twice returns cached results."""
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE

        # First paste
        resp1 = _paste_text(test_client, mock_llm)
        assert resp1.status_code == 200
        assert resp1.json()["was_duplicate"] is False

        # Second paste with same text
        resp2 = _paste_text(test_client, mock_llm)
        assert resp2.status_code == 200
        result2 = resp2.json()
        assert result2["was_duplicate"] is True
        assert result2["questions_count"] == 4

        # LLM should only have been called once (first paste)
        assert mock_llm.chat.call_count == 1

    def test_paste_with_company_context(self, test_client, mock_llm):
        """Paste with company/role context passes to extractor."""
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE

        resp = _paste_text(
            test_client, mock_llm,
            company="Meta", role="Research Scientist",
        )
        assert resp.status_code == 200
        assert resp.json()["questions_count"] == 4

        # Verify context was passed to LLM
        call_args = mock_llm.chat.call_args
        user_msg = call_args[1]["messages"][0]["content"]
        assert "Meta" in user_msg
        assert "Research Scientist" in user_msg

    def test_paste_no_questions_extracted(self, test_client, mock_llm):
        """Paste text that yields no questions returns empty list."""
        mock_llm.chat.return_value = []

        resp = _paste_text(
            test_client, mock_llm,
            text="Just a random blog post about my day at work, nothing special.",
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["questions_count"] == 0
        assert result["questions"] == []

    def test_paste_llm_error_returns_empty(self, test_client, mock_llm):
        """LLM returning error dict yields no questions."""
        mock_llm.chat.return_value = {"error": "API rate limit exceeded"}

        resp = _paste_text(
            test_client, mock_llm,
            text="Interview at Amazon: Design a fraud detection system.",
        )
        assert resp.status_code == 200
        result = resp.json()
        assert result["questions_count"] == 0

    def test_paste_text_too_short_rejected(self, test_client, mock_llm):
        """Text shorter than 10 chars is rejected by schema validation."""
        mock_llm.chat.return_value = []

        with patch(
            "src.backend.routers.scraper.LLMService", return_value=mock_llm
        ):
            resp = test_client.post(
                "/api/scraper/paste", json={"text": "short"}
            )
        assert resp.status_code == 422


class TestQuestionListAndFilter:
    """Question listing with various filters."""

    def _seed_questions(self, test_client, mock_llm):
        """Paste two different experiences to create diverse questions."""
        # First experience: Google coding + ML design
        mock_llm.chat.return_value = [
            {
                "company": "Google",
                "role": "MLE",
                "question_text": "Implement LRU cache",
                "question_type": "coding",
                "tags": ["data_structures"],
            },
            {
                "company": "Google",
                "role": "MLE",
                "question_text": "Design YouTube recommendations",
                "question_type": "ml_system_design",
                "tags": ["recommendation"],
            },
        ]
        _paste_text(
            test_client, mock_llm,
            text="Google MLE interview: LRU cache coding and YouTube rec design",
        )

        # Second experience: Meta behavioral
        mock_llm.chat.return_value = [
            {
                "company": "Meta",
                "role": "Research Scientist",
                "question_text": "Describe a failed project",
                "question_type": "behavioral",
                "tags": ["leadership"],
            },
        ]
        _paste_text(
            test_client, mock_llm,
            text="Meta RS behavioral round: describe a failed project and learnings",
        )

    def test_filter_by_company(self, test_client, mock_llm):
        """Filter questions by company name."""
        self._seed_questions(test_client, mock_llm)

        resp = test_client.get("/api/questions", params={"company": "Google"})
        assert resp.status_code == 200
        questions = resp.json()
        assert len(questions) == 2
        assert all(q["company"] == "Google" for q in questions)

    def test_filter_by_question_type(self, test_client, mock_llm):
        """Filter questions by type."""
        self._seed_questions(test_client, mock_llm)

        resp = test_client.get(
            "/api/questions", params={"question_type": "behavioral"}
        )
        assert resp.status_code == 200
        questions = resp.json()
        assert len(questions) == 1
        assert questions[0]["company"] == "Meta"

    def test_filter_by_search(self, test_client, mock_llm):
        """Search questions by text."""
        self._seed_questions(test_client, mock_llm)

        resp = test_client.get(
            "/api/questions", params={"search": "LRU"}
        )
        assert resp.status_code == 200
        questions = resp.json()
        assert len(questions) == 1
        assert "LRU" in questions[0]["question_text"]

    def test_filter_by_is_reviewed(self, test_client, mock_llm):
        """Filter by review status."""
        self._seed_questions(test_client, mock_llm)

        # All unreviewed initially
        resp = test_client.get(
            "/api/questions", params={"is_reviewed": False}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3

        resp = test_client.get(
            "/api/questions", params={"is_reviewed": True}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_pagination(self, test_client, mock_llm):
        """Verify limit and offset work."""
        self._seed_questions(test_client, mock_llm)

        resp = test_client.get(
            "/api/questions", params={"limit": 2, "offset": 0}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        resp = test_client.get(
            "/api/questions", params={"limit": 2, "offset": 2}
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1  # only 3 total


class TestQuestionUpdate:
    """Update question fields."""

    def test_mark_reviewed(self, test_client, mock_llm):
        """Mark a question as reviewed."""
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE[:1]
        _paste_text(test_client, mock_llm)

        resp = test_client.get("/api/questions")
        q_id = resp.json()[0]["id"]

        resp = test_client.put(
            f"/api/questions/{q_id}",
            json={"is_reviewed": True},
        )
        assert resp.status_code == 200
        assert resp.json()["is_reviewed"] is True

        # Verify via filter
        resp = test_client.get(
            "/api/questions", params={"is_reviewed": True}
        )
        assert len(resp.json()) == 1

    def test_add_notes_and_difficulty(self, test_client, mock_llm):
        """Update notes and difficulty estimate."""
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE[:1]
        _paste_text(test_client, mock_llm)

        resp = test_client.get("/api/questions")
        q_id = resp.json()[0]["id"]

        resp = test_client.put(
            f"/api/questions/{q_id}",
            json={
                "notes": "Review tree traversal patterns",
                "difficulty_estimate": "hard",
            },
        )
        assert resp.status_code == 200

    def test_update_nonexistent_question(self, test_client):
        """Updating non-existent question returns 404."""
        resp = test_client.put(
            "/api/questions/99999",
            json={"is_reviewed": True},
        )
        assert resp.status_code == 404


class TestQuestionAnalysis:
    """LLM-powered question analysis."""

    def test_analyze_stores_result(self, test_client, mock_llm):
        """Analyze stores result in notes field."""
        # Create a question
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE[:1]
        _paste_text(test_client, mock_llm)

        resp = test_client.get("/api/questions")
        q_id = resp.json()[0]["id"]

        # Analyze
        mock_llm.chat.return_value = ANALYSIS_RESPONSE
        with patch(
            "src.backend.routers.scraper.LLMService", return_value=mock_llm
        ):
            resp = test_client.post(f"/api/questions/{q_id}/analyze")
        assert resp.status_code == 200
        analysis = resp.json()
        assert analysis["difficulty"] == "hard"
        assert "suggested_study" in analysis

    def test_analyze_nonexistent_question(self, test_client, mock_llm):
        """Analyzing non-existent question returns 404."""
        with patch(
            "src.backend.routers.scraper.LLMService", return_value=mock_llm
        ):
            resp = test_client.post("/api/questions/99999/analyze")
        assert resp.status_code == 404

    def test_analyze_with_llm_error(self, test_client, mock_llm):
        """LLM error during analysis returns error dict without storing."""
        mock_llm.chat.return_value = EXTRACTED_QUESTIONS_RESPONSE[:1]
        _paste_text(test_client, mock_llm)

        resp = test_client.get("/api/questions")
        q_id = resp.json()[0]["id"]

        # Simulate LLM error
        mock_llm.chat.return_value = {"error": "API timeout"}
        with patch(
            "src.backend.routers.scraper.LLMService", return_value=mock_llm
        ):
            resp = test_client.post(f"/api/questions/{q_id}/analyze")
        assert resp.status_code == 200
        result = resp.json()
        assert "error" in result

        # Notes should NOT be updated (error result)
        resp = test_client.get("/api/questions")
        q = next(q for q in resp.json() if q["id"] == q_id)
        assert q["notes"] is None


class TestScraperJobStatus:
    """Scraper run and status endpoints."""

    def setup_method(self):
        """Clear global job state before each test."""
        from src.backend.routers.scraper import _scraper_jobs
        _scraper_jobs.clear()

    def teardown_method(self):
        """Clear global job state after each test."""
        from src.backend.routers.scraper import _scraper_jobs
        _scraper_jobs.clear()

    def test_run_returns_job_id(self, test_client):
        """POST /scraper/run returns 202 with job_id."""
        resp = test_client.post(
            "/api/scraper/run", json={"seed_url_ids": None}
        )
        assert resp.status_code == 202
        result = resp.json()
        assert "job_id" in result
        assert result["status"] == "started"

    def test_status_returns_jobs(self, test_client):
        """GET /scraper/status returns list of job statuses."""
        # Trigger a job first
        test_client.post("/api/scraper/run", json={})

        resp = test_client.get("/api/scraper/status")
        assert resp.status_code == 200
        jobs = resp.json()
        assert len(jobs) >= 1
        assert "job_id" in jobs[0]
        assert "status" in jobs[0]
        assert "seeds_total" in jobs[0]
