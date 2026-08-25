**Collaborator:** aidlc-developer-agent

# Code Summary - infra (Turbo consolidado)

Este unit foi gerado em conjunto com `hr-agent` e `chat-frontend` no caminho
Turbo. Ver `../../chat-frontend/code-generation/code-summary.md` para
detalhes cross-unit.

## Sources

- [rq] `../../../inception/requirements-analysis/requirements.md` FR3, FR7, NFR5.
- [cs] `../../../inception/contract-design/contract-summary.md` C2, C3.
- [pj] `aidlc/spaces/default/memory/project.md § Mandated / Forbidden` - IAM least-privilege, region us-east-1, encryption SSE-S3.

## Deliverables (unit-specific)

- `infra/app.py` - CDK app entrypoint (region hardcoded us-east-1).
- `infra/stack.py` - `ChatbotRhStack`:
  - S3 bucket com SSE-S3, versioning, block public access, enforce SSL.
  - `AgentExecutionRole` least-privilege: bedrock:InvokeModel* nos 2
    inference profile ARNs, bedrock:Retrieve na KB (wildcard restrito a
    conta/regiao ate KB_ID conhecido), logs no group `/aws/bedrock-agentcore/*`.
  - `KbIngestionRole` para a KB (S3 read grants).
  - `FrontendInvokePolicy` managed policy (attachavel a user/role do participante).
  - 6 CFN Outputs: DocsBucketName, IngestionRoleArn, AgentExecutionRoleArn,
    FrontendInvokePolicyArn, InferenceProfileArnClaudeHaiku, InferenceProfileArnNovaPro.
- `infra/__init__.py`, `cdk.json` - config.

## Deferred to manual steps (documentado no README)

- Knowledge Base creation via console (Bedrock UI mais estavel que CDK L1
  para S3 Vectors backend).
- AgentCore Runtime deploy via `agentcore` CLI (aws-bedrock-agentcore-starter-toolkit).
- Upload dos 5 PDFs para o bucket + `StartIngestionJob`.

## Design decisions materialized

- NFR5.1.1: 3 statements na execution role, sem `Resource: "*"`.
- NFR5.3.1: `s3.BucketEncryption.S3_MANAGED`.
- Region us-east-1 forcada no `env=cdk.Environment(region="us-east-1")`.
- Idempotencia: `cdk deploy` recreates stack; `removal_policy=DESTROY +
  auto_delete_objects=True` no bucket (workshop sandbox descartavel).

## Assumptions & Open Questions

None.
