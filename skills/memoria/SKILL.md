---
name: memoria
description: Consultar, propor ou revisar estado de memória auditável.
argument-hint: <search|propose|status> <args> [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: memory-librarian
  cli: "orchestra memory <search|propose|status> <args> [--json]"
---

# /orchestra:memoria

## Sintaxe

`/orchestra:memoria <search|propose|status> <args> [--json]`

## Responsável

`memory-librarian`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Consultar, propor ou revisar estado de memória auditável.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Usar exatamente uma ação: search QUERY [--scope SCOPE] [--verified-only]; propose exige --type, --title, --summary e --content-ref; status exige memory-id, status e evidence refs quando disponíveis.
3. Traduzir para a CLI: Repassar a ação e suas opções oficiais; verify e invalidate são valores de status, não subcomandos.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Memórias encontradas, memory_id PROPOSED ou status atualizado. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra memory <search|propose|status> <args> [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:memoria <search|propose|status>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
