**Collaborator:** aidlc-developer-agent

## Contribution

Adições ao `## Code Style` de `team-practices.md` sob a lente developer — o
draft atual está correto no espírito (ruff + PEP 8 + estrutura de
`tech-env.md`), mas fica genérico demais para um codebase Strands + boto3
onde algumas convenções valem mais do que "os defaults do ruff atendem".

### Fronteiras de camada (`agent/` vs `src/` vs `frontend/` vs `tests/`)

A estrutura em `tech-env.md` § "Project Structure" é a que adotamos, mas o
invariante de dependência que a torna sã não está escrito em lugar
nenhum. Registrar explicitamente:

- **`agent/`** roda **dentro** do AgentCore Runtime (microVM gerenciada,
  deploy separado). É auto-contido: só depende de `strands`,
  `strands_tools` e `boto3`. **Nunca** importa de `src/` ou `frontend/`
  — são runtimes diferentes.
- **`src/`** é a cola de invocação (o cliente boto3 do
  `bedrock-agentcore`). Não conhece Streamlit e não conhece o código
  interno do agente — só a assinatura de `invoke_agent_runtime`.
- **`frontend/app.py`** depende de `src/` (import `from src.invoke
  import ask_agent`). **Nunca** o inverso: `src/` não importa
  `streamlit`.
- **`tests/`** espelha a árvore de fontes: `tests/test_invoke.py` mapeia
  para `src/invoke.py`; se `agent/` ganhar testes, `tests/agent/`
  espelha `agent/`. Um `tests/conftest.py` centraliza fixtures de mock
  do cliente `bedrock-agentcore` para não repetir o `patch("boto3.client")`
  visto no `test_ask_agent_returns_answer` de `tech-env.md`.

A direção da dependência é: `frontend/ → src/ → boto3`; `agent/` isolado.
Isso é o que permite trocar o frontend (Streamlit hoje, outra UI depois)
ou trocar o agente sem quebrar o outro lado.

### Configuração ruff — não deixar no default

O default puro do ruff (`ruff check` sem seleção) ativa só `E`+`F`
(pycodestyle errors + Pyflakes), o que é fino demais para um codebase
boto3 onde erros de idioma Python 3.12 e bugs sutis do bugbear pegam mais
do que a inconsistência de estilo. Configurar no `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = [
    "E", "F",     # pycodestyle + pyflakes
    "I",          # isort (ordem de imports determinística)
    "UP",         # pyupgrade — força idiomas 3.12 (ex.: `str | None` em vez de `Optional[str]`)
    "B",          # flake8-bugbear — pega `mutable default args`, `except Exception: pass`
    "SIM",        # flake8-simplify
]
ignore = [
    "E501",       # line-too-long — o formatter já cobre; deixar o ruff só reclamar de comprimento em prosa
]

[tool.ruff.format]
# usar o formatter do ruff (equivalente ao black), sem black separado
quote-style = "double"
```

Rodar `ruff check --fix` e `ruff format` antes de cada commit. Bloqueio
manual (não há CI), mas violação não entra no `main` via squash-merge.

### Type hints — obrigatórios na fronteira, encorajados internamente

O draft diz "encorajados nas funções públicas". Especializar: **exigir**
type hints em toda função exportada por `src/` e `frontend/` (é o
contrato de camada) e em toda tool do agente (`agent/agent.py`). Interno
do módulo (helpers privados prefixados `_`) fica encorajado, não
obrigatório. Preferir sintaxe PEP 604 do Python 3.12: `str | None` no
lugar de `Optional[str]`, `list[str]` no lugar de `List[str]`. O ruff
`UP` já sinaliza os desvios.

### Naming — além do PEP 8

- **Env vars**: `UPPER_SNAKE_CASE`, sem prefixo de app (o escopo do
  workshop é pequeno o suficiente para não colidir). Conjunto fixo:
  `AGENT_RUNTIME_ARN`, `KNOWLEDGE_BASE_ID`, `AWS_REGION`. `AWS_REGION`
  substitui a região hard-coded (`region_name="us-east-1"`) nos exemplos
  de `tech-env.md`, mas com fallback para `us-east-1` (regra dura).
