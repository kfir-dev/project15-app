from time import perf_counter

from flask import Response, g, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)


def init_metrics(app):
    registry = CollectorRegistry()

    request_count = Counter(
        "project15_http_requests_total",
        "Total HTTP requests handled by the application.",
        ("method", "endpoint", "status"),
        registry=registry,
    )
    request_duration = Histogram(
        "project15_http_request_duration_seconds",
        "HTTP request duration in seconds.",
        ("method", "endpoint"),
        registry=registry,
    )
    orders_created = Counter(
        "project15_orders_created_total",
        "Total orders created successfully.",
        registry=registry,
    )

    app.extensions["project15_metrics"] = {
        "registry": registry,
        "orders_created": orders_created,
    }

    @app.before_request
    def start_request_timer():
        if request.path != "/metrics":
            g.request_started_at = perf_counter()

    @app.after_request
    def record_request_metrics(response):
        if request.path == "/metrics":
            return response

        endpoint = (
            request.url_rule.rule
            if request.url_rule is not None
            else "unmatched"
        )
        method = request.method

        request_count.labels(
            method=method,
            endpoint=endpoint,
            status=str(response.status_code),
        ).inc()

        started_at = getattr(g, "request_started_at", None)
        if started_at is not None:
            request_duration.labels(
                method=method,
                endpoint=endpoint,
            ).observe(perf_counter() - started_at)

        return response

    @app.get("/metrics")
    def prometheus_metrics():
        return Response(
            generate_latest(registry),
            content_type=CONTENT_TYPE_LATEST,
        )
