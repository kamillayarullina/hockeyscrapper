# Week 3 Reflection — HockeyScrapper MVP v1

## Learning points

### Product Backlog migration
Learned to migrate PBIs from the initial flat list into a structured Product Backlog linked to milestones and issues.

### Product Backlog refinement
Customer review on 20.06.2026 added 6 new/changed scope items ([customer-review-summary](./customer-review-summary.md)):
- Standalone admin panel website (new PBI)
- Avatar upload (new PBI)
- Password policy enforcement (modified US-10)
- Server migration Render → own infra (infrastructure PBI)
- Parser + proxy formal test cycle (testing PBI)

### MVP v1 delivery
MVP v1 was delivered to the customer as a deployed site on Render with the following working: user registration, login, subscription management (web + Telegram sync), KHL team listing, match data display, parser engine, and Telegram bot.

### Customer review
The customer provided clear, actionable feedback. Key insight: the customer evaluates the product as an end user, not an implementer — UX details (icons, password rules, avatar) matter as much as backend features.

### Release preparation
The team identified that Render hosting is too slow for production use. Server migration to an in-house/own server is planned before sharing the final link.

---

## Validated assumptions

| Assumption | Validation | Verdict |
|---|---|---|
| Subscription sync (web ↔ Telegram) is technically feasible | Implemented end-to-end — user subscribes on web, notifications arrive in Telegram, and vice versa | ✅ Confirmed |
| Playwright-based parser can extract ticket data from KHL-adjacent sites | Will be tested on All-Star match site | ❓ Unconfirmed |
| Anti-bot measures (captcha) on major ticketing platforms will not block the parser | Not yet tested on Yandex.Afisha / World Cup tickets | ❓ Unconfirmed |
| Proxy rotation will be sufficient to avoid IP blocking | Implemented but not yet tested in production | ❓ Unconfirmed |
| Render free tier is adequate for MVP demo | Performance was extremely slow — user experienced lag | ❌ Rejected — must migrate |
| Password recovery (email-based) is feasible within MVP timeline | Backend started, frontend pending; email sending not implemented | ❌ Partially rejected — needs more time |
| Telegram handle `@` prefix is intuitive to users | Bug confirmed — users who omit `@` face errors; input normalisation is needed | ❌ Rejected — must fix |

---

## Friction and gaps

### Unresolved requirements
- **Email notification** (part of US-05): Not implemented. Customer did not emphasise it, but it remains in the backlog.
- **Monetisation** (US-06): Not started. MoSCoW "Must have" — deferred to post-MVP.
- **Number of subscriptions** (US-09): Not started. MoSCoW "Could have".
- **Standalone admin panel**: Requirements not yet drafted — customer will send specifications.

### Technical risks
- **Parser on Yandex.Afisha (World Cup tickets)**: Untested. Captcha and rate-limiting may block scraping. High risk for production.
- **Proxy reliability**: Code is in place but no production test has been run.
- **Render performance**: Current deployment is too slow for a good user experience.

### Missing scope
- Password recovery frontend is not implemented (backend partial).
- No admin panel for database user management (add/remove/change passwords).
- No server migration completed.
- CHANGELOG.md is empty — release notes not maintained.

### Follow-up questions
- How will the standalone admin panel be deployed?
- What is the expected parsing frequency for World Cup tickets during playoffs?

### Uncertainties
- Customer's exact requirements for the admin panel are unknown until they send the specification.
- Whether the parser can sustain high-frequency scraping against Yandex.Afisha anti-bot measures is unknown until tested.

---

## Planned response

### Sprint 2 — scope and priorities

| Action |
|---|
| **Server migration**: Move from Render to in-house/own server before sharing final link. |
| **Parser testing on Yandex.Afisha**: Run formal test cycle for World Cup tickets with proxy rotation and captcha handling. |
| **Proxy integration testing**: Validate proxy health-check, rotation, and failover in production-like conditions. |
| **Password validation**: Enforce minimum 8 characters, English alphabet only during registration. |
| **Telegram handle normalisation**: Accept usernames with or without `@` — trim or append automatically. | 
| **Avatar upload**: Allow users to upload a profile picture on the website. |
| **Icons on website**: Add KHL team logos/icons to the subscription UI. |
| **Standalone admin panel**: Wait for customer requirements, then design and implement. |
| **Customer tests final link**: Once migrated, send the deployed link for customer acceptance. |