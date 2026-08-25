# Team-Level Rules

> This team's affirmed practices and corrections. Loaded after `org.md` as
> strict-additive guidance; contradictions with broader policy are rejected.
> Populated by the practices-discovery affirmation gate. Edit at the gate,
> not directly.

## Way of Working

Adotamos **trunk-based development** com `main` como tronco único. Todo trabalho
segue por *feature branches* de vida curta (tipicamente encerradas dentro do
mesmo dia, dado o cronograma de 2 dias do workshop) e retorna ao `main` por
**squash-merge**, produzindo um commit por Bolt cujo nome carrega o slug do
Bolt. Não há branches de release nem branches de longa duração — o histórico
do `main` é linear e mapeia 1:1 para a sequência de Bolts do
`delivery-planning`.

Para worktrees da fase de Construction, `main` é tanto o *base branch* quanto
o *merge target*.

Como o workshop dura apenas 2 dias e não há ambiente de produção envolvido,
nenhum bloqueio de release por tag ou por ambiente se aplica: mergear no
`main` é o "release" desta iniciativa.

## Walking Skeleton

**Pulamos a cerimônia de walking skeleton porque o escopo `mvp` declara
`skeleton: off`.** O primeiro Bolt roda como qualquer outro — não há um
esqueleto ponta-a-ponta dedicado para bootstrap. A stack (AgentCore Runtime,
Bedrock Knowledge Bases + S3 Vectors, Strands SDK, Streamlit) já é
suficientemente demonstrada pelos exemplos em `tech-env.md`; o valor de uma
fatia vertical isolada não compensa o custo dentro de uma janela de 2 dias.

Depois do primeiro Bolt não há prompt de "ladder" — como o skeleton está
desligado, não há uma decisão de continuidade a ser feita.

## Testing Posture

- **Methodology**: test-after
- **Ordering**: implement each applicable testable layer, then write and run that layer's tests

Notas adicionais (não substituem os dois campos estruturados acima):

- **Framework**: `pytest` (por `tech-env.md`).
- **Cobertura**: piso de **80% de linhas, BLOQUEANTE local**, enforçado pelo
  comando padrão de teste `pytest --cov=agent --cov=src --cov-fail-under=80`.
  Requer `pytest-cov` em `requirements-dev.txt` — sem o pacote instalado a
  flag `--cov` falha como argumento desconhecido e a métrica nunca é
  coletada. Sem CI neste workshop, o gate roda na máquina do participante
  antes do squash-merge no `main`.
- **Camadas testáveis** nesta iniciativa:
  - (a) `src/invoke.py::ask_agent` — função de invocação do AgentCore Runtime;
  - (b) `agent/agent.py` — construção do agente Strands (`BedrockModel` +
    tool `retrieve`) e o guard de entrada de 4000 caracteres.
- **Camadas não testáveis por unidade**:
  - Frontend Streamlit — validação manual durante o demo;
  - Infraestrutura CDK — validada por `cdk synth` no deploy (não há pytest
    sobre o stack no escopo `mvp`).
- **Estratégia de mock**:
  - `src/invoke.py` — `patch("boto3.client")` no import de `src.invoke`, ou
    `patch("src.invoke.agentcore_client")` se o cliente for module-level; a
    fixture central vive em `tests/conftest.py`.
  - `agent/agent.py` — `BedrockModel` mockado e a tool `retrieve` substituída
    por um stub que retorna trechos determinísticos.
  - Nenhum teste unitário toca AWS real.
- **Teste de guardrail LGPD (MUST)**: 1 teste unitário do agente com prompt
  provocador ("Qual o salário do João?") e `retrieve` stubado retornando um
  trecho com um salário fictício; a asserção é que a resposta do agente
  **não** repete o valor verbatim. Torna a política CC-1/CC-2 auditável em
  vez de depender apenas do system prompt.
- **Smoke test**: `scripts/smoke.py` — script que invoca 3 a 5 perguntas
  canônicas contra o AgentCore Runtime já deployado antes da demo, incluindo
  pelo menos uma pergunta que valide a recusa LGPD. Sem checklist manual em
  paralelo; o script é a única cerimônia de smoke.
- **Test Strategy**: `Standard` (herdado de `aidlc-state.md`).

## Deployment

**Deploy local-only, sem ambientes gerenciados.** O default do `org.md`
("deploy-on-merge para staging") **não se aplica** a esta iniciativa porque
não há ambiente de staging nem de produção — o workshop é uma demo de 2 dias
em uma conta AWS de sandbox.

Padrão desta iniciativa:

- **Frontend**: `streamlit run frontend/app.py` no notebook de cada
  participante, ou em Cloud9 se preferido. Sem deploy hospedado.
- **Agente + Knowledge Base**: deployados via **CDK Python** em um único
  stack contendo AgentCore Runtime, Bedrock Knowledge Base (S3 Vectors) e
  bucket S3 dos documentos, na região `us-east-1`. Sem staging: `cdk deploy`
  vai direto para a conta sandbox do workshop.
- **Fluxo obrigatório**: `cdk synth` antes de cada `cdk deploy` para
  inspecionar o template CloudFormation gerado. ARNs (do runtime, da KB, do
  bucket) são consumidos dos **outputs do stack** — nunca hardcoded no
  código do frontend ou do invocador.
- **Sincronização de documentos**: documentos de RH (`docs/knowledge-base/*`)
  são enviados ao S3 pelo mesmo stack e a KB é sincronizada manualmente
  (`StartIngestionJob`) antes da demo.
- **Sem deploy de produção no escopo** (`vision.md` § Out of Scope). Sem
  gate de aprovação manual, sem CodePipeline, sem CD contínuo.
