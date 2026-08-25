**Collaborator:** aidlc-delivery-agent

# Team Allocation - Chatbot de RH com Bedrock AgentCore

Atribuicao de mob por Bolt. Como o escopo `mvp` **skip 1.5 (team-formation)**,
nao ha equipes humanas nem Program Board formal; todos os Bolts executam
por `aidlc-developer-agent`, com colaboradores AI dos support agents
convocados pelos estagios de Construction conforme necessario.

Fontes consumidas: `requirements.md`, `stories.md`, `mockups.md`,
`components.md`, `unit-of-work.md`, `unit-of-work-dependency.md`,
`unit-of-work-story-map.md`, `contract-summary.md`, `team-practices.md`.

## Sources

- [rq] `requirements.md`.
- [st] `stories.md`.
- [mk] `mockups.md`.
- [cp] `components.md`.
- [uw] `unit-of-work.md`.
- [ud] `unit-of-work-dependency.md`.
- [sm] `unit-of-work-story-map.md`.
- [cs] `contract-summary.md`.
- [tp] `team-practices.md` - deploy local-only, sem CI/CD.
- [bp] `bolt-plan.md` deste stage - Bolt 1 hr-agent, Bolt 2 infra,
  Bolt 3 chat-frontend.

## Bolt-to-mob assignment

Um "mob" no vocabulario de AI-DLC e o grupo de agentes responsaveis por
executar um Bolt. Como team-formation foi SKIP no escopo `mvp`, o mob
efetivo e um agente unico + supports pontuais.

| Bolt | Unit | Lead agent           | Support agents (invocados por stage de Construction)                    |
| ---- | ---- | -------------------- | ----------------------------------------------------------------------- |
| 1    | U2 hr-agent | aidlc-developer-agent | aidlc-architect-agent (functional-design), aidlc-quality-agent (build-and-test), aidlc-devsecops-agent (nfr-requirements, prompt-injection review) |
| 2    | U3 infra    | aidlc-developer-agent | aidlc-aws-platform-agent (infrastructure-design), aidlc-devsecops-agent (IAM review) |
| 3    | U1 chat-frontend | aidlc-developer-agent | aidlc-design-agent (interaction spec crosscheck), aidlc-quality-agent (build-and-test) |

## Program Board

**Nao aplicavel** neste MVP (team count = 1). O Program Board e uma
visualizacao usada quando ha mais de uma equipe humana simultanea
(`enterprise`, `feature` com team-formation ativo). Aqui, ha um agente
sequencial, entao a sequencia de Bolts em `bolt-plan.md` ja e a
"programacao" completa.

## Human touchpoints

Apesar da execucao ser AI-major, o humano continua no loop nos gates
padrao dos estagios de Construction (functional-design, nfr-requirements,
nfr-design, infrastructure-design, code-generation, build-and-test,
ci-pipeline). Especificamente para este MVP:

- **Bolt 1**: revisao humana do system prompt em portugues antes do
  merge (CC-1/CC-2 depende de linguagem exata).
- **Bolt 2**: revisao humana do template CDK sintetizado por `cdk synth`
  antes do `cdk deploy` [tp § Deployment][project.md § Mandated].
  Revisao humana dos 5 documentos de RH antes de `StartIngestionJob`
  (CC-1/CC-2 em ingestion time).
- **Bolt 3**: revisao humana do fluxo E2E via `streamlit run` antes do
  demo final.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
