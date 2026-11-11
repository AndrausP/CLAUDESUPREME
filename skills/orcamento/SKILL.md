---
name: orcamento
description: Consultar profiles ou verificar consumo contra um profile.
argument-hint: <list|check> [PROFILE] [usage-options] [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: central-orchestrator
  cli: "orchestra budget <list|check> [PROFILE] [usage-options] [--json]"
---

# /orchestra:orcamento

## Sintaxe

`/orchestra:orcamento <list|check> [PROFILE] [usage-options] [--json]`

## Responsável

`central-orchestrator`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Consultar profiles ou verificar consumo contra um profile.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: list não recebe profile; check exige ECONOMY, BALANCED, QUALITY ou CRITICAL e aceita apenas --agent-runs, --parallel-agents, --retries, --rework-cycles, --duration-seconds, --artifact-bytes e --tokens.
3. Traduzir para a CLI: Repassar list ou check e suas opções; o parser atual verifica limites, mas não oferece set nem --task.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Lista de profiles ou within_budget com uso normalizado. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra budget <list|check> [PROFILE] [usage-options] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:orcamento <list|check>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
