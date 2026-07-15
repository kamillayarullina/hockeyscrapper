# Monetization

HockeyScrapper uses paid, per-team subscriptions. There are no free team slots: the
first team and every additional team require a subscription period.

| Period | Price | Access granted |
|---|---:|---:|
| Monthly | 39 RUB | 30 days |
| Yearly | 390 RUB | 365 days |

The yearly price is exactly ten monthly payments, as requested by the customer.
A period belongs to one team only; HockeyScrapper does not offer a single premium
plan that unlocks every team.

## Simulated payment flow

No real payment provider is connected. Checkout always shows that the operation is
an educational simulation. After the user confirms and clicks **Pay**, the backend:

1. records a successful simulated payment;
2. activates the selected team for the selected period;
3. enables ticket notifications for that team and its venue;
4. returns `real_money_charged: false` to the frontend.

No card number, payment account, provider token, shop key, or other financial
credential is requested or stored. The same simulated behavior is used in every
environment, so production configuration cannot accidentally enable real charges.

Direct team subscription attempts through the web toggle, the Telegram bot, or the
legacy HTTP API are rejected until that user has an active period for the team.
Rows left by the previous three-free-teams model are disabled when the user next
loads or changes subscriptions.

## Auto-renewal

Auto-renewal is also simulated. It extends the same monthly or yearly plan without
contacting an external service and writes another simulated payment record. Run the
renewal job periodically:

```bash
python -m Backend.renewals
```

Users must explicitly confirm enabling auto-renewal and can disable it independently
for each team. If auto-renewal is disabled, notifications stop when the current
period expires.

## Billing API

- `GET /billing/plans` — monthly and yearly prices plus the simulation notice.
- `POST /billing/checkout` — simulates payment and activates one team.
- `GET /billing/subscriptions` — active and expired per-team periods.
- `PATCH /billing/subscriptions/{team_name}/auto-renew` — changes renewal settings.
- `GET /billing/payments/{payment_id}` — reads the simulated payment record.
