**Collaborator:** aidlc-architect-agent

# Security Design — chat-frontend (U1)

Design que aterrissa `security-requirements.md § NFR2.1.1..NFR5.4.1` para
o unit `chat-frontend`. Kind `ui` — descreve controles no client-side
Streamlit + boundary com `src/invoke.py`, sem entrar em código completo.

## Sources

- [sec] `security-requirements.md` — NFR2.1.1 (renderização em português),
  NFR3.2.1 (session_id via uuid), NFR4.1.1 (não sanitizar), NFR4.3.1
  (Guardrails não ativados), NFR4.5.1 (sem log em sink externo), NFR5.1.1
  (least-privilege), NFR5.2.1 (sem hardcode), NFR5.4.1 (sem GetSecretValue).
- [prf] `performance-requirements.md` — NFR1.1.1 (guard 4000 é upstream).
- [tsd] `tech-stack-decisions.md` — logging config, layered boundaries.
- [fs] `functional-spec.md` — AC1.6 (guard 4000), AC1.7 (mapping de erro),
  AC1.9.2 (`uuid.uuid4()`).
- [cs] `contract-summary.md` — C1 payload (`runtimeSessionId`), C2 env vars.
- [rules] `project.md § Mandated/Forbidden`, `phases/construction.md § Security`.

## Design Solutions

### D1 — Input guard 4000 em `src/invoke.py` (não em `frontend/app.py`)

O guard de tamanho de input vive em `src/invoke.py::ask_agent` como
primeiro statement, levantando `ValueError` se `len(prompt) > 4000`.
`frontend/app.py` também valida antes de chamar `ask_agent` (defense in
depth), mostrando `st.warning(...)` com o copy fixo:
`"Sua pergunta ficou muito longa para eu processar. Tente resumir em uma unica pergunta mais curta."`
(copy exato de `mockups.md § US1.6`).

