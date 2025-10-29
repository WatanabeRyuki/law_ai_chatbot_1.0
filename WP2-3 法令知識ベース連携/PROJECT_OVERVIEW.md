# 法令知識ベース連携モジュール - プロジェクト概要

## 実装完了内容

このプロジェクトは、e-Gov API を利用して日本法の条文を取得・パース・インデックス化し、
対話システム（Gemini）や上流モジュールが利用できるように各種APIを提供する法令知識ベース連携モジュールです。

### ✅ 実装済みコンポーネント

#### 1. コア機能
- ✅ FastAPI ベースのRESTful API
- ✅ e-Gov API クライアント（XML 取得 + パース）
- ✅ XML→JSON パーサー
- ✅ Gemini API 連携（要約・論点抽出）
- ✅ Redis キャッシュサービス
- ✅ PostgreSQL データベースモデル（SQLAlchemy）
- ✅ ETL 同期バッチ（フル同期・差分更新）
- ✅ レート制限ミドルウェア
- ✅ エラーハンドリング
- ✅ 構造化ログ

#### 2. API エンドポイント
- ✅ `GET /laws/list` - 法令リスト取得
- ✅ `GET /laws/{law_id}` - 法令詳細取得
- ✅ `GET /laws/{law_id}/articles/{article_no}` - 条文取得
- ✅ `POST /laws/{law_id}/articles/{article_no}/summarize` - 条文要約
- ✅ `POST /laws/extract_topics` - 論点抽出
- ✅ `POST /laws/search` - 法令検索

#### 3. データベーススキーマ
- ✅ `legal_refs` - 法令マスタテーブル
- ✅ `articles` - 条文テーブル
- ✅ `article_embeddings` - 条文埋め込みベクトル
- ✅ `sync_log` - 同期ログテーブル

#### 4. サービス実装
- ✅ `EGOvClient` - e-Gov API クライアント
- ✅ `LegalXMLParser` - XML パーサー
- ✅ `GeminiClient` - Gemini API クライアント
- ✅ `ArticleSummarizer` - 要約サービス
- ✅ `TopicExtractor` - 論点抽出サービス
- ✅ `CacheService` - Redis キャッシュサービス

#### 5. プロンプトテンプレート
- ✅ `summarize_ja.txt` - 要約プロンプト
- ✅ `extract_topics_ja.txt` - 論点抽出プロンプト

#### 6. テスト
- ✅ `test_parser.py` - XML パーサーの単体テスト
- ✅ `test_api.py` - API エンドポイントのテスト
- ✅ pytest 設定

#### 7. ドキュメント
- ✅ `README.md` - プロジェクトドキュメント
- ✅ `openapi.yaml` - OpenAPI 仕様
- ✅ `PROJECT_OVERVIEW.md` - プロジェクト概要（本ファイル）
- ✅ `env.example` - 環境変数サンプル

#### 8. インフラ
- ✅ `Dockerfile` - Docker イメージ定義
- ✅ `.gitignore` - Git 無視ファイル設定
- ✅ `requirements.txt` - Python 依存パッケージ

## プロジェクト構造

