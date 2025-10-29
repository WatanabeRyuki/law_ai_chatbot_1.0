"""
Error mapping and custom exceptions for Law Chat Dialog Module
アプリケーション例外とHTTP例外へのマッピング
"""
from fastapi import HTTPException, status


class AppError(Exception):
    """アプリケーション独自例外"""
    
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def to_http_exception(err: AppError) -> HTTPException:
    """
    AppErrorをHTTPExceptionに変換
    
    Args:
        err: AppErrorインスタンス
        
    Returns:
        HTTPExceptionインスタンス
    """
    status_code = status.HTTP_502_BAD_GATEWAY  # デフォルト
    
    if err.code in {"INVALID_INPUT", "VALIDATION_ERROR"}:
        status_code = status.HTTP_400_BAD_REQUEST
    elif err.code in {"GEMINI_TIMEOUT", "REQUEST_TIMEOUT"}:
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
    elif err.code in {"MISSING_API_KEY", "AUTHENTICATION_ERROR"}:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif err.code in {"RATE_LIMIT_EXCEEDED"}:
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    
    return HTTPException(
        status_code=status_code,
        detail={
            "code": err.code,
            "message": err.message,
            "details": err.details
        }
    )
