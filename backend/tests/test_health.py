"""Tests for health and system endpoints."""


def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_check(client):
    response = client.get("/api/v1/system/database")
    assert response.status_code == 200
    assert response.json() == {"database": "ok"}
