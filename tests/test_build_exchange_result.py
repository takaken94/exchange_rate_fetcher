from main import build_exchange_result

def test_build_exchange_result_format():
    """ 正常系: 為替レートデータ構築 """

    # APIレスポンス
    response = {
        "date": "2026-02-13",
        "base": "USD",
        "rates": {
            "EUR": 0.85,
            "JPY": 150.0
        }
    }
    # 実行
    exchange_rates = build_exchange_result(response)
    
    # 検証
    assert exchange_rates is not None
    assert len(exchange_rates) == 2

    # 共通項の検証
    for er in exchange_rates:
        assert er.date.isoformat() == "2026-02-13"
        assert er.base == "USD"

    # 通貨ごとの検証
    currencies = {er.currency: er for er in exchange_rates}
    assert currencies["EUR"].rate == 0.85
    assert currencies["JPY"].rate == 150.0