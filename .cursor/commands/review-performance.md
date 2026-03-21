# Review performance command

Run a **performance-focused** review: algorithmic complexity on hot paths, async I/O correctness (no blocking calls), Pydantic validation overhead, caching strategy (`aiocache`) usage, retry/timeout behavior, middleware cost (e.g. GZip), and memory growth risks. Your reply must be a **plan of suggested changes**: concise, actionable, and structured—not only prose.

## Cursor command usage

This file is a [Cursor custom command](https://docs.cursor.com/context/commands): plain Markdown in `.cursor/commands/`. When the user runs `/review-performance` in chat, this content is sent as the prompt.

- **Parameters:** Any text after `/review-performance` is scope—e.g. `/review-performance endpoints`, `/review-performance aiocache`, `/review-performance httpx`, `/review-performance retry/middleware`—narrow accordingly. If none given, assume full performance review (endpoints/core + caching + outbound I/O + middleware).

This command is project-scoped and works with @ mentions and Rules. For a full review use `/review` instead.

## Best practices alignment

- **Hot-path efficiency** — Prefer O(n) or better in request-critical logic; avoid repeated list scans; avoid sorting inside handlers unless required.
- **Async/event-loop safety** — `async def` paths must not perform blocking I/O (no `time.sleep`, sync file reads, sync network/DB calls); outbound calls use async clients and timeouts.
- **Pydantic validation cost** — Validators are lightweight; avoid expensive computations in `model_validator`/field validators; keep DTOs minimal.
- **Caching strategy (`aiocache`)** — Cache only when consistent/safe; choose correct cache keys + TTLs; prevent unbounded growth.
- **Middleware cost** — Middleware (e.g. `GZipMiddleware`) is configured appropriately (thresholds match expected payload sizes) and does not add unnecessary per-request overhead.

## Deep technical review

Conduct a performance-only review. Inspect the following and call out violations or improvements.

### Algorithmic complexity and data structures

- **Checks:** No O(n²) or worse in request hot paths (e.g. nested loops over large inputs). Avoid repeated linear scans; prefer dict/set lookups. No sorting inside request handlers unless required. Apply pagination/limits for large lists.

### Async I/O and blocking calls

- **Checks:** `async def` paths must not perform blocking I/O (no `time.sleep`, sync file reads, or sync network/DB calls). Outbound HTTP uses `httpx` async with connection reuse and timeouts.

### Pydantic validation overhead

- **Checks:** Validators are lightweight (no CPU-heavy work or outbound calls). DTOs are minimal; avoid constructing large intermediate objects during validation.

### Caching strategy (aiocache)

- **Checks:** Cache keys include all relevant parameters; TTL matches consistency requirements; cached values are safe to store/serialize; avoid unbounded growth.

### Memory growth and long-lived state

- **Checks:** No unbounded in-memory caches or module-level growth. Decorators/retry utilities do not capture request-specific data in global state.

### Anti-patterns to flag

- Blocking calls inside `async def` handlers (sync IO/sleeps).
- Heavy work inside Pydantic validators (CPU-heavy or outbound calls).
- `aiocache` usage with missing TTL (effectively unbounded) or overly broad keys (collisions).
- Outbound `httpx` requests without timeouts (hung requests / latency spikes).

## Steps

1. **Gather scope** — Full performance review or a specific area (endpoints/core hot paths, Pydantic validation, `aiocache`, outbound `httpx`, retry/middleware). Default to full.
2. **Inspect hot paths** — reason about complexity and repeated work; validate limits/pagination.
3. **Inspect async I/O** — identify blocking calls inside `async def`, ensure timeouts and connection reuse for outbound requests.
4. **Inspect Pydantic validation overhead** — ensure validators are lightweight and DTOs are not excessively large/complex.
5. **Inspect caching + retry utilities** — `aiocache` key/TTL correctness, and that retry behavior is not causing retry storms or latency spikes.
6. **Inspect middleware cost** — validate GZip thresholds and that middleware ordering is intentional.
7. **Compose plan** — Critical / Improvements / Optional; each item: **what**, **where**, **why**. One-line "no issues" per sub-area if none.

## Checklist

- [ ] Scope clear
- [ ] Algorithmic complexity and data structures reviewed
- [ ] Async I/O and blocking-call risks reviewed
- [ ] Pydantic validation overhead reviewed
- [ ] Caching strategy (`aiocache`) reviewed
- [ ] Memory and long-lived state reviewed
- [ ] Plan structured as Critical / Improvements / Optional with what/where/why

## Review checklist

- **Correctness:** Complexity claims and caching semantics are accurate; no incorrect optimizations.
- **Quality:** Measurable or reasoned impact (e.g. reduces request latency or CPU usage).
- **Actionability:** Every suggestion is implementable (e.g. extract a hot-path helper, add timeouts, tighten cache keys/TTL).
- **Trade-offs:** Note any (e.g. cache TTL vs freshness, retry aggressiveness vs latency).
- **Scope:** Performance only; defer correctness/security to their reviews.

## Output format

Respond with a **plan** only (no implementation unless the user asks):

1. **Critical** – Must-fix (severe complexity, memory growth risk, broken/unsafe caching, blocking I/O in async paths, missing timeouts causing hung requests).
2. **Improvements** – Worthwhile (better data structure, correct `aiocache` key/TTL strategy, Pydantic validator optimizations, improved retry behavior).
3. **Optional** – Nice-to-haves (minor refactors for latency/CPU, middleware threshold tuning). Prefix with **Nit:** for non-blocking polish.

For each item: **what** to change, **where** (file/area), and **why**. If a sub-area has no findings, state it in one line.
