**Collaborator:** aidlc-architect-agent

# Security Requirements — chat-frontend (U1)

Requisitos de segurança derivados de `requirements.md` NFR2, NFR3, NFR4,
NFR5 e NFR7, especializados para o unit `chat-frontend` (kind `ui`).
Cobrem autenticação/autorização (via IAM role do participante),
proteção de dados em trânsito, isolamento de sessão, LGPD e logging.

## Sources

- [fs] `functional-spec.md` — chat-frontend, § "AC1.6" (guard 4000 chars),
  § "AC1.7" (mapping de erro sem stack trace), § "AC1.9" (uuid.uuid4()
  server-side).
- [rq] `requirements.md` — NFR2.1 (português), NFR3.2 (session_id
  server-side), NFR4.1/4.2/4.3 (LGPD), NFR5.1/5.2/5.4 (IAM), FR8/FR9
  (validação de input e error handling).
- [cs] `contract-summary.md` — C1 payload (`session_id` como
  `runtimeSessionId`), C2 (env vars vindas de outputs CDK, nunca
  hardcoded), § "Nota importante" (client `bedrock-agentcore`).
- [rules] `aidlc/spaces/default/memory/{org,team,project}.md` —
  project.md § Mandated (uuid.uuid4() server-side, `bedrock-agentcore`
  client, IAM least-privilege), project.md § Forbidden (LGPD, sem
  Resource:*, sem Secrets Manager direto, sem logs em sinks externos),
  phases/construction.md § Security (nunca hardcode credenciais).

## Requirements

### NFR2.1.1 — Renderização em português no frontend

**Descrição**: O `chat-frontend` renderiza APENAS conteúdo em português —
tanto a saudação inicial, quanto as mensagens de erro, avisos e o texto
da resposta do agente. [rq NFR2.1]

- Copy fixo (saudação, `st.warning`, `st.error`) em português definido em
  `mockups.md` e `frontend-components.md`.
- O agente (U2) retorna `response.response` em português (system prompt
  em U2 obriga isso); U1 NÃO faz tradução nem transformação.
- Se por acaso o agente retornar texto em outro idioma (falha do system
  prompt de U2), U1 renderiza como está — a violação é detectada por
  `NFR8.3` (smoke test) e corrigida em U2, não em U1.

**Testabilidade**: revisão visual + assert em smoke test de que a
resposta contém pelo menos uma palavra-chave em português esperada por
pergunta canônica.

### NFR3.2.1 — Session ID gerado server-side

**Descrição**: `st.session_state.session_id` DEVE ser gerado dentro do
processo do frontend via `uuid.uuid4()`, NUNCA aceito de query string,
header HTTP, cookie, campo de input ou variável de ambiente controlável
pelo usuário. [rq NFR3.2][fs AC1.9.2][project.md § Mandated]

**Regras concretas**:

- No primeiro rerun (session_state vazio):
  `st.session_state.session_id = str(uuid.uuid4())`.
- No handler `_clear_conversation`:
  `st.session_state.session_id = str(uuid.uuid4())`.
- O valor é passado como `runtimeSessionId` na chamada
  `invoke_agent_runtime`. [cs C1 AWS-owned]
- Não há endpoint ou UI que aceite `session_id` externo — Streamlit não
  expõe query string writable ao runtime da aplicação por default nesse
  padrão de uso.

**Testabilidade**: teste unitário em `tests/test_invoke.py` (ou fixture
Streamlit) verifica que dois `_clear_conversation()` consecutivos geram
UUIDs distintos e ambos passam o regex de UUIDv4.

### NFR4.1.1 — Não sanitizar resposta no frontend (controle upstream)

**Descrição**: O `chat-frontend` NÃO implementa sanitização, mascaramento
ou filtro de PII sobre o texto retornado pelo agente. Renderiza o
conteúdo de `response.response` verbatim. A responsabilidade LGPD (nunca
expor dados individuais de colaboradores) é enforcada UPSTREAM: (a)
system prompt em U2 com regra explícita; (b) curadoria de
`docs/knowledge-base/` sem dados individuais [rq NFR4.2]; (c) teste
unitário `NFR8.2` (guardrail LGPD auditável). [rq NFR4.1]

**Rationale (decisão consciente Q2=B)**: adicionar sanitização no
frontend criaria segundo caminho para regex/heurística que competiria
com o system prompt sem melhorar auditabilidade — o vazamento, se
ocorrer, deve ser tratado em U2 e coberto por teste, não escondido em
regex frontend.

**Escopo do frontend**: apenas a política de `NFR4.5.1` abaixo (não
logar payload de resposta em sink externo).

### NFR4.3.1 — Bedrock Guardrails não ativados no MVP

