# Wireframes - Chatbot de RH com Bedrock AgentCore

Wireframes de baixa fidelidade da interface Streamlit do MVP definido em
`scope-document.md` e `intent-backlog.md` (B-3 - frontend Streamlit).
Consomem tambem o `intent-statement.md` (fronteira de produto e criterios de
sucesso).

## Tela unica - Assistente Virtual de RH

Interface de chat com sidebar de configuracao. Layout adotado conforme
[Q1] (opcao D - chat + botao limpar + seletor de modelo).

```text
+--------------------------------------------------------------------------+
|                                                                          |
|  [SIDEBAR]              |  Assistente Virtual de RH                      |
|                         |                                                |
|  Modelo de chat         |  +------------------------------------------+  |
|  +-------------------+  |  | [assistant] Ola! Sou o assistente de RH. |  |
|  | Claude Haiku 4.5v |  |  |             Posso ajudar com politicas   |  |
|  +-------------------+  |  |             de RH, ferias, onboarding    |  |
|                         |  |             e avaliacoes. Qual sua       |  |
|  [ Limpar conversa ]    |  |             duvida?                      |  |
|                         |  +------------------------------------------+  |
|                         |                                                |
|                         |  +------------------------------------------+  |
|                         |  | [user] Quantos dias de ferias tenho      |  |
|                         |  |        direito por ano?                  |  |
|                         |  +------------------------------------------+  |
|                         |                                                |
|                         |  +------------------------------------------+  |
|                         |  | [assistant] De acordo com a politica de  |  |
|                         |  |             ferias, o colaborador tem    |  |
|                         |  |             direito a 30 dias de ferias  |  |
|                         |  |             anuais apos 12 meses de      |  |
|                         |  |             trabalho continuo, podendo   |  |
|                         |  |             ser divididos em ate 3       |  |
|                         |  |             periodos.                    |  |
|                         |  +------------------------------------------+  |
|                         |                                                |
|                         |  +------------------------------------------+  |
|                         |  | Pergunte sobre politicas de RH...    [>] |  |
|                         |  +------------------------------------------+  |
|                         |                                                |
+--------------------------------------------------------------------------+
```

## Componentes visiveis

| Elemento | Papel | Fonte |
|----------|-------|-------|
| Titulo "Assistente Virtual de RH" | Cabecalho da pagina Streamlit | [desc] |
| Sidebar > Seletor de modelo (dropdown) | Escolher o modelo de chat entre pelo menos 2 opcoes; realiza a capacidade B-5 do `intent-backlog.md` | [Q1] |
| Sidebar > Botao "Limpar conversa" | Reinicia `session_id` e `messages`, comeca sessao nova no AgentCore Runtime | [Q1] |
| Historico de chat (bolhas usuario/assistente) | Renderiza `st.session_state.messages` em `st.chat_message` | [desc] |
| Input de chat na base | `st.chat_input("Pergunte sobre politicas de RH, ferias, onboarding...")` | [desc] |
| Spinner "Consultando base de conhecimento..." | Feedback enquanto o `invoke_agent_runtime` esta em execucao | [desc] |

## Estados

| Estado | Comportamento visivel | Fonte |
|--------|----------------------|-------|
| Inicial | Uma unica bolha de assistente com saudacao; input habilitado | [Q1] |
| Aguardando resposta | Spinner "Consultando base de conhecimento..." dentro da bolha de assistente sendo formada | [desc] |
| Resposta recebida | Nova bolha de assistente com o texto de resposta; historico rolado ate o final | [desc] |
| Erro | Bolha de assistente com mensagem amigavel: "Nao consegui responder agora. Tente reformular ou contate o RH." Nao mostra stack trace nem detalhes tecnicos | [Q3] |
| Sessao nova | Ao clicar em "Limpar conversa": novo `session_id` (UUID), historico zerado, bolha de saudacao reaparece | [Q1] |

## Nao mostra fonte na UI (desvio consciente do criterio "Rastreabilidade")

