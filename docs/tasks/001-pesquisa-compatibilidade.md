# [WRITER] Pesquisa oficial e matriz de compatibilidade

- Status: COMPLETED
- Fase: A
- Estimativa: 2 dias
- Depende de: Nenhuma
- Responsável: Writer, com evidências do Broker/Reader

## O que fazer

Consolidar as fontes oficiais atuais de plugins, skills, subagentes, hooks, agent teams, MCP, Agent SDK, headless, settings, telemetria, segurança/legal, Textual/Rich e Ink. Classificar cada recurso como NATIVO, CONDICIONAL, PERSONALIZADO ou NÃO SUPORTADO.

## Critério de conclusão

- `docs/research.md` contém links primários, data e versão observada do Claude Code.
- Matriz separa modo Native do modo Programmatic.
- Limitações de plugin agents, autenticação, custos estimados e TUI complementar estão explícitas.
- Nenhuma API, flag ou capacidade sem fonte é apresentada como existente.

## Limites de arquivos

Pode alterar somente `docs/research.md` e anexos em `docs/research/`.

## Risco

Documentação muda rapidamente; registrar versão e data evita congelar suposições.

## Evidência de conclusão

- `docs/research.md`, verificado em 2026-11-11 contra Claude Code 2.1.322.
- Matriz Native/Programmatic e classificação NATIVO/CONDICIONAL/PERSONALIZADO/NÃO SUPORTADO concluídas.
- Decisão técnica preparada para o Architect: Python 3.12, plugin native-first, SDK/Textual/Rich opcionais e agent teams fora do baseline.

## Reconciliação final

- [x] Fontes primárias e versão observada registradas.
- [x] Matriz Native/Programmatic e limitações explícitas.
- [x] QA aprovou coerência documental na suíte 77/77.

