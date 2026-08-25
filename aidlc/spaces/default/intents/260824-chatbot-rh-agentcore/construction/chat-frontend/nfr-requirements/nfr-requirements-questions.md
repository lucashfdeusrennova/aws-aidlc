# NFR Requirements Questions — chat-frontend (U1)

Unit: `chat-frontend` (kind: `ui`) — aplicação Streamlit local que renderiza o chat e invoca AgentCore Runtime.

Contexto já fixado:

- **NFR1.1**: latência total ≤ 5 s (`requirements.md`).
- **NFR3.2**: `session_id` server-side via `uuid.uuid4()` (`project.md § Mandated`).
- **NFR4.1**: LGPD — nunca expor dados individuais (system prompt em U2, mas U1 renderiza a resposta).
- **NFR5** e `project.md § Mandated/Forbidden`: least-privilege, sem hardcode de ARN, sem chamadas diretas a Secrets Manager.
- **NFR6.1**: 1–3 sessões simultâneas na demo.
- **Framework**: Streamlit; error handling policy fixada em `team.md § Code Style`.
- **Kind `ui`**: produz somente `performance-requirements`, `security-requirements`, `tech-stack-decisions` e `traceability.json` (per `produces_kinds`); scalability, reliability e observability caem para o unit `hr-agent` (kind `service`).

Perguntas focadas em lacunas reais (Standard depth, ~4 perguntas):

---

## Q1 — Orçamento de latência do frontend dentro do NFR1.1

`NFR1.1` fixa 5 s totais entre envio da pergunta e primeira renderização da resposta. Precisamos decidir quanto desse orçamento o frontend pode consumir (render + boto3 + wire) antes de a latência do backend (AgentCore + Bedrock + retrieve) começar a apertar o alvo. Qual orçamento você quer registrar como `NFR1.1.<n>` para o unit `chat-frontend`?

- A. **Rígido — 500 ms** para tudo que não é AgentCore: render Streamlit + serialização JSON + latência de rede boto3 (conta sandbox → `us-east-1`). Sobra 4,5 s para o backend, o que é confortável.
- B. **Padrão — 1 s** para o frontend (idem A), sobrando 4 s para o backend. Alinhado com a experiência típica de um Streamlit local em notebook do participante.
- C. **Frouxo — 2 s** para o frontend, sobrando 3 s para o backend. Faz sentido se o notebook tiver rede instável durante a demo.
- D. **Sem orçamento explícito** — registrar só `NFR1.1` global e deixar a decomposição para observação em `scripts/smoke.py` na demo.
- X. Other (please specify)

[Answer]:B

---

## Q2 — Bedrock Guardrails como defesa em profundidade para LGPD

`team.md § Bedrock Guardrails (recomendado, não mandatório)` afirma que o time "considera caso a caso" configurar `associatedGuardrailArn` no `BedrockModel` com filtro de PII em OUTPUT e denied topics (salário, remuneração, folha, dados individuais). O guard primário é o system prompt em U2, mas o frontend renderiza a saída — se o backend vazasse PII, a UI mostraria. Como você quer registrar isso para chat-frontend?

- A. **Ativar Guardrails** — declarar em `security-requirements.md` que o unit U2 (hr-agent) DEVE configurar `associatedGuardrailArn` com filtro OUTPUT PII + denied topics. U1 confia na saída filtrada; sem lógica de sanitização no frontend.
- B. **Não ativar Guardrails** — o system prompt em U2 + a curadoria de `docs/knowledge-base/` (sem dados individuais) são suficientes para o MVP de 2 dias. Registrar como decisão consciente, com o teste unitário `NFR8.2` como controle auditável.
- C. **Guardrails opcional, decidir na demo** — deixar o unit U3 (infra) preparar o guardrail no stack CDK mas sem `associate` no `BedrockModel`; se sobrar tempo no dia 2, ligar.
- X. Other (please specify)

[Answer]:B

---

## Q3 — Destino e formato de logs do Streamlit local

`team.md § Code Style` fixa `logging.getLogger(__name__).error(...)` para o `ClientError` original em `src/invoke.py`, e `project.md § Forbidden` proíbe logar payload completo em sinks externos. Falta decidir onde o log do Streamlit vai parar durante a demo. Qual é a preferência?

- A. **stdout apenas** — `logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")` no top-level de `frontend/app.py`. Log aparece no terminal onde `streamlit run` está rodando; sem rotação, sem arquivo.
- B. **stdout + arquivo local** — mesma config do A, mais um `FileHandler` gravando em `./logs/frontend.log` (`.gitignore` já cobre o diretório). Útil se algo quebrar entre demos e você quiser reler depois.
- C. **stdout + CloudWatch da conta sandbox** — mais próximo do padrão que `hr-agent` vai usar dentro do AgentCore Runtime. Requer credencial local com `logs:PutLogEvents`, o que muda a role do frontend.
- D. **Só o handler default do logging Python** (sem `basicConfig`) — o console do Streamlit já mostra `WARNING+`; para o MVP é o suficiente.
- X. Other (please specify)

[Answer]:A

---

## Q4 — Pinagem exata das versões Python do frontend

`project.md § Mandated` obriga `==X.Y.Z` em `requirements.txt`. Para `chat-frontend` os pacotes são `streamlit` e `boto3`. Você quer travar em versões específicas agora (parte do `tech-stack-decisions.md`) ou deixar o developer pinar no code-generation com "última estável no dia do deploy"?

- A. **Travar agora** — registrar `streamlit==1.38.0` e `boto3==1.35.36` (estáveis em `us-east-1` no dia 25/08/2026, ambas com suporte a `bedrock-agentcore`). `pytest==8.3.3` e `pytest-cov==5.0.0` para dev.
- B. **Deixar o developer travar** — declarar em `tech-stack-decisions.md` apenas o *floor* (`streamlit>=1.36`, `boto3>=1.35 com cliente bedrock-agentcore`) e pedir ao developer para escolher a versão exata em `code-generation`, registrando no PR.
- C. **Travar Streamlit, deixar boto3 flutuar** — Streamlit tem API que quebra entre minor versions (`st.chat_input` mudou em 1.32+); boto3 é mais estável. `streamlit==1.38.0` fixo, `boto3` com o *floor* mais recente que reconhece `bedrock-agentcore`.
- X. Other (please specify)

[Answer]:A

---

## Consolidated Summary Confirmation

**Resumo consolidado das respostas** (para conferência antes da geração dos artefatos):

- **Q1 = B** — Orçamento de latência do frontend: **1 s** (render Streamlit + serialização JSON + wire boto3), sobrando 4 s para o backend dentro de NFR1.1 (5 s totais). Vira `NFR1.1.1` sob `performance-requirements.md`.
- **Q2 = B** — **Não** ativar Bedrock Guardrails no MVP. Controles primários: system prompt em U2 + curadoria de `docs/knowledge-base/` (sem dados individuais) + teste unitário NFR8.2 (guardrail LGPD auditável). Registrar como decisão consciente em `security-requirements.md`.
- **Q3 = A** — Log em **stdout apenas** via `logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")` no top-level de `frontend/app.py`. Sem arquivo, sem CloudWatch, sem rotação.
- **Q4 = A** — **Travar versões agora** em `tech-stack-decisions.md`: `streamlit==1.38.0`, `boto3==1.35.36`, `pytest==8.3.3`, `pytest-cov==5.0.0`.

- Looks correct
- Request changes

[Answer]: Looks correct
