# [BACKEND] Catálogo de skills principais e compartilhadas

- Status: COMPLETED
- Fase: B/C
- Estimativa: 3 dias
- Depende de: 005
- Responsável: Dev Backend

## O que fazer

Criar as 36 skills principais nomeadas na especificação e skills compartilhadas sem duplicação. Aplicar progressive disclosure e catálogo pesquisável.

## Critério de conclusão

- Cada agente referencia uma skill principal existente.
- Cada `SKILL.md` contém objetivo, uso/não uso, pré-condições, procedimento, ferramentas, saída, validação, erros e exemplo.
- Skills de efeito colateral são manuais.
- Catálogo pesquisa por responsabilidade, tag, tarefa e compatibilidade.

## Limites de arquivos

`skills/**`, `config/skills.json`, `tests/unit/catalog/test_skills*`.

## Risco

Conteúdo duplicado aumenta manutenção; procedimentos comuns devem ser referenciados.

## Contrato técnico consolidado

- Ownership exclusivo: `skills/**`, `config/skills.json` e testes de catálogo; não editar agentes fora de correção referencial coordenada.
- Fonte canônica: catálogo JSON; cada `SKILL.md` permanece abaixo de 500 linhas e referencia material longo em `references/`.
- Skills com efeito colateral usam `disable-model-invocation: true`; skills informativas podem ser model-invocable.
- 36 skills principais são 1:1 com competências; procedimentos compartilhados têm IDs próprios e são referenciados, não copiados.
- Teste valida frontmatter, descoberta, referência agente→skill, tags, compatibilidade, exemplos e conteúdo mínimo obrigatório.

## Evidência de conclusão

- [x] 36 skills primárias descobertas e ligadas aos agentes.
- [x] Progressive disclosure e frontmatter verificados.
- [x] Catálogo pesquisável coberto pelos testes de catálogo.

