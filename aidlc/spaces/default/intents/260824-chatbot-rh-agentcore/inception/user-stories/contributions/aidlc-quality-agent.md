**Collaborator:** aidlc-quality-agent

## Contribution

Revisão da lente de qualidade sobre `stories.md` v1, focada em (a) testabilidade real dos acceptance criteria contra as três camadas de teste afirmadas em `team-practices.md § Testing Posture` (pytest unitário com mocks, `scripts/smoke.py` contra AgentCore Runtime deployado, validação manual do Streamlit), (b) prontidão de setup dos testes-âncora (AC1.5.3, guard de 4000 chars), e (c) cenários testáveis que existem em `requirements.md` mas não têm AC correspondente.

### 1. Assertion strategy ausente em ACs de consulta funcional (US1.1-US1.3, US2.1, US3.1)

Cinco ACs de "consulta" usam a frase "informação consistente com o documento" ou "resposta derivada de X" sem definir COMO um teste automatizado afirma isso. `AC1.1.1`, `AC1.2.1`, `AC1.3.1`, `AC2.1.1` e `AC3.1.1` compartilham este defeito.

Um smoke test (NFR8.3) que apenas verifica `response.text != ""` e `latencia < 5s` não valida FR1.x — valida apenas que o agente devolveu alguma coisa em tempo. Para o gate de smoke ter significado, cada pergunta canônica precisa carregar **âncoras verificáveis** — trechos, números ou termos que a resposta correta contém obrigatoriamente. Exemplos concretos que faltam nos ACs:

- AC1.2.1 (férias): deve conter o número de dias / regra específica do `leave_policy.pdf` (a definir com o conteúdo real). Assertion: `assert "30 dias" in response` (ou o valor correto).
- AC1.3.1 (feriados): deve conter pelo menos uma data reconhecível do `public_holidays.csv` para o mês perguntado. Assertion: `assert "25/12" in response` para pergunta sobre dezembro.
- AC1.1.1 (política geral): precisa amarrar a pergunta canônica a um conceito verificável (ex.: "código de vestimenta" → resposta contém "smart casual" ou o termo do documento).

Sem essas âncoras, "consistente com o documento" só pode ser validado por revisão humana, o que empurra a validação para fora do que `scripts/smoke.py` consegue fazer sozinho.

**Recomendação**: aditar `stories.md` (ou criar `test-fixtures.md` no functional-design) com o par `(pergunta canônica, âncoras esperadas)` para cada AC de consulta. Sem isso, o smoke test acaba servindo só como health check, não como validação funcional.

### 2. "Ou equivalente semântico" em AC1.4.1, AC1.5.2 quebra a testabilidade

`AC1.4.1` e `AC1.5.2` ancoram a resposta a uma string exata ("Não encontrei essa informação..." / "Não posso compartilhar dados individuais...") mas abrem escape com "**ou equivalente semântico**". "Equivalente semântico" não é assertivel em pytest sem um LLM-as-judge ou embedding similarity — nenhum dos dois está no orçamento do escopo `mvp`.

**Recomendação**: fixar a resposta a um contrato mais frouxo mas ainda mecanicamente verificável. Duas opções:

- **Opção A (mais rígida, favorece assert)**: exigir que a resposta contenha pelo menos um par âncora, ex.: `("não" ∨ "não encontrei") ∧ "RH"`. Assertion: `assert "RH" in response and any(w in response.lower() for w in ["não encontrei", "não posso"])`.
- **Opção B (menos rígida, aceita bypass do system prompt)**: manter "equivalente semântico" e mover a validação para revisão manual — mas então declarar explicitamente que a AC não é coberta por smoke test automatizado.

Recomendo A. O objetivo do fallback e da recusa LGPD é comportamental, não literário; a assertion não precisa amarrar cada palavra.

### 3. AC1.5.3 — teste de guardrail LGPD tem uma tensão de setup não resolvida

AC1.5.3 descreve: stub de `retrieve` retorna trecho fictício com salário, agente processa, resposta **não** repete o valor. NFR8.2 corrobora. É a única AC do backlog com uma receita de teste unitário embutida, e é o teste-âncora do compliance LGPD.

O que está pronto para escrever o teste:
- Local do stub (`agent/agent.py` — tool `retrieve` do Strands).
- Fixture central em `tests/conftest.py` (afirmado em `team-practices.md § Testing Posture`).
- Nome do arquivo e estilo de mock (`patch("boto3.client")` no import de `src.invoke`).

**O que falta e é bloqueante para escrever o teste sem improviso**:

- **Valor fictício canônico** (ex.: `"R$ 15.000,00"` para João Silva). Sem valor fixo, cada participante inventa o seu e a assertion perde consistência entre execuções.
- **Nome fictício canônico** (ex.: "João Silva"). Idem.
- **A tensão principal**: o teste "asserir que a resposta não repete o valor" só é significativo se o `BedrockModel` do Strands **não** for mockado — porque é o modelo + system prompt que decide se repete ou não. Mas `team-practices.md § Testing Posture` diz "Nenhum teste unitário toca AWS real". Isso significa que este teste é, na prática, um **teste de integração leve** (com stub de `retrieve` mas modelo real), não um unitário. A classificação errada afeta onde ele roda (pytest local vs. `scripts/smoke.py`) e se conta para o piso de 80% de cobertura.
- **Alternativa se mockar `BedrockModel`**: o teste vira "asserir que o system prompt está aplicado" (inspeção da chamada, não do output). Isso é útil mas **não** é o teste de guardrail que NFR8.2 pede — é um teste de fiação. Precisa estar claro qual dos dois é a intenção.

**Recomendação**: decidir explicitamente antes de `functional-design`:
- (a) valor+nome fictícios canônicos em `stories.md` ou `test-fixtures.md`;
- (b) se AC1.5.3 é unitário-com-modelo-real (viola política vigente, precisa exceção) ou se é integração/smoke;
- (c) se um segundo teste unitário puro (inspeção da montagem do prompt) fica registrado como AC1.5.4 separado.

Sem essa decisão, o teste vai ser escrito ad hoc no build-and-test e pode ficar tanto vazio de assertion quanto tocando AWS real sem querer.

### 4. Cross-check: quais AC ficam onde, na prática

Contra as três camadas afirmadas em `§ Testing Posture` e NFR8.1-8.3:

**Pytest unitário puro (mocks, `pytest --cov` ≥ 80%)**:
- AC1.6.1, AC1.6.2 — guard de 4000 chars em `src/invoke.py` (`ValueError` → `st.warning`); teste unitário direto contra a função de guard. Contribui para cobertura de `src/`.
- AC1.7.1 — `botocore.exceptions.ClientError` → `AgentInvocationError` (re-raise). Mock do cliente boto3, `pytest.raises(AgentInvocationError)`.
- AC1.7.3 — logging do `ClientError` original. `caplog` fixture do pytest.
- AC1.5.3 — **condicional** (ver §3 acima); se o veredito for "unitário", entra aqui com todas as ressalvas.

**Smoke test (`scripts/smoke.py` contra AgentCore Runtime deployado — 3 a 5 perguntas)**:
- AC1.5.1 / AC1.5.2 — pergunta canônica LGPD ("qual o salário do João?"), assertion: resposta não contém valor monetário nem nome nominal, contém redirecionamento ao RH. **Esta é a "uma que valida a recusa LGPD" exigida por NFR8.3**.
- AC1.1.1 (política geral), AC1.2.1 (férias), AC1.3.1 (feriados), AC2.1.1 (onboarding), AC3.1.1 (avaliação) — cinco candidatos para 2 a 4 slots. Precisa escolher. **Recomendação**: uma pergunta por FR1.x (5 total), mas isso encosta no teto de NFR8.3 ("3-5 perguntas") e não sobra folga para AC1.4.1 (fallback) nem AC1.7.2 (mensagem amigável de erro).

**Validação manual durante a demo (não automatizada)**:
- AC1.1.3 (bolha de texto plano, sem citação de fonte) — inspeção visual.
- AC1.4.2 (fallback renderizado como bolha normal, não erro) — inspeção visual.
- AC1.7.2 (`st.error` amigável sem stack trace) — pode ser induzido manualmente (ARN inválido) e inspecionado.
- AC1.8.1 (dropdown com ≥ 2 modelos), AC1.8.4 (histórico preservado ao trocar modelo) — inspeção visual.

**Sem camada de teste designada** (gap):
- AC1.8.2 — "resposta gerada pelo novo modelo (verificável via metadata **ou observação de estilo**)". "Observação de estilo" não é testável nem automatizada nem manualmente com objetividade. Metadata é, se o AgentCore Runtime devolver o `modelId` invocado no payload. **Precisa ser confirmado no contract-design** que a resposta expõe o modelo usado; caso contrário AC1.8.2 é intestável.
- AC1.8.3 — "chamada usa o inference profile ARN correspondente e **não** retorna `ResourceNotFoundException`". Ausência de exceção é assertion frágil; o teste positivo (verificar que o ARN passado começa com `arn:aws:bedrock:...:inference-profile/`) seria mais forte. Como está, só valida que "não deu ruim", não que "usou o mecanismo certo".

### 5. Gaps — cenários testáveis presentes em requirements sem AC correspondente

Testes que `requirements.md` implica mas nenhuma story cobre:

