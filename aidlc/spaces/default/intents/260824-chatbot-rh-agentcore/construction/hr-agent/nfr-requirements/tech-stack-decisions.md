**Collaborator:** aidlc-architect-agent

# Tech Stack Decisions - Unit hr-agent

Escolhas técnicas locked pelo `project.md § Mandated` / § Forbidden e pelo
`contract-summary § C3`. Este documento consolida as decisões relevantes ao
unit `hr-agent` e explica cada rationale — não introduz decisões novas.

## Sources

- [pj] `project.md § Mandated` — 13 ALWAYS rules; § Forbidden — 13 NEVER rules.
- [tp] `team.md § Code Style` — Python 3.12, ruff default (`E`+`F`), fronteiras de camada.
- [rl] `rules.md` § BR6.1 (label → ARN via env vars C3), § BR6.2 (echo `model_id`), § BR6.4 (fail-fast em `model_id` ausente), § BR7.1 (statelessness — informa "sem retention / sem cache" nas decisões deste stage).
- [cs] `contract-summary.md § C3` — env vars, IAM policy skeleton, inference profile ARNs.
- [rq] `requirements.md § FR3` — AgentCore Runtime + Strands + inference profile ARN.
- [fs] `functional-spec.md § Deployment shape`, § Handler workflow.

## Locked Stack

### Language: Python 3.12

- **Decision**: `agent/agent.py` em Python 3.12.
- **Rationale**: `project.md § Mandated` — ALWAYS write agent, frontend and infrastructure code in Python 3.12 (affirmed 2026-08-24). Consistência com o resto do repo (frontend Streamlit também Python, CDK Python em U3).
- **Alternatives rejected**:
  - Python 3.11 — supported pelo Strands e boto3, mas sem ganho vs 3.12. Ir com o mais recente estável.
  - Python 3.13 — recém-lançado; risco de incompatibilidade com strands_tools no momento do workshop.

### Framework: Strands Agents SDK

- **Decision**: `strands` + `strands_tools` para construção do agente.
- **Rationale**: `project.md § Mandated` — ALWAYS use the Strands Agents SDK. Nativamente integra com Bedrock (`BedrockModel`) e com Bedrock Knowledge Bases (tool `retrieve`).
- **Alternatives rejected** (todos afirmados em `project.md § Forbidden`):
  - **LangChain / LangGraph** — complexidade desnecessária para MVP; Strands cobre.
  - **OpenAI SDK** — modelos consumidos exclusivamente via Bedrock.
  - **FastAPI / Flask** — não são frameworks de agente; interface é Streamlit direto ao Runtime.

### Model runtime: Amazon Bedrock AgentCore Runtime

- **Decision**: agente empacotado e deployado dentro de `bedrock-agentcore` (não `bedrock-agent-runtime`).
- **Rationale**: `project.md § Mandated` — ALWAYS use `boto3.client("bedrock-agentcore")`. Explicitação necessária porque o serviço `bedrock-agent-runtime` (Bedrock Agents) tem nome similar mas é um produto DIFERENTE.
- **Client boto3**: `bedrock-agentcore` para invocação (do lado do frontend U1 via `AgentInvoker`).

### Foundation models: Claude Haiku 4.5 e Amazon Nova Pro

- **Decision**: 2 modelos ativos, resolvidos por label humano via env vars C3:
  - `"Claude Haiku 4.5"` → `INFERENCE_PROFILE_ARN_CLAUDE_HAIKU`.
  - `"Amazon Nova Pro"` → `INFERENCE_PROFILE_ARN_NOVA_PRO`.
- **Passagem ao `BedrockModel`**: SEMPRE via inference profile ARN completo, NUNCA como ID `us.*` direto.
- **Rationale**: `project.md § Mandated` — ALWAYS use inference profile ARNs for models with the `us.*` prefix; § Forbidden — NEVER pass a `us.*` model ID directly as `foundation-model`.
- **Consequência prática**: `foundation-model="us.anthropic.claude-haiku-4-5-20260101-v1:0"` retorna `ResourceNotFoundException` — evitar.
- **Cobertura FR6.3**: 2 modelos > 1, satisfaz "pelo menos 2 modelos testados".

### Vector store: Bedrock Knowledge Bases + S3 Vectors

- **Decision**: Knowledge Base gerenciada Bedrock com backend S3 Vectors.
- **Rationale**: `project.md § Mandated` (afirmado) e `project.md § Forbidden` — NEVER use ChromaDB or Pinecone. Escolha gerenciada elimina operação de vector DB externo.
- **Consumido via**: tool `retrieve` do `strands_tools`. `KNOWLEDGE_BASE_ID` vem via env var (o SDK Strands resolve por env, não passa como argumento na tool call — `team.md § Code Style`).

### Storage backing da KB: S3 com SSE-S3

- **Decision**: bucket S3 dos 5 documentos com criptografia SSE-S3 em repouso.
- **Rationale**: `project.md § Mandated` — ALWAYS apply IAM least-privilege ... and keep S3 objects encrypted at rest (SSE-S3).
- **Not agent's responsibility**: provisionado por U3; o agente lê via `retrieve` que abstrai S3.

### Cliente AWS: boto3 (single client per module)

- **Decision**: em `agent/agent.py`, criar `bedrock-runtime` (ou o que Strands usar internamente) top-level, NÃO recriar por invocação.
- **Rationale**: `team.md § Code Style Idiomas Python 3.12 para boto3 + Strands`. Reuso de connection pool.
- **Nota**: Strands SDK gerencia o cliente Bedrock internamente; o handler não instancia boto3 diretamente para `bedrock-runtime` no caso comum. Se precisar, top-level.

