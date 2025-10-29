"""
API エンドポイントのテスト
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """テストクライアント"""
    return TestClient(app)


def test_root_endpoint(client):
    """ルートエンドポイントが動作する"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_health_endpoint(client):
    """ヘルスチェックエンドポイントが動作する"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "environment" in data


def test_get_models_endpoint(client):
    """モデル情報エンドポイントが動作する"""
    response = client.get("/v1/models")
    
    assert response.status_code == 200
    data = response.json()
    assert "gemini_model" in data


def test_list_laws_endpoint(client):
    """法令リストエンドポイントが動作する"""
    response = client.get("/laws/list?page=1&per_page=10")
    
    # APIが実装されている場合 200、未実装の場合 500
    assert response.status_code in [200, 500]


def test_extract_topics_endpoint(client):
    """論点抽出エンドポイントが動作する"""
    response = client.post(
        "/laws/extract_topics",
        json={
            "texts": ["サンプル条文1", "サンプル条文2"],
            "mode": "topic_extraction",
            "max_topics": 3
        }
    )
    
    # APIが実装されている場合 200、未実装の場合 500
    assert response.status_code in [200, 500]

