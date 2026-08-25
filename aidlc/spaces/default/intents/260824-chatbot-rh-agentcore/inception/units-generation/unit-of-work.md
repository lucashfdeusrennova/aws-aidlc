**Collaborator:** aidlc-architect-agent

# Unit of Work - Chatbot de RH com Bedrock AgentCore

Decomposicao em 3 unidades de trabalho, uma por target de deploy: UI local
Streamlit, servico Strands rodando em AgentCore Runtime, e stack CDK que
provisiona a infra AWS. Cada unidade carrega um `kind` distinto (`ui`,
`service`, `packaging`).

Fontes consumidas: `components.md` e `decisions.md` (Domain Design),
`requirements.md` (FR/NFR) e `stories.md` (11 stories).

## Sources

- [cp] `components.md` - 3 componentes: `HRChatFrontend`, `AgentInvoker`,
  `HRAgent`.
- [ad] `decisions.md` - 5 ADRs. ADR-001 fixa as fronteiras de camada
  refletidas nas unidades; ADR-002 e ADR-005 informam o kind e o
  deploy-time coupling.
- [rq] `requirements.md` - FR1-FR9 e NFR1-NFR10.
- [st] `stories.md` - 11 stories (US1.1..US4.1).
- [tp] `team-practices.md § Deployment` - `cdk deploy` unico stack em
  `us-east-1` para AgentCore Runtime + KB + S3.

## Units

### U1 - chat-frontend

- **Directory**: `u1-chat-frontend`
- **Kind**: `ui`
- **Descricao**: Aplicacao Streamlit local que renderiza o chat de RH e
  invoca o agente via `bedrock-agentcore.InvokeAgentRuntime`. Contem os
  componentes `HRChatFrontend` e `AgentInvoker` do `components.md` -
  ambos moram no mesmo repo Python (`frontend/` importando `src/`) e
  compartilham o mesmo lifecycle de dev (`streamlit run frontend/app.py`).
  Consome ARNs de outputs do CDK stack (U3) em runtime via env vars.
  [cp][st US1.6, US1.7, US1.9, US4.1][tp § Deployment].
- **Responsabilidades**:
  - Renderizar a UI de chat (Streamlit) sem CSS customizado.
  - Gerar `session_id` server-side via `uuid.uuid4()` e gerenciar
    `st.session_state`.
  - Validar `len(prompt) <= 4000` (guard defense-in-depth) antes de
    chamar `ask_agent`.
  - Encapsular a chamada `bedrock-agentcore.InvokeAgentRuntime` em
    `us-east-1` (via `src/invoke.py`).
  - Capturar `ClientError` e re-elevar como `AgentInvocationError`;
    frontend renderiza `st.error(...)` amigavel sem stack trace.
  - Ler `AGENT_RUNTIME_ARN`, `AWS_REGION` (fallback `us-east-1`) e
    dicionario `MODEL_ARNS` (Claude Haiku 4.5, Amazon Nova Pro) de env
    vars / configuracao local.
- **Deployment model**: `standalone` (executa localmente com
  `streamlit run frontend/app.py`; nao ha hosting hospedado).
- **Estimated complexity**: M (media). O core da UI e direto, mas o
  guard 4000, o mapping de erro, o dicionario `MODEL_ARNS`, o botao
  "Limpar conversa" e o contador de caracteres compoem varios
  componentes Streamlit no mesmo arquivo.
- **Notas de implementacao**:
  - Aderir a fronteira de camada: `frontend/app.py` importa `src/invoke.py`,
    `src/` nao importa `streamlit` [tp § Code Style].
  - Todos os packages Python pinados em `requirements.txt`
    (`streamlit==X.Y.Z`, `boto3==X.Y.Z`) [project.md § Mandated].
  - `pytest --cov=src --cov-fail-under=80` cobre a camada testavel
    (`src/invoke.py::ask_agent`); frontend Streamlit e validado
    manualmente durante a demo [tp § Testing Posture].
- **Constraints**:
  - Sem CSS/HTML custom (`unsafe_allow_html=False`).
  - Sem `st.set_page_config` com `lang="pt-BR"` explicito (WCAG 3.1.1
    gap consciente).
  - Roda em desktop com Chrome/Edge/Firefox modernos, resolucao >=
    1024px.

