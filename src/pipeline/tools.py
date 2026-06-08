import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
LGPD_FILE = ROOT_DIR / "data" / "corpus" / "lgpd_lei_13709_compilado.txt"


def _load_lgpd_text() -> str:
    if not LGPD_FILE.exists():
        return ""

    return LGPD_FILE.read_text(encoding="utf-8", errors="ignore")


def cite_article(article_number: int) -> str:
    """
    Tool customizada do domínio.

    Retorna o trecho do artigo informado da LGPD, usando o texto oficial
    salvo em data/corpus/lgpd_lei_13709_compilado.txt.
    """
    text = _load_lgpd_text()

    if not text:
        return (
            "Corpus da LGPD não encontrado. "
            "Execute primeiro: python scripts/download_corpus.py"
        )

    pattern = rf"(Art\.\s*{article_number}\s*(?:º|°|o)?[\s\S]*?)(?=\nArt\.\s*\d+\s*(?:º|°|o)?|\nCAPÍTULO|\nSeção|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return f"Art. {article_number} da LGPD não encontrado no corpus local."

    article_text = match.group(1).strip()

    return f"Fonte: LGPD — Lei nº 13.709/2018\n\n{article_text}"


def extract_article_number(question: str) -> int | None:
    """
    Extrai número de artigo quando a pergunta menciona 'artigo 7' ou 'art. 7'.
    """
    match = re.search(r"(?:artigo|art\.?)\s*(\d+)", question.lower())

    if not match:
        return None

    return int(match.group(1))


TOOLS = {
    "cite_article": cite_article,
}
