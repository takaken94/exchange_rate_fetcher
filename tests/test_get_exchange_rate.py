import logging
import requests
from unittest.mock import patch, Mock
from main import build_exchange_result, request_api_exchange_rate, get_exchange_rate

def test_request_api_exchange_rate():
    """ 正常系: APIリクエスト """

    mock_response = Mock()
    mock_response.json.return_value = {"dummy": "data"}
    mock_response.raise_for_status.return_value = None

    with patch("main.requests.get", return_value=mock_response):
        data = request_api_exchange_rate("USD", ["JPY", "EUR"])

    # 検証
    assert data is not None
    assert data == {"dummy": "data"}

def test_build_exchange_result_format():
    """ 正常系: 為替レートデータ構築 """

    # APIレスポンス
    data = {
        "date": "2026-02-13",
        "base": "USD",
        "rates": {"JPY": 150.0}
    }
    # 実行
    result = build_exchange_result(data)
    
    # 検証
    assert result["date"] == "2026-02-13"
    assert result["base"] == "USD"
    assert result["rates"]["JPY"] == 150.0
    assert "fetched_at" in result

def test_get_exchange_rate_success():
    mock_data = {
        "date": "2026-02-13",
        "base": "USD",
        "rates": {"JPY": 150.0}
    }

    with patch("main.request_api_exchange_rate", return_value=mock_data):
        result = get_exchange_rate("USD", ["JPY"])

    assert result is not None
    assert result["date"] == "2026-02-13"
    assert result["base"] == "USD"
    assert result["rates"]["JPY"] == 150.0
    assert "fetched_at" in result

def test_get_exchange_rate_api_timeout(caplog):
    """ 異常系: APIタイムアウト """

    caplog.set_level(logging.ERROR)
    with patch("main.requests.get", side_effect=requests.exceptions.Timeout):
        result = get_exchange_rate("USD", ["JPY"])

    assert result is None
    assert "APIタイムアウト" in caplog.text

def test_get_exchange_rate_api_error(caplog):
    """ 異常系: APIエラー """

    caplog.set_level(logging.ERROR)
    with patch("main.requests.get", side_effect=requests.exceptions.RequestException("API Error")):
        result = get_exchange_rate("USD", ["JPY"])

    assert result is None
    assert "APIエラー" in caplog.text