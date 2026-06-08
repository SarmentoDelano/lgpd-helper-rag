import streamlit as st

from src.pipeline.rag import answer


st.set_page_config(
    page_title="LGPD Helper",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ LGPD Helper")
st.caption("Assistente RAG para dúvidas práticas sobre LGPD")

question = st.text_area(
    "Digite sua pergunta:",
    placeholder="Ex: Posso armazenar CPF de clientes para emissão de nota fiscal?",
)

if st.button("Responder"):
    if not question.strip():
        st.warning("Digite uma pergunta antes de continuar.")
    else:
        with st.spinner("Consultando o assistente..."):
            result = answer(question)

        st.subheader("Resposta")
        st.write(result["answer"])

        st.caption(f"Complexidade detectada: {result['complexity']}")

        if result.get("sources"):
            st.subheader("Fontes")
            for source in result["sources"]:
                st.write(source)
