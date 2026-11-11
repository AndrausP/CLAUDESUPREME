# [BACKEND] Núcleo determinístico e persistência local

- Status: COMPLETED
- Fase: C
- Estimativa: 3 dias
- Depende de: 002
- Responsável: Dev Backend

## O que fazer

Implementar bootstrap idempotente, classificador DIRECT/LEAN/STANDARD/DEEP, seleção mínima de competências, workflow persistente, budgets, checkpoints, handoffs, memória textual/SQLite, eventos JSONL/SQLite e recuperação.

## Critério de conclusão

- Funciona localmente sem Ledger, API key, servidor HTTP ou `sqlite3` CLI.
- Todos os 13 estados exigidos existem e transições inválidas falham de forma tipada.
- Persistência usa transação, IDs de correlação e payload sanitizado.
- Bootstrap detecta projeto, ambiente e tarefas interrompidas sem chamada LLM.
- Testes unitários do núcleo passam.

## Limites de arquivos

`src/orchestra/core/**`, `config/**`, `schemas/**`, `tests/unit/core/**`.

## Risco

Escolha de runtime precisa respeitar Windows e dependências ausentes.

## Contrato técnico consolidado

- Runtime: Python 3.12; Domain usa somente stdlib e não importa adapters.
- Ownership: `src/orchestra/{domain,application,infrastructure}/**`, `schemas/{task,transition,checkpoint,event,budget,error}*.json`, migrations e `tests/unit/core/**`.
- SQLite é fonte de verdade com WAL quando suportado, foreign keys, busy timeout, `user_version`, optimistic locking por `revision` e outbox na mesma transação.
- JSONL é exportação idempotente, nunca fonte autoritativa de transições.
- Entrada: DTOs validados por JSON Schema 2020-12. Saída: DTO ou erro tipado com `correlation_id`.
- `COMPLETED` exige critérios/evidências; `FAILED` e `CANCELLED` são terminais; retomada cria attempt/task filha.
- Bridge Claude, CLI, TUI, SDK e Ledger só acessam Application ports.

## Evidência de conclusão

- [x] Bootstrap idempotente, routing, budgets, workflow, checkpoints, memória, eventos e recuperação exercitados.
- [x] Dependências são revalidadas antes de `RUNNING`; bloqueio e liberação possuem regressões.
- [x] Cancelamento persiste checkpoint `pre-cancellation` antes de `CANCELLED`.
- [x] Suíte integrada 77/77 e categorias de núcleo aprovadas.

