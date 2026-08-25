"""Streamlit chat UI para o chatbot de RH.

Executa localmente: `streamlit run frontend/app.py`.
Requer `AGENT_RUNTIME_ARN` e (opcionalmente) `AWS_REGION` no ambiente.
"""

from __future__ import annotations

import uuid

import streamlit as st

from src.invoke import (
    AgentInvocationError,
    MODEL_LABELS_TO_ARN_ENV,
    ask_agent,
)

st.set_page_config(page_title="Assistente de RH", page_icon="[RH]", layout="centered")
st.title("Assistente Virtual de RH")
st.caption("Chatbot demo - politicas de RH, ferias, onboarding e avaliacoes.")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_id" not in st.session_state:
    st.session_state.model_id = next(iter(MODEL_LABELS_TO_ARN_ENV.keys()))

# ---------------------------------------------------------------------------
# Sidebar - selecao de modelo + reset
# ---------------------------------------------------------------------------
with st.sidebar:
    st.subheader("Configuracao")
    labels = list(MODEL_LABELS_TO_ARN_ENV.keys())
    st.session_state.model_id = st.selectbox(
        "Modelo",
        labels,
        index=labels.index(st.session_state.model_id),
        help="Troca o inference profile ARN usado pelo Strands Agent.",
    )
    st.caption(f"session_id: `{st.session_state.session_id[:8]}...`")

    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Historico
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("model_used"):
            st.caption(f"[Modelo: {msg['model_used']}]")

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
prompt = st.chat_input("Pergunte sobre politicas de RH, ferias, onboarding...")
if prompt:
    if len(prompt) > 4000:
        st.warning("A pergunta esta muito longa (limite: 4000 caracteres).")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando base de conhecimento..."):
                try:
                    result = ask_agent(
                        question=prompt,
                        session_id=st.session_state.session_id,
                        model_id=st.session_state.model_id,
                    )
                    answer = result["response"]
                    model_used = result["model_id"]
                    st.write(answer)
                    st.caption(f"[Modelo: {model_used}]")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "model_used": model_used}
                    )
                except ValueError as exc:
                    st.warning(str(exc))
                except AgentInvocationError as exc:
                    st.error(f"Nao consegui responder agora. Tente novamente em alguns segundos.\n\nDetalhe: {exc}")
