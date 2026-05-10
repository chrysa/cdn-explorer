# ── Stage 1: deps ─────────────────────────────────────────────────────────────
FROM python:3.14-slim AS deps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY api/ ./api/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[dev]"

# ── Stage 2: production ────────────────────────────────────────────────────────
FROM python:3.14-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY api/ /app/api/

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 3: dev ──────────────────────────────────────────────────────────────
FROM deps AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY api/ /app/api/

CMD ["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ── Stage 4: test ─────────────────────────────────────────────────────────────
FROM deps AS test

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY api/ /app/api/
COPY tests/ /app/tests/
COPY pyproject.toml /app/

CMD ["pytest", "--cov=api", "--cov-report=xml", "-v"]
