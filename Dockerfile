# syntax=docker/dockerfile:1.7

FROM python:3.12-slim-trixie AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN python -m venv /opt/venv

COPY requirements.txt .

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim-trixie AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade liblzma5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app \
        --home-dir /app --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 app ./app
COPY --chown=10001:10001 migrations ./migrations
COPY --chown=10001:10001 run.py ./run.py
COPY --chown=10001:10001 docker-entrypoint.sh /usr/local/bin/project15-entrypoint

RUN chmod 0555 /usr/local/bin/project15-entrypoint \
    && mkdir -p /app/instance \
    && chown 10001:10001 /app/instance

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)"]

ENTRYPOINT ["project15-entrypoint"]

CMD ["gunicorn", "--control-socket", "/tmp/gunicorn-control.sock", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "30", "run:app"]
