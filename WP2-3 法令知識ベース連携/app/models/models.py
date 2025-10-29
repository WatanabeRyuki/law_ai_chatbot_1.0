"""
法令知識ベースデータベースモデル
SQLAlchemy ORM を使用したテーブル定義
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LegalRef(Base):
    """
    法令マスタテーブル
    法令の基本情報を保存
    """
    __tablename__ = "legal_refs"
    
    # 主キー（法令ID：法令番号など）
    law_id = Column(String(100), primary_key=True, comment="法令ID")
    title = Column(String(500), nullable=False, comment="法令名")
    law_no = Column(String(50), nullable=False, comment="法令番号")
    law_type = Column(String(50), comment="法令種別（憲法・法律・政令など）")
    enact_date = Column(DateTime, comment="施行年月日")
    source_url = Column(Text, comment="e-Gov API のURL")
    raw_xml = Column(Text, comment="元のXMLデータ（バックアップ用）")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    articles = relationship("Article", back_populates="legal_ref", cascade="all, delete-orphan")


class Article(Base):
    """
    条文テーブル
    各条文の内容を保存
    """
    __tablename__ = "articles"
    
    article_id = Column(Integer, primary_key=True, autoincrement=True)
    law_id = Column(String(100), ForeignKey("legal_refs.law_id"), nullable=False)
    article_no = Column(String(50), nullable=False, comment="条番号（例：第1条、第1条の2）")
    heading = Column(String(500), comment="見出し・題名")
    text = Column(Text, nullable=False, comment="条文本文")
    parsed_json = Column(JSON, comment="正規化された構造データ（項・号など）")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    legal_ref = relationship("LegalRef", back_populates="articles")
    embedding = relationship("ArticleEmbedding", back_populates="article", uselist=False)


class ArticleEmbedding(Base):
    """
    条文埋め込みベクトルテーブル
    ベクトル検索用の埋め込みデータを保存
    """
    __tablename__ = "article_embeddings"
    
    embedding_id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.article_id"), nullable=False, unique=True)
    embedding = Column(Text, comment="ベクトルデータ（JSON形式）")
    model_name = Column(String(100), default="bert-base-japanese-v3")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    article = relationship("Article", back_populates="embedding")


class SyncLog(Base):
    """
    同期ログテーブル
    e-Gov API からの同期処理の履歴を記録
    """
    __tablename__ = "sync_log"
    
    sync_id = Column(Integer, primary_key=True, autoincrement=True)
    sync_type = Column(String(50), nullable=False, comment="同期種別（full/update）")
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    result_count = Column(Integer, default=0, comment="取得件数")
    status = Column(String(20), default="running", comment="running/success/failed")
    error_message = Column(Text, comment="エラーメッセージ")
    created_at = Column(DateTime, default=datetime.utcnow)


class CacheEntry(Base):
    """
    キャッシュエントリ（オプション）
    Redis の代わりに DB でキャッシュを管理する場合
    """
    __tablename__ = "cache_entries"
    
    cache_key = Column(String(500), primary_key=True)
    cache_value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

