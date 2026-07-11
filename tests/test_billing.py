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


def add_three_free_teams(client, user):
    for index in range(3):
        response = client.post(
            "/subscription/toggle",
            headers=auth_headers(user),
            json={"chat_id": user["chat_id"], "team_name": f"Team {index}"},
        )
        assert response.status_code == 200


def test_first_three_team_subscriptions_are_free(client):
    user = register_user(client)
    add_three_free_teams(client, user)

    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "Fourth team"},
    )
    assert response.status_code == 402
    assert response.json()["detail"] == {
        "code": "payment_required",
        "message": "Первые 3 команды бесплатны. Подписка на следующую команду стоит 39 ₽.",
        "team_name": "Fourth team",
        "price_rub": 39,
    }


def test_user_cannot_manage_another_users_subscriptions(client):
    first_user = register_user(client, "first-billing@example.com")
    second_user = register_user(client, "second-billing@example.com")

    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(first_user),
        json={"chat_id": second_user["chat_id"], "team_name": "CSKA"},
    )
    assert response.status_code == 403


def test_checkout_creates_payment_for_a_team(client, monkeypatch):
    user = register_user(client)
    add_three_free_teams(client, user)
    monkeypatch.setenv("APP_BASE_URL", "https://hockeyscrapper.example")

    captured = {}

    def fake_create_payment(**kwargs):
        captured.update(kwargs)
        return {
            "id": "provider-payment-1",
            "status": "pending",
            "confirmation": {"confirmation_url": "https://payment.example/checkout"},
        }

    monkeypatch.setattr(payments, "create_payment", fake_create_payment)
    response = client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={"team_name": "CSKA"},
    )
    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://payment.example/checkout"
    assert captured["amount"] == "39.00"
    assert captured["description"] == "HockeyScrapper: подписка на CSKA"


def test_verified_webhook_adds_paid_team_subscription(client, monkeypatch):
    user = register_user(client)
    add_three_free_teams(client, user)
    monkeypatch.setenv("APP_BASE_URL", "https://hockeyscrapper.example")

    monkeypatch.setattr(
        payments,
        "create_payment",
        lambda **kwargs: {
            "id": "provider-payment-2",
            "status": "pending",
            "confirmation": {"confirmation_url": "https://payment.example/checkout"},
        },
    )
    checkout = client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={"team_name": "CSKA"},
    )
    assert checkout.status_code == 200
    payment_id = checkout.json()["payment_id"]

    monkeypatch.setattr(
        payments,
        "get_payment",
        lambda provider_payment_id: {
            "id": provider_payment_id,
            "status": "succeeded",
            "amount": {"value": "39.00", "currency": "RUB"},
            "metadata": {"order_id": payment_id},
        },
    )
    webhook = client.post("/payments/yookassa/webhook", json={"object": {"id": "provider-payment-2"}})
    assert webhook.status_code == 200

    subscriptions = client.get(f"/subscriptions/{user['chat_id']}", headers=auth_headers(user))
    assert subscriptions.status_code == 200
    assert "cska" in subscriptions.json()["subscriptions"]
    assert subscriptions.json()["membership"]["team_subscription_count"] == 4
    assert subscriptions.json()["membership"]["paid_team_price_rub"] == 39


def test_webhook_rejects_payment_with_wrong_order(client, monkeypatch):
    user = register_user(client)
    add_three_free_teams(client, user)
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
        json={"team_name": "CSKA"},
    )
    assert response.status_code == 200

    monkeypatch.setattr(
        payments,
        "get_payment",
        lambda provider_payment_id: {
            "id": provider_payment_id,
            "status": "succeeded",
            "amount": {"value": "39.00", "currency": "RUB"},
            "metadata": {"order_id": "someone-elses-order"},
        },
    )
    webhook = client.post("/payments/yookassa/webhook", json={"object": {"id": "provider-payment-3"}})
    assert webhook.status_code == 400
