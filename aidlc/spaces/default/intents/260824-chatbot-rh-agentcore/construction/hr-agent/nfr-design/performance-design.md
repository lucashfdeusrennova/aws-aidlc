**Collaborator:** aidlc-architect-agent

# Performance Design - Unit hr-agent

Desenhos de performance para atender os requisitos travados em
`performance-requirements.md` (NFR1.1.1..NFR1.1.4) dentro do orcamento
de 2 dias do workshop. Sem instrumentacao adicional alem do `scripts/smoke.py`
externo e do log INFO estruturado interno (Q1=A do stage anterior).

## Sources

- [pr] `performance-requirements.md` NFR1.1.1..NFR1.1.4 — target <5s end-to-end,
  sem sub-budget interno, tom breve como amplificador percebido, comparacao
  inter-modelo qualitativa.
- [ts] `tech-stack-decisions.md` § Locked stack — Strands + Bedrock via
  inference profile ARN, boto3 top-level (single client per module), region
  fixa `us-east-1`.
- [fs] `functional-spec.md` § Handler workflow (7 steps sync), § Deployment
  shape (microVM per session).
- [cs] `contract-summary.md` § C1 SLA (NFR1.1 <5s), C1 request/response.
- [sc] `scalability-requirements.md` NFR6.2.2 (troca de modelo nao afeta
  curva de escala).
- [obs] `observability-requirements.md` NFR1.1.5 (sem instrumentacao de
  sub-etapas), NFR4.1.3 (log INFO estruturado com `response_ms` interno).
- [q1] Design Q1=A — modulo unico plano (afeta reuso de cliente boto3).

## Design Decisions

### PD-1 — Reuse de cliente Strands/Bedrock em nivel de modulo (client-per-module pattern)

**Requirement**: NFR1.1.1 (<5s end-to-end).

**Design**: instanciar `BedrockModel` UMA VEZ por invocacao dentro do handler
`invoke(payload)` — a instancia carrega o `inference_profile_arn` resolvido
por `context.model_id`, portanto NAO pode ser cacheada module-level (o modelo
pode trocar entre invocacoes por US4.1). PORÉM, o boto3 client subjacente
(`bedrock-runtime`) que o Strands SDK usa e criado top-level pelo SDK, garantindo
reuso de connection pool entre invocacoes na MESMA microVM.

**Rationale**: fixa a origem do overhead que o `functional-spec` deixou solto
— reuso de connection pool e critico em cold start; a instancia de
`BedrockModel` e barata (wrapper Strands), o custo real esta no HTTP client
subjacente. Um cliente por invocacao anularia o pool e adicionaria dezenas
de ms.

**Implementation shape** (nao codigo final):

```python
# top-level do agent/agent.py — importa o SDK, deixa Strands gerenciar o boto3 client interno
from strands import Agent
from strands.models import BedrockModel
from strands_tools import retrieve

def invoke(payload: dict) -> dict:
    label = payload["context"]["model_id"]
    arn = _MODEL_LABEL_TO_ENVVAR[label]  # KeyError propaga (BR6.3)
    arn_value = os.environ[arn]           # KeyError propaga
    model = BedrockModel(model_id=arn_value)
    agent = Agent(model=model, system_prompt=_SYSTEM_PROMPT, tools=[retrieve])
    response = agent(payload["prompt"])
    ...
```

**Trade-off**: se o time futuramente adicionar caching per-model_id via LRU
(`functools.lru_cache` sobre `BedrockModel` factory), NFR6.2.2 continua
satisfeito e cold-start subsequente cai. Nao no MVP — inutil para 1-3 sessoes.

### PD-2 — Sem cache de respostas nem de embeddings

**Requirement**: NFR1.1.2 (sem sub-budget interno; se estourar, investigar
caso a caso), NFR10.1.1 (statelessness como decisao locked).

**Design**: NAO implementar response cache (ex.: Redis, memcache, dict em
memoria) nem cache de embeddings do `retrieve`. Cada invocacao consulta a
KB do zero.

**Rationale**: cache seria estado compartilhado, violando BR7.1
(statelessness). E a probabilidade de dois usuarios fazerem a mesma pergunta
literal em janela de 2 dias e desprezivel — cache miss dominaria.

**Trade-off aceito**: `retrieve` roda em toda invocacao (~200-500ms
tipicamente). Nao ha caminho mais rapido dentro das restricoes.

### PD-3 — Prompt as latency amplifier: tom breve via `_TONE_SECTION`

**Requirement**: NFR1.1.3 (2-4 frases por resposta como amplificador de
performance percebida).

**Design**: `_TONE_SECTION` no system prompt (functional-spec § System prompt
architecture) instrui o modelo a limitar a resposta a 2-4 frases em portugues
formal-neutro. **Sem** `max_tokens` como hard-cap (Q2=A do functional-design,
BR5.1). **Sem** validacao pos-hoc do numero de frases.

