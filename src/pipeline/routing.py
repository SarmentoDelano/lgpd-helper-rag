def classify_complexity(question: str) -> str:
    """
    Classifica a pergunta como simples ou complexa.

    simple: perguntas conceituais curtas.
    complex: perguntas que exigem RAG, análise, artigo ou base legal.
    """
    question_lower = question.lower()

    complex_terms = [
        "posso",
        "pode",
        "base legal",
        "artigo",
        "consentimento",
        "retenção",
        "retencao",
        "exclusão",
        "exclusao",
        "risco",
        "compare",
        "analise",
        "controlador",
        "operador",
    ]

    if any(term in question_lower for term in complex_terms):
        return "complex"

    return "simple"
