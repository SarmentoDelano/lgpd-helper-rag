from src.pipeline.rag import answer
from src.pipeline.routing import classify_complexity
from src.pipeline.tools import cite_article


def test_answer_returns_dict():
    result = answer("O que é dado pessoal?")
    assert isinstance(result, dict)
    assert "answer" in result


def test_routing_complex_question():
    result = classify_complexity("Posso armazenar CPF de clientes?")
    assert result == "complex"


def test_cite_article_returns_text():
    result = cite_article(7)
    assert "Art. 7" in result
