from unittest.mock import patch
import os
import main
from main import get_exchange_rate

def test_run_logic_jpy_injection():
    """環境変数に JPY がなくても自動追加されることをテスト"""
    # 環境変数
    mock_envs = {
        "BASE_CURRENCY": "USD",
        "TARGET_CURRENCIES": "EUR, GBP ", # JPYなし、前後に空白
        "S3_BUCKET_NAME": "dummy-bucket",
        "S3_PREFIX": "dummy-prefix"
    }
    
    with patch.dict(os.environ, mock_envs, clear=True), \
         patch("main.get_exchange_rate") as mock_get, \
         patch("main.save_to_json"), \
         patch("main.upload_to_s3"), \
         patch("main.setup_logging"):
        
        # APIの戻り値を設定
        mock_get.return_value = {
            "date": "2026-01-21",
            "base": "USD",
            "rates": {
                "EUR": 0.9,
                "GBP": 0.8,
                "JPY": 150.0
            },
            "fetched_at": "2026-01-21T00:00:00Z"
        }

        # runを実行
        main.run()

        # get_exchange_rate が呼ばれた際の targets 引数を確認
        _, kwargs = mock_get.call_args
        targets = kwargs.get('targets')
        
        assert "JPY" in targets
        assert targets[0] == "JPY"   # JPY が先頭に追加される
        assert " " not in targets[1] # 空白が除去される
        assert targets == ["JPY", "EUR", "GBP"]

def test_default_target_currencies_used():
    """ 環境変数が未設定時のデフォルト値使用テスト """
    # 環境変数
    mock_envs = {
        "S3_BUCKET_NAME": "dummy-bucket",
        "S3_PREFIX": "dummy-prefix"
    }

    with patch.dict(os.environ, mock_envs, clear=True), \
         patch("main.get_exchange_rate") as mock_get, \
         patch("main.save_to_json"), \
         patch("main.upload_to_s3"), \
         patch("main.setup_logging"):

        # APIの戻り値を設定
        mock_get.return_value = {
            "date": "2026-01-21",
            "base": "USD",
            "rates": {
                "EUR": 0.9,
                "GBP": 0.8,
                "JPY": 150.0
                },
            "fetched_at": "2026-01-21T00:00:00Z"
        }

        main.run()

        # get_exchange_rate が呼ばれた際の targets 引数を確認
        _, kwargs = mock_get.call_args
        targets = mock_get.call_args.kwargs["targets"]

        assert targets == ["JPY", "EUR", "GBP"]

def test_cross_rate_calculation(caplog):
    """ログに出力される対円計算結果が正しいか確認"""
    import logging
    caplog.set_level(logging.INFO)

    mock_result = {
        "date": "2026-01-21",
        "base": "USD",
        "rates": {
            "EUR": 0.75,  # 150 / 0.75 = 200.00 円になるはず
            "JPY": 150.0
        },
        "fetched_at": "2026-01-21T00:00:00Z"
    }

    with patch.dict(os.environ, {"BASE_CURRENCY": "USD", "TARGET_CURRENCIES": "JPY,EUR", "S3_BUCKET_NAME": "b", "S3_PREFIX": "p"}), \
         patch("main.get_exchange_rate", return_value=mock_result), \
         patch("main.save_to_json"), \
         patch("main.upload_to_s3"):
        
        main.run()
        
        # ログの内容を検証
        assert "USD_JPY: 150.00 円" in caplog.text
        assert "EUR_JPY: 200.00 円" in caplog.text