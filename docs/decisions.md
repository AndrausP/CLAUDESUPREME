# Decisões arquiteturais

## Sessão 2026-11-11

As decisões abaixo foram aprovadas na arquitetura do Orchestra Core. Mudanças exigem novo ADR; não se alteram silenciosamente por conveniência de implementação.

| ADR | Decisão | Motivo | Agente |
|---|---|---|---|
| ADR-001 | Adotar Python 3.12 e biblioteca padrão no núcleo e na CLI. | O ambiente possui Python compatível; `sqlite3`, `argparse`, JSON e filesystem atendem o baseline sem runtime ou dependência obrigatória adicional. | Architect |
| ADR-002 | Manter core determinístico com limites hexagonais: adapters dependem dos application services e do domínio, nunca o contrário. | Estado, routing, budgets e validação precisam permanecer testáveis e corretos sem Claude, rede, TUI ou Ledger. | Architect |
| ADR-003 | Usar SQLite como fonte autoritativa, outbox transacional e JSONL como exportação interoperável. | SQLite fornece consistência, migrações e recuperação local; JSONL desacopla consumidores sem virar fonte de verdade para transições. | Architect |
| ADR-004 | Priorizar o modo Claude Code Native; Agent SDK é adapter opcional. | Plugin, skills, subagentes e hooks oficiais atendem o uso interativo sem API própria, enquanto o SDK exige pacote, autenticação e configuração adicionais. | Architect |
| ADR-005 | Criar novas ações como skills namespaced `/orchestra:*`, preservando `commands/` apenas para compatibilidade legada. | Skills são o formato atual, suportam progressive disclosure e o namespace evita colisões com comandos/plugins globais. | Architect |
| ADR-006 | Tornar Rich e Textual extras opcionais; manter renderer stdlib, `--plain`, `--json` e `NO_COLOR`. | O baseline observado inclui `TERM=dumb`, CP850 e ausência dessas bibliotecas; a administração não pode depender de fullscreen ou ANSI. | Architect |
| ADR-007 | Não depender de agent teams para correção ou execução básica. | Agent teams permanecem condicionais/experimentais; subagentes e o core determinístico oferecem baseline verificável. | Architect |
| ADR-008 | Integrar Claude Ledger por manifesto/eventos unilaterais e versionados, sem servidor permanente. | Orchestra deve funcionar sozinho e o Ledger deve observar/administrar sem tornar-se segundo orquestrador ou acessar estado privado diretamente. | Architect |
| ADR-009 | Começar memória com Markdown/JSON, índice textual e SQLite; busca semântica é adapter opcional. | Recuperação textual é local, auditável e barata; embeddings não são necessários para correção da primeira versão. | Architect |
| ADR-010 | Tratar segurança como boundary determinístico: permissions, hooks, schemas, quarentena, checksums e confirmação externa. | Prompts não constituem barreira de segurança e agentes de plugin ignoram alguns campos de permissão no frontmatter. | Architect |

## Consequências consolidadas

- O modo básico não exige Claude Ledger, Textual, Rich, Agent SDK, banco externo ou servidor HTTP.
- Métricas carregam proveniência `observed`, `calculated`, `estimated` ou `unknown`; custo do SDK não é cobrança autoritativa.
- A TUI e integrações nunca acessam o SQLite fora dos application services.
- Operações destrutivas e elevação de permissões exigem decisão externa ao texto gerado pelo modelo.
- Recursos condicionais podem ser adicionados por adapters sem alterar a semântica do core.

## Status e validação

ADRs 001–010: **ACCEPTED** pelo Product Owner e validados pelo QA em 2026-11-11.

Evidência: 77/77 testes, 23/23 categorias obrigatórias, 8/8 cenários, plugin normal/directory aprovado e wheel SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`.

A aceitação não amplia o escopo observado: Rich/Textual, aplicativo Ledger real, execução autenticada do Agent SDK, billing e chamadas reais de modelo continuam opcionais ou não exercitados. O benchmark aprovado mede apenas roteamento determinístico local em Windows.
