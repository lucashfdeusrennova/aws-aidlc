"""Testes unitarios de `src/invoke.py`.

Cobre: happy path, guard 4000 chars, ClientError propagation, resposta
vazia como AgentInvocationError, ausencia de AGENT_RUNTIME_ARN.
"""

from __future__ import annotations

import json

import pytest
from botocore.exceptions import ClientError


def test_ask_agent_happy_path(mock_agentcore, make_agentcore_response):
    from src.invoke import ask_agent

    mock_agentcore.invoke_agent_runtime.return_value = make_agentcore_response(
        {
            "response": "Voce tem direito a 30 dias de ferias anuais.",
            "model_id": "Claude Haiku 4.5",
            "session_id": "sess-abc",
        }
    )

    result = ask_agent("Quantos dias de ferias tenho?", "sess-abc", "Claude Haiku 4.5")

    assert result["response"] == "Voce tem direito a 30 dias de ferias anuais."
    assert result["model_id"] == "Claude Haiku 4.5"
    assert result["session_id"] == "sess-abc"


def test_ask_agent_rejects_prompt_over_4000_chars(_env_agent_runtime):
    from src.invoke import ask_agent

    long_prompt = "a" * 4001
    with pytest.raises(ValueError, match="4001"):
        ask_agent(long_prompt, "sess-abc")


def test_ask_agent_wraps_client_error(mock_agentcore):
    from src.invoke import AgentInvocationError, ask_agent

    mock_agentcore.invoke_agent_runtime.side_effect = ClientError(
        {"Error": {"Code": "ThrottlingException", "Message": "slow down"}},
        "InvokeAgentRuntime",
    )

    with pytest.raises(AgentInvocationError, match="ThrottlingException"):
        ask_agent("Pergunta", "sess-abc")


def test_ask_agent_missing_runtime_arn(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("AGENT_RUNTIME_ARN", raising=False)
    from src.invoke import AgentInvocationError, ask_agent

    with pytest.raises(AgentInvocationError, match="AGENT_RUNTIME_ARN"):
        ask_agent("Pergunta", "sess-abc")


def test_ask_agent_empty_response(mock_agentcore, make_agentcore_response):
    from src.invoke import AgentInvocationError, ask_agent

    mock_agentcore.invoke_agent_runtime.return_value = make_agentcore_response(
        {"response": "", "model_id": "Claude Haiku 4.5", "session_id": "sess"}
    )

    with pytest.raises(AgentInvocationError, match="vazia"):
        ask_agent("Pergunta", "sess")


def test_ask_agent_invalid_json_body(mock_agentcore):
    from unittest.mock import MagicMock

    from src.invoke import AgentInvocationError, ask_agent

    mock_agentcore.invoke_agent_runtime.return_value = {
        "response": MagicMock(read=MagicMock(return_value=b"this is not json"))
    }
    with pytest.raises(AgentInvocationError, match="nao-JSON"):
        ask_agent("Pergunta", "sess")


def test_ask_agent_falls_back_to_output_text_shape(mock_agentcore, make_agentcore_response):
    """Compatibilidade com shape antigo `{output: {text: ...}}` do tech-env exemplo."""
    from src.invoke import ask_agent

    mock_agentcore.invoke_agent_runtime.return_value = make_agentcore_response(
        {"output": {"text": "30 dias de ferias."}}
    )
    result = ask_agent("Ferias?", "sess-abc")
    assert "30 dias" in result["response"]
