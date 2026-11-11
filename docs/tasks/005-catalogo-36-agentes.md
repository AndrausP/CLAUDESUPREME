# [BACKEND] Catálogo completo de 36 agentes

- Status: COMPLETED
- Fase: B/C
- Estimativa: 3 dias
- Depende de: 004
- Responsável: Dev Backend

## O que fazer

Criar exatamente 35 agentes em sete departamentos, cinco por departamento incluindo líder, mais Central Orchestrator. Cada definição deve ser única, completa e lazy-loaded.

## Critério de conclusão

- Contagem automatizada retorna exatamente 36.
- Todos têm ID, responsabilidade exclusiva, limites, tools, skill, modelo/alternativas, esforço, budget, I/O, sucesso, escalação, memória, comunicação e critério de não convocação.
- Descrições são curtas; detalhes ficam no corpo.
- Frontmatter passa validação oficial/local.

## Limites de arquivos

`agents/**`, `config/agents.json`, `tests/unit/catalog/test_agents*`.

## Risco

Descrições longas consomem contexto; manter catálogo enxuto e validar duplicatas.

## Contrato técnico consolidado

- Ownership exclusivo: `agents/**`, `config/agents.json` e testes de catálogo; não editar skills.
- Fonte canônica: `config/agents.json`; arquivos Markdown devem corresponder por ID e checksum.
- Exatamente 7 departamentos × 5 agentes + `central-orchestrator`; IDs kebab-case únicos.
- Descrição curta para roteamento; responsabilidade, limites, I/O, budget, memória e não-convocação ficam no corpo.
- Frontmatter usa apenas campos suportados por plugin agents; segurança não depende de campos ignorados.
- Teste falha por contagem, ID duplicado, skill ausente, tools inválidas ou descrição acima do limite acordado.

## Evidência de conclusão

- [x] 36 agentes carregados: sete departamentos com cinco especialistas e Central Orchestrator.
- [x] Frontmatters e vínculos de skills validados automaticamente.
- [x] Catálogo e plugin passaram os gates de QA.

