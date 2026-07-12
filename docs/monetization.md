# Monetization

HockeyScrapper uses a mock per-team subscription model approved by the customer during the Week 6 trial meeting.

## Customer Rules

- There are no free team subscriptions. The first team and every additional team require a separate subscription.
- A subscription unlocks only the team selected by the user.
- The monthly plan costs 39 RUB and lasts 30 days.
- The yearly plan costs 390 RUB and lasts 365 days.
- The yearly price is ten times the monthly price, as requested by the customer.
- Users can unsubscribe from notifications without losing the remaining paid period. They can subscribe to the same team again before expiry without another mock payment.
- Auto-renewal is configured separately for each team and can be enabled or disabled while the subscription is active.

## Mock Payment Flow

No real payment provider is connected. The checkout page clearly tells the user that the operation is educational and that no money will be charged. After the user confirms the mock payment, the backend immediately:

1. records a successful mock payment;
2. activates the selected team for the selected period;
3. adds the team to notification subscriptions;
4. stores the auto-renewal preference.

The system does not request bank-card details, save a payment method, redirect to YooKassa or require payment credentials. `APP_BASE_URL`, `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, webhooks and `BILLING_DEMO_MODE` are not part of this implementation.

## Mock Auto-Renewal

The command below processes expired subscriptions:

```bash
python -m Backend.renewals
```

For an expired subscription with auto-renewal enabled, it creates a successful mock renewal and extends the same monthly or yearly plan. For an expired subscription without auto-renewal, it stops team notifications. No external charge is attempted in either case.

## Run Locally

No billing-specific environment variables are needed:

```powershell
.\.venv\Scripts\python.exe -m main --api-only
```

Open `http://127.0.0.1:8000`, log in, choose a team and press `Подписаться`. The checkout page lets you choose the monthly or yearly mock plan.
