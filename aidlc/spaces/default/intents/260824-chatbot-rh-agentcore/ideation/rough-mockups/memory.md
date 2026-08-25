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

- 2026-08-24T19:15:00Z — Interpretação: interface e Streamlit (chat unico), com titulo, historico e input; o `tech-env.md` traz codigo de referencia que ja define o layout basico. Vou usar isso como ponto de partida e pedir confirmacao das poucas variacoes possiveis (indicador de fonte, elementos adicionais como troca de modelo).
- 2026-08-24T19:15:00Z — Tradeoff: depth Standard sugere 5-8 perguntas, mas UI e um chat de tela unica; vou ficar entre 3-5 para nao inflar. Perguntas focam em: elementos visiveis alem do chat, indicacao de fonte na resposta, tratamento de erro, forma factor.
- 2026-08-24T19:15:00Z — Tradeoff: Streamlit tem acessibilidade limitada (compoem HTML padrao mas nao e WCAG-certificado); vou registrar uma nota de acessibilidade rasa e sinalizar que WCAG completo requer teste manual com tecnologias assistivas.
