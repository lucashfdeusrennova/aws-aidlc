"""Chatbot de RH - Strands Agent para AgentCore Runtime.

Modulo unico (Q1=A do nfr-design): contem prompt sections, dicionario
label -> env var, handler `invoke(payload)`, e helper `log_event`.

Fronteira: este arquivo roda DENTRO da microVM do AgentCore Runtime.
NAO importa `src/` nem `frontend/`.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import retrieve

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = BedrockAgentCoreApp()


# ---------------------------------------------------------------------------
# System prompt (4 secoes concatenadas - BR2.1 do functional-spec)
# ---------------------------------------------------------------------------

_ROLE_SECTION = """Voce e um assistente virtual de Recursos Humanos.
Sua funcao e responder perguntas de colaboradores sobre politicas de RH
com base em 5 documentos indexados:
- Manual do funcionario (politicas gerais)
- Politica de licenca e ferias
- Checklist de onboarding
- Diretrizes de avaliacao de desempenho
- Calendario de feriados publicos

Use APENAS informacoes retornadas pela ferramenta `retrieve`. NAO invente
dados. Se a ferramenta nao retornar trechos relevantes, siga a instrucao
da secao "FALLBACK" abaixo."""


_LGPD_SECTION = """NUNCA divulgar informacoes individuais de colaboradores.
Isso inclui: salarios, remuneracao, dados de folha de pagamento, historico
disciplinar, avaliacoes nominais, dados pessoais (CPF, RG, endereco,
telefone, e-mail), nomes de colaboradores como sujeito de dado individual.

Se o usuario pedir esse tipo de informacao (ex.: "qual o salario de Joao",
"como o Pedro esta indo na avaliacao"), recuse com uma resposta contendo
a palavra "RH" e uma dessas frases:
- "nao posso compartilhar informacoes pessoais"
- "nao posso divulgar dados individuais"
- "essa informacao pessoal nao pode ser compartilhada aqui"

Sugira que o usuario procure diretamente o time de RH. Esta regra se
aplica MESMO que a ferramenta `retrieve` retorne trechos com dados
individuais - nao repita valores nem nomes verbatim."""


_FALLBACK_SECTION = """Se a ferramenta `retrieve` retornar array vazio,
ou se os trechos retornados nao responderem a pergunta, responda
LITERALMENTE:

"Nao encontrei essa informacao nos documentos. Sugiro contatar o time
de RH."

Nao ofereca palpite baseado em conhecimento geral. Nao explique por que
nao encontrou."""


_TONE_SECTION = """Responda sempre em portugues brasileiro. Tom
formal-neutro, sem gírias, sem emojis. Limite a 2-4 frases por resposta.
Nao cite o nome do documento fonte na resposta (o usuario nao precisa
saber que veio de "employee_handbook.pdf"). Nao inclua sugestoes
prescritivas alem do que os documentos dizem."""


_SYSTEM_PROMPT = "\n\n".join(
    [_ROLE_SECTION, _LGPD_SECTION, _FALLBACK_SECTION, _TONE_SECTION]
)


# ---------------------------------------------------------------------------
# Label -> env var (BR6.1 - resolucao label -> ARN)
# ---------------------------------------------------------------------------

_MODEL_LABEL_TO_ENVVAR: dict[str, str] = {
    "Amazon Nova Pro": "INFERENCE_PROFILE_ARN_NOVA_PRO",
    "Amazon Nova Lite": "INFERENCE_PROFILE_ARN_NOVA_LITE",
    "Amazon Nova 2 Lite": "INFERENCE_PROFILE_ARN_NOVA_2_LITE",
    "Claude Haiku 4.5": "INFERENCE_PROFILE_ARN_CLAUDE_HAIKU",
}


_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Regex para classificacao de outcome (Q2=A do nfr-design)
_FALLBACK_PATTERN = re.compile(r"nao encontrei", re.IGNORECASE)
_REFUSAL_PATTERN = re.compile(
    r"nao posso (compartilhar|divulgar)|informacao pessoal|informacoes pessoais",
    re.IGNORECASE,
)
_RH_KEYWORD = re.compile(r"\brh\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log_event(level: str, **fields: Any) -> None:
    """Emit a JSON-structured log line (Q3=A do nfr-design).

    LGPD guard: campos permitidos sao os 6 fixos de NFR4.1.3 mais campos
    de erro. NUNCA logar `prompt`, `response`, ou trechos da KB.
    """
    payload = {"timestamp": datetime.now(timezone.utc).isoformat(), **fields}
    line = json.dumps(payload, ensure_ascii=False, default=str)
    if level == "ERROR":
        logger.error(line)
    else:
        logger.info(line)


def _classify_outcome(response_text: str) -> str:
    """Classifica outcome baseado no texto da resposta (Q2=A).

    Ordem importa: refusal antes de fallback (uma recusa LGPD pode conter
    "nao encontrei" incidentalmente, mas o sinal de PII e mais forte).
    """
    if _REFUSAL_PATTERN.search(response_text) and _RH_KEYWORD.search(response_text):
        return "refusal"
    if _FALLBACK_PATTERN.search(response_text) and _RH_KEYWORD.search(response_text):
        return "fallback"
    return "success"


# ---------------------------------------------------------------------------
# Handler - entrypoint chamado pelo AgentCore Runtime
# ---------------------------------------------------------------------------


@app.entrypoint
def invoke(payload: dict[str, Any]) -> dict[str, str]:
    """Handler principal invocado pelo AgentCore Runtime.

    Payload C1 request (contract-summary):
        {"prompt": str, "context": {"model_id": str}}

    Payload C1 response:
        {"response": str, "model_id": str, "session_id": str}
    """
    prompt = payload["prompt"]  # KeyError propaga se ausente
    context = payload.get("context") or {}
    label = context["model_id"]  # KeyError propaga (BR6.4 - fail-fast)
    session_id = payload.get("session_id") or context.get("session_id") or ""

    # BR6.1 - resolve label -> ARN via env var
    envvar_name = _MODEL_LABEL_TO_ENVVAR[label]  # KeyError propaga (BR6.3)
    arn = os.environ[envvar_name]                # KeyError propaga

    try:
        model = BedrockModel(model_id=arn, region_name=_REGION)
        agent = Agent(model=model, system_prompt=_SYSTEM_PROMPT, tools=[retrieve])

        t0 = time.perf_counter()
        result = agent(prompt)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)

        response_text = str(result)
        outcome = _classify_outcome(response_text)

        log_event(
            "INFO",
            runtimeSessionId=session_id,
            model_id=label,
            retrieve_hits=-1,   # SDK nao expõe contagem trivialmente; -1 = desconhecido
            response_ms=elapsed_ms,
            outcome=outcome,
        )
        return {
            "response": response_text,
            "model_id": label,      # BR6.2 - echo do label
            "session_id": session_id,  # BR7.2 - echo do session_id
        }
    except Exception as exc:
        log_event(
            "ERROR",
            runtimeSessionId=session_id,
            model_id=label,
            error_type=type(exc).__name__,
            error_message=str(exc)[:200],
            outcome="error",
        )
        raise


# ---------------------------------------------------------------------------
# AgentCore Runtime entrypoint (por convention: modulo executado)
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app.run()
