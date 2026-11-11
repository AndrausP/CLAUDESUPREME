---
name: revisar-arquitetura
description: Verificar boundaries, contratos e decisões arquiteturais aplicáveis.
argument-hint: [target] [--task-id ID] [--security] [--timeout SECONDS] [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: architecture-lead
  cli: "orchestra clareza HIGH [target] [--task-id ID] --architecture [--security] [--timeout SECONDS] [--json]"
---

# /orchestra:revisar-arquitetura

## Sintaxe

`/orchestra:revisar-arquitetura [target] [--task-id ID] [--security] [--timeout SECONDS] [--json]`

## Responsável

`architecture-lead`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Verificar boundaries, contratos e decisões arquiteturais aplicáveis.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Target deve ficar dentro do projeto; timeout é inteiro positivo; task-id é opcional.
3. Traduzir para a CLI: Fixar HIGH e --architecture, preservando target e opções suportadas.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

ReviewReport v1 em HIGH com especialista de arquitetura registrado. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra clareza HIGH [target] [--task-id ID] --architecture [--security] [--timeout SECONDS] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:revisar-arquitetura [target]` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
