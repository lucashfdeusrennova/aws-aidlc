# NFR Requirements Questions — hr-agent (U2)

Unit: `hr-agent` (kind: `service`) — agente Strands dentro do AgentCore Runtime.

Contexto herdado (não re-perguntar):

- **NFR1.1 latency**: <5s por resposta end-to-end (requirements.md).
- **NFR3.1/3.2 isolation**: microVM per session pelo AgentCore Runtime; `session_id` via `uuid.uuid4()` server-side (chat-frontend/functional-spec § AC1.9.2, BR7.2).
- **NFR4.1-4.3 LGPD**: guard primario via system prompt `_LGPD_SECTION` + teste unitario BR4.3; guardrails Bedrock NAO ativados no MVP (functional-spec § Non-goals).
- **NFR5.1-5.4 IAM**: execution role least-privilege (`bedrock:InvokeModel*` para os 2 inference profile ARNs + `bedrock:Retrieve` para a KB especifica + logs), provisionada por U3 (contract-summary § C3); SSE-S3 no bucket dos docs.
- **NFR6.1 concurrency**: 1-3 sessoes simultaneas — AgentCore Runtime gerencia via microVM per session.
- **NFR7.1 reprodutibilidade**: `agent/requirements.txt` com deps pinadas `==X.Y.Z` (project.md § Mandated).
- **NFR8.1 coverage**: 80% linhas em `agent/`, bloqueante local via `pytest --cov=agent --cov-fail-under=80` (team.md § Testing Posture).
- **NFR8.2 LGPD test**: 1 teste unitario com stub de `retrieve` retornando trecho com salario ficticio — coberto por BR4.3.
- **NFR9 disponibilidade**: sem alvo formal 24/7 na demo (requirements.md).
- **NFR10.1 memory**: Deferred (Should Have; stateless por invocacao — Q4=A, BR7.1).
- **Tech stack**: Python 3.12, Strands Agents SDK, Bedrock Knowledge Base + S3 Vectors, inference profile ARN via env vars — todos afirmados em `project.md § Mandated` e locked em `contract-summary § C3`.
- **Modelos ativos**: Claude Haiku 4.5 e Amazon Nova Pro via inference profile ARN (contract-summary § C3).

Perguntas focadas em lacunas quantitativas do agente (Standard depth, 5 perguntas):

---

## Q1 — Alocação do budget de latência (NFR1.1)

O contrato NFR1.1 é "<5s end-to-end" medido pelo frontend. Do lado do `hr-agent`, o budget se divide entre (a) tempo do Runtime alocar microVM, (b) `retrieve` da KB e (c) resposta do modelo. Como você quer registrar essa alocação para servir de baseline no smoke test?

- A. **Sem sub-budget** — Rastrear apenas o total <5s no smoke test. Se estourar, investigar caso a caso qual etapa consumiu tempo. Aceita menos observabilidade em troca de simplicidade no MVP.
- B. **Sub-budget informal** — Fixar sub-metas orientativas: `retrieve` ~1.5s p95, modelo ~3s p95, overhead ~0.5s. Sem enforcement automatizado; smoke test só verifica o total.
- C. **Sub-budget com traces** — Instrumentar `agent/agent.py` para emitir CloudWatch metrics de `retrieve_ms` e `model_ms`; consulta cada durante o smoke test. Custo: instrumentação extra + config do CloudWatch dentro do Runtime.
- X. Other (please specify)

[Answer]:A

---

## Q2 — Observabilidade: o que logar e o que NÃO logar

`project.md § Forbidden` proíbe logar o payload completo (prompt + resposta) fora da conta sandbox. CloudWatch da conta sandbox é OK. Como você quer registrar o comportamento do agente no MVP?

