from src.pipeline.routing import classify_complexity
from src.pipeline.tools import cite_article


def ingest_and_index() -> dict:
    """
    TODO 1: Ler PDFs do corpus, fazer chunking, embeddings e indexar no Chroma.
    """
    return {
        "status": "pending",
        "message": "Ingestão ainda será implementada.",
    }


def retrieve(question: str, top_k: int = 4) -> list[dict]:
    """
    TODO 2: Buscar chunks relevantes no Chroma.
    """
    return []


def answer(question: str) -> dict:
    """
    TODO 3: Responder usando RAG + tool-use.
    """
    complexity = classify_complexity(question)

    if "artigo" in question.lower() or "art." in question.lower():
        return {
            "answer": cite_article(7),
            "complexity": complexity,
            "sources": [],
        }

    return {
        "answer": (
            "Pipeline inicial criado com sucesso. "
            "Na próxima etapa, conectaremos o corpus da LGPD e o RAG."
        ),
        "complexity": complexity,
        "sources": [],
    }
