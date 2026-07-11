from Backend import payments


def register_user(client, email="billing@example.com"):
    response = client.post(
        "/register",
        json={
            "username": "billinguser",
            "email": email,
            "telegram": "@billinguser",
            "password": "Billingpass123",
        },
    )
    assert response.status_code == 200
    return response.json()


def auth_headers(user):
    return {"Authorization": f"Bearer {user['access_token']}"}


def test_free_plan_limits_team_subscriptions(client):
    user = register_user(client)
    headers = auth_headers(user)

    for index in range(3):
        response = client.post(
            "/subscription/toggle",
            headers=headers,
            json={"chat_id": user["chat_id"], "team_name": f"Team {index}"},
        )
        assert response.status_code == 200

    response = client.post(
        "/subscription/toggle",
        headers=headers,
        json={"chat_id": user["chat_id"], "team_name": "Fourth team"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "premium_required"


def test_user_cannot_manage_another_users_subscriptions(client):
    first_user = register_user(client, "first-billing@example.com")
    second_user = register_user(client, "second-billing@example.com")

    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(first_user),
        json={"chat_id": second_user["chat_id"], "team_name": "CSKA"},
    )
    assert response.status_code == 403


def test_checkout_creates_yookassa_redirect(client, monkeypatch):
    user = register_user(client)
    monkeypatch.setenv("APP_BASE_URL", "https://hockeyscrapper.example")

    monkeypatch.setattr(
        payments,
        "create_payment",
        lambda **kwargs: {
            "id": "provider-payment-1",
            "status": "pending",
            "confirmation": {"confirmation_url": "https://payment.example/checkout"},
        },
    )

    response = client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={"plan_code": "monthly"},
    )
    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://payment.example/checkout"


def test_verified_webhook_activates_premium(client, monkeypatch):
    user = register_user(client)
    monkeypatch.setenv("APP_BASE_URL", "https://hockeyscrapper.example")

    def fake_create_payment(**kwargs):
        return {
            "id": "provider-payment-2",
            "status": "pending",
            "confirmation": {"confirmation_url": "https://payment.example/checkout"},
        }

    monkeypatch.setattr(payments, "create_payment", fake_create_payment)
    checkout = client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={"plan_code": "annual"},
    )
    assert checkout.status_code == 200
    payment_id = checkout.json()["payment_id"]

    monkeypatch.setattr(
        payments,
        "get_payment",
        lambda provider_payment_id: {
            "id": provider_payment_id,
            "status": "succeeded",
            "amount": {"value": "2990.00", "currency": "RUB"},
            "metadata": {"order_id": payment_id},
        },
    )
    webhook = client.post("/payments/yookassa/webhook", json={"object": {"id": "provider-payment-2"}})
    assert webhook.status_code == 200

    membership = client.get("/billing/me", headers=auth_headers(user))
    assert membership.status_code == 200
    assert membership.json()["is_premium"] is True
    assert membership.json()["plan"] == "annual"


def test_webhook_rejects_payment_with_wrong_order(client, monkeypatch):
    user = register_user(client)
    monkeypatch.setenv("APP_BASE_URL", "https://hockeyscrapper.example")
    monkeypatch.setattr(
        payments,
        "create_payment",
        lambda **kwargs: {
            "id": "provider-payment-3",
            "status": "pending",
            "confirmation": {"confirmation_url": "https://payment.example/checkout"},
        },
    )
    response = client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={"plan_code": "monthly"},
    )
    assert response.status_code == 200

    monkeypatch.setattr(
        payments,
        "get_payment",
        lambda provider_payment_id: {
            "id": provider_payment_id,
            "status": "succeeded",
            "amount": {"value": "299.00", "currency": "RUB"},
            "metadata": {"order_id": "someone-elses-order"},
        },
    )
    webhook = client.post("/payments/yookassa/webhook", json={"object": {"id": "provider-payment-3"}})
    assert webhook.status_code == 400
