# Functional Design Questions — hr-agent (U2)

Unit: `hr-agent` (kind: `service`) — agente Strands dentro do AgentCore Runtime. 7 stories atribuídas (US1.1, US1.2, US1.3, US1.4, US1.5, US2.1, US3.1).

Contexto já fixado por artefatos anteriores (não re-perguntar):

- **Framework**: Strands Agents SDK (`strands` + `strands_tools`) — `project.md § Mandated`.
- **Tool**: `retrieve` do Strands consumindo a Knowledge Base via env var `KNOWLEDGE_BASE_ID` — `team.md § Code Style`, `components.md § HRAgent`.
- **Model**: `BedrockModel` recebe inference profile ARN (nunca ID `us.*` direto) — `project.md § Mandated`, `NEVER pass a us.*`.
- **Payload C1** (`contract-summary.md`): request `{prompt, context.model_id}` → response `{response, model_id, session_id}`.
- **Model resolution**: label → ARN via env vars `INFERENCE_PROFILE_ARN_CLAUDE_HAIKU` / `INFERENCE_PROFILE_ARN_NOVA_PRO` (`chat-frontend/functional-spec.md § AC4.1.3`).
- **Guardrails Bedrock**: NÃO ativados no MVP (`chat-frontend/nfr-design/security-design.md § D7`, cross-unit contract). U2 tem que respeitar essa decisão; o system prompt é o guard primário.
- **LGPD test (MUST)**: teste unitário obrigatório com prompt provocador ("Qual o salário do João?") + `retrieve` stubado retornando trecho com salário fictício; asserção: resposta NÃO repete valor verbatim (`team.md § Testing Posture`).
- **Session isolation**: microVM per session — garantia do AgentCore Runtime (`NFR3.1`); U2 não gerencia sessão explicitamente.

Perguntas focadas em lacunas de design deste unit (Standard depth, 4 perguntas):

---

## Q1 — System prompt: texto integral ou skeleton com seções?

Como você quer que o system prompt de `HRAgent` seja escrito? Isso afeta manutenção pós-workshop e a auditabilidade da política LGPD.

- A. **Texto integral inline** — Um único bloco em português, hardcoded como constante `_SYSTEM_PROMPT` no top-level de `agent/agent.py`. Fácil de reler, fácil de auditar (`grep salário agent/agent.py`), difícil de dividir em seções para tests.
- B. **Skeleton + seções** — Constante `_SYSTEM_PROMPT` construída de fragmentos (`_ROLE_SECTION`, `_LGPD_SECTION`, `_FALLBACK_SECTION`, `_TONE_SECTION`) concatenados. Mais modular, mais fácil de testar cada seção isoladamente, mas adiciona ~30 linhas de indireção.
- C. **Texto integral em arquivo separado** — `agent/system_prompt.md` carregado no boot com `Path(__file__).parent / "system_prompt.md"`. Facilita revisão por não-desenvolvedores (RH pode ler o prompt sem abrir Python), mas adiciona I/O no boot.
- X. Other (please specify)

[Answer]:B

---

## Q2 — Response length enforcement (2–4 frases)

`components.md § HRAgent behaviour` diz "responder em portugues em 2 a 4 frases, tom formal-neutro breve e direto". Como enforçar?

- A. **Só via system prompt** — Instrução literal no prompt ("Sua resposta deve ter entre 2 e 4 frases. Seja breve e direto."). Modelo geralmente respeita, mas não é determinístico. Sem hard-cap no código; se o modelo estourar, a resposta longa passa.
- B. **System prompt + max_tokens** — Instrução no prompt PLUS parâmetro `max_tokens=350` no `BedrockModel` (aprox. 2–4 frases em português). Hard-cap via SDK; se o modelo tentar mais, é truncado no meio da frase (feio mas seguro).
- C. **System prompt + validação pós-hoc** — Após o agente responder, contar sentenças no `response.response`; se >4, re-invocar o agente pedindo condensação. Adiciona custo extra ($ + latência) para caso raro.
- D. **Sem enforcement rígido** — Deixar o system prompt guiar; se o modelo produzir 6 frases, ok — o operador do workshop pode ajustar o prompt na hora se a demo mostrar problema.
- X. Other (please specify)

[Answer]:A

---

## Q3 — Trigger do fallback "não encontrei" (US1.4)

`stories.md § US1.4 AC1.4.1` exige que o agente responda "Não encontrei essa informação nos documentos. Sugiro contatar o time de RH." quando a KB não tem a resposta. Como o agente sabe que a KB "não tem"?

