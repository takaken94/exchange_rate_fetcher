import requests
from dataclasses import dataclass
from typing import Optional

# データの構造を定義
@dataclass
class ExchangeData:
    date: str
    rate: float
    base: str
    target: str

def get_exchange_rate_simple(base="USD", target="JPY") -> Optional[ExchangeData]:
    url = "https://api.frankfurter.app/latest"
    params = {"from": base, "to": target}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # クラスのインスタンスとして返す
        return ExchangeData(
            date=data["date"],
            rate=data["rates"][target],
            base=base,
            target=target
        )
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    result = get_exchange_rate_simple("USD", "JPY")
    
    if result:
        print(f"--- 取得結果 ---")
        # ドット演算子でアクセスできる（エディタで補完が効く！）
        print(f"日付: {result.date}")
        print(f"レート: {result.rate}")
        print(f"元の通貨: {result.base}")
        print(f"対象通貨: {result.target}")