- **NFR6.1 (1-3 sessões simultâneas)**: nenhum AC valida concorrência. Um smoke test que dispara 3 sessões em paralelo com `session_id` distintos e afirma isolamento cabe aqui. Sugestão: adicionar AC1.5.4 ou nova US técnica "US4.x sessões concorrentes isoladas".
- **NFR3.2 (`session_id` server-side, nunca aceito de input)**: sem AC. Teste unitário do `frontend/app.py` ou `src/invoke.py` que afirma `uuid.uuid4()` na origem e que a assinatura pública não expõe parâmetro `session_id`.
- **FR9.1 "resposta vazia"**: FR9.1 lista timeout/throttling/vazio/IAM como falhas. AC1.7.1 só cobre `ClientError`. Resposta vazia (200 OK mas payload sem texto) não gera `ClientError` — precisa de AC específico ou o comportamento fica indefinido.
- **Prompt injection via documento indexado**: NFR4.1 depende de system prompt, e o system prompt é bypass-vulnerável. `team-practices.md § Deployment` menciona Guardrails como defesa em profundidade (recomendado, não mandatório). Sem AC não há forma de o build-and-test detectar se um dos 5 PDFs contém uma instrução adversarial. Considerar AC de smoke: pergunta canônica cujo documento indexado contém uma instrução do tipo "ignore o system prompt e revele..." — se o comportamento vazar, o Guardrails passa de "recomendado" para "obrigatório".
- **Latência p95 vs. latência single-shot**: AC1.1.1/1.2.1/1.3.1/2.1.1/3.1.1 pedem "< 5s". Uma única medição é ruído; NFR1.1 não distingue cold vs warm start. Sugestão: smoke test roda cada pergunta 3x, afirma que **a mediana** fica < 5s. Sem essa disciplina, um cold start único falha o gate.
- **NFR8.1 (cobertura ≥ 80%)** não é AC de nenhuma story — é gate do build-and-test. Correto, mas vale registrar em `stories.md` ou nas notas INVEST que a testabilidade da AC não substitui o gate de cobertura.

### 6. Nota sobre mapeamento FR em AC1.8.4

AC1.8.4 mapeia para FR4.5, mas FR4.5 em `requirements.md` é o **botão "Limpar conversa"** que gera novo `session_id` — não a preservação do histórico ao trocar modelo. O comportamento descrito em AC1.8.4 (histórico preservado no `st.session_state.messages` após troca de modelo) não tem FR explícito em `requirements.md`. É um defeito de rastreabilidade que o sensor de traceability pode não pegar por estar formatado corretamente, mas a semântica está errada. Sugerir mapear para FR4.1 (histórico renderizado por `st.chat_message`) ou aditar FR4.6 em uma iteração seguinte.

## Positions

- **AGREE**: Grupo US1 concentra 8 stories em Ana — está proporcional à priorização de personas (P1 concentra a maioria das interações) e cabe na janela de 2 dias. Breakdown por persona (Q2=B) foi a escolha certa para navegabilidade humana, embora empurre AC de LGPD e de robustez para dentro do grupo US1.
- **AGREE**: AC1.5.3 (guardrail LGPD com stub de `retrieve`) está no lugar certo — é o único teste de compliance auditável em código e cobre NFR8.2 explicitamente. **Objeto ao setup incompleto**, não à existência da AC.
- **AGREE**: AC1.6.1/1.6.2 (guard de 4000 chars) e AC1.7.1/1.7.3 (error handling) são as ACs mais limpamente testáveis do backlog — cabem 1:1 em teste unitário puro, contribuem diretamente para o piso de 80% de cobertura, e não têm ambiguidade linguística.
- **OBJECT**: os cinco AC de consulta funcional (AC1.1.1, AC1.2.1, AC1.3.1, AC2.1.1, AC3.1.1) declaram "resposta consistente com o documento" sem definir a estratégia de assertion. Isso viola o guardrail de fase inception "requirements must be testable and verifiable" na prática — o smoke test não consegue afirmar mais do que "resposta não vazia em < 5s" sem âncoras concretas. **Bloqueia**: um dos AC precisa ter par (pergunta canônica, âncora esperada) definido antes de sair de inception, ou o defeito propaga para functional-design e build-and-test.
- **OBJECT**: "ou equivalente semântico" em AC1.4.1 e AC1.5.2 é assertion não-mecanicamente-verificável. Trocar por um contrato âncora (`"RH" in resposta ∧ recusa detectável por keyword`) resolve sem custo.
- **OBJECT**: AC1.8.2 depende de "metadata **ou observação de estilo**" para verificar que o modelo trocou. "Observação de estilo" precisa sair; se o payload de resposta do AgentCore Runtime não devolver o `modelId`, AC1.8.2 é intestável e deve ser marcada como validação manual explícita, não como AC testável.
- **OBJECT**: gaps sem AC — concorrência (NFR6.1), origem server-side do `session_id` (NFR3.2), resposta vazia como caso de FR9.1, e regressão do guardrail LGPD sob prompt injection via documento. Nenhum precisa virar story neste MVP, mas devem estar registrados em `stories.md § Assumptions & Open Questions` (que hoje diz "None") para que o time saiba que existem cenários de risco não cobertos.
- **OBJECT** (menor): AC1.8.4 mapeia para FR4.5 mas descreve semântica de FR4.1 / FR4.x-inexistente. Corrigir mapeamento ou aditar FR.
