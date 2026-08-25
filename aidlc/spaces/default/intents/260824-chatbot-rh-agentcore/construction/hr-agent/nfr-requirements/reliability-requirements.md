**Collaborator:** aidlc-architect-agent

# Reliability Requirements - Unit hr-agent

Requisitos de confiabilidade derivados de `requirements.md § NFR9` (sem SLA
formal), § NFR7 (reprodutibilidade) e das decisões cross-stage sobre statelessness
(Q4=A) e retry policy (contract-summary § C1 Suggestions).

## Sources

- [rq] `requirements.md` § NFR9.1 (sem alvo formal 24/7 na demo), § NFR7.1-7.2 (deps pinadas, cdk synth).
- [fs] `functional-spec.md` § Handler workflow step 7 (erros não capturados), § Non-goals (sem retry customizado).
- [rl] `rules.md` § BR6.3-6.4 (fail-fast), § BR7.1 (statelessness).
- [cs] `contract-summary.md` § C1 Erros (ClientError propaga), § Suggestions (boto3 retry default ~3 tentativas).
- [tp] `team.md` § Deployment (sandbox account, sem produção).
- [pj] `project.md` § Mandated (deps pinadas `==X.Y.Z`, cdk synth antes de deploy).

## Requirements

### NFR9.1.1 — Sem SLA formal de disponibilidade

- **Statement**: NÃO há alvo formal de disponibilidade 24/7 ou SLA por percentual (99.9%, 99.95%, etc.) no MVP.
- **Expected availability**: enquanto a conta sandbox AWS estiver ativa E o AgentCore Runtime estiver deployado E os inference profile ARNs estiverem acessíveis, o agente responde. Fora dessas janelas (manutenção AWS, expiração da conta sandbox, quota exceeded), o agente é indisponível — sem gate de SLA.
- **Rationale**: workshop de 2 dias em conta sandbox não justifica engenharia para 99.9%. Se o Runtime der issue mid-demo, o operador reinicia/redeploy manualmente.

### NFR9.1.2 — MTTR (Mean Time To Recovery) informal

- **Statement**: se o agente ficar indisponível durante a demo, o operador restaura em `<15 minutos` via um de:
  - `cdk deploy` novamente (idempotente); OU
  - Trocar `AGENT_RUNTIME_ARN` no frontend para um ARN de runtime anterior (se disponível); OU
  - Escalar para AWS support se for falha regional.
- **Sem automação de failover**: MVP não implementa multi-region, active-passive, health-check com auto-restart, etc.
- **Rationale**: workshop de 2 dias e conta sandbox; risco de indisponibilidade regional é aceito.

### NFR7.1.1 — Reprodutibilidade via deps pinadas

- **Statement**: `agent/requirements.txt` fixa TODAS as dependências Python com `==X.Y.Z` (versão exata), incluindo `strands`, `strands-tools`, `boto3`, e transitivas.
- **Enforcement**: `project.md § Mandated`; auditoria via `pip freeze | diff` local antes de commit.
- **Rationale**: entre notebooks dos participantes durante 2 dias, versão flutuante quebra a demo. Sem CI, deps drift é o único risco não-humano à reprodutibilidade.

### NFR7.2.1 — CDK synth obrigatório antes de deploy

- **Statement**: `cdk synth` inspecionado (visual) antes de cada `cdk deploy`. ARNs (runtime, KB, bucket) consumidos de outputs CFN, nunca hardcoded no código do agente ou do frontend.
- **Scope**: responsabilidade de U3, mas o agente depende disso — se ARN for hardcoded errado, agente falha silenciosamente ao invocar modelo/KB inexistente.
- **Enforcement**: `project.md § Mandated`; grep no template CFN antes de deploy.

### NFR9.1.3 — Fault tolerance: fail-fast, sem retry customizado

