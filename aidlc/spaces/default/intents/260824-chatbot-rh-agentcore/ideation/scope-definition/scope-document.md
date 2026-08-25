# Scope Document - Chatbot de RH com Bedrock AgentCore

Este documento consolida a fronteira de escopo do MVP para a demo de 2 dias.
Consome e refina a fronteira ja capturada em `intent-statement.md`, respeita
as restricoes do `constraint-register.md` e adota como base a viabilidade
avaliada em `feasibility-assessment.md`.

## MVP - Escopo Minimo Viavel

O MVP entrega valor no fim do dia 2 sendo composto por: um chatbot funcional
que responde perguntas sobre os 5 documentos de RH via Streamlit, com resposta
em portugues em menos de 5s por resposta, citando o documento fonte quando
aplicavel; e a capacidade de trocar o modelo de chat via configuracao para
comparar qualidade e latencia com pelo menos 2 modelos testados. [Q1]

Nao entram no MVP a troca de modelo de embedding, reranker, observabilidade
formal, IaC completo ou deploy em producao. [Q1][Q4][Q5]

## Fronteira Dentro (In Scope)

- Base de conhecimento indexada com os 5 documentos de RH em Bedrock
  Knowledge Bases + S3 Vectors (`employee_handbook.pdf`, `leave_policy.pdf`,
  `onboarding_checklist.pdf`, `performance_review_guidelines.pdf`,
  `public_holidays.csv`). [Q1][Q2][desc]
- Agente construido com Strands Agents SDK rodando no AgentCore Runtime,
  usando a tool `retrieve` para RAG na Knowledge Base. Necessario para o
  MVP definido em [Q1] rodar de ponta a ponta.
- Frontend Streamlit chamando `invoke_agent_runtime` via boto3. Necessario
  para o MVP definido em [Q1].
- Prompt de sistema com regra explicita "sem dados individuais" (LGPD +
  politica interna registrada em `constraint-register.md` CC-1/CC-2).
  Necessario para manter a viabilidade de compliance avaliada em
  `feasibility-assessment.md`.
- Troca de modelo de chat via configuracao para experimentacao (pelo menos
  2 modelos comparados em qualidade e latencia). [Q1]
- Regiao unica `us-east-1` conforme `constraint-register.md` CA-1. [Q1]

## Fronteira Fora (Out of Scope / Won't Have)

Consolidacao das exclusoes de `intent-statement.md`, `constraint-register.md`
e respostas de [Q5]:

- Integracoes com sistemas transacionais (folha de pagamento, ERP, LDAP/AD,
  portal interno, tickets). [Q5][constraint-register.md CT-1]
- Acoes transacionais (solicitar ferias, abrir chamado, alterar cadastro).
  [Q5]
- Atendimento por voz. [Q5]
- Acesso a dados individuais de colaboradores (salario, historico pessoal).
  [Q5][constraint-register.md CC-2]
- Treinamento / fine-tuning de modelos customizados. [Q5]
- Deploy em producao. [Q5][constraint-register.md CO-3]
- Reindexacao continua da Knowledge Base durante a demo (snapshot fixo).
  [constraint-register.md CT-2]
- Historico de conversacao persistido (AgentCore Memory) - se possivel roda,
  mas nao e requisito de MVP. [Q2]
- Alvos formais de concorrencia (N usuarios), disponibilidade 24/7 ou custo
  por resposta. [constraint-register.md CN-3]

## Sequenciamento

A ordem preferida de construcao e **risk-first**: comecar pelo componente
de maior incerteza tecnica (agente Strands rodando no AgentCore Runtime),
depois integrar a Knowledge Base, depois plugar o frontend Streamlit. [Q6]

Esta ordem alinha com o risco R-1 do `raid-log.md` (curva de aprendizado
em AgentCore e Strands) - resolver o componente novo primeiro protege o
prazo de 2 dias.

## Prazos

Prazo unico: demo funcional no fim do dia 2. Sem prazos duros amarrados a
capacidades individuais. [Q7][constraint-register.md CO-1]

## Assumptions & Open Questions

None.
