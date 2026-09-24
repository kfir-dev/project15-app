def test_products_list_is_empty(client):
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.get_json() == {
        "products": [],
        "count": 0,
    }


def test_create_product(client):
    response = client.post(
        "/api/products",
        json={
            "name": "Mechanical Keyboard",
            "description": "Compact keyboard for developers",
            "price": "349.90",
            "stock": 12,
        },
    )

    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["id"] == 1
    assert response_data["name"] == "Mechanical Keyboard"
    assert response_data["price"] == "349.90"
    assert response_data["stock"] == 12

    list_response = client.get("/api/products")
    assert list_response.status_code == 200
    assert list_response.get_json()["count"] == 1


def test_create_product_requires_name(client):
    response = client.post(
        "/api/products",
        json={
            "price": "49.90",
            "stock": 5,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Product name is required"


def test_create_product_rejects_invalid_price(client):
    response = client.post(
        "/api/products",
        json={
            "name": "USB-C Cable",
            "price": "invalid",
            "stock": 5,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Product price must be a valid number"


def test_create_product_rejects_negative_stock(client):
    response = client.post(
        "/api/products",
        json={
            "name": "USB-C Dock",
            "price": "599.00",
            "stock": -1,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Product stock must not be negative"
