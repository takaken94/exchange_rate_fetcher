from datetime import date, datetime, timezone
import logging
import boto3
import main

def make_rate(currency: str, rate: float) -> main.ExchangeRate:
    # helper to create ExchangeRate for a fixed date/time
    return main.ExchangeRate(
        date=date(2026, 2, 13),
        base="USD",
        currency=currency,
        rate=rate,
        fetched_at=datetime(2026, 2, 13, tzinfo=timezone.utc),
    )

def test_calculate_display_rates_basic():
    # JPY only
    rates = [make_rate("JPY", 150.0)]
    base_date, display = main.calculate_display_rates(rates=rates, targets=["JPY"])
    assert base_date == "2026-02-13"
    assert display == [{"name": "USD_JPY", "rate": 150.0}]

def test_calculate_display_rates_cross():
    # JPY + EUR
    rates = [make_rate("JPY", 150.0), make_rate("EUR", 0.75)]
    base_date, display = main.calculate_display_rates(rates=rates, targets=["JPY", "EUR"])
    # JPY rate unchanged; EUR to JPY computed as 150/0.75
    assert display[0]["rate"] == 150.0
    assert display[1]["name"] == "EUR_JPY"
    assert abs(display[1]["rate"] - 200.0) < 1e-6

def test_calculate_display_rates_empty():
    base_date, display = main.calculate_display_rates(rates=[], targets=["JPY"])
    assert base_date == ""
    assert display == []

def test_log_display_rates(caplog):
    caplog.set_level(logging.INFO)
    rates_display: list[main.DisplayRate] = [
        {"name": "USD_JPY", "rate": 150.0},
        {"name": "EUR_JPY", "rate": 200.0}
    ]
    main.log_display_rates("2026-02-13", rates_display)
    assert "為替レート取得結果（基準日:2026-02-13）" in caplog.text
    assert "USD_JPY: 150.00 円" in caplog.text
    assert "EUR_JPY: 200.00 円" in caplog.text

def test_build_s3_key():
    d = date(2026, 2, 13)
    key = main.build_s3_key("prefix", d)
    assert key.startswith("prefix/year=2026/month=02/")
    assert key.endswith("rates_20260213.json")

def test_upload_to_s3_success(monkeypatch):
    rates = [make_rate("JPY", 150.0)]
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
    assert "JPY" in called['args'][0].decode("utf-8") # Body に JPY が含まれているか確認