---
name: clareza
description: Revisar tarefa, diff, código ou arquitetura com evidência proporcional ao risco.
argument-hint: [quick|normal|high] [target] [--task-id ID] [--security] [--architecture] [--timeout SECONDS] [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: code-review-specialist
  cli: "orchestra clareza [QUICK|NORMAL|HIGH] [target] [--task-id ID] [--security] [--architecture] [--timeout SECONDS] [--json]"
---

# /orchestra:clareza

## Sintaxe

`/orchestra:clareza [quick|normal|high] [target] [--task-id ID] [--security] [--architecture] [--timeout SECONDS] [--json]`

## Responsável

`code-review-specialist`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Revisar tarefa, diff, código ou arquitetura com evidência proporcional ao risco.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Profundidade pública deve ser quick, normal ou high; HIGH aceita no máximo dois especialistas justificados. O target fica dentro do projeto e timeout é inteiro positivo.
3. Traduzir para a CLI: Normalizar quick, normal ou high para QUICK, NORMAL ou HIGH antes de chamar a CLI; preservar as flags oficiais --security e --architecture.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

ReviewReport v1 com veredicto APPROVED, APPROVED_WITH_NOTES, CHANGES_REQUESTED ou INCONCLUSIVE. Cada achado informa gravidade, arquivo, localização, evidência, impacto, correção proposta e confiança. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra clareza [QUICK|NORMAL|HIGH] [target] [--task-id ID] [--security] [--architecture] [--timeout SECONDS] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:clareza [quick|normal|high]` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
