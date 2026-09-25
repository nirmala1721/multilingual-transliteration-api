import pytest

from app import create_app


@pytest.fixture
def client():

    app = create_app()

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_valid_telugu_request(client):

    response = client.post(
        "/api/v1/transliterate/text",
        json={
            "text": "తిన్నావా?"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["language"] == "telugu"
    assert data["data"]["transliterated_text"] == "tinnava?"


def test_valid_english_request(client):

    response = client.post(
        "/api/v1/transliterate/text",
        json={
            "text": "Hello world"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["language"] == "english"
    assert data["data"]["transliterated_text"] == "Hello world"


def test_missing_text(client):

    response = client.post(
        "/api/v1/transliterate/text",
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Request body is required"

def test_empty_text(client):

    response = client.post(
        "/api/v1/transliterate/text",
        json={
            "text": ""
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


def test_wrong_language(client):

    response = client.post(
        "/api/v1/transliterate/text",
        json={
            "text": "నమస్కారం",
            "language": "hindi"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "mismatch" in data["message"].lower()


def test_unsupported_language(client):

    response = client.post(
        "/api/v1/transliterate/text",
        json={
            "text": "നമസ്കാരം"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "provider" in data["message"].lower()