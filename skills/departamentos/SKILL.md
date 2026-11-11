---
name: departamentos
description: Consultar departamentos, líderes e competências.
argument-hint: [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: central-orchestrator
  cli: "orchestra departments [--json]"
---

# /orchestra:departamentos

## Sintaxe

`/orchestra:departamentos [--json]`

## Responsável

`central-orchestrator`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Consultar departamentos, líderes e competências.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: O subcomando não aceita filtros ou ações adicionais.
3. Traduzir para a CLI: Executar departments diretamente, sem ação intermediária.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Estrutura departamental completa e contagem. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra departments [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:departamentos [--json]` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
