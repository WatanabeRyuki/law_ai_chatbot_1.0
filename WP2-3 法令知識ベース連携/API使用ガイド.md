# API 使用ガイド

法令知識ベース連携モジュールのAPI使用方法を初心者向けに説明します。

## 目次
1. [基本的な使い方](#1-基本的な使い方)
2. [API 呼び出し例](#2-api-呼び出し例)
3. [エラーハンドリング](#3-エラーハンドリング)
4. [よくある使い方](#4-よくある使い方)

---

## 1. 基本的な使い方

### 1.1 サーバーが起動しているか確認

まず、サーバーが動作しているか確認します。

```bash
# ヘルスチェック
curl http://localhost:8083/health
```

**期待されるレスポンス**:
```json
{
  "status": "healthy",
  "environment": "dev",
  "gemini_model": "gemini-1.5-flash"
}
```

### 1.2 API ドキュメントの確認

ブラウザで以下にアクセスすると、インタラクティブなAPI ドキュメントが表示されます。

```
http://localhost:8083/docs
```

---

## 2. API 呼び出し例

### 2.1 法令リストを取得する

**リクエスト**:
```bash
curl "http://localhost:8083/laws/list?page=1&per_page=10"
```

**レスポンス**:
```json
{
  "laws": [
    {
      "law_id": "CIVIL_LAW_001",
      "title": "民法",
      "law_no": "明治29年法律第89号",
      "enact_date": "1896-04-27T00:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 10
}
```

### 2.2 条文を要約する

**リクエスト**:
```bash
curl -X POST \
  "http://localhost:8083/laws/CIVIL_LAW_001/articles/第1条/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "max_length": 200,
    "style": "plain"
  }'
```

**レスポンス**:
```json
{
  "summary_text": "私権は公共の福祉に適合する必要がある。",
  "original_reference": {
    "law_id": "CIVIL_LAW_001",
    "article_no": "第1条"
  },
  "citations": [],
  "style": "plain",
  "word_count": 25
}
```

### 2.3 論点を抽出する

**リクエスト**:
```bash
curl -X POST \
  "http://localhost:8083/laws/extract_topics" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "私権は、公共の福祉に適合しなければならない。",
      "この法律は、個人の尊厳と両性の本質的平等を明記して、解釈しなければならない。"
    ],
    "mode": "topic_extraction",
    "max_topics": 5
  }'
```

**レスポンス**:
```json
{
  "topics": [
    {
      "id": "1",
      "title": "私権と公共の福祉",
      "description": "私権の行使は公共の福祉に適合する必要がある",
      "source_refs": ["民法第1条"]
    },
    {
      "id": "2",
      "title": "個人の尊厳と平等",
      "description": "個人の尊厳と両性の本質的平等を明記",
      "source_refs": ["民法第2条"]
    }
  ],
  "relations": [
    {
      "topic_id_1": "1",
      "topic_id_2": "2",
      "relation_type": "補足"
    }
  ]
}
```

---

## 3. エラーハンドリング

### 3.1 HTTP ステータスコード

| コード | 意味 | 対応方法 |
|-------|-----|---------|
| 200 | 成功 | - |
| 404 | リソースが見つからない | 指定した法令ID・条番号を確認 |
| 429 | レート制限超過 | 1分待ってからリトライ |
| 500 | サーバーエラー | 管理者に連絡 |

### 3.2 Python でのエラーハンドリング

```python
import httpx

async def call_law_api():
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8083/laws/CIVIL_001/articles/第1条/summarize",
                json={"max_length": 200, "style": "plain"}
            )
            
            # ステータスコードをチェック
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print("条文が見つかりません")
                return None
            elif response.status_code == 429:
                print("レート制限です。しばらく待ってから再試行してください")
                return None
            else:
                print(f"エラー: {response.status_code}")
                return None
                
    except httpx.TimeoutException:
        print("タイムアウト: サーバーへの接続に失敗しました")
        return None
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return None
```

---

## 4. よくある使い方

### 4.1 Python で法令を検索する

```python
import httpx
import asyncio

async def search_laws(keyword):
    """キーワードで法令を検索"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8083/laws/search",
            params={"keyword": keyword, "page": 1, "per_page": 10}
        )
        return response.json()

# 使用例
result = asyncio.run(search_laws("民法"))
print(result)
```

### 4.2 複数の条文を並列取得する

```python
async def get_multiple_articles(law_id, article_nos):
    """複数の条文を並列取得"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [
            client.get(f"http://localhost:8083/laws/{law_id}/articles/{no}")
            for no in article_nos
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses if r.status_code == 200]

# 使用例
articles = asyncio.run(
    get_multiple_articles("CIVIL_LAW_001", ["第1条", "第2条", "第3条"])
)
```

### 4.3 条文を要約してファイルに保存

```python
async def summarize_and_save(law_id, article_no):
    """条文を要約してファイルに保存"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 要約APIを呼び出し
        response = await client.post(
            f"http://localhost:8083/laws/{law_id}/articles/{article_no}/summarize",
            json={"max_length": 200, "style": "for_layperson"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # ファイルに保存
            filename = f"{law_id}_{article_no}_summary.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"法令: {result['original_reference']['law_id']}\n")
                f.write(f"条文: {result['original_reference']['article_no']}\n")
                f.write(f"要約: {result['summary_text']}\n")
            
            print(f"要約を{filename}に保存しました")
            return result
        
        return None

# 使用例
asyncio.run(summarize_and_save("CIVIL_LAW_001", "第1条"))
```

---

## 5. トラブルシューティング

### 5.1 サーバーが起動しない

**原因**: ポートが既に使用されている

**解決方法**:
```bash
# 別のポートを使用
uvicorn app.main:app --reload --port 8084
```

### 5.2 "Module not found" エラー

**原因**: モジュールのインポートパスが間違っている

**解決方法**:
```bash
# PYTHONPATH を設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# またはプロジェクトルートから実行
cd "WP2-3 法令知識ベース連携"
python -m app.main
```

### 5.3 APIがタイムアウトする

**原因**: サーバーが長時間処理している、またはネットワークの問題

**解決方法**:
```python
# タイムアウトを増やす
async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(url, json=data)
```

---

## 6. 参考資料

- **詳細設計書**: `詳細設計書.md`
- **README**: `README.md`
- **クイックスタート**: `QUICK_START.md`
- **OpenAPI 仕様**: `openapi.yaml`

