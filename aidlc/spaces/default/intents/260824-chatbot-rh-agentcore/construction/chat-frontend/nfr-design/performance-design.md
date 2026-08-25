**Collaborator:** aidlc-architect-agent

# Performance Design — chat-frontend (U1)

Design que aterrissa os requisitos de performance declarados em
`performance-requirements.md` (NFR1.1.1 orçamento 1 s frontend e
NFR6.1.1 modelo 1-participante/1-notebook). Kind `ui` — este artefato
descreve estratégias de execução para o Streamlit local e o cliente
boto3, sem entrar em código completo (isso mora em `code-generation`).

## Sources

- [prf] `performance-requirements.md` — NFR1.1.1 (frontend ≤ 1 s isolado do
  backend via 4 timestamps), NFR6.1.1 (1 notebook = 1 sessão = 1 processo).
- [sec] `security-requirements.md` — NFR4.5.1 (log só em stdout, sem sinks
  externos).
- [tsd] `tech-stack-decisions.md` — `streamlit==1.38.0`, `boto3==1.42.97`,
  `logging.basicConfig` no top-level de `frontend/app.py`.
- [fs] `functional-spec.md` — chat-frontend, § "State Machine" (rerun síncrono
  em `Sending`) e § "Workflows por AC".
- [cs] `contract-summary.md` — C1 (`invoke_agent_runtime` síncrono, sem streaming),
  § "SLA / NFR".
- [rules] `aidlc/spaces/default/memory/team.md § Code Style` (Error handling
  policy, boto3 idioms), `phases/construction.md § Error Handling`.

## Design Solutions

### D1 — Cliente boto3 module-level (para NFR1.1.1)

O cliente `boto3.client("bedrock-agentcore", ...)` é criado UMA vez no
top-level de `src/invoke.py` (não por chamada). Elimina o custo de
handshake TLS e resolução de credencial a cada request, mantendo o
`t_agent_call − t_submit` estável entre chamadas. Alinhado com o idiom
"um único cliente boto3 por módulo" fixado em `team.md § Code Style`.

Sketch (≤15 linhas):

```python
# src/invoke.py (top-level, illustrative)
import boto3
from botocore.config import Config

_AGENTCORE_CONFIG = Config(
    region_name="us-east-1",
    connect_timeout=5,
    read_timeout=30,
)
agentcore_client = boto3.client("bedrock-agentcore", config=_AGENTCORE_CONFIG)
```

**Nota**: implementação completa (guard 4000, mapping de erro) mora em
`code-generation` — este é o esqueleto de decisão, não código pronto.

### D2 — Retry delegado ao boto3 (Q1=C)

`src/invoke.py::ask_agent` NÃO envolve `invoke_agent_runtime` em loop
próprio de retry. A camada de retry é o `standard` mode do boto3 (≤ 3
tentativas com backoff exponencial em `ThrottlingException`,
`RequestTimeoutException`, `RequestTimeout` e affins), habilitado por
default no cliente. `AgentInvocationError` re-elevado por `ask_agent` é
tratado como erro do usuário e nunca é retornado ao boto3 para nova
tentativa.

- **Rationale**: adicionar retry aplicativo introduz uma dimensão a mais
  para explicar quando o smoke test do NFR1.1.1 estourar. Delegando ao
  boto3, o `frontend_elapsed` computado no smoke script continua
  contabilizando o comportamento real observado em produção.
- **Onde a política vive**: `team.md § Code Style — Error handling policy`
  e o comportamento default do SDK. Este artefato não duplica a política;
  aponta para ela.

### D3 — Sem cache local (decisão consciente do MVP)

Nenhum `functools.lru_cache`, `st.cache_data`, nem cache externo em
`chat-frontend`. Cada submit vira uma chamada boto3 nova.

- **Rationale**: RAG do agente pode retornar respostas ligeiramente
  diferentes entre calls (a KB retrieve é determinística mas o modelo
  não), e cache silencioso quebra a expectativa "toda pergunta vai ao
  agente". Também conflitaria com FR4.5 ("Limpar conversa" gera novo
  `session_id`).

### D4 — Sem streaming (herdado do C1)

`contract-summary.md § C1 SLA / NFR` fixou `invoke_agent_runtime` como
sync single-shot. `chat-frontend` renderiza `st.chat_message("assistant").write(response)`
com o texto plano completo — nada de token-by-token streaming.

- **Rationale**: streaming exigiria trocar a assinatura de
  `ask_agent(prompt, session_id, model_id) -> str` para um generator,
  o que não está em contrato-design [cs C1] e adiciona complexidade
  para 5 s de latência total. Fica registrado como candidato para uma
  segunda iteração pós-workshop.

### D5 — Sem cache no seletor de modelo (fs AC4.1)

`st.session_state.model_id` inicializa no primeiro rerun a partir do
default do `st.selectbox`. Trocar de modelo dispara um rerun natural do
Streamlit — não há custo cognitivo para o usuário nem trabalho extra
(o histórico `st.session_state.messages` fica preservado por AC4.1.4).

