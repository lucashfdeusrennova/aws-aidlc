**Collaborator:** aidlc-developer-agent

# Unit Test Instructions - hr-agent

## Sources

- Ver `code-summary.md` neste diretorio.

## How to run

```bash
pytest tests/test_agent.py -v
pytest --cov=agent --cov-fail-under=80
```

## Coverage plan

11 testes em `tests/test_agent.py`:
- 4 asserts de fiacao do system prompt.
- 3 testes de `_classify_outcome`.
- 3 testes de fail-fast (BR6.3, BR6.4, env var ausente).
- 2 testes BR4.3 MUST (LGPD refuse + echo).
- 1 teste fallback.
- 1 teste log LGPD-safe (NFR4.1.3 defense-in-depth).

## Assumptions & Open Questions

None.
