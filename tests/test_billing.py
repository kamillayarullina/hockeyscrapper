from datetime import datetime, timedelta

from Backend import models
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


def checkout(client, user, team="CSKA", plan_code="team_monthly", auto_renew=False):
    return client.post(
        "/billing/checkout",
        headers=auth_headers(user),
        json={
            "team_name": team,
            "plan_code": plan_code,
            "enable_auto_renew": auto_renew,
        },
    )


def test_first_team_requires_a_paid_plan(client):
    user = register_user(client)

    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )

    assert response.status_code == 402
    detail = response.json()["detail"]
    assert detail["code"] == "payment_required"
    assert detail["team_name"] == "CSKA"
    assert detail["plans"] == [
        {"code": "team_monthly", "amount_rub": 39},
        {"code": "team_yearly", "amount_rub": 390},
    ]


def test_user_cannot_manage_another_users_subscriptions(client):
    first_user = register_user(client, "first-billing@example.com")
    second_user = register_user(client, "second-billing@example.com")

    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(first_user),
        json={"chat_id": second_user["chat_id"], "team_name": "CSKA"},
    )

    assert response.status_code == 403


def test_legacy_free_team_is_removed_and_now_requires_payment(client, db_session):
    user = register_user(client, "legacy-free@example.com")
    db_session.add(models.SubscriptionModel(chat_id=user["chat_id"], type="team", value="cska"))
    db_session.commit()

    membership = client.get("/billing/me", headers=auth_headers(user))
    response = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )

    assert membership.status_code == 200
    assert membership.json()["team_subscription_count"] == 0
    assert response.status_code == 402


def test_billing_plans_are_monthly_and_yearly_mock_plans(client):
    response = client.get("/billing/plans")

    assert response.status_code == 200
    data = response.json()
    assert data["payment_mode"] == "mock"
    assert data["free_team_limit"] == 0
    assert data["plans"] == [
        {
            "code": "team_monthly",
            "name": "Подписка на команду на месяц",
            "amount_rub": 39,
            "duration_days": 30,
            "period_label": "месяц",
        },
        {
            "code": "team_yearly",
            "name": "Подписка на команду на год",
            "amount_rub": 390,
            "duration_days": 365,
            "period_label": "год",
        },
    ]


def test_monthly_mock_checkout_activates_first_team(client, db_session):
    user = register_user(client, "monthly@example.com")

    response = checkout(client, user, auto_renew=True)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["plan_code"] == "team_monthly"
    assert "Реальные деньги не списывались" in data["message"]

    payment = db_session.query(models.PaymentModel).one()
    assert payment.provider == "mock"
    assert payment.amount_kopeks == 3900
    assert payment.status == "succeeded"

    subscription = db_session.query(models.PaidTeamSubscriptionModel).one()
    assert subscription.team_name == "cska"
    assert subscription.plan_code == "team_monthly"
    assert subscription.auto_renew is True
    assert timedelta(days=29) < subscription.expires_at - datetime.utcnow() <= timedelta(days=30)


def test_yearly_mock_checkout_activates_team_for_a_year(client, db_session):
    user = register_user(client, "yearly@example.com")

    response = checkout(client, user, team="SKA", plan_code="team_yearly")

    assert response.status_code == 200
    payment = db_session.query(models.PaymentModel).one()
    subscription = db_session.query(models.PaidTeamSubscriptionModel).one()
    assert payment.amount_kopeks == 39000
    assert subscription.plan_code == "team_yearly"
    assert timedelta(days=364) < subscription.expires_at - datetime.utcnow() <= timedelta(days=365)


def test_unknown_plan_is_rejected(client):
    user = register_user(client, "unknown-plan@example.com")

    response = checkout(client, user, plan_code="lifetime")

    assert response.status_code == 400
    assert response.json()["detail"] == "Unknown subscription plan"


