def cite_article(article_number: int) -> str:
    """
    Tool customizada do domínio.

    Futuramente, esta função buscará o texto integral do artigo informado
    dentro do corpus da LGPD.
    """
    return (
        f"Consulta ao Art. {article_number} da LGPD ainda será conectada "
        "ao corpus na próxima etapa do projeto."
    )


TOOLS = {
    "cite_article": cite_article,
}
