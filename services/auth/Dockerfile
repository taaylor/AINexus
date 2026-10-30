FROM ghcr.io/astral-sh/uv:0.13.3-python3.12-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-default-groups \
    --group auth \
    --no-install-project \
    --no-editable

COPY services/auth/src ./services/auth/src
COPY services/trace ./services/trace


FROM python:3.12-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/services \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --system authuser \
    && useradd \
        --system \
        --gid authuser \
        --no-create-home \
        --shell /usr/sbin/nologin \
        authuser

WORKDIR /app

COPY --from=builder --chown=authuser:authuser /app/.venv /app/.venv
COPY --from=builder --chown=authuser:authuser /app/services/auth/src /app/services/auth/src
COPY --from=builder --chown=authuser:authuser /app/services/trace /app/services/trace

USER authuser:authuser

EXPOSE 8000

ENTRYPOINT ["uvicorn", \
    "auth.src.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--log-level", "info", \
    "--log-config", "/app/services/auth/src/common/json/logging.json", \
    "--access-log", \
    "--timeout-graceful-shutdown", "10", \
    "--lifespan", "on", \
    "--workers", "1"]
