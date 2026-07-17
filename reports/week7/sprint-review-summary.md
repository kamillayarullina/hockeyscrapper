# Sprint Review Summary

## Date and participants

17.07.2026
- Kamilla Iarullina
- Gleb Shamiev
- Samir Shakirov
- Khamza Valikhanov
- Bulat Bulatov

## Artifacts Demonstrated

- Parser (Sprint 5) — anti-bot protection via human emulation.
- Monetisation rework — first subscription is paid, monthly/yearly tiers with auto-renewal.
- Customer handover document — deployment guide, SMTP setup, bot transfer procedure.

## Delivered Increment Discussed

Sprint 5 (Final) delivered the following increment:

| Area | Delivered |
|------|-----------|
| **Monetisation (US-06)** | Reworked per week6 feedback: first subscription is paid . Monthly  and yearly tiers. Auto-renewal toggle per subscription. Subscription management page (view, cancel, toggle). |
| **UX Improvements** | Logout button added. |

## UAT Results

- **Parser demonstration**: Customer confirmed KHL and ticket.hockey parsing works in real time. Parser correctly distinguishes between "no tickets"  and "tickets available" .
- **Subscription flow **: Reworked correctly — customer tested subscribing to Ak Bars, was redirected to the mocked payment page with monthly/yearly options and educational disclaimer.
- **Logout**: Implemented and demonstrated.
- **Handover document**: Customer read it before the meeting and confirmed it is detailed enough for independent operation.

## Customer Feedback & Requested Changes

| # | Request / Feedback | Status / Team Response |
| :--- | :--- | :--- |
| 1 | **Add logout confirmation dialog** — "Are you sure you want to log out?" with confirmation button. | Optional- team will think about implementing |
| 2 | **Increase padding in admin panel** — text too close to the edge. | Optional- team will think about implementing |
| 4 | **Transfer repository ownership** — customer asked to take ownership of the repo instead of it being open. | Accepted — team will transfer repository and Telegram bot to the customer. |
| 5 | **Product confirmed ready for transfer** — customer stated "You guys are great, you handled everything." | Confirmed — no more development work required. |

## Risks Identified

- Yandex and club website parsers untested in production — no matches available on those platforms yet.
- SMTP credentials still need to be configured by the customer post-handover.

## Action Points

1. **Team:** Add logout confirmation dialog(optional).
2. **Team:** Fix padding in admin panel UI(optional).
3. **Team:** Transfer repository ownership to the customer.
4. **Team:** Transfer Telegram bot (`HockeyScrapper_bot`) to the customer.
5. **Customer:** Configure SMTP credentials in `.env` post-handover.


## Resulting Product Backlog / Scope Changes

- **[Completed] Parser — Anti-bot Protection (US-04):** Human emulation implemented, KHL and ticket.hockey working. Yandex/club websites pending real match data.
- **[Completed] Monetisation Rework (US-06):** First-paid model, monthly/yearly tiers, mocked payments, auto-renewal — delivered and accepted.
- **[Not Started] Number of Subscriptions (US-09):** MoSCoW "Could have" — never prioritised.

