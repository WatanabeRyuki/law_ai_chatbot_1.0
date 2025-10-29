# Law Chat Dialog Module - README

## 概要
Google Gemini APIを利用した法律対話AI機能の実装です。
WP2-1の目的である「プロンプト設計」と「Gemini API連携設計」を実装しています。

## ディレクトリ構成
```
WP2-1　対話理解モジュール/
├── app/
│   ├── main.py                  # FastAPI起動、ルーティング
│   ├── config.py                # 環境変数/設定、タイムアウト値
│   ├── logger.py                # 構造化ロギング
│   ├── schemas.py               # 入出力Pydanticモデル、統一JSON
│   ├── clients/
│   │   └── gemini_client.py     # Gemini呼び出し、リトライ、例外変換
│   ├── prompts/
│   │   └── prompt_builder.py    # system/user/assistantロールの設計と生成
│   ├── services/
│   │   └── chat_service.py     # 会話生成ユースケース層
│   └── utils/
│       └── error_mapping.py     # エラーマッピング/アプリ例外
├── env.example                  # APIキー/設定テンプレート
├── requirements.txt             # 依存ライブラリ
└── README.md                    # このファイル
```

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
```bash
cp env.example .env
# .envファイルを編集してGEMINI_API_KEYを設定
```

### 3. アプリケーション起動
```bash
# 開発モード
uvicorn app.main:app --reload --port 8081

# 本番モード
python app/main.py
```

## API仕様

### エンドポイント
- `GET /` - ヘルスチェック
- `GET /health` - 詳細ヘルスチェック
- `POST /v1/chat` - チャット処理

### リクエスト例
```json
{
  "messages": [
    {"role": "system", "content": "あなたは行政法に詳しいアシスタントです。"},
    {"role": "user", "content": "行政手続法の趣旨を初心者向けに説明して。"}
  ],
  "max_output_tokens": 512,
  "temperature": 0.6
}
```

### レスポンス例（成功時）
```json
{
  "success": true,
  "data": {
    "assistant": {
      "text": "行政手続法の趣旨について説明します...",
      "reasoning": null
    },
    "usage": {
      "prompt_tokens": null,
      "completion_tokens": null,
      "total_tokens": null
    },
    "meta": {
      "model": "gemini-1.5-pro",
      "latency_ms": 842
    }
  },
  "error": null
}
```

### レスポンス例（失敗時）
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "GEMINI_TIMEOUT",
    "message": "Upstream request timed out",
    "details": {"error": "Request timeout"}
  }
}
```

## 設計特徴

### 1. プロンプト設計
- system/user/assistantロール構成
- 拡張性を考慮した設計（会話履歴、外部知識参照対応）
- 基底システムプロンプトで法律専門性を確保

### 2. Gemini API連携
- REST API経由での通信
- タイムアウト処理とエラーハンドリング
- 構造化ログによる監視

### 3. 統一JSONレスポンス
- 成功/失敗の統一フォーマット
- UI接続を考慮した設計
- エラーコードとメッセージの構造化

### 4. セキュリティ
- 環境変数によるAPIキー管理
- 入力検証とサニタイゼーション

## 将来の拡張予定
- 会話履歴の永続化
- 外部法令データベースとの連携
- 感情分析モジュールとの統合
- レスポンスキャッシュ機能
