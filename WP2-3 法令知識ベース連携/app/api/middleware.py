"""
API ミドルウェア
レート制限、エラーハンドリングなど
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
import time

from ..logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    レート制限ミドルウェア
    
    API の呼び出し頻度を制限
    """
    
    def __init__(self, app, rate_limit: int = 60):
        """
        Args:
            app: FastAPI アプリケーション
            rate_limit: 1分あたりのリクエスト数
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        """
        リクエストを処理
        
        Args:
            request: HTTP リクエスト
            call_next: 次のミドルウェア/エンドポイント
            
        Returns:
            HTTP レスポンス
        """
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # レート制限チェック
        if self._is_rate_limited(client_ip, current_time):
            from fastapi import HTTPException
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="レート制限を超えました。しばらく待ってから再度お試しください。"
            )
        
        # リクエストを記録
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip].append(current_time)
        
        # 1分以上前のリクエストを削除
        cutoff_time = current_time - 60
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > cutoff_time
        ]
        
        # 次のミドルウェア/エンドポイントを実行
        response = await call_next(request)
        
        return response
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """
        レート制限に達しているかチェック
        
        Args:
            client_ip: クライアントIP
            current_time: 現在時刻
            
        Returns:
            レート制限に達している場合 True
        """
        if client_ip not in self.requests:
            return False
        
        cutoff_time = current_time - 60
        recent_requests = [
            t for t in self.requests[client_ip] if t > cutoff_time
        ]
        
        return len(recent_requests) >= self.rate_limit


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    エラーハンドリングミドルウェア
    
    例外をキャッチして適切なエラーレスポンスを返す
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        リクエストを処理
        
        Args:
            request: HTTP リクエスト
            call_next: 次のミドルウェア/エンドポイント
            
        Returns:
            HTTP レスポンス
        """
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            from fastapi import HTTPException
            from fastapi.responses import JSONResponse
            
            # 既にHTTPExceptionの場合はそのまま返す
            if isinstance(e, HTTPException):
                raise
            
            # その他の例外は500エラーとして返す
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "内部サーバーエラーが発生しました",
                    "error": str(e) if logger.level <= 10 else "Internal error"
                }
            )

