"""
条文要約サービス
条文をローカル要約ルールで処理し、Geminiで最終要約を生成
"""
import re
from typing import Dict, Any, Optional, List
from ..clients.gemini_client import GeminiClient
from ..logger import get_logger

logger = get_logger(__name__)


class ArticleSummarizer:
    """
    条文要約サービス
    
    ローカル短縮ルールとGeminiを組み合わせて条文を要約
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def summarize_article(
        self,
        article_text: str,
        article_no: str,
        max_length: int = 200,
        style: str = "plain"
    ) -> Dict[str, Any]:
        """
        条文を要約
        
        Args:
            article_text: 条文テキスト
            article_no: 条番号
            max_length: 最大文字数
            style: 要約スタイル（plain/legal_summary/for_layperson）
            
        Returns:
            要約結果
        """
        logger.info(f"Summarizing article {article_no} with style={style}")
        
        # ステップ1: ローカル短縮処理
        reduced_text = self._apply_local_reduction(article_text, style)
        
        # ステップ2: Geminiで最終要約生成
        gemini_result = await self.gemini_client.generate_summary(
            text=reduced_text,
            context_items=[f"条文番号: {article_no}"],
            max_tokens=min(max_length // 4, 512)  # トークン数に変換
        )
        
        # ステップ3: 結果を整形
        summary = self._format_summary(
            gemini_result,
            article_no,
            style,
            max_length
        )
        
        return summary
    
    def _apply_local_reduction(
        self,
        text: str,
        style: str
    ) -> str:
        """
        ローカル短縮ルールを適用
        
        Args:
            text: 原文
            style: スタイル
            
        Returns:
            短縮されたテキスト
        """
        # 段落を抽出
        paragraphs = self._extract_paragraphs(text)
        
        # 冗長な部分を削除
        cleaned_paragraphs = self._remove_redundancy(paragraphs)
        
        # 結合
        reduced_text = "\n".join(cleaned_paragraphs)
        
        # スタイル別の追加処理
        if style == "for_layperson":
            # 一般人向け：専門用語を説明
            reduced_text = self._explain_terms(reduced_text)
        
        return reduced_text
    
    def _extract_paragraphs(self, text: str) -> List[str]:
        """
        段落を抽出
        
        Args:
            text: テキスト
            
        Returns:
            段落リスト
        """
        # 句点で分割
        paragraphs = re.split(r'[。\n]', text)
        
        # 空行を除去
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _remove_redundancy(self, paragraphs: List[str]) -> List[str]:
        """
        冗長な部分を削除
        
        Args:
            paragraphs: 段落リスト
            
        Returns:
            クリーンアップされた段落リスト
        """
        cleaned = []
        
        for para in paragraphs:
            # 空の段落をスキップ
            if not para or len(para) < 3:
                continue
            
            # 繰り返しの表現を削除
            para = self._remove_repetition(para)
            
            # 短すぎる段落は除外
            if len(para) > 5:
                cleaned.append(para)
        
        return cleaned
    
    def _remove_repetition(self, text: str) -> str:
        """
        繰り返し表現を削除
        
        Args:
            text: テキスト
            
        Returns:
            クリーンアップされたテキスト
        """
        # 簡単な繰り返し削除ロジック
        words = text.split()
        
        # 連続する同じ単語を削除
        result = []
        prev_word = None
        
        for word in words:
            if word != prev_word:
                result.append(word)
                prev_word = word
        
        return ' '.join(result)
    
    def _explain_terms(self, text: str) -> str:
        """
        専門用語を説明（スタブ実装）
        
        Args:
            text: テキスト
            
        Returns:
            説明付きテキスト
        """
        # 本来は専門用語辞書を参照して説明を追加
        # ここでは簡易実装
        return text
    
    def _format_summary(
        self,
        gemini_result: Dict[str, Any],
        article_no: str,
        style: str,
        max_length: int
    ) -> Dict[str, Any]:
        """
        要約結果を整形
        
        Args:
            gemini_result: Gemini結果
            article_no: 条番号
            style: スタイル
            max_length: 最大長
            
        Returns:
            整形済み結果
        """
        summary_text = gemini_result.get("summary", "")
        
        # 長さ制限を適用
        if len(summary_text) > max_length:
            summary_text = summary_text[:max_length] + "..."
        
        return {
            "summary_text": summary_text,
            "original_reference": {
                "law_id": "PLACEHOLDER",
                "article_no": article_no
            },
            "citations": gemini_result.get("citations", []),
            "style": style,
            "word_count": len(summary_text)
        }

