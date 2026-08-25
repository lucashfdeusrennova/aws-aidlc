# Requirements - Chatbot de RH com Bedrock AgentCore

Requisitos funcionais e nao-funcionais derivados de `intent-statement.md`,
`scope-document.md`, `intent-backlog.md` e `team-practices.md`, refinados pelas
respostas Q1-Q6 desta etapa. Cada requisito carrega um ID estavel (FRn / NFRn)
que sera preservado pelas fases seguintes (User Stories, Domain Design,
Contract Design, Functional Design).

## Intent Analysis

O objetivo do usuario e reduzir o custo de consultar politicas de RH manualmente:
colaboradores devem obter respostas confiaveis sobre politicas, ferias, onboarding,
avaliacoes de desempenho e feriados diretamente em linguagem natural, sem depender
de intervencao humana para cada duvida cotidiana. [intent-statement.md]

O sucesso desta iniciativa e um chatbot funcional que respeita a fronteira de LGPD
("nao expor dados individuais") e opera em `us-east-1` sobre a stack afirmada em
`team-practices.md` (AgentCore Runtime + Knowledge Bases + Strands + Streamlit).
[intent-statement.md][scope-document.md][team-practices.md]

## Functional Requirements

Cada requisito funcional carrega o ID `FR{n}` (permanente) e mapeia para itens
do `intent-backlog.md` quando aplicavel.

### FR1. Responder perguntas em linguagem natural em portugues sobre politicas de RH

O chatbot deve responder perguntas em portugues sobre os 5 documentos de RH da base
de conhecimento. [Q1][intent-statement.md]

- **FR1.1** - Politicas gerais de RH (fonte: `employee_handbook.pdf`). [Q1 A]
- **FR1.2** - Ferias, licencas e afastamentos (fonte: `leave_policy.pdf`). [Q1 B]
- **FR1.3** - Onboarding de novos funcionarios (fonte: `onboarding_checklist.pdf`). [Q1 C]
- **FR1.4** - Avaliacao de desempenho (fonte: `performance_review_guidelines.pdf`). [Q1 D]
- **FR1.5** - Feriados da empresa (fonte: `public_holidays.csv`). [Q1 E]

Criterio de sucesso funcional: para cada FR1.x, ha pelo menos uma pergunta canonica
respondida corretamente durante o smoke test. [team-practices.md § Testing Posture]

### FR2. Base de conhecimento indexada em Bedrock Knowledge Bases + S3 Vectors

O sistema deve possuir uma Knowledge Base do Bedrock indexada com os 5 documentos
de RH em `us-east-1`, com vector store S3 Vectors. [intent-backlog.md B-1][scope-document.md]

- **FR2.1** - Bucket S3 com os 5 documentos vinculado a KB. [intent-backlog.md B-1]
- **FR2.2** - Sincronizacao inicial dos documentos (`StartIngestionJob`) executada
  antes da demo. [team-practices.md § Deployment]
- **FR2.3** - Snapshot fixo dos documentos durante os 2 dias de demo (sem re-sync
  automatico). [scope-document.md][intent-statement.md Q9]

### FR3. Agente executado em AgentCore Runtime respondendo perguntas

O agente Strands deve ser deployado no Amazon Bedrock AgentCore Runtime na regiao
`us-east-1`, invocado via `boto3.client("bedrock-agentcore")` e
`invoke_agent_runtime`. [intent-backlog.md B-2][team-practices.md § Deployment]

- **FR3.1** - Agente construido com Strands Agents SDK usando a tool `retrieve`
  para RAG na Knowledge Base. [scope-document.md]
- **FR3.2** - Sessoes isoladas em microVM (garantido pelo AgentCore Runtime).
  [intent-statement.md]

### FR4. Interface web Streamlit para o colaborador

O sistema deve possuir uma interface de chat via Streamlit rodando localmente
(`streamlit run frontend/app.py`), invocando o agente via `invoke_agent_runtime`.
[intent-backlog.md B-3][wireframes.md]

- **FR4.1** - Chat central com historico de mensagens (bolhas usuario/assistente)
  renderizado por `st.chat_message`. [wireframes.md]
- **FR4.2** - Input de chat na base da tela (`st.chat_input`). [wireframes.md]
- **FR4.3** - Spinner "Consultando base de conhecimento..." exibido enquanto
  `invoke_agent_runtime` esta em execucao. [wireframes.md]
