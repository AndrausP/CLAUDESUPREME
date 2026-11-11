---
name: memory-curation
description: Consolidar, relacionar e expirar memórias. Use quando a task exigir memória proposta, duplicada ou contraditória.
allowed-tools: Read Glob Grep
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: memory-librarian
  tags: [knowledge, memory-proposal, primary]
---

# memory-curation

## Objetivo

Consolidar, relacionar e expirar memórias, produzindo `memory-proposal` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver memória proposta, duplicada ou contraditória e a task atribuir ownership a `memory-librarian` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não promove memória sem evidência. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para memória proposta, duplicada ou contraditória.
3. Executar consolidar, relacionar e expirar memórias, respeitando o limite: não promove memória sem evidência.
4. Produzir `memory-proposal` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `memory-proposal`
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

Entrada: task pede memória proposta, duplicada ou contraditória. Saída: `memory-proposal` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../technical-evidence/SKILL.md`, `../context-compression/SKILL.md`, `../structured-handoff/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
