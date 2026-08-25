# Intent Backlog - Chatbot de RH com Bedrock AgentCore

Backlog priorizado por MoSCoW. Deriva da fronteira de escopo em
`scope-document.md`, respeita as restricoes de `constraint-register.md` e
consome o MVP declarado em `intent-statement.md`. Cada item e uma proto-Unit
que sera decomposta em Units concretas na fase de Inception.

## Legenda de prioridade

- **Must** - sem isto o MVP definido em `intent-statement.md` e Q1 nao roda.
- **Should** - agrega valor significativo ao MVP; entra se cabe no prazo.
- **Could** - se sobrar tempo; nao afeta a demo funcional.
- **Won't** - explicitamente fora desta iniciativa.

## Backlog

| ID | Item | Prioridade | Justificativa / Rastreabilidade |
|----|------|------------|----------------------------------|
| B-1 | Base de conhecimento indexada em Bedrock Knowledge Bases + S3 Vectors com os 5 documentos de RH em `us-east-1` | Must | Requisito estrutural do RAG; [Q2 A][desc][constraint-register.md CT-2, CA-1, CA-3] |
| B-2 | Agente Strands rodando no AgentCore Runtime com a tool `retrieve` fazendo RAG na KB | Must | Sem o agente o MVP de [Q1] nao existe; risco tecnico maior por ser componente novo para o time ([raid-log.md] R-1). Reclassificado de Q2 B como Must porque e implicado pelo MVP em [Q1] |
| B-3 | Frontend Streamlit chamando `invoke_agent_runtime` via boto3 | Must | [Q1] declara "via Streamlit"; sem o frontend nao ha demo. Reclassificado de Q2 C como Must porque e implicado pelo MVP em [Q1] |
| B-4 | Prompt de sistema com regra explicita "sem dados individuais" (LGPD) | Must | Compliance obrigatorio pelo `constraint-register.md` CC-1/CC-2; sem essa regra o [raid-log.md] R-2 (risco de exposicao) nao esta mitigado. Reclassificado de Q2 D como Must |
| B-5 | Troca de modelo de chat via configuracao (2+ modelos comparados em qualidade e latencia) | Must | Faz parte do MVP declarado em [Q1] (item B). Reclassificado de [Q3 A] Should para Must por essa razao |
| B-6 | Testes unitarios com mock do AgentCore (`pytest`) | Should | [Q3 B] - importante para regressao mas nao critico para a demo funcional |
| B-7 | README com comandos de deploy e execucao | Should | [Q3 C] - facilita reproducao pos-demo |
| B-8 | Reranker (`cohere.rerank-v3-5:0`) para melhorar precisao das respostas | Could | [Q4 A] - se sobrar tempo apos as prioridades acima |
| B-9 | Troca de modelo de embedding (`amazon.titan-embed-text-v2:0`) com reindex documentado | Could | [Q4 B] - custo alto (reindex) por [raid-log.md] R-5; adiar |
| B-10 | IaC completo em CDK Python para provisionar KB + role + bucket | Could | [Q4 C] - repetibilidade pos-demo; nao afeta demo funcional |
| B-11 | Historico de conversacao por sessao (AgentCore Memory) | Should | [Q2 E] nao marcado; classificado como Should porque agrega valor mas nao e critico para responder perguntas com RAG |
| B-12 | Integracoes com sistemas transacionais, acoes transacionais, voz, dados individuais, fine-tuning, deploy em producao | Won't | [Q5 A][constraint-register.md CT-1, CO-3, CC-2] |
| B-13 | Metricas de custo por resposta | Could | [Q4 D] nao marcado explicitamente pelo usuario, mas ficou aberto como possibilidade em Q4; classificado como Could por consistencia com os outros itens da Q4. Nao entra se disputar tempo com Must/Should |

## Notas de sequenciamento

Sequenciamento risk-first por [Q6][scope-document.md]:

1. B-2 (agente Strands + AgentCore Runtime) - resolver a maior incerteza tecnica primeiro
2. B-1 (KB indexada) - dependencia funcional do agente
3. B-4 (prompt LGPD) - integra ao agente em B-2
4. B-3 (frontend Streamlit) - depende de B-2 estar respondendo
5. B-5 (troca de modelo de chat) - configuracao sobre B-2 ja rodando
6. B-11 (AgentCore Memory) - opcional, se cabe
7. B-6, B-7 - transversais, ao longo dos 2 dias
8. B-8, B-9, B-10, B-13 - Could Have, apenas se sobrar tempo apos os Must + Should

Nota de reinterpretacao: as respostas do usuario em Q2 e Q3 nao marcaram B, C, D como Must nem A (troca de modelo) como Must, mas [Q1] declara essas capacidades como parte do MVP. Com a confirmacao "Looks correct" registrada apos apresentacao explicita da inconsistencia, a interpretacao adotada foi: qualquer capacidade necessaria para o MVP de [Q1] rodar e Must, independentemente da marcacao em Q2/Q3.

## Assumptions & Open Questions

None.
