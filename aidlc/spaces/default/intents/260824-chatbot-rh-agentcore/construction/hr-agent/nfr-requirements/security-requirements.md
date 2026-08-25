**Collaborator:** aidlc-architect-agent

# Security Requirements - Unit hr-agent

Requisitos de segurança derivados de `requirements.md § NFR4` (LGPD) e § NFR5
(IAM), da decisão Q4=A (Guardrails deferred) e do chain LGPD já capturado no
functional-design (BR2.3, BR4.1-4.4). Contribuições cross-agent: `aidlc-devsecops-agent`
(threat model, controles) e `aidlc-compliance-agent` (mapeamento LGPD).

## Sources

- [rq] `requirements.md` § NFR4.1-4.3 (LGPD), § NFR5.1-5.4 (IAM).
- [fs] `functional-spec.md` § AC1.5.1-3, § AC3.1.2, § Non-goals ("Bedrock Guardrails desligado no MVP").
- [rl] `rules.md` § BR2.3 (_LGPD_SECTION), § BR4.1-4.4 (LGPD chain), § BR4.3 (teste auditável).
- [cs] `contract-summary.md` § C3 (IAM policy skeleton: `bedrock:InvokeModel*` per inference profile ARN, `bedrock:Retrieve` per KB, logs).
- [pj] `project.md § Forbidden` e § Mandated (LGPD, IAM sem `Resource: "*"`, region us-east-1, inference profile ARN, secrets via CDK resolve, `.gitignore` seeds).
- [tp] `team.md` § Bedrock Guardrails (recomendado) — decisão de ativar é caso a caso.
- [q4] Q4 = A — Guardrails Bedrock NÃO ativados no MVP.

## Threat Model (STRIDE, resumido)

Aplicado ao handler `agent/agent.py` rodando na microVM do AgentCore Runtime:

| Categoria | Ameaça relevante | Mitigação MVP |
|-----------|------------------|---------------|
| **S** — Spoofing | Attacker chama `invoke_agent_runtime` diretamente com session_id forjado | IAM execution role do frontend (provisionada por U3, ver `contract-summary § Ownership rules — U3 owns C2/C3`) permite apenas o ARN específico do runtime; `runtimeSessionId` server-side gerado por U1 via `uuid.uuid4()` (BR7.2, NFR3.2). |
| **T** — Tampering | Attacker modifica payload em trânsito | AgentCore Runtime é TLS-por-default (HTTPS-only na API AWS). Sem controle adicional necessário no agente. |
| **R** — Repudiation | Auditar quem/quando invocou o agente | CloudWatch log per invocation (NFR4.1.3 em `observability-requirements.md`); CloudTrail cobre a chamada `InvokeAgentRuntime` no nível AWS. |
| **I** — Information Disclosure | (i) resposta expõe PII; (ii) log vaza payload; (iii) log vazado da sandbox | (i) `_LGPD_SECTION` (BR2.3) + BR4.1-4.4 + teste BR4.3; (ii) log INFO estruturado sem prompt/response (NFR4.1.3, Q2=A); (iii) `project.md § Forbidden` proíbe sink fora da sandbox — CloudWatch da conta sandbox é OK. |
| **D** — Denial of Service | Attacker faz burst de invocações | Delegado ao AgentCore Runtime (backpressure/quota nativa) — Q3=A. Guard 4000 chars em U1 (BR6.1 chat-frontend) limita tamanho de input. |
| **E** — Elevation of Privilege | Attacker no agente lê outra KB / invoca outro modelo | Execution role least-privilege: só `bedrock:Retrieve` na KB específica e `bedrock:InvokeModel*` nos 2 inference profile ARNs específicos (C3, `project.md § Forbidden`). Sem `Resource: "*"`. |

## Requirements

### NFR4.1.1 — Proibição de dados individuais na resposta (LGPD Response-Time)

