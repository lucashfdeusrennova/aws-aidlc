# Feasibility Assessment - Chatbot de RH com Bedrock AgentCore

Este documento avalia a viabilidade tecnica, organizacional e de compliance do
`intent-statement.md` desta iniciativa, dentro do escopo `mvp` de uma demo de
2 dias.

## Viabilidade Tecnica

A iniciativa e considerada viavel para o escopo desta demo. [Q3][Q4][Q6]

O time responsavel possui experiencia previa em AWS e Python e tera primeira
exposicao aos servicos-chave (AgentCore Runtime, Bedrock Knowledge Bases e
Strands Agents SDK), o que introduz curva de aprendizado mas nao inviabiliza
a entrega no prazo definido. [Q3]

A conta AWS de sandbox do workshop, em `us-east-1`, ja possui Bedrock
habilitado com model access liberado para as familias de modelos previstas
(Claude, Nova, Llama, Titan e Cohere embed/rerank) e S3 Vectors disponivel na
regiao, o que elimina o risco de bloqueio por liberacao de servico ou modelo.
[Q6]

O escopo confirmado no `intent-statement.md` (chatbot funcional sobre 5
documentos de RH, sem integracoes externas e sem deploy em producao) mantem
a superficie de risco reduzida e compativel com o prazo de 2 dias. [Q1][Q4]

## Viabilidade Organizacional

Nao foram identificados bloqueadores organizacionais para esta demo. [Q5]

O time tecnico do workshop decide sozinho o escopo desta demo (registrado no
`stakeholder-map.md`), a demo e isolada, sem dependencia de outros times e
sem change-freeze aplicavel. [Q5]

O orcamento esta coberto pelos creditos da conta AWS de sandbox do workshop,
o que remove a necessidade de aprovacao de investimento adicional. [Q4]

## Viabilidade de Compliance

O quadro regulatorio aplicavel e a LGPD combinada a uma politica interna de
"sem dados individuais": o bot nao deve expor salario, historico pessoal ou
dados nominais de colaboradores. [Q2]

Como a base de conhecimento contem apenas politicas gerais de RH e nao
carrega registros pessoais, o risco de vazamento de dados individuais e
controlavel via prompt de sistema (regras explicitas de nao exposicao) e via
o proprio conteudo indexado. Nao ha PII/PHI a mapear nas respostas do bot.
[Q2]

Como esta e uma demo isolada em conta sandbox e nao ha deploy em producao,
nao se aplicam frameworks HIPAA, PCI-DSS ou SOC 2 nesta iniciativa. [Q2]

## Requisitos Nao-Funcionais Adicionais

Alem da restricao ja capturada no `intent-statement.md` (latencia < 5s por
resposta e respostas em portugues), nao ha requisitos nao-funcionais
adicionais definidos para esta demo. [Q7]

Nao ha alvo especifico de concorrencia (numero de usuarios simultaneos),
disponibilidade 24/7 ou metrica de custo por resposta acordado para esta
demo. [Q7]

## Conclusao

A iniciativa e considerada viavel dentro do escopo `mvp` e do prazo de 2
dias, com risco tecnico concentrado na curva de aprendizado dos servicos
novos para o time e risco de compliance mitigado pela ausencia de dados
individuais na base e pela isolacao da conta sandbox. Riscos, suposicoes,
issues e dependencias estao registrados em `raid-log.md`, e todas as
restricoes duras e imposicoes externas estao consolidadas em
`constraint-register.md`. [Q3][Q4][Q5][Q6][Q7]

## Assumptions & Open Questions

None.
