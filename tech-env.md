# Technical Environment: Chatbot de RH com Bedrock AgentCore

---

## Project Technical Summary

- **Project Type:** Greenfield
- **Primary Language:** Python 3.12
- **Runtime:** Amazon Bedrock AgentCore Runtime (managed serverless microVM)
- **Agent Framework:** Strands Agents SDK
- **RAG:** Bedrock Knowledge Bases + S3 Vectors
- **Frontend:** Streamlit
- **Database:** Nenhum (base de conhecimento via Bedrock Knowledge Bases + S3 Vectors)
- **Infrastructure:** AgentCore Runtime (agente) + Streamlit (frontend local/Cloud9)
- **Package Manager:** pip (requirements.txt)
- **Test Framework:** pytest
- **Linter / Formatter:** ruff
- **IaC Tool:** CDK em Python
- **Region:** `us-east-1` (obrigatorio - Bedrock e S3 Vectors liberados apenas em us-east-1 e us-west-2)

---

## Architecture Overview

```
Colaborador (Browser)
    |
Streamlit App (frontend web)
    |
AgentCore Runtime (invoke_agent_runtime)
    |
Strands Agent (codigo do agente em Python)
    |-- Bedrock Knowledge Bases (tool: busca semantica nos docs de RH)
    |-- AgentCore Memory (historico de conversacao por sessao)
    |-- Model (intercambiavel - ver tabela abaixo)

```

### Fluxo de uma pergunta

1. Usuario digita pergunta no Streamlit
2. Frontend chama `invoke_agent_runtime` via boto3
3. AgentCore Runtime inicia sessao isolada (microVM)
4. Strands Agent recebe o prompt e decide usar a tool de Knowledge Base
5. Tool faz `retrieve` na KB e retorna trechos relevantes dos documentos
6. Agent gera resposta com base nos trechos + instrucao do sistema
7. Resposta retorna ao frontend via streaming

---

## Modelos Bedrock (validados em us-east-1)

### Configuracao recomendada para iniciar

| Funcao | Model ID | Nota |
| --- | --- | --- |
| Chatbot (LLM do agente) | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | 1,9s latencia, bom custo-beneficio para demo |
| Embedding (Knowledge Base) | `cohere.embed-multilingual-v3` (1024 dims) | Melhor acerto em portugues para Knowledge Bases |

### Modelos alternativos para experimentacao

A equipe pode trocar modelos para comparar qualidade e latencia:

| Model ID | Funcao | Caracteristica |
| --- | --- | --- |
| `amazon.nova-pro-v1:0` | chatbot | Mais rapido (1,2s), resposta mais curta |
| `us.anthropic.claude-sonnet-4-6` | chatbot | Melhor redacao, 2,7s |
| `us.meta.llama3-3-70b-instruct-v1:0` | chatbot | Alternativa open weights, 1,8s |
| `amazon.titan-embed-text-v2:0` | embedding | Padrao dos tutoriais; erra mais em PT, aceita 256/512/1024 dims |
| `cohere.rerank-v3-5:0` | reranker | Maior ganho de precisao (separacao de 0,03 para 0,46 entre resultados) |

### Notas importantes sobre modelos

- Modelos com prefixo `us.` funcionam apenas via inference profile. O ARN muda de forma. Passar o ID `us.*` como foundation-model retorna `ResourceNotFoundException`.
- Trocar modelo de embedding requer reindexar a Knowledge Base (nova sincronizacao do data source).
- Trocar modelo de chat nao requer reindexacao - basta alterar no codigo do agente.

---

## Knowledge Base (Documentos de RH)

Os seguintes documentos compoem a base de conhecimento do chatbot. Devem ser carregados no bucket S3 vinculado ao Bedrock Knowledge Bases (vector store: S3 Vectors):

| Documento | Conteudo |
| --- | --- |
| `employee_handbook.pdf` | Manual do funcionario - politicas gerais de RH |
| `leave_policy.pdf` | Politicas de licenca e ferias da empresa |
| `onboarding_checklist.pdf` | Processo de integracao de novos funcionarios |
| `performance_review_guidelines.pdf` | Diretrizes de avaliacao de desempenho |
| `public_holidays.csv` | Calendario de feriados da empresa |

---

## Prohibited Libraries / Patterns

