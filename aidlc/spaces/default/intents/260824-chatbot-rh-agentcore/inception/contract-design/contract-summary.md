**Collaborator:** aidlc-architect-agent

# Contract Summary - Chatbot de RH com Bedrock AgentCore

Sumario dos contratos entre as 3 unidades declaradas em `unit-of-work.md`
e o AgentCore Runtime (external dependency mediadora). Sem API publica
externa no MVP - o Streamlit e local no notebook do participante.

Fontes consumidas: `unit-of-work.md`, `unit-of-work-dependency.md`,
`components.md`, `requirements.md`.

## Sources

- [uw] `unit-of-work.md` - U1 chat-frontend (ui), U2 hr-agent (service),
  U3 infra (packaging).
- [ud] `unit-of-work-dependency.md` - DAG: `infra -> hr-agent` em
  build-time; U1 e U2 folhas independentes; U3 -> U1 e U3 -> U2 como
  runtime coupling via outputs e env vars.
- [cp] `components.md` - `HRChatFrontend`, `AgentInvoker`, `HRAgent`;
  ADR-002 fixa `AgentInvocationError` como excecao Python idiomatica.
- [rq] `requirements.md` - FR6.1 (`model_id` observavel), FR9 (error
  handling), NFR1.1 (<5s), NFR3.2 (`session_id` server-side).

## Contracts table

| # | Provider Unit | Consumer                | Mechanism                                  | Owner              |
| - | ------------- | ----------------------- | ------------------------------------------ | ------------------ |
| C1 | U1 chat-frontend | U2 hr-agent (via AgentCore Runtime) | JSON payload via `invoke_agent_runtime` | U1 `AgentInvoker`  |
| C2 | U3 infra      | U1 chat-frontend        | CloudFormation stack outputs -> env vars    | U3 `infrastructure` |
| C3 | U3 infra      | U2 hr-agent             | Env vars injetadas pelo IAM execution role | U3 `infrastructure` |

Alem desses contratos internos, o `AgentInvoker` fala com a **AWS API**
`bedrock-agentcore.InvokeAgentRuntime` - um contrato **AWS-owned**
(nao ha versionamento nosso). Documentado abaixo como referencia.

## C1 - U1 chat-frontend -> U2 hr-agent (payload via AgentCore Runtime)

**Mecanismo**: JSON serializado como bytes no `payload` do
`bedrock-agentcore.InvokeAgentRuntime`. Sincrono, single-shot (sem
streaming) [ADR-005].

**Owner**: `AgentInvoker` (U1). Additive-only rule: consumidor
(`HRAgent`) ignora campos desconhecidos; breaking changes exigem
redeploy coordenado das duas unidades [Q4=A].

**Payload de request** (U1 -> U2), spec compartilhada:

```yaml
# shared-schema: request payload
type: object
required: [prompt]
properties:
  prompt:
    type: string
    description: Pergunta do usuario em portugues.
    maxLength: 4000
    example: "Quantos dias de ferias tenho direito por ano?"
  context:
    type: object
    description: Metadados da chamada. Opcional para retro-compat.
    properties:
      model_id:
        type: string
        description: Rotulo humano do modelo escolhido pelo Operador (US4.1).
        example: "Claude Haiku 4.5"
```

**Payload de response** (U2 -> U1), spec compartilhada:

```yaml
# shared-schema: response payload
type: object
required: [response]
properties:
  response:
    type: string
    description: Resposta do agente em portugues (tom breve, 2-4 frases).
    example: "O colaborador tem direito a 30 dias de ferias anuais..."
  model_id:
    type: string
    description: >
      Rotulo do modelo que gerou a resposta. Materializa o contrato de
      observabilidade AC4.1.2 - "model_id observavel". Deve ecoar o
      valor recebido em `context.model_id` do request.
    example: "Claude Haiku 4.5"
  session_id:
    type: string
    format: uuid
    description: >
      Eco do `runtimeSessionId` recebido do AgentCore Runtime. Nao e
      gerado por U2; e o mesmo `session_id` que U1 gerou via
      `uuid.uuid4()` (NFR3.2).
```

**Erros** [Q2=A]:

