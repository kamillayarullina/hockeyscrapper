# Week 5 Report — MVP v2: HockeyScrapper

**Team number:** 25

**Project:** HockeyScrapper — a web platform that lets KHL fans follow teams, track ticket sales, and receive Telegram and email notifications.

**License:** [MIT](../../LICENSE)

---

## Backlog and Sprint

### Product Backlog

The Product Backlog contains all issues not yet assigned to a Sprint. Managed via GitHub Issues with the **Milestone** field left empty for uncommitted items.

- **Total Product Backlog size (Story Points):** 21 SP
- [**Product Backlog board**](https://github.com/users/kamillayarullina/projects/3/views/1)

### Sprint 3 — Assignment 5 Sprint (MVP v2)

- **Sprint milestone:** [Assignment 5 Sprint — Milestone 3](https://github.com/kamillayarullina/hockeyscrapper/milestone/3)
- **Sprint Goal:** Deliver admin panel for managing options such as parsing time, improve the website interface (customer requirement), add email notifications, and extend quality requirement tests.
- **Sprint dates:** June 29, 2026 — July 5, 2026
- **Total Sprint size:** 16 SP
- [**Sprint Backlog view**](https://github.com/users/kamillayarullina/projects/6)

### Sprint 3 Scope

| PBI | Issue | SP | Admin Panel Backend | [#131](https://github.com/kamillayarullina/hockeyscrapper/issues/131) | 5 | Done |
| Admin Panel Frontend | [#127](https://github.com/kamillayarullina/hockeyscrapper/issues/127) | 3 | Done |
| Interface improving | [#179](https://github.com/kamillayarullina/hockeyscrapper/issues/179) | 3 | Done |
| Email notification | [#182](https://github.com/kamillayarullina/hockeyscrapper/issues/182) | 3 | Done |
| Quality-requirements tests (QR-004, QR-005) | [#186](https://github.com/kamillayarullina/hockeyscrapper/issues/186) | 2 | Done |

### Delivered MVP v2 Changes

| Change | Issue/PR | Summary |
|---|---|---|
| Admin panel backend | [#131](https://github.com/kamillayarullina/hockeyscrapper/issues/131), PR [#199](https://github.com/kamillayarullina/hockeyscrapper/pull/199) | API endpoints for managing parsing interval, proxies, users, and system settings |
| Admin panel frontend | [#127](https://github.com/kamillayarullina/hockeyscrapper/issues/127), PR [#200](https://github.com/kamillayarullina/hockeyscrapper/pull/200) | Web-based admin UI for managing parsing time, adding proxies, and viewing system stats |
| Interface improvement | [#179](https://github.com/kamillayarullina/hockeyscrapper/issues/179), PR [#201](https://github.com/kamillayarullina/hockeyscrapper/pull/201) | Improved UI/UX across main pages — better layout, responsive design, consistent styling |
| Email notifications (US-05) | [#182](https://github.com/kamillayarullina/hockeyscrapper/issues/182), PR [#202](https://github.com/kamillayarullina/hockeyscrapper/pull/202) | SMTP-based email alerts sent to users when ticket availability changes for subscribed teams |
| New quality requirements | [#186](https://github.com/kamillayarullina/hockeyscrapper/issues/186), PR [#203](https://github.com/kamillayarullina/hockeyscrapper/pull/203) | QR-004 (ruff lint compliance) and QR-005 (startup reliability) with corresponding QRTs |
| Architecture documentation | PR [#204](https://github.com/kamillayarullina/hockeyscrapper/pull/204) | Added `docs/architecture/README.md` with static, dynamic, and deployment views; 3 ADRs |
| Architecture diagrams | PR [#204](https://github.com/kamillayarullina/hockeyscrapper/pull/204) | PlantUML component, sequence, and deployment diagrams in `docs/diagrams/src/` |
rtup reliability) with corresponding QRTs |

### Deployment

- **Deployed product:** [http://89.125.169.128:8000](http://89.125.169.128:8000)

### Run Instructions

- **Local development:** See [`docs/development-process.md`](../../docs/development-process.md) for setup steps
- **Docker Compose:** `docker compose up` (api + bot services)
- **Standalone:** `python -m main --all` (API + bot + parser) or `--api-only` / `--bot-only`

---

## Customer Feedback Response

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| Customer requested standalone admin panel with specific actions | [#131](https://github.com/kamillayarullina/hockeyscrapper/issues/131), [#127](https://github.com/kamillayarullina/hockeyscrapper/issues/127) | Done | Admin panel delivered with parsing interval management, proxy management, and user management |
| Improve website interface and visual design | [#179](https://github.com/kamillayarullina/hockeyscrapper/issues/179) | Done | Redesigned main pages with improved layout, responsive elements, and consistent styling |
| Email notifications when ticket availability changes | [#182](https://github.com/kamillayarullina/hockeyscrapper/issues/182) | Done | SMTP-based email alerts implemented; users receive notifications for subscribed teams |
| Strengthen quality gates with more automated checks | [#186](https://github.com/kamillayarullina/hockeyscrapper/issues/186) | Done | Added QR-004 (ruff lint compliance) and QR-005 (startup reliability) with automated QRTs |

### Feedback Not Addressed

- **Monetisation (US-06)**: The team scoped a plan but ran out of capacity to begin implementation. It remains a MoSCoW "Must have" with no committed sprint. The next sprint (Sprint 4) should be reserved exclusively for this work.

---

## Documentation

| Artifact | Link |
|---|---|
| Roadmap | [`docs/roadmap.md`](../../docs/roadmap.md) |
| Definition of Done | [`docs/definition-of-done.md`](../../docs/definition-of-done.md) |
| Testing Strategy | [`docs/testing.md`](../../docs/testing.md) |
| Quality Requirements | [`docs/quality-requirements.md`](../../docs/quality-requirements.md) |
| Quality Requirement Tests | [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md) |
| User Acceptance Tests | [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md) |
| Development Process | [`docs/development-process.md`](../../docs/development-process.md) |
| Architecture Documentation | [`docs/architecture/README.md`](../../docs/architecture/README.md) |

---

## Architecture Views

| View | Source (PlantUML) | Description |
|---|---|---|
| Static (component) | [`docs/diagrams/src/static.puml`](../../docs/diagrams/src/static.puml) | Internal components, external systems, communication paths, and protocols |
| Dynamic (sequence) | [`docs/diagrams/src/dynamic.puml`](../../docs/diagrams/src/dynamic.puml) | Full parser cycle — scraping, change detection, subscriber lookup, notification dispatch |
| Deployment | [`docs/diagrams/src/deployment.puml`](../../docs/diagrams/src/deployment.puml) | Runtime structure across user device, Render platform (Frankfurt), and external services |

Rendered SVG output is available in [`docs/diagrams/out/`](../../docs/diagrams/out/).

### ADR Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](../../docs/architecture/adr/ADR-001-modular-parser-architecture.md) | Modular Parser Architecture with Strategy Pattern | Accepted |
| [ADR-002](../../docs/architecture/adr/ADR-002-bcrypt-jwt-authentication.md) | Layered Authentication with bcrypt and JWT | Accepted |
| [ADR-003](../../docs/architecture/adr/ADR-003-dual-service-deployment.md) | Dual-Service Deployment Model with Shared Image | Accepted |

---

## Architecture Summary

The system follows a **modular monolithic** architecture with three concentric layers:

1. **Scraping Layer** (`parsers/` + `services/parser_runner.py` + `services/proxy_rotator.py`) — Periodically scrapes three Russian hockey ticket websites using Playwright with automated proxy rotation, anti-detection measures, and retry logic.
2. **Storage & Matching Layer** (`services/database.py` + `services/team_matcher.py`) — Persists events to a relational database, tracks changes over time, and maps match titles to known KHL teams and venues.
3. **Delivery Layer** (`bot/telegram_bot.py` + `services/notifier.py` + `Backend/` + `Frontend/`) — Pushes notifications to subscribed users (Telegram + email), provides a web dashboard, and exposes a REST API.

The architecture supports the current product by:

- Enabling **independent parser development** — each site has its own parser class, so adding or modifying a data source does not affect other components.
- **Separating concerns** — parsers return structured data without knowing about databases or notifications; the `ParserRunner` orchestrates the full pipeline.
- **Supporting dual deployment** — the API and bot/parser run as separate processes (or containers), allowing independent scaling and fault isolation.
- **Maintaining testability** — the `BaseParser` abstraction and shared service layer make each component independently testable.

### Quality Requirements and Architecture

| Quality Requirement | Linked ADR | How Architecture Supports It |
|---|---|---|
| **QR-001** — Testability | ADR-001 | Modular parser architecture enables isolated unit testing of each parser subclass |
| **QR-002** — Analysability | ADR-002 | Authentication architecture defines security-sensitive code paths that bandit gates target |
| **QR-003** — Confidentiality | ADR-002 | bcrypt password hashing ensures passwords are never stored in plaintext |
| **QR-004** — Maintainability | ADR-001 | Consistent interface patterns across parser modules reduce lint noise |
| **QR-005** — Reliability | ADR-003 | Dual-service deployment isolates startup paths so each service validates its import chain independently |

---

## Testing and CI Status

### Test Suite Summary

| Test Type | File | Tests | Scope |
|---|---|---|---|
| Unit | `tests/test_team_matcher.py` | 23 | Team name extraction, normalisation, info lookup |
| Unit | `tests/test_security.py` | 9 | Password hashing and verification (bcrypt) |
| Unit | `tests/test_jwt_auth.py` | 12 | JWT token creation, verification, expiration |
| Integration | `tests/test_api_integration.py` | 16 | Register, login, forgot/new password, /me, /stats |
| QRT | `tests/test_qrt_coverage.py` | 3 | Validates `.coveragerc` config and threshold |
| QRT | `tests/test_qrt_bandit.py` | 3 | Validates bandit config and execution |
| QRT | `tests/test_qrt_ruff.py` | 2 | Validates ruff config and lint compliance |
| QRT | `tests/test_qrt_startup.py` | 3 | Validates module imports and startup integrity |
| **Total** | **8 files** | **71** | |

### CI Pipeline

| Artifact | Link |
|---|---|
| CI pipeline (Tests & QA) | [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) |
| CI pipeline (Lint) | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |
| Link check | [`.github/workflows/lychee.yml`](../../.github/workflows/lychee.yml) |
| Latest protected-default-branch CI run | [Actions: Tests & QA](https://github.com/kamillayarullina/hockeyscrapper/actions/workflows/tests.yml) |

### CI Checks

The CI pipeline runs on every push/PR to `main`:

1. **Ruff lint** — `ruff check .` (zero-tolerance, fails on any violation)
2. **pip-audit** — dependency vulnerability scan
3. **Bandit security lint** — security-focused static analysis
4. **pytest with coverage** — runs all unit + integration + QRT tests; enforces `fail_under >= 20`
5. **Coverage artifact** — XML report uploaded for inspection
6. **Lychee link check** — validates all markdown links

### Branch Protection

The `main` branch is protected with:

- Require pull request reviews before merging
- Require status checks to pass (Tests & QA, Lychee, CI)
- Require branches to be up-to-date

---

## Release

| Artifact | Link |
|---|---|
| SemVer release (MVP v2) | [v1.4.0](https://github.com/kamillayarullina/hockeyscrapper/releases/tag/v1.4.0) |
| CHANGELOG | [`CHANGELOG.md`](../../CHANGELOG.md) |

---

## Demo Video

Public sanitized demo video — walkthrough of MVP v2 features including admin panel, email notifications, interface improvements, and architecture diagrams.

[https://drive.google.com/drive/folders/1STPn8drqVQ8jTalQJr-JKmn8CW1I13tT?usp=sharing](https://drive.google.com/drive/folders/1STPn8drqVQ8jTalQJr-JKmn8CW1I13tT?usp=sharing)

---

## User Acceptance Testing

- **UAT results summary:** [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md)
  - UAT-001 (Subscribe to a team) — Active
  - UAT-002 (Unsubscribe team) — Active
  - UAT-003 (Password Recovery) — Active
  - UAT-004 (Manage parsing time) — Active (new, Sprint 3)
  - UAT-005 (Add proxy) — Active (new, Sprint 3)

---

## Hosted Documentation Site

- **Documentation site:** [https://kamillayarullina.github.io/hockeyscrapper](https://kamillayarullina.github.io/hockeyscrapper)

---

## Sprint Review

- **Sprint Review summary:** [`reports/week5/sprint-review-summary.md`](sprint-review-summary.md)
- **Sprint Review transcript:** [`reports/week5/sprint-review-transcript.md`](sprint-review-transcript.md)

The Sprint Review was conducted with the customer. A recording was offered but the customer declined; the review notes and summary are shared through the repository as the primary channel.

---

## Deviation Justifications

All artifacts follow the expected default patterns. No deviations from the expected submission format.

---

## Week 5 Reports

| Report | Link |
|---|---|
| Sprint Review Summary | [`reports/week5/sprint-review-summary.md`](sprint-review-summary.md) |
| Reflection | [`reports/week5/reflection.md`](reflection.md) |
| Retrospective | [`reports/week5/retrospective.md`](retrospective.md) |
| LLM Report | [`reports/week5/llm-report.md`](llm-report.md) |

---

## Product Status

**Current state:** MVP v2 delivered and deployed at [http://89.125.169.128:8000](http://89.125.169.128:8000).

**Working features:** Registration with field validation, login with JWT auth, subscription management (web + Telegram sync), KHL team listing with icons, match data display, parser engine (khl.ru, ticket-hockey.ru, Yandex.Afisha), Telegram bot with commands, password recovery via email code, Telegram account linking, admin panel (parsing interval, proxy management, user management), email notifications for ticket availability changes, improved UI/UX across all pages, architecture documentation with static/dynamic/deployment views.

**Quality infrastructure:** 71 automated tests, ruff lint gate, bandit security gate, pip-audit dependency scan, coverage gate (fail_under >= 20%), lychee link check, branch protection with required reviews, 5 quality requirements linked to architecture decisions.

---

## Next Steps

1. **Monetisation (US-06)** — Reserve Sprint 4 exclusively for implementing subscription tiers or payment integration as a dedicated sprint goal.
2. **Subscription to a stadium (US-08)** — Implement venue-based subscriptions (carried over from earlier sprints).
3. **Number of subscriptions (US-09)** — Display subscription count on team pages.
4. **Parser testing on Yandex.Afisha** — Test captcha handling and rate limits for World Cup tickets.

---

## Contribution Traceability

| Team Member | GitHub | Issues Created | PRs/MRs Authored | PRs/MRs Reviewed | Testing/QA | Architecture/Docs |
|---|---|---|---|---|---|---|
| Kamilla Iarullina | [kamillayarullina](https://github.com/kamillayarullina) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Akamillayarullina) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Akamillayarullina) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Akamillayarullina) | QRTs, CI config | ADRs, architecture docs, diagrams |
| Gleb Shamiev | [xleb-sha](https://github.com/xleb-sha) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Axleb-sha) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Axleb-sha) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Axleb-sha) | Email notification tests | Deployment diagram, run instructions |
| Samir Shakirov | [samirshakirov6](https://github.com/samirshakirov6) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Asamirshakirov6) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Asamirshakirov6) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Asamirshakirov6) | Admin panel testing | Interface docs, UAT updates |
| Bulat Bulatov | [bulat1223312](https://github.com/bulat1223312) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Abulat1223312) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Abulat1223312) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Abulat1223312) | Lint compliance, ruff setup | Development process docs |
| Khamza Valikhanov | [h-vlhnv](https://github.com/h-vlhnv) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Ah-vlhnv) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Ah-vlhnv) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Ah-vlhnv) | Email notification implementation | Static diagram, user stories |

---

## Screenshots

### Sprint Milestone

![Sprint Milestone](images/screenshot-milestone.png)

### Board / Project Workflow View

![Sprint Backlog Board](images/screenshot-board.png)

### Latest Protected-Default-Branch CI Run

![CI Run](images/screenshot-ci.png)

### SemVer Release

![SemVer Release](images/screenshot-release.png)

### Example Reviewed Issue-Linked PR

![Reviewed PR](images/screenshot-pr.png)

### Hosted Docs Site

![Hosted Docs Site](images/screenshot-docs.png)

---

## Quick Links Summary

| Artifact | Link |
|---|---|
| Product Backlog | [Board](https://github.com/users/kamillayarullina/projects/3/views/1) |
| Sprint Backlog | [Board](https://github.com/users/kamillayarullina/projects/6) |
| Sprint 3 Milestone | [Milestone 3](https://github.com/kamillayarullina/hockeyscrapper/milestone/3) |
| Deployed product | [http://89.125.169.128:8000](http://89.125.169.128:8000) |
| CHANGELOG | [`CHANGELOG.md`](../../CHANGELOG.md) |
| SemVer release | [v1.4.0](https://github.com/kamillayarullina/hockeyscrapper/releases/tag/v1.4.0) |
| CI pipeline | [Tests & QA](https://github.com/kamillayarullina/hockeyscrapper/actions/workflows/tests.yml) |
| Demo video | [Google Drive](https://drive.google.com/drive/folders/1STPn8drqVQ8jTalQJr-JKmn8CW1I13tT?usp=sharing) |
| Documentation site | [GitHub Pages](https://kamillayarullina.github.io/hockeyscrapper) |

**Team number:** 25

**Project:** HockeyScrapper — a web platform that lets KHL fans follow teams, track ticket sales, and receive Telegram and email notifications.

**License:** [MIT](../../LICENSE)

---

## Backlog and Sprint

### Product Backlog

The Product Backlog contains all issues not yet assigned to a Sprint. Managed via GitHub Issues with the **Milestone** field left empty for uncommitted items.

- **Total Product Backlog size (Story Points):** 21 SP
- [**Product Backlog board**](https://github.com/users/kamillayarullina/projects/3/views/1)

### Sprint 3 — Assignment 5 Sprint (MVP v2)

- **Sprint milestone:** [Assignment 5 Sprint — Milestone 3](https://github.com/kamillayarullina/hockeyscrapper/milestone/3)
- **Sprint Goal:** Deliver admin panel for managing options such as parsing time, improve the website interface (customer requirement), add email notifications, and extend quality requirement tests.
- **Sprint dates:** June 29, 2026 — July 5, 2026
- **Total Sprint size:** 16 SP
- [**Sprint Backlog view**](https://github.com/users/kamillayarullina/projects/6)

### Sprint 3 Scope

| PBI | Issue | SP | Admin Panel Backend | [#131](https://github.com/kamillayarullina/hockeyscrapper/issues/131) | 5 | Done |
| Admin Panel Frontend | [#127](https://github.com/kamillayarullina/hockeyscrapper/issues/127) | 3 | Done |
| Interface improving | [#179](https://github.com/kamillayarullina/hockeyscrapper/issues/179) | 3 | Done |
| Email notification | [#182](https://github.com/kamillayarullina/hockeyscrapper/issues/182) | 3 | Done |
| Quality-requirements tests (QR-004, QR-005) | [#186](https://github.com/kamillayarullina/hockeyscrapper/issues/186) | 2 | Done |

### Delivered MVP v2 Changes

| Change | Issue/PR | Summary |
|---|---|---|
| Admin panel backend | [#131](https://github.com/kamillayarullina/hockeyscrapper/issues/131), PR [#199](https://github.com/kamillayarullina/hockeyscrapper/pull/199) | API endpoints for managing parsing interval, proxies, users, and system settings |
| Admin panel frontend | [#127](https://github.com/kamillayarullina/hockeyscrapper/issues/127), PR [#200](https://github.com/kamillayarullina/hockeyscrapper/pull/200) | Web-based admin UI for managing parsing time, adding proxies, and viewing system stats |
| Interface improvement | [#179](https://github.com/kamillayarullina/hockeyscrapper/issues/179), PR [#201](https://github.com/kamillayarullina/hockeyscrapper/pull/201) | Improved UI/UX across main pages — better layout, responsive design, consistent styling |
| Email notifications (US-05) | [#182](https://github.com/kamillayarullina/hockeyscrapper/issues/182), PR [#202](https://github.com/kamillayarullina/hockeyscrapper/pull/202) | SMTP-based email alerts sent to users when ticket availability changes for subscribed teams |
| New quality requirements | [#186](https://github.com/kamillayarullina/hockeyscrapper/issues/186), PR [#203](https://github.com/kamillayarullina/hockeyscrapper/pull/203) | QR-004 (ruff lint compliance) and QR-005 (startup reliability) with corresponding QRTs |
| Architecture documentation | PR [#204](https://github.com/kamillayarullina/hockeyscrapper/pull/204) | Added `docs/architecture/README.md` with static, dynamic, and deployment views; 3 ADRs |
| Architecture diagrams | PR [#204](https://github.com/kamillayarullina/hockeyscrapper/pull/204) | PlantUML component, sequence, and deployment diagrams in `docs/diagrams/src/` |
rtup reliability) with corresponding QRTs |

### Deployment

- **Deployed product:** [http://89.125.169.128:8000](http://89.125.169.128:8000)

### Run Instructions

- **Local development:** See [`docs/development-process.md`](../../docs/development-process.md) for setup steps
- **Docker Compose:** `docker compose up` (api + bot services)
- **Standalone:** `python -m main --all` (API + bot + parser) or `--api-only` / `--bot-only`

---

## Customer Feedback Response

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| Customer requested standalone admin panel with specific actions | [#131](https://github.com/kamillayarullina/hockeyscrapper/issues/131), [#127](https://github.com/kamillayarullina/hockeyscrapper/issues/127) | Done | Admin panel delivered with parsing interval management, proxy management, and user management |
| Improve website interface and visual design | [#179](https://github.com/kamillayarullina/hockeyscrapper/issues/179) | Done | Redesigned main pages with improved layout, responsive elements, and consistent styling |
| Email notifications when ticket availability changes | [#182](https://github.com/kamillayarullina/hockeyscrapper/issues/182) | Done | SMTP-based email alerts implemented; users receive notifications for subscribed teams |
| Strengthen quality gates with more automated checks | [#186](https://github.com/kamillayarullina/hockeyscrapper/issues/186) | Done | Added QR-004 (ruff lint compliance) and QR-005 (startup reliability) with automated QRTs |

### Feedback Not Addressed

- **Monetisation (US-06)**: The team scoped a plan but ran out of capacity to begin implementation. It remains a MoSCoW "Must have" with no committed sprint. The next sprint (Sprint 4) should be reserved exclusively for this work.

---

## Documentation

| Artifact | Link |
|---|---|
| Roadmap | [`docs/roadmap.md`](../../docs/roadmap.md) |
| Definition of Done | [`docs/definition-of-done.md`](../../docs/definition-of-done.md) |
| Testing Strategy | [`docs/testing.md`](../../docs/testing.md) |
| Quality Requirements | [`docs/quality-requirements.md`](../../docs/quality-requirements.md) |
| Quality Requirement Tests | [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md) |
| User Acceptance Tests | [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md) |
| Development Process | [`docs/development-process.md`](../../docs/development-process.md) |
| Architecture Documentation | [`docs/architecture/README.md`](../../docs/architecture/README.md) |

---

## Architecture Views

| View | Source (PlantUML) | Description |
|---|---|---|
| Static (component) | [`docs/diagrams/src/static.puml`](../../docs/diagrams/src/static.puml) | Internal components, external systems, communication paths, and protocols |
| Dynamic (sequence) | [`docs/diagrams/src/dynamic.puml`](../../docs/diagrams/src/dynamic.puml) | Full parser cycle — scraping, change detection, subscriber lookup, notification dispatch |
| Deployment | [`docs/diagrams/src/deployment.puml`](../../docs/diagrams/src/deployment.puml) | Runtime structure across user device, Render platform (Frankfurt), and external services |

Rendered SVG output is available in [`docs/diagrams/out/`](../../docs/diagrams/out/).

### ADR Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](../../docs/architecture/adr/ADR-001-modular-parser-architecture.md) | Modular Parser Architecture with Strategy Pattern | Accepted |
| [ADR-002](../../docs/architecture/adr/ADR-002-bcrypt-jwt-authentication.md) | Layered Authentication with bcrypt and JWT | Accepted |
| [ADR-003](../../docs/architecture/adr/ADR-003-dual-service-deployment.md) | Dual-Service Deployment Model with Shared Image | Accepted |

---

## Architecture Summary

The system follows a **modular monolithic** architecture with three concentric layers:

1. **Scraping Layer** (`parsers/` + `services/parser_runner.py` + `services/proxy_rotator.py`) — Periodically scrapes three Russian hockey ticket websites using Playwright with automated proxy rotation, anti-detection measures, and retry logic.
2. **Storage & Matching Layer** (`services/database.py` + `services/team_matcher.py`) — Persists events to a relational database, tracks changes over time, and maps match titles to known KHL teams and venues.
3. **Delivery Layer** (`bot/telegram_bot.py` + `services/notifier.py` + `Backend/` + `Frontend/`) — Pushes notifications to subscribed users (Telegram + email), provides a web dashboard, and exposes a REST API.

The architecture supports the current product by:

- Enabling **independent parser development** — each site has its own parser class, so adding or modifying a data source does not affect other components.
- **Separating concerns** — parsers return structured data without knowing about databases or notifications; the `ParserRunner` orchestrates the full pipeline.
- **Supporting dual deployment** — the API and bot/parser run as separate processes (or containers), allowing independent scaling and fault isolation.
- **Maintaining testability** — the `BaseParser` abstraction and shared service layer make each component independently testable.

### Quality Requirements and Architecture

| Quality Requirement | Linked ADR | How Architecture Supports It |
|---|---|---|
| **QR-001** — Testability | ADR-001 | Modular parser architecture enables isolated unit testing of each parser subclass |
| **QR-002** — Analysability | ADR-002 | Authentication architecture defines security-sensitive code paths that bandit gates target |
| **QR-003** — Confidentiality | ADR-002 | bcrypt password hashing ensures passwords are never stored in plaintext |
| **QR-004** — Maintainability | ADR-001 | Consistent interface patterns across parser modules reduce lint noise |
| **QR-005** — Reliability | ADR-003 | Dual-service deployment isolates startup paths so each service validates its import chain independently |

---

## Testing and CI Status

### Test Suite Summary

| Test Type | File | Tests | Scope |
|---|---|---|---|
| Unit | `tests/test_team_matcher.py` | 23 | Team name extraction, normalisation, info lookup |
| Unit | `tests/test_security.py` | 9 | Password hashing and verification (bcrypt) |
| Unit | `tests/test_jwt_auth.py` | 12 | JWT token creation, verification, expiration |
| Integration | `tests/test_api_integration.py` | 16 | Register, login, forgot/new password, /me, /stats |
| QRT | `tests/test_qrt_coverage.py` | 3 | Validates `.coveragerc` config and threshold |
| QRT | `tests/test_qrt_bandit.py` | 3 | Validates bandit config and execution |
| QRT | `tests/test_qrt_ruff.py` | 2 | Validates ruff config and lint compliance |
| QRT | `tests/test_qrt_startup.py` | 3 | Validates module imports and startup integrity |
| **Total** | **8 files** | **71** | |

### CI Pipeline

| Artifact | Link |
|---|---|
| CI pipeline (Tests & QA) | [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) |
| CI pipeline (Lint) | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |
| Link check | [`.github/workflows/lychee.yml`](../../.github/workflows/lychee.yml) |
| Latest protected-default-branch CI run | [Actions: Tests & QA](https://github.com/kamillayarullina/hockeyscrapper/actions/workflows/tests.yml) |

### CI Checks

The CI pipeline runs on every push/PR to `main`:

1. **Ruff lint** — `ruff check .` (zero-tolerance, fails on any violation)
2. **pip-audit** — dependency vulnerability scan
3. **Bandit security lint** — security-focused static analysis
4. **pytest with coverage** — runs all unit + integration + QRT tests; enforces `fail_under >= 20`
5. **Coverage artifact** — XML report uploaded for inspection
6. **Lychee link check** — validates all markdown links

### Branch Protection

The `main` branch is protected with:

- Require pull request reviews before merging
- Require status checks to pass (Tests & QA, Lychee, CI)
- Require branches to be up-to-date

---

## Release

| Artifact | Link |
|---|---|
| SemVer release (MVP v2) | [v1.4.0](https://github.com/kamillayarullina/hockeyscrapper/releases/tag/v1.4.0) |
| CHANGELOG | [`CHANGELOG.md`](../../CHANGELOG.md) |

---

## Demo Video

Public sanitized demo video — walkthrough of MVP v2 features including admin panel, email notifications, interface improvements, and architecture diagrams.

[https://drive.google.com/drive/folders/1STPn8drqVQ8jTalQJr-JKmn8CW1I13tT?usp=sharing](https://drive.google.com/drive/folders/1STPn8drqVQ8jTalQJr-JKmn8CW1I13tT?usp=sharing)

---

## User Acceptance Testing

- **UAT results summary:** [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md)
  - UAT-001 (Subscribe to a team) — Active
  - UAT-002 (Unsubscribe team) — Active
  - UAT-003 (Password Recovery) — Active
  - UAT-004 (Manage parsing time) — Active (new, Sprint 3)
  - UAT-005 (Add proxy) — Active (new, Sprint 3)

---

## Hosted Documentation Site

- **Documentation site:** [https://kamillayarullina.github.io/hockeyscrapper](https://kamillayarullina.github.io/hockeyscrapper)

---

## Sprint Review

- **Sprint Review summary:** [`reports/week5/sprint-review-summary.md`](sprint-review-summary.md)
- **Sprint Review transcript:** [`reports/week5/sprint-review-transcript.md`](sprint-review-transcript.md)

The Sprint Review was conducted with the customer. A recording was offered but the customer declined; the review notes and summary are shared through the repository as the primary channel.

---

## Deviation Justifications

All artifacts follow the expected default patterns. No deviations from the expected submission format.

---

## Week 5 Reports

| Report | Link |
|---|---|
| Sprint Review Summary | [`reports/week5/sprint-review-summary.md`](sprint-review-summary.md) |
| Reflection | [`reports/week5/reflection.md`](reflection.md) |
| Retrospective | [`reports/week5/retrospective.md`](retrospective.md) |
| LLM Report | [`reports/week5/llm-report.md`](llm-report.md) |

---

## Product Status

**Current state:** MVP v2 delivered and deployed at [http://89.125.169.128:8000](http://89.125.169.128:8000).

**Working features:** Registration with field validation, login with JWT auth, subscription management (web + Telegram sync), KHL team listing with icons, match data display, parser engine (khl.ru, ticket-hockey.ru, Yandex.Afisha), Telegram bot with commands, password recovery via email code, Telegram account linking, admin panel (parsing interval, proxy management, user management), email notifications for ticket availability changes, improved UI/UX across all pages, architecture documentation with static/dynamic/deployment views.

**Quality infrastructure:** 71 automated tests, ruff lint gate, bandit security gate, pip-audit dependency scan, coverage gate (fail_under >= 20%), lychee link check, branch protection with required reviews, 5 quality requirements linked to architecture decisions.

---

## Next Steps

1. **Monetisation (US-06)** — Reserve Sprint 4 exclusively for implementing subscription tiers or payment integration as a dedicated sprint goal.
2. **Subscription to a stadium (US-08)** — Implement venue-based subscriptions (carried over from earlier sprints).
3. **Number of subscriptions (US-09)** — Display subscription count on team pages.
4. **Parser testing on Yandex.Afisha** — Test captcha handling and rate limits for World Cup tickets.

---

## Contribution Traceability

| Team Member | GitHub | Issues Created | PRs/MRs Authored | PRs/MRs Reviewed | Testing/QA | Architecture/Docs |
|---|---|---|---|---|---|---|
| Kamilla Iarullina | [kamillayarullina](https://github.com/kamillayarullina) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Akamillayarullina) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Akamillayarullina) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Akamillayarullina) | QRTs, CI config | ADRs, architecture docs, diagrams |
| Gleb Shamiev | [xleb-sha](https://github.com/xleb-sha) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Axleb-sha) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Axleb-sha) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Axleb-sha) | Email notification tests | Deployment diagram, run instructions |
| Samir Shakirov | [samirshakirov6](https://github.com/samirshakirov6) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Asamirshakirov6) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Asamirshakirov6) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Asamirshakirov6) | Admin panel testing | Interface docs, UAT updates |
| Bulat Bulatov | [bulat1223312](https://github.com/bulat1223312) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Abulat1223312) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Abulat1223312) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Abulat1223312) | Lint compliance, ruff setup | Development process docs |
| Khamza Valikhanov | [h-vlhnv](https://github.com/h-vlhnv) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Ah-vlhnv) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Ah-vlhnv) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Ah-vlhnv) | Email notification implementation | Static diagram, user stories |

---

## Screenshots

### Sprint Milestone

![Sprint Milestone](images/screenshot-milestone.png)

### Board / Project Workflow View

![Sprint Backlog Board](images/screenshot-board.png)

### Latest Protected-Default-Branch CI Run

![CI Run](images/screenshot-ci.png)

### SemVer Release

![SemVer Release](images/screenshot-release.png)

### Example Reviewed Issue-Linked PR

![Reviewed PR](images/screenshot-pr.png)

### Hosted Docs Site

![Hosted Docs Site](images/screenshot-docs.png)

---

## Quick Links Summary

| Artifact | Link |
|---|---|
| Product Backlog | [Board](https://github.com/users/kamillayarullina/projects/3/views/1) |
| Sprint Backlog | [Board](https://github.com/users/kamillayarullina/projects/6) |
| Sprint 3 Milestone | [Milestone 3](https://github.com/kamillayarullina/hockeyscrapper/milestone/3) |
| Deployed product | [http://89.125.169.128:8000](http://89.125.169.128:8000) |
| CHANGELOG | [`CHANGELOG.md`](../../CHANGELOG.md) |
| SemVer release | [v1.4.0](https://github.com/kamillayarullina/hockeyscrapper/releases/tag/v1.4.0) |
| CI pipeline | [Tests & QA](https://github.com/kamillayarullina/hockeyscrapper/actions/workflows/tests.yml) |
| Demo video | [Google Drive](https://drive.google.com/drive/folders/1STPn8drqVQ8jTalQJr-JKmn8CW1I13tT?usp=sharing) |
| Documentation site | [GitHub Pages](https://kamillayarullina.github.io/hockeyscrapper) |
