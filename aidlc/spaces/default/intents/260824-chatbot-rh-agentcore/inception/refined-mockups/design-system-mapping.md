**Collaborator:** aidlc-design-agent

# Design System Mapping - Chatbot de RH com Bedrock AgentCore

Mapeia cada elemento visual descrito em `mockups.md` e `interaction-spec.md`
para o widget Streamlit correspondente do "design system implicito" que a
biblioteca oferece. Como [q2 A] fixou "Streamlit padrao, sem tema
customizado", este documento e principalmente uma referencia de widgets +
justificativa de escolha, nao a definicao de um design system autoral.

Fontes consumidas: `wireframes.md` (elementos), `user-flow.md` (fluxos),
`stories.md` (11 stories, 28 ACs), `requirements.md` (FR/NFR),
`team-practices.md` (stack e restricoes).

## Sources

- [wf] `wireframes.md`.
- [uf] `user-flow.md`.
- [st] `stories.md`.
- [rq] `requirements.md`.
- [tp] `team-practices.md`.
- [mk] `mockups.md` deste stage.
- [is] `interaction-spec.md` deste stage.
- [q2] Q2 = A - Streamlit padrao.

## Design tokens

Como o tema custom foi rejeitado em [q2 A], os tokens do "design system"
sao os defaults do Streamlit e sua versao pinada no `requirements.txt`
(a pinar em `code-generation`, cf. [tp § Testing Posture, § Deployment]).
Documentado aqui para tornar a decisao rastreavel:

| Token             | Valor                                                        |
| ----------------- | ------------------------------------------------------------ |
| Tema              | `light` default do Streamlit.                                |
| Cor primaria      | Padrao Streamlit (varia por versao; nao dependemos disso).   |
| Cor de fundo      | `#FFFFFF` (default light).                                   |
| Cor de erro       | Padrao do `st.error` (vermelho/rosa claro).                  |
| Cor de warning    | Padrao do `st.warning` (amarelo claro).                      |
| Fonte             | Sans-serif do sistema (Streamlit escolhe).                   |
| Espacamento       | Layout padrao com `st.title`, `st.caption`, `st.sidebar`.    |
| Bolhas de chat    | Estilo default de `st.chat_message` (icones "user" e "assistant"). |
| Icones            | Padrao do `st.chat_message` (nao customizado).               |
| Favicon           | Padrao do Streamlit ([q2 A] rejeita favicon custom).         |

## Mapeamento elemento por elemento

Um bloco por elemento visual do `mockups.md`. Cada bloco indica o widget
Streamlit exato, propriedades relevantes, alternativas rejeitadas e ACs
cobertos.

### DS-1. Titulo da pagina

- **Widget**: `st.title("Assistente Virtual de RH")`
- **Renderiza como**: `<h1>` (semantica; auxilia navegacao por leitor de
  tela, [q4 A]).
- **Alternativas rejeitadas**: `st.header` (H2, quebra hierarquia
  esperada de "unica pagina") e `st.markdown("# ...")` (mesmo resultado
  visual, sem semantica reforcada).
- **Rastreavel a**: [wf], [mk § C1].
- **AC coberto**: -

### DS-2. Indicador de modelo no cabecalho

- **Widget**: `st.caption(f"Modelo em uso: {st.session_state.model_id}")`
- **Renderiza como**: paragrafo pequeno em cinza, abaixo do titulo.
- **Alternativas rejeitadas**: `st.metric` (visualmente pesado para um
  string), `st.badge` (nao existe como widget nativo do Streamlit sem
  custom HTML; violaria [q2 A]).
- **Rastreavel a**: [q3 D], [mk § C1], [st AC4.1.2].
- **AC coberto**: AC4.1.2.

### DS-3. Sidebar - Rotulo "Modelo de chat"

- **Widget**: label do proprio `st.selectbox` (parametro `label`).
- **Renderiza como**: label textual acima do dropdown, semantica de
  `<label>` associada ao controle.
- **Rastreavel a**: [wf], [mk § C2], [is § C2].

### DS-4. Sidebar - Dropdown de modelo

- **Widget**: `st.sidebar.selectbox(...)`
- **Propriedades**: `options=["Claude Haiku 4.5", "Amazon Nova Pro"]`,
  `index=<posicao do model_id atual>`, `key="model_selector"`.
- **Alternativas rejeitadas**: `st.radio` (funciona, mas ocupa mais
  vertical na sidebar), `st.select_slider` (semantica errada para lista
  categorica sem ordem), `st.multiselect` (nao aplicavel; escolhe-se um
  modelo por vez para o proximo turno).
- **Rastreavel a**: [wf], [mk § C2], [is § C2], [st AC4.1.1].
- **AC coberto**: AC4.1.1, AC4.1.3.

### DS-5. Sidebar - Botao "Limpar conversa"

- **Widget**: `st.sidebar.button("Limpar conversa",
  on_click=_clear_conversation, key="clear_chat")`
- **Renderiza como**: `<button>` HTML nativo, focavel por Tab.
- **Alternativas rejeitadas**: `st.link_button` (link visual; semantica
  errada para acao destrutiva), `st.download_button` (nao e download).
- **Rastreavel a**: [wf], [mk § C3], [is § C3], [st AC1.9.1].
- **AC coberto**: AC1.9.1.

### DS-6. Historico de chat - bolhas

- **Widget**: `st.chat_message(role)` como context manager, iterado
  sobre `st.session_state.messages`.
