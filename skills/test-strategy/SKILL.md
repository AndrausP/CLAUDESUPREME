---
name: test-strategy
description: Definir cobertura proporcional ao risco. Use quando a task exigir lacunas entre risco, critérios e níveis de teste.
allowed-tools: Read Glob Grep
compatibility: Claude Code >=2.1.322; Windows, Linux, macOS
metadata:
  kind: primary
  owner: test-strategist
  tags: [quality, test-strategy, primary]
---

# test-strategy

## Objetivo

Definir cobertura proporcional ao risco, produzindo `test-strategy` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver lacunas entre risco, critérios e níveis de teste e a task atribuir ownership a `test-strategist` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; não infla suíte sem justificativa. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para lacunas entre risco, critérios e níveis de teste.
3. Executar definir cobertura proporcional ao risco, respeitando o limite: não infla suíte sem justificativa.
4. Produzir `test-strategy` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

Read, Glob, Grep. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `test-strategy`
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

Entrada: task pede lacunas entre risco, critérios e níveis de teste. Saída: `test-strategy` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: `../git-diff-analysis/SKILL.md`, `../technical-evidence/SKILL.md`, `../test-result-validation/SKILL.md`. Carregue somente o arquivo necessário à etapa atual.
