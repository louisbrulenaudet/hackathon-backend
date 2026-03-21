# Review Code Quality Command

Run a **code-quality-focused** review: naming conventions, strict type hints, Ruff lint/format compliance, Pydantic v2 usage, duplication/readability, CoreError/error-handling patterns, async/await correctness, and testability. Your reply must be a **plan of suggested changes**: concise, actionable, and structured—not only prose.

## Cursor command usage

This file is a [Cursor custom command](https://docs.cursor.com/context/commands): plain Markdown in `.cursor/commands/`. When the user runs `/review-code-quality` in chat, this content is sent as the prompt.

- **Parameters:** Any text after `/review-code-quality` is scope—e.g. `/review-code-quality naming`, `/review-code-quality types`, `/review-code-quality errors`, `/review-code-quality async`, `/review-code-quality tests`—narrow accordingly. If none given, assume full code quality review for this repo (`app/` + `tests/`).

This command is project-scoped and works with @ mentions and Rules. For a full review use `/review` instead.

## Best practices alignment

- **Naming & conventions** — Follow root conventions in `AGENTS.md`:
  - variables and functions: `snake_case`
  - classes: `PascalCase`
  - constants: `UPPER_SNAKE_CASE`
  - enum names: `PascalCase`
  - enum members: `UPPER_SNAKE_CASE`
  - avoid single-letter names except trivial loop indices
- **Type hints** — Python 3.12+ with comprehensive type hints:
  - annotate every function parameter and return type
  - avoid `Any` unless justified and documented
  - prefer precise types over broad unions when possible
- **Ruff (lint + format)** — Formatting and lint enforced via Ruff:
  - no unused imports/variables
  - consistent style with Ruff formatter and `pyproject.toml`
  - do not leave debug prints or logs in production paths
- **Structure** — Single responsibility per file/function where practical:
  - keep endpoint handlers focused on transport (Pydantic validation and response models)
  - keep business logic in `app/core/*` and reusable helpers in `app/utils/*`
  - errors extend the `CoreError` hierarchy
- **Errors** — App-specific errors should extend `CoreError`:
  - avoid generic `Exception` throws in domain/I/O paths when an app error exists
  - ensure exception handler returns JSON-safe error details
  - log only safe/sanitized details
- **Duplication and dead code** — Remove copy/paste blocks and dead imports; avoid magic strings for finite sets by using enums/constants.

Align with root `AGENTS.md` as the source of truth for conventions and patterns.

## Deep technical review

Conduct a code-quality-only review. Inspect the following and call out violations or improvements.

### Naming conventions

- **Artifacts to check (in this repo):**
  - All Python modules under `app/`
  - Public exports (`app/__init__.py` and any module-level `__all__`)
  - Enums in `app/enums/*`
- **Checks:**
  - Variables and functions follow `snake_case`
  - Classes follow `PascalCase`
  - Constants and enum members follow `UPPER_SNAKE_CASE`
  - Avoid single-letter names except trivial loop indices

### Type hints and type safety

- **Artifacts to check:**
  - All functions/methods under `app/`
  - DTOs in `app/dtos/*`
  - exception classes in `app/exceptions/*`
- **Checks:**
  - every function parameter and return type is annotated
  - avoid `Any` unless justified
  - prefer precise types over broad unions when possible
  - ensure `CoreError.details` is JSON-safe (dict/str/None)

### Ruff format and lint

- **Artifacts to check:**
  - `pyproject.toml` (`tool.ruff.*`) and Ruff configuration
  - All modified/new code in `app/` and `tests/`
- **Checks:**
  - No unused imports/variables
  - Consistent quoting and formatting per Ruff config
  - Avoid unnecessary complexity (extract helpers when it improves readability)
  - No `# noqa` without a short justification

### Duplication and DRY

- **Artifacts to check:**
  - Endpoint handlers in `app/api/v1/endpoints/*`
  - Core logic in `app/core/*`
  - Utilities in `app/utils/*`
  - DTOs in `app/dtos/*`
- **Checks:**
  - Repeated parsing/validation or response-shaping extracted where appropriate
  - Shared constants/limits defined once (or centralized in settings/enums)
  - No dead imports or unused helper functions

### Error handling patterns (CoreError)

- **Artifacts to check:**
  - `app/exceptions/core_exception.py` (`CoreError`)
  - `app/exceptions/*`
  - global exception handler in `app/main.py`
  - where `CoreError` subclasses are raised/caught in core/endpoint code
- **Checks:**
  - raised errors are `CoreError` subclasses in domain/I/O paths
  - exception handler returns JSON-safe `details` (dict/str/None)
  - logging does not leak secrets or sensitive user input
  - avoid generic `Exception` throws when a domain error exists

### Readability and structure

- **Artifacts to check:**
  - Large modules (commonly `app/main.py`, `app/core/*`, `app/utils/*`)
  - Endpoint handlers in `app/api/v1/endpoints/*`
- **Checks:**
  - functions are decomposed into small named helpers when complexity grows
  - imports are grouped (external then internal)
  - avoid circular dependencies
  - prefer docstrings for public functions/classes

### Testability

- **Artifacts to check:**
  - Core logic in `app/core/*` and helper utilities in `app/utils/*`
  - Any async I/O code paths that should be isolated
- **Checks:**
  - Pure logic extracted into testable helpers
  - Dependencies are injected where it improves testing (avoid hard-coded env access in pure functions)
  - Module scope does not maintain unbounded state across requests

### Dead code and string literals

- **Artifacts to check:**
  - `app/enums/*` vs string literals used across the app
  - Magic numbers in endpoints/core logic
- **Checks:**
  - Prefer enums/constants over repeated literals
  - Avoid unreachable code after `return`/`raise`
  - Remove commented-out blocks unless there is an explicit rationale

### Anti-patterns to flag

Explicitly look for these categories and propose better alternatives:

- Enum member casing drift from `UPPER_SNAKE_CASE`
- Module-level side effects or heavy initialization during import (especially in settings)
- Generic `raise Exception(...)` in domain/I/O paths instead of `CoreError` subclasses
- `app/main.py` exception handling relying on fragile string class-name mapping (typos/renames can cause missed status codes)
- `CoreError.details` containing non-JSON-serializable objects or sensitive data
- Blocking I/O inside `async def` route handlers

## Steps

1. **Gather scope** — Full code quality review or a narrower scope if parameters are provided.
2. **Inspect naming and exports** — Verify conventions for all public identifiers and module boundaries.
3. **Inspect type hints** — Look for missing annotations, overly broad types, and drift from DTO definitions.
4. **Inspect Ruff formatting/lint** — Unused imports/vars, formatting consistency, and complexity hotspots.
5. **Inspect Pydantic DTO correctness** — Ensure response models match return values and validators are safe.
6. **Inspect duplication and structure** — DRY, readability, and file/function sizes.
7. **Inspect error handling and async correctness** — CoreError hierarchy, JSON-safe error serialization/logging, and blocking I/O risks.
8. **Compose plan** — Output **Critical / Improvements / Optional**; each item must specify **what**, **where**, and **why**. Include a one-line “no issues” statement for any sub-area with no findings.

## Checklist

- [ ] Scope clear (full `app/` + `tests/` or provided sub-scope)
- [ ] Naming conventions reviewed (AGENTS.md)
- [ ] Type hints and type safety reviewed
- [ ] Ruff format/lint reviewed (Ruff config in `pyproject.toml`)
- [ ] Pydantic DTO correctness reviewed
- [ ] Duplication/DRY and structure reviewed
- [ ] Error handling patterns reviewed (CoreError)
- [ ] Async correctness, retry utilities, and testability reviewed
- [ ] Output structured as Critical / Improvements / Optional with what/where/why

## Review checklist

- **Correctness:** Suggestions do not create logic regressions.
- **Conventions:** Matches project standards (Ruff + strict type hints + CoreError patterns).
- **Quality:** Maintainability improves; testability is not reduced.
- **Actionability:** Every suggestion is implementable (e.g. add missing annotations, extract helper, align DTO return types).
- **Trade-offs:** Mention any trade-offs (e.g. adding helper functions vs readability; stricter types vs brevity).
- **Scope:** Code quality only; defer performance/security to their dedicated reviews.

## Output format

Respond with a **plan** only (no implementation unless the user asks):

1. **Critical** – Must-fix (severe naming violations in public API, `any` without justification, swallowed errors, behavior-affecting dead code).
2. **Improvements** – Worthwhile (extract duplication, tighten type safety, consistent CoreError usage, use enums/constants for finite literals).
3. **Optional** – Nice-to-haves (shorter functions, barrel cleanup). Prefix with **Nit:** for non-blocking polish.

For each item: **what** to change, **where** (file/area), and **why**. If a sub-area has no findings, state it in one line.

