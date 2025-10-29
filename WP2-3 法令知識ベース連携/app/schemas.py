"""
Pydantic スキーマ定義
API のリクエスト・レスポンスを定義
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ==================== リクエストスキーマ ====================

class SummarizeArticleRequest(BaseModel):
    """条文要約リクエスト"""
    max_length: Optional[int] = Field(default=200, ge=50, le=2000)
    style: str = Field(default="plain", pattern="^plain$|^legal_summary$|^for_layperson$")


class ExtractTopicsRequest(BaseModel):
    """論点抽出リクエスト"""
    texts: List[str] = Field(..., min_items=1)
    mode: str = Field(default="topic_extraction", pattern="^topic_extraction$|^issue_mapping$")
    max_topics: Optional[int] = Field(default=5, ge=1, le=20)


class SearchLawsRequest(BaseModel):
    """法令検索リクエスト"""
    keyword: Optional[str] = None
    law_reference: Optional[str] = None  # 例: "民法第1条"
    law_type: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# ==================== レスポンススキーマ ====================

class ArticleInfo(BaseModel):
    """条文情報"""
    article_no: str
    heading: Optional[str] = None
    text: str
    structure: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "article_no": "第1条",
                "heading": "私権の内容",
                "text": "私権は、公共の福祉に適合しなければならない...",
                "structure": {
                    "items": [
                        {"level": 1, "text": "私権は、公共の福祉に適合しなければならない。"}
                    ]
                }
            }
        }


class LawInfo(BaseModel):
    """法令基本情報"""
    law_id: str
    title: str
    law_no: str
    enact_date: Optional[datetime] = None
    articles: Optional[List[ArticleInfo]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "CIVIL_LAW_001",
                "title": "民法",
                "law_no": "明治29年法律第89号",
                "enact_date": "1896-04-27T00:00:00",
                "articles": []
            }
        }


class LawListItem(BaseModel):
    """法令リスト項目"""
    law_id: str
    title: str
    law_no: str
    law_type: Optional[str] = None
    enact_date: Optional[datetime] = None


class LawListResponse(BaseModel):
    """法令リストレスポンス"""
    laws: List[LawListItem]
    total: int
    page: int
    per_page: int


class SummaryResponse(BaseModel):
    """要約レスポンス"""
    summary_text: str
    original_reference: Dict[str, str]
    citations: List[str]
    style: str
    word_count: int


class TopicItem(BaseModel):
    """論点項目"""
    id: str
    title: str
    description: str
    source_refs: List[str]


class TopicsResponse(BaseModel):
    """論点抽出レスポンス"""
    topics: List[TopicItem]
    relations: List[Dict[str, Any]]


class ErrorDetail(BaseModel):
    """エラー詳細"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ApiResponse(BaseModel):
    """統一APIレスポンス形式"""
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None

