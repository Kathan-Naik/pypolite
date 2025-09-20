import json
import pytest
from flask import Flask, jsonify, request
from pypolite.flask_middleware import PyPoliteFlaskMiddleware


# --- Minimal Flask app setup for testing ---
@pytest.fixture
def app():
    app = Flask(__name__)

    # Attach PyPolite middleware
    PyPoliteFlaskMiddleware(
        app,
        profanity_words=["idiot", "stupid"],  # profanity list for test
        endpoints=["/echo/"],                 # endpoints to check
        fields=["message"],                   # fields to check
    )

    @app.route("/echo/", methods=["POST"])
    def echo():
        data = request.get_json()
        return jsonify({"received": data})

    @app.route("/other/", methods=["POST"])
    def other():
        data = request.get_json()
        return jsonify({"received": data})

    return app


@pytest.fixture
def client(app):
    return app.test_client()


# --- Tests ---
def test_allows_clean_message(client):
    """Test that a clean message passes"""
    response = client.post(
        "/echo/",
        data=json.dumps({"message": "Hello friend!"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["received"]["message"] == "Hello friend!"


def test_not_included_endpoint_passes(client):
    """Test that requests to endpoints not in PYPOLITE_ENDPOINTS are allowed"""
    response = client.post(
        "/other/",
        data=json.dumps({"message": "You are stupid!"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["received"]["message"] == "You are stupid!"


def test_blocks_profanity(client):
    """Test that a profane message is blocked"""
    response = client.post(
        "/echo/",
        data=json.dumps({"message": "You are stupid!"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "Profanity detected" in response.get_json()["error"]
