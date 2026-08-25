**Collaborator:** aidlc-architect-agent (com input do aidlc-aws-platform-agent)

# Security Design - Unit hr-agent

Design de controles de seguranca implementando `security-requirements.md`
(NFR4.1.x, NFR4.2.x, NFR4.3.x, NFR5.1.x, NFR5.2.x, NFR5.3.x, NFR5.4.x) e o
threat model STRIDE ja documentado la. Foco: defense-in-depth para LGPD,
IAM least-privilege, e a decisao explicita de deferir Bedrock Guardrails.

## Sources

- [sr] `security-requirements.md` — NFR4.1.1, NFR4.1.2, NFR4.2.1, NFR4.3.1,
  NFR5.1.1, NFR5.1.2, NFR5.2.1, NFR5.3.1, NFR5.4.1 + threat model STRIDE.
- [ts] `tech-stack-decisions.md` § Region, § Deps pinning, § Rejected stacks
  (secretsmanager runtime, `Resource: "*"`).
- [fs] `functional-spec.md` § System prompt architecture (`_LGPD_SECTION`),
  § Handler workflow step 2 (label -> ARN).
- [cs] `contract-summary.md` § C3 (IAM policy skeleton, env vars via IAM
  execution role).
- [pj] `project.md § Forbidden` (13 NEVER rules), § Mandated (13 ALWAYS).
- [tp] `team.md § Bedrock Guardrails` (recomendado, caso a caso).
- [rl] `rules.md` § BR4.1-4.4 (LGPD chain), § BR6.3-6.4 (fail-fast em
  label/env desconhecido — parte do vetor de ataque IAM se bypassed).

## Design Decisions

### SD-1 — Defense-in-depth para LGPD: 3 camadas ordenadas

**Requirement**: NFR4.1.1 (proibicao de dados individuais na resposta),
NFR4.2.1 (proibicao de ingestao de PII), NFR4.3.1 (Guardrails deferred).

**Design**: 3 camadas ordenadas por ordem de leverage decrescente (a mais
efetiva primeiro):

1. **Ingestion-time control** (NFR4.2.1) — nenhum documento contendo PII
   entra no bucket S3 da KB. Revisao humana antes de `StartIngestionJob`.
   *E a camada mais efetiva*: se PII nao esta na KB, nao pode ser vazada
   por prompt injection nem por Guardrail bypass.
2. **Response-time control via system prompt** (NFR4.1.1, BR2.3) —
   `_LGPD_SECTION` instrui o modelo a recusar pedidos de dado individual.
   *E a camada mais ampla mas nao a mais forte*: system prompt e
   bypass-vulneravel a prompt injection (documento contaminado ou input
   adversarial).
3. **Auditable test** (BR4.3) — teste unitario `test_lgpd_guardrail_refuses_
   salary` valida mecanicamente que, dado um trecho PII no stub de `retrieve`,
   o agente NAO repete valor monetario verbatim. *E o audit trail*: bloqueia
   regressao no CI local.

**Rationale**: cada camada tem falha independente. Ingestion review pode
falhar (humano distraido); prompt pode ser bypassed (documento contaminado);
teste pode ficar green mas o modelo real ter drift. Camadas em serie tornam
a violacao improvavel.

**Not-designed** (deferido por Q4=A / NFR4.3.1): Bedrock Guardrails como 4a
camada. Ativacao futura via `associatedGuardrailArn` no `BedrockModel`;
requer U3 provisionar Guardrail e expor ARN via nova env var.

### SD-2 — Trigger de reativacao para Bedrock Guardrails

**Requirement**: NFR4.3.1 (Should Have deferred).

**Design**: reativar Guardrails quando QUALQUER um dos triggers ocorrer:

- **T1 Semantic**: RH ou stakeholder questiona uma resposta especifica
  pos-demo (auditoria retroativa).
- **T2 Structural**: novo documento (alem dos 5 iniciais) e adicionado a KB
  E ha risco nao-zero de PII (mesmo mitigado por NFR4.2.1).
- **T3 Scale**: uso alem do workshop (>3 sessoes concorrentes por >2 dias).

**Design shape** de ativacao (nao codigo final):

```python
# Quando reativar (funcional-spec Migration Path):
# 1. U3 cria Guardrail com filtro PII em OUTPUT + denied_topics
#    ("salario, remuneracao, folha, dados individuais");
# 2. U3 adiciona nova env var GUARDRAIL_ARN no execution role;
# 3. U2 usa BedrockModel(model_id=arn, associated_guardrail_arn=os.environ["GUARDRAIL_ARN"]).
```

**Rationale**: registrar triggers concretos previne "sempre defer" ou
"nunca reativar". Cada trigger e testavel — RH pergunta, ou KB cresce,
ou concorrencia sobe.

### SD-3 — IAM policy pattern: least-privilege por ARN especifico

