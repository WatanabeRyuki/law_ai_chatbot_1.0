"""
Pydantic schemas for Law Chat Dialog Module API
統一JSONレスポンス形式とリクエスト/レスポンスモデル
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ロール定義
Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    """会話メッセージモデル"""
    role: Role
    content: str


class ChatRequest(BaseModel):
    """チャットリクエストモデル"""
    messages: List[Message] = Field(
        description="system/user/assistantの順不同履歴。最後がuser想定。"
    )
    max_output_tokens: Optional[int] = Field(default=1024, ge=1, le=8192)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)


class AssistantPayload(BaseModel):
    """アシスタント応答ペイロード"""
    text: str
    reasoning: Optional[str] = None


class UsagePayload(BaseModel):
    """使用量情報ペイロード"""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class MetaPayload(BaseModel):
    """メタ情報ペイロード"""
    model: str
    latency_ms: int


class SuccessData(BaseModel):
    """成功レスポンスデータ"""
    assistant: AssistantPayload
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
