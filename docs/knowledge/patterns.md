# Padrões validados

| Data | Padrão | Motivo | Evidência | Agente |
|---|---|---|---|---|
| 2026-11-11 | Core determinístico stdlib, com adapters opcionais nas bordas. | Mantém routing, estado, budgets e recuperação testáveis sem Claude, Ledger, TUI ou rede. | 77/77 testes; execução sem Ledger aprovada. | Architect + QA |
| 2026-11-11 | SQLite como fonte autoritativa e JSONL como exportação idempotente. | Transações e outbox preservam consistência; consumidores não precisam acessar o banco privado. | Categorias de recuperação, eventos e Ledger aprovadas. | Architect + QA |
| 2026-11-11 | Skills namespaced `/orchestra:*` com progressive disclosure. | Evita colisões globais e carrega instrução detalhada somente quando usada. | 36 skills primárias, 19 command skills e plugin validator aprovados. | Architect + QA |
| 2026-11-11 | Validar dependências imediatamente antes de `READY -> RUNNING`. | Uma task pode ficar stale entre planejamento e execução; o gate tardio impede iniciar com pré-condição ausente. | Regressões bloqueiam dependência inexistente/incompleta e liberam dependências `COMPLETED`. | Dev Backend + QA |
| 2026-11-11 | Cancelamento salva checkpoint `pre-cancellation` antes do estado terminal. | Preserva estado anterior, motivo, evidências e ponto seguro de retomada. | Teste de cancelamento seguro aprovado e checkpoint exposto pela CLI. | Dev Backend + QA |
| 2026-11-11 | Command skills são verificadas contra o parser real. | Documentação manual diverge facilmente da CLI e pode duplicar flags globais. | 19 exemplos aceitos; nenhum `--json --json`. | Dev Backend + QA |
| 2026-11-11 | Renderer plain/JSON é baseline; Rich/Textual são extras. | `TERM=dumb`, `NO_COLOR`, CI e terminais legados precisam permanecer funcionais. | Smoke plain/JSON e wrappers Windows/POSIX aprovados; runtime Rich/Textual não foi exercitado. | Dev Frontend + QA |
| 2026-11-11 | Artefato de release é reproduzido e identificado por hash. | Um checksum explícito liga documentação ao wheel realmente validado. | Wheel 38.480 bytes, SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`. | QA |
