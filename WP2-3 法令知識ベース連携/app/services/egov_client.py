"""
e-Gov API クライアント
法令APIを利用して法令データを取得
"""
import httpx
from typing import Optional, Dict, Any
from .xml_parser import LegalXMLParser
from ..config import settings
from ..logger import get_logger

logger = get_logger(__name__)


class EGOvClient:
    """
    e-Gov法令APIクライアント
    
    e-Gov API から法令データを取得し、XMLをパースして内部形式に変換
    """
    
    def __init__(self):
        self.base_url = settings.egov_base_url
        self.api_key = settings.egov_api_key
        self.timeout = settings.request_timeout_sec
        self.parser = LegalXMLParser()
        
        # HTTPクライアント設定
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "User-Agent": "Law-Chat-Bot/1.0"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_law_list(
        self,
        law_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        法令リストを取得
        
        Args:
            law_type: 法令種別（任意）
            page: ページ番号
            per_page: 1ページあたりの件数
            
        Returns:
            法令リスト（辞書形式）
        """
        try:
            params = {
                "page": page,
                "per_page": per_page
            }
            if law_type:
                params["type"] = law_type
            
            # 注: 実際のAPI仕様に合わせてURLを調整してください
            # ここではサンプル実装
            url = f"{self.base_url}/laws/list"
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('laws', []))} laws from e-Gov API")
            
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from e-Gov API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting law list: {str(e)}")
            raise
    
    async def get_law_details(self, law_id: str) -> Dict[str, Any]:
        """
        法令詳細情報を取得（XML形式）
        
        Args:
            law_id: 法令ID
            
        Returns:
            パース済み法令データ（辞書形式）
        """
        try:
            # 実際のAPIエンドポイントに合わせて調整
            url = f"{self.base_url}/laws/{law_id}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            # XMLデータを取得
            xml_content = response.text
            
            # XMLをパースして内部形式に変換
            parsed_data = self.parser.parse_xml(xml_content)
            
            logger.info(f"Retrieved and parsed law: {law_id}")
            
            return parsed_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting law details: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting law details: {str(e)}")
            raise
    
    async def get_article(
        self,
        law_id: str,
        article_no: str
    ) -> Dict[str, Any]:
        """
        特定の条文を取得
        
        Args:
            law_id: 法令ID
            article_no: 条番号（例: "第1条"）
            
        Returns:
            条文データ（辞書形式）
        """
        try:
            # 法令全体を取得してから該当条文を抽出
            law_data = await self.get_law_details(law_id)
            
            # 該当条文を検索
            for article in law_data.get("articles", []):
                if article.get("article_no") == article_no:
                    return article
            
            raise ValueError(f"Article {article_no} not found in law {law_id}")
            
        except Exception as e:
            logger.error(f"Error getting article: {str(e)}")
            raise
    
    async def close(self):
        """HTTPクライアントをクローズ"""
        await self.client.aclose()

