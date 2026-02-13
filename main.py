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
    date: str # 基準日
    base: str # 基準通貨コード
    rates: dict[str, float] # 通貨コードとレートの辞書
    fetched_at: str  # データ取得日時（ISOフォーマット）

class Config(TypedDict):
    base: str
    targets: list[str]
    bucket: str
    prefix: str

def request_api_exchange_rate(base: str, targets: list[str]) -> dict:
    """ APIリクエスト """

    url = "https://api.frankfurter.dev/v1/latest"
    params = {
        "from": base,
        "to": ",".join(targets),
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def build_exchange_result(data: dict) -> ExchangeResult:
    """ APIレスポンスからExchangeResultに変換 """

    return {
        "date": data["date"],
        "base": data["base"],
        "rates": data["rates"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

def get_exchange_rate(base: str, targets: list[str]) -> ExchangeResult | None:
    """ 為替レート取得 """

    try:
        data = request_api_exchange_rate(base, targets)
        return build_exchange_result(data)

    except requests.exceptions.Timeout:
        logger.exception(f"APIタイムアウトが発生しました")
        return None
    except requests.exceptions.RequestException:
        logger.exception(f"APIエラーが発生しました")
        return None
    except Exception:
        logger.exception(f"エラーが発生しました")
        return None

def save_to_json(result: ExchangeResult) -> Path:
    """ JOSONファイルの一時保存 """
    output_dir = Path(tempfile.gettempdir()) / "exchange_rates"
    output_dir.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%dT%H-%M-%SZ")
    file_path = output_dir / f"exchange_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info("JSONファイル保存完了 path=%s", file_path)
    return file_path

def upload_to_s3(file_path: Path, bucket_name: str, prefix: str) -> None:
    """ S3アップロード """

    s3_key = f"{prefix}/{file_path.name}"

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            str(file_path),
            bucket_name,
            s3_key,
            ExtraArgs={"ContentType": "application/json"},
        )
        logger.info("S3アップロード完了 s3://%s/%s", bucket_name, s3_key)

        # 一時ファイル（tempfile配下のJSONファイル）を削除する
        if file_path.exists():
            file_path.unlink()
            logger.info("一時ファイル削除完了 path=%s", file_path)
    except Exception:
        logger.exception("S3へのアップロードに失敗しました。")
        raise

    return

def get_config() -> Config:
    """ 環境変数の取得 """

    base = os.getenv("BASE_CURRENCY", "USD")
    targets = os.getenv("TARGET_CURRENCIES", "JPY,EUR,GBP")
    bucket = os.getenv("S3_BUCKET_NAME")
    prefix = os.getenv("S3_PREFIX")

    # 環境変数のチェック
    if not bucket:
        raise ValueError("S3_BUCKET_NAME が設定されていません。")
    if not prefix:
        raise ValueError("S3_PREFIX が設定されていません。")
    # targets
    target_currencies = [t.strip() for t in targets.split(",")]
    # JPY が含まれていない場合は先頭に追加
    if "JPY" not in target_currencies:
        target_currencies.insert(0, "JPY")
        logger.info("リストに JPY が含まれていなかったため、先頭に追加しました。")

    return {
        "base": base,
        "targets": target_currencies,
        "bucket": bucket,
        "prefix": prefix,
    }

def display_rates(result: ExchangeResult, targets: list[str]) -> None:
    """ 為替レートの表示 """

    #  USD_JPY レートを取得
    usd_jpy_rate = result['rates'].get("JPY", 0)
    logger.info(f"為替レート取得結果（基準日:{result['date']}）")
    # targets のリスト順にループを回す
    for target in targets:
        rate = result['rates'].get(target)
        if rate is None:
            continue

        if target == "JPY":
            # 基準通貨(USD)とJPYのペアを表示
            display_name = f"{result['base']}_{target}"
            display_rate = rate
        else:
            # それ以外の通貨は対円(XXX_JPY)に変換
            display_name = f"{target}_JPY"
            display_rate = usd_jpy_rate / rate
            
        # ログ出力
        logger.info(f"{display_name}: {display_rate:.2f} 円")

def run() -> None:
    # ロギング設定
    setup_logging()

    # 環境変数の取得
    try:
        config = get_config()
    except ValueError as e:
        logger.exception(f"環境変数の取得に失敗しました。エラー: {e}")
        sys.exit(1)

    # 為替レートを取得
    result = get_exchange_rate(base=config["base"], targets=config["targets"])
    if not result:
        logger.error("為替レートの取得に失敗しました。")
        sys.exit(1)
    logger.info("為替レート取得完了")

    # 結果をJSONファイルに保存
    json_path = save_to_json(result)

    # S3 アップロード
    upload_to_s3(file_path=json_path, bucket_name=config["bucket"], prefix=config["prefix"])

    # 為替レートの表示
    display_rates(result=result, targets=config["targets"])

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
    # .env ファイルの読み込み
    if load_dotenv:
        load_dotenv()

    run()