- A. **System prompt heurística** — O prompt instrui: "Se o `retrieve` retornar trechos vazios OU trechos que não respondem a pergunta, responda EXATAMENTE 'Não encontrei essa informação nos documentos. Sugiro contatar o time de RH.'". O modelo decide; o teste unitário verifica com stub que retorna `[]`.
- B. **Confidence threshold do `retrieve`** — Configurar `retrieve` com `numberOfResults=3` e `retrievalConfiguration.filter` (se aplicável); se o Strands tool retornar array vazio ou com score baixo, o agente cai no fallback. Determinístico, mas requer que o Strands SDK exponha esse controle (a documentar via web).
- C. **Second-round check** — O agente sempre tenta responder; se a resposta contiver a substring "não sei" ou "não tenho informação", re-emite como o fallback canônico. Menos elegante mas garante contrato de contains.
- X. Other (please specify)

[Answer]:A

---

## Q4 — Multi-turn memory: usar AgentCore Memory ou stateless por invocação?

`requirements.md § NFR10.1 (Should Have)` diz "historico de conversação dentro da mesma sessão Streamlit usando AgentCore Memory, se sobrar tempo apos os Must Have". Como você quer registrar isso em `functional-spec.md`?

- A. **Stateless por invocação (MVP)** — Cada call de `invoke_agent_runtime` recebe só o prompt atual. O AgentCore Runtime isola por microVM per session, mas o AGENTE não vê histórico de turnos anteriores. Aceita perder qualidade em perguntas de follow-up ("e para gestores?" após "quantos dias de férias?") em favor de simplicidade. Registrar NFR10 como Deferred no `traceability.json`.
- B. **AgentCore Memory (Should Have deferred to Bolt final)** — Documentar que `HRAgent` vai usar `AgentCore Memory` se sobrar tempo no dia 2. Adicionar seção "Migration path" em `functional-spec.md`. O MVP core (Must Haves) roda com A.
- C. **Frontend passa histórico no payload** — Alternativa: `chat-frontend` envia os últimos N turnos como parte do `context` no payload C1. Mudaria o C1 contract (breaking — não additive). Rejeitado por contrato de contract-summary.md § C1 (que já está travado).
- X. Other (please specify)

[Answer]:A

---

## Consolidated Summary Confirmation

Resumo consolidado das respostas antes de gerar `entities.md`, `rules.md`, `functional-spec.md` e `traceability.json` para o unit `hr-agent`:

- **Q1 = B — Skeleton + seções.** System prompt de `HRAgent` construído a partir de fragmentos concatenados (`_ROLE_SECTION`, `_LGPD_SECTION`, `_FALLBACK_SECTION`, `_TONE_SECTION`) → constante `_SYSTEM_PROMPT` em `agent/agent.py`. Trade-off aceito: ~30 linhas extras de indireção em troca de testabilidade por seção e auditabilidade da política LGPD.
- **Q2 = A — Só via system prompt.** Regra de comprimento (2–4 frases, tom breve) fica na `_TONE_SECTION` do prompt. Sem `max_tokens` como hard-cap; sem validação pós-hoc. Se o modelo estourar, a resposta longa passa — trade-off consciente (simplicidade > determinismo estrito).
- **Q3 = A — System prompt heurística para fallback.** A `_FALLBACK_SECTION` instrui o modelo a emitir literalmente "Não encontrei essa informação nos documentos. Sugiro contatar o time de RH." quando `retrieve` retornar trechos vazios ou irrelevantes. Verificação via teste unitário com stub retornando `[]`. Sem confidence threshold configurável no SDK; sem second-round check.
- **Q4 = A — Stateless por invocação (MVP).** Cada chamada de `invoke_agent_runtime` recebe apenas o prompt atual; o agente NÃO vê histórico de turnos anteriores. AgentCore Memory fica registrado como `Deferred` no `traceability.json` (NFR10.1). Perguntas de follow-up com pronomes ("e para gestores?") não são resolvidas — aceito como custo do MVP.

Efeito nos artefatos:

- `entities.md`: sem entities persistidas em U2 (agente stateless; sessão isolada pelo Runtime, não modelada como entity). YAML de source-of-truth listará zero entities e explicará por quê.
- `rules.md`: business rules `BRx.y` cobrindo as 7 stories (US1.1–1.5, US2.1, US3.1) + regras de compliance LGPD + tom/comprimento + fallback canônico.
- `functional-spec.md`: workflow de invocação single-turn, estrutura por seções do system prompt, contrato de contains do fallback, ausência intencional de state machine (stateless).
- `traceability.json`: 7 ACs cobertos com `OK`, apontando cada um para 1+ `BRx.y`. NFR10.1 marcado como `Deferred` no `reverse` array.

Escolha a opção que reflete sua decisão:

- Looks correct
- Request changes

[Answer]: Looks correct