- **FR4.4** - Sidebar com seletor de modelo de chat (dropdown com pelo menos 2
  opcoes). [wireframes.md Q1][intent-backlog.md B-5]
- **FR4.5** - Sidebar com botao "Limpar conversa" que gera novo `session_id`
  (via `uuid.uuid4()`) e zera o historico. [wireframes.md Q1]

### FR5. Prompt de sistema com regra de compliance LGPD

O agente deve executar com prompt de sistema explicito que proibe expor dados
individuais de colaboradores (salario, historico pessoal, dados nominais).
[intent-backlog.md B-4][project.md § Forbidden]

- **FR5.1** - System prompt instrui responder em portugues, cita documento fonte
  quando aplicavel (uso interno - vide FR7.2), e recusa responder sobre dados
  individuais. [scope-document.md]
- **FR5.2** - Quando informacao nao esta na Knowledge Base, o agente responde
  "Nao encontrei essa informacao nos documentos. Sugiro contatar o time de RH."
  Nao inventa. [Q2 A][intent-statement.md]

### FR6. Troca de modelo de chat via configuracao

O sistema deve suportar troca do modelo de chat sem redeploy do agente, permitindo
comparar qualidade e latencia entre pelo menos 2 modelos. [intent-backlog.md B-5]
[scope-document.md]

- **FR6.1** - Modelo de chat lido de variavel de ambiente ou parametro do agente.
  [team-practices.md § Code Style]
- **FR6.2** - Modelos `us.*` acessados via inference profile ARN (nunca como ID
  direto). [project.md § Mandated]
- **FR6.3** - Pelo menos 2 modelos testados durante a demo (registrados em
  smoke test ou README). [intent-statement.md Success Criteria]

### FR7. Renderizacao da resposta ao colaborador

Renderizacao da resposta final ao usuario final na UI do Streamlit.

- **FR7.1** - Resposta em portugues, em texto plano, dentro da bolha de assistente.
  [wireframes.md]
- **FR7.2** - **Sem citacao explicita do documento fonte na UI** (desvio consciente
  do criterio "Rastreabilidade" original em `intent-statement.md`). O agente usa a
  base internamente; a citacao nao aparece na resposta ao colaborador.
  [wireframes.md Q2][user-flow.md]

### FR8. Validacao de tamanho maximo de input

O sistema deve rejeitar inputs com mais de 4000 caracteres antes de invocar o
agente. [Q5 A][project.md § Mandated][tech-env.md § Security Basics]

- **FR8.1** - Guard de comprimento implementado em `src/invoke.py`, levantando
  `ValueError`. [team-practices.md § Code Style]
- **FR8.2** - Frontend Streamlit captura o `ValueError` e mostra aviso amigavel
  (`st.warning(...)`): "Sua pergunta ultrapassa 4000 caracteres. Reformule mais
  curto." Nao chama o agente. [Q5 A][team-practices.md § Code Style]

### FR9. Tratamento de erro na UI

Quando o `invoke_agent_runtime` falhar (timeout, throttling, resposta vazia, erro
de IAM), a UI deve mostrar mensagem amigavel, sem stack trace. [wireframes.md Q3]
[user-flow.md][team-practices.md § Code Style Error handling policy]

- **FR9.1** - `src/invoke.py` captura `botocore.exceptions.ClientError` e re-eleva
  como `AgentInvocationError`.
- **FR9.2** - `frontend/app.py` captura `AgentInvocationError` e renderiza como
  `st.error("Nao consegui responder agora. Tente reformular ou contate o RH.")`.
- **FR9.3** - Log do `ClientError` original via `logging.getLogger(__name__)`
  para debug local.

## Non-Functional Requirements

### NFR1. Latencia por resposta

- **NFR1.1** - Latencia maxima de **5 segundos** por resposta (tempo entre envio
  da pergunta e primeira renderizacao no chat). [intent-statement.md]
  [constraint-register.md CN-1]

### NFR2. Idioma

- **NFR2.1** - Todas as respostas do chatbot em **portugues**.
  [intent-statement.md][constraint-register.md CN-2]

### NFR3. Isolamento de sessao (Seguranca / Compliance)

- **NFR3.1** - Cada sessao roda em microVM isolada, garantido pelo AgentCore
  Runtime (fora do controle do time; e caracteristica do servico).
  [intent-statement.md]
- **NFR3.2** - `session_id` gerado server-side (`uuid.uuid4()`), nunca aceito de
  input do usuario, query string ou header. [project.md § Mandated]

### NFR4. Compliance LGPD

