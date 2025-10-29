# WP2-2 論争解析モジュール

## 概要
対話ログ（双方の発言）を解析して「論点化」および「対立関係の抽出」を行うモジュールです。
Gemini APIとBERT（自然言語分類モデル）を組み合わせて、発言間の立場・主張・論点を自動抽出します。

## ディレクトリ構成

```
WP2-2　論争解析モジュール/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPIメインアプリケーション
│   ├── config.py                   # 設定管理
│   ├── logger.py                   # ログ設定
│   ├── schemas.py                  # データモデル定義
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── gemini_client.py        # Gemini APIクライアント
│   │   └── bert_client.py          # BERT分類クライアント
│   ├── services/
│   │   ├── __init__.py
│   │   └── dispute_analysis_service.py  # 論争解析サービス
│   └── utils/
│       ├── __init__.py
│       └── error_mapping.py        # エラーハンドリング
├── requirements.txt                 # 依存関係
├── env.example                     # 環境変数設定例
├── 処理フロー図.md                 # GeminiとBERTの役割分担
└── 入出力例.md                     # API使用例とサンプルJSON
```

## 主要機能

### 1. 論点抽出
- Gemini APIを使用して対話から主要な論点を自然言語理解で抽出
- 各論点の信頼度とキーワードを付与

### 2. 立場分析
- 各発言者の論点に対する立場を分析
- 根拠となる発言を特定

### 3. 関係分析
- 論点間の対立・合意関係を分析
- 対立強度を数値化

### 4. 発言分類
- BERTを使用して各発言を「主張/根拠/反論/補足」等に分類
- 信頼度スコアとサブカテゴリを付与

## 技術仕様

### 使用技術
- **FastAPI**: REST APIフレームワーク
- **Gemini API**: 自然言語理解・生成
- **BERT (Hugging Face)**: 自然言語分類
- **Pydantic**: データバリデーション
- **httpx**: HTTPクライアント

### APIエンドポイント
- `POST /v1/analyze`: 論争解析実行
- `GET /health`: ヘルスチェック
- `GET /v1/models`: モデル情報取得

### 入力形式
```json
{
  "messages": [
    {"speaker": "A", "text": "発言内容"},
    {"speaker": "B", "text": "発言内容"}
  ],
  "analysis_depth": "standard"
}
```

### 出力形式
```json
{
  "success": true,
  "data": {
    "analysis": {
      "topics": [...],      // 論点リスト
      "relations": [...],  // 対立関係データ
      "message_analyses": [...], // 発言分析結果
      "summary": {...}      // 解析サマリー
    },
    "usage": {...},        // 使用量情報
    "meta": {...}          // メタ情報
  }
}
```

## セットアップ

### 1. 依存関係インストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数設定
```bash
cp env.example .env
# .envファイルを編集してAPIキー等を設定
```

### 3. アプリケーション起動
```bash
python -m app.main
# または
uvicorn app.main:app --host 0.0.0.0 --port 8082
```

## 設定項目

| 環境変数 | 説明 | デフォルト値 |
|---------|------|-------------|
| `GEMINI_API_KEY` | Gemini APIキー | - |
| `GEMINI_MODEL` | Geminiモデル名 | `gemini-1.5-flash` |
| `BERT_MODEL_NAME` | BERTモデル名 | `cl-tohoku/bert-base-japanese-v3` |
| `MAX_TOPICS` | 最大論点数 | `10` |
| `MIN_CONFIDENCE_THRESHOLD` | 最小信頼度閾値 | `0.7` |
| `REQUEST_TIMEOUT_SEC` | リクエストタイムアウト | `30` |

## エラーハンドリング

### エラーコード
- `INVALID_INPUT`: 入力データが無効
- `MISSING_API_KEY`: APIキーが設定されていない
- `GEMINI_TIMEOUT`: Gemini APIタイムアウト
- `GEMINI_REQUEST_ERROR`: Gemini API通信エラー
- `BERT_MODEL_ERROR`: BERTモデル初期化エラー
- `BERT_INFERENCE_ERROR`: BERT推論エラー
- `ANALYSIS_TIMEOUT`: 解析処理タイムアウト

## 注意事項

1. **APIキー管理**: 実際のAPIキーは環境変数で管理し、コードに含めない
2. **トークン制限**: Gemini APIのトークン数制限を考慮
3. **モデルサイズ**: BERTモデルのダウンロードとメモリ使用量に注意
4. **並列処理**: Gemini APIの複数呼び出しは並列実行で効率化
5. **エラー復旧**: API失敗時はフォールバック処理を実装

## 今後の拡張予定

- 感情分析機能の追加
- より詳細な論点階層化
- リアルタイム解析機能
- 多言語対応
- カスタム分類モデルの学習機能
