**Collaborator:** aidlc-design-agent

# Refined Mockups - Chatbot de RH com Bedrock AgentCore

Refina os wireframes de `wireframes.md` para especificacao de UI concreta,
mapeando cada acceptance criterion de `stories.md` para o widget Streamlit
correspondente + estado + copy exata. Consumido por Domain Design e Code
Generation.

Fontes consumidas: `wireframes.md` (layout), `user-flow.md` (transicoes),
`stories.md` (11 stories, 28 ACs), `requirements.md` (FR/NFR),
`team-practices.md` (stack e restricoes de codigo).

## Sources

- [wf] `wireframes.md` - layout ASCII, componentes visiveis, estados.
- [uf] `user-flow.md` - passos do happy path, desvios e limpeza de sessao.
- [st] `stories.md` - 11 stories (US1.1-US1.9, US2.1, US3.1, US4.1) com
  28 ACs em BDD.
- [rq] `requirements.md` - FR1-FR9 e NFR1-NFR10.
- [tp] `team-practices.md` - stack Streamlit + Python 3.12 + fronteiras
  de camada (`frontend/ -> src/ -> boto3`).
- [q1] Q1 (refined-mockups-questions.md) = A - tom breve e direto,
  formal-neutro.
- [q2] Q2 = A - Streamlit padrao, sem tema customizado.
- [q3] Q3 = D - adota contador `{n}/4000` acima de 3500 chars **e**
  indicador de modelo no cabecalho.
- [q4] Q4 = A - WCAG 2.1 AA como checklist referencial, sem certificacao.

## Tela unica - Assistente Virtual de RH

O MVP tem uma unica pagina. Layout confirma o wireframe [wf], adicionando
o indicador de modelo no cabecalho [q3] e o contador de caracteres no
input [q3].

```text
+----------------------------------------------------------------------------+
|                                                                            |
|  [SIDEBAR]                    | Assistente Virtual de RH                   |
|                               | Modelo em uso: Claude Haiku 4.5            |
|                               |                                            |
|  Modelo de chat               | +----------------------------------------+ |
|  +--------------------------+ | | [assistant] Ola! Sou o assistente de   | |
|  | Claude Haiku 4.5      v  | | | RH. Posso ajudar com politicas de RH,  | |
|  +--------------------------+ | | ferias, onboarding e avaliacoes. Qual  | |
|                               | | sua duvida?                            | |
|  [ Limpar conversa      ]     | +----------------------------------------+ |
|                               |                                            |
|  ----                         | +----------------------------------------+ |
|  Feedback                     | | [user] Quantos dias de ferias tenho    | |
|  Consultando base de          | |        direito por ano?                | |
|  conhecimento...              | +----------------------------------------+ |
|  (aparece durante             |                                            |
|   invoke_agent_runtime)       | +----------------------------------------+ |
|                               | | [assistant] O colaborador tem direito  | |
|                               | | a 30 dias de ferias anuais apos 12     | |
|                               | | meses de trabalho continuo, podendo    | |
|                               | | ser divididos em ate 3 periodos.       | |
|                               | +----------------------------------------+ |
|                               |                                            |
|                               | +----------------------------------------+ |
|                               | | Pergunte sobre politicas de RH...  [>] | |
|                               | +----------------------------------------+ |
|                               |                              3520/4000     |
|                               |                                            |
+----------------------------------------------------------------------------+
```

Rodape do input mostra o contador **apenas quando** o texto passa de 3500
caracteres (regra [q3] combinada com o guard de 4000 do FR8.1).

## Mockup por User Story

### US1.1 / US1.2 / US1.3 / US2.1 / US3.1 - Consulta a documento

Cinco stories compartilham o mesmo padrao de UI (RAG textual). Diferem
apenas na pergunta e no documento fonte. AC comum: latencia <5s
[rq NFR1.1], resposta em portugues [rq NFR2.1], spinner enquanto processa
[st AC1.1.4].

