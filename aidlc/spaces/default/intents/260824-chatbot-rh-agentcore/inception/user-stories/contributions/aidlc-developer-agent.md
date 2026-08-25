**Collaborator:** aidlc-developer-agent

## Contribution

Análise de implementabilidade, sizing, dependências e feasibility técnica das
10 stories propostas contra o code layout afirmado em `team-practices.md` §
Code Style (`agent/agent.py`, `src/invoke.py`, `frontend/app.py`) e o
inventário de requisitos (FR1–FR9, NFR1–NFR10).

### Sizing (2 dias × equipe de workshop)

- **10 stories em 2 dias é viável.** Cinco das dez (US1.1, US1.2, US1.3, US2.1,
  US3.1) compartilham exatamente o mesmo caminho de código:
  `frontend/app.py` → `src/invoke.py::ask_agent` → AgentCore Runtime →
  `agent/agent.py` com tool `retrieve`. A diferença entre elas é apenas o
  documento fonte na KB. Uma vez que a primeira dessas cinco esteja no ar, as
  outras quatro custam ~10–20min cada (pergunta canônica no smoke test +
  validação manual) — muito abaixo do range estimado de 30–90min declarado em
  "INVEST Notes / Estimable". A estimativa como está é conservadora, o que é
  saudável.
- **US1.6 (guard 4000 chars)** é a menor story do lote — provavelmente <30min:
  um `if len(question) > 4000: raise ValueError` em `src/invoke.py` e um
  `try/except ValueError` no frontend. Cabe em Small sem quebrar INVEST.
- **US1.8 (troca de modelo) é a maior story** e a única com risco não trivial
  de estouro — ver seção "Implementabilidade" abaixo. Ajustar sizing mental
  para 60–90min, não 30.

### Implementabilidade por story

| Story | Caminho de código | Risco |
|-------|-------------------|-------|
| US1.1–1.3, US2.1, US3.1 | Mesmo pipeline RAG (agent + `retrieve` + KB indexada) | Baixo, desde que FR2.2 (ingestion job) esteja concluído antes de qualquer smoke |
| US1.4 (fallback) | Instrução no system prompt de `agent/agent.py` | Baixo — só depende do prompt |
| US1.5 (recusa LGPD) | System prompt + teste com `retrieve` stubbed | Baixo — ver nota Strands abaixo |
| US1.6 (>4000 chars) | Guard em `src/invoke.py` + `st.warning` | Trivial |
| US1.7 (erro AgentCore) | `try/except ClientError → AgentInvocationError` em `src/invoke.py`; `st.error` em `frontend/app.py` | Trivial |
| US1.8 (troca de modelo) | Sidebar dropdown + parâmetro dinâmico do `BedrockModel` do Strands | **Médio** — ver objeção |

### US1.5 AC1.5.3 — stub de `retrieve` com Strands

**Feasível.** O Strands Agents SDK trata tools como callables Python
registrados via `Agent(tools=[...])`. Em pytest, o padrão é:

```python
def fake_retrieve(query: str) -> str:
    return "Salário do João: R$ 42.000,00 mensais."

agent = Agent(model=mock_model, tools=[fake_retrieve])
```

