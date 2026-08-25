# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance; contradictions with broader policy
> are rejected. Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

<!-- Project-specific specialisation. Example: -->
<!-- This monorepo requires package-scoped branch names and a package owner -->
<!-- review in addition to the team's normal merge policy. -->

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

<!-- Project-specific specialisation. -->

## Deployment

<!-- Project-specific specialisation. -->

## Code Style

<!-- Project-specific specialisation. -->

## Tech Stack

<!-- Technology choices locked for this project. -->

## Decided

<!-- Decisions made in earlier stages that should not be re-asked. -->
<!-- Format: DECIDED: [decision] (Stage [slug], [date]) -->

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: NEVER [behavior] (affirmed [date]) -->
<!-- Example: NEVER throw exceptions across service layer boundaries (affirmed 2026-05-17) -->

- NEVER use LangChain or LangGraph in this project — complexidade desnecessária para o demo; use Strands Agents SDK. (affirmed 2026-08-24)
- NEVER use the OpenAI SDK — os modelos são consumidos exclusivamente via Bedrock (`boto3 bedrock-runtime` / Strands). (affirmed 2026-08-24)
- NEVER use FastAPI or Flask in this project — a interface é Streamlit e a invocação vai por `invoke_agent_runtime`. (affirmed 2026-08-24)
- NEVER use ChromaDB or Pinecone — o vector store é Bedrock Knowledge Bases + S3 Vectors (gerenciado). (affirmed 2026-08-24)
- NEVER use SQLAlchemy — não há banco relacional no projeto. (affirmed 2026-08-24)
- NEVER use React or Next.js as frontend — o frontend é Streamlit. (affirmed 2026-08-24)
- NEVER expose individual employee data (salário, histórico pessoal, dados de folha) in bot responses — LGPD; escopo limita as respostas a políticas gerais. (affirmed 2026-08-24)
- NEVER pass a `us.*` model ID directly as `foundation-model` — a chamada deve ir através de um inference profile ARN. (affirmed 2026-08-24)
- NEVER hardcode account IDs, ARNs, IAM access keys, tokens or any credential in source code — o placeholder `ACCOUNT_ID` de `tech-env.md` deve ser resolvido em runtime via env var ou output do CDK. (affirmed 2026-08-24)
- NEVER call `secretsmanager:GetSecretValue` or `BatchGetSecretValue` directly at runtime — segredos, se necessários, resolvem por template placeholder no deploy do CDK. (affirmed 2026-08-24)
- NEVER ingest documents containing individual employee data (contracheque, avaliações nominais, histórico disciplinar, cadastro pessoal) into the KB S3 bucket — o controle CC-1/CC-2 se aplica primeiro no *ingestion time*, não só no *response time*; qualquer novo documento requer revisão antes do `StartIngestionJob`. (affirmed 2026-08-24)
- NEVER use `Resource: "*"` in `bedrock:InvokeModel*`, `bedrock:Retrieve*`, `s3:*` or `bedrock-agentcore:*` IAM policies — least-privilege requer ARN específico do inference profile, da KB, do bucket e do runtime. (affirmed 2026-08-24)
- NEVER log the complete conversation payload (prompt do usuário + resposta) to any sink outside the sandbox AWS account — CloudWatch da conta sandbox é OK; SaaS de observabilidade externo, analytics ou telemetria de terceiros, não. (affirmed 2026-08-24)
## Mandated

<!-- Populated by practices-discovery affirmation gate. -->
<!-- Format: ALWAYS [behavior] (affirmed [date]) -->
<!-- Example: ALWAYS use Result<T,E> for fallible operations in service layer (affirmed 2026-05-17) -->

- ALWAYS use `boto3.client("bedrock-agentcore")` (never `bedrock-agent-runtime`) when invoking AgentCore Runtime — o cliente `bedrock-agent-runtime` pertence ao serviço Bedrock Agents, que é diferente do AgentCore Runtime. (affirmed 2026-08-24)
- ALWAYS use inference profile ARNs for models with the `us.*` prefix — passar o ID `us.*` diretamente como `foundation-model` retorna `ResourceNotFoundException`. (affirmed 2026-08-24)
- ALWAYS use region `us-east-1` for all AWS calls (Bedrock, AgentCore, Knowledge Bases e S3 Vectors) — a stack só está liberada nesta região no workshop. (affirmed 2026-08-24)
- ALWAYS write agent, frontend and infrastructure code in Python 3.12. (affirmed 2026-08-24)
- ALWAYS use the Strands Agents SDK as the agent framework (`strands` + `strands_tools`). (affirmed 2026-08-24)
- ALWAYS validate that the user prompt is at most 4000 characters before invoking the agent (input-length guard exigido em `tech-env.md` § Security Basics). (affirmed 2026-08-24)
- ALWAYS apply IAM least-privilege for Bedrock, AgentCore, S3 and Knowledge Bases access, and keep S3 objects encrypted at rest (SSE-S3). (affirmed 2026-08-24)
- ALWAYS pin all Python dependencies to exact versions (`==X.Y.Z`) in `requirements.txt` and `agent/requirements.txt` — reprodutibilidade do demo entre notebooks dos participantes e defesa contra dependency drift durante a janela de 2 dias. (affirmed 2026-08-24)
- ALWAYS enforce distinct IAM roles per plano de acesso — execution role do AgentCore Runtime (apenas `bedrock:InvokeModel*` para os inference profile ARNs específicos, `bedrock:Retrieve` para a KB específica e logs); role/credencial do frontend Streamlit (apenas `bedrock-agentcore:InvokeAgentRuntime` para o ARN do runtime); role de ingestão da KB (`s3:GetObject`/`s3:ListBucket` no bucket dos docs e `bedrock:StartIngestionJob` na KB) — sem `Resource: "*"` em nenhuma delas. (affirmed 2026-08-24)
- ALWAYS generate `session_id` server-side via `uuid.uuid4()` and never accept it from user input, query string or header — isolamento de sessão do AgentCore só é garantido se `runtimeSessionId` não for atacante-controlável. (affirmed 2026-08-24)
- ALWAYS resolve secrets via `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` in CDK templates (or via variáveis de ambiente injetadas pelo IAM role) — nunca chamar `secretsmanager:GetSecretValue` diretamente no runtime. (affirmed 2026-08-24)
- ALWAYS keep `.env`, `*.pem`, `credentials`, `*.pfx`, `aws-credentials*` and `**/secrets/**` in `.gitignore` desde o commit inicial — janela de 2 dias, muitos participantes: um segredo comitado por engano fica para sempre no histórico. (affirmed 2026-08-24)
- ALWAYS run `cdk synth` before `cdk deploy` and inspect the generated CloudFormation template; consume ARNs (runtime, KB, bucket) from stack outputs — never hardcoded no código do frontend ou do invocador. (affirmed 2026-08-24)
## Corrections

<!-- Project-specific corrections from human feedback. -->
<!-- Format: NEVER/ALWAYS [behavior] (learned [date]) -->
