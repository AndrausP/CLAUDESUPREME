---
name: validar
description: Executar validações determinísticas e consolidar evidências.
argument-hint: [QUICK|NORMAL|HIGH] [target] --task-id ID [--security] [--architecture] [--timeout SECONDS] [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: quality-lead
  cli: "orchestra clareza [QUICK|NORMAL|HIGH] [target] --task-id <task-id> [--security] [--architecture] [--timeout SECONDS] [--json]"
---

# /orchestra:validar

## Sintaxe

`/orchestra:validar [QUICK|NORMAL|HIGH] [target] --task-id ID [--security] [--architecture] [--timeout SECONDS] [--json]`

## Responsável

`quality-lead`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Executar validações determinísticas e consolidar evidências.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Task-id é obrigatório nesta fachada; profundidade, target e flags seguem exatamente o contrato de clareza.
3. Traduzir para a CLI: Delegar a execução ao subcomando clareza e rejeitar opções alheias ao parser.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

ReviewReport v1 e evidence refs; o chamador persiste a transição separadamente quando aplicável. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra clareza [QUICK|NORMAL|HIGH] [target] --task-id <task-id> [--security] [--architecture] [--timeout SECONDS] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:validar [QUICK|NORMAL|HIGH]` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
