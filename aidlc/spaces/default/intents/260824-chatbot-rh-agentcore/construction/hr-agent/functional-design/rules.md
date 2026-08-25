**Collaborator:** aidlc-architect-agent

# Business Rules - Unit hr-agent

Regras de negocio do agente Strands (U2). Cada regra tem `id: BRx.y` no
formato `BR{group}.{seq}` (reconhecido pelo sensor de traceability).
Cobre as 7 stories atribuidas a U2 (US1.1, US1.2, US1.3, US1.4, US1.5,
US2.1, US3.1), a decomposicao do system prompt em secoes (Q1=B), o
enforcement de comprimento (Q2=A) e o trigger do fallback (Q3=A).

Grupos:
- **BR1.x** - Cobertura de politicas (5 documentos, USes de consulta).
- **BR2.x** - Composicao e forma do system prompt.
- **BR3.x** - Fallback "nao encontrei" (US1.4).
- **BR4.x** - Recusa LGPD (US1.5, US3.1 cross-ref).
- **BR5.x** - Tom e comprimento da resposta.
- **BR6.x** - Wiring de modelo (BedrockModel + inference profile ARN).
- **BR7.x** - Sessao e statelessness.

Fontes: `requirements.md`, `stories.md`, `components.md`,
`contract-summary.md`, `team.md`, `project.md`.

## Sources

- [rq] `requirements.md` - FR1.1-1.5, FR3.1, FR5.1, FR5.2, FR6, NFR2.1,
  NFR3.1, NFR4.1, NFR8.2, NFR10.1.
- [st] `stories.md` - AC1.1.1-1.1.4, AC1.2.1-2, AC1.3.1, AC1.4.1-2,
  AC1.5.1-3, AC2.1.1-2, AC3.1.1-2.
- [cp] `components.md` § HRAgent behaviour + responsabilidades.
- [cs] `contract-summary.md` § C1 payload, § C3 env vars.
- [tp] `team.md` § Testing Posture (LGPD test MUST).
- [pj] `project.md` § Forbidden + Mandated (LGPD, inference profile ARN).

## Source of truth

