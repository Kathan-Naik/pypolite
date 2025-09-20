import json
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from pypolite.fastapi_middleware import PyPoliteFastAPIMiddleware


# --- Configure minimal FastAPI app for tests ---
def create_app():
    app = FastAPI()

    # attach middleware
    PyPoliteFastAPIMiddleware(
        app,
        profanity_words=["idiot", "stupid"],
        endpoints=["/echo/"],
        fields=["message"],
    )

    @app.post("/echo/")
    async def echo(request: Request):
        data = await request.json()
        return JSONResponse({"received": data})

    @app.post("/other/")
    async def other(request: Request):
        data = await request.json()
        return JSONResponse({"received": data})

    return app


# --- Test Case ---
class TestPyPoliteFastAPIMiddleware:
    def setup_method(self):
        """Initialize client before each test"""
        app = create_app()
        self.client = TestClient(app)

    def test_allows_clean_message(self):
        """Test that a clean message passes"""
        response = self.client.post(
            "/echo/",
            json={"message": "Hello friend!"},
        )
        assert response.status_code == 200
        assert response.json()["received"]["message"] == "Hello friend!"

    def test_not_included_endpoint_passes(self):
        """Test that requests to endpoints not in PYPOLITE_ENDPOINTS are allowed"""
        response = self.client.post(
            "/other/",
            json={"message": "You are stupid!"},
        )
        assert response.status_code == 200
        assert response.json()["received"]["message"] == "You are stupid!"

    def test_blocks_profanity(self):
        """Test that a profane message is blocked"""
        response = self.client.post(
            "/echo/",
            json={"message": "You are stupid!"},
        )
        assert response.status_code == 400
        assert "Profanity detected" in response.json()["error"]
