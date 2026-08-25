# Evidence — Practices Discovery

> O que o lead (`aidlc-pipeline-deploy-agent`) inspecionou para produzir
> `team-practices.md` e `discovered-rules.md`. Fica registrado o que foi
> lido, o que foi inferido, o que foi contribuído pelos support agents,
> como o humano respondeu na entrevista e o que ficou explicitamente fora
> das regras duras.

## Project context inspected

- **Project type**: Greenfield (fonte: `aidlc-state.md` → `Project Type: Greenfield`).
- **Scope**: `mvp` (fonte: `aidlc-state.md` → `Scope: mvp`; `Test Strategy: Standard`; `Depth: Standard`).
- **Active space**: `default` (padrão do workspace; não há `active-space` alterado).
- **Prior affirmation**: nenhuma — `Practices Affirmed Timestamp` está vazio em `aidlc-state.md`. Esta é a primeira execução do stage.

## Sources scanned

### Framework defaults

- `aidlc/spaces/default/memory/org.md` — usado como fonte das cinco seções default para greenfield:
  - `## Way of Working` → trunk-based, squash-merge, branches curtas, `main` = tronco.
  - `## Walking Skeleton` → skeleton segue o flag do escopo (`skeleton: on/off`); `mvp` declara `skeleton: off` na scope-graph, portanto pulado.
  - `## Testing Posture` → default para escopo `mvp`: `Methodology: test-after`, ordering "implement each applicable testable layer, then write and run that layer's tests", com piso de 80% de cobertura de linhas.
  - `## Deployment` → default é "deploy on merge para staging"; não aplicável a este demo (não há staging).
  - `## Code Style` → defere ao formatador/linter do projeto.
- `aidlc/spaces/default/memory/team.md` — **vazio** (só comentários HTML de template). Não há baseline afirmado; não há sobreposição sobre `org.md`.

### Technical baseline

- `tech-env.md` (raiz do workspace) — fonte primária de restrições técnicas duras:
  - § "Project Technical Summary" → Python 3.12, ruff, pytest, pip/requirements.txt, CDK Python, região `us-east-1`.
  - § "Prohibited Libraries / Patterns" → LangChain/LangGraph, OpenAI SDK, FastAPI/Flask, ChromaDB/Pinecone, SQLAlchemy, React/Next.js, `boto3.client("bedrock-agent-runtime")`.
  - § "Security Basics" → IAM, validação de tamanho de mensagem (4000 chars), PII (não expor dados individuais), SSE-S3, IAM least-privilege.
  - § "Notas importantes sobre modelos" → modelos `us.*` só via inference profile ARN.
  - § "Notes for Beginners" → uso obrigatório de `boto3.client("bedrock-agentcore")` e não `bedrock-agent-runtime`.
- `vision.md` (raiz do workspace):
  - § Constraints → stack obrigatória, região `us-east-1`, LGPD (não expor dados individuais).
  - § Out of Scope → sem deploy em produção; sem acesso a dados individuais.

### Ideation artifacts

- `intent-statement.md`, `feasibility-assessment.md`, `scope-document.md`, `wireframes.md`, `user-flow.md` — leitura contextual, sem contribuições novas para as práticas.
- `constraint-register.md` — referenciado como o registro consolidado das
  restrições:
  - **CC-1 / CC-2** (compliance/LGPD) → subsidia "NEVER expose individual employee data".
  - **CT-1..CT-3** (tecnológicas) → subsidiam Python 3.12, Strands Agents SDK, AgentCore Runtime.
  - **CO-1..CO-4** (operacionais) → subsidiam ausência de staging/produção e a definição de deploy local-only.
  - **CA-1..CA-3** (arquitetônicas) → subsidiam a proibição de FastAPI/Flask/React e a escolha de Streamlit + AgentCore.
  - **CN-1..CN-3** (não-funcionais) → subsidiam a latência-alvo e o piso de cobertura.
- `intent-backlog.md` — 13 itens; usado para dimensionar a janela de 2 dias (por-Bolt viable), sem impacto direto nas 5 seções.

### Not available (greenfield)

