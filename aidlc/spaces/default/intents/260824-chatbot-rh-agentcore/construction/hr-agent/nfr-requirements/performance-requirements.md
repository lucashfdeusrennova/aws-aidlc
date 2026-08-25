**Collaborator:** aidlc-architect-agent

# Performance Requirements - Unit hr-agent

Requisitos de performance derivados de `requirements.md § NFR1.1` (<5s end-to-end)
e da decisão Q1=A (sem sub-budget interno). Companion de `security-requirements.md`,
`scalability-requirements.md`, `reliability-requirements.md`, `observability-requirements.md`
e `tech-stack-decisions.md` deste unit.

## Sources

- [rq] `requirements.md` § NFR1.1 (<5s), § FR6.3 (2 modelos comparados).
- [fs] `functional-spec.md` § Handler workflow (single invocation) — 7 steps sync.
- [rl] `rules.md` § BR5.1 (comprimento 2-4 frases via prompt, sem `max_tokens`), § BR6.1 (label -> ARN).
- [cs] `contract-summary.md` § C1 latency: NFR1.1 <5s, NFR6.1 1-3 sessões.
- [q1] Q1 = A — sem sub-budget, só total.
- [q5] Q5 = A — comparação qualitativa no smoke test.

## Requirements

### NFR1.1.1 — Latência end-to-end <5s

- **Metric — external `response_ms`**: tempo entre o `invoke_agent_runtime` enviado pelo `AgentInvoker` (U1) e o retorno bem-sucedido do response C1. Inclui overhead de rede + alocação de microVM pelo Runtime + processamento interno do handler + rede de volta.
- **Target**: <5s.
- **Percentile**: sem alvo formal de percentil no MVP (workshop de 2 dias com 1-3 sessões concorrentes torna p95/p99 estatisticamente frágeis com N pequeno). O contrato é "cada uma das 3-5 perguntas canônicas do smoke test retorna em <5s".
- **Load condition**: até 3 sessões concorrentes (NFR6.1).
- **Measurement method**: `scripts/smoke.py` mede `time.perf_counter()` antes/depois de `ask_agent(...)` e imprime o delta por pergunta — esse é o **`response_ms` externo**. Distinto do **`response_ms` interno** que NFR4.1.3 registra no log estruturado do handler (mede apenas o processamento dentro da microVM, sem rede nem overhead do Runtime). Os dois números não precisam bater; a diferença entre eles quantifica o overhead do Runtime. Sem instrumentação CloudWatch adicional (Q1=A rejeita a opção C).
- **Enforcement**: bloqueante local — se qualquer pergunta canônica passar de 5s no smoke test, a demo é considerada não-pronta e o operador ajusta (modelo, temperatura, prompt) antes de continuar.

### NFR1.1.2 — Sem sub-budget interno (documentado)

- **Decisão**: NÃO fixar sub-metas separadas para `retrieve_ms` vs `model_ms` vs overhead do Runtime. O total <5s é o único alvo (Q1=A).
- **Consequência**: se o total estourar, investigação é caso a caso (adicionar `logging.getLogger(__name__).info(f"retrieve took {ms}ms")` ad-hoc se necessário, sem instrumentação permanente).
- **Rationale**: MVP de 2 dias com 3-5 perguntas canônicas não justifica overhead de instrumentação CloudWatch por etapa. Se o time quiser após o workshop, adicionar métricas emit-once via boto3 CloudWatch client dentro do handler é trivial.

### NFR1.1.3 — Tom breve como amplificador de performance percebida

- **Metric**: comprimento da resposta em número de frases.
- **Target**: 2-4 frases por resposta (BR5.1).
- **Enforcement**: soft — apenas via `_TONE_SECTION` do system prompt (Q2=A do stage anterior). Sem `max_tokens` como hard-cap; sem validação pós-hoc.
- **Rationale**: respostas curtas percebidas como mais rápidas mesmo quando o `response_ms` seria o mesmo. O tom breve também reduz custo de token (~2x-3x versus respostas de 8-10 frases). Como observação: se um modelo consistentemente produzir respostas de 6+ frases apesar do prompt, o operador do workshop deve ajustar prompt na hora — não é bug de performance.

### NFR1.1.4 — Comparação inter-modelo (latência)

