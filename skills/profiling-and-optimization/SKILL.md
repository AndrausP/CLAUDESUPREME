---
name: profiling-and-optimization
description: Diagnosticar e corrigir gargalos medidos. Use quando a task exigir latência, throughput, memória e I/O comprovados.
allowed-tools: Read Glob Grep Write Edit Bash
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: performance-engineer
  tags: [backend, performance-evidence, primary]
---

# profiling-and-optimization

## Objetivo

Diagnosticar e corrigir gargalos medidos, produzindo `performance-evidence` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver latência, throughput, memória e I/O comprovados e a task atribuir ownership a `performance-engineer` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não otimiza sem baseline. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para latência, throughput, memória e I/O comprovados.
3. Executar diagnosticar e corrigir gargalos medidos, respeitando o limite: não otimiza sem baseline.
4. Produzir `performance-evidence` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit, Bash. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `performance-evidence`
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

Entrada: task pede latência, throughput, memória e I/O comprovados. Saída: `performance-evidence` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../structured-handoff/SKILL.md`, `../safe-tool-execution/SKILL.md`, `../test-result-validation/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
