"""
Google Gemini API クライアント
要約、論点抽出などのAI機能を提供
"""
import json
import httpx
from typing import Dict, Any, Optional, List
from ..config import settings
from ..logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """
    Google Gemini API クライアント
    
    Gemini API を使って要約や論点抽出などの処理を行う
    """
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.max_tokens = settings.gemini_max_tokens
        self.temperature = settings.gemini_temperature
        
        if not self.api_key or self.api_key == "":
            logger.warning("GEMINI_API_KEY is not set. Mock mode will be used.")
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def generate_summary(
        self,
        text: str,
        context_items: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        テキストを要約
        
        Args:
            text: 要約対象テキスト
            context_items: 追加コンテキスト（任意）
            max_tokens: 最大トークン数
            temperature: 生成温度
            
        Returns:
            要約結果（JSON形式）
        """
        if not self.api_key:
            return self._mock_summary(text)
        
        try:
            prompt = self._build_summary_prompt(text, context_items)
            
            response = await self._call_api(
                prompt=prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            
            return self._parse_summary_response(response)
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # フォールバック: モック要約を返す
            return self._mock_summary(text)
    
    async def extract_topics(
        self,
        texts: List[str],
        mode: str = "topic_extraction",
        max_topics: int = 5
    ) -> Dict[str, Any]:
        """
        論点を抽出
        
        Args:
            texts: テキストリスト
            mode: 抽出モード（topic_extraction/issue_mapping）
            max_topics: 最大論点数
            
        Returns:
            論点抽出結果（JSON形式）
        """
        if not self.api_key:
            return self._mock_topics_extraction(texts, max_topics)
        
        try:
            prompt = self._build_topics_prompt(texts, mode, max_topics)
            
            response = await self._call_api(
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=0.3  # 論点抽出は低温度
            )
            
            return self._parse_topics_response(response)
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            # フォールバック: モック抽出を返す
            return self._mock_topics_extraction(texts, max_topics)
    
    async def _call_api(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """
        Gemini API を呼び出し
        
        Args:
            prompt: プロンプト
            max_tokens: 最大トークン数
            temperature: 温度
            
        Returns:
            APIレスポンス
        """
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        response = await self.client.post(
            f"{url}?key={self.api_key}",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def _build_summary_prompt(
        self,
        text: str,
        context_items: Optional[List[str]] = None
    ) -> str:
        """
        要約プロンプトを構築
        
        Args:
            text: 対象テキスト
            context_items: 追加コンテキスト
            
        Returns:
            プロンプト文字列
        """
        # プロンプトテンプレートを読み込み
        prompt_template = self._load_prompt_template("summarize_ja.txt")
        
        # コンテキストを追加
        context_section = ""
        if context_items:
            context_section = "\n\n関連条文:\n" + "\n".join(context_items)
        
        prompt = prompt_template.format(
            text=text,
            context=context_section
        )
        
        return prompt
    
    def _build_topics_prompt(
        self,
        texts: List[str],
        mode: str,
        max_topics: int
    ) -> str:
        """
        論点抽出プロンプトを構築
        
        Args:
            texts: テキストリスト
            mode: 抽出モード
            max_topics: 最大論点数
            
        Returns:
            プロンプト文字列
        """
        # プロンプトテンプレートを読み込み
        prompt_template = self._load_prompt_template("extract_topics_ja.txt")
        
        # テキストを結合
        combined_text = "\n\n---\n\n".join(texts)
        
        prompt = prompt_template.format(
            texts=combined_text,
            mode=mode,
            max_topics=max_topics
        )
        
        return prompt
    
    def _load_prompt_template(self, filename: str) -> str:
        """
        プロンプトテンプレートを読み込み
        
        Args:
            filename: テンプレートファイル名
            
        Returns:
            テンプレート文字列
        """
        from pathlib import Path
        
        template_path = Path("prompt_templates") / filename
        
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        else:
            # デフォルトテンプレート
            return self._get_default_template(filename)
    
    def _get_default_template(self, filename: str) -> str:
        """
        デフォルトプロンプトテンプレートを取得
        
        Args:
            filename: テンプレートファイル名
            
        Returns:
            デフォルトテンプレート文字列
        """
        templates = {
            "summarize_ja.txt": """法令条文の要約をお願いします。

条文:
{text}
{context}

以下の形式でJSON出力してください:
{{"summary": "要約文", "highlights": ["要点1", "要点2"], "citations": []}}""",
            
            "extract_topics_ja.txt": """法令条文から論点を抽出してください。

条文:
{texts}

モード: {mode}
最大論点数: {max_topics}

以下の形式でJSON出力してください:
{{"topics": [{{"id": "1", "title": "論点名", "description": "説明", "source_refs": []}}]}}"""
        }
        
        return templates.get(filename, "")
    
    def _parse_summary_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        要約レスポンスをパース
        
        Args:
            response: APIレスポンス
            
        Returns:
            パース済み結果
        """
        try:
            # Gemini API のレスポンスからテキストを抽出
            text = response['candidates'][0]['content']['parts'][0]['text']
            
            # JSONをパース
            return json.loads(text)
            
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing summary response: {str(e)}")
            return {"summary": "要約の生成に失敗しました。", "highlights": [], "citations": []}
    
    def _parse_topics_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        論点抽出レスポンスをパース
        
        Args:
            response: APIレスポンス
            
        Returns:
            パース済み結果
        """
        try:
            # Gemini API のレスポンスからテキストを抽出
            text = response['candidates'][0]['content']['parts'][0]['text']
            
            # JSONをパース
            return json.loads(text)
            
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing topics response: {str(e)}")
            return {"topics": [], "relations": []}
    
    def _mock_summary(self, text: str) -> Dict[str, Any]:
        """
        モック要約（APIキーがない場合）
        
        Args:
            text: 対象テキスト
            
        Returns:
            モック要約結果
        """
        # 先頭の一部を要約として返す
        summary = text[:200] + "..." if len(text) > 200 else text
        
        return {
            "summary": summary,
            "highlights": [text[:100] + "..."],
            "citations": []
        }
    
    def _mock_topics_extraction(self, texts: List[str], max_topics: int) -> Dict[str, Any]:
        """
        モック論点抽出（APIキーがない場合）
        
        Args:
            texts: テキストリスト
            max_topics: 最大論点数
            
        Returns:
            モック抽出結果
        """
        topics = []
        
        for i in range(min(max_topics, len(texts))):
            topics.append({
                "id": str(i + 1),
                "title": f"論点 {i + 1}",
                "description": texts[i][:100] + "...",
                "source_refs": []
            })
        
        return {"topics": topics, "relations": []}
    
    async def close(self):
        """HTTPクライアントをクローズ"""
        await self.client.aclose()

