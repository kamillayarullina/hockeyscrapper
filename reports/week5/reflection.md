# Week 5 Reflection — HockeyScrapper Sprint 3

## Learning points

### Documenting architecture

The absence of a single architecture document became noticeable as the codebase grew across three sprints. The team learned that a lightweight `docs/architecture.md` — even a single diagram — would have reduced onboarding time.

### Recording ADRs

No Architecture Decision Records were kept during the project. Decisions were discussed in Telegram and then forgotten. The team recognised that recording even brief ADRs (context, decision, consequence) would prevent re-litigating the same trade-offs in later sprints and would make the rationale visible to the customer.

### Refining the workflow

The Definition of Done matured across sprints. The team learned that workflow automation is not a one-time setup — each sprint revealed new gaps that needed codification. The process itself became a product to iterate on.

### Delivering Sprint 3 scope

Sprint 3 delivered the admin panel and email notifications for subscribed users. These were the two largest outstanding items from the backlog. The admin panel required close coordination with the customer to finalise the required actions, and the email notification feature completed the remaining scope of US-05.

### Reviewing the increment with the customer

будет чуть позже

---

## Validated assumptions

| Assumption | Validation | Verdict |
|---|---|---|
| Email notifications can be added without breaking existing subscription logic | Implemented without regression; all 66 tests pass | ✅ Confirmed |
| ADRs can be retroactively written and still provide value | Team tried writing 3 retrospective ADRs — found them useful but less precise than contemporary records | ✅ Confirmed — start earlier |

---

## Friction and gaps

### Unresolved requirements
- **Monetisation (US-06)**: Not started. Still a MoSCoW "Must have" with no committed sprint.


### Gaps in process
- **Architecture documentation**: None exists beyond code comments. The project lacks a system-context or container diagram.

---

## Planned response

| Action |
|---|
| Reserve Sprint 4 exclusively for monetisation (US-06) as a dedicated goal. |