- **Rationale**: dois pontos de validação — o frontend evita a chamada
  boto3 (mais rápido para o usuário), e a camada `src/` protege o
  contrato caso alguma outra UI chame `ask_agent` no futuro. Alinha com
  `phases/construction.md § Security` ("Validate and sanitize all inputs
  at system boundaries").

### D2 — Session ID gerado no client-side em `_clear_conversation` (NFR3.2.1)

O handler chama `str(uuid.uuid4())` e escreve em
`st.session_state.session_id`. Isso vira o `runtimeSessionId` na
próxima chamada a `invoke_agent_runtime` [cs C1]. Nunca vem de query
string, header ou input.

Boundary check adicional (defense in depth): antes da chamada boto3,
`src/invoke.py::ask_agent` valida
`re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", session_id)`.
Se falhar, levanta `ValueError("session_id inválido")`. Blindagem para
o caso de futuras UIs que possam passar valores mal-formados.

### D3 — Error message envelope (mapping determinístico)

`src/invoke.py::ask_agent` captura `botocore.exceptions.ClientError` e
re-eleva como `AgentInvocationError(user_message, cause=err)` com
mapeamento por tipo:

| ClientError type | user_message em português |
|------------------|---------------------------|
| `ThrottlingException` | "O serviço está ocupado agora. Tente de novo em alguns segundos." |
| `AccessDeniedException` | "Não consegui acessar o assistente. Contate o time técnico." |
| `ResourceNotFoundException` | "O assistente está indisponível. Contate o time técnico." |
| `ValidationException` | "Sua pergunta não pôde ser processada. Tente reformular." |
| `InternalServerException` | "O assistente teve um problema. Tente de novo em alguns instantes." |
| timeout / `RequestTimeout*` | "A resposta demorou demais. Tente perguntar novamente." |
| default (outros `ClientError`) | "Não consegui responder agora. Tente novamente em alguns segundos ou contate o RH se o problema persistir." |

`frontend/app.py` renderiza APENAS `err.user_message` via
`st.error(...)` — nunca `str(err.cause)` (evita vazar stack trace,
`__str__` do botocore expõe request-id que é PII do sistema, não do
usuário, mas é ruído para o participante).

### D4 — Trust boundary do rendering (NFR4.1.1)

O texto de `response.response` retornado por U2 é renderizado com
`st.chat_message("assistant").write(response)` — **`write`**, não
`markdown` com `unsafe_allow_html=True`. Se o agente retornar HTML/JS
literal, o Streamlit trata como texto plano; nenhum XSS possível.

- **Escopo**: não sanitizar, não filtrar. Confia na saída do agente
  [sec NFR4.1.1] — a política LGPD é enforced upstream em U2.
- **Anti-pattern proibido**: `st.markdown(response, unsafe_allow_html=True)`.
  O linter default do ruff (`E`+`F`) não detecta isso; fica como
  convenção verificada em code review.

### D5 — Logging non-leaky

`logging.getLogger(__name__).error("AgentCore invocation failed",
exc_info=err)` grava o stack trace do `ClientError` original no stdout
do processo Streamlit. NUNCA loga `prompt` completo em nível ERROR.
Se algum debug futuro quiser log do prompt, DEVE usar
`logger.debug("prompt=%s", prompt[:200])` truncado a 200 chars.

- **Alinhamento com NFR4.5.1**: destino é stdout local do notebook do
  participante; nenhum handler externo (Sentry, Datadog, Segment) em
  `requirements.txt`.
- **Formato**: JSON estruturado (ver `logical-components.md § D-Log`)
  — a session_id vai no envelope para correlação frontend↔backend
  futura.

### D6 — Credencial AWS resolvida pela chain default do boto3

`chat-frontend` NÃO chama `boto3.Session(aws_access_key_id=..., ...)`.
A credencial é resolvida pela chain padrão do boto3: `~/.aws/credentials`
→ env vars → IAM role. O participante configura via `aws configure` ou
`AWS_PROFILE` antes de rodar `streamlit run frontend/app.py`.

- **NFR5.1.1**: a documentação do workshop DEVE informar que o profile
  usado tem apenas `bedrock-agentcore:InvokeAgentRuntime` sobre o ARN do
  runtime provisionado por U3.
- **NFR5.2.1**: `AGENT_RUNTIME_ARN` e `AWS_REGION` vêm de `os.environ`
  (`AWS_REGION` com fallback `"us-east-1"` explícito no código); zero
  ARN literal em `frontend/app.py` ou `src/invoke.py`.
- **NFR5.4.1**: se algum segredo precisar ser adicionado futuramente,
  a resolução é `{{resolve:secretsmanager:secret-id:SecretString:json-key}}`
  no CDK (U3) com injeção via env var pelo IAM role.

### D7 — Guardrails Bedrock: registro do não-uso e ponto de retorno

Este design confirma `NFR4.3.1`: `associatedGuardrailArn` NÃO é
configurado no MVP. Se o time reverter essa decisão pós-workshop, o
efeito em `chat-frontend` é nulo (renderiza `response.response` como
está, com ou sem filtro); apenas U2 (hr-agent) precisa de mudança
(`security-design.md` de hr-agent registrará a decisão em seu próprio
stage NFR Design).

## Threat model (STRIDE simplificado)

Aplicado só na fronteira U1 (chat-frontend), assumindo que a rede é a
conta sandbox e o operador do workshop é confiável:

| Categoria | Vetor no chat-frontend | Mitigação |
|-----------|-----------------------|-----------|
| Spoofing | Participante faz outra UI que reusa a mesma role para atacar outros runtimes | Fora de escopo: least-privilege da role cobre isso (NFR5.1.1); design confia. |
| Tampering | Payload C1 modificado in-flight | TLS 1.2+ default do boto3; não há shared network segment na conta sandbox. |
| Repudiation | Participante nega ter feito uma pergunta | Log stdout com session_id (D5) — auditável para post-mortem local. |
| Information disclosure | UI mostra PII de outro colaborador via prompt injection | Guard primário em U2 (system prompt + curadoria KB, NFR8.2 test); UI trust boundary em D4. |
| Denial of service | Participante faz loop de submits e derruba a KB | boto3 default retry lida com throttling; volume total de 1–3 participantes × dezenas de queries é insignificante. |
| Elevation of privilege | Participante escala além do runtime que a role permite | Fora de escopo: least-privilege da role cobre (NFR5.1.1). |

## Coverage snapshot

| NFR (requirements) | Design solution |
|--------------------|-----------------|
| NFR2.1.1 (rendering pt-BR) | D4 (write, não markdown-html) + copy fixo em D3 |
| NFR3.2.1 (session_id server-side) | D2 (uuid + regex validation) |
| NFR4.1.1 (não sanitizar) | D4 (trust boundary explícito) |
| NFR4.3.1 (Guardrails não ativados) | D7 (registro e ponto de retorno) |
| NFR4.5.1 (log só em stdout) | D5 (formato JSON, sem handlers externos) |
| NFR5.1.1 (credencial least-privilege) | D6 (chain default + doc runtime) |
| NFR5.2.1 (sem hardcode) | D6 (`os.environ` + `.gitignore`) |
| NFR5.4.1 (sem GetSecretValue direto) | D6 (roteamento futuro via CDK resolve) |

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
