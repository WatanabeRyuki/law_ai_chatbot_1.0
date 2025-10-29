"""
XML パーサーの単体テスト
"""
import pytest
from app.services.xml_parser import LegalXMLParser


@pytest.fixture
def parser():
    """パーサーインスタンス"""
    return LegalXMLParser()


@pytest.fixture
def sample_xml():
    """サンプルXMLデータ"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<Law>
    <LawId>CIVIL_LAW_001</LawId>
    <Title>民法</Title>
    <LawNo>明治29年法律第89号</LawNo>
    <Articles>
        <Article number="第1条" heading="私権の内容">
            <Paragraph number="1">
                私権は、公共の福祉に適合しなければならない。
            </Paragraph>
        </Article>
        <Article number="第2条" heading="解釈の基準">
            <Paragraph number="1">
                この法律は、個人の尊厳と両性の本質的平等を明記して、解釈しなければならない。
            </Paragraph>
        </Article>
    </Articles>
</Law>
"""


def test_parse_xml(parser, sample_xml):
    """XML をパースしてJSON形式に変換できる"""
    result = parser.parse_xml(sample_xml)
    
    assert "law_id" in result
    assert "title" in result
    assert "articles" in result
    
    assert result["law_id"] == "CIVIL_LAW_001"
    assert result["title"] == "民法"
    assert len(result["articles"]) == 2


def test_extract_articles(parser, sample_xml):
    """条文が正しく抽出される"""
    result = parser.parse_xml(sample_xml)
    articles = result["articles"]
    
    assert len(articles) == 2
    assert articles[0]["article_no"] == "第1条"
    assert articles[1]["article_no"] == "第2条"


def test_normalize_article_no(parser):
    """条番号が正規化される"""
    assert parser.normalize_article_no("1") == "第1条"
    assert parser.normalize_article_no("第1条") == "第1条"
    assert parser.normalize_article_no("第123条") == "第123条"

