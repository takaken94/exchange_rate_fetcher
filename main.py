import requests
from typing import TypedDict

class ExchangeResult(TypedDict):
    date: str
    base: str
    rates: dict[str, float] # 通貨コードとレートの辞書

def get_exchange_rate(base: str, targets: list[str]) -> ExchangeResult | None:
    # API のURL
    url = "https://api.frankfurter.app/latest"
    # targets をカンマ区切りの文字列に変換
    target_str = ",".join(targets)
    params = {
        "from": base,
        "to": target_str,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "date": data["date"],
            "base": base,
            "rates": data["rates"],
        }
    except requests.exceptions.RequestException as e:
        print(f"APIエラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # パラメータ設定
    base_currency = "JPY"
    target_currencies = ["USD", "EUR", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "KRW"]

    # 為替レートを取得
    result = get_exchange_rate(base=base_currency, targets=target_currencies)
    
    if result:
        print(f"--- 為替レート取得結果 ({result['date']}) ---")
        
        # 取得した各通貨（USD, EURなど）についてループ処理
        for target, rate in result['rates'].items():
            # 逆数を計算して「1ターゲット通貨 = 〇〇 JPY」にする
            jpy_rate = 1 / rate
            display_name = f"{target}_{result['base']}"
            # 結果を表示
            print(f"{display_name}: {jpy_rate:.2f} 円")