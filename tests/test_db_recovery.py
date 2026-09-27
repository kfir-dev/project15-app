from unittest.mock import patch

from sqlalchemy.exc import OperationalError

from app.extensions import db


def database_disconnect():
    return OperationalError("SELECT 1", {}, OSError("connection refused"))


def test_order_read_reports_database_outage(client):
    with patch.object(db.session, "get", side_effect=database_disconnect()):
        response = client.get("/api/orders/1")

    assert response.status_code == 503
    assert response.get_json() == {"message": "Database unavailable"}


def test_product_create_reports_database_outage(client):
    with patch.object(db.session, "commit", side_effect=database_disconnect()):
        response = client.post(
            "/api/products",
            json={"name": "Test", "price": "10.00", "stock": 1},
        )

    assert response.status_code == 503
    assert response.get_json() == {"message": "Database unavailable"}
    assert client.get("/api/products").get_json()["count"] == 0
