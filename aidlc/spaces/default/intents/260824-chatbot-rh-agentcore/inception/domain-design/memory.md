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

- 2026-08-24T21:00:00Z — Interpretacao: as fronteiras de camada ja fixadas em team-practices § Code Style (`frontend/ -> src/ -> boto3`, `agent/` isolado) pre-definem os 3 componentes naturais. Perguntas focam em confirmar shape das entities e granularidade (fundir invoker+frontend ou separar retriever).
- 2026-08-24T21:00:00Z — Tradeoff: infra CDK (stack, bucket, KB, runtime) NAO e componente - e infra deployada; entra em `external_dependencies` de cada componente que consome.
- 2026-08-24T21:15:00Z — Interpretacao: US1.6 e US1.7 mapeados para AgentInvoker (dono do guard 4000 primario e da politica ClientError -> AgentInvocationError). O frontend faz defense-in-depth do guard e renderiza o warning/error, mas a decisao de dominio pertence ao invoker.
- 2026-08-24T21:15:00Z — Tradeoff: ADR-002 optou por AgentInvocationError como excecao Python idiomatica, nao entity. Reduz ruido no modelo de dominio, alinhado com [tp § Code Style "erro e excecao idiomatica em Python"].
- 2026-08-24T21:15:00Z — Interpretacao: infra (bucket S3, KB, AgentCore Runtime, stack CDK) NAO entra como componente porque nao ha codigo de dominio proprio. Aparece como external_dependencies. O CDK stack em si e infra-como-codigo; sera tratado em infrastructure-design.
- 2026-08-24T21:15:00Z — Deviation: nao gerei ADR sobre streaming vs sync (ADR-005) como decisao Q4 formal na questions file, mas capturei o rationale em decisions.md. Q4=A ja era um framing pre-decidido.
