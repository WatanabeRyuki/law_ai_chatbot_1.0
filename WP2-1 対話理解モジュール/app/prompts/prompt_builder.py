"""
Prompt builder for Law Chat Dialog Module
system/user/assistantロール構成のプロンプト設計と生成
"""
from typing import List
from ..schemas import Message


# 基底システムプロンプト
BASE_SYSTEM_PROMPT = """あなたは日本の法律に詳しい対話アシスタントです。

以下の指針に従って回答してください：
- 回答は日本語で簡潔かつ正確に行う
- 不確かな場合は推測せず、必要な情報を明示的に尋ねる
- 法令名・条文番号・根拠の出典を示す（分かる範囲で）
- 法的助言の免責を短く付す
- ユーザーの感情に配慮し、分かりやすい説明を心がける

将来の拡張性を考慮し、会話履歴や外部知識参照に対応できる設計になっています。"""


class PromptBuilder:
    """プロンプト構築クラス"""
    
    @staticmethod
    def build_prompt(messages: List[Message]) -> List[dict]:
        """
        Gemini向けのマルチターン入力を組み立てる
        
        Args:
            messages: 会話履歴メッセージリスト
            
        Returns:
            Gemini API用のcontents形式
        """
        normalized: List[dict] = []
        
        # systemメッセージを最初のuserメッセージに統合
        system_content = BASE_SYSTEM_PROMPT
        user_messages = []
        
        for m in messages:
            if m.role == "system":
                system_content += "\n\n" + m.content
            elif m.role == "user":
                user_messages.append(m.content)
            elif m.role == "assistant":
                # assistantメッセージはmodelロールに変換
                normalized.append({
                    "role": "model", 
                    "parts": [{"text": m.content}]
                })
        
        # 最初のuserメッセージにsystem内容を統合
        if user_messages:
            first_user_content = system_content + "\n\n" + user_messages[0]
            normalized.append({
                "role": "user", 
                "parts": [{"text": first_user_content}]
            })
            
            # 残りのuserメッセージを追加
            for content in user_messages[1:]:
                normalized.append({
                    "role": "user", 
                    "parts": [{"text": content}]
                })
        
        return normalized
    
    @staticmethod
    def add_external_knowledge(base_prompt: str, knowledge: str) -> str:
        """
        外部知識をプロンプトに追加（将来拡張用）
        
        Args:
            base_prompt: 基底プロンプト
            knowledge: 外部知識テキスト
            
        Returns:
            拡張されたプロンプト
        """
        return f"{base_prompt}\n\n参考情報:\n{knowledge}"
    
    @staticmethod
    def trim_conversation_history(messages: List[Message], max_tokens: int = 4000) -> List[Message]:
        """
        会話履歴をトークン数制限でトリミング（将来拡張用）
        
        Args:
            messages: 会話履歴
            max_tokens: 最大トークン数
            
        Returns:
            トリミングされた会話履歴
        """
        # 簡易実装：最新のuser-assistantペアを保持
        trimmed = []
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == "user":
                # このuserとその後のassistantを保持
                trimmed.insert(0, messages[i])
                if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                    trimmed.insert(1, messages[i + 1])
                break
        
        return trimmed
