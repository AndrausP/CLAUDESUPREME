# [QA] Testes automatizados e gates de qualidade

- Status: COMPLETED
- Fase: F
- Estimativa: 3 dias
- Depende de: 005, 006, 007, 008, 009, 010, 012
- Responsável: QA

## O que fazer

Implementar as 23 categorias obrigatórias de testes, validação de frontmatter/plugin/schemas, falhas de ferramentas, recuperação, cancelamento, anti-loop, permissões e operação sem Ledger.

## Critério de conclusão

- Suite informa quantidade, duração, skips e falhas reais.
- Plugin validator e testes locais passam.
- Cobertura crítica inclui transições, segurança, budgets e sanitização.
- Nenhum teste marcado como executado sem evidência de comando/saída.

## Limites de arquivos

`tests/**`, configuração de CI e `docs/validation.md` apenas para evidências automáticas.

## Risco

Dependências opcionais exigem matriz de skips explícitos, não falso sucesso.

## Contrato técnico consolidado

- Ownership QA: `tests/**` e configuração de CI; mudanças em produção retornam ao Dev responsável.
- Gates: JSON Schema success/failure fixtures, state edges, revision conflicts, outbox idempotente, recovery, budgets, redaction, registry quarantine e plugin validator.
- Cada skip informa requisito ausente e não conta como aprovação da superfície.
- Teste de plugin valida forma; testes semânticos validam 36 agentes/skills e comandos.
- Falha QA retorna à task implementadora com evidence ID; não segue ao Writer.

## Evidência de conclusão

- [x] 77/77 testes, zero falhas, erros e skips.
- [x] 23/23 categorias obrigatórias aprovadas.
- [x] `compileall`, instalação editable, wheel e plugin validators aprovados.
- [x] `reports/qa/test-plan.md` e `reports/qa/findings.md` preservam evidências.