- `AgentInvoker` captura `botocore.exceptions.ClientError` (`ThrottlingException`,
  `ValidationException`, `ResourceNotFoundException`, `AccessDeniedException`,
  `InternalServerException`, timeout) e re-eleva como `AgentInvocationError`
  com mensagem legivel [tp § Code Style Error handling policy].
- Resposta 200 com body vazio (sem campo `response` ou string vazia) e
  tratada como erro de aplicacao: `AgentInvoker` levanta
  `AgentInvocationError` com mensagem "Resposta vazia do agente".
- Guard de `len(prompt) > 4000` levanta `ValueError` antes da chamada;
  nunca chega ao AgentCore Runtime [FR8.1, US1.6 AC1.6.1].

**SLA / NFR**:

- NFR1.1 - latencia <5s por resposta.
- NFR6.1 - 1-3 sessoes simultaneas no MVP.

## C2 - U3 infra -> U1 chat-frontend (CloudFormation outputs)

**Mecanismo**: CloudFormation outputs consumidos pelo participante do
workshop como env vars locais (setadas manualmente ou via script de
setup pos-`cdk deploy`). Nunca hardcoded em codigo [tp § Deployment,
project.md § Mandated].

**Owner**: `infra` (U3). Additive: novos outputs podem ser adicionados
sem quebrar U1; remocao de output requer notificacao ao consumidor.

**Contract spec** (shared-schema):

```yaml
# shared-schema: CFN outputs -> frontend env vars
outputs:
  AgentRuntimeArn:
    description: ARN do AgentCore Runtime provisionado.
    consumed_as_env: AGENT_RUNTIME_ARN
    format: "arn:aws:bedrock-agentcore:us-east-1:<account>:runtime/<name>-<suffix>"
    example: "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/hr-agent-abc123"
    required_by_consumer: true
  DocumentsBucketName:
    description: Nome do bucket S3 com os documentos de RH (informativo; U1 nao le).
    consumed_as_env: null
    format: "<bucket-name>"
    required_by_consumer: false
  KnowledgeBaseId:
    description: ID da KB (informativo; U1 nao le, U2 le - vide C3).
    consumed_as_env: null
    format: "<10-char-alphanumeric>"
    required_by_consumer: false

env_vars_required_by_frontend:
  AGENT_RUNTIME_ARN:
    source: CFN output AgentRuntimeArn
    optional: false
  AWS_REGION:
    source: default do participante ou setado manualmente
    optional: true
    default: "us-east-1"
```

## C3 - U3 infra -> U2 hr-agent (env vars via IAM execution role)

**Mecanismo**: Env vars injetadas pelo IAM execution role do AgentCore
Runtime. O SDK Strands le `KNOWLEDGE_BASE_ID` diretamente do env; a tool
`retrieve` nao aceita o ID como argumento [tp § Code Style].

**Owner**: `infra` (U3). Additive: novas env vars podem ser adicionadas.
Renomear e breaking change.

**Contract spec** (shared-schema):

```yaml
# shared-schema: env vars injected into AgentCore Runtime for U2
env_vars:
  KNOWLEDGE_BASE_ID:
    description: ID da Bedrock Knowledge Base indexada com os 5 documentos.
    source: CFN output resolvido em runtime pelo CDK stack
    optional: false
    example: "ABCDEF1234"
  AWS_REGION:
    description: Regiao AWS unica do MVP.
    source: default do runtime
    optional: false
    fixed: "us-east-1"
  INFERENCE_PROFILE_ARN_CLAUDE_HAIKU:
    description: >
      ARN do inference profile para Claude Haiku 4.5. Consumido pelo
      HRAgent quando `model_id == "Claude Haiku 4.5"` (a resolucao
      label -> ARN mora em U1 no `MODEL_ARNS`, mas U2 pode receber
      diretamente o ARN via payload; a env var e defensive fallback).
    source: CFN output
    optional: true
    format: "arn:aws:bedrock:us-east-1:<account>:inference-profile/us.*"
  INFERENCE_PROFILE_ARN_NOVA_PRO:
    description: idem, para Amazon Nova Pro.
    source: CFN output
    optional: true
```

**IAM policy attached to this role** (least-privilege) [project.md § Mandated]:

```yaml
# IAM policy skeleton (nao e o template completo; documenta o contrato)
statements:
  - effect: Allow
    action: [bedrock:InvokeModel, bedrock:InvokeModelWithResponseStream]
    resource:
      - <INFERENCE_PROFILE_ARN_CLAUDE_HAIKU>
      - <INFERENCE_PROFILE_ARN_NOVA_PRO>
  - effect: Allow
    action: [bedrock:Retrieve]
    resource:
      - arn:aws:bedrock:us-east-1:<account>:knowledge-base/<KB_ID>
  - effect: Allow
    action: [logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents]
    resource:
      - arn:aws:logs:us-east-1:<account>:log-group:/aws/bedrock-agentcore/*
```

## AWS-owned contract (referencia)

**`bedrock-agentcore.InvokeAgentRuntime`** e um contrato AWS. Nao
versionamos, apenas consumimos. Documentado aqui para leitura conjunta
com C1:

```yaml
# AWS-owned - referencia
service: bedrock-agentcore
operation: InvokeAgentRuntime
region: us-east-1
request:
  agentRuntimeArn: string  # ARN do runtime (do C2)
  runtimeSessionId: string  # UUID gerado por U1 (NFR3.2)
  payload: bytes  # JSON encoded conforme C1
response:
  contentType: application/json
  payload: bytes  # JSON encoded conforme C1
```

**Nota importante**: usar `boto3.client("bedrock-agentcore")` (nunca
`bedrock-agent-runtime`) [project.md § Mandated]. Os dois clientes tem
nomes parecidos mas pertencem a servicos AWS diferentes.

## Contract ownership rules

- **C1 (payload JSON)**: owner `AgentInvoker` (U1). Consumer `HRAgent`
  (U2). Additive-only: consumidor ignora campos desconhecidos. Breaking
  changes exigem redeploy coordenado de U1 e U2. Sem versionamento no
  header/URL no MVP.
- **C2 (CFN outputs)**: owner `infra` (U3). Consumer U1. Additive:
  novos outputs OK; remocao/rename e breaking.
- **C3 (env vars runtime)**: owner `infra` (U3). Consumer U2. Additive:
  novas env vars OK; rename e breaking.
- **AWS API**: owner AWS. Consultar changelog do `bedrock-agentcore`
  para heads-up de deprecations.
- **Consumidores ignoram campos desconhecidos**: politica geral -
  qualquer JSON com fields extras nao quebra o parser.

## Open questions

| Contract | Question                                                                   | Blocks                       |
| -------- | -------------------------------------------------------------------------- | ---------------------------- |
| C1       | `AgentInvoker` ecoa `context.model_id` ate o response? Ou U2 escreve por conta propria em `response.model_id`? Definir em `functional-design`. | AC4.1.2 (`model_id` observavel) |
| C1       | Formato exato quando `retrieve` da KB nao retorna trechos (fallback US1.4). Body do response e string plana OU carrega marcador `{"response": "...", "fallback": true}`? | US1.4 AC1.4.1 (contrato de contains) |
| C3       | `INFERENCE_PROFILE_ARN_*` como env var de U2 e conveniencia (defensive fallback) - a resolucao label -> ARN normalmente vive em U1 no `MODEL_ARNS`. Decidir em `functional-design` se U2 precisa dessa fallback ou se aceita apenas o ARN via payload. | US4.1 AC4.1.3 |

Nenhuma bloqueia `delivery-planning` (o proximo stage); todas ficam
resolvidas antes de `code-generation` na fase Construction.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->

## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Verdict:** READY
**Date:** 2026-08-24
**Iteration:** 1
**Review class:** advisory

### Findings