- **Statement**: o agente NUNCA divulga dados individuais de colaboradores (salário, histórico pessoal, dados nominais como sujeito de dado) em qualquer resposta.
- **Control primary**: system prompt `_LGPD_SECTION` (BR2.3) instala a política; predicado testável em BR4.2 (resposta contém `RH` + keyword de recusa entre `{"nao posso compartilhar", "nao posso divulgar", "informacao pessoal"}`).
- **Control auditable**: teste unitário `test_lgpd_guardrail_refuses_salary` (BR4.3) — obrigatório, bloqueante local. Stub de `retrieve` retorna trecho com salário fictício (`"Joao Silva - Salario mensal: R$ 15.000,00"`); assertion garante que a resposta NÃO repete "R$ 15.000,00" nem "15.000".
- **Scope**: aplica a US1.5 e US3.1 (cross-ref BR4.4).
- **Enforcement**: BR4.3 bloqueia commit no `main` local via `pytest --cov=agent --cov-fail-under=80`.

### NFR4.2.1 — Proibição de ingestão de PII (LGPD Ingestion-Time)

- **Statement**: documentos contendo dados individuais de colaboradores (contracheque, avaliações nominais, histórico disciplinar, cadastro pessoal) NÃO podem entrar no bucket S3 da Knowledge Base.
- **Scope**: aplica ao bucket S3 provisionado por U3. Cross-unit: contrato de ingestão de U3.
- **Control**: `project.md § Forbidden` — regra afirmada; revisão manual dos documentos antes de `StartIngestionJob`. Sem controle automatizado no MVP.
- **Rationale**: se PII entra na KB, mesmo o system prompt e o teste BR4.3 podem ser bypassed por prompt injection via documento indexado. Bloqueio na fonte é mais eficaz que bloqueio no output.

### NFR4.3.1 — Bedrock Guardrails: Should Have deferred

- **Statement**: Bedrock Guardrails NÃO são ativados no MVP; ficam registrados como Should-Have para reavaliação pós-workshop.
- **Rationale (Q4=A)**: system prompt `_LGPD_SECTION` + teste BR4.3 são suficientes para o MVP. Custo de Guardrails (latência ~50-100ms extra + custo per invocation + config no CDK U3) supera benefício em 2 dias. Se o RH questionar uma resposta específica pós-demo, ativar Guardrails é a Migration Path #2 de `functional-spec.md`.
- **Trigger para reavaliação**: (i) pergunta de RH sobre resposta específica; (ii) ingestão futura de novos documentos que possam conter PII (mesmo mitigada por NFR4.2.1); (iii) escala além do workshop.

### NFR5.1.1 — Execution role least-privilege

- **Statement**: a IAM execution role do AgentCore Runtime (provisionada por U3) autoriza EXATAMENTE:
  - `bedrock:InvokeModel*` nos ARNs específicos `INFERENCE_PROFILE_ARN_CLAUDE_HAIKU` e `INFERENCE_PROFILE_ARN_NOVA_PRO` (nada além);
  - `bedrock:Retrieve` no ARN específico da Knowledge Base (não wildcard);
  - `logs:CreateLogGroup` / `logs:CreateLogStream` / `logs:PutLogEvents` em log group `/aws/bedrock-agentcore/*` da conta sandbox.
- **Prohibição explícita**: sem `Resource: "*"` (project.md § Forbidden); sem `bedrock:InvokeModel` sem restrição de ARN; sem `s3:*` (o agente não escreve no S3 nem lê direto).
- **Scope**: provisionada por U3 (packaging). U2 valida o comportamento indiretamente — se o agente conseguir invocar um modelo/KB fora do escopo, a role está mal configurada.

### NFR5.2.1 — Sem `Resource: "*"` em nenhuma policy tocada pelo agente

- **Statement**: nenhuma policy de U3 (execution role de U2, role/credencial de U1, role de ingestão da KB) usa `Resource: "*"` em `bedrock:InvokeModel*`, `bedrock:Retrieve*`, `s3:*` ou `bedrock-agentcore:*`.
- **Validation**: `cdk synth` inspecionado antes de `cdk deploy` (project.md § Mandated). Grep no template CFN gerado por `synth` deve retornar ARNs específicos, não `"*"`.

