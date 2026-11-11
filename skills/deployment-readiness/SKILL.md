---
name: deployment-readiness
description: Decidir prontidão operacional. Use quando a task exigir conflitos de release, observabilidade e rollback.
allowed-tools: Read Glob Grep Write Edit
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: operations-lead
  tags: [operations, readiness-verdict, primary]
---

# deployment-readiness

## Objetivo

Decidir prontidão operacional, produzindo `readiness-verdict` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver conflitos de release, observabilidade e rollback e a task atribuir ownership a `operations-lead` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não executa deploy não autorizado. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para conflitos de release, observabilidade e rollback.
3. Executar decidir prontidão operacional, respeitando o limite: não executa deploy não autorizado.
4. Produzir `readiness-verdict` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `readiness-verdict`
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

Entrada: task pede conflitos de release, observabilidade e rollback. Saída: `readiness-verdict` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../safe-tool-execution/SKILL.md`, `../incident-triage/SKILL.md`, `../technical-evidence/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
