# Requisitos do Orchestra Core

## Regra de negócio

O Orchestra Core deve selecionar dinamicamente o menor conjunto de agentes necessário para entregar resultados verificáveis, com baixo consumo de contexto, segurança, rastreabilidade e funcionamento independente do Claude Ledger.

## Personas e resultados

- **Desenvolvedor:** solicita trabalho e recebe resultado, evidências e pendências sem operar a organização manualmente.
- **Líder técnico:** audita roteamento, contratos, decisões, budgets e qualidade.
- **Administrador:** instala e restringe agentes, skills, MCP e extensões com menor privilégio.
- **Mantenedor do Ledger:** consome manifesto e eventos sem virar orquestrador.

## Requisitos funcionais

### Organização e routing

- **FR-001:** disponibilizar exatamente 36 agentes: 7 departamentos com 5 agentes e um Central Orchestrator.
- **FR-002:** carregar definições e skills apenas sob demanda, mantendo descrições iniciais curtas.
- **FR-003:** classificar tasks em DIRECT, LEAN, STANDARD ou DEEP por sinais auditáveis.
- **FR-004:** registrar agentes escolhidos, candidatos rejeitados e justificativas.
- **FR-005:** convocar líderes somente para coordenação, conflito ou aprovação.

### Workflow

- **FR-010:** persistir os 13 estados e rejeitar transições não declaradas.
- **FR-011:** suportar dependências, checkpoint, cancelamento seguro, timeout, retry/backoff e recuperação.
- **FR-012:** limitar ciclos de review/rework e interromper repetição da mesma falha.
- **FR-013:** exigir critérios e evidências antes de `COMPLETED`.
- **FR-014:** manter ID, owner, revision e correlation ID em todo trabalho.

### Plugin e comandos

- **FR-020:** distribuir plugin Claude Code validável e namespaced `orchestra`.
- **FR-021:** fornecer `/orchestra:clareza` em QUICK, NORMAL e HIGH.
- **FR-022:** limitar o parecer a APPROVED, APPROVED_WITH_NOTES, CHANGES_REQUESTED ou INCONCLUSIVE.
- **FR-023:** achados de revisão contêm gravidade, arquivo, localização, evidência, impacto e correção.
- **FR-024:** HIGH convoca no máximo dois especialistas adicionais, com justificativa registrada.
- **FR-025:** fornecer 18 skills/comandos adicionais exigidos com equivalentes CLI.

Lista: `organizar`, `planejar`, `construir`, `validar`, `diagnostico`, `revisar-arquitetura`, `pesquisar`, `memoria`, `agentes`, `departamentos`, `skills`, `orcamento`, `esteira`, `retomar`, `relatorio`, `auditar`, `doctor-org`, `ajuda-org`.

### Skills e conhecimento

- **FR-030:** fornecer 36 skills principais e catálogo pesquisável por responsabilidade, tags, task e compatibilidade.
- **FR-031:** cada skill define uso/não uso, pré-condições, procedimento, tools, output, validação, erros e exemplo.
- **FR-032:** reutilizar skills compartilhadas em vez de duplicar procedimentos.
- **FR-033:** oferecer memórias organizational, project, department-agent e episodic.
- **FR-034:** suportar PROPOSED, VERIFIED, OUTDATED, SUPERSEDED e REJECTED, com evidência e histórico.
- **FR-035:** deduplicar, relacionar contradições e invalidar memória sem apagar auditoria.

### Budget e observabilidade

- **FR-040:** oferecer ECONOMY, BALANCED, QUALITY e CRITICAL.
- **FR-041:** limitar calls, agents, retries, rework, duração e artefatos sem reduzir segurança mínima.
- **FR-042:** marcar métricas como observed, calculated, estimated ou unknown.
- **FR-043:** persistir eventos versionados e correlacionados sem conteúdo sensível por padrão.
- **FR-044:** exportar JSONL local e permitir OTel opcional.

### CLI/TUI

- **FR-050:** executar bootstrap, tasks, catálogo, memória, budgets, registry, doctor e launch do Claude Code pela CLI.
- **FR-051:** fornecer `--json`, exit codes e fallback estático/no-color.
- **FR-052:** oferecer TUI opcional com início, departamentos, agentes, esteira, tasks, memória, skills/MCP e timeline.
- **FR-053:** não alegar controle de sessão nativa que a API oficial não fornece.

### Extensões e Ledger

