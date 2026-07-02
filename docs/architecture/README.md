# Architecture Documentation

## Architecture Decisions

The architecture is driven by three key decisions, each documented as an Architecture Decision Record (ADR):

| ADR | Decision | Key quality impact |
|---|---|---|
| [ADR-001](adr/ADR-001-modular-parser-architecture.md) | Modular parser architecture with Strategy pattern | Enables QR-001 (testability) by isolating each source's parsing logic |
| [ADR-002](adr/ADR-002-bcrypt-jwt-authentication.md) | bcrypt password hashing + JWT Bearer tokens | Satisfies QR-003 (password confidentiality); shapes all authenticated API routes |
| [ADR-003](adr/ADR-003-dual-service-deployment.md) | Separate API and bot services sharing one Docker image | Supports QR-005 (startup reliability) by isolating each service's import chain |

These decisions map to the views below: ADR-001 shapes the static parser structure, ADR-002 defines the authentication boundary visible in the static and dynamic views, and ADR-003 explains the deployment topology.

## Traceability

Architecture elements are traceable to quality requirements, ADRs, and tests:

- `parsers/` (BaseParser + subclasses) ← ADR-001 ← QR-001 → QRT-001 → `tests/test_qrt_coverage.py`
- `Backend/security.py` + `Backend/jwt_auth.py` ← ADR-002 ← QR-003 → QRT-003 → `tests/test_security.py`
- `main.py` + `docker-compose.yml` + `render.yaml` ← ADR-003 ← QR-005 → QRT-005 → `tests/test_qrt_startup.py`

## Static View

### What the Diagram Shows

The component diagram in [`docs/diagrams/src/static.puml`](../diagrams/src/static.puml) presents the top-level decomposition of the HockeyScrapper system. It visualises:

- **Internal components**: the orchestrator (`main.py`), FastAPI backend, static frontend, Telegram bot, parser runner with its three site-specific parsers (Club, KHL, Yandex), proxy rotator, notifier, team matcher, and the shared database layer.
- **External systems**: Telegram Bot API, three target websites (KHL.ru, ticket-hockey.ru, Yandex Afisha), Gmail SMTP, and the two user roles (Telegram user, web user).
- **Communication paths and protocols**: HTTP/HTTPS for scraping and REST API calls, SQL for persistence, SMTP for email, and the Telegram Bot API for messaging.
- **Data flows**: periodic scraping → parsing → team matching → change detection → subscriber lookup → notification dispatch, alongside the user-facing web and bot interaction flows.

The system follows a **modular monolithic** architecture where all components run within a single process (or two Render services) and share a common database and service layer.

### Coupling and Cohesion

- **Cohesion** — Each package has a well-defined responsibility: `parsers/` owns extraction logic, `services/` owns orchestration and cross-cutting logic, `bot/` owns Telegram interaction, `Backend/` and `Frontend/` own the web experience. Within `parsers/`, each parser class is cohesive around a single site's scraping logic. The `services/database.py` module is a single point of truth for storage operations, used by all components.
- **Coupling** — The parser runner in `services/parser_runner.py` couples to all three parsers via `ParserFactory`, to `services/database.py`, `services/team_matcher.py`, and `services/notifier.py`. This makes the runner a moderately coupled hub. The Telegram bot and the FastAPI backend both depend on `services/database.py`, creating implicit coupling through the shared schema. The database layer itself is coupled to both the `databases` library (async, services layer) and SQLAlchemy (sync, backend layer), which adds some duplication risk.

### Maintainability Implications

- **Positive**: Separating parsers by site means adding a new data source only requires a new parser class and a `sites.yaml` entry — no changes to other components. The shared service layer avoids scattered duplication of database or notification logic.
- **Negative**: The dual ORM setup (`databases` for async services, SQLAlchemy for sync Backend) creates two sets of models and migration paths. Schema changes must be mirrored in both layers. The `ParserRunner` hub is a potential bottleneck — any change to the scraping pipeline or notification flow touches this class.
- **Testing**: The separation of parsers from the runner (via the `BaseParser` interface) makes parsers independently testable. However, the runner itself requires mocking multiple services, making integration tests more involved.