### U2 - hr-agent

- **Directory**: `u2-hr-agent`
- **Kind**: `service`
- **Descricao**: Agente Strands empacotado para rodar dentro da microVM do
  AgentCore Runtime. Contem o componente `HRAgent` do `components.md`.
  Auto-contido: importa apenas `strands`, `strands_tools` e `boto3`
  [tp § Code Style]. Nao conhece `src/` nem `frontend/`. O deploy final
  entra no stack CDK (U3), mas o **codigo** do agente e um unit proprio,
  testavel isoladamente (fixture central em `tests/conftest.py` com
  `BedrockModel` mockado + stub de `retrieve`).
  [cp][st US1.1-1.5, US2.1, US3.1][tp § Testing Posture].
- **Responsabilidades**:
  - Definir o system prompt de RH (portugues, tom breve, LGPD, sem
    inventar).
  - Configurar `BedrockModel` com o inference profile ARN passado como
    parametro (nunca ID `us.*` direto).
  - Registrar a tool `retrieve` do Strands consumindo a KB
    (`KNOWLEDGE_BASE_ID` via env var - o SDK resolve por env).
  - Emitir fallback "nao encontrei" e recusa LGPD conforme contratos de
    contains dos ACs (AC1.4.1, AC1.5.2, AC3.1.2).
  - Aderir ao contrato de guardrail testavel: 1 teste unitario com prompt
    provocador + `retrieve` stubado retornando trecho com salario
    ficticio; asserir que resposta **nao** repete verbatim
    [tp § Testing Posture].
- **Deployment model**: `standalone` (deployado dentro do AgentCore
  Runtime resource criado por U3).
- **Estimated complexity**: M (media). System prompt LGPD + Strands
  wiring + tool `retrieve` + integracao com inference profile ARN.
- **Notas de implementacao**:
  - `agent/requirements.txt` pinado com `strands==X.Y.Z`,
    `strands-tools==X.Y.Z`, `boto3==X.Y.Z`.
  - Nao importar de `src/` ou `frontend/` [tp § Code Style].
  - Cobertura >= 80% linhas em `agent/agent.py` obrigatoria
    [tp § Testing Posture].
- **Constraints**:
  - Regiao unica: `us-east-1`.
  - Modelos consumidos exclusivamente via inference profile ARN.
  - Sem chamadas `secretsmanager:GetSecretValue` diretas
    [project.md § Forbidden].

### U3 - infra

- **Directory**: `u3-infra`
- **Kind**: `packaging`
- **Descricao**: Stack CDK Python em `us-east-1` que provisiona
  Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Base (S3 Vectors) e
  bucket S3 dos documentos de RH, alem das 3 IAM roles distintas
  (execution role do Runtime, role/credencial do frontend, role de
  ingestao da KB) [tp § Deployment][project.md § Mandated]. Empacota o
  codigo de U2 no Runtime. Expoe ARNs (Runtime, KB, bucket) como outputs
  do stack, consumidos por U1 e pelo `scripts/smoke.py`. Sincroniza os 5
  documentos (`employee_handbook.pdf`, `leave_policy.pdf`,
  `onboarding_checklist.pdf`, `performance_review_guidelines.pdf`,
  `public_holidays.csv`) para o S3 e a KB executa `StartIngestionJob`
  manualmente antes da demo.
- **Responsabilidades**:
  - Provisionar Amazon Bedrock Knowledge Base + S3 Vectors + bucket S3
    dos documentos (SSE-S3).
  - Provisionar AgentCore Runtime consumindo o codigo/imagem de U2.
  - Provisionar 3 IAM roles least-privilege:
    - Runtime execution role: `bedrock:InvokeModel*` para os inference
      profile ARNs especificos + `bedrock:Retrieve` para a KB especifica
      + logs;
    - Role/credencial do frontend: `bedrock-agentcore:InvokeAgentRuntime`
      para o ARN do runtime;
    - Role de ingestao da KB: `s3:GetObject`/`s3:ListBucket` no bucket +
      `bedrock:StartIngestionJob` na KB.
  - Exportar ARNs como CloudFormation outputs.
  - Resolver segredos (se houver) via `{{resolve:secretsmanager:...}}`
    no template CDK; nunca no runtime.