```
WP2-3 法令知識ベース連携/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI アプリケーション
│   ├── config.py            # 設定管理
│   ├── logger.py            # ログ設定
│   ├── schemas.py           # Pydantic スキーマ
│   │
│   ├── models/              # データベースモデル
│   │   ├── __init__.py
│   │   └── models.py       # SQLAlchemy モデル
│   │
│   ├── services/            # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── egov_client.py  # e-Gov API クライアント
│   │   ├── xml_parser.py   # XML パーサー
│   │   ├── summarizer.py   # 要約サービス
│   │   ├── topic_extractor.py # 論点抽出サービス
│   │   └── cache_service.py # キャッシュサービス
│   │
│   ├── clients/             # 外部APIクライアント
│   │   ├── __init__.py
│   │   └── gemini_client.py # Gemini API クライアント
│   │
│   ├── api/                 # API ルーター
│   │   ├── __init__.py
│   │   ├── laws.py         # 法令API
│   │   └── middleware.py   # ミドルウェア
│   │
│   ├── scripts/             # バッチスクリプト
│   │   ├── __init__.py
│   │   └── sync_egov.py    # e-Gov 同期バッチ
│   │
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       └── error_mapping.py # エラーマッピング
│
├── prompt_templates/        # プロンプトテンプレート
│   ├── summarize_ja.txt     # 要約プロンプト
│   └── extract_topics_ja.txt # 論点抽出プロンプト
│
├── sample_xml/              # サンプルXML
│   └── law_civil_001.xml   # 民法サンプル
│
├── tests/                   # テスト
│   ├── __init__.py
│   ├── test_parser.py      # パーサーテスト
│   └── test_api.py         # APIテスト
│
├── Dockerfile              # Docker イメージ定義
├── env.example             # 環境変数サンプル
├── openapi.yaml            # OpenAPI 仕様
├── requirements.txt        # 依存パッケージ
├── README.md              # プロジェクトドキュメント
└── .gitignore             # Git 無視ファイル
```

## 使用技術スタック

- **Web Framework**: FastAPI 0.115.0
- **HTTP Client**: httpx 0.27.2
- **Validation**: Pydantic 2.9.2
- **ORM**: SQLAlchemy 2.0.29
- **Cache**: Redis 5.0.5
- **XML Processing**: lxml 5.1.0
- **ML/NLP**: transformers 4.36.0
- **Testing**: pytest 8.0.0
- **Container**: Docker

## セットアップ手順

1. **依存パッケージのインストール**
   ```bash
   cd WP2-3\ 法令知識ベース連携
   pip install -r requirements.txt
   ```

2. **環境変数の設定**
   ```bash
   cp env.example .env
   # .env ファイルを編集してAPIキーを設定
   ```

3. **データベースの初期化**（将来実装）
   ```bash
   alembic upgrade head
   ```

4. **開発サーバーの起動**
   ```bash
   uvicorn app.main:app --reload --port 8083
   ```

5. **テストの実行**
   ```bash
   pytest tests/
   ```

## API 使用例

### 1. 法令リスト取得
```bash
curl http://localhost:8083/laws/list?page=1&per_page=20
```

### 2. 条文要約
```bash
curl -X POST http://localhost:8083/laws/{law_id}/articles/{article_no}/summarize \
  -H "Content-Type: application/json" \
  -d '{"max_length": 200, "style": "plain"}'
```

### 3. 論点抽出
```bash
curl -X POST http://localhost:8083/laws/extract_topics \
  -H "Content-Type: application/json" \
  -d '{"texts": ["条文1", "条文2"], "mode": "topic_extraction", "max_topics": 5}'
```

## ETL バッチ実行

### フル同期（初回インポート）
```bash
python -m app.scripts.sync_egov --mode full
```

### 差分更新
```bash
python -m app.scripts.sync_egov --mode update
```

### Cron 設定（毎日午前2時に実行）
```bash
0 2 * * * cd /path/to/WP2-3 && python -m app.scripts.sync_egov --mode update
```

## 注意事項

⚠️ **重要な注意事項**

1. **API キー**: 実際の API キーはコードに含めず、`.env` ファイルで管理してください
2. **e-Gov API**: 利用規約・レート制限を遵守してください
3. **Gemini API**: コストがかかるため、モックモードも利用できます
4. **データベース**: 初回は Alembic でマイグレーションが必要です（将来実装）
5. **本番環境**: CORS設定、レート制限、エラーハンドリングを適切に設定してください

## 次のステップ（将来実装）

- [ ] Alembic マイグレーションファイルの作成
- [ ] ベクトル埋め込みの実装（pgvector）
- [ ] 全文検索機能の実装（Elasticsearch/PostgreSQL full-text search）
- [ ] Celery バックグラウンドタスクの実装
- [ ] Prometheus メトリクス収集
- [ ] 本番環境でのセキュリティ強化
- [ ] Docker Compose の設定

## サポート

問題や質問がある場合は、プロジェクトメンテナーに連絡してください。

