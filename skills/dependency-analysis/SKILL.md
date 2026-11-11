---
name: dependency-analysis
description: Mapear dependências diretas, transitivas e contratos afetados.
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: shared
  tags: [shared, evidence, workflow]
---

# dependency-analysis

## Objetivo

Mapear dependências diretas, transitivas e contratos afetados.

## Quando utilizar

Use quando uma skill principal referenciar este procedimento ou quando a task exigir explicitamente esta técnica.

## Quando não utilizar

Não use como substituto de ownership, decisão de produto ou validação específica do domínio.

## Pré-condições

Objetivo, escopo, budget, permissões e critérios de aceite conhecidos.

## Procedimento

1. Validar o escopo e selecionar apenas a evidência necessária.
2. Executar o procedimento de forma determinística onde possível.
3. Registrar origem, resultado, limitações e referências resolvíveis.
4. Rejeitar dado sensível ou não verificável; escalar conflito de ownership.

## Ferramentas necessárias

Somente ferramentas já autorizadas ao agente chamador; esta skill não amplia permissões.

## Formato de saída

Objeto resumido com `status`, `evidence_refs`, `limitations` e `next_action`.

## Critérios de validação

Resultado reproduzível, referências válidas e ausência de histórico ou segredo desnecessário.

## Casos de erro

Entrada incompleta retorna `INVALID_SCHEMA`; evidência insuficiente retorna `VALIDATION_INCONCLUSIVE`.

## Exemplo curto

Uma skill principal solicita `dependency-analysis`; o procedimento devolve evidência compacta e a referência do artefato, sem copiar seu conteúdo integral.
