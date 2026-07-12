# Week 6 Report — Trial Release: HockeyScrapper

**Team number:** 25

**Project:** HockeyScrapper — a web platform that lets KHL fans follow teams, track ticket sales, and receive Telegram and email notifications.

**License:** [MIT](../../LICENSE)

---

## Backlog and Sprint

### Product Backlog

- [**Product Backlog board**](https://github.com/users/kamillayarullina/projects/3/views/1)

### Sprint 4 — Assignment 6 Sprint (Trial Release)

- **Sprint milestone:** [Sprint 4 — Milestone 4](https://github.com/kamillayarullina/hockeyscrapper/milestone/4)
- [**Sprint 4 Backlog view**](https://github.com/users/kamillayarullina/projects/7)

### Sprint 4 Scope

| PBI | Issue | SP | Status |
|---|---|---|---|
| US-06: Monetization | [#63](https://github.com/kamillayarullina/hockeyscrapper/issues/63) | 8 | In Progress |
| Monetisation Backend | [#228](https://github.com/kamillayarullina/hockeyscrapper/issues/228) | 5 | In Progress |
| Monetisation Frontend | [#229](https://github.com/kamillayarullina/hockeyscrapper/issues/229) | 3 | In Progress |
| Parsing time validation | [#230](https://github.com/kamillayarullina/hockeyscrapper/issues/230) | 2 | In Progress |
| Parser improvements and parsing of KHL websites | [#231](https://github.com/kamillayarullina/hockeyscrapper/issues/231) | 5 | In Progress |
| Password improvement | [#232](https://github.com/kamillayarullina/hockeyscrapper/issues/232) | 2 | In Progress |

total:17 SP

### Week 6 Trial-Release Changes

| Change | Issue/PR | Summary |
|---|---|---|
| Monetisation Backend | [#228](https://github.com/kamillayarullina/hockeyscrapper/issues/228) | Per-team mock subscriptions from the first team, with monthly and yearly periods |
| Monetisation Frontend | [#229](https://github.com/kamillayarullina/hockeyscrapper/issues/229) | Mock checkout, plan selection, expiry dates, and per-team auto-renewal management |
| Monetisation (US-06) | [#63](https://github.com/kamillayarullina/hockeyscrapper/issues/63) | Customer-approved mock-only flow: 39 RUB/month or 390 RUB/year per team |
| Parsing time validation | [#230](https://github.com/kamillayarullina/hockeyscrapper/issues/230) | Frontend and backend validation for parsing time input in admin panel (range 1–999) |
| Parser improvements | [#231](https://github.com/kamillayarullina/hockeyscrapper/issues/231) | Improved parsing of individual KHL club websites, better CAPTCHA bypass |
| Password improvement | [#232](https://github.com/kamillayarullina/hockeyscrapper/issues/232) | Password strength requirements display on registration page, stronger backend validation |

---

## Product Access

- **Week 6 product access:** [http://139.100.225.113:8000](http://139.100.225.113:8000)
- **Run instructions:** See [README.md](../../README.md) or [docs/development-process.md](../../docs/development-process.md)
- **README.md:** [`README.md`](../../README.md)
- **CONTRIBUTING.md:** *(not present in repository — contribution guidelines are covered in [docs/development-process.md](../../docs/development-process.md))*
- **AGENTS.md:** *(not present in repository)*
- **Customer handover:** [`docs/customer-handover.md`](../../docs/customer-handover.md)
- **Hosted documentation site:** [https://kamillayarullina.github.io/hockeyscrapper/](https://kamillayarullina.github.io/hockeyscrapper/)

---

## Customer-Facing Documentation Review

During the Week 6 meeting, the team walked the customer through the repository README, run instructions, architecture/testing documentation, and the customer-handover document. The customer did not request documentation changes during the call and planned to review the updated hosted version later. The monetisation documentation was updated after the meeting to record the mock-only payment decision and the monthly/yearly per-team plans.

---

## Transition-Readiness Summary

| Area | Status | Week 7 Actions |
|---|---|---|
| Hardcoded secrets migration | Not started | Move JWT_SECRET_KEY, SMTP credentials, ADMIN_CHAT_ID to environment variables |
| Customer Render account | Not started | Customer must create a Render account and deploy via Blueprint |
| Customer SMTP credentials | Not started | Customer provides own email/app password for password recovery |
| Telegram bot ownership transfer | Not started | Transfer bot from team account to customer BotFather |
| VPS access handover | Not started | Provide SSH access or migrate to customer infrastructure |
| Backup/recovery documentation | Not started | Document SQLite and PostgreSQL backup steps |
| Final UAT walkthrough | Planned | Conduct final UAT session with customer to sign off |
| Payment-provider account | Not required | Keep monetisation as a clearly labelled educational mock, per customer decision |

---

## Customer Feedback Response Table

| Feedback point | Resulting PBI or issue | Status | Response |
|---|---|---|---|
| Every team must be paid, including the first | [#63](https://github.com/kamillayarullina/hockeyscrapper/issues/63), [#228](https://github.com/kamillayarullina/hockeyscrapper/issues/228), [#229](https://github.com/kamillayarullina/hockeyscrapper/issues/229) | Implemented | Removed the three-free-team rule; each team has its own subscription |
| Do not connect real YooKassa/YooMoney payments | [#228](https://github.com/kamillayarullina/hockeyscrapper/issues/228), [#229](https://github.com/kamillayarullina/hockeyscrapper/issues/229) | Implemented | Checkout explicitly simulates success and never charges money or requests card data |
| Offer monthly and yearly periods | [#63](https://github.com/kamillayarullina/hockeyscrapper/issues/63) | Implemented | Added 39 RUB/30-day and 390 RUB/365-day plans per team |
| Parsing time should be validated (1–999 range) | [#230](https://github.com/kamillayarullina/hockeyscrapper/issues/230) | In Progress | Input validation added to admin panel settings |
| Parser does not handle some individual KHL club sites | [#231](https://github.com/kamillayarullina/hockeyscrapper/issues/231) | In Progress | Extended parser coverage for individual club websites |
| Password requirements should be visible to users | [#232](https://github.com/kamillayarullina/hockeyscrapper/issues/232) | In Progress | Password strength requirements displayed on registration page |

### Feedback Not Addressed

- **Mobile compatibility** — Full responsive design for mobile was scoped but not yet implemented. The team has deferred this to future maintenance.

---

## Documentation Maintained During Sprint 4

| Document | Link | Updates |
|---|---|---|
| Roadmap | [`docs/roadmap.md`](../../docs/roadmap.md) | Sprint 4 scope added with monetisation, parser improvements, password validation |
| Quality Requirements | [`docs/quality-requirements.md`](../../docs/quality-requirements.md) | Unchanged (5 QRs stable) |
| Quality Requirement Tests | [`docs/quality-requirement-tests.md`](../../docs/quality-requirement-tests.md) | Unchanged (5 QRTs stable) |
| Testing Strategy | [`docs/testing.md`](../../docs/testing.md) | Updated with new test files and coverage targets |
| User Acceptance Tests | [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md) | Historical free-subscription UAT marked superseded; mock monetisation UAT added for MVP v3 |
| Architecture Documentation | [`docs/architecture/README.md`](../../docs/architecture/README.md) | Unchanged |
| Development Process | [`docs/development-process.md`](../../docs/development-process.md) | Unchanged |
| Definition of Done | [`docs/definition-of-done.md`](../../docs/definition-of-done.md) | Unchanged |
| Customer Handover | [`docs/customer-handover.md`](../../docs/customer-handover.md) | Updated with Week 6 trial-release status and transition readiness |
| CHANGELOG | [`CHANGELOG.md`](../../CHANGELOG.md) | Updated with trial-release version |

---

## UAT / Customer-Trial Results

Six historical UAT scenarios were executed on 3 July 2026 (Week 5). UAT-001 is now superseded because the customer clarified that the first team must be paid. UAT-007 was added for the revised mock monetisation flow and remains to be executed in Week 7.

| UAT | Description | Result | Executed by |
|---|---|---|---|
| UAT-001 | Subscribe to a team | Pass | Daniil |
| UAT-002 | Unsubscribe from a team | Pass | Daniil | 
| UAT-003 | Password recovery | Pass | Daniil |
| UAT-004 | Manage parsing time (admin) | Pass | Daniil |
| UAT-005 | Add proxy (admin) | Pass | Daniil |
| UAT-006 | Upload avatar | Pass | Daniil |
| UAT-007 | Monthly/yearly mock subscription for a team | Not executed | Not assigned |

Full details: [`docs/user-acceptance-tests.md`](../../docs/user-acceptance-tests.md)

---

## Release

| Artifact | Link |
|---|---|
| SemVer trial release (Week 6) | [v1.3.1](https://github.com/kamillayarullina/hockeyscrapper/releases/tag/v1.3.1) *(Week 6 changes will be tagged as a new release upon Sprint completion)* |
| CHANGELOG | [`CHANGELOG.md`](../../CHANGELOG.md) |

---

## Sprint Review

- **Sprint Review summary:** [`reports/week6/sprint-review-summary.md`](sprint-review-summary.md)
- **Sprint Review transcript:** [`reports/week6/sprint-review-transcript.md`](sprint-review-transcript.md)


---

## Week 6 Reports

| Report | Link |
|---|---|
| Sprint Review Summary | [`reports/week6/sprint-review-summary.md`](sprint-review-summary.md) |
| Reflection | [`reports/week6/reflection.md`](reflection.md) |
| Retrospective | [`reports/week6/retrospective.md`](retrospective.md) |
| LLM Report | [`reports/week6/llm-report.md`](llm-report.md) |

---

## Product Status and Expected Week 7 Follow-Up Work

**Current state:** The Week 6 customer trial confirmed the visual direction of monetisation and changed its business rules. The implementation now charges every team from the first subscription, offers monthly and yearly periods, and uses no real payment provider. The customer identified parser-driven ticket-availability notifications as the main remaining readiness blocker.


**Expected Week 7 follow-up work:**
1. **Customer transition** — Migrate hardcoded secrets to environment variables, assist customer with Render account setup and deployment, transfer Telegram bot ownership, provide SMTP credentials setup guide.
2. **Backup/recovery documentation** — Document SQLite and PostgreSQL backup and restore procedures.
3. **Final UAT walkthrough** — Conduct final UAT session with customer covering all features including monetisation.
4. **Documentation finalisation** — Complete any remaining documentation updates based on customer feedback.

---

## Contribution Traceability

| Team Member | GitHub | Issues Created | PRs/MRs Authored | PRs/MRs Reviewed | Testing/QA | Architecture/Docs |
|---|---|---|---|---|---|---|
| Kamilla Iarullina | [kamillayarullina](https://github.com/kamillayarullina) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Akamillayarullina) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Akamillayarullina) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Akamillayarullina) | UAT execution | customer-handover, roadmap, llm-report, sprint-review |
| Gleb Shamiev | [xleb-sha](https://github.com/xleb-sha) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Axleb-sha) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Axleb-sha) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Axleb-sha) | Parser tests | Deployment, architecture diagrams |
| Samir Shakirov | [samirshakirov6](https://github.com/samirshakirov6) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Asamirshakirov6) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Asamirshakirov6) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Asamirshakirov6) | Monetisation testing | definition-of-done, reflection, retrospective |
| Bulat Bulatov | [bulat1223312](https://github.com/bulat1223312) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Abulat1223312) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Abulat1223312) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Abulat1223312) | Admin panel tests | - |
| Khamza Valikhanov | [h-vlhnv](https://github.com/h-vlhnv) | [issues](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Aissue+author%3Ah-vlhnv) | [PRs](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+author%3Ah-vlhnv) | [reviews](https://github.com/kamillayarullina/hockeyscrapper/issues?q=is%3Apr+reviewed-by%3Ah-vlhnv) | - | Monetisation research |

---

## Screenshots

Embedded screenshots are stored in [`reports/week6/images/`](images/). *(Screenshots to be added after Sprint 4 completion — place images in the `images/` directory and reference them below.)*

### Sprint Milestone

*Screenshot of Sprint 4 milestone view to be inserted.*

### Sprint 4 Backlog Board

*Screenshot of Sprint 4 Backlog board to be inserted.*

### Week 6 Trial Release

*Screenshot of Week 6 SemVer release to be inserted.*

### Example Reviewed Issue-Linked PR

*Screenshot of a reviewed PR from Sprint 4 to be inserted.*

### CI Run

*Screenshot of the latest CI run on the default branch to be inserted.*

### Hosted Documentation Site

*Screenshot of the documentation site to be inserted.*