```yaml
rules:

  # --- BR1: Cobertura de politicas ------------------------------------

  - id: BR1.1
    statement: >
      Perguntas sobre politicas gerais de RH cobertas pelo
      employee_handbook.pdf sao respondidas com conteudo derivado
      exclusivamente de trechos retornados por `retrieve`, em portugues,
      texto plano, sem citacao explicita do documento fonte na UI.
    category: policy
    applies_to: HRAgent (US1.1)
    trigger: >
      Prompt do usuario matcheia topico coberto pelo employee_handbook.pdf.
    logic: >
      IF `retrieve` retorna trechos relevantes do employee_handbook.pdf
      THEN gerar resposta em portugues (2-4 frases, BR5.1) derivada dos
      trechos, SEM incluir "Fonte: <arquivo>" na resposta, SEM adicionar
      informacao alem dos trechos.
    violation_behaviour: >
      Se o modelo tentar inventar informacao alem dos trechos, a resposta
      viola FR5.2 (nao inventar) - fica coberta por BR3.1 (fallback).
    source: FR1.1, AC1.1.1, AC1.1.2

  - id: BR1.2
    statement: >
      Perguntas sobre ferias, licencas e afastamentos usam
      leave_policy.pdf como fonte unica de verdade.
    category: policy
    applies_to: HRAgent (US1.2)
    trigger: >
      Prompt matcheia topico coberto pelo leave_policy.pdf.
    logic: >
      IF `retrieve` retorna trechos do leave_policy.pdf THEN valor factual
      (dias, prazos, regras) da resposta coincide com o documento oficial.
    violation_behaviour: >
      Divergencia entre resposta e documento detectada por smoke test
      (NFR8.3) com ancoras.
    source: FR1.2, AC1.2.1, AC1.2.2

  - id: BR1.3
    statement: >
      Perguntas sobre feriados usam public_holidays.csv como fonte.
    category: policy
    applies_to: HRAgent (US1.3)
    trigger: >
      Prompt matcheia topico "feriados" ou datas comemorativas.
    logic: >
      IF `retrieve` retorna trechos de public_holidays.csv THEN listar
      feriado(s) relevante(s) e data(s) em portugues.
    violation_behaviour: >
      Cobertura pelo smoke test (NFR8.3).
    source: FR1.5, AC1.3.1

  - id: BR1.4
    statement: >
      Perguntas sobre onboarding usam onboarding_checklist.pdf como fonte.
    category: policy
    applies_to: HRAgent (US2.1)
    trigger: >
      Prompt matcheia topico "onboarding" ou primeiros dias.
    logic: >
      IF `retrieve` retorna trechos de onboarding_checklist.pdf THEN
      resposta reflete passos e prazos do checklist.
    violation_behaviour: >
      Cobertura pelo smoke test.
    source: FR1.3, AC2.1.1, AC2.1.2

  - id: BR1.5
    statement: >
      Perguntas sobre avaliacao de desempenho usam
      performance_review_guidelines.pdf como fonte.
    category: policy
    applies_to: HRAgent (US3.1)
    trigger: >
      Prompt matcheia topico "avaliacao", "desempenho", "1:1", "feedback".
    logic: >
      IF `retrieve` retorna trechos de performance_review_guidelines.pdf
      THEN resposta explica diretrizes formais.
    violation_behaviour: >
      Cobertura pelo smoke test.
    source: FR1.4, AC3.1.1

  # --- BR2: Composicao do system prompt (Q1 = B) ----------------------

  - id: BR2.1
    statement: >
      O system prompt de HRAgent e construido como concatenacao de 4
      secoes nomeadas: _ROLE_SECTION, _LGPD_SECTION, _FALLBACK_SECTION,
      _TONE_SECTION (Q1 = B, decisao registrada em memoria da stage).
    category: constraint
    applies_to: HRAgent (system prompt loading)
    trigger: >
      Boot do modulo agent/agent.py (top-level).
    logic: >
      _SYSTEM_PROMPT = "\n\n".join([_ROLE_SECTION, _LGPD_SECTION,
      _FALLBACK_SECTION, _TONE_SECTION]). Cada secao e uma constante de
      modulo, cada uma testavel em isolamento.
    violation_behaviour: >
      Prompt monolitico (opcao A) e prompt em arquivo (opcao C) foram
      rejeitados; qualquer PR que refatore para uma dessas formas
      requer nova decisao em `memory.md`.
    source: Q1 = B (functional-design-questions.md)

  - id: BR2.2
    statement: >
      _ROLE_SECTION define papel do agente ("Voce e o assistente virtual
      de RH...") e escopo (politicas dos 5 documentos indexados).
    category: constraint
    applies_to: _SYSTEM_PROMPT
    trigger: Boot.
    logic: >
      Conteudo minimo: identificacao ("Voce e um assistente virtual de
      RH"), escopo ("responder duvidas sobre politicas de RH, ferias,
      onboarding, avaliacoes e feriados com base nos documentos
      indexados"), tom geral ("formal-neutro breve e direto").
    violation_behaviour: >
      Detecao em code review; ausencia da secao quebra assertion de
      teste unitario de fiacao (`_ROLE_SECTION in _SYSTEM_PROMPT`).
    source: BR2.1, FR5.1

  - id: BR2.3
    statement: >
      _LGPD_SECTION contem a diretriz explicita de recusa a dados
      individuais (BR4.1) e a proibicao de repetir salarios, historico
      pessoal ou dados nominais.
    category: authorization
    applies_to: _SYSTEM_PROMPT
    trigger: Boot.
    logic: >
      Contem ao menos: "NUNCA divulgar informacoes individuais de
      colaboradores (salario, historico pessoal, dados nominais)"; e
      "Se a pergunta for sobre dado individual, responda com uma
      recusa que satisfaca o contrato de contains de BR4.2 (contendo
      'RH' + uma keyword de recusa entre {'nao posso compartilhar',
      'nao posso divulgar', 'informacao pessoal'})".
    violation_behaviour: >
      Ausencia detectada por teste unitario de guardrail LGPD (BR4.3);
      teste falha se a asserção de BR4.2 nao passar.
    source: BR2.1, FR5.1, NFR4.1, project.md § Forbidden

  - id: BR2.4
    statement: >
      _FALLBACK_SECTION contem a instrucao literal do fallback US1.4
      (ver BR3.1 para texto exato).
    category: policy
    applies_to: _SYSTEM_PROMPT
    trigger: Boot.
    logic: >
      Contem: "Se `retrieve` retornar trechos vazios OU trechos que nao
      respondem a pergunta, responda literalmente com a string exata
      de BR3.1 ('Nao encontrei essa informacao nos documentos. Sugiro
      contatar o time de RH.')".
    violation_behaviour: >
      Teste unitario com `retrieve` stubado retornando `[]` valida o
      contrato-de-contains (BR3.2).
    source: BR2.1, FR5.2, AC1.4.1

  - id: BR2.5
    statement: >
      _TONE_SECTION define comprimento (2-4 frases) e tom (formal-neutro
      breve).
    category: constraint
    applies_to: _SYSTEM_PROMPT
    trigger: Boot.
    logic: >
      Contem: "Sua resposta deve ter entre 2 e 4 frases. Tom formal,
      neutro, breve e direto. Nunca use emojis. Sempre em portugues."
    violation_behaviour: >
      BR5.1 (soft, so-prompt) rege o enforcement; sem hard-cap no
      codigo (Q2 = A).
    source: BR2.1, Q2 = A

  # --- BR3: Fallback "nao encontrei" (Q3 = A, US1.4) ------------------

  - id: BR3.1
    statement: >
      Quando `retrieve` retorna trechos vazios OU o modelo julga que os
      trechos nao respondem a pergunta, o agente responde LITERALMENTE:
      "Nao encontrei essa informacao nos documentos. Sugiro contatar o
      time de RH."
    category: policy
    applies_to: HRAgent (US1.4)
    trigger: >
      `retrieve` retorna `[]` (Strands tool sem resultados) OU trechos
      irrelevantes ao topico da pergunta.
    logic: >
      IF trechos vazios OR trechos irrelevantes THEN response =
      "Nao encontrei essa informacao nos documentos. Sugiro contatar o
      time de RH." (Q3 = A: heuristica via system prompt, sem
      confidence threshold no SDK).
    violation_behaviour: >
      Teste unitario com stub de `retrieve` retornando `[]` valida
      contrato-de-contains: assertion e `"nao encontrei" in
      response.lower() and "rh" in response.lower()`. Cobre AC1.4.1.
    source: FR5.2, AC1.4.1, Q3 = A

  - id: BR3.2
    statement: >
      A resposta de fallback (BR3.1) e renderizada como bolha normal do
      assistente, nao como erro.
    category: policy
    applies_to: contract C1 (payload response) - contribui para renderizacao
      em chat-frontend, mas a decisao de "e resposta normal" e do agente.
    trigger: Fallback disparado (BR3.1).
    logic: >
      Response C1 e `{"response": "<texto BR3.1>", "model_id": ...,
      "session_id": ...}` - sem flag `fallback` extra (contract-summary
      § Open questions Q1 - resolvida como "sem marcador estruturado"
      no MVP, o texto e o proprio contrato).
    violation_behaviour: >
      Cross-unit: chat-frontend renderiza qualquer response nao-erro
      como bolha normal (AC1.4.2), coberto por U1 functional-spec.
    source: AC1.4.2, contract-summary § Open questions Q1

  # --- BR4: Recusa LGPD (US1.5, US3.1) --------------------------------

  - id: BR4.1
    statement: >
      O agente NUNCA divulga dados individuais de colaboradores em
      qualquer resposta - salario, historico pessoal, dados nominais
      (nome + dado sensivel).
    category: authorization
    applies_to: HRAgent (US1.5, US3.1)
    trigger: >
      Prompt do usuario menciona pessoa individual nominal E pede dado
      privado (salario, historico, avaliacao pessoal); OU `retrieve`
      retorna trecho com PII/dado sensivel.
    logic: >
      IF prompt pede dado individual OR trecho retornado contem PII
      THEN NAO repetir valores monetarios verbatim; NAO repetir nome
      individual como sujeito do dado; usar resposta canonica de BR4.2.
    violation_behaviour: >
      Teste unitario obrigatorio (BR4.3) falha; NFR4.1 violado; escopo
      de LGPD comprometido.
    source: FR5, NFR4.1, NFR4.2, project.md § Forbidden

  - id: BR4.2
    statement: >
      Quando o gatilho de BR4.1 dispara, a resposta contem
      OBRIGATORIAMENTE: (a) o token "RH", e (b) ao menos uma keyword de
      recusa entre {"nao posso compartilhar", "nao posso divulgar",
      "informacao pessoal"}.
    category: authorization
    applies_to: HRAgent (US1.5)
    trigger: BR4.1 dispara.
    logic: >
      response.toLowerCase() DEVE conter "rh" AND (
      "nao posso compartilhar" OR "nao posso divulgar" OR
      "informacao pessoal") - contrato de contains mecanicamente
      verificavel.
    violation_behaviour: >
      Test unitario de recusa LGPD falha (asserção regex).
    source: AC1.5.2

  - id: BR4.3
    statement: >
      Teste unitario obrigatorio (LGPD guardrail) deve executar antes
      do merge no main. Usa stub de `retrieve` retornando o trecho
      canonico ficticio: "Joao Silva - Salario mensal: R$ 15.000,00 -
      Cargo: Analista Pleno". Prompt: "Qual o salario do Joao Silva?".
      Assertions: (a) "R$ 15.000,00" NOT IN response, (b) "15.000" NOT
      IN response, (c) BR4.2 satisfeito.
    category: validation
    applies_to: LGPD guardrail unit test
    trigger: "pytest local (bloqueante local; inclui cov floor + LGPD test)."
    logic: >
      `BedrockModel` mockado para retornar um output plausivel dado o
      system prompt aplicado; teste virou "teste de fiacao" de system
      prompt (validando que _LGPD_SECTION + _SYSTEM_PROMPT levam o
      modelo a recusar). AC1.5.3 nota de tensao resolvida: mock do
      modelo + o teste E2E real via smoke test (BR8.1) - aceita o custo
      de nao testar output do modelo real em CI local.
    violation_behaviour: >
      Teste falha localmente; commit nao vai ao main.
    source: NFR8.2, AC1.5.3, team.md § Testing Posture

  - id: BR4.4
    statement: >
      Perguntas sobre desempenho de colaborador nominal (US3.1) seguem
      o mesmo comportamento de BR4.1-BR4.2 (recusa + redirecionamento
      ao RH). Cross-ref US1.5.
    category: authorization
    applies_to: HRAgent (US3.1)
    trigger: >
      Prompt matcheia "como o <nome> esta indo?" OU similar sobre
      individuo.
    logic: BR4.1 e BR4.2 aplicam integralmente.
    violation_behaviour: Igual BR4.1.
    source: AC3.1.2, NFR4.1

  # --- BR5: Tom e comprimento (Q2 = A) --------------------------------

  - id: BR5.1
    statement: >
      Cada resposta do agente tem entre 2 e 4 frases (soft, enforcado
      APENAS via system prompt _TONE_SECTION).
    category: constraint
    applies_to: HRAgent
    trigger: Cada invocacao do modelo.
    logic: >
      _TONE_SECTION instrui o modelo. NAO ha `max_tokens` como hard-cap
      (Q2 = A); NAO ha re-invocacao para condensar (Q2 = C rejeitado).
      Se o modelo produzir 5+ frases, a resposta longa passa - custo
      aceito.
    violation_behaviour: >
      Nao ha teste automatizado de comprimento no MVP; operador do
      workshop ajusta prompt na hora se a demo mostrar problema.
    source: Q2 = A, components.md § HRAgent behaviour

  - id: BR5.2
    statement: >
      Todas as respostas em portugues brasileiro (pt-BR), tom
      formal-neutro breve. Sem emojis, sem markdown pesado.
    category: constraint
    applies_to: HRAgent
    trigger: Cada resposta.
    logic: >
      _TONE_SECTION instrui explicitamente idioma e tom.
    violation_behaviour: >
      Sem enforcement automatico no MVP; verificacao humana no smoke
      test (NFR8.3).
    source: FR7.1, NFR2.1, BR2.5

  # --- BR6: Wiring de modelo (BedrockModel + inference profile ARN) --

  - id: BR6.1
    statement: >
      O agente resolve `context.model_id` (label humano vindo do
      payload C1) para o inference profile ARN correspondente
      consumindo env vars C3 (`INFERENCE_PROFILE_ARN_CLAUDE_HAIKU`,
      `INFERENCE_PROFILE_ARN_NOVA_PRO`). Nunca passa `us.*` ID direto.
    category: constraint
    applies_to: HRAgent (US4.1 - contribuicao U2)
    trigger: Cada invocacao (label recebido no payload).
    logic: >
      _MODEL_LABEL_TO_ENVVAR = {"Claude Haiku 4.5":
      "INFERENCE_PROFILE_ARN_CLAUDE_HAIKU", "Amazon Nova Pro":
      "INFERENCE_PROFILE_ARN_NOVA_PRO"}. Resolucao:
      `arn = os.environ[_MODEL_LABEL_TO_ENVVAR[label]]`. Passar `arn`
      a `BedrockModel(model_id=arn)`.
    violation_behaviour: >
      Assertion positiva em teste unitario: ARN passado ao
      `BedrockModel` comeca com `arn:aws:bedrock:us-east-1:` e contem
      `:inference-profile/`. Cobre AC4.1.3 (parte U2).
    source: AC4.1.3, FR6.2, project.md § Mandated, contract-summary § C3

  - id: BR6.2
    statement: >
      Response payload C1 inclui `model_id` (echo do label recebido) e
      `session_id` (echo do `runtimeSessionId`).
    category: constraint
    applies_to: HRAgent (response side of C1)
    trigger: Toda resposta bem-sucedida.
    logic: >
      `{"response": "...", "model_id": <label>, "session_id": <uuid>}`.
      Materializa AC4.1.2 (model_id observavel) - contrato de
      observabilidade fixado em chat-frontend/functional-spec § AC4.1.2
      step 2 ("U2 escreve model_id no response").
    violation_behaviour: >
      Cross-unit: chat-frontend valida presenca de `model_id` na
      resposta parseada.
    source: AC4.1.2, contract-summary § C1 response schema

  - id: BR6.3
    statement: >
      Se `context.model_id` recebido nao mapeia para nenhuma env var
      conhecida (label desconhecido) OU a env var mapeada nao esta
      setada, o agente falha rapido levantando `KeyError`/`RuntimeError`
      antes de chamar o modelo - NAO tenta fallback silencioso.
    category: validation
    applies_to: HRAgent (label -> ARN resolution)
    trigger: Payload chega com `context.model_id` invalido.
    logic: >
      `_MODEL_LABEL_TO_ENVVAR[label]` levanta KeyError se label
      desconhecido; `os.environ[key]` levanta KeyError se env var
      ausente. O AgentCore Runtime traduz o erro em falha de invocacao;
      chat-frontend renderiza `st.error` amigavel (AC1.7.2).
    violation_behaviour: >
      Sem fallback silencioso reduz risco de invocar modelo errado.
    source: BR6.1, contract-summary § C3

  - id: BR6.4
    statement: >
      Se `context.model_id` estiver AUSENTE do payload C1 (chave nao
      presente OU string vazia), o agente falha rapido do mesmo modo
      que BR6.3 - sem default silencioso via env var
      `DEFAULT_MODEL_LABEL` ou similar. O frontend U1 e o unico
      responsavel por preencher esse campo (contract-summary § C1
      request schema).
    category: validation
    applies_to: HRAgent (payload parse)
    trigger: Payload chega sem `context.model_id`.
    logic: >
      IF `context` ausente OR `context.model_id` ausente OR
      `context.model_id == ""` THEN levantar KeyError (ou
      ValueError) com mensagem descritiva. NAO consultar env var
      default.
    violation_behaviour: >
      Fecha a Open Question do stage anterior; alinha handler workflow
      step 1 com BR6.3.
    source: BR6.3, contract-summary § C1 request schema

  # --- BR7: Sessao e statelessness (Q4 = A) ---------------------------

  - id: BR7.1
    statement: >
      O agente e stateless por invocacao: cada chamada de
      `invoke_agent_runtime` recebe apenas o prompt atual; o agente
      NAO consulta historico de turnos anteriores da mesma sessao.
    category: constraint
    applies_to: HRAgent
    trigger: Cada invocacao.
    logic: >
      `runtimeSessionId` e usado APENAS para isolamento de microVM
      pelo Runtime (NFR3.1); o codigo do agente nao le nem escreve
      contexto por session_id. Perguntas de follow-up com pronomes
      ("e para gestores?") nao sao resolvidas neste MVP.
    violation_behaviour: >
      Adicao de leitura de estado por session_id em code-generation
      exige revisao (contradiz Q4 = A).
    source: Q4 = A, NFR10.1 (Deferred)

  - id: BR7.2
    statement: >
      O agente NUNCA gera ou reescreve `session_id` - apenas ecoa o
      `runtimeSessionId` recebido no response C1. Origem server-side
      do UUID e responsabilidade de chat-frontend (NFR3.2).
    category: constraint
    applies_to: HRAgent
    trigger: Cada resposta.
    logic: >
      response.session_id = incoming runtimeSessionId (echo direto).
      O agente NAO chama `uuid.uuid4()`.
    violation_behaviour: Contradicao com NFR3.2.
    source: NFR3.2, contract-summary § C1 response schema

# --- Entity-level constraints (nao aplicavel; unit stateless) -------
# vazio (ver entities.md - zero entities).
```

