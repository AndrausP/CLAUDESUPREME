---
name: requirements-extraction
description: Converter pedidos ambíguos em requisitos verificáveis. Use quando a task exigir requisitos implícitos, vagos ou contraditórios.
allowed-tools: Read Glob Grep
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: requirements-analyst
  tags: [product, requirements-spec, primary]
---

# requirements-extraction

## Objetivo

Converter pedidos ambíguos em requisitos verificáveis, produzindo `requirements-spec` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver requisitos implícitos, vagos ou contraditórios e a task atribuir ownership a `requirements-analyst` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não prioriza nem aprova escopo. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para requisitos implícitos, vagos ou contraditórios.
3. Executar converter pedidos ambíguos em requisitos verificáveis, respeitando o limite: não prioriza nem aprova escopo.
4. Produzir `requirements-spec` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `requirements-spec`
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

Entrada: task pede requisitos implícitos, vagos ou contraditórios. Saída: `requirements-spec` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../structured-handoff/SKILL.md`, `../risk-classification/SKILL.md`, `../task-decomposition/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
