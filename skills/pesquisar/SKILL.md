---
name: pesquisar
description: Acionar investigação técnica em fontes primárias por meio do especialista correto.
argument-hint: <question> [--json]
disable-model-invocation: false
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: evidence-researcher
  cli: "orchestra route --capability technical-source-research --external-dependencies 1 --validations 1 [--json]"
---

# /orchestra:pesquisar

## Sintaxe

`/orchestra:pesquisar <question> [--json]`

## Responsável

`evidence-researcher`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Acionar investigação técnica em fontes primárias por meio do especialista correto.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Question deve ser verificável e declarar o recorte temporal; a CLI só decide o roteamento, sem fabricar um dossiê.
3. Traduzir para a CLI: Manter question no contexto da skill e usar route para seleção determinística. Não alegar um subcomando research inexistente.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Decisão de roteamento para technical-source-research; o dossiê é produzido pelo agente com fontes e limitações. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra route --capability technical-source-research --external-dependencies 1 --validations 1 [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:pesquisar <question>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
