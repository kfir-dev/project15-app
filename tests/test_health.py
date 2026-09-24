def test_service_info(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "name": "project15-app",
        "status": "running",
    }


def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
    }


def test_readiness(client):
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ready",
        "database": "available",
    }
