**Collaborator:** aidlc-architect-agent

# Performance Requirements — chat-frontend (U1)

Requisitos de performance derivados de `requirements.md` NFR1 e NFR6,
especializados para o unit `chat-frontend` (kind `ui`, Streamlit local).
Cada requisito herda o ID do NFR de inception e recebe um sufixo `.<n>`
específico deste stage.

## Sources

- [fs] `functional-spec.md` — chat-frontend, § "State Machine" (rerun Streamlit síncrono durante `Sending`) e § "Workflows por AC" (AC1.6, AC1.7).
- [rq] `requirements.md` — NFR1.1 (≤5 s), NFR6.1 (1–3 sessões simultâneas), NFR6.2 (sem alvo formal além de 3).
- [cs] `contract-summary.md` — C1 (payload síncrono via `invoke_agent_runtime`, sem streaming), § "SLA / NFR".
- [rules] `aidlc/spaces/default/memory/{org,team,project}.md` — team.md § Testing Posture (smoke test como cerimônia de latência), § Deployment (Streamlit local, sem CDN).

## Requirements

### NFR1.1.1 — Orçamento de latência do frontend

**Descrição**: O tempo consumido pelo unit `chat-frontend` entre o
submit do `st.chat_input` e a chamada `bedrock-agentcore.InvokeAgentRuntime`,
somado ao tempo entre o retorno da resposta e a renderização da bolha
`assistant`, DEVE ser ≤ **1 segundo** em condições normais (notebook do
participante, rede sandbox estável). Isso reserva **≥ 4 s** do orçamento
total de `NFR1.1` (5 s) para o backend (AgentCore Runtime + Bedrock
inference + KB retrieve). [rq NFR1.1][cs C1 SLA]

**Componentes contabilizados no orçamento frontend**:

- Serialização do payload JSON (`json.dumps({...}).encode()`).
- Chamada síncrona `invoke_agent_runtime` — apenas overhead de wire boto3
  (excluído o tempo do backend, que é medido em U2).
- Deserialização da response e leitura de `response["response"]`.
- Renderização do `st.chat_message("assistant")` com o texto plano.

**Componentes fora do orçamento** (contabilizados no backend, U2):

- Tempo de execução do agente Strands.
- Latência do modelo Bedrock (Claude Haiku 4.5 ou Nova Pro).
- Retrieve na Knowledge Base.

**Medição**: `scripts/smoke.py` (definido em `team.md § Testing Posture`)
DEVE logar 4 timestamps por request canônica:

- `t_submit` — imediatamente após capturar o prompt do `st.chat_input`.
- `t_agent_call` — imediatamente antes de chamar
  `agentcore_client.invoke_agent_runtime(...)`.
- `t_agent_returned` — logo após `response = agentcore_client.invoke_agent_runtime(...)`
  ter retornado e `payload_bytes = response["payload"].read()` ter
  materializado o corpo (o momento em que o wire boto3 termina, ANTES
  de qualquer parse ou render).
- `t_response_rendered` — após `st.chat_message("assistant").write(...)`
  ter renderizado o texto.

**Asserção testável** que ISOLA frontend do backend:

```
frontend_elapsed = (t_agent_call - t_submit) + (t_response_rendered - t_agent_returned)
backend_elapsed  = t_agent_returned - t_agent_call
```

- Assertion primária deste NFR: `frontend_elapsed <= 1 s` como média de 5
  execuções consecutivas.
- O `backend_elapsed` é observação, NÃO assertion neste stage — a
  cobertura de backend mora em U2 (`hr-agent`).

Essa decomposição sobrevive a um dia com backend lento: se `NFR1.1`
global falhar mas `frontend_elapsed <= 1 s`, apontamos o dedo com dados
para U2, não para U1. Sem CloudWatch metrics dedicadas (fora do escopo
para o MVP local).

**Rationale**: 1 s é o teto observado empiricamente para um Streamlit
local invocando boto3 em `us-east-1` a partir de um notebook comum;
valores acima disso indicam problema de rede do participante ou payload
mal-formado, não do agente. Empurra a pressão de performance para o
backend, onde ela é auditável via CloudWatch. [Q1=B]

**Testabilidade**: `frontend_elapsed` (definido acima) sobre média de 5
execuções contra uma pergunta canônica; falha se média > 1 s. O teste NÃO
depende de o backend estar rápido — o cálculo subtrai explicitamente o
intervalo entre `t_agent_call` e `t_agent_returned`.

### NFR6.1.1 — Modelo de deploy 1-participante/1-notebook

**Descrição**: Cada participante roda uma instância própria de
`streamlit run frontend/app.py` no seu notebook (porta default `8501`
por host); os `st.session_state` são isolados por aba do navegador
dentro do mesmo processo, e cada notebook é um host distinto. Portanto
1–3 sessões simultâneas equivalem a 1–3 notebooks. [rq NFR6.1][tp
§ Deployment]

