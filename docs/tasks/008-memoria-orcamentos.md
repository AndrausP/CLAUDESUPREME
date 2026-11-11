# [BACKEND] Memória organizacional e orçamentos

- Status: COMPLETED
- Fase: C
- Estimativa: 3 dias
- Depende de: 003, 006
- Responsável: Dev Backend

## O que fazer

Completar memórias organizacional, projeto, departamento/agente e episódica; deduplicação, contradição, expiração e consolidação. Implementar perfis ECONOMY/BALANCED/QUALITY/CRITICAL e interrupção/recuperação por budget.

## Critério de conclusão

- Estados PROPOSED, VERIFIED, OUTDATED, SUPERSEDED e REJECTED são testados.
- Fatos importantes exigem evidência e versão.
- Busca textual funciona sem embeddings; semântica é opcional.
- Métricas indisponíveis ficam `unknown`; custos locais ficam `estimated`.

## Limites de arquivos

`src/orchestra/memory/**`, `src/orchestra/budgets/**`, `config/profiles/**`, `tests/unit/{memory,budgets}/**`.

## Risco

Salvar conversa ou segredo por padrão é proibido.

## Contrato técnico consolidado

- Ownership: `src/orchestra/{memory,budgets}/**`, `schemas/memory*.json`, `config/profiles/**` e respectivos testes.
- `Memory v1` aceita quatro tipos e cinco estados; somente VERIFIED entra automaticamente no contexto.
- Deduplicação usa chave canônica + hash sanitizado; contradição cria relação, nunca overwrite silencioso.
- Perfis limitam calls, agents, retries, rework, duração e bytes; segurança mínima não é configurável para baixo.
- Token budget no Native é advisory quando não observado; `unknown` usa `value:null`; custo SDK é `estimated`.
- Conteúdo durável humano fica em Markdown sob governança do Writer; runtime persiste índice/metadados no SQLite.

## Evidência de conclusão

- [x] Quatro tipos e cinco estados de memória exercitados.
- [x] Deduplicação, evidência e busca textual aprovadas.
- [x] Perfis ECONOMY/BALANCED/QUALITY/CRITICAL verificados.
- [x] Tokens/custo permanecem `unknown` por ausência de fonte observada.

