# Constraint Register - Chatbot de RH com Bedrock AgentCore

Restricoes rastreadas para esta iniciativa. Cada restricao carrega tipo,
origem e fonte. As restricoes desta pagina complementam o
`intent-statement.md` (fronteira de produto) e alimentam o `raid-log.md`
quando geram riscos, dependencias ou issues associados.

## Restricoes Tecnicas

| ID | Restricao | Tipo | Origem | Source |
|----|-----------|------|--------|--------|
| CT-1 | Sem integracao com sistemas externos (folha de pagamento, ERP, LDAP/AD, portal interno, tickets) | Fronteira tecnica | Escopo da demo | [Q1] |
| CT-2 | Base de conhecimento durante a demo e um snapshot fixo dos 5 documentos de RH; sem re-sync durante os 2 dias | Fronteira tecnica | Escopo da demo | [Q9 - intent-statement.md] |
| CT-3 | Time tem primeira exposicao a AgentCore Runtime, Bedrock Knowledge Bases e Strands Agents SDK; curva de aprendizado esperada | Capacidade do time | Perfil do time | [Q3] |

## Restricoes Organizacionais / Temporais

| ID | Restricao | Tipo | Origem | Source |
|----|-----------|------|--------|--------|
| CO-1 | Prazo fixo de 2 dias corridos para conclusao da demo | Temporal | Escopo da demo | [Q4] |
| CO-2 | Orcamento coberto pelos creditos da conta AWS de sandbox do workshop; sem investimento adicional necessario | Financeira | Ambiente do workshop | [Q4] |
| CO-3 | Sem deploy em producao; escopo limitado a demo funcional | Organizacional | Escopo da demo | [desc][Q8 - intent-statement.md] |
| CO-4 | Sem bloqueadores organizacionais conhecidos (sem change-freeze, sem aprovacao pendente, sem dependencia de outros times) | Organizacional | Ambiente do workshop | [Q5] |

## Restricoes de Ambiente AWS

| ID | Restricao | Tipo | Origem | Source |
|----|-----------|------|--------|--------|
| CA-1 | Regiao unica: `us-east-1` | Ambiente | Conta sandbox do workshop / disponibilidade de Bedrock e S3 Vectors | [Q6][desc] |
| CA-2 | Conta sandbox do workshop, com Bedrock ja habilitado e model access liberado para Claude, Nova, Llama, Titan e Cohere embed/rerank | Ambiente | Conta sandbox do workshop | [Q6] |
| CA-3 | S3 Vectors disponivel em `us-east-1` como vector store gerenciado | Ambiente | Disponibilidade de servico | [Q6][desc] |

## Restricoes de Compliance

| ID | Restricao | Tipo | Origem | Source |
|----|-----------|------|--------|--------|
| CC-1 | LGPD (Brasil) aplicavel a dados pessoais de colaboradores | Regulatoria | Legislacao brasileira | [Q2] |
| CC-2 | Politica interna: o bot NAO deve expor dados individuais (salario, historico pessoal, dados nominais) | Politica interna | Politica organizacional | [Q2] |
| CC-3 | HIPAA, PCI-DSS e SOC 2 nao aplicaveis a esta demo isolada em conta sandbox | Regulatoria | Escopo e ambiente | [Q2] |

## Restricoes Nao-Funcionais

| ID | Restricao | Tipo | Origem | Source |
|----|-----------|------|--------|--------|
| CN-1 | Latencia maxima de 5s por resposta | NFR - performance | intent-statement.md | [Q3 - intent-statement.md] |
| CN-2 | Idioma das respostas: portugues | NFR - qualidade | intent-statement.md | [Q3 - intent-statement.md] |
| CN-3 | Sem alvo definido para concorrencia (usuarios simultaneos), disponibilidade 24/7 ou metrica de custo por resposta | NFR - lacuna consciente | Escopo da demo | [Q7] |

## Assumptions & Open Questions

None.
