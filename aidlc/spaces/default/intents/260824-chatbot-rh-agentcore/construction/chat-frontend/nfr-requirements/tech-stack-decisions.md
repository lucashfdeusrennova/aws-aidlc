**Collaborator:** aidlc-architect-agent

# Tech Stack Decisions — chat-frontend (U1)

Escolhas tecnológicas travadas para o unit `chat-frontend` (kind `ui`).
Complementa as decisões de nível de projeto em `team.md § Code Style`,
`team.md § Deployment` e `project.md § Mandated/Forbidden` — este
documento só registra o que é específico do frontend Streamlit.

## Sources

- [fs] `functional-spec.md` — chat-frontend, § "State Machine" (rerun
  Streamlit síncrono), § "Frontend hierarchy summary" (dependência
  `frontend/ → src/`).
- [rq] `requirements.md` — NFR7.1 (pinagem exata `==X.Y.Z`), NFR7.2
  (`cdk synth` — não aplicável a U1 mas informativo), FR4.x (Streamlit),
  FR8.1 (guard 4000 em `src/invoke.py`), FR9.1 (`AgentInvocationError`).
- [cs] `contract-summary.md` — C1 payload (JSON via `invoke_agent_runtime`),
  § "Nota importante" (`boto3.client("bedrock-agentcore")`).
- [rules] `aidlc/spaces/default/memory/{org,team,project}.md` — project.md
  § Forbidden (React, Next.js, FastAPI, Flask, LangChain, OpenAI SDK,
  ChromaDB, SQLAlchemy), § Mandated (Python 3.12, Strands SDK,
  `bedrock-agentcore` client, pinagem exata, ruff), team.md § Code Style
  (ruff default `E`+`F`, PEP 604, type hints obrigatórios em `src/` e
  `frontend/`), team.md § Testing Posture (pytest, cobertura ≥80%).

## Chosen stack

### Runtime language

- **Python 3.12** — [project.md § Mandated]. Sem alternativa considerada;
  Strands SDK é Python-only e o time inteiro está alinhado.

### UI framework

- **Streamlit** [project.md § Forbidden proíbe React, Next.js, FastAPI,
  Flask; team.md § Deployment fixa `streamlit run frontend/app.py`].
- **Versão travada**: `streamlit==1.38.0`. [Q4=A]
- **Rationale da pinagem exata**: reprodutibilidade entre os notebooks
  dos participantes durante os 2 dias de workshop — sem CI e sem
  lockfile compartilhado, qualquer deriva de minor pode fazer um
  participante ver comportamento diferente do outro. `1.38.0` é uma
  versão estável testada localmente com os widgets do MVP
  (`st.chat_input`, `st.chat_message`, `st.session_state`, `st.selectbox`,
  `st.sidebar.button`, `st.warning`, `st.error`, `st.spinner`).
- **Alternativas rejeitadas**: `>=1.36` (deixaria o developer decidir a
  minor exata em code-generation — risco de deriva entre laptops em
  janela de 2 dias); Gradio, Panel, Chainlit (não estão em
  `team.md`/`project.md` e adicionariam divergência entre a stack afirmada
  e a stack rodando).

### AWS SDK

- **boto3** [team.md § Code Style fixa `boto3.client("bedrock-agentcore")`
  nunca `bedrock-agent-runtime`; project.md § Forbidden proíbe OpenAI SDK].
- **Versão travada**: `boto3==1.42.97`. [Q4=A]
- **Rationale**: o serviço `bedrock-agentcore` foi para GA em jul/2025 e
  entrou no botocore/boto3 na série 1.42.x (referências públicas em
  `docs.aws.amazon.com/botocore/latest/reference/services/bedrock-agentcore-control/`
  e em
  `docs.aws.amazon.com/boto3/latest/reference/services/bedrock-agentcore.html`,
  ambas mostrando as operações `create_agent_runtime`,
  `get_agent_runtime` e `invoke_agent_runtime` em versões 1.42.x). A
  pinagem em 1.42.97 escolhe a última minor comprovadamente estável da
  série 1.42 no dia 25/08/2026, evitando arrastar o participante para as
  minor mais recentes 1.43.x que ainda podem receber mudanças de shape
  em `bedrock-agentcore-control`. Compatível com Python 3.12.
- **Build-time verification (obrigatória)**: o developer, no primeiro
  `python -c "import boto3; boto3.client('bedrock-agentcore', region_name='us-east-1')"`
  do dia, DEVE confirmar que o cliente inicializa. Se falhar com
  `UnknownServiceError`, subir a versão dentro da série 1.42.x até
  aceitar (registrar no PR).
- **Alternativas rejeitadas**: `>=1.42` (Q4=A pediu pinagem exata);
  `aioboto3` (Streamlit executa `invoke_agent_runtime` de forma síncrona
  dentro do rerun — assíncrono adicionaria complexidade sem ganho de
  latência).

### Testing tooling (dev-time only)

