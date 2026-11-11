# Integração opcional com Claude Ledger

## Limite de responsabilidade

O Orchestra Core executa e valida o workflow. O Claude Ledger pode ler configuração e eventos para administração e observabilidade, mas não é um segundo orquestrador, não chama agentes e não transiciona tasks diretamente. A ausência ou falha do Ledger não bloqueia nenhuma operação do Orchestra.

## Protocolo local

A CLI exporta dois artefatos versionados:

```powershell
orchestra ledger export --output .\integrations\claude-ledger\out
```

- `organization.manifest.json`: identidade, versão de protocolo/pacote, departamentos, agentes, skills, perfis, políticas, integrações e checksums;
- `events.jsonl`: eventos sanitizados com `event_id`, correlação, timestamp, origem, schema e proveniência das métricas.

Os arquivos devem validar contra:

- `schemas/organization-manifest.schema.json`;
- `schemas/event.schema.json`.

O protocolo `1.x` aceita adições opcionais. Um consumidor deve rejeitar major version desconhecida, tratar `event_id` como chave idempotente e ignorar repetições já processadas.

## Privacidade e proveniência

O protocolo público exclui prompts, respostas, raciocínio privado, segredos, conteúdo bruto de arquivos e argumentos crus de ferramentas. Valores quantitativos informam proveniência:

- `observed`: emitido diretamente por uma fonte suportada;
- `calculated`: derivado por fórmula documentada;
- `estimated`: aproximação, incluindo custo local do SDK;
- `unknown`: dado indisponível.

Custos estimados não são cobrança autoritativa e não devem dirigir faturamento ou decisão financeira.

Na revalidação de 2026-11-11, schemas, export opcional e execução sem Ledger passaram. Um aplicativo Claude Ledger real e telemetria de billing não foram exercitados; tokens e custo do benchmark ficaram `null` com proveniência `unknown`.

## Transporte e armazenamento

A baseline usa arquivos locais e SQLite/JSONL. Não existe requisito de servidor HTTP permanente. Um receptor OpenTelemetry pode ser acrescentado de forma opt-in, mas continua independente do contrato de execução do workflow.

O adapter `orchestra_core.adapters.ledger` escreve apenas no destino informado. Ele não abre nem migra o banco privado do Ledger e não depende do aplicativo estar instalado.

## Ativação futura no Ledger

Uma seção Organização pode consumir o manifesto e os eventos para exibir saúde, catálogo, tasks, memória e auditoria. Qualquer mutação administrativa deve retornar pela CLI/application service do Orchestra, com schema, permissões, checksum e confirmação aplicáveis.

## Falhas esperadas

- destino ausente: a CLI cria diretórios quando permitido;
- major version incompatível: o consumidor rejeita sem afetar o Orchestra;
- linha JSONL truncada: o consumidor preserva o último offset válido e relata diagnóstico;
- evento duplicado: ignorar por `event_id`;
- Ledger indisponível: registrar integração como opcional/indisponível, sem mudar o estado da task.

Consulte também `integrations/claude-ledger/README.md` e `integrations/claude-ledger/organization.manifest.example.json`.
