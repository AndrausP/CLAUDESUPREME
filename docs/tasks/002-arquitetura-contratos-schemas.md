# [ARCHITECT] Arquitetura, contratos e schemas

- Status: COMPLETED
- Fase: A/B
- Estimativa: 3 dias
- Depende de: 001
- Responsável: Architect

## O que fazer

Definir limites entre plugin nativo, núcleo determinístico, CLI/TUI, adaptador Agent SDK e integração Ledger. Especificar máquina de estados, roteamento, orçamentos, handoff, manifesto, eventos, memória, registry e checkpoints.

## Critério de conclusão

- Diagrama e ADRs registram alternativas e motivos.
- Schemas JSON versionados cobrem handoff, task, event, memory, component e organization manifest.
- Transições válidas/inválidas e políticas de retry, backoff, timeout, cancelamento e anti-loop estão fechadas.
- Contratos não dependem de Ledger nem de uma TUI ativa.

## Limites de arquivos

`docs/architecture.md`, `docs/requirements.md` e `docs/contracts.md`. Schemas executáveis foram delegados às tasks implementadoras 003, 004, 008, 009 e 012; `docs/decisions.md` permanece reservado ao Writer após aprovação.

## Risco

Duplicar funcionalidades nativas; toda camada personalizada precisa de justificativa.

## Evidência de conclusão

- `docs/architecture.md`: arquitetura hexagonal, state machine, routing, budgets, storage, segurança e adapters.
- `docs/requirements.md`: FR/NFR, critérios MVP/completo e rastreabilidade por task.
- `docs/contracts.md`: contratos lógicos v1 e política de evolução.
- Decisões fechadas: Python 3.12; SQLite autoritativo; outbox/JSONL; plugin native-first; CLI stdlib; Textual/Rich opcionais; Ledger unilateral; agent teams não-baseline.

## Reconciliação final

- [x] ADRs 001–010 aceitos em `docs/decisions.md`.
- [x] Schemas e contratos exercitados pelas categorias obrigatórias.
- [x] QA aprovou arquitetura sem dependência de Ledger/TUI.

