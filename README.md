# Exchange Rate Fetcher

## 概要
外部APIから為替レートを取得して、JSON形式ファイルを S3にアップロードする。

## 使用技術
- Python 3.11
- requests ライブラリ
- AWS (Lambda, S3, EventBridge)

## 機能
- 外部APIから為替レート取得
- JSON形式でファイル一時保存
- S3 にアップロード

## 実行方法
### 開発環境
Windows 11 + WSL2 (Ubuntu) + Dev Container を想定。<br>
前提条件: aws sso login で認証済みであること。

```bash
python main.py
```

```plaintext
vscode ➜ /workspaces/exchange_rate_fetcher (main) $ python main.py
2026-01-21 11:11:57,886 INFO main .env ファイルから環境変数の値を読み込みました。
2026-01-21 11:11:58,769 INFO main 為替レート取得結果 (2026-01-20)
2026-01-21 11:11:58,770 INFO main AUD_JPY: 106.27 円
2026-01-21 11:11:58,770 INFO main CAD_JPY: 114.16 円
2026-01-21 11:11:58,770 INFO main CHF_JPY: 200.00 円
2026-01-21 11:11:58,770 INFO main CNY_JPY: 22.69 円
2026-01-21 11:11:58,771 INFO main EUR_JPY: 185.19 円
2026-01-21 11:11:58,771 INFO main GBP_JPY: 212.31 円
2026-01-21 11:11:58,771 INFO main HKD_JPY: 20.25 円
2026-01-21 11:11:58,771 INFO main KRW_JPY: 0.11 円
2026-01-21 11:11:58,771 INFO main NZD_JPY: 92.17 円
2026-01-21 11:11:58,771 INFO main USD_JPY: 157.98 円
2026-01-21 11:11:58,784 INFO main JSONファイル保存完了 path=/tmp/exchange_rates/exchange_2026-01-21T02-11-58Z.json
2026-01-21 11:11:58,953 INFO botocore.tokens Loading cached SSO token for takaken94-sso
2026-01-21 11:11:59,303 INFO botocore.tokens SSO Token refresh succeeded
2026-01-21 11:12:00,004 INFO main S3アップロード完了 s3://takaken94-exchange-rate-fetcher/rates-data/exchange_2026-01-21T02-11-58Z.json
2026-01-21 11:12:00,005 INFO main 一時ファイル削除完了 path=/tmp/exchange_rates/exchange_2026-01-21T02-11-58Z.json
```

### テスト
```bash
pytest
```

```plaintext
================================================================================ test session starts ================================================================================
platform linux -- Python 3.11.14, pytest-9.0.2, pluggy-1.6.0
rootdir: /workspaces/exchange_rate_fetcher
collected 2 items                                                                                                                                                                   

tests/test_exchange.py ..                                                                                                                                                     [100%]

================================================================================= 2 passed in 0.27s =================================================================================
```

### 運用環境
```
システム構成

EventBridge スケジュール（cron 定期実行）
      ↓
Lambda 関数 exchange-rate-fetcher（zip）
      ↓
S3バケット takaken94-exchange-rate-fetcher/rates-data/
```

## ファイルサンプル
```json
ファイル名: exchange_2026-01-21T02-11-58Z.json
ファイル内容:
{
  "date": "2026-01-20",
  "base": "JPY",
  "rates": {
    "AUD": 0.00941,
    "CAD": 0.00876,
    "CHF": 0.005,
    "CNY": 0.04407,
    "EUR": 0.0054,
    "GBP": 0.00471,
    "HKD": 0.04939,
    "KRW": 9.353,
    "NZD": 0.01085,
    "USD": 0.00633
  },
  "fetched_at": "2026-01-21T02:11:58.768828+00:00"
}
```
