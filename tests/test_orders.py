def create_product(client, name="USB-C Dock", price="599.00", stock=10):
    response = client.post(
        "/api/products",
        json={
            "name": name,
            "description": f"{name} for order tests",
            "price": price,
            "stock": stock,
        },
    )
    return response.get_json()["id"]


def add_to_cart(client, user_id, product_id, quantity):
    return client.post(
        "/api/cart",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    )


def test_create_order_from_cart(client):
    product_id = create_product(client, stock=5)
    add_to_cart(client, user_id=1, product_id=product_id, quantity=2)

    response = client.post("/api/orders", json={"user_id": 1})

    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["id"] == 1
    assert response_data["user_id"] == 1
    assert response_data["status"] == "pending"
    assert response_data["total_amount"] == "1198.00"
    assert len(response_data["items"]) == 1
    assert response_data["items"][0]["product_id"] == product_id
    assert response_data["items"][0]["product_name"] == "USB-C Dock"
    assert response_data["items"][0]["quantity"] == 2
    assert response_data["items"][0]["subtotal"] == "1198.00"

    cart_response = client.get("/api/cart/1")
    assert cart_response.get_json()["count"] == 0

    products_response = client.get("/api/products")
    assert products_response.get_json()["products"][0]["stock"] == 3


def test_get_order_status(client):
    product_id = create_product(client)
    add_to_cart(client, user_id=1, product_id=product_id, quantity=1)
    create_response = client.post("/api/orders", json={"user_id": 1})
    order_id = create_response.get_json()["id"]

    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == order_id
    assert response.get_json()["status"] == "pending"


def test_create_order_calculates_multiple_items(client):
    first_product_id = create_product(
        client,
        name="USB-C Dock",
        price="100.00",
    )
    second_product_id = create_product(
        client,
        name="Mechanical Keyboard",
        price="250.00",
    )
    add_to_cart(client, 1, first_product_id, 2)
    add_to_cart(client, 1, second_product_id, 1)

    response = client.post("/api/orders", json={"user_id": 1})

    assert response.status_code == 201
    assert response.get_json()["total_amount"] == "450.00"
    assert len(response.get_json()["items"]) == 2


def test_create_order_rejects_empty_cart(client):
    response = client.post("/api/orders", json={"user_id": 1})

    assert response.status_code == 400
    assert response.get_json()["message"] == "Cart is empty"


def test_create_order_rejects_invalid_user_id(client):
    response = client.post("/api/orders", json={"user_id": 0})

    assert response.status_code == 400
    assert response.get_json()["message"] == "User ID must be a positive integer"


def test_create_order_checks_current_stock(client):
    product_id = create_product(client, stock=3)
    add_to_cart(client, user_id=1, product_id=product_id, quantity=3)
    client.put(
        f"/api/products/{product_id}",
        json={
            "name": "USB-C Dock",
            "description": "Stock changed after cart update",
            "price": "599.00",
            "stock": 2,
        },
    )

    response = client.post("/api/orders", json={"user_id": 1})

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        f"Insufficient stock for product {product_id}"
    )
    assert client.get("/api/cart/1").get_json()["count"] == 1


def test_get_unknown_order_returns_404(client):
    response = client.get("/api/orders/999")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Order not found"
