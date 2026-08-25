**Collaborator:** aidlc-aws-platform-agent

# CI/CD Pipeline — chat-frontend (U1)

Documento do fluxo de entrega para o unit `chat-frontend`. **Não há CI
hospedado no workshop** (`team.md § Testing Posture`) — o gate roda na
máquina do participante antes do squash-merge no `main`. Este documento
formaliza o checklist local que substitui o pipeline.

## Sources

- [rules] `team.md § Testing Posture` ("sem CI neste workshop, o gate
  roda na máquina do participante antes do squash-merge no `main`"),
  `team.md § Way of Working` (trunk-based, squash-merge, `main` como
  base+target), `team.md § Code Style` (ruff default `E`+`F` + `ruff
  format`), `project.md § Mandated` (pinagem exata `==X.Y.Z`, `.gitignore`
  desde o commit inicial), `project.md § Forbidden` (sem hardcode de ARN
  ou credencial).
- [tsd] `tech-stack-decisions.md` — `ruff==0.6.9`, `pytest==8.3.3`,
  `pytest-cov==5.0.0` em `requirements-dev.txt`.
- [prf] `performance-design.md` — nenhum SLA de deploy time.
- [sec] `security-design.md` — D6 credential chain default; sem
  `boto3.Session(aws_access_key_id=...)`.

## Delivery model — no-CI + checklist local

Fluxo do participante em cada iteração:

```
work → local checks → git commit → gh pr create → squash-merge → main
```

### Local checks (obrigatórios antes do commit)

Executados na raiz do repo, pela CLI do participante:

| Stage | Command | Gate | Blocking? |
|-------|---------|------|-----------|
| Format | `ruff format .` | Sem diff residual no working tree após o comando. | Yes — commit rejeitado no code review se o format não foi aplicado. |
| Lint | `ruff check .` | Zero violações do select default (`E`+`F`). | Yes — commit rejeitado se retornar violações. |
| Unit tests | `pytest --cov=src --cov=agent --cov-fail-under=80` | Todos os testes passam; cobertura ≥ 80% em `src/` e `agent/`. | Yes — bloqueia commit local; `pytest-cov` obrigatório em `requirements-dev.txt` (sem ele a flag `--cov` falha como argumento desconhecido). |
| ARN/credencial audit (opcional) | `git grep -E "arn:aws:.*:[0-9]{12}:|AKIA[0-9A-Z]{16}" -- '*.py' '*.md'` | Zero matches em código `.py` (matches em `.md` do workspace `aidlc/` são placeholders documentais e OK). | No — check manual, discricionário; se algum ARN literal aparecer em `.py`, PARAR e resolver via env var. |

### Merge flow

```
git switch -c feat/<bolt-slug>          # feature branch curta (1-2 dias)
# ... work + local checks ...
git add <files>                          # nunca `git add .` (evita segredo por engano)
git commit -m "<descriptive message>"    # mensagem clara; segue o slug do Bolt
git push -u origin feat/<bolt-slug>
gh pr create --base main                 # target = main (trunk-based)
# ... code review humano ...
# na aprovação, squash-merge via `gh pr merge --squash` OU botão da UI
```

O commit final no `main` carrega o slug do Bolt como nome (`team.md
§ Way of Working`); o histórico intermediário fica preservado só na
branch source até ela ser descartada.

### Rollback

Como o MVP não tem staging nem production, "rollback" significa:
- Se um commit no `main` quebrou `streamlit run frontend/app.py` localmente
  no notebook do participante, o próximo commit corrige e é mergeado.
- Não há revert automático, feature flag, ou blue-green. `git revert` é
  aceitável mas raramente necessário em uma janela de 2 dias.

### Secrets management no fluxo

`project.md § Mandated` obriga `.gitignore` desde o commit inicial cobrindo
`.env`, `*.pem`, `credentials`, `*.pfx`, `aws-credentials*`, `**/secrets/**`.
Nenhum segredo é gerado por `chat-frontend`; a credencial AWS resolve
pela chain default do boto3 (`~/.aws/credentials`) que fica fora do repo
(`security-design.md § D6`).

## Migration path (post-MVP, não deployado no workshop)

Se o time promover este projeto após a demo:

- **GitHub Actions workflow** (`.github/workflows/ci.yml`): job com Python
  3.12, `ruff format --check`, `ruff check`, `pytest --cov ... --cov-fail-under=80`.
  Trigger `pull_request` para o `main`.
- **Branch protection** no `main`: exigir "CI check passed" + 1 aprovação
  humana antes do squash-merge.
- **Dependabot** ou `renovate`: PRs automáticos de bump de versão para
  `streamlit`, `boto3`, `pytest`, `ruff`.

Nenhum desses passos é executado no workshop. Documentados aqui para
não perder o contexto.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-25 -->