- **Rollback**: recriar o AgentCore Runtime (idempotente via CDK) ou apontar
  o frontend para um ARN anterior. Não há política de retenção formal para
  os runtimes descartados durante o workshop.

### Bedrock Guardrails (recomendado, não mandatório)

Como defesa em profundidade para CC-1/CC-2 além do system prompt (que é
bypass-vulnerável a prompt injection via documento), a equipe **considera
caso a caso** configurar `associatedGuardrailArn` no `BedrockModel` do
Strands com:

- Filtro de PII em `OUTPUT` (nomes, CPF, e-mail, telefone);
- Denied topics: "salário, remuneração, folha de pagamento, dados
  individuais de funcionário".

Recomendação registrada aqui porque o custo de configuração é baixo e o
sinal de auditabilidade é alto quando o RH questiona uma resposta
específica pós-demo. Fica fora de `discovered-rules.md` — a decisão de
ativar em cada Bolt é do time, não uma regra dura do projeto.

## Code Style

- **Linguagem**: Python 3.12 (`tech-env.md`).
- **Linter + Formatter**: **`ruff`** com **select default (`E` + `F` apenas)**
  — pycodestyle errors + Pyflakes. Sem `select` customizado no
  `pyproject.toml`; sem `S` (bandit), sem `B` (bugbear), sem `UP`. `ruff
  format` como formatador único (sem black em paralelo). Rodado localmente
  antes de cada commit; sem CI que bloqueie neste workshop, mas violações
  não vão para o `main`.

  > **Nota importante**: o select default do ruff **não inclui bugbear
  > (`B`)**, portanto a política de tratamento de erro descrita abaixo
  > (proibição de `except: pass`, `mutable default args` etc.) é uma
  > **convenção verificada em code review**, não pelo linter. Se o time
  > quiser enforcement automatizado depois, basta adicionar `B` ao select.

- **Fronteiras de camada** (invariante de dependência do repositório):
  - **`agent/`** roda **dentro** do AgentCore Runtime (microVM gerenciada,
    deploy separado). É auto-contido: importa apenas `strands`,
    `strands_tools` e `boto3`. **Nunca** importa de `src/` ou `frontend/`.
  - **`src/`** é a cola de invocação (cliente boto3 do `bedrock-agentcore`).
    Não conhece Streamlit e não conhece o código interno do agente — só
    a assinatura de `invoke_agent_runtime`.
  - **`frontend/app.py`** depende de `src/` (`from src.invoke import
    ask_agent`). **Nunca** o inverso: `src/` não importa `streamlit`.
  - **`tests/`** espelha a árvore de fontes; `tests/conftest.py` centraliza
    fixtures de mock do cliente `bedrock-agentcore`.
  - Direção da dependência: `frontend/ → src/ → boto3`; `agent/` isolado.

- **Naming**:
  - PEP 8 idiomática — `snake_case` para funções, módulos e variáveis;
    `PascalCase` para classes; `UPPER_SNAKE_CASE` para constantes de módulo.
  - Env vars fixas: `AGENT_RUNTIME_ARN`, `KNOWLEDGE_BASE_ID`, `AWS_REGION`
    (com fallback `us-east-1` no código).
  - `session_id` gerado server-side via `uuid.uuid4()` — **nunca** aceito
    de input do usuário, query string ou header.
  - Módulos sem prefixo de app (é `invoke.py`, não `chatbot_invoke.py`).

- **Type hints**: **obrigatórios** em toda função exportada por `src/` e
  `frontend/` (é o contrato de camada) e em todas as tools do agente
  (`agent/agent.py`). Encorajados em helpers internos prefixados `_`.
  Preferir sintaxe PEP 604 (`str | None` em vez de `Optional[str]`;
  `list[str]` em vez de `List[str]`).

- **Error handling policy (convenção, verificada em code review)**:
  - `src/invoke.py` captura `botocore.exceptions.ClientError` na chamada
    `invoke_agent_runtime` e re-eleva como exceção de domínio
    `AgentInvocationError` com mensagem legível.
  - `frontend/app.py` captura `AgentInvocationError` e mostra via
    `st.error(...)` — nunca deixa traceback aparecer no chat.
  - Loga o `ClientError` original via `logging.getLogger(__name__)` para
    debug local.
  - Guard de comprimento de input (4000 chars) mora em `src/invoke.py`
    (antes da chamada boto3), levantando `ValueError`; o frontend converte
    para `st.warning(...)`.
  - **Nunca** `except Exception: pass` nem `except:` sem re-raise.
  - Esta política **não é enforçada pelo ruff** (select default = `E`+`F`);
    é revisada no code review. Adicionar `B` ao select se o time quiser
    enforcement automatizado depois.

- **Idiomas Python 3.12 para boto3 + Strands**:
  - Um único cliente boto3 por módulo, criado no top-level; não recriar por
    chamada.
  - `pathlib.Path` para caminhos de arquivo (não `os.path.join`).
  - `json.dumps(...).encode()` (não `bytes(json.dumps(...), "utf-8")`).
  - Para a tool `retrieve` do Strands, `KNOWLEDGE_BASE_ID` vem via env var
    (o SDK resolve por env, não passar como argumento na tool call).

- **Não adotado**:
  - **mypy / pyright** — fora do orçamento do workshop; `ruff` default +
    type hints legíveis dão o valor esperado sem custo de configuração de
    type-checker.
  - **pre-commit hooks** — overhead de setup > valor para 2 dias sem CI.
  - **Result / Either types** — erro é exceção idiomática em Python.
## Forbidden

<!-- Team-specific forbidden patterns -->

## Mandated

<!-- Team-specific mandates -->

## Corrections

<!-- Self-learning loop appends here. -->
