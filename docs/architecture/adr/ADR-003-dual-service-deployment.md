# ADR-003: Dual-Service Deployment Model with Shared Image and Separate Entry Points

**Status:** Accepted

**Context:** The system comprises two long-running workloads with fundamentally different runtime characteristics: a FastAPI HTTP server (request-response, short-lived connections) and a Telegram bot with a polling loop (long-running event-driven process). Additionally, a parser runner operates as a periodic background task within the bot process. The system is deployed on Render (production) and via Docker Compose (development) and must support starting one or both components.

**Decision:**

1. **Separate OS processes**: The API and bot run as distinct OS processes (threads in `--all` mode, separate containers in deployment). In Docker Compose, `api` and `bot` are separate services sharing the same Docker image. On Render, the web service runs the API and the worker service runs the bot.
2. **Single codebase, single image**: Both workloads use the same Docker image (`Dockerfile`) and the same `main.py` entry point, differentiated by CLI flags (`--api-only`, `--bot-only`, `--all`).
3. **Shared database**: Both services connect to the same SQLite (dev) or PostgreSQL (prod) database, coordinated via SQLAlchemy. No separate message queue or API gateway is used for inter-service coordination; the parser runner reads a `parse_trigger_requested_at` setting from the DB to detect admin-triggered parse requests.

**Consequences and tradeoffs:**

- Positive: Independent scaling — the API can be scaled horizontally without affecting the bot polling loop, and vice versa.
- Positive: Fault isolation — a bot crash does not affect API availability and vice versa.
- Positive: Single Docker image simplifies CI/CD — one build, two deployments.
- Negative: No service mesh or message queue — the bot and API communicate through the shared database (polling for settings), which introduces latency and coupling via the DB schema.
- Negative: Startup sequence is not coordinated — if the bot starts before database migrations complete or before the API is ready, it may operate on stale or incomplete state.

**Quality requirements addressed:** QR-005 (Startup reliability) — separating startup paths allows each service to validate its own import chain and configuration independently, and the `main.py` CLI parser ensures explicit mode selection before any workload starts.
