"""
論争解析モジュールのスキーマ定義
入出力データモデルとAPIレスポンス形式
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class SpeakerMessage(BaseModel):
    """発言者メッセージモデル"""
    speaker: Literal["A", "B"] = Field(description="発言者（A or B）")
    text: str = Field(description="発言内容")


class DisputeAnalysisRequest(BaseModel):
    """論争解析リクエストモデル"""
    messages: List[SpeakerMessage] = Field(
        description="双方の発言ログ（JSON形式）"
    )
    analysis_depth: Optional[str] = Field(
        default="standard", 
        description="解析深度（basic/standard/detailed）"
    )


class TopicInfo(BaseModel):
    """論点情報"""
    topic_id: str = Field(description="論点ID")
    topic_name: str = Field(description="論点名")
    confidence: float = Field(description="信頼度（0.0-1.0）")
    keywords: List[str] = Field(description="関連キーワード")


class PositionInfo(BaseModel):
    """立場情報"""
    speaker: Literal["A", "B"] = Field(description="発言者")
    position: str = Field(description="立場（賛成/反対/中立/懸念等）")
    confidence: float = Field(description="信頼度（0.0-1.0）")
    supporting_evidence: List[str] = Field(description="根拠となる発言")


class TopicRelation(BaseModel):
    """論点間関係"""
    topic: str = Field(description="論点名")
    a_position: str = Field(description="Aの立場")
    b_position: str = Field(description="Bの立場")
    relation_type: str = Field(description="関係タイプ（対立/合意/補足等）")
    intensity: float = Field(description="対立強度（0.0-1.0）")


class ClassificationResult(BaseModel):
    """BERT分類結果"""
    category: str = Field(description="分類カテゴリ（主張/根拠/反論/補足等）")
    confidence: float = Field(description="信頼度")
    subcategory: Optional[str] = Field(description="サブカテゴリ")


class MessageAnalysis(BaseModel):
    """発言分析結果"""
    speaker: Literal["A", "B"] = Field(description="発言者")
    text: str = Field(description="発言内容")
    classification: ClassificationResult = Field(description="BERT分類結果")
    topics: List[str] = Field(description="関連論点")
    sentiment: Optional[str] = Field(description="感情分析結果")


class DisputeAnalysisData(BaseModel):
    """論争解析結果データ"""
    topics: List[TopicInfo] = Field(description="論点リスト")
    relations: List[TopicRelation] = Field(description="対立関係データ")
    message_analyses: List[MessageAnalysis] = Field(description="発言分析結果")
    summary: Dict[str, Any] = Field(description="解析サマリー")


class UsagePayload(BaseModel):
    """使用量情報ペイロード"""
    gemini_tokens: Optional[int] = None
    bert_inferences: int = Field(default=0)
    processing_time_ms: int = Field(description="処理時間（ミリ秒）")


class MetaPayload(BaseModel):
    """メタ情報ペイロード"""
    model: str
    analysis_depth: str
    total_messages: int


class SuccessData(BaseModel):
    """成功レスポンスデータ"""
    analysis: DisputeAnalysisData
    usage: UsagePayload
    meta: MetaPayload


class ErrorPayload(BaseModel):
    """エラーペイロード"""
    code: str
    message: str
    details: Optional[dict] = None


class ApiResponse(BaseModel):
    """統一APIレスポンス形式"""
    success: bool
    data: Optional[SuccessData] = None
    error: Optional[ErrorPayload] = None
