# Exchange Rate Fetcher

## 概要
外部APIから為替レートを取得して保存する。

## 使用技術
- Python 3.11
- requests
- Docker
<!-- - AWS (Lambda, EventBridge, S3) -->

## 機能
- 為替レート取得
- JSON形式での保存
- ログ出力
<!-- - S3への保存 -->

<!-- 
## システム構成
（簡単な構成図 or テキスト）
-->

## 実行方法
### 開発環境
Windows 11 + WSL2 (Ubuntu) + Docker Engine を想定
```bash
docker build -f docker/Dockerfile -t exchange_rate_fetcher .
docker run --rm -e BASE_CURRENCY=JPY -v $(pwd)/data:/app/data exchange_rate_fetcher
```
### テスト
```bash
docker run --rm -e BASE_CURRENCY=JPY -v $(pwd)/data:/app/data exchange_rate_fetcher pytest
```

<!-- 
### 運用環境
AWS Lambda + Amazon EventBridge + Amazon S3
-->

## 出力例
- JSON形式で為替レートを保存
- 実行ごとにタイムスタンプ付きファイルを生成
```json
{
  "date": "2026-01-13",
  "base": "JPY",
  "rates": {
    "AUD": 0.0094,
    "CAD": 0.00874,
    "CHF": 0.00503,
    "CNY": 0.04391,
    "EUR": 0.0054,
    "GBP": 0.00468,
    "HKD": 0.04912,
    "KRW": 9.2799,
    "NZD": 0.01093,
    "USD": 0.0063
  }
}
```
