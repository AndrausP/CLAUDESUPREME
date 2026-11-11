# UX da CLI/TUI do Orchestra Core

## Objetivo e contrato de experiência

A interface torna o estado observável da organização compreensível sem simular atividade. Ela mostra o que o core registrou: decisões, responsáveis, eventos, evidências, limites e falhas. Nunca mostra pensamentos privados, não inventa progresso e não promete controlar uma sessão nativa do Claude Code.

Há três renderers sobre os mesmos application services:

1. **Texto puro (baseline):** sempre disponível; saída estática, ASCII e sem dependências.
2. **Rich (opcional):** melhora tabelas e cor, mas não altera conteúdo, ordem, comandos ou exit codes.
3. **Textual (opcional):** navegação full-screen e atualização reativa; todas as ações têm equivalente CLI.

Se `NO_COLOR` estiver definido, `TERM=dumb`, stdout não for TTY, a largura for menor que 80 colunas ou Rich/Textual não puderem ser importados, o sistema escolhe texto puro. A degradação é silenciosa em uso normal e aparece em `orchestra doctor`.

## Princípios de interação

- **Estado antes de decoração:** status textual e evidência têm precedência sobre cor.
- **Densidade compacta:** uma linha por entidade; detalhe abre sob demanda.
- **Progressive disclosure:** a visão inicial mostra situação e exceções, não os 36 agentes.
- **Uma ação, um nome:** `Validar`, `Retomar`, `Cancelar`, `Desabilitar` e `Abrir no Claude Code` não mudam entre telas.
- **Sem sucesso prematuro:** `solicitado`, `gravado`, `validado` e `concluído` são estados diferentes.
- **Honestidade:** valores ausentes aparecem como `unknown`; estimativas exibem `estimated`.
- **Segurança visível:** ações destrutivas informam alvo, impacto e reversibilidade antes da confirmação externa.

## Arquitetura de informação

Ordem estável da navegação:

1. **Início** — saúde, projeto, tarefa ativa e alertas.
2. **Esteira** — tasks e etapas realmente utilizadas.
3. **Departamentos** — capacidade disponível e trabalho atual.
4. **Agentes** — catálogo, configuração e histórico observável.
5. **Memória** — índices, escopos, estado e proveniência.
6. **Skills e MCP** — extensões, compatibilidade e saúde.
7. **Execução** — timeline, evidências e diagnósticos de uma task.

Na TUI, `1` a `7` abre a seção correspondente. No renderer estático, os equivalentes são `orchestra status`, `pipeline`, `departments`, `agents`, `memory`, `components` e `task show <id>`.

## Shell da TUI

### Cabeçalho

Uma única linha persistente:

`ORCHESTRA CORE | projeto | perfil | estado | task ativa`

Não usar banner ASCII. O nome não ultrapassa 16 caracteres; valores longos são truncados visualmente com `...`, preservando o texto completo na tela de detalhe e em `--json`.

### Área principal

- Largura >= 120: navegação lateral de 22 colunas + conteúdo + painel contextual de 32 colunas.
- Largura 80–119: navegação superior compacta; detalhe substitui a lista.
- Largura < 80 ou altura < 24: sair do full-screen e renderizar snapshot estático.
- Tabelas nunca exigem rolagem horizontal para ações primárias. Colunas menos importantes somem na ordem: modelo, duração, departamento, timestamp completo.

### Rodapé

Exibe apenas atalhos válidos no contexto, por exemplo:

`[Enter] Detalhes  [v] Validar  [r] Retomar  [/] Filtrar  [?] Ajuda  [q] Sair`

Atalhos não disponíveis não aparecem. `Esc` volta um nível; nunca cancela uma task.

## Fluxos

### 1. Inicialização e recuperação

**Objetivo:** entender se a organização está pronta e retomar trabalho interrompido sem ambiguidade.

1. Abrir com `orchestra` ou `orchestra status`.
2. Mostrar `Verificando ambiente...` com etapas textuais; sem spinner quando o terminal é degradado.
3. Se o bootstrap concluir, abrir Início e posicionar foco no primeiro alerta acionável; sem alertas, focar `Tarefas ativas`.
4. Se houver checkpoints recuperáveis, mostrar resumo e ação `Revisar retomada`; não retomar automaticamente uma mutação.
5. Se uma dependência opcional falhar, manter estado `Pronto com alertas` e informar a função degradada.
6. Se SQLite/schema falhar, mostrar `Falha de inicialização`, caminho sanitizado do diagnóstico e comando `orchestra doctor`; não abrir uma TUI vazia.

