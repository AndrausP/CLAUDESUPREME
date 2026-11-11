---
name: system-design
description: Projetar componentes, limites e dependências. Use quando a task exigir novos módulos e mudanças cross-cutting.
allowed-tools: Read Glob Grep Write Edit Bash
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: solution-architect
  tags: [architecture, solution-design, primary]
---

# system-design

## Objetivo

Projetar componentes, limites e dependências, produzindo `solution-design` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver novos módulos e mudanças cross-cutting e a task atribuir ownership a `solution-architect` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não aprova prioridade de produto. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para novos módulos e mudanças cross-cutting.
3. Executar projetar componentes, limites e dependências, respeitando o limite: não aprova prioridade de produto.
4. Produzir `solution-design` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit, Bash. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `solution-design`
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

Entrada: task pede novos módulos e mudanças cross-cutting. Saída: `solution-design` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../structured-handoff/SKILL.md`, `../technical-evidence/SKILL.md`, `../dependency-analysis/SKILL.md`, `../artifact-contracts/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
