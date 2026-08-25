<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-08-25T14:00:00Z — chat-frontend (kind: ui) so produz 4 artefatos (performance-requirements, security-requirements, tech-stack-decisions, traceability.json); scalability/reliability/observability caem para o unit hr-agent (kind: service) por produces_kinds do stage. Registrado em traceability.json como N/A explicito para NFR8/NFR9 e como "target upstream em U2/U3" onde aplicavel.
- 2026-08-25T14:00:00Z — NFR1.1.1 decompoe o teto de 5s em 1s frontend + 4s backend; a medicao vive em scripts/smoke.py (t_submit, t_agent_call, t_response_rendered), nao em CloudWatch, porque o Streamlit e local no notebook do participante durante os 2 dias de workshop.

## Deviations
- 2026-08-25T14:00:00Z — decidimos NAO ativar Bedrock Guardrails no MVP (Q2=B), contrariando a recomendacao "considera caso a caso" de team.md. Registrado como NFR4.3.1 com o teste unitario NFR8.2 (em U2) como controle auditavel equivalente; a decisao e reversivel sem mudar o payload C1.

## Tradeoffs
- 2026-08-25T14:00:00Z — travamos versoes Python exatas AGORA (streamlit==1.38.0, boto3==1.35.36, pytest==8.3.3, pytest-cov==5.0.0, ruff==0.6.9) versus deixar o developer resolver em code-generation. Trade: menos flexibilidade para pegar patch de ultima hora, mais reprodutibilidade entre os notebooks dos participantes na janela de 2 dias. Reproducibilidade venceu por project.md § Mandated exigir `==X.Y.Z`.
- 2026-08-25T14:00:00Z — log em stdout apenas (Q3=A) vs stdout+arquivo ou stdout+CloudWatch. Trade: perdemos historico entre demos, mas ganhamos zero setup adicional (sem `logs:PutLogEvents` na role do frontend, sem `.gitignore` para pasta ./logs). Coerente com "workshop local de 2 dias".

## Open questions
- 2026-08-25T14:00:00Z — se algum dia o time reconsiderar Guardrails, verificar se a versao do Strands SDK em uso no dia oferece `associatedGuardrailArn` como parametro publico de BedrockModel; a documentacao muda a cada minor. Nao bloqueia o MVP.
