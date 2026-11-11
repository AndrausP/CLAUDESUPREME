# Instalação

## Pré-requisitos

- Python 3.12 ou superior;
- Git para desenvolvimento e worktrees;
- Claude Code instalado somente para validar/carregar o plugin nativo.

O núcleo usa `sqlite3` da biblioteca padrão do Python. O executável externo `sqlite3` não é necessário. Rich, Textual, Claude Agent SDK e Claude Ledger são opcionais.

## Instalação editável

No diretório raiz do Orchestra Core:

```powershell
python -m pip install -e .
orchestra --version
orchestra bootstrap
orchestra status
```

O bootstrap é idempotente e cria o estado de runtime em `.orchestra/` do projeto operado. Esse diretório contém dados locais e está excluído do Git.

Para desenvolvimento isolado:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## TUI opcional

```powershell
python -m pip install -e ".[tui]"
orchestra tui
```

Se Rich/Textual não estiverem instalados, o terminal não for interativo ou `TERM=dumb`, use:

```powershell
$env:NO_COLOR = "1"
orchestra --plain status
```

A TUI não substitui nem controla a interface nativa do Claude Code; ela consulta os mesmos serviços de aplicação da CLI.

## Plugin Claude Code em desenvolvimento

```powershell
claude plugin validate .
claude --plugin-dir .
```

O validador deve ser executado contra a raiz que contém `.claude-plugin/plugin.json`. O `README.md` da raiz também é o arquivo declarado em `pyproject.toml`, portanto precisa existir antes de construir um wheel. O aviso `ICON_MISSING` é aceitável: `icon` é metadado opcional e não altera a execução.

Depois de carregar o plugin, as skills usam namespace, por exemplo:

```text
/orchestra:clareza HIGH src/ --security
/orchestra:doctor-org
```

## Verificação local

```powershell
python -m unittest discover -s tests -p "test*.py"
orchestra doctor --validate-plugin
claude plugin validate .
```

Esses comandos devem ser executados no ambiente de destino. Registre a saída real em `reports/qa/`; não considere esta página evidência de aprovação.

Na revalidação de 2026-11-11, instalação editable, wheel, plugin normal/directory, wrappers `.cmd`/`.ps1`/POSIX e smoke CLI passaram. A suíte executou 77/77 testes, 23/23 categorias e 8/8 cenários. Rich/Textual não estavam instalados, portanto a aprovação da interface cobre o fallback plain/JSON, não o runtime fullscreen.

## Build de pacote

```powershell
python -m pip install build
python -m build
```

Os diretórios `build/`, `dist/` e `*.egg-info/` são artefatos locais e ficam ignorados. Artefatos explicitamente preservados em `reports/qa/` não são ignorados.

Wheel validado: `orchestra_core-0.1.0-py3-none-any.whl`, 38.480 bytes, SHA-256 `232E83BBAED92562BD5D04179928F7BF8C32F6B804B02431DBC388F5E0678682`.