- **Metric**: latência aproximada e qualidade percebida.
- **Target**: os 2 modelos ativos (Claude Haiku 4.5, Amazon Nova Pro) devem responder em <5s para cada uma das perguntas canônicas.
- **Measurement**: `scripts/smoke.py` roda cada pergunta contra cada modelo (via `context.model_id` no payload C1); operador anota em bloco de comentário no script os deltas observados e nota subjetiva de qualidade (Q5=A).
- **Sem NFR quantitativo diferenciado**: NÃO fixar "Claude Haiku <2s p95" ou "Nova Pro <3.5s p95" separadamente (Q5=B rejeitado). O teto compartilhado <5s de NFR1.1 basta para o MVP.

## Validation

- **`scripts/smoke.py`** com bloco de perguntas canônicas + medição de tempo por pergunta.
- Sem load test formal no MVP (NFR6.1 limita a 1-3 sessões; carga sintética não faz sentido para essa escala).
- Sem targets de p95/p99 formais (baixo N no smoke test não sustenta estatística).

## Anti-Requirements (excluídos explicitamente)

- "Latência baixa" sem número — substituído por NFR1.1.1 (<5s).
- Sub-budget individual (retrieve X, modelo Y) — rejeitado por Q1=A; investigação ad-hoc se necessário.
- Load testing sintético — fora do escopo MVP (NFR6.1).
- SLO/SLA formal com percentil — fora do escopo MVP (baixo N).

## Assumptions & Open Questions

None.



## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-08-25T16:52:39Z
**Iteration:** 2 (final under review cap `reviewer_max_iterations: 2`)
**Pass class:** adversarial

### Status dos findings da iteracao 1

| # | Sev iter-1 | Status iter-2 | Evidencia |
|---|---|---|---|
| F1 | Critical | Resolved | `NFR7.1.1` aparece somente em `reliability-requirements.md` como "Reprodutibilidade via deps pinadas". `scalability-requirements.md` renomeou statelessness para `NFR10.1.1` (deriva de `NFR10.1 Deferred`). Grep `^### NFR7\.1\.1` retorna 1 hit (reliability). Sem colisao. |
| F2 | Critical | Resolved | `NFR5.1.1` aparece somente em `security-requirements.md` como "Execution role least-privilege". `performance-requirements.md` renomeou tom breve para `NFR1.1.3`. Grep `^### NFR5\.1\.1` retorna 1 hit (security). Sem colisao. |
| F3 | Critical | Resolved | `NFR6.1.1` aparece somente em `scalability-requirements.md` como "Suportar 1-3 sessoes simultaneas". `performance-requirements.md` renomeou comparacao inter-modelo para `NFR1.1.4`. Grep `^### NFR6\.1\.1` retorna 1 hit (scalability). Sem colisao. |
| F4 | Major | Resolved | `observability-requirements.md § Sources` cita `[rq] requirements.md`, `[fs] functional-spec.md`, `[rl] rules.md` (NOVO), `[cs] contract-summary.md` (NOVO), `[pj] project.md`, mais `[q2]` e `[q5]`. Cobertura dos 4 consumes obrigatorios do stage frontmatter (`requirements`, `functional-spec`, `rules`, `contract-summary`) verificada. |
| F5 | Major | Resolved | `tech-stack-decisions.md § Sources` cita `[pj]`, `[tp]`, `[rl] rules.md` (NOVO), `[cs] contract-summary.md`, `[rq] requirements.md`, `[fs] functional-spec.md`. `rules.md` referenciado explicitamente para BR6.1/6.2/6.4/7.1. |
| F6 | Major | Resolved | Grep `NFR-(SEC\|REL\|SCALE\|OBS\|PERF)-\d+` retorna 0 hits nos 5 arquivos de requisitos e em `traceability.json`. Unicos hits sao no arquivo historico `nfr-requirements-questions.md § Consolidated Summary` (rotulos originais das opcoes B/C - nao sao IDs de artefato). `traceability.json` foi reescrito: chaves de topo sao `stage, unit, upstream_ids, coverage` - ZERO campo `reverse`. Todas as 10 entradas de `coverage[]` visam inception NFR IDs (`NFR1..NFR10`); os `target` sao IDs derivativos `NFRx.y.z` (ou prosa para N/A). |
| F7 | Major | Resolved | `NFR7` em `reliability-requirements.md` contem apenas `NFR7.1.1` (Reprodutibilidade / deps pinadas) e `NFR7.2.1` (CDK synth). Statelessness como facilitador de escala moveu para `NFR10.1.1` (scalability, deriva explicita de `NFR10.1 Deferred`) e statelessness como eliminador de bugs em `NFR10.1.2` (reliability, mesma deriva). Semantica coerente com `requirements.md § NFR7.1-7.2` (reprodutibilidade) e `§ NFR10.1` (memory Deferred). |
| Minor-1 (`response_ms` external vs internal) | Minor | Resolved | `NFR1.1.1` distingue explicitamente `response_ms` external (medido por `scripts/smoke.py` em `time.perf_counter()` ao redor de `ask_agent(...)`) do `response_ms` internal (registrado por `NFR4.1.3` no log estruturado dentro da microVM). "Os dois numeros nao precisam bater; a diferenca entre eles quantifica o overhead do Runtime." |
| Minor-2 (STRIDE.S -> C3) | Minor | Resolved | Tabela STRIDE em `security-requirements.md § Threat Model` categoria S referencia "U3 owns C2/C3" - `C3` (env vars + IAM policy skeleton) e a fonte correta da execution role least-privilege usada na mitigacao; `contract-summary.md § C3` valida. |
| Minor-3 (INFERENCE_PROFILE_ARN divergence acknowledged) | Minor | Resolved | `tech-stack-decisions.md § Environment variables (from contract-summary § C3)` documenta explicitamente: "false (era optional em C3; hr-agent trata como obrigatoria)" para os 2 ARNs, e adiciona "Note (efeito em C3)" apontando que atualizacao formal de `contract-summary § C3` e tarefa cross-unit downstream. `BR6.3` e `BR6.4` em `rules.md` implementam a fail-fast policy que sustenta essa tightening. |