Estados: loading, pronto vazio, pronto com tasks, pronto com alertas, recuperação disponível e erro fatal.

### 2. Inspecionar departamentos

**Objetivo:** conferir capacidade e responsáveis sem acordar agentes.

1. Listar exatamente sete departamentos, líder, disponibilidade e contagem de tasks.
2. Abrir um departamento para mostrar cinco agentes e suas competências resumidas.
3. Abrir um agente para ver configuração; consultar não significa convocar.
4. Quando não houver atividade, mostrar `Nenhuma tarefa ativa neste departamento` e preservar o catálogo disponível.

### 3. Acompanhar a esteira

**Objetivo:** identificar etapa atual, bloqueio e próxima ação.

1. Selecionar uma task ou abrir a task ativa.
2. Mostrar somente etapas usadas: Planejamento, Arquitetura, Implementação, Testes, Revisão e Entrega.
3. Cada etapa exibe token textual de status, owner e última evidência.
4. Em bloqueio, o painel contextual começa por `Motivo` e `Ação necessária`.
5. `Retomar` só aparece quando o core oferece uma transição válida/checkpoint; não é ação visual otimista.

### 4. Consultar agentes

**Objetivo:** entender especialização e custo operacional antes de convocação.

1. Filtrar por departamento, disponibilidade, skill ou tag.
2. A lista mostra nome, competência única e estado.
3. O detalhe mostra departamento, tools, skills, modelo configurado, limites, histórico e métricas com proveniência.
4. Permissões ignoradas pelo plugin aparecem como `Não aplicável no agente de plugin`, nunca como ativas.
5. Eficiência sem amostra suficiente aparece como `unknown — sem amostra verificada`.

### 5. Curar memória

**Objetivo:** localizar conhecimento e revisar confiabilidade sem expor conteúdo sensível.

1. Filtrar por tipo, escopo, estado, tag ou texto.
2. A lista mostra título, tipo, estado, última validação e confiabilidade.
3. O detalhe mostra resumo, origem, evidências e relações; conteúdo grande abre sob demanda.
4. `Propor`, `Verificar`, `Invalidar` e `Substituir` usam verbos distintos.
5. Contradição apresenta as duas memórias lado a lado e exige decisão explícita; nunca sobrescreve silenciosamente.

### 6. Administrar Skills e MCP

**Objetivo:** verificar saúde e alterar componentes com menor privilégio.

1. Separar `Skills`, `MCP` e `Outros componentes` por abas/filtros.
2. Mostrar estado textual: habilitado, desabilitado, incompatível, autenticação necessária ou falha.
3. Abrir detalhe para origem, versão, checksum, permissões, dependências e diagnóstico.
4. `Habilitar`/`Desabilitar` mostra impacto antes de aplicar.
5. Instalação externa mostra quarentena e análise; a confirmação informa que código de terceiros será instalado.
6. Falha de MCP nunca bloqueia telas que não dependem dele.

### 7. Auditar uma execução

**Objetivo:** reconstruir o que aconteceu por eventos observáveis.

1. Abrir task e selecionar `Timeline`.
2. Mostrar eventos em ordem: início, classificação, seleção/rejeição de agentes, tools, testes, diagnóstico e conclusão.
3. Cada evento mostra timestamp curto, tipo, actor e resumo sanitizado.
4. Abrir evento para correlation ID, schema version, evidence refs e proveniência.
5. Pensamentos privados, prompts, respostas e argumentos crus não têm campo na UI.
6. `Exportar relatório` informa caminho e formato; só então confirma `Relatório gravado`.

## Especificação das telas

### Início

Prioridade visual:

1. estado global e alertas acionáveis;
2. task ativa e etapa;
3. tarefas ativas/bloqueadas;
4. departamento e agente atuais;
5. budget e última operação.

Estado vazio: `Organização pronta. Nenhuma tarefa ativa.` Ações: `Nova tarefa` (informa o comando) e `Abrir ajuda`.

### Departamentos

Tabela: `Departamento | Líder | Disponíveis | Tasks | Estado`. Detalhe: objetivo, cinco agentes, tasks e alertas. `Disponíveis` significa configurados/habilitados, não processos em execução.

### Esteira

Linha de etapas com token + nome. Em largura reduzida, uma etapa por linha. A etapa ativa recebe foco/borda; conclusão anterior não compete visualmente com o bloqueio atual.

### Agentes

Lista mestre/detalhe. Campos: competência, limites, tools, skills, modelo, esforço, orçamento, disponibilidade, últimas execuções e métricas com proveniência.

### Memória

