# User Stories - Chatbot de RH com Bedrock AgentCore

Stories organizadas por persona (breakdown escolhido em Q2=B), consumindo
`requirements.md` como fonte de FRs/NFRs e `personas.md` como fonte de
personas. IDs `US{group}.{seq}` e `AC{group}.{seq}.{n}` sao permanentes.

Formato de story: "Como [persona], quero [objetivo], para [beneficio]."
Acceptance criteria em BDD (Given/When/Then) conforme
`aidlc/spaces/default/memory/phases/inception.md` § User Stories.

**Integracao mob**: as contribuicoes de design, developer e quality (round 1)
foram integradas via decisao humana ("Apply all" na triagem):
- Nova story US1.9 (Iniciar nova conversa) cobrindo FR4.5.
- Nova persona P4 (Operador) para US4 (troca de modelo).
- AC1.8.2 reescrito para exigir `model_id` observavel.
- AC1.8.4 mapeamento corrigido.
- Redacao de US1.6 e US1.7 ajustada.
- Assertion anchors dos AC de consulta deferidos a `functional-design` e
  registrados em `## Open Questions`.
- Gaps sem AC (concorrencia, session_id origem, resposta vazia, prompt
  injection) registrados em `## Open Questions`.

## Grupo US1 - Ana (Colaboradora)

Persona primaria, 9 stories (8 originais + US1.9 Iniciar nova conversa).

### US1.1 - Consultar politicas gerais de RH

**Como** Ana, **quero** perguntar em portugues sobre politicas gerais de RH,
**para** obter uma resposta clara sem abrir o `employee_handbook.pdf`.

- **Prioridade**: Must Have
- **Mapeia**: FR1.1, FR1, NFR1.1, NFR2.1
- **INVEST**: Independente, Negociavel, Valiosa, Estimavel, Small, Testavel
  (com par (pergunta canonica, ancoras) a ser definido em `functional-design`).

**Acceptance criteria**:

- **AC1.1.1**: **Given** Ana esta no Streamlit com sessao iniciada, **when**
  ela digita uma pergunta sobre uma politica geral coberta pelo
  `employee_handbook.pdf`, **then** o chatbot responde em portugues em menos
  de 5 segundos com resposta derivada de trechos do documento (par (pergunta,
  ancoras esperadas) sera definido em `functional-design`). [NFR1.1, NFR2.1]
- **AC1.1.2**: **Given** a pergunta esta coberta pela KB, **when** a resposta
  e renderizada, **then** ela e derivada de trechos do
  `employee_handbook.pdf` via `retrieve`, e nao expoe dados individuais de
  nenhum funcionario. [FR5.2, NFR4.1]
- **AC1.1.3**: **Given** a resposta e renderizada, **when** Ana ve a bolha do
  assistente, **then** o texto e texto plano em portugues, sem citacao
  explicita do documento fonte na UI (desvio consciente documentado em
  `wireframes.md`). [FR7.1, FR7.2]
- **AC1.1.4**: **Given** Ana envia a pergunta, **when** a chamada ao agente
  esta em execucao, **then** a bolha do assistente sendo formada exibe o
  spinner "Consultando base de conhecimento..." ate a resposta chegar (nova
  AC atendendo objecao de design sobre estado "aguardando resposta"). [FR4.3]

### US1.2 - Consultar politica de ferias

**Como** Ana, **quero** perguntar sobre regras de ferias e afastamentos,
**para** planejar minhas ferias sem precisar contatar o time de RH.

- **Prioridade**: Must Have
- **Mapeia**: FR1.2, NFR1.1, NFR2.1

**Acceptance criteria**:

- **AC1.2.1**: **Given** Ana esta no Streamlit, **when** ela pergunta sobre
  ferias (par (pergunta canonica, ancoras) a definir em `functional-design`),
  **then** o chatbot retorna resposta derivada do `leave_policy.pdf` em
  portugues em <5s. [FR1.2, NFR1.1, NFR2.1]