### Verificacoes novas (iter-2)

| # | Escopo | Metodo | Resultado |
|---|---|---|---|
| N1 | Sem duplicatas de `NFRx.y.z` entre os 5 arquivos | Grep `^### NFR\d+\.\d+\.\d+` + set de IDs em bun script | 34 IDs unicos, zero colisoes. Distribuicao: performance 4, security 9, scalability 5, reliability 8, observability 8. |
| N2 | Zero legado `NFR-{TAG}-N` | `grep_search "NFR-(SEC\|REL\|SCALE\|OBS\|PERF)-\d+"` no diretorio `nfr-requirements/` | Zero hits nos 5 arquivos de requisitos e em `traceability.json`. Unicos hits sao no arquivo historico de perguntas (nao e artefato). |
| N3 | `traceability.json` parseavel e coerente | `bun -e "require(...)"` + inspecao de chaves | Parse OK. `stage: nfr-requirements`, `unit: hr-agent`, `|upstream_ids|=10`, `|coverage|=10`, `has_reverse=false`, `statuses={OK, N/A}`. Zero entradas `Deferred`, `Pending`, `TBD`. |
| N4 | Cada `target` de coverage OK aponta para `### NFRx.y.z` real | Set-membership programatica em bun (parse dos 5 arquivos + split de `target`) | 7/7 NFR1 targets OK, 7/7 NFR4, 6/6 NFR5, 4/4 NFR6, 2/2 NFR7, 6/6 NFR9, 2/2 NFR10 = 34/34 IDs resolvem. NFR2/NFR3/NFR8 sao N/A com prosa justificativa (nao sao IDs). |
| N5 | Q1-Q5 = A materializados | Cross-check das 5 respostas com os artefatos | Q1=A ("sem sub-budget") em `NFR1.1.2`; Q2=A ("log INFO minimo estruturado sem payload") em `NFR4.1.3` + `NFR4.1.4`; Q3=A ("delegar >3 sessoes ao Runtime") em `NFR6.1.2`; Q4=A ("Guardrails Bedrock deferred") em `NFR4.3.1`; Q5=A ("comparacao qualitativa no smoke test") em `NFR1.1.4` + `NFR1.1.7`. Nenhuma decisao invertida. |
| N6 | Consistencia com `contract-summary § C1` (shape) | Leitura dos artefatos vs `contract-summary.md § C1 request/response schema` | C1 request: `prompt` + `context.model_id` - `NFR6.2.2` ("troca de modelo via `context.model_id` no payload") preserva o shape; C1 response: `response, model_id, session_id` - `NFR4.1.3` loga `model_id` e `runtimeSessionId` (o UUID do envelope AWS API), coerente com `BR6.2`/`BR7.2`. Contrato C1 preservado. |
| N7 | Consistencia com `contract-summary § C3` (env vars) | Leitura da tabela `env_vars_required_by_frontend` e da `IAM policy skeleton` | `NFR5.1.1` reproduz o skeleton IAM (`bedrock:InvokeModel*` nos 2 ARNs, `bedrock:Retrieve` na KB especifica, `logs:*` no grupo `/aws/bedrock-agentcore/*`). `NFR5.2.1` reforca a proibicao de `Resource: "*"`. Divergencia optional-vs-required em `INFERENCE_PROFILE_ARN_*` esta declarada em `tech-stack-decisions.md` (Minor-3 acima) - contradicao controlada, nao silenciada. |
| N8 | Consistencia com `rules.md` (BR chain) | Verificacao dos IDs de regra citados | Todas as BRs citadas nos NFRs (`BR2.3`, `BR3.1`, `BR4.1-4.4`, `BR5.1`, `BR6.1-6.4`, `BR7.1-7.2`) existem no bloco YAML `source of truth` de `rules.md`. Nenhuma BR-ID pendurada. |
| N9 | Escopo cross-unit respeitado | Auditoria dos artefatos | Toda referencia a U1 (`AgentInvoker`, chat-frontend) ou U3 (infra, CDK, IAM roles) e feita via `contract-summary.md § C1/C2/C3` ou via `project.md § Mandated/Forbidden` - nunca por leitura direta de `construction/chat-frontend/` ou `construction/infra/`. Nenhum sibling unit path lido nesta review. |
| N10 | Anti-regressao vs iter-1 | Re-execucao dos 3 checks Critical + 4 Major iter-1 nos artefatos iter-2 | Todos os PASSes de iter-1 (se houvesse - iter-1 falhou com 3 Critical + 4 Major) foram convertidos em PASSes iter-2. Nenhum novo defeito estrutural introduzido pelas correcoes. |

