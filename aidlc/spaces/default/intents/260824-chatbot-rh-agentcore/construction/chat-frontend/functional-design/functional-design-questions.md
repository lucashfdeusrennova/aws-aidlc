# Functional Design - Unit chat-frontend - Perguntas

## Sources

- [uw] `unit-of-work.md` - U1 chat-frontend (kind: ui, complexity M).
- [sm] `unit-of-work-story-map.md` - stories US1.6, US1.7, US1.9, US4.1.
- [rq] `requirements.md` - FR4, FR7, FR8, FR9, NFR1, NFR2, NFR3.
- [cp] `components.md` - HRChatFrontend + AgentInvoker.
- [cs] `contract-summary.md` - C1 payload, C2 CFN outputs.
- [is] `interaction-spec.md` (refined-mockups) - 9 componentes UI.

## Q1. Escopo dos artefatos

- A. Aderir estrito ao produces_kinds: apenas functional-spec.md, traceability.json e frontend-components.md. Sem entities.md nem rules.md (chat-frontend kind: ui exclui).
- X. Other

[Answer]: A

## Q2. Formato do workflow em functional-spec

- A. Numbered step sequences por AC, com state machine textual e mermaid.
- X. Other

[Answer]: A

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Functional Design de U1 chat-frontend (kind: ui) produziu 3 artefatos aplicaveis por produces_kinds:
- `functional-spec.md` - state machine + workflows por AC + business scenarios.
- `frontend-components.md` - hierarquia + session state + widget catalogue + constants + API integration point.
- `traceability.json` - 14 ACs (US1.6, US1.7, US1.9, US4.1) todos com target OK.

Q1=A (apenas os 3 artefatos aplicaveis; entities.md/rules.md sao para service/spec/library).
Q2=A (numbered workflow por AC + state machine).

[Answer]: Looks correct