**Componente**: bolha do assistente (`st.chat_message("assistant")`).
**Estado inicial**: apos envio da pergunta, adicionar bolha vazia com
spinner. **Estado final**: substituir por texto plano em portugues, tom
breve e direto [q1] (2 a 4 frases, formal-neutro).

**Copy do spinner** (ancorado em [wf][st AC1.1.4]):

```
Consultando base de conhecimento...
```

**Copy da saudacao inicial** (ancorado em [wf][st AC1.9.5]):

```
Ola! Sou o assistente de RH. Posso ajudar com politicas de RH, ferias,
onboarding e avaliacoes. Qual sua duvida?
```

**Tom da resposta [q1]**: o system prompt do agente carrega a diretriz
"Responda em portugues, em 2 a 4 frases, sem parafrasear a fonte alem do
necessario. Cite a regra ou politica em texto plano, sem link nem link
explicito para o documento". A UI nao renderiza citacao [rq FR7.2].

### US1.4 - Fallback "nao encontrei"

**Componente**: bolha normal do assistente (nao um erro) [st AC1.4.2].
**Copy sugerida** (contrato: contem "RH" + keyword de negativa) [st AC1.4.1]:

```
Nao encontrei essa informacao nos documentos da base de conhecimento.
Sugiro contatar o time de RH.
```

Renderiza no mesmo componente das respostas normais, mesma bolha, mesmo
estilo. Sem cor de erro. Alinhado com [uf § Pergunta fora da base de
conhecimento].

### US1.5 - Recusa LGPD

**Componente**: bolha normal do assistente [st AC1.5.2].
**Copy sugerida** (contrato: contem "RH" + keyword de recusa entre
{"nao posso compartilhar", "nao posso divulgar", "informacao pessoal"})
[st AC1.5.2]:

```
Nao posso compartilhar informacao pessoal sobre colaboradores especificos.
Politicas gerais eu posso explicar. Para dados individuais, procure o RH.
```

Copy nao repete o nome individual como sujeito do dado [st AC1.5.1]. O
teste unitario NFR8.2 confere que valores monetarios nao aparecem [st
AC1.5.3].

### US1.6 - Input >4000 chars

**Componente**: `st.warning(...)` renderizado logo acima da bolha do
usuario que **nao foi enviada** [st AC1.6.1][rq FR8.2].
**Copy exata** (ancorada em [st AC1.6.1]):

```
Sua pergunta ficou muito longa para eu processar. Tente resumir em uma
unica pergunta mais curta.
```

**Contador progressivo [q3]**: um `st.caption(...)` alinhado a direita
sob o `st.chat_input`, visivel apenas quando `len(prompt) > 3500`, com
o formato `{n}/4000`. Cor default do Streamlit (cinza). Nao alarga o
input. Some assim que `len(prompt) <= 3500` novamente. Nao bloqueia digitacao;
a rejeicao acontece no submit, conforme AC1.6.1.

### US1.7 - Erro do AgentCore

**Componente**: `st.error(...)` renderizado no lugar da bolha do
assistente que seria formada [st AC1.7.2][rq FR9.2].
**Copy exata** (ancorada em [st AC1.7.2]):

```
Nao consegui responder agora. Tente novamente em alguns segundos ou
contate o RH se o problema persistir.
```

Bolha do usuario (que disparou a chamada) permanece visivel no historico.
Stack trace nao aparece [st AC1.7.2]. Log do `ClientError` fica em
`logging.getLogger(__name__)` [st AC1.7.3].

### US1.9 - Iniciar nova conversa (limpar)

**Componente**: `st.button("Limpar conversa", key="clear_chat")` na
sidebar [st AC1.9.1][wf].
**Interacao**:
- Ao clicar, o handler executa:
  1. `st.session_state.session_id = str(uuid.uuid4())` [st AC1.9.2].
  2. `st.session_state.messages = []` [st AC1.9.3].
  3. `st.rerun()`.
- Apos rerun, o chat renderiza somente a bolha de saudacao inicial [st
  AC1.9.5][wf § Estados].

**Sem confirmacao intermediaria** (nao ha modal "Tem certeza?"): dentro
do escopo MVP e da janela de 2 dias, um clique acidental so custa recomecar
a conversa; o valor de um confirm dialog nao compensa o atrito.

### US4.1 - Trocar modelo de chat (Operador)

**Componente**: `st.selectbox("Modelo de chat", options=MODELS,
key="model_id")` na sidebar [st AC4.1.1][wf].
**Options iniciais** (pelo menos 2 [st AC4.1.1]):

```
["Claude Haiku 4.5", "Amazon Nova Pro"]
```

O rotulo humano visivel mapeia para o inference profile ARN correspondente
via dicionario `MODEL_ARNS` no `frontend/app.py` [st AC4.1.3]. O ARN e
passado ao payload da chamada `invoke_agent_runtime`.

**Indicador de modelo no cabecalho [q3][st AC4.1.2]**: logo abaixo do
`st.title("Assistente Virtual de RH")`, um `st.caption(f"Modelo em uso:
{st.session_state.model_id}")`. Atualiza reativamente a cada mudanca no
selectbox.

**Preservacao de historico [st AC4.1.4]**: trocar o modelo **nao** limpa
`st.session_state.messages` nem o `session_id`. Somente a proxima chamada
usa o novo modelo. Consistente com [uf § Trocar modelo de chat].

## Mapa AC -> Widget Streamlit

Mapeia cada AC de `stories.md` para o widget que o realiza. Serve como
contrato de entrada para `functional-design` e `code-generation`.

| AC       | Widget / Local                                                  | Estado / Copy                                  |
| -------- | --------------------------------------------------------------- | ---------------------------------------------- |
| AC1.1.1  | `st.chat_message("assistant")` em `frontend/app.py`             | Texto plano PT, <5s                            |
| AC1.1.2  | System prompt do agente em `agent/agent.py`                     | Nao renderiza dados individuais                |
| AC1.1.3  | Bolha assistente                                                | Texto plano, sem citacao fonte                 |
| AC1.1.4  | `st.chat_message("assistant")` + `st.spinner("Consultando...")` | Spinner enquanto `invoke_agent_runtime` roda   |
| AC1.2.1  | idem AC1.1.1                                                    | Fonte `leave_policy.pdf`                       |
| AC1.3.1  | idem AC1.1.1                                                    | Fonte `public_holidays.csv`                    |
| AC1.4.1  | Bolha assistente (nao erro)                                     | Contem "RH" + keyword negativa                 |
| AC1.4.2  | `st.chat_message("assistant")`                                  | Mesma bolha das respostas normais              |
| AC1.5.1  | Bolha assistente                                                | Sem substring de valor BRL                     |
| AC1.5.2  | Bolha assistente                                                | Contem "RH" + keyword de recusa                |
| AC1.5.3  | Teste unitario (NFR8.2)                                         | Nao verbatim em resposta gerada                |
| AC1.6.1  | `st.warning(...)`                                               | "Sua pergunta ficou muito longa..."            |
| AC1.6.2  | Fluxo normal                                                    | Segue para `invoke_agent_runtime`              |
| AC1.7.1  | Camada `src/invoke.py`                                          | Re-raise como `AgentInvocationError`           |
| AC1.7.2  | `st.error(...)`                                                 | "Nao consegui responder agora..."              |
| AC1.7.3  | Logger em `frontend/app.py`                                     | `logger.error(...)` do `ClientError` original  |
| AC1.9.1  | `st.button("Limpar conversa")` na sidebar                       | Visivel                                        |
| AC1.9.2  | Handler do botao                                                | `st.session_state.session_id = uuid.uuid4()`   |
| AC1.9.3  | Handler do botao                                                | `st.session_state.messages = []`               |
| AC1.9.4  | Proxima chamada `invoke_agent_runtime`                          | Usa novo `session_id`                          |
| AC1.9.5  | Render pos-rerun                                                | Bolha unica de saudacao                        |
| AC2.1.1  | idem AC1.1.1                                                    | Fonte `onboarding_checklist.pdf`               |
| AC2.1.2  | Bolha assistente                                                | Reflete passos do checklist                    |
| AC3.1.1  | idem AC1.1.1                                                    | Fonte `performance_review_guidelines.pdf`      |
| AC3.1.2  | Bolha assistente (via US1.5)                                    | Redireciona ao RH                              |
| AC4.1.1  | `st.selectbox("Modelo de chat")` sidebar                        | 2+ opcoes                                      |
| AC4.1.2  | `st.caption(f"Modelo em uso: {...}")` cabecalho                 | Atualiza a cada troca; `model_id` observavel   |
| AC4.1.3  | `MODEL_ARNS` dict + payload                                     | ARN comeca com `arn:aws:bedrock:...:inference-profile/` |
| AC4.1.4  | `st.session_state.messages` preservado                          | Historico continua; proximo turno usa novo modelo |

