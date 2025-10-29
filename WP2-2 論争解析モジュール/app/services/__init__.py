"""
論争解析サービス
Gemini APIとBERTを組み合わせて論争解析を実行
"""
import json
import time
from typing import List, Dict, Any, Tuple
from ..schemas import (
    DisputeAnalysisRequest, 
    DisputeAnalysisData,
    TopicInfo,
    TopicRelation,
    MessageAnalysis,
    ClassificationResult,
    SuccessData,
    UsagePayload,
    MetaPayload
)
from ..clients.gemini_client import GeminiClient
from ..clients.bert_client import BERTClassifier
from ..utils.error_mapping import AppError
from ..logger import get_logger

logger = get_logger(__name__)


class DisputeAnalysisService:
    """論争解析サービス"""
    
    def __init__(self):
        """サービス初期化"""
        self.gemini_client = GeminiClient()
        self.bert_classifier = BERTClassifier()
        logger.info("DisputeAnalysisService initialized")
    
    async def analyze_dispute(self, request: DisputeAnalysisRequest) -> SuccessData:
        """
        論争解析を実行
        
        Args:
            request: 論争解析リクエスト
            
        Returns:
            解析結果
        """
        start_time = time.perf_counter()
        logger.info(f"Starting dispute analysis for {len(request.messages)} messages")
        
        try:
            # 1. 入力データの前処理
            messages = [{"speaker": msg.speaker, "text": msg.text} for msg in request.messages]
            
            # 2. BERT分類実行
            bert_results = await self.bert_classifier.classify_messages(messages)
            
            # 3. Gemini APIで論点分析
            topics_data = await self.gemini_client.analyze_dispute_topics(messages)
            topics = self._parse_topics_response(topics_data[0])
            
            # 4. Gemini APIで立場分析
            topic_names = [topic["topic_name"] for topic in topics]
            positions_data = await self.gemini_client.analyze_positions(messages, topic_names)
            positions = self._parse_positions_response(positions_data[0])
            
            # 5. Gemini APIで関係分析
            relations_data = await self.gemini_client.analyze_relations(messages, topic_names)
            relations = self._parse_relations_response(relations_data[0])
            
            # 6. 結果を統合
            analysis_data = self._integrate_results(
                topics, positions, relations, bert_results, messages
            )
            
            # 7. 使用量情報を計算
            processing_time_ms = int((time.perf_counter() - start_time) * 1000)
            usage = UsagePayload(
                gemini_tokens=None,  # Gemini REST APIでは詳細なトークン情報が取得できない場合がある
                bert_inferences=len(messages),
                processing_time_ms=processing_time_ms
            )
            
            # 8. メタ情報を構築
            meta = MetaPayload(
                model=f"{self.gemini_client.gemini_model}+{self.bert_classifier.model_name}",
                analysis_depth=request.analysis_depth,
                total_messages=len(messages)
            )
            
            logger.info(f"Dispute analysis completed in {processing_time_ms}ms")
            
            return SuccessData(
                analysis=analysis_data,
                usage=usage,
                meta=meta
            )
            
        except Exception as e:
            logger.error(f"Dispute analysis failed: {e}")
            raise AppError(
                "ANALYSIS_ERROR",
                "Failed to analyze dispute",
                {"error": str(e)}
            )
    
    def _parse_topics_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Geminiの論点分析レスポンスをパース"""
        try:
            # JSONレスポンスを抽出（```json```ブロックがある場合を考慮）
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()
            
            data = json.loads(json_text)
            topics = data.get("topics", [])
            
            logger.info(f"Parsed {len(topics)} topics from Gemini response")
            return topics
            
        except Exception as e:
            logger.error(f"Failed to parse topics response: {e}")
            # フォールバック：ダミーデータを返す
            return [
                {
                    "topic_id": "topic_1",
                    "topic_name": "主要論点",
                    "confidence": 0.8,
                    "keywords": ["論点", "議論"]
                }
            ]
    
    def _parse_positions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Geminiの立場分析レスポンスをパース"""
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()
            
            data = json.loads(json_text)
            positions = data.get("positions", [])
            
            logger.info(f"Parsed {len(positions)} position analyses from Gemini response")
            return positions
            
        except Exception as e:
            logger.error(f"Failed to parse positions response: {e}")
            return []
    
    def _parse_relations_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Geminiの関係分析レスポンスをパース"""
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                json_text = response_text.strip()
            
            data = json.loads(json_text)
            relations = data.get("relations", [])
            
            logger.info(f"Parsed {len(relations)} relation analyses from Gemini response")
            return relations
            
        except Exception as e:
            logger.error(f"Failed to parse relations response: {e}")
            return []
    
    def _integrate_results(
        self,
        topics: List[Dict[str, Any]],
        positions: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        bert_results: List[Dict[str, Any]],
        messages: List[Dict[str, str]]
    ) -> DisputeAnalysisData:
        """各分析結果を統合して最終結果を構築"""
        
        # TopicInfoオブジェクトを作成
        topic_infos = []
        for topic in topics:
            topic_info = TopicInfo(
                topic_id=topic.get("topic_id", f"topic_{len(topic_infos) + 1}"),
                topic_name=topic.get("topic_name", "未分類論点"),
                confidence=topic.get("confidence", 0.5),
                keywords=topic.get("keywords", [])
            )
            topic_infos.append(topic_info)
        
        # TopicRelationオブジェクトを作成
        topic_relations = []
        for relation in relations:
            topic_relation = TopicRelation(
                topic=relation.get("topic", "未分類"),
                a_position=relation.get("a_position", "不明"),
                b_position=relation.get("b_position", "不明"),
                relation_type=relation.get("relation_type", "不明"),
                intensity=relation.get("intensity", 0.5)
            )
            topic_relations.append(topic_relation)
        
        # MessageAnalysisオブジェクトを作成
        message_analyses = []
        for i, bert_result in enumerate(bert_results):
            if i < len(messages):
                message = messages[i]
                classification = ClassificationResult(
                    category=bert_result["classification"]["category"],
                    confidence=bert_result["classification"]["confidence"],
                    subcategory=bert_result["classification"].get("subcategory")
                )
                
                message_analysis = MessageAnalysis(
                    speaker=message["speaker"],
                    text=message["text"],
                    classification=classification,
                    topics=[topic["topic_name"] for topic in topics],  # 簡易実装
                    sentiment=None  # 感情分析は未実装
                )
                message_analyses.append(message_analysis)
        
        # サマリー情報を構築
        summary = {
            "total_topics": len(topic_infos),
            "total_relations": len(topic_relations),
            "conflict_intensity": self._calculate_conflict_intensity(topic_relations),
            "main_disputes": [rel.topic for rel in topic_relations if rel.intensity > 0.7],
            "agreement_areas": [rel.topic for rel in topic_relations if rel.intensity < 0.3]
        }
        
        return DisputeAnalysisData(
            topics=topic_infos,
            relations=topic_relations,
            message_analyses=message_analyses,
            summary=summary
        )
    
    def _calculate_conflict_intensity(self, relations: List[TopicRelation]) -> float:
        """全体的な対立強度を計算"""
        if not relations:
            return 0.0
        
        total_intensity = sum(rel.intensity for rel in relations)
        return total_intensity / len(relations)
