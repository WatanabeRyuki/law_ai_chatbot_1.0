"""
論争解析モジュールのエラーハンドリング
WP2-1の設計を継承
"""
from typing import Optional, Dict, Any


class AppError(Exception):
    """アプリケーションエラーベースクラス"""
    
    def __init__(
        self, 
        code: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


def to_http_exception(error: AppError):
    """AppErrorをHTTPExceptionに変換"""
    from fastapi import HTTPException
    
    # エラーコードに基づくHTTPステータスコードマッピング
    status_code_map = {
        "INVALID_INPUT": 400,
        "MISSING_API_KEY": 500,
        "GEMINI_TIMEOUT": 504,
        "GEMINI_REQUEST_ERROR": 502,
        "GEMINI_BAD_RESPONSE": 502,
        "GEMINI_PARSE_ERROR": 502,
        "BERT_MODEL_ERROR": 500,
        "BERT_INFERENCE_ERROR": 500,
        "ANALYSIS_TIMEOUT": 504,
        "UNEXPECTED": 500,
    }
    
    status_code = status_code_map.get(error.code, 500)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "code": error.code,
            "message": error.message,
            "details": error.details
        }
    )
