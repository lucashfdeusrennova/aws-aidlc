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

- 2026-08-24T20:50:00Z — Interpretação: interface e Streamlit puro, sem CSS customizado. "Refinar" o mockup significa: (a) mapear cada componente do wireframe para o widget Streamlit correspondente, (b) especificar interacoes/estados exatos, (c) documentar o "design system" implicito do Streamlit, (d) accessibility checklist com WCAG 2.1 AA como referencia (nao certificado).
- 2026-08-24T20:50:00Z — Interpretação: `stories.md` ja carrega 28 ACs BDD com strings literais e estados esperados. O trabalho aqui e transformar cada AC em spec de UI concreto (widget + estado + copy).
- 2026-08-24T20:50:00Z — Tradeoff: perguntas focadas em: (a) mockup ASCII refinado vs mockup textual, (b) linguagem/tom das mensagens do bot (breve vs detalhado), (c) design system - Streamlit padrao vs tema customizado.
- 2026-08-24T20:55:00Z — Interpretacao: Q1-Q4 sem resposta explicita do humano; adotados defaults MVP (Q1=A, Q2=A, Q3=D, Q4=A) e confirmados pelo humano com "pode continuar".
- 2026-08-24T20:55:00Z — Tradeoff (contador de caracteres): st.chat_input nao expoe valor ao vivo. Adotada Opcao A (aviso apos submit entre 3501-4000) em vez de trocar para st.text_area + botao. Simples, mantem padrao Streamlit para chat; Opcao B fica registrada como caminho de refino pos-demo.
- 2026-08-24T20:55:00Z — Tradeoff (limpar conversa): sem confirmacao intermediaria ("Tem certeza?"). Justificativa: clique acidental so custa recomecar a conversa, valor de confirm dialog nao compensa o atrito no MVP.
- 2026-08-24T20:55:00Z — Deviation (WCAG 3.1.1 Language of Page): st.set_page_config nao define lang="pt-BR" nativamente e Q2=A proibe HTML custom. Aceito como Gap consciente; registrado explicitamente em accessibility-checklist.md.
- 2026-08-24T20:55:00Z — Interpretacao (bolha de erro): em US1.7, st.error e renderizado no lugar da bolha do assistente e NAO faz append a messages (evita bolha fantasma no historico). AC1.7.2 nao especifica, entao a decisao ficou aqui.
- 2026-08-24T20:55:00Z — Open question: contrato final de src.invoke.ask_agent(prompt, session_id, model_id) -> str e assumido; a resolucao definitiva pertence a contract-design. Se o formato variar, interaction-spec § C8 precisa ajuste antes de code-generation.
