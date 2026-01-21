from unittest.mock import patch, Mock
from main import get_exchange_rate
from typing import TypedDict

class MockApiResponse(TypedDict):
    date: str
    rates: dict[str, float]

def test_get_exchange_rate_success():
    mock_response: MockApiResponse = {
        "date": "2026-01-13",
        "rates": {"USD": 0.007}
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        result = get_exchange_rate("JPY", ["USD"])

    assert result is not None
    assert result["base"] == "JPY"
    assert result["rates"]["USD"] == 0.007

def test_get_exchange_rate_api_error():
    import requests
    from unittest.mock import patch

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        result = get_exchange_rate("JPY", ["USD"])

    assert result is None
