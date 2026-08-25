# User Stories Assessment - Chatbot de RH com Bedrock AgentCore

## Decision

**Execute.**

## Rationale

Este projeto e user-facing (colaboradores interagindo com o chatbot via Streamlit), com personas ja identificadas em `stakeholder-map.md` (colaboradores em geral com duvidas sobre politicas de RH, ferias e beneficios) e requisitos funcionais claros e organizados em `requirements.md` (FR1-FR9 com 24 sub-requisitos totais).

User stories agregam valor porque:

- **Multiplas nuances de persona**: colaborador geral, novo funcionario em onboarding (com necessidades especificas de FR1.3), gestor consultando avaliacao de desempenho (FR1.4). Modelar como uma persona principal + cenarios especializados. Uma quarta persona (P4 Operador) foi introduzida na triagem mob para separar troca de modelo do consumo do bot.
- **Fluxos com dependencia**: pergunta -> agent -> KB -> resposta com estados diferentes (aguardando, resposta, erro, fora-da-KB) que Criterio de Aceitacao BDD (Given/When/Then) captura melhor que requisitos textuais.
- **Testabilidade**: acceptance criteria com ID estavel (`AC{group}.{seq}.{n}`) alimentam diretamente o smoke test (`scripts/smoke.py` requerido por NFR8.3) e o teste de guardrail LGPD (NFR8.2).
- **Rastreabilidade downstream**: stories com IDs `US{n}.{m}` sao consumidas pelo `functional-design`, `code-generation` e `build-and-test`, mantendo o tracing dos FRs/NFRs ate o codigo.

## Factors Considered

- **Project type**: user-facing chatbot (nao infrastructure-only, nao developer tooling).
- **User-facing scope**: interface Streamlit + interacao natural em portugues (`wireframes.md`, `user-flow.md`).
- **Persona complexity**: uma persona primaria com 2 sub-personas de cenario + 1 persona operacional; nao complexa mas suficiente para justificar stories.
- **Business logic**: RAG + system prompt LGPD + troca de modelo -- logica de negocio testavel via acceptance criteria.
- **Cross-team**: nao aplicavel (time unico de workshop), mas cross-agent no AI-DLC (developer + quality + design contribuem).

## Key Areas Where Stories Add the Most Value

- **Cobertura funcional por documento** (FR1.1-FR1.5): cada documento vira 1 story com acceptance criteria por caso canonico.
- **Recusa LGPD** (FR5, NFR4): story dedicada com acceptance criteria "given prompt provocador, when submit, then response nao expoe dados individuais". Alimenta NFR8.2 (teste de guardrail LGPD).
- **Fallback "nao encontrei"** (FR5.2): story dedicada com acceptance criteria "given pergunta fora da base, when submit, then response = 'Nao encontrei...' e nao inventa".
- **Fluxos de erro e limite** (FR8, FR9): stories dedicadas.
- **Experimentacao de modelo** (FR6): story dedicada ao Operador para trocar modelo durante a demo.
- **Iniciar nova conversa** (FR4.5): story dedicada com AC cobrindo botao, `session_id` novo via `uuid.uuid4()`, historico zerado e isolamento de sessao.

## Assumptions & Open Questions

None.
