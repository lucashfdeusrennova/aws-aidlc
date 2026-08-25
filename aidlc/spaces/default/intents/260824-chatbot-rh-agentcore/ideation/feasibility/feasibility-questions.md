# Feasibility - Perguntas de Restricao e Viabilidade

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Q1. Com quais sistemas existentes esta iniciativa precisa integrar?

- A. Nenhum. Demo isolada; sem integracao com folha de pagamento, ERP, LDAP/AD, portal interno ou sistema de tickets.
- B. Somente leitura de documentos de RH ja publicados em um bucket S3 do workshop (sem integracao com sistemas transacionais).
- C. Integracao com sistema de autenticacao corporativo (SSO/AD).
- D. Not applicable.
- X. Other (please specify)

[Answer]:A

## Q2. Existem requisitos regulatorios ou de compliance aplicaveis?

- A. LGPD (Brasil) - dados pessoais de colaboradores nao sao expostos; base de conhecimento contem apenas politicas gerais. Sem obrigacao de mapear PII/PHI nas respostas do bot.
- B. LGPD + politica interna de "sem dados individuais" - o bot nao deve expor salario, historico pessoal ou dados nominais.
- C. HIPAA / PCI-DSS / SOC2 aplicavel.
- D. Nenhum requisito regulatorio formal para esta demo isolada.
- E. Not yet defined.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:B

## Q3. Qual e o perfil tecnico do time que executa a demo?

- A. Time com experiencia em AWS + Python; primeira exposicao a AgentCore Runtime, Bedrock Knowledge Bases e Strands Agents SDK.
- B. Time avancado em Bedrock e AgentCore ja em producao.
- C. Time iniciante em AWS; primeira exposicao ao ecossistema.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q4. Qual e o prazo e o orcamento desta demo?

- A. Prazo fixo de 2 dias corridos; orcamento coberto pelos creditos da conta AWS do workshop (sandbox).
- B. Prazo flexivel; sem restricao dura de tempo.
- C. Orcamento com teto especifico definido.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q5. Ha bloqueadores organizacionais que podem afetar a execucao?

- A. Nenhum bloqueador conhecido; demo isolada, conta de sandbox, sem dependencia de outros times.
- B. Change-freeze / freeze de deploy em algum sistema externo.
- C. Aprovacao pendente de lideranca para uso de IA Generativa.
- D. Dependencia de outro time para liberar acessos (IAM, Bedrock model access).
- E. Not identified.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q6. Qual conta AWS sera usada e quais servicos ja estao habilitados?

- A. Conta sandbox do workshop em `us-east-1`, com Bedrock ja habilitado e model access liberado para Claude, Nova, Llama, Titan e Cohere embed/rerank; S3 Vectors disponivel em `us-east-1`.
- B. Conta sandbox do workshop, mas Bedrock model access ainda nao foi liberado (precisa solicitar).
- C. Conta corporativa com restricoes de service catalog / SCP.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q7. Existe algum requisito nao-funcional adicional alem de latencia < 5s por resposta?

- A. Nao. Apenas latencia < 5s (ja em vision.md) e respostas em portugues.
- B. Precisamos suportar N usuarios simultaneos (definir N).
- C. Precisamos de disponibilidade 24/7 durante e apos a demo.
- D. Precisamos de metrica de custo por resposta.
- E. Not applicable.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