- **AC1.2.2**: **Given** a pergunta e sobre um cenario coberto pelo documento,
  **when** a resposta e gerada, **then** o valor factual (dias, prazos,
  regras) coincide com o documento oficial (validado via smoke test com
  ancoras esperadas definidas em `functional-design`). [FR1.2]

### US1.3 - Consultar feriados da empresa

**Como** Ana, **quero** consultar os feriados da empresa, **para** planejar
folgas e organizar minha agenda.

- **Prioridade**: Must Have
- **Mapeia**: FR1.5, NFR1.1, NFR2.1

**Acceptance criteria**:

- **AC1.3.1**: **Given** Ana esta no Streamlit, **when** ela pergunta sobre
  feriados (par (pergunta, ancoras esperadas) a definir em
  `functional-design`), **then** o chatbot retorna resposta derivada do
  `public_holidays.csv` em portugues em <5s. [FR1.5, NFR1.1]

### US1.4 - Fallback "nao encontrei essa informacao"

**Como** Ana, **quero** que o chatbot admita quando nao encontra a resposta,
**para** eu saber que preciso contatar o RH em vez de receber uma resposta
inventada.

- **Prioridade**: Should Have
- **Mapeia**: FR5.2, NFR4.1

**Acceptance criteria**:

- **AC1.4.1**: **Given** Ana pergunta algo que nao esta coberto por nenhum
  dos 5 documentos, **when** o agente processa a pergunta, **then** a
  resposta contem o token "RH" e uma keyword de negativa entre
  {"nao encontrei", "nao posso", "nao consegui localizar"}, e o agente
  **nao** inventa informacao (contrato ancora mecanicamente verificavel;
  substitui "ou equivalente semantico"). [FR5.2]
- **AC1.4.2**: **Given** a resposta e o fallback, **when** ela e renderizada,
  **then** e apresentada como uma bolha normal do assistente (nao um erro).
  [FR7.1]

### US1.5 - Recusa de perguntas sobre dados individuais (LGPD)

**Como** empresa, **quero** que o chatbot recuse perguntas sobre dados
individuais de qualquer colaborador (salario, historico pessoal), **para**
manter a conformidade com LGPD.

- **Prioridade**: Must Have
- **Mapeia**: FR5, NFR4.1, NFR4.2, NFR8.2

**Acceptance criteria**:

- **AC1.5.1**: **Given** Ana pergunta "Qual o salario do Joao Silva?" (ou
  variacao envolvendo dado individual nominal), **when** o agente processa
  a pergunta, **then** a resposta **nao** contem substring correspondente a
  valores monetarios do trecho retornado por `retrieve` (contrato ancora:
  regex de valor em BRL ausente na resposta), nem repete o nome individual
  como sujeito do dado. [NFR4.1, NFR8.2]
- **AC1.5.2**: **Given** a pergunta e sobre dados individuais, **when** a
  resposta e gerada, **then** ela contem o token "RH" e uma keyword de
  recusa entre {"nao posso compartilhar", "nao posso divulgar",
  "informacao pessoal"} (contrato ancora mecanicamente verificavel). [FR5, NFR4.1]
- **AC1.5.3**: **Given** o teste de guardrail LGPD executado com um stub
  de `retrieve` que retorna o trecho canonico ficticio
  `"Joao Silva - Salario mensal: R$ 15.000,00 - Cargo: Analista Pleno"`,
  **when** o agente gera a resposta, **then** a resposta **nao** repete
  "R$ 15.000,00" nem "15.000" verbatim. Valor e nome ficticios canonicos
  fixados aqui para consistencia entre execucoes. **Nota de tensao**: se o
  `BedrockModel` for mockado, este teste vira "teste de fiacao" (inspeciona
  system prompt aplicado, nao output); se `BedrockModel` for real, o teste
  toca AWS e vira integracao/smoke (viola team-practices §Testing Posture).
  Decisao a resolver em `functional-design` (opcao a) unitario com mock do
  modelo + AC1.5.4 separado para output real via smoke, ou opcao b) unico
  teste integrado no `scripts/smoke.py`). [NFR8.2]

### US1.6 - Input maior que 4000 caracteres rejeitado com aviso

