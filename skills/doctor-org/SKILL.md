---
name: doctor-org
description: Diagnosticar instalação, catálogos, schemas, CLI e integrações.
argument-hint: [--validate-plugin] [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: operations-lead
  cli: "orchestra doctor [--validate-plugin] [--json]"
---

# /orchestra:doctor-org

## Sintaxe

`/orchestra:doctor-org [--validate-plugin] [--json]`

## Responsável

`operations-lead`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Diagnosticar instalação, catálogos, schemas, CLI e integrações.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: A única opção específica é --validate-plugin; o comando é estritamente read-only.
3. Traduzir para a CLI: Executar doctor diretamente; nenhuma correção é aplicada pelo contrato atual.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Health report com checks e healthy; dependências opcionais permanecem sinalizadas como optional ou warning. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra doctor [--validate-plugin] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:doctor-org [--validate-plugin]` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
