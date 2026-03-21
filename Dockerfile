# syntax=docker/dockerfile:1.7
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTE=1
ENV UV_LINK_MODE=copy
# Defense-in-depth: do not send Pydantic Logfire data (no logfire dependency; harmless if unset).
ENV LOGFIRE_SEND_TO_LOGFIRE=false
ENV LOGFIRE_PYDANTIC_PLUGIN_RECORD=off

# Change the working directory to the `app` directory
WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY ./pyproject.toml ./uv.lock /app/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy the project into the image
COPY ./app /app/app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import sys,urllib.request; url='http://127.0.0.1:8001/api/v1/health'; r=urllib.request.urlopen(url,timeout=3); sys.exit(0 if r.status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

# Hot-reload for local Compose; same dependency set as runtime (optional dev extras are for CI/editor tooling).
FROM runtime AS reload
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8001", "--reload"]
