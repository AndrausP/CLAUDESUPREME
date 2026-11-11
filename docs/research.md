# Pesquisa técnica e matriz de compatibilidade

Data da verificação: 2026-11-11  
Ambiente observado: Claude Code 2.1.322, Windows 11 Enterprise, PowerShell 7.6.9, Python 3.12.10, Node.js 24.13.0.

## Resumo executivo

O Claude Code já fornece o plano de extensão necessário para o modo primário do Orchestra: plugins, skills, subagentes, hooks, MCP e execução não interativa. O Orchestra deve empacotar esses recursos, não reproduzi-los. O componente personalizado é o plano de controle determinístico: classificação, estado, orçamento, contratos, persistência, auditoria e recuperação.

Skills são a unidade nativa para comandos novos. O corpo da skill é carregado apenas quando utilizado; para ações com efeito colateral, `disable-model-invocation: true` remove também a descrição do contexto até a invocação manual. Subagentes têm contexto separado, mas geram consumo próprio e suas descrições permanecem no contexto do coordenador. Portanto, 36 definições disponíveis não justificam 36 invocações.

Agent teams permitem comunicação entre sessões, mas continuam condicionais/experimentais. O fluxo básico não pode depender deles. O modo programático usa Agent SDK ou `claude -p`, com autenticação oficialmente suportada e permissões explícitas. Custos expostos pelo SDK são estimativas locais, não faturamento autoritativo.

## Matriz de compatibilidade

| Recurso | Native | Programmatic | Classe | Decisão para o Orchestra |
|---|---|---|---|---|
| Plugin com `.claude-plugin/plugin.json` | Sim | Carregável pelo SDK | NATIVO | Unidade de distribuição do modo principal. |
| Skills em `skills/<nome>/SKILL.md` | Sim | Sim, se habilitadas | NATIVO | Base de todos os comandos novos e procedimentos sob demanda. |
| Comandos em `commands/*.md` | Sim, legado | Depende do carregamento | NATIVO/LEGADO | Não criar novos; skills substituem comandos. |
| Namespace `/orchestra:<skill>` | Sim para plugin | Sim ao carregar plugin | NATIVO | Obrigatório para evitar colisões globais. |
| Subagentes em `agents/**/*.md` | Sim | Sim | NATIVO | Catálogo de 36 competências; invocação seletiva. |
| `permissionMode`, hooks e MCP no frontmatter de plugin agent | Ignorados | Configuráveis no host SDK | NÃO SUPORTADO no plugin | Permissões ficam na sessão/host; hooks e MCP no nível do plugin. |
| Hooks em `hooks/hooks.json` | Sim | Sim | NATIVO | Guardrails, bootstrap e captura de eventos determinísticos. |
| MCP em `.mcp.json` | Sim | Sim | NATIVO | Opcional; nenhuma dependência MCP no funcionamento básico. |
| Agent teams | Desativados por padrão/experimentais | Não é contrato básico do SDK | CONDICIONAL | Nunca requisito do fluxo; otimização futura. |
| Dynamic workflows de plugin | Dependem da versão/feature | Não presumidos | CONDICIONAL | Não são o motor autoritativo; podem adaptar o core no futuro. |
| `claude -p` com JSON | Sim | É a interface CLI programática | NATIVO | Adapter opcional para automação, não para o core local. |
| Claude Agent SDK Python/TypeScript | Não necessário à sessão nativa | Sim | CONDICIONAL | Extra opcional, com autenticação e permissões próprias. |
| Settings user/project/local/managed | Sim | Fontes selecionáveis | NATIVO | Instalador não altera configuração global silenciosamente. |
| OpenTelemetry do Claude Code | Opt-in | O SDK também expõe OTel | NATIVO/CONDICIONAL | Integração opcional; eventos locais continuam funcionando sem coletor. |
| SQLite local | Não é recurso Claude | Sim, stdlib Python | PERSONALIZADO | Fonte autoritativa de estado operacional. |
| JSONL de eventos | Não | Sim | PERSONALIZADO | Exportação append-only e integração desacoplada. |
| Memória Markdown/JSON indexada | Auto memory não cobre o contrato pedido | Sim | PERSONALIZADO | Memória Orchestra com proveniência e lifecycle próprios. |
| TUI substituindo a interface do Claude Code | Não | Não há API geral para isso | NÃO SUPORTADO | TUI complementar, capaz apenas de lançar o Claude Code. |
| Integração Claude Ledger | Não existe no Ledger observado | Adapter local | PERSONALIZADO | Protocolo unilateral, versionado e opcional. |
| Modificar o binário do Claude Code | Proibido pelos termos | Proibido | NÃO SUPORTADO | Fora de escopo. |

## Compatibilidade de plugin e frontmatter