**Como** Ana, **quero** ser avisada quando minha pergunta e longa demais,
**para** eu reformular em vez de disparar uma chamada que falharia.

- **Prioridade**: Must Have
- **Mapeia**: FR8.1, FR8.2

**Acceptance criteria**:

- **AC1.6.1**: **Given** Ana cola no input um texto com mais de 4000
  caracteres, **when** ela pressiona Enter, **then** o frontend Streamlit
  mostra o aviso `st.warning("Sua pergunta ficou muito longa para eu
  processar. Tente resumir em uma unica pergunta mais curta.")` e **nao**
  chama `invoke_agent_runtime` (redacao ajustada por design). [FR8.1, FR8.2]
- **AC1.6.2**: **Given** Ana envia um input com 4000 caracteres ou menos,
  **when** ela pressiona Enter, **then** a pergunta segue normalmente para o
  agente. [FR8.1]

### US1.7 - Erro do AgentCore renderizado como mensagem amigavel

**Como** Ana, **quero** receber uma mensagem clara quando o agente falha,
**para** eu tentar novamente ou contatar o RH sem ser exposta a stack trace.

- **Prioridade**: Must Have
- **Mapeia**: FR9.1, FR9.2, FR9.3

**Acceptance criteria**:

- **AC1.7.1**: **Given** Ana faz uma pergunta, **when** o
  `invoke_agent_runtime` retorna um `ClientError` (throttling, timeout, IAM
  ou similar), **then** o `src/invoke.py` captura e re-eleva como
  `AgentInvocationError`. [FR9.1]
- **AC1.7.2**: **Given** o `frontend/app.py` recebe um `AgentInvocationError`,
  **when** ele renderiza, **then** exibe `st.error("Nao consegui responder
  agora. Tente novamente em alguns segundos ou contate o RH se o problema
  persistir.")` **sem** stack trace (redacao ajustada por design). [FR9.2]
- **AC1.7.3**: **Given** um erro ocorre, **when** o frontend renderiza a
  mensagem amigavel, **then** o `ClientError` original e registrado via
  `logging.getLogger(__name__)` para debug local. [FR9.3]

### US1.9 - Iniciar nova conversa

*(Renumerado: era US1.8 no draft; agora US1.8 foi movida para grupo US4
com persona P4 Operador conforme triagem.)*

**Como** Ana, **quero** limpar a conversa atual e comecar uma nova sessao,
**para** fazer perguntas de assunto diferente sem contaminar com contexto
anterior.

- **Prioridade**: Must Have (novo, atende gap de FR4.5 sinalizado por
  design e developer)
- **Mapeia**: FR4.5, NFR3.1, NFR3.2

**Acceptance criteria**:

- **AC1.9.1**: **Given** Ana esta em uma sessao com historico de mensagens,
  **when** ela abre a sidebar, **then** ela ve o botao "Limpar conversa"
  visivel. [FR4.5, wireframes.md Q1]
- **AC1.9.2**: **Given** Ana clica em "Limpar conversa", **when** o handler
  executa, **then** um novo `session_id` e gerado via `uuid.uuid4()` no
  frontend. [FR4.5, NFR3.2, project.md § Mandated]
- **AC1.9.3**: **Given** o clique em "Limpar conversa" ocorreu, **when** o
  Streamlit renderiza, **then** `st.session_state.messages` esta zerado
  (`[]`) e o historico de bolhas anteriores nao e mais visivel. [FR4.5]
- **AC1.9.4**: **Given** a sessao foi zerada, **when** Ana faz a proxima
  pergunta, **then** a chamada ao AgentCore Runtime usa o novo `session_id`
  e a sessao roda em microVM isolada da anterior (garantia do servico).
  [NFR3.1, FR3.2]
- **AC1.9.5**: **Given** uma sessao nova foi iniciada, **when** o Streamlit
  renderiza o estado inicial, **then** aparece a bolha unica de saudacao do
  assistente ("Ola! Sou o assistente de RH. Posso ajudar com politicas de
  RH, ferias, onboarding e avaliacoes. Qual sua duvida?"). [wireframes.md
  § Estados, atende objecao de design sobre estado inicial sem AC]

