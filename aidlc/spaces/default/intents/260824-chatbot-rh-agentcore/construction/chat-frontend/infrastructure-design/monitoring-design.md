**Collaborator:** aidlc-aws-platform-agent

# Monitoring Design — chat-frontend (U1)

Design de observabilidade do unit `chat-frontend` (kind `ui`). Reflete o
que já foi decidido em `logical-components.md § D-Log` (JSON structured
logs em stdout com `session_id`) e a decisão consciente Q2=A: **log-only,
sem métricas coletadas nem SLI/SLO próprio ao unit**.

## Sources

- [lc] `logical-components.md § D-Log` — JSON stdout com session_id via
  `logging.LoggerAdapter`; nenhum handler externo.
- [sec] `security-design.md § D5` — logging non-leaky (não loga prompt em
  ERROR); NFR4.5.1.
- [tsd] `tech-stack-decisions.md` — `logging` do stdlib (Python 3.12).
- [prf] `performance-design.md` — nenhum SLI/SLO 24/7; smoke test é a
  cerimônia de latência (NFR1.1.1).
- [fs] `functional-spec.md` — state machine síncrona; `st.error` renderiza
  erro amigável sem stack trace.
- [cs] `contract-summary.md` — C1 sync single-shot, sem streaming.
- [rules] `team.md § Testing Posture` (`scripts/smoke.py` é a única
  cerimônia de smoke); `project.md § Forbidden` (sem sinks externos).

## Metrics & KPIs

| Metric | Source | Threshold | Why it matters |
|--------|--------|-----------|----------------|
| _(nenhuma métrica coletada em runtime)_ | — | — | Decisão consciente Q2=A: `chat-frontend` no MVP não coleta métrica alguma. Observabilidade se resume aos logs JSON em stdout durante a demo, lidos manualmente pelo operador do workshop se necessário. A cerimônia formal de smoke test (`scripts/smoke.py`, `team.md § Testing Posture`) roda ANTES da demo e cobre o SLI de `frontend_elapsed <= 1 s` (`NFR1.1.1`) — ele pertence ao smoke, não a este stage. |

**Nota**: se algum participante insistir em ter contadores visíveis
(submits, errors), a alternativa Q2=C fica documentada como candidata
post-MVP em `logical-components.md § Migration path`.

## Alerts

| Alert | Condition | Severity | Routes to |
|-------|-----------|----------|-----------|
| _(nenhum alerta configurado)_ | — | — | Sem coleta de métricas + sem sink externo = nenhum alerta automático possível. O operador do workshop lê stdout em tempo real durante a demo. Se um participante relatar problema, o troubleshooting é manual (tail do terminal onde `streamlit run` está rodando). |

## SLIs / SLOs

| SLI | SLO target | Measurement window |
|-----|------------|--------------------|
| _(nenhum SLI/SLO nativo do unit)_ | — | — | O único SLI operacional relevante — `frontend_elapsed <= 1 s` (`NFR1.1.1`) — pertence ao smoke test em `team.md § Testing Posture`, não a este stage. Não há SLO 24/7 (`performance-requirements.md § Non-Requirements`). |

## Logs & Tracing

**Estratégia de log** (aterrissada de `logical-components.md § D-Log`):

- **Formato**: JSON structured. Template:
  `{"ts":"<ISO>","logger":"<name>","level":"<LEVEL>","session_id":"<uuid>","msg":"<text>"}`.
- **Destination**: stdout do processo `streamlit run frontend/app.py` (o
  terminal onde o participante rodou o comando).
- **Handler**: default do stdlib `logging` via `basicConfig`; nenhum
  handler adicional (`FileHandler`, `SysLogHandler`, `SentryHandler` etc.).
- **Retention**: apenas o buffer do terminal do participante. Se o
  participante fechar o terminal, o log é perdido — comportamento
  esperado do MVP local.
- **PII policy** (`security-design.md § D5`): `logger.error(...)` grava
  a mensagem do `ClientError` original e o stack trace, mas **NÃO** loga
  o `prompt` completo. Debug futuro que precisar do prompt DEVE usar
  `logger.debug("prompt=%s", prompt[:200])` truncado.

**Tracing distribuído**: fora de escopo. Não há X-Ray, OpenTelemetry, ou
correlation-id propagation client-side. O `session_id` é a única
correlation key entre `chat-frontend` (log local) e `hr-agent` (log
CloudWatch do runtime); um `grep session_id=<uuid>` cruzado post-demo é
a única cerimônia de correlação prevista.

## Dashboards

Nenhum. O terminal do participante é o "dashboard" — logs JSON em stdout
são human-readable a olho para 1–3 sessões concorrentes de <15 turnos
cada. CloudWatch dashboards, Grafana, ou similar ficam para U2 e
`environment-provisioning` post-MVP.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
