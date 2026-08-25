# Intent Capture - Perguntas de Enquadramento

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Q1. Qual e o problema de negocio que estamos resolvendo?

- A. Colaboradores gastam tempo procurando respostas em documentos de RH (manual do funcionario, politica de ferias, onboarding), gerando respostas inconsistentes e desatualizadas, e sobrecarregando o time de RH com chamados repetitivos.
- B. Onboarding de novos funcionarios e lento por falta de canal de auto-atendimento.
- C. Time de RH nao consegue escalar atendimento com o crescimento da empresa.
- D. Nao identificado.
- X. Other (please specify)

[Answer]:A, B, C

## Q2. Quem e o cliente (colaborador atendido) e qual a dor especifica?

- A. Colaboradores em geral com duvidas sobre politicas de RH, ferias e beneficios.
- B. Novos funcionarios em processo de onboarding.
- C. Gestores consultando diretrizes de avaliacao de desempenho.
- D. Todos os itens acima (A, B, C).
- E. Not identified.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q3. Como e o sucesso? Quais metricas importam para esta demo de 2 dias?

- A. Chatbot responde corretamente perguntas sobre os 5 documentos da base, em portugues, com referencia ao documento fonte, em menos de 5s.
- B. Equipe testa e compara pelo menos 2 modelos de chat (qualidade x latencia).
- C. Reducao mensuravel do volume de chamados/emails de RH (metrica de longo prazo, fora do escopo da demo).
- D. Todos os anteriores.
- E. Not yet defined.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q4. Qual e o gatilho desta iniciativa (por que agora)?

- A. Oportunidade tecnica: demonstrar valor de IA Generativa com AgentCore Runtime em producao em 2 dias.
- B. Pressao operacional: RH sobrecarregado com perguntas repetitivas.
- C. Regulatorio / compliance: precisamos padronizar respostas sobre politicas.
- D. Not identified.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q5. Quem sao os stakeholders principais e o que cada um se importa?

- A. Time de RH (dono do conteudo, valida qualidade das respostas), Colaboradores (usuarios finais), Time tecnico do workshop (executor).
- B. Somente time tecnico do workshop (demo interna).
- C. RH + Lideranca de tecnologia (sponsor).
- D. Not identified.
- X. Other (please specify)

[Answer]:A

## Q6. Quem decide escopo e prioridade, e quem influencia essas decisoes?

- A. Time tecnico do workshop decide escopo (limitado a demo de 2 dias); vision.md e tech-env.md sao as diretrizes.
- B. RH decide o que entra na base de conhecimento; time tecnico decide arquitetura.
- C. Um sponsor especifico (lideranca) decide prioridade.
- D. Not identified.
- X. Other (please specify)

[Answer]:A

## Q7. Ha requisitos de comunicacao ou cadencia de reporte?

- A. Nao. Demo isolada de 2 dias, sem relatorio formal.
- B. Sim, demo/apresentacao final ao encerrar os 2 dias.
- C. Sim, checkpoints diarios com o time tecnico.
- D. Not applicable.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Q8. O workflow foi iniciado com escopo `mvp` - isso corresponde a fronteira de produto pretendida?

- A. Confirmo `mvp`: chatbot funcional respondendo em cima dos 5 documentos de RH, sem integracoes externas, sem deploy em producao. Fronteira igual a `vision.md`.
- B. Confirmo `mvp` mas com ajuste na fronteira (descrever em Other).
- C. A fronteira de produto e diferente do escopo `mvp` do workflow (descrever em Other).
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct

## Assumption Confirmation

Suposicoes retidas nos artefatos:

- `intent-statement.md`: a frequencia de atualizacao dos documentos de RH no S3 nao foi definida; a demo assume snapshot fixo dos 5 documentos.
- `intent-statement.md`: o canal final de integracao pos-demo (Slack, WhatsApp, portal interno) ainda nao foi decidido; esta fora do escopo `mvp`.
- `stakeholder-map.md`: a participacao do time de RH como validador do conteudo esta implicita pela sua funcao de dono dos documentos, mas nao foi formalizada nesta captura de intencao.
- `stakeholder-map.md`: nao foi identificado sponsor de lideranca (RH ou tecnologia) para esta demo alem do time tecnico do workshop.

Opcoes:

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: B. Convert to follow-up questions

## Q9. Frequencia de atualizacao dos documentos de RH no S3 durante a demo

- A. Snapshot fixo dos 5 documentos durante os 2 dias da demo; sem re-sync.
- B. Snapshot inicial, mas equipe pode re-sync manual da Knowledge Base ao trocar embedding.
- C. Atualizacao continua (fora do escopo desta demo).
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q10. Canal final de integracao pos-demo (Slack, WhatsApp, portal interno)

- A. Fora do escopo desta demo; sera decidido depois. Registrar como "nao decidido".
- B. Definido: Slack.
- C. Definido: WhatsApp.
- D. Definido: portal interno.
- E. Not yet defined.
- X. Other (please specify)

[Answer]:E

## Q11. Papel formal do time de RH nesta demo

- A. Time de RH e dono do conteudo da base e valida qualidade das respostas do chatbot.
- B. Time de RH apenas fornece os documentos; validacao de qualidade fica com o time tecnico.
- C. Time de RH nao esta envolvido nesta demo (documentos ja foram fornecidos previamente).
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q12. Sponsor de lideranca desta demo

- A. Nao ha sponsor de lideranca formal; o time tecnico do workshop conduz sozinho.
- B. Sponsor de RH.
- C. Sponsor de tecnologia / lideranca de engenharia.
- D. Sponsor de RH e sponsor de tecnologia em conjunto.
- E. Not identified.
- X. Other (please specify)

[Answer]:A
