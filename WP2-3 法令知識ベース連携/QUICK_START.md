# クイックスタートガイド

法令知識ベース連携モジュールの起動手順

## 1. 必要な環境

- Python 3.10+
- pip
- PostgreSQL 14+（オプション）
- Redis 6+（オプション）

## 2. セットアップ

```bash
# 1. ディレクトリに移動
cd "WP2-3 法令知識ベース連携"

# 2. 依存パッケージのインストール
pip install -r requirements.txt

# 3. 環境変数を設定
cp env.example .env

# 4. .env ファイルを編集（最低限の設定）
# GEMINI_API_KEY を設定（任意、モックモードも可能）
```

## 3. 起動方法

### 開発モード（推奨）

```bash
# モジュールとして起動
python -m app.main
```

または

```bash
# uvicorn で起動
uvicorn app.main:app --reload --port 8083
```

### 起動確認

ブラウザで以下のURLにアクセス：
- http://localhost:8083/docs - Swagger UI（API ドキュメント）
- http://localhost:8083 - ヘルスチェック

## 4. 基本的な使用例

### API テスト（curl）

```bash
# ヘルスチェック
curl http://localhost:8083/health

# 法令リスト取得
curl http://localhost:8083/laws/list?page=1&per_page=20

# 条文要約（POST）
curl -X POST http://localhost:8083/laws/CIVIL_LAW_001/articles/%E7%AC%AC1%E6%9D%A1/summarize \
  -H "Content-Type: application/json" \
  -d '{"max_length": 200, "style": "plain"}'
```

### Python サンプル

```python
import httpx

# ヘルスチェック
response = httpx.get("http://localhost:8083/health")
print(response.json())

# 法令リスト取得
response = httpx.get(
    "http://localhost:8083/laws/list",
    params={"page": 1, "per_page": 10}
)
print(response.json())
```

## 5. テスト実行

```bash
# 全てのテストを実行
pytest tests/

# 特定のテストファイル
pytest tests/test_api.py

# 詳細表示
pytest -v tests/
```

## 6. トラブルシューティング

### インポートエラー

```bash
# PYTHONPATH を設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m app.main
```

### ポートが既に使用されている場合

```bash
# 別のポートを使用
uvicorn app.main:app --reload --port 8084
```

### Gemini API キーが設定されていない場合

モックモードで自動的に動作します：
- 要約機能：条文の先頭部分を返す
- 論点抽出：簡易キーワード抽出

## 7. 本番環境でのデプロイ

### Docker を使用する場合

```bash
# イメージをビルド
docker build -t law-kb-module .

# コンテナを起動
docker run -p 8083:8083 --env-file .env law-kb-module
```

## 8. 次のステップ

- [ ] PostgreSQL データベースの設定
- [ ] Redis キャッシュの設定
- [ ] e-Gov API キーの設定
- [ ] ETL バッチの実行（初回データインポート）

詳細は `README.md` を参照してください。

