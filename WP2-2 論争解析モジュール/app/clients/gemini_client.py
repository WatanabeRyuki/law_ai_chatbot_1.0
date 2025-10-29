"""
Gemini API client for Dispute Analysis Module
WP2-1の設計を継承し、論争解析用のプロンプト生成機能を追加
"""
import time
from typing import Any, Dict, Tuple, List
import httpx
from ..config import settings
from ..utils.error_mapping import AppError
from ..logger import get_logger

logger = get_logger(__name__)

# Gemini API URL
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiClient:
    """論争解析用Gemini API クライアント"""
    
    def __init__(self):
        """クライアント初期化"""
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            raise AppError("MISSING_API_KEY", "GEMINI_API_KEY is not set")
        
        logger.info(f"GeminiClient initialized with model: {settings.gemini_model}")
    
    async def analyze_dispute_topics(
        self, 
        messages: List[Dict[str, str]]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        論争の論点を分析
        
        Args:
            messages: 発言ログ [{"speaker": "A", "text": "..."}, ...]
            
        Returns:
            (分析結果JSON, 使用量情報)
        """
        prompt = self._build_topic_analysis_prompt(messages)
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        
        return await self.generate(contents, max_tokens=2048, temperature=0.3)
    
    async def analyze_positions(
        self, 
        messages: List[Dict[str, str]], 
        topics: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        各論点での立場を分析
        
        Args:
            messages: 発言ログ
            topics: 論点リスト
            
        Returns:
            (分析結果JSON, 使用量情報)
        """
        prompt = self._build_position_analysis_prompt(messages, topics)
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        
        return await self.generate(contents, max_tokens=2048, temperature=0.3)
    
    async def analyze_relations(
        self, 
        messages: List[Dict[str, str]], 
        topics: List[str]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        論点間の関係を分析
        
        Args:
            messages: 発言ログ
            topics: 論点リスト
            
        Returns:
            (分析結果JSON, 使用量情報)
        """
        prompt = self._build_relation_analysis_prompt(messages, topics)
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        
        return await self.generate(contents, max_tokens=2048, temperature=0.3)
    
    def _build_topic_analysis_prompt(self, messages: List[Dict[str, str]]) -> str:
        """論点分析用プロンプトを構築"""
        messages_text = "\n".join([
            f"{msg['speaker']}: {msg['text']}" for msg in messages
        ])
        
        return f"""
以下の対話ログを分析して、主要な論点を抽出してください。

対話ログ:
{messages_text}

以下のJSON形式で回答してください：
{{
  "topics": [
    {{
      "topic_id": "topic_1",
      "topic_name": "論点名",
      "confidence": 0.95,
      "keywords": ["キーワード1", "キーワード2"]
    }}
  ]
}}

要件：
- 論点は最大{settings.max_topics}個まで
- 各論点の信頼度は0.0-1.0で評価
- キーワードは3-5個程度
- 論点名は簡潔で具体的に
"""
    
    def _build_position_analysis_prompt(
        self, 
        messages: List[Dict[str, str]], 
        topics: List[str]
    ) -> str:
        """立場分析用プロンプトを構築"""
        messages_text = "\n".join([
            f"{msg['speaker']}: {msg['text']}" for msg in messages
        ])
        topics_text = "\n".join([f"- {topic}" for topic in topics])
        
        return f"""
以下の対話ログと論点について、各発言者の立場を分析してください。

対話ログ:
{messages_text}

論点:
{topics_text}

以下のJSON形式で回答してください：
{{
  "positions": [
    {{
      "topic": "論点名",
      "a_position": "Aの立場（賛成/反対/中立/懸念等）",
      "b_position": "Bの立場（賛成/反対/中立/懸念等）",
      "a_confidence": 0.9,
      "b_confidence": 0.8,
      "supporting_evidence": ["根拠となる発言1", "根拠となる発言2"]
    }}
  ]
}}

要件：
- 立場は簡潔に表現
- 信頼度は0.0-1.0で評価
- 根拠は具体的な発言を引用
"""
    
    def _build_relation_analysis_prompt(
        self, 
        messages: List[Dict[str, str]], 
        topics: List[str]
    ) -> str:
        """関係分析用プロンプトを構築"""
        messages_text = "\n".join([
            f"{msg['speaker']}: {msg['text']}" for msg in messages
        ])
        topics_text = "\n".join([f"- {topic}" for topic in topics])
        
        return f"""
以下の対話ログと論点について、論点間の関係と対立強度を分析してください。

対話ログ:
{messages_text}

論点:
{topics_text}

以下のJSON形式で回答してください：
{{
  "relations": [
    {{
      "topic": "論点名",
      "a_position": "Aの立場",
      "b_position": "Bの立場",
      "relation_type": "対立/合意/補足/中立",
      "intensity": 0.8
    }}
  ]
}}

要件：
- 対立強度は0.0-1.0で評価（1.0が最大対立）
- 関係タイプは適切に分類
- 各論点について分析
"""
    
    async def generate(
        self, 
        contents: list[dict], 
        max_tokens: int | None, 
        temperature: float | None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Gemini APIを呼び出してテキスト生成
        WP2-1の実装を継承
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
                if candidate.get("finishReason") == "MAX_TOKENS":
                    logger.warning("Response truncated due to max tokens")
                
                content = candidate.get("content", {})
                if "parts" in content and content["parts"]:
                    text = content["parts"][0].get("text", "")
                else:
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
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "latency_ms": latency_ms,
            "raw": None
        }
        
        logger.info(f"Generated text length: {len(text)} chars")
        return text, usage_like