- Apenas `plugin.json` pertence em `.claude-plugin/`; componentes ficam no root do plugin.
- O layout padrão reconhece `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `workflows/` e `bin/`.
- `claude plugin validate <diretório>` é o gate local autoritativo do manifesto e dos componentes.
- Plugin skills recebem namespace automaticamente. O nome público será `/orchestra:<nome>`.
- Skills novas devem ter descrição curta e corpo abaixo de 500 linhas; detalhes extensos ficam em `references/`.
- Plugin agents suportam `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd` e `isolation`. Não se deve declarar segurança ilusória por `permissionMode` no agent do plugin.
- Agent teams não serão usados como requisito de comunicação; handoffs persistidos permanecem válidos com ou sem suporte experimental.

## Context engineering e economia de tokens

O critério é maximizar sinal por token, não reduzir contexto indiscriminadamente. O desenho aplica:

1. descrições curtas de agentes e skills;
2. conteúdo completo somente sob demanda;
3. handoffs com referências a artefatos, nunca históricos completos;
4. busca textual e filtros antes de leitura semântica;
5. validação determinística antes de revisão por modelo;
6. apenas o menor conjunto de agentes que cobre risco e critérios;
7. checkpoint e retomada sem reenviar toda a conversa;
8. budgets com `unknown` quando a telemetria não estiver disponível.

Memória em tiers segue o princípio de separar contexto ativo de armazenamento durável. O Orchestra não salvará conversas inteiras; persistirá fatos reutilizáveis, decisões, evidências, resumos e referências com estado e validade.

## Textual/Rich versus Ink

| Critério | Textual + Rich | Ink |
|---|---|---|
| Runtime | Python 3.9+ | Node.js e React |
| Alinhamento com o core escolhido | Mesmo runtime e tipos | Segundo runtime e toolchain |
| Windows | Suporte oficial; Windows Terminal recomendado | Suporte prático do renderer; exige tratamento de ANSI/CI |
| CMD/terminal degradado | Rich suporta CMD e `NO_COLOR`; TUI pode não ser adequada | Exige fallback próprio e raw mode confiável |
| Layout interativo | Widgets, CSS, resize, teclado | Componentes React e Flexbox |
| Empacotamento | Wheel/zipapp; executável opcional por PyInstaller | Pacote npm ou bundle Node |
| Custo operacional | Extras Python opcionais | Node + React adicionais ao core |
| Decisão | Escolhido como extra `tui` | Descartado no v1 para evitar dois runtimes |

O CLI base usa somente stdlib e saída estática. Rich é extra de apresentação; Textual é extra da TUI. Se não estiverem instalados, se `NO_COLOR` estiver definido, se não houver TTY ou se `TERM=dumb`, o sistema usa texto simples. A persistência permanece UTF-8 independentemente da code page do console.

## Fontes primárias

- [Índice oficial do Claude Code](https://code.claude.com/docs/llms.txt)
- [Criação de plugins](https://code.claude.com/docs/en/plugins/create.md)
- [Componentes de plugin](https://code.claude.com/docs/en/plugins/components.md)
- [Referência do manifesto](https://code.claude.com/docs/en/plugins/manifest-reference.md)
- [Skills](https://code.claude.com/docs/en/skills.md)
- [Subagentes](https://code.claude.com/docs/en/sub-agents.md)
- [Hooks](https://code.claude.com/docs/en/hooks.md)
- [Agent teams](https://code.claude.com/docs/en/agent-teams.md)
- [MCP](https://code.claude.com/docs/en/mcp.md)
- [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview.md)
- [Execução programática](https://code.claude.com/docs/en/headless.md)
- [Permissões no Agent SDK](https://code.claude.com/docs/en/agent-sdk/permissions.md)
- [Custos e uso no Agent SDK](https://code.claude.com/docs/en/agent-sdk/cost-tracking.md)
- [Settings e precedência](https://code.claude.com/docs/en/settings.md)
- [Monitoramento OpenTelemetry](https://code.claude.com/docs/en/monitoring-usage.md)
- [Legal e compliance](https://code.claude.com/docs/en/legal-and-compliance.md)
- [Context engineering pela Anthropic](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
- [Textual: getting started](https://textual.textualize.io/getting_started/)
- [Rich: introdução e Windows](https://rich.readthedocs.io/en/latest/introduction.html)
- [Rich: `NO_COLOR` e detecção de terminal](https://rich.readthedocs.io/en/latest/console.html)
- [Ink: repositório oficial](https://github.com/vadimdemedes/ink)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [MemGPT: memória em tiers](https://arxiv.org/abs/2310.08560)

## Limitações verificadas

- A documentação é versionada continuamente; toda compatibilidade precisa ser revalidada no gate de release.
- A execução nativa não oferece contagem confiável de custo para toda operação. Ausência de dado é `unknown`.
- `total_cost_usd`/`costUSD` do SDK é `estimated`, nunca cobrança observada.
- Uma TUI própria não recebe controle implícito sobre sessões interativas do Claude Code.
- O ambiente atual tem `TERM=dumb`, CP850 e não possui Rich/Textual; isso valida a necessidade do fallback, não a portabilidade completa.