- A. **Mínimo estruturado** — Log INFO por invocação com: `timestamp`, `runtimeSessionId`, `model_id`, `retrieve_hits` (contagem, não conteúdo), `response_ms`, `outcome` (success/fallback/refusal). NÃO logar `prompt` nem `response` completos. Ideal para auditoria sem violar LGPD.
- B. **Full trace em CloudWatch da sandbox** — Log INFO com prompt + response completos, aceitando que o sink é sandbox (permitido por `project.md`). Facilita debug pós-demo, custo de armazenamento e risco reputacional se log vazar.
- C. **Só ERROR** — Log apenas em falhas (`ClientError`, `KeyError` de BR6.3/6.4, resposta vazia). Sucesso é silencioso.
- X. Other (please specify)

[Answer]:A

---

## Q3 — Comportamento sob >3 sessões concorrentes (NFR6)

`requirements.md § NFR6.1` diz "1-3 sessões simultâneas". O AgentCore Runtime gerencia microVMs; o time do workshop pode estourar isso rodando 4+ notebooks em paralelo. Como registrar esse comportamento como requisito?

- A. **Delegar ao serviço** — Registrar em `scalability-requirements.md` que o comportamento além de 3 sessões é responsabilidade do AgentCore Runtime (backpressure, quota do serviço). O agente não implementa limite próprio. Aceita que respostas podem degradar em latência quando o Runtime enfileirar.
- B. **Fail-fast em quota** — Se `invoke_agent_runtime` retornar `ThrottlingException` ou `ServiceQuotaExceededException`, `AgentInvoker` (U1) converte em `AgentInvocationError` com mensagem específica ("O serviço está ocupado, tente em alguns segundos") — chat-frontend já renderiza `st.error`. Zero código novo no `hr-agent`.
- C. **Circuit-breaker no invoker** — Se falhar 3x seguidas com Throttling, `AgentInvoker` para de tentar por 30s. Overhead de implementação; ganho pequeno para 1-3 sessões.
- X. Other (please specify)

[Answer]:A

---

## Q4 — Bedrock Guardrails: MVP ou Should Have deferred?

`team.md § Bedrock Guardrails (recomendado, não mandatório)` sugere considerar Guardrails com filtro PII em output + denied topics como defense-in-depth para LGPD. `chat-frontend/nfr-design § D7` já registrou "NAO ativados no MVP" — mas essa decisão é registrada aqui em `security-requirements.md` para hr-agent também. Confirmar ou revisar?

- A. **Confirmar: NÃO ativados no MVP** — System prompt (BR2.3, _LGPD_SECTION) é o guard primário. Teste unitário BR4.3 auditavel. Guardrails ficam registrados como Should-Have deferido pós-workshop, se o RH questionar uma resposta específica. Alinha com decisão cross-unit.
- B. **Ativar Guardrails no MVP** — Provisionar Guardrail via CDK U3 com filtro PII (nomes, CPF, e-mail, telefone) em `OUTPUT` e denied topics ("salário, remuneração, folha, dados individuais"). Passar `associatedGuardrailArn` ao `BedrockModel` do Strands. Custo: config no CDK U3, latência extra (~50-100ms por invocação), custo de Guardrail per invocation.
- C. **Ativar só denied topics (sem filtro PII)** — Compromisso: filtrar tópicos proibidos mas não fazer scan de PII no output. Menos latência que B.
- X. Other (please specify)

[Answer]:A

---

## Q5 — Comparação entre modelos (Claude Haiku 4.5 vs Amazon Nova Pro)

`requirements.md § FR6.3` diz "pelo menos 2 modelos testados". `contract-summary § C3` já expõe env vars para os 2. Como quantificar/comparar durante a demo?

- A. **Registro qualitativo no smoke test** — `scripts/smoke.py` roda as 3-5 perguntas canônicas contra cada modelo; operador anota latência aproximada e qualidade (score subjetivo) num bloco de comentário no próprio script. Sem métrica bloqueante.
- B. **NFR quantitativo por modelo** — Fixar targets diferenciados: Claude Haiku <2s p95, Nova Pro <3.5s p95 (Nova é maior). Smoke test valida cada uma via `time.perf_counter()` no invoker. Custo: instrumentação simples em `scripts/smoke.py`.
- C. **Sem comparação estruturada** — O operador troca modelos ao vivo durante a demo e a audiência avalia empiricamente. Sem output escrito.
- X. Other (please specify)

