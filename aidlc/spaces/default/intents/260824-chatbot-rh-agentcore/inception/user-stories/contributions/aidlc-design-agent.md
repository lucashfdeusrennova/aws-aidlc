**Collaborator:** aidlc-design-agent

## Contribution

Revisao pela lente UX: fidelidade aos wireframes, coerencia das personas com a
interacao real, qualidade das mensagens visiveis ao usuario e cobertura dos
estados de tela definidos em `wireframes.md` / `user-flow.md`.

### 1. Profundidade das personas

As tres personas estao distintas em papel e dor, mas todas carecem de tres
atributos que impactam decisoes de UX (redacao, densidade da resposta, uso do
seletor de modelo):

- **Alfabetizacao tecnica**: Ana precisa acessar `http://localhost:8501` num
  notebook durante a demo. Isso pressupoe conforto minimo com navegador + URL
  local, mas nao esta declarado. Sugestao: acrescentar "conforto medio com
  aplicativos web; nao e desenvolvedora nem power user" no bloco Contexto de
  Ana.
- **Frequencia de uso**: implicita ("uma pergunta e uma resposta em menos de
  5s" nao diz quantas por semana). Sugestao: Ana ~2-3 vezes por semana, Bruno
  diariamente nos 30 dias iniciais, Carla pontual (uma janela de ~2 semanas
  por ciclo).
- **Faixa etaria / contexto sensorial**: nao e necessario faixa etaria
  precisa, mas registrar "adulto em ambiente de escritorio, sem restricao
  declarada de acessibilidade nesta demo" mantem alinhamento com a decisao
  [Q5] de `wireframes.md` (WCAG nao certificado nesta iteracao) e evita que
  design system decisions no `functional-design` assumam algo mais forte.

### 2. Aderencia stories x wireframes

O layout definido em `wireframes.md` (chat central + sidebar com dropdown de
modelo + botao "Limpar conversa") tem duas capacidades visiveis. A stories.md
cobre uma (US1.8, seletor de modelo) mas **nao cobre a segunda** (botao
"Limpar conversa"), embora o botao esteja no wireframe, no requisito FR4.5 e
no desvio "Limpar conversa / nova sessao" do `user-flow.md`. Isso e uma
lacuna testavel: sem story nao ha AC BDD para o comportamento (novo
`session_id`, historico zerado, saudacao inicial reaparece).

Adicionalmente, o **estado inicial** (bolha unica de saudacao) e o **estado
"aguardando resposta"** (spinner "Consultando base de conhecimento...") estao
em `wireframes.md § Estados` mas nao aparecem em nenhum AC. US1.1 e as demais
consultas assumem a resposta chega, mas nao asseguram que o spinner e
mostrado durante a chamada nem que a saudacao aparece no `first paint`.

### 3. US1.8 - conflacao de papel (Ana como operadora)

O texto "Como Ana (no papel de operadora da demo), quero..." mistura duas
personas em uma. Ana e colaboradora consumidora do bot; quem opera a demo
comparando modelos e o time tecnico do workshop (mencionado em NFR6.1 como
"operado pelo time tecnico do workshop"). Duas alternativas de UX:

- **Alt A (preferida)**: introduzir uma quarta persona minima "Operador da
  demo (time tecnico)" para ser sujeito de US1.8. Deixa Ana pura como
  consumidora e libera o AC1.8.4 (preservacao de historico apos troca) para
  ser realmente testavel do ponto de vista do operador.
- **Alt B**: manter Ana como sujeito, mas remover o parentesis "no papel de
  operadora" e reescrever a story como "Como Ana, quero ver o modelo em uso
  na sidebar" (visibilidade, nao troca). A troca vira uma capacidade oculta
  atras de flag ou query string e sai da UI publica. Reduz a lacuna de
  persona mas exige mexer nos wireframes.

### 4. Redacao das mensagens visiveis ao usuario

Tres textos chegam a Ana literalmente e merecem revisao:

- **US1.6 (aviso >4000 chars)**: "Sua pergunta ultrapassa 4000 caracteres.
  Reformule mais curto."
  - "4000 caracteres" e um limite tecnico que Ana nao consegue estimar
    visualmente (nao ha contador). "Reformule mais curto" tambem soa um pouco
    seco em PT-BR.
  - Sugestao de redacao Ana-appropriate: **"Sua pergunta ficou muito longa
    para eu processar. Tente resumir em uma unica pergunta mais curta."**
  - Melhoria complementar (nao bloqueia esta stage, fica de recomendacao
    para `functional-design`): mostrar contador de caracteres progressivo
    (`{n}/4000`) quando o input ultrapassar ~3500 chars - progressive
    disclosure em vez de aviso post-facto.
- **US1.7 (erro AgentCore)**: "Nao consegui responder agora. Tente reformular
  ou contate o RH."
  - "Tente reformular" nao ajuda quando a causa e throttling / timeout / IAM
    (nada a ver com a redacao da pergunta). Confunde a expectativa da Ana.
  - Sugestao: **"Nao consegui responder agora. Tente novamente em alguns
    segundos ou contate o RH se o problema persistir."**
- **US1.4 (fallback)**: "Nao encontrei essa informacao nos documentos.
  Sugiro contatar o time de RH."
  - Tom aceitavel; direto e acionavel. Sugestao opcional de calor:
    **"Nao encontrei essa informacao nos documentos disponiveis. Voce pode
    falar com o time de RH para tirar essa duvida."** - troca "sugiro"
    (imperativo suave) por "voce pode" (habilitante), consistente com o
    tom conversacional de assistente.

### 5. Cenarios UX faltantes (do `user-flow.md`)

O `user-flow.md` lista tres desvios que hoje nao tem story dedicada:

- **"Limpar conversa / nova sessao"** - ver item 2 acima. **Faltando.**
- **"Trocar modelo de chat"** - coberta por US1.8 (com ressalva de persona
  no item 3).
- **"Pergunta fora da base de conhecimento"** - coberta por US1.4.
- **"Nao mostra fonte na UI"** - coberta por AC1.1.3 (desvio consciente
  citado). OK.
- **Saudacao inicial** e **spinner** - ver item 2. Nao sao desvios mas
  compoem o estado observavel; a ausencia de AC deixa uma zona nao
  testavel.

## Positions

- **AGREE**: agrupamento por persona escolhido em Q2=B - facilita leitura
  linear e mantem as sub-personas Bruno/Carla visiveis sem se dissolverem
  numa unica lista funcional; **AGREE**: US1.4 na prioridade Should Have
  refletindo Q3=A - fallback educado nao bloqueia o MVP funcional mas eleva
  confianca; **AGREE**: AC1.1.3 documentando o desvio FR7.2 (sem citacao do
  documento fonte) de forma explicita - a decisao sai auditavel em vez de
  silenciosa; **AGREE**: AC1.6.1 usando o texto exato do `st.warning` como
  criterio testavel - segue o padrao "requirements com string literal" de
  FR8.2 e evita interpretacao livre no build; **AGREE**: cross-ref
  AC3.1.2 -> US1.5 - Carla e o vetor mais provavel de pergunta sobre
  desempenho de subordinado nominal, o link explicito impede regressao.
- **OBJECT**: **falta story para "Limpar conversa"** - o botao esta em
  `wireframes.md`, em FR4.5 e em `user-flow.md § Limpar conversa`, mas
  nenhuma story em stories.md o testa. Sugestao concreta: adicionar
  **US1.9 - Iniciar nova conversa** (Grupo US1, Ana) com ACs cobrindo
  (a) botao visivel na sidebar, (b) clique gera novo `session_id` via
  `uuid.uuid4()`, (c) `st.session_state.messages` e zerado, (d) a bolha de
  saudacao inicial reaparece, (e) a nova sessao no AgentCore Runtime roda
  isolada da anterior (nao ha vazamento de contexto).
- **OBJECT**: **US1.8 conflaciona persona** - "Ana no papel de operadora da
  demo" mistura consumidora do bot com operador tecnico do workshop
  (chamado em NFR6.1). Preferencia por Alt A (nova persona minima
  "Operador"); Alt B (esconder a troca da UI publica) tambem resolve mas
  exige alterar os wireframes ja aprovados. Sem correcao, AC1.8.1-1.8.4
  ficam testaveis mas atribuidos a persona errada, o que polui o rastro de
  quem consome o que.
- **OBJECT**: **US1.6 e US1.7 tem redacao subotima para Ana** - detalhe em
  itens 4.1 e 4.2 acima. Nao bloqueia o build (o texto exato e passivel de
  edicao no frontend), mas como AC1.6.1 e AC1.7.2 congelam a string
  literalmente, a redacao entra em stories.md como contrato. Corrigir agora
  poupa uma rodada de retrabalho em `code-generation`.
- **OBJECT (leve)**: **falta AC para estado "aguardando resposta"** (spinner)
  e para o **estado inicial** (bolha de saudacao). Sao estados observaveis
  declarados em `wireframes.md § Estados` sem contrapartida testavel.
  Sugestao minima: adicionar um AC em US1.1 do tipo "Given Ana envia a
  pergunta, when a chamada esta em execucao, then a bolha do assistente
  mostra o spinner 'Consultando base de conhecimento...' ate a resposta
  chegar" e um AC em US1.9 (ou em US1.1 como pre-condicao) cobrindo a
  saudacao inicial.
