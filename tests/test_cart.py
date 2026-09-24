def create_product(client, stock=10):
    response = client.post(
        "/api/products",
        json={
            "name": "USB-C Dock",
            "description": "Docking station for laptops",
            "price": "599.00",
            "stock": stock,
        },
    )
    return response.get_json()["id"]


def test_get_empty_cart(client):
    response = client.get("/api/cart/1")

    assert response.status_code == 200
    assert response.get_json() == {
        "user_id": 1,
        "items": [],
        "count": 0,
        "total": "0.00",
    }


def test_add_item_to_cart(client):
    product_id = create_product(client)

    response = client.post(
        "/api/cart",
        json={"user_id": 1, "product_id": product_id, "quantity": 2},
    )

    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["user_id"] == 1
    assert response_data["product_id"] == product_id
    assert response_data["quantity"] == 2
    assert response_data["product"]["name"] == "USB-C Dock"
    assert response_data["subtotal"] == "1198.00"


def test_add_existing_item_increases_quantity(client):
    product_id = create_product(client)
    payload = {"user_id": 1, "product_id": product_id, "quantity": 2}

    first_response = client.post("/api/cart", json=payload)
    second_response = client.post("/api/cart", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 200
    assert second_response.get_json()["quantity"] == 4

    cart_response = client.get("/api/cart/1")
    assert cart_response.get_json()["count"] == 1
    assert cart_response.get_json()["total"] == "2396.00"


def test_add_item_rejects_invalid_quantity(client):
    product_id = create_product(client)

    response = client.post(
        "/api/cart",
        json={"user_id": 1, "product_id": product_id, "quantity": 0},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Quantity must be a positive integer"


def test_add_item_rejects_unknown_product(client):
    response = client.post(
        "/api/cart",
        json={"user_id": 1, "product_id": 999, "quantity": 1},
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"


def test_add_item_rejects_quantity_above_stock(client):
    product_id = create_product(client, stock=3)

    response = client.post(
        "/api/cart",
        json={"user_id": 1, "product_id": product_id, "quantity": 4},
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Requested quantity exceeds product stock"
    )


def test_carts_are_separated_by_user(client):
    product_id = create_product(client)
    client.post(
        "/api/cart",
        json={"user_id": 1, "product_id": product_id, "quantity": 1},
    )

    first_cart = client.get("/api/cart/1").get_json()
    second_cart = client.get("/api/cart/2").get_json()

    assert first_cart["count"] == 1
    assert second_cart["count"] == 0


def test_remove_item_from_cart(client):
    product_id = create_product(client)
    client.post(
        "/api/cart",
        json={"user_id": 1, "product_id": product_id, "quantity": 1},
    )

    response = client.delete(f"/api/cart/1/item/{product_id}")

    assert response.status_code == 204
    assert response.data == b""
    assert client.get("/api/cart/1").get_json()["count"] == 0


def test_remove_unknown_cart_item_returns_404(client):
    response = client.delete("/api/cart/1/item/999")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Cart item not found"
