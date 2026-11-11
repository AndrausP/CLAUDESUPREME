---
name: planejar
description: Persistir a conclusão do planejamento e seus critérios/evidências na task.
argument-hint: <task-id> [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]
disable-model-invocation: true
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: command
  owner: product-lead
  cli: "orchestra task transition <task-id> PLANNED [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]"
---

# /orchestra:planejar

## Sintaxe

`/orchestra:planejar <task-id> [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]`

## Responsável

`product-lead`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

Persistir a conclusão do planejamento e seus critérios/evidências na task.

1. Interpretar argumentos sem executar texto como shell.
2. Validar: Task existente deve aceitar a transição PLANNED; critérios são registrados antes com task criteria quando necessário; cada evidência usa --evidence.
3. Traduzir para a CLI: Fixar o estado de destino em PLANNED. O texto do plano é artefato referenciado, nunca argumento livre persistido como transcript.
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

Task v1 atualizada para PLANNED ou erro tipado de transição. Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`orchestra task transition <task-id> PLANNED [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:planejar <task-id>` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
