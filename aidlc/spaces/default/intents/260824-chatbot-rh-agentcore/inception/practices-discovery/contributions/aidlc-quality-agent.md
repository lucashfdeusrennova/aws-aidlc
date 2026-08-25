**Collaborator:** aidlc-quality-agent

## Contribution

Revisão QA do draft do lead sob a lente de estratégia de teste, ferramenta de
cobertura, gates de qualidade e padrões de mock. Foco: o que precisa entrar em
`## Testing Posture` (ou ficar como pergunta na entrevista) para que o demo de
2 dias não vá ao ar cego a regressões silenciosas de RAG e a violações das
regras duras em `discovered-rules.md`.

### 1. Metodologia e ordenação — endosso condicional

`test-after` com "implement each applicable testable layer, then write and run
that layer's tests" é a escolha correta para um workshop de 2 dias com equipe
que está aprendendo a stack pela primeira vez. TDD forçaria o time a escrever
testes contra APIs do Strands/AgentCore antes de entendê-las, o que consome
tempo de aprendizado em vez de acelerar. **AGREE** no par metodologia+ordenação.

**Adição pedida:** o texto do ordering diz "each applicable testable layer" mas
não enumera as camadas testáveis. Para não ficar ambíguo em Construction,
propor esta lista explícita em `## Testing Posture` (como notas adicionais, não
substitutas dos dois campos estruturados):

- Camadas testáveis nesta iniciativa: (a) `src/invoke.py` — função
  `ask_agent`; (b) `agent/agent.py` — construção do agente Strands e
  validação de entrada (guarda de 4000 chars); (c) frontend Streamlit **não**
  é camada testável nesta iniciativa (a validação é manual pelo demo).
- Camadas **não** testáveis por unidade: infraestrutura CDK (validada por
  `cdk synth` no deploy), Bedrock Knowledge Base (validada por queries
  manuais durante a preparação do demo).

### 2. Piso de cobertura — 80% é frágil no formato atual

O draft diz "piso de 80% de linhas … apresentado como métrica de saúde antes
de cada Bolt fechar." Isso não é um piso, é um alvo. Um piso que não bloqueia
é uma nota decorativa. Duas correções possíveis, a escolher na entrevista:

- **Opção A (recomendada para 2 dias):** reduzir para **cobertura de happy
  path por função pública em `src/` e `agent/`** (ou seja: cada função
  exportada tem no mínimo um teste que exercita seu caminho de sucesso), sem
  piso percentual. Isso está alinhado com o exemplo em `tech-env.md` § "Test
  Example" (2 testes para `ask_agent`, cobrindo resposta normal e resposta
  vazia) e é honesto sobre o que um workshop consegue entregar.
- **Opção B (se o time quiser manter o número):** manter 80% mas torná-lo
  bloqueante local via `pytest --cov=agent --cov=src --cov-fail-under=80`
  como parte do comando `pytest` documentado no README. Sem enforcement, o
  número não protege ninguém.

**Ferramenta de cobertura pedida:** adicionar `pytest-cov` a
`requirements-dev.txt` (o draft menciona `pytest --cov` mas o pacote não está
listado em `tech-env.md`). Sem `pytest-cov` instalado, a flag `--cov` falha
silenciosamente para "unrecognized argument" e a métrica nunca é coletada.

### 3. Escopo de mock — cobertura parcial, precisa ampliar

O draft menciona apenas "mock do cliente AgentCore
(`boto3.client('bedrock-agentcore')`)". Isso cobre `src/invoke.py::ask_agent`,
mas **não** cobre `agent/agent.py`, que é a camada mais nova e mais arriscada
do sistema. Especificar:

- **`src/invoke.py`** — mock de `boto3.client('bedrock-agentcore')` e do
  `invoke_agent_runtime`. Padrão já demonstrado em `tech-env.md`. Ressalva:
  o exemplo usa `patch("boto3.client")` no import de `src.invoke` — isso só
  funciona se `boto3.client` for chamado dentro de `ask_agent`, não no topo
  do módulo. Se `agentcore_client` for module-level (como está no exemplo
  do frontend), o patch precisa mirar em `src.invoke.agentcore_client`.
  Vale um comentário na diretriz de teste para evitar hora perdida com
  patches que "não pegam".
