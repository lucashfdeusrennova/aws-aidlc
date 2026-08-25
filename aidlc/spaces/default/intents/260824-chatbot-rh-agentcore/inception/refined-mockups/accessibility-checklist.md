**Collaborator:** aidlc-design-agent

# Accessibility Checklist - Chatbot de RH com Bedrock AgentCore

Checklist WCAG 2.1 nivel AA como **referencia**, marcando cada criterio
como coberto pelo default do Streamlit, requerendo verificacao manual, ou
nao aplicavel a esta demo [q4 A]. **Nao e uma certificacao formal**; o
`wireframes.md` ja registra que validacao completa exige teste com
tecnologias assistivas e revisao especializada, fora do escopo do MVP.

Fontes consumidas: `wireframes.md` (declaracao de nao-certificacao),
`user-flow.md` (input por teclado), `stories.md` (28 ACs),
`requirements.md` (FR/NFR), `team-practices.md` (stack), mais
`.kiro/knowledge/aidlc-design-agent/accessibility-wcag.md`.

## Sources

- [wf] `wireframes.md`.
- [uf] `user-flow.md`.
- [st] `stories.md`.
- [rq] `requirements.md`.
- [tp] `team-practices.md`.
- [mk] `mockups.md` deste stage.
- [ds] `design-system-mapping.md` deste stage.
- [q4] Q4 = A - WCAG 2.1 AA referencial, sem certificacao.

## Legenda

- **[Streamlit default]**: coberto pelo comportamento default da
  biblioteca sem esforco adicional (ex.: semantica HTML de `st.title`,
  `role="alert"` em `st.warning` / `st.error`).
- **[Manual]**: requer verificacao manual antes da demo (ex.: contraste
  de cor apos qualquer tema custom; smoke com leitor de tela).
- **[N/A]**: nao aplicavel a esta demo (ex.: video, audio, PDF renderizado
  na UI).
- **[Gap]**: nao coberto e conscientemente aceito no MVP.

## 1. Perceivable

### 1.1 Text Alternatives

- **1.1.1 Non-text Content (A)** - [Streamlit default] - unicas imagens
  no MVP sao os icones de `st.chat_message`, gerados por Streamlit com
  alt implicito. [ds DS-6][ds DS-7][ds DS-12]. Sem `st.image` no MVP.

### 1.2 Time-based Media

- **1.2.1 - 1.2.5** - [N/A] - Sem video nem audio. [wf][mk].

### 1.3 Adaptable

- **1.3.1 Info and Relationships (A)** - [Streamlit default] -
  `st.title` gera `<h1>`, `st.caption` gera `<p>`, `st.chat_message`
  agrupa a bolha, `st.warning`/`st.error` usam `role="alert"`. [ds DS-1,
  DS-2, DS-6, DS-10, DS-11].
- **1.3.2 Meaningful Sequence (A)** - [Streamlit default] - ordem do DOM
  segue a ordem visual (titulo -> caption modelo -> historico -> input),
  Streamlit renderiza de cima para baixo. [wf][mk].
- **1.3.3 Sensory Characteristics (A)** - [Streamlit default] - instrucoes
  do bot nao dependem de cor, forma ou posicao ("botao azul"); referem-se
  ao nome ("Limpar conversa"). [mk copy].
- **1.3.4 Orientation (AA)** - [Streamlit default] - Streamlit funciona
  em portrait e landscape sem forcar orientacao.
- **1.3.5 Identify Input Purpose (AA)** - [N/A] - nao ha campos de perfil
  do usuario (nome, endereco, cartao). O unico input e a pergunta livre.

### 1.4 Distinguishable

- **1.4.1 Use of Color (A)** - [Streamlit default] - warning/erro usam
  cor + icone + texto; nao dependem so de cor. [ds DS-10, DS-11].
- **1.4.2 Audio Control (A)** - [N/A] - sem audio.
- **1.4.3 Contrast (Minimum) (AA)** - [Manual] - tema padrao do Streamlit
  passa contraste WCAG AA na maior parte dos elementos, mas [q2 A] fixa
  "sem tema customizado", entao antes da demo cabe verificar contraste
  do caption cinza sobre fundo branco (indicador de modelo, contador).
  Se falhar, trocar `st.caption` por texto normal.
- **1.4.4 Resize Text (AA)** - [Streamlit default] - Streamlit respeita o
  zoom do navegador; texto redimensiona ate 200% sem perda de conteudo.
- **1.4.5 Images of Text (AA)** - [N/A] - sem imagens de texto.
- **1.4.10 Reflow (AA)** - [Streamlit default] - layout responsivo do
  Streamlit reflua ate 320px de largura sem scroll horizontal ***embora
  nao seja testado nesta demo*** [wf § Form factor].
- **1.4.11 Non-text Contrast (AA)** - [Manual] - bordas do `st.chat_input`
  e do dropdown precisam >= 3:1. Padrao Streamlit deve cobrir; verificar
  visualmente antes da demo.
- **1.4.12 Text Spacing (AA)** - [Streamlit default] - Streamlit nao
  aplica line-height / letter-spacing agressivo; texto adapta a
  configuracoes de espacamento do usuario.
- **1.4.13 Content on Hover or Focus (AA)** - [N/A] - sem tooltips
  customizados; tooltips nativos do dropdown seguem padrao do navegador.

## 2. Operable

### 2.1 Keyboard Accessible

- **2.1.1 Keyboard (A)** - [Streamlit default] - Tab move o foco entre
  dropdown, botao "Limpar conversa" e `st.chat_input`. Enter submete o
  input. Space ativa o botao. [uf § Passo 2, "input focado"].
- **2.1.2 No Keyboard Trap (A)** - [Streamlit default] - foco nao fica
  preso em nenhum widget.
- **2.1.4 Character Key Shortcuts (A)** - [N/A] - sem atalhos de tecla
  unica customizados.

### 2.2 Enough Time

- **2.2.1 Timing Adjustable (A)** - [N/A] - sem timeout de sessao do lado
  cliente. AgentCore Runtime tem timeout proprio (>=5s NFR1.1), coberto
  pelo tratamento de erro US1.7.
- **2.2.2 Pause, Stop, Hide (A)** - [N/A] - sem conteudo em movimento
  alem do spinner do `st.spinner`, que so dura o intervalo do
  `invoke_agent_runtime` (<5s NFR1.1).

### 2.3 Seizures and Physical Reactions

- **2.3.1 Three Flashes or Below Threshold (A)** - [Streamlit default] -
  spinner do Streamlit gira suavemente; sem flashes.

### 2.4 Navigable

- **2.4.1 Bypass Blocks (A)** - [Streamlit default] - Streamlit gera
  landmarks basicos (`<header>`, `<main>`, `<aside>` para sidebar). Uma
  pagina unica; sem necessidade de skip-link customizado.
- **2.4.2 Page Titled (A)** - [Streamlit default] - `st.set_page_config`
  em `frontend/app.py` (recomendado adicionar em code-generation) define
  o `<title>`. Sem ela, o titulo vira o nome do arquivo Python.
  **[Recomendacao para code-generation]**: incluir
  `st.set_page_config(page_title="Assistente Virtual de RH", ...)`.
- **2.4.3 Focus Order (A)** - [Streamlit default] - ordem visual = ordem
  do DOM.
- **2.4.4 Link Purpose (In Context) (A)** - [N/A] - sem links externos no
  MVP.
- **2.4.5 Multiple Ways (AA)** - [N/A] - unica pagina.
- **2.4.6 Headings and Labels (AA)** - [Streamlit default] - `st.title`,
  `st.selectbox("Modelo de chat", ...)`, `st.chat_input("Pergunte...")`
  todos com labels descritivos. [mk][is].
- **2.4.7 Focus Visible (AA)** - [Streamlit default] - Streamlit mantem
  outline padrao do navegador nos widgets.

### 2.5 Input Modalities

- **2.5.1 Pointer Gestures (A)** - [N/A] - sem gestos multi-touch
  customizados.
- **2.5.2 Pointer Cancellation (A)** - [Streamlit default] - botoes
  disparam no `pointerup`.
- **2.5.3 Label in Name (A)** - [Streamlit default] - texto visivel
  ("Modelo de chat", "Limpar conversa", "Pergunte sobre politicas...")
  bate com o accessible name.
- **2.5.4 Motion Actuation (A)** - [N/A] - sem controles por movimento.

## 3. Understandable

### 3.1 Readable

- **3.1.1 Language of Page (A)** - [Manual] - garantir que
  `st.set_page_config(...)` ou o container HTML defina `lang="pt-BR"`
  quando o Streamlit renderiza. Como o Streamlit 1.x default nao tem esse
  ajuste, e uma pendencia para `code-generation`: definir via
  `st.set_page_config(page_title="...", ...)` mais uma injecao minima
  aceitavel de `<meta http-equiv>` **ou** aceitar a limitacao de que o
  atributo `lang` pode vir vazio. Como [q2 A] proibe HTML custom, adotamos
  a limitacao para MVP. **[Gap consciente]**.
- **3.1.2 Language of Parts (AA)** - [N/A] - todo conteudo em portugues,
  sem partes em outras linguas.

### 3.2 Predictable

- **3.2.1 On Focus (A)** - [Streamlit default] - foco nao dispara mudanca
  de contexto.
- **3.2.2 On Input (A)** - [Streamlit default] - selecionar um modelo no
  dropdown rerenderiza a pagina, comportamento padrao esperado do
  Streamlit; o usuario nao e transportado para outra pagina.
- **3.2.3 Consistent Navigation (AA)** - [Streamlit default] - pagina
  unica.
- **3.2.4 Consistent Identification (AA)** - [Streamlit default] -
  botao "Limpar conversa" e dropdown mantem rotulo e posicao em toda a
  sessao.

### 3.3 Input Assistance

- **3.3.1 Error Identification (A)** - [Streamlit default] - warning
  (US1.6) e error (US1.7) sao renderizados por `st.warning`/`st.error`
  com `role="alert"`. [ds DS-10, DS-11][st AC1.6.1, AC1.7.2].
- **3.3.2 Labels or Instructions (A)** - [Streamlit default] - dropdown
  e chat_input tem labels visiveis; o placeholder do chat_input serve
  como instrucao adicional.
- **3.3.3 Error Suggestion (AA)** - [Streamlit default] - warning de
  US1.6 sugere "tente resumir em uma unica pergunta mais curta"; erro
  de US1.7 sugere "tente novamente em alguns segundos ou contate o RH".
  [mk][st AC1.6.1, AC1.7.2].
- **3.3.4 Error Prevention (Legal, Financial, Data) (AA)** - [N/A] - sem
  submissao legal/financeira/dados irreversiveis. Limpar conversa e
  destrutivo mas escopado ao proprio historico local; nao afeta dados
  externos, e o custo de recuperacao e "digitar de novo" [mk § US1.9].

## 4. Robust

### 4.1 Compatible

- **4.1.1 Parsing (A) - deprecated na WCAG 2.2** - [Streamlit default] -
  Streamlit gera HTML valido.
- **4.1.2 Name, Role, Value (A)** - [Streamlit default] - widgets
  geram HTML nativo (`<button>`, `<select>`, `<textarea>`) com nome
  e role apropriados. `st.warning`/`st.error` como `role="alert"`
  [ds DS-10, DS-11].
- **4.1.3 Status Messages (AA)** - [Streamlit default] - spinner e
  warning/erro sao aria-live regions default do Streamlit. Leitores de
  tela anunciam sem precisar mover o foco.

## Gaps conscientemente aceitos

- **Language of Page (3.1.1)**: `lang="pt-BR"` no HTML pode nao ser
  definido explicitamente pelo Streamlit. Impacto: alguns leitores de
  tela podem usar a pronuncia default do sistema. Aceito por [q2 A] +
  janela de 2 dias. Se relevante pos-demo, aplicar via
  `st.markdown` custom **ou** aguardar suporte nativo do Streamlit.
- **Certificacao WCAG formal**: nao ha auditoria com ferramenta
  automatizada (axe, WAVE) nem teste com NVDA/JAWS/VoiceOver como parte
  do MVP. [wf § Acessibilidade] ja registra isso.
- **Contraste 1.4.3, 1.4.11**: sem verificacao numerica formal. Confiamos
  no default do Streamlit e no `body -> demo`. Se um participante do
  workshop reportar contraste ruim, o refinamento post-demo e aplicar
  tema custom minimo.

## Pendencias para code-generation

- Incluir `st.set_page_config(page_title="Assistente Virtual de RH",
  page_icon=":speech_balloon:", layout="centered")` no topo de
  `frontend/app.py`. Cobre 2.4.2 e melhora reconhecimento em abas do
  navegador.
- Manter todos os labels de widget em portugues; nunca deixar vazio.

## Alinhamento com team-practices

- **Sem CSS/HTML custom** [tp][q2 A]: reduz risco de quebrar semantica
  nativa; toda acessibilidade e "gratuita" via widgets Streamlit.
- **Copy exata** [mk][is]: cada texto de warning/erro/fallback foi
  escolhido para atender WCAG 3.3.3 (sugestao de correcao) automaticamente
  ao ser breve, direto e acionavel [q1 A].

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
