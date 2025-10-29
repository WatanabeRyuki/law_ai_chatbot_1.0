"""
FastAPI main application for Law Chat Dialog Module
API エンドポイントとルーティング設定
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ChatRequest, ApiResponse, ErrorPayload
from .services.chat_service import ChatService
from .utils.error_mapping import AppError, to_http_exception
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Law Chat - Dialog Module",
    description="Google Gemini APIを利用した法律対話AI機能",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# サービス初期化
service = ChatService()


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "message": "Law Chat Dialog Module API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """詳細ヘルスチェック"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "model": settings.gemini_model
    }


@app.post("/v1/chat", response_model=ApiResponse)
async def chat(req: ChatRequest):
    """
    チャットエンドポイント
    
    Args:
        req: チャットリクエスト
        
    Returns:
        統一JSONレスポンス形式
    """
    logger.info(f"Received chat request: {len(req.messages)} messages")
    
    # 入力検証
    if not req.messages:
        raise to_http_exception(
            AppError("INVALID_INPUT", "messages is required")
        )
    
    # 最後のメッセージがuserであることを推奨（警告のみ）
    if req.messages[-1].role != "user":
        logger.warning("Last message is not from user role")
    
    try:
        # チャット処理実行
        data = await service.chat(req)
        
        response = ApiResponse(success=True, data=data, error=None)
        logger.info("Chat request processed successfully")
        
        return JSONResponse(content=response.model_dump())
        
    except AppError as e:
        logger.error(f"Application error: {e.code} - {e.message}")
        raise to_http_exception(e)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise to_http_exception(
            AppError("UNEXPECTED", "Unexpected error", {"error": str(e)})
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
