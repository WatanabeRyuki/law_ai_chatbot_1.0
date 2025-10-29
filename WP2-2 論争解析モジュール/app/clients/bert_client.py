"""
BERT分類モデルクライアント
Hugging Face Transformersを使用して発言を分類
"""
import torch
from typing import List, Dict, Any, Tuple
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline
)
from ..config import settings
from ..utils.error_mapping import AppError
from ..logger import get_logger

logger = get_logger(__name__)


class BERTClassifier:
    """BERT分類モデルクライアント"""
    
    def __init__(self):
        """BERT分類器を初期化"""
        self.model_name = settings.bert_model_name
        self.max_length = settings.bert_max_length
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing BERT classifier with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")
        
        try:
            # トークナイザーとモデルをロード
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # 分類用のパイプラインを作成（ダミー実装）
            # 実際の実装では、事前学習済みの分類モデルを使用
            self.classifier = self._create_dummy_classifier()
            
            logger.info("BERT classifier initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize BERT classifier: {e}")
            raise AppError(
                "BERT_MODEL_ERROR",
                "Failed to initialize BERT model",
                {"error": str(e), "model": self.model_name}
            )
    
    def _create_dummy_classifier(self):
        """ダミー分類器を作成（実際の実装では事前学習済みモデルを使用）"""
        # 実際の実装では、以下のような分類カテゴリを使用
        categories = [
            "主張", "根拠", "反論", "補足", "質問", "確認", "同意", "不同意"
        ]
        
        class DummyClassifier:
            def __init__(self, categories):
                self.categories = categories
            
            def __call__(self, text: str) -> List[Dict[str, Any]]:
                # ダミー実装：テキストの長さと内容に基づいて分類
                import random
                
                # 簡単なルールベース分類
                if "?" in text or "？" in text:
                    category = "質問"
                elif "反対" in text or "違う" in text or "間違い" in text:
                    category = "反論"
                elif "賛成" in text or "同意" in text or "そうだ" in text:
                    category = "同意"
                elif "なぜ" in text or "理由" in text or "根拠" in text:
                    category = "根拠"
                else:
                    category = random.choice(self.categories)
                
                confidence = random.uniform(0.7, 0.95)
                
                return [{
                    "label": category,
                    "score": confidence
                }]
        
        return DummyClassifier(categories)
    
    async def classify_messages(
        self, 
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        発言リストを分類
        
        Args:
            messages: 発言リスト [{"speaker": "A", "text": "..."}, ...]
            
        Returns:
            分類結果リスト
        """
        logger.info(f"Classifying {len(messages)} messages")
        
        results = []
        
        try:
            for i, message in enumerate(messages):
                text = message["text"]
                speaker = message["speaker"]
                
                # BERT分類実行
                classification_result = self.classifier(text)
                
                # 結果を整形
                result = {
                    "index": i,
                    "speaker": speaker,
                    "text": text,
                    "classification": {
                        "category": classification_result[0]["label"],
                        "confidence": classification_result[0]["score"],
                        "subcategory": self._get_subcategory(
                            classification_result[0]["label"], 
                            text
                        )
                    }
                }
                
                results.append(result)
                
                logger.debug(f"Classified message {i}: {result['classification']['category']}")
            
            logger.info(f"Successfully classified {len(results)} messages")
            return results
            
        except Exception as e:
            logger.error(f"BERT classification failed: {e}")
            raise AppError(
                "BERT_INFERENCE_ERROR",
                "Failed to classify messages",
                {"error": str(e)}
            )
    
    def _get_subcategory(self, category: str, text: str) -> str:
        """サブカテゴリを決定"""
        subcategories = {
            "主張": ["積極的主張", "消極的主張", "条件付き主張"],
            "根拠": ["データ根拠", "経験根拠", "論理根拠"],
            "反論": ["直接反論", "間接反論", "条件反論"],
            "補足": ["説明補足", "例示補足", "定義補足"],
            "質問": ["確認質問", "探求質問", "反駁質問"],
            "同意": ["完全同意", "部分同意", "条件付き同意"],
            "不同意": ["完全不同意", "部分不同意", "条件付き不同意"]
        }
        
        if category in subcategories:
            # 簡単なルールベースでサブカテゴリを決定
            if "完全" in text or "絶対" in text:
                return subcategories[category][0]
            elif "部分的" in text or "一部" in text:
                return subcategories[category][1]
            elif "条件" in text or "もし" in text:
                return subcategories[category][2] if len(subcategories[category]) > 2 else subcategories[category][0]
            else:
                return subcategories[category][0]
        
        return None
    
    def extract_topics_from_messages(
        self, 
        messages: List[Dict[str, str]]
    ) -> List[str]:
        """
        発言から論点キーワードを抽出
        
        Args:
            messages: 発言リスト
            
        Returns:
            論点キーワードリスト
        """
        logger.info("Extracting topic keywords from messages")
        
        # 簡単なキーワード抽出（実際の実装ではNERやキーワード抽出モデルを使用）
        keywords = set()
        
        for message in messages:
            text = message["text"]
            
            # 基本的なキーワード抽出
            words = text.split()
            for word in words:
                # 2文字以上の名詞を抽出（簡易実装）
                if len(word) >= 2 and word.isalpha():
                    keywords.add(word)
        
        # 上位10個のキーワードを返す
        result = list(keywords)[:10]
        logger.info(f"Extracted {len(result)} topic keywords")
        
        return result
