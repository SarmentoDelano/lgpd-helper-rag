import hashlib
import json
import math
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

from src.pipeline.cache import ExactCache
from src.pipeline.routing import classify_complexity
from src.pipeline.tools import cite_article, extract_article_number


load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT_DIR / "data" / "corpus"
VECTOR_DIR = ROOT_DIR / "data" / "chroma"
VECTOR_STORE_FILE = VECTOR_DIR / "vector_store.json"

XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "grok-4.3")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K = int(os.getenv("TOP_K", "4"))

EMBEDDING_DIM = 384

CACHE = ExactCache()


def _xai_client() -> OpenAI:
    api_key = os.getenv("XAI_API_KEY")

    if not api_key or api_key == "coloque_sua_chave_xai_aqui":
        raise RuntimeError(
            "XAI_API_KEY não configurada. Preencha o arquivo .env com sua chave da xAI/Grok."
        )

    return OpenAI(
        api_key=api_key,
        base_url=XAI_BASE_URL,
    )


def _clean_text(text: str) -> str:
    lines = []

    for line in text.splitlines():
        clean = " ".join(line.strip().split())
        if clean:
            lines.append(clean)

    return "\n".join(lines)


def _read_txt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")

    return [
        {
            "text": _clean_text(text),
            "metadata": {
                "source": path.name,
                "page": "N/A",
                "type": "txt",
            },
        }
    ]


def _read_pdf(path: Path) -> list[dict]:
    reader = PdfReader(str(path))
    docs = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = _clean_text(text)

        if text:
            docs.append(
                {
                    "text": text,
                    "metadata": {
                        "source": path.name,
                        "page": str(index),
                        "type": "pdf",
                    },
                }
            )

    return docs


def _load_documents() -> list[dict]:
    docs = []

    for path in CORPUS_DIR.glob("*"):
        name = path.name.lower()

        if name.startswith("readme") or name.startswith("corpus_index"):
            continue

        if path.suffix.lower() == ".txt":
            docs.extend(_read_txt(path))

        elif path.suffix.lower() == ".pdf":
            docs.extend(_read_pdf(path))

    return docs


def _chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    if not text:
        return []

    if overlap >= chunk_size:
        overlap = 0

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    return re.findall(r"[a-záàâãéèêíïóôõöúçñ0-9]+", text)


def _local_embedding(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIM
    tokens = _tokenize(text)

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % EMBEDDING_DIM
        sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [value / norm for value in vector]


def _cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    return sum(a * b for a, b in zip(vector_a, vector_b))


def _load_vector_store() -> list[dict]:
    if not VECTOR_STORE_FILE.exists():
        return []

    return json.loads(VECTOR_STORE_FILE.read_text(encoding="utf-8"))


def _save_vector_store(records: list[dict]) -> None:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ingest_and_index(force_rebuild: bool = False) -> dict:
    if VECTOR_STORE_FILE.exists() and not force_rebuild:
        records = _load_vector_store()

        return {
            "status": "ok",
            "message": "Índice local já existe.",
            "chunks": len(records),
        }

    documents = _load_documents()

    if not documents:
        return {
            "status": "error",
            "message": "Nenhum documento encontrado em data/corpus.",
            "chunks": 0,
        }

    records = []
    chunk_counter = 0

    for doc in documents:
        chunks = _chunk_text(doc["text"])

        for chunk_index, chunk in enumerate(chunks):
            chunk_counter += 1

            if chunk_counter % 25 == 0:
                print(f"Processando chunk {chunk_counter}...", flush=True)

            records.append(
                {
                    "id": f"chunk-{chunk_counter}",
                    "content": chunk,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_index": str(chunk_index),
                    },
                    "embedding": _local_embedding(chunk),
                }
            )

    _save_vector_store(records)

    return {
        "status": "ok",
        "message": "Corpus indexado com sucesso no vector store local.",
        "chunks": len(records),
    }


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    records = _load_vector_store()

    if not records:
        ingest_and_index(force_rebuild=True)
        records = _load_vector_store()

    query_embedding = _local_embedding(question)

    scored_records = []

    for record in records:
        similarity = _cosine_similarity(query_embedding, record["embedding"])
        distance = 1 - similarity

        scored_records.append(
            {
                "content": record["content"],
                "metadata": record["metadata"],
                "distance": distance,
                "similarity": similarity,
            }
        )

    scored_records.sort(key=lambda item: item["distance"])

    return scored_records[:top_k]


def _format_context(docs: list[dict]) -> str:
    parts = []

    for index, doc in enumerate(docs, start=1):
        metadata = doc["metadata"]
        source = metadata.get("source", "fonte desconhecida")
        page = metadata.get("page", "N/A")

        parts.append(
            f"[Fonte {index}: {source}, página {page}]\n{doc['content']}"
        )

    return "\n\n---\n\n".join(parts)


def _format_sources(docs: list[dict]) -> list[str]:
    sources = []

    for doc in docs:
        metadata = doc["metadata"]
        source = metadata.get("source", "fonte desconhecida")
        page = metadata.get("page", "N/A")
        distance = doc.get("distance", 0)

        sources.append(
            f"{source} — página {page} — distância: {distance:.4f}"
        )

    return sources


def _generate_answer(prompt: str) -> str:
    client = _xai_client()

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é o LGPD Helper, um assistente especializado em LGPD, "
                    "RAG e dúvidas práticas de compliance."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content


def answer(question: str) -> dict:
    question = question.strip()

    if not question:
        return {
            "answer": "Digite uma pergunta para continuar.",
            "complexity": "empty",
            "sources": [],
            "cache_hit": False,
        }

    cached_answer = CACHE.get(question)

    if cached_answer:
        return {
            "answer": cached_answer,
            "complexity": "cached",
            "sources": [],
            "cache_hit": True,
        }

    complexity = classify_complexity(question)
    article_number = extract_article_number(question)

    tool_context = ""

    if article_number is not None:
        tool_context = cite_article(article_number)

    top_k = 2 if complexity == "simple" else TOP_K
    docs = retrieve(question, top_k=top_k)
    context = _format_context(docs)

    prompt = f"""
Você é o LGPD Helper, um assistente de compliance sobre a Lei Geral de Proteção de Dados Pessoais.

Regras:
- Responda em português do Brasil.
- Use apenas o contexto fornecido.
- Se o contexto não for suficiente, diga que não encontrou base suficiente no corpus.
- Não invente número de artigo.
- Quando houver artigo consultado pela tool, use esse artigo como referência principal.
- Explique de forma prática, como para uma pessoa desenvolvedora ou estudante.
- Finalize com uma observação curta dizendo que a resposta não substitui orientação jurídica especializada.

Pergunta do usuário:
{question}

Resultado da tool cite_article, se houver:
{tool_context}

Contexto recuperado pelo RAG:
{context}

Resposta:
"""

    final_answer = _generate_answer(prompt)
    CACHE.set(question, final_answer)

    return {
        "answer": final_answer,
        "complexity": complexity,
        "sources": _format_sources(docs),
        "cache_hit": False,
    }


def cache_stats() -> dict:
    return CACHE.stats()
