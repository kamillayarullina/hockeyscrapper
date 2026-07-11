# Monetization

HockeyScrapper has a free plan with up to three team subscriptions and two one-time Premium purchases:

- Premium for 30 days: 299 RUB.
- Premium for 365 days: 2990 RUB.

Premium removes the team-subscription limit. It is activated only after the backend verifies a successful payment with YooKassa.

## Configure YooKassa

1. Create a YooKassa shop and first use its test credentials.
2. Set `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, and the public HTTPS `APP_BASE_URL` in the deployment environment.
3. In the YooKassa dashboard, register `https://<your-domain>/payments/yookassa/webhook` for `payment.succeeded` and `payment.canceled`.
4. Make a test payment. The application retrieves the payment from YooKassa and compares its order id, amount, currency, and status before it enables Premium.

Never put YooKassa keys in frontend files or Git. The user is redirected to YooKassa for card entry, so HockeyScrapper does not process or store card data.
