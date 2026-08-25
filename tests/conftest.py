"""Fixtures centrais de mock (team.md Testing Posture).

- Sem chamada AWS real em nenhum teste unitario.
- Mock do cliente `bedrock-agentcore` para `src/invoke.py`.
- Mock de `BedrockModel` e stub de `retrieve` para `agent/agent.py`.
"""

from __future__ import annotations

import json
import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def _env_agent_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set env vars mandatorios do src/invoke.py e agent/agent.py."""
    monkeypatch.setenv(
        "AGENT_RUNTIME_ARN",
        "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/hr-agent-test",
    )
    monkeypatch.setenv(
        "INFERENCE_PROFILE_ARN_CLAUDE_HAIKU",
        "arn:aws:bedrock:us-east-1:123456789012:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0",
    )
    monkeypatch.setenv(
        "INFERENCE_PROFILE_ARN_NOVA_PRO",
        "arn:aws:bedrock:us-east-1:123456789012:inference-profile/us.amazon.nova-pro-v1:0",
    )
    monkeypatch.setenv("KNOWLEDGE_BASE_ID", "TESTKBID42")
    monkeypatch.setenv("AWS_REGION", "us-east-1")


@pytest.fixture
def mock_agentcore(_env_agent_runtime: None) -> Any:
    """Mocka `boto3.client('bedrock-agentcore')` para o modulo src.invoke.

    Retorna o MagicMock do client para os testes configurarem o response.
    """
    # Import tardio para pegar o env var configurado.
    import src.invoke as invoke_mod

    mock_client = MagicMock()
    monkey_target = invoke_mod.agentcore_client
    invoke_mod.agentcore_client = mock_client
    yield mock_client
    invoke_mod.agentcore_client = monkey_target


def _make_agentcore_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Constroi o shape que agentcore_client.invoke_agent_runtime retorna."""
    body_bytes = json.dumps(payload).encode()
    return {"response": MagicMock(read=MagicMock(return_value=body_bytes))}


@pytest.fixture
def make_agentcore_response():
    """Factory para o teste montar o response com payload custom."""
    return _make_agentcore_response


@pytest.fixture
def mock_bedrock_model(_env_agent_runtime: None):
    """Mocka `BedrockModel` do agent/agent.py e stub da tool `retrieve`.

    Retorna (patched_agent_call, patched_bedrock_model) para o teste
    configurar o retorno de `agent(prompt)`.
    """
    from unittest.mock import MagicMock

    # Reimport limpo do modulo agent para nao carregar state anterior
    with patch("agent.agent.BedrockModel") as bm, patch("agent.agent.Agent") as ag, \
         patch("agent.agent.retrieve") as rt:
        agent_instance = MagicMock()
        ag.return_value = agent_instance
        # default: response canonica que NAO viola LGPD
        agent_instance.return_value = "De acordo com a politica, voce tem direito a 30 dias de ferias anuais."
        yield {"model": bm, "agent_cls": ag, "agent": agent_instance, "retrieve": rt}