## Anti-Requirements

- **Sem bound em `st.session_state.messages`** (Q2=A). Decisão consciente:
  1–3 sessões locais × <15 turnos por sessão torna a limitação
  irrelevante para o MVP. Se um participante insistir em >50 turnos e a
  UI travar, o operador aciona `_clear_conversation`. Ponto de observação
  para post-mortem, não um bug.
- **Sem SLO 24/7**. Herda de `performance-requirements.md § Non-Requirements`.
- **Sem throughput target (RPS)** — Streamlit local não é servidor
  multi-tenant.
- **Sem cache local** (D3 acima).
- **Sem preloading** do dropdown de modelo.
- **Sem streaming** (D4 acima).

## Coverage snapshot

| NFR (requirements) | Design solution |
|--------------------|-----------------|
| NFR1.1.1 (1 s frontend budget) | D1 (cliente module-level) + D2 (retry no boto3) + D4 (sem streaming) — nenhum overhead evitável |
| NFR6.1.1 (1 notebook/1 processo) | Nenhum design novo — mora no modelo de deploy de `team.md § Deployment`; o design confirma que o processo Streamlit é single-tenant natural |

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->

## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Date:** 2026-08-25T14:44:46Z
**Iteration:** 1
**Review class:** adversarial

### Findings

| # | Severity | Location | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | Minor | `performance-design.md § D1` | `Config(read_timeout=30, connect_timeout=5)` desalinha com o SLA total de `NFR1.1` (5 s) declarado em `contract-summary.md § C1 SLA / NFR`. Um backend travado deixa o wire boto3 esperar até 30 s por tentativa, e com o retry `standard` (`≤ 3 tentativas`) que D2 delega ao SDK, o pior-caso soma dezenas de segundos silenciosos. `NFR1.1.1` (asserção `frontend_elapsed ≤ 1 s`) sobrevive porque exclui explicitamente o intervalo `t_agent_call → t_agent_returned`, então o teste de U1 não regressa — o custo é UX total, não a métrica do stage. | Alinhar `read_timeout` ao envelope somado de NFR1.1 mais margem para 3 tentativas (ex.: `read_timeout=10, connect_timeout=3`), ou registrar em `Anti-Requirements` que UX além de 5 s ficará silenciosa por design e é observação de post-mortem. Decisão vai para `code-generation`; o design deve apenas fixar a intenção. |
| 2 | Minor | `security-design.md § D3` | O mapping de `ClientError` ecoa fielmente `contract-summary.md § C1 Erros` (mesma lista de 6 tipos + timeout), então é internamente consistente. Porém `bedrock-agentcore.InvokeAgentRuntime` também emite `ServiceQuotaExceededException` e `ConflictException` como `ClientError` (docs públicos do serviço `bedrock-agentcore` referenciados em `tech-stack-decisions.md § Compatibility matrix`). Ambos caem no bucket `default` com a copy "Não consegui responder agora…" — funciona, mas perde sinal (quota exhaustion é orientação técnica, não "tente de novo em alguns segundos"). | Adicionar duas linhas na tabela D3 para `ServiceQuotaExceededException` ("O limite do serviço foi atingido. Contate o time técnico.") e `ConflictException` ("Sessão em conflito. Clique em 'Limpar conversa' e tente de novo."). Ajuste opcional em code-generation; o `default` cobre. |

### Validation Tool Results

