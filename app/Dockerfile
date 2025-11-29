# ---------- Builder ----------
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

# System deps for building optional wheels (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# ---------- Runtime ----------
FROM python:3.11-slim AS runtime

# Security: create non-root user
RUN useradd -m -u 10001 appuser

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Install curl for container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Copy application
COPY app ./app
COPY migrations ./migrations

# Permissions
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000
ENV PYTHONUNBUFFERED=1 \
    GUNICORN_CMD_ARGS="--workers=2 --threads=4 --timeout=60 --bind 0.0.0.0:5000 --access-logfile - --error-logfile -" \
    FLASK_APP="app:create_app()"

HEALTHCHECK --interval=10s --timeout=3s --retries=10 CMD curl -fsS http://127.0.0.1:5000/health || exit 1

CMD ["gunicorn", "app:create_app()"]
