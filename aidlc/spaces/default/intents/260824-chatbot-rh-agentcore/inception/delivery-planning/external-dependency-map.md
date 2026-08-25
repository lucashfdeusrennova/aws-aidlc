**Collaborator:** aidlc-delivery-agent

# External Dependency Map - Chatbot de RH com Bedrock AgentCore

Mapeia itens fora do controle do time de execucao (nao pertencem a
`aidlc-developer-agent` nem aos support agents) que podem bloquear
Bolts. Como o projeto e AI-major, a lista e enxuta, mas nao vazia.

Fontes consumidas: `requirements.md`, `stories.md`, `mockups.md`,
`components.md`, `unit-of-work.md`, `unit-of-work-dependency.md`,
`unit-of-work-story-map.md`, `contract-summary.md`, `team-practices.md`,
`bolt-plan.md`.

## Sources

- [rq] `requirements.md` § Assumptions + § Constraints.
- [st] `stories.md`.
- [mk] `mockups.md`.
- [cp] `components.md`.
- [uw] `unit-of-work.md`.
- [ud] `unit-of-work-dependency.md`.
- [sm] `unit-of-work-story-map.md`.
- [cs] `contract-summary.md`.
- [tp] `team-practices.md § Deployment`.
- [bp] `bolt-plan.md`.

## External dependencies table

| # | Item                                                    | Owner                     | Lead time            | Blocks Bolt(s) | If it slips                                                       |
| - | ------------------------------------------------------- | ------------------------- | -------------------- | -------------- | ----------------------------------------------------------------- |
| E1 | Conta AWS sandbox valida (credenciais + regiao us-east-1 liberada) | Time do workshop / AWS   | Deve estar valida por 2 dias corridos | 1, 2, 3 | Sem sandbox, Bolt 1 continua (unitarios), Bolts 2 e 3 param. Mitigacao: validar credenciais no Dia 1 antes de comecar. |
| E2 | Bedrock, AgentCore Runtime e Knowledge Bases habilitados em us-east-1 na conta sandbox | Time do workshop / AWS   | Habilitacao previa   | 2, 3           | Se AgentCore Runtime nao estiver liberado, Bolt 2 falha no `cdk deploy`. Mitigacao: `aws bedrock-agentcore list-agent-runtimes --region us-east-1` como smoke pre-Bolt 2. |
| E3 | Inference profile ARN para Claude Haiku 4.5 e Amazon Nova Pro liberados em `us-east-1`, prefixo `us.*` | Time do workshop / AWS   | Habilitacao previa   | 1 (unit test com ARN fake, sem chamada real), 2, 3 | Sem inference profile, `bedrock:InvokeModel` falha com `ResourceNotFoundException` [project.md]. Mitigacao: `aws bedrock list-inference-profiles --region us-east-1` no Dia 1. |
| E4 | 5 documentos de RH (`employee_handbook.pdf`, `leave_policy.pdf`, `onboarding_checklist.pdf`, `performance_review_guidelines.pdf`, `public_holidays.csv`) disponiveis para upload | Cliente / RH da empresa   | Antes do Dia 1 [rq A-1] | 2 (ingestion), 3 (E2E)      | Sem documentos, KB fica vazia, agente vira "nao encontrei" para tudo. Mitigacao: pedir os 5 docs no dia 0 do workshop. |
| E5 | Revisao humana dos 5 documentos antes de `StartIngestionJob` (CC-1/CC-2 em ingestion time) | Time do workshop + review de compliance | 1-2h no Dia 2 antes do deploy | 2 (ingestao) | Sem revisao, risco de ingerir dados individuais violando LGPD. Mitigacao: checklist manual + regra `NEVER ingest ... individual employee data` em `project.md § Forbidden`. |
| E6 | Modelos Claude Haiku 4.5 e Amazon Nova Pro respondendo em portugues aceitavelmente | AWS / provedor de modelo | Habilitacao previa   | 3 (smoke test) | Se qualidade de PT-BR estiver ruim em algum modelo, trocar por outro liberado na conta. Mitigacao: 2 modelos configurados (fallback natural). |

Todas as assumptions ja estao registradas em `requirements.md § Assumptions`.

## Risk register aplicavel (subset)

Do `requirements.md § Open Questions` e das constrainedas:

- **R1**: Latencia mediana vs single-shot em <5s. Se um turno demorar 6-8s
  em cold start, NFR1.1 falha na primeira medicao. Mitigacao: registrar
  mediana de 3 chamadas em `scripts/smoke.py` (nao single-shot).
- **R2**: Bedrock Guardrails NAO obrigatorio no MVP (recomendacao apenas).
  Se o guardrail LGPD unitario falhar em teste E2E, considerar ativar
  Bedrock Guardrails como defesa em profundidade em cima do system
  prompt [tp § Bedrock Guardrails].
- **R3**: `StartIngestionJob` e assincrono; se demorar mais que o
  esperado, o Bolt 3 pode comecar antes da KB estar totalmente
  indexada. Mitigacao: aguardar `ingestionJobStatus == COMPLETE`
  antes de rodar smoke test.

## Not applicable in this MVP

- Approvals de outro time.
- Handoffs entre 2 mobs humanos (team-formation SKIP).
- APIs de sistemas externos (folha, ERP, LDAP) - todos em Out of Scope
  de `requirements.md`.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
