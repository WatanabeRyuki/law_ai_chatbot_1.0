"""
Gemini API client for Law Chat Dialog Module
Google Gemini APIとの通信、タイムアウト処理、エラーハンドリング
"""
import time
from typing import Any, Dict, Tuple
import httpx
from ..config import settings
from ..utils.error_mapping import AppError
from ..logger import get_logger

logger = get_logger(__name__)

# Gemini API URL
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiClient:
    """Gemini API クライアント"""
    
    def __init__(self):
        """クライアント初期化"""
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            raise AppError("MISSING_API_KEY", "GEMINI_API_KEY is not set")
        
        logger.info(f"GeminiClient initialized with model: {settings.gemini_model}")
    
    async def generate(
        self, 
        contents: list[dict], 
        max_tokens: int | None, 
        temperature: float | None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Gemini APIを呼び出してテキスト生成
        
        Args:
            contents: Gemini API用のcontents形式
            max_tokens: 最大出力トークン数
            temperature: 温度パラメータ
            
        Returns:
            (生成テキスト, 使用量情報)
        """
        url = GEMINI_API_URL.format(model=settings.gemini_model)
        params = {"key": self.api_key}
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens or 1024,
                "temperature": temperature or 0.7,
            },
        }
        
        timeout = httpx.Timeout(
            timeout=settings.request_timeout_sec,
            connect=settings.connect_timeout_sec
        )
        
        start = time.perf_counter()
        
        try:
            logger.debug(f"Sending request to Gemini API: {url}")
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, params=params, json=payload)
                
        except httpx.TimeoutException as e:
            logger.error(f"Gemini API timeout: {e}")
            raise AppError(
                "GEMINI_TIMEOUT", 
                "Upstream request timed out", 
                {"error": str(e)}
            )
        except httpx.RequestError as e:
            logger.error(f"Gemini API request error: {e}")
            raise AppError(
                "GEMINI_REQUEST_ERROR", 
                "Network error to Gemini", 
                {"error": str(e)}
            )
        
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        if resp.status_code >= 400:
            logger.error(f"Gemini API error response: {resp.status_code} - {resp.text}")
            raise AppError(
                "GEMINI_BAD_RESPONSE", 
                "Gemini returned error", 
                {"status": resp.status_code, "body": resp.text}
            )
        
        try:
            data = resp.json()
            logger.debug(f"Gemini API response received in {latency_ms}ms")
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise AppError(
                "GEMINI_PARSE_ERROR", 
                "Failed to parse Gemini response", 
                {"error": str(e)}
            )
        
        # Geminiレスポンスからテキスト抽出
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("No candidates in Gemini response")
                text = ""
            else:
                candidate = candidates[0]
                # finishReasonがMAX_TOKENSの場合、部分的な応答を取得
                if candidate.get("finishReason") == "MAX_TOKENS":
                    logger.warning("Response truncated due to max tokens")
                
                # content構造を確認
                content = candidate.get("content", {})
                if "parts" in content and content["parts"]:
                    text = content["parts"][0].get("text", "")
                else:
                    # partsが無い場合（thinking mode等）
                    text = ""
                    logger.warning("No text parts in response content")
                
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to extract text from Gemini response: {e}")
            raise AppError(
                "GEMINI_PARSE_ERROR", 
                "Failed to extract text from Gemini response", 
                {"raw": data, "error": str(e)}
            )
        
        # 使用量情報を構築
        usage_like = {
            "prompt_tokens": None,  # REST APIではトークン情報が無い場合がある
            "completion_tokens": None,
            "total_tokens": None,
            "latency_ms": latency_ms,
            "raw": None  # 必要に応じて省略/格納
        }
        
        logger.info(f"Generated text length: {len(text)} chars")
        return text, usage_like
