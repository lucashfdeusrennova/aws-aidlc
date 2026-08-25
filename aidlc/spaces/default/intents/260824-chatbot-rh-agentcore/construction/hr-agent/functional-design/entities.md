**Collaborator:** aidlc-architect-agent

# Entities - Unit hr-agent

Modelo de entidades do unit `hr-agent` (U2, kind: `service`). Agente
Strands stateless por invocacao (decisao Q4=A): nao mantem entidades
persistidas nem em memoria de longo prazo. Isolamento de sessao e
delegado ao AgentCore Runtime (microVM per session, NFR3.1), fora do
codigo do agente.

Fontes consumidas: `unit-of-work.md` (U2 responsabilidades),
`components.md` (`HRAgent` - zero entities), `requirements.md` (FR3.2,
NFR3.1, NFR3.2, NFR10.1), decisao Q4=A (stateless por invocacao).

## Sources

- [uw] `unit-of-work.md` § U2 - agente Strands rodando em microVM.
- [cp] `components.md` § HRAgent - lista `entities: []`.
- [rq] `requirements.md` - FR3.2 (microVM), NFR3.1 (isolamento), NFR3.2
  (`session_id` server-side), NFR10.1 (Should Have deferido).
- [q4] Q4 = A - stateless por invocacao (MVP); AgentCore Memory
  registrado como `Deferred`.

## Source of truth

```yaml
unit: hr-agent
entities: []
entity_level_constraints: []
relationships: []
rationale: >
  O unit hr-agent nao possui entidades no sentido dominio-modelagem:
  (1) o agente e stateless por invocacao (Q4=A) - cada chamada de
  `invoke_agent_runtime` recebe apenas o prompt atual, sem historico
  persistente do lado do agente;
  (2) a sessao (`runtimeSessionId`) e um identificador opaco recebido
  do frontend e repassado ao Runtime; o agente NAO instancia uma entity
  ChatSession propria (ChatSession pertence a chat-frontend, ownership
  registrado em components.md);
  (3) `retrieve` retorna trechos de documentos como dados de leitura
  transient (nao entidades persistidas do dominio hr-agent);
  (4) system prompt e fragmentos concatenados sao constantes de codigo
  (Q1=B), nao entidades com identidade + atributos consultaveis;
  (5) NFR10.1 (historico via AgentCore Memory) esta explicitamente
  deferido - se acontecer no dia 2, adiciona uma entity `ConversationMemory`
  gerenciada pelo servico AWS (nao pelo codigo do agente).
deferred:
  - id: ConversationMemory
    scope: NFR10.1 (Should Have)
    location: AgentCore Memory (servico gerenciado AWS)
    trigger: Sobrar tempo no dia 2 do workshop apos os Must Have.
    migration_path: Estender agent/agent.py para receber a memoria
      injetada pelo Runtime (contrato Strands + AgentCore Memory).
```

## Summary

O modelo de dados de hr-agent e vazio por design. Toda persistencia de
conversa (historico visivel na UI) mora em `ChatSession` do
`chat-frontend` (`st.session_state.messages`). Toda persistencia de
conhecimento consultado (documentos, embeddings) mora na Bedrock
Knowledge Base (external dependency, nao entity do agente). O sistema
so tem "estado" no sentido de session isolation garantido pela microVM
do Runtime - transparente para o codigo do agente.

Consequencias praticas:

- Zero migrations, zero DDL, zero DAOs em `agent/agent.py`.
- Tests unitarios de `agent/agent.py` nao precisam fixture de banco.
- Nao ha esquema versionado a preocupar em code-generation.

## Assumptions & Open Questions

None.
