**Collaborator:** aidlc-design-agent

# Interaction Spec - Chatbot de RH com Bedrock AgentCore

Especificacao de interacao componente-a-componente do frontend Streamlit
descrito em `mockups.md`. Consumido por `code-generation` para gerar
`frontend/app.py`. Segue o formato de component-spec-template
(`.kiro/knowledge/aidlc-design-agent/component-spec-template.md`).

Fontes consumidas: `wireframes.md` (layout base), `user-flow.md`
(transicoes), `stories.md` (28 ACs), `requirements.md` (FR/NFR),
`team-practices.md` (stack e fronteiras de camada).

## Sources

- [wf] `wireframes.md` - layout e estados existentes.
- [uf] `user-flow.md` - passos happy path e desvios.
- [st] `stories.md` - contratos de AC (BDD).
- [rq] `requirements.md` - FR1-FR9 e NFR1-NFR10.
- [tp] `team-practices.md` - stack Python 3.12 + Streamlit + fronteiras
  de camada.
- [mk] `mockups.md` deste stage - layout refinado, copy exata.

## Contexto global

- **Framework**: Streamlit, executado com `streamlit run frontend/app.py`
  [tp][rq FR4].
- **Fronteira de dependencias** [tp § Code Style]: o frontend importa
  `src.invoke.ask_agent` e **nao** conhece `boto3` diretamente.
- **Estado**: exclusivamente via `st.session_state`. Nada em disco, sem
  cache externo.
- **Session state inicial** (chaves obrigatorias):
  - `messages: list[dict]` - lista de `{"role": "user"|"assistant",
    "content": str}`, inicializada com a bolha de saudacao.
  - `session_id: str` - `uuid.uuid4()` gerado no primeiro carregamento
    [rq NFR3.2][st AC1.9.2].
  - `model_id: str` - rotulo humano do modelo em uso; default =
    `"Claude Haiku 4.5"` [st AC4.1.1].

## Componente C1 - PageHeader

**Descricao**: cabecalho da pagina com titulo e indicador de modelo.
**Widget**: `st.title(...)` + `st.caption(...)`.
**Snippet**:

```python
st.title("Assistente Virtual de RH")
st.caption(f"Modelo em uso: {st.session_state.model_id}")
```

**Interacoes**: nenhuma direta.
**Reatividade**: o caption atualiza automaticamente a cada rerun quando
`st.session_state.model_id` muda [st AC4.1.2][mk § Indicador de modelo].
**AC coberto**: AC4.1.2.

## Componente C2 - Sidebar/ModelSelector

**Descricao**: dropdown na sidebar para trocar modelo.
**Widget**: `st.selectbox(...)`.
**Snippet**:

```python
MODEL_OPTIONS = ["Claude Haiku 4.5", "Amazon Nova Pro"]
st.session_state.model_id = st.sidebar.selectbox(
    "Modelo de chat",
    options=MODEL_OPTIONS,
    index=MODEL_OPTIONS.index(st.session_state.model_id),
    key="model_selector",
)
```

**Interacoes**:
- Ao selecionar outra opcao, o rerun atualiza `st.session_state.model_id`
  antes do proximo turno de chat.
- O ARN do inference profile e resolvido em runtime a partir do rotulo,
  via dicionario `MODEL_ARNS: dict[str, str]` em `frontend/app.py`
  [st AC4.1.3][rq FR6.2].

**Preservacao de historico**: trocar o modelo **nao** limpa `messages`
nem `session_id` [st AC4.1.4].

**AC coberto**: AC4.1.1, AC4.1.3, AC4.1.4.

## Componente C3 - Sidebar/ClearConversation

**Descricao**: botao para iniciar nova conversa.
**Widget**: `st.button(...)` com callback `on_click`.
**Snippet**:

```python
def _clear_conversation() -> None:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [
        {"role": "assistant", "content": GREETING_MESSAGE}
    ]

st.sidebar.button(
    "Limpar conversa",
    on_click=_clear_conversation,
    key="clear_chat",
)
```

**Interacoes**:
- Clique -> gera novo `session_id`, reseta `messages` para a bolha de
  saudacao, rerun automatico do Streamlit.
- **Sem modal de confirmacao** [mk § US1.9].

**AC coberto**: AC1.9.1, AC1.9.2, AC1.9.3, AC1.9.4, AC1.9.5.

## Componente C4 - Sidebar/StatusIndicator (implicito)

**Descricao**: area vazia da sidebar; o spinner "Consultando base de
conhecimento..." e renderizado **dentro** da bolha do assistente sendo
formada, nao na sidebar. Fica registrado aqui apenas para evitar que
alguem interprete o wireframe como "sidebar tem status area".

## Componente C5 - ChatHistory

**Descricao**: lista de bolhas usuario/assistente.
**Widget**: iteracao sobre `st.session_state.messages` renderizando cada
mensagem via `st.chat_message(role)`.
**Snippet**:

```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

**Interacoes**: nenhuma direta; a lista e recriada a cada rerun.
**Estado inicial** [st AC1.9.5][mk]:

```python
GREETING_MESSAGE = (
    "Ola! Sou o assistente de RH. Posso ajudar com politicas de RH, "
    "ferias, onboarding e avaliacoes. Qual sua duvida?"
)
```

**AC coberto**: AC1.1.3, AC1.9.5.

## Componente C6 - ChatInput

**Descricao**: caixa de input do chat, sempre visivel na base.
**Widget**: `st.chat_input(...)`.
**Snippet**:

```python
prompt = st.chat_input("Pergunte sobre politicas de RH...")
```

**Interacoes**:
- Enter (ou clique no botao de envio) submete o prompt.
- **Guard de tamanho** [st AC1.6.1][rq FR8.2]: `if prompt and
  len(prompt) > 4000` renderiza `st.warning(...)` e retorna sem invocar
  `ask_agent`.
- Submit valido chama fluxo C8 (InvokePath).

**Copy do warning** (exata) [st AC1.6.1]:

```
Sua pergunta ficou muito longa para eu processar. Tente resumir em uma
unica pergunta mais curta.
```

**AC coberto**: AC1.6.1, AC1.6.2.

## Componente C7 - CharCounter

**Descricao**: contador de caracteres progressivo, visivel apenas quando
`n > 3500` [mk § Q3][rq FR4.2].
**Widget**: `st.caption(...)` condicionalmente renderizado abaixo do
`st.chat_input`.
**Nota tecnica**: como `st.chat_input` nao expoe o valor durante digitacao
(so no submit), o contador **nao pode** ser ligado ao rascunho ao vivo.
A opcao pragmatica adotada:

- **Opcao A - reativo ao submit**: exibir o contador apenas para o
  **ultimo prompt submetido**, uma unica vez, se estiver entre 3501 e
  4000 chars (nao passou do limite, mas ficou perto). Serve como sinal de
  "cuidado com o proximo".
- **Opcao B - trocar para `st.text_area` + `st.button("Enviar")`**:
  desvia do padrao `st.chat_input` e da acesso ao valor ao vivo.

**Decisao para MVP**: **Opcao A** [mk][tp]. Simples, um `st.caption` na
mesma coluna do chat_input, exibido quando `len(prompt) > 3500 and
len(prompt) <= 4000`. Nao adiciona custo de desenvolvimento nem quebra o
padrao Streamlit para chat. Se o feedback do time apontar que "avisar
tardio" nao ajuda, a Opcao B fica registrada aqui como caminho de refino
pos-demo.

**Snippet**:

```python
if prompt is not None and 3500 < len(prompt) <= 4000:
    st.caption(f"Sua pergunta teve {len(prompt)}/4000 caracteres. "
               "Considere ser mais direta.")
```

**AC coberto**: contribui para AC1.6.1 sinalizando o guard antes de o
usuario atingir 4000.

## Componente C8 - InvokePath (fluxo)

**Descricao**: fluxo executado quando um prompt valido e submetido no C6.
Nao e widget; e a orquestracao entre C6, C5 e o servico.

**Sequencia**:

1. Append `{"role": "user", "content": prompt}` a `messages` e
   renderizar via C5.
2. Renderizar `st.chat_message("assistant")` com `st.spinner(
   "Consultando base de conhecimento...")` [st AC1.1.4][mk].
3. Chamar `ask_agent(prompt=prompt, session_id=st.session_state.session_id,
   model_id=st.session_state.model_id)` (assinatura em `src/invoke.py`).
4. **Sucesso**: substituir o spinner pelo texto retornado; append
   `{"role": "assistant", "content": resposta}` a `messages`.
5. **`ValueError` do guard (defense-in-depth)**: renderizar
   `st.warning(...)` com a copy de C6.
6. **`AgentInvocationError`**: renderizar `st.error(...)` no lugar da
   bolha do assistente. **Nao** faz append da bolha vazia a `messages`
   (para que o usuario possa reenviar sem ver bolha fantasma no historico).

**Snippet**:

```python
if prompt:
    if len(prompt) > 4000:
        st.warning(WARNING_TOO_LONG)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conhecimento..."):
                try:
                    resposta = ask_agent(
                        prompt=prompt,
                        session_id=st.session_state.session_id,
                        model_id=st.session_state.model_id,
                    )
                    st.markdown(resposta)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": resposta}
                    )
                except AgentInvocationError as err:
                    logging.getLogger(__name__).error(
                        "AgentCore invocation failed", exc_info=err,
                    )
                    st.error(ERROR_MESSAGE)
```

**Copy exata (constantes)** [mk][st AC1.6.1][st AC1.7.2]:

```python
WARNING_TOO_LONG = (
    "Sua pergunta ficou muito longa para eu processar. "
    "Tente resumir em uma unica pergunta mais curta."
)
ERROR_MESSAGE = (
    "Nao consegui responder agora. Tente novamente em alguns segundos "
    "ou contate o RH se o problema persistir."
)
```

**AC coberto**: AC1.1.4, AC1.6.1, AC1.6.2, AC1.7.1 (via `src/invoke.py`),
AC1.7.2, AC1.7.3, AC1.4.2, AC1.5.2 (via texto retornado).

## Componente C9 - InitializationOnLoad

**Descricao**: bloco no topo de `frontend/app.py` que inicializa
`st.session_state` na primeira renderizacao.
**Snippet**:

```python
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": GREETING_MESSAGE}
    ]
if "model_id" not in st.session_state:
    st.session_state.model_id = MODEL_OPTIONS[0]
```

**AC coberto**: pre-condicao para AC1.1.4, AC1.9.5 e AC4.1.1.

## Fluxo de transicao (state machine)

Transicoes documentadas de forma explicita para reduzir a leitura de
`mockups.md § Estados agregados`:

```text
    +--------+  user_input       +----------+  resposta OK    +---------+
    |  Idle  | ----------------> | Enviando | --------------> |   Idle  |
    +--------+                   +----------+                  +---------+
       |  ^                          |                             |
       |  | limpar_conversa          | erro                        |
       |  +--------------------------+                             |
       |                             v                             |
       |                        +----------+                       |
       |                        |   Erro   | ---- reenvia ---------+
       |                        +----------+
       |
       | troca_modelo (ortogonal, nao altera messages nem session_id)
       v
    +--------+
    |  Idle  |
    +--------+
```

- **Transicao user_input**: guard `<= 4000 chars` [st AC1.6.2]; caso
  contrario `Idle -> Idle` com `st.warning` [st AC1.6.1].
- **Transicao resposta OK**: texto plano em portugues, ancorado nos
  documentos [rq FR7.1][rq NFR2.1].
- **Transicao erro**: `st.error` renderizado; historico preservado.
- **Transicao limpar_conversa**: `Idle/Enviando/Erro -> Idle` com nova
  `session_id` e `messages` resetado [st AC1.9.1-1.9.5].
- **Transicao troca_modelo**: nao muda o estado do chat; ortogonal
  [st AC4.1.4].

## Alinhamento com team-practices

- **Fronteira de camada** [tp]: nenhum componente listado importa `boto3`;
  toda chamada externa passa por `src.invoke.ask_agent`.
- **Error handling** [tp][rq FR9]: apenas exceptions de dominio
  (`AgentInvocationError`, `ValueError`) capturadas; sem `except:` largo.
  `logging.getLogger(__name__).error(...)` conforme convencao.
- **Naming** [tp]: `snake_case` para variaveis e funcoes, `UPPER_SNAKE`
  para constantes de copy (`WARNING_TOO_LONG`, `ERROR_MESSAGE`,
  `GREETING_MESSAGE`, `MODEL_OPTIONS`).
- **Sem CSS customizado** [q2]: nao ha `st.markdown(unsafe_allow_html=True)`
  nem `st.components.v1.html` neste MVP.

## Assumptions & Open Questions

- **Contrato final de `ask_agent`**: assinatura assumida
  `ask_agent(prompt, session_id, model_id) -> str`. A resolucao final
  vive em `contract-design`. Se o formato variar (ex.: retornar objeto
  com metadados), a interacao no C8 precisa ajustar antes de code-generation.
- **Formato de erro rich**: se a equipe decidir por um objeto
  `AgentInvocationError` com codigos (throttling vs timeout vs IAM), o C8
  pode diferenciar copys (fica como refinamento). MVP mantem uma copy
  unica.

<!-- confirmed 2026-08-24 -->