- **Deployment model**: `standalone` (`cdk deploy` unico stack; sem
  staging, sem CD).
- **Estimated complexity**: L (grande). CDK Python + AgentCore Runtime +
  Bedrock KB + S3 Vectors + 3 IAM roles + outputs + sincronizacao de
  documentos. E onde a maior parte da configuracao AWS mora.
- **Notas de implementacao**:
  - `cdk synth` obrigatorio antes de `cdk deploy` [project.md § Mandated].
  - Consumir ARNs de outputs do stack; nunca hardcoded no codigo de U1 ou
    U2 [tp § Deployment].
  - `.gitignore` do commit inicial: `.env`, `*.pem`, `credentials`,
    `*.pfx`, `aws-credentials*`, `**/secrets/**` [project.md § Mandated].
- **Constraints**:
  - Sem `Resource: "*"` em `bedrock:InvokeModel*`, `bedrock:Retrieve*`,
    `s3:*` ou `bedrock-agentcore:*` [project.md § Forbidden].
  - Bucket S3 SSE-S3 obrigatorio [project.md § Mandated].
  - Sem deploy em producao; conta sandbox do workshop [tp § Deployment].

## Summary Table

| Unit ID | Directory          | Name           | Kind      | Deployment model | Complexity | Componentes contidos                    |
| ------- | ------------------ | -------------- | --------- | ---------------- | ---------- | --------------------------------------- |
| U1      | `u1-chat-frontend` | chat-frontend  | ui        | standalone       | M          | HRChatFrontend, AgentInvoker            |
| U2      | `u2-hr-agent`      | hr-agent       | service   | standalone       | M          | HRAgent                                 |
| U3      | `u3-infra`         | infra          | packaging | standalone       | L          | (nao contem componente de dominio; empacota U2 e provisiona a infra AWS que U1 e U2 usam) |

## Rationale

Optamos pela **fronteira por target de deploy** (Q1=A) porque as 3
unidades tem lifecycles de deploy distintos que ja estao codificados em
`team-practices.md § Deployment`: Streamlit local, servico dentro do
AgentCore Runtime, e stack CDK unificado. Manter menos unidades (Q1
opcao B, C) escondia a fronteira mais importante do MVP - a de deploy
AWS - e forcava o mesmo unit a carregar tanto o design de UI quanto o
codigo de infra.

**Alternatives Rejected**:

- **Fine-grained com 5 unidades** (Q2 opcao B - separando invoker e KB):
  invoker nao tem lifecycle proprio de deploy (mora no mesmo repo do
  frontend); KB nao tem codigo nosso a possuir (Strands SDK resolve por
  env var). Ambos ficam melhor como parte de U1 e U3 respectivamente.
- **Cadeia estrita sequencial `U3 -> U2 -> U1`** (Q3 opcao B): impediria
  paralelismo em Construction. Como U1 e U2 sao independentes em
  build-time (frontend testa contra invoker mockado, agente testa contra
  `BedrockModel` mockado + `retrieve` stubado), Q3=A libera o time para
  dividir o trabalho.
- **Deploy monolitico com um comando** (Q5 opcao B): CDK deploy de U3 ja
  provisiona U2 dentro do runtime; U1 continua um `streamlit run` local.
  Nao ha ganho em envolver os dois em um script unico dentro de 2 dias.
- **Colocar o CDK stack como `service`** (Q2 alternativa): CDK stack e
  packaging de infra, nao um service consumido por HTTP. `kind: packaging`
  ativa a matriz correta de design em construction (sem contract-design
  pesado, sem NFR requirements de servico).

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->

## Review

**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-08-24
**Iteration:** 1
**Review class:** advisory
**Verdict:** READY

### Findings

