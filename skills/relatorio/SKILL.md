---
name: relatorio
description: Gerar relatório técnico de uma task em arquivo local.
argument-hint: <task-id> --output PATH [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: technical-writer
  cli: "orchestra report <task-id> --output PATH [--json]"
---

# /orchestra:relatorio

## Sintaxe

`/orchestra:relatorio <task-id> --output PATH [--json]`

## Responsável

`technical-writer`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Gerar relatório técnico de uma task em arquivo local.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Task-id e output são obrigatórios; output deve permanecer dentro do projeto e a extensão .json seleciona JSON, qualquer outra usa Markdown.
3. Traduzir para a CLI: Repassar task-id e --output; não aceitar período nem usar --format como formato do relatório.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Arquivo de relatório escrito e caminho relativo confirmado. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra report <task-id> --output PATH [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:relatorio <task-id>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
