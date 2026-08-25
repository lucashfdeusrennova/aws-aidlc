# Units Generation - Perguntas

## Sources

- [desc] Initial description: Chatbot de RH com AgentCore Runtime + KB + Streamlit.
- [scope] Workflow-selected scope: `mvp`.
- [cp] `components.md` - 3 componentes: `HRChatFrontend`, `AgentInvoker`, `HRAgent`.
- [ad] `decisions.md` - 5 ADRs (ADR-001 fixa a decomposicao em 3 componentes).
- [rq] `requirements.md` - FR/NFR.
- [st] `stories.md` - 11 stories.
- [tp] `team-practices.md § Deployment` - CDK Python em um unico stack para AgentCore Runtime + KB + S3.

## Q1. Estrategia de fronteira de unidade

- A. Por fronteira de deploy (target de deploy = 1 unidade). Streamlit local, agente Strands no AgentCore Runtime, e infra CDK sao 3 unidades distintas.
- B. Por fronteira de camada (`agent/`, `src/`, `frontend/` = 3 unidades, infra funde com o agente).
- C. Por fronteira de repositorio (tudo em 1 monorepo = 1 unidade).
- X. Other (please specify)

[Answer]: A

## Q2. Granularidade

- A. Coarse-grained: 3 unidades (chat-frontend, hr-agent, infra) - uma por target de deploy.
- B. Fine-grained: 5 unidades (frontend, invoker, agent, kb, cdk-stack) - separando invoker e KB como unidades proprias.
- X. Other (please specify)

[Answer]: A

## Q3. Dependency ordering

- A. DAG topologico estrito com paralelismo: `U2 hr-agent` e `U1 chat-frontend` sem dependencia de build (podem ser escritos em paralelo); `U3 infra` depende de `U2` (o stack CDK empacota a imagem/codigo do agente).
- B. Cadeia estrita sequencial `U3 -> U2 -> U1` (infra primeiro, depois agente, depois frontend). Nao permite paralelismo.
- X. Other (please specify)

[Answer]: A

## Q4. Integration points / contratos entre unidades

- A. `U3 infra` expoe ARNs (Runtime, KB, bucket) via outputs do stack CDK; `U1 chat-frontend` le esses ARNs de env vars em runtime; `U2 hr-agent` le `KNOWLEDGE_BASE_ID` via env var injetada pelo IAM role. Contratos definidos em `contract-design`.
- B. Idem A + adicionar teste de contrato entre U1 e U3 (verificar formato do ARN de Runtime).
- X. Other (please specify)

[Answer]: A

## Q5. Modelo de deploy

- A. Deploy independente por unidade: `U3 cdk deploy` -> `U2` deployado dentro do stack de U3 -> `U1 streamlit run` local. Sem CI, sem CD; execucao manual em ordem.
- B. Deploy monolitico: um unico comando compoem tudo.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

3 unidades = 3 kinds distintos (ui, service, packaging), evitando colocar CDK como service e forcar a matriz errada de design em construction. AgentInvoker (`src/`) fica dentro de U1 porque nao tem lifecycle proprio de deploy - mora no mesmo repo Python que o frontend Streamlit. O time confirmou o padrao com "Aprovado" na fase anterior.

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumo consolidado das decisoes deste stage:

- 3 unidades espelhando fronteiras de deploy (Q1=A).
- Coarse-grained: 3 unidades, nao 5 (Q2=A).
- DAG com paralelismo: U2 e U1 independentes; U3 depends_on: [U2] (Q3=A).
- Contratos via CDK outputs + env vars (Q4=A).
- Deploy manual em ordem, sem CI/CD (Q5=A).
- 11 stories rastreadas 1:1: 6 -> U2, 5 -> U1, 0 -> U3 (packaging).

Artefatos produzidos:
- `unit-of-work.md`
- `unit-of-work-dependency.md`
- `unit-of-work-story-map.md`
- `traceability.json`

[Answer]: Looks correct
