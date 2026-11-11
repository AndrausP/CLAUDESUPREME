# CLI examples

```powershell
orchestra bootstrap --plain
orchestra task create "Add authentication" --objective "Protect the API" --criteria "Unauthorized requests return 401"
orchestra route --mutation --security --capability threat-modeling --json
orchestra clareza HIGH src/auth --security
orchestra doctor --validate-plugin
orchestra ledger export
```

Every command works without Rich, Textual, Claude Ledger, a network service, or
an API credential. `--json` is stable machine output; `--plain` is the ASCII
baseline for redirected output, screen readers, `TERM=dumb`, and legacy Windows
consoles.
