"""Tests for scraper API routes."""
from unittest.mock import MagicMock, patch


def test_seed_url_create_list(test_client):
    """Create and list seed URLs."""
    resp = test_client.post("/api/scraper/seeds", json={
        "url": "https://example.com/page1",
        "source_site": "blind",
    })
    assert resp.status_code == 201

    resp = test_client.get("/api/scraper/seeds")
    assert len(resp.json()) == 1


def test_seed_url_duplicate(test_client):
    """Duplicate seed URL returns 409."""
    test_client.post("/api/scraper/seeds", json={
        "url": "https://example.com/dup",
        "source_site": "blind",
    })
    resp = test_client.post("/api/scraper/seeds", json={
        "url": "https://example.com/dup",
        "source_site": "1point3acres",
    })
    assert resp.status_code == 409


def test_seed_url_filter(test_client):
    """Filter by source_site works."""
    test_client.post("/api/scraper/seeds", json={
        "url": "https://a.com", "source_site": "blind",
    })
    test_client.post("/api/scraper/seeds", json={
        "url": "https://b.com", "source_site": "1point3acres",
    })

    resp = test_client.get("/api/scraper/seeds?source_site=blind")
    assert len(resp.json()) == 1


def test_paste_experience(test_client):
    """Paste text extracts questions."""
    mock_questions = [
        {
            "company": "Google",
            "role": "MLE",
            "question_text": "Design a rec system",
            "question_type": "ml_system_design",
            "tags": ["recsys"],
        }
    ]

    with patch("src.backend.routers.scraper.LLMService") as mock_cls:
        mock_llm = MagicMock()
        mock_llm.chat.return_value = mock_questions
        mock_cls.return_value = mock_llm

        with patch("src.backend.routers.scraper.extract_questions", return_value=mock_questions):
            resp = test_client.post("/api/scraper/paste", json={
                "text": "I interviewed at Google for MLE. They asked me to design a rec system.",
                "company": "Google",
                "role": "MLE",
            })

    assert resp.status_code == 200
    data = resp.json()
    assert data["questions_count"] == 1
    assert data["was_duplicate"] is False


def test_scraper_status_empty(test_client):
    """No jobs returns empty list."""
    resp = test_client.get("/api/scraper/status")
    assert resp.status_code == 200
    assert resp.json() == []


def test_questions_list_empty(test_client):
    """Empty questions returns empty list."""
    resp = test_client.get("/api/questions")
    assert resp.status_code == 200
    assert resp.json() == []
