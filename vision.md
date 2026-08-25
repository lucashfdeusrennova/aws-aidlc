# Chatbot de RH com Amazon Bedrock AgentCore - Vision

---

## Selected Use Case

- **Use Case Name:** Chatbot de RH (Recursos Humanos)
- **Context:** Demo de 2 dias. Construcao de um chatbot inteligente que responde perguntas de colaboradores sobre politicas de RH, ferias, onboarding e avaliacoes de desempenho. Utiliza Amazon Bedrock AgentCore Runtime como runtime gerenciado para o agente, Bedrock Knowledge Bases + S3 Vectors para RAG, e Strands Agents SDK como framework.
- **Why this use case was selected:** Projeto simples, de alto impacto e com dominio bem definido. Documentos de RH sao estruturados e frequentemente consultados, o que torna o RAG altamente eficaz. Ideal para equipes iniciantes demonstrarem o valor de IA Generativa com infraestrutura de agente em producao em 2 dias.

---

## VISION STATEMENT

### Problem Statement

Colaboradores precisam consultar manualmente documentos de RH (manual do funcionario, politicas de ferias, checklist de onboarding) para tirar duvidas do dia a dia, o que consome tempo e frequentemente gera respostas inconsistentes ou desatualizadas.

### Core Problem

Nao existe um canal automatizado que interprete perguntas em linguagem natural sobre politicas de RH e retorne respostas precisas com base na documentacao oficial da empresa.

### Target Users

- Colaboradores com duvidas sobre politicas de RH, ferias, beneficios
- Novos funcionarios em processo de onboarding
- Gestores que precisam consultar diretrizes de avaliacao de desempenho

### Desired Outcome

- Respostas automaticas e precisas sobre politicas de RH em linguagem natural
- Reducao do volume de chamados e emails repetitivos para o time de RH
- Onboarding mais autonomo para novos colaboradores
- Disponibilidade 24/7 sem dependencia de atendentes humanos

### Success Vision

Ao final dos 2 dias de demo, o chatbot responde corretamente perguntas sobre politicas de ferias, processo de onboarding, avaliacoes de desempenho e feriados da empresa, com base nos documentos de RH fornecidos. A equipe consegue trocar modelos (chat e embedding) e observar diferencas de qualidade e latencia. O agente roda em AgentCore Runtime com sessao isolada.

### Unique Value

- Runtime 100% gerenciado (AgentCore Runtime) - sessoes isoladas em microVM, sem servidor/container
- Agente deployado com poucas linhas usando Strands Agents SDK
- Knowledge Bases para RAG (busca semantica nos documentos de RH)
- Memoria de conversacao via AgentCore Memory
- Interface web simples (Streamlit) - deploy rapido sem conhecimento de frontend
- Modelos intercambiaveis - equipe pode testar diferentes combinacoes de chat + embedding

### Success Criteria

- **Funcional:** Chatbot responde corretamente perguntas sobre todos os 5 documentos da base
- **Qualidade:** Respostas em portugues, claras e com referencia ao documento fonte
- **Velocidade:** Resposta em menos de 5 segundos
- **Experimentacao:** Equipe testou pelo menos 2 modelos de chat e comparou resultados

---

## Constraints

- **Must use:** Python, Amazon Bedrock AgentCore Runtime, Bedrock Knowledge Bases + S3 Vectors, Strands Agents SDK, regiao `us-east-1` (ver `tech-env.md`)
- **Compliance / security:** Respostas nao devem expor informacoes individuais de funcionarios. IAM para controle de acesso. Sessoes isoladas em microVM (garantido pelo AgentCore Runtime).
- **Non-functional targets:** Latencia < 5s por resposta

## Out of Scope

- Integracoes com sistemas de folha de pagamento ou ERP
- Acoes transacionais (solicitar ferias, abrir chamado)
- Treinamento/fine-tuning de modelos customizados
- Atendimento por voz
- Acesso a dados individuais de funcionarios (salario, historico pessoal)
- Deploy em producao (escopo limitado a demo funcional)

## Open Questions

- [ ] Os documentos de RH serao atualizados com que frequencia no S3?
- [ ] Qual o canal final de integracao apos a demo? (Slack, WhatsApp, portal interno)