- **Módulos**: sem prefixo (é `invoke.py`, não `chatbot_invoke.py`) — o
  pacote é o namespace suficiente.
- **`session_id`**: gerado via `uuid.uuid4()` no frontend (como em
  `tech-env.md` § "Frontend Example"); nunca aceito do input do usuário.
  Persistido em `st.session_state`.

### Tratamento de erro — política mínima para chamadas boto3

`tech-env.md` mostra `try/except` em prosa mas o exemplo de
`ask_agent` não o wrappa — o comportamento atual vaza a `ClientError`
para o Streamlit. Padrão para este projeto:

- **Em `src/invoke.py`**: capturar `botocore.exceptions.ClientError` na
  chamada `invoke_agent_runtime`. Se o `Code` for `ThrottlingException`,
  `ValidationException` ou `ResourceNotFoundException`, relevantar como
  uma exceção de domínio simples (ex.: `AgentInvocationError`) com uma
  mensagem legível. Não engolir silenciosamente.
- **Em `frontend/app.py`**: capturar essa `AgentInvocationError` e
  mostrar via `st.error(...)` — nunca deixar o traceback aparecer no
  chat. Logar o `ClientError` original via `logging.getLogger(__name__)`
  para debug local.
- **Validação de input (regra dura CT-?)**: o guard de 4000 chars mora
  em `src/invoke.py` (antes da chamada boto3), não no frontend — assim
  qualquer chamador da função herda a validação. Levantar `ValueError`
  quando exceder; frontend converte para `st.warning(...)`.
- **Escopo do `except`**: **nunca** `except Exception: pass` nem `except:
  ...` sem re-raise. A regra `B` do ruff (bugbear) já sinaliza; deixar
  ativa.

Este bloco é o que mais falta no draft — sem ele, o piso de 80% de
cobertura mede código que se comporta imprevisivelmente quando o
AgentCore lança `ThrottlingException` (comum em contas de workshop com
quota compartilhada).

### Idioma Python 3.12 para boto3 + Strands

- Um único cliente boto3 por módulo, criado no top-level (como em
  `tech-env.md`) — não recriar por chamada. É idempotente e barato.
- `pathlib.Path` para qualquer caminho de arquivo (não `os.path.join`).
- `json.dumps(...).encode()` como no exemplo — não `bytes(json.dumps(...),
  "utf-8")`.
- Para o `retrieve` do Strands, deixar o `KNOWLEDGE_BASE_ID` via env
  var (pattern em `tech-env.md` § "Knowledge Base Tool"); não passar
  como argumento na tool call, o SDK resolve por env.

### Não adotar

- **mypy / pyright**: fora do escopo do workshop de 2 dias. O `ruff
  UP` + type hints legíveis já dão o valor esperado sem custo de
  configuração de type-checker.
- **pre-commit hooks**: não configurar. Overhead de setup > valor para
  workshop de 2 dias sem CI.
- **`Result` types / oxide**: erro é exceção idiomática em Python. Não
  introduzir Result/Either.

## Positions

- AGREE: Adotar `ruff` como single-tool (linter + formatter) — para uma
  janela de 2 dias, uma configuração única com um binário elimina o
  bikeshedding sobre black-vs-ruff-format e mantém a barreira de entrada
  baixa para participantes iniciantes.
- OBJECT: `## Code Style` diz "nenhuma além do que o `ruff` já cobre" e
  para o padrão de tratamento de erro em torno de `invoke_agent_runtime`
  — o default puro do ruff é `E`+`F` só (fino demais para um codebase
  boto3, especialmente sem o bugbear `B` para `mutable default args` e
  `bare except`), e `tech-env.md` menciona `try/except` em prosa mas o
  exemplo canônico vaza `ClientError` para o Streamlit; sem uma
  política mínima de erro (ClientError → domain error → `st.error`), o
  chatbot fica frágil em quotas compartilhadas de workshop.
