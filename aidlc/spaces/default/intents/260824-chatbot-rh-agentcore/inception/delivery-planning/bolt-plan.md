**Collaborator:** aidlc-delivery-agent

# Bolt Plan - Chatbot de RH com Bedrock AgentCore

Sequencia ordenada dos Bolts (um Bolt = uma passada completa dos estagios
3.1-3.7 de Construction sobre uma fatia de trabalho terminando em codigo
que roda) para as 3 unidades declaradas em `unit-of-work.md`. Sem
walking skeleton porque o escopo `mvp` declara `skeleton: off` em
`team-practices.md § Walking Skeleton`.

Fontes consumidas: `requirements.md`, `stories.md`, `mockups.md`,
`components.md`, `unit-of-work.md`, `unit-of-work-dependency.md`,
`unit-of-work-story-map.md`, `contract-summary.md`, `team-practices.md`.

## Sources

- [rq] `requirements.md` - FR1-FR9 e NFR1-NFR10.
- [st] `stories.md` - 11 stories (US1.1..US4.1, 28 ACs).
- [mk] `mockups.md` - refined mockups do frontend Streamlit.
- [cp] `components.md` - 3 componentes.
- [uw] `unit-of-work.md` - U1 chat-frontend (ui, M), U2 hr-agent
  (service, M), U3 infra (packaging, L).
- [ud] `unit-of-work-dependency.md` - DAG: `infra -> hr-agent`.
- [sm] `unit-of-work-story-map.md` - 5 stories em U1, 6 em U2, 0 em U3
  (packaging).
- [cs] `contract-summary.md` - contratos C1, C2, C3.
- [tp] `team-practices.md § Walking Skeleton, § Deployment` -
  `skeleton: off`, deploy local + CDK stack unico.

## Bolt sequence

Ordem: **Bolt 1 U2 -> Bolt 2 U3 -> Bolt 3 U1**. Segue topologia do DAG
`unit-of-work-dependency.md` (Bolt 2 pega o codigo do Bolt 1 e o empacota;
Bolt 3 consome os outputs do Bolt 2) e o rationale risk-first documentado
em `risk-and-sequencing-rationale.md`.

Cada Bolt gera um squash-merge no `main` conforme
`team-practices.md § Way of Working` (nome do commit = slug do Bolt).

### Bolt 1 - hr-agent

- **Unidade**: U2 `u2-hr-agent` (kind: service, complexity M).
- **Walking skeleton**: nao aplicavel (`skeleton: off`).
- **Stories entregues** (6): US1.1, US1.2, US1.3, US1.4, US1.5, US2.1,
  US3.1 [sm]. Nota: US3.1 e a 7a story se contar - a distribuicao real
  em `unit-of-work-story-map.md` mostra 7 stories em U2 (US1.1-1.5 + US2.1 +
  US3.1). O finding cosmetico F1 do reviewer de units-generation ja
  documenta essa nuance.
- **Definition of Done (DoD)**:
  - `agent/agent.py` construido com Strands SDK, tool `retrieve`
    registrada, `BedrockModel` com inference profile ARN.
  - System prompt em portugues cobrindo tom breve, RAG-only,
    fallback "nao encontrei", recusa LGPD.
  - Testes unitarios com `BedrockModel` mockado + stub de `retrieve`
    passando com cobertura >= 80% linhas em `agent/`
    ([tp § Testing Posture]).
  - Teste unitario NFR8.2 (guardrail LGPD com salario ficticio)
    presente e verde.
  - `agent/requirements.txt` pinado com versoes exatas.
  - Nao importa de `src/` nem `frontend/` (invariante de fronteira).
- **Confidence hypothesis**: shipping deste Bolt prova que a
  combinacao Strands + BedrockModel + inference profile ARN + tool
  `retrieve` produz respostas em portugues aderentes ao system prompt
  LGPD, com o guardrail unitario auditavel. Sem essa base, os proximos
  Bolts sao E2E-inuteis.
- **Demo esperada**: `pytest agent/tests/` verde (incluindo NFR8.2);
  smoke unitario mostrando o mock retorna resposta plausivel para as
  4 perguntas canonicas (ferias, feriados, onboarding, avaliacao).
- **Mob owner**: `aidlc-developer-agent` (default MVP - sem
  team-formation).

### Bolt 2 - infra

- **Unidade**: U3 `u3-infra` (kind: packaging, complexity L).
- **Walking skeleton**: nao aplicavel.
- **Stories entregues** (0 diretamente; realiza FR2.1, FR2.2, FR2.3,
  FR3.1, FR3.2, NFR5.1-5.4, NFR7.1-7.2).
