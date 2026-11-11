---
name: repository-mapping
description: Mapear repositórios e dependências em modo read-only. Use quando a task exigir código desconhecido sem índice confiável.
allowed-tools: Read Glob Grep
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: repository-cartographer
  tags: [knowledge, repository-map, primary]
---

# repository-mapping

## Objetivo

Mapear repositórios e dependências em modo read-only, produzindo `repository-map` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver código desconhecido sem índice confiável e a task atribuir ownership a `repository-cartographer` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não decide nem modifica arquivos. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para código desconhecido sem índice confiável.
3. Executar mapear repositórios e dependências em modo read-only, respeitando o limite: não decide nem modifica arquivos.
4. Produzir `repository-map` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `repository-map`
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

Entrada: task pede código desconhecido sem índice confiável. Saída: `repository-map` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../technical-evidence/SKILL.md`, `../context-compression/SKILL.md`, `../structured-handoff/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
