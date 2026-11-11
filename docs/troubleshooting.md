# Troubleshooting

## `orchestra` não é reconhecido

Confirme Python 3.12+ e reinstale em modo editável:

```powershell
python --version
python -m pip install -e .
python -m orchestra_core.cli --help
```

Se `python -m orchestra_core.cli` funcionar e `orchestra` não, reinicie o terminal e confira o diretório de scripts do Python no `PATH`.

## Build reclama que `README.md` não existe

Execute o build na raiz do checkout. `pyproject.toml` declara `README.md` como metadata do pacote; versões anteriores do diretório incompleto não podem ser empacotadas. Limpe apenas os artefatos locais `build/`, `dist/` e `src/*.egg-info/`, reinstale e tente novamente.

## Validator do plugin

```powershell
claude --version
claude plugin validate .
```

Rode contra a raiz que contém `.claude-plugin/plugin.json`. `ICON_MISSING` é aviso opcional. Erros de manifesto, frontmatter, caminhos fora do plugin ou arquivos ausentes devem ser corrigidos antes do carregamento.

## Skill ou agente não aparece

- confirme `skills/<nome>/SKILL.md` ou `agents/<departamento>/<agente>.md`;
- verifique se `---` é a primeira linha e se o YAML é válido;
- recarregue plugins ou inicie nova sessão;
- use o nome completo `/orchestra:<skill>` para evitar colisões;
- execute `claude plugin validate .`.

## Saída corrompida, sem cores ou `TERM=dumb`

O fallback recomendado é estático:

```powershell
$env:NO_COLOR = "1"
orchestra --plain status
orchestra --json status
```

No Windows, use UTF-8 quando o host permitir (`chcp 65001`) e uma fonte monoespaçada compatível. Não force Rich/Textual em redirecionamento, CI, CMD legado ou terminal que não anuncia TTY.

## TUI não inicia

```powershell
python -m pip install -e ".[tui]"
orchestra tui
```

Se o terminal não suportar fullscreen, use a CLI. `orchestra tui --force` serve somente para diagnóstico; não torna um terminal incompatível seguro ou legível.

## Banco local bloqueado ou indisponível

- confirme que o projeto está em disco local, não em pasta de rede/sincronização;
- encerre processos Orchestra que usem o mesmo `.orchestra/`;
- não edite o SQLite manualmente;
- use `orchestra doctor` e preserve o banco/checkpoints antes de qualquer recuperação.

O Orchestra usa `sqlite3` do Python; instalar o executável `sqlite3` não é necessário.

## Agent SDK indisponível

O modo nativo e a CLI não dependem do SDK. O adapter programático exige pacote opcional, autenticação oficial gerenciada pelo host e configuração explícita. A baseline atual pode retornar `VALIDATION_INCONCLUSIVE` para execução programática; isso não é falha do modo nativo.

Nunca extraia nem encaminhe credenciais pessoais de assinatura para contornar autenticação.

## Export do Ledger falha

- confirme permissão de escrita no `--output`;
- valide manifest/eventos contra os schemas locais;
- remova ou corrija somente a linha JSONL inválida após preservar o arquivo original;
- trate o Ledger como consumidor opcional: sua indisponibilidade não deve bloquear tasks.

## `graphify-out/` ou relatórios de QA aparecem no Git

Isso é intencional. `.gitignore` não exclui `graphify-out/` nem `reports/qa/`, pois a memória indexada e as evidências de validação podem precisar ser compartilhadas. Se o projeto decidir não versioná-los, registre a decisão antes de mudar a política.

## Diagnóstico mínimo

```powershell
orchestra --version
orchestra bootstrap
orchestra doctor --validate-plugin
python -m unittest discover -s tests -p "test*.py"
claude plugin validate .
```

Anexe saídas sanitizadas e versão/terminal ao relatório; não inclua prompts, tokens, chaves ou argumentos sensíveis.

Baseline de referência validada em 2026-11-11: 77/77 testes, 23/23 categorias, 8/8 cenários e wheel SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`. Compare novos resultados com essa evidência sem presumir que dependências opcionais ou outros sistemas operacionais foram cobertos.