[Answer]:A

---

## Consolidated Summary Confirmation

Resumo consolidado das respostas antes de gerar os 7 artefatos (`performance-requirements.md`, `security-requirements.md`, `scalability-requirements.md`, `reliability-requirements.md`, `observability-requirements.md`, `tech-stack-decisions.md`, `traceability.json`) para o unit `hr-agent`:

- **Q1 = A — Sem sub-budget de latência.** Só rastrear o total <5s no smoke test (`scripts/smoke.py`). NFR1.1 vira `NFR1.1.1` end-to-end, sem sub-metas para `retrieve` ou modelo separadamente. Se estourar, investigação caso a caso.
- **Q2 = A — Log INFO mínimo estruturado.** Cada invocação registra `timestamp`, `runtimeSessionId`, `model_id`, `retrieve_hits` (contagem), `response_ms`, `outcome` (success/fallback/refusal). **Nunca** logar `prompt` nem `response` completos. Sink: CloudWatch da conta sandbox. Alinha com `project.md § Forbidden` (não vazar payload).
- **Q3 = A — Delegar concurrency ao AgentCore Runtime.** Registrar em `scalability-requirements.md` que comportamento >3 sessões é do serviço (backpressure, quota nativa). Agente não implementa limite próprio, sem circuit-breaker no invoker. Se estourar quota, o `ThrottlingException` sobe naturalmente e chat-frontend renderiza `st.error`.
- **Q4 = A — Bedrock Guardrails NÃO ativados no MVP.** Confirma decisão cross-unit já registrada em chat-frontend/nfr-design § D7. System prompt `_LGPD_SECTION` (BR2.3) é o guard primário; BR4.3 é o teste auditável. Guardrails ficam como Should-Have deferido pós-workshop.
- **Q5 = A — Registro qualitativo dos 2 modelos.** `scripts/smoke.py` roda as 3-5 perguntas canônicas contra Claude Haiku 4.5 e Amazon Nova Pro; operador anota latência aproximada e qualidade num bloco de comentário no script. Sem NFR quantitativo diferenciado por modelo (só o teto compartilhado <5s de NFR1.1).

Efeito nos artefatos:

- `performance-requirements.md`: NFR1.1.1 (latência <5s end-to-end, sem sub-budget), sem SLO detalhado por etapa, medição via `scripts/smoke.py`.
- `security-requirements.md`: NFR4.1.1 (LGPD via system prompt), NFR4.2.1 (proibição ingestão PII), NFR4.3.1 (Guardrails deferred), NFR5.1.1-5.4.1 (IAM roles least-privilege — U3 provisiona).
- `scalability-requirements.md`: NFR6.1.1 (1-3 sessões, delegado ao Runtime), sem circuit-breaker; ThrottlingException propaga naturalmente.
- `reliability-requirements.md`: NFR9.1.1 (sem SLA formal), NFR7.1.1 (deps pinadas), sem retry customizado.
- `observability-requirements.md`: NFR-OBS-1 (log INFO estruturado sem payload), NFR-OBS-2 (só CloudWatch sandbox), NFR-OBS-3 (comparação qualitativa entre modelos no smoke).
- `tech-stack-decisions.md`: Python 3.12, Strands Agents SDK, Bedrock KB + S3 Vectors, boto3 `bedrock-agentcore`, 2 modelos via inference profile ARN — todos já locked em `project.md` e `contract-summary`.
- `traceability.json`: cada NFR1-NFR10 do inception mapeado para `NFRx.y` deste unit, com `N/A` explicado onde aplicável.

Escolha a opção que reflete sua decisão:

- Looks correct
- Request changes

[Answer]: Looks correct
