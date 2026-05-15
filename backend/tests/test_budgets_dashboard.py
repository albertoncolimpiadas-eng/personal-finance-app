from decimal import Decimal

from fastapi.testclient import TestClient


def create_account(client: TestClient, name: str) -> int:
    response = client.post("/accounts", json={"name": name, "type": "current_account"})
    assert response.status_code == 201
    return int(response.json()["id"])


def create_category(client: TestClient, name: str, category_type: str) -> int:
    response = client.post("/categories", json={"name": name, "type": category_type})
    assert response.status_code == 201
    return int(response.json()["id"])


def create_transaction(
    client: TestClient,
    transaction_type: str,
    amount: str,
    category_id: int,
    account_id: int,
    description: str,
) -> int:
    response = client.post(
        "/transactions",
        json={
            "transaction_type": transaction_type,
            "amount": amount,
            "date": "2026-05-15",
            "description": description,
            "account_id": account_id,
            "category_id": category_id,
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_budget_create_and_monthly_summary(client: TestClient) -> None:
    account_id = create_account(client, "Checking")
    category_id = create_category(client, "Groceries", "expense")
    create_transaction(client, "expense", "40.00", category_id, account_id, "Groceries")

    budget_response = client.post(
        "/budgets",
        json={
            "category_id": category_id,
            "year": 2026,
            "month": 5,
            "limit_amount": "100.00",
        },
    )
    summary_response = client.get("/budgets/monthly-summary?year=2026&month=5")

    assert budget_response.status_code == 201
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert len(summary) == 1
    assert summary[0]["category"]["name"] == "Groceries"
    assert Decimal(summary[0]["limit_amount"]) == Decimal("100.00")
    assert Decimal(summary[0]["spent_amount"]) == Decimal("40.00")
    assert Decimal(summary[0]["remaining_amount"]) == Decimal("60.00")
    assert Decimal(summary[0]["percentage_used"]) == Decimal("40.00")


def test_budget_rejects_income_category_and_duplicates(client: TestClient) -> None:
    income_category_id = create_category(client, "Salary", "income")
    expense_category_id = create_category(client, "Housing", "expense")

    income_response = client.post(
        "/budgets",
        json={
            "category_id": income_category_id,
            "year": 2026,
            "month": 5,
            "limit_amount": "100.00",
        },
    )
    first_response = client.post(
        "/budgets",
        json={
            "category_id": expense_category_id,
            "year": 2026,
            "month": 5,
            "limit_amount": "100.00",
        },
    )
    duplicate_response = client.post(
        "/budgets",
        json={
            "category_id": expense_category_id,
            "year": 2026,
            "month": 5,
            "limit_amount": "150.00",
        },
    )

    assert income_response.status_code == 400
    assert income_response.json()["detail"] == "budget category must be an expense category"
    assert first_response.status_code == 201
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "budget already exists for this category/year/month"


def test_dashboard_monthly_summary(client: TestClient) -> None:
    account_id = create_account(client, "Checking")
    income_category_id = create_category(client, "Salary", "income")
    expense_category_id = create_category(client, "Restaurants", "expense")
    create_transaction(client, "income", "1000.00", income_category_id, account_id, "Salary")
    create_transaction(client, "expense", "250.00", expense_category_id, account_id, "Dinner")

    response = client.get("/dashboard/monthly-summary?year=2026&month=5")

    assert response.status_code == 200
    summary = response.json()
    assert Decimal(summary["total_income"]) == Decimal("1000.00")
    assert Decimal(summary["total_expense"]) == Decimal("250.00")
    assert Decimal(summary["net_savings"]) == Decimal("750.00")
    assert Decimal(summary["savings_rate"]) == Decimal("75.00")
    assert summary["income_by_category"][0]["category"]["name"] == "Salary"
    assert summary["expenses_by_category"][0]["category"]["name"] == "Restaurants"
    assert summary["account_balances"][0]["current_balance"] == "750.00"


def test_dashboard_empty_month_and_yearly_summary_return_zeros(client: TestClient) -> None:
    monthly_response = client.get("/dashboard/monthly-summary?year=2026&month=6")
    yearly_response = client.get("/dashboard/yearly-summary?year=2026")

    assert monthly_response.status_code == 200
    monthly_summary = monthly_response.json()
    assert monthly_summary["total_income"] == "0"
    assert monthly_summary["total_expense"] == "0"
    assert monthly_summary["net_savings"] == "0"
    assert monthly_summary["savings_rate"] == "0"
    assert monthly_summary["expenses_by_category"] == []
    assert monthly_summary["income_by_category"] == []

    assert yearly_response.status_code == 200
    yearly_summary = yearly_response.json()
    assert len(yearly_summary) == 12
    assert yearly_summary[0] == {
        "month": 1,
        "total_income": "0",
        "total_expense": "0",
        "net_savings": "0",
    }
