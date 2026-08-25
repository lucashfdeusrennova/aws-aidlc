# Chatbot de RH - Amazon Bedrock AgentCore

Chatbot que responde perguntas de colaboradores sobre politicas de RH, ferias, onboarding e avaliacoes de desempenho, usando:

- **Strands Agents SDK** dentro do **AgentCore Runtime** (microVM gerenciada).
- **Bedrock Knowledge Bases + S3 Vectors** para RAG sobre 5 documentos de RH.
- **Streamlit** para o chat frontend local.
- **CDK Python** para IAM roles, bucket S3 e outputs.

Region **us-east-1** obrigatoria.

## Estrutura

```
chatbot-rh-agentcore/
├── agent/                  Codigo do Strands Agent (roda dentro do AgentCore Runtime)
│   ├── agent.py
│   └── requirements.txt
├── src/
│   └── invoke.py           Cola boto3 → AgentCore
├── frontend/
│   └── app.py              Streamlit chat UI
├── infra/                  CDK stack (S3 bucket, IAM roles)
│   ├── app.py
│   └── stack.py
├── tests/                  pytest (mock AWS, guardrail LGPD obrigatorio)
├── scripts/
│   └── smoke.py            Smoke test contra Runtime deployado
├── docs/knowledge-base/    Coloque os 5 PDFs aqui (upload manual para o bucket)
├── cdk.json
├── pyproject.toml          Config do ruff + pytest
├── requirements.txt        Deps do frontend e do src/invoke
├── requirements-dev.txt    Deps de dev (pytest, cdk, agentcore CLI, ruff)
├── .env.example
└── AGENTS.md               Contexto AI-DLC
```

## Pre-requisitos

- Python 3.12
- AWS CLI configurado (`us-east-1`, credencial do workshop)
- Node.js e AWS CDK CLI (`npm install -g aws-cdk`) para o CDK
- Docker (o `agentcore` CLI usa Docker para empacotar o agente)

## Setup

```bash
# 1. Instale as deps
python -m venv .venv
.venv\Scripts\activate            # PowerShell no Windows
# source .venv/bin/activate       # macOS / Linux

pip install -r requirements-dev.txt

# 2. Copie o env template
cp .env.example .env               # macOS / Linux
copy .env.example .env             # Windows
# Voce vai preencher os ARNs depois dos passos abaixo.
```

## 1) Deploy da infra (CDK)

```bash
# bootstrap uma unica vez por conta/regiao
cdk bootstrap aws://<ACCOUNT_ID>/us-east-1

# preview + deploy
cdk synth
cdk deploy
```

Outputs importantes (aparecem no console apos o deploy):

- `DocsBucketName` — bucket para upload dos 5 PDFs
- `AgentExecutionRoleArn` — passar para `agentcore configure`
- `FrontendInvokePolicyArn` — anexar ao usuario/role que roda o Streamlit
- `InferenceProfileArnClaudeHaiku`, `InferenceProfileArnNovaPro` — copiar para o `.env`

## 2) Upload dos documentos + criar Knowledge Base

Documentos esperados em `docs/knowledge-base/`:

- `employee_handbook.pdf`, `leave_policy.pdf`, `onboarding_checklist.pdf`, `performance_review_guidelines.pdf`, `public_holidays.csv`

```bash
aws s3 cp docs/knowledge-base/ s3://<DocsBucketName>/ --recursive --region us-east-1
```

Crie a Knowledge Base no console (Bedrock > Knowledge bases > Create):

- **Data source**: aponta para `s3://<DocsBucketName>/`
- **Vector store**: **S3 Vectors** (novo bucket vector-store default)
- **Embedding model**: `cohere.embed-multilingual-v3` (recomendado para PT-BR)
- **IAM role**: usar `IngestionRoleArn` do output do CDK (opcional; console tambem cria)

Anote o `KNOWLEDGE_BASE_ID` (10 caracteres alfanumericos) e coloque no `.env`.

Sincronize o data source (**Sync now** no console) — leva ~2-5 min.

## 3) Deploy do agente no AgentCore Runtime

```bash
# Configura o container e o CFN necessarios (usa docker + ECR)
agentcore configure \
  --entrypoint agent/agent.py \
  --execution-role <AgentExecutionRoleArn do CDK output> \
  --region us-east-1 \
  --env INFERENCE_PROFILE_ARN_CLAUDE_HAIKU=<arn do output> \
  --env INFERENCE_PROFILE_ARN_NOVA_PRO=<arn do output> \
  --env KNOWLEDGE_BASE_ID=<KB_ID>

# Build + push + create runtime
agentcore launch
```

Copie o `agentRuntimeArn` produzido e cole em `AGENT_RUNTIME_ARN` no `.env`.

> Alternativa manual: no console **Bedrock > AgentCore > Create Runtime**,
> apontando para o Dockerfile gerado pela CLI em `.bedrock_agentcore/`.

## 4) Rode a UI local

Windows PowerShell:

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#][^=]*)=(.*)$') { $env:($matches[1].Trim()) = $matches[2].Trim() }
}
streamlit run frontend/app.py
```

macOS / Linux:

```bash
set -a && source .env && set +a
streamlit run frontend/app.py
```

Abre em `http://localhost:8501`. Use a sidebar para trocar o modelo entre Claude Haiku 4.5 e Amazon Nova Pro.

## 5) Testes locais (sem AWS real)

```bash
pytest --cov=agent --cov=src --cov-fail-under=80
```

Cobertura minima local: 80% (`team.md § Testing Posture`). Inclui obrigatoriamente:

- `test_lgpd_guardrail_refuses_salary` — MUST, valida BR4.3.

## 6) Smoke test contra Runtime real

Depois do `agentcore launch` bem-sucedido:

```bash
python scripts/smoke.py --model "Claude Haiku 4.5"
python scripts/smoke.py --model "Amazon Nova Pro"
```

5 perguntas canonicas + validacao LGPD embutida. Alvo: <5s por resposta (NFR1.1.1).

## Troubleshooting

- **`ResourceNotFoundException`** ao invocar Bedrock — voce provavelmente passou um `us.*` ID direto em vez do inference profile ARN. Cheque o `.env`.
- **`AccessDeniedException`** no frontend — a policy `FrontendInvokePolicy` do CDK precisa estar anexada ao seu usuario/role.
- **Retrieve retorna vazio** — a KB nao foi sincronizada apos o upload dos PDFs. Rode **Sync now** no console e espere.
- **`streamlit: command not found`** — ative o venv (`.venv\Scripts\activate`).

## Notas de seguranca (project.md § Mandated / Forbidden)

- Nunca commite `.env`, `credentials`, `*.pem` — ja estao no `.gitignore`.
- Nunca use `Resource: "*"` em policies Bedrock/S3.
- Nunca ingira documentos com PII (contracheque, avaliacoes nominais).
- Modelos `us.*` sempre via inference profile ARN, nunca ID direto.
- Logs NUNCA carregam prompt/response completo (NFR4.1.3).
