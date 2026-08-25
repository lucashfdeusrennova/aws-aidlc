"""AgentInvoker: cola boto3 -> AgentCore Runtime.

Fronteira: NAO importa `streamlit`. Consumido por `frontend/app.py`.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Single client per module (team.md Code Style - Idiomas Python 3.12)
agentcore_client = boto3.client("bedrock-agentcore", region_name=_REGION)

# BR6.1 chat-frontend: label -> ARN via env var
# Ordem = ordem do dropdown; primeiro item = default.
# Claude Haiku 4.5 depende de aprovacao de agreement no Bedrock Marketplace
# (Anthropic). Habilite em Console > Bedrock > Model access e adicione a linha
# comentada abaixo de volta ao dict.
MODEL_LABELS_TO_ARN_ENV: dict[str, str] = {
    "Amazon Nova Pro": "INFERENCE_PROFILE_ARN_NOVA_PRO",
    # "Claude Haiku 4.5": "INFERENCE_PROFILE_ARN_CLAUDE_HAIKU",
}

_MAX_PROMPT_LEN = 4000  # NFR4.1.2 - guard primario


class AgentInvocationError(Exception):
    """Exception de dominio para falhas de invocacao ao AgentCore Runtime."""


def _get_runtime_arn() -> str:
    arn = os.environ.get("AGENT_RUNTIME_ARN")
    if not arn:
        raise AgentInvocationError(
            "AGENT_RUNTIME_ARN nao configurado. Exporte a env var antes de rodar."
        )
    return arn


def ask_agent(
    question: str,
    session_id: str,
    model_id: str = "Claude Haiku 4.5",
) -> dict[str, str]:
    """Invoca o agente deployado no AgentCore Runtime.

    Args:
        question: prompt do usuario (max 4000 chars).
        session_id: UUID gerado por chat-frontend via uuid.uuid4().
        model_id: label humano do modelo (chave em MODEL_LABELS_TO_ARN_ENV).

    Returns:
        dict com {response, model_id, session_id}.

    Raises:
        ValueError: se `question` estourar 4000 chars.
        AgentInvocationError: para qualquer falha do runtime AWS.
    """
    if len(question) > _MAX_PROMPT_LEN:
        raise ValueError(
            f"Pergunta com {len(question)} caracteres excede o limite de {_MAX_PROMPT_LEN}."
        )

    runtime_arn = _get_runtime_arn()

    payload = json.dumps(
        {
            "prompt": question,
            "context": {"model_id": model_id},
            "session_id": session_id,
        }
    ).encode()

    try:
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            runtimeSessionId=session_id,
            payload=payload,
            qualifier="DEFAULT",
        )
    except ClientError as exc:
        logger.error("AgentCore ClientError: %s", exc, exc_info=True)
        err = exc.response.get("Error", {})
        code = err.get("Code", "Unknown")
        msg = err.get("Message", "")
        # AccessDenied com aws-marketplace indica agreement Anthropic pendente
        if code == "AccessDeniedException" and "aws-marketplace" in msg.lower():
            raise AgentInvocationError(
                "Modelo bloqueado: falta aceitar o agreement no Bedrock Marketplace "
                "(Console > Bedrock > Model access)."
            ) from exc
        raise AgentInvocationError(f"Falha ao invocar o agente: {code}") from exc

    body = response.get("response")
    if body is None:
        raise AgentInvocationError("AgentCore retornou resposta vazia (sem body).")

    raw = body.read() if hasattr(body, "read") else body
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")

    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentInvocationError(f"AgentCore retornou payload nao-JSON: {raw[:200]}") from exc

    answer = data.get("response") or data.get("output", {}).get("text") or ""
    if not answer:
        raise AgentInvocationError("Resposta vazia do agente.")

    return {
        "response": answer,
        "model_id": data.get("model_id", model_id),
        "session_id": data.get("session_id", session_id),
    }
