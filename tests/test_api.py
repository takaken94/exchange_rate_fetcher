from unittest.mock import patch, Mock
from main import request_api_exchange_rate

def test_request_api_exchange_rate():
    """ 正常系: APIリクエスト """

    mock_response = Mock()
    mock_response.json.return_value = {"dummy": "data"}
    mock_response.raise_for_status.return_value = None

    with patch("main.requests.get", return_value=mock_response) as m:
        request_api_exchange_rate("JPY", ["USD", "EUR"])

    m.assert_called_once()
    args, kwargs = m.call_args
    assert kwargs["params"]["symbols"] == "USD,EUR"
    assert kwargs["timeout"] == 10
