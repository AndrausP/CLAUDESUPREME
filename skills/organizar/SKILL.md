---
name: organizar
description: Criar uma solicitação persistente para processamento pela esteira.
argument-hint: <title> --objective <text> [--owner ID] [--criteria TEXT ...] [--profile PROFILE] [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: central-orchestrator
  cli: "orchestra task create <title> --objective <text> [--owner ID] [--criteria TEXT ...] [--profile PROFILE] [--json]"
---

# /orchestra:organizar

## Sintaxe

`/orchestra:organizar <title> --objective <text> [--owner ID] [--criteria TEXT ...] [--profile PROFILE] [--json]`

## Responsável

`central-orchestrator`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Criar uma solicitação persistente para processamento pela esteira.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Title e objective são obrigatórios; profile deve ser ECONOMY, BALANCED, QUALITY ou CRITICAL; cada critério usa uma ocorrência de --criteria.
3. Traduzir para a CLI: Mapear diretamente para task create e não executar roteamento implícito.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Task v1 em CREATED, com owner, profile e critérios normalizados. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra task create <title> --objective <text> [--owner ID] [--criteria TEXT ...] [--profile PROFILE] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:organizar <title>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
