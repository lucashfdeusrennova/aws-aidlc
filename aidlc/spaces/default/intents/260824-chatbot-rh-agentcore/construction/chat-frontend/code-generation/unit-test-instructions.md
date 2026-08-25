**Collaborator:** aidlc-developer-agent

# Unit Test Instructions - Consolidated

## Sources

- [tp] `team.md § Testing Posture` - pytest, cov floor 80%, mock strategy.
- [rl] `rules.md` § BR4.3 (LGPD teste MUST).

## How to run

```bash
pip install -r requirements-dev.txt
pytest --cov=agent --cov=src --cov-fail-under=80
```

Sem CI - roda local antes do commit no `main`.

## Coverage plan

- `agent/agent.py`: 11 testes cobrindo prompt sections, `_classify_outcome`,
  fail-fast em label/env, guardrail LGPD (BR4.3 MUST), log estruturado
  LGPD-safe.
- `src/invoke.py`: 6 testes cobrindo happy path, guard 4000 chars,
  ClientError propagation, resposta vazia, AGENT_RUNTIME_ARN ausente,
  shape antigo do payload.
- `frontend/app.py`: nao testado por unit (validacao manual no demo,
  ver `team.md § Camadas nao testaveis por unidade`).
- `infra/stack.py`: nao testado por unit (validado por `cdk synth`).

## Mock strategy

Ver `tests/conftest.py`:

- Env vars mandatorios via `monkeypatch.setenv` (`_env_agent_runtime`).
- `boto3.client("bedrock-agentcore")` mockado via substituicao
  `invoke_mod.agentcore_client` (fixture `mock_agentcore`).
- `BedrockModel`, `Agent`, `retrieve` mockados via `patch("agent.agent...")`
  (fixture `mock_bedrock_model`).

## MUST tests

- `tests/test_agent.py::test_lgpd_guardrail_refuses_salary` - BR4.3.
- `tests/test_agent.py::test_log_event_never_contains_prompt_or_response`
  - NFR4.1.3 defense-in-depth.

## Assumptions & Open Questions

None.
