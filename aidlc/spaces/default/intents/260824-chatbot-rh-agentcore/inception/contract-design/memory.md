<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->

- 2026-08-24T22:00:00Z — Interpretacao: no MVP nao ha API publica/externa; a UI e local (`streamlit run` no notebook). As fronteiras contratuais sao (a) U1->U2 mediada pelo AgentCore Runtime, (b) U3->U1 outputs do CDK stack, (c) U3->U2 env vars via IAM role.
- 2026-08-24T22:00:00Z — Interpretacao: o contrato central do MVP e o payload JSON de `invoke_agent_runtime`. AWS define o envelope do servico (runtimeSessionId, agentRuntimeArn, payload bytes); nos definimos o CONTEUDO do payload (o body user->agent) e o formato da resposta.
- 2026-08-24T22:00:00Z — Tradeoff: usar shared-schema YAML para os 3 contratos (payload JSON + CFN outputs + env vars) em vez de OpenAPI. Nao ha REST/HTTP proprio; OpenAPI seria over-engineering. AsyncAPI tambem nao se aplica (fluxo sync).
- 2026-08-24T22:10:00Z — Interpretacao: escolhi Q1=B (payload estruturado com `model_id` + `session_id` no response) porque materializa AC4.1.2 (`model_id` observavel) de forma explicita. Q1=A seria mais simples mas descumpre o contrato de observabilidade.
- 2026-08-24T22:10:00Z — Open question: contract-summary.md deixa 3 open questions relacionadas ao echo de `model_id`, formato do fallback US1.4, e necessidade de INFERENCE_PROFILE_ARN_* env vars em U2. Todas para `functional-design` resolver.
- 2026-08-24T22:10:00Z — Tradeoff: nao criei bloco OpenAPI porque o boundary U1->U2 nao e REST; e um envelope AWS. Documentei o AWS-owned contract como referencia para o leitor entender o quadro completo.
