"""
XML パーサー
e-Gov API から取得したXMLデータを内部JSON形式に変換
"""
from typing import Dict, List, Any
import xml.etree.ElementTree as ET
import re
from ..logger import get_logger

# lxml が利用可能な場合のみインポート
try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

logger = get_logger(__name__)


class LegalXMLParser:
    """
    法令XMLパーサー
    
    e-Gov法令APIのXML形式を内部で使用するJSON形式に変換
    """
    
    def __init__(self):
        pass
    
    def parse_xml(self, xml_content: str) -> Dict[str, Any]:
        """
        XML文字列をパースして内部形式に変換
        
        Args:
            xml_content: XML文字列
            
        Returns:
            パース済み法令データ（辞書形式）
        """
        try:
            if HAS_LXML:
                # lxml を使用してパース（より堅牢）
                root = etree.fromstring(xml_content.encode('utf-8'))
            else:
                # 標準ライブラリのElementTreeを使用
                root = ET.fromstring(xml_content)
            
            # 法令基本情報を抽出
            law_info = self._extract_law_info(root)
            
            # 条文を抽出
            articles = self._extract_articles(root)
            law_info["articles"] = articles
            
            logger.info(f"Parsed law: {law_info.get('law_id')} with {len(articles)} articles")
            
            return law_info
            
        except (ET.ParseError, ValueError) as e:
            logger.error(f"XML syntax error: {str(e)}")
            raise ValueError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing XML: {str(e)}")
            raise
    
    def _extract_law_info(self, root: ET.Element) -> Dict[str, Any]:
        """
        法令基本情報を抽出
        
        Args:
            root: XMLルート要素
            
        Returns:
            法令基本情報（辞書）
        """
        # 実際のXML構造に合わせて調整が必要
        # ここではサンプル実装
        
        return {
            "law_id": root.get("lawId", ""),
            "title": root.get("title", ""),
            "law_no": root.get("lawNo", ""),
            "law_type": root.get("type", ""),
            "enact_date": root.get("enactDate", ""),
            "source_url": root.get("sourceUrl", "")
        }
    
    def _extract_articles(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        条文データを抽出
        
        Args:
            root: XMLルート要素
            
        Returns:
            条文リスト
        """
        articles = []
        
        # XML の構造に基づいて条文を抽出
        # 実際のXML形式に合わせて調整が必要
        
        # サンプル: <Article> 要素を探す
        for article_elem in root.findall(".//Article"):
            article = {
                "article_no": article_elem.get("number", ""),
                "heading": article_elem.get("heading", ""),
                "text": self._extract_text(article_elem),
                "structure": self._parse_structure(article_elem)
            }
            articles.append(article)
        
        return articles
    
    def _extract_text(self, element: ET.Element) -> str:
        """
        要素のテキストを抽出（ネストされた要素も含む）
        
        Args:
            element: XML要素
            
        Returns:
            テキスト内容
        """
        text_parts = []
        
        # 直接テキストを追加
        if element.text:
            text_parts.append(element.text.strip())
        
        # 子要素のテキストを再帰的に追加
        for child in element:
            if child.text:
                text_parts.append(child.text.strip())
            text_parts.extend(self._extract_text(child).split('\n'))
        
        # 末尾テキストを追加
        if element.tail:
            text_parts.append(element.tail.strip())
        
        return '\n'.join(filter(None, text_parts))
    
    def _parse_structure(self, article_elem: ET.Element) -> Dict[str, Any]:
        """
        条文の構造を解析（項・号などの階層構造）
        
        Args:
            article_elem: 条文XML要素
            
        Returns:
            構造データ
        """
        structure = {"items": []}
        
        # 項レベルを抽出
        for paragraph in article_elem.findall(".//Paragraph"):
            para_text = self._extract_text(paragraph)
            structure["items"].append({
                "level": 1,
                "text": para_text,
                "number": paragraph.get("number")
            })
        
        return structure
    
    def normalize_article_no(self, article_no: str) -> str:
        """
        条番号を正規化（例: "1" -> "第1条"）
        
        Args:
            article_no: 条番号（様々な形式）
            
        Returns:
            正規化された条番号
        """
        # 数字のみの場合
        if article_no.isdigit():
            return f"第{article_no}条"
        
        # 既に"第X条"形式の場合
        if re.match(r'第\d+条', article_no):
            return article_no
        
        # その他の形式を処理
        return article_no

