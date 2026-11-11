# Contratos e schemas do Orchestra Core

Este documento define os contratos lógicos. Os arquivos em `schemas/` serão as definições JSON Schema executáveis.

## Convenções

- JSON Schema 2020-12.
- `schema_version` usa SemVer. Mudança incompatível incrementa major.
- IDs são UUID v4 em lowercase; slugs são kebab-case.
- Timestamps são UTC RFC 3339 com offset `Z`.
- Objetos rejeitam propriedades desconhecidas nos limites de confiança.
- Campo ausente não equivale a dado medido. Métricas usam `value` + `provenance`.
- Referências detalhadas usam URI/path relativo/ID; handoffs não incorporam históricos extensos.
- Todo payload persistido passa por sanitização e limite de tamanho.

## Handoff v1

Campos obrigatórios:

```json
{
  "schema_version": "1.0.0",
  "handoff_id": "uuid",
  "task_id": "uuid",
  "parent_task_id": null,
  "correlation_id": "uuid",
  "from_department": "quality",
  "from_agent": "code-review-specialist",
  "to": "quality-lead",
  "objective": "Validar critérios de aceite",
  "minimal_context": "Resumo sanitizado",
  "relevant_files": [{"path": "src/module.py", "sha256": "hex"}],
  "memory_refs": ["memory:uuid"],
  "confirmed_decisions": ["decision:ADR-001"],
  "acceptance_criteria": [{"id": "AC-1", "text": "..."}],
  "artifacts": [{"id": "artifact:uuid", "uri": "relative/path"}],
  "test_results": [{"id": "evidence:uuid", "status": "passed"}],
  "issues": [{"id": "issue:uuid", "severity": "high"}],
  "status": "READY",
  "next_action": "Executar validação",
  "evidence_refs": ["evidence:uuid"],
  "created_at": "2026-11-11T00:00:00Z"
}
```

Validações: origem e destino existem no catálogo; status pertence ao enum; paths são relativos ao project root; artifact/evidence refs resolvem; conteúdo sensível é recusado.

## Task v1

```json
{
  "schema_version": "1.0.0",
  "task_id": "uuid",
  "parent_task_id": null,
  "attempt_of": null,
  "project_id": "uuid",
  "correlation_id": "uuid",
  "title": "string",
  "objective": "string",
  "mode": "STANDARD",
  "risk": "medium",
  "status": "CREATED",
  "owner": "feature-engineer",
  "selected_agents": [{"id": "feature-engineer", "reason_code": "CAPABILITY_MATCH"}],
  "rejected_candidates": [{"id": "backend-lead", "reason_code": "NO_COORDINATION_NEEDED"}],
  "acceptance_criteria": [{"id": "AC-1", "text": "string", "status": "pending"}],
  "dependencies": [],
  "budget_profile": "BALANCED",
  "revision": 0,
  "created_at": "2026-11-11T00:00:00Z",
  "updated_at": "2026-11-11T00:00:00Z"
}
```

Enums de mode: DIRECT, LEAN, STANDARD, DEEP. Risk: low, medium, high, critical. Status usa os 13 estados oficiais.

## Transition v1

```json
{
  "schema_version": "1.0.0",
  "transition_id": "uuid",
  "task_id": "uuid",
  "expected_revision": 3,
  "from": "RUNNING",
  "to": "VALIDATING",
  "actor": {"type": "agent", "id": "feature-engineer"},
  "reason_code": "IMPLEMENTATION_READY",
  "reason": "string",
  "evidence_refs": ["evidence:uuid"],
  "occurred_at": "2026-11-11T00:00:00Z"
}
```

O use case compara `expected_revision`, valida a aresta, grava transition/task/outbox atomicamente e retorna conflito tipado em revision divergente.

## Checkpoint v1

```json
{
  "schema_version": "1.0.0",
  "checkpoint_id": "uuid",
  "task_id": "uuid",
  "attempt": 1,
  "state": "RUNNING",
  "step": "implementation",
  "completed_units": ["artifact:uuid"],
  "pending_units": ["AC-2"],
  "resume_after": null,
  "budget_snapshot": {"calls_used": 2, "tokens": {"value": null, "provenance": "unknown"}},
  "artifact_refs": ["artifact:uuid"],
  "created_at": "2026-11-11T00:00:00Z"
}
```

Checkpoint não contém transcript ou reasoning privado.

## Event v1

```json
{
  "schema_version": "1.0.0",
  "event_id": "uuid",
  "event_type": "task.created",
  "correlation_id": "uuid",
  "causation_id": null,
  "task_id": "uuid",
  "source": {"component": "orchestra-core", "version": "0.1.0"},
  "occurred_at": "2026-11-11T00:00:00Z",
  "sequence": 1,
  "data_classification": "internal",
  "payload": {},
  "payload_sha256": "hex"
}
```

Tipos mínimos: `task.created`, `task.classified`, `workflow.started`, `agent.started`, `agent.completed`, `tool.completed`, `handoff.created`, `validation.completed`, `memory.proposed`, `diagnostic.created`, `budget.warning`, `task.completed`, `task.failed`.

Payload usa allowlist por `event_type`. Prompt, response, reasoning, secret, tool arguments crus e paths absolutos não entram no evento.

## Métrica v1

```json
{
  "name": "tokens.input",
  "value": 1234,
  "unit": "token",
  "provenance": "observed",
  "source": "agent-sdk-result",
  "measured_at": "2026-11-11T00:00:00Z"
}
```

