# Review Configuration Command

Run a **configuration-focused** review: environment and secrets handling, Docker/Compose + uv lockfile parity, Pydantic settings contract, Ruff configuration, and dev/prod wiring consistency. Your reply must be a **plan of suggested changes**: concise, actionable, and structured—not only prose.

## Cursor command usage

This file is a [Cursor custom command](https://docs.cursor.com/context/commands): plain Markdown in `.cursor/commands/`. When the user runs `/review-configuration` in chat, this content is sent as the prompt.

- **Parameters:** Any text after `/review-configuration` is scope—e.g. `/review-configuration env only`, `/review-configuration docker`, `/review-configuration ruff/pydantic`, `/review-configuration ports/healthcheck`—narrow accordingly. If none given, assume all configuration (env/secrets, Docker/Compose, uv/Ruff/Pydantic, build modes, parity).

This command is project-scoped and works with @ mentions and Rules. For a full review use `/review` instead.

## Best practices alignment

- **Secrets** — Never committed and never embedded into build artifacts. Secrets should flow via `.env` / Compose environment only. `.env.template` must be placeholder-only.
- **Environment** — Clear split between:
  - required runtime values (defined in `app/core/config.py`): `APP_NAME`, `API_KEY`, `API_CLIENT`
  - operational values (ports/host used by server + docker): `8000` for local dev expectations, `8001` for production/container expectations
  - optional tuning values (only if present in code; ensure they are documented in `.env.template`)
- **Ruff/typing parity** — Single source of truth at `pyproject.toml` (Ruff rules). Make sure Docker installs runtime deps deterministically via `uv sync --frozen --no-dev` and does not depend on dev-only tooling.
- **Docker/runtime parity** — Local `make dev` behavior (port 8000) should match container runtime behavior (Docker `CMD`/`HEALTHCHECK`, port 8001) so config changes don’t “work locally but fail in Docker”.

Align with root `AGENTS.md` for environment and port allocation guidance.

## Deep technical review

Conduct a configuration-only review. Inspect the following and call out violations or improvements.

### Environment and secrets

- **Artifacts:**
  - `.env.template`
  - `.env` (must contain real values; must be gitignored)
  - `.gitignore` (env + secrets entries)
  - `.dockerignore` (must exclude env files from Docker build context)
  - `compose.yaml` (`env_file` usage for the `app` service`)
  - Env consumption in code:
    - `app/core/config.py` (Pydantic Settings: `APP_NAME`, `API_KEY`, `API_CLIENT`)
    - `app/main.py` (`load_dotenv()` for local development)

- **Checks:**
  - `.env.template` lists required variables with placeholder/descriptions only (no real secrets).
  - `.env` is never committed, and Compose uses it via `env_file`.
  - `.dockerignore` prevents `.env*` files from being copied into the image (important because Docker uses `COPY . .` in the prerelease stage).
  - Settings enforces a correct env contract (missing/empty required values are caught early).
  - `.env` loading behavior is deliberate: local dev works, container runtime does not assume a `.env` file exists inside the image.
  - Numeric envs are parsed robustly (if any numeric tuning envs exist).

- **Anti-patterns to flag (repo-specific):**
  - Silent fallback defaults for required secrets (e.g. defaulting `API_KEY` / `API_CLIENT` to empty strings can mask misconfiguration).
  - `load_dotenv()` or Settings initialization relying on `.env` being present inside the container instead of being injected via `compose.yaml` / environment variables.
  - Missing env contract documentation: `.env.template` or README doesn’t mention optional tuning envs (if any) used by the code.

### Docker Compose (compose.yaml)

- **Artifacts:**
  - `compose.yaml` (service `app`, `env_file`, `ports`, `volumes`, `networks`)

- **Checks:**
  - `env_file: .env` is used for the `app` service (secrets are injected at runtime, not baked in)
  - Container port mapping matches the server port expected by `Dockerfile`/`make prod` (container listens on `8001`)
  - Volumes are appropriate for the target environment (dev hot-reload vs prod immutability)
  - Any healthcheck/ready mechanism (if added) targets the correct FastAPI route

- **Anti-patterns to flag:**
  - Hardcoded secrets in `compose.yaml` or baked into image layers
  - Port drift between `compose.yaml`, `Dockerfile`, and Makefile targets
  - Mounting the source tree into containers in production-like runs

### Dockerfile (build stages + runtime)

- **Artifacts:**
  - `Dockerfile` (uv sync frozen install, runtime entrypoint, HEALTHCHECK)

- **Checks:**
  - Deterministic installs: Docker uses `uv sync --frozen --no-dev` and therefore expects `uv.lock` to be committed and up to date.
  - Runtime entrypoint uses the expected app import path (currently `uvicorn app.main:app`) and listens on the expected port (8001).
  - HEALTHCHECK points at the correct FastAPI route and port (currently `/api/v1/health` on `8001`).
  - Required OS dependencies for healthchecks exist (e.g. `curl` is installed when HEALTHCHECK relies on it).

- **Anti-patterns to flag:**
  - Secrets copied into the image due to missing `.dockerignore` coverage for `.env*`.
  - HEALTHCHECK fails due to missing `curl` or incorrect route/port.

### Ruff configuration (lint/format)

- **Artifacts:**
  - `pyproject.toml` (`tool.ruff.*` sections)
  - Makefile targets (`make check`, `make format`)

- **Checks:**
  - Local `make check`/`make format` uses the same Ruff rules as CI/Docker expectations
  - No `# noqa`/suppression patterns hide correctness issues

### Pydantic settings configuration

- **Artifacts:**
  - `app/core/config.py` (`Settings` + Pydantic Settings config)
  - `app/main.py` (`load_dotenv()`)

- **Checks:**
  - Required env vars are enforced (avoid silent empty defaults for secrets unless intentional)
  - `.env` is loaded for local dev, while Docker/compose injects env at runtime

### Build modes and reproducibility

- **Artifacts:**
  - `uv.lock` and `pyproject.toml` (dependency pinning)
  - `Dockerfile` dependency install command (`uv sync --frozen --no-dev`)
  - Makefile targets (`make dev`, `make prod`, `make check`, `make format`, `make test`)
  - `compose.yaml` (container command + ports)

- **Checks:**
  - Docker installs runtime dependencies deterministically from `uv.lock`
  - Local development does not accidentally depend on dev-only dependencies that are excluded in Docker
  - Host/port expectations are consistent (local dev typically uses 8000; containers typically use 8001)

### API wiring that is configuration-like

- **Artifacts:**
  - `app/main.py`

- **Checks:**
  - Middleware order is intentional (e.g. CORS then GZip) and matches what routes expect
  - Router prefixing is consistent (`/api/v1`) with endpoint paths (e.g. `/api/v1/ping`, `/api/v1/health`)
  - Global exception handler maps `CoreError` to the expected HTTP status codes and returns JSON-safe payloads

## Steps

1. **Gather scope** — Full configuration review or narrower scope if parameters are provided.
2. **Inspect env and secrets** — `.env.template`, `.env` usage in `compose.yaml`, `.gitignore`, `.dockerignore`, and env consumption in `app/core/config.py` and `app/main.py`.
3. **Inspect Docker/Compose alignment** — `Dockerfile` + `compose.yaml` + HEALTHCHECK + port consistency.
4. **Inspect Ruff + Pydantic settings** — `pyproject.toml` (Ruff config) and `app/core/config.py` (Pydantic Settings contract).
5. **Inspect build modes and reproducibility** — `uv.lock` and frozen installs (`uv sync --frozen --no-dev`).
6. **Compose plan** — Output **Critical / Improvements / Optional** with **what/where/why** and a one-line “no issues” statement for any sub-area with no findings.

## Checklist

- [ ] Scope clear
- [ ] Secrets handling reviewed (`.env`, `.env.template`, `.gitignore`, `.dockerignore`, `compose.yaml`)
- [ ] Dockerfile reviewed (uv sync frozen installs, runtime entrypoint, HEALTHCHECK)
- [ ] Pydantic Settings contract reviewed (`app/core/config.py`)
- [ ] Ruff configuration reviewed (`pyproject.toml`, `make check`, `make format`)
- [ ] Build modes + reproducibility reviewed (`uv.lock`, `uv sync --frozen --no-dev`)
- [ ] Middleware/Router/Error wiring reviewed (`app/main.py`)
- [ ] Output structured as Critical / Improvements / Optional with what/where/why

## Context usage

- Use `@file` for config files: `compose.yaml`, `Dockerfile`, `.env.template`, `.gitignore`, `.dockerignore`, `pyproject.toml`, `uv.lock`, `app/core/config.py`, `app/main.py`.
- Use `@code` for env/parsing snippets:
  - `Settings` initialization + env validation in `app/core/config.py`
  - `load_dotenv()` behavior in `app/main.py`
- Use `@git` when checking recent configuration changes for quality regressions.

If context is insufficient, suggest which config files or `@file` references to add.

## Review checklist

- **Correctness:** Configuration claims match actual files and code paths.
- **Conventions:** Changes align with `AGENTS.md` (ports, env contract expectations).
- **Quality:** Improves clarity and reduces misconfiguration risk.
- **Actionability:** Every suggestion is implementable (e.g. update `.env.template`, tighten env validation, add `.dockerignore` coverage, ensure Docker and local parity).
- **Trade-offs:** Note any (e.g. stricter env validation may require code changes).
- **Scope:** Configuration only; defer performance/security to their dedicated reviews.

## Output format

Respond with a **plan only** (no implementation unless the user asks):

1. **Critical** — Must-fix (severe configuration issues that break CI/build/runtime or weaken correctness/security).
2. **Improvements** — Worthwhile (documentation of env contract, clearer Ruff/Pydantic rules, compatibility/parity tweaks).
3. **Optional** — Nice-to-haves (minor tidy and comments). Prefix with **Nit:** for non-blocking polish.

For each item: **what** to change, **where** (file/area), and **why**. If a sub-area has no findings, state it in one line.