Conforme resposta [Q2 C] desta etapa, a interface **nao** exibe o documento
fonte da resposta ao usuario final; o prompt de sistema instrui o agente a
usar apenas informacoes da Knowledge Base internamente. Isso relaxa o
criterio "Rastreabilidade" do `intent-statement.md` (Success Metrics: "Cada
resposta cita o documento fonte quando aplicavel") para esta demo: o agente
continua obrigado a nao inventar informacoes, mas a citacao explicita nao
aparece na UI. Se o time quiser restaurar o criterio original, a mudanca e
uma edicao no prompt de sistema mais uma linha adicional na renderizacao da
resposta.

## Form factor

Suporte: desktop com Chrome, Edge ou Firefox modernos, resolucao >= 1024px,
suficiente para demo em notebook. [Q4]

Sem exigencia de layout mobile responsivo dedicado nesta demo. Streamlit
comprime a interface em telas menores como comportamento padrao, mas isso
nao foi testado nem validado. [Q4]

## Acessibilidade

Padrao Streamlit sem certificacao WCAG formal para esta demo. [Q5]

- Estrutura HTML: cabecalho (`st.title` gera `<h1>`), regiao principal
  (bolhas de `st.chat_message`), input focavel por teclado.
- Landmarks: `st.title` como `main > h1`, sidebar como landmark
  complementar, chat_input como formulario com submit por Enter.
- Ponto de entrada por teclado: input de chat na base.

Validacao completa WCAG 2.1 AA requer teste manual com tecnologias
assistivas e revisao especializada; nao esta no escopo desta demo. [Q5]

## Assumptions & Open Questions

None.

## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-08-24T19:30:07Z
**Iteration:** 1
**Review class:** advisory

**Findings:**

- Nenhum defeito com evidencia que justifique NOT-READY. Reconfirmado item a item:
  (1) Todo bloco substantivo em `wireframes.md` e `user-flow.md` carrega tag inline resolvivel contra `## Sources` de `rough-mockups-questions.md` ou referencia upstream por nome de arquivo (`intent-statement.md`, `scope-document.md`, `intent-backlog.md`).
  (2) Ambos os artefatos declaram `## Assumptions & Open Questions: None.`
  (3) O desvio [Q2 C] esta explicitamente documentado como "desvio consciente do criterio 'Rastreabilidade'" em secao propria no `wireframes.md` e replicado em subsecao no `user-flow.md`, citando o criterio original do `intent-statement.md` e apontando o caminho de reversao. Nao ha ocultacao.
  (4) Wireframe reflete a interpretacao maximal do [Q1] (A+B+C+D marcados; D subsume B e C): sidebar com seletor de modelo, botao "Limpar conversa" e chat central com input na base.
  (5) Erro tratado exatamente como em [Q3 A] - bolha de assistente com mensagem amigavel, sem stack trace. Toast/banner ([Q3 B]) nao aparece nem e negado.
  (6) Form factor descrito como desktop >= 1024px em navegadores modernos, alinhado a [Q4 A]. A nota sobre Streamlit comprimir em telas menores esta redigida como comportamento padrao nao testado, nao como suporte declarado - dentro do contrato de grounding.
  (7) Acessibilidade descrita como padrao Streamlit sem certificacao WCAG formal, com nota de que validacao WCAG 2.1 AA requer teste manual - alinhado a [Q5 A] sem transformar [Q5 B] em exclusao factual.
  (8) Nenhuma opcao nao selecionada foi convertida em requisito ou exclusao factual.

**Suggestions:**

- `wireframes.md` - o `[Answer]: A, B, C, D` no `rough-mockups-questions.md` seleciona quatro opcoes mutuamente inclusivas em ordem crescente de UI (A=so chat, D=A+B+C). A interpretacao adotada (D) e a leitura maximal e razoavel, mas ficaria mais explicita com uma linha curta tipo "Nota de interpretacao: [Q1] marcou A, B, C e D; adotou-se D por subsumir B e C" - espelhando o padrao ja usado em `intent-backlog.md`.
- `user-flow.md` - o desvio "Trocar modelo de chat" cita "risco R-4 do `raid-log.md`". `raid-log.md` nao esta no `consumes:` do stage `rough-mockups`, entao a referencia depende de o leitor descobrir esse artefato por conta propria. Considere trocar para uma nota inline curta ("modelos com prefixo `us.*` exigem inference profile") ou explicitar que o R-4 vem de um artefato upstream nao consumido diretamente.
- `wireframes.md` - o unico wireframe ASCII exibe uma resposta concreta sobre ferias com valores especificos (30 dias, 12 meses, 3 periodos). E texto ilustrativo, nao um claim, mas para uma demo interna vale ancorar em `[desc]` ou marcar explicitamente "conteudo ilustrativo, nao validado contra `leave_policy.pdf`" - evita que alguem leia como especificacao de resposta esperada.
- `wireframes.md` - a secao "Acessibilidade" descreve o markup gerado pelo Streamlit (`<h1>`, landmarks, chat_input focavel) sem citar fonte. Sao afirmacoes sobre o comportamento padrao da biblioteca (razoaveis e verificaveis), mas se quiser manter o padrao rigoroso de sourcing, uma tag `[desc]` ou uma nota "comportamento padrao da biblioteca Streamlit" fecha o loop.
