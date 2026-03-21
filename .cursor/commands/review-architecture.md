# Review Architecture Command

Run an **architecture-focused** review of this repo: layout and layering, dependency direction, module coupling/cohesion, and build pipeline boundaries. Your reply must be a **plan of suggested changes**: concise, actionable, and structured—not only prose.

## Cursor command usage

This file is a [Cursor custom command](https://docs.cursor.com/context/commands): plain Markdown in `.cursor/commands/`. When the user runs `/review-architecture` in chat, this content is sent as the prompt.

- **Parameters:** Any text after `/review-architecture` is additional scope—e.g. `/review-architecture endpoints wiring`, `/review-architecture error handling`, `/review-architecture Docker/compose parity`—narrow the review accordingly. If none given, assume full architecture review for this repo.

This command is project-scoped and works with @ mentions and Rules. For broader reviews use `/review` instead.

## Best practices alignment

- **Dependency direction** — Endpoints (HTTP) depend on core logic; core logic depends on dtos/enums/errors/utils; utils are as independent as possible (prefer “leaf” utilities).
- **Single responsibility** — Each module has one clear purpose:
  - `app/api/v1/endpoints/*`: FastAPI route handlers (HTTP wiring only)
  - `app/api/v1/router.py`: API router composition (`include_router`)
  - `app/main.py`: FastAPI app wiring (middleware, router include, global exception handler)
  - `app/core/*`: Application configuration and business logic orchestration (no HTTP concerns)
  - `app/dtos/*`: Pydantic DTOs (request/response models)
  - `app/enums/*`: Stable enums (e.g. `ErrorCodes`)
  - `app/exceptions/*`: `CoreError` subclasses + domain/I/O error types
  - `app/utils/*`: Small reusable helpers (e.g. `retry`, `async_retry`)
- **Public API surface** — Use Python package exports (`__all__`, `__init__.py`) to define what is public; avoid fragile deep imports across internal modules.
- **Cohesion and coupling** — Avoid “god” files; keep domain logic out of endpoints; avoid core modules importing unrelated HTTP-layer details.
- **Build pipeline boundaries** — Ensure Docker runtime entrypoints, ports, and healthcheck routes match the app wiring and local scripts.

Align with root `AGENTS.md` for architectural expectations and conventions.

## Deep technical review

Conduct an architecture-only review. Inspect the following and call out violations or improvements.

### Layout and layering (this repo)

- **Artifacts:**
  - `app/main.py` (FastAPI app wiring + middleware + global exception handler)
  - `app/api/v1/router.py` (router composition)
  - `app/api/v1/endpoints/*` (endpoint handlers)
  - `app/core/*` (settings + core logic)
  - `app/dtos/*` (Pydantic models)
  - `app/enums/*` (error codes, enums)
  - `app/exceptions/*` (`CoreError` subclasses)
  - `app/utils/*` (small helper utilities)
  - `tests/` (API/business logic coverage expectations)
- **Checks:**
  - Endpoint handlers remain thin: validate/shape via Pydantic, then delegate to core logic (or keep logic minimal when the repo is small).
  - Core modules do not depend on FastAPI request/response types.
  - DTOs contain schema/typing only; they do not include transport logic.
  - Errors are thrown as `CoreError` subclasses and serialized in a consistent shape by `app/main.py`.
  - Middleware configuration stays in `app/main.py` and does not duplicate error/validation logic.

### Dependency direction and import graph

This repo is a single Python package (no monorepo workspaces). Instead:

- **Artifacts:**
  - Import graph across `app/`
  - `__init__.py` + `__all__` exports (public surface definition)
- **Checks:**
  - No reverse dependency direction (e.g. `app/utils/*` importing from `app/api/*` or `app/main.py`, unless clearly justified).
  - No circular imports between modules (reason about import graph; flag cycles).
  - Shared foundations (`enums/*`, `dtos/*`, `exceptions/*`, `utils/*`) are reused by higher layers without forcing tighter coupling.

### Build pipeline task graph and caching (Docker + uv)

- **Artifacts:**
  - `Dockerfile` (uv sync with frozen lock, runtime entrypoint, healthcheck)
  - `compose.yaml` (service command + ports + env injection)
  - `Makefile` + `make/*.mk` (dev/prod/test/check/format entrypoints)
  - `uv.lock` + `pyproject.toml` (dependency pinning source of truth)
- **Checks:**
  - Docker uses `uv sync --frozen` and runs an entrypoint consistent with your app (`uvicorn app.main:app`).
  - Healthcheck path/port matches FastAPI routing and `Dockerfile` CMD/HEALTHCHECK.
  - Local dev (`make dev` / Makefile dev target) and Docker production (`make prod` / Docker CMD) agree on host/port expectations.
  - CI/quality gates referenced in Makefile (e.g. `make check`, `make format`) are not accidentally skipped in Docker where they should exist.

### Public API surface and exports

- **Artifacts:**
  - `app/__init__.py`, `app/api/v1/endpoints/__init__.py`, `app/api/v1/__init__.py` (if present)
  - `__all__` in key modules (when defined)
- **Checks:**
  - Exports are explicit and minimal (avoid wildcard re-exports of internal helpers unless intentional).
  - Callers don’t rely on brittle internal file structure when stable exports exist.

### App vs internal boundaries (module coupling/cohesion)

- **Artifacts:**
  - `app/main.py` vs `app/api/v1/endpoints/*`
  - `app/api/v1/endpoints/*` vs `app/core/*`
  - `app/utils/*` vs everything else
- **Checks:**
  - HTTP concerns do not creep into core modules (no FastAPI `Request`, `Response`, dependency injection types inside core).
  - Global wiring stays in `app/main.py` (middleware order, router include, exception handler).
  - Errors are defined close to the failure domain: transport errors stay in `exceptions/` or are wrapped into `CoreError` subclasses.

### Anti-patterns to flag

- Circular imports between modules (direct or via `__init__.py` re-exports).
- Endpoints duplicating core logic (when core modules exist) or core modules calling HTTP-layer utilities.
- Exceptions not extending `CoreError`, or inconsistent error serialization contracts.
- Global side effects in import time (e.g. heavy initialization in module scope) that should be moved behind settings/lazy initialization.
- Build/runtime drift: Docker port/healthcheck/entrypoint not matching the actual routing in the app.
- Brittle deep imports that couple modules to specific file layout.

## Steps

1. **Gather scope** — Full architecture review, or narrow scope based on `/review-architecture <scope>`.
2. **Inspect layout and layering** — Verify module responsibilities in `app/`.
3. **Inspect dependency direction** — Trace imports across `app/api/`, `app/core/`, `app/utils/`, `app/exceptions/`, `app/dtos/`, `app/enums/`.
4. **Inspect exports** — Ensure public surface is minimal and stable (prefer explicit `__all__` over deep imports).
5. **Inspect build pipeline** — Compare `Dockerfile`, `compose.yaml`, and Makefile targets for parity (ports, entrypoints, healthcheck paths).
6. **Review cohesion/coupling hotspots** — Identify any “god modules” (common candidates: `app/main.py`, `app/core/config.py`).
7. **Compose plan** — Critical / Improvements / Optional; each item must specify **what**, **where**, **why**. If a sub-area has no findings, state it in one line.

## Checklist

- [ ] Scope clear (full repo or parameter-narrowed)
- [ ] Root `AGENTS.md` consulted for architectural expectations
- [ ] Module responsibilities reviewed (endpoints/core/dtos/enums/exceptions/utils/main)
- [ ] Dependency direction checked (no reverse deps, no cycles)
- [ ] Public API surface reviewed (`__all__` / exports)
- [ ] Build pipeline reviewed (Dockerfile + compose.yaml + Makefile)
- [ ] Global exception + middleware wiring reviewed for boundary correctness
- [ ] Plan structured as Critical / Improvements / Optional with what/where/why

## Context usage

- Use `@file` for: `app/main.py`, `app/api/v1/router.py`, `app/api/v1/endpoints/*`, `app/core/*`, `app/dtos/*`, `app/enums/*`, `app/exceptions/*`, `app/utils/*`, `Dockerfile`, `compose.yaml`, `Makefile`, `make/*.mk`, `AGENTS.md`.
- Use `@code` for: dependency/import snippets, global middleware/exception handler mappings, or export statements.
- Use `@git` when reviewing recent architectural changes for regressions.

If context is insufficient, suggest which `@file` references to add.

## Review checklist

- **Correctness:** Dependency direction and layering suggestions don’t break module contracts.
- **Conventions:** Align with `AGENTS.md` naming and structure.
- **Quality:** Coupling decreases; cohesion increases; responsibilities become clearer.
- **Actionability:** Every suggestion is implementable (e.g. move logic to `app/core/*`, extract util, tighten exports, align Docker entrypoints).
- **Trade-offs:** Mention trade-offs (e.g. extra files vs easier navigation).
- **Scope:** Architecture only; defer performance/security to dedicated reviews.

## Output format

Respond with a **plan only** (no implementation unless the user asks):

1. **Critical** – Architecture violations (cycles, wrong dependency direction, broken build/runtime wiring, major boundary leaks).
2. **Improvements** – Worthwhile changes (clearer layering, cleaner public API surface, improved cohesion/coupling).
3. **Optional** – Nice-to-haves (minor refactors, documentation, small module renames). Prefix with **Nit:** for non-blocking polish.

For each item: **what** to change, **where** (file/area), and **why**. If a sub-area has no findings, state it in one line.

