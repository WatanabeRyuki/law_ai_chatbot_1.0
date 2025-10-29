"""
キャッシュサービス
Redis を使用したキャッシュ機能
"""
import json
import redis.asyncio as redis
from typing import Optional, Any
from ..config import settings
from ..logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """
    Redis キャッシュサービス
    
    条文取得結果などをキャッシュしてパフォーマンス向上
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = settings.cache_ttl
    
    async def connect(self):
        """Redis に接続"""
        try:
            self.redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            # Redis が利用不可でも動作は継続
            self.redis_client = None
    
    async def disconnect(self):
        """Redis 接続を切断"""
        if self.redis_client:
            await self.redis_client.aclose()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        キャッシュから値を取得
        
        Args:
            key: キャッシュキー
            
        Returns:
            キャッシュされた値（なければ None）
        """
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        キャッシュに値を保存
        
        Args:
            key: キャッシュキー
            value: 保存する値
            ttl: 有効期限（秒）、デフォルトは settings.cache_ttl
        """
        if not self.redis_client:
            return
        
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            ttl = ttl or self.ttl
            
            await self.redis_client.set(
                key,
                json_value,
                ex=ttl
            )
            
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
            
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
    
    async def delete(self, key: str):
        """
        キャッシュを削除
        
        Args:
            key: キャッシュキー
        """
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
    
    async def exists(self, key: str) -> bool:
        """
        キャッシュキーの存在確認
        
        Args:
            key: キャッシュキー
            
        Returns:
            存在するかどうか
        """
        if not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Error checking cache existence: {str(e)}")
            return False
    
    def make_key(self, prefix: str, *args) -> str:
        """
        キャッシュキーを生成
        
        Args:
            prefix: プレフィックス
            *args: キーを構成する要素
            
        Returns:
            生成されたキー
        """
        parts = [prefix] + [str(arg) for arg in args]
        return ":".join(parts)

