from pathlib import Path

import requests
from bs4 import BeautifulSoup


CORPUS_DIR = Path("data/corpus")
CORPUS_DIR.mkdir(parents=True, exist_ok=True)


SOURCES = {
    "lgpd_html": {
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/Lei/L13709compilado.htm",
        "output": CORPUS_DIR / "lgpd_lei_13709_compilado.txt",
        "type": "html_to_txt",
    },
    "guia_agentes": {
        "url": "https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/2021.05.27GuiaAgentesdeTratamento_Final.pdf/@@download/file",
        "output": CORPUS_DIR / "guia_anpd_agentes_tratamento.pdf",
        "type": "pdf",
    },
    "guia_seguranca": {
        "url": "https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-vf.pdf/@@display-file/file",
        "output": CORPUS_DIR / "guia_anpd_seguranca_atpp.pdf",
        "type": "pdf",
    },
}


def download(url: str) -> requests.Response:
    headers = {
        "User-Agent": "Mozilla/5.0 lgpd-helper-rag academic project",
    }

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = []

    for line in text.splitlines():
        clean = " ".join(line.strip().split())
        if clean:
            lines.append(clean)

    return "\n".join(lines)


def save_lgpd_text(url: str, output: Path) -> None:
    print(f"Baixando LGPD: {url}")
    response = download(url)
    response.encoding = response.apparent_encoding or "utf-8"

    text = html_to_text(response.text)

    header = """Lei Geral de Proteção de Dados Pessoais — LGPD
Lei nº 13.709, de 14 de agosto de 2018
Fonte: Presidência da República / Planalto
Arquivo preparado para uso no projeto LGPD Helper RAG.

"""

    output.write_text(header + text, encoding="utf-8")
    print(f"Arquivo salvo em: {output}")


def save_pdf(url: str, output: Path) -> None:
    print(f"Baixando PDF: {url}")
    response = download(url)
    output.write_bytes(response.content)
    print(f"Arquivo salvo em: {output}")


def write_index() -> None:
    index = """# Corpus utilizado no LGPD Helper

Este corpus foi preparado para o projeto final da disciplina Desenvolvendo Software com IA Generativa.

## Documentos

1. `lgpd_lei_13709_compilado.txt`
   - Texto compilado da Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais.
   - Fonte: Presidência da República / Planalto.

2. `guia_anpd_agentes_tratamento.pdf`
   - Guia Orientativo para Definições dos Agentes de Tratamento de Dados Pessoais e do Encarregado.
   - Fonte: Autoridade Nacional de Proteção de Dados — ANPD.

3. `guia_anpd_seguranca_atpp.pdf`
   - Guia Orientativo sobre Segurança da Informação para Agentes de Tratamento de Pequeno Porte.
   - Fonte: Autoridade Nacional de Proteção de Dados — ANPD.

## Uso no projeto

Os arquivos serão lidos pelo pipeline RAG, divididos em chunks, transformados em embeddings e indexados no Chroma.
"""

    (CORPUS_DIR / "CORPUS_INDEX.md").write_text(index, encoding="utf-8")


def main() -> None:
    save_lgpd_text(
        SOURCES["lgpd_html"]["url"],
        SOURCES["lgpd_html"]["output"],
    )

    save_pdf(
        SOURCES["guia_agentes"]["url"],
        SOURCES["guia_agentes"]["output"],
    )

    save_pdf(
        SOURCES["guia_seguranca"]["url"],
        SOURCES["guia_seguranca"]["output"],
    )

    write_index()

    print("\nCorpus preparado com sucesso!")


if __name__ == "__main__":
    main()
