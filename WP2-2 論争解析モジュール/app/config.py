"""
論争解析モジュールの設定管理
環境変数とアプリケーション設定を管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """論争解析モジュール設定クラス"""
    app_name: str = "Law Chat - Dispute Analysis Module"
    environment: str = Field(default="dev")
    
    # Google Gemini API設定（WP2-1と共通）
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")
    
    # BERTモデル設定
    bert_model_name: str = Field(default="cl-tohoku/bert-base-japanese-v3", env="BERT_MODEL_NAME")
    bert_max_length: int = Field(default=512, env="BERT_MAX_LENGTH")
    
    # ネットワーク設定
    request_timeout_sec: int = Field(default=30, env="REQUEST_TIMEOUT_SEC")
    connect_timeout_sec: int = Field(default=5, env="CONNECT_TIMEOUT_SEC")
    
    # ログ設定
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 論争解析設定
    max_topics: int = Field(default=10, env="MAX_TOPICS")
    min_confidence_threshold: float = Field(default=0.7, env="MIN_CONFIDENCE_THRESHOLD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
settings = Settings()