## Estados agregados

Estados da tela como maquina de estados (fecha a lacuna do [wf § Estados]):

- **Idle / Inicial**: `st.session_state.messages == [<saudacao>]`,
  input habilitado, sem spinner, sem contador (n <= 3500), sem indicador
  de erro.
- **Digitando**: usuario com foco no `st.chat_input`. Se
  `len(prompt_atual) > 3500`, o contador `{n}/4000` aparece; se
  `len(prompt_atual) > 4000`, o `st.warning` de US1.6 sera disparado no
  submit.
- **Enviando**: apos submit valido, `st.session_state.messages` recebe
  a bolha do usuario e uma bolha do assistente com spinner
  "Consultando base de conhecimento...". Input **habilitado**
  (comportamento default do Streamlit; nao ha requisito para desabilitar).
- **Resposta OK**: a bolha do assistente substitui o spinner pelo texto
  final. Historico rola ate o final.
- **Resposta Fallback** (US1.4): identica a "Resposta OK" com texto de
  fallback; nao usa estilo de erro.
- **Recusa LGPD** (US1.5): identica a "Resposta OK" com texto de recusa.
- **Erro** (US1.7): a bolha do assistente e substituida por `st.error`;
  bolha do usuario permanece.
- **Sessao nova** (US1.9): apos `st.rerun`, retorna ao estado Idle com
  novo `session_id`.

Modelo trocado (US4.1) e ortogonal aos estados acima: ocorre a qualquer
momento e afeta apenas a proxima chamada.

## Alinhamento com team-practices

- **Fronteira de camada** [tp]: o wireframe atende ao invariante
  `frontend/ -> src/ -> boto3`. O selectbox, o botao "Limpar", o
  contador e a captura de erros vivem em `frontend/app.py`. A geracao de
  `session_id` (via `uuid.uuid4()`) tambem, respeitando NFR3.2.
- **Sem estado externo**: toda a UI trabalha sobre `st.session_state`;
  nao ha banco, cache Redis, cookie ou localStorage. Alinhado a
  [rq NFR6.1] (1 a 3 sessoes).
- **Localizacao PT-BR** [tp][rq NFR2.1]: toda copy renderizada esta em
  portugues. Nomes de tokens tecnicos (`session_id`, `model_id`) vivem
  apenas em variaveis, nao na UI.

## Assumptions & Open Questions

None.

<!-- confirmed 2026-08-24 -->

## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-08-24
**Iteration:** 1
**Review class:** advisory

### Findings

