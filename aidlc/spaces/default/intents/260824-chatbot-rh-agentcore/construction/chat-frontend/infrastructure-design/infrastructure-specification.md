**Collaborator:** aidlc-aws-platform-agent

# Infrastructure Specification — chat-frontend (U1)

Documento de infraestrutura do unit `chat-frontend` (kind `ui`). O unit é
um processo Streamlit local rodando no notebook de cada participante,
consumindo ARNs provisionados pelo unit `infra` (U3, kind `packaging`).
NENHUMA infra AWS é criada por este unit — os recursos AWS
(AgentCore Runtime, Knowledge Base, S3 bucket) são owned por U3.

## Sources

- [prf] `performance-design.md` — D1 (cliente boto3 module-level),
  D-Concurrency (rerun síncrono, 1 processo por sessão).
- [sec] `security-design.md` — D6 (credencial via chain default do boto3),
  NFR5.1.1 (least-privilege scope na role do frontend).
- [lc] `logical-components.md` — Fronteira `frontend/ → src/ → boto3`;
  D-Log (stdout JSON com session_id).
- [cp] `components.md` — HRChatFrontend + AgentInvoker moram em U1;
  HRAgent mora em U2 dentro do AgentCore Runtime (provisioned por U3).
- [fs] `functional-spec.md` — chat-frontend, single-page Streamlit;
  state machine síncrona.
- [cs] `contract-summary.md` — C2 (CFN outputs de U3 consumidos por U1
  via env vars: `AGENT_RUNTIME_ARN`, com fallback `AWS_REGION=us-east-1`).
- [rules] `team.md § Deployment` (Streamlit local + CDK único em U3),
  `project.md § Mandated` (região us-east-1, no-hardcode, least-privilege).

## Deployment

| Facet | Choice | Rationale |
|-------|--------|-----------|
| Compute model | Notebook do participante (macOS / Linux / Windows) executando `streamlit run frontend/app.py`. | `team.md § Deployment` fixa "Streamlit local no notebook de cada participante"; nenhum hosting hospedado no MVP. |
| Networking topology | N/A — local. Streamlit ouve em `localhost:8501` do próprio notebook. Nenhum VPC, ALB, NAT gateway ou security group provisionado por este unit. | Modelo 1-participante/1-notebook (`performance-requirements.md § NFR6.1.1`); comunicação Internet direta do notebook para AWS via chain default boto3 sobre TLS 1.2+. |
| Storage strategy | N/A — `st.session_state` em memória do processo. Sem persistência entre reruns do processo. | `functional-spec.md § State Machine` + Anti-Requirements em `performance-design.md` (sem cache local). Histórico da sessão perdido ao fechar o notebook — comportamento esperado do MVP. |
| Environments | `workshop-sandbox` — conta AWS de sandbox única, região `us-east-1`. Nenhum staging, nenhum production. | `team.md § Deployment` ("nenhum ambiente de staging nem de produção") + `project.md § Mandated` (`us-east-1` fixo). |
| IaC approach | None-in-this-unit. Nenhum CDK, CloudFormation, Terraform em U1. | Toda a infra AWS relevante ao chat-frontend (o AgentCore Runtime que ele invoca) mora em U3 via CDK Python. U1 CONSOME ARNs; não provisiona. |
| Resource sizing | Desktop-class do participante (mínimo recomendado: 4 GB RAM livres, Python 3.12). | Streamlit + boto3 + JSON payload de <4KB não pressionam nenhum recurso do laptop moderno. Não há sizing horizontal (`NFR6.1.1`: 1 processo por notebook). |

## Infrastructure Services

| Service | Role | Configuration | Notes |
|---------|------|---------------|-------|
| _(nenhum provisionado por este unit)_ | — | — | Todo AWS-hosted service que `chat-frontend` toca (`bedrock-agentcore.InvokeAgentRuntime`) é provisionado pelo unit `infra` (U3). Consulte `construction/infra/infrastructure-design/` para a lista completa de recursos. |

## Shared Infrastructure

| Shared Resource | Owner Unit | Consumer Units | Access Boundary |
|-----------------|------------|----------------|------------------|
| `AGENT_RUNTIME_ARN` (ARN do AgentCore Runtime provisionado em `us-east-1`) | `infra` (U3) | `chat-frontend` (U1) | Chain default do boto3 (`~/.aws/credentials`, env vars, IAM role) do participante. A role usada DEVE ter apenas `bedrock-agentcore:InvokeAgentRuntime` sobre esse ARN específico (`project.md § Mandated`). Consumido via env var `AGENT_RUNTIME_ARN` (`contract-summary.md § C2`); nunca hardcoded no código (`NFR5.2.1`, `project.md § Forbidden`). |
| `AWS_REGION` (`us-east-1`) | `infra` (U3) — fixado pelo stack CDK | `chat-frontend` (U1) | Env var opcional com fallback `"us-east-1"` explícito no código de `src/invoke.py` (`security-design.md § D6`). `project.md § Mandated` obriga região única em todas as chamadas AWS. |

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->

## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Date:** 2026-08-25T14:55:51Z
**Iteration:** 1
**Review class:** adversarial

### Findings

| # | Severity | Location | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | Minor | `infrastructure-specification.md § Sources` (e por extensão os três deliverables) | O `consumes:` frontmatter de `.kiro/aidlc-common/stages/construction/infrastructure-design.md` declara `scalability-design`, `reliability-design` e `observability-design` como `required: true`. Nenhum dos três slugs aparece em qualquer forma aceita pelo sensor `aidlc-upstream-coverage` (token isolado, wikilink, backtick, ou path segment) nos deliverables deste stage. A ausência é intencional — `nfr-design-questions.md` linha 3 declara literalmente "Reliability, scalability e observability caem para U2 (`hr-agent`) por `produces_kinds`", e o diretório `nfr-design/` de fato não contém esses três arquivos — mas para um leitor externo (ou para o próprio sensor advisory) parece omissão. | Adicionar uma linha explícita em `## Sources` do `infrastructure-specification.md`: "`scalability-design`, `reliability-design`, `observability-design` — não produzidos por `nfr-design` para kind `ui` (`nfr-design-questions.md` linha 3); esses NFRs caem em U2 (`hr-agent`)". Ativa o token no output (o sensor `upstream-coverage` conta ocorrência do slug como token isolado) e torna a intenção auditável. Não bloqueante — o sensor é advisory e a decisão upstream é legítima. |
| 2 | Minor | `infrastructure-specification.md § Shared Infrastructure` (linha `AWS_REGION`) | A tabela afirma `Owner Unit: infra (U3) — fixado pelo stack CDK`. Contradiz `contract-summary.md § C2 env_vars_required_by_frontend.AWS_REGION`, que declara `source: default do participante ou setado manualmente`, `optional: true`, `default: "us-east-1"`. U3 não provisiona essa env var — quem a fornece é o ambiente do participante, com fallback no código de `src/invoke.py` (`security-design.md § D6`). O contrato passado C2 é a fonte de verdade cross-unit; a linha diverge dela. Consequência funcional: nula (o fallback no código está correto e coerente com `project.md § Mandated` região `us-east-1`); consequência auditável: um leitor que só consulta esta tabela conclui erradamente que U3 é dono da variável. | Reescrever a coluna Owner para `Convenção (project.md § Mandated: região us-east-1) + fallback no código (src/invoke.py, security-design.md § D6)`; ou remover a linha do quadro `Shared Infrastructure` (a variável não é um recurso compartilhado — é uma convenção com default no código). Cross-verificação: `contract-summary.md § C2` já cita explicitamente "default do participante ou setado manualmente". |
| 3 | Minor | `cicd-pipeline.md § Local checks` (linha "ARN/credencial audit") | A linha marca o check como `Blocking? No — check manual, discricionário`. Isso desalinha com `project.md § Forbidden`: "NEVER hardcode account IDs, ARNs, IAM access keys, tokens or any credential in source code" — um NEVER Mandated (`affirmed 2026-08-24`), não uma convenção discricionária. Também desalinha com `project.md § Mandated`: "ALWAYS ... never hardcoded no código do frontend ou do invocador". Rotular o único guard mecânico da regra como opcional-e-discricionário enfraquece a política. | Uma das duas: (a) elevar o check para `Blocking? Yes` com o mesmo padrão regex, ou (b) removê-lo do checklist e declarar em prosa que o enforcement do NEVER hardcode é responsabilidade do code review humano (que é o que `team.md § Code Style` já assume para outras convenções, e.g. error handling policy). "Opcional/discricionário" para um NEVER Mandated é a única combinação que não cabe. |
| 4 | Minor | `cicd-pipeline.md § Local checks` (omissão) | `project.md § Mandated` afirma "ALWAYS pin all Python dependencies to exact versions (`==X.Y.Z`) in `requirements.txt` and `agent/requirements.txt`" — reprodutibilidade do demo entre notebooks. O `chat-frontend` possui `requirements.txt` (Streamlit + boto3) e `requirements-dev.txt` (`ruff`, `pytest`, `pytest-cov` — todos pinados em `tech-stack-decisions.md`). Nenhuma linha do checklist verifica a pinagem. É a única regra Mandated auditável mecanicamente que este stage seria o lugar natural para materializar. | Adicionar uma linha ao checklist local: `git grep -nE '(^\|[[:space:]])(streamlit\|boto3\|ruff\|pytest\|pytest-cov)([[:space:]]*)?(>=\|~=\|\^\|>\|<)([^=]\|$)' -- 'requirements*.txt' 'agent/requirements*.txt'` com gate "zero matches"; ou uma linha mais leve: `grep -nE '(>=\|~=\|\^)' requirements*.txt agent/requirements*.txt \|\| true` como advertência. Não bloqueante; a alternativa é reconhecer em prosa que a pinagem é verificada no code review e não no gate local. |
| 5 | Minor | `traceability.json` linhas `NFR1.1.1` e `NFR3.2.1` (status `N/A`) | Ambos os itens têm status `N/A` com justificativa não-vazia — o schema do sensor `aidlc-traceability` permite `N/A` desde que o `target` seja não-vazio, e ambas as linhas passam essa checagem. As justificativas ("nenhuma infra deste unit contribui para NFR1.1.1"; "session_id via uuid4 é comportamento de código em C1 ... fora de escopo de infraestrutura") são defensáveis — o kind `ui` local não provisiona nada em AWS, e a coverage real para esses dois NFRs mora em `performance-design.md § D1` e `security-design.md § D2` respectivamente, ambos do stage anterior. Não é órfão escondido — os dois requirements têm coverage upstream real, apenas não neste stage. | Nenhuma ação obrigatória. Sugestão de melhoria de legibilidade: adicionar campo textual "covered_at" apontando o stage anterior (`nfr-design/performance-design.md § D1` / `nfr-design/security-design.md § D2`), para reduzir a fricção de auditoria pós-workshop. Fora do schema oficial do sensor mas informativo. |

