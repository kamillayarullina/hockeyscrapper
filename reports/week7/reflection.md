# Week 7 Reflection — HockeyScrapper Sprint 5 (Final)

## Learning points

### Follow-up maintenance after trial release

 The team learned that a trial release is not the end of development — it is a discovery phase that feeds a dedicated maintenance sprint.

### Final transition work

Week 7 was the first sprint dedicated entirely to handover. The team learned that transition work — moving secrets to env vars, documenting backup procedures, writing a customer handover guide — is invisible in the product backlog but essential for delivery. Without a dedicated transition sprint, the customer would have received a running system they could not operate independently.

### Customer usefulness feedback

Customer confirmed at the final sprint review that all MVP requirements are met and the product is ready for transfer.
Minor requests: logout confirmation dialog and padding fix in admin panel. The customer explicitly confirmed the product is fully ready for transfer.

### Final delivery of MVP v3

All three MVP milestones were delivered:
- **MVP v1** : Subscription management, Telegram notifications.
- **MVP v2** : Avatar upload, password recovery, admin panel, email notifications
- **MVP v3** : Monetisation, parser improvements, error notifications, password strength, performance optimization

---

## Validated assumptions

| Assumption | Validation | Verdict |
|---|---|---|
| Customer can operate the system independently after handover | Handover document written and reviewed; transition blockers documented | Confirmed (pending customer execution) |
| MVP v3 scope covers all customer "must-have" requirements | Customer confirmed usefulness and asked only for maintenance docs | Confirmed |

---

## Friction and gaps

### Unresolved requirements
- **Mobile compatibility**: Deferred. The customer acknowledged it as a future enhancement, not a release blocker.
- **Number of subscriptions (US-09)**: Not started. MoSCoW "Could have" — never prioritised.

### Transition blockers not yet resolved
- Telegram bot ownership transfer not yet executed.
- SMTP credentials still hardcoded (identified, documented, but not migrated).

---

## Planned response

Since the project is concluding, no further sprint is planned. The repository is archived with all documentation finalised:

| Action |
|---|
| Repository archived with final README, handover doc, and runbooks. |
| Customer provided with deployment guide, SMTP setup instructions, and bot transfer procedure from `docs/customer-handover.md`. |
| ADRs finalised to cover all architecture decisions across 7 weeks. |