## Grupo US2 - Bruno (Novo Funcionario)

Sub-persona, 1 story.

### US2.1 - Consultar processo de onboarding

**Como** Bruno, **quero** perguntar sobre o processo e o checklist de
onboarding, **para** entender rapidamente o que preciso fazer nos primeiros
dias sem depender exclusivamente do padrinho.

- **Prioridade**: Must Have
- **Mapeia**: FR1.3, NFR1.1, NFR2.1

**Acceptance criteria**:

- **AC2.1.1**: **Given** Bruno esta no Streamlit, **when** ele pergunta
  sobre onboarding (par (pergunta canonica, ancoras) a definir em
  `functional-design`), **then** o chatbot retorna resposta derivada do
  `onboarding_checklist.pdf` em portugues em <5s. [FR1.3, NFR1.1, NFR2.1]
- **AC2.1.2**: **Given** a pergunta e sobre um item explicito do checklist,
  **when** a resposta e gerada, **then** ela reflete os passos/prazos
  descritos (validacao via smoke test com ancoras esperadas). [FR1.3]

## Grupo US3 - Carla (Gestora)

Sub-persona, 1 story.

### US3.1 - Consultar diretrizes de avaliacao de desempenho

**Como** Carla, **quero** consultar as diretrizes de avaliacao de desempenho,
**para** conduzir 1:1s e ciclos de feedback alinhados ao processo formal.

- **Prioridade**: Must Have
- **Mapeia**: FR1.4, NFR1.1, NFR2.1

**Acceptance criteria**:

- **AC3.1.1**: **Given** Carla esta no Streamlit, **when** ela pergunta
  sobre avaliacao de desempenho (par (pergunta, ancoras) a definir em
  `functional-design`), **then** o chatbot retorna resposta derivada do
  `performance_review_guidelines.pdf` em portugues em <5s. [FR1.4, NFR1.1]
- **AC3.1.2**: **Given** Carla pergunta sobre desempenho de um colaborador
  especifico nominal (ex.: "como o Joao esta indo?"), **when** o agente
  processa, **then** o comportamento e o mesmo de AC1.5: recusa dados
  individuais e redireciona ao RH. [NFR4.1, cross-ref US1.5]

## Grupo US4 - Operador (Time tecnico do workshop)

Nova persona P4, 1 story (era US1.8 no draft anterior).

### US4.1 - Trocar modelo de chat via sidebar

**Como** Operador (time tecnico), **quero** escolher o modelo de chat via
seletor na sidebar, **para** comparar qualidade e latencia entre pelo menos
2 modelos durante a demo.

- **Prioridade**: Must Have
- **Mapeia**: FR4.4, FR6.1, FR6.2, FR6.3

**Acceptance criteria**:

- **AC4.1.1**: **Given** o Operador esta no Streamlit, **when** ele abre a
  sidebar, **then** ele ve um dropdown "Modelo de chat" com pelo menos 2
  opcoes (ex.: Claude Haiku 4.5 e Amazon Nova Pro). [FR4.4]
- **AC4.1.2**: **Given** o Operador seleciona um modelo diferente no
  dropdown, **when** ele envia a proxima pergunta, **then** o agente inclui
  o `model_id` selecionado como campo estruturado no output final (ou no
  payload da chamada ao AgentCore Runtime), verificavel por inspecao da
  resposta ou do log da chamada (contrato de observabilidade explicito;
  substitui "observacao de estilo"). [FR6.1]
- **AC4.1.3**: **Given** um modelo com prefixo `us.*` esta selecionado,
  **when** o agente invoca o modelo, **then** o codigo do agente resolve
  o inference profile ARN correspondente (ARN comeca com
  `arn:aws:bedrock:...:inference-profile/`) e passa-o ao `BedrockModel` do
  Strands (assertion positiva: verifica prefixo do ARN, nao apenas ausencia
  de excecao). [FR6.2, project.md § Mandated]
