---
name: backend-coordination
description: Coordenar e validar entregas de backend. Use quando a task exigir múltiplos especialistas backend ou integração conflitante.
allowed-tools: Read Glob Grep Write Edit
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: backend-lead
  tags: [backend, backend-plan, primary]
---

# backend-coordination

## Objetivo

Coordenar e validar entregas de backend, produzindo `backend-plan` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver múltiplos especialistas backend ou integração conflitante e a task atribuir ownership a `backend-lead` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não substitui especialistas em task simples. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para múltiplos especialistas backend ou integração conflitante.
3. Executar coordenar e validar entregas de backend, respeitando o limite: não substitui especialistas em task simples.
4. Produzir `backend-plan` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, Write, Edit. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `backend-plan`
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

Entrada: task pede múltiplos especialistas backend ou integração conflitante. Saída: `backend-plan` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../structured-handoff/SKILL.md`, `../safe-tool-execution/SKILL.md`, `../test-result-validation/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
