**Collaborator:** aidlc-architect-agent

# Observability Requirements - Unit hr-agent

Requisitos de observabilidade derivados da decisão Q2=A (log INFO mínimo
estruturado, sem payload) e dos guardrails LGPD que proíbem payload completo
fora da sandbox (`project.md § Forbidden`).

## Sources

- [rq] `requirements.md` § NFR4.1 (LGPD — implica cuidado com o que se loga).
- [fs] `functional-spec.md` § Handler workflow — steps auditáveis.
- [rl] `rules.md` § BR6.2 (echo `model_id` no response — fonte para o campo `model_id` do log NFR4.1.3), § BR7.2 (echo `session_id` — fonte para `runtimeSessionId` do log).
- [cs] `contract-summary.md` § C1 response schema (`response, model_id, session_id`) — contrato dos campos que NFR4.1.3 registra sem expor payload.
- [pj] `project.md § Forbidden` — proíbe log de payload completo fora da conta sandbox.
- [q2] Q2 = A — log INFO mínimo estruturado.
- [q5] Q5 = A — comparação de modelos qualitativa no smoke test.

## Requirements

### NFR4.1.3 — Log INFO estruturado por invocação (LGPD-safe)

- **Statement**: cada invocação do handler emite EXATAMENTE UM log INFO estruturado, contendo apenas:
  - `timestamp` — ISO 8601, gerado no handler.
  - `runtimeSessionId` — o UUID recebido do envelope AWS API (não expor além do log).
  - `model_id` — label humano (ex.: `"Claude Haiku 4.5"`).
  - `retrieve_hits` — contagem de trechos retornados pelo tool `retrieve` (número inteiro; **não** o conteúdo).
  - `response_ms` — latência interna medida no handler (`time.perf_counter()` antes/depois de `agent(prompt)`).
  - `outcome` — enum: `success` | `fallback` | `refusal` | `error`.
- **Proibido no log** (defense-in-depth com `project.md § Forbidden`):
  - Prompt do usuário (mesmo truncado).
  - Response do agente (mesmo truncado).
  - Nomes individuais, valores monetários, CPF, e-mail, telefone (mesmo se aparecerem no trecho retornado).
  - Contexto adicional além dos 6 campos acima.
- **Formato**: JSON structured logging via `logging.getLogger(__name__).info(json.dumps({...}))`.
- **Sink**: CloudWatch Logs da conta sandbox AWS (log group `/aws/bedrock-agentcore/*` — herdado da execution role, NFR5.1.1).
- **Rationale**: auditável (RH pode reconstruir "quantas perguntas foram feitas no dia da demo", "qual outcome distribuido"), sem violar LGPD (nenhum PII propaga ao log).

### NFR4.1.4 — Sink permitido: CloudWatch da conta sandbox APENAS

- **Statement**: logs do agente vão SOMENTE para CloudWatch da conta sandbox AWS.
- **Proibido** (`project.md § Forbidden`):
  - SaaS de observabilidade externo (Datadog, New Relic, Splunk Cloud, etc.).
  - Analytics de produto (Segment, Amplitude, Mixpanel, etc.).
  - Telemetria de terceiros (Sentry, Rollbar, etc.).
- **Retention**: default do CloudWatch (indefinida no MVP; sem retention policy custom). A conta sandbox é descartável pós-workshop; logs vão junto.

### NFR9.1.5 — Log ERROR em falhas capturadas

- **Statement**: quando o handler encontra erro capturável (KeyError em BR6.3/6.4, resposta vazia do modelo, exceção não prevista), emite log ERROR com:
  - `timestamp`;
  - `runtimeSessionId`;
  - `model_id` (se disponível);
  - `error_type` (classe da exceção, ex.: `KeyError`);
  - `error_message` (string curta, não stack trace completo — evita vazar internos);
  - `outcome: "error"` (mesmo campo do log INFO — permite queries unificadas).
- **Não capturado**: `ClientError` do bedrock-runtime propaga naturalmente para o AgentCore Runtime; log é emitido pelo Runtime, não pelo handler.

