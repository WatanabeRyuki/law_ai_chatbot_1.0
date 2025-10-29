FROM python:3.10-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ app/
COPY prompt_templates/ prompt_templates/

# 環境変数を設定
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# ポート8083を公開
EXPOSE 8083

# アプリケーションを起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083"]

