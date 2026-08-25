**Collaborator:** aidlc-architect-agent

# Story Map por Unit - Chatbot de RH com Bedrock AgentCore

Mapeia cada uma das 11 user stories (`stories.md`) para a unidade
declarada em `unit-of-work.md` que a implementa. Serve como contrato de
entrada para `delivery-planning` (Bolt sequencing) e como validacao de
cobertura downstream.

Fontes consumidas: `components.md`, `decisions.md`, `requirements.md`,
`stories.md`, `unit-of-work.md`.

## Sources

- [cp] `components.md` - 3 componentes.
- [ad] `decisions.md` - ADR-001 (decomposicao) e ADR-002 (erro como
  excecao no invoker).
- [rq] `requirements.md` - FR/NFR.
- [st] `stories.md` - 11 stories, 28 ACs.
- [uw] `unit-of-work.md` - 3 unidades U1, U2, U3.

## Story -> Unit

| Story  | Titulo curto                        | Unit ID | Directory          | Componente principal | Notas cross-unit                                  |
| ------ | ----------------------------------- | ------- | ------------------ | -------------------- | ------------------------------------------------- |
| US1.1  | Consultar politicas gerais de RH    | U2      | `u2-hr-agent`      | HRAgent              | Depende de U3 provisionar KB e U1 renderizar spinner (AC1.1.4). |
| US1.2  | Consultar politica de ferias        | U2      | `u2-hr-agent`      | HRAgent              | idem US1.1.                                       |
| US1.3  | Consultar feriados da empresa       | U2      | `u2-hr-agent`      | HRAgent              | idem US1.1.                                       |
| US1.4  | Fallback "nao encontrei"            | U2      | `u2-hr-agent`      | HRAgent              | Contrato de contains no system prompt (AC1.4.1).  |
| US1.5  | Recusa LGPD                         | U2      | `u2-hr-agent`      | HRAgent              | System prompt + teste NFR8.2 (guardrail unitario com stub de `retrieve`). |
| US1.6  | Input >4000 chars rejeitado         | U1      | `u1-chat-frontend` | AgentInvoker + Streamlit | Guard primario em `src/invoke.py::ask_agent` (AgentInvoker); frontend re-guardua para `st.warning` (AC1.6.1). |
| US1.7  | Erro do AgentCore amigavel          | U1      | `u1-chat-frontend` | AgentInvoker + Streamlit | Mapping `ClientError -> AgentInvocationError` em `src/invoke.py`; frontend renderiza `st.error` (AC1.7.2). |
| US1.9  | Iniciar nova conversa (limpar)      | U1      | `u1-chat-frontend` | HRChatFrontend       | Handler local via `uuid.uuid4()` e reset de `st.session_state.messages` (AC1.9.2, AC1.9.3). |
| US2.1  | Consultar processo de onboarding    | U2      | `u2-hr-agent`      | HRAgent              | idem US1.1 (fonte: onboarding_checklist.pdf).     |
| US3.1  | Consultar avaliacao de desempenho   | U2      | `u2-hr-agent`      | HRAgent              | AC3.1.2 cross-referencia US1.5 (recusa dados individuais). |
| US4.1  | Trocar modelo de chat (Operador)    | U1      | `u1-chat-frontend` | HRChatFrontend       | Dicionario `MODEL_ARNS` em `frontend/app.py`; ARN passado a chamada `invoke_agent_runtime` (AC4.1.3). |

## Cross-cutting concerns

Nenhuma story cruza duas unidades no MVP - o mapeamento e 1:1 por design.
Alguns ACs, porem, dependem de configuracao provisionada por U3 antes de
o comportamento poder ser observado end-to-end:

- **AC1.1.1 / AC1.2.1 / AC1.3.1 / AC2.1.1 / AC3.1.1** (consulta com <5s
  em portugues) exigem: U3 com KB indexada + `StartIngestionJob`
  executado antes da demo [rq FR2.2][tp § Deployment].
