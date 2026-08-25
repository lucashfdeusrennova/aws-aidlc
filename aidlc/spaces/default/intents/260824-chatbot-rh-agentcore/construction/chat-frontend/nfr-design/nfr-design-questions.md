# NFR Design Questions — chat-frontend (U1)

Unit: `chat-frontend` (kind: `ui`) — decisões de design que aterrissam os NFR Requirements aprovados em performance-design, security-design e logical-components. Reliability, scalability e observability caem para U2 (`hr-agent`) por `produces_kinds`.

Contexto já fixado por artefatos anteriores (não re-perguntar):

- **Retry policy — política de erro**: `src/invoke.py::ask_agent` re-eleva `ClientError` como `AgentInvocationError` sem retry adicional (`team.md § Code Style Error handling policy`); boto3 default retry (`standard` mode, ~3 tentativas com backoff em `ThrottlingException`) permanece ativo.
- **Logging**: stdout com `logging.basicConfig(level=logging.INFO, ...)`; sem sinks externos (`security-requirements.md § NFR4.5.1`).
- **Layered boundaries**: `frontend/ → src/ → boto3`; `agent/` isolado (team.md § Code Style).
- **Session ID**: `uuid.uuid4()` server-side (`NFR3.2.1`).
- **Guardrails**: não ativados no MVP (`NFR4.3.1`).

Perguntas focadas em lacunas de design (Standard depth, ~4 perguntas):

---

## Q1 — Retry design em cima do boto3 default

`team.md § Code Style` fixa que `src/invoke.py` captura `ClientError` e re-eleva como `AgentInvocationError` sem retry aplicativo — o retry `standard` do boto3 (padrão do SDK: até 3 tentativas com backoff exponencial em `ThrottlingException`, `RequestTimeoutException`, `RequestTimeout`, etc.) já resolve os transientes. Precisamos declarar isso explicitamente em `performance-design.md`? Ou o silêncio já fala por si?

- A. **Explicit-retry, aceita default do boto3** — Registrar em `performance-design.md` que o retry vive na configuração do cliente boto3 (`config=Config(retries={"mode": "standard", "max_attempts": 3})` explicitamente na criação do cliente para tornar auditável), sem retry aplicativo em `src/invoke.py`. `AgentInvocationError` é sempre um erro do usuário (não retryable de novo).
- B. **Explicit-retry, custom (retry aplicativo)** — Adicionar loop de retry em `src/invoke.py` além do boto3, com 2 tentativas em `ClientError` transiente. Ganha resiliência extra mas complica o error handling e ferra a assinatura de `t_agent_returned` do smoke test (NFR1.1.1).
- C. **Implicit-retry (não registrar)** — Manter a política em `team.md § Code Style` como suficiente; não adicionar seção em `performance-design.md`. Sensor `traceability` ainda vai cobrir via NFR2.x, mas menos auditable.
- X. Other (please specify)

[Answer]:C

---

## Q2 — Bound do histórico de conversação em `st.session_state.messages`

`functional-spec.md § State Machine` e `mockups.md` mostram que `st.session_state.messages` cresce ilimitadamente durante uma sessão até `_clear_conversation` ser chamado. Streamlit re-renderiza a lista inteira a cada rerun; para uma demo curta (10–15 turnos) isso é irrelevante, mas se um participante insistir em uma sessão de 100+ turnos o render fica pesado e a UI trava. Como você quer tratar isso em `performance-design.md`?

- A. **Sem bound** — 1–3 sessões simultâneas × <15 turnos por sessão = irrelevante. Streamlit vai bem até ~50 mensagens antes de qualquer degradação perceptível. Registrar como decisão consciente e ponto de observação para post-mortem.
- B. **Bound suave — 50 mensagens** — Após 50 mensagens, mostrar `st.info("Sua conversa está longa. Clique em 'Limpar conversa' para começar de novo.")` no topo do chat. Sem eviction automática.
- C. **Bound rígido — janela deslizante de 30 turnos** — Manter só os últimos 30 pares user/assistant em `st.session_state.messages`; mais antigos são descartados silenciosamente. Preserva latência mas quebra o "histórico visível" que FR4.1 promete.
- D. **Bound reativo via `NFR1.1.1`** — Detectar via smoke test se o render passa de 500 ms (uma proxy de "muito histórico"); se acontecer na demo, decidir on-the-fly. Não codificar no design.
- X. Other (please specify)

