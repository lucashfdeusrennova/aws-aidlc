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

- 2026-08-24T21:30:00Z — Interpretacao: decomposicao em 3 unidades espelhando as fronteiras de deploy: U1 chat-frontend (ui, Streamlit local), U2 hr-agent (service, Strands rodando dentro do AgentCore Runtime), U3 infra (packaging, stack CDK). AgentInvoker fica dentro de U1 porque e importado pelo frontend e nao tem lifecycle proprio de deploy (o `src/` mora no mesmo repo do frontend).
- 2026-08-24T21:30:00Z — Tradeoff: DAG com U3 depends_on: [U2] (o stack CDK empacota o agente em container/imagem) e U1 independente (frontend testavel isoladamente com invoker mockado). U1 usa ARNs de U3 em RUNTIME, mas nao em build/dev-time.
- 2026-08-24T21:30:00Z — Interpretacao: 3 unidades = 3 kinds distintos (ui, service, packaging), o que evita colocar CDK como service e ativar a matriz de design errada.
- 2026-08-24T21:45:00Z — Interpretacao: US1.6 e US1.7 mapeados unicamente para U1 no traceability, embora tenham componente de dominio no AgentInvoker (guard primario, error mapping). Como AgentInvoker mora no mesmo unit target-de-deploy que o frontend (U1), a linha e do unit `chat-frontend`. Nao ha cross-unit real; apenas cross-component dentro de U1.
- 2026-08-24T21:45:00Z — Tradeoff: U3 (infra) sem story direta e proposital - stories mapeiam para codigo de dominio, U3 e packaging/provisioning. As FR2.x/FR3/NFR5/NFR7 que U3 realiza sao rastreadas em requirements-analysis. delivery-planning saberá que U3 e pre-condicao operacional dos ACs de U2.
- 2026-08-24T21:45:00Z — Deviation: unit-of-work-dependency.md nao lista U1 como depending on U3 apesar do runtime deployment coupling (U1 le ARN do CDK output). Preservei "build-time only" como forma da edge, alinhado com nota do stage sobre topologia vs sequencia economica. Marca esse coupling como "runtime dependency, not build dep" em prosa.
