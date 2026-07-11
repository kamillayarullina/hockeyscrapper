# Monetization

HockeyScrapper lets each user follow their first three teams for free. Every additional
team costs 39 RUB per month. A paid team is added only after the backend verifies a
successful YooKassa payment and remains active for 30 days.

Users can see their paid teams, expiry dates, and auto-renewal settings on
`paid-subscriptions.html`. At the first payment they may explicitly opt in to
auto-renewal. The backend then stores only YooKassa's saved payment-method ID,
never card data. Turning auto-renewal off prevents the next charge; the team stops
receiving notifications when its current month ends.

## Configure YooKassa

1. Create a YooKassa shop and first use its test credentials.
2. Set `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, and the public HTTPS `APP_BASE_URL` in the deployment environment.
3. In the YooKassa dashboard, register `https://<your-domain>/payments/yookassa/webhook` for `payment.succeeded` and `payment.canceled`.
4. Tell your YooKassa manager that the shop will use auto-payments and make sure the
   shop is approved for them. YooKassa requires both this and the user's consent.
5. Make a test payment for a fourth team. To test auto-renewal, select the consent
   checkbox during checkout so that YooKassa saves the payment method.
6. Schedule the following command on the production server once per hour:

   ```bash
   python -m Backend.renewals
   ```

   The command starts due auto-renewal payments and turns off notifications for
   expired subscriptions without auto-renewal. The YooKassa webhook confirms every
   successful renewal before the next 30 days are granted.

Never put YooKassa keys in frontend files or Git. The user is redirected to YooKassa for card entry, so HockeyScrapper does not process or store card data.
