# [FRONTEND] TUI complementar e design profissional

- Status: COMPLETED
- Fase: D
- Estimativa: 3 dias
- Depende de: 010
- Responsável: Dev Frontend + Designer

## O que fazer

Implementar TUI complementar com telas inicial, departamentos, agentes, esteira, tarefas, memória, skills/MCP, execução e timeline. Aplicar paleta e acessibilidade solicitadas sem substituir a UI do Claude Code.

## Critério de conclusão

- Tema usa `#0C0C0C`, `#BAF3DB`, `#C9372C` e neutros com contraste revisado.
- Resize, teclado, loading/empty/error e screen reader são considerados.
- TUI lança Claude Code por mecanismo documentado, sem controlar sessão não exposta.
- Ausência da dependência TUI cai para CLI simples.

## Limites de arquivos

`src/orchestra/tui/**`, `tests/integration/tui/**`, `docs/ui.md`.

## Risco

Textual/Ink precisam de decisão arquitetural; dependência deve ser opcional.

## Contrato técnico consolidado

- Decisão fechada: Textual + Rich como extra `tui`; Ink descartado no v1 para evitar segundo runtime.
- Ownership Frontend: `src/orchestra/tui/**` e testes; Designer possui `docs/ui.md`, fluxo, contraste, estados e tokens visuais.
- TUI consome Application ports e eventos; nunca abre SQLite diretamente.
- Import ausente, terminal legado ou falha de application mode volta à CLI sem perda de função.
- Telas mostram somente decisões observáveis, ações, evidências e estados; reasoning privado não é exposto.
- Paleta e teclado precisam de gate de contraste, resize, reduced-motion e screen reader.

## Evidência de conclusão

- [x] TUI complementar, tema e fallback estão implementados e cobertos estruturalmente.
- [x] Core e fallback plain/JSON passaram sem dependências opcionais.
- [ ] Runtime fullscreen Rich/Textual não foi exercitado: pacotes ausentes no host QA.

Conclusão com limitação: a task entrega o adapter opcional e a degradação segura; validação visual interativa completa permanece futura, sem bloquear o core.

