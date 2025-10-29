"""
論点抽出サービス
複数条文から論点と関係を抽出
"""
from typing import Dict, Any, List
from ..clients.gemini_client import GeminiClient
from ..logger import get_logger

logger = get_logger(__name__)


class TopicExtractor:
    """
    論点抽出サービス
    
    Geminiとルールベース処理を組み合わせて論点を抽出
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def extract_topics(
        self,
        texts: List[str],
        mode: str = "topic_extraction",
        max_topics: int = 5
    ) -> Dict[str, Any]:
        """
        複数条文から論点を抽出
        
        Args:
            texts: 条文テキストリスト
            mode: 抽出モード（topic_extraction/issue_mapping）
            max_topics: 最大論点数
            
        Returns:
            論点抽出結果
        """
        logger.info(f"Extracting topics from {len(texts)} texts, mode={mode}")
        
        try:
            # Geminiで論点抽出
            gemini_result = await self.gemini_client.extract_topics(
                texts=texts,
                mode=mode,
                max_topics=max_topics
            )
            
            # 結果を整形
            formatted_result = self._format_topics(gemini_result, mode)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            # フォールバック
            return self._fallback_extraction(texts, max_topics)
    
    def _format_topics(
        self,
        gemini_result: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """
        論点抽出結果を整形
        
        Args:
            gemini_result: Gemini結果
            mode: 抽出モード
            
        Returns:
            整形済み結果
        """
        topics = gemini_result.get("topics", [])
        relations = gemini_result.get("relations", [])
        
        # 論点を整形
        formatted_topics = []
        for topic in topics:
            formatted_topics.append({
                "id": topic.get("id", ""),
                "title": topic.get("title", ""),
                "description": topic.get("description", ""),
                "source_refs": topic.get("source_refs", [])
            })
        
        return {
            "topics": formatted_topics,
            "relations": relations
        }
    
    def _fallback_extraction(
        self,
        texts: List[str],
        max_topics: int
    ) -> Dict[str, Any]:
        """
        フォールバック論点抽出（Gemini失敗時）
        
        Args:
            texts: テキストリスト
            max_topics: 最大論点数
            
        Returns:
            簡易抽出結果
        """
        topics = []
        
        # 簡単なキーワード抽出
        for i, text in enumerate(texts[:max_topics]):
            # 条文から重要な語句を抽出（簡単な実装）
            key_phrases = self._extract_key_phrases(text)
            
            topics.append({
                "id": str(i + 1),
                "title": key_phrases[0] if key_phrases else f"論点 {i + 1}",
                "description": text[:150] + "..." if len(text) > 150 else text,
                "source_refs": []
            })
        
        return {
            "topics": topics,
            "relations": []
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        重要語句を抽出（簡易実装）
        
        Args:
            text: テキスト
            
        Returns:
            重要語句リスト
        """
        # 簡単な実装：長い名詞句を抽出
        import re
        
        # 名詞句パターン
        pattern = r'[^。、]{5,}'
        phrases = re.findall(pattern, text)
        
        # 最初の3つを返す
        return phrases[:3]

