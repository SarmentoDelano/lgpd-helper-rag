import streamlit as st

from src.pipeline.rag import answer, cache_stats, ingest_and_index


st.set_page_config(
    page_title="LGPD Helper",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ LGPD Helper")
st.caption("Assistente RAG para dúvidas práticas sobre LGPD")

with st.sidebar:
    st.header("Configurações")

    if st.button("Indexar/Reindexar corpus"):
        with st.spinner("Indexando corpus... isso pode levar alguns minutos."):
            result = ingest_and_index(force_rebuild=True)

        st.success(result["message"])
        st.write(result)

    st.divider()

    stats = cache_stats()
    st.subheader("Cache")
    st.write(f"Hits: {stats['hits']}")
    st.write(f"Misses: {stats['misses']}")
    st.write(f"Hit-rate: {stats['hit_rate']:.2%}")

st.markdown(
    """
Faça perguntas sobre a LGPD, bases legais, tratamento de dados pessoais,
consentimento, controlador, operador, retenção e segurança da informação.
"""
)

examples = [
    "Posso armazenar CPF de clientes para emissão de nota fiscal?",
    "O que diz o artigo 7 da LGPD?",
    "Qual a diferença entre controlador e operador?",
    "O que a LGPD diz sobre consentimento?",
]

selected_example = st.selectbox(
    "Exemplos de perguntas:",
    [""] + examples,
)

question = st.text_area(
    "Digite sua pergunta:",
    value=selected_example,
    placeholder="Ex: Posso armazenar CPF de clientes para emissão de nota fiscal?",
    height=120,
)

if st.button("Responder", type="primary"):
    if not question.strip():
        st.warning("Digite uma pergunta antes de continuar.")
    else:
        with st.spinner("Consultando corpus e gerando resposta..."):
            result = answer(question)

        if result.get("cache_hit"):
            st.info("Resposta recuperada do cache.")

        st.subheader("Resposta")
        st.write(result["answer"])

        st.caption(f"Complexidade detectada: {result['complexity']}")

        if result.get("sources"):
            st.subheader("Fontes recuperadas")
            for source in result["sources"]:
                st.write(f"- {source}")
