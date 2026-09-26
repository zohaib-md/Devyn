"""API tests: POST validation and GET 404. No network."""
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_post_empty_topic_returns_400():
    client = APIClient()
    res = client.post("/api/runs", {"topic": ""}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_post_too_long_topic_returns_400():
    client = APIClient()
    res = client.post("/api/runs", {"topic": "x" * 201}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_post_valid_enqueues_and_returns_201():
    client = APIClient()
    with patch("research.api.views.async_task") as mock_task:
        res = client.post("/api/runs", {"topic": "Android + AI"}, format="json")
    assert res.status_code == 201
    assert "id" in res.data
    assert res.data["status"] == "queued"
    mock_task.assert_called_once()


@pytest.mark.django_db
def test_get_missing_run_returns_404():
    client = APIClient()
    res = client.get("/api/runs/999999")
    assert res.status_code == 404
