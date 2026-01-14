import requests
import logging
from typing import TypedDict
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    except requests.exceptions.Timeout as e:
        logger.error(f"タイムアウトが発生しました: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"APIエラーが発生しました: {e}")
        return None
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return None

def save_to_json(result: ExchangeResult) -> Path:
    output_dir = Path("data")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = output_dir / f"exchange_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("JSON保存完了 path=%s", file_path)
    return file_path

if __name__ == "__main__":
    # .env ファイルの読み込み
    load_dotenv()
    base_currency = os.getenv("BASE_CURRENCY")
    if not base_currency:
        base_currency = "JPY"

    # パラメータ設定
    target_currencies = ["USD", "EUR", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "KRW"]

    # 為替レートを取得
    result = get_exchange_rate(base=base_currency, targets=target_currencies)
    
    if result:
        logger.info(f"為替レート取得結果 ({result['date']})")
        
        # 取得した各通貨（USD, EURなど）についてループ処理
        for target, rate in result['rates'].items():
            # 逆数を計算して「1ターゲット通貨 = 〇〇 JPY」にする
            jpy_rate = 1 / rate
            display_name = f"{target}_{result['base']}"
            # 結果を表示
            logger.info(f"{display_name}: {jpy_rate:.2f} 円")

        # 結果をJSONファイルに保存
        save_to_json(result)
    else:
        logger.error("為替レートの取得に失敗しました。")