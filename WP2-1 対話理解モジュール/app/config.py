"""
Configuration management for Law Chat Dialog Module
環境変数とアプリケーション設定を管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    app_name: str = "Law Chat - Dialog Module"
    environment: str = Field(default="dev")
    
    # Google Gemini API設定
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")
    
    # ネットワーク設定
    request_timeout_sec: int = Field(default=20, env="REQUEST_TIMEOUT_SEC")
    connect_timeout_sec: int = Field(default=5, env="CONNECT_TIMEOUT_SEC")
    
    # ログ設定
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
settings = Settings()
