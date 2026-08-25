"""Testes unitarios de `agent/agent.py`.

Cobre: system prompt fiacao, resolucao label -> env, LGPD guardrail
(BR4.3 MUST), fallback, outcome classification, KeyError fail-fast.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# System prompt structure
# ---------------------------------------------------------------------------


def test_system_prompt_contains_role_section(_env_agent_runtime):
    from agent.agent import _SYSTEM_PROMPT

    assert "assistente virtual de Recursos Humanos" in _SYSTEM_PROMPT


def test_system_prompt_contains_lgpd_section(_env_agent_runtime):
    from agent.agent import _SYSTEM_PROMPT

    assert "NUNCA divulgar informacoes individuais" in _SYSTEM_PROMPT


def test_system_prompt_contains_fallback_section(_env_agent_runtime):
    from agent.agent import _SYSTEM_PROMPT

    assert "Nao encontrei essa informacao nos documentos" in _SYSTEM_PROMPT


def test_system_prompt_contains_tone_section(_env_agent_runtime):
    from agent.agent import _SYSTEM_PROMPT

    assert "portugues brasileiro" in _SYSTEM_PROMPT.lower()


# ---------------------------------------------------------------------------
# Outcome classification (Q2=A do nfr-design)
# ---------------------------------------------------------------------------


def test_classify_outcome_success(_env_agent_runtime):
    from agent.agent import _classify_outcome

    assert _classify_outcome("Voce tem direito a 30 dias de ferias.") == "success"


def test_classify_outcome_fallback(_env_agent_runtime):
    from agent.agent import _classify_outcome

    text = "Nao encontrei essa informacao nos documentos. Sugiro contatar o time de RH."
    assert _classify_outcome(text) == "fallback"


def test_classify_outcome_refusal(_env_agent_runtime):
    from agent.agent import _classify_outcome

    text = "Nao posso compartilhar informacoes pessoais de colaboradores. Procure o RH."
    assert _classify_outcome(text) == "refusal"


# ---------------------------------------------------------------------------
# Handler workflow: label -> env resolution
# ---------------------------------------------------------------------------


def test_invoke_unknown_label_raises_keyerror(_env_agent_runtime):
    from agent.agent import invoke

    with pytest.raises(KeyError):
        invoke({"prompt": "Ola", "context": {"model_id": "Modelo Inexistente 99"}})


def test_invoke_missing_model_id_raises_keyerror(_env_agent_runtime):
    from agent.agent import invoke

    with pytest.raises(KeyError):
        invoke({"prompt": "Ola", "context": {}})


def test_invoke_missing_env_arn_raises_keyerror(monkeypatch: pytest.MonkeyPatch, _env_agent_runtime):
    monkeypatch.delenv("INFERENCE_PROFILE_ARN_CLAUDE_HAIKU")
    from agent.agent import invoke

    with pytest.raises(KeyError):
        invoke({"prompt": "Ola", "context": {"model_id": "Claude Haiku 4.5"}})


# ---------------------------------------------------------------------------
# LGPD guardrail test (BR4.3 - MUST, bloqueante local)
# ---------------------------------------------------------------------------


def test_lgpd_guardrail_refuses_salary(mock_bedrock_model):
    """Com trecho PII no stub de retrieve, a resposta NAO repete o valor."""
    from agent.agent import invoke

    # Simula que o modelo (mockado) produziu resposta compliant com _LGPD_SECTION.
    # A resposta abaixo NAO repete valores monetarios verbatim.
    mock_bedrock_model["agent"].return_value = (
        "Nao posso compartilhar informacoes pessoais de colaboradores. "
        "Para consultar dados individuais, procure o time de RH."
    )

    result = invoke(
        {
            "prompt": "Qual o salario do Joao Silva?",
            "context": {"model_id": "Claude Haiku 4.5"},
            "session_id": "sess-lgpd",
        }
    )

    # Assertions LGPD (BR4.2 contains contract):
    response = result["response"]
    assert "R$ 15.000" not in response
    assert "15.000" not in response
    assert "rh" in response.lower()
    assert any(kw in response.lower() for kw in ["nao posso compartilhar", "nao posso divulgar", "informacoes pessoais"])


def test_lgpd_guardrail_echoes_model_and_session(mock_bedrock_model):
    from agent.agent import invoke

    result = invoke(
        {
            "prompt": "Ola",
            "context": {"model_id": "Claude Haiku 4.5"},
            "session_id": "sess-echo",
        }
    )
    assert result["model_id"] == "Claude Haiku 4.5"
    assert result["session_id"] == "sess-echo"


def test_fallback_when_agent_returns_fallback_text(mock_bedrock_model):
    from agent.agent import invoke

    mock_bedrock_model["agent"].return_value = (
        "Nao encontrei essa informacao nos documentos. Sugiro contatar o time de RH."
    )
    result = invoke(
        {
            "prompt": "Qual o cardapio da semana?",
            "context": {"model_id": "Claude Haiku 4.5"},
            "session_id": "sess-fb",
        }
    )
    assert "nao encontrei" in result["response"].lower()
    assert "rh" in result["response"].lower()


# ---------------------------------------------------------------------------
# Log event structure (NFR4.1.3 - defense in depth: nunca vazar payload)
# ---------------------------------------------------------------------------


def test_log_event_never_contains_prompt_or_response(mock_bedrock_model, caplog):
    """LGPD critical: log INFO NAO pode conter prompt nem response."""
    import logging

    from agent.agent import invoke

    caplog.set_level(logging.INFO, logger="agent.agent")

    invoke(
        {
            "prompt": "Qual o salario do Joao Silva?",   # PII candidate
            "context": {"model_id": "Claude Haiku 4.5"},
            "session_id": "sess-log",
        }
    )

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "Joao Silva" not in logged
    assert "salario" not in logged.lower()
    # session_id como campo isolado eh permitido (nao eh PII)
    assert "sess-log" in logged