- **Git history**: não inspecionado além do commit inicial do scaffold do workspace; nenhum padrão de branching ou cadência de merge pode ser inferido do histórico.
- **CI configuration**: **inexistente** — não há `.github/workflows/`, `codebuild-*.yml`, `Jenkinsfile`, `.gitlab-ci.yml` nem `buildspec.yml` no repositório. Nenhuma cadência de deploy pode ser inferida de configuração.
- **Reverse-engineering artifacts**: nenhum — o stage `reverse-engineering` está marcado como `SKIP` em `aidlc-state.md` (greenfield).
- **Existing test suites**: inexistentes; não há `tests/` populado, nem `pytest.ini`, nem `pyproject.toml` com `[tool.pytest.ini_options]`.

## Inferences and decisions (initial draft)

- **Way of Working**: adotado o default do `org.md` (trunk-based, squash-merge). Ajuste para o cenário de workshop: branches devem se resolver dentro do próprio dia; nenhum bloqueio de release aplicável.
- **Walking Skeleton**: pulado por `skeleton: off` do escopo `mvp` (registrado em memory.md como interpretação).
- **Testing Posture (draft inicial)**: adotado o default de `mvp` (`test-after`, 80% de cobertura de linhas, pytest). Especialização: mock do cliente AgentCore (`boto3.client("bedrock-agentcore")`) para evitar chamadas reais em unit tests, alinhado ao exemplo em `tech-env.md` § "Test Example".
- **Deployment**: **desvio consciente** do default do `org.md`. Em vez de "deploy on merge para staging", declaramos "local-only + AgentCore Runtime na conta workshop" porque não há ambiente de staging nem produção no escopo (`vision.md` § Out of Scope, `constraint-register.md` CO-*). Registrado como *deviation* em `memory.md`.
- **Code Style (draft inicial)**: adotado `ruff` (single tool para lint + format), Python 3.12, PEP 8 idiomática. Sem regras adicionais além do que o ruff cobre.
- **Hard constraints promovidos como `## Mandated` / `## Forbidden` (draft inicial)**: derivados 1:1 das seções de `tech-env.md` acima; nenhuma regra foi criada sem uma linha citável no tech-env.

## Support contributions integrated

Três support agents contribuíram e suas propostas foram integradas (com
exceções abaixo) nas versões finais:

- **`aidlc-quality-agent`** — endossou `test-after` + ordering estruturada;
  objetou o piso de cobertura como "métrica de saúde" não bloqueante e
  pediu `pytest-cov` explícito. Contribuiu com: enumeração das camadas
  testáveis (`src/invoke.py::ask_agent`, `agent/agent.py`) e não testáveis
  (frontend Streamlit, infra CDK); ampliação da estratégia de mock para
  cobrir `agent/agent.py` (`BedrockModel` mockado + `retrieve` stubado);
  proposta de teste de guardrail LGPD com prompt provocador e stub de
  `retrieve`; proposta de smoke test (checklist manual e/ou script `.py`).
- **`aidlc-developer-agent`** — endossou `ruff` como single-tool; objetou o
  ruff no default puro (`E`+`F` apenas) e a ausência de política de
  tratamento de erro. Contribuiu com: fronteiras de camada explícitas
  (`agent/` isolado, `frontend/ → src/ → boto3`); regras de naming e env
  vars (`AGENT_RUNTIME_ARN`, `KNOWLEDGE_BASE_ID`, `AWS_REGION`);
  `session_id` server-side via `uuid.uuid4()`; type hints obrigatórios na
  fronteira; **política de erro** `ClientError → AgentInvocationError →
  st.error(...)` + log; idiomas Python 3.12 para boto3+Strands; lista de
  não-adotados (mypy, pre-commit, Result types).
- **`aidlc-devsecops-agent`** — endossou o mock de `bedrock-agentcore`;
  objetou a ausência de defesa em profundidade para CC-1/CC-2 e a ausência
  de pin de dependências. Contribuiu com: pin exato em ambos os
  `requirements.txt`; IAM roles distintas por plano de acesso (execution
  role do runtime, role do frontend, role de ingestão da KB) sem
  `Resource: "*"`; `session_id` via `uuid.uuid4()` (converge com
  developer); política de segredos via `{{resolve:secretsmanager:...}}` +
  `.gitignore` mínimo; proibição de ingestão de docs com dados individuais
  na KB; proibição de logar payload completo fora da conta sandbox; fluxo
  `cdk synth` antes de `cdk deploy` com ARNs vindos de outputs; proposta
  de Bedrock Guardrails (denied topics + PII em `OUTPUT`); proposta de
  `pip-audit` uma vez antes da demo; proposta de ativar `S`+`B` no ruff.