### Region: us-east-1

- **Decision**: única region para Bedrock, AgentCore, Knowledge Bases e S3 Vectors.
- **Rationale**: `project.md § Mandated` — ALWAYS use region `us-east-1`. Stack só liberada nessa region no workshop.
- **Failure mode**: se `AWS_REGION` for setada para outra region no ambiente do participante, boto3 tentaria fallback e falharia com `EndpointConnectionError`. Prevenido por env var C3 (`AWS_REGION=us-east-1` fixo).

### Deps pinning: `==X.Y.Z`

- **Decision**: `agent/requirements.txt` fixa toda dependência com versão exata.
- **Rationale**: `project.md § Mandated` — ALWAYS pin all Python dependencies. Reprodutibilidade entre notebooks dos participantes durante 2 dias.
- **Deps mínimas esperadas**:
  - `strands==<X.Y.Z>`
  - `strands-tools==<X.Y.Z>` (para a tool `retrieve`)
  - `boto3==<X.Y.Z>` (transitiva de strands; pinar explicitamente para lock)
  - `botocore==<X.Y.Z>` (idem)
- **Versões concretas**: fixadas em code-generation após smoke test inicial confirmar compatibilidade Strands + Bedrock atual.

### Linter + formatter: `ruff` com select default

- **Decision**: `ruff` (`E` + `F` apenas — pycodestyle errors + Pyflakes), `ruff format` como formatador único.
- **Rationale**: `team.md § Code Style`. Sem `S` (bandit), sem `B` (bugbear), sem black em paralelo.
- **Consequência**: política de error handling (`except: pass` proibido, etc.) é convenção verificada em code review, não pelo linter.
- **Consumo em CI**: sem CI no workshop; roda local antes do commit.

### Test framework: pytest + pytest-cov

- **Decision**: `pytest` como test runner; `pytest-cov` para coverage floor 80%.
- **Rationale**: `team.md § Testing Posture` — Framework: `pytest`; Cobertura: piso de 80% de linhas, BLOQUEANTE local, enforçado pelo comando `pytest --cov=agent --cov=src --cov-fail-under=80`.
- **Fixture central**: `tests/conftest.py` com `BedrockModel` mockado e stub de `retrieve`.

### Type hints: obrigatórios em funções exportadas

- **Decision**: todas as tools do agente (funções expostas em `agent/agent.py`) têm type hints PEP 604 (`str | None`, `list[str]`).
- **Rationale**: `team.md § Code Style Type hints — obrigatórios em toda função exportada por src/ e frontend/ (é o contrato de camada) e em todas as tools do agente (agent/agent.py)`.
- **Encorajados** em helpers internos prefixados `_`.
- **Not enforced by**: sem mypy/pyright no MVP (`team.md § Não adotado`).

### Environment variables (from contract-summary § C3)

Injetadas pelo IAM execution role do AgentCore Runtime:

| Env var | Purpose | Optional | Default |
|---------|---------|----------|---------|
| `KNOWLEDGE_BASE_ID` | ID da Bedrock KB consumida pelo tool `retrieve` | false | (from CFN output) |
| `AWS_REGION` | Região AWS única | false | `us-east-1` |
| `INFERENCE_PROFILE_ARN_CLAUDE_HAIKU` | ARN para model_id `"Claude Haiku 4.5"` | false (era optional em C3; hr-agent trata como obrigatória) | (from CFN output) |
| `INFERENCE_PROFILE_ARN_NOVA_PRO` | ARN para model_id `"Amazon Nova Pro"` | false (idem) | (from CFN output) |

**Note (efeito em C3)**: `functional-spec § Assumptions & Open Questions` já
registrou que essas duas env vars passam de `optional: true` a `false` na
prática, dado que Q4 do stage anterior (não confundir com Q4 deste stage)
resolveu que U2 é o único que resolve label → ARN. Atualização formal de
`contract-summary § C3` é tarefa cross-unit downstream ao próximo revisão da
Inception.

## Rejected stacks (rationale explícito)

Registrado por completude para não voltarmos a essas escolhas:

| Rejeitado | Razão | Fonte |
|-----------|-------|-------|
| **LangChain / LangGraph** | complexidade desnecessária | `project.md § Forbidden` |
| **OpenAI SDK** | modelos via Bedrock exclusivamente | `project.md § Forbidden` |
| **FastAPI / Flask** | não é interface do MVP | `project.md § Forbidden` |
| **ChromaDB / Pinecone** | vector store gerenciado (Bedrock KB + S3 Vectors) | `project.md § Forbidden` |
| **SQLAlchemy** | sem banco relacional no MVP | `project.md § Forbidden` |
| **React / Next.js** | frontend é Streamlit | `project.md § Forbidden` (afeta U1, listado aqui por completude) |
| **mypy / pyright** | fora do orçamento MVP | `team.md § Não adotado` |
| **pre-commit hooks** | overhead > valor para 2 dias sem CI | `team.md § Não adotado` |
| **Result / Either types** | exception idiomática em Python | `team.md § Não adotado` |
| **Model ID `us.*` direto** | retorna `ResourceNotFoundException` | `project.md § Forbidden` |
| **client `bedrock-agent-runtime`** | serviço diferente do AgentCore | `project.md § Mandated` |
| **`Resource: "*"` em IAM Bedrock** | least-privilege | `project.md § Forbidden` |
| **`secretsmanager:GetSecretValue` runtime** | via CDK resolve placeholder | `project.md § Forbidden` |

## Assumptions & Open Questions

None.
