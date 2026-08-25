# Contract Design - Perguntas

## Sources

- [desc] Initial description: Chatbot de RH com AgentCore Runtime + KB + Streamlit.
- [scope] Workflow-selected scope: `mvp`.
- [uw] `unit-of-work.md` - 3 unidades: U1 chat-frontend, U2 hr-agent, U3 infra.
- [ud] `unit-of-work-dependency.md` - DAG: U3 depends_on U2; U1 e U2 folhas independentes em build-time. Contratos runtime: U3->U1 e U3->U2.
- [cp] `components.md` - HRChatFrontend, AgentInvoker, HRAgent.
- [rq] `requirements.md` - FR/NFR.

## Contexto

Boundaries identificadas:

1. **U1 -> U2** mediada pelo AgentCore Runtime (external dependency). Payload JSON via `invoke_agent_runtime`.
2. **U3 -> U1** CloudFormation stack outputs consumidos por env vars.
3. **U3 -> U2** env vars injetadas pelo IAM execution role.

Sem API publica externa: a UI e local no notebook do participante.

## Q1. Formato do payload U1 -> U2

Como o `AgentInvoker` envia a pergunta ao agente via `invoke_agent_runtime`?

- A. Body JSON minimo: `{"prompt": "<texto>"}`; agente retorna `{"response": "<texto>"}`. Simples, sem versionamento; formato canonico do workshop.
- B. Body JSON estruturado: `{"prompt": "<texto>", "context": {"model_id": "<label>"}}`; agente retorna `{"response": "<texto>", "model_id": "<label>", "session_id": "<uuid>"}` (para atender AC4.1.2 - model_id observavel).
- C. Como B + campo `response_metadata` (`retrieved_docs`, `tokens_used`) para observabilidade.
- X. Other (please specify)

[Answer]: B

## Q2. Contrato de erro U1 -> U2

- A. `ClientError` do boto3 (`ThrottlingException`, `ValidationException`, `ResourceNotFoundException`) e o unico canal de erro; U1 mapeia para `AgentInvocationError`. Resposta 200 com body vazio tratada como erro de aplicacao (raise `AgentInvocationError` com mensagem "Resposta vazia do agente").
- B. Idem A, mas adicionar contrato de resposta rica: `{"response": "", "error": {"code": "EMPTY_RESPONSE", "message": "..."}}` para casos degradados.
- X. Other (please specify)

[Answer]: A

## Q3. CloudFormation outputs de U3

Quais outputs o stack CDK expoe?

- A. Minimo: `AgentRuntimeArn`, `KnowledgeBaseId`, `DocumentsBucketName`. U1 le `AGENT_RUNTIME_ARN` via env var; U2 le `KNOWLEDGE_BASE_ID` via env var injetada pelo role.
- B. Como A + `FrontendRoleArn` e `IngestionRoleArn` para debug/auditoria da IAM.
- X. Other (please specify)

[Answer]: A

## Q4. Ownership + versionamento do payload

- A. `AgentInvoker` (U1) define o payload; `HRAgent` (U2) e o consumidor. Sem versionamento formal no MVP - additive-only rule ("consumidor ignora campos desconhecidos"). Se precisar de breaking change, redeploy coordenado.
- B. Contrato compartilhado em `agent/schemas/payload.py` importado por U1 e U2 - fere fronteira `agent/ isolado`.
- X. Other (please specify)

[Answer]: A

## Q5. Env vars como contrato

- A. `AGENT_RUNTIME_ARN`, `KNOWLEDGE_BASE_ID`, `AWS_REGION` (fallback `us-east-1`). Documentar em `contract-summary.md`. U3 injeta via CDK/IAM; U1 le do ambiente local; U2 le do IAM role do runtime.
- X. Other (please specify)

[Answer]: A

## Assumption Confirmation

Sem API publica/externa no MVP. Formato canonico do payload segue Q1=B (estruturado com `model_id` explicito para atender AC4.1.2). Erro tratado por `ClientError` + mapping para `AgentInvocationError` (Q2=A), consistente com `team-practices § Error handling policy` e ADR-002 de domain-design.

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumo consolidado das decisoes deste stage:

- Payload estruturado `{prompt, context.model_id}` -> `{response, model_id, session_id}` (Q1=B, materializa AC4.1.2).
- Erros via `ClientError` -> `AgentInvocationError`; resposta vazia = erro de aplicacao (Q2=A).
- CFN outputs minimos: `AgentRuntimeArn`, `KnowledgeBaseId`, `DocumentsBucketName` (Q3=A).
- Owner do payload: U1 `AgentInvoker`. Additive-only, sem versionamento formal (Q4=A).
- Env vars canonicas: `AGENT_RUNTIME_ARN`, `KNOWLEDGE_BASE_ID`, `AWS_REGION` (Q5=A).
- 3 contratos definidos (C1, C2, C3) + AWS-owned como referencia.
- 3 open questions deferidas a functional-design.

Artefato produzido:
- `contract-summary.md`

[Answer]: Looks correct