- **FR-060:** registrar agent, department, skill, MCP, command, hook, validator, workflow e storage provider.
- **FR-061:** analisar extensão em quarentena antes de instalar; registrar origem, versão, checksum, permissões e dependências.
- **FR-062:** suportar disable, export, import e remoção segura com rollback.
- **FR-063:** publicar `organization.manifest.json` e eventos versionados para Ledger.
- **FR-064:** funcionar integralmente quando Ledger estiver ausente, incompatível ou falhar.

## Requisitos não funcionais

- **NFR-001 — Segurança:** menor privilégio, redaction, allowlists e confirmação externa para ações destrutivas.
- **NFR-002 — Privacidade:** não persistir prompts, respostas, secrets ou argumentos crus de tools por padrão.
- **NFR-003 — Recuperabilidade:** toda operação mutável crítica é transacional ou retomável por checkpoint.
- **NFR-004 — Windows:** suportar PowerShell, CMD e Windows Terminal; persistência sempre UTF-8.
- **NFR-005 — Degradação:** funcionar sem Rich, Textual, Ledger, OTel, MCP, API key, rede, banco externo ou `sqlite3` CLI.
- **NFR-006 — Auditabilidade:** decisão, transição, validação e memória importante possuem provenance/evidence refs.
- **NFR-007 — Extensibilidade:** contratos versionados e adapters não vazam para Domain.
- **NFR-008 — Performance:** bootstrap não usa LLM e não lê os 36 corpos de agentes/skills.
- **NFR-009 — Honestidade:** métricas ausentes são `unknown`; benchmark declara amostra e ambiente.
- **NFR-010 — Manutenibilidade:** fontes canônicas geram catálogos/tabelas; duplicata é detectada por teste.

## Critérios de aceite do MVP vertical

1. Repositório instalável e documentado.
2. Plugin válido com Central Orchestrator e um especialista real.
3. Router cobre quatro modos e explica seleção mínima.
4. Workflow persistente rejeita transição inválida.
5. Uma skill completa aplica progressive disclosure.
6. `/orchestra:clareza` valida argumentos e produz parecer estruturado.
7. Handoff passa por JSON Schema.
8. Memória local é consultável sem Ledger/banco externo.
9. Eventos têm correlação e payload sanitizado.
10. Bootstrap é idempotente e recupera tasks interrompidas.
11. Instalação, execução, recuperação e testes passam localmente.
12. Dado indisponível é `unknown` ou `estimated`, nunca fabricado.

## Critérios da entrega completa

- Contagem e validação automatizada de 36 agents e 36 skills principais.
- Todos os comandos obrigatórios possuem parsing, help, erros e equivalente CLI.
- Máquina de estados, retries, cancelamento, checkpoints, dependências, concorrência e anti-loop são testados.
- Quatro tipos e cinco estados de memória são testados.
- CLI/TUI cobrem telas e fallback exigidos.
- Registry e integração Ledger obedecem menor privilégio e independência.
- Dois modos são documentados; Programmatic exige autenticação oficial.
- As 23 categorias de teste e 8 cenários possuem evidência ou limitação explícita.
- Documentação inclui instalação, extensão, integração, troubleshooting e resultados reais.

## Não objetivos

- Modificar o binário ou substituir a UI do Claude Code.
- Manter 36 agentes ativos.
- Implementar dashboard Ledger.
- Exigir servidor HTTP, PostgreSQL, Redis, banco vetorial ou API paga no modo básico.
- Usar prompt como fronteira de segurança.
- Afirmar ganho, custo ou compatibilidade sem medição.

## Rastreabilidade

| Área | Requisitos | Tasks |
|---|---|---|
| Pesquisa/compatibilidade | NFR-007, NFR-009 | 001 |
| Arquitetura/contratos | FR-010–014, NFR-003, NFR-007 | 002 |
| Core | FR-003–005, FR-010–014, FR-040–043 | 003 |
| MVP plugin/clareza | FR-020–024 | 004 |
| Agentes | FR-001–005 | 005 |
| Skills | FR-030–032 | 006 |
| Comandos | FR-025 | 007 |
| Memória/budget | FR-033–043 | 008 |
| Segurança/registry | FR-060–062, NFR-001–002 | 009 |
| CLI | FR-050–051, NFR-004–005 | 010 |
| TUI | FR-052–053 | 011 |
| Ledger/telemetria | FR-043–044, FR-063–064 | 012 |
| Testes | todos | 013–014 |
| Documentação/memória | NFR-006, NFR-009–010 | 015 |

