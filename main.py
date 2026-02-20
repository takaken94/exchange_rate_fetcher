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
from datetime import date, datetime, timezone
import boto3
import io
from dataclasses import dataclass
from src.logging_config import setup_logging


logger = logging.getLogger(Path(__file__).stem)

@dataclass(frozen=True)
class ExchangeRate:
    base_date: date      # 基準日
    base: str            # 基準通貨コード
    currency: str        # 通貨コード
    rate: float          # 為替レート
    fetched_at: datetime # データ取得日時

@dataclass(frozen=True)
class Config:
    base: str            # 基準通貨コード
    targets: list[str]   # 取得対象通貨コードのリスト
    bucket: str          # S3バケット名
    prefix: str          # S3プレフィックス

    def __post_init__(self):
        """インスタンス化直後にバリデーションを実行"""
        if not self.bucket:
            raise ValueError("S3_BUCKET_NAME が設定されていません。")
        if not self.prefix:
            raise ValueError("S3_PREFIX が設定されていません。")
        if "JPY" not in self.targets:
            raise ValueError("TARGET_CURRENCIES に JPY が含まれていません。")

def request_api_exchange_rate(base: str, targets: list[str]) -> dict:
    """ APIリクエスト """

    url = "https://api.frankfurter.dev/v1/latest"
    params = {
        "base": base,
        "symbols": ",".join(targets),
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def build_exchange_result(data: dict) -> list[ExchangeRate]:
    """ APIレスポンスから為替レートデータ構築 """

    fetched_at = datetime.now(timezone.utc)

    results = []
    for currency, rate in data["rates"].items():
        results.append(
            ExchangeRate(
                base_date=datetime.fromisoformat(data["date"]).date(),
                base=data["base"],
                currency=currency,
                rate=rate,
                fetched_at=fetched_at,
            )
        )
    return results

def fetch_exchange_rate(base: str, targets: list[str]) -> list[ExchangeRate] | None:
    """ 為替レート取得 """

    try:
        response = request_api_exchange_rate(base, targets)
        return build_exchange_result(response)

    except requests.exceptions.Timeout:
        logger.exception("APIタイムアウトが発生しました")
        return None
    except requests.exceptions.RequestException:
        logger.exception("APIエラーが発生しました")
        return None
    except Exception:
        logger.exception("エラーが発生しました")
        return None

def exchange_rate_to_dict(rate: ExchangeRate) -> dict:
    return {
        "base_date": rate.base_date.isoformat(),
        "base": rate.base,
        "currency": rate.currency,
        "rate": rate.rate,
        "fetched_at": rate.fetched_at.isoformat(),
    }

def build_s3_key(base_prefix: str, target_date: date) -> str:
    year = target_date.strftime("%Y")
    month = target_date.strftime("%m")
    filename = f"rates_{target_date.strftime('%Y%m%d')}.json"

    return f"{base_prefix}/year={year}/month={month}/{filename}"

def upload_to_s3(rates: list[ExchangeRate], bucket_name: str, prefix: str) -> None:
    """ S3アップロード """

    if not rates:
        raise ValueError("アップロードする為替レートデータがありません。")

    # JSON Lines 形式でデータを作成する
    json_lines = "\n".join(json.dumps(exchange_rate_to_dict(r), ensure_ascii=False) for r in rates)

    # S3キーの生成
    target_date = rates[0].base_date
    s3_key = build_s3_key(prefix, target_date)

    # S3ファイルアップロード
    s3_client = boto3.client("s3")
    try:
        s3_client.put_object(
            Body=json_lines.encode("utf-8"),
            Bucket=bucket_name,
            Key=s3_key,
            ContentType="application/json",
        )
        logger.info("S3アップロード完了 s3://%s/%s", bucket_name, s3_key)
    except Exception:
        logger.exception("S3へのアップロードに失敗しました。")
        raise
    return

def get_config() -> Config:
    """ 環境変数を取得して Config オブジェクトを返す """

    targets = os.getenv("TARGET_CURRENCIES", "JPY,EUR,GBP")
    target_list = [t.strip() for t in targets.split(",")]

    return Config(
        base=os.getenv("BASE_CURRENCY", "USD"),
        targets=target_list,
        bucket=os.getenv("S3_BUCKET_NAME", ""),
        prefix=os.getenv("S3_PREFIX", ""),
    )

class DisplayRate(TypedDict):
    name: str
    rate: float

def calculate_display_rates(
    rates: list[ExchangeRate],
    targets: list[str],
) -> tuple[str, list[DisplayRate]]:
    """ 表示用レートを計算する """

    if not rates:
        return "", []

    base = rates[0].base
    base_date = rates[0].base_date.isoformat()

    rate_map = {r.currency: r.rate for r in rates}
    usd_jpy_rate = rate_map.get("JPY")

    results: list[DisplayRate] = []

    for target in targets:
        rate = rate_map.get(target)
        if rate is None:
            continue

        if target == "JPY":
            display_name = f"{base}_{target}"
            display_rate = rate
        else:
            if usd_jpy_rate is None:
                continue
            display_name = f"{target}_JPY"
            if rate == 0:
                continue
            display_rate = usd_jpy_rate / rate

        results.append({"name": display_name, "rate": display_rate})

    return base_date, results

def log_display_rates(base_date: str, display_rates: list[DisplayRate]) -> None:
    logger.info("為替レート取得結果（基準日:%s）", base_date)

    for r in display_rates:
        logger.info("%s: %.2f 円", r["name"], r["rate"])

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
    result = fetch_exchange_rate(base=config.base, targets=config.targets)
    if not result:
        logger.error("為替レートの取得に失敗しました。")
        sys.exit(1)
    logger.info("為替レート取得完了")

    # S3 アップロード
    upload_to_s3(rates=result, bucket_name=config.bucket, prefix=config.prefix)

    # 為替レートの表示
    base_date, display_rates = calculate_display_rates(rates=result, targets=config.targets)
    log_display_rates(base_date, display_rates)

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