def test_duplicate_active_team_cannot_be_purchased_again(client):
    user = register_user(client, "duplicate@example.com")
    assert checkout(client, user).status_code == 200

    response = checkout(client, user)

    assert response.status_code == 409
    assert response.json()["detail"] == "You are already subscribed to this team"


def test_unsubscribe_keeps_paid_access_and_resubscribe_is_free(client):
    user = register_user(client, "resubscribe@example.com")
    assert checkout(client, user).status_code == 200

    unsubscribe = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )
    assert unsubscribe.status_code == 200
    assert unsubscribe.json()["status"] == "removed"

    resubscribe = client.post(
        "/subscription/toggle",
        headers=auth_headers(user),
        json={"chat_id": user["chat_id"], "team_name": "CSKA"},
    )
    assert resubscribe.status_code == 200
    assert resubscribe.json()["status"] == "added"


def test_paid_subscription_list_contains_plan_and_expiry(client):
    user = register_user(client, "list@example.com")
    assert checkout(client, user, plan_code="team_yearly").status_code == 200

    response = client.get("/billing/subscriptions", headers=auth_headers(user))

    assert response.status_code == 200
    subscription = response.json()["subscriptions"][0]
    assert subscription["team_name"] == "cska"
    assert subscription["plan_code"] == "team_yearly"
    assert subscription["price_rub"] == 390
    assert subscription["period_label"] == "год"
    assert subscription["is_active"] is True


def test_auto_renew_can_be_enabled_and_disabled_without_payment_method(client):
    user = register_user(client, "auto-renew@example.com")
    assert checkout(client, user).status_code == 200

    enabled = client.patch(
        "/billing/subscriptions/cska/auto-renew",
        headers=auth_headers(user),
        json={"enabled": True},
    )
    disabled = client.patch(
        "/billing/subscriptions/cska/auto-renew",
        headers=auth_headers(user),
        json={"enabled": False},
    )

    assert enabled.status_code == 200
    assert enabled.json()["auto_renew"] is True
    assert disabled.status_code == 200
    assert disabled.json()["auto_renew"] is False


def test_expired_subscription_without_auto_renew_stops_notifications(client, db_session):
    user = register_user(client, "expired@example.com")
    db_session.add(models.SubscriptionModel(chat_id=user["chat_id"], type="team", value="cska"))
    db_session.add(
        models.PaidTeamSubscriptionModel(
            chat_id=user["chat_id"],
            team_name="cska",
            plan_code="team_monthly",
            expires_at=datetime.utcnow() - timedelta(days=1),
            auto_renew=False,
        )
    )
    db_session.commit()

    response = client.get(f"/subscriptions/{user['chat_id']}", headers=auth_headers(user))

    assert response.status_code == 200
    assert "cska" not in response.json()["subscriptions"]


def test_due_yearly_auto_renewal_is_simulated(client, db_session):
    user = register_user(client, "due-renewal@example.com")
    db_session.add(models.SubscriptionModel(chat_id=user["chat_id"], type="team", value="ska"))
    subscription = models.PaidTeamSubscriptionModel(
        chat_id=user["chat_id"],
        team_name="ska",
        plan_code="team_yearly",
        expires_at=datetime.utcnow() - timedelta(minutes=1),
        auto_renew=True,
    )
    db_session.add(subscription)
    db_session.commit()

    result = process_due_renewals(db_session)

    db_session.refresh(subscription)
    payment = db_session.query(models.PaymentModel).one()
    assert result["renewals_started"] == 1
    assert payment.provider == "mock"
    assert payment.amount_kopeks == 39000
    assert payment.status == "succeeded"
    assert timedelta(days=364) < subscription.expires_at - datetime.utcnow() <= timedelta(days=365)


def test_billing_endpoints_require_authentication(client):
    assert client.get("/billing/me").status_code in {401, 403}
    assert client.get("/billing/subscriptions").status_code in {401, 403}
    assert client.post(
        "/billing/checkout",
        json={"team_name": "CSKA", "plan_code": "team_monthly"},
    ).status_code in {401, 403}
