**Collaborator:** aidlc-architect-agent

# Architecture Decision Records - Domain Design

Registro durável das decisoes significativas tomadas em Domain Design.
Complementa a coluna "Rationale" de `components.md` (justificativa
por-componente) com Context/Decision/Consequences/Alternatives Rejected
por decisao arquitetural.

Fontes consumidas: `requirements.md`, `stories.md`, `team-practices.md`.

## Sources

- [rq] `requirements.md` - FR1-FR9 e NFR1-NFR10.
- [st] `stories.md` - 11 stories, 28 ACs.
- [tp] `team-practices.md` - fronteiras de camada, stack, error handling policy.

## ADR-001: Decompor em 3 componentes espelhando as fronteiras de camada

**Context.** As fronteiras de camada `frontend/ -> src/ -> boto3` mais
`agent/` isolado ja estao afirmadas em `team-practices.md § Code Style`
(regra de dependencia do repositorio). O escopo `mvp` tem janela de 2 dias
com deploy local + AgentCore Runtime em sandbox. As 11 user stories cabem
naturalmente em UI (US1.9, US4.1, US1.6, US1.7), invocacao (US1.6, US1.7)
e agente (US1.1-1.5, US2.1, US3.1). Precisavamos decidir se 3 fronteiras
de codigo geram 3 componentes distintos ou se algo pode ser fundido.

**Decision.** Decompor em **3 componentes**: `HRChatFrontend`,
`AgentInvoker` e `HRAgent`, alinhados 1:1 com `frontend/`, `src/` e
`agent/`. Referenciado em [rq] e [tp].

**Consequences (+).**

- Cada componente e testavel isoladamente com estrategia de mock diferente
  (fixtures em `tests/conftest.py` para o cliente `bedrock-agentcore`;
  `BedrockModel` mockado e `retrieve` stubada para `HRAgent`).
- A fronteira `frontend/ -> src/ -> boto3` do `team-practices` fica
  auto-enforcada: nao ha componente `HRChatApp` que possa importar boto3
  diretamente.
- `HRAgent` sendo componente proprio deixa claro que roda em processo
  separado (microVM AgentCore Runtime) e nao pode importar de `src/` ou
  `frontend/`.
- Contratos de camada explicitos casam com AC1.7.1/AC1.7.2 (erro definido
  no invoker, tratado no frontend).

**Consequences (-).**

- 3 componentes = 3 conjuntos de responsabilidades para manter alinhados.
  Aceitavel na janela de 2 dias porque as fronteiras ja estao afirmadas.

**Alternatives Rejected.**

- **Opcao B - fundir `HRChatFrontend` + `AgentInvoker` em `HRChatApp`**:
  compacto (2 componentes), mas obriga o frontend a importar boto3 direto
  ou torna a fronteira `frontend/ -> src/` ambigua. Perderiamos a
  testabilidade isolada do guard de 4000 chars e da politica de erro.
- **Opcao C - 4 componentes com `KnowledgeBaseRetriever` proprio**: a tool
  `retrieve` e resolvida pelo Strands SDK via env var `KNOWLEDGE_BASE_ID`;
  nao ha logica de negocio nossa a possuir. Manter como
  `external_dependency` do `HRAgent`.

## ADR-002: `AgentInvocationError` como excecao de dominio, nao entity

**Context.** O tratamento de erro de invocacao ao AgentCore Runtime esta
ancorado em US1.7 (AC1.7.1, AC1.7.2, AC1.7.3) e no `team-practices.md §
Code Style Error handling policy`: `src/invoke.py` captura
`ClientError` do botocore e re-eleva como `AgentInvocationError` legivel;
`frontend/app.py` captura e renderiza como `st.error(...)` sem stack trace.
A pergunta era se capturar `AgentInvocationError` como entity de dominio
(estrutura de dados com identifier + attributes) ou como excecao Python
idiomatica.

**Decision.** Tratar como **excecao Python idiomatica**, propriedade do
componente `AgentInvoker` (definida em `src/invoke.py`), sem entrada na
lista de `entities:` do componente. Sua semantica vive no `behaviour` do
`AgentInvoker` e no ADR-003.

**Consequences (+).**

