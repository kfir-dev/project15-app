# Project 15 - Secure E-Commerce API

Flask backend for the Technion DevOps Final Project 15.

This version provides a clean application factory, database integration, health endpoints, product, cart, order, security report APIs, Prometheus metrics, and automated tests.

## Requirements

- Python 3.12
- PostgreSQL 15+ for the final environment

SQLite is used as the local default so the application and tests can run before the PostgreSQL container is introduced.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

## Run

```bash
flask --app run.py run --debug
```

The API listens on `http://127.0.0.1:5000`.

Available endpoints:

- `GET /`
- `GET /health/live`
- `GET /health/ready`
- `GET /api/products`
- `POST /api/products`
- `PUT /api/products/<product_id>`
- `DELETE /api/products/<product_id>`
- `POST /api/cart`
- `GET /api/cart/<user_id>`
- `DELETE /api/cart/<user_id>/item/<product_id>`
- `POST /api/orders`
- `GET /api/orders/<order_id>`
- `GET /api/security/sbom`
- `GET /api/security/scan-report`
- `GET /metrics`

`POST /api/cart` expects `user_id`, `product_id`, and `quantity`. Authentication is outside the current project phase, so the user ID is supplied explicitly.

`POST /api/orders` expects `user_id`. It creates an order from that user's cart, stores product and price snapshots, reduces stock, and clears the cart.

Security report endpoints read real JSON artifacts from `SECURITY_REPORTS_DIR`. The pipeline will write `sbom.json` and `scan-report.json` to that directory. Until a report exists, the matching endpoint returns `404` instead of fabricated data.

The Prometheus endpoint exposes low-cardinality HTTP request counters and latency histograms using route templates, plus a business counter for successfully created orders:

- `project15_http_requests_total`
- `project15_http_request_duration_seconds`
- `project15_orders_created_total`

## Test and lint

```bash
pytest
flake8 .
```

## Docker Compose

The local container path runs the API with Gunicorn as a non-root user and uses PostgreSQL 15.19. Database migrations run automatically before the API starts.

```bash
cp .env.example .env
docker compose config
docker compose build
docker compose up -d
docker compose ps
```

Runtime checks:

```bash
curl --fail http://127.0.0.1:5000/health/live
curl --fail http://127.0.0.1:5000/health/ready
curl --fail http://127.0.0.1:5000/metrics
docker compose exec database psql -U project15 -d project15 -c "SELECT version();"
docker compose exec app id
```

Stop the environment without deleting its database volume:

```bash
docker compose down
```

Database connections are checked when reused. During a PostgreSQL outage, API
database operations return `503` with `{"message":"Database unavailable"}`;
readiness also returns `503`. Requests can resume when PostgreSQL is ready.

Delete the local database volume only when a full reset is intended:

```bash
docker compose down --volumes
```

Run Hadolint using its pinned container image:

```bash
docker run --rm -i hadolint/hadolint:v2.14.0-debian < Dockerfile
```
