"""Tests for forum API routes."""
import pytest

from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed


@pytest.fixture()
def _seed_and_company(test_client):
    """Create a company and a forum seed for testing.

    Returns:
        Tuple of (company_id, seed_id).
    """
    resp = test_client.post("/api/companies", json={
        "name": "TestCo",
        "status": "applied",
    })
    company_id = resp.json()["id"]

    resp = test_client.post("/api/forum/seeds", json={
        "url": "https://1point3acres.com/bbs/forum-123",
        "source_site": "1point3acres",
        "label": "TestCo interviews",
        "company_id": company_id,
    })
    seed_id = resp.json()["id"]
    return company_id, seed_id


class TestSeedEndpoints:
    """Tests for forum seed CRUD endpoints."""

    def test_create_seed(self, test_client):
        """POST /forum/seeds creates a new seed."""
        resp = test_client.post("/api/forum/seeds", json={
            "url": "https://1point3acres.com/bbs/forum-100",
            "source_site": "1point3acres",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == "https://1point3acres.com/bbs/forum-100"
        assert data["source_site"] == "1point3acres"
        assert data["is_active"] is True

    def test_create_seed_with_company(self, test_client):
        """POST /forum/seeds with company_id links to company."""
        company = test_client.post("/api/companies", json={
            "name": "SeedCo",
            "status": "applied",
        }).json()

        resp = test_client.post("/api/forum/seeds", json={
            "url": "https://1point3acres.com/bbs/forum-200",
            "source_site": "1point3acres",
            "company_id": company["id"],
            "label": "SeedCo interviews",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["company_id"] == company["id"]
        assert data["label"] == "SeedCo interviews"

    def test_create_seed_duplicate_url(self, test_client):
        """POST /forum/seeds with duplicate URL returns 409."""
        test_client.post("/api/forum/seeds", json={
            "url": "https://1point3acres.com/bbs/forum-dup",
            "source_site": "1point3acres",
        })
        resp = test_client.post("/api/forum/seeds", json={
            "url": "https://1point3acres.com/bbs/forum-dup",
            "source_site": "1point3acres",
        })
        assert resp.status_code == 409

    def test_create_seed_empty_url(self, test_client):
        """POST /forum/seeds with empty URL returns 422."""
        resp = test_client.post("/api/forum/seeds", json={
            "url": "",
            "source_site": "1point3acres",
        })
        assert resp.status_code == 422

    def test_list_seeds_empty(self, test_client):
        """GET /forum/seeds returns empty list when no seeds exist."""
        resp = test_client.get("/api/forum/seeds")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_seeds(self, test_client, _seed_and_company):
        """GET /forum/seeds returns created seeds."""
        resp = test_client.get("/api/forum/seeds")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_seeds_filter_company(self, test_client, _seed_and_company):
        """GET /forum/seeds?company_id=X filters by company."""
        company_id, _ = _seed_and_company
        resp = test_client.get(f"/api/forum/seeds?company_id={company_id}")
        assert len(resp.json()) == 1

        resp = test_client.get("/api/forum/seeds?company_id=99999")
        assert len(resp.json()) == 0

    def test_list_seeds_filter_source_site(self, test_client, _seed_and_company):
        """GET /forum/seeds?source_site=X filters by source."""
        resp = test_client.get("/api/forum/seeds?source_site=1point3acres")
        assert len(resp.json()) == 1

        resp = test_client.get("/api/forum/seeds?source_site=other")
        assert len(resp.json()) == 0

    def test_delete_seed(self, test_client, _seed_and_company):
        """DELETE /forum/seeds/{id} removes seed."""
        _, seed_id = _seed_and_company
        resp = test_client.delete(f"/api/forum/seeds/{seed_id}")
        assert resp.status_code == 204

        resp = test_client.get("/api/forum/seeds")
        assert len(resp.json()) == 0

    def test_delete_seed_not_found(self, test_client):
        """DELETE /forum/seeds/{id} returns 404 for missing seed."""
        resp = test_client.delete("/api/forum/seeds/99999")
        assert resp.status_code == 404


class TestLinkEndpoints:
    """Tests for forum post link endpoints."""

    def test_list_links_empty(self, test_client, _seed_and_company):
        """GET /forum/seeds/{id}/links returns empty when no links."""
        _, seed_id = _seed_and_company
        resp = test_client.get(f"/api/forum/seeds/{seed_id}/links")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_links_not_found(self, test_client):
        """GET /forum/seeds/{id}/links returns 404 for missing seed."""
        resp = test_client.get("/api/forum/seeds/99999/links")
        assert resp.status_code == 404

    def test_scrape_links(self, test_client, _seed_and_company, db_session):
        """POST /forum/seeds/{id}/scrape returns discovered links."""
        _, seed_id = _seed_and_company

        # Pre-insert a link to simulate scrape result
        link = ForumPostLink(
            forum_seed_id=seed_id,
            url="https://1point3acres.com/bbs/thread-111",
            title="Interview Q1",
            status="pending",
            fetch_order=0,
        )
        db_session.add(link)
        db_session.commit()

        resp = test_client.get(f"/api/forum/seeds/{seed_id}/links")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "Interview Q1"

    def test_scrape_seed_not_found(self, test_client):
        """POST /forum/seeds/{id}/scrape returns 404 for missing seed."""
        resp = test_client.post("/api/forum/seeds/99999/scrape")
        assert resp.status_code == 404


class TestPostEndpoints:
    """Tests for forum post endpoints."""

    def test_get_post_not_found(self, test_client):
        """GET /forum/posts/{id} returns 404 for missing post."""
        resp = test_client.get("/api/forum/posts/99999")
        assert resp.status_code == 404

    def test_get_post(self, test_client, _seed_and_company, db_session):
        """GET /forum/posts/{id} returns post content."""
        _, seed_id = _seed_and_company

        link = ForumPostLink(
            forum_seed_id=seed_id,
            url="https://1point3acres.com/bbs/thread-222",
            title="Interview Q2",
            status="fetched",
            fetch_order=0,
        )
        db_session.add(link)
        db_session.flush()

        post = ForumPost(
            forum_post_link_id=link.id,
            raw_text="System design question about caching",
            content_hash="abc123",
            author="user1",
            published_at="2026-03-01",
        )
        db_session.add(post)
        db_session.commit()

        resp = test_client.get(f"/api/forum/posts/{post.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["raw_text"] == "System design question about caching"
        assert data["author"] == "user1"

    def test_fetch_link_not_found(self, test_client):
        """POST /forum/links/{id}/fetch returns 404 for missing link."""
        resp = test_client.post("/api/forum/links/99999/fetch")
        assert resp.status_code == 404

    def test_fetch_next_seed_not_found(self, test_client):
        """POST /forum/seeds/{id}/fetch-next returns 404 for missing seed."""
        resp = test_client.post("/api/forum/seeds/99999/fetch-next")
        assert resp.status_code == 404


class TestProgressEndpoint:
    """Tests for forum progress endpoint."""

    def test_progress_empty(self, test_client, _seed_and_company):
        """GET /forum/seeds/{id}/progress returns zeros when no links."""
        _, seed_id = _seed_and_company
        resp = test_client.get(f"/api/forum/seeds/{seed_id}/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["pending"] == 0
        assert data["fetched"] == 0
        assert data["failed"] == 0
        assert data["last_fetched_url"] is None

    def test_progress_with_links(self, test_client, _seed_and_company, db_session):
        """GET /forum/seeds/{id}/progress returns accurate counts."""
        _, seed_id = _seed_and_company

        for i, status in enumerate(["pending", "pending", "fetched", "failed"]):
            link = ForumPostLink(
                forum_seed_id=seed_id,
                url=f"https://1point3acres.com/bbs/thread-{300 + i}",
                status=status,
                fetch_order=i,
            )
            db_session.add(link)
        db_session.commit()

        resp = test_client.get(f"/api/forum/seeds/{seed_id}/progress")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 4
        assert data["pending"] == 2
        assert data["fetched"] == 1
        assert data["failed"] == 1

    def test_progress_not_found(self, test_client):
        """GET /forum/seeds/{id}/progress returns 404 for missing seed."""
        resp = test_client.get("/api/forum/seeds/99999/progress")
        assert resp.status_code == 404


class TestImportEndpoint:
    """Tests for forum post import endpoint."""

    def test_import_post(self, test_client, _seed_and_company, db_session):
        """POST /forum/posts/{id}/import appends to company prep notes."""
        company_id, seed_id = _seed_and_company

        link = ForumPostLink(
            forum_seed_id=seed_id,
            url="https://1point3acres.com/bbs/thread-400",
            title="ML Design Q",
            status="fetched",
            fetch_order=0,
        )
        db_session.add(link)
        db_session.flush()

        post = ForumPost(
            forum_post_link_id=link.id,
            raw_text="Design a recommendation system",
            content_hash="hash400",
        )
        db_session.add(post)
        db_session.commit()

        resp = test_client.post(
            f"/api/forum/posts/{post.id}/import",
            json={"company_id": company_id},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == company_id
        assert "Design a recommendation system" in data["prep_notes"]

    def test_import_post_not_found(self, test_client, _seed_and_company):
        """POST /forum/posts/{id}/import returns 404 for missing post."""
        company_id, _ = _seed_and_company
        resp = test_client.post(
            "/api/forum/posts/99999/import",
            json={"company_id": company_id},
        )
        assert resp.status_code == 404

    def test_import_company_not_found(self, test_client, _seed_and_company, db_session):
        """POST /forum/posts/{id}/import returns 404 for missing company."""
        _, seed_id = _seed_and_company

        link = ForumPostLink(
            forum_seed_id=seed_id,
            url="https://1point3acres.com/bbs/thread-500",
            title="Q",
            status="fetched",
            fetch_order=0,
        )
        db_session.add(link)
        db_session.flush()

        post = ForumPost(
            forum_post_link_id=link.id,
            raw_text="content",
            content_hash="hash500",
        )
        db_session.add(post)
        db_session.commit()

        resp = test_client.post(
            f"/api/forum/posts/{post.id}/import",
            json={"company_id": 99999},
        )
        assert resp.status_code == 404


class TestDeleteCascade:
    """Tests for cascade delete behavior."""

    def test_delete_seed_cascades_links_and_posts(
        self, test_client, _seed_and_company, db_session
    ):
        """DELETE /forum/seeds/{id} removes seed, links, and posts."""
        _, seed_id = _seed_and_company

        link = ForumPostLink(
            forum_seed_id=seed_id,
            url="https://1point3acres.com/bbs/thread-600",
            status="fetched",
            fetch_order=0,
        )
        db_session.add(link)
        db_session.flush()

        post = ForumPost(
            forum_post_link_id=link.id,
            raw_text="cascade test",
            content_hash="hash600",
        )
        db_session.add(post)
        db_session.commit()

        link_id = link.id
        post_id = post.id

        resp = test_client.delete(f"/api/forum/seeds/{seed_id}")
        assert resp.status_code == 204

        # Verify cascade
        assert db_session.query(ForumSeed).filter(ForumSeed.id == seed_id).first() is None
        assert db_session.query(ForumPostLink).filter(ForumPostLink.id == link_id).first() is None
        assert db_session.query(ForumPost).filter(ForumPost.id == post_id).first() is None
