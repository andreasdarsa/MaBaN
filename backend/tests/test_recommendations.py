from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


RULES = [
    {
        "antecedents": ["milk"],
        "consequents": ["bread"],
        "support": 0.4,
        "confidence": 0.8,
        "lift": 1.2,
    },
    {
        "antecedents": ["milk"],
        "consequents": ["butter"],
        "support": 0.3,
        "confidence": 0.6,
        "lift": 1.1,
    },
    {
        "antecedents": ["bread"],
        "consequents": ["butter"],
        "support": 0.3,
        "confidence": 0.7,
        "lift": 1.15,
    },
]

def test_recommendations():
    response = client.post(
        "/api/v1/recommendations",
        json={
            "rules": RULES,
            "basket": ["milk"],
            "top_n": 5,
            "ranking_metric": "confidence",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["basket"] == ["milk"]
    assert data["ranking_metric"] == "confidence"
    assert data["top_n"] == 5

    assert data["statistics"]["num_matching_rules"] == 2
    assert data["statistics"]["num_candidate_items"] == 2
    assert data["statistics"]["num_recommendations"] == 2

    assert len(data["recommendations"]) == 2

def test_recommendations_ranking():
    response = client.post(
        "/api/v1/recommendations",
        json={
            "rules": RULES,
            "basket": ["milk"],
            "top_n": 5,
            "ranking_metric": "confidence",
        },
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    assert recommendations[0]["item"] == "bread"
    assert recommendations[0]["score"] == 0.8

    assert recommendations[1]["item"] == "butter"
    assert recommendations[1]["score"] == 0.6

def test_recommendations_no_matching_rules():
    response = client.post(
        "/api/v1/recommendations",
        json={
            "rules": RULES,
            "basket": ["chocolate"],
            "top_n": 5,
            "ranking_metric": "confidence",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["statistics"]["num_matching_rules"] == 0
    assert data["statistics"]["num_candidate_items"] == 0
    assert data["statistics"]["num_recommendations"] == 0

    assert data["recommendations"] == []

def test_recommendations_top_n():
    response = client.post(
        "/api/v1/recommendations",
        json={
            "rules": RULES,
            "basket": ["milk"],
            "top_n": 1,
            "ranking_metric": "confidence",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["statistics"]["num_matching_rules"] == 2
    assert data["statistics"]["num_candidate_items"] == 2
    assert data["statistics"]["num_recommendations"] == 1

    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["item"] == "bread"

def test_recommendations_invalid_top_n():
    response = client.post(
        "/api/v1/recommendations",
        json={
            "rules": RULES,
            "basket": ["milk"],
            "top_n": 0,
            "ranking_metric": "confidence",
        },
    )

    assert response.status_code == 422

def test_recommendations_empty_basket():
    response = client.post(
        "/api/v1/recommendations",
        json={
            "rules": RULES,
            "basket": [],
            "top_n": 5,
            "ranking_metric": "confidence",
        },
    )

    assert response.status_code == 422
    