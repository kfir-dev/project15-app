def get_metric_line(response_text, metric_name, labels=None):
    expected_prefix = metric_name
    if labels:
        label_text = ",".join(
            f'{name}="{value}"' for name, value in sorted(labels.items())
        )
        expected_prefix = f"{metric_name}{{{label_text}}}"

    return next(
        line
        for line in response_text.splitlines()
        if line.startswith(expected_prefix)
    )


def test_metrics_endpoint_returns_prometheus_content(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.content_type.startswith("text/plain")
    assert "project15_http_requests_total" in response.text
    assert "project15_http_request_duration_seconds" in response.text
    assert "project15_orders_created_total" in response.text


def test_metrics_count_requests_by_route_and_status(client):
    client.get("/health/live")

    response = client.get("/metrics")
    metric_line = get_metric_line(
        response.text,
        "project15_http_requests_total",
        {
            "endpoint": "/health/live",
            "method": "GET",
            "status": "200",
        },
    )

    assert metric_line.endswith(" 1.0")


def test_metrics_use_unmatched_label_for_unknown_routes(client):
    client.get("/not-found")

    response = client.get("/metrics")
    metric_line = get_metric_line(
        response.text,
        "project15_http_requests_total",
        {
            "endpoint": "unmatched",
            "method": "GET",
            "status": "404",
        },
    )

    assert metric_line.endswith(" 1.0")


def test_successful_order_increments_business_metric(client):
    product_response = client.post(
        "/api/products",
        json={
            "name": "Metrics Product",
            "description": "Used for a metrics test",
            "price": "100.00",
            "stock": 2,
        },
    )
    product_id = product_response.get_json()["id"]
    client.post(
        "/api/cart",
        json={
            "user_id": 501,
            "product_id": product_id,
            "quantity": 1,
        },
    )

    order_response = client.post("/api/orders", json={"user_id": 501})
    metrics_response = client.get("/metrics")
    metric_line = get_metric_line(
        metrics_response.text,
        "project15_orders_created_total",
    )

    assert order_response.status_code == 201
    assert metric_line.endswith(" 1.0")
