---
name: technical-source-research
description: Recuperar e avaliar fontes técnicas primárias. Use quando a task exigir decisão que depende de capacidade externa mutável.
allowed-tools: Read Glob Grep WebFetch WebSearch
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: evidence-researcher
  tags: [knowledge, research-dossier, primary]
---

# technical-source-research

## Objetivo

Recuperar e avaliar fontes técnicas primárias, produzindo `research-dossier` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver decisão que depende de capacidade externa mutável e a task atribuir ownership a `evidence-researcher` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não usa fonte secundária quando há primária. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para decisão que depende de capacidade externa mutável.
3. Executar recuperar e avaliar fontes técnicas primárias, respeitando o limite: não usa fonte secundária quando há primária.
4. Produzir `research-dossier` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep, WebFetch, WebSearch. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `research-dossier`
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

Entrada: task pede decisão que depende de capacidade externa mutável. Saída: `research-dossier` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../technical-evidence/SKILL.md`, `../context-compression/SKILL.md`, `../structured-handoff/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