### Quality Requirements

| Quality Attribute | How the Structure Supports or Constrains It |
|---|---|
| **Modifiability** | Adding a new parser requires no changes outside `parsers/` and `config/sites.yaml`. Changing the notification channel requires modifying only `services/notifier.py` and the bot interface. |
| **Reliability** | The proxy rotator and retry logic (with exponential backoff) in `BaseParser` isolate scraping failures from the rest of the system. The notifier deduplicates via the `notified_events` table, preventing duplicate messages. |
| **Performance** | Current single-threaded/scraping-per-site design limits throughput. All parsers run sequentially within each cycle, so scraping N sites takes approximately the sum of their individual run times. |
| **Security** | JWT authentication in the Backend and bcrypt password hashing follow established patterns. Account linking uses one-time codes with no sensitive data transfer over Telegram. |
| **Testability** | Parser classes are unit-testable due to the `BaseParser` abstraction. The shared database service can be replaced with an in-memory SQLite instance for tests. |

## Dynamic View

### What the Diagram Shows

The sequence diagram in [`docs/diagrams/src/dynamic.puml`](../diagrams/src/dynamic.puml) traces a complete parser cycle — the central runtime workflow of the system. The scenario covers:

1. **Config loading** — `ParserRunner` reads `sites.yaml` to determine which sites to scrape and how often.
2. **Parser creation** — `ParserFactory` instantiates the right parser class for each site (e.g., `KHLParser`).
3. **Scraping with proxy** — The parser requests a proxy from `ProxyRotator`, then uses Playwright to fetch the target website HTML.
4. **Parsing** — The extracted HTML is parsed into structured `MatchEvent` objects.
5. **Change detection & persistence** — New matches are compared against previously stored data; the database is updated and change types (new, sold-out, price-changed, re-available) are recorded.
6. **Team matching** — `TeamMatcher` extracts known KHL team names and venues from each event title.
7. **Subscriber lookup** — The database is queried for users subscribed to the identified teams or venues.
8. **Notification dispatch** — For each subscriber, `Notifier` deduplicates against the `notified_events` table and sends a formatted Telegram message via the Bot API.
9. **Cycle repeat** — After processing all sites, the runner sleeps for the configured interval before starting the next cycle.

### Why This Scenario Is Important

The parser cycle is the **core value-delivery loop** of the product. It is the mechanism that turns third-party ticket data into timely, personalised notifications for end users. Without this flow, the system would be a static database of hockey events with no practical utility. The scenario also exercises the most components in a single transaction, making it a good stress test for the architecture's integration points.

### Architecture Decisions and Quality Requirements Illustrated

| Aspect | What the Diagram Reveals |
|---|---|
| **Separation of concerns** | The parser never talks to the database or notifier directly — it returns structured data to the runner, which delegates storage and notification. This keeps parsers focused and reusable. |
| **Deduplication strategy** | The `notified_events` check before each message prevents duplicate notifications across restarts or multiple change events for the same match. |
| **Proxy integration** | Proxies are requested per-fetch, allowing the rotator to manage pool health and failure tracking transparently to the parser. |
| **Sequential site processing** | The loop shows sites are scraped one after another, not in parallel. This is a deliberate simplicity trade-off that limits throughput but avoids resource contention on the Playwright browser instance. |
| **Modifiability** | Adding a new notification channel (e.g., email, SMS) would require changes only in `Notifier` and the runner's notification loop — the scraping and matching pipeline stays untouched. |
| **Reliability** | The diagram highlights two resilience points: proxy rotation (isolates IP bans to individual requests) and deduplication (prevents spam after transient failures). |
| **Testability** | Each participant (parser, matcher, notifier, proxy rotator) has a narrow contract, making them mockable in isolation for both unit and integration tests. |

## Deployment View

### What the Diagram Shows

The deployment diagram in [`docs/diagrams/src/deployment.puml`](../diagrams/src/deployment.puml) shows the runtime structure across three tiers:

- **User device** — Browser (web UI) and Telegram App (bot interface).
- **Render platform (Frankfurt)** — Two Docker services sharing a managed PostgreSQL database:
  - **Web service** (`hockeyscrapper-api`) — runs the FastAPI backend and serves the static frontend on port 8000. Exposed to the internet via HTTPS. Health-checked at `/stats`.
  - **Worker service** (`hockeyscrapper-bot`) — runs the Telegram bot and parser runner. No public HTTP port. Communicates outbound to Telegram Bot API, target websites (via Playwright), and Gmail SMTP.
  - **Managed PostgreSQL** (`hockeyscrapper-db`) — shared state store, accessed internally by both services.
- **External services** — Telegram Bot API, three scraped websites (KHL.ru, ticket-hockey.ru, Yandex Afisha), and Gmail SMTP for password recovery emails.

The customer-facing access path is:
```
User Browser → Internet (HTTPS) → Render Web Service → PostgreSQL
User Telegram App → Telegram Bot API → Render Worker → PostgreSQL
```

### Why This Deployment Model Was Chosen

Render was selected as a **platform-as-a-service** that minimises operational overhead while supporting Docker-based deployments. Key factors:

- **Two-service split** — The web service handles user-facing HTTP requests and can scale independently of the background worker that runs the scraper and bot. This prevents a scrape-heavy cycle from degrading API response times.
- **Shared Docker image** — Both services use the same `Dockerfile`; the only difference is the startup command (`--api-only` vs `--bot-only`). This simplifies CI/CD — one build produces both artefacts.
- **Managed PostgreSQL** — Render provides a free-tier PostgreSQL database with automated backups, offloading DBA concerns from the team.
- **Local parity with Docker Compose** — The same image and environment variables work locally with SQLite, enabling development without a cloud account.

### How the Deployment Supports or Constrains the Product

| Aspect | Support | Constraint |
|---|---|---|
| **Scalability** | Web and worker can be scaled to different instance sizes. | Free-tier Render has limited CPU/memory; Playwright (Chromium) is memory-intensive, so the worker may hit resource limits under sustained scraping. |
| **Latency** | Render Frankfurt region is close to target Russian websites, reducing scrape time. | User-facing latency from outside Europe may be higher; no CDN is used for the static frontend. |
| **Reliability** | Render provides auto-restart on failure and managed PostgreSQL with daily backups. | No built-in redundancy — a single instance per service means downtime during deploys or if the worker crashes mid-cycle. |
| **Data persistence** | PostgreSQL is a managed service; SQLite file is mounted via Docker volume in dev. | SQLite in Docker Compose is ephemeral if the volume is not properly persisted. |
| **Security** | Secrets (BOT_TOKEN, MAIL_PASSWORD) are stored as Render secret env vars, not in the repo. | JWT_SECRET_KEY is currently hardcoded in `render.yaml` with a sync: true value — this is a production risk. |

### Operational Considerations

- **Playwright resource usage** — The Chromium browser launched by Playwright is the heaviest dependency. On Render's free/starter plans, the worker instance must have enough memory to run both Python and a headless Chromium process concurrently. Monitor for OOM kills.
- **Scraping frequency** — The scraping interval in `sites.yaml` should be tuned to avoid aggressive hitting of target sites (rate limiting / IP bans). Current defaults (every 5–15 minutes per site) are reasonable but should be validated against site tolerance.
- **Outbound networking** — Render workers can make outbound HTTPS requests, but some target sites may geo-block or employ anti-bot measures. The proxy rotator is designed to mitigate this, but a proxy pool must be configured and maintained.
- **Telegram bot webhook vs polling** — The current implementation uses long-polling, which is simpler but requires the worker to maintain a persistent connection. Switching to a webhook would require a public HTTPS endpoint on the worker, which the current Render setup does not provide.
- **Secret rotation** — The hardcoded `JWT_SECRET_KEY` in `render.yaml` should be replaced with a sync: false secret before production use. All other secrets (BOT_TOKEN, MAIL_PASSWORD, ADMIN_CHAT_ID) are already managed as Render secrets.
