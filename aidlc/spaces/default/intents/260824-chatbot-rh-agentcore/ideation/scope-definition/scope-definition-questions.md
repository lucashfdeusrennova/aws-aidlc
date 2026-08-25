# Scope Definition - Perguntas de Priorizacao

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Q1. Qual e o escopo minimo viavel (MVP) que entrega valor no fim do dia 2?

- A. Chatbot funcional respondendo perguntas sobre os 5 documentos de RH via Streamlit, com resposta em portugues em menos de 5s, e citando o documento fonte quando aplicavel. Sem troca de modelo, sem reranker, sem observabilidade formal.
- B. Item A + capacidade de trocar o modelo de chat via configuracao para comparar qualidade e latencia (pelo menos 2 modelos testados).
- C. Item B + reranker opcional para melhorar precisao das respostas.
- D. Item B + troca de modelo de embedding (com reindex documentado).
- E. Not yet defined.
- X. Other (please specify)

[Answer]:A, B

## Q2. Quais capacidades sao MUST HAVE para a demo (MoSCoW - Must)?

Marque todas que se aplicam:
- A. Base de conhecimento indexada com os 5 documentos de RH em Bedrock Knowledge Bases + S3 Vectors
- B. Agente Strands rodando no AgentCore Runtime respondendo perguntas
- C. Frontend Streamlit chamando `invoke_agent_runtime`
- D. Prompt de sistema com regra "sem dados individuais" (compliance LGPD)
- E. Historico de conversacao por sessao (AgentCore Memory)
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q3. Quais capacidades sao SHOULD HAVE (Should) - importantes mas nao criticas?

- A. Troca de modelo de chat via configuracao (comparacao de qualidade x latencia entre 2+ modelos)
- B. Testes unitarios com mock do AgentCore (`pytest`)
- C. Documentacao / README rapido com comandos de deploy e execucao
- D. Nenhuma - manter apenas MUST HAVE
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q4. Quais capacidades sao COULD HAVE (Could) - se sobrar tempo?

- A. Reranker (`cohere.rerank-v3-5:0`) para melhorar precisao das respostas
- B. Troca de modelo de embedding (`amazon.titan-embed-text-v2:0`) com reindex documentado
- C. IaC completo em CDK Python para provisionar KB + role + bucket
- D. Metricas de custo por resposta
- E. Nenhuma - descartar Could Have
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A, B, C

## Q5. O que fica explicitamente FORA (Won't Have) desta demo?

- A. Integracoes com sistemas transacionais (folha, ERP, tickets); acoes transacionais (solicitar ferias, abrir chamado); atendimento por voz; acesso a dados individuais; treinamento/fine-tuning; deploy em producao. (Tudo isso ja consta em vision.md e constraint-register.md)
- B. Item A + tudo alem do MVP definido em Q1
- C. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q6. Qual e a preferencia de sequenciamento das capacidades?

- A. Risk-first: comecar pelo componente de maior incerteza tecnica (agente no AgentCore Runtime), depois integrar KB e frontend.
- B. Value-first: comecar pelo frontend Streamlit + agente basico respondendo (sem KB), depois plugar RAG.
- C. Dependency-first: comecar pela base (KB indexada + IAM), depois agente, depois frontend.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q7. Existem prazos duros amarrados a capacidades especificas alem do prazo de 2 dias?

- A. Nao. Unico prazo duro e a demo funcional no fim do dia 2.
- B. Sim (descrever em Other).
- C. Not applicable.
- X. Other (please specify)

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
