"""
法令知識ベース連携モジュールのメインAPI
FastAPIアプリケーションとエンドポイント定義
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .logger import get_logger
from .schemas import (
    LawListResponse, LawListItem, LawInfo, ArticleInfo,
    SummarizeArticleRequest, SummaryResponse,
    ExtractTopicsRequest, TopicsResponse,
    ApiResponse
)
from .api import laws
from .api.middleware import RateLimitMiddleware, ErrorHandlerMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の初期化処理
    logger.info("Starting Law Knowledge Base Module...")
    logger.info(f"Environment: {settings.environment}")
    
    yield
    
    # 終了時のクリーンアップ処理
    logger.info("Shutting down Law Knowledge Base Module...")


# FastAPIアプリケーション初期化
app = FastAPI(
    title="Law Chat - Legal Knowledge Base Module",
    description="法令知識ベース連携モジュール：e-Gov API連携、条文取得・要約・論点抽出",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# エラーハンドリングミドルウェア
app.add_middleware(ErrorHandlerMiddleware)

# レート制限ミドルウェア
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=settings.rate_limit_per_minute
)

# ルーター登録
app.include_router(laws.router, prefix="/laws", tags=["laws"])


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "message": "Law Chat Legal Knowledge Base Module API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """詳細ヘルスチェック"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "gemini_model": settings.gemini_model,
        "database_url": settings.database_url.split('@')[-1] if '@' in settings.database_url else "not configured"
    }


@app.get("/v1/models")
async def get_models():
    """使用中のモデル情報を取得"""
    return {
        "gemini_model": settings.gemini_model,
        "bert_model": settings.bert_model_name,
        "cache_ttl": settings.cache_ttl
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)

