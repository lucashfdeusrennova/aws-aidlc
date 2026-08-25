# User Stories - Plano e Perguntas

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Plano proposto

### Personas

Uma persona primaria com 2-3 cenarios especializados. Base em `stakeholder-map.md`:

- **P1. Colaborador (Ana)** - colaboradora geral com duvidas cotidianas sobre politicas de RH, ferias e beneficios. Persona primaria.
- **P2. Novo funcionario (Bruno)** - colaborador em processo de onboarding, primeiras semanas na empresa. Sub-persona (mesmo perfil de acesso, contexto especifico).
- **P3. Gestor (Carla)** - lider consultando diretrizes de avaliacao de desempenho. Sub-persona.

### Story format

INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.

Formato: "Como [persona], quero [objetivo], para [beneficio]."

Acceptance criteria em BDD (Given/When/Then), com IDs `AC{story-group}.{story-seq}.{criterion-seq}` (por regra do phase inception).

### Breakdown

Proponho breakdown **por FR funcional**, resultando em ~8-10 stories agrupadas assim:

- **Grupo US1 - Consultar politicas de RH via chatbot** (mapeia FR1)
  - US1.1: consultar politicas gerais (Ana)
  - US1.2: consultar politica de ferias (Ana)
  - US1.3: consultar processo de onboarding (Bruno)
  - US1.4: consultar diretrizes de avaliacao (Carla)
  - US1.5: consultar feriados da empresa (Ana)
- **Grupo US2 - Comportamentos de fallback e recusa** (mapeia FR5, NFR4)
  - US2.1: pergunta fora da base -> "nao encontrei"
  - US2.2: pergunta sobre dado individual -> recusa LGPD
- **Grupo US3 - Robustez da UI** (mapeia FR8, FR9)
  - US3.1: input maior que 4000 chars -> aviso amigavel
  - US3.2: erro do AgentCore -> mensagem amigavel sem stack trace
- **Grupo US4 - Experimentacao pelo operador** (mapeia FR6)
  - US4.1: trocar modelo de chat via sidebar

### Prioridade MoSCoW proposta

- **Must**: US1.1-US1.5 (cobertura funcional), US2.2 (recusa LGPD - critico compliance), US3.1 e US3.2 (robustez basica), US4.1 (parte do MVP definido em Q1 do scope-definition).
- **Should**: US2.1 (fallback educado).
- **Could / Won't**: nao ha nesta iteracao (as capacidades Could Have do backlog nao sao stories por si so - reranker, troca de embedding, IaC completo, custo/resposta sao infraestrutura ou operacao, nao user-facing).

## Q1. Confirmar as 3 personas propostas?

- A. Sim, 3 personas: Ana (colaborador), Bruno (novo funcionario), Carla (gestora).
- B. So Ana - basta uma persona generica para o MVP.
- C. Mais personas (descrever em Other).
- X. Other (please specify)

[Answer]:A

## Q2. Confirmar breakdown por FR funcional (10 stories agrupadas em 4 grupos US)?

- A. Sim, o breakdown proposto acima esta bom.
- B. Preferir breakdown por persona (US por persona - US-Ana, US-Bruno, US-Carla).
- C. Preferir breakdown por workflow (US por fluxo - consulta, fallback, erro, config).
- X. Other (please specify)

[Answer]:B

## Q3. Confirmar as prioridades MoSCoW propostas?

- A. Sim: US1.1-US1.5, US2.2, US3.1, US3.2, US4.1 sao Must; US2.1 e Should.
- B. Ajustar (descrever em Other - por exemplo tornar US2.1 tambem Must, ou tornar US4.1 Should para focar em cobertura funcional primeiro).
- X. Other (please specify)

[Answer]:A

## Q4. Ha alguma story adicional que voce quer incluir alem das 10 propostas?

- A. Nao, as 10 propostas cobrem o MVP.
- B. Sim, adicionar historia de conversacao (`AgentCore Memory`, NFR10) como story Should Have.
- C. Sim, adicionar outra (descrever em Other).
- X. Other (please specify)

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