| # | Severity | Location | Finding | Evidence |
|---|----------|----------|---------|----------|
| 1 | Minor | C1 § Erros | Retry policy nao esta explicita. A lista captura `ThrottlingException` e re-eleva como `AgentInvocationError`, mas nao diz se existe backoff/retry antes do re-raise (boto3 tem retry padrao no client). No MVP com 1-3 sessoes isso e aceitavel, mas fica implicito. | contract-summary.md § C1 Erros; NFR6.1 |
| 2 | Minor | C1 § SLA / NFR | Timeout absoluto do `invoke_agent_runtime` (client-side) nao esta declarado como parte do contrato. NFR1.1 (<5s) e citado, mas o valor de `read_timeout`/`connect_timeout` do boto3 config nao aparece - fica delegado ao `functional-design`. | contract-summary.md § C1 SLA |
| 3 | Minor | C2 e C3 | Comportamento quando uma env var obrigatoria esta ausente nao esta documentado explicitamente (fail-fast na inicializacao? fallback? erro de configuracao?). C2 marca `AGENT_RUNTIME_ARN` como `optional: false` mas nao define o "erro" no boundary. | contract-summary.md § C2, § C3 |
| 4 | Minor | AWS-owned contract § response | O bloco declara `response.contentType: application/json` e `payload: bytes`, mas a API real `bedrock-agentcore.InvokeAgentRuntime` devolve um streaming body iteravel (mesmo em modo sync). O contrato interno C1 nao depende disso (o `AgentInvoker` faz o `.read().decode()`), mas o bloco de referencia pode induzir a erro se lido isoladamente. | contract-summary.md § AWS-owned |
| 5 | Minor | Open questions Q1 (C1) | A duvida "AgentInvoker ecoa `context.model_id` OU U2 escreve por conta propria em `response.model_id`?" e legitima e nao esta bloqueando o gate, mas afeta AC4.1.2 (observabilidade). Ficou explicitamente deferida a `functional-design` - mantida como suggestion, nao finding critico. | contract-summary.md § Open questions |

Boundaries cobertos (checklist executado):

- U1 -> U2 (via AgentCore Runtime): C1 (payload JSON request/response) - OK, com spec YAML.
- U3 -> U1 (CFN outputs): C2 - OK, com spec YAML.
- U3 -> U2 (env vars via IAM role): C3 - OK, com spec YAML + IAM policy skeleton.
- AWS-owned (`bedrock-agentcore.InvokeAgentRuntime`): documentado como referencia, nao como contrato versionado.

Consistencia com `team-practices` / `project.md`:

- Client `bedrock-agentcore` (nao `bedrock-agent-runtime`): OK. A nota explicita ("Nota importante") esta correta.
- Inference profile ARN com padrao `us.*`: OK (`arn:aws:bedrock:us-east-1:<account>:inference-profile/us.*`).
- Regiao `us-east-1` fixada em C2, C3 e AWS-owned: OK.
- IAM sem `Resource: "*"`: OK, o skeleton usa ARNs especificos.
- Ownership + additive-only + breaking = redeploy coordenado: OK.

Cobertura de upstream (sensor `aidlc-upstream-coverage`):

- `unit-of-work.md` [uw]: referenciado.
- `unit-of-work-dependency.md` [ud]: referenciado.
- `components.md` [cp]: referenciado.
- `requirements.md` [rq]: referenciado.

### Suggestions (non-blocking)

- Adicionar em C1 uma linha explicita sobre retry: "boto3 retry padrao (`standard` mode, ~3 tentativas com backoff) aplica para `ThrottlingException`; sem retry adicional no `AgentInvoker`". Isso torna o contrato de erro auditavel sem esperar `functional-design`.
- Declarar em C1 o timeout numerico (ex.: `read_timeout: 30s`) alinhado com NFR1.1 (<5s por resposta) + margem para retry - dessa forma o `functional-design` apenas implementa.
- Em C2 e C3, uma linha "Comportamento quando ausente: fail-fast com mensagem clara na inicializacao (`ConfigurationError`)" fecha o loop de error handling nos boundaries de infra.
- Ajustar o bloco AWS-owned para refletir que `response.payload` e um streaming body (`StreamingBody` do botocore) - ou apenas remover o pseudo-schema e apontar para a doc AWS, ja que nao versionamos.

### Summary

Contract design cobre 100% dos boundaries do DAG (U1->U2, U3->U1, U3->U2) com spec YAML shared-schema, ownership definido e politica additive-only. Consistente com `team-practices` (client name, inference profile pattern, regiao). Findings sao todos Minor - o design e implementavel como esta; as sugestoes acima reduzem ambiguidade em `functional-design` mas nao gateiam. Verdict: READY.
