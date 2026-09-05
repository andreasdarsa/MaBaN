from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


DATASET = [
    {
        "transaction_id": "T1",
        "items": ["milk", "bread", "butter"],
    },
    {
        "transaction_id": "T2",
        "items": ["milk", "bread"],
    },
    {
        "transaction_id": "T3",
        "items": ["bread", "butter"],
    },
    {
        "transaction_id": "T4",
        "items": ["milk", "butter"],
    },
    {
        "transaction_id": "T5",
        "items": ["milk", "bread", "butter"],
    },
]

def test_analysis_apriori():
    response = client.post(
        "/api/v1/analysis",
        json={
            "transactions": DATASET,
            "algorithm": "apriori",
            "min_support": 0.4,
            "max_len": 3,
            "rule_metric": "confidence",
            "rule_threshold": 0.5,
            "top_n": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_summary"]["num_transactions"] == 5
    assert data["dataset_summary"]["num_unique_items"] == 3

    assert data["mining_statistics"]["num_transactions"] == 5
    assert data["mining_statistics"]["num_items"] == 3

    assert isinstance(data["frequent_itemsets"], list)
    assert isinstance(data["rules"], list)
    assert isinstance(data["top_items"], list)
    assert isinstance(data["top_itemsets"], list)
    assert isinstance(data["top_rules"], list)
    assert isinstance(data["item_role_summary"], list)

def test_analysis_fpgrowth():
    response = client.post(
        "/api/v1/analysis",
        json={
            "transactions": DATASET,
            "algorithm": "fpgrowth",
            "min_support": 0.4,
            "max_len": 3,
            "rule_metric": "confidence",
            "rule_threshold": 0.5,
            "top_n": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_summary"]["num_transactions"] == 5
    assert data["dataset_summary"]["num_unique_items"] == 3

    assert data["mining_statistics"]["num_transactions"] == 5
    assert data["mining_statistics"]["num_items"] == 3

def test_analysis_invalid_min_support():
    response = client.post(
        "/api/v1/analysis",
        json={
            "transactions": DATASET,
            "algorithm": "apriori",
            "min_support": 1.5,
        },
    )

    assert response.status_code == 422

def test_analysis_empty_transactions():
    response = client.post(
        "/api/v1/analysis",
        json={
            "transactions": [],
            "algorithm": "apriori",
            "min_support": 0.4,
        },
    )

    assert response.status_code == 422

def test_analysis_no_frequent_itemsets():
    response = client.post(
        "/api/v1/analysis",
        json={
            "transactions": DATASET,
            "algorithm": "apriori",
            "min_support": 1.0,
            "max_len": 3,
            "rule_metric": "confidence",
            "rule_threshold": 0.5,
            "top_n": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["frequent_itemsets"] == []
    assert data["rules"] == []
    assert data["top_itemsets"] == []
    assert data["top_rules"] == []
    