Resumo por tipo e estado, depois lista. Estados `OUTDATED`, `SUPERSEDED` e `REJECTED` permanecem consultáveis em filtro `Histórico`, mas não poluem o padrão `Ativas`.

### Skills e MCP

Saúde agregada no topo, componentes abaixo. Componentes com falha sobem para o início. Ações destrutivas (`Remover`, `Revogar permissão`) usam confirmação externa e nunca ficam ligadas a uma tecla de um único toque.

### Execução

Cabeçalho com task/status/owner/revision, timeline compacta, critérios, evidências, problemas e próxima ação. Uma task `COMPLETED` sem evidência é exibida como inconsistência crítica, não como sucesso.

## Estados e feedback

| Estado | Token ASCII | Cor opcional | Significado |
|---|---:|---|---|
| Pendente | `[ ]` | muted | ainda não iniciado |
| Em execução | `[>]` | accent | atividade observada em curso |
| Concluído | `[OK]` | success | critério e evidência registrados |
| Bloqueado | `[!]` | warning | requer ação/estado externo |
| Falha | `[X]` | error | tentativa terminou com erro |
| Cancelado | `[-]` | muted | encerrado intencionalmente |
| Desconhecido | `[?]` | muted | dado indisponível |

Cor nunca é o único diferenciador. O texto do estado sempre acompanha o token. O vermelho `#C9372C` serve para borda, token e destaque; texto pequeno sobre fundo escuro usa `text-primary`, pois o vermelho não atinge contraste de texto normal.

### Assíncrono

Toda ação assíncrona segue quatro fases observáveis:

1. `Pronto` — ação habilitada.
2. `Processando` — ação desabilitada, alvo preservado e status visível.
3. `Concluído` — resultado confirmado pelo core, com ID/evidência quando aplicável.
4. `Falha` — mensagem clara, diagnóstico/ação de recuperação e valores anteriores preservados.

Não usar apenas spinner. Operações maiores que dois segundos atualizam uma mensagem de fase, não porcentagem inventada.

### Confirmação destrutiva

Exibir: ação, alvo exato, efeitos, reversibilidade e confirmação exigida. O texto `Digite REMOVER` é reservado a remoção sem rollback. Cancelar é a opção focada por padrão.

## Busca, filtros e seleção

- `/` foca a busca na TUI; `Esc` limpa primeiro e volta no segundo acionamento.
- Filtros ativos aparecem como texto (`estado:falha`, `departamento:qualidade`).
- Resultado vazio informa filtros e ação `Limpar filtros`.
- Seleção por teclado permanece visível; atualização de dados não move foco para outra entidade sem aviso.

## Microcopy

- Preferir `Sem tarefas ativas` a `No data`.
- Preferir `MCP requer autenticação` a `Unauthorized`.
- Preferir `Não foi possível validar o plugin` e a causa a `Erro 1`.
- Usar `Solicitação de cancelamento registrada` antes do boundary seguro; somente depois `Task cancelada`.
- Usar `unknown` para valor de contrato e explicar em texto: `Dado não fornecido pela integração`.

## Renderer estático e automação

- Saída humana: título curto, resumo de estado, lista/tabela e próxima ação.
- `--json`: JSON válido sem códigos ANSI, mensagens decorativas ou progresso em stdout.
- Diagnósticos e progresso de automação vão para stderr.
- Ordem e nomes de campos não mudam entre renderers.
- Caracteres baseline limitados a ASCII. Unicode pode ser habilitado somente após detecção positiva; não é requisito visual.
- Persistência é UTF-8; a console CP850 recebe texto transliterado/seguro sem alterar os arquivos.

## Critérios de validação para Frontend/QA

- Todas as sete seções têm estado normal, vazio, loading, erro e bloqueado/não aplicável quando pertinente.
- A mesma informação e ação existe no renderer texto, Rich e Textual; ausência de extra não bloqueia o comando.
- `TERM=dumb`, stdout redirecionado e `NO_COLOR=1` não emitem ANSI nem Unicode obrigatório.
- Larguras 120, 100, 80 e 60 colunas não escondem status, motivo de bloqueio ou próxima ação.
- Navegação completa funciona sem mouse; foco é visível e previsível.
- Nenhum estado depende só de vermelho/verde; tokens e rótulos permanecem.
- Nenhuma tela mostra raciocínio privado ou dados sensíveis.
- Toda métrica mostra proveniência ou `unknown`.
- Confirmações destrutivas focam Cancelar e identificam o alvo.
- TUI observa application services; não acessa SQLite diretamente.
- Screen reader recebe títulos, estado e mudança assíncrona em texto estável, sem animação indispensável.

