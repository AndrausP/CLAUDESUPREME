---
name: frontend-coordination
description: Coordenar implementação visual e integração de ui. Use quando a task exigir fluxos que cruzam componentes ou especialistas.
allowed-tools: Read Glob Grep Write Edit
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: frontend-lead
  tags: [frontend, frontend-plan, primary]
---

# frontend-coordination

## Objetivo

Coordenar implementação visual e integração de ui, produzindo `frontend-plan` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver fluxos que cruzam componentes ou especialistas e a task atribuir ownership a `frontend-lead` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não redefine requisitos de produto. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para fluxos que cruzam componentes ou especialistas.
3. Executar coordenar implementação visual e integração de UI, respeitando o limite: não redefine requisitos de produto.
4. Produzir `frontend-plan` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `frontend-plan`
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

Entrada: task pede fluxos que cruzam componentes ou especialistas. Saída: `frontend-plan` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../structured-handoff/SKILL.md`, `../technical-evidence/SKILL.md`, `../test-result-validation/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