### Verificações que passaram

| Critério | Resultado | Evidência |
|---|---|---|
| Coerência com `contract-summary.md § C2` (`AGENT_RUNTIME_ARN`) | PASS | `infrastructure-specification.md § Shared Infrastructure` linha 1 declara `Owner: infra (U3), Consumer: chat-frontend (U1), consumo via env var AGENT_RUNTIME_ARN`. `contract-summary.md § C2 env_vars_required_by_frontend.AGENT_RUNTIME_ARN` declara `source: CFN output AgentRuntimeArn, optional: false`. Match exato — nenhum drift no contrato principal. Também alinhado com `components.md § External Dependencies` (`AgentInvoker` depende de `Amazon Bedrock AgentCore Runtime` como `third-party-api`) e `contract-summary.md § C2` output `AgentRuntimeArn`. |
| Boundary "no-cloud-infra" registrado explicitamente | PASS | Preâmbulo declara "NENHUMA infra AWS é criada por este unit — os recursos AWS ... são owned por U3"; tabela `Deployment` marca `IaC approach: None-in-this-unit`; tabela `Infrastructure Services` traz linha única `(nenhum provisionado por este unit)` com redirecionamento a U3; Q1=A materializado exatamente como o `Consolidated Summary Confirmation` prometia. |
| Cobertura upstream (sensor `aidlc-upstream-coverage`) — artefatos produzidos | PASS PARCIAL | 6 dos 9 slugs de `consumes:` aparecem como token isolado em `Sources`: `performance-design`, `security-design`, `logical-components`, `components`, `functional-spec`, `contract-summary`. Os 3 ausentes (`scalability-design`, `reliability-design`, `observability-design`) são intencionais e mora no Finding #1 acima. |
| Sensor `required-sections` (≥2 H2) | PASS | `infrastructure-specification.md`: 6 H2s (`Sources`, `Deployment`, `Infrastructure Services`, `Shared Infrastructure`, `Assumptions & Open Questions`, `Review`). `monitoring-design.md`: 7 H2s. `cicd-pipeline.md`: 4 H2s + subsecões. Todos acima do piso genérico de 2. |
| Sensor `traceability` — schema JSON | PASS | `stage: "infrastructure-design"`, `unit: "chat-frontend"`, `upstream_ids` com 6 IDs (`NFR1.1.1`, `NFR3.2.1`, `NFR4.5.1`, `NFR5.1.1`, `NFR5.2.1`, `NFR6.1.1`), `coverage` com 6 entradas (uma por upstream_id), status ∈ {OK, N/A}, todos os `target` não-vazios, `reverse: []`. Valida contra o schema explicitado em `.kiro/sensors/aidlc-traceability.md`. |
| Sensor `traceability` — coverage-vs-upstream | PASS | Set de IDs em `upstream_ids` = set em `coverage[].id`. Nenhum GAP, nenhum ORPHAN, nenhum ID de upstream não referenciado, nenhum ID em coverage não declarado. |
| Sensor `linter` / `type-check` (snippets TS/JS/TSX) | PASS | Nenhum snippet TypeScript/JavaScript/TSX nos 3 markdowns produzidos. O único código embedded em qualquer artefato upstream é Python (fora do escopo destes dois sensors). |
| Checklist local (`cicd-pipeline.md`) reflete `team.md § Testing Posture` | PASS SUBSTANTIVAMENTE | Comando canônico `pytest --cov=src --cov=agent --cov-fail-under=80` presente e blocking. `ruff format .` + `ruff check .` presentes e blocking, alinhados com `team.md § Code Style` (select default `E`+`F`). Fluxo squash-merge para `main` + `gh pr create --base main` alinhado com `team.md § Way of Working` (trunk-based, `main` como base+target). Advertência sobre `.gitignore` desde o commit inicial cobrindo `.env`, `credentials`, `*.pem`, `*.pfx` alinhada com `project.md § Mandated`. |
| Boundary declarada em `monitoring-design.md` (SLI do smoke ≠ SLI deste stage) | PASS | Nota explícita: "O único SLI operacional relevante — `frontend_elapsed <= 1 s` (`NFR1.1.1`) — pertence ao smoke test em `team.md § Testing Posture`, não a este stage." Coerente com Q2=A e com o fato de que `NFR1.1.1` está marcada como `N/A` na `traceability.json` deste stage por essa mesma razão. |
| STRIDE / threat modeling explícito neste stage | PASS (delegação legítima) | `security-design.md § Threat model` já executou a análise STRIDE para chat-frontend na fronteira U1 (assumindo rede da conta sandbox e operador confiável). `infrastructure-design` não adiciona nova infra AWS, portanto não adiciona nova superfície de ataque — não há nada a modelar aqui. Delegação coerente; a advertência sobre least-privilege da role do participante (`NFR5.1.1`) fica na linha `AGENT_RUNTIME_ARN` de `Shared Infrastructure` e é reforçada no `Access Boundary`. |
| Ausência de ciclos U1↔U3 | PASS | U1 consome `AGENT_RUNTIME_ARN` (env var) de U3 em runtime; U3 não consome nada de U1 (nem em build-time nem em runtime). `unit-of-work-dependency.md`: U3 → U1 (runtime coupling via outputs); nenhuma aresta de retorno. Sem ciclo. |
| Blast radius do processo Streamlit | PASS | `logical-components.md § D-FailureIsolation` já cobriu (crash local ao processo do notebook; nenhum efeito em outras sessões; `Ctrl+C` + reinicia é a recuperação); `infrastructure-specification.md` reafirma indiretamente via `Environments: workshop-sandbox único` + `Resource sizing: desktop-class do participante`. Coerente. Nenhum novo blast radius introduzido por este stage. |
| Segredos / `NFR5.4.1` | PASS | `cicd-pipeline.md § Secrets management` afirma "Nenhum segredo é gerado por `chat-frontend`; a credencial AWS resolve pela chain default do boto3". Alinhado com `project.md § Forbidden` ("NEVER call `secretsmanager:GetSecretValue` ... directly at runtime"). Nenhum uso de Secrets Manager neste unit, nenhum need-to-verify na infraestrutura. |

### Summary

Design implementável. Um developer consegue construir/rodar `chat-frontend` a partir destes 4 artefatos (specification + monitoring + cicd + traceability) e do checklist local sem reabrir Inception, Domain ou NFR Design. A decisão consciente de registrar a natureza "no-cloud-infra" com tabelas substantivas + N/A justificado (Q1=A) foi bem executada: a tabela `Deployment` traz facetas concretas, `Infrastructure Services` explicita o redirecionamento a U3, e `Shared Infrastructure` materializa o único recurso cross-unit (`AGENT_RUNTIME_ARN`) com boundary IAM aterrissado no least-privilege do `project.md § Mandated`. As cinco findings são todas Minor e residem em duas categorias: (a) atribuições que divergem do contrato passado (`AWS_REGION` owner na tabela Shared, Finding #2), e (b) omissões auditáveis (Findings #1, #3, #4 — cobertura upstream, gate mandatado, pinagem mandatada). Nenhuma é bloqueante; a decisão do gate fica com o humano. Verdict: **READY**.

