---
name: workflow-routing
description: Classificar trabalho e selecionar o menor conjunto suficiente. Use quando a task exigir tarefas que exigem roteamento, orçamento e coordenação.
allowed-tools: Read Glob Grep Write Edit
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: central-orchestrator
  tags: [central, execution-plan, primary]
---

# workflow-routing

## Objetivo

Classificar trabalho e selecionar o menor conjunto suficiente, produzindo `execution-plan` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver tarefas que exigem roteamento, orçamento e coordenação e a task atribuir ownership a `central-orchestrator` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não implementa quando existe especialista adequado. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para tarefas que exigem roteamento, orçamento e coordenação.
3. Executar classificar trabalho e selecionar o menor conjunto suficiente, respeitando o limite: não implementa quando existe especialista adequado.
4. Produzir `execution-plan` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `execution-plan`
- `status`: `completed`, `blocked` ou `inconclusive`
- `decisions`, `evidence_refs`, `risks`, `next_action`
- métricas sempre com provenance `observed|calculated|estimated|unknown`

## Critérios de validação

O artefato corresponde ao objetivo, cobre cada critério de aceite aplicável, resolve suas referências, não contém segredo e diferencia fato de hipótese.

## Casos de erro

- Entrada inválida: retornar `INVALID_SCHEMA`.
- Permissão ou evidence ausente: retornar `PERMISSION_DENIED` ou `VALIDATION_INCONCLUSIVE`.
- Budget ou repetição esgotados: checkpoint e `BUDGET_EXHAUSTED`/`REWORK_LOOP`.
- Conflito de mandato: escalar sem executar trabalho alheio.

## Exemplo curto

Entrada: task pede tarefas que exigem roteamento, orçamento e coordenação. Saída: `execution-plan` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../token-budgeting/SKILL.md`, `../risk-classification/SKILL.md`, `../task-decomposition/SKILL.md`, `../context-compression/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
