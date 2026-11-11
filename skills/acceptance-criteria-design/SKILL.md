---
name: acceptance-criteria-design
description: Definir critérios objetivos de aprovação. Use quando a task exigir entregas sem condição observável de sucesso.
allowed-tools: Read Glob Grep
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: acceptance-engineer
  tags: [product, acceptance-contract, primary]
---

# acceptance-criteria-design

## Objetivo

Definir critérios objetivos de aprovação, produzindo `acceptance-contract` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver entregas sem condição observável de sucesso e a task atribuir ownership a `acceptance-engineer` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não executa a validação final. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para entregas sem condição observável de sucesso.
3. Executar definir critérios objetivos de aprovação, respeitando o limite: não executa a validação final.
4. Produzir `acceptance-contract` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `acceptance-contract`
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

Entrada: task pede entregas sem condição observável de sucesso. Saída: `acceptance-contract` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../structured-handoff/SKILL.md`, `../risk-classification/SKILL.md`, `../task-decomposition/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