- **AC4.1.4**: **Given** o Operador troca o modelo mid-sessao, **when** o
  Streamlit renderiza o proximo turno, **then** `st.session_state.messages`
  preserva o historico anterior e o proximo turno usa o novo modelo
  (mapeamento corrigido de FR4.5 para FR4.1). [FR4.1, FR6.1]

## Story Dependencies

Ordem sugerida de construcao (risk-first, conforme `scope-document.md`):

- **US1.1, US1.2, US1.3, US2.1, US3.1** (cobertura funcional) dependem de
  FR2 (KB indexada) + FR3 (agente rodando) prontos primeiro.
- **US1.4** (fallback) e **US1.5** (recusa LGPD) dependem do system prompt
  (FR5) aplicado.
- **US1.6** (input >4000) depende de FR8 (guard em `src/invoke.py`).
- **US1.7** (erro AgentCore) depende de FR9 (error policy) implementada.
- **US1.6 e US1.7** compartilham o mesmo `try/except` em `frontend/app.py`;
  podem ser implementadas em paralelo em um mesmo commit.
- **US1.9** (limpar conversa) depende de FR4.4 (sidebar) + FR4.5.
- **US4.1** (troca de modelo) depende de FR4.4 (sidebar) + FR6.1 (config
  dinamica) + FR6.2 (inference profile ARN). Demonstravel apos as
  cobertura funcional estar no ar.
- **Pre-condicao operacional para todas**: FR2.2 (`StartIngestionJob`
  executado antes da demo). Sem isso, `retrieve` retorna vazio e todas as
  10 stories aparentam quebradas mesmo com codigo correto.

## INVEST Notes

Todas as 11 stories foram avaliadas contra INVEST:

- **Independent**: cada story demonstravel isoladamente.
- **Negotiable**: redacao das respostas ajustavel via system prompt sem
  quebrar acceptance criteria.
- **Valuable**: consultas entregam valor imediato; robustez entrega
  confianca; troca de modelo entrega experimentacao.
- **Estimable**: cada story cabe em 30-90 min na janela de 2 dias (com
  US4.1 no limite superior, US1.6 no inferior).
- **Small**: menor unidade util para demo funcional.
- **Testable**: todas com AC BDD verificaveis via smoke test (NFR8.3) e/ou
  teste unitario (NFR8.2). AC de consulta funcional (5) tem par (pergunta,
  ancoras) deferido a `functional-design`.

## Assumptions & Open Questions

Registrado para `functional-design` considerar:

- **Assertion anchors dos AC de consulta** (AC1.1.1, AC1.2.1, AC1.3.1,
  AC2.1.1, AC3.1.1): definir pares `(pergunta canonica, ancoras esperadas)`
  com base no conteudo real dos 5 documentos, para viabilizar assertion no
  `scripts/smoke.py`. Sem ancoras, o smoke degenera para health check.
- **US1.5 AC1.5.3 - decisao unitario vs integracao**: se `BedrockModel` for
  mockado, teste vira "teste de fiacao" (system prompt aplicado); se real,
  vira integracao/smoke (viola `team-practices § Testing Posture`).
  Resolver antes de `code-generation`.
- **AC4.1.2 - contrato de observabilidade do model_id**: confirmar em
  `contract-design` o formato exato (campo estruturado no output do agente,
  ou inspecao do payload). O envelope default do `invoke_agent_runtime` nao
  retorna `modelId`; o agente precisa incluir.
- **Concorrencia (NFR6.1) sem AC**: sem cenario testavel de 3 sessoes
  simultaneas com `session_id` distintos. Considerar smoke test dedicado
  em `build-and-test` ou registrar como limitacao aceita.
- **Origem server-side do `session_id` (NFR3.2) sem AC dedicada**: US1.9
  cobre indiretamente via AC1.9.2, mas nao ha AC afirmando que a assinatura
  publica nao aceita `session_id` externo. Considerar em `functional-design`.
- **FR9.1 resposta vazia sem AC**: AC1.7.1 cobre `ClientError` mas nao
  cobre resposta 200 OK com payload sem texto. Comportamento indefinido -
  precisa decisao em `functional-design` (retornar fallback do
  `_ClientError` ou renderizar bolha vazia).
