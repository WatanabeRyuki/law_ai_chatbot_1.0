"""
論争解析モジュールのログ設定
"""
import logging
import sys
from typing import Optional
from .config import settings


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得
    
    Args:
        name: ロガー名（通常は__name__）
        
    Returns:
        設定済みロガー
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # ログレベル設定
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # フォーマッター設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # プロパゲーション設定
        logger.propagate = False
    
    return logger