| Prohibited | Reason | Use Instead |
| --- | --- | --- |
| LangChain / LangGraph | Complexidade desnecessaria para esta demo | Strands Agents SDK (AWS-native, mais simples) |
| OpenAI SDK | Projeto usa exclusivamente modelos via Bedrock | boto3 bedrock-runtime / Strands |
| FastAPI/Flask | Frontend e Streamlit, invocacao e via AgentCore | Streamlit + invoke_agent_runtime |
| ChromaDB/Pinecone | Vector store externo nao necessario | Bedrock Knowledge Bases + S3 Vectors (gerenciado) |
| SQLAlchemy | Sem banco de dados relacional no projeto | N/A |
| React/Next.js | Complexidade de frontend desnecessaria para demo | Streamlit |
| `boto3.client("bedrock-agent-runtime")` | Isso e Bedrock Agents, nao AgentCore | `boto3.client("bedrock-agentcore")` |

---

## Security Basics

- **Authentication:** IAM para chamadas ao AgentCore Runtime; credenciais do workshop
- **Authorization:** IAM policies para acesso ao Bedrock, AgentCore, S3 e Knowledge Bases
- **Session Isolation:** Cada sessao roda em microVM isolada (garantido pelo AgentCore Runtime)
- **Input Validation:** Validacao de tamanho maximo da mensagem (4000 chars) no agente
- **PII Handling:** Chatbot nao deve expor dados individuais de funcionarios; respostas limitadas a politicas gerais
- **Secrets Management:** Nenhum segredo customizado necessario (IAM roles)
- **Compliance:** IAM least-privilege; dados em S3 com encryption at rest (SSE-S3)

---

## Example Code Patterns

### Agent Code (Strands Agents)

```python
# agent.py - Codigo do agente que roda no AgentCore Runtime
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools import retrieve

# Modelo configuravel - troque aqui para experimentar
model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-east-1",
)

SYSTEM_PROMPT = """Voce e um assistente virtual de Recursos Humanos.
Responda perguntas dos colaboradores sobre politicas de RH, ferias,
onboarding e avaliacoes de desempenho.

Regras:
- Use APENAS informacoes da base de conhecimento (tool retrieve).
- Responda em portugues, de forma clara e objetiva.
- Cite o documento fonte quando possivel.
- Se nao encontrar a informacao, diga que nao encontrou e sugira contatar o RH.
- NAO invente informacoes.
"""

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[retrieve],
)

```

### Invoking the Agent (Frontend -> AgentCore Runtime)

```python
import boto3
import json
import uuid

agentcore_client = boto3.client("bedrock-agentcore", region_name="us-east-1")

AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/agent-XXXXXXXXXXXX"


def ask_agent(question: str, session_id: str) -> str:
    """Invoca o agente deployado no AgentCore Runtime."""
    payload = json.dumps({"prompt": question}).encode()

    response = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_RUNTIME_ARN,
        runtimeSessionId=session_id,
        payload=payload,
        qualifier="DEFAULT",
    )

    response_data = json.loads(response["response"].read())
    return response_data.get("output", {}).get("text", "")

```

### Frontend Example (Streamlit)

```python
import streamlit as st
import boto3
import json
import uuid

st.set_page_config(page_title="Assistente de RH", page_icon="")
st.title("Assistente Virtual de RH")

agentcore_client = boto3.client("bedrock-agentcore", region_name="us-east-1")
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/agent-XXXXXXXXXXXX"

# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Pergunte sobre politicas de RH, ferias, onboarding..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando base de conhecimento..."):
            payload = json.dumps({"prompt": prompt}).encode()
            response = agentcore_client.invoke_agent_runtime(
                agentRuntimeArn=AGENT_RUNTIME_ARN,
                runtimeSessionId=st.session_state.session_id,
                payload=payload,
                qualifier="DEFAULT",
            )
            response_data = json.loads(response["response"].read())
            answer = response_data.get("output", {}).get("text", "Sem resposta.")
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

```

### Knowledge Base Tool (usado pelo Strands Agent)

```python
# O Strands SDK ja inclui a tool `retrieve` que faz RAG via Bedrock Knowledge Bases.
# Configuracao da Knowledge Base ID e feita via environment variable ou parametro:

# No deploy do agente, configure:
# KNOWLEDGE_BASE_ID=KB_ID_HERE

# A tool `retrieve` do strands_tools faz automaticamente:
# 1. Busca semantica na KB usando o embedding model configurado
# 2. Retorna os trechos mais relevantes
# 3. O agente usa os trechos para gerar a resposta

```

### Test Example

