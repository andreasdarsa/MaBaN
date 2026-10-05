from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_valid_csv():
    csv_content = "transaction_id,item\nT1,milk\nT1,bread\nT2,milk\n"
    response = client.post(
        "/api/v1/upload",
        files={"file": ("transactions.csv", BytesIO(csv_content.encode()), "text/csv")},
        data={
            "dataset_format": "long",
            "transaction_col": "transaction_id",
            "item_col": "item",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "transactions.csv"
    assert data["rows"] == 3
    assert data["columns"] == ["transaction_id", "item"]


def test_upload_empty_csv_is_rejected():
    response = client.post(
        "/api/v1/upload",
        files={"file": ("empty.csv", BytesIO(b"transaction_id,item\n"), "text/csv")},
        data={
            "dataset_format": "long",
            "transaction_col": "transaction_id",
            "item_col": "item",
        },
    )
    assert response.status_code == 422


def test_upload_invalid_csv_is_rejected():
    response = client.post(
        "/api/v1/upload",
        files={"file": ("invalid.csv", BytesIO(b'"unterminated'), "text/csv")},
        data={
            "dataset_format": "long",
            "transaction_col": "transaction_id",
            "item_col": "item",
        },
    )
    assert response.status_code == 422
