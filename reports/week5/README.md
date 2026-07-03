# Week 5 Report — HockeyScrapper

## Sprint 3 — MVP v2

**Sprint Goal:** Improve admin panel, add avatar support, and harden database reliability for MVP v2.

**Delivered MVP v2 changes:**
- Redesigned admin panel to match main site theme (white/blue, background)
- Added Telegram-linked, registration date, and subscription date columns to admin panel
- Fixed Cyrillic encoding in admin panel
- Added `avatar_url` column to bot users table
- Enabled SQLite WAL mode and busy timeout for concurrent access

## Documentation

- [Hosted Documentation Site](https://kamillayarullina.github.io/hockeyscrapper/)
- [Product Backlog](https://github.com/kamillayarullina/hockeyscrapper/issues)
- [Sprint 3 Milestone](https://github.com/kamillayarullina/hockeyscrapper/milestones)
- [Development Process](docs/development-process.md)
- [Architecture](docs/architecture/README.md)
- [User Stories](docs/user-stories.md)
- [Testing Strategy](docs/testing.md)
- [Quality Requirements](docs/quality-requirements.md)
- [Quality Requirement Tests](docs/quality-requirement-tests.md)
- [User Acceptance Tests](docs/user-acceptance-tests.md)
- [Definition of Done](docs/definition-of-done.md)
- [Roadmap](docs/roadmap.md)
- [CHANGELOG](CHANGELOG.md)

### Architecture Views
- [Static View (Component Diagram)](docs/architecture/static-view/static.svg)
- [Dynamic View (Sequence Diagram)](docs/architecture/dynamic-view/dynamic.svg)
- [Deployment View (Deployment Diagram)](docs/architecture/deployment-view/deployment.svg)

### ADRs
- [ADR-001: Modular Parser Architecture](docs/architecture/adr/ADR-001-modular-parser-architecture.md)
- [ADR-002: bcrypt + JWT Authentication](docs/architecture/adr/ADR-002-bcrypt-jwt-authentication.md)
- [ADR-003: Dual Service Deployment](docs/architecture/adr/ADR-003-dual-service-deployment.md)

## Reports

- [Sprint Review Summary](sprint-review-summary.md)
- [Sprint Review Transcript](sprint-review-transcript.md)
- [Reflection](reflection.md)
- [Retrospective](retrospective.md)
- [LLM Report](llm-report.md)

## CI & Testing

- [CI Pipeline](https://github.com/kamillayarullina/hockeyscrapper/actions)
- **Tests:** 107 tests passing
- **Coverage gate:** 30% (fail_under)

## MVP v2 Release

- **SemVer:** v0.2.1
- [Public Demo Video](#)
