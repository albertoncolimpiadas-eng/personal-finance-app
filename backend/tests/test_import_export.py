from fastapi.testclient import TestClient


def seed_import_dependencies(client: TestClient) -> None:
    assert client.post(
        "/accounts",
        json={"name": "Checking", "type": "current_account"},
    ).status_code == 201
    assert client.post(
        "/categories",
        json={"name": "Salary", "type": "income"},
    ).status_code == 201
    assert client.post(
        "/categories",
        json={"name": "Groceries", "type": "expense"},
    ).status_code == 201


def test_preview_transactions_csv(client: TestClient) -> None:
    seed_import_dependencies(client)
    csv_content = (
        "date,description,amount,account_name,category_name,transaction_type\n"
        "2026-05-15,May salary,1000.00,Checking,Salary,income\n"
        "bad-date,Bad row,nope,Missing,Groceries,expense\n"
    )

    response = client.post(
        "/imports/transactions-csv/preview",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid_count"] == 1
    assert body["invalid_count"] == 1
    assert body["rows"][0]["valid"] is True
    assert "date must be a valid ISO date" in body["rows"][1]["errors"]
    assert "amount must be a valid decimal" in body["rows"][1]["errors"]
    assert "account must exist" in body["rows"][1]["errors"]


def test_confirm_transactions_csv_imports_valid_rows(client: TestClient) -> None:
    seed_import_dependencies(client)
    csv_content = (
        "date,description,amount,account_name,category_name,transaction_type\n"
        "2026-05-15,May salary,1000.00,Checking,Salary,income\n"
        "2026-05-16,Groceries,25.50,Checking,Groceries,expense\n"
    )

    response = client.post(
        "/imports/transactions-csv/confirm",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )
    transactions = client.get("/transactions").json()

    assert response.status_code == 200
    assert response.json()["imported_count"] == 2
    assert [transaction["description"] for transaction in transactions] == [
        "Groceries",
        "May salary",
    ]


def test_export_transactions_csv(client: TestClient) -> None:
    seed_import_dependencies(client)
    csv_content = (
        "date,description,amount,account_name,category_name,transaction_type\n"
        "2026-05-15,May salary,1000.00,Checking,Salary,income\n"
    )
    client.post(
        "/imports/transactions-csv/confirm",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )

    response = client.get("/exports/transactions.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "date,description,amount,account_name,category_name,transaction_type" in response.text
    assert "May salary" in response.text