- **Definition of Done (DoD)**:
  - Stack CDK Python em `us-east-1` provisionando bucket S3 (SSE-S3),
    Bedrock Knowledge Base (S3 Vectors), AgentCore Runtime consumindo
    o codigo do Bolt 1, e 3 IAM roles least-privilege.
  - `cdk synth` executado e template CloudFormation revisado;
    `cdk deploy` bem-sucedido em conta sandbox.
  - 5 documentos de RH sincronizados para o bucket + `StartIngestionJob`
    executado manualmente [rq FR2.2][tp § Deployment].
  - Outputs `AgentRuntimeArn`, `KnowledgeBaseId`, `DocumentsBucketName`
    expostos [cs C2].
  - Nenhum `Resource: "*"` nas policies IAM
    ([project.md § Forbidden]).
- **Confidence hypothesis**: shipping deste Bolt prova que a
  combinacao das 4 pecas AWS (S3 + KB + Runtime + IAM) e provisionavel
  em `us-east-1` sem `Resource: "*"` e que a KB responde a `Retrieve`
  com trechos dos documentos indexados. Este e o risco AWS-side maior
  do MVP.
- **Demo esperada**: `cdk deploy` completa em <5min; `aws bedrock-agent
  retrieve --knowledge-base-id <KB> --retrieval-query "quantos dias de
  ferias?"` retorna trechos plausiveis; `aws bedrock-agentcore
  invoke-agent-runtime` chamado direto (sem frontend) responde
  corretamente.
- **Mob owner**: `aidlc-developer-agent`.

### Bolt 3 - chat-frontend

- **Unidade**: U1 `u1-chat-frontend` (kind: ui, complexity M).
- **Walking skeleton**: nao aplicavel.
- **Stories entregues** (5): US1.6, US1.7, US1.9, US4.1, mais o wiring
  E2E de US1.1-1.5/US2.1/US3.1 do Bolt 1 [sm].
- **Definition of Done (DoD)**:
  - `frontend/app.py` (Streamlit) com layout de `mockups.md` +
    `interaction-spec.md`.
  - `src/invoke.py` com `ask_agent(prompt, session_id, model_id) -> str`
    conforme [cs C1]; guard 4000 chars primario; mapping
    `ClientError -> AgentInvocationError`; logger de debug.
  - `MODEL_ARNS` com 2 modelos (Claude Haiku 4.5, Amazon Nova Pro);
    dropdown na sidebar; indicador de modelo no cabecalho; botao
    "Limpar conversa".
  - Testes unitarios de `src/invoke.py` (guard 4000, mapping erro)
    com cobertura >= 80% linhas em `src/`.
  - `.env` lido por env vars (`AGENT_RUNTIME_ARN`, `AWS_REGION`)
    consumidas dos outputs do Bolt 2.
  - `scripts/smoke.py` invoca 3-5 perguntas canonicas + 1 pergunta
    LGPD provocadora contra o AgentCore Runtime deployado
    ([tp § Testing Posture]).
- **Confidence hypothesis**: shipping deste Bolt prova E2E que o
  colaborador consegue conversar com o bot em portugues, receber
  respostas de RH em <5s, ver mensagens amigaveis em caso de erro, e
  trocar de modelo sem perder historico. Materializa o valor final da
  iniciativa.
- **Demo esperada**: `streamlit run frontend/app.py` local; 5
  perguntas manuais cobrindo as 11 stories; `scripts/smoke.py` verde
  antes do demo.
- **Mob owner**: `aidlc-developer-agent`.

## Bolt sequence summary

| Order | Bolt | Unit | Kind | Stories | DoD centralizada em                  |
| ----- | ---- | ---- | ---- | ------- | ------------------------------------ |
| 1     | hr-agent | U2 | service | 7 (US1.1-1.5, US2.1, US3.1) | agent/agent.py + testes unitarios     |
| 2     | infra    | U3 | packaging | 0 (realiza FR2-3, NFR5, NFR7) | `cdk synth` + `cdk deploy` + StartIngestionJob |
| 3     | chat-frontend | U1 | ui | 4 (US1.6, US1.7, US1.9, US4.1) + wiring E2E | frontend/app.py + src/invoke.py + scripts/smoke.py |

## Construction iteration mode

Este plano casa com **`unit-major`** iteration: cada Bolt = uma unidade
inteira desenhada AND construida antes da proxima. Alinhado com
`skeleton: off` (nao ha slice horizontal); cada Bolt entrega uma unidade
completa antes do proximo comecar. Ao final do gate, o comando

`bun .kiro/tools/aidlc-state.ts set-construction-iteration unit-major`

sera executado antes da fase Construction.

## Parallel opportunities

Nenhuma. Todos os Bolts executados sequencialmente por
`aidlc-developer-agent` (Q4=A). Team = 1, entao "paralelismo" nao se
aplica.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