**Rationale**: `team.md § Deployment` já fixa "Frontend: `streamlit run
frontend/app.py` no notebook de cada participante" — não há
co-location em uma única máquina, portanto nenhuma configuração de
porta múltipla é necessária. Streamlit atende múltiplas sessões
concorrentes com estado isolado por-sessão no mesmo processo (websocket
por aba), mas essa capacidade é acidental para o MVP: o design é 1
notebook = 1 sessão = 1 processo.

**Escopo**: fora do MVP suportar > 3 notebooks simultâneos (`NFR6.2`).

**Testabilidade**: verificação manual durante o dia da demo — 3
participantes rodam simultaneamente `streamlit run frontend/app.py` em
notebooks distintos, cada um mantém histórico próprio, e o
`session_id` gerado por cada notebook é distinto (auditável via log em
stdout se necessário).

## Non-Requirements (Anti-Requirements)

- **Sem SLO formal de latência 24/7**. Alvo aplica somente durante a
  janela de demo (2 dias); a métrica não é rastreada continuamente.
- **Sem targets de throughput** (RPS). Streamlit local não é servidor
  multi-tenant; a discussão é por-sessão. [rq NFR6.2]
- **Sem cache local** de respostas do agente no frontend. Cada `submit`
  vira uma chamada nova; cache adicionaria complexidade e conflitaria
  com FR4.5 ("Limpar conversa" gera novo `session_id`). [fs § AC1.9.2]
- **Sem preloading** do dropdown de modelo. `st.session_state.model_id`
  é inicializado no primeiro rerun; usuário não percebe custo cognitivo.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->

## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Date:** 2026-08-25T11:22:29Z
**Iteration:** 3
**Recovery:** stale-receipt
**Review class:** adversarial

### Status dos findings da iter-2

| # | Sev iter-2 | Status iter-3 | Evidência |
|---|------------|---------------|-----------|
| 1 | Major | RESOLVIDO | `NFR1.1.1` agora define quatro timestamps: `t_submit`, `t_agent_call`, `t_agent_returned` (logo após `response["payload"].read()` — endpoint do wire boto3, ANTES de qualquer parse/render), `t_response_rendered`. A asserção primária é `frontend_elapsed = (t_agent_call − t_submit) + (t_response_rendered − t_agent_returned) <= 1 s`; `backend_elapsed = t_agent_returned − t_agent_call` é observação, não assertion. O intervalo backend (`t_agent_call → t_agent_returned`) é subtraído explicitamente, então a métrica frontend não depende de o backend estar rápido. Isolamento matematicamente correto entre budget frontend e wire+backend. |
| 2 | Major | RESOLVIDO | `NFR6.1.1` reescrito para "modelo 1-participante/1-notebook": cada participante roda `streamlit run frontend/app.py` no seu próprio notebook, `session_state` isolado por aba dentro do mesmo processo, cada notebook é um host distinto, portanto 1–3 sessões simultâneas = 1–3 notebooks. Nenhuma orientação de portas 8501/8502/8503 restante — a menção a `8501` é como "porta default por host", coerente com um-processo-por-host. Reconhece explicitamente que Streamlit atende múltiplas sessões concorrentes por processo via websocket-por-aba, mas classifica essa capacidade como acidental ao MVP. Alinhado com `team.md § Deployment` ("Frontend: streamlit run no notebook de cada participante"). |
| 3 | Major | RESOLVIDO | `traceability.json § reverse` agora é `[]`. `coverage[]` mantém NFR1..NFR10, com NFR4 → {NFR4.1.1, NFR4.3.1, NFR4.5.1} (OK) e NFR6 → {NFR6.1.1} (OK). Não há mais NFR listado simultaneamente como coberto e órfão. Leitura única e consistente. |
| 4 | Minor | RESOLVIDO | `boto3==1.42.97` (substituindo `1.35.36`), com rationale ancorado em `docs.aws.amazon.com/botocore/latest/reference/services/bedrock-agentcore-control/` e `docs.aws.amazon.com/boto3/latest/reference/services/bedrock-agentcore.html`; adicionada verificação obrigatória em build-time (`python -c "import boto3; boto3.client('bedrock-agentcore', region_name='us-east-1')"`) com instrução de subir dentro da série 1.42.x se falhar. Rationale agora tem lastro externo verificável + gate operacional. |
| 5 | Minor | RESOLVIDO | Retirada a claim falsa "st.chat_input mudou em 1.32+". Substituída por argumento genérico de reprodutibilidade (workshop de 2 dias, sem CI, sem lockfile compartilhado — deriva de minor entre laptops é o risco a mitigar) + enumeração explícita dos widgets do MVP suportados por `1.38.0` (`st.chat_input`, `st.chat_message`, `st.session_state`, `st.selectbox`, `st.sidebar.button`, `st.warning`, `st.error`, `st.spinner`). Auditável instalando `streamlit==1.38.0` e verificando presença dos widgets. |

### Não-regressões (spot-check contra passes anteriores)

| Item | Resultado | Evidência |
|------|-----------|-----------|
| NFR4.3.1 Guardrails não-ativados | PASS | `security-requirements.md § NFR4.3.1` mantém a decisão consciente, com `NFR8.2` (teste unitário LGPD em U2) como controle auditável equivalente. Coerente com `team.md § Bedrock Guardrails (recomendado, não mandatório)` ("considera caso a caso"). Sem contradição com `project.md § Forbidden` LGPD. |
| NFR5.1.1 credencial least-privilege | PASS | `security-requirements.md § NFR5.1.1` limita a credencial local a `bedrock-agentcore:InvokeAgentRuntime` sobre o ARN específico. Alinhado com `project.md § Mandated` ("credencial do frontend Streamlit (apenas `bedrock-agentcore:InvokeAgentRuntime` para o ARN do runtime)"). |
| NFR5.2.1 fallback `us-east-1` | PASS | `security-requirements.md § NFR5.2.1` prescreve `os.environ.get("AWS_REGION", "us-east-1")`. Coerente com `project.md § Mandated` (região única `us-east-1`) e com `contract-summary.md § C2` (`AWS_REGION` optional, default `us-east-1`). |
| Upstream coverage NFR1..NFR10 completo | PASS | `traceability.json § coverage[]` lista os 10 upstream_ids com status `OK` (NFR1, 2, 3, 4, 5, 6, 7, 10) ou `N/A` (NFR8, 9). Targets citam `performance-requirements.md`, `security-requirements.md` e `tech-stack-decisions.md` de forma resolvível. |
| `## Sources` presente nos 3 MDs | PASS | Confirmado em `performance-requirements.md`, `security-requirements.md`, `tech-stack-decisions.md`. |
| `## Assumptions & Open Questions` presente nos 3 MDs | PASS | Confirmado nos três; todos declaram `None.` — coerente com o estágio, não é lacuna. |
| Nenhum resíduo `context.model_arn` ou `MODEL_ARNS` em U1 | PASS | `grep` sobre os quatro artefatos deste stage não encontra `model_arn` nem `MODEL_ARNS` — a decisão de `functional-spec § AC4.1.3` (U1 envia label; U2 resolve via env vars C3) permanece intacta. |

