# Sprint Review Summary

## Date and participants

10.07.2026
- Gleb Shamiev
- Samir Shakirov
- Khamza Valikhanov

## Artifacts Demonstrated

- Monetisation system — full subscription management with YooMoney/YooKassa integration (mocked)
- UX errors — inline error messages on registration and log in form replacing popup alerts
- Documentation — README, handover plan
- Updated scraping interval configuration (1–1999 minutes)

## Delivered Increment Discussed

Sprint 4 delivered the following increment:

| Area | Delivered |
|------|-----------|
| **Monetisation / Subscription Management (US-06)** | Users get 3 free subscriptions; 4th subscription costs 39 RUB/month. YooKassa integration links user account to YooMoney. Auto-renewal toggle with confirmation step. Subscription management page (view, cancel, toggle auto-renewal). |
| **UX errors** | Password format errors now shown inline on the registration page instead of browser popup alerts. Passwords mismatch and format validation messages appear directly on the site. |
| **Scraping Interval** | Range extended from 1–1440 to 1–1999 minutes. |
| **Documentation** | README describing product launch, test procedures, development history, architecture diagram, and handover plan. |

## UAT Results

- **Subscription flow (first 3 free)**: The team demonstrated that subscribing to 3 teams works without payment. Attempting to subscribe to a 4th team triggers the payment flow. Customer noted this was not the requested behaviour — the first subscription, not the fourth, should be paid.
- **Payment flow**: YooKassa redirect works in demo. Customer requested switching to fully mocked payments with a notice that this is an educational project and no real money is processed.
- **Password validation**: Inline messages appear correctly for invalid format and mismatched passwords.
- **Subscription management page**: Users can view subscribed teams and toggle auto-renewal per subscription.

## Customer Feedback & Requested Changes

| # | Request / Feedback | Status / Team Response |
| :--- | :--- | :--- |
| 1 | **First subscription should be paid** — not the first 3 free. | Accepted — the team will change the model so the very first team subscription requires payment. |
| 2 | **Mock payments** — no real YooMoney/YooKassa integration; display educational-purpose notice on payment attempt. | Accepted — the team will replace real payment processing with a simulated flow. |
| 3 | **Monthly and yearly subscription tiers** — yearly price should be 10× the monthly price. | Accepted — the team will add subscription period options. |
| 4 | **Parser is still #1 priority** — customer explicitly asked about ticket notification functionality. | Confirmed — parser work deferred to next week; team committed to delivering it. |
| 5 | **Host not updated since last meeting** — customer asked to be notified when the latest version is deployed. | Accepted — team will fix the host and notify the customer. |

## Risks Identified

- Parser (core functionality) is to be updated despite being the customer's #1 priority across multiple sprints.
- Main branch had version/canvas issues during the demo — deployment pipeline reliability needs attention.
- YooKassa registration blocked by legal entity requirement (IP or LLC) — mock approach avoids this blocker but means payment is non-functional in production.

## Action Points

1. Change subscription model — first subscription is paid, not the 4th.
2. Replace real YooKassa integration with mocked payment flow (educational-purpose notice).
3. Add monthly/yearly subscription period options (yearly = 10× monthly).
4. Implement parser functionality next week (ticket availability monitoring).
5. Fix deployment on main branch and notify customer when updated.
6. Share repository link for customer to review documentation and handover plan.

## Resulting Product Backlog / Scope Changes

- **[In Progress] Monetisation (US-06):** Subscription management UI implemented; payment model needs rework (first paid, mock flow, yearly tier).
- **[Deferred → Next Sprint] Parser (US-04):** No work this week; moved to next week as highest priority.
- **[New] Subscription Period Options:** Monthly and yearly subscription tiers (yearly at 10× monthly price).
