"""Small, server-side YooKassa client used by the billing API.

Card details never reach HockeyScrapper: YooKassa hosts the confirmation page.
"""

import os
from typing import Any

import httpx


YOOKASSA_API_URL = "https://api.yookassa.ru/v3"


class PaymentProviderError(RuntimeError):
    """Raised when YooKassa cannot create or retrieve a payment."""


def _credentials() -> tuple[str, str]:
    shop_id = os.getenv("YOOKASSA_SHOP_ID", "")
    secret_key = os.getenv("YOOKASSA_SECRET_KEY", "")
    if not shop_id or not secret_key:
        raise PaymentProviderError("YooKassa is not configured")
    return shop_id, secret_key


def create_payment(
    *,
    amount: str,
    description: str,
    return_url: str,
    order_id: str,
    idempotency_key: str,
) -> dict[str, Any]:
    """Create a redirect payment and return YooKassa's payment object."""
    response = httpx.post(
        f"{YOOKASSA_API_URL}/payments",
        auth=_credentials(),
        headers={"Idempotence-Key": idempotency_key},
        json={
            "amount": {"value": amount, "currency": "RUB"},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": description,
            "metadata": {"order_id": order_id},
        },
        timeout=15.0,
    )
    if response.is_error:
        raise PaymentProviderError("YooKassa could not create the payment")
    return response.json()


def get_payment(provider_payment_id: str) -> dict[str, Any]:
    """Retrieve payment status from YooKassa instead of trusting a webhook body."""
    response = httpx.get(
        f"{YOOKASSA_API_URL}/payments/{provider_payment_id}",
        auth=_credentials(),
        timeout=15.0,
    )
    if response.is_error:
        raise PaymentProviderError("YooKassa could not verify the payment")
    return response.json()
