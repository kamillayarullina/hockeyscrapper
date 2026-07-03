# Sprint Review Summary

## Date and participants

03.07.2026
- Kamilla Iarullina
- Gleb Shamiev
- Samir Shakirov
- Bulat Bulatov

## Artifacts Demonstrated

- Admin panel (redesigned, white/blue theme)
- Architecture diagrams: static view (component diagram), dynamic view (sequence diagram), deployment view
- Parser architecture overview — three parsers 
- Proxy rotator configuration via admin panel
- Parser cycle diagram

## Delivered Increment Discussed

Sprint 3 delivered the following increment:

| Area | Delivered |
|------|-----------|
| **Admin Panel** | Redesigned to match main site theme (white/blue); added Telegram-linked, registration date, and subscription date columns; fixed Cyrillic encoding |
| **Email Notifications (US-05)** | SMTP integration completed and tested end-to-end — users receive alerts on ticket availability changes |
| **Parser Infrastructure** | Three parsers deployed ; proxy rotator implemented for captcha bypass |
| **Architecture Documentation** | Static, dynamic, and deployment view diagrams created |
| **ADRs** | ADR-001 (Modular Parser Architecture), ADR-002 (bcrypt + JWT Authentication), ADR-003 (Dual Service Deployment) recorded |

## UAT Results
-Team subscription and unsubscription. We tested how a user can subscribe to their favorite hockey team and unsubscribe from it.The only thing we noticed is that the back button is labeled "Back," but it would be more logical to name it "Save changes," because the user expects to save their changes rather than just go back. This is a minor UI improvement that we will definitely implement.
-Password recovery. The user enters their email address, receives a confirmation code, enters a new password, and successfully changes it. The entire chain works perfectly, and we had no comments on this scenario.
-Managing parsing time. The mechanism itself works correctly, but we decided that input validation should be added — only allowing numbers from 1 to 999 to prevent the administrator from accidentally entering zero or negative values.
-Adding proxy servers. The administrator can add new proxy servers through the admin panel. The function works flawlessly, with no comments.
-Avatar upload. The user can upload their photo to the profile page, crop it as needed, and save it. The avatar is stored in the database and displayed on the profile page. Everything works perfectly.
## Architecture Evidence Discussed


1. **Static View (Component Diagram)** — Shows parsers, websites, web user, Telegram bot, and their relationships. Customer asked about: different parser types, proxy rotator purpose, scraping method , and universal vs specific parser trade-offs.
2. **Dynamic View (Sequence Diagram)** — Parser interaction flow presented but author was absent; team committed to send a voice explanation separately.
3. **Deployment View (Deployment Diagram)** — Shown alongside static view.

Architecture decisions were supported by three recorded ADRs:
- ADR-001: Modular Parser Architecture (three specialised parsers + universal)
- ADR-002: bcrypt + JWT Authentication
- ADR-003: Dual Service Deployment

## Customer Feedback & Requested Changes

| # | Request / Feedback | Status / Team Response |
| :--- | :--- | :--- |
| 1 | **Parser is #1 priority** — monetisation should be the last priority. | Accepted — the team will reorder the backlog accordingly. |
| 2 | **Improve input validation in admin panel** — case sensitivity issues when adding team names . | Accepted — the team will work on normalisation. |
| 3 | **Explain the proxy rotator in more detail** — why it is needed and how it is configured. | Explained during the meeting: used for captcha bypass with automatic proxy rotation. |
| 4 | **Testing coverage** — key scenarios  should be covered. | Confirmed: 107 unit + CI tests passing. Customer asked to clarify API vs UI test levels. |


## Risks Identified


- Monetisation (US-06) remains unstarted despite being a must-have; deferred across multiple sprints.
- Parsers not yet tested under production load against active ticket-selling events — real-world captcha and anti-bot behaviour unknown.


## Action Points

1. **Team:** Reorder backlog — prioritise parser improvements over monetisation.
2. **Team:** Improve admin panel input validation .
3. **Team:** Add all KHL club websites to the universal parser configuration.
4. **Team:** Clarify test levels for key scenarios as discussed.
5. **Team:** Add parsing time validation (1–999 range) to admin panel.


## Resulting Product Backlog / Scope Changes

- **[Reprioritised] Parser Improvements:** Moved to #1 priority. Includes per-club optimisation, adding all KHL club sites, and testing under real traffic.
- **[Reprioritised] Monetisation (US-06):** Moved to lowest priority.
- **[New] Input Normalisation for Admin Panel:** Case-insensitive team name matching and duplicate prevention.
- **[Completed] Admin Panel:** Redesign, columns, Cyrillic fix — delivered and accepted.
- **[Completed] Avatar Upload (UAT-006):** Implemented and passed.
- **[Completed] Email Notifications (US-05):** Shipped and tested.
- **[Completed] Proxy Management (UAT-005):** Implemented and passed.
- **[Completed] Parsing Time Management (UAT-004):** Implemented and passed .
