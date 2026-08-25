<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-08-25T14:52:00Z — chat-frontend (kind: ui) sem infra AWS propria: os 3 artefatos (infrastructure-specification, monitoring-design, cicd-pipeline) documentam explicitamente a natureza "no-cloud-infra" com N/A justificado. Toda infra AWS relevante mora em U3 (infra). Shared Infrastructure tabela lista AGENT_RUNTIME_ARN como recurso compartilhado owner U3 -> consumer U1.
- 2026-08-25T14:52:00Z — monitoring "log-only" (Q2=A) com tabelas de Metrics/Alerts/SLIs vazias mas explicitamente justificadas. O SLI operacional relevante (frontend_elapsed <=1s) mora em scripts/smoke.py e team.md § Testing Posture, nao neste stage.

## Deviations
- 2026-08-25T14:52:00Z — cicd-pipeline.md documenta um checklist local (`ruff format` + `ruff check` + `pytest --cov`) como substituto ao pipeline hospedado (Q3=A). Nao e "CI" no sentido estrito, mas honra a cerimonia de gate local afirmada em team.md § Testing Posture. Migration path (GitHub Actions post-MVP) documentado como referencia futura.

## Tradeoffs
- 2026-08-25T14:52:00Z — Q1=A (tabelas substantivas com N/A) versus Q1=C (redirect completo). Escolhemos verbosidade para audibilidade do sensor `required-sections` e do `traceability`. Custo: uma tabela cheia de N/A pode parecer ceremoniosa; ganho: proximo leitor entende explicitamente que o unit nao tem infra AWS propria, sem precisar cross-referenciar U3.

## Open questions
- 2026-08-25T14:52:00Z — se o time promover este projeto pos-workshop e adotar GitHub Actions, o Migration path em cicd-pipeline.md deveria ser expandido em um novo NFR/design cycle. Registrado para nao esquecer.
