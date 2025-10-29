"""
Chat service for Law Chat Dialog Module
会話生成ユースケース層、プロンプト構築とGemini呼び出しの統合
"""
from ..schemas import ChatRequest, SuccessData, AssistantPayload, UsagePayload, MetaPayload
from ..config import settings
from ..clients.gemini_client import GeminiClient
from ..prompts.prompt_builder import PromptBuilder
from ..logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """チャットサービス"""
    
    def __init__(self):
        """サービス初期化"""
        # 遅延初期化：APIキー未設定でもサーバ起動可能にする
        self.client = None
        self.prompt_builder = PromptBuilder()
        logger.info("ChatService initialized")
    
    async def chat(self, req: ChatRequest) -> SuccessData:
        """
        チャット処理を実行
        
        Args:
            req: チャットリクエスト
            
        Returns:
            成功レスポンスデータ
        """
        logger.info(f"Processing chat request with {len(req.messages)} messages")
        
        # プロンプト構築
        contents = self.prompt_builder.build_prompt(req.messages)
        
        # Geminiクライアント遅延初期化
        if self.client is None:
            self.client = GeminiClient()

        # Gemini API呼び出し
        text, usage_raw = await self.client.generate(
            contents=contents,
            max_tokens=req.max_output_tokens,
            temperature=req.temperature,
        )
        
        # レスポンス構築
        result = SuccessData(
            assistant=AssistantPayload(text=text),
            usage=UsagePayload(
                prompt_tokens=usage_raw.get("prompt_tokens"),
                completion_tokens=usage_raw.get("completion_tokens"),
                total_tokens=usage_raw.get("total_tokens"),
            ),
            meta=MetaPayload(
                model=settings.gemini_model,
                latency_ms=usage_raw.get("latency_ms", 0),
            )
        )
        
        logger.info(f"Chat processing completed successfully")
        return result
