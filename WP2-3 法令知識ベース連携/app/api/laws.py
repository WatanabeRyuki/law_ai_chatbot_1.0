"""
法令APIエンドポイント
法令取得、検索、要約、論点抽出
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path

from ..schemas import (
    LawListResponse, LawListItem, LawInfo, ArticleInfo,
    SummarizeArticleRequest, SummaryResponse,
    ExtractTopicsRequest, TopicsResponse,
    ApiResponse
)
from ..services.egov_client import EGOvClient
from ..services.summarizer import ArticleSummarizer
from ..services.topic_extractor import TopicExtractor
from ..logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/list", response_model=LawListResponse)
async def list_laws(
    law_type: Optional[str] = Query(None, description="法令種別（任意）"),
    page: int = Query(1, ge=1, description="ページ番号"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数")
):
    """
    法令リストを取得
    
    Args:
        law_type: 法令種別（任意）
        page: ページ番号
        per_page: 1ページあたりの件数
        
    Returns:
        法令リスト
    """
    logger.info(f"Getting law list: type={law_type}, page={page}, per_page={per_page}")
    
    try:
        async with EGOvClient() as client:
            data = await client.get_law_list(
                law_type=law_type,
                page=page,
                per_page=per_page
            )
        
        laws = [
            LawListItem(
                law_id=item.get("law_id", ""),
                title=item.get("title", ""),
                law_no=item.get("law_no", ""),
                law_type=item.get("law_type"),
                enact_date=item.get("enact_date")
            )
            for item in data.get("laws", [])
        ]
        
        return LawListResponse(
            laws=laws,
            total=data.get("total", len(laws)),
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error getting law list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"法令リストの取得に失敗しました: {str(e)}")


@router.get("/{law_id}", response_model=LawInfo)
async def get_law_details(
    law_id: str = Path(..., description="法令ID")
):
    """
    法令詳細情報を取得
    
    Args:
        law_id: 法令ID
        
    Returns:
        法令詳細情報
    """
    logger.info(f"Getting law details: {law_id}")
    
    try:
        async with EGOvClient() as client:
            data = await client.get_law_details(law_id)
        
        articles = [
            ArticleInfo(
                article_no=article.get("article_no", ""),
                heading=article.get("heading"),
                text=article.get("text", ""),
                structure=article.get("structure")
            )
            for article in data.get("articles", [])
        ]
        
        return LawInfo(
            law_id=data.get("law_id", law_id),
            title=data.get("title", ""),
            law_no=data.get("law_no", ""),
            enact_date=data.get("enact_date"),
            articles=articles,
            metadata=data.get("metadata")
        )
        
    except Exception as e:
        logger.error(f"Error getting law details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"法令詳細の取得に失敗しました: {str(e)}")


@router.get("/{law_id}/articles/{article_no}", response_model=ArticleInfo)
async def get_article(
    law_id: str = Path(..., description="法令ID"),
    article_no: str = Path(..., description="条番号")
):
    """
    特定の条文を取得
    
    Args:
        law_id: 法令ID
        article_no: 条番号
        
    Returns:
        条文情報
    """
    logger.info(f"Getting article: {law_id}/{article_no}")
    
    try:
        async with EGOvClient() as client:
            article_data = await client.get_article(law_id, article_no)
        
        return ArticleInfo(
            article_no=article_data.get("article_no", article_no),
            heading=article_data.get("heading"),
            text=article_data.get("text", ""),
            structure=article_data.get("structure")
        )
        
    except ValueError as e:
        logger.error(f"Article not found: {str(e)}")
        raise HTTPException(status_code=404, detail=f"条文が見つかりません: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"条文の取得に失敗しました: {str(e)}")


@router.post("/{law_id}/articles/{article_no}/summarize", response_model=SummaryResponse)
async def summarize_article(
    law_id: str = Path(..., description="法令ID"),
    article_no: str = Path(..., description="条番号"),
    request: SummarizeArticleRequest = None
):
    """
    条文を要約
    
    Args:
        law_id: 法令ID
        article_no: 条番号
        request: 要約リクエスト
        
    Returns:
        要約結果
    """
    if request is None:
        request = SummarizeArticleRequest()
    
    logger.info(f"Summarizing article: {law_id}/{article_no}")
    
    try:
        # まず条文を取得
        async with EGOvClient() as client:
            article_data = await client.get_article(law_id, article_no)
        
        article_text = article_data.get("text", "")
        
        # 要約を実行
        summarizer = ArticleSummarizer()
        summary = await summarizer.summarize_article(
            article_text=article_text,
            article_no=article_no,
            max_length=request.max_length,
            style=request.style
        )
        
        return SummaryResponse(
            summary_text=summary["summary_text"],
            original_reference=summary["original_reference"],
            citations=summary.get("citations", []),
            style=request.style,
            word_count=summary.get("word_count", 0)
        )
        
    except ValueError as e:
        logger.error(f"Article not found: {str(e)}")
        raise HTTPException(status_code=404, detail=f"条文が見つかりません: {str(e)}")
    except Exception as e:
        logger.error(f"Error summarizing article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"条文の要約に失敗しました: {str(e)}")


@router.post("/extract_topics", response_model=TopicsResponse)
async def extract_topics(request: ExtractTopicsRequest):
    """
    複数条文から論点を抽出
    
    Args:
        request: 論点抽出リクエスト
        
    Returns:
        論点抽出結果
    """
    logger.info(f"Extracting topics from {len(request.texts)} texts")
    
    try:
        extractor = TopicExtractor()
        result = await extractor.extract_topics(
            texts=request.texts,
            mode=request.mode,
            max_topics=request.max_topics
        )
        
        return TopicsResponse(
            topics=result.get("topics", []),
            relations=result.get("relations", [])
        )
        
    except Exception as e:
        logger.error(f"Error extracting topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"論点の抽出に失敗しました: {str(e)}")


@router.post("/search", response_model=LawListResponse)
async def search_laws(
    keyword: Optional[str] = None,
    law_reference: Optional[str] = None,
    law_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
):
    """
    法令を検索（キーワード or 条文参照）
    
    Args:
        keyword: キーワード
        law_reference: 条文参照（例: "民法第1条"）
        law_type: 法令種別
        page: ページ番号
        per_page: 1ページあたりの件数
        
    Returns:
        検索結果
    """
    logger.info(f"Searching laws: keyword={keyword}, reference={law_reference}")
    
    try:
        # 実装: e-Gov API またはデータベースで検索
        # ここではサンプル実装
        
        sample_laws = [
            LawListItem(
                law_id="CIVIL_LAW_001",
                title="民法",
                law_no="明治29年法律第89号",
                law_type="法律",
                enact_date=None
            )
        ]
        
        return LawListResponse(
            laws=sample_laws,
            total=1,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error searching laws: {str(e)}")
        raise HTTPException(status_code=500, detail=f"法令の検索に失敗しました: {str(e)}")

