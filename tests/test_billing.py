from datetime import datetime, timedelta

from Backend import models, payments
from Backend.main import process_due_renewals


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
        json={"team_name": "CSKA", "enable_auto_renew": True},
    )
    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://payment.example/checkout"
    assert captured["amount"] == "39.00"
    assert captured["description"] == "HockeyScrapper: подписка на CSKA"
    assert captured["save_payment_method"] is True


def test_local_demo_checkout_activates_team_without_yookassa(client, monkeypatch):
    user = register_user(client, "demo-billing@example.com")
    add_three_free_teams(client, user)
    monkeypatch.setenv("APP_BASE_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("BILLING_DEMO_MODE", "true")

    response = client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={"team_name": "CSKA", "enable_auto_renew": True},
    )
    assert response.status_code == 200
    assert response.json()["checkout_url"].startswith("http://127.0.0.1:8000/billing.html?payment=success")

    subscriptions = client.get(f"/subscriptions/{user['chat_id']}", headers=auth_headers(user))
    assert "cska" in subscriptions.json()["subscriptions"]
    paid = client.get("/billing/subscriptions", headers=auth_headers(user)).json()["subscriptions"][0]
    assert paid["auto_renew"] is True


def test_local_demo_can_enable_auto_renew_after_first_payment(client, db_session, monkeypatch):
    user = register_user(client, "demo-toggle@example.com")
    monkeypatch.setenv("APP_BASE_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("BILLING_DEMO_MODE", "true")
    db_session.add(
        models.PaidTeamSubscriptionModel(
            chat_id=user["chat_id"],
            team_name="cska",
            expires_at=datetime.utcnow() + timedelta(days=30),
            auto_renew=False,
        )
    )
    db_session.commit()

    response = client.patch(
        "/billing/subscriptions/cska/auto-renew",
        headers=auth_headers(user),
        json={"enabled": True},
    )
    assert response.status_code == 200
    assert response.json()["auto_renew"] is True


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
        json={"team_name": "CSKA", "enable_auto_renew": True},
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
            "payment_method": {"id": "saved-card-1", "saved": True},
        },
    )
    webhook = client.post("/payments/yookassa/webhook", json={"object": {"id": "provider-payment-2"}})
    assert webhook.status_code == 200

    subscriptions = client.get(f"/subscriptions/{user['chat_id']}", headers=auth_headers(user))
    assert subscriptions.status_code == 200
    assert "cska" in subscriptions.json()["subscriptions"]
    assert subscriptions.json()["membership"]["team_subscription_count"] == 4
    assert subscriptions.json()["membership"]["paid_team_price_rub"] == 39

    paid_subscriptions = client.get("/billing/subscriptions", headers=auth_headers(user))
    assert paid_subscriptions.status_code == 200
    paid_team = paid_subscriptions.json()["subscriptions"][0]
    assert paid_team["team_name"] == "cska"
    assert paid_team["is_active"] is True
    assert paid_team["auto_renew"] is True
    assert paid_team["can_enable_auto_renew"] is True

    disable_auto_renew = client.patch(
        "/billing/subscriptions/cska/auto-renew",
        headers=auth_headers(user),
        json={"enabled": False},
    )
    assert disable_auto_renew.json()["auto_renew"] is False

    # Unsubscribing only disables notifications while the monthly subscription is active.
    unsubscribe = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )
    assert unsubscribe.status_code == 200

    resubscribe = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )
    assert resubscribe.status_code == 200
    subscriptions = client.get(f"/subscriptions/{user['chat_id']}", headers=auth_headers(user))
    assert "cska" in subscriptions.json()["subscriptions"]

    # A paid team does not occupy a free slot: replacing a free team is still free.
    remove_free_team = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "Team 0"},
    )
    assert remove_free_team.status_code == 200
    replacement = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "Replacement team"},
    )
    assert replacement.status_code == 200


def test_expired_paid_team_subscription_stops_notifications(client, db_session):
    user = register_user(client)
    add_three_free_teams(client, user)
    db_session.add(models.SubscriptionModel(chat_id=user["chat_id"], type="team", value="cska"))
    db_session.add(
        models.PaidTeamSubscriptionModel(
            chat_id=user["chat_id"],
            team_name="cska",
            expires_at=datetime.utcnow() - timedelta(minutes=1),
            auto_renew=False,
        )
    )
    db_session.commit()

    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )
    assert response.status_code == 402
    subscriptions = client.get(f"/subscriptions/{user['chat_id']}", headers=auth_headers(user))
    assert "cska" not in subscriptions.json()["subscriptions"]


def test_due_auto_renewal_creates_yookassa_payment(db_session, monkeypatch):
    db_session.add(
        models.PaidTeamSubscriptionModel(
            chat_id=99,
            team_name="cska",
            expires_at=datetime.utcnow() - timedelta(minutes=1),
            auto_renew=True,
            payment_method_id="saved-card-1",
        )
    )
    db_session.commit()
    captured = {}

    def fake_recurring_payment(**kwargs):
        captured.update(kwargs)
        return {"id": "renewal-payment-1", "status": "pending"}

    monkeypatch.setattr(payments, "create_recurring_payment", fake_recurring_payment)
    result = process_due_renewals(db_session)

    assert result["renewals_started"] == 1
    assert captured["amount"] == "39.00"
    assert captured["payment_method_id"] == "saved-card-1"
    payment = db_session.query(models.PaymentModel).filter(
        models.PaymentModel.provider_payment_id == "renewal-payment-1"
    ).first()
    assert payment.plan_code == "team_subscription_renewal"


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
