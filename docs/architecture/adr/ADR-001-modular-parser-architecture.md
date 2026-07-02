# ADR-001: Modular Parser Architecture with Strategy Pattern

**Status:** Accepted

**Context:** The system must scrape KHL hockey ticket data from multiple heterogeneous sources (ticket-hockey.ru, khl.ru, yandex.afisha). Each source has a unique HTML structure, anti-bot protection level, and parsing logic, but all sources share common infrastructure needs: Playwright-based page loading, configurable retries with exponential backoff, User-Agent rotation, proxy rotation, and response validation.

**Decision:** Adopt a strategy-pattern architecture with an abstract base class (`BaseParser` in `parsers/base_parser.py`) defining a common interface and shared infrastructure, and concrete subclasses (`ClubParser`, `YandexParser`, `KHLParser`) implementing only source-specific HTML parsing in a required `parse(html)` method. A `ParserFactory` registry (`services/parser_runner.py:25`) maps parser names from `config/sites.yaml` to concrete classes, decoupling site configuration from parser instantiation.

**Consequences and tradeoffs:**

- Positive: Each parser is independently testable against fixture HTML, improving testability of critical scraping logic.
- Positive: Adding a new ticket source requires only a new subclass implementing `parse()` and a one-line factory registration — no change to the fetch/retry/proxy infrastructure.
- Positive: Shared retry, proxy rotation, and UA rotation logic is maintained in one place, reducing duplication.
- Negative: The abstract interface constrains parsers to the `run() -> fetch() -> parse()` flow; sources requiring non-standard interaction patterns (e.g., multi-page navigation, forms) may need workarounds or interface extensions.
- Negative: Factory registration is manual; a new parser class that is not registered will silently never be used.

**Quality requirements addressed:** QR-001 (Critical module testability) — each parser subclass is a critical module whose line coverage can be independently measured and gated.