### Suggestions (non-blocking)

- `NFR1.1.5` (Sem instrumentacao de sub-etapas) vive em `observability-requirements.md` mas carrega prefixo `NFR1.x` (raiz "performance latency"). Coerente semanticamente (rejeita observabilidade extra que apoiaria a raiz latency), mas um leitor procurando "tudo que e NFR1" so olharia `performance-requirements.md`. Considerar em iteracoes futuras: (a) mover para `performance-requirements.md`, ou (b) manter em observability e adicionar cross-ref explicito em `performance-requirements.md § Requirements`. Nao bloqueia porque o NFR e localizado por `traceability.json § coverage[NFR1].target` que enumera todos os 7 IDs.
- `NFR1.1.6` (Sem X-Ray) e `NFR9.1.6` (Sem alerting) sao "anti-requisitos" formatados como requisitos numerados. Alternativa que aparece em `performance-requirements.md § Anti-Requirements` e em `security-requirements.md § Anti-Requirements` e listar em bullet list sem numeracao NFR. Os dois estilos convivem hoje - ambos rastreados pelo traceability, so o codigo autoral fica um pouco misto. Nao acao agora.
- Minor-3 (divergencia optional-vs-required em `INFERENCE_PROFILE_ARN_*`) esta reconhecida em `tech-stack-decisions.md`, mas o "ticket" cross-unit para atualizar `contract-summary § C3` vive so como frase ("tarefa cross-unit downstream ao proximo revisao da Inception"). Considerar registrar isso como item explicito em `<record>/inception/contract-design/` para a proxima passada, evitando que fique orfao. Fora do escopo deste stage.
- `tech-stack-decisions.md § Rejected stacks` inclui "Model ID `us.*` direto" e "client `bedrock-agent-runtime`" na tabela - excelente para prevenir re-decisao, mas esses dois nao sao "stacks" no sentido convencional (sao API misuse patterns). Categorizacao secundaria; nao impacta traceability.

### Summary

Todos os 7 findings de iteracao 1 (3 Critical + 4 Major) e os 3 Minors declarados no dispatch estao resolvidos com evidencia mecanicamente verificavel: (i) 34 IDs `NFRx.y.z` unicos entre os 5 arquivos, sem colisao; (ii) zero ocorrencias do legado `NFR-{TAG}-N` nos artefatos; (iii) `traceability.json` valido, 10 upstream cobertos, statuses `{OK, N/A}`, todos os 34 targets `OK` resolvem para secoes reais; (iv) `observability-requirements.md § Sources` e `tech-stack-decisions.md § Sources` completos; (v) semantica NFR7 restaurada (reprodutibilidade) com statelessness migrada para NFR10.x. Consistencia com `contract-summary § C1/C3` e `rules.md § BR1-BR7` verificada; escopo cross-unit respeitado. Q1-Q5=A materializados. Nenhum defeito novo introduzido pelas correcoes de iter-1. A especificacao NFR atende ao criterio "um dev consegue implementar sem consultar o arquiteto" e esta pronta para fluir para `nfr-design`.

**Verdict:** READY
