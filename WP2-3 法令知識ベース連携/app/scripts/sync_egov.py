"""
e-Gov API 同期バッチ
定期的に e-Gov API から法令データを取得してデータベースを更新
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any

from ..services.egov_client import EGOvClient
from ..models.models import LegalRef, Article, SyncLog
from ..config import settings
from ..logger import get_logger

logger = get_logger(__name__)


class EGOvSyncBatch:
    """
    e-Gov API 同期バッチ
    
    初回取得および定期更新を実行
    """
    
    def __init__(self):
        self.sync_type = "full"  # or "update"
    
    async def run_full_sync(self):
        """
        フル同期を実行（全法令を取得）
        
        初回インポート時に使用
        """
        logger.info("Starting full sync with e-Gov API...")
        
        sync_log = SyncLog(
            sync_type="full",
            started_at=datetime.utcnow(),
            status="running"
        )
        
        try:
            async with EGOvClient() as client:
                # 法令リストを取得
                laws_data = await client.get_law_list(page=1, per_page=100)
                
                total_laws = laws_data.get("total", 0)
                logger.info(f"Found {total_laws} laws to import")
                
                # 各法令を処理
                processed_count = 0
                
                for law_item in laws_data.get("laws", []):
                    try:
                        await self._import_law(client, law_item)
                        processed_count += 1
                        
                        if processed_count % 10 == 0:
                            logger.info(f"Processed {processed_count}/{total_laws} laws")
                        
                    except Exception as e:
                        logger.error(f"Error importing law {law_item.get('law_id')}: {str(e)}")
                        continue
                
                sync_log.finished_at = datetime.utcnow()
                sync_log.result_count = processed_count
                sync_log.status = "success"
                
                logger.info(f"Full sync completed: {processed_count} laws imported")
        
        except Exception as e:
            logger.error(f"Error in full sync: {str(e)}")
            sync_log.finished_at = datetime.utcnow()
            sync_log.status = "failed"
            sync_log.error_message = str(e)
        
        return sync_log
    
    async def run_update_sync(self):
        """
        差分更新を実行
        
        定期的に実行して変更を取得
        """
        logger.info("Starting update sync with e-Gov API...")
        
        sync_log = SyncLog(
            sync_type="update",
            started_at=datetime.utcnow(),
            status="running"
        )
        
        try:
            async with EGOvClient() as client:
                # 変更検知の実装は e-Gov API の仕様に依存
                # ここではサンプル実装
                
                # 最新の法令リストを取得
                laws_data = await client.get_law_list(page=1, per_page=50)
                
                updated_count = 0
                
                for law_item in laws_data.get("laws", []):
                    # 既存レコードと比較
                    # 差分があれば更新
                    # （実装詳細は省略）
                    updated_count += 1
                
                sync_log.finished_at = datetime.utcnow()
                sync_log.result_count = updated_count
                sync_log.status = "success"
                
                logger.info(f"Update sync completed: {updated_count} laws updated")
        
        except Exception as e:
            logger.error(f"Error in update sync: {str(e)}")
            sync_log.finished_at = datetime.utcnow()
            sync_log.status = "failed"
            sync_log.error_message = str(e)
        
        return sync_log
    
    async def _import_law(
        self,
        client: EGOvClient,
        law_item: Dict[str, Any]
    ):
        """
        個別の法令をインポート
        
        Args:
            client: e-Gov API クライアント
            law_item: 法令項目データ
        """
        law_id = law_item.get("law_id")
        
        # 法令詳細を取得
        law_details = await client.get_law_details(law_id)
        
        # データベースに保存
        # （実装詳細は省略、実際には SQLAlchemy を使用）
        logger.debug(f"Imported law: {law_id}")
    
    async def compare_and_log_changes(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> List[str]:
        """
        データの変更を検出してログに記録
        
        Args:
            old_data: 既存データ
            new_data: 新規データ
            
        Returns:
            変更内容のリスト
        """
        changes = []
        
        # 簡単な実装：主要フィールドを比較
        for key in ["title", "text"]:
            if old_data.get(key) != new_data.get(key):
                changes.append(f"{key} changed")
        
        if changes:
            logger.info(f"Changes detected: {', '.join(changes)}")
        
        return changes


async def main():
    """メイン処理（CLI実行時）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="e-Gov API Synchronization Batch")
    parser.add_argument("--mode", choices=["full", "update"], default="update")
    
    args = parser.parse_args()
    
    batch = EGOvSyncBatch()
    
    if args.mode == "full":
        await batch.run_full_sync()
    else:
        await batch.run_update_sync()


if __name__ == "__main__":
    asyncio.run(main())

