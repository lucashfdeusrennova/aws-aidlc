# Requirements Analysis - Perguntas de Refinamento

## Sources

- [desc] Initial description: "Chatbot de RH com Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK e Streamlit. Ver vision.md e tech-env.md na raiz do workspace."
- [scope] Workflow-selected scope: `mvp`.

## Q1. Tipos de pergunta que o chatbot deve responder (cobertura funcional)

Marque todos os casos de uso que sao obrigatorios no MVP:
- A. Politicas gerais de RH (baseado em `employee_handbook.pdf`)
- B. Ferias, licencas e afastamentos (baseado em `leave_policy.pdf`)
- C. Onboarding de novos funcionarios (baseado em `onboarding_checklist.pdf`)
- D. Avaliacao de desempenho (baseado em `performance_review_guidelines.pdf`)
- E. Feriados da empresa (baseado em `public_holidays.csv`)
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply). Recomendacao: todos (A-E) para cobrir os 5 documentos do escopo.*

[Answer]:A, B, C, D, E

## Q2. Comportamento quando o bot nao encontra a informacao na base

- A. Responder "Nao encontrei essa informacao nos documentos. Sugiro contatar o time de RH." (default do system prompt em `tech-env.md`).
- B. Tentar responder com conhecimento geral do modelo (nao recomendado - risco de invencao).
- C. Recusar responder e sugerir buscar em outro canal.
- D. Not yet defined.
- X. Other (please specify)

[Answer]:A

## Q3. Volume esperado de sessoes simultaneas durante a demo

- A. 1-3 sessoes simultaneas (time tecnico do workshop testando).
- B. 5-10 sessoes simultaneas (turma inteira interagindo).
- C. 10+ sessoes simultaneas.
- D. Sem alvo definido - AgentCore Runtime gerencia sozinho (microVM por sessao).
- X. Other (please specify)

[Answer]:A

## Q4. Historico de conversacao por sessao (AgentCore Memory)

O intent-backlog classifica B-11 (AgentCore Memory) como Should Have.

- A. Should Have: se sobrar tempo, habilitar historico de conversacao dentro da mesma sessao (`session_id` estavel enquanto a aba estiver aberta).
- B. Must Have: precisa funcionar no MVP - reformular perguntas assumindo contexto ("e para gestantes?") depende do historico.
- C. Fora do escopo: cada pergunta e stateless.
- X. Other (please specify)

[Answer]:A

## Q5. Comportamento quando o input excede 4000 caracteres

- A. Rejeitar no frontend com aviso amigavel ("Sua pergunta ultrapassa 4000 caracteres. Reformule mais curto.") e nao chamar o agente.
- B. Truncar automaticamente para 4000 e chamar o agente.
- C. Deixar o `ValueError` do `src/invoke.py` vazar para a UI (comportamento default do error handling).
- X. Other (please specify)

[Answer]:A

## Q6. Metrica de sucesso pos-demo (metrica de longo prazo)

Alem da corretude na demo, ha alguma metrica de sucesso longitudinal a monitorar?

- A. Nenhuma - metrica de sucesso e apenas a demo funcional em 2 dias (`intent-statement.md`).
- B. Reducao mensuravel do volume de chamados/emails de RH (registrar como metrica futura, fora do escopo do MVP).
- C. NPS/CSAT do chatbot (registrar como futuro).
- D. Not applicable.
- X. Other (please specify)

*Pode marcar mais de uma opcao (select all that apply).*

[Answer]:A

## Consolidated Summary Confirmation

- Looks correct
- Request changes

[Answer]: Looks correct