- **pytest** [team.md § Testing Posture].
  - **Versão travada**: `pytest==8.3.3`. [Q4=A]
- **pytest-cov** [team.md § Testing Posture — piso de 80% via
  `pytest --cov=agent --cov=src --cov-fail-under=80`].
  - **Versão travada**: `pytest-cov==5.0.0`. [Q4=A]
- **Rationale**: sem `pytest-cov` a flag `--cov` falha como argumento
  desconhecido e a métrica NUNCA é coletada — o gate de cobertura
  precisa do pacote instalado no ambiente de teste.

### Linter/formatter

- **ruff** com select default (`E` + `F` apenas). [team.md § Code Style].
- **Versão travada**: `ruff==0.6.9`. Rodado localmente antes de cada
  commit; não há CI que bloqueie no workshop, mas violações não vão
  para `main`.
- **`ruff format`** como formatador único (não usar black em paralelo).
- **Nota importante** (repetida de team.md): o select default do ruff
  **não inclui bugbear (`B`)** — a política de error handling (proibição
  de `except: pass`, mutable default args) é convenção verificada em
  code review, não pelo linter.

## Requirements files layout

Duas árvores independentes de dependências, refletindo a fronteira
`agent/` isolado (U2) vs `frontend/`+`src/` (U1):

### `requirements.txt` (raiz do repo — usado pelo frontend/src)

```
streamlit==1.38.0
boto3==1.42.97
```

### `requirements-dev.txt` (raiz do repo — dev/CI local)

```
pytest==8.3.3
pytest-cov==5.0.0
ruff==0.6.9
```

Nota: `agent/requirements.txt` (Strands, `strands-tools`, boto3 do U2)
é escopo do unit U2 (hr-agent), não deste stage.

## Directory conventions (U1-specific)

Reafirma a fronteira de camada de `team.md § Code Style`:

```
project-root/
├── frontend/
│   └── app.py                # Streamlit — importa src.invoke
├── src/
│   ├── __init__.py
│   └── invoke.py             # ask_agent(), boto3 bedrock-agentcore
├── tests/
│   ├── conftest.py           # fixtures de mock do cliente
│   └── test_invoke.py
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml            # ruff config (select default)
```

- `frontend/app.py` importa `src.invoke.ask_agent` e a exceção
  `src.invoke.AgentInvocationError`. Nunca o inverso: `src/` não importa
  `streamlit`. [team.md § Code Style]

## Logging config

Top-level em `frontend/app.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
```

- Handler default = stdout. Log aparece no terminal do
  `streamlit run frontend/app.py`. [Q3=A]
- Sem `FileHandler`, sem CloudWatch handler local, sem `sentry-sdk` ou
  telemetria externa (vide `security-requirements.md § NFR4.5.1`).

## Not adopted (com rationale)

- **React/Next.js** — proibido em `project.md § Forbidden`; frontend é
  Streamlit por decisão de escopo.
- **FastAPI/Flask** — proibido em `project.md § Forbidden`; não há API
  HTTP nossa (a invocação vai por AgentCore Runtime).
- **LangChain/LangGraph** — proibido em `project.md § Forbidden`;
  complexidade desnecessária para o demo. Strands (em U2) já cobre RAG.
- **mypy/pyright** — fora do orçamento do workshop [team.md § Code Style
  "Não adotado"]. Type hints legíveis + ruff default entregam valor sem
  custo de setup de type-checker.
- **pre-commit hooks** — overhead > valor para 2 dias sem CI [team.md
  § Code Style "Não adotado"].
- **aioboto3 / asyncio** — Streamlit executa o rerun sincronamente;
  chamada async adiciona custo cognitivo sem melhorar a latência (o wire
  boto3 já é rápido — o gargalo é o backend, coberto por
  `performance-requirements.md § NFR1.1.1`).
- **Sentry / Datadog / Segment / analytics client-side** — proibido
  logar payload completo em sinks externos [project.md § Forbidden].
- **Sistema de configuração externo** (`hydra`, `dynaconf`, `pydantic-settings`) —
  o frontend consome apenas 2 env vars (`AGENT_RUNTIME_ARN`, `AWS_REGION`);
  `os.environ` direto é suficiente e mais legível.

## Compatibility matrix

| Componente | Versão | Compatível com | Verificado em |
|---|---|---|---|
| Python | 3.12 | streamlit≥1.36, boto3≥1.35 | Python.org release notes |
| streamlit | 1.38.0 | Python 3.9-3.12 | Streamlit changelog |
| boto3 | 1.42.97 | Python 3.8+; `bedrock-agentcore` client | docs.aws.amazon.com/boto3/latest/reference/services/bedrock-agentcore.html |
| pytest | 8.3.3 | Python 3.8+ | pytest docs |
| pytest-cov | 5.0.0 | pytest ≥6.0 | pytest-cov docs |
| ruff | 0.6.9 | Python 3.12 | ruff docs |

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
