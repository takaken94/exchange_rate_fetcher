from main import build_exchange_result

def test_build_exchange_result_format():
    """ 正常系: 為替レートデータ構築 """

    # APIレスポンス
    response = {
        "amount": 100,
        "base": "JPY",
        "date": "2026-02-20",
        "rates": {
            "EUR": 0.54756,
            "USD": 0.64431
        }
    }
    # 実行
    exchange_rates = build_exchange_result(response)
    
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