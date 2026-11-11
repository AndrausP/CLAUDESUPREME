---
name: auditar
description: Examinar decisões, transições, permissões e evidências registradas.
argument-hint: [--task-id ID] [--file PATH] [--limit N] [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: quality-lead
  cli: "orchestra audit [--task-id ID] [--file PATH] [--limit N] [--json]"
---

# /orchestra:auditar

## Sintaxe

`/orchestra:auditar [--task-id ID] [--file PATH] [--limit N] [--json]`

## Responsável

`quality-lead`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Examinar decisões, transições, permissões e evidências registradas.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: File opcional deve ser JSONL legível; limit é inteiro positivo; task-id filtra eventos quando informado.
3. Traduzir para a CLI: Repassar os filtros ao subcomando audit; correlation-id não é filtro suportado.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Audit trail ordenado e limitado, com gaps explícitos quando a fonte não existe. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra audit [--task-id ID] [--file PATH] [--limit N] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:auditar [--task-id` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
