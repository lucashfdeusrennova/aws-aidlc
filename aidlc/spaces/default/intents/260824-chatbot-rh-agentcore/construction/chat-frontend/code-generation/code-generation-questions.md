# Code Generation Questions — chat-frontend (U1)

## Plan Approval

O plano completo está em `code-generation-plan.md` (8 steps numerados, Testing Contract embedded, story→step map inline). As instruções de teste unit-scoped estão em `unit-test-instructions.md` (comando `pytest tests/test_invoke.py --cov=src --cov-fail-under=80`, 8 testes cobrindo guard 4000, session_id validation, error mapping, happy path e empty-response).

Resumo do que vai ser gerado:

- `frontend/app.py` — Streamlit UI (chat + sidebar model selector + botão "Limpar conversa"), com guard 4000 na submissão, mapping `AgentInvocationError` → `st.error`, log JSON via `LoggerAdapter`.
- `src/invoke.py` — `ask_agent(prompt, session_id, model_id) -> str` com cliente boto3 module-level, guard 4000, regex UUID de session_id (defense in depth), payload C1 (`{"prompt", "context.model_id"}`), mapping `ClientError` → `AgentInvocationError` com copy pt-BR determinística por tipo, `AgentInvocationError` classe própria.
- `tests/conftest.py` + `tests/test_invoke.py` — 8 testes cobrindo `src/invoke.py`, coverage ≥ 80% linhas.
- `pyproject.toml` — ruff (select default `E`+`F`), pytest config.
- `requirements.txt` (`streamlit==1.38.0`, `boto3==1.42.97`) + `requirements-dev.txt` (`pytest==8.3.3`, `pytest-cov==5.0.0`, `ruff==0.6.9`).
- `.gitignore` atualizado com `.env`, `credentials`, `*.pem`, `*.pfx`, `aws-credentials*`, `**/secrets/**`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `htmlcov/`, `.coverage`.

Boundaries respeitadas (`team.md § Code Style`):

- `frontend/ → src/ → boto3` unidirecional.
- `src/` NÃO importa `streamlit`.
- `frontend/` NÃO importa `boto3` direto.

Testing Contract (methodology `test-after`, order `implement each applicable testable layer, then write and run that layer's tests`, floor 80% linhas): embedded no `code-generation-plan.md`. Não será re-resolvido pelo developer-agent.

- Approve Plan
- Request Changes

[Approval Fingerprint]: sha256:77cdef6bec15657e3cbf72e762667c4ee65dd79937dcec9adaf6ffcb49d60d8f

[Answer]: Approve Plan