| Tool / Check | Result | Interpretation |
|---|---|---|
| Traceability `upstream_ids` vs `## Requirements` upstream | PASS | 10 IDs em `traceability.json` — `NFR1.1.1`, `NFR6.1.1` (2 de `performance-requirements.md`) + `NFR2.1.1`, `NFR3.2.1`, `NFR4.1.1`, `NFR4.3.1`, `NFR4.5.1`, `NFR5.1.1`, `NFR5.2.1`, `NFR5.4.1` (8 de `security-requirements.md`). Nenhum órfão upstream, `reverse: []`. Cobertura completa. |
| Traceability `coverage[].target` resolvibilidade | PASS | Cada um dos 10 targets aponta para seção nomeada existente (`performance-design.md § D1..D5`, `security-design.md § D2..D7`, `logical-components.md § D-Log / D-Concurrency / D-FailureIsolation`). Spot-check manual confirmou as âncoras. |
| Snippets ≤ 15 linhas (constraint do stage) | PASS | `performance-design.md § D1` sketch = 10 linhas não-vazias; `logical-components.md § D-Log` sketch = 13 linhas não-vazias. Ambos declarados "illustrative" e adiam `guard 4000` / `mapping de erro` / shape final do adapter para `code-generation`. Fronteira estratégia/implementação respeitada. |
| Ausência de imports circulares na fronteira C1↔C2 | PASS | `logical-components.md § Fronteira (invariante de camada)` desenha `frontend/ → src/ → boto3` unidirecional. C1 declara não depender de `boto3`/U2 direto; C2 declara não depender de `streamlit`/U2/`frontend/`. Nenhum back-edge. Coerente com `team.md § Code Style — Fronteiras de camada`. |
| Coerência cross-artifact (D5 → D-Log) | PASS | `security-design.md § D5` afirma "Formato: JSON estruturado (ver `logical-components.md § D-Log`)" e D-Log detalha o format string + LoggerAdapter. Referência resolve. Sem redação divergente entre os dois arquivos. |
| Consistência mapping D3 vs `contract-summary.md § C1 Erros` | PASS | `contract-summary.md § C1 Erros` enumera `ThrottlingException`, `ValidationException`, `ResourceNotFoundException`, `AccessDeniedException`, `InternalServerException`, timeout — todos os 6 aparecem em D3 com copy pt-BR determinística por tipo. `AgentInvocationError` re-elevado é tratado como erro do usuário, não retryable (alinhado com D2 e `team.md § Code Style — Error handling policy`). |
| Consistência D6 credential chain vs `project.md` | PASS | D6 confirma resolução via chain default do boto3 (`~/.aws/credentials` → env → IAM role) e proíbe `boto3.Session(aws_access_key_id=…)`. Alinha com `project.md § Forbidden` ("NEVER hardcode account IDs, ARNs…") e `project.md § Mandated` (least-privilege role, `os.environ` para `AGENT_RUNTIME_ARN`/`AWS_REGION`, `.gitignore` desde o commit inicial). Nenhum `secretsmanager:GetSecretValue` direto — segredos futuros roteados via CDK `{{resolve:secretsmanager:…}}` conforme `project.md § Mandated`. |
| Rendering trust boundary (D4) | PASS | `st.chat_message("assistant").write(response)` — `write`, não `markdown(unsafe_allow_html=True)` — trata payload literal como texto plano. Coerente com `NFR4.1.1` (não sanitizar; controle upstream em U2 via `NFR8.2`) e `NFR2.1.1` (renderização pt-BR verbatim). |
| STRIDE — escopo declarado | PASS | Assunção explícita "rede é a conta sandbox e o operador do workshop é confiável" é honesta: `Spoofing`/`Elevation of privilege` são delegados a least-privilege (`NFR5.1.1`), `Information disclosure` é primariamente responsabilidade de U2 (system prompt + curadoria KB + `NFR8.2`), e o STRIDE marca isso explicitamente. Não há risco material empurrado para fora sem controle nomeado. |
| Supersedência do format string (Q4=B) | ADVISORY | `logical-components.md § D-Log` declara **explicitamente** que refina `tech-stack-decisions.md § Logging config` trocando o format plain-text por JSON com `session_id`. A supersedência é auditável em prosa e a `traceability.json` (NFR4.5.1 → D5 + D-Log) aponta para o artefato mais recente. Porém `tech-stack-decisions.md § Logging config` continua mostrando o format plain-text sem callback para D-Log — dois textos co-existem. Design é a camada posterior e prevalece por ordenação, mas leitura isolada de `tech-stack-decisions.md` induziria a implementação errada. Sem autoridade do design para editar o upstream; melhor mitigação é a declaração explícita em D-Log, que já existe. Advisory, não bloqueio. |
| Retry design vs Q1=C (mild deviation) | ADVISORY | Q1=C pedia "não adicionar seção dedicada em `performance-design.md`", mas `§ D2` existe como parágrafo curto documentando a **não-implementação** ("`ask_agent` NÃO envolve em loop próprio; camada de retry é o `standard` mode do boto3, ~3 tentativas") e apontando `team.md § Code Style — Error handling policy` como autoridade. É expansão sutil sobre a letra de Q1=C (que preferia silêncio), mas fiel à substância (delegação ao SDK; sem retry aplicativo). Ganho auditável > custo de aderência literal. Advisory. |

### Summary

O design aterrissa os 10 NFRs do upstream com targets resolvíveis, fronteira de camada acíclica, STRIDE escopado com honestidade e snippets dentro do teto de 15 linhas. As duas questões Minor (`read_timeout=30` desalinhado com o envelope total NFR1.1; mapping D3 sem linhas dedicadas para `ServiceQuotaExceededException`/`ConflictException`) não bloqueiam: a primeira preserva a assertion isolada de `NFR1.1.1` porque o cálculo `frontend_elapsed` subtrai o wire time; a segunda é fielmente derivada do `contract-summary.md § C1 Erros` passado, e o bucket `default` cobre operacionalmente. As duas advertências residuais (supersedência do format-string ficar registrada só no design, e D2 ser um pouco mais explícito do que Q1=C pedia) são operacionais, mitigadas pela declaração explícita em D-Log e por apontar `team.md` como autoridade. Um developer consegue construir `frontend/app.py`, `src/invoke.py` e o adapter de logging a partir destes 4 artefatos sem reabrir requirements nem consultar o architect. Verdict: READY.
