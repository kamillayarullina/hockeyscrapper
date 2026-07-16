from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, inspect, text

from Backend import models
from Backend import database as backend_database
from Backend.main import TEAM_MONTHLY_PLAN, TEAM_YEARLY_PLAN, process_due_renewals


def _register(client, suffix: str = "billing") -> tuple[int, dict[str, str]]:
    response = client.post("/register", json={
        "username": f"user_{suffix}",
        "email": f"{suffix}@example.com",
        "telegram": f"@{suffix}",
        "password": "Testpass123!",
    })
    assert response.status_code == 200
    data = response.json()
    return data["chat_id"], {"Authorization": f"Bearer {data['access_token']}"}


def test_plans_match_customer_prices_and_are_always_simulated(client):
    response = client.get("/billing/plans")

    assert response.status_code == 200
    data = response.json()
    assert data["free_team_limit"] == 0
    assert data["payment_mode"] == "simulation"
    assert data["real_money_charged"] is False
    assert [(plan["code"], plan["amount_rub"], plan["duration_days"]) for plan in data["plans"]] == [
        (TEAM_MONTHLY_PLAN, 39, 30),
        (TEAM_YEARLY_PLAN, 390, 365),
    ]
    assert data["plans"][1]["amount_rub"] == data["plans"][0]["amount_rub"] * 10


def test_first_team_requires_payment(client):
    chat_id, headers = _register(client, "first_paid")

    response = client.post(
        "/subscription/toggle",
        headers=headers,
        json={"chat_id": chat_id, "team_name": "Ак Барс"},
    )

    assert response.status_code == 402
    detail = response.json()["detail"]
    assert detail["code"] == "payment_required"
    assert detail["monthly_price_rub"] == 39
    assert detail["yearly_price_rub"] == 390
    subscriptions = client.get(f"/subscriptions/{chat_id}", headers=headers).json()
    assert subscriptions["subscriptions"] == []


def test_monthly_checkout_immediately_activates_team_without_charging_money(client):
    chat_id, headers = _register(client, "monthly")

    response = client.post(
        "/billing/checkout",
        headers=headers,
        json={"team_name": "Ак Барс", "plan_code": TEAM_MONTHLY_PLAN},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["amount_rub"] == 39
    assert data["duration_days"] == 30
    assert data["payment_mode"] == "simulation"
    assert data["real_money_charged"] is False
    assert "реальные деньги не списывались" in data["message"]

    subscriptions = client.get(f"/subscriptions/{chat_id}", headers=headers).json()
    assert subscriptions["subscriptions"] == ["ак барс"]

    paid = client.get("/billing/subscriptions", headers=headers).json()["subscriptions"]
    assert len(paid) == 1
    assert paid[0]["plan_code"] == TEAM_MONTHLY_PLAN
    assert paid[0]["amount_rub"] == 39
    assert paid[0]["is_active"] is True


def test_yearly_checkout_uses_ten_month_price_and_365_day_period(client):
    _, headers = _register(client, "yearly")
    before = datetime.now(timezone.utc).replace(tzinfo=None)

    response = client.post(
        "/billing/checkout",
        headers=headers,
        json={"team_name": "ЦСКА", "plan_code": TEAM_YEARLY_PLAN},
    )

    assert response.status_code == 200
    assert response.json()["amount_rub"] == 390
    paid = client.get("/billing/subscriptions", headers=headers).json()["subscriptions"][0]
    expires_at = datetime.fromisoformat(paid["expires_at"])
    assert paid["plan_code"] == TEAM_YEARLY_PLAN
    assert paid["period_label"] == "1 год"
    assert timedelta(days=364) < expires_at - before < timedelta(days=366)


def test_unknown_plan_does_not_create_subscription(client):
    chat_id, headers = _register(client, "bad_plan")

    response = client.post(
        "/billing/checkout",
        headers=headers,
        json={"team_name": "СКА", "plan_code": "lifetime"},
    )

    assert response.status_code == 400
    subscriptions = client.get(f"/subscriptions/{chat_id}", headers=headers).json()
    assert subscriptions["subscriptions"] == []


def test_legacy_free_team_is_disabled(client, db_session):
    chat_id, headers = _register(client, "legacy_free")
    db_session.add(models.SubscriptionModel(chat_id=chat_id, type="team", value="ска"))
    db_session.commit()

    response = client.get(f"/subscriptions/{chat_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["subscriptions"] == []
    assert db_session.query(models.SubscriptionModel).filter_by(chat_id=chat_id, type="team").count() == 0


def test_yearly_auto_renewal_is_simulated_with_same_plan(client, db_session):
    chat_id, headers = _register(client, "renew_year")
    checkout = client.post(
        "/billing/checkout",
        headers=headers,
        json={
            "team_name": "Спартак",
            "plan_code": TEAM_YEARLY_PLAN,
            "enable_auto_renew": True,
        },
    )
    assert checkout.status_code == 200

    subscription = db_session.query(models.PaidTeamSubscriptionModel).filter_by(
        chat_id=chat_id,
        team_name="спартак",
    ).one()
    subscription.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    db_session.commit()

    result = process_due_renewals(db_session)

    db_session.refresh(subscription)
    assert result == {"renewed": 1, "expired_disabled": 0}
    assert subscription.plan_code == TEAM_YEARLY_PLAN
    assert subscription.expires_at > datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=364)
    payments = db_session.query(models.PaymentModel).filter_by(chat_id=chat_id).all()
    assert len(payments) == 2
    assert all(payment.provider == "simulation" for payment in payments)
    assert all(payment.status == "succeeded" for payment in payments)


def test_schema_migration_removes_old_provider_credentials(tmp_path, monkeypatch):
    legacy_engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with legacy_engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (chat_id INTEGER PRIMARY KEY)"))
        connection.execute(text(
            "CREATE TABLE payments ("
            "id VARCHAR PRIMARY KEY, provider VARCHAR NOT NULL, "
            "provider_payment_id VARCHAR, status VARCHAR)"
        ))
        connection.execute(text(
            "INSERT INTO payments VALUES "
            "('old-payment', 'yookassa', 'external-id', 'pending')"
        ))
        connection.execute(text(
            "CREATE TABLE paid_team_subscriptions ("
            "chat_id INTEGER, team_name VARCHAR, payment_method_id VARCHAR)"
        ))
        connection.execute(text(
            "INSERT INTO paid_team_subscriptions VALUES (1, 'ска', 'saved-method-id')"
        ))
        connection.execute(text(
            "CREATE TABLE billing_profiles (chat_id INTEGER, payment_method_id VARCHAR)"
        ))

    monkeypatch.setattr(backend_database, "engine", legacy_engine)
    backend_database.ensure_schema()

    schema = inspect(legacy_engine)
    assert "billing_profiles" not in schema.get_table_names()
    assert "plan_code" in {column["name"] for column in schema.get_columns("paid_team_subscriptions")}
    with legacy_engine.connect() as connection:
        old_payment = connection.execute(text(
            "SELECT provider_payment_id, status FROM payments WHERE id = 'old-payment'"
        )).one()
        old_subscription = connection.execute(text(
            "SELECT payment_method_id, plan_code FROM paid_team_subscriptions"
        )).one()
    assert old_payment == (None, "canceled")
    assert old_subscription == (None, TEAM_MONTHLY_PLAN)