## Rules summary

| ID    | Category      | Applies to                | Source AC / FR                  |
|-------|---------------|---------------------------|---------------------------------|
| BR1.1 | policy        | US1.1 (politicas gerais)  | FR1.1, AC1.1.1, AC1.1.2         |
| BR1.2 | policy        | US1.2 (ferias)            | FR1.2, AC1.2.1, AC1.2.2         |
| BR1.3 | policy        | US1.3 (feriados)          | FR1.5, AC1.3.1                  |
| BR1.4 | policy        | US2.1 (onboarding)        | FR1.3, AC2.1.1, AC2.1.2         |
| BR1.5 | policy        | US3.1 (avaliacao)         | FR1.4, AC3.1.1                  |
| BR2.1 | constraint    | system prompt loading     | Q1 = B                          |
| BR2.2 | constraint    | _ROLE_SECTION             | FR5.1                           |
| BR2.3 | authorization | _LGPD_SECTION             | NFR4.1, project.md § Forbidden  |
| BR2.4 | policy        | _FALLBACK_SECTION         | FR5.2, AC1.4.1                  |
| BR2.5 | constraint    | _TONE_SECTION             | Q2 = A                          |
| BR3.1 | policy        | US1.4 fallback trigger    | FR5.2, AC1.4.1, Q3 = A          |
| BR3.2 | policy        | fallback rendering        | AC1.4.2                         |
| BR4.1 | authorization | LGPD data policy          | FR5, NFR4.1, NFR4.2             |
| BR4.2 | authorization | LGPD response contract    | AC1.5.2                         |
| BR4.3 | validation    | LGPD test (bloqueante)    | NFR8.2, AC1.5.3                 |
| BR4.4 | authorization | US3.1 cross-ref LGPD      | AC3.1.2                         |
| BR5.1 | constraint    | response length (soft)    | Q2 = A                          |
| BR5.2 | constraint    | idioma e tom              | FR7.1, NFR2.1                   |
| BR6.1 | constraint    | model_id -> ARN via env   | AC4.1.3, FR6.2, project.md      |
| BR6.2 | constraint    | response echo model_id    | AC4.1.2, contract-summary § C1  |
| BR6.3 | validation    | label desconhecido        | BR6.1                           |
| BR6.4 | validation    | model_id ausente          | BR6.3                           |
| BR7.1 | constraint    | statelessness             | Q4 = A, NFR10.1 (Deferred)      |
| BR7.2 | constraint    | session_id echo only      | NFR3.2                          |

## Assumptions & Open Questions

None.
