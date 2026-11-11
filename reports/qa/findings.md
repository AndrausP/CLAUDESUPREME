# Evidência de revalidação QA — Orchestra Core

Data observada: 2026-11-11  
Status: `APPROVED`

## Resultado consolidado

| Gate | Resultado | Evidência observada |
|---|---:|---|
| Descoberta padrão | PASS | `python -m unittest discover -s tests -v`, sem `PYTHONPATH` |
| Suíte integrada | PASS | 77 executados; 77 aprovados; 0 falhas; 0 erros; 0 skips |
| Categorias obrigatórias | PASS | 23/23, mais regressão explícita de dependências |
| Cenários reais | PASS | 8/8 |
| Catálogo | PASS | 36 agentes; 7 departamentos com 5 especialistas; 36 skills primárias; 19 command skills |
| Dependências | PASS | execução bloqueada enquanto incompletas e liberada quando todas estão `COMPLETED` |
| Cancelamento seguro | PASS | checkpoint `pre-cancellation` persistido e exposto antes de `CANCELLED` |
| Contratos CLI | PASS | 19 exemplos aceitos pelo parser real; nenhum `--json --json` |
| `compileall` | PASS | `python -m compileall -q src scripts tests benchmarks` |
| Instalação editable | PASS | `python -m pip install -e . --no-deps` instalou `orchestra-core 0.1.0` |
| Wheel | PASS | 38.480 bytes; SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682` |
| Plugin nativo | PASS | `claude plugin validate .` |
| Plugin directory | PASS | `claude plugin validate . --profile directory` |
| Smoke CLI | PASS | version, status JSON e doctor plain com `TERM=dumb`/`NO_COLOR` |
| Wrappers | PASS | `.cmd`, `.ps1` e POSIX via Git Bash retornaram `orchestra 0.1.0` |
| Benchmark | PASS limitado | 25 iterações por profile; métricas observadas em `profile-matrix.json` |

## Correções revalidadas

- Dependência inexistente ou não concluída retorna `DEPENDENCY_BLOCKED` antes de `READY -> RUNNING`.
- Dependências integralmente concluídas permitem a transição.
- Cancelamento pelo CLI grava checkpoint com estado anterior, motivo, evidências e `safe_to_resume=true`.
- As 19 command skills estão sincronizadas com a superfície real do parser.
- O README existe, supera o mínimo de 40 palavras e remove o bloqueio `README_MISSING`.

## Avisos não bloqueantes

- O validator recomenda um ícone quadrado para o diretório (`ICON_MISSING`).
- O validator recomenda incluir no README a linha de instalação via marketplace quando `<owner>/<repo>` estiver definido.
- `rich`, `textual` e Ledger não estavam instalados. São integrações opcionais; core, fallback plain e execução sem Ledger passaram.
- `sh` não está no `PATH` do PowerShell; o wrapper POSIX foi executado com `C:\Program Files\Git\bin\bash.exe` e passou.

## Limitações do benchmark

- Mede somente roteamento determinístico local, em um host Windows.
- Não executa chamadas reais de modelo nem fornece comparação equivalente sem Orchestra.
- Tokens e custo permanecem `null`, com proveniência `unknown`; nenhum valor foi fabricado.

## Artefatos

- `reports/qa/profile-matrix.json`
- `reports/qa/test-plan.md`
- `reports/qa/wheels/orchestra_core-0.1.0-py3-none-any.whl`

