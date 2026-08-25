**Collaborator:** aidlc-architect-agent

# Logical Components — chat-frontend (U1)

Vista de fronteiras internas do unit `chat-frontend` (dois componentes
lógicos dentro do mesmo processo Python) e das fronteiras entre esse
processo e o resto do mundo. Complementa `components.md` de Domain
Design com decisões design-time (concurrency, logging, failure isolation)
que só apareceram no NFR Design.

## Sources

- [cp] `components.md` (Domain Design) — HRChatFrontend, AgentInvoker,
  HRAgent; ADR-001 fronteiras de camada.
- [fs] `functional-spec.md` — chat-frontend, § "State Machine" e § "Frontend
  hierarchy summary".
- [prf] `performance-requirements.md` — NFR1.1.1, NFR6.1.1.
- [sec] `security-requirements.md` — NFR3.2.1, NFR4.5.1.
- [tsd] `tech-stack-decisions.md` — logging config, layered boundaries.
- [cs] `contract-summary.md` — C1 (payload), C2 (env vars).
- [rules] `team.md § Code Style — Fronteiras de camada`.

## Component inventory (interno ao processo)

Dois componentes lógicos vivem no mesmo processo Python (uma única
instância de `streamlit run frontend/app.py`), separados por módulo:

### C1 — HRChatFrontend (`frontend/app.py`)

- **Responsabilidade**: renderização do chat, gerenciamento de
  `st.session_state`, guard 4000 (defense in depth), catch de
  `AgentInvocationError` → `st.error`, botão "Limpar conversa" →
  `_clear_conversation`, dropdown de modelo.
- **Dependências**: `streamlit`, `src.invoke.ask_agent`,
  `src.invoke.AgentInvocationError`, `uuid` (stdlib), `logging` (stdlib).
- **Não depende de**: `boto3` direto, `botocore` direto, `src.invoke`
  detalhes internos, U2 (`agent/`).
- **Fronteira**: chama `ask_agent(prompt, session_id, model_id) -> str`
  como única superfície de invocação do agente.

### C2 — AgentInvoker (`src/invoke.py`)

- **Responsabilidade**: encapsula `boto3.client("bedrock-agentcore")`,
  guard 4000 primário (levantando `ValueError`), validação do
  `session_id` (regex UUID), serialização do payload C1, chamada síncrona
  a `invoke_agent_runtime`, mapping de `ClientError` →
  `AgentInvocationError` (com `user_message` determinístico por tipo).
- **Dependências**: `boto3`, `botocore.config`, `botocore.exceptions`,
  `json` (stdlib), `logging` (stdlib), `os` (stdlib).
- **Não depende de**: `streamlit`, U2 (`agent/`), `frontend/`.
- **Estado**: um cliente boto3 module-level (D1 de performance-design);
  sem outros singletons.

### Fronteira (invariante de camada)

```
frontend/app.py  ──►  src/invoke.py  ──►  boto3.client("bedrock-agentcore")
    (C1)                (C2)                     (AWS API)
      │                  │
      │                  └── logging (stdlib)  ──►  stdout
      │
      └── streamlit + logging (stdlib)  ──►  stdout
```

Nenhuma seta na direção oposta. Nenhum shortcut de `frontend/` chamando
`boto3` direto. Nenhum shortcut de `src/` importando `streamlit`. Regra
verificada em code review (não pelo ruff default). Alinha com
`team.md § Code Style — Fronteiras de camada`.

## D-Concurrency — Single-flight via default do Streamlit (Q3=A)

O `st.chat_input` fica visualmente disabled durante um rerun; enquanto
`ask_agent` executa, o campo não aceita novo submit. `st.session_state`
é isolado por sessão (uma aba do browser = uma sessão = um `session_id`),
então nenhum estado compartilhado entre sessões requer lock.

- **Não há** `st.session_state.request_in_flight`.
- **Não há** `dict[session_id, timestamp]` global.
- **Decisão consciente**: 1–3 sessões locais + 1 processo por notebook +
  UI síncrona = double-submit não é vetor real. Adicionar guarda seria
  over-engineering para o MVP.
- **Sinal para post-mortem**: se algum participante relatar
  "cliquei duas vezes e apareceu duplicado", a mitigação futura é B
  (`request_in_flight` guard); registrar como candidato em `Migration path`.

