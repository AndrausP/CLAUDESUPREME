# [QA] Cenários reais, benchmark e empacotamento Windows

- Status: COMPLETED
- Fase: F
- Estimativa: 3 dias
- Depende de: 011, 013
- Responsável: QA + Dev Frontend

## O que fazer

Executar oito cenários reais, matriz A/B/C/D de perfis, testes PowerShell/CMD/Windows Terminal/no-color e build instalável. Registrar apenas dados observados.

## Critério de conclusão

- Cada cenário possui fixture, resultado esperado e evidência.
- Benchmark usa tarefas equivalentes, múltiplas execuções quando possível e fórmula documentada.
- Não há percentuais inventados; amostra insuficiente é declarada.
- Artefato Windows inicia e executa `doctor` e `status`.

## Limites de arquivos

`tests/end-to-end/**`, `tests/benchmarks/**`, `examples/**`, config de build e `docs/benchmarks.md`.

## Risco

Uma única máquina não comprova portabilidade; separar observado de não validado.

## Contrato técnico consolidado

- Ownership: QA possui cenários/medição; Frontend possui packaging e correções de compatibilidade; Writer apenas documenta resultados aprovados.
- Cenários usam fixtures equivalentes e registram ambiente, versão, profile, duração, tokens quando observáveis, retrabalho e critérios satisfeitos.
- Custo por sucesso só é calculado com numerador e sucesso verificado; caso contrário é `unknown`.
- Matrix mínima local: PowerShell, CMD, `TERM=dumb`, `NO_COLOR`, non-TTY e interrupção/retomada.
- Build Windows deve executar bootstrap, `doctor`, `status` e operação sem extras.

## Evidência de conclusão

- [x] 8/8 cenários ponta a ponta aprovados.
- [x] 25 iterações por profile registradas em `reports/qa/profile-matrix.json`.
- [x] Wheel de 38.480 bytes validado com SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`.
- [ ] Não houve chamadas reais de modelo, baseline equivalente sem Orchestra ou billing.

Conclusão com limitação: benchmark aprovado somente como microbenchmark de routing determinístico em um host Windows; nenhum ganho percentual foi inferido.