- **Prompt injection via documento indexado**: NFR4.1 depende de system
  prompt bypass-vulneravel. Sem AC no MVP; Bedrock Guardrails e recomendado
  em `team-practices.md § Deployment` mas nao Mandated. Se aparecer
  documento adversarial na KB, comportamento nao coberto.
- **Latencia mediana vs single-shot (NFR1.1)**: AC dos AC de consulta pedem
  "<5s". Sem definir mediana, cold start unico pode falhar. Considerar
  medir 3x/pergunta no `scripts/smoke.py` e afirmar mediana.

## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-08-24T17:24:57Z
**Iteration:** 2
**Review class:** advisory

**Findings:**

- Recovery pass motivado pela re-gravacao de `user-stories-assessment.md`. O diff material em relacao a iteracao 1 e restrito a esse arquivo, e e cosmético/curatorial:
  - Secao `## Rationale` agora reconhece a persona P4 Operador introduzida na triagem mob (linha "Uma quarta persona (P4 Operador) foi introduzida na triagem mob para separar troca de modelo do consumo do bot.").
  - Secao `## Factors Considered` atualizou "persona primaria com 2 sub-personas" para "uma persona primaria com 2 sub-personas de cenario + 1 persona operacional" — consistente com `personas.md`.
  - Secao `## Key Areas Where Stories Add the Most Value` acrescentou dois bullets: "Experimentacao de modelo (FR6): story dedicada ao Operador" e "Iniciar nova conversa (FR4.5): story dedicada com AC cobrindo botao, `session_id` novo via `uuid.uuid4()`, historico zerado e isolamento de sessao" — cobre US4.1 e US1.9 explicitamente.
  - A decisao (Execute) e o rationale principal permanecem inalterados. Nenhum criterio de sensor (`required-sections`, `upstream-coverage`, `traceability`) e afetado.
- Verificacao cruzada com os artefatos nao modificados desde iteracao 1:
  - `stories.md`: 11 stories (US1.1-1.7, US1.9, US2.1, US3.1, US4.1), 28 ACs em BDD, IDs `AC{group}.{story-seq}.{n}` estaveis. Nada mudou. Continua aderente.
  - `personas.md`: 4 personas (P1 Ana, P2 Bruno, P3 Carla, P4 Operador) com Papel/Objetivos/Dores/Contexto e priority ranking. Nada mudou. Assessment agora bate com o que ja estava em personas.md desde iteracao 1.
  - `traceability.json`: 19 upstream_ids (FR1-FR9, NFR1-NFR10) todos com linha de cobertura; targets `OK` apontam para US existentes; `Deferred` nomeia estagio downstream; unico `N/A` (NFR9) justificado por `constraint-register.md CN-3`. Nada mudou.
  - Os tres arquivos de contribuicao mob (design/developer/quality) permanecem com identity marker na primeira linha.
- Reafirmacao dos 13 criterios: todos continuam atendidos com a mesma evidencia da iteracao 1; o realinhamento do assessment com a realidade dos outros artefatos so reforca criterio (5) (4 personas) e criterio (9) (ajustes da triagem cobertos) — nao introduz regressao.

**Suggestions:**

- **Todas as Suggestions da iteracao 1 permanecem validas** (INVEST inline por story, cobertura FR4.2 na traceability, refactor da nota de tensao de AC1.5.3, ancoragem de AC4.1.2 ao `contract-design`, estado inicial de saudacao sem AC dedicado, latencia mediana vs single-shot no smoke test). Nao vou repeti-las item a item; nada foi endereçado nesta re-gravacao (era esperado — o escopo era apenas curatorial no assessment).
- **Nova sugestao editorial (baixa prioridade)**: a linha do assessment "**Iniciar nova conversa** (FR4.5): story dedicada..." nao cita o ID `US1.9` explicitamente, embora o dispatch tenha mencionado que o refinamento "mentions US1.9". Se a intencao era criar ancora navegavel de assessment→stories, vale acrescentar o ID entre parenteses ("story dedicada (US1.9)"). Puramente cosmetico; nao bloqueia.


