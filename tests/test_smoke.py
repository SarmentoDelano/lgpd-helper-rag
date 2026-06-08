from src.pipeline.routing import classify_complexity
from src.pipeline.tools import cite_article, extract_article_number


def test_routing_complex_question():
    result = classify_complexity("Posso armazenar CPF de clientes?")
    assert result == "complex"


def test_extract_article_number():
    result = extract_article_number("O que diz o artigo 7 da LGPD?")
    assert result == 7


def test_cite_article_returns_text():
    result = cite_article(7)
    assert isinstance(result, str)
    assert len(result) > 20
