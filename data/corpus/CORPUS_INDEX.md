# Corpus utilizado no LGPD Helper

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
