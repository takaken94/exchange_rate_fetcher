import requests
import logging
from typing import TypedDict
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from src.logging_config import setup_logging
import boto3
import tempfile

logger = logging.getLogger(Path(__file__).stem)

class ExchangeResult(TypedDict):
    date: str # 為替レート基準日
    base: str
    rates: dict[str, float] # 通貨コードとレートの辞書
    fetched_at: str  # データ取得日時（ISOフォーマット）

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
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except requests.exceptions.Timeout:
        logger.exception(f"タイムアウトが発生しました")
        return None
    except requests.exceptions.RequestException:
        logger.exception(f"APIエラーが発生しました")
        return None
    except Exception:
        logger.exception(f"エラーが発生しました")
        return None

def save_to_json(result: ExchangeResult) -> Path:
    output_dir = Path(tempfile.gettempdir()) / "exchange_rates"
    output_dir.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%dT%H-%M-%SZ")
    file_path = output_dir / f"exchange_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("JSON保存完了 path=%s", file_path)
    return file_path

def upload_to_s3(file_path: Path, bucket_name: str, prefix: str) -> None:

    s3_key = f"{prefix}/{file_path.name}"

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            str(file_path),
            bucket_name,
            s3_key,
            ExtraArgs={"ContentType": "application/json"},
        )
    except Exception:
        logger.exception("S3へのアップロードに失敗しました。")
        raise

    logger.info("S3アップロード完了 s3://%s/%s", bucket_name, s3_key)
    return

def run() -> None:

    # ロギング設定
    setup_logging()

    # .env ファイルの読み込み
    if load_dotenv:
        load_dotenv()
    base_currency = os.getenv("BASE_CURRENCY")
    if not base_currency:
        base_currency = "JPY"
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        logger.error("S3_BUCKET_NAME が設定されていません。")
        sys.exit(1)
    prefix = os.getenv("S3_PREFIX")
    if not prefix:
        logger.error("S3_PREFIX が設定されていません。")
        sys.exit(1)

    # パラメータ設定
    target_currencies = ["USD", "EUR", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD", "KRW"]

    # 為替レートを取得
    result = get_exchange_rate(base=base_currency, targets=target_currencies)
    if not result:
        logger.error("為替レートの取得に失敗しました。")
        sys.exit(1)

    logger.info(f"為替レート取得結果 ({result['date']})")
    # 取得した各通貨（USD, EURなど）についてループ処理
    for target, rate in result['rates'].items():
        # 逆数を計算して「1ターゲット通貨 = 〇〇 JPY」にする
        jpy_rate = 1 / rate
        display_name = f"{target}_{result['base']}"
        # 結果を表示
        logger.info(f"{display_name}: {jpy_rate:.2f} 円")

    # 結果をJSONファイルに保存
    json_path = save_to_json(result)

    # S3 アップロード
    upload_to_s3(json_path, bucket_name, prefix)

def lambda_handler(evnt, context):
    """
    AWS Lambda エントリーポイント
    """
    run()
    return {
        "statusCode": 200,
        "message": "exchange rate fetched and uploaded"
    }

if __name__ == "__main__":
    run()