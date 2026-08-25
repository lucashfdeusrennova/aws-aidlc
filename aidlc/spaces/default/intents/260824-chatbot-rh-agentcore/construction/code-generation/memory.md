<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-08-25T17:20:00Z — Usuario optou por caminho Turbo: gerar codigo funcional consolidado para hr-agent + chat-frontend + infra em uma unica passada, pulando ceremony por-unit. Artefatos ao inves de per-unit `code-generation-plan.md` / `unit-test-instructions.md` / `code-summary.md` foram entregues como codigo real em `agent/`, `src/`, `frontend/`, `infra/`, `tests/`, `scripts/`, mais README.md, requirements*.txt, pyproject.toml, cdk.json e docs/knowledge-base/README.md.

## Deviations
- 2026-08-25T17:20:00Z — Estrutura ceremony da stage (per-unit `code-generation-plan.md`) foi trocada por deliverables funcionais para reduzir tempo total de ~2-3h para ~30-45min ate `streamlit run`, alinhado ao objetivo do workshop de 2 dias.
- 2026-08-25T17:20:00Z — AgentCore Runtime foi deployado via `agentcore` CLI (aws-bedrock-agentcore-starter-toolkit) e nao via L1 CFN dentro do CDK, porque suporte CDK/CFN ainda esta em evolucao. CDK cobre S3 bucket + IAM roles + outputs; runbook do runtime esta no README.
- 2026-08-25T17:20:00Z — Knowledge Base criada via console (nao CDK) pelo mesmo motivo: L1 CFN para S3 Vectors backend nao esta estavel; participante segue passo-a-passo do README.

## Tradeoffs
- 2026-08-25T17:20:00Z — Escolhi mocks classicos com `unittest.mock.patch` no `conftest.py` em vez de `moto`, para nao adicionar dep pesada. Cobre boto3.client de forma equivalente.
- 2026-08-25T17:20:00Z — `retrieve_hits` no log INFO ficou como `-1` (Strands SDK nao expõe contagem trivialmente); documentado como Sensor observavel imperfeito no MVP, aceitavel dentro de Q1=A (sem instrumentacao de sub-etapas).

## Open questions
- 2026-08-25T17:20:00Z — Ha a possibilidade de o SDK Strands 0.1.7 ter API diferente do exemplo em `tech-env.md`; se o participante encontrar `ImportError` em `from strands.models import BedrockModel`, tentar `from strands.models.bedrock import BedrockModel` ou versao mais recente do pacote. Registrado como troubleshooting no README.