| # | Severity | Location | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | Minor | `unit-of-work-story-map.md` § "Story implementation order dentro de cada unit" (cabecalhos `U1 chat-frontend (5 stories)` e `U2 hr-agent (6 stories)`); `unit-of-work.md` § "Rationale" ("Manter menos unidades..."); `units-generation-questions.md` § "Consolidated Summary Confirmation" ("11 stories rastreadas 1:1: 6 -> U2, 5 -> U1, 0 -> U3") | Contagem por unidade divergente da distribuicao real no `traceability.json` e na tabela `Story -> Unit`. A distribuicao efetiva e **U1 = 4** stories (US1.6, US1.7, US1.9, US4.1) e **U2 = 7** stories (US1.1, US1.2, US1.3, US1.4, US1.5, US2.1, US3.1). O total (11) e a atribuicao por story estao corretos; so os subtotais estao errados. Provavelmente resquicio da re-numeracao US1.8 -> US4.1 + insercao de US1.9. Nao afeta downstream (delivery-planning consome a tabela e o `traceability.json`, nao os subtotais), mas induz erro em qualquer leitor que confie no numero agregado. | Editar os tres pontos para "U1 (4 stories)" e "U2 (7 stories)". Nenhum reordenamento de commit dentro de U1/U2 precisa mudar - a lista granular de commits ja esta certa; so o rotulo do cabecalho e o texto do resumo. |
| 2 | Minor | `unit-of-work-dependency.md` § "Edge Block" (bloco YAML) e § "Contrato U3 -> U1" | O edge block registra apenas `infra -> hr-agent` como aresta de build. `chat-frontend` fica formalmente sem nenhuma dependencia declarada, mesmo carregando um contrato bem-definido com U3 (envelope de outputs `AgentRuntimeArn`, `KnowledgeBaseId`, `DocumentsBucketName`, prefixo esperado do ARN). A prosa justifica ("runtime deployment coupling nao e build dep"), o que e defensavel para o esquema do edge block. Mas cria assimetria: U2 tem um contrato de execution role/env var com U3 igualmente runtime e tambem nao aparece no edge block; U3 tem um contrato de empacotamento com U2 e aparece. O criterio "build-time apenas" e legitimo, so deixa o desenvolvedor de U1 sem sinal estrutural de que existe um acoplamento por outputs. | Duas opcoes, ambas nao bloqueantes: (a) manter o edge block estrito (build-time), e adicionar uma secao `## Runtime dependencies (informativa)` com um segundo pseudo-bloco YAML (ou tabela) listando `chat-frontend -> infra` e `hr-agent -> infra` como dependencias de deploy/runtime, deixando claro que sao consumidas em `delivery-planning` mas nao afetam a ordem de build; (b) mudar o esquema do edge block para incluir `depends_on_runtime` como campo separado. A leitura (a) preserva a semantica atual do sensor e o significado de "topologia de build", so ganha visibilidade. |
| 3 | Minor | `unit-of-work.md` § U3 "Sincroniza os 5 documentos ... para o S3 e a KB executa `StartIngestionJob` manualmente antes da demo" vs § U3 "Responsabilidades" ("Provisionar Bedrock Knowledge Base + ... bucket S3 dos documentos") | Ambiguidade sobre quem executa `StartIngestionJob`. A prosa da descricao diz "manualmente antes da demo" (operacao humana); a lista de responsabilidades de U3 nao inclui a chamada, so o provisionamento. `unit-of-work-story-map.md § Cross-cutting concerns` registra a mesma pre-condicao mas atribui a execucao manual. `unit-of-work-dependency.md § Direct dependencies § U3 § Runtime dependencies` fecha o loop ("`StartIngestionJob` manual apos deploy"). O sinal esta consistente entre os tres artefatos ("manual"), mas a fronteira de U3 nao registra a operacao como parte da checklist de deploy - ela fica orfa entre codigo CDK e operacao humana. Se o developer de U3 assumir que basta `cdk deploy`, a demo aparenta quebrada. | Adicionar uma linha em `U3.Constraints` ou `U3.Notas de implementacao` reafirmando: "`cdk deploy` NAO chama `StartIngestionJob`; a ingestao inicial e passo operacional documentado no plano de demo (registrado em `delivery-planning`)." Ou promover uma responsabilidade auxiliar em U3 do tipo "Publicar comando/script `aws bedrock-agent start-ingestion-job` na documentacao do runbook, mesmo que a execucao seja humana". |
| 4 | Minor | `unit-of-work-story-map.md` § "Story -> Unit" - linhas US1.6 e US1.7 (coluna "Componente principal": "AgentInvoker + Streamlit") vs `traceability.json` - linhas US1.6 e US1.7 (`"target": "U1"` sem breakdown por componente) | US1.6 e US1.7 sao explicitamente descritas como stories que atravessam a fronteira `frontend/ -> src/` dentro de U1 (guard primario e `ClientError` mapping em `AgentInvoker`, `st.warning`/`st.error`/logging no `HRChatFrontend`). A tabela do story-map ja marca "AgentInvoker + Streamlit" na coluna componente, mas o `traceability.json` so vai ate o nivel unit (nao componente). Consistente com o esquema atual da traceability, mas perde informacao que os proprios artefatos deste stage produziram. | Nao bloqueia. Se a traceability sensor evoluir para aceitar `secondary_component` ou `owning_components: [...]`, este eh o par de stories a materializar primeiro. Fica como sinal para `functional-design`, que consome a tabela do story-map para decidir onde a assinatura publica `ask_agent(prompt, session_id, model_id) -> str` mora - a resposta ja esta implicita na coluna "Componente principal". |

