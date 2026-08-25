**Collaborator:** aidlc-architect-agent

# NFR Design Questions - Unit hr-agent

Este stage roda em fase de Construction: a maior parte do design ja
esta travada por `nfr-requirements/` (5 arquivos + tech-stack-decisions +
traceability.json) e por `project.md § Mandated / Forbidden`. As perguntas
abaixo cobrem os poucos pontos genuinamente abertos que impactam artefato
de design (nao codigo).

Depth: **Standard** (heranca de `aidlc-state.md`). Test Strategy: Standard.

## Q1 — Decomposicao logica do modulo `agent/agent.py`

O `functional-spec § System prompt architecture` fixa que existem 4
constantes de secao (`_ROLE_SECTION`, `_LGPD_SECTION`, `_FALLBACK_SECTION`,
`_TONE_SECTION`) mais o handler workflow (7 steps) mais o dicionario
`_MODEL_LABEL_TO_ENVVAR`. A pergunta e sobre a granularidade fisica:

- **A.** Modulo unico plano: `agent/agent.py` contem TUDO (secoes do prompt,
  dicionario label->envvar, handler, agente Strands). Zero submodulos.
  Alinha com MVP mais enxuto e com `team.md § Code Style Fronteiras de camada`
  ("agent/ e auto-contido").
- **B.** 2 arquivos: `agent/agent.py` (handler + logging + montagem do Agent)
  e `agent/prompts.py` (as 4 secoes + `_SYSTEM_PROMPT` concatenado).
  Separa o texto do prompt (que muda com frequencia) da fiacao runtime.
- **C.** 3+ arquivos: `agent/agent.py`, `agent/prompts.py`, `agent/logging_.py`
  (helper de log estruturado NFR4.1.3). Maior separacao de concerns; mais
  arquivos para 2 dias de workshop.
- **X.** Other (please specify)

[Answer]:A

## Q2 — Classificacao do campo `outcome` no log INFO estruturado (NFR4.1.3)

O log INFO por invocacao carrega o campo `outcome` com enum
`{success, fallback, refusal, error}`. Como o handler decide qual valor
escrever?

- **A.** Regex sobre o `response` do agente antes de emitir o log:
  se resposta contem "nao encontrei" + "rh" -> `fallback`;
  se contem "nao posso" + ("informacoes pessoais" | "compartilhar") -> `refusal`;
  caso contrario -> `success`. Simples, sem mudanca na chamada do Agent. Risco:
  falso positivo se o modelo variar a linguagem (assumivel no MVP).
- **B.** Trocar sinal explicito: o handler NAO classifica; loga sempre
  `outcome: "handled"` para respostas bem-sucedidas e `outcome: "error"`
  para excecoes. Zero heuristica; menos rico em auditoria, mas 100% deterministico.
- **C.** Retornar tuple do agente (response, classification_hint) via
  helper que inspeciona a decisao do LLM. Requer wrapper do `agent(prompt)`;
  maior fidelidade mas ceremonia alta para MVP.
- **X.** Other (please specify)

[Answer]:A

## Q3 — Shape do logger estruturado (NFR4.1.3 + NFR9.1.5)

Como emitir o log JSON estruturado?

- **A.** Helper `log_event(logger, level, **fields)` em `agent/agent.py`
  (ou em `agent/logging_.py` conforme Q1). Chama internamente
  `logger.log(level, json.dumps(fields))`. Testavel (mock do logger),
  reutilizavel entre log INFO e log ERROR.
- **B.** Inline em cada ponto de emissao: `logger.info(json.dumps({"ts": ...,
  "outcome": ...}))`. Sem helper. 2 chamadas totais (INFO no happy path,
  ERROR no except); pouca duplicacao.
- **X.** Other (please specify)

[Answer]:A

## Consolidated Summary Confirmation

<!-- filled after all Q answered; do not touch until then -->

- Looks correct
- Request changes

[Answer]: Looks correct