### Verificações novas de recovery

| Critério | Resultado | Evidência |
|----------|-----------|-----------|
| `t_agent_returned` capturado ANTES de qualquer parse/render | PASS | Prosa explicitamente diz "logo após `response["payload"].read()` ter materializado o corpo (o momento em que o wire boto3 termina, ANTES de qualquer parse ou render)". A ordem cronológica dos 4 timestamps é `t_submit < t_agent_call < t_agent_returned < t_response_rendered`, e a decomposição soma dois intervalos não-sobrepostos. Sem risco de dupla contagem. |
| Rationale de 1s ainda coerente após a mudança | PASS | Rationale mantém "1 s é o teto observado empiricamente para um Streamlit local invocando boto3"; a asserção agora exclui o intervalo de wire, o que torna o teto de 1s ainda mais defensável (não pode ser violado por rede lenta do backend). |
| Testabilidade sobrevive backend lento | PASS | O parágrafo "Essa decomposição sobrevive a um dia com backend lento…" descreve o cenário adversarial exato — o teste falha em U1 apenas se o próprio frontend violar o budget. Correta atribuição de culpa. |
| NFR6.1.1 não implica multi-tenant no processo Streamlit | PASS | Prosa afirma que o modelo é "1 notebook = 1 sessão = 1 processo" e classifica a capacidade multi-sessão do Streamlit como acidental. Não há claim de que 1 processo Streamlit deva atender 3 participantes — o design é 3 processos independentes, um por notebook. |
| `boto3==1.42.97` compatível com `bedrock-agentcore` | ADVISORY | O rationale ancora na doc pública e o build-time check falha ruidosamente se o cliente não carrega, mas a versão exata `1.42.97` só é auditável no dia da instalação (não posso confirmá-la sem hit externo). O gate de instalação (pip resolvendo `==1.42.97`) e o `boto3.client('bedrock-agentcore', ...)` em tempo de build absorvem o risco. Advisory, não bloqueio. |
| `frontend_elapsed` como média de 5 execuções | ADVISORY | Amostra pequena (n=5) — variância pontual pode passar como PASS/FAIL sem sinal estatístico forte. Coerente com o escopo de smoke test do MVP (`team.md § Testing Posture`) e não é regressão; apenas registro para code-generation considerar percentil se sobrar tempo. Advisory. |

### Summary

Os três Major (NFR1.1.1 testability, NFR6.1.1 modelo de deploy, traceability.json auto-contradição) e os dois Minor (boto3 rationale, streamlit rationale) da iter-2 foram absorvidos com evidência auditável. Nenhuma regressão detectada nos itens OK das iterações anteriores; o design não introduz claims novos que exijam refutação estrutural. As duas advertências residuais (versão exata `1.42.97` auditável só na instalação; amostra `n=5` no cálculo de média) são operacionais, mitigadas por gates de build/instalação, e não afetam a implementabilidade. Um developer consegue construir `frontend/app.py`, `src/invoke.py`, `requirements.txt` e `scripts/smoke.py` a partir destes artefatos sem reabrir Inception nem consultar o architect. Verdict: READY.
