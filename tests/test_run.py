import pytest
from unittest.mock import patch
import os
import main
from main import Config
from tests.test_utils import make_rate

def test_run_success():
    """正常系: 必要な関数が呼ばれ、例外を投げずに終了することを確認"""
    mock_config = Config(base="USD", targets=["JPY"], bucket="b", prefix="p")
    result = [make_rate("JPY", 152.0)]
    display = ("2026-02-13", [{"name": "USD_JPY", "rate": 152.0}])

    called = {}

    def fake_setup():
        called['setup'] = True

    def fake_log_display_rates(base_date, display_rates):
        called['logged'] = (base_date, display_rates)

    with patch("main.setup_logging", fake_setup), \
         patch("main.get_config", return_value=mock_config), \
         patch("main.fetch_exchange_rate", return_value=result) as m_get, \
         patch("main.upload_to_s3") as m_upload, \
         patch("main.calculate_display_rates", return_value=display) as m_calc, \
         patch("main.log_display_rates", fake_log_display_rates):
        # should not raise
        main.run()

    assert called.get('setup')
    m_get.assert_called_once_with(base=mock_config.base, targets=mock_config.targets)
    m_upload.assert_called_once_with(rates=result, bucket_name=mock_config.bucket, prefix=mock_config.prefix)
    m_calc.assert_called_once_with(rates=result, targets=mock_config.targets)
    assert called.get('logged') == display


def test_get_config_defaults():
    """環境変数未設定時にデフォルトが使われる"""
    envs = {"S3_BUCKET_NAME": "b", "S3_PREFIX": "p"}
    result = {"base_date": "2026-02-13", "rates": {"JPY": 150.0, "EUR": 0.9, "GBP": 0.8}}
    with patch.dict(os.environ, envs, clear=True), \
         patch("main.setup_logging"), \
         patch("main.fetch_exchange_rate", return_value=result) as m_get, \
         patch("main.upload_to_s3"), \
         patch("main.calculate_display_rates", return_value=("2026-02-13", [])), \
         patch("main.log_display_rates"):
        main.run()

    _, kwargs = m_get.call_args
    targets = kwargs.get('targets')
    assert targets == ["JPY", "EUR", "GBP"]

def test_get_config_failure():
    """ 異常系: 環境変数の取得で例外発生し終了することを確認 """
    with patch.dict(os.environ, {"S3_PREFIX": "p"}, clear=True), \
         patch("main.setup_logging"), \
         patch("main.get_config", side_effect=ValueError("no env")):
        with pytest.raises(SystemExit) as e:
            main.run()

    assert e.value.code == 1

def test_get_config_raises_value_error_if_no_jpy():
    """異常系: JPYがない場合に ValueError を投げるか"""
    mock_envs = {
        "TARGET_CURRENCIES": "EUR,GBP",
        "S3_BUCKET_NAME": "b",
        "S3_PREFIX": "p"
    }
    with patch.dict(os.environ, mock_envs, clear=True):
        # 1. 例外が発生することを検証
        with pytest.raises(ValueError) as excinfo:
            main.get_config()
        
        # 2. エラーメッセージが意図通りかを assert で検証
        assert "JPY が含まれていません" in str(excinfo.value)

def test_fetch_exchange_rate_failure():
    """異常系: 為替レートが取得できなかったときに終了コード1になる"""
    mock_config = Config(base="USD", targets=["JPY", "EUR"], bucket="b", prefix="p")
    with patch("main.setup_logging"), \
         patch("main.get_config", return_value=mock_config), \
         patch("main.fetch_exchange_rate", return_value=None):
        with pytest.raises(SystemExit) as e:
            main.run()

    assert e.value.code == 1