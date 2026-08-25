# Delivery Planning - Perguntas

## Sources

- [desc] Initial description: Chatbot de RH com AgentCore Runtime + KB + Streamlit.
- [scope] Workflow-selected scope: `mvp`, `skeleton: off`.
- [rq] `requirements.md` - FR/NFR.
- [st] `stories.md` - 11 stories.
- [mk] `mockups.md` - refined mockups.
- [cp] `components.md` - 3 componentes.
- [uw] `unit-of-work.md` - 3 unidades (U1 chat-frontend, U2 hr-agent, U3 infra).
- [ud] `unit-of-work-dependency.md` - DAG: `infra -> hr-agent`; U1 e U2 folhas independentes.
- [sm] `unit-of-work-story-map.md` - 6 stories em U2, 5 em U1, 0 em U3 (packaging).
- [cs] `contract-summary.md` - 3 contratos (C1, C2, C3).
- [tp] `team-practices.md` - `skeleton: off`, deploy local-only, sem CI/CD.

## Estrategicas

### Q1. O que construir primeiro

Riskiest, most valuable, walking skeleton, ou mix?

- A. Risk-first pragmatico: comecar por U2 (agente Strands + system prompt LGPD) e U3 (KB + IAM) porque sao os itens com maior risco tecnico (Bedrock, inference profile, KB ingestion). Deixar U1 (Streamlit) por ultimo - riscos menores, apenas plumbing de UI.
- B. Value-first: comecar por U1 (frontend com mock) porque e o que o usuario final ve. Agente e infra depois.
- C. Walking skeleton: um Bolt inicial thin-slice que toca as 3 camadas. **Nao aplicavel: team-practices declara `skeleton: off`.**
- X. Other (please specify)

[Answer]: A

### Q2. Modelo de scoring

WSJF, CD3, SAFe, ou informal?

- A. Informal / rationale narrativo. Escopo travado (11 stories, 3 unidades); 2 dias; nao ha trade-off real entre valor incremental e risco. WSJF formal seria overhead.
- B. WSJF simplificado (score = risk_reduction / job_size) para tie-break entre Bolts.
- X. Other (please specify)

[Answer]: A

### Q3. Tamanho de um Bolt

Unit single, bundle, ou thin slice cross-Unit?

- A. Um Bolt por Unit de Work: 3 Bolts. Cada Bolt entrega uma unidade completa. Alinhado com kind + directory de `unit-of-work.md`.
- B. Bundle: fundir U2+U3 em um Bolt "agente deployado" e U1 em outro. 2 Bolts.
- C. Thin slice: cross-Unit, um AC por Bolt. Fragmenta demais.
- X. Other (please specify)

[Answer]: A

### Q4. Paralelismo

Bolts em paralelo ou sequenciais?

- A. Sequenciais. Time = 1 (aidlc-developer-agent). AI executa um Bolt de cada vez.
- B. Paralelos onde a topologia permite (U1 e U2 sao folhas independentes).
- X. Other (please specify)

[Answer]: A

### Q5. Dependencias externas

O que fora deste time pode segurar?

- A. Conta AWS sandbox valida durante os 2 dias + credenciais + Bedrock/AgentCore/KB liberados em us-east-1 + 5 documentos de RH disponiveis para upload antes do Dia 1. Todos ja registrados como assumptions em `requirements.md`.
- B. Adicionar: revisao humana obrigatoria dos documentos antes do `StartIngestionJob` (CC-1/CC-2 em ingestion time).
- X. Other (please specify)

[Answer]: B

### Q6. Preocupacao maior

- A. IAM least-privilege quebrar durante deploy (roles sem `Resource: "*"`). Mitigacao: `cdk synth` obrigatorio + revisao do template antes de `cdk deploy`.
- B. Inference profile ARN nao liberado na conta sandbox (`us.*` requer profile). Mitigacao: verificar liberacao antes do Bolt 1.
- C. LGPD - agente vazar dados individuais (mesmo com system prompt). Mitigacao: teste unitario NFR8.2 obrigatorio + recomendacao de Bedrock Guardrails.
- D. Todas acima. Endereco em Bolts 1, 2 e 3 respectivamente.
- X. Other (please specify)

[Answer]: D

## Assumption Confirmation

Sem team-formation neste MVP -> todos os Bolts executam por `aidlc-developer-agent`. `skeleton: off` -> primeiro Bolt e um Bolt normal. Sequencia proposta segue topologia + risk-first: Bolt 1 = U2 hr-agent (validar LGPD + Strands + KB retrieve), Bolt 2 = U3 infra (empacotar + IAM + deploy), Bolt 3 = U1 chat-frontend (integrar e demo E2E).

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumo consolidado das decisoes deste stage:

- 3 Bolts sequenciais em ordem `[Bolt 1 hr-agent, Bolt 2 infra, Bolt 3 chat-frontend]` (Q1=A risk-first, Q2=A informal, Q3=A 1 Bolt/Unit, Q4=A sequencial).
- Sem walking skeleton (`skeleton: off` em team-practices).
- Todos os Bolts executados por `aidlc-developer-agent` (team-formation SKIP no mvp).
- 6 dependencias externas mapeadas (Q5=B inclui revisao humana de docs pre-ingestao).
- Riscos endereçados: IAM (Bolt 2), inference profile (Bolt 2), LGPD (Bolt 1 + NFR8.2) - Q6=D.
- Phase Boundary Verification: PASS (0 GAP em user-stories/domain-design/units-generation).
- Construction iteration mode: `unit-major`.

Artefatos produzidos:
- `bolt-plan.md`
- `team-allocation.md`
- `risk-and-sequencing-rationale.md`
- `external-dependency-map.md`
- `verification/phase-check-inception.md`

[Answer]: Looks correct
