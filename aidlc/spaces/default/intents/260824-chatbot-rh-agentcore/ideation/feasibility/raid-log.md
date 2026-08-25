# RAID Log - Chatbot de RH com Bedrock AgentCore

Riscos, Suposicoes (Assumptions), Issues e Dependencias registrados para esta
iniciativa. Referenciam o `intent-statement.md`, o `constraint-register.md` e
as fontes registradas em `feasibility-questions.md`.

## Riscos

| ID | Risco | Probabilidade | Impacto | Severidade | Mitigacao | Source |
|----|-------|---------------|---------|------------|-----------|--------|
| R-1 | Curva de aprendizado do time em AgentCore Runtime + Strands Agents SDK + Bedrock Knowledge Bases estoura o prazo de 2 dias | Media | Alto | Alto | Comecar pelo exemplo minimo de Strands + KB antes de integrar AgentCore; usar `tech-env.md` como referencia; reservar tempo para leitura de docs no dia 1 | [Q3][Q4] |
| R-2 | Bot expor dados individuais de colaborador em uma resposta (violando politica LGPD interna descrita em `constraint-register.md` CC-1/CC-2) | Baixa | Alto | Medio | Prompt de sistema com regra explicita "sem dados individuais"; base de conhecimento contem apenas politicas gerais; validacao manual das respostas na demo | [Q2] |
| R-3 | Latencia > 5s por resposta em algum modelo de chat testado (viola NFR CN-1 do `constraint-register.md`) | Media | Medio | Medio | Comecar com o modelo recomendado por `tech-env.md` (baixa latencia); trocar apenas apos baseline funcionar; medir latencia por modelo antes da demo | [Q7 - intent-statement.md] |
| R-4 | Modelo com prefixo `us.*` retorna `ResourceNotFoundException` se passado como foundation-model direto em vez de via inference profile | Media | Medio | Medio | Seguir a orientacao de `tech-env.md` sobre uso de inference profile para modelos `us.*`; validar cada modelo antes de trocar em producao da demo | [desc] |
| R-5 | Reindexacao da Knowledge Base necessaria ao trocar modelo de embedding pode consumir tempo alem do previsto no dia 2 | Baixa | Medio | Baixo | Fixar o modelo de embedding para a demo (evitar troca no dia 2); documentar procedimento para consumo pos-demo | [desc] |

## Suposicoes (Assumptions)

| ID | Suposicao | Como sera validada | Source |
|----|-----------|--------------------|--------|
| A-1 | Os 5 documentos de RH previstos estarao disponiveis para upload no S3 antes do dia 1 da demo | Verificar upload dos arquivos previstos na conta sandbox antes de iniciar a Construction | [desc] |
| A-2 | O time podera trabalhar em ambos os dias sem interrupcoes por outras atividades | Compromisso do time; confirmar cronograma na abertura do dia 1 | [Q4] |
| A-3 | A conta sandbox permanecera valida e sem revogacao de acessos durante os 2 dias | Verificar credenciais e permissoes no inicio do dia 1 | [Q6] |

## Issues

Nenhum issue identificado no momento desta captura de viabilidade.

## Dependencias

| ID | Dependencia | Tipo | Bloqueador? | Source |
|----|-------------|------|-------------|--------|
| D-1 | Bedrock model access liberado em `us-east-1` para as familias previstas (Claude, Nova, Llama, Titan, Cohere embed/rerank) | Servico AWS | Nao (ja liberado) | [Q6] |
| D-2 | S3 Vectors disponivel em `us-east-1` como vector store gerenciado da Knowledge Base | Servico AWS | Nao (ja disponivel) | [Q6][desc] |
| D-3 | 5 documentos de RH (`employee_handbook.pdf`, `leave_policy.pdf`, `onboarding_checklist.pdf`, `performance_review_guidelines.pdf`, `public_holidays.csv`) a serem carregados no bucket S3 vinculado a Knowledge Base | Conteudo (RH / time do workshop) | Sim (necessario antes de indexar a KB) | [desc] |

## Assumptions & Open Questions

None.