**Rationale**: hard-cap por token quebra respostas mid-sentence em pior UX;
soft-cap via prompt e o padrao aceito para Bedrock. Amplificacao percebida:
resposta de 3 frases lida em 2s parece "mais rapida" que resposta de 8 frases
em 3s.

**Migration path**: se o operador do workshop observar que o modelo produz
consistentemente >5 frases, ajustar o texto de `_TONE_SECTION` no dia da
demo. Codigo nao muda.

### PD-4 — Sem instrumentacao de sub-etapas (`retrieve_ms`, `model_ms`)

**Requirement**: NFR1.1.2 + NFR1.1.5 (sem instrumentacao adicional).

**Design**: o handler mede APENAS `response_ms` total (interno a microVM) via
`time.perf_counter()` ao redor de `agent(prompt)`. NAO decompoe em
`retrieve_ms` + `model_ms`. O log INFO estruturado (NFR4.1.3) carrega apenas
o total.

**Rationale**: Q1=A rejeita opcao C (instrumentacao CloudWatch Metrics).
Se estourar 5s, o operador adiciona logs ad-hoc em `agent/agent.py` para
debug local — sem commitar.

**Implementation shape**:

```python
import time
t0 = time.perf_counter()
response = agent(prompt)
elapsed_ms = int((time.perf_counter() - t0) * 1000)
log_event(logger, "INFO", response_ms=elapsed_ms, outcome=_classify(response), ...)
```

### PD-5 — `retrieve` com defaults do Strands SDK (sem `numberOfResults` custom, sem filtros)

**Requirement**: NFR1.1.1, funcional AC1.4.1 (fallback baseado em heuristica
do prompt).

**Design**: a tool `retrieve` do `strands_tools` e adicionada ao agente sem
customizacao (nao passar `numberOfResults`, nao passar `filter`, nao passar
`overrideSearchType`). O SDK usa defaults do Bedrock Knowledge Bases (top-5
chunks por default, semantic search).

**Rationale**: Q3=A do functional-design ja rejeitou tuning do retrieve;
mudar defaults adiciona superficie de teste e nao acelera nada perceptivel
em uma KB de 5 documentos. Menos chunks poderia acelerar mas quebraria
recall.

### PD-6 — Sem streaming de resposta

**Requirement**: NFR1.1.1 (target e response completo, nao first-token).

**Design**: `invoke_agent_runtime` chamado em modo single-shot (ADR-005 de
`functional-spec § Non-goals`). Resposta chega em UMA payload; sem chunks
SSE nem `bedrock-runtime.invoke_model_with_response_stream`.

**Rationale**: 2-4 frases nao justifica UX de streaming; codigo do agente e
do frontend fica mais simples; contrato C1 preserva shape unico.

**Migration path**: se time quiser TTFT (time-to-first-token) reduzido
pos-demo, C1 mudaria para SSE — reabrir ADR-005.

### PD-7 — Latency budget breakdown esperado (informativo)

Estimativa qualitativa (nao target formal):

| Etapa | Contribuicao esperada | Observacao |
|-------|-----------------------|------------|
| Rede U1 -> AgentCore Runtime | ~50-100ms | dependende da geografia do participante |
| Cold-start microVM (primeiro invoke) | ~500-2000ms | Runtime gerenciado |
| Warm invoke | ~0ms | subsequentes na mesma sessao |
| `retrieve` (KB semantic search) | ~200-500ms | 5 docs, top-5 chunks |
| Model inference | ~1000-3000ms | varia por modelo/prompt |
| Rede Runtime -> U1 | ~50-100ms | idem |
| **Total esperado** | **~2-5s** | dentro de NFR1.1.1 |

Sem obrigacao de reproducibilidade dos numeros acima; sao apenas para
o operador ter expectativa razoavel do que "normal" parece.

### PD-8 — Comparacao inter-modelo: `scripts/smoke.py` como oraculo (Q5=A)

**Requirement**: NFR1.1.4 (comparacao qualitativa entre Claude Haiku 4.5 e
Amazon Nova Pro).

**Design**: `scripts/smoke.py` roda 3-5 perguntas canonicas contra cada modelo
(via `context.model_id` no payload). Operador anota bloco de comentario com
delta observado + nota subjetiva. Nao ha CSV, nao ha dashboard, nao ha
benchmark statistico.

**Rationale**: N pequeno + 2 dias tornam qualquer analise estatistica ruido.

## Anti-Patterns Rejected

- **Retry customizado com backoff exponencial** — vetor de amplificacao de
  DoS (NFR5.1.2); boto3 default (~3 tentativas) e suficiente.
- **Cache Redis/memcache** — viola statelessness (NFR10.1.1).
- **CloudWatch Metrics `put_metric_data`** — rejeitado por Q1=A.
- **Async processing / queue** — quebra contrato sincrono C1; nao aplicavel.
- **CDN para respostas** — respostas sao dinamicas e session-specific;
  ininteligivel para chatbot.

## Assumptions & Open Questions

None.
