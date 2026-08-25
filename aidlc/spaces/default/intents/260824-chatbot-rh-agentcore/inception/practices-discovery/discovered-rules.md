# Discovered Rules — Chatbot de RH com AgentCore

> Regras duras descobertas durante o `practices-discovery`. Fontes: `tech-env.md`
> (§ "Prohibited Libraries / Patterns", § "Security Basics", § "Notas
> importantes sobre modelos", § "Notes for Beginners"), `vision.md` (§
> Constraints, § Out of Scope), `constraint-register.md` (CC-1/CC-2 LGPD,
> CT-1..CT-3, CO-1..CO-4, CA-1..CA-3, CN-1..CN-3), contribuições dos support
> agents (quality, developer, devsecops) e entrevista humana Q1–Q10.
>
> Formato: `## Mandated` em `ALWAYS …` e `## Forbidden` em `NEVER …`, cada
> item uma frase única. Após aprovação, são anexados carimbados sob
> `## Mandated` / `## Forbidden` de `aidlc/spaces/default/memory/project.md`
> pelo `aidlc-state.ts practices-promote`.
>
> **Nota de escopo**: Bedrock Guardrails e `pip-audit` foram propostos pelo
> devsecops mas ficam como **recomendações** em `team-practices.md`
> (§ Deployment e § Testing Posture) — não entram em `## Mandated` conforme
> decisão do humano em Q7=B. Expansão do `select` do ruff (adição de `S`,
> `B`, `UP`) também foi proposta e recusada em Q8=B — o linter fica no
> default `E`+`F`.

## Mandated

- ALWAYS use `boto3.client("bedrock-agentcore")` (never `bedrock-agent-runtime`) when invoking AgentCore Runtime — o cliente `bedrock-agent-runtime` pertence ao serviço Bedrock Agents, que é diferente do AgentCore Runtime.
- ALWAYS use inference profile ARNs for models with the `us.*` prefix — passar o ID `us.*` diretamente como `foundation-model` retorna `ResourceNotFoundException`.
- ALWAYS use region `us-east-1` for all AWS calls (Bedrock, AgentCore, Knowledge Bases e S3 Vectors) — a stack só está liberada nesta região no workshop.
- ALWAYS write agent, frontend and infrastructure code in Python 3.12.
- ALWAYS use the Strands Agents SDK as the agent framework (`strands` + `strands_tools`).
- ALWAYS validate that the user prompt is at most 4000 characters before invoking the agent (input-length guard exigido em `tech-env.md` § Security Basics).
- ALWAYS apply IAM least-privilege for Bedrock, AgentCore, S3 and Knowledge Bases access, and keep S3 objects encrypted at rest (SSE-S3).
- ALWAYS pin all Python dependencies to exact versions (`==X.Y.Z`) in `requirements.txt` and `agent/requirements.txt` — reprodutibilidade do demo entre notebooks dos participantes e defesa contra dependency drift durante a janela de 2 dias.
- ALWAYS enforce distinct IAM roles per plano de acesso — execution role do AgentCore Runtime (apenas `bedrock:InvokeModel*` para os inference profile ARNs específicos, `bedrock:Retrieve` para a KB específica e logs); role/credencial do frontend Streamlit (apenas `bedrock-agentcore:InvokeAgentRuntime` para o ARN do runtime); role de ingestão da KB (`s3:GetObject`/`s3:ListBucket` no bucket dos docs e `bedrock:StartIngestionJob` na KB) — sem `Resource: "*"` em nenhuma delas.
- ALWAYS generate `session_id` server-side via `uuid.uuid4()` and never accept it from user input, query string or header — isolamento de sessão do AgentCore só é garantido se `runtimeSessionId` não for atacante-controlável.
- ALWAYS resolve secrets via `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` in CDK templates (or via variáveis de ambiente injetadas pelo IAM role) — nunca chamar `secretsmanager:GetSecretValue` diretamente no runtime.
- ALWAYS keep `.env`, `*.pem`, `credentials`, `*.pfx`, `aws-credentials*` and `**/secrets/**` in `.gitignore` desde o commit inicial — janela de 2 dias, muitos participantes: um segredo comitado por engano fica para sempre no histórico.
- ALWAYS run `cdk synth` before `cdk deploy` and inspect the generated CloudFormation template; consume ARNs (runtime, KB, bucket) from stack outputs — never hardcoded no código do frontend ou do invocador.

## Forbidden

- NEVER use LangChain or LangGraph in this project — complexidade desnecessária para o demo; use Strands Agents SDK.
- NEVER use the OpenAI SDK — os modelos são consumidos exclusivamente via Bedrock (`boto3 bedrock-runtime` / Strands).
- NEVER use FastAPI or Flask in this project — a interface é Streamlit e a invocação vai por `invoke_agent_runtime`.
- NEVER use ChromaDB or Pinecone — o vector store é Bedrock Knowledge Bases + S3 Vectors (gerenciado).
- NEVER use SQLAlchemy — não há banco relacional no projeto.
- NEVER use React or Next.js as frontend — o frontend é Streamlit.
- NEVER expose individual employee data (salário, histórico pessoal, dados de folha) in bot responses — LGPD; escopo limita as respostas a políticas gerais.
- NEVER pass a `us.*` model ID directly as `foundation-model` — a chamada deve ir através de um inference profile ARN.
- NEVER hardcode account IDs, ARNs, IAM access keys, tokens or any credential in source code — o placeholder `ACCOUNT_ID` de `tech-env.md` deve ser resolvido em runtime via env var ou output do CDK.
- NEVER call `secretsmanager:GetSecretValue` or `BatchGetSecretValue` directly at runtime — segredos, se necessários, resolvem por template placeholder no deploy do CDK.
- NEVER ingest documents containing individual employee data (contracheque, avaliações nominais, histórico disciplinar, cadastro pessoal) into the KB S3 bucket — o controle CC-1/CC-2 se aplica primeiro no *ingestion time*, não só no *response time*; qualquer novo documento requer revisão antes do `StartIngestionJob`.
- NEVER use `Resource: "*"` in `bedrock:InvokeModel*`, `bedrock:Retrieve*`, `s3:*` or `bedrock-agentcore:*` IAM policies — least-privilege requer ARN específico do inference profile, da KB, do bucket e do runtime.
- NEVER log the complete conversation payload (prompt do usuário + resposta) to any sink outside the sandbox AWS account — CloudWatch da conta sandbox é OK; SaaS de observabilidade externo, analytics ou telemetria de terceiros, não.
