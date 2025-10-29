"""
法令知識ベース連携モジュールのロガー設定
構造化ログ（JSON形式）と監査ログをサポート
"""
import logging
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得
    
    Args:
        name: ロガー名（通常は __name__）
        
    Returns:
        設定済みロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 既にハンドラが設定されている場合は再設定しない
    if logger.handlers:
        return logger
    
    # フォーマット設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # ファイルハンドラ（ログディレクトリが存在する場合）
    log_dir = Path("logs")
    if log_dir.exists():
        file_handler = logging.FileHandler(log_dir / "law_kb_module.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.addHandler(console_handler)
    
    return logger

