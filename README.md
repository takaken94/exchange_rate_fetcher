# Exchange Rate Fetcher

## 概要
外部APIから為替レートを定期取得して保存する。

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
### ローカル
docker build / docker run

### AWS
Lambda + EventBridge