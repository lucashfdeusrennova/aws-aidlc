# User Flow - Chatbot de RH com Bedrock AgentCore

Fluxo principal (happy path) e desvios do MVP definido em
`scope-document.md` e detalhado em `intent-backlog.md`. Rastreia ao
`intent-statement.md` (fronteira de produto).

## Happy path

```text
+------------------+     +--------------+     +--------------------+
| Colaborador      | --> | Streamlit UI | --> | AgentCore Runtime  |
| digita pergunta  |     | (localhost)  |     | (invoke_agent_...) |
+------------------+     +--------------+     +--------------------+
                                                        |
                                                        v
                                              +--------------------+
                                              | Strands Agent      |
                                              | (tool: retrieve)   |
                                              +--------------------+
                                                        |
                                                        v
                                              +--------------------+
                                              | Knowledge Base     |
                                              | (S3 Vectors)       |
                                              +--------------------+
                                                        |
                                                        v
                                              +--------------------+
                                              | Model (Bedrock)    |
                                              | gera resposta      |
                                              +--------------------+
                                                        |
                                                        v
+------------------+     +--------------+     +--------------------+
| Colaborador ve   | <-- | Streamlit UI | <-- | Resposta retorna   |
| resposta em pt   |     | renderiza    |     | ao frontend        |
+------------------+     +--------------+     +--------------------+
```

## Passos do fluxo principal

1. Colaborador abre `http://localhost:8501` no navegador (form factor
   desktop, [Q4]).
2. Streamlit renderiza a saudacao inicial e o input de chat esta focado.
3. Colaborador digita uma pergunta em portugues (ex.: "Quantos dias de
   ferias tenho por ano?") e envia com Enter.
4. Streamlit adiciona a bolha do usuario ao historico e monta uma bolha
   vazia de assistente com o spinner "Consultando base de conhecimento...".
5. Streamlit chama `agentcore_client.invoke_agent_runtime(...)` com o
   `session_id` da sessao atual (UUID por sessao) e o payload contendo a
   pergunta.
6. AgentCore Runtime inicia sessao isolada (microVM); Strands Agent recebe
   o prompt e decide usar a tool `retrieve`.
7. Tool `retrieve` faz busca semantica na Knowledge Base (Bedrock KB + S3
   Vectors), retorna trechos relevantes dos documentos de RH.
8. Strands Agent gera resposta em portugues usando os trechos + prompt de
   sistema (com regra "sem dados individuais", [scope-document.md]).
9. Resposta retorna ao Streamlit em menos de 5s por resposta (NFR de
   latencia do `intent-statement.md`).
10. Streamlit renderiza a resposta na bolha de assistente e adiciona ao
    `st.session_state.messages` para historico.
11. Colaborador le a resposta; pode digitar nova pergunta na mesma sessao
    (historico preservado por `session_id`).

## Desvios do fluxo

### Erro em qualquer etapa

Se `invoke_agent_runtime` falhar (timeout, throttling, resposta vazia,
erro de IAM, indisponibilidade de servico), a UI mostra uma bolha de
assistente com mensagem amigavel: "Nao consegui responder agora. Tente
reformular ou contate o RH." Sem stack trace visivel. O erro tecnico
completo fica no log do Streamlit para debug. [Q3]

### Trocar modelo de chat

Colaborador (ou operador da demo) seleciona outro modelo no dropdown da
sidebar (item [Q1] D). A troca afeta o proximo `invoke_agent_runtime`; nao
requer redeploy do agente (basta o agente ler a env/parametro de modelo).
Historico da sessao atual e preservado; o proximo turno usa o novo modelo.
[Q1][intent-backlog.md B-5]

Nota: modelos com prefixo `us.*` precisam ser referenciados via inference
profile no codigo do agente (risco R-4 do `raid-log.md`).

### Limpar conversa / nova sessao

Colaborador clica em "Limpar conversa" na sidebar. Streamlit:
- Gera novo `session_id` (UUID)
- Zera `st.session_state.messages`
- Renderiza a saudacao inicial novamente

A nova sessao no AgentCore Runtime rodara em microVM isolada (garantia da
plataforma); nao ha vazamento de contexto da sessao anterior. [Q1]

### Pergunta fora da base de conhecimento

Se a KB nao retornar trechos relevantes, o prompt de sistema orienta o
agente a responder que nao encontrou a informacao e sugerir contatar o RH.
Nao inventa resposta. [intent-statement.md - regra "NAO invente informacoes"
no exemplo de codigo do `tech-env.md`, refletida no prompt de sistema]

### Nao mostra fonte na UI

Conforme decidido em [Q2 C], o documento fonte nao aparece na resposta ao
colaborador. O agente usa a KB internamente para gerar a resposta correta,
mas nao imprime a referencia. Desvio consciente do criterio "Rastreabilidade"
do `intent-statement.md`, documentado no `wireframes.md`.

## Assumptions & Open Questions

None.
