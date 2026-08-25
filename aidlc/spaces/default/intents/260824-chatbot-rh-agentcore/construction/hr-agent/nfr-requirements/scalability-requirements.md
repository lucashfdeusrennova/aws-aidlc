**Collaborator:** aidlc-architect-agent

# Scalability Requirements - Unit hr-agent

Requisitos de escalabilidade derivados de `requirements.md § NFR6` (1-3 sessões)
e da decisão Q3=A (delegar comportamento >3 sessões ao AgentCore Runtime).

## Sources

- [rq] `requirements.md` § NFR6.1 (1-3 sessões simultâneas), § NFR6.2 (sem alvo além disso).
- [fs] `functional-spec.md` § Handler workflow (single invocation, stateless).
- [rl] `rules.md` § BR7.1 (statelessness — Q4=A).
- [cs] `contract-summary.md` § C1 SLA (NFR6.1 no MVP).
- [q3] Q3 = A — delegar comportamento >3 sessões ao serviço.

## Requirements

### NFR6.1.1 — Suportar 1-3 sessões simultâneas

- **Metric**: número de sessões concorrentes (uma sessão = uma aba Streamlit ativa fazendo perguntas com o mesmo `runtimeSessionId`).
- **Target**: 1-3.
- **Load condition**: 2 dias de workshop, 3 notebooks paralelos do time técnico.
- **Enforcement**: garantido pelo AgentCore Runtime via microVM per session (não pelo código do agente).
- **Validation**: teste manual — 3 participantes rodam Streamlit em paralelo durante 1 pergunta cada; verificar que as 3 respostas retornam <5s (NFR1.1.1) sem erro.

### NFR6.1.2 — Comportamento além de 3 sessões: delegado ao AgentCore Runtime

- **Statement**: o agente NÃO implementa limite próprio de concorrência, backpressure customizado ou circuit-breaker. O comportamento acima de 3 sessões é responsabilidade do AgentCore Runtime (Q3=A).
- **Expected behavior** (não garantido pelo agente):
  - Runtime enfileira invocações extras e responde com latência elevada; OU
  - Runtime retorna `ThrottlingException` / `ServiceQuotaExceededException` — `AgentInvoker` (U1) converte em `AgentInvocationError` e chat-frontend renderiza `st.error` amigável (BR6.1 chat-frontend / AC1.7.2).
- **Rationale**:
  - MVP com 3 sessões esperadas não justifica overhead de circuit-breaker customizado (Q3=C rejeitado).
  - O `ThrottlingException` natural do boto3 já é uma sinalização observável do limite (contract-summary § C1 Erros).
  - Escalar limite de sessões requer aumentar quota do serviço (AWS support ticket), não código do agente.

### NFR6.2.1 — Sem alvos de escala além do MVP

- **Statement**: NÃO há target formal para dezenas ou centenas de sessões concorrentes no MVP.
- **Migration path pós-workshop**: se a demanda pós-demo justificar, avaliar (a) provisionar quota adicional do AgentCore Runtime, (b) trocar modelo (Nova Pro tem mais throughput que Haiku), (c) adicionar circuit-breaker no `AgentInvoker` se necessário. Todos os passos são cross-unit e reabrem esta decisão.

### NFR10.1.1 — Statelessness como facilitador de escala (deriva de NFR10.1 Deferred)

- **Statement**: agente stateless por invocação (BR7.1, Q4=A do stage anterior). Cada `InvokeAgentRuntime` é independente; sem memória compartilhada entre sessões nem entre turnos da mesma sessão.
- **Consequência para escalabilidade**: horizontal scaling é trivial no lado do agente — cada microVM do Runtime é auto-suficiente. Nenhum cache/estado compartilhado limita.
- **Custo dessa decisão**: perguntas de follow-up sem contexto ("e para gestores?") não são resolvidas — trade-off aceito no MVP.

### NFR6.2.2 — Modelo escolhido não afeta a curva de escala do agente

- **Statement**: troca de modelo (`context.model_id` no payload) NÃO altera o comportamento de escala do handler; muda apenas latência per invocation e custo per token. A escala em sessões concorrentes continua a ser governada pelo Runtime, não pelo modelo.
- **Validation**: `scripts/smoke.py` deve produzir resultados <5s (NFR1.1.1) para ambos os modelos ativos durante o teste 3-participantes-paralelos.

## Data Growth (não aplicável ao agente)

O agente NÃO persiste dados. Growth do bucket S3 (documentos) e da Knowledge Base
(embeddings) é responsabilidade de U3 e não impacta o comportamento do agente:

- KB `retrieve` continua funcionando com N documentos até o limite do S3 Vectors.
- Sem retention policy no agente (não há o que reter — statelessness).

## Anti-Requirements

- Auto-scaling horizontal do agente — não aplicável (AgentCore Runtime é gerenciado).
- Circuit-breaker customizado — rejeitado por Q3=C.
- Rate limit interno — rejeitado por Q3=A (delegado).
- Cache de respostas — rejeitado (BR7.1 stateless; cache implicaria estado compartilhado).
- Sharding por documento — não aplicável (KB unificada, sem tenant).

## Assumptions & Open Questions

None.
