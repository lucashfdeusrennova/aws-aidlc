**Collaborator:** aidlc-delivery-agent

# Risk and Sequencing Rationale - Chatbot de RH com Bedrock AgentCore

Justifica a ordem escolhida em `bolt-plan.md` (Bolt 1 hr-agent -> Bolt 2
infra -> Bolt 3 chat-frontend) e confirma que respeita o DAG topologico
de `unit-of-work-dependency.md`.

Fontes consumidas: `requirements.md`, `stories.md`, `mockups.md`,
`components.md`, `unit-of-work.md`, `unit-of-work-dependency.md`,
`unit-of-work-story-map.md`, `contract-summary.md`, `team-practices.md`.

## Sources

- [rq] `requirements.md`.
- [st] `stories.md`.
- [mk] `mockups.md`.
- [cp] `components.md`.
- [uw] `unit-of-work.md`.
- [ud] `unit-of-work-dependency.md`.
- [sm] `unit-of-work-story-map.md`.
- [cs] `contract-summary.md`.
- [tp] `team-practices.md`.
- [bp] `bolt-plan.md`.

## Approach

**Heuristica escolhida**: risk-first + narrative rationale (Cohn / Reinertsen
CD3 informal, sem escoragem WSJF formal - Q2=A). Rationale:

- WSJF (Weighted Shortest Job First, Reinertsen/SAFe) tem melhor payoff em
  backlogs onde ha trade-off real entre valor incremental e job size.
  Aqui: 11 stories congeladas + 3 Units + 2 dias = otimizar por WSJF nao
  muda a ordem final.
- Cada Bolt tem "job size" comparavel (Medium, Medium, Large) e as
  dependencias topologicas ja restringem a ordem substancialmente.
- O que importa e reduzir risco AWS-side cedo. Risk-first bate value-first
  neste contexto porque o "valor" so materializa quando os 3 Bolts estao
  no ar.

## Bolt sequence vs topological order

DAG de `unit-of-work-dependency.md`:

```
hr-agent (U2) <-- infra (U3)   (arestas de build-time)
chat-frontend (U1)              (folha independente em build-time)
```

Ordens topologicas validas: `[U1, U2, U3]` e `[U2, U1, U3]` (U3 sempre por
ultimo em build; U1 pode ir em qualquer posicao antes de U3).

Escolhida: `[U2, U3, U1]` = **desvio da topologia estrita** para U1.
U1 nao depende de U3 em build-time, mas depende dos outputs de U3 (ARN
do Runtime) em RUNTIME. Colocar U1 no final permite que ele consuma
`AGENT_RUNTIME_ARN` real desde o primeiro run, sem `--reload` posterior.

Este desvio esta explicitamente registrado aqui (per stage prose:
"deviation must be captured in risk-and-sequencing-rationale.md").

## Risk-first argument por Bolt

### Bolt 1 hr-agent - por que primeiro

**Riscos endereçados**:

- **Prompt injection / LGPD**: sistema em portugues, tom breve, RAG-only,
  recusa de dados individuais - tudo depende do system prompt correto.
  Bolt 1 forca o time a escrever, testar (NFR8.2), e revisar o prompt
  antes de qualquer chamada AWS real. Se o prompt vazar dados no teste
  unitario com stub, o problema mora aqui e nao chega em producao.
  [rq NFR4.1, NFR8.2, US1.5].
- **Strands SDK familiarity**: primeira exposicao do time a Strands
  Agents SDK + `strands_tools.retrieve`. Se o SDK nao se comportar como
  esperado (versao pinada, breaking change de API), o problema aparece
  no Bolt 1 (testes) e nao no Bolt 3 (E2E demo).
- **`us.*` inference profile ARN**: contrato de tool `retrieve` +
  `BedrockModel` com inference profile ARN. Se o ARN nao for aceito,
  falha unitaria clara com `BedrockModel` mockado (schema-only).
  [project.md § Mandated].

**Riscos NAO endereçados aqui** (adiam para Bolt 2 ou 3):

- IAM real (adia para Bolt 2 - so precisa quando a chamada Bedrock e
  real).
- Latencia real <5s (adia para Bolt 3 smoke test).

### Bolt 2 infra - por que segundo

**Riscos endereçados**:

- **IAM least-privilege sem `Resource: "*"`**: policies enxutas em
  `bedrock:InvokeModel*`, `bedrock:Retrieve`, `s3:*` sao proibidas de
  usar wildcard. Bolt 2 forca o time a resolver ARNs especificos no
  CDK e revisar o template sintetizado antes do deploy
  [project.md § Forbidden].
- **KB ingestion + S3 Vectors funcionando**: `StartIngestionJob`
  precisa concluir com sucesso; a KB responder a `Retrieve` com trechos
  reais dos 5 documentos. Bolt 2 valida essa cadeia end-to-end
  (KB + S3 Vectors + role de ingestao) [rq FR2].
- **AgentCore Runtime provisionavel na conta sandbox**: primeira vez que
  o time cria um Runtime real. Se o servico nao estiver liberado em
  `us-east-1`, o problema aparece no Bolt 2 (cdk deploy falha) e nao
  no Bolt 3.
- **Documentos revisados antes de ingestao (CC-1/CC-2)**: gate humano
  obrigatorio antes de `StartIngestionJob`. Registrar em
  `team-allocation.md § Human touchpoints`.

**Riscos NAO endereçados aqui**:

- Wiring E2E via Streamlit (adia para Bolt 3).
- UI/UX (adia para Bolt 3).

### Bolt 3 chat-frontend - por que ultimo

**Riscos endereçados**:

- **E2E funcional em <5s [rq NFR1.1]**: primeira vez que a cadeia
  completa (Streamlit -> `invoke_agent_runtime` -> AgentCore Runtime ->
  Strands -> BedrockModel -> KB) roda ponta-a-ponta. `scripts/smoke.py`
  materializa o gate.
- **Guard 4000 chars + mapping de erro**: coberto pelos testes unitarios
  do `src/invoke.py` [rq FR8, FR9].
- **UI navegavel + tom breve + LGPD visivel no chat**: revisao manual
  humana antes do demo, mockups como referencia.

**Argumento para U1 no final** (nao no inicio, apesar de ser folha do
DAG):

- Sem Bolt 2 deployado, U1 so testa contra mocks. E possivel, mas o
  valor incremental de U1 antes de U2/U3 sao apenas testes unitarios
  do guard + mapping - Bolt 3 continua obrigatorio para o E2E.
- Colocar U1 primeiro geraria dois "momentos de wiring" (unitario e
  E2E); no final unifica em um so.

## Confidence hypothesis por Bolt (resumo)

Repetido de `bolt-plan.md § Bolt sequence`:

- **Bolt 1**: Strands + BedrockModel + tool `retrieve` + system prompt
  LGPD funcionam via unit tests.
- **Bolt 2**: 4 pecas AWS (S3 + KB + Runtime + IAM) provisionaveis em
  `us-east-1` sem `Resource: "*"` e KB responde a `Retrieve`.
- **Bolt 3**: E2E colaborador -> Streamlit -> AgentCore Runtime ->
  resposta em portugues em <5s, com guards + error handling.

## Score matrix (opcional)

Nao escorado formalmente (Q2=A). A tabela abaixo sumariza a heuristica
narrativa:

| Bolt | Value (1-5) | Risk reduction (1-5) | Job size (1-5) | Rationale                                                              |
| ---- | ----------- | -------------------- | -------------- | ---------------------------------------------------------------------- |
| Bolt 1 hr-agent   | 3 | 5 | 3 | Valor moderado isoladamente (nao demonstravel sem infra); alto risk reduction (LGPD + SDK). |
| Bolt 2 infra      | 4 | 5 | 4 | Alto valor (habilita E2E); alto risk reduction (IAM + KB); job size maior por conta de CDK. |
| Bolt 3 chat-frontend | 5 | 2 | 3 | Alto valor final (demo); risco baixo remanescente; tamanho medio.       |

Se o time quiser aplicar WSJF ad-hoc: `(3+5)/3 = 2.67`, `(4+5)/4 = 2.25`,
`(5+2)/3 = 2.33`. WSJF rankearia Bolt 1 > Bolt 3 > Bolt 2. Ignoramos
esse ranking porque a topologia forca Bolt 2 antes de Bolt 3 (Bolt 3
consome ARN de Bolt 2). Fica documentado apenas como sanity check.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->
