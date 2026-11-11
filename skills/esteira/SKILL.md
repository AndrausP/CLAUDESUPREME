---
name: esteira
description: Visualizar etapas realmente usadas e seus estados.
argument-hint: <task-id> [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: central-orchestrator
  cli: "orchestra pipeline <task-id> [--json]"
---

# /orchestra:esteira

## Sintaxe

`/orchestra:esteira <task-id> [--json]`

## Responsável

`central-orchestrator`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Visualizar etapas realmente usadas e seus estados.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Task-id posicional é obrigatório e deve resolver para task persistida.
3. Traduzir para a CLI: Mapear task-id diretamente para pipeline; não usar --task.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Pipeline compacto com status de Planning a Delivery. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra pipeline <task-id> [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:esteira <task-id>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