### NFR1.1.5 — Sem instrumentação de sub-etapas (Q1=A)

- **Statement**: NÃO instrumentar `retrieve_ms` e `model_ms` separadamente no MVP (Q1=A rejeita a opção C do stage anterior).
- **Consequência**: se `response_ms` estourar 5s, investigação é caso a caso (adicionar log ad-hoc temporário se necessário; nunca comitar).
- **Migration path**: adicionar CloudWatch Metrics via `boto3.client("cloudwatch").put_metric_data(...)` no handler é trivial pós-workshop se o time quiser.

### NFR1.1.6 — Sem correlação distributed-tracing (X-Ray)

- **Statement**: NÃO configurar AWS X-Ray no MVP para o handler. AgentCore Runtime pode emitir seus próprios traces (fora do controle do agente); esses são herdados sem código adicional.
- **Rationale**: 1-3 sessões e 2 dias não justificam config de X-Ray sampling, service map, etc. Se debug pós-demo revelar necessidade, ativar via env `_X_AMZN_TRACE_ID` propagation é trivial.

### NFR9.1.6 — Sem alerting formal

- **Statement**: NÃO configurar CloudWatch Alarms, SNS notifications, PagerDuty, etc. no MVP.
- **Rationale**: NFR9.1.1 já elimina SLA; sem SLA, alerting não tem contrato. Operador monitora demo em tempo real.

### NFR1.1.7 — Comparação inter-modelo qualitativa (Q5=A) — registro da comparação

- **Statement**: comparação Claude Haiku 4.5 vs Amazon Nova Pro é registrada como bloco de comentário no `scripts/smoke.py` durante execução manual do operador, contendo:
  - Latência aproximada observada por pergunta canônica;
  - Nota subjetiva de qualidade (score livre — ex.: "Haiku: 3/5, respostas curtas; Nova: 4/5, mais fluência").
- **Sem output estruturado adicional** (NFR quantitativo por modelo rejeitado por Q5=B).
- **Consumidor**: operador registra a decisão de qual modelo usar como default no dia da demo.

### NFR5.1.3 — Audit trail via CloudTrail (herdado)

- **Statement**: chamadas AWS API (`InvokeAgentRuntime`, `bedrock:InvokeModel`, `bedrock:Retrieve`) são logadas por CloudTrail na conta sandbox (default AWS).
- **Não é responsabilidade do agente**: CloudTrail é configuração da conta; U3 pode habilitá-lo se ainda não estiver ativo (fora do escopo específico deste unit).
- **Uso**: em caso de auditoria pós-demo (RH questiona uma invocação), CloudTrail + o log INFO estruturado do agente reconstroem o cenário.

## Dashboards (não aplicável ao MVP)

MVP não define dashboards. Se pós-workshop houver interesse, um dashboard CloudWatch simples com:

- Contagem de invocações por hora.
- Distribuição de `outcome` (success/fallback/refusal/error).
- p50/p95 de `response_ms` (agregado das próximas semanas de uso, se aplicável).

É construível a partir dos logs INFO estruturados via CloudWatch Log Insights queries. Registrado apenas como Migration Path.

## Alerting Template (não aplicável ao MVP)

Registrado como referência para pós-workshop, se o time optar por operação continuada:

```
Alert: hr-agent error rate elevated
SLI: outcome=error / total invocations
Threshold: > 5% em janela de 15 minutos
Severity: ticket (não page — demo scope)
Runbook: verificar log ERROR + CloudTrail
Notification: e-mail do operador do workshop
Auto-remediation: nenhuma
```

## Anti-Requirements

- Log de prompt/response completo — rejeitado por `project.md § Forbidden` + Q2=A.
- SaaS observability externo — rejeitado por `project.md § Forbidden`.
- CloudWatch Metrics customizadas — rejeitado por Q1=A no MVP.
- X-Ray distributed tracing — não configurado no MVP (NFR1.1.6).
- SLA-driven alerting — rejeitado (NFR9.1.1 elimina SLA).

## Assumptions & Open Questions

None.