`provenance`: observed, calculated, estimated, unknown. Para unknown, `value` é null e `source` explica a indisponibilidade.

## Memory v1

```json
{
  "schema_version": "1.0.0",
  "memory_id": "uuid",
  "type": "project",
  "scope": "project:uuid",
  "title": "string",
  "summary": "string",
  "content_ref": "docs/knowledge/patterns.md#id",
  "origin": {"type": "task", "id": "uuid"},
  "created_at": "2026-11-11T00:00:00Z",
  "last_validated_at": null,
  "confidence": "medium",
  "status": "PROPOSED",
  "tags": ["routing"],
  "relations": [{"type": "supports", "target": "memory:uuid"}],
  "revision": 1,
  "evidence_refs": ["evidence:uuid"],
  "content_sha256": "hex"
}
```

Tipos: organizational, project, department-agent, episodic. Status: PROPOSED, VERIFIED, OUTDATED, SUPERSEDED, REJECTED.

## Review report v1

```json
{
  "schema_version": "1.0.0",
  "review_id": "uuid",
  "task_id": "uuid",
  "depth": "HIGH",
  "scope": ["src/auth"],
  "security_requested": true,
  "verdict": "CHANGES_REQUESTED",
  "findings": [{
    "finding_id": "uuid",
    "severity": "high",
    "file": "src/auth/token.py",
    "location": {"line": 42},
    "evidence": "evidence:uuid",
    "impact": "string",
    "proposed_fix": "string",
    "confidence": "confirmed"
  }],
  "specialists": [{"agent_id": "security-architect", "reason_code": "SECURITY_FLAG"}],
  "evidence_refs": ["evidence:uuid"]
}
```

Veredictos: APPROVED, APPROVED_WITH_NOTES, CHANGES_REQUESTED, INCONCLUSIVE. HIGH aceita no máximo dois specialists.

## Component registry v1

```json
{
  "schema_version": "1.0.0",
  "component_id": "skill:scope-governance",
  "version": "1.0.0",
  "type": "skill",
  "origin": {"kind": "local", "uri": "skills/scope-governance"},
  "description": "string",
  "permissions": {"tools": ["Read"], "network": false, "write_scopes": []},
  "dependencies": [],
  "compatibility": {"claude_code": ">=2.1.322", "os": ["windows", "linux", "macos"]},
  "status": "enabled",
  "checksum": {"algorithm": "sha256", "value": "hex"},
  "configuration_ref": null
}
```

Tipos: agent, department, skill, mcp, command, hook, validator, workflow, storage-provider. Status: quarantined, disabled, enabled, incompatible, failed, removed.

## Organization manifest v1

```json
{
  "schema_version": "1.0.0",
  "organization_id": "orchestra-core-default",
  "protocol_version": "1.0.0",
  "package_version": "0.1.0",
  "generated_at": "2026-11-11T00:00:00Z",
  "departments": [{"id": "product", "leader": "product-lead", "agents": []}],
  "agents": [{"id": "central-orchestrator", "enabled": true, "ref": "agents/central-orchestrator.md"}],
  "skills": [{"id": "workflow-routing", "ref": "skills/workflow-routing/SKILL.md"}],
  "mcp_servers": [],
  "profiles": ["ECONOMY", "BALANCED", "QUALITY", "CRITICAL"],
  "policies": [{"id": "least-privilege", "version": "1.0.0"}],
  "dependencies": [],
  "integrations": {"claude_code": "available", "claude_ledger": "optional"},
  "checksums": {}
}
```

O manifesto contém metadados e referências, não secrets nem configurações privadas.

## Budget profile v1

```json
{
  "schema_version": "1.0.0",
  "profile": "BALANCED",
  "limits": {
    "max_agent_runs": 3,
    "max_parallel_agents": 2,
    "max_retries_per_step": 2,
    "max_rework_cycles": 2,
    "max_duration_seconds": 3600,
    "max_artifact_bytes": 10485760,
    "max_tokens": null
  },
  "enforcement": {
    "max_tokens": "advisory-when-unobserved",
    "safety_minimums": "always"
  }
}
```

Valores finais ficam em `config/profiles/` e são testáveis; o schema não fixa política comercial.

## Erros tipados

Formato comum:

```json
{
  "error": {
    "code": "INVALID_TRANSITION",
    "message": "RUNNING não pode transicionar para COMPLETED",
    "retryable": false,
    "details": {"from": "RUNNING", "to": "COMPLETED"},
    "correlation_id": "uuid"
  }
}
```

Códigos mínimos: INVALID_SCHEMA, INVALID_TRANSITION, REVISION_CONFLICT, BUDGET_EXHAUSTED, RETRY_LIMIT, REWORK_LOOP, DEPENDENCY_BLOCKED, PERMISSION_DENIED, UNSAFE_EXTENSION, CHECKSUM_MISMATCH, INCOMPATIBLE_VERSION, STORAGE_FAILURE, VALIDATION_INCONCLUSIVE.

## Política de evolução

- Readers aceitam minor nova com campos opcionais, mas recusam major desconhecida.
- Writers emitem somente a versão configurada.
- Migração transforma e valida antes de substituir; original permanece recuperável até commit.
- Ledger recebe apenas contratos públicos do diretório de integração.
- Fixtures de cada schema são obrigatórias para success e failure paths.