```python
import json
import pytest
from unittest.mock import patch, MagicMock


def test_ask_agent_returns_answer():
    """Testa a funcao ask_agent com mock do AgentCore."""
    mock_response_body = json.dumps({
        "output": {"text": "De acordo com a politica de ferias, voce tem direito a 30 dias."}
    }).encode()

    mock_response = {
        "response": MagicMock(read=MagicMock(return_value=mock_response_body))
    }

    with patch("boto3.client") as mock_client:
        mock_client.return_value.invoke_agent_runtime.return_value = mock_response

        from src.invoke import ask_agent
        result = ask_agent("Quantos dias de ferias?", "test-session")

        assert "30 dias" in result


def test_ask_agent_handles_empty_response():
    """Testa comportamento com resposta vazia."""
    mock_response_body = json.dumps({"output": {}}).encode()
    mock_response = {
        "response": MagicMock(read=MagicMock(return_value=mock_response_body))
    }

    with patch("boto3.client") as mock_client:
        mock_client.return_value.invoke_agent_runtime.return_value = mock_response

        from src.invoke import ask_agent
        result = ask_agent("Pergunta sem resposta", "test-session")

        assert result == ""

```

---

## Project Structure

```
chatbot-rh-agentcore/
|-- agent/
|   |-- agent.py            # Codigo do Strands Agent (roda no AgentCore Runtime)
|   |-- requirements.txt    # Deps do agente (strands-agents, strands-tools, boto3)
|-- src/
|   |-- invoke.py           # Funcao para invocar o agente via AgentCore
|-- frontend/
|   |-- app.py              # Streamlit app (interface web)
|-- tests/
|   |-- test_invoke.py      # Testes unitarios
|-- docs/
|   |-- knowledge-base/     # Documentos de RH para a base de conhecimento
|   |   |-- employee_handbook.pdf
|   |   |-- leave_policy.pdf
|   |   |-- onboarding_checklist.pdf
|   |   |-- performance_review_guidelines.pdf
|   |   |-- public_holidays.csv
|-- requirements.txt
|-- requirements-dev.txt
|-- README.md

```

---

## How to Run

| Command | Description |
| --- | --- |
| `export AWS_DEFAULT_REGION=us-east-1` | Configurar regiao (obrigatorio) |
| `pip install -r requirements.txt` | Install dependencies |
| `pytest` | Run tests |
| `streamlit run frontend/app.py` | Run frontend locally |

### Deploy do agente no AgentCore Runtime

```bash
# 1. Instalar Strands CLI (se disponivel) ou usar SDK
pip install strands-agents strands-agents-tools

# 2. Deploy do agente
# Via console Bedrock > AgentCore > Create Runtime
# Ou via SDK (ver docs AgentCore)

```

---

## Environments

| Environment | Purpose | Who Has Access |
| --- | --- | --- |
| Local dev | Testes unitarios (mock do AgentCore) | All devs |
| Workshop (us-east-1) | Demo com AgentCore real (conta AWS do workshop) | All devs |

---

## Notes for Beginners

- **Regiao:** Sempre use `us-east-1`. A credencial do workshop pode vir com outra regiao padrao - sobrescreva com `export AWS_DEFAULT_REGION=us-east-1`.
- **AgentCore Runtime** e diferente de Bedrock Agents. O AgentCore e o runtime gerenciado onde seu codigo de agente roda em microVMs isoladas. Voce escreve o agente, o AgentCore hospeda.
- **Strands Agents** e o SDK da AWS para escrever agentes. Simples: defina um modelo, um system prompt, e tools. Pronto.
- **Knowledge Base** indexa automaticamente os PDFs de RH do S3 Vectors - basta fazer upload e sincronizar.
- **AgentCore Memory** gerencia o historico de conversacao por sessao automaticamente.
- **Streamlit** cria a interface web com poucas linhas de Python - nao precisa saber HTML/CSS/JS.
- **Trocar modelo de chat** e simples - altere o `model_id` no codigo do agente e faca redeploy.
- **Trocar modelo de embedding** requer reindexar (sincronizar data source novamente). Faca isso com calma.
- **Modelos **`us.*` precisam de inference profile - nao passe como foundation-model ID direto.
- **Client correto:** Use `boto3.client("bedrock-agentcore")`, NAO `boto3.client("bedrock-agent-runtime")` (esse e do Bedrock Agents, servico diferente).
- Para rodar o frontend local: `streamlit run frontend/app.py` (abre no browser automaticamente).