| # | Severity | Location | Finding | Recommendation |
|---|---|---|---|---|
| 1 | Minor | mockups.md § "Mapa AC -> Widget Streamlit" | O mapa cobre 27 dos 28 ACs de `stories.md`, mas **AC1.2.2** (par (dias, prazos, regras) de ferias coincide com o `leave_policy.pdf`, validado via smoke com ancoras) nao aparece explicitamente. Semelhante em espirito a AC1.1.2/AC2.1.2/AC3.1.2, que aparecem como linha propria. | Adicionar linha `AC1.2.2 | Bolha assistente / smoke test com ancoras (deferido a functional-design) | Valor factual bate com leave_policy.pdf`, ou uma nota de rodape agrupando AC1.1.2, AC1.2.2, AC2.1.2, AC3.1.2 sob "ancoras de fidelidade fatica deferidas". Nao bloqueia; o smoke test ja e o contrato downstream. |
| 2 | Minor | mockups.md § "Tela unica" (wireframe ASCII, rodape do input com `3520/4000`) vs interaction-spec.md § C7 / design-system-mapping.md § DS-9 | O wireframe ASCII do `mockups.md` mostra `3520/4000` **abaixo do `st.chat_input`** implicando contador **ao vivo durante a digitacao**. Ja `interaction-spec.md § C7` e `design-system-mapping.md § DS-9` documentam explicitamente que `st.chat_input` nao expoe o valor durante digitacao e adotam **Opcao A - reativo ao submit**. Um leitor que so olhe o wireframe pode achar que o contador atualiza em keystroke. | Adicionar uma linha logo abaixo do wireframe ASCII: "O `3520/4000` aparece **apenas apos o submit** e apenas quando 3500 < len(prompt) <= 4000 - vide interaction-spec.md § C7 (Opcao A)". Ou substituir `3520/4000` por `Sua pergunta teve 3520/4000 caracteres. Considere ser mais direta.` para casar visualmente com o snippet do C7. |
| 3 | Minor | mockups.md § "US1.6 - Input >4000 chars" ("Rodape do input mostra o contador **apenas quando** o texto passa de 3500 caracteres") | Mesmo tema do #2: essa frase, isolada, sugere contador ao vivo por caracter digitado, conflitando com a decisao Opcao A ja registrada em interaction-spec.md. | Reescrever para: "Rodape do input mostra o contador apos o submit **apenas quando** o ultimo prompt ficou entre 3501 e 4000 caracteres (Opcao A, interaction-spec.md § C7). Nao ha contador ao vivo por keystroke - limitacao consciente do `st.chat_input`." |
| 4 | Minor | design-system-mapping.md § DS-9 (copy do caption) vs mockups.md § "Tela unica" (formato `{n}/4000`) | O caption em DS-9 e no snippet de C7 usa `"Sua pergunta teve {n}/4000 caracteres. Considere ser mais direta."` enquanto o wireframe ASCII exibe simplesmente `3520/4000`. Duas copys de contador convivem no stage sem uma escolha canonica. | Fixar **uma unica** copy (recomendo a do C7/DS-9, que ja e acionavel WCAG 3.3.3) e atualizar o ASCII do wireframe para refletir a mesma string, ou explicitar que `3520/4000` no wireframe e "forma abreviada meramente ilustrativa". |
| 5 | Minor | accessibility-checklist.md § 1.4.10 Reflow | Texto misto no mesmo item: marcado como `[Streamlit default]` mas conclui com "***embora nao seja testado nesta demo***". Se nao foi testado, e mais honesto marcar como `[Manual]` ou `[Gap]` consciente, alinhado a como 1.4.3 e 1.4.11 ja foram tratados. | Reclassificar 1.4.10 como `[Manual]` com nota "reflow ate 320px nao testado nesta demo; padrao Streamlit reflua, mas nao foi validado". |

### Verificacao dos 6 pontos do dispatch

