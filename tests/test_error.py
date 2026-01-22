import pytest
from unittest.mock import patch
import os
import main
from main import get_exchange_rate

def test_get_exchange_rate_api_error():
    """ 異常系: APIエラー """
    import requests

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        result = get_exchange_rate("USD", ["JPY", "EUR"])

    assert result is None

def test_run_fail_error():
    """ 異常系: 異常発生時の終了テスト """
    with patch.dict(os.environ, {"S3_PREFIX": "p"}, clear=True), \
         patch("main.setup_logging"):
        with pytest.raises(SystemExit) as e:
            main.run()

    assert e.value.code == 1
