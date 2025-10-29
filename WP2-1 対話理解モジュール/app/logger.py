"""
Structured logging configuration for Law Chat Dialog Module
構造化ログの設定とロガー取得
"""
import logging
import sys
from typing import Optional


def get_logger(name: str = "dialog") -> logging.Logger:
    """
    構造化ログロガーを取得
    
    Args:
        name: ロガー名
        
    Returns:
        設定済みロガーインスタンス
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"level":"%(levelname)s","name":"%(name)s","message":"%(message)s","ts":"%(asctime)s"}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def setup_logging(level: str = "INFO") -> None:
    """
    アプリケーション全体のログレベルを設定
    
    Args:
        level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='{"level":"%(levelname)s","name":"%(name)s","message":"%(message)s","ts":"%(asctime)s"}',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
