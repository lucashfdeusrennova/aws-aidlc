# Domain Design - Perguntas

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit."
- [scope] Workflow-selected scope: `mvp`.
- [rq] `requirements.md` - FR1-FR9, NFR1-NFR10.
- [st] `stories.md` - 11 stories.
- [tp] `team-practices.md` - fronteiras de camada `frontend/ -> src/ -> boto3`, `agent/` isolado.

## Contexto

As fronteiras de camada ja foram afirmadas em `team-practices.md § Code Style`:

- `agent/` roda **dentro** do AgentCore Runtime (microVM gerenciada), auto-contido, importa apenas `strands`, `strands_tools` e `boto3`. **Nunca** importa de `src/` ou `frontend/`.
- `src/` e a cola de invocacao (cliente boto3 do `bedrock-agentcore`), nao conhece Streamlit nem o codigo interno do agente.
- `frontend/app.py` depende de `src/` (`from src.invoke import ask_agent`). Nunca o inverso.

Isso ja pre-define 3 componentes candidatos. As perguntas abaixo apenas confirmam o refinamento.

## Q1. Decomposicao de componentes

Quantos componentes distintos capturamos em `components.md`?

- A. 3 componentes: `HRChatFrontend` (Streamlit), `AgentInvoker` (cliente boto3), `HRAgent` (Strands + tool retrieve). Espelha as 3 fronteiras de camada de `team-practices.md` 1:1.
- B. 2 componentes: `HRChatApp` (frontend + invoker fundidos - "aplicacao de chat local") + `HRAgent`. Fica mais compacto se o invoker for so 1 funcao.
- C. 4 componentes: A + separar `KnowledgeBaseRetriever` (a tool retrieve do agente) como componente proprio.
- X. Other (please specify)

[Answer]: A

## Q2. Escopo do componente `HRAgent`

O `HRAgent` inclui explicitamente:

- A. Apenas a construcao do agente Strands + system prompt + tool `retrieve` do Strands SDK. A tool `retrieve` e dependencia externa (Bedrock Knowledge Base + S3 Vectors), nao entity/atributo do componente.
- B. Como A, mais um "SystemPrompt" como entity de configuracao capturada explicitamente (identifier: id textual do prompt; attributes: `regras_lgpd`, `fallback_text`, `tom`).
- X. Other (please specify)

[Answer]: A

## Q3. Entities do domain

Qual conjunto de entities capturamos (nivel ownership + shape, sem tipo/validacao)?

- A. Minimo: `ChatMessage` (owned by `HRChatFrontend`; identifier: `session_id + index`; attributes: `role`, `content`), `ChatSession` (owned by `HRChatFrontend`; identifier: `session_id`; attributes: `session_id`, `messages`, `model_id`). Suficiente para MVP.
- B. Como A + `ModelChoice` (owned by `HRChatFrontend`; identifier: `label`; attributes: `label`, `inference_profile_arn`) para representar o dicionario `MODEL_ARNS`.
- C. Como B + `AgentInvocationError` (owned by `AgentInvoker`; identifier: `error_code`; attributes: `error_code`, `message`, `original_client_error`) como entity de erro de dominio.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]: B

## Q4. Estilo de interacao entre componentes

- A. Todas `sync` (chamada de funcao Python bloqueante). O `st.spinner` cuida do feedback. Consistente com AgentCore Runtime chamada single-shot (nao streaming) no MVP.
- B. Chamada Streamlit -> AgentInvoker `sync`; AgentInvoker -> AgentCore Runtime `sync` mas com timeout explicito documentado; AgentCore Runtime -> KB `sync` interno do Strands.
- X. Other (please specify)

[Answer]: AA

## Q5. Cross-component dependency de erro (`AgentInvocationError`)

Se Q3 = C (capturar `AgentInvocationError` como entity de dominio):

- A. `AgentInvoker` **define e possui**; `HRChatFrontend` apenas **consome** (catch + `st.error`). Assimetrico: `AgentInvocationError` aparece em `entities` do `AgentInvoker` e em `references` do `HRChatFrontend`.
- B. Idem A + adicionar `ValueError` do guard >4000 chars como parte da mesma entity de erro. Simplifica, mas mistura input-validation error com invocation error.
- C. N/A porque Q3 nao selecionou C.

[Answer]: CA


## Assumption Confirmation

Nenhuma assuncao nova alem das ja fixadas em `requirements.md`, `stories.md` e `team-practices.md`. As respostas Q1-Q5 foram propostas pelo agente como defaults MVP e confirmadas pelo humano ("Nao quero que me retorne essas perguntas na tela, quero que sugira como antes").

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumo consolidado das decisoes deste stage:

- 3 componentes: `HRChatFrontend`, `AgentInvoker`, `HRAgent` (Q1=A).
- `HRAgent` sem `SystemPrompt` como entity (Q2=A).
- Entities: `ChatSession`, `ChatMessage`, `ModelChoice` (Q3=B).
- Todas as interacoes `sync` (Q4=A).
- `AgentInvocationError` como excecao Python idiomatica, nao entity (Q5=C via ADR-002).
- 5 ADRs em `decisions.md`; 11 stories rastreadas em `traceability.json`.

Artefatos produzidos:
- `components.md`
- `decisions.md`
- `traceability.json`

[Answer]: Looks correct