Ou, se `agent/agent.py` já importa `strands_tools.retrieve` no top-level,
`monkeypatch.setattr("agent.agent.retrieve", fake_retrieve)` funciona. A
prática está pré-afirmada em `team-practices.md § Testing Posture` ("`retrieve`
substituída por um stub que retorna trechos determinísticos"), então o AC é
consistente com a testing posture do time. Sem objeção.

### US1.7 — nomear `AgentInvocationError` no AC

O AC1.7.1 cita o nome da exceção (`AgentInvocationError`) e o arquivo
(`src/invoke.py`). Isso é detalhe de design, não de requisito puro — mesma
observação que já saiu no review advisory do `requirements.md` (findings §
FR9). **Mantenho como não bloqueio** porque:

1. A convenção já está afirmada em `team-practices.md § Code Style` ("Error
   handling policy") e portanto a story está honrando um contrato existente,
   não inventando um novo.
2. Remover o nome da exceção não muda observabilidade externa (o usuário
   nunca vê a exceção; só vê o `st.error`). Refatorar depois é seguro.

### US1.8 AC1.8.2 — verificabilidade da "resposta gerada pelo novo modelo"

**Este AC é o ponto fraco do lote e merece endurecer.** O texto atual diz
"verificável via metadata de resposta ou observação de estilo". Do ponto de
vista de implementação:

- **"Observação de estilo"** não é um critério testável — é subjetivo e não
  serve para smoke test automatizável.
- **"Metadata de resposta"**: o `invoke_agent_runtime` do AgentCore Runtime
  retorna um payload que é o output do agente Strands. **O `modelId` que o
  Strands usou internamente NÃO é retornado por default no envelope de
  resposta do AgentCore.** O que o Strands expõe é o resultado da conversação;
  para saber qual modelo respondeu é preciso ou (a) instrumentar o próprio
  `agent/agent.py` para incluir o `model_id` na resposta, ou (b) inspecionar
  logs do lado do agente.
- **Recomendação técnica**: reescrever AC1.8.2 como um dos dois observáveis
  concretos:
  - **(a)** "a chamada `invoke_agent_runtime` inclui o `model_id` selecionado
    no payload (ex.: chave `model_id` no JSON body), verificável por
    inspeção do payload"; ou
  - **(b)** "o `agent/agent.py` inclui `model_id` como campo estruturado no
    output final, e o smoke test para US1.8 asserta que esse campo bate com o
    dropdown."

Sem essa correção, US1.8 fica na fronteira de "não testável" — INVEST-T
violado.

### Dependências — validação da ordem

A seção "Story Dependencies" está tecnicamente correta, mas incompleta.
Faltam três dependências implícitas que um developer descobriria no primeiro
dia:

1. **US1.6 e US1.7 dependem entre si** implicitamente na camada de frontend:
   ambos vivem no mesmo `try/except` em `frontend/app.py` (um pega
   `ValueError` do guard, outro pega `AgentInvocationError`). Não bloqueante
   — as duas podem ser implementadas em paralelo em um mesmo commit, mas
   isso deveria ser sinalizado.
2. **US1.8 (troca de modelo) depende também de FR6.2** (inference profile
   ARN para modelos `us.*`). O AC1.8.3 cobre isso, mas a seção de
   dependências só menciona "FR4.4 + FR6 (config de modelo)" — vale amarrar
   explicitamente ao ARN de inference profile.
3. **Todas as stories dependem de FR2.2 (StartIngestionJob) ter rodado.**
   Está implícito em "FR2 (KB indexada)" mas o ingestion job em si (rodar
   `bedrock:StartIngestionJob` manualmente antes da demo, conforme
   `team-practices.md § Deployment`) é a etapa concreta que destrava tudo —
   se esquecerem, o `retrieve` retorna vazio e todas as 10 stories aparentam
   estar quebradas. Vale um lembrete visível no arquivo, mesmo que não vire
   story.

### Backlog gaps (missing stories)

Q4=A confirma "as 10 propostas cobrem o MVP", então oficialmente nada falta.
Ainda assim, do lado do developer, três gaps merecem menção no arquivo mesmo
que não virem story:

1. **FR4.5 (botão "Limpar conversa" + regenera `session_id`)** está sem
   story. É user-facing e está afirmado como requisito. US1.8.4 encosta no
   tema (preservação de histórico durante troca de modelo) mas não cobre o
   fluxo de limpeza. **Este é o único gap real que eu levantaria como
   candidato a story adicional** — algo como "US1.9 — Limpar conversa e
   iniciar nova sessão".
2. **FR4.3 (spinner "Consultando base de conhecimento...")** — não é story,
   é polimento de UX que sai grátis em qualquer implementação de
   `st.chat_input`. OK omitir.
3. **Deploy (`cdk synth`/`cdk deploy` + smoke pré-demo)** — operacional, não
   user-facing. Sem story está correto.
4. **KB sync (`StartIngestionJob`)** — mesma categoria: task operacional, não
   user story. Correto omitir.

## Positions

- **AGREE**: Sizing global (10 stories × 2 dias) é realista — cinco delas
  compartilham código e custam pouco marginal cada. A curva de dificuldade
  está bem distribuída (uma story hard = US1.8, uma story trivial = US1.6, o
  resto médio-baixo).
- **AGREE**: US1.5 AC1.5.3 (stub de `retrieve`) é totalmente feasível com
  Strands Agents SDK, e alinha com a testing posture já afirmada em
  `team-practices.md`. Sem risco técnico.
- **AGREE**: Mapear todas as stories para o code layout `agent/` + `src/` +
  `frontend/` funciona — os three-layer boundaries de `team-practices.md`
  são respeitados por cada story sem exceção.
- **AGREE**: US1.7 nomear `AgentInvocationError` no AC é aceitável porque a
  convenção já existe em `team-practices.md § Code Style`. Non-blocking
  advisory apenas.
- **OBJECT**: **US1.8 AC1.8.2 é fraco em testabilidade** — "observação de
  estilo" não é observável e "metadata de resposta" não é retornado por
  default pelo `invoke_agent_runtime`. Recomendo reescrever o AC como
  observável concreto (payload de chamada OU campo estruturado no output do
  agente). Sem isso, US1.8 falha o "T" do INVEST.
- **OBJECT**: **Falta story para FR4.5 (limpar conversa + novo
  `session_id`)**. É requisito user-facing afirmado, não é coberto por
  nenhuma das 10 stories, e US1.8.4 apenas encosta no tema. Sugiro adicionar
  US1.9 ou expandir US1.8 com um AC1.8.5 dedicado ao botão "Limpar conversa"
  — a implementação em si é `st.session_state.messages = []; session_id =
  uuid.uuid4()`, cabe em <20min, mas o requisito precisa de teste manual
  documentado.
- **OBJECT (menor)**: A seção "Story Dependencies" deveria explicitar que
  **todas as stories user-facing dependem de FR2.2 (StartIngestionJob
  concluído)**. Não como pré-condição de código, mas como pré-condição
  operacional da demo. Se o job não rodar, todas as 10 stories retornam
  vazio e o time gastará tempo debugando o que não é bug.
