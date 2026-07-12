# Week 6 Reflection — HockeyScrapper Sprint 4 (Final)

## Learning points

### Project-wide architecture maturity

Over six weeks, the architecture evolved from a monolithic script into a modular system with three distinct layers (scraping, storage/matching, delivery). The team learned that architecture emerges through iterative refinement driven by customer feedback and technical debt.

### Customer collaboration over contract negotiation

Regular sprint reviews with the customer shaped every major prioritisation decision. The customer's shift from "monetisation first" to "parser is #1 priority" in Sprint 3. The team learned that early and frequent customer involvement prevents building the wrong product.

### Definition of Done as a living document

The DoD was refined each sprint — from basic task completion to include code review requirements, test coverage gates, lint/security checks, and documentation updates. By Sprint 4, the DoD covered 7 quality requirements enforced by CI. The team learned that process automation must be iterated on just like product code.

### Sprint 4 delivery

Sprint 4 delivered the parser improvements prioritised by the customer: all KHL club websites were added to the universal parser configuration and parser time validation was added.

### Final customer review

During the Sprint 4 review, the customer:
- **Approved the monetisation UI** — complimented the team on rapid progress.
- **Corrected the pricing model** — clarified that the first subscription should be paid (not 3 free then paid), and suggested monthly/annual tier with proportional pricing.
- **Agreed to mock payments** — real YooKassa integration requires IP/legal entity, so the team will show a placeholder message instead.
- **Reiterated that parsing is the #1 priority** — the product is not ready for handover until the parser sends notifications when tickets go on sale.

---

## Validated assumptions

| Assumption | Validation | Verdict |
|---|---|---|
| Parsers can handle all KHL club websites without per-site specialisation | Universal parser configuration extended to cover all KHL clubs; | Confirmed |
| Architecture documentation (ADRs, diagrams) helps onboarding and customer communication | Used in sprint reviews; customer referenced diagrams when discussing trade-offs | Confirmed |

---

## Friction and gaps

### Unresolved requirements
- **Number of subscriptions (US-09)**: Not started. MoSCoW "Could have".

### Gaps in process
- **ADRs were written retroactively**: ADR-001, ADR-002, ADR-003 were created in Sprint 3 after most decisions were already made. Future projects should record ADRs as decisions are made.

### Technical debt
- Proxy rotator is configured but not tested under real captcha conditions on Yandex.Afisha.

---

## Planned response

Since the project is concluding, the planned response focuses on knowledge transfer and project handover:

| Action |
|---|
| Archive the repository with final README documenting deployment URLs, credentials, and runbooks. |
| Record ADR-005 (Parser Configuration Strategy) to capture Sprint 4 decisions. |

