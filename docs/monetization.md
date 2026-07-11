# Monetization

HockeyScrapper lets each user follow their first three teams for free. Every additional
team costs 39 RUB per month. A paid team is added only after the backend verifies a
successful YooKassa payment and remains active for 30 days.

Users can see their paid teams, expiry dates, and auto-renewal settings on
`paid-subscriptions.html`. At the first paid-team checkout they must explicitly
consent to YooKassa saving the payment method. The backend stores one YooKassa
payment-method ID in the user's billing profile, never card data. The same method
is then used for later team purchases and for any team whose auto-renewal is
enabled; the card does not need to be linked again. Auto-renewal remains an
independent setting for each team.

## Configure YooKassa

1. Create a YooKassa shop and first use its test credentials.
2. Set `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, and the public HTTPS `APP_BASE_URL` in the deployment environment.
3. In the YooKassa dashboard, register `https://<your-domain>/payments/yookassa/webhook` for `payment.succeeded` and `payment.canceled`.
4. Tell your YooKassa manager that the shop will use auto-payments and make sure the
   shop is approved for them. YooKassa requires both this and the user's consent.
5. Make a test payment for a fourth team and accept the separate payment-method
   saving consent. The auto-renewal checkbox is optional. After YooKassa confirms
   that the method was saved, later paid teams can use the same method.
6. Schedule the following command on the production server once per hour:

   ```bash
   python -m Backend.renewals
   ```

   The command starts due auto-renewal payments and turns off notifications for
   expired subscriptions without auto-renewal. The YooKassa webhook confirms every
   successful renewal before the next 30 days are granted.

Never put YooKassa keys in frontend files or Git. The user is redirected to YooKassa for card entry, so HockeyScrapper does not process or store card data.

## Local Demo

To review the interface without YooKassa credentials, start the application with:

```powershell
$env:APP_BASE_URL = "http://127.0.0.1:8000"
$env:BILLING_DEMO_MODE = "true"
.\.venv\Scripts\python.exe -m uvicorn Backend.main:app --host 127.0.0.1 --port 8000
```

The demo mode only works for `localhost` or `127.0.0.1`. Each checkout is marked as
successful without contacting YooKassa or charging money. Never enable it on a
public server.
