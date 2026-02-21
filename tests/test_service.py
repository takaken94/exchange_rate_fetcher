from unittest.mock import patch
from main import fetch_exchange_rate
import logging
import requests

def test_fetch_exchange_rate_success():
    mock_data = {
        "date": "2026-02-20",
        "base": "JPY",
        "rates": {
            "EUR": 0.54756,
            "USD": 0.64431
        }
    }

    with patch("main.request_api_exchange_rate", return_value=mock_data):
        exchange_rates = fetch_exchange_rate("JPY", ["EUR", "USD"])

    # 検証
    assert exchange_rates is not None
    assert len(exchange_rates) == 2

    # 共通項の検証
    for er in exchange_rates:
        assert er.base_date.isoformat() == "2026-02-20"
        assert er.base == "JPY"

    # 通貨ごとの検証
    currencies = {er.currency: er for er in exchange_rates}
    assert currencies["EUR"].rate == 182.63
    assert currencies["USD"].rate == 155.20

def test_fetch_exchange_rate_api_timeout(caplog):
    """ 異常系: APIタイムアウト """

    caplog.set_level(logging.ERROR)
    with patch("main.requests.get", side_effect=requests.exceptions.Timeout):
        result = fetch_exchange_rate("USD", ["JPY"])

    assert result is None
    assert "APIタイムアウト" in caplog.text

def test_fetch_exchange_rate_api_error(caplog):
    """ 異常系: APIエラー """

    caplog.set_level(logging.ERROR)
    with patch("main.requests.get", side_effect=requests.exceptions.RequestException("API Error")):
        result = fetch_exchange_rate("USD", ["JPY"])

    assert result is None
    assert "APIエラー" in caplog.text