## D-FailureIsolation — Blast radius do processo Streamlit

Cada notebook roda um processo Python isolado; blast radius de um crash
de `frontend/app.py`:

- **Local**: mata só a sessão do participante daquele notebook.
- **Externo**: nenhuma outra sessão afetada (processos separados,
  hosts separados). O AgentCore Runtime permanece ativo.
- **Recuperação**: participante mata o processo (`Ctrl+C`) e reinicia
  (`streamlit run frontend/app.py`). Histórico do `st.session_state` é
  perdido (não há persistência) — é o comportamento esperado do MVP.

Nenhuma orquestração multi-processo, nenhum supervisor, nenhum health
check externo. Overkill para 1–3 notebooks em uma janela de 2 dias.

## D-Log — Formato JSON estruturado com session_id (Q4=B)

**Supersedência explícita**: `tech-stack-decisions.md § Logging config`
fixou `format="%(asctime)s %(name)s %(levelname)s %(message)s"`. Este
design REFINA aquela decisão trocando o format string para JSON
estruturado com `session_id` injetado. A ferramenta de logging
continua sendo o `logging` do stdlib (nenhuma nova dependência); só o
`format` e um `LoggerAdapter` mudam.

Racional para a supersedência: `hr-agent` (U2) vai rodar dentro do
AgentCore Runtime e logar em CloudWatch. Se `chat-frontend` já
estiver em JSON com `session_id`, um `grep` frontend↔backend em uma
mesma sessão fica trivial pós-workshop, sem retrabalho de format.

Sketch (≤15 linhas):

```python
# frontend/app.py (top-level, illustrative)
import logging

_JSON_FORMAT = (
    '{"ts":"%(asctime)s","logger":"%(name)s","level":"%(levelname)s",'
    '"session_id":"%(session_id)s","msg":"%(message)s"}'
)
logging.basicConfig(level=logging.INFO, format=_JSON_FORMAT)

def _adapter(session_id: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(
        logging.getLogger(__name__),
        {"session_id": session_id},
    )
```

- **Onde usar**: `frontend/app.py` cria o adapter uma vez por rerun com
  o `st.session_state.session_id` corrente e passa para `ask_agent` via
  parâmetro `logger` opcional (ou os `logger.error` acontecem dentro de
  `src/invoke.py::ask_agent` com o session_id já validado).
- **`src/invoke.py`** usa o mesmo `_JSON_FORMAT` internamente
  (o `basicConfig` no top-level de `frontend/app.py` é module-level, mas
  `src/invoke.py` pode ser importado por outros callers no futuro —
  duplicar o format no top-level de `src/invoke.py` é aceitável ou
  extrair para `src/logging_config.py` compartilhado. Decisão de shape
  fica para code-generation).
- **Sem** `structlog`, `python-json-logger`, ou qualquer dep extra:
  format string do stdlib é suficiente para o MVP.

## Migration path (post-MVP)

Sinalizações registradas aqui para não perder — nenhum trabalho no
`code-generation` do MVP:

- **CloudWatch handler local**: se `chat-frontend` for hospedado
  (e.g., em Cloud9 ou EC2 no futuro), trocar stdout por `watchtower`
  ou similar. O JSON format facilita a migração.
- **Guarda `request_in_flight`**: se participantes reportarem duplo
  submit, adicionar `st.session_state.request_in_flight` (opção B de
  Q3).
- **Streaming de resposta**: se a resposta ficar longa e a UX pedir
  streaming, trocar `ask_agent -> str` por `ask_agent -> Iterator[str]`
  e usar `st.write_stream(...)`. Requer mudança em C1 do contract-summary.
- **Bound de histórico**: se o participante mantiver a mesma sessão
  por muito tempo, adicionar `st.info(...)` em 50 mensagens (opção B
  de Q2).

## Coverage snapshot

| NFR (requirements) | Component design |
|--------------------|------------------|
| NFR1.1.1 (frontend 1 s) | D-Concurrency (rerun síncrono) + D-Log (sem I/O extra em stdout) |
| NFR3.2.1 (session_id server-side) | C2 valida com regex UUID (defense in depth) |
| NFR4.5.1 (log stdout) | D-Log (JSON no stdlib, zero dependência extra) |
| NFR6.1.1 (1 notebook / 1 processo) | D-FailureIsolation (blast radius local ao processo) |

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
