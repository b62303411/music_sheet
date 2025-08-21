# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY requirements.txt ./
RUN pip install --upgrade pip wheel && pip install -r requirements.txt
COPY . .

FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /src /app

ENV PORT=8000 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=8 \
    GUNICORN_TIMEOUT=60
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:${PORT}/healthz || exit 1

USER appuser
# Ajuste "app:app" si ton module n’est pas app.py
ENV PORT=8000
CMD ["python", "app.py"]
