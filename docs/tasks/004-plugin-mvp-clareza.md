# [BACKEND] Plugin MVP e `/orchestra:clareza`

- Status: COMPLETED
- Fase: C
- Estimativa: 3 dias
- Depende de: 003
- Responsável: Dev Backend

## O que fazer

Criar plugin nativo válido com Central Orchestrator, um especialista de revisão, skill `clareza`, hook seguro, launcher CLI e integração ao núcleo. Implementar QUICK, NORMAL e HIGH com saídas estruturadas.

## Critério de conclusão

- `claude plugin validate` passa.
- `/orchestra:clareza` aceita profundidade, caminho e `--seguranca`.
- Vereditos limitam-se a APPROVED, APPROVED_WITH_NOTES, CHANGES_REQUESTED e INCONCLUSIVE.
- Cada achado informa gravidade, arquivo/local, evidência, impacto e correção.
- HIGH convoca no máximo dois especialistas adicionais e somente com justificativa de risco.

## Limites de arquivos

`.claude-plugin/**`, `agents/central-orchestrator.md`, `agents/quality/code-review-specialist.md`, `skills/clareza/**`, `hooks/**`, `bin/**`, `tests/integration/plugin/**`.

## Risco

Plugin agents ignoram `permissionMode`, hooks e MCP próprios; guardrails precisam ficar no nível do plugin.

## Contrato técnico consolidado

- Ownership: `.claude-plugin/**`, `agents/central-orchestrator.md`, `agents/quality/code-review-specialist.md`, `skills/clareza/**`, `hooks/**`, `bin/**`, `schemas/review-report*.json` e testes do plugin.
- Skills chamam o bridge CLI; não implementam uma segunda state machine.
- Namespace público obrigatório: `/orchestra:clareza`; nenhum atalho global é instalado.
- `ReviewReport v1` rejeita propriedades desconhecidas, limita HIGH a dois especialistas e exige evidence refs.
- Hooks de segurança ficam em `hooks/hooks.json`; não declarar `permissionMode`, `hooks` ou `mcpServers` no plugin agent.
- Gate: validator oficial, parsing QUICK/NORMAL/HIGH e execução no fallback sem Rich/Textual.

## Evidência de conclusão

- [x] `claude plugin validate .` aprovado.
- [x] `claude plugin validate . --profile directory` aprovado.
- [x] `/orchestra:clareza` e equivalente CLI cobertos por parser/testes.
- [x] `ICON_MISSING` permanece aviso opcional, não falha.

