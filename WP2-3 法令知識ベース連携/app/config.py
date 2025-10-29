"""
法令知識ベース連携モジュールの設定管理
環境変数とアプリケーション設定を管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """法令知識ベース連携モジュール設定クラス"""
    app_name: str = "Law Chat - Legal Knowledge Base Module"
    environment: str = Field(default="dev")
    
    # Google Gemini API設定
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")
    gemini_max_tokens: int = Field(default=2048, env="GEMINI_MAX_TOKENS")
    gemini_temperature: float = Field(default=0.7, env="GEMINI_TEMPERATURE")
    
    # e-Gov API設定
    egov_api_key: str = Field(default="", env="E_GOV_API_KEY")
    egov_base_url: str = Field(
        default="https://elaws.e-gov.go.jp/api/1",
        env="E_GOV_BASE_URL"
    )
    
    # PostgreSQL Database設定
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/law_chat_db",
        env="DATABASE_URL"
    )
    
    # Redis Cache設定
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    cache_ttl: int = Field(default=86400, env="CACHE_TTL")  # 24時間
    
    # BERT Model設定
    bert_model_name: str = Field(
        default="cl-tohoku/bert-base-japanese-v3",
        env="BERT_MODEL_NAME"
    )
    bert_max_length: int = Field(default=512, env="BERT_MAX_LENGTH")
    
    # ネットワーク設定
    request_timeout_sec: int = Field(default=30, env="REQUEST_TIMEOUT_SEC")
    connect_timeout_sec: int = Field(default=5, env="CONNECT_TIMEOUT_SEC")
    
    # ログ設定
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API設定
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Celery設定
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_RESULT_BACKEND"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
settings = Settings()

