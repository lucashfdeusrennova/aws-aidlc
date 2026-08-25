# Refined Mockups - Perguntas

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Q1. Tom das respostas do bot

Como o bot deve responder em geral?

- A. Breve e direto (2-4 frases), formal-neutro; cita politica/regra sem parafrasear demais. Adequado para RH.
- B. Conversacional e amigavel (bullets, "Voce pode...", tom acolhedor), mais explicativo.
- C. Formato misto: paragrafo curto + lista quando houver mais de 1 item (ex.: multiplas etapas de onboarding).
- X. Other (please specify)

[Answer]: A

## Q2. Design system / tema

- A. Streamlit padrao (tema light, sem customizacao). Suficiente para demo.
- B. Aplicar tema customizado minimo (cor primaria da empresa, favicon).
- C. Not yet defined.
- X. Other (please specify)

[Answer]: A

## Q3. Componentes adicionais alem do essencial

- A. Nenhum adicional. Mantem so o que ja esta em wireframes.md (chat + sidebar com dropdown de modelo + botao limpar).
- B. Adicionar contador de caracteres progressivo `{n}/4000` quando >3500 chars (sugestao do design agent em user-stories).
- C. Adicionar indicador visual do modelo em uso no cabecalho (`Assistente Virtual de RH - Modelo: Claude Haiku 4.5`) para reforcar AC4.1.2.
- D. B + C.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]: D

## Q4. Nivel de spec do accessibility-checklist

- A. Checklist WCAG 2.1 AA por criterio, marcado como "Streamlit default cobre" / "manual" / "nao aplicavel a esta demo". Sem certificacao formal.
- B. Somente WCAG A (basico) - focar em navegacao por teclado e contraste.
- C. Sem checklist WCAG - so registrar que acessibilidade nao esta certificada.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

Nenhuma assunção nova alem das ja fixadas em `stories.md` e `wireframes.md`. As escolhas acima foram propostas pelo agente como defaults MVP e confirmadas pelo humano ("pode continuar").

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumo consolidado das decisoes deste stage:

- Q1 = A - tom breve e direto (2-4 frases, formal-neutro).
- Q2 = A - Streamlit padrao, sem tema customizado.
- Q3 = D - contador de caracteres progressivo `{n}/4000` quando >3500 chars + indicador visual do modelo em uso no cabecalho.
- Q4 = A - checklist WCAG 2.1 AA referencial, sem certificacao formal.

Artefatos produzidos:
- `mockups.md`
- `interaction-spec.md`
- `design-system-mapping.md`
- `accessibility-checklist.md`

[Answer]: Looks correct