- **`agent/agent.py`** — não é chamado a partir do frontend nos testes
  unitários (roda dentro do AgentCore Runtime). Ainda assim, é testável em
  isolamento por: (a) construir o `Agent` com um `BedrockModel` mockado e
  ferramenta `retrieve` substituída por uma função dummy que retorna
  trechos determinísticos; (b) validar que a guarda de 4000 caracteres
  rejeita entrada oversize antes de chamar o modelo. **Sem esse teste, a
  regra `ALWAYS validate that the user prompt is at most 4000 characters`
  em `discovered-rules.md` não tem verificação automatizada.**
- **Bedrock Runtime / Knowledge Base** — nenhuma chamada direta partindo do
  código do host (tudo passa por `invoke_agent_runtime`), então não há mock
  adicional a fazer no host. Dentro do agente Strands, a tool `retrieve`
  precisa ser stubada nos testes unitários do agente.

### 4. Validação end-to-end manual — aceitável, mas incompleta

Para um demo é aceitável validar manualmente pelo Streamlit. O que **não** é
aceitável é ir para a demo sem uma verificação automatizada mínima de que o
agente responde a perguntas conhecidas. Propor:

- **Smoke test manual documentado**: um checklist curto (3 a 5 perguntas
  canônicas: "quantos dias de férias?", "qual o processo de onboarding?",
  "quais são os feriados de dezembro?", "qual meu salário?" — essa última
  para validar a recusa LGPD) que a pessoa que faz o demo roda no Streamlit
  antes de apresentar. Vive em `docs/smoke-test.md` ou como uma seção do
  README.
- **Opcional, se sobrar tempo em Q4/Could**: um script `scripts/smoke.py`
  que chama `ask_agent` contra o AgentCore Runtime já deployado com as
  mesmas 3 a 5 perguntas e imprime as respostas. Não substitui olho humano
  no demo, mas dá reprodutibilidade.

### 5. Gaps de tipos de teste — o que está faltando

Além dos unitários, o draft omite três categorias que valem discutir na
entrevista:

- **Teste de guardrail LGPD** (crítico): a regra "NEVER expose individual
  employee data" está em `discovered-rules.md` mas não tem cadeia de
  verificação. Propor um teste unitário de agente com uma tool `retrieve`
  stubada que retorna um trecho contendo um salário fictício, e asserção de
  que a resposta do agente **não** o repete verbatim. Isso valida o system
  prompt como parte do produto testável, não como texto solto.
- **Teste de regressão de prompt / golden answers** (recomendado): dado o
  system prompt atual e um conjunto pequeno de perguntas/respostas de
  referência, um teste que compara semanticamente (ou por palavras-chave
  âncora) que a resposta cita o documento correto. Barato de escrever para
  o escopo `mvp` e paga imediatamente quando o time trocar de modelo
  (B-5 do backlog é exatamente esse cenário).
- **Contract test entre `invoke.py` e o payload do AgentCore** (dispensável
  para o mvp, registrar como Could): confirmar que o formato
  `{"prompt": "..."}` esperado pelo agente é o mesmo que o frontend envia.
  Em um projeto real seria obrigatório, num workshop de 2 dias fica como
  Could-have.
- **Testes de infraestrutura CDK**: pytest sobre o stack CDK está fora do
  escopo `mvp`; `cdk synth` no deploy é suficiente. Registrar como fora de
  escopo para não gerar expectativa.

### 6. Perguntas a acrescentar na entrevista

Sugestões para o lead considerar no `practices-discovery-questions.md`:

- **Piso de cobertura**: manter 80% bloqueante, adotar happy-path por função
  sem percentual, ou remover o alvo? (opções A/B/C acima).
- **Teste de guardrail LGPD**: incluído no `mvp` ou deixado para depois do
  workshop? A recomendação QA é incluir.
- **Prompt regression**: 3 a 5 perguntas âncora com respostas de referência
  entram no `mvp` (B-6 já está como Should)?
- **Smoke test antes do demo**: checklist manual documentado, script `.py`
  automatizado, ou ambos?

## Positions

- AGREE: metodologia `test-after` com ordering "implement each applicable testable layer, then write and run that layer's tests" — combina com equipe iniciante na stack, escopo `mvp` e janela de 2 dias; TDD custaria tempo de aprendizado sem compensar em regressão dentro desse horizonte.
- OBJECT: piso de 80% de cobertura "apresentado como métrica de saúde, não bloqueante" — piso não bloqueante não é piso; ou vira `--cov-fail-under=80` no comando local, ou é substituído por happy-path por função pública, ou é removido. Do jeito atual, `pytest-cov` sequer aparece em `requirements-dev.txt`, então o número nem chega a ser medido.