[Answer]:A

---

## Q3 — Comportamento de single-flight no submit

Streamlit protege o submit natively (o `st.chat_input` fica disabled durante um rerun), mas se o participante clicar rapidamente ou o rerun demorar >5 s, pode acontecer double-submit de um mesmo prompt. Isso gera duas invocações do AgentCore Runtime consumindo tempo × custo × sessão dupla. Como você quer tratar em `logical-components.md`?

- A. **Confiar no comportamento default do Streamlit** — `st.chat_input` já bloqueia visualmente durante o processamento; adicionar guarda extra é over-engineering para 1–3 sessões locais. Registrar como decisão consciente.
- B. **Guarda em `st.session_state`** — Adicionar `st.session_state.request_in_flight = True` ao iniciar `ask_agent` e resetar no `finally`. Se o usuário clicar durante um in-flight, `st.warning("Aguarde a resposta anterior antes de enviar outra pergunta.")` e não invoca.
- C. **Guarda por `session_id`** — Manter um `dict[session_id, timestamp]` local; se um segundo submit para o mesmo `session_id` chegar dentro de 100 ms, silenciosamente descartar. Menos user-friendly que B.
- X. Other (please specify)

[Answer]:A

---

## Q4 — Formato de log estruturado para NFR observability futuro

`security-requirements.md § NFR4.5.1` fixa "log em stdout" e `tech-stack-decisions.md § Logging config` fixa `format="%(asctime)s %(name)s %(levelname)s %(message)s"`. Isso já é auditável a olho, mas se algum dia o time promover `hr-agent` para CloudWatch (o que é padrão do AgentCore Runtime) e quiser correlacionar frontend↔backend, JSON structured seria mais amigável. Como você quer registrar em `logical-components.md`?

- A. **Plain text agora, JSON depois** — Manter o format string atual para o workshop; registrar como futuro-work no `logical-components.md § Migration path` que o time considerará JSON logs quando o frontend for expandido para além do MVP local. Nenhum trabalho extra no code-generation.
- B. **JSON structured agora** — Trocar `logging.basicConfig(...)` por `logging.basicConfig(format='{"ts":"%(asctime)s","logger":"%(name)s","level":"%(levelname)s","msg":"%(message)s","session_id":"%(session_id)s"}')` + `logging.LoggerAdapter` que injeta `session_id`. Alinha frontend↔backend desde o dia 1.
- C. **Sem opinar** — Deixar para code-generation decidir. Sinaliza indeterminação de design.
- X. Other (please specify)

[Answer]:B

---

## Consolidated Summary Confirmation

**Resumo consolidado das respostas** (para conferência antes da geração dos artefatos):

- **Q1 = C** — **Implicit-retry**: não registrar seção dedicada de retry em `performance-design.md`. `team.md § Code Style Error handling policy` + o retry `standard` default do boto3 (`~3 tentativas`, backoff exponencial) são suficientes; o design refere-se a esses locais em vez de duplicar a política.
- **Q2 = A** — **Sem bound** em `st.session_state.messages`. Decisão consciente: 1–3 sessões locais × <15 turnos torna a limitação irrelevante para o MVP. Registrar como ponto de observação em `performance-design.md § Anti-requirements`.
- **Q3 = A** — **Single-flight via default do Streamlit**. Confiar em `st.chat_input` que fica disabled durante rerun. Sem `request_in_flight` em `st.session_state`. Registrar como decisão consciente em `logical-components.md § Concurrency`.
- **Q4 = B** — **JSON structured desde o dia 1**. Substituir `logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")` (que `tech-stack-decisions.md § Logging config` havia fixado) por um format JSON com `session_id` injetado via `logging.LoggerAdapter`. Nota importante: esse é um refinamento design-time que **supersede** o format string em `tech-stack-decisions.md` — o design vai declarar isso explicitamente para não deixar drift.

- Looks correct
- Request changes

[Answer]: Looks correct
