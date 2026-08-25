# Intent Statement - Chatbot de RH com Bedrock AgentCore

## Problem Statement

Colaboradores gastam tempo procurando respostas em documentos de RH (manual do funcionario, politica de ferias, onboarding), o que gera respostas inconsistentes e desatualizadas e sobrecarrega o time de RH com chamados repetitivos; alem disso, o onboarding de novos funcionarios e lento por falta de canal de auto-atendimento, e o time de RH nao consegue escalar atendimento com o crescimento da empresa. [Q1]

O nucleo do problema e a ausencia de um canal automatizado que interprete perguntas em linguagem natural sobre politicas de RH e retorne respostas precisas com base na documentacao oficial da empresa. [desc][Q1]

## Target Customer

Colaboradores em geral com duvidas sobre politicas de RH, ferias e beneficios sao o publico primario desta iniciativa. [Q2]

O beneficio direto e ter respostas automaticas, precisas e disponiveis a qualquer momento sobre politicas de RH, sem depender de intervencao humana para cada duvida cotidiana. [Q1][Q2]

## Success Metrics

Para a demo de 2 dias, o sucesso e medido por uma unica condicao objetiva: o chatbot responde corretamente perguntas sobre os 5 documentos da base, em portugues, com referencia ao documento fonte, em menos de 5s por resposta. [Q3]

| Metrica | Alvo | Fonte |
|---------|------|-------|
| Corretude funcional | Chatbot responde corretamente perguntas sobre os 5 documentos da base de conhecimento | [Q3] |
| Idioma | Respostas em portugues | [Q3] |
| Rastreabilidade | Cada resposta cita o documento fonte quando aplicavel | [Q3] |
| Latencia | Menos de 5s por resposta | [Q3] |

## Initiative Trigger

O gatilho e uma oportunidade tecnica: demonstrar valor de IA Generativa com Amazon Bedrock AgentCore Runtime em producao em 2 dias, usando um caso de uso com dominio bem definido e alto impacto para colaboradores. [Q4][desc]

## Initial Scope Signal

| Sinal de escopo | Valor | Fonte |
|-----------------|-------|-------|
| Workflow-selected scope | `mvp` (definido pelo workflow no start) | [scope] (workflow-selected) |
| Fronteira de produto confirmada pelo usuario | Chatbot funcional respondendo em cima dos 5 documentos de RH, sem integracoes externas e sem deploy em producao | [Q8] |
| Base de conhecimento durante a demo | Snapshot fixo dos 5 documentos durante os 2 dias da demo, sem re-sync | [Q9] |
| Canal final de integracao pos-demo | Nao definido nesta captura; fora do escopo `mvp` | [Q10] |

O escopo confirmado esta alinhado ao workflow-selected `mvp` e corresponde a uma demo funcional de 2 dias, com fronteira igual a descrita na intencao inicial. [Q8][desc]

## Assumptions & Open Questions

None.

## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-08-24T15:35:22Z
**Iteration:** 2
**Review class:** advisory

**Findings:**

- Nenhum defeito com evidencia que justifique NOT-READY. Conteudo semanticamente inalterado desde a iteracao 1 (recovery pass motivado por re-save apos correcao de hook do Kiro IDE, nao por revisao de conteudo). Reconfirmado item a item: (1) todo bloco substantivo (paragrafos, itens de tabela) carrega tag inline resolvivel contra o `## Sources` do `intent-capture-questions.md` - `[desc]`, `[scope]`, `[Q1]`-`[Q12]`; (2) ambos os artefatos declaram `## Assumptions & Open Questions: None.` apos o loop Q9-Q12 ter fechado as quatro suposicoes; (3) `[scope]` aparece rotulado como `workflow-selected` na linha "Workflow-selected scope" e esta separado da fronteira confirmada pelo usuario, ancorada em `[Q8]`; (4) metricas de sucesso sao objetivas e testaveis (corretude nos 5 documentos, idioma pt-BR, citacao do documento fonte, latencia <5s por resposta); (5) nenhum item nao selecionado foi convertido em exclusao factual ou requisito - as linhas "Checkpoints diarios" e "Apresentacao final" no `stakeholder-map.md` mantem redacao neutra ("nao definidos" / "nao confirmada"), permanecendo dentro do contrato de grounding.

**Suggestions:**

- `stakeholder-map.md` - secao "Communication Requirements": as linhas "Checkpoints diarios" e "Apresentacao final ao fim dos 2 dias" enumeram opcoes nao escolhidas em Q7 (a resposta foi apenas A). Estao ancoradas em [Q7] e apresentadas como "nao definidos" / "nao confirmada", portanto nao configuram exclusao factual, mas a tabela ficaria mais enxuta reduzindo a unica linha positiva de Q7 - evita a impressao de que opcoes alternativas foram avaliadas e rejeitadas.
- `intent-statement.md` - Problem Statement, segundo paragrafo ("O nucleo do problema e a ausencia de um canal automatizado..."): e uma parafrase-sintese razoavel, mas incorpora o conceito de "canal automatizado / linguagem natural / documentacao oficial" que vem mais de `[desc]` do que de Q1. As tags [desc][Q1] cobrem, mas se quiser reduzir o grau de inferencia, colar mais perto do texto literal de Q1 (respostas inconsistentes, sobrecarga do RH) deixa o claim ainda mais direto.
- `stakeholder-map.md` - linha "`vision.md` e `tech-env.md`" em Decision-Makers vs Influencers: documentos de referencia nao sao stakeholders no sentido estrito da secao. A informacao e util e sourced ([Q6][desc]), mas talvez caiba melhor como nota abaixo da tabela ou dentro da linha "Time tecnico do workshop" (o que ele usa como diretriz), preservando a tabela para atores decisorios.
