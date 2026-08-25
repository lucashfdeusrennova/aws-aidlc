# Practices Discovery - Entrevista (5 secoes)

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Way of Working

### Q1. Ciclo de branches, dado o workshop de 2 dias

- A. Manter o default do `org.md`: branches curtas de 1-2 dias, squash-merge no `main`, trunk-based.
- B. Ainda mais curto: branches que se resolvem no mesmo dia (dia 1 = fundacao, dia 2 = features + demo), squash-merge.
- C. Nenhuma branch dedicada - todo mundo commita direto no `main` no workshop.
- X. Other (please specify)

[Answer]:A

## Walking Skeleton

### Q2. Manter skeleton off (default do escopo `mvp`)?

Um walking skeleton e uma fatia vertical minima ponta-a-ponta que prova a arquitetura antes das features. Nesta demo, `mvp` declara `skeleton: off` por padrao.

- A. Sim, manter `skeleton: off` - o codigo do primeiro Bolt ja e ponta-a-ponta suficiente (agente + KB + frontend).
- B. Nao, quero rodar um walking skeleton primeiro mesmo assim (custo extra de meio dia).
- X. Other (please specify)

[Answer]:A

## Testing Posture

### Q3. Piso de cobertura (o QA agent objetou ao piso nao-bloqueante atual)

- A. Adotar 80% bloqueante local (`pytest --cov=agent --cov=src --cov-fail-under=80` no comando padrao). Adicionar `pytest-cov` ao `requirements-dev.txt`.
- B. Happy-path por funcao publica em `src/` e `agent/` (sem percentual). Cada funcao exportada tem no minimo 1 teste de sucesso. Recomendacao do QA agent para 2 dias.
- C. Sem piso, so testes de exemplos do `tech-env.md` (2 testes de `ask_agent`).
- X. Other (please specify)

[Answer]:A

### Q4. Teste de guardrail LGPD (o QA agent apontou que a regra "NEVER expose individual employee data" nao tem verificacao automatizada)

- A. Sim - incluir 1 teste unitario com prompt provocador ("Qual o salario do Joao?") e tool `retrieve` stubada retornando um trecho com salario ficticio; assertar que a resposta nao repete o valor. Entra como Must.
- B. Nao - validar apenas manualmente no smoke test antes da demo.
- C. Ambos: teste automatizado + smoke test manual.
- X. Other (please specify)

[Answer]:A

### Q5. Escopo do smoke test antes da demo

- A. Checklist manual documentado (`docs/smoke-test.md`) com 3-5 perguntas canonicas, incluindo uma que valida a recusa LGPD.
- B. Script `scripts/smoke.py` que chama `ask_agent` contra o AgentCore Runtime deployado com as mesmas 3-5 perguntas.
- C. Ambos.
- D. Nenhum.
- X. Other (please specify)

[Answer]:B

## Deployment

### Q6. Local-only + AgentCore Runtime (o lead propos, sem staging)

- A. Aceitar como esta: frontend Streamlit local, agente no AgentCore Runtime via CDK Python, KB provisionada pelo mesmo stack. Sem ambiente hospedado.
- B. Preferir console Bedrock para o AgentCore Runtime (sem CDK) - reduzir custo de configuracao para participantes que nao tem CDK setup.
- C. Ambos como opcoes documentadas no README: CDK como preferencial, console como fallback.
- X. Other (please specify)

[Answer]:A

### Q7. Bedrock Guardrails para reforcar LGPD (o devsecops agent recomenda como Mandated)

Bedrock Guardrails com filtro de PII no `OUTPUT` + denied topics para "salario, remuneracao, folha, dados individuais" - defesa em profundidade alem do system prompt.

- A. Mandated: guardrail obrigatorio, configurado no `BedrockModel` do Strands via `associatedGuardrailArn`. Custo: 30-60 min de configuracao no dia 1.
- B. Recomendado (nao Mandated): entra em `## Deployment` como boa pratica; time decide caso a caso.
- C. Fora do escopo desta demo: apenas system prompt.
- X. Other (please specify)

[Answer]:B

## Code Style

### Q8. Configuracao do ruff (o developer agent e o devsecops agent objetaram ao "defaults do ruff atendem")

- A. Adotar `select = ["E", "F", "I", "UP", "B", "SIM", "S"]` no `pyproject.toml`. Cobre pycodestyle, pyflakes, import order, pyupgrade (idiomas 3.12), bugbear (`mutable default args`, `bare except`), simplify, e bandit (SAST leve). Formatter do ruff (sem black separado). `line-length = 100`, `target-version = "py312"`.
- B. Manter default puro do ruff (`E`+`F`) - suficiente para demo.
- C. Adotar select mais conservador: `["E", "F", "I", "B"]` (sem `S` bandit, sem `UP`).
- X. Other (please specify)

[Answer]:B

### Q9. Politica de tratamento de erro em torno de `invoke_agent_runtime`

- A. Adotar o padrao proposto pelo developer agent: `src/invoke.py` captura `ClientError`, relevanta como `AgentInvocationError` (excecao de dominio simples); `frontend/app.py` captura e mostra via `st.error(...)`; log via `logging.getLogger(__name__)`.
- B. Deixar como no exemplo de `tech-env.md` (sem try/except explicito) - `ClientError` vaza para o Streamlit, que exibe traceback.
- X. Other (please specify)

[Answer]:A

### Q10. Pin exato de dependencias (o devsecops agent recomenda `==` em requirements.txt)

- A. Sim - pin exato (`package==X.Y.Z`) para reprodutibilidade entre notebooks dos participantes. Vale para `requirements.txt` e `agent/requirements.txt`.
- B. Nao - deixar `>=` (default do pip freeze).
- X. Other (please specify)

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
