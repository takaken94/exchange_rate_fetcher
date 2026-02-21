import requests
import json
import boto3
from datetime import datetime, timezone

def reprocess_exchange_rates(start_date: str, end_date: str):
    # 設定
    bucket_name = "takaken94-exchange-rate"
    base_prefix = "rate-data"
    symbols = "USD,EUR,GBP,CAD,AUD"
    
    # APIリクエスト (amount=100で精度を確保)
    url = f"https://api.frankfurter.dev/v1/{start_date}..{end_date}?amount=100&base=JPY&symbols={symbols}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        rates_by_date = data.get("rates", {})
        s3_client = boto3.client("s3")

        for date_str, rates in rates_by_date.items():
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            fetched_at = datetime.now(timezone.utc).isoformat()
            
            # JSON Lines 形式の作成
            # 100で割って1円あたりのレート（対円）に直して保存
            jsonl_content = []
            for currency, val_per_100 in rates.items():
                rate_jpy = round(100 / val_per_100, 2)
                record = {
                    "base_date": date_str,
                    "base": "JPY",
                    "currency": currency,
                    "rate": rate_jpy,
                    "fetched_at": fetched_at,
                }
                jsonl_content.append(json.dumps(record))
            
            # S3のパス作成 (Hive形式パーティション)
            # 例: rate-data/year=2026/month=01/rates_20260102.jsonl
            file_key = f"{base_prefix}/year={dt.year}/month={dt.strftime('%m')}/rates_{dt.strftime('%Y%m%d')}.jsonl"
            
            # S3へアップロード
            s3_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body="\n".join(jsonl_content),
                ContentType="application/x-jsonlines"
            )
            print(f"Successfully uploaded: {file_key}")

    except Exception as e:
        print(f"Error during reprocessing: {e}")

# 実行例
if __name__ == "__main__":
    reprocess_exchange_rates("2026-02-02", "2026-02-20")