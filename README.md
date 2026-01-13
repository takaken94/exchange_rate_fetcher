# Exchange Rate Fetcher

## 概要
外部API (https://frankfurter.dev/) から為替レートを定期取得して保存する。

## 使用技術
- Python 3.11
- requests
- Docker
- AWS (Lambda, S3, EventBridge)

## 機能
- 為替レート取得
- APIエラー時のリトライ
- ログ出力
- S3への保存

## システム構成
（簡単な構成図 or テキスト）

## 実行方法
### 開発環境
Windows 11 + WSL2 + Docker Engine を想定
```bash
docker build -f docker/Dockerfile -t exchange_rate_fetcher .
docker run --rm -e BASE_CURRENCY=JPY exchange_rate_fetcher
```

### 運用環境
AWS Lambda + Amazon EventBridge