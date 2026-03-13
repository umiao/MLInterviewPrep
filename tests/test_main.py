"""Tests for FastAPI app skeleton and health endpoint (T-P0-7)."""


class TestHealthEndpoint:
    """Health check endpoint tests."""

    def test_health_returns_200(self, test_client):
        """GET /api/health returns 200."""
        resp = test_client.get("/api/health")
        assert resp.status_code == 200

    def test_health_returns_status_ok(self, test_client):
        """GET /api/health returns {status: ok}."""
        resp = test_client.get("/api/health")
        assert resp.json() == {"status": "ok"}

    def test_health_content_type_json(self, test_client):
        """Health endpoint returns JSON content type."""
        resp = test_client.get("/api/health")
        assert resp.headers["content-type"] == "application/json"


class TestCORSMiddleware:
    """CORS middleware configuration tests."""

    def test_cors_allows_configured_origin(self, test_client):
        """CORS headers present for configured origin."""
        resp = test_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_allows_credentials(self, test_client):
        """CORS allows credentials."""
        resp = test_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("access-control-allow-credentials") == "true"

    def test_cors_allows_all_methods(self, test_client):
        """CORS allows all HTTP methods."""
        resp = test_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "DELETE",
            },
        )
        assert "DELETE" in resp.headers.get("access-control-allow-methods", "")


class TestAppConfiguration:
    """App-level configuration tests."""

    def test_app_title(self, test_client):
        """App has correct title in OpenAPI schema."""
        resp = test_client.get("/openapi.json")
        assert resp.status_code == 200
        assert resp.json()["info"]["title"] == "MLE Interview Prep"

    def test_api_prefix_on_routes(self, test_client):
        """All routes are under /api prefix."""
        resp = test_client.get("/openapi.json")
        paths = resp.json()["paths"]
        for path in paths:
            assert path.startswith("/api/"), f"Route {path} not under /api prefix"

    def test_unknown_route_returns_404(self, test_client):
        """Unknown route returns 404."""
        resp = test_client.get("/api/nonexistent")
        assert resp.status_code == 404
