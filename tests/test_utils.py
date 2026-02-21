from datetime import date, datetime, timezone
import logging
import boto3
import main

def make_rate(currency: str, rate: float) -> main.ExchangeRate:
    return main.ExchangeRate(
        base_date=date(2026, 2, 20),
        base="JPY",
        currency=currency,
        rate=rate,
        fetched_at=datetime(2026, 2, 20, tzinfo=timezone.utc),
    )

def test_build_s3_key():
    d = date(2026, 2, 20)
    key = main.build_s3_key("prefix", d)
    assert key.startswith("prefix/year=2026/month=02/")
    assert key.endswith("rates_20260220.jsonl")

def test_upload_to_s3_success(monkeypatch):
    rates = [make_rate("USD", 155.20)]
    called = {}

    class FakeClient:
        # put_object メソッドに変更し、引数を受け取れるようにする
        def put_object(self, Body, Bucket, Key, ContentType):
            called['args'] = (Body, Bucket, Key, ContentType)

    # boto3.client("s3") が FakeClient を返すように設定
    monkeypatch.setattr(boto3, "client", lambda service: FakeClient())
    
    # 実行
    main.upload_to_s3(rates=rates, bucket_name="b", prefix="p")
    
    # 検証
    assert called['args'][1] == "b"  # Bucket が "b" か確認
    assert "USD" in called['args'][0].decode("utf-8") # Body に USD が含まれているか確認

def test_display_exchange_rate(caplog):
    caplog.set_level(logging.INFO)
    rates = [make_rate("EUR", 182.63), make_rate("USD", 155.20)]
    main.display_exchange_rate(rates=rates)

    # 検証
    assert "為替レート取得結果（基準日:2026-02-20）" in caplog.text
    assert "EUR_JPY: 182.63 円" in caplog.text
    assert "USD_JPY: 155.20 円" in caplog.text