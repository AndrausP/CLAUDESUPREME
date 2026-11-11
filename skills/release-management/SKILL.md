---
name: release-management
description: Preparar versão, migração e rollback. Use quando a task exigir coordenação de artefatos e janela de entrega.
allowed-tools: Read Glob Grep Write Edit Bash
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: release-manager
  tags: [operations, release-plan, primary]
---

# release-management

## Objetivo

Preparar versão, migração e rollback, produzindo `release-plan` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver coordenação de artefatos e janela de entrega e a task atribuir ownership a `release-manager` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não aprova qualidade técnica. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para coordenação de artefatos e janela de entrega.
3. Executar preparar versão, migração e rollback, respeitando o limite: não aprova qualidade técnica.
4. Produzir `release-plan` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit, Bash. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `release-plan`
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

Entrada: task pede coordenação de artefatos e janela de entrega. Saída: `release-plan` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../safe-tool-execution/SKILL.md`, `../incident-triage/SKILL.md`, `../technical-evidence/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
