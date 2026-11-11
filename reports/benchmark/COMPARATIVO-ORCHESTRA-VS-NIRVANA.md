# Orchestra Core vs Nirvana — Benchmark e Comparativo

Data: 2026-11-11 · Host único: Windows 11, Python 3.12.10, Node 24.13.0
Versões: Orchestra Core 0.1.0 (pré-release, sem histórico git) · Nirvana 2.2.0 (30 commits, plugin publicado)

## TL;DR

| | Orchestra Core | Nirvana |
|---|---|---|
| Natureza | Plano de controle **determinístico** (Python + SQLite) | Sistema de **skills + markdown** com memória neural opcional (Node) |
| Ponto forte | Desempenho, regras impostas por código, workflow transacional | Maturidade de produto, memória associativa rica, CI multi-OS |
| Ponto fraco | Sem CI, sem commits, guard com brechas, memória simples | Memória neural não escala, sem enforcement, SessionStart lento |
| Melhor para | Base técnica de orquestração | Uso diário imediato |

**Veredito:** Nirvana é o **produto mais completo hoje** (lançado, testado em 3 SOs, documentado). Orchestra Core é o **motor de orquestração mais completo e mais rápido**, mas ainda imaturo. Caminho recomendado: Orchestra como motor (estado, roteamento, budgets) + memória neural do Nirvana por cima, após corrigir o gargalo de escrita dela.

---

## 1. Desempenho — Orchestra Core

Harness: `benchmarks/full_matrix.py` · Dados: `reports/benchmark/full-matrix-2026-11-11.json`

### Núcleo em processo

| Operação | Mediana | p95 |
|---|---|---|
| `Router.classify` | 0,0013 ms | 0,0014 ms |
| `Router.route` (3 candidatos) | 0,0038 ms | 0,0041 ms |
| `route` — 36 / 200 / 1000 agentes | 0,11 / 0,79 / 3,75 ms | — |
| `StateMachine.validate` | 0,0001 ms | 0,0002 ms |
| `sanitize` / `digest` (payload médio) | 0,092 / 0,048 ms | — |
| `store.create_task` (SQLite WAL) | 0,36 ms (~2.600 op/s) | 0,47 ms |
| `store.get_task` | 0,014 ms | 0,015 ms |
| Ciclo CREATED→COMPLETED (7 transições) | 3,06 ms (~0,44 ms/transição) | 6,6 ms |
| `export_events` (lote de 100) | 40–62 ms, estável | — |

### Memória (escala linear)

| Itens | `propose` | `search` |
|---|---|---|
| 100 | 0,56 ms | 0,07 ms |
| 1.000 | 1,0 ms | 0,58 ms |
| 5.000 | 4,9 ms | 4,7 ms |

Causa: `find_memory` usa `lower(col) LIKE '%q%'`, então o índice `idx_memory_search` não é usado e toda busca faz full scan; `propose` chama a busca antes de inserir.

### Custo real no Claude Code (subprocesso)

| Processo | Mediana |
|---|---|
| `python -c pass` (baseline) | 25 ms |
| `guard_hook` (PreToolUse) | 45–49 ms |
| `telemetry_hook` desligado / ligado | 64 / 63 ms |
| `bootstrap_hook` (SessionStart) | 56 ms |
| CLI (`--help`, `route`, `agents`, `status`) | 127–139 ms |

- Overhead por tool call (Bash/PowerShell/Write/Edit): **~110 ms**.
- `telemetry_hook` importa `hashlib`, `uuid`, `datetime` e `pathlib` antes de checar `ORCHESTRA_HOOK_TELEMETRY`; checar antes economiza ~40 ms por chamada.
- Import da CLI: ~120 ms, dominado pela stdlib (`dataclasses`, `re`, `inspect`, `enum`).

### Suíte de testes
77/77 OK em 1,27 s (≈1,9 s wall).

## 2. Desempenho — Nirvana

Harness: `benchmarks/nirvana_neural_bench.js` · Dados: `reports/benchmark/nirvana-neural-2026-11-11.json`

| Medida | Resultado |
|---|---|
| SessionStart `nirvana-banner.ps1` | 510–560 ms (1ª execução: 930 ms) |
| SessionStart `nirvana-banner.sh` | 630–770 ms |
| Overhead por tool call | 0 ms (não há hooks Pre/PostToolUse) |
| Testes neural | 27 testes: 25 pass, 2 skip, 0 fail · ~4,4 s wall |
| Memória neural, 100 itens — indexação | **6,7 s** · 5.869 conexões · 5.973 eventos · 3,4 MB |
| Memória neural, 100 itens — recall | 10,5 ms mediana · 15,4 ms p95 |
| Memória neural, 100 itens — busca | 0,99 ms |
| Reabrir (replay do log de eventos) | 53 ms |
| Memória neural, 1.000 itens — indexação | **abortada após >600 s** |

Causas:
1. Cada evento chama `Store.append` → cria e remove `.lock` + `appendFileSync` individual. Milhares de eventos = milhares de ciclos de I/O com lock.
2. As conexões por conceito compartilhado crescem ~O(n²). Ressalva: o dataset sintético repete muitos conceitos, então documentos reais devem gerar um grafo menos denso — mas o desenho não escala para milhares de memórias.
3. O estado é reconstruído por replay completo do `events.jsonl` em cada abertura.

## 3. Head-to-head

| Medida | Orchestra | Nirvana | Vence |
|---|---|---|---|
| Início de sessão | 56 ms | ~550 ms | Orchestra (~10x) |
| Overhead por tool call | ~110 ms | 0 ms | Nirvana |
| Gravar 100 memórias | ~56 ms | 6,7 s | Orchestra (~100x) |
| Busca em 100 memórias | 0,07 ms | 0,99 ms (busca) / 10,5 ms (recall) | Orchestra |
| Escala da memória até 5k | linear, ~5 ms | inviável acima de ~1k | Orchestra |
| Velocidade da suíte de testes | 1,3 s | 4,4 s (só neural) | Orchestra |

## 4. Funcionalidades

| Aspecto | Orchestra Core | Nirvana |
|---|---|---|
| Agentes | 36 em 7 departamentos + Central Orchestrator | 9 papéis em cadeia sequencial |
| Skills | 36 primárias | 8 (`light`, `bigtask`, `smalltask`, `law`, `karma`, `path`, `reflect`, `brain`) |
| Roteamento | DIRECT/LEAN/STANDARD/DEEP explicável, seleção mínima por capability | Fixo: bigtask vs smalltask |
| Workflow | 13 estados, transições validadas, lock otimista, checkpoints, retomada, dependências | Sprints/tasks em markdown, sem validação por código |
| Budgets / retry / rework guard | Sim | Não |
| Guardrail de comandos destrutivos | Sim (com brechas, ver §5) | Não |
| Persistência | SQLite WAL + transactional outbox | Markdown + event log JSONL |
| Memória | Curada, PROPOSED→VERIFIED com evidência, detecção de contradição por chave | Grafo associativo: plasticidade só com evidência, contradições preservadas, recall com peso por papel, decaimento, redação de segredos, detecção de prompt injection, viewer 3D, pgvector opcional |
| Integração graphify | Não | Sim |
| Interface | CLI texto/JSON, TUI Textual opcional, `NO_COLOR` | Banner SessionStart + viewer web |
| Integrações | Claude Ledger (opcional), Agent SDK (só detecção) | Claude Code plugin marketplace |
| Testes | 77 unit/e2e/acceptance/catalog | Neural + hooks + installers |
| CI | **Nenhuma** | GitHub Actions: Windows PS 5.1, macOS, Linux, validação do plugin |
| Distribuição | Wheel local | Plugin no marketplace + instaladores ps1/sh |
| Histórico / processo | Sem commits antes deste push | 30 commits, PRs, CHANGELOG, CONTRIBUTING |
| Dependências | Zero (stdlib), Rich/Textual opcionais | Zero (stdlib do Node), pg opcional |

## 5. Achados de qualidade

### Orchestra Core
- **[Alto — corrigido após o benchmark] O guard deixava passar comandos destrutivos:** `rm -fr build`, `rm --recursive --force x`, `del /s /q C:\x`. Falso positivo: `echo format c: is bad`. Agora o guard analisa cada segmento do comando, e há 47 casos cobertos em `tests/unit/test_guard_hook.py`.
- **[Processo — corrigido]** CI adicionada em `.github/workflows/ci.yml`.
- **[Médio]** A busca de memória faz full scan (`LIKE '%q%'`); trocar por FTS5 ou busca exata por `canonical_key`.
- **[Médio]** O `telemetry_hook` paga o custo de import mesmo desligado.
- **[Baixo]** `benchmarks/profile_matrix.py` percorre os `BudgetProfile` mas não os passa para `route()`, então as 4 medições são idênticas.
- **[Processo]** Sem CI; o adapter do Agent SDK não executa.

### Nirvana
- **[Alto]** Gargalo de escrita da memória neural (lock + append por evento). Corrigir com escrita em lote dentro de um único lock.
- **[Médio]** Explosão de conexões; limitar top-k por memória ou exigir peso mínimo.
- **[Médio]** SessionStart ~0,5–0,8 s (inicialização do PowerShell/bash).
- **[Baixo]** `node --test tests/neural/` (diretório) falha no Windows/Node 24; a CI usa a lista de arquivos e passa.
- **[Design]** A disciplina da cadeia depende do modelo seguir as instruções; não há enforcement por código.

## 6. Limitações deste benchmark
- Host único; sem repetição em outra máquina.
- Nenhuma chamada real de modelo: tokens e custo de cada sistema são `unknown`.
- O dataset de memória é sintético e denso em conceitos, o que é desfavorável ao Nirvana.
- Os testes de shell/installer do Nirvana não foram rodados localmente (rodam na CI dele).

## 7. Recomendação
1. Corrigir o guard do Orchestra (segurança).
2. Montar a CI do Orchestra no mesmo molde da CI do Nirvana (matriz de 3 SOs).
3. Corrigir o lock por evento do Nirvana (escrita em lote).
4. Avaliar a fusão: o Orchestra como camada de estado/roteamento e a memória neural do Nirvana como provedor de contexto.
