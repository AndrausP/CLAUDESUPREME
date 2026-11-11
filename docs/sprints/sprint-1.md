# Sprint 1 — MVP vertical verificável

## Status

COMPLETED — implementação, QA, documentação e memória indexada.

## Objetivo

Entregar o primeiro fluxo ponta a ponta do Orchestra Core: pesquisa oficial consolidada, arquitetura aprovada, núcleo determinístico persistente e plugin Claude Code validável com um agente, uma skill e `/orchestra:clareza`.

## Capacidade e viabilidade

O produto completo é grande demais para um único sprint humano de 1 dev júnior em meio período. O Sprint 1 contém apenas o caminho crítico do MVP. As tasks 005–015 permanecem planejadas e sequenciadas para expansão após o gate do MVP, embora possam ser executadas em paralelo por uma cadeia de agentes quando não houver conflito de arquivos.

## Tasks executadas

- [x] 001 — Pesquisa e matriz de compatibilidade
- [x] 002 — Arquitetura, contratos e schemas
- [x] 003 — Núcleo determinístico e persistência local
- [x] 004 — Plugin vertical e `/orchestra:clareza`
- [x] 005 — Catálogo de 36 agentes
- [x] 006 — Catálogo de skills
- [x] 007 — Comandos e workflows
- [x] 008 — Memória e budgets
- [x] 009 — Segurança e extensões
- [x] 010 — CLI e fallback
- [x] 011 — TUI opcional, com runtime Rich/Textual não exercitado
- [x] 012 — Ledger/telemetria opcional, sem billing observado
- [x] 013 — Testes automatizados
- [x] 014 — Cenários/benchmark Windows, limitado a routing local
- [x] 015 — Documentação, memória e graphify

## Gate de saída

- `claude plugin validate . --strict` passa, ou limitações de versão são registradas com o comando realmente suportado.
- Núcleo executa sem Ledger, servidor HTTP, API key ou `sqlite3` CLI.
- Estado inválido é rejeitado; execução interrompida é recuperável.
- Skill e agente são descobertos sob namespace `orchestra`.
- Testes do MVP passam em Windows/PowerShell e saída sem cor é legível.

## Evidência do gate

- QA `APPROVED`: 77/77 testes, 23/23 categorias e 8/8 cenários.
- Plugin normal e profile directory aprovados.
- Wheel: 38.480 bytes, SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`.
- Fallback plain/JSON passou com `TERM=dumb` e `NO_COLOR`.

## Riscos residuais

- Rich/Textual fullscreen, aplicativo Ledger real e Agent SDK autenticado não foram executados.
- Benchmark não chama modelos, não mede billing e não compara um harness equivalente sem Orchestra.
- Marketplace ainda não foi publicado; `ICON_MISSING` é aviso opcional.
- A extração graphify não recebeu telemetria de tokens do subagente; o grafo não direcionado colapsou um par de endpoints recíprocos.

