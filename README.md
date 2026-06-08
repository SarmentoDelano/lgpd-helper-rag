# LGPD Helper — Assistente RAG para Compliance LGPD

> Assistente com IA Generativa que responde dúvidas práticas sobre LGPD usando RAG, citações do corpus e uma tool customizada para consulta de artigos da lei.

<!-- GIF de demo será adicionado ao final do projeto -->

**Live demo:** https://lgpd-apper-rag.streamlit.app

## Problem statement

O projeto resolve o problema de consulta prática à LGPD para pessoas desenvolvedoras, estudantes e profissionais que precisam entender obrigações básicas sobre tratamento de dados pessoais.

A abordagem com LLM + RAG + Tool-use é adequada porque as respostas precisam ser fundamentadas em um corpus específico, evitando respostas genéricas ou inventadas. O RAG recupera trechos relevantes da legislação e dos guias usados como base, enquanto a tool customizada permite consultar artigos específicos da LGPD de forma controlada.

## Arquitetura

```mermaid
flowchart LR
    USER([User]) --> UI[Streamlit UI]
    UI --> CACHE{Exact cache?}
    CACHE -->|hit| RESP[Response]
    CACHE -->|miss| ROUTING[Classify complexity]
    ROUTING -->|simple| CHEAP[Cheap LLM]
    ROUTING -->|complex| RAG[(Chroma RAG)]
    RAG --> TOOL[Custom tool: cite_article]
    TOOL --> LLM[LLM]
    CHEAP --> RESP
    LLM --> RESP
```

## Setup

```bash
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar ambiente no Windows
.venv\Scripts\activate

# 3. Instalar dependências
pip install -e .

# 4. Configurar variáveis
copy .env.example .env

# 5. Rodar localmente
streamlit run src/ui/streamlit_app.py
```

## Cost & Latency

O projeto implementa uma estratégia simples de redução de custo baseada em **exact cache**. Quando uma pergunta já foi respondida anteriormente, a resposta é recuperada do cache em memória, evitando uma nova chamada ao modelo LLM.

Benchmark realizado com 10 perguntas, sendo 5 perguntas únicas e 5 perguntas repetidas para testar o cache.

| Estratégia         | Chamadas LLM | Redução | P95 latency |
| ------------------ | -----------: | ------: | ----------: |
| Baseline sem cache |  10 chamadas |       — |  2416.28 ms |
| + Exact cache      |   5 chamadas |  50.00% |  2416.28 ms |

Métricas observadas:

* Total de perguntas: 10
* Cache hits: 5
* Cache misses: 5
* Hit-rate: 50.00%
* Redução estimada de chamadas LLM: 50.00%
* Latência média: 856.15 ms
* P95 latency: 2416.28 ms

As perguntas repetidas foram respondidas com latência próxima de 0 ms, demonstrando que o cache evita chamadas desnecessárias ao LLM.

## Design decisions

* O corpus foi composto por documentos oficiais da LGPD e da ANPD, priorizando fontes institucionais e relevantes para dúvidas práticas de compliance.
* A aplicação usa RAG para recuperar trechos do corpus antes de gerar a resposta, reduzindo o risco de respostas genéricas ou sem base documental.
* A tool `cite_article` foi criada para consultar artigos específicos da LGPD diretamente no corpus local, evitando que o modelo invente números ou conteúdos de artigos.
* A primeira versão usava Chroma como vector store, mas a solução final usa um vector store local em JSON com embeddings por hashing, evitando problemas de compatibilidade com `onnxruntime` no Windows e simplificando o deploy.
* O cache exato foi escolhido como estratégia inicial de redução de custo por ser simples, transparente e suficiente para demonstrar redução de chamadas ao LLM.
* O modelo de geração usa a API da Groq com o modelo `openai/gpt-oss-20b`, por oferecer boa velocidade e facilidade de uso em projetos acadêmicos.

## Limitations

* O corpus é fixo e não permite upload de novos documentos pela interface.
* O sistema não substitui orientação jurídica especializada; as respostas devem ser usadas apenas como apoio inicial.
* O embedding local baseado em hashing é simples e pode ter menor qualidade semântica do que embeddings comerciais especializados.
* O cache atual é mantido em memória, então é reiniciado quando a aplicação é reiniciada.
* A qualidade da resposta depende da qualidade dos trechos recuperados pelo RAG e da cobertura dos documentos presentes no corpus.

## Tech stack

* **LLM:** Groq API com modelo `openai/gpt-oss-20b`
* **RAG:** recuperação local sobre corpus LGPD/ANPD
* **Embeddings:** embedding local baseado em hashing
* **Vector store:** JSON local com similaridade cosseno
* **Tool-use:** função `cite_article` para consulta direta a artigos da LGPD
* **Cache:** exact cache em memória
* **UI:** Streamlit
* **Deploy:** Streamlit Community Cloud


## Estrutura

```text
lgpd-helper-rag/
├── data/
│   ├── corpus/
│   └── chroma/
├── src/
│   ├── ui/streamlit_app.py
│   ├── pipeline/
│   │   ├── rag.py
│   │   ├── tools.py
│   │   ├── cache.py
│   │   └── routing.py
│   └── observability/trace.py
├── tests/test_smoke.py
├── pyproject.toml
├── .env.example
└── README.md
```

## Rubrica

| Critério | Peso | Entrega |
|---|:-:|---|
| Técnica | 40% | RAG + tool-use + cache/routing funcionando |
| README | 30% | README com problema, setup, arquitetura, métricas e limites |
| Custo | 20% | Redução de custo com cache ou routing |
| Demo | 10% | URL pública funcionando |

## Deploy

O deploy foi planejado para o Streamlit Community Cloud.

Arquivo principal:

```bash
src/ui/streamlit_app.py