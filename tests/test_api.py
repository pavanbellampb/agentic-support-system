
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint():
    mock_result = {
        "answer": "Your order is in transit.",
        "intent": "order",
        "order_result": "Your order is in transit.",
        "policy_result": None,
    }

    with patch("app.main.support_graph.invoke", return_value=mock_result) as mock_invoke:
        response = client.post(
            "/chat",
            json={"message": "Where is my order?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Your order is in transit."
    assert data["intent"] == "order"
    mock_invoke.assert_called_once_with({"message": "Where is my order?"})
