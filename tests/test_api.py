import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app, check_rate_limit, ip_request_timestamps
from app.config import settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limit():
    ip_request_timestamps.clear()
    settings.slack_webhook_url = "https://example.com/mock-slack-webhook"
    yield


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["slack_configured"] is True


def test_widget_js_served():
    response = client.get("/widget.js")
    assert response.status_code == 200
    assert "application/javascript" in response.headers["content-type"]
    assert "biocore-feedback" in response.text


@patch("app.main.send_to_slack", new_callable=AsyncMock)
def test_submit_feedback_success(mock_send):
    mock_send.return_value = None
    payload = {
        "name": "Maria",
        "app": "Genomics Apps",
        "message": "Love the index selector, could we export to CSV?",
        "page_url": "http://localhost:8000/",
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert mock_send.called
    feedback_arg = mock_send.call_args[0][1]
    assert feedback_arg.name == "Maria"
    assert feedback_arg.app == "Genomics Apps"


def test_submit_feedback_validation_error():
    # Empty message
    payload = {
        "name": "Maria",
        "app": "Genomics Apps",
        "message": "",
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 422


@patch("app.main.send_to_slack", new_callable=AsyncMock)
def test_submit_feedback_slack_error(mock_send):
    mock_send.side_effect = RuntimeError("Slack 500 error")
    payload = {
        "name": "Maria",
        "app": "Genomics Apps",
        "message": "Test error",
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 502


def test_submit_feedback_missing_webhook():
    settings.slack_webhook_url = None
    payload = {
        "name": "Maria",
        "app": "Genomics Apps",
        "message": "Test error",
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 503


@patch("app.main.send_to_slack", new_callable=AsyncMock)
def test_rate_limiting(mock_send):
    mock_send.return_value = None
    settings.rate_limit_per_minute = 3
    payload = {
        "name": "Maria",
        "app": "Genomics Apps",
        "message": "Spam test",
    }
    for _ in range(3):
        res = client.post("/api/feedback", json=payload)
        assert res.status_code == 200

    # 4th should be throttled
    res = client.post("/api/feedback", json=payload)
    assert res.status_code == 429
