# Project 15 - Secure E-Commerce API

Flask backend for the Technion DevOps Final Project 15.

This version provides a clean application factory, database integration, health endpoints, a product API, and automated tests. Cart and order resources will be added in the next phases.

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

## Test and lint

```bash
pytest
flake8 .
```
