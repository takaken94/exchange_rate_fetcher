# S3バケットの作成
resource "aws_s3_bucket" "exchange_rate" {
  bucket = "takaken94-exchange-rate"

  tags = {
    Name        = "exchange-rate-bucket"
    Environment = "dev"
  }
}

# パブリックアクセスのブロック設定
resource "aws_s3_bucket_public_access_block" "exchange_rate" {
  bucket = aws_s3_bucket.exchange_rate.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}