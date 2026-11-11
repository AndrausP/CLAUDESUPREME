---
name: diagnostico
description: Investigar falha usando a timeline de eventos e evidências.
argument-hint: --task-id ID [--file PATH] [--limit N] [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: defect-investigator
  cli: "orchestra audit --task-id <task-id> [--file PATH] [--limit N] [--json]"
---

# /orchestra:diagnostico

## Sintaxe

`/orchestra:diagnostico --task-id ID [--file PATH] [--limit N] [--json]`

## Responsável

`defect-investigator`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Investigar falha usando a timeline de eventos e evidências.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Task-id é obrigatório nesta fachada; file opcional aponta para JSONL legível e limit é inteiro positivo.
3. Traduzir para a CLI: Usar audit como fonte observável do diagnóstico.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Timeline de auditoria que alimenta diagnóstico com hipóteses classificadas. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra audit --task-id <task-id> [--file PATH] [--limit N] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:diagnostico --task-id` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
