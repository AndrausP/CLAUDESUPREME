---
name: retomar
description: Retomar uma task interrompida a partir do estado recuperável.
argument-hint: <task-id> [--actor ID] [--reason TEXT] [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: central-orchestrator
  cli: "orchestra task resume <task-id> [--actor ID] [--reason TEXT] [--json]"
---

# /orchestra:retomar

## Sintaxe

`/orchestra:retomar <task-id> [--actor ID] [--reason TEXT] [--json]`

## Responsável

`central-orchestrator`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Retomar uma task interrompida a partir do estado recuperável.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Task deve ser retomável; actor e reason são opcionais e não autorizam transição inválida.
3. Traduzir para a CLI: Repassar ao subcomando task resume; não prometer uma nova task quando o core atualiza a existente.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Task v1 retomada com nova revisão e evento auditável. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra task resume <task-id> [--actor ID] [--reason TEXT] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:retomar <task-id>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