- **Renderiza como**: bolha com icone do `role` (user / assistant),
  fundo levemente cinza (default do widget).
- **Conteudo**: `st.markdown(message["content"])` (permite negritos e
  listas simples caso o agente os inclua).
- **Alternativas rejeitadas**: renderizar tudo em `st.markdown` com
  prefixo "Usuario:" / "Assistente:" (perde acessibilidade e semantica);
  usar HTML customizado (viola [q2 A]).
- **Rastreavel a**: [wf], [mk § C5], [is § C5].
- **AC coberto**: AC1.1.3, AC1.9.5.

### DS-7. Bolha de assistente sendo formada com spinner

- **Widget composto**: `st.chat_message("assistant")` + `st.spinner(...)`.
- **Copy do spinner**: `"Consultando base de conhecimento..."` [mk][wf].
- **Renderiza como**: bolha do assistente com um spinner animado e o
  texto ao lado.
- **Alternativas rejeitadas**: `st.status(...)` (visual mais pesado,
  parece card de log; nao alinhado com fluxo de chat), toast global
  (usuario perde a associacao com a mensagem que foi enviada).
- **Rastreavel a**: [wf], [uf], [mk § US1.1-US3.1], [is § C8],
  [st AC1.1.4].
- **AC coberto**: AC1.1.4.

### DS-8. Input de chat

- **Widget**: `st.chat_input("Pergunte sobre politicas de RH...")`.
- **Comportamento**: submit por Enter, botao de envio embutido, foco por
  Tab, placeholder visivel.
- **Alternativas rejeitadas**: `st.text_area` + `st.button` (mais
  flexivel para contador ao vivo, mas custa layout e onboarding para o
  usuario; adiado como Opcao B em [is § C7]).
- **Rastreavel a**: [wf], [mk § C6], [is § C6].
- **AC coberto**: AC1.6.2.

### DS-9. Contador de caracteres

- **Widget**: `st.caption(f"Sua pergunta teve {n}/4000 caracteres...")`
  renderizado condicionalmente apos o submit.
- **Renderiza como**: linha cinza pequena abaixo do input.
- **Nota tecnica**: nao existe evento "on_change" no `st.chat_input`;
  o contador reage ao **valor submetido**, nao ao rascunho ao vivo
  [is § C7]. Aceito como limitacao consciente.
- **Rastreavel a**: [q3 D], [is § C7].
- **AC coberto**: contribui a AC1.6.1.

### DS-10. Warning de input muito longo

- **Widget**: `st.warning(...)` com texto exato de [mk][st AC1.6.1].
- **Renderiza como**: caixa amarela com icone de aviso, focalizavel por
  leitor de tela como `role="alert"` (comportamento default do Streamlit).
- **Alternativas rejeitadas**: `st.toast` (nao persiste na tela; usuario
  pode perder). `st.error` (semantica errada; o usuario nao teve erro,
  so precisa reformular).
- **Rastreavel a**: [mk § US1.6], [is § C6], [st AC1.6.1].
- **AC coberto**: AC1.6.1.

### DS-11. Erro do AgentCore

- **Widget**: `st.error(...)` com texto exato de [mk][st AC1.7.2].
- **Renderiza como**: caixa vermelha/rosa com icone de erro,
  `role="alert"`.
- **Rastreavel a**: [wf § Estados], [uf § Erro], [mk § US1.7],
  [is § C8].
- **AC coberto**: AC1.7.2.

### DS-12. Bolha de saudacao inicial

- **Widget**: `st.chat_message("assistant")` renderizado como parte de
  `messages`.
- **Copy exata**: [mk § US1.1-US3.1 - "Copy da saudacao inicial"].
- **Rastreavel a**: [wf § Estados], [mk], [is § C9], [st AC1.9.5].
- **AC coberto**: AC1.9.5.

## Elementos nao usados

Widgets Streamlit que **nao** foram escolhidos, com justificativa breve
(evita reintroducao acidental em code-generation):

- `st.tabs`: uma unica pagina, sem separacao.
- `st.expander`: sem conteudo escondido em progressive disclosure.
- `st.dataframe`, `st.table`: nao renderizamos dados tabulares.
- `st.metric`: sem KPI visivel para o colaborador.
- `st.progress`: latencia esta abaixo de 5s [rq NFR1.1]; barra de
  progresso soa exagerada, e o spinner ja cobre o feedback.
- `st.toast`: usuario precisa ver o warning e o erro; toast passa muito
  rapido.
- `st.status`: pesado demais para o feedback de "consultando".
- `st.form`: `st.chat_input` ja lida com submit; embutir em form nao
  agrega.
- `st.file_uploader`: sem upload de arquivo no MVP.
- `st.download_button`: sem download.
- Componentes custom via `st.components.v1.html`: [q2 A] rejeita CSS/HTML
  custom.

## Alinhamento com team-practices

- **Sem CSS/HTML custom** [q2 A][tp § Code Style]: nao ha
  `st.markdown(..., unsafe_allow_html=True)`. Toda copy e Markdown "seguro".
- **Widgets nativos apenas**: reduz o risco de manutencao entre versoes
  Streamlit pinadas em `requirements.txt` [rq NFR7.1].
- **Semantica preservada**: cada widget renderiza HTML semantico
  (heading, button, alert), o que ajuda o checklist WCAG do arquivo
  `accessibility-checklist.md`.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
