# Personas - Chatbot de RH com Bedrock AgentCore

Personas derivadas de `stakeholder-map.md`, `requirements.md` (FR1.1-1.5, FR4)
e Q1 desta etapa. Uma persona primaria (Ana), duas sub-personas de contexto
especifico (Bruno para onboarding, Carla para avaliacao) e uma persona
operacional (Operador do time tecnico) para US4 (troca de modelo).

## Priority ranking

1. **P1 - Ana (Colaboradora)** - persona primaria, cobre a maior parte das
   interacoes.
2. **P2 - Bruno (Novo Funcionario)** - sub-persona de onboarding.
3. **P3 - Carla (Gestora)** - sub-persona de avaliacao de desempenho.
4. **P4 - Operador (Time tecnico do workshop)** - persona operacional para
   troca de modelo durante a demo (introduzida na triagem mob por objecao de
   design/developer sobre US1.8).

## P1. Ana - Colaboradora

**Papel**: colaboradora efetiva da empresa, tem duvidas cotidianas sobre
politicas de RH, ferias, beneficios e feriados.

**Objetivos**:

- Obter respostas claras e imediatas sobre politicas de RH sem depender do
  time de RH para cada duvida. [FR1.1, FR1.2, FR1.5]
- Consultar em portugues, em linguagem natural. [NFR2.1]
- Ter certeza de que a resposta e baseada nos documentos oficiais (nao
  inventada). [FR5.2]

**Dores**:

- Perder tempo abrindo PDFs para cada duvida simples.
- Respostas verbais do RH podem variar entre consultas.
- Nao saber se uma informacao ouvida esta atualizada.

**Contexto**:

- Adulto em ambiente de escritorio; conforto medio com aplicativos web (nao e
  desenvolvedora nem power user).
- Frequencia de uso: ~2-3 vezes por semana.
- Sem restricao declarada de acessibilidade nesta demo (alinhado a Q5 de
  `wireframes.md`).
- Usa a interface Streamlit no proprio notebook. [wireframes.md]
- Expectativa de latencia: <5s por resposta. [NFR1.1]
- Sabe que dados individuais (salario, cadastro pessoal) nao devem estar ali.
  [NFR4.1]

## P2. Bruno - Novo Funcionario

**Papel**: colaborador nos primeiros 30 dias de empresa, em processo de
onboarding.

**Objetivos**:

- Entender rapidamente o checklist e as etapas do onboarding. [FR1.3]
- Confirmar o que precisa ser feito nos primeiros dias.

**Dores**:

- Muita informacao nova simultaneamente; risco de esquecer etapas.
- Nao saber a quem perguntar cada tipo de duvida.

**Contexto**:

- Adulto, primeiro emprego ou primeira semana na empresa.
- Frequencia de uso: diaria nos primeiros 30 dias.
- Vocabulario interno ainda em construcao.
- Consulta com perguntas do tipo "o que preciso fazer antes de comecar a
  trabalhar no primeiro dia?"

## P3. Carla - Gestora

**Papel**: lider de equipe conduzindo um ciclo de avaliacao de desempenho.

**Objetivos**:

- Consultar as diretrizes de avaliacao antes de 1:1s. [FR1.4]
- Alinhar-se ao processo formal sem depender de treinamento presencial.

**Dores**:

- Cada ciclo tem regras diferentes; e facil aplicar criterios desatualizados.
- Nao pode consultar dados individuais de subordinados (LGPD - NFR4.1).

**Contexto**:

- Adulto, papel de gestao.
- Frequencia de uso: pontual (~2 semanas por ciclo de avaliacao).
- Perguntas analiticas ("qual a diferenca entre feedback continuo e avaliacao
  formal?").

## P4. Operador (Time tecnico do workshop)

**Papel**: membro do time tecnico que roda a demo, testa modelos e configura
o ambiente. Nao e um colaborador consumidor do bot.

**Objetivos**:

- Trocar o modelo de chat durante a demo para comparar qualidade e latencia
  entre pelo menos 2 modelos. [FR6, intent-backlog.md B-5]
- Confirmar visualmente qual modelo esta ativo em cada resposta.
- Preservar o historico de conversacao ao trocar de modelo, para permitir
  comparacao em contexto identico.

**Dores**:

- Modelos com prefixo `us.*` retornam `ResourceNotFoundException` se passados
  como foundation-model direto. [R-4 do raid-log.md, project.md § Mandated]
- Sem instrumentacao explicita do modelo usado, dificil distinguir "modelo
  novo respondeu" de "modelo antigo respondeu de novo".

**Contexto**:

- Perfil tecnico (Python + AWS), primeira exposicao a AgentCore Runtime.
  [feasibility Q3]
- Uso durante os 2 dias de workshop, dentro da conta sandbox.
- Nao consome respostas para uso proprio; observa e compara.

## Assumptions & Open Questions

None.