- **AC1.9.4** (nova sessao usa novo `session_id` no proximo turno) exige:
  U3 com AgentCore Runtime ativo. A implementacao vive em U1, mas a
  validacao E2E depende de U3 deployado.
- **AC4.1.3** (ARN de inference profile) exige: U3 com IAM execution role
  de U2 tendo `bedrock:InvokeModel*` no inference profile especifico
  [project.md § Mandated].

Estas ligacoes runtime nao viram entradas em `unit-of-work-dependency.md
§ Edge Block` (que registra dependencias de build); ficam registradas
aqui para que `delivery-planning` saiba que a validacao E2E das stories
de U2 exige U3 deployado.

## Story implementation order dentro de cada unit

Esta stage nao decide ordem entre unidades; apenas sugere granularidade
de commits dentro de cada uma. **A ordem final entre e dentro de bolts
pertence a `delivery-planning`.**

### U1 `chat-frontend` (5 stories)

Sugestao de granularidade (agrupavel por commit / feature branch):

1. Setup `frontend/app.py` + `src/invoke.py` esqueleto (sem AgentCore
   real) + fixtures de mock (`tests/conftest.py`).
2. **US1.9** - saudacao inicial, layout basico, botao "Limpar conversa".
   Rende a UI navegavel sem invocar AgentCore ainda.
3. **US4.1** - dropdown de modelo na sidebar + `MODEL_ARNS` + indicador
   de modelo no cabecalho.
4. **US1.6** - guard 4000 chars (primario em `src/invoke.py::ask_agent`
   com `ValueError` + defense-in-depth com `st.warning` no frontend).
5. **US1.7** - mapping `ClientError -> AgentInvocationError` + `st.error`
   + logger de debug.

### U2 `hr-agent` (6 stories)

1. Setup `agent/agent.py` esqueleto: `BedrockModel` + tool `retrieve` +
   fixture de mock em `tests/conftest.py`.
2. **US1.1 / US1.2 / US1.3 / US2.1 / US3.1** - system prompt de politicas
   gerais + validacao via smoke test com ancoras (a definir em
   `functional-design`). Podem cair no mesmo commit porque compartilham
   o mesmo system prompt e a mesma tool `retrieve`.
3. **US1.4** - fallback "nao encontrei" (parte do system prompt +
   contrato de contains em teste unitario).
4. **US1.5** - recusa LGPD (parte do system prompt) + teste unitario
   NFR8.2 obrigatorio (stub de `retrieve` com salario ficticio).

### U3 `infra` (0 stories diretamente; provisiona a base)

U3 nao "implementa" stories no sentido AC-por-AC. Contribui para:

- **FR2.1** (bucket S3), **FR2.2** (KB indexada + `StartIngestionJob`),
  **FR2.3** (snapshot fixo), **FR3** (AgentCore Runtime), **NFR5**
  (IAM roles least-privilege), **NFR7.2** (`cdk synth` obrigatorio).

Estas sao pre-condicoes operacionais para as stories de U1 e U2
funcionarem end-to-end. `delivery-planning` decidira em qual Bolt U3 e
provisionado.

## Coverage verification

- **Cobertura de stories**: 11 stories atribuidas: 5 -> U1, 6 -> U2, 0 ->
  U3. Nenhuma story sem unit.
- **Unidade sem story direta**: U3 provisiona infra; suas FR/NFR
  (FR2.x, FR3, NFR5, NFR7.x) sao rastreadas no `traceability.json` da
  fase `requirements-analysis` e ficam operacionais como pre-condicoes
  das stories de U1 e U2.
- **AC cross-unit**: US1.6 e US1.7 tem componente de dominio em
  AgentInvoker (`ClientError` mapping, guard primario `ValueError`) e
  componente de UI em Streamlit (`st.warning`, `st.error`, logger).
  Ambos moram em U1 porque `frontend/` e `src/` compartilham o mesmo
  target de deploy.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