### Verificacoes que passaram

| Criterio | Resultado | Evidencia |
|---|---|---|
| YAML edge block bem-formado | PASS | Bloco fenced ```yaml ... ``` em `unit-of-work-dependency.md § Edge Block`; chaves top-level `units`; cada item tem `name`, `kind`, `depends_on`. |
| Edge block cycle-free | PASS | Unica aresta declarada: `infra -> hr-agent`. Nenhum ciclo possivel com uma unica aresta direcionada. |
| Edge block com kinds validos | PASS | `ui`, `service`, `packaging` - todos no conjunto permitido (`service`/`spec`/`ui`/`packaging`/`library`). |
| `depends_on` so referencia unidades declaradas | PASS | `infra.depends_on = [hr-agent]` - `hr-agent` esta declarado tres linhas acima como `- name: hr-agent`. |
| 11 stories mapeadas em `unit-of-work-story-map.md` | PASS | 11 linhas de `\| US\d+\.\d+` na tabela `Story -> Unit`: US1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.9, US2.1, US3.1, US4.1. Bate 1:1 com os 11 cabecalhos `### US...` em `stories.md`. |
| 11 stories em `traceability.json` com status `OK` | PASS | `upstream_ids` lista as 11; `coverage` traz 11 objetos com `"status": "OK"` e `"target"` apontando para U1 ou U2. |
| Kind coerente com conteudo - U1 = `ui` | PASS | Streamlit app renderizando UI de chat, sem endpoint de servico, sem template de infra. |
| Kind coerente com conteudo - U2 = `service` | PASS | Agente Strands em processo isolado (microVM AgentCore Runtime), com `BedrockModel` + tool `retrieve`, consumido via `invoke_agent_runtime`. |
| Kind coerente com conteudo - U3 = `packaging` | PASS | CDK Python stack unico em `us-east-1`, empacota codigo de U2, provisiona 3 IAM roles, KB, bucket S3. Nao expoe endpoint proprio. |
| Topologia de dependencia (nao ordem de implementacao) | PASS | `unit-of-work-dependency.md` afirma explicitamente "Esta observacao topologica **nao e** uma recomendacao de ordem de implementacao - a decisao economica ... pertence a `delivery-planning`". Y-invertido U1/U2 folhas -> U3 convergindo. |
| Sensor `upstream-coverage`: referencia components + decisions + requirements + stories | PASS | `unit-of-work.md § Sources`: cita `components.md` [cp], `decisions.md` [ad], `requirements.md` [rq], `stories.md` [st], `team-practices.md` [tp]. `unit-of-work-dependency.md § Sources` idem, com `unit-of-work.md` [uw] adicionado. `unit-of-work-story-map.md § Sources` idem. |
| Boundary alignment com `team-practices.md § Code Style` (`frontend/ -> src/ -> boto3`) | PASS | U1 abriga `frontend/` E `src/` no mesmo diretorio-unidade porque compartilham deployment lifecycle (Streamlit local); a fronteira interna a U1 e enfatizada na nota de implementacao "`frontend/app.py` importa `src/invoke.py`, `src/` nao importa `streamlit`". |
| Boundary alignment com `team-practices.md § Code Style` (`agent/` isolado) | PASS | U2 lista explicitamente "Nao importar de `src/` ou `frontend/`" como Nota de implementacao; `agent/requirements.txt` proprio; nenhuma referencia a `AgentInvoker` como import Python (o coupling e via AgentCore Runtime, external dependency). |
| Componentes contidos em unidades - `HRChatFrontend`, `AgentInvoker` em U1; `HRAgent` em U2 | PASS | `unit-of-work.md § Summary Table` mapeia os 3 componentes de `components.md` para U1/U2 sem duplicacao nem orfaos. U3 corretamente registra "nao contem componente de dominio; empacota U2 e provisiona a infra AWS". |
| Assinaturas dos contratos U1<->U2, U3->U1, U3->U2 rastreaveis | PASS (bonus) | `unit-of-work-dependency.md § Integration points` explicita `ask_agent(prompt, session_id, model_id) -> str`, prefixo do ARN de Runtime, env vars `AGENT_RUNTIME_ARN`/`KNOWLEDGE_BASE_ID`, e diferimento formal a `contract-design`. |
| Q1-Q5 respondidos e coerentes com artefatos | PASS | `units-generation-questions.md` traz `[Answer]: A` em Q1-Q5 e "Looks correct" no summary confirmation. Cada resposta bate com a decisao materializada em `unit-of-work.md § Rationale` e § Alternatives Rejected. |

