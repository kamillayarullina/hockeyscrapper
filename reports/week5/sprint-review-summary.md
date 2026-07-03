# Sprint Review Summary

## Date and participants

03.07.2026
- Kamilla Iarullina
- Gleb Shamiev
- Samir Shakirov
- Bulat Bulatov

## Artifacts Demonstrated

- Admin panel 
- Architecture diagrams: static view (component diagram), dynamic view (sequence diagram), deployment view
- Parser architecture overview — three parsers 
- Proxy rotator configuration via admin panel

## Scope Reviewed

The team presented the current state of the product, covering:

- **Admin Panel:** Fully redesigned to match the main site theme.
- **Parser System:** Three parsers operational — a universal club parser and two specific parsers. Parsers are not yet actively finding tickets as no events are listed yet.
- **Proxy Rotator:** Implemented to bypass captchas. Rotates through available proxies and falls back to direct connection.
- **Architecture Documentation:** Static, dynamic, and deployment view diagrams created and reviewed.

## Implemented Increment Discussed

Sprint 3 (MVP v2) delivered the admin panel, email notifications. The admin panel is feature-complete per customer requirements. The parser system is deployed with three data sources for broader coverage. Architecture diagrams have been created for all three standard views.

## Customer Feedback & Requested Changes

| # | Request / Feedback | Status / Team Response |
| :--- | :--- | :--- |
| 1 | **Parser is #1 priority** — monetisation should be the last priority. | Accepted — the team will reorder the backlog accordingly. |
| 2 | **Improve input validation in admin panel** — case sensitivity issues when adding team names (e.g., "LADA" vs "lada" creates duplicate subscriptions). | Accepted — the team will work on normalisation. |
| 3 | **Explain the proxy rotator in more detail** — why it is needed and how it is configured. | Explained during the meeting: used for captcha bypass with automatic proxy rotation. |
| 4 | **Clarify scraping method** — does the parser call APIs or use browser automation? | Explained: parsers read site JavaScript directly without login or browser automation. |
| 5 | **Testing coverage** — key scenarios (registration, subscription, checkout, scraping) should be covered by tests. | Confirmed: unit and CI tests exist (107 tests passing). Customer wants both API and UI test levels clarified. |

## Risks Identified

- Monetisation (US-06) remains unstarted despite being a must-have; deferred across multiple sprints.
- Admin panel input validation is too basic — case mismatches can create duplicate subscriptions.

## Action Points

1.  Reorder backlog — prioritise parser improvements over monetisation.
2.  Improve admin panel input validation.
4.  Add all KHL club websites to the universal parser configuration.
6.  Clarify test levels for key scenarios as discussed.


## Resulting Product Backlog / Scope Changes

- **[Reprioritised] Parser Improvements:** Moved to #1 priority. Includes per-club optimisation, adding all KHL club sites, and testing under real traffic.
- **[Reprioritised] Monetisation (US-06):** Moved to lowest priority.
- **[New] Input Normalisation for Admin Panel:** Case-insensitive team name matching and duplicate prevention.
- **[Deferred] Mobile Site Adaptation:** Postponed due to reprioritisation.
- **[Completed] Admin Panel:** Redesign, columns, Cyrillic fix — delivered and accepted.
- **[Completed] Email Notifications (US-05):** Shipped and tested.

