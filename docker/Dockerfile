FROM python:3.11-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコード
COPY src/ ./src

CMD ["python", "src/main.py"]