# [BACKEND] Protocolo Ledger e telemetria

- Status: COMPLETED
- Fase: E
- Estimativa: 3 dias
- Depende de: 002, 003, 009
- Responsável: Dev Backend

## O que fazer

Criar `organization.manifest.json`, schemas de eventos, exportador JSONL/SQLite e adapter opcional para Claude Ledger. Preparar OTel opcional sem exigir servidor HTTP.

## Critério de conclusão

- Eventos exigidos possuem schema version, correlation ID, timestamp e origem.
- Dados são marcados observed/calculated/estimated/unknown.
- Orchestra opera com adapter ausente ou falho.
- Nenhum código do Ledger é alterado nesta task.
- Prompts, respostas e argumentos crus não são persistidos por padrão.

## Limites de arquivos

`integrations/claude-ledger/**`, `src/orchestra/telemetry/**`, `schemas/{organization,event}*.json`, `tests/integration/ledger/**`.

## Risco

Ledger atual não conhece Orchestra; contrato deve permanecer unilateral e versionado.

## Contrato técnico consolidado

- Ownership: `integrations/claude-ledger/**`, `src/orchestra/{telemetry,adapters/ledger,adapters/otel}/**`, `schemas/{organization,event,metric}*.json` e testes.
- Integração pública: `Organization Manifest v1` + `Event v1` JSONL; sem escrita direta no banco do Ledger e sem servidor permanente.
- Adapter é substituível; ausência, falha ou major incompatível nunca bloqueia workflow.
- SQLite outbox exporta JSONL idempotente por `event_id` e sequence.
- OTel é opt-in; atributos seguem allowlist e não duplicam custos/eventos já correlacionados.
- Proveniência obrigatória: observed/calculated/estimated/unknown.

## Evidência de conclusão

- [x] Manifesto, schema de eventos e export opcional aprovados.
- [x] Operação sem Ledger passou.
- [x] Sanitização e proveniência foram validadas.
- [ ] Aplicativo Ledger real e billing telemetry não foram exercitados; tokens/custo ficaram `unknown`.

Conclusão com limitação: contrato local aprovado, integração externa real permanece opcional.

