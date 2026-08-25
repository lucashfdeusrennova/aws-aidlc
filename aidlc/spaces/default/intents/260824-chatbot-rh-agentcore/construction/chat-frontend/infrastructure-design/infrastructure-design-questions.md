# Infrastructure Design Questions — chat-frontend (U1)

Unit: `chat-frontend` (kind: `ui`) — Streamlit local no notebook do participante. Contexto já fixado:

- **Deploy model**: `streamlit run frontend/app.py` local, sem hosting hospedado (`team.md § Deployment`).
- **Nenhuma infra AWS **provisionada** por U1** — U1 CONSOME ARNs (via env vars) provisionados por U3 (`infra`, kind `packaging`) [`contract-summary.md § C2`]. Este stage não vai criar CDK constructs, security groups, ou IAM roles — isso mora em U3.
- **Sem CI hospedado**: `team.md § Testing Posture` fixa "sem CI neste workshop, o gate roda na máquina do participante antes do squash-merge no `main`". `project.md § Mandated` ainda exige `.gitignore` do commit inicial + pinagem exata + no-hardcode.
- **Log destination**: stdout local (JSON via `logging.LoggerAdapter`, `logical-components.md § D-Log`).

Perguntas focadas em lacunas do design deste unit (Minimal-Standard depth, 3 perguntas):

---

## Q1 — Como registrar a natureza "no-cloud-infra" de chat-frontend em `infrastructure-specification.md`?

Este stage pede tabelas de "Deployment", "Infrastructure Services" e "Shared Infrastructure". Para um Streamlit local que só CONSOME 1 ARN de U3, a maioria dessas tabelas fica quase vazia. Como você prefere registrar?

- A. **Tabelas substantivas com N/A explícito** — Preencher a tabela de Deployment com facetas (Compute: notebook do participante, Networking: n/a — local, Storage: n/a — session_state em memória, Environments: workshop-sandbox só, IaC: n/a — sem CDK em U1, Sizing: n/a — desktop). Infrastructure Services fica vazia com nota "Ver U3 infra". Shared Infrastructure lista `AGENT_RUNTIME_ARN` como recurso compartilhado provisionado por U3 e consumido por U1.
- B. **Stub minimalista** — Uma tabela "Deployment" curta (só 3 linhas: Compute=notebook local, Environments=workshop-sandbox, IaC=none-in-this-unit) e uma seção prose curta redirecionando ao U3 para o resto. Menor superfície de manutenção, mas o sensor `required-sections` pode reclamar de baixa densidade.
- C. **Redirect completo** — Um documento de meia página apontando para U3 como owner de toda a infra AWS relevante, sem tabelas (o sensor `required-sections` só exige ≥2 H2 headings, então usar `## Sources` + `## Redirect to U3`). Alinha com a verdade do design mas pode falhar checks de conteúdo.
- X. Other (please specify)

[Answer]:A

---

## Q2 — Monitoring de chat-frontend: aceitar o "log-only" ou adicionar algo?

`logical-components.md § D-Log` já fixa JSON structured logs em stdout com `session_id`. Não há CloudWatch handler local (fora do escopo) nem métricas coletadas. Você quer registrar algo mais em `monitoring-design.md`, ou aceitar o "log-only" como o design final?

- A. **Log-only, sem métricas** — `monitoring-design.md` documenta que a "observabilidade" de U1 no MVP se resume aos logs JSON em stdout do processo Streamlit; nenhuma coleta de métrica (contador de submissions, latency histogram, etc.). Tabela de "Metrics & KPIs" fica vazia com nota "Delegado à observação manual do log em stdout durante a demo". Tabela de "Alerts" vazia. Nenhum SLI/SLO.
- B. **Log + smoke test como monitoring** — Documentar `scripts/smoke.py` (definido em `team.md § Testing Posture`) como a única cerimônia de monitoring pré-demo: 3-5 perguntas canônicas + timing (`t_submit`, `t_agent_call`, `t_agent_returned`, `t_response_rendered`) + guardrail LGPD check. Um SLI simples ("`frontend_elapsed <= 1 s` em 5 execuções") pelo smoke script.
- C. **Log + streamlit-side counters** — Adicionar contadores in-memory (`st.session_state.submit_count`, `error_count`) e mostrar num footer discreto na sidebar. Mais visibilidade para o operador do workshop mas mais código de UI.
- X. Other (please specify)

[Answer]:A

---

## Q3 — CI/CD para chat-frontend: nenhum ou checklist local?

`team.md § Testing Posture` fixa "sem CI neste workshop; o gate roda na máquina do participante antes do squash-merge no main". `team.md § Way of Working` fixa squash-merge, trunk-based, `main` como base+target. Como você prefere `cicd-pipeline.md`?

- A. **Documentar o "no-CI" com checklist local** — Um único documento descrevendo o fluxo local do participante: `ruff format . && ruff check . && pytest --cov=src --cov=agent --cov-fail-under=80` antes do commit; `git commit -m` + `gh pr create` + squash-merge no `main`. Tabela stage→gate com uma linha por check local. Não é "CI" mas descreve a cerimônia pré-merge.
- B. **Marcar como "não aplicável ao unit"** — Reafirmar que CI/CD é escopo de projeto (não de unit), redirecionar `cicd-pipeline.md` para o roteiro de workshop, sem checklist. Mais fiel ao domínio "unit" mas menos útil para o developer.
- C. **Documentar CI hipotético (post-MVP)** — Colocar um esboço do GitHub Actions workflow (ruff + pytest + coverage) como referência futura, marcado explicitamente como "não deployado no workshop". Zero custo agora, ganho de documentação para depois.
- X. Other (please specify)

[Answer]:A

---

## Consolidated Summary Confirmation

**Resumo consolidado das respostas** (para conferência antes da geração dos artefatos):

- **Q1 = A** — Em `infrastructure-specification.md`: tabelas substantivas com N/A explícito. Deployment traz facetas (Compute=notebook do participante, Networking=local, Storage=`st.session_state` em memória, Environments=workshop-sandbox, IaC=none-in-this-unit, Sizing=desktop). Infrastructure Services vazia com nota "Ver U3". Shared Infrastructure lista `AGENT_RUNTIME_ARN` como recurso compartilhado (owner U3, consumer U1).
- **Q2 = A** — `monitoring-design.md`: log-only, sem métricas. Tabelas "Metrics & KPIs" e "Alerts" ficam vazias com nota "Delegado à observação manual do log em stdout durante a demo". Nenhum SLI/SLO em U1 (o único SLI operacional — `frontend_elapsed <= 1 s` — pertence ao smoke test em `team.md § Testing Posture`, não a este stage).
- **Q3 = A** — `cicd-pipeline.md`: no-CI + checklist local. Fluxo do participante: `ruff format . && ruff check . && pytest --cov=src --cov=agent --cov-fail-under=80` antes do commit; `git commit` + `gh pr create` + squash-merge no `main`. Tabela stage→gate com uma linha por check local.

- Looks correct
- Request changes

[Answer]: Looks correct