- **(1) AC -> widget**: 27/28 mapeados; unico gap e AC1.2.2 (finding #1, cosmetico).
- **(2) Copy literal**: TODAS as strings ancoradas conferem literalmente com stories.md - saudacao US1.9 AC1.9.5, warning US1.6 AC1.6.1, error US1.7 AC1.7.2. As copys de fallback (US1.4) e recusa (US1.5) atendem ao **contrato de contains** definido em AC1.4.1 (contem "RH" + "nao encontrei") e AC1.5.2 (contem "RH" + "nao posso compartilhar" + "informacao pessoal") - nao ha copy literal exigida por esses AC, so contrato de substrings, e ambas as copys propostas satisfazem.
- **(3) Q2=A respeitado**: design-system-mapping.md explicitamente rejeita `unsafe_allow_html`, `st.components.v1.html` e tema custom; DS-2 rejeita `st.badge` justamente porque exigiria HTML custom. Nenhum widget contrabandeia CSS. Conforme.
- **(4) WCAG 2.1 AA + gaps conscientes**: checklist completo (1.1 a 4.1), gaps explicitos (`lang="pt-BR"`, ausencia de certificacao formal, contraste sem verificacao numerica) todos ancorados em [q4 A]. Conforme, sujeito ao ajuste do finding #5.
- **(5) team-practices**: fronteira `frontend/ -> src/ -> boto3` reafirmada em mockups.md § "Alinhamento com team-practices" e em interaction-spec.md § "Alinhamento com team-practices" ("nenhum componente listado importa `boto3`"). Nenhuma lib proibida citada (LangChain/FastAPI/React etc). Python 3.12 herdado implicitamente via [tp]; nenhum snippet quebra 3.12. Conforme.
- **(6) upstream-coverage**: os 4 artefatos deste stage carregam `## Sources` referenciando **wireframes.md, user-flow.md, stories.md, requirements.md, team-practices.md** (mockups.md tags [wf][uf][st][rq][tp]; interaction-spec.md tags [wf][uf][st][rq][tp]; design-system-mapping.md tags [wf][uf][st][rq][tp]; accessibility-checklist.md tags [wf][uf][st][rq][tp]). Todos os 5 upstreams presentes em todos os 4 outputs. Conforme.

### Suggestions (nao bloqueantes)

- **S1**: A "Opcao B - trocar para `st.text_area` + `st.button`" em interaction-spec.md § C7 esta bem registrada como caminho pos-demo. Se o contador ao vivo se tornar requisito real, essa Opcao B tambem quebra o wireframe atual e o layout de DS-8. Vale registrar em `refined-mockups` a nota "adotar Opcao B exige revisao de wireframe + DS-8 + DS-9" para evitar surpresa em `code-generation`.
- **S2**: interaction-spec.md § C7 usa `f"Sua pergunta teve {len(prompt)}/4000 caracteres..."` mas o snippet de C8 nao mostra a chamada de C7. Como C7 e "post-submit" e C8 e "post-submit", vale um comentario em C8 apontando "apos processar prompt, se `3500 < len(prompt) <= 4000` renderizar caption de C7" para casar as duas mecanicas.
- **S3**: accessibility-checklist.md § 2.4.2 e § 3.1.1 ambos recomendam `st.set_page_config(page_title=..., page_icon=..., layout="centered")` para code-generation. Como sao **duas** recomendacoes ao mesmo componente, vale consolidar em uma unica linha em `## Pendencias para code-generation` (ja existe) e retirar a recomendacao inline nos criterios (deixar so o veredito por criterio). Reduz risco de code-generation implementar duas vezes ou uma so.
- **S4**: mockups.md § "US4.1" cita `MODEL_ARNS: dict[str, str]` como dicionario de mapeamento rotulo->ARN mas nao mostra a **forma** do valor esperado. AC4.1.3 exige prefixo `arn:aws:bedrock:...:inference-profile/`. Um comentario inline `# ex.: "Claude Haiku 4.5": "arn:aws:bedrock:us-east-1:...:inference-profile/us.anthropic.claude-haiku-4-5-..."` ancoraria o teste de AC4.1.3 sem esperar por `contract-design`.

### Summary

Os quatro artefatos do stage estao consistentes, ancorados em fontes upstream, respeitam Q1-Q4 e a fronteira de camada de team-practices, e cobrem 27/28 ACs de stories.md com widget nomeado, estado e copy exata. As copys criticas (saudacao US1.9, warning US1.6, erro US1.7) batem literalmente; fallback US1.4 e recusa US1.5 satisfazem os contratos de contains. Achados sao todos Minor e concentram-se em uma unica area cosmetica: o contador de caracteres aparece **ao vivo no wireframe** mas **so post-submit** na spec de interacao/design-system - uma unificacao de copy e uma nota explicativa resolvem. Como advisory, verdict e READY; findings vao ao gate de aprovacao para o humano decidir se pedir Request Changes antes de avancar para functional-design.