### Sugestoes (nao bloqueantes)

- **S1 - Nomear as duas orderings topologicas na secao final de `unit-of-work-dependency.md` como candidatas de entrada para `delivery-planning`.** O texto ja diz "`[U1, U2, U3]` e `[U2, U1, U3]`, ambas com U3 no fim", mas nao rotula qual seria a walking-skeleton-first (`[U2, U1, U3]`, com risco maior primeiro) vs pipeline-optimizada (`[U1, U2, U3]`). Rotular ajuda `delivery-planning` a nao redescobrir a distincao. Deliberadamente nao decida ordem aqui; so nomeie.
- **S2 - Consolidar o dicionario `MODEL_ARNS` como possivel candidato a config file dedicado em vez de literal Python em `frontend/app.py`.** Nao e finding: `functional-design` e o lugar. Registrar aqui so como sinal para o proximo stage.
- **S3 - Ao editar Finding #1, aproveitar para eliminar a frase "estas ligacoes runtime nao viram entradas em `unit-of-work-dependency.md § Edge Block` (que registra dependencias de build)" duplicada entre `unit-of-work-story-map.md § Cross-cutting concerns` e `unit-of-work-dependency.md § Direct dependencies`.** Nao contradiz nada, mas centralizar num lugar so reduz drift em revisoes futuras.
- **S4 - Documentar a decisao "IAM role de U2 recebe `KNOWLEDGE_BASE_ID` via env var injetada pelo role" no proximo iteration de `decisions.md` (nao neste stage).** Hoje isso aparece so em `unit-of-work-dependency.md § Contrato U3 -> U2` sem ADR. `contract-design` sera o local natural para formalizar; anotar aqui apenas para nao esquecer.

### Summary

Os quatro artefatos formam um decompositor coerente: 3 unidades com kinds distintos (ui/service/packaging), edge block YAML bem-formado com aresta unica U3->U2, 11 stories rastreadas 1:1 sem orfaos, fronteiras de deploy alinhadas ao `team-practices.md § Deployment` e `§ Code Style`. Nenhum ciclo, nenhuma referencia dangling, nenhuma story sem unit. As quatro Findings sao todas Minor e nao alteram a topologia nem os contratos; a mais visivel (numero por unidade escrito como 5/6 em vez de 4/7) e um erro de contagem que se corrige com edicao em tres linhas. Num pass advisory o veredito e READY - as decisoes ficam com o humano no gate de aprovacao.