**Requirement**: NFR5.1.1, NFR5.2.1, § Threat Model E — Elevation of Privilege.

**Design**: 3 statements na execution role do AgentCore Runtime, sem
`Resource: "*"` em nenhum:

1. `bedrock:InvokeModel*` restrito a lista fixa de 2 inference profile ARNs
   (Claude Haiku 4.5, Amazon Nova Pro).
2. `bedrock:Retrieve` restrito ao ARN especifico da Knowledge Base.
3. `logs:{CreateLogGroup, CreateLogStream, PutLogEvents}` restrito a log
   group `/aws/bedrock-agentcore/*` da conta sandbox.

**Design shape** (segue `contract-summary § C3 IAM policy skeleton`):

```yaml
statements:
  - effect: Allow
    action: [bedrock:InvokeModel, bedrock:InvokeModelWithResponseStream]
    resource:
      - "${INFERENCE_PROFILE_ARN_CLAUDE_HAIKU}"
      - "${INFERENCE_PROFILE_ARN_NOVA_PRO}"
  - effect: Allow
    action: [bedrock:Retrieve]
    resource: ["arn:aws:bedrock:us-east-1:${ACCOUNT_ID}:knowledge-base/${KB_ID}"]
  - effect: Allow
    action: [logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents]
    resource: ["arn:aws:logs:us-east-1:${ACCOUNT_ID}:log-group:/aws/bedrock-agentcore/*"]
```

**Rationale**: qualquer chamada Bedrock/logs a recurso fora dessa lista
retorna `AccessDeniedException`. Se compromised (attacker executa codigo no
agente), o blast radius e limitado — nao acessa outras KBs, outros modelos,
outros buckets, outros log groups.

**Sensor de verificacao**: `cdk synth` gera CFN template; grep
`"Resource": "\*"` no bloco de policies do agente = zero hits antes de
`cdk deploy` (afirmado em `project.md § Mandated`).

### SD-4 — Encryption in-transit e at-rest (herdado)

**Requirement**: NFR5.3.1 (SSE-S3), LGPD Art. 46.

**Design**:

- **In-transit**: TLS 1.2+ nativo em toda API AWS (Bedrock, AgentCore,
  Knowledge Bases, S3, CloudWatch). Sem HTTP plaintext em nenhuma etapa.
  Zero design work no lado do agente.
- **At-rest S3 bucket dos documentos**: SSE-S3 (AES-256 gerenciado pelo S3).
  Provisionado por U3 via `bucket_encryption` no CDK.
- **At-rest S3 Vectors da KB**: gerenciado por Bedrock (encryption default
  da service).
- **At-rest CloudWatch Logs**: encryption default da service (nao KMS
  customer-managed no MVP).

**Rationale**: SSE-S3 e configuracao 1-line no CDK, zero overhead operacional,
satisfaz LGPD Art. 46. KMS customer-managed adicionaria custo + rotacao;
fora do escopo MVP.

### SD-5 — Input validation: single-guard pattern em U1

**Requirement**: NFR4.1.2 (agente NAO revalida guard de 4000 chars).

**Design**: guard de comprimento vive EXCLUSIVAMENTE em `AgentInvoker` (U1,
BR6.1 chat-frontend). Handler U2 aceita payload como recebido. Camada extra
no U2 seria dupla validacao redundante que confunde a fronteira.

**Rationale (defense in depth vs single source of truth)**: DiD e valioso
quando cada camada custa proximo de zero (ex.: WAF + validation + prepared
statement em SQL). Aqui, dupla validacao custa clareza (onde o erro sobe?
frontend ou agente?) sem ganho — se attacker bypassa U1 chamando
`InvokeAgentRuntime` direto, ele precisa de IAM valido, e nesse caso
NFR5.1.1 (least-privilege) e o controle real.

**Failure mode se U1 for bypassed**: attacker com IAM valido envia payload
>4000 chars. Bedrock rejeita natively com `ValidationException` — o
`AgentInvoker` do proprio attacker capturaria; nao afeta a estabilidade
do agente.

### SD-6 — Session isolation: 1 microVM per session (herdado do Runtime)

**Requirement**: NFR3.1 (isolamento de sessao, herdado de requirements.md),
§ Threat Model S — Spoofing.

**Design**: o AgentCore Runtime aloca uma microVM por `runtimeSessionId`
recebido. Nenhum state cruza entre sessoes. `session_id` server-side
gerado por U1 via `uuid.uuid4()` (BR7.2, NFR3.2) — nao aceito de query
string, header ou input do usuario.

**Rationale**: attack surface para session hijacking = 0 no lado do agente
porque nao ha shared state entre microVMs. U1 e o unico ator que gera IDs;
attacker precisaria comprometer U1 ou o IAM do frontend para forjar
`session_id`.

**Not-designed**: rotacao de session_id mid-conversation (nao aplicavel a
Q4=A stateless).

