# Orchestra Core

Orchestra Core é um plano de controle local-first para organizar 36 competências de engenharia sob demanda no Claude Code. O núcleo determinístico classifica tarefas, aplica budgets, valida transições, persiste checkpoints e registra evidências sem depender do Claude Ledger, de um servidor permanente ou de uma credencial de API. Agentes e skills continuam carregados apenas quando necessários.

## O que existe

- plugin nativo `orchestra` com skills, agentes e hooks oficiais do Claude Code;
- CLI Python sem dependências obrigatórias, com saída texto e JSON;
- roteamento `DIRECT`, `LEAN`, `STANDARD` e `DEEP`;
- workflow persistente, memória local, registry de extensões e eventos sanitizados;
- 36 agentes em sete departamentos mais o Central Orchestrator;
- integração unilateral e opcional com Claude Ledger;
- Rich/Textual opcionais, sempre com fallback estático e `NO_COLOR`.

## Instalação local

Requer Python 3.12 ou superior. Em PowerShell, CMD ou Windows Terminal:

```powershell
python -m pip install -e .
orchestra bootstrap
orchestra status
```

Para instalar a TUI opcional:

```powershell
python -m pip install -e ".[tui]"
orchestra tui
```

## Plugin nativo do Claude Code

Valide e carregue o plugin diretamente do checkout:

```powershell
claude plugin validate .
claude --plugin-dir .
```

As skills ficam namespaced, por exemplo `/orchestra:clareza`, `/orchestra:organizar` e `/orchestra:doctor-org`. O plugin não modifica o binário do Claude Code nem substitui sua interface nativa. A ausência de `icon` pode aparecer como `ICON_MISSING`; esse campo é opcional e não impede o carregamento.

## Uso da CLI

```powershell
orchestra --help
orchestra route --mutation --areas 2 --validations 2
orchestra clareza HIGH src --security
orchestra agents
orchestra skills --query testing
orchestra doctor --validate-plugin
```

Use `--json` para automação e `--plain` ou `NO_COLOR=1` em terminais limitados. O estado de runtime fica em `.orchestra/` dentro do projeto operado e não deve ser versionado.

## Testes

```powershell
python -m pip install -e ".[dev]"   # jsonschema, usado pelos testes de aceitação
python -m unittest discover -s tests -p "test*.py"
claude plugin validate .
```

## Estado validado em 2026-11-11

- QA: `APPROVED`;
- suíte integrada: 77/77, sem falhas, erros, skips ou `PYTHONPATH` manual;
- categorias obrigatórias: 23/23;
- cenários ponta a ponta: 8/8;
- catálogo: 36 agentes, sete departamentos e 36 skills primárias;
- plugin: `claude plugin validate .` e `--profile directory` aprovados;
- wheel: 38.480 bytes, SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`.

Evidências completas estão em `reports/qa/`. O benchmark executou 25 iterações por profile, mas mede somente routing determinístico no host Windows. Não houve chamada real de modelo, baseline equivalente sem Orchestra ou telemetria de billing; tokens e custo permanecem `unknown`.

## Limitações honestas

- O adapter do Agent SDK é opcional e, nesta baseline, detecta disponibilidade e autenticação; execução programática completa não é habilitada automaticamente.
- A TUI Textual é complementar. Rich/Textual não estavam instalados no host de QA; fallback plain/JSON, `TERM=dumb` e `NO_COLOR` foram validados.
- O Claude Ledger é consumidor opcional de manifesto e eventos; a execução sem Ledger passou, mas um aplicativo Ledger real não integrou esta rodada.
- Budgets de tokens no modo nativo podem ser apenas `unknown` ou `estimated` quando a telemetria observada não estiver disponível.
- Hooks e prompts não substituem sandbox, ACLs ou confirmação externa para operações destrutivas.

## Documentação

- [Pesquisa e compatibilidade](docs/research.md)
- [Arquitetura](docs/architecture.md)
- [Requisitos](docs/requirements.md)
- [Instalação](docs/installation.md)
- [Extensões](docs/extensions.md)
- [Integração com Claude Ledger](docs/ledger-integration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Decisões arquiteturais](docs/decisions.md)
- [Contratos e schemas](docs/contracts.md)

## Fontes primárias

As decisões de integração seguem a documentação oficial de [plugins](https://code.claude.com/docs/en/plugins/create.md), [skills](https://code.claude.com/docs/en/skills.md), [subagentes](https://code.claude.com/docs/en/sub-agents.md), [hooks](https://code.claude.com/docs/en/hooks.md), [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md), [execução programática](https://code.claude.com/docs/en/headless.md), [settings](https://code.claude.com/docs/en/settings.md) e [telemetria](https://code.claude.com/docs/en/monitoring-usage.md).
