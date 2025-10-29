"""
エラーマッピングユーティリティ
アプリケーションエラーをHTTP例外に変換
"""
from fastapi import HTTPException


class AppError(Exception):
    """アプリケーションエラー"""
    
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        return f"{self.code}: {self.message}"


def to_http_exception(error: AppError) -> HTTPException:
    """
    AppError を HTTPException に変換
    
    Args:
        error: AppError インスタンス
        
    Returns:
        HTTPException
    """
    # エラーコードに基づいてHTTPステータスコードを決定
    status_codes = {
        "NOT_FOUND": 404,
        "INVALID_INPUT": 400,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
        "UNEXPECTED": 500
    }
    
    status_code = status_codes.get(error.code, 500)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": error.code,
            "message": error.message,
            "details": error.details
        }
    )