### SD-7 — Secrets: sem chamada `secretsmanager:GetSecretValue` no runtime

**Requirement**: NFR5.4.1, `project.md § Forbidden` (NEVER call
`secretsmanager:GetSecretValue` or `BatchGetSecretValue` directly at runtime).

**Design**: o agente NUNCA importa `boto3.client("secretsmanager")` nem
executa `get_secret_value(...)` em runtime. Se houver segredo (nao aplicavel
ao MVP), resolucao vive no template CDK via
`{{resolve:secretsmanager:secret-id:SecretString:json-key}}` — o valor
resolve em deploy-time e chega ao runtime como env var normal.

**Rationale**: chamada runtime cria dependencia de latencia + custo por
invocacao + audit log verboso. CDK resolve elimina o proprio caminho de
codigo. Para o MVP, nao ha segredo — ARNs vem de outputs CFN, nao de
Secrets Manager.

**Sensor de verificacao**: grep `secretsmanager` em `agent/**/*.py` = zero
hits.

### SD-8 — No custom retry pattern (fail-fast reinforcing IAM)

**Requirement**: NFR5.1.2 (sem retry customizado com credenciais).

**Design**: o handler NAO envolve `agent(prompt)` em `try/except ClientError`
com retry loop. Toda exception propaga para o Runtime, que traduz em resposta
de erro para o AgentInvoker.

**Rationale de seguranca**: retry loop customizado sob ThrottlingException
amplifica DoS (attacker forca throttle -> agente re-tenta N vezes -> quota
esgota mais rapido -> DoS mais amplo). boto3 default (~3 tentativas com
backoff) e conservador o suficiente. Fail-fast e alinhado com BR6.3/BR6.4.

**Cross-ref**: `reliability-design.md § RD-1` reforca a mesma decisao com
lente de confiabilidade.

### SD-9 — Prompt injection defense: aceita risco mitigado por SD-1

**Requirement**: `security-requirements.md § Anti-Requirements` (prompt
injection defense alem do system prompt — sem defesa adicional no MVP).

**Design**: SD-1 e a defesa. Nao ha filtro pos-hoc no agente contra
patterns adversariais nem PII detection library rodando sobre o output.

**Rationale**: patterns adversariais evoluem mais rapido que regex; PII
detection libraries em portugues sao imaturas; overhead custa latencia
sem benefit claro no MVP. Se drift-attack e observado pos-demo, o path
de reativacao e SD-2 (Guardrails), nao filtro custom.

## STRIDE Matrix Design View

Como SD-1 a SD-9 mapeiam ao threat model de `security-requirements.md`:

| STRIDE | Threat | Design(s) que mitigam |
|--------|--------|-----------------------|
| S | Spoofed `session_id` | SD-6 (server-side uuid), SD-3 (IAM restringe quem invoca) |
| T | Payload tampering | SD-4 (TLS native) |
| R | Repudiation | `observability-design.md § OD-1/OD-2` (audit log) + CloudTrail |
| I | PII disclosure | SD-1 (3 camadas), SD-2 (trigger Guardrails), SD-4 (encryption), `observability-design.md § OD-1` (log sem payload) |
| D | DoS | SD-8 (sem retry loop amplifica), `scalability-design.md § SCD-2` (delega ao Runtime), NFR4.1.2 (guard 4000 chars em U1) |
| E | Privilege escalation | SD-3 (least-privilege por ARN), SD-7 (sem secretsmanager runtime) |

Todo threat tem >= 1 design vinculado.

## Compliance Mapping (LGPD)

| Artigo | Requisito | Design |
|--------|-----------|--------|
| Art. 6 (finalidade) | Dados so para politicas de RH gerais | SD-1 layer 1 (ingestion) |
| Art. 6 (necessidade) | Nao coletar mais que necessario | SD-6 (statelessness = zero collection) |
| Art. 7 (base legal) | So com base legal | consequencia de SD-1 (agente nao toca PII) |
| Art. 46 (seguranca) | Medidas tecnicas | SD-4 (SSE-S3 + TLS), SD-3 (IAM least-privilege) |
| Art. 48 (notificacao) | Rastreabilidade de incidente | `observability-design.md § OD-1` (audit log) + CloudTrail |

## Anti-Patterns Rejected

- **`Resource: "*"` em qualquer statement Bedrock/S3** — violado NFR5.2.1.
- **Retry customizado com backoff exponencial** — amplifica DoS (SD-8).
- **Rate limit / WAF no lado do agente** — delegado ao Runtime (Q3=A).
- **KMS customer-managed keys** — overhead > valor no MVP.
- **Guardrails ativados agora** — Q4=A adia (SD-2 tem trigger explicito).
- **Log de prompt/response completo** — `project.md § Forbidden`; ver
  `observability-design.md § OD-1`.

## Assumptions & Open Questions

None.
