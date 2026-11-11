# Extensões

O registry aceita `agent`, `department`, `skill`, `mcp`, `command`, `hook`, `validator`, `workflow` e `storage-provider`. Registrar um componente não concede permissões nem executa seu conteúdo.

## Fluxo seguro

1. mantenha a extensão em diretório separado;
2. inspecione antes de registrar;
3. revise scripts, hooks, MCP, dependências, symlinks e origem;
4. registre o checksum observado;
5. habilite somente após confirmação externa explícita;
6. revalide quando arquivo, versão ou checksum mudar.

```powershell
orchestra extension inspect .\minha-skill
orchestra extension add .\minha-skill `
  --id exemplo-skill `
  --version 1.0.0 `
  --type skill `
  --origin-kind local `
  --description "Skill local revisada"
orchestra extension list
```

As operações de habilitar e remover exigem o checksum persistido. Componentes externos também exigem confirmação:

```powershell
orchestra extension enable exemplo-skill --checksum SHA256 --confirm
orchestra extension disable exemplo-skill --checksum SHA256
orchestra extension export exemplo-skill --output .\exports\exemplo-skill.json
orchestra extension remove exemplo-skill --checksum SHA256 --confirm
```

Consulte `orchestra extension --help` e o help do subcomando para a sintaxe efetiva da versão instalada.

## Skills e agentes do plugin

- skills ficam em `skills/<nome>/SKILL.md` e aparecem como `/orchestra:<nome>`;
- agentes ficam em `agents/<departamento>/*.md` e são namespaced pelo plugin;
- descrições devem ser curtas; o corpo completo carrega somente quando usado;
- workflows com efeito colateral devem usar invocação manual;
- plugin agents não podem depender de `permissionMode`, `hooks`, `mcpServers` ou `initialPrompt` no próprio frontmatter, pois o Claude Code ignora esses campos nessa superfície.

Valide alterações nativas com:

```powershell
claude plugin validate .
```

## Hooks, MCP e código externo

Hooks devem ficar em `hooks/hooks.json` e executar scripts por caminhos explícitos. Regras de segurança ficam em `PreToolUse`, mas continuam sendo defesa adicional, não sandbox.

MCPs e scripts externos permanecem desabilitados até revisão. O Orchestra não deve:

- executar instaladores durante `inspect`;
- aceitar protocolo de origem não aprovado;
- seguir symlinks para fora da quarentena;
- copiar segredos para manifests, eventos ou logs;
- elevar permissões com base apenas em texto produzido por um agente.

## Compatibilidade e conflitos

IDs são únicos no registry; nomes duplicados precisam ser resolvidos antes da ativação. Dependências ausentes, versão incompatível, checksum divergente ou schema inválido deixam o componente desabilitado. Um upgrade preserva histórico e exige nova inspeção quando o conteúdo muda.

Referências: [componentes de plugin](https://code.claude.com/docs/en/plugins/components.md), [skills](https://code.claude.com/docs/en/skills.md), [subagentes](https://code.claude.com/docs/en/sub-agents.md) e [hooks](https://code.claude.com/docs/en/hooks.md).