### NFR5.3.1 — Bucket S3 dos documentos com SSE-S3

- **Statement**: bucket S3 que hospeda os 5 documentos de RH tem criptografia SSE-S3 em repouso.
- **Scope**: provisionado por U3; o agente lê via `retrieve` que consulta a KB, não o S3 direto. Cross-unit assertion: nunca há motivo para o agente ler `s3:GetObject`.

### NFR5.4.1 — Secrets via CDK resolve placeholder

- **Statement**: qualquer segredo (se surgir) resolve via `{{resolve:secretsmanager:...}}` no template CDK ou via env var injetada pelo IAM role — NUNCA chamada `secretsmanager:GetSecretValue` no runtime do agente.
- **Applicable to MVP**: baixa relevância direta — o MVP não precisa de segredos além dos ARNs (que vêm de outputs CFN, não de Secrets Manager). Registro mantido como guardrail proativo.

### NFR4.1.2 — Input validation server-side (defense-in-depth)

- **Statement**: o agente NÃO revalida o guard de 4000 caracteres do prompt (guard primário está em `AgentInvoker` U1, BR6.1 chat-frontend). Aceita payload tal como recebido, confiando em (a) a fronteira de U1 e (b) o AgentCore Runtime que já rejeita payloads sobredimensionados.
- **Rationale**: dupla validação de tamanho não agrega segurança e desnormaliza o contrato C1. Se U1 for bypassed (attacker chama `InvokeAgentRuntime` direto com IAM válido), o problema é de IAM (NFR5.1.1), não de validação no agente.

### NFR5.1.2 — Sem retry customizado com credenciais

- **Statement**: o agente NÃO implementa retry customizado sobre `ClientError` no boto3 client. Confia no retry padrão do SDK (~3 tentativas com backoff em `ThrottlingException`).
- **Rationale**: retry loop customizado é vetor de amplificação de DoS (attacker força throttle → agente tenta N vezes). O default do SDK é conservador o suficiente para o MVP.

## Compliance Mapping (LGPD)

| Artigo LGPD | Requisito | Como o agente atende |
|-------------|-----------|----------------------|
| Art. 6º — Finalidade | Dados usados apenas para responder a políticas de RH gerais | Escopo restrito por `_ROLE_SECTION` (BR2.2) e por conteúdo indexado na KB (5 docs pré-aprovados, sem PII) |
| Art. 6º — Necessidade | Não coletar mais do que o necessário | Agente stateless (Q4=A); não persiste histórico, não armazena PII |
| Art. 7º — Base legal | Dados de colaboradores só com base legal | Consequência de NFR4.1.1 + NFR4.2.1: o agente nunca toca PII |
| Art. 46 — Segurança | Medidas técnicas e administrativas | SSE-S3 (NFR5.3.1), IAM least-privilege (NFR5.1.1), TLS by default (AWS API) |
| Art. 48 — Notificação de incidentes | Rastreabilidade em caso de vazamento | Audit trail via CloudWatch (log INFO estruturado sem payload — NFR4.1.3) + CloudTrail (chamadas AWS API) |

## Validation

- **BR4.3** — teste unitário LGPD (bloqueante local). Cobre NFR4.1.1.
- **`cdk synth`** — inspecionado antes de `cdk deploy`; validação humana de que não há `Resource: "*"` (NFR5.2.1) e que ARNs são específicos.
- **Smoke test** — `scripts/smoke.py` inclui pelo menos 1 pergunta que valida a recusa LGPD (`team.md § Testing Posture`).

## Anti-Requirements

- "Sistema seguro" sem controle específico — substituído por NFR4.x/5.x/-SEC-x.
- Bedrock Guardrails obrigatório — rejeitado por Q4=A (Should-Have deferido).
- WAF / rate limit no agente — fora do escopo (Q3=A delega ao Runtime).
- Prompt injection defense além do system prompt — sem defesa adicional no MVP; risco aceito (mitigado por NFR4.2.1 no ingestion-time).

## Assumptions & Open Questions

None.
