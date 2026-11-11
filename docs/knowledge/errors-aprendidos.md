# Erros aprendidos

| Data | Erro | Causa | Correção | Evidência | Agente |
|---|---|---|---|---|---|
| 2026-11-11 | Task podia iniciar mesmo com dependência ausente ou incompleta. | O gate `READY -> RUNNING` não revalidava o grafo de dependências no momento da execução. | Retornar `DEPENDENCY_BLOCKED` até todas as dependências existirem e estarem `COMPLETED`. | Regressões positiva e negativa aprovadas na suíte 77/77. | Dev Backend + QA |
| 2026-11-11 | Cancelamento não expunha prova completa do boundary seguro. | Estado terminal era priorizado sem contrato observável de checkpoint prévio. | Persistir checkpoint `pre-cancellation` com estado anterior, motivo, evidências e `safe_to_resume=true` antes de `CANCELLED`. | Categoria 16 e smoke CLI aprovados. | Dev Backend + QA |
| 2026-11-11 | Exemplos de command skills podiam divergir do parser ou repetir `--json`. | A documentação era validada por texto, não pelo `argparse` efetivo e pela posição das opções globais. | Sincronizar 19 skills com a superfície real e parsear todos os exemplos em teste. | 19/19 exemplos aceitos; nenhuma duplicação. | Dev Backend + QA |
| 2026-11-11 | Build/wheel falhava com `README_MISSING`. | `pyproject.toml` declarava `README.md`, mas o arquivo ainda não existia no diretório do perfil de validação. | Criar README raiz completo antes do empacotamento e validar wheel/profile directory. | Wheel e `claude plugin validate . --profile directory` aprovados. | Writer + QA |
| 2026-11-11 | Teste de TUI completa seria falsamente apresentado como aprovado. | Rich e Textual não estavam instalados no host da revalidação. | Aprovar somente fallback plain/JSON e registrar runtime Rich/Textual como limitação residual. | Relatório QA registra dependências opcionais ausentes. | QA |
| 2026-11-11 | Benchmark poderia sugerir ganhos ou custos inexistentes. | Não havia harness equivalente sem Orchestra, chamadas reais de modelo nem telemetria de billing. | Limitar o benchmark a 25 iterações locais por profile e registrar tokens/custo como `unknown`. | `reports/qa/profile-matrix.json`. | QA |

## Limitações conhecidas

- `ICON_MISSING` permanece aviso opcional do validator; não bloqueia o plugin.
- Instalação via marketplace não foi testada porque `<owner>/<repo>` ainda não foi publicado.
- Rich/Textual, Claude Ledger real e Agent SDK com modelo autenticado não foram executados no host de QA.
- O benchmark mede routing determinístico em um único Windows; não mede qualidade de modelo, custo por sucesso ou ganho contra baseline sem Orchestra.
