import pytest
from unittest.mock import patch
import os
import main
from main import Config
from tests.test_utils import make_rate

def test_run_success():
    """正常系: 必要な関数が呼ばれ、例外を投げずに終了することを確認"""
    mock_config = Config(base="JPY", targets=["USD", "EUR"], bucket="b", prefix="p")
    rates = [make_rate("EUR", 182.63), make_rate("USD", 155.20)]

    called = {}

    def fake_setup():
        called['setup'] = True

    def fake_display_exchange_rate(rates=rates):
        called['logged'] = rates

    with patch("main.setup_logging", fake_setup), \
         patch("main.get_config", return_value=mock_config), \
         patch("main.fetch_exchange_rate", return_value=rates) as m_get, \
         patch("main.upload_to_s3") as m_upload, \
         patch("main.display_exchange_rate", fake_display_exchange_rate):
        # should not raise
        main.run()

    assert called.get('setup')
    m_get.assert_called_once_with(base=mock_config.base, targets=mock_config.targets)
    m_upload.assert_called_once_with(rates=rates, bucket_name=mock_config.bucket, prefix=mock_config.prefix)
    assert called.get('logged') == rates

def test_get_config_defaults():
    """環境変数未設定時にデフォルトが使われる"""
    envs = {"S3_BUCKET_NAME": "b", "S3_PREFIX": "p"}
    rates = [make_rate("EUR", 182.63), make_rate("GBP", 209.24), make_rate("USD", 155.20)]
    with patch.dict(os.environ, envs, clear=True), \
         patch("main.setup_logging"), \
         patch("main.fetch_exchange_rate", return_value=rates) as m_get, \
         patch("main.upload_to_s3"), \
         patch("main.display_exchange_rate"):
        main.run()

    _, kwargs = m_get.call_args
    targets = kwargs.get('targets')
    assert targets == ["USD", "EUR", "GBP"]

def test_get_config_failure():
    """ 異常系: 環境変数の取得で例外発生し終了することを確認 """
    with patch.dict(os.environ, {"S3_PREFIX": "p"}, clear=True), \
         patch("main.setup_logging"), \
         patch("main.get_config", side_effect=ValueError("no env")):
        with pytest.raises(SystemExit) as e:
            main.run()

    assert e.value.code == 1

def test_fetch_exchange_rate_failure():
    """異常系: 為替レートが取得できなかったときに終了コード1になる"""
    mock_config = Config(base="USD", targets=["JPY", "EUR"], bucket="b", prefix="p")
    with patch("main.setup_logging"), \
         patch("main.get_config", return_value=mock_config), \
         patch("main.fetch_exchange_rate", return_value=None):
        with pytest.raises(SystemExit) as e:
            main.run()

    assert e.value.code == 1