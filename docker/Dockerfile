FROM python:3.11-slim

ENV TZ=Asia/Tokyo

RUN apt-get update \
    && apt-get install -y tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && echo "Asia/Tokyo" > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 環境変数
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコード
COPY src/ ./src
COPY tests/ ./tests

CMD ["python", "src/main.py"]