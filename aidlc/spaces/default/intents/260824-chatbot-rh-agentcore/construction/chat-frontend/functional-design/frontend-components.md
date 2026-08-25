**Collaborator:** aidlc-architect-agent

# Frontend Components - Unit chat-frontend

Hierarquia de componentes Streamlit, props/state design, e integracao com
`AgentInvoker`. Fontes: `unit-of-work.md`, `unit-of-work-story-map.md`,
`requirements.md`, `components.md`, `contract-summary.md`. Deriva de
`interaction-spec.md` de refined-mockups.

## Sources

- [uw] `unit-of-work.md`.
- [sm] `unit-of-work-story-map.md`.
- [rq] `requirements.md`.
- [cp] `components.md`.
- [cs] `contract-summary.md`.
- [is] `interaction-spec.md` (refined-mockups).
- [mk] `mockups.md` (refined-mockups).
- [ds] `design-system-mapping.md` (refined-mockups).

## Component hierarchy

```text
Page (frontend/app.py entrypoint)
├── PageHeader
│   ├── Title ("Assistente Virtual de RH")
│   └── ModelCaption ("Modelo em uso: {model_id}")
├── Sidebar
│   ├── ModelSelector (st.selectbox)
│   └── ClearConversationButton (st.button)
├── ChatArea
│   ├── ChatHistory (loop over st.session_state.messages)
│   │   └── MessageBubble (st.chat_message per role)
│   ├── ChatInput (st.chat_input)
│   └── CharCounter (st.caption, condicional 3500 < n <= 4000)
└── ErrorRegions
    ├── WarningBox (st.warning, on submit >4000)
    └── ErrorBox (st.error, on AgentInvocationError)
```

## Session state schema

Todas as chaves de `st.session_state` que a unit gerencia. Type hints
obrigatorios em toda funcao exportada [tp § Code Style].

| Key            | Type            | Init value                                   | Owner                      | AC coverage         |
| -------------- | --------------- | -------------------------------------------- | -------------------------- | ------------------- |
| `session_id`   | `str` (uuid)    | `str(uuid.uuid4())` no primeiro carregamento | `_init_session_state()`    | AC1.9.2, AC1.9.4    |
| `messages`     | `list[dict]`    | `[{"role": "assistant", "content": GREETING_MESSAGE}]` | `_init_session_state()` + append por turno | AC1.9.3, AC1.9.5    |
| `model_id`     | `str`           | `MODEL_OPTIONS[0]` = `"Claude Haiku 4.5"`    | `st.selectbox` via `key="model_selector"` | AC4.1.1, AC4.1.4    |

Cada `messages[i]` tem shape `{"role": "user" | "assistant", "content": str}`.

## Widget catalogue

Um bloco por widget Streamlit visivel; alinhado com `interaction-spec.md § C1..C9`.

### W1 - Title

- Widget: `st.title("Assistente Virtual de RH")`
- Location: topo da pagina.
- Semantica: `<h1>`, focavel por leitor de tela.
- AC: (nenhum direto; suporte a acessibilidade).

### W2 - ModelCaption

- Widget: `st.caption(f"Modelo em uso: {st.session_state.model_id}")`
- Location: logo abaixo do Title.
- Reativo: rerender a cada troca no ModelSelector.
- AC: AC4.1.2 (materializa `model_id` observavel na UI).

### W3 - ModelSelector

- Widget: `st.sidebar.selectbox("Modelo de chat", options=MODEL_OPTIONS, index=<posicao atual>, key="model_selector")`
- Constant: `MODEL_OPTIONS = ["Claude Haiku 4.5", "Amazon Nova Pro"]`.
- Interacao: mudanca dispara rerun, atualiza `st.session_state.model_id` via `key`.
- **U1 nao carrega `MODEL_ARNS`**. A resolucao label -> inference profile ARN vive em U2 (hr-agent) via env vars C3 (`INFERENCE_PROFILE_ARN_*`) - decisao tomada em `functional-spec.md § AC4.1.3` (resolve Q3 de contract-summary).
- AC: AC4.1.1, AC4.1.4 (AC4.1.3 e verificada em U2).

### W4 - ClearConversationButton

- Widget: `st.sidebar.button("Limpar conversa", on_click=_clear_conversation, key="clear_chat")`
- Callback `_clear_conversation()`:
  1. `st.session_state.session_id = str(uuid.uuid4())`
  2. `st.session_state.messages = [{"role": "assistant", "content": GREETING_MESSAGE}]`
- Sem confirmation dialog.
- AC: AC1.9.1, AC1.9.2, AC1.9.3, AC1.9.5.

### W5 - ChatHistory (iteracao)

- Widget composto:

```python
# 15 linhas ilustrativas — code-generation materializa
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

- AC: (renderiza AC1.9.5 + o wiring E2E de US1.1-1.5, US2.1, US3.1).

### W6 - ChatInput

- Widget: `prompt = st.chat_input("Pergunte sobre politicas de RH...")`
- Submit por Enter ou botao embutido.
- AC: (entry point; guardado por W7 e W8).

### W7 - WarningBox (>4000 chars)

- Widget: `st.warning(WARNING_TOO_LONG)` renderizado condicionalmente.
- Copy exata: `WARNING_TOO_LONG = "Sua pergunta ficou muito longa para eu processar. Tente resumir em uma unica pergunta mais curta."`
- Trigger: `if prompt and len(prompt) > 4000` no fluxo pos-submit.
- AC: AC1.6.1.

### W8 - CharCounter hint (post-submit hint para proxima mensagem)

- Widget: `st.caption(f"Sua ultima pergunta teve {len(last_prompt)}/4000 caracteres. Tente ser mais direta na proxima.")` renderizado condicionalmente `if last_prompt is not None and 3500 < len(last_prompt) <= 4000`.
- **Post-submit** apenas (limitacao de `st.chat_input` que nao expoe valor ao vivo). Serve como hint para a proxima pergunta, nao como guard - guard e W7 para inputs >4000.
- Copy explicitamente NAO clama contribuir a AC1.6.1 (que trata >4000, coberto por W7).
- AC: (nenhum direto; UX hint opcional).

### W9 - ErrorBox

- Widget: `st.error(ERROR_MESSAGE)` renderizado no bloco `except AgentInvocationError`.
- Copy exata: `ERROR_MESSAGE = "Nao consegui responder agora. Tente novamente em alguns segundos ou contate o RH se o problema persistir."`
- AC: AC1.7.2.

### W10 - Spinner (feedback durante invoke)

- Widget: `st.spinner("Consultando base de conhecimento...")` como context manager dentro de `st.chat_message("assistant")`.
- Sumido ao final da chamada (sucesso ou erro).
- AC: (feedback; suporta AC1.6.2, AC1.9.4).

## Constants (module-level, UPPER_SNAKE)

```python
# 15 linhas ilustrativas — code-generation materializa
GREETING_MESSAGE: str = (
    "Ola! Sou o assistente de RH. Posso ajudar com politicas de RH, "
    "ferias, onboarding e avaliacoes. Qual sua duvida?"
)
WARNING_TOO_LONG: str = (
    "Sua pergunta ficou muito longa para eu processar. "
    "Tente resumir em uma unica pergunta mais curta."
)
ERROR_MESSAGE: str = (
    "Nao consegui responder agora. Tente novamente em alguns segundos "
    "ou contate o RH se o problema persistir."
)
MODEL_OPTIONS: list[str] = ["Claude Haiku 4.5", "Amazon Nova Pro"]
```

## Logging config (top-level de frontend/app.py)

```python
# 15 linhas ilustrativas — code-generation materializa
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
```

Cobre tanto o logger do modulo em `__main__` (Streamlit) quanto o logger
`src.invoke` invocado internamente. Endereça o finding de logger ambiguo
sem configuracao comum.

## API integration point (frontend -> AgentInvoker)

Assinatura contratada (via `contract-summary.md § C1`):

```python
# 15 linhas ilustrativas — code-generation materializa
from src.invoke import ask_agent, AgentInvocationError

def _submit(prompt: str) -> None:
    if len(prompt) > 4000:
        st.warning(WARNING_TOO_LONG); return
    try:
        resposta = ask_agent(
            prompt=prompt,
            session_id=st.session_state.session_id,
            model_id=st.session_state.model_id,
        )
    except AgentInvocationError as err:
        logging.getLogger(__name__).error("AgentCore invocation failed", exc_info=err)
        st.error(ERROR_MESSAGE); return
    # ... append e render bolha do assistente
```

## Form validation

Somente uma validacao: comprimento maximo de 4000 chars (AC1.6.1). Sem
outros forms neste MVP.

## Non-widgets used

Conforme [ds § Elementos nao usados]: sem tabs, expander, dataframe, form,
file_uploader, download_button, toast, status, progress, components.v1.html,
`unsafe_allow_html`.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