- Alinhado com [tp § Code Style, "Result / Either types - erro e excecao
  idiomatica em Python"].
- Sem ruido em `components.md` com entities que nao representam dado
  persistido.
- `AgentInvocationError` pode ser subclasseada no futuro (`ThrottlingError`,
  `TimeoutError`) sem mexer no domain model.

**Consequences (-).**

- Menos "explicito" no diagrama de entidades: quem le so `entities` nao ve
  o formato da excecao. Compensado por `behaviour` e ADR-003.

**Alternatives Rejected.**

- **`AgentInvocationError` como entity de `AgentInvoker`**: exageraria o
  modelo de dominio; um DTO de erro faz sentido em RPC entre servicos,
  nao em Python single-process.
- **Fundir `AgentInvocationError` com `ValueError` do guard 4000 chars**:
  mistura input-validation (`ValueError`, pre-invocacao) com erro de
  invocacao (`AgentInvocationError`, pos-chamada). Semanticas diferentes,
  mensagens diferentes ao usuario (US1.6 `st.warning` vs US1.7 `st.error`).

## ADR-003: `session_id` gerado server-side no `HRChatFrontend`

**Context.** Uma pergunta legitima seria: onde geramos o `session_id`? No
frontend, no invoker, ou no proprio AgentCore Runtime? A regra NFR3.2 e o
`project.md § Mandated` fixam: "gerado server-side via `uuid.uuid4()`,
nunca aceito de input do usuario, query string ou header". Precisavamos
decidir qual componente e o dono.

**Decision.** `HRChatFrontend` **gera** o `session_id` (via `uuid.uuid4()`
no primeiro carregamento e em "Limpar conversa"). `AgentInvoker` apenas
**repassa** para o AgentCore Runtime como `runtimeSessionId`.

**Consequences (+).**

- Como o frontend nao expoe endpoint HTTP proprio (roda local no notebook),
  "server-side" no contexto dessa demo significa "no processo Python", e
  o Streamlit e onde a sessao logica nasce. NFR3.2 continua satisfeita.
- Isolamento de sessao no AgentCore Runtime (microVM por `session_id`)
  fica garantido pelo servico.
- Testable: US1.9 (AC1.9.2) verifica que o botao "Limpar conversa" gera
  um novo `session_id`.

**Consequences (-).**

- Se em algum momento o frontend for hospedado em servidor multi-usuario
  (fora do escopo `mvp`, mas concebivel para pos-demo), a mesma regra
  precisa valer: cada nova aba HTTP gera seu proprio `session_id` no
  primeiro request; nunca aceitar de cookie ou query string.

**Alternatives Rejected.**

- **Gerar no `AgentInvoker`**: o invoker nao "conhece" a nocao de sessao
  logica do usuario (troca de modelo, botao limpar); apenas repassa. Se
  o invoker gerasse, o botao "Limpar conversa" precisaria falar com o
  invoker so para trocar de UUID, quebrando a simplicidade.
- **Deixar o AgentCore Runtime gerar** (nao passar `session_id`): pode
  funcionar para invocacao single-shot, mas quebra AC1.9.4 (proxima
  pergunta apos limpar usa o novo `session_id` conhecido pelo cliente
  para futura observabilidade).

## ADR-004: Entities minimas no dominio do frontend

**Context.** O `HRChatFrontend` gerencia estado de UI via
`st.session_state`. Precisavamos decidir quais estruturas subir para
entities de dominio (Q3 do questionnaire).

**Decision.** Capturar tres entities: `ChatSession`, `ChatMessage`,
`ModelChoice`. Ownership: todas do `HRChatFrontend`.

**Consequences (+).**

- `ChatSession` e o container natural para `session_id`, `messages` e
  `model_id` (o que Streamlit ja armazena em `st.session_state`).
- `ChatMessage` explicita o par (`role`, `content`) que renderiza cada
  bolha, casando com o snippet de `interaction-spec.md § C5`.
- `ModelChoice` da nome ao dicionario `MODEL_ARNS` de
  `refined-mockups/mockups.md § US4.1`, tornando explicito que rotulo
  humano e ARN sao atributos de uma escolha, nao string solta.
- Coerente com AC4.1.3 (`inference_profile_arn` como atributo obriga
  code-generation a materializar o ARN completo).

**Consequences (-).**

- Sem entity de erro (ADR-002) e sem entity de prompt (nao capturado
  neste MVP). Se necessario, adicionar em contract-design ou pos-demo.

**Alternatives Rejected.**

- **Apenas `ChatMessage` + `ChatSession`, sem `ModelChoice`**: o
  dicionario `MODEL_ARNS` vira "magic dict" sem ownership explicito no
  domain. Perde a rastreabilidade de AC4.1.1/AC4.1.3.
- **Adicionar `SystemPrompt` como entity do `HRAgent`**: excedente no MVP;
  o system prompt e uma string fixa no codigo, nao consultada nem
  persistida em nenhum store proprio.

## ADR-005: Interacoes entre componentes `sync`, sem streaming

**Context.** AgentCore Runtime + Strands + Bedrock podem operar em modo
streaming (SSE), mas o MVP tem latencia alvo de <5s por resposta (NFR1.1)
e usa `st.spinner("Consultando base de conhecimento...")` como feedback
(AC1.1.4). Precisavamos escolher entre `sync` simples e `streaming`.

**Decision.** Todas as interacoes internas entre componentes sao `sync`
(chamada de funcao Python bloqueante). O AgentInvoker faz uma chamada
`invoke_agent_runtime` single-shot; a resposta chega inteira e e
renderizada de uma vez.

**Consequences (+).**

- Codigo simples, sem gerenciamento manual de streaming, backpressure ou
  cancelamento.
- `st.spinner` do Streamlit cobre a percepcao de latencia; 5s single-shot
  e aceitavel para chat de RH.
- Facilita testes unitarios (mock retorna string, nao gerador).

**Consequences (-).**

- Sem "typing indicator" avancado; se a resposta demorar 4s, o usuario
  ve apenas o spinner ate ela aparecer completa.
- Se latencia crescer > 5s por qualquer motivo (cold start, throttling),
  a UX degrada. Coberto por `AgentInvocationError` (US1.7) via timeout.

**Alternatives Rejected.**

- **Streaming SSE**: valor real quando respostas ultrapassam 8-10s ou
  quando ha necessidade de mostrar "digitando..." token a token; nao vale
  o custo de setup em 2 dias.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
