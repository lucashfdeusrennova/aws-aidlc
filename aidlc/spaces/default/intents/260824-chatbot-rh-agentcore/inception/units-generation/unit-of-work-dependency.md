**Collaborator:** aidlc-architect-agent

# Unit Dependency DAG - Chatbot de RH com Bedrock AgentCore

Topologia de dependencias entre as 3 unidades declaradas em
`unit-of-work.md`. Esta etapa descreve **topologia** (o que pode depender
de que); a decisao economica de qual unidade vai primeiro (Bolt sequence)
pertence ao stage `delivery-planning`.

Fontes consumidas: `components.md` (fronteiras de camada),
`decisions.md` (ADR-005 sobre interacoes `sync` e desacoplamento em
build-time), `requirements.md`, `stories.md`.

## Sources

- [cp] `components.md` - fronteiras de camada `frontend/ -> src/ -> boto3`;
  `agent/` isolado.
- [ad] `decisions.md` - ADR-001 (3 componentes), ADR-005 (`sync` sem
  streaming).
- [rq] `requirements.md` - FR2.2 (`StartIngestionJob` antes da demo),
  FR6.2 (inference profile ARN), NFR7.2 (`cdk synth` obrigatorio).
- [st] `stories.md` - 11 stories; nenhuma cruza duas unidades no MVP
  (mapeamento 1:1 em `unit-of-work-story-map.md`).
- [tp] `team-practices.md § Deployment` - `cdk deploy` empacota U2 em
  U3; ARNs consumidos de outputs.
- [uw] `unit-of-work.md` - 3 unidades (U1, U2, U3) com kinds
  ui/service/packaging.

## Edge Block (machine-readable, cycle-free)

```yaml
units:
  - name: chat-frontend
    kind: ui
    depends_on: []
  - name: hr-agent
    kind: service
    depends_on: []
  - name: infra
    kind: packaging
    depends_on: [hr-agent]
```

## Dependency DAG - forma textual

```text
+---------------+          +---------------+
|  hr-agent     |          | chat-frontend |
|  (U2, service)|          | (U1, ui)      |
+-------+-------+          +---------------+
        |
        | infra empacota
        | o agent no
        | AgentCore Runtime
        v
+---------------+
|   infra       |
|  (U3, packaging)
+---------------+
```

O DAG tem apenas 1 aresta declarada em `depends_on`: `infra -> hr-agent`.
`chat-frontend` fica na base como componente independente porque seu
codigo pode ser desenvolvido e testado (guard 4000, mapping de erro,
gerenciamento de `st.session_state`) sem que `hr-agent` esteja pronto - a
camada de testes de U1 mocka `boto3.client("bedrock-agentcore")` na
fronteira do invoker (`patch("src.invoke.agentcore_client")`)
[tp § Testing Posture].

## Direct dependencies (por unidade)

### U1 `chat-frontend`

- **Build-time dependencies**: nenhuma sobre U2 ou U3.
  - Testes unitarios: `patch("boto3.client")` na fronteira; nao precisa
    do agente pronto nem do stack deployado [tp § Testing Posture].
- **Runtime dependencies (dev/demo)**: precisa dos outputs de U3
  (`AGENT_RUNTIME_ARN`) em env vars para invocar. Nao expresso no
  edge block porque runtime deployment coupling nao e build dep.

### U2 `hr-agent`

- **Build-time dependencies**: nenhuma sobre U1 ou U3.
  - Testes unitarios: `BedrockModel` mockado + tool `retrieve` stubada
    retornando trechos deterministicos; nao precisa do stack deployado
    nem da KB indexada [tp § Testing Posture].
- **Runtime dependencies**: precisa da KB e do Runtime provisionados por
  U3, mais `KNOWLEDGE_BASE_ID` via env var. Nao expresso como build dep.

### U3 `infra`

- **Build-time dependencies**: `[hr-agent]`. O stack CDK precisa
  referenciar o codigo/imagem do agente para criar o AgentCore Runtime.
  Sem o codigo de U2, o `cdk synth` de U3 nao gera um template
  deployable.
  - Formalmente: U3 empacota o artefato produzido por U2.
- **Runtime dependencies**: `StartIngestionJob` manual apos deploy
  [rq FR2.2][tp § Deployment].

## Integration points

### Contrato U3 -> U1 (outputs do stack)

Outputs do CloudFormation stack consumidos por U1 em runtime:

- `AgentRuntimeArn`: ARN do AgentCore Runtime provisionado. U1 le via env
  var `AGENT_RUNTIME_ARN`.
- `KnowledgeBaseId`: ID da KB (informativo; U2 le via env var, nao U1).
- `DocumentsBucketName`: nome do bucket S3 (informativo).

Formato: ARN comeca com `arn:aws:bedrock-agentcore:us-east-1:<account>:runtime/...`
[project.md § Mandated - "consume ARNs from stack outputs"].

### Contrato U3 -> U2 (execution role + env vars)

- Env var `KNOWLEDGE_BASE_ID` injetada pelo IAM execution role de U2.
- IAM policy do execution role: `bedrock:InvokeModel*` para os inference
  profile ARNs + `bedrock:Retrieve` para a KB especifica + logs. Sem
  `Resource: "*"` [project.md § Forbidden].

### Contrato U1 -> U2 (via AgentCore Runtime)

Nao ha chamada direta Python de U1 para U2. A mediacao e o
AgentCore Runtime (external dependency, `sync` [ad ADR-005]):

- U1 chama `bedrock-agentcore.InvokeAgentRuntime` com payload contendo
  o prompt e o `model_id`.
- Runtime encaminha para o processo do agente (U2) em microVM isolada.
- Agente retorna resposta que Runtime devolve ao U1.

Contrato de assinatura (a fixar em `contract-design`):
`ask_agent(prompt: str, session_id: str, model_id: str) -> str`.

## Parallel development opportunities

- **U1 || U2**: sem dependencia de build. Um dev pode escrever
  `frontend/app.py` + `src/invoke.py` enquanto outro escreve
  `agent/agent.py`. Ambos testaveis isoladamente com mocks
  centralizados em `tests/conftest.py` [tp § Testing Posture].
- **U3 aguarda U2**: quando U2 tem versao inicial estavel, U3 pode ser
  escrito. Enquanto U2 esta em desenvolvimento, U3 pode ser preparado
  em paralelo referenciando um stub ou um path relativo ao codigo de
  U2 - `cdk synth` valida a estrutura antes do `cdk deploy`.

O DAG e um Y invertido: U1 e U2 sao folhas independentes na base, U3
converge sobre U2 no topo. Ha exatamente **2 orderings topologicas**
validas: `[U1, U2, U3]` e `[U2, U1, U3]`, ambas com U3 no fim. `U3`
sempre depois de `U2`; `U1` pode ir em qualquer posicao anterior a U3.

Esta observacao topologica **nao e** uma recomendacao de ordem de
implementacao - a decisao economica (walking skeleton primeiro, tempo
maior no maior risco, etc.) pertence a `delivery-planning` (stage 2.9).

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