**Descrição**: `associatedGuardrailArn` NÃO é configurado no
`BedrockModel` do agente (U2) para este MVP. Registrado em
`team.md § Bedrock Guardrails (recomendado, não mandatório)` como
"considera caso a caso"; este workflow marca a decisão como
**não-ativar**, com o teste unitário LGPD (`NFR8.2`, unit U2) como
controle auditável equivalente. [rq NFR4.3][Q2=B]

**Efeito no chat-frontend**: nenhum. `chat-frontend` continua tratando
`response.response` como texto pt-BR seguro para renderização
(vide `NFR4.1.1`). Caso o time decida ativar Guardrails após a demo, a
única mudança em U1 é observacional (o payload de C1 não muda, e U1 já
renderiza `response` verbatim).

### NFR4.5.1 — Nenhum log de payload em sink externo

**Descrição**: O `chat-frontend` NÃO envia payload completo (prompt do
usuário + resposta do agente) para nenhum sink fora da conta AWS sandbox
(SaaS de observabilidade, analytics, telemetria de terceiros). [project.md
§ Forbidden]

**Regras concretas**:

- `logging.getLogger(__name__).error(...)` no bloco `except
  AgentInvocationError` (fs AC1.7.3) grava apenas em stdout (vide
  `NFR6.4.1`).
- O log da exceção captura mensagem do `ClientError` (útil para debug)
  mas **NÃO** loga o prompt completo em nível ERROR — usar `logger.debug`
  se algum dia for necessário logar prompt (por default o handler não
  emite DEBUG).
- Nenhum pacote de telemetria externa (`sentry-sdk`, `datadog`,
  `segment`, etc.) em `requirements.txt` — vide `tech-stack-decisions.md`
  § "Not adopted".

**Testabilidade**: inspeção de `requirements.txt` (ausência de pacotes
proibidos) + revisão de código em PR.

### NFR5.1.1 — Credencial do frontend limitada ao AgentCore Runtime

**Descrição**: A credencial AWS local do participante (perfil `default`
do `aws configure` ou `AWS_PROFILE`/`AWS_ACCESS_KEY_ID` em env) DEVE
possuir permissão APENAS para
`bedrock-agentcore:InvokeAgentRuntime` sobre o ARN específico do runtime
provisionado por U3 — nada mais. [rq NFR5.1][project.md § Mandated]

**Efeito**: em uma conta sandbox onde os participantes têm credencial
com permissões amplas, este NFR se torna prescritivo (documentação) mais
que enforceável — o time do workshop DEVE registrar em README/roteiro
que o principal usado para rodar o frontend é o role específico do
frontend, e não um role administrativo.

**Escopo**: não inclui provisionamento da role (isso é U3), inclui
apenas a política de uso.

### NFR5.2.1 — Sem hardcode de ARN, account ID ou credencial

**Descrição**: NENHUM ARN, account ID, IAM access key, session token ou
credencial pode aparecer no código de `frontend/app.py`, `src/invoke.py`
ou em qualquer módulo do unit `chat-frontend`. [project.md § Forbidden][rq NFR5.2]

**Regras concretas**:

- `AGENT_RUNTIME_ARN` lido via `os.environ["AGENT_RUNTIME_ARN"]`,
  populado a partir do output CDK (`AgentRuntimeArn`). [cs C2]
- `AWS_REGION` lido via `os.environ.get("AWS_REGION", "us-east-1")`. [cs C2]
- Nenhum uso de `boto3.Session(aws_access_key_id=..., aws_secret_access_key=...)`.
  A resolução de credencial fica na chain padrão do boto3
  (`~/.aws/credentials`, env vars, IAM role).
- `.gitignore` do commit inicial já cobre `.env`, `credentials`,
  `aws-credentials*`, `*.pem`, `*.pfx`, `**/secrets/**`. [project.md
  § Mandated]

**Testabilidade**: sensor `linter` (ruff) executado no CI local +
inspeção de `git log` procurando por regex de ARN antes de cada
squash-merge.

### NFR5.4.1 — Segredos não são resolvidos em runtime pelo frontend

**Descrição**: O `chat-frontend` NÃO chama
`secretsmanager:GetSecretValue` nem `BatchGetSecretValue` diretamente em
runtime. Se algum dia o frontend precisar de um segredo, a resolução
DEVE ser `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` no
template CDK (U3), com o valor injetado como env var pelo role.
[project.md § Forbidden][rq NFR5.4]

**Efeito no MVP**: `chat-frontend` não consome segredo algum atualmente
(apenas ARN público-por-natureza e região). Este NFR previne regressão
se um segredo for adicionado depois.

## Transport-level considerations

`boto3` usa TLS 1.2+ por default para chamar
`bedrock-agentcore.us-east-1.amazonaws.com`; nenhum override de HTTPS
handler é necessário. O único endpoint que o frontend fala é
AgentCore Runtime — não há chamada custom a outros serviços AWS ou
terceiros. [cs C1 AWS-owned]

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