## Human interview outcomes

Entrevista humana com 10 perguntas Q1–Q10 cobrindo as cinco seções e as
propostas dos support agents. Respostas registradas em
`practices-discovery-questions.md`:

- **Q1=A** — Way of Working: manter default do `org.md` (trunk-based,
  branches 1–2 dias, squash-merge). Draft do lead confirmado.
- **Q2=A** — Walking Skeleton: `off` (default do escopo `mvp`). Draft do
  lead confirmado.
- **Q3=A** — Cobertura: piso de **80% bloqueante local** via `pytest
  --cov-fail-under=80`; `pytest-cov` adicionado a `requirements-dev.txt`.
  Escolhida a opção B do QA (bloqueante) sobre a opção A (happy-path sem
  percentual).
- **Q4=A** — Teste de guardrail LGPD como **Must** (não Could): 1 unit
  test com prompt provocador e stub de `retrieve` retornando salário
  fictício; asserção de que a resposta não repete o valor.
- **Q5=B** — Smoke test como **script `.py`** (`scripts/smoke.py`) somente;
  **sem** checklist manual em paralelo.
- **Q6=A** — Deployment via **CDK Python** (AgentCore Runtime + KB no
  mesmo stack); sem staging.
- **Q7=B** — Bedrock Guardrails: **Recomendado, NÃO Mandatório**. Vai
  para `## Deployment` de `team-practices.md` como best practice; **não**
  entra em `discovered-rules.md`. Time decide caso a caso.
- **Q8=B** — Ruff config: **default puro (`E`+`F`)**. Sem `select`
  customizado; sem `S` (bandit), sem `B` (bugbear), sem `UP`.
- **Q9=A** — Error handling: adotar a proposta do developer agent
  (`ClientError → AgentInvocationError → st.error(...)` + log).
- **Q10=A** — Deps: pin exato `==` em `requirements.txt` **e**
  `agent/requirements.txt`.

Propostas dos support agents que foram **recusadas pelo humano** ficam
registradas como recomendações em `team-practices.md`, não como regras
duras: expansão do `select` do ruff (`S`, `B`, `UP`) recusada em Q8=B e
Bedrock Guardrails como `Mandated` recusado em Q7=B (fica como
recomendação em § Deployment).

## Q8/Q9 tension note

O humano escolheu ruff no **default puro (`E`+`F`)** em Q8=B **e** adotou
uma política explícita de tratamento de erro em Q9=A. O default do ruff
**não inclui bugbear (`B`)**, que é a regra que pegaria automaticamente as
violações operativas da política de Q9 — `except Exception: pass`, `bare
except` sem re-raise, `mutable default args`. Consequência intencional:

- A **política de erro** (`ClientError → AgentInvocationError → st.error`,
  input guard em `src/invoke.py`, nunca `except: pass`) é uma **convenção
  verificada em code review**, não pelo linter.
- Se o time quiser enforcement automatizado depois do workshop, basta
  adicionar `B` ao `select` do ruff no `pyproject.toml`; a política do
  código já está escrita para passar nessa regra.
- Registrado explicitamente em `team-practices.md` § Code Style (nota
  logo abaixo da configuração do ruff e no fim da subsection de error
  handling policy) para que a intenção do humano fique visível a quem lê
  o memory promovido.

## Coverage note

- **required-sections** (sensor): `team-practices.md` inclui as cinco seções H2 obrigatórias (`## Way of Working`, `## Walking Skeleton`, `## Testing Posture`, `## Deployment`, `## Code Style`); `## Testing Posture` inclui os dois campos estruturados `- **Methodology**:` e `- **Ordering**:`; `discovered-rules.md` inclui `## Mandated` e `## Forbidden`.
- **upstream-coverage** (sensor): não há entradas condicionais brownfield para cobrir (todos os `consumes` do stage são `conditional_on: brownfield`); a exigência é *absente por design* em greenfield.
