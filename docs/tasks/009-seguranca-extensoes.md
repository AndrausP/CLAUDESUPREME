# [BACKEND] Segurança, permissões e registry de extensões

- Status: COMPLETED
- Fase: C
- Estimativa: 3 dias
- Depende de: 002, 003
- Responsável: Dev Backend

## O que fazer

Implementar registry versionado para agentes, departamentos, skills, MCP, comandos, hooks, validadores, workflows e storage. Aplicar quarentena, checksum, HTTPS, menor privilégio, validação de origem, conflitos, disable/remove seguro e proteção de secrets/logs.

## Critério de conclusão

- Extensão desconhecida nunca executa durante análise.
- Operação destrutiva exige confirmação externa ao prompt do agente.
- Hooks bloqueiam padrões destrutivos e protegem arquivos de política.
- Import/export e rollback preservam estado válido.

## Limites de arquivos

`src/orchestra/registry/**`, `src/orchestra/security/**`, `hooks/**`, `tests/{unit,integration}/security/**`.

## Risco

Supply-chain e prompt injection; prompts não contam como isolamento.

## Contrato técnico consolidado

- Ownership: `src/orchestra/{registry,security}/**`, `schemas/component*.json`, hooks de proteção e testes de segurança.
- `Component Registry v1` inicia origem externa em `quarantined`; somente HTTPS, sem symlink, com checksum e análise sem execução.
- Instalar, remover, elevar permissão ou executar ação destrutiva exige decisão do host/usuário fora de texto gerado pelo modelo.
- Hooks são defesa complementar; sandbox, deny rules, worktree/ACL e scopes continuam necessários.
- Logs e eventos usam allowlist; secrets, prompts, responses, reasoning, args crus e paths absolutos são recusados/redigidos.
- Registry nunca escreve diretamente no core state fora dos application services.

## Evidência de conclusão

- [x] Confirmação externa e checksum exigidos para ativação/remoção.
- [x] Eventos e logs sanitizados, sem prompts ou argumentos crus.
- [x] Atualização/desinstalação é a categoria obrigatória 23/23.

