# [FRONTEND] CLI funcional e fallback legível

- Status: COMPLETED
- Fase: D
- Estimativa: 3 dias
- Depende de: 003, 007, 009
- Responsável: Dev Frontend

## O que fazer

Criar executável `orchestra` com bootstrap, tasks, agentes, departamentos, skills, MCP, memória, budgets, registry, doctor e launch do Claude Code. Garantir saída não interativa e `--no-color`.

## Critério de conclusão

- PowerShell, CMD e Windows Terminal recebem comandos equivalentes.
- UTF-8 e CP850 não corrompem dados persistidos.
- `NO_COLOR`, terminal não-TTY e `TERM=dumb` usam fallback estático.
- Erros retornam exit codes e mensagens acionáveis.

## Limites de arquivos

`src/orchestra/cli/**`, `bin/**`, `tests/integration/cli/**`, configuração de empacotamento.

## Risco

Terminal atual é degradado; não depender de ANSI ou modo interativo.

## Contrato técnico consolidado

- Ownership: `src/orchestra/cli/**`, launchers em `bin/**`, packaging e testes CLI; não acessar SQLite diretamente fora dos ports.
- Baseline: `argparse` + renderer stdlib. Rich é extra opcional, nunca requisito de comando.
- Todos os comandos suportam automação não interativa com `--json`; stdout carrega resultado, stderr carrega diagnóstico e exit code é estável.
- `NO_COLOR`, non-TTY, `TERM=dumb` ou import ausente forçam texto estático.
- Persistência é UTF-8; encoding do console recebe adaptação na borda sem alterar bytes armazenados.
- Launch do Claude Code usa subprocesso documentado e não promete controle de sessão nativa.

## Evidência de conclusão

- [x] Instalação editable e smoke de version/status/doctor aprovados.
- [x] Wrappers `.cmd`, `.ps1` e POSIX via Git Bash aprovados.
- [x] `TERM=dumb`, `NO_COLOR`, plain e JSON exercitados.
- [x] Windows Terminal gráfico não foi exigido para validar o fallback.