- **Statement**: o agente NÃO implementa retry loop customizado. Confia no retry default do boto3 SDK (~3 tentativas com exponential backoff em `ThrottlingException`, ver `contract-summary § C1 Suggestions`).
- **Erros propagam** conforme functional-spec § Handler workflow step 7:
  - `ClientError` do `bedrock-runtime` (Throttling, Quota, IAM) → AgentCore Runtime traduz → `AgentInvoker` converte em `AgentInvocationError` → chat-frontend renderiza `st.error` amigável (BR6.1 chat-frontend, AC1.7.2).
  - `KeyError` de BR6.3/6.4 (model_id inválido/ausente) → mesma cadeia.
  - `retrieve` retorna vazio → NÃO é erro; agente emite fallback canônico (BR3.1).
- **Rationale**:
  - Retry customizado é vetor de amplificação de DoS (NFR5.1.2).
  - boto3 retry default é conservador o suficiente para 1-3 sessões concorrentes.
  - Se retry default falhar 3x, o erro é sinalizador legítimo (não transiente) e merece feedback ao usuário via `st.error`.

### NFR10.1.2 — Statelessness elimina classe de bugs (deriva de NFR10.1 Deferred)

- **Statement**: agente stateless (BR7.1) elimina classe de bugs relacionados a estado corrompido / vazamento entre sessões.
- **Consequência**: recovery é trivial — kill microVM, Runtime aloca outra. Sem checkpoint, sem replay, sem migration.
- **Trade-off**: perguntas de follow-up sem contexto (Q4=A do stage anterior).

### NFR4.2.2 — Ingestão inicial da KB é pré-condição operacional

- **Statement**: antes da demo, `StartIngestionJob` deve rodar manualmente para popular o vector store S3 Vectors com os 5 documentos (`team.md § Deployment`). Sem isso, `retrieve` retorna sempre vazio e todas as consultas caem no fallback BR3.1 (que é resposta legítima, mas não é o comportamento esperado).
- **Not responsibility of the agent**: U3 provisiona a KB; a ingestão é operação humana pré-demo. `hr-agent` NÃO chama `StartIngestionJob` nem valida o estado da KB.
- **Failure mode**: se KB estiver vazia no dia da demo, todas as respostas do agente parecerão "não encontrei" — sintoma facilmente reconhecível para o operador.

### NFR9.1.4 — Backup e disaster recovery: fora do escopo

- **Statement**: sem backup formal do agente (não há estado a fazer backup — Q4=A). Documentos da KB estão no S3 (durabilidade 11 9's do S3 é herdada; sem lifecycle policy custom no MVP).
- **DR strategy**: recriar tudo via `cdk deploy` em outra conta/região se necessário (idempotente).
- **RTO / RPO**: sem targets formais.

## Failure Modes (documentados)

| Falha | Sintoma | Recovery |
|-------|---------|----------|
| `ThrottlingException` do Bedrock | `st.error("Nao consegui responder agora...")` no frontend | Boto3 retry default 3x; se persistir, operador espera 30-60s e re-envia |
| `ResourceNotFoundException` do inference profile | `st.error` no frontend; log ERROR local | Verificar env vars `INFERENCE_PROFILE_ARN_*` no runtime (C3); redeploy CDK U3 |
| KB não populada (`retrieve` sempre vazio) | Todas respostas caem no fallback BR3.1 ("Nao encontrei...") | Operador roda `StartIngestionJob` manualmente e espera ~2-5 min |
| microVM do Runtime crash mid-invocation | Timeout ou erro genérico | Boto3 retry default; se persistir, operador espera Runtime alocar outra microVM |
| Frontend Streamlit crash | Frontend recarrega; `session_id` novo | Ana clica "Limpar conversa" ou reabre a aba (AC1.9.4) |
| KeyError em BR6.3/6.4 (label desconhecido) | `st.error` no frontend | Bug em U1 (frontend enviou label não mapeado); corrigir e redeploy frontend |

## Anti-Requirements

- SLA 99.9%+ — rejeitado (NFR9.1.1).
- Retry customizado — rejeitado (NFR9.1.3).
- Backup / DR estratégico — fora do escopo MVP.
- Multi-region deployment — fora do escopo (project.md § Mandated fixa us-east-1).
- Health check endpoint customizado — não implementado; Runtime gerencia.

## Assumptions & Open Questions

None.
