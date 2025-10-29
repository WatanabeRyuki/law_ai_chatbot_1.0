"""
論争解析モジュールのメインAPI
FastAPIアプリケーションとエンドポイント定義
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schemas import DisputeAnalysisRequest, ApiResponse, ErrorPayload
from .services.dispute_analysis_service import DisputeAnalysisService
from .utils.error_mapping import AppError, to_http_exception
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Law Chat - Dispute Analysis Module",
    description="論争解析モジュール：対話ログから論点化と対立関係抽出",
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
service = DisputeAnalysisService()


@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "message": "Law Chat Dispute Analysis Module API",
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
        "bert_model": settings.bert_model_name
    }


@app.post("/v1/analyze", response_model=ApiResponse)
async def analyze_dispute(req: DisputeAnalysisRequest):
    """
    論争解析エンドポイント
    
    Args:
        req: 論争解析リクエスト
        
    Returns:
        統一JSONレスポンス形式
    """
    logger.info(f"Received dispute analysis request: {len(req.messages)} messages")
    
    # 入力検証
    if not req.messages:
        raise to_http_exception(
            AppError("INVALID_INPUT", "messages is required")
        )
    
    if len(req.messages) < 2:
        raise to_http_exception(
            AppError("INVALID_INPUT", "At least 2 messages are required for analysis")
        )
    
    try:
        # 論争解析処理実行
        data = await service.analyze_dispute(req)
        
        response = ApiResponse(success=True, data=data, error=None)
        logger.info("Dispute analysis request processed successfully")
        
        return JSONResponse(content=response.model_dump())
        
    except AppError as e:
        logger.error(f"Application error: {e.code} - {e.message}")
        raise to_http_exception(e)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise to_http_exception(
            AppError("UNEXPECTED", "Unexpected error", {"error": str(e)})
        )


@app.get("/v1/models")
async def get_models():
    """使用中のモデル情報を取得"""
    return {
        "gemini_model": settings.gemini_model,
        "bert_model": settings.bert_model_name,
        "max_topics": settings.max_topics,
        "min_confidence_threshold": settings.min_confidence_threshold
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