- **NFR4.1** - **NUNCA** expor dados individuais de colaboradores (salario,
  historico pessoal, dados nominais) em qualquer resposta. Controle primario:
  system prompt + conteudo da KB. [project.md § Forbidden][constraint-register.md CC-1, CC-2]
- **NFR4.2** - Ingestao de documentos com dados individuais na KB e proibida
  (controle CC-1/CC-2 em ingestion-time). [project.md § Forbidden]
- **NFR4.3** - Recomendacao (nao Mandated): Bedrock Guardrails configurado com
  filtro de PII em `OUTPUT` e denied topics ("salario, remuneracao, folha, dados
  individuais") como defesa em profundidade. [team-practices.md § Deployment]

### NFR5. Seguranca e IAM

- **NFR5.1** - IAM roles distintas por plano de acesso: execution role do
  AgentCore Runtime, role do frontend Streamlit, role de ingestao da KB.
  [project.md § Mandated]
- **NFR5.2** - Nenhuma politica IAM com `Resource: "*"` em `bedrock:InvokeModel*`,
  `bedrock:Retrieve*`, `s3:*` ou `bedrock-agentcore:*`. [project.md § Forbidden]
- **NFR5.3** - Objetos do S3 (bucket dos documentos) com criptografia em repouso
  (SSE-S3). [project.md § Mandated][tech-env.md § Security Basics]
- **NFR5.4** - Segredos (se surgirem) via `{{resolve:secretsmanager:...}}` no CDK;
  nunca `secretsmanager:GetSecretValue` direto no runtime. [project.md § Forbidden]

### NFR6. Escala esperada durante a demo

- **NFR6.1** - Suporte a **1-3 sessoes simultaneas** durante os 2 dias de demo,
  operado pelo time tecnico do workshop. [Q3 A]
- **NFR6.2** - Nao ha alvo de escala alem de 3 sessoes; capacidade adicional e
  fornecida pelo AgentCore Runtime como servico gerenciado (microVM por sessao).

### NFR7. Reprodutibilidade

- **NFR7.1** - Todas as dependencias Python pinadas com `==X.Y.Z` em
  `requirements.txt` e `agent/requirements.txt`. [project.md § Mandated]
- **NFR7.2** - `cdk synth` obrigatorio antes de `cdk deploy`; ARNs consumidos
  de outputs do stack, nunca hardcoded. [project.md § Mandated]

### NFR8. Testabilidade

- **NFR8.1** - Cobertura de linhas >= **80%** no codigo de `agent/` e `src/`,
  bloqueante local via `pytest --cov=agent --cov=src --cov-fail-under=80`.
  [team-practices.md § Testing Posture]
- **NFR8.2** - Teste unitario obrigatorio para guardrail LGPD: prompt provocador
  + tool `retrieve` stubada retornando trecho com salario ficticio; asserir que a
  resposta do agente **nao** repete o valor. [team-practices.md § Testing Posture]
- **NFR8.3** - Smoke test via `scripts/smoke.py` executado antes da demo, com
  3-5 perguntas canonicas incluindo uma que valida a recusa LGPD.
  [team-practices.md § Testing Posture]

### NFR9. Disponibilidade

- **NFR9.1** - Sem alvo formal de disponibilidade 24/7 nesta demo. O agente esta
  disponivel enquanto a conta sandbox e o AgentCore Runtime estiverem ativos.
  [constraint-register.md CN-3][intent-statement.md]

### NFR10. Historico de conversacao (Should Have)

- **NFR10.1** - Historico de conversacao dentro da mesma sessao Streamlit
  (`session_id` estavel enquanto a aba estiver aberta) usando AgentCore Memory,
  se sobrar tempo apos os Must Have. [Q4 A][intent-backlog.md B-11]

## Constraints

Restricoes ja consolidadas em `constraint-register.md` (referenciadas por ID) e
`project.md`:

- Regiao unica: `us-east-1` (CA-1). [project.md § Mandated]
- Stack fixa: Bedrock AgentCore Runtime + Bedrock Knowledge Bases + S3 Vectors +
  Strands Agents SDK + Streamlit (CA-1..CA-3, CT-1..CT-3).
- Sem integracao com sistemas externos (folha, ERP, LDAP/AD, portal, tickets)
  (CT-1).
- Sem deploy em producao; local-only + AgentCore Runtime na conta sandbox
  (CO-3, `team-practices.md § Deployment`).
- Prazo fixo de 2 dias corridos (CO-1).
- Bibliotecas proibidas: LangChain, LangGraph, OpenAI SDK, FastAPI, Flask,
  ChromaDB, Pinecone, SQLAlchemy, React, Next.js. [project.md § Forbidden]
- Sem CI configurado nesta demo; cobertura e lint sao gates locais.
  [team-practices.md]

## Assumptions

- Os 5 documentos de RH previstos estarao disponiveis para upload no S3 antes
  do dia 1 da demo. [raid-log.md A-1][NFR2.2]
- O time podera trabalhar nos 2 dias sem interrupcao por outras atividades.
  [raid-log.md A-2]
- A conta sandbox e as credenciais permanecerao validas durante os 2 dias.
  [raid-log.md A-3]

## Out of Scope

Consolidado do `scope-document.md`, `intent-statement.md § Out of Scope` e
respostas Q1-Q6 desta etapa:

- Integracoes com folha de pagamento, ERP, LDAP/AD, portal interno, sistema de
  tickets. [scope-document.md]
- Acoes transacionais (solicitar ferias, abrir chamado, alterar cadastro).
  [scope-document.md][intent-statement.md]
- Atendimento por voz. [intent-statement.md]
- Acesso a dados individuais de colaboradores (salario, historico pessoal).
  [intent-statement.md][NFR4.1]
- Treinamento / fine-tuning de modelos customizados. [intent-statement.md]
- Deploy em producao ou ambiente de staging. [scope-document.md]
- Reindexacao continua da Knowledge Base durante a demo. [FR2.3]
- Alvos formais de concorrencia (N usuarios simultaneos alem de 3),
  disponibilidade 24/7, ou custo por resposta. [NFR6.2][NFR9.1]
- Reranker, troca de modelo de embedding, IaC completo em CDK, metrica de custo
  por resposta - todos classificados como Could Have em `intent-backlog.md`
  (B-8, B-9, B-10, B-13), fora do MVP.
- Metricas de sucesso longitudinais (reducao de chamados, NPS/CSAT). [Q6 A]

## Open Questions

- Qual sera a frequencia de atualizacao dos documentos de RH pos-demo? Fica em
  aberto porque o MVP usa snapshot fixo (FR2.3), mas a resposta afeta como o
  time operacionalizara a KB depois. [intent-statement.md Open Questions]
- Qual canal final de integracao pos-demo (Slack, WhatsApp, portal interno)?
  Fora do MVP, mas registrado para nao perder.
  [intent-statement.md Open Questions]

## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-08-24T17:04:22Z
**Iteration:** 1
**Review class:** advisory

**Findings:**

- Nenhum defeito com evidencia que justifique NOT-READY. Reconferido item a item contra os 10 criterios de verificacao:
  (1) **IDs estaveis e unicos** - FR1..FR9 mais sub-IDs (FR1.1-1.5, FR2.1-2.3, FR3.1-3.2, FR4.1-4.5, FR5.1-5.2, FR6.1-6.3, FR7.1-7.2, FR8.1-8.2, FR9.1-9.3) e NFR1..NFR10 mais sub-IDs (NFR1.1, NFR2.1, NFR3.1-3.2, NFR4.1-4.3, NFR5.1-5.4, NFR6.1-6.2, NFR7.1-7.2, NFR8.1-8.3, NFR9.1, NFR10.1) - todos formatados `FR{n}[.{m}]` / `NFR{n}[.{m}]`, sem duplicatas, sem lacunas dentro do intervalo alocado.
  (2) **Rastreabilidade** - toda clausula substantiva carrega tag inline resolvivel (`[intent-statement.md]`, `[scope-document.md]`, `[team-practices.md]`, `[Q1]`-`[Q6]`) ou tag para artefato de estagio anterior desta mesma esteira (`[intent-backlog.md]`, `[constraint-register.md]`, `[wireframes.md]`, `[user-flow.md]`, `[project.md]`, `[raid-log.md]`, `[tech-env.md]`).
  (3) **Testabilidade** - criterios sao objetivos: FR1 possui criterio de smoke test explicito; NFR1.1 (5s), NFR6.1 (1-3 sessoes), NFR8.1 (>=80% linhas), NFR8.2 (teste unitario nomeado com fixture), NFR8.3 (3-5 perguntas canonicas) todos com threshold ou artefato concreto.
  (4) **Ausencia de linguagem vaga** - "amigavel" em FR8.2/FR9.2 vem sempre acompanhado da string exata a ser exibida; nada de "rapido"/"user-friendly" solto.
  (5) **Out of Scope completo** - deploy em producao, acoes transacionais, voz, dados individuais, fine-tuning e integracoes externas estao explicitamente listados; alvos formais de concorrencia/24-7/custo e metricas longitudinais tambem excluidos.
  (6) **NFR4 LGPD multicamada** - system prompt + conteudo da KB (NFR4.1), proibicao de ingestao de PII (NFR4.2), Guardrails como defesa em profundidade (NFR4.3); NFR8.2 adiciona verificacao unitaria auditavel.
  (7) **FR7.2 deviation documentada** - deixa claro que a UI nao cita documento fonte, referencia `wireframes.md Q2` e reconhece o desvio contra o criterio "Rastreabilidade" do `intent-statement.md`.
  (8) **Q1 = A,B,C,D,E reflete em FR1.1-FR1.5** - cinco sub-IDs, um por documento, cada um citando a resposta correspondente.
  (9) **Q4 (Should Have historico) reflete em NFR10.1** - marcado como "se sobrar tempo apos os Must Have", coerente com Should Have.
  (10) **Q5 (>4000 chars) reflete em FR8** - FR8.1 (guard em `src/invoke.py` com `ValueError`) + FR8.2 (frontend converte para `st.warning` com texto exato).
- Alinhamento com o guardrail de fase inception ("must be testable and verifiable") confirmado; a unica classe de requisito sem threshold formal e NFR9 (disponibilidade), e a ausencia esta explicitamente declarada e ancorada em `constraint-register.md CN-3`.

**Suggestions:**

- **Traceability sensor scope** - varios claims citam artefatos de estagios anteriores que nao estao declarados no `consumes:` deste estagio (`intent-backlog.md`, `constraint-register.md`, `wireframes.md`, `user-flow.md`, `raid-log.md`, `project.md`, `tech-env.md`). Sao citacoes legitimas do trilho de historia do intent, mas o sensor `upstream-coverage` so mede referencias aos artefatos declarados em `consumes:` (intent-statement, scope-document, team-practices). Nao muda o veredito; se voces preferirem que o sensor "veja" essas fontes explicitamente, considerar (a) adicionar um paragrafo introdutorio que cite os tres artefatos declarados juntos, ou (b) na proxima iteracao do arquivo de estagio, ampliar `consumes:` para incluir os artefatos co-produzidos que ja estao sendo usados em pratica.
- **FR6.3 "pelo menos 2 modelos testados"** - o gate de sucesso e "registrados em smoke test ou README". Ficaria ainda mais testavel amarrando ao artefato concreto: p.ex. "resultado registrado em `scripts/smoke.py` como bloco comentado com nome do modelo, latencia observada e resposta canonica". Como sugestao, nao bloqueio.
- **FR8.1 / FR9.1-9.3 mencionam caminhos de implementacao** (`src/invoke.py`, `frontend/app.py`, nome da excecao `AgentInvocationError`) que sao decisoes de design mais que de requisito. O acordo esta em `team-practices.md § Code Style` e a rastreabilidade esta intacta, mas puristas de "requisitos como o que, nao como" podem preferir mover esses detalhes para Domain Design / Functional Design e manter aqui apenas o comportamento observavel (rejeicao pre-invocacao com mensagem X; UI nao mostra stack trace). Trade-off consciente dado o cronograma de 2 dias.
- **NFR8.2 tem redacao mista de requisito e implementacao** ("teste unitario obrigatorio... com prompt provocador + tool `retrieve` stubada"). O requisito (auditar a recusa LGPD) e forte; a receita do teste ja e detalhe de execucao. Considerar dividir em NFR8.2 (requisito: "existe verificacao automatizada de que o agente nao repete valores de PII retornados por `retrieve`") + NFR8.2.1 (nota de implementacao) para separar o "o que" do "como". Nao bloqueio.
- **Open Questions esta enxuto (2 itens)** e ambos apontam para pos-demo. Vale confirmar com o time se nao ha ainda uma incerteza de dia 1 nao capturada (por exemplo: quem executa `StartIngestionJob` no dia da demo? Onde ficam as credenciais AWS de cada participante do workshop?). Se nao ha, manter como esta.
- **Consistencia de estilo de referencia** - alguns claims citam `[Q5 A]` (com letra da opcao) e outros apenas `[Q4 A]` ou apenas `[Q1]`. Uniformizar para "sempre inclui a letra da opcao escolhida" ajuda a auditar em uma unica passada. Detalhe.
