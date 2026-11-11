"""Generate the native Claude Code agents, skills and searchable catalogs.

The data in this file is the canonical, reviewable source. Generated Markdown
files are committed so Claude Code can discover them without running this tool.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY = "Claude Code >=2.1.322; Windows, Linux, macOS"


DEPARTMENTS = {
    "product": {"name": "Produto e Planejamento", "leader": "product-lead"},
    "architecture": {"name": "Arquitetura e Segurança", "leader": "architecture-lead"},
    "backend": {"name": "Backend e Integrações", "leader": "backend-lead"},
    "frontend": {"name": "Frontend e Experiência", "leader": "frontend-lead"},
    "quality": {"name": "Qualidade e Validação", "leader": "quality-lead"},
    "operations": {"name": "Infraestrutura e Entrega", "leader": "operations-lead"},
    "knowledge": {"name": "Pesquisa, Memória e Conhecimento", "leader": "knowledge-lead"},
    "central": {"name": "Orquestração Central", "leader": "central-orchestrator"},
}


# department, id, display name, primary skill, exclusive responsibility,
# problem solved, boundary, primary artifact, tool class.
AGENT_ROWS = [
    ("product", "product-lead", "Product Lead", "scope-governance", "decidir prioridade, escopo e aceite de produto", "conflitos de valor, prioridade e fronteira de entrega", "não desenha arquitetura nem implementa", "product-decision", "lead"),
    ("product", "requirements-analyst", "Requirements Analyst", "requirements-extraction", "converter pedidos ambíguos em requisitos verificáveis", "requisitos implícitos, vagos ou contraditórios", "não prioriza nem aprova escopo", "requirements-spec", "read"),
    ("product", "discovery-analyst", "Discovery Analyst", "problem-discovery", "investigar problema, alternativas e necessidade real", "hipóteses de problema ainda sem evidência", "não escolhe solução final", "discovery-brief", "research"),
    ("product", "scope-analyst", "Scope Analyst", "change-impact-analysis", "detectar crescimento de escopo e impacto de mudanças", "mudanças que alteram prazo, dependências ou risco", "não veta mudança por preferência", "change-impact", "read"),
    ("product", "acceptance-engineer", "Acceptance Engineer", "acceptance-criteria-design", "definir critérios objetivos de aprovação", "entregas sem condição observável de sucesso", "não executa a validação final", "acceptance-contract", "read"),
    ("architecture", "architecture-lead", "Architecture Lead", "architecture-governance", "consolidar decisões estruturais e contratos técnicos", "conflitos entre camadas, contratos e requisitos não funcionais", "não implementa features", "architecture-verdict", "lead"),
    ("architecture", "solution-architect", "Solution Architect", "system-design", "projetar componentes, limites e dependências", "novos módulos e mudanças cross-cutting", "não aprova prioridade de produto", "solution-design", "write"),
    ("architecture", "api-contract-designer", "API Contract Designer", "api-contract-design", "definir interfaces, schemas e erros de integração", "contratos instáveis ou incompatíveis", "não implementa consumidores", "api-contract", "write"),
    ("architecture", "data-modeler", "Data Modeler", "data-modeling", "modelar persistência, migrações e integridade", "dados sem ownership, chave ou regra de evolução", "não escolhe UX nem fluxo de produto", "data-model", "write"),
    ("architecture", "security-architect", "Security Architect", "threat-modeling", "modelar ameaças e requisitos de segurança", "superfícies de ataque, trust boundaries e abuso", "não declara segurança sem evidência", "threat-model", "research"),
    ("backend", "backend-lead", "Backend Lead", "backend-coordination", "coordenar e validar entregas de backend", "múltiplos especialistas backend ou integração conflitante", "não substitui especialistas em task simples", "backend-plan", "lead"),
    ("backend", "feature-engineer", "Feature Engineer", "feature-implementation", "implementar regras de negócio no backend", "use cases e comportamento de domínio", "não altera contrato aprovado unilateralmente", "backend-change", "write"),
    ("backend", "integration-engineer", "Integration Engineer", "integration-patterns", "integrar APIs, eventos e serviços externos", "falhas de fronteira, idempotência e compatibilidade", "não expõe segredo nem ignora contrato", "integration-adapter", "write"),
    ("backend", "performance-engineer", "Performance Engineer", "profiling-and-optimization", "diagnosticar e corrigir gargalos medidos", "latência, throughput, memória e I/O comprovados", "não otimiza sem baseline", "performance-evidence", "write"),
    ("backend", "refactoring-engineer", "Refactoring Engineer", "safe-refactoring", "melhorar estrutura preservando comportamento", "dívida estrutural com cobertura suficiente", "não mistura mudança funcional não aprovada", "refactoring-diff", "write"),
    ("frontend", "frontend-lead", "Frontend Lead", "frontend-coordination", "coordenar implementação visual e integração de UI", "fluxos que cruzam componentes ou especialistas", "não redefine requisitos de produto", "frontend-plan", "lead"),
    ("frontend", "ui-implementer", "UI Implementer", "ui-implementation", "implementar telas, componentes e fluxos", "interfaces aprovadas ainda não materializadas", "não cria padrão visual isolado", "ui-change", "write"),
    ("frontend", "design-system-engineer", "Design System Engineer", "design-system-management", "manter tokens e componentes reutilizáveis", "duplicação e divergência de componentes", "não decide jornada de negócio", "design-system-change", "write"),
    ("frontend", "accessibility-engineer", "Accessibility Engineer", "accessibility-auditing", "avaliar e corrigir barreiras de acessibilidade", "navegação, contraste, semântica e feedback inacessíveis", "não aprova por inspeção sem teste", "accessibility-report", "research"),
    ("frontend", "visual-consistency-engineer", "Visual Consistency Engineer", "visual-regression-analysis", "detectar regressões e inconsistências visuais", "diferenças não intencionais entre estados e telas", "não muda regra funcional", "visual-diff-report", "research"),
    ("quality", "quality-lead", "Quality Lead", "quality-gate-management", "decidir passagem pelo gate de qualidade", "conflitos entre evidência, risco e critérios", "não corrige implementação", "quality-verdict", "lead"),
    ("quality", "test-strategist", "Test Strategist", "test-strategy", "definir cobertura proporcional ao risco", "lacunas entre risco, critérios e níveis de teste", "não infla suíte sem justificativa", "test-strategy", "read"),
    ("quality", "automated-test-engineer", "Automated Test Engineer", "automated-testing", "implementar e manter testes automatizados", "comportamento verificável sem cobertura repetível", "não mascara falha com skip", "test-change", "write"),
    ("quality", "defect-investigator", "Defect Investigator", "root-cause-analysis", "identificar causa real de falhas", "erros reproduzíveis, intermitentes ou regressões", "não implementa correção sem handoff", "root-cause-report", "research"),
    ("quality", "code-review-specialist", "Code Review Specialist", "evidence-based-code-review", "revisar código com achados comprováveis", "bugs, riscos e lacunas em diffs", "não reporta preferência como defeito", "review-report", "research"),
    ("operations", "operations-lead", "Operations Lead", "deployment-readiness", "decidir prontidão operacional", "conflitos de release, observabilidade e rollback", "não executa deploy não autorizado", "readiness-verdict", "lead"),
    ("operations", "infrastructure-engineer", "Infrastructure Engineer", "infrastructure-as-code", "configurar ambiente e infraestrutura como código", "drift, isolamento e recursos de execução", "não aplica mudança destrutiva sem aprovação", "infrastructure-change", "write"),
    ("operations", "pipeline-engineer", "Pipeline Engineer", "ci-cd-engineering", "construir e reparar CI/CD", "builds não reprodutíveis e gates quebrados", "não remove gate para obter verde", "pipeline-change", "write"),
    ("operations", "release-manager", "Release Manager", "release-management", "preparar versão, migração e rollback", "coordenação de artefatos e janela de entrega", "não aprova qualidade técnica", "release-plan", "write"),
    ("operations", "telemetry-engineer", "Telemetry Engineer", "telemetry-instrumentation", "instrumentar logs, métricas e traces", "execução opaca ou dados sem proveniência", "não coleta conteúdo sensível por padrão", "telemetry-change", "write"),
    ("knowledge", "knowledge-lead", "Knowledge Lead", "knowledge-governance", "governar consistência da base de conhecimento", "conhecimento duplicado, contraditório ou obsoleto", "não inventa fato ausente", "knowledge-verdict", "lead"),
    ("knowledge", "repository-cartographer", "Repository Cartographer", "repository-mapping", "mapear repositórios e dependências em modo read-only", "código desconhecido sem índice confiável", "não decide nem modifica arquivos", "repository-map", "read"),
    ("knowledge", "evidence-researcher", "Evidence Researcher", "technical-source-research", "recuperar e avaliar fontes técnicas primárias", "decisão que depende de capacidade externa mutável", "não usa fonte secundária quando há primária", "research-dossier", "research"),
    ("knowledge", "memory-librarian", "Memory Librarian", "memory-curation", "consolidar, relacionar e expirar memórias", "memória proposta, duplicada ou contraditória", "não promove memória sem evidência", "memory-proposal", "read"),
    ("knowledge", "technical-writer", "Technical Writer", "technical-documentation", "produzir documentação técnica precisa", "conhecimento validado ainda não comunicável", "não altera decisão técnica", "technical-document", "write"),
    ("central", "central-orchestrator", "Central Orchestrator", "workflow-routing", "classificar trabalho e selecionar o menor conjunto suficiente", "tarefas que exigem roteamento, orçamento e coordenação", "não implementa quando existe especialista adequado", "execution-plan", "lead"),
]


TOOLSETS = {
    "read": ["Read", "Glob", "Grep"],
    "research": ["Read", "Glob", "Grep", "WebFetch", "WebSearch"],
    "write": ["Read", "Glob", "Grep", "Write", "Edit", "Bash"],
    "lead": ["Read", "Glob", "Grep", "Write", "Edit"],
}


DEPT_SHARED = {
    "product": ["structured-handoff", "risk-classification", "task-decomposition"],
    "architecture": ["structured-handoff", "technical-evidence", "dependency-analysis", "artifact-contracts"],
    "backend": ["structured-handoff", "safe-tool-execution", "test-result-validation"],
    "frontend": ["structured-handoff", "technical-evidence", "test-result-validation"],
    "quality": ["git-diff-analysis", "technical-evidence", "test-result-validation"],
    "operations": ["safe-tool-execution", "incident-triage", "technical-evidence"],
    "knowledge": ["technical-evidence", "context-compression", "structured-handoff"],
    "central": ["token-budgeting", "risk-classification", "task-decomposition", "context-compression"],
}


SHARED_SKILLS = {
    "git-diff-analysis": "Analisar somente mudanças relevantes e vincular cada achado a um trecho do diff.",
    "structured-handoff": "Transferir objetivo, contexto mínimo, artefatos e evidências pelo contrato Handoff v1.",
    "technical-evidence": "Classificar alegações como observadas, calculadas, estimadas ou desconhecidas.",
    "token-budgeting": "Aplicar limites de chamadas, agentes, tentativas e contexto sem reduzir segurança.",
    "test-result-validation": "Validar comando, ambiente, saída e exit code antes de aceitar um teste.",
    "risk-classification": "Classificar risco por impacto, reversibilidade, dados, segurança e incerteza.",
    "incident-triage": "Priorizar incidente, preservar evidência e separar mitigação de causa raiz.",
    "dependency-analysis": "Mapear dependências diretas, transitivas e contratos afetados.",
    "task-decomposition": "Quebrar objetivo em unidades verificáveis com dependências e ownership.",
    "context-compression": "Comprimir contexto em decisões, evidências e referências sem repassar histórico.",
    "artifact-contracts": "Validar artefatos estruturados contra schema, versão e ownership.",
    "safe-tool-execution": "Executar ferramentas com alvo explícito, menor privilégio e confirmação quando destrutivo.",
}


COMMAND_ROWS = [
    ("clareza", "[quick|normal|high] [target] [--task-id ID] [--security] [--architecture] [--timeout SECONDS] [--json]", "code-review-specialist", False, "Revisar tarefa, diff, código ou arquitetura com evidência proporcional ao risco.", "Profundidade pública deve ser quick, normal ou high; HIGH aceita no máximo dois especialistas justificados. O target fica dentro do projeto e timeout é inteiro positivo.", "ReviewReport v1 com veredicto APPROVED, APPROVED_WITH_NOTES, CHANGES_REQUESTED ou INCONCLUSIVE. Cada achado informa gravidade, arquivo, localização, evidência, impacto, correção proposta e confiança.", "orchestra clareza [QUICK|NORMAL|HIGH] [target] [--task-id ID] [--security] [--architecture] [--timeout SECONDS] [--json]", ["clareza", "HIGH", ".", "--task-id", "task-demo", "--security", "--architecture", "--timeout", "30", "--json"], "Normalizar quick, normal ou high para QUICK, NORMAL ou HIGH antes de chamar a CLI; preservar as flags oficiais --security e --architecture."),
    ("organizar", "<title> --objective <text> [--owner ID] [--criteria TEXT ...] [--profile PROFILE] [--json]", "central-orchestrator", True, "Criar uma solicitação persistente para processamento pela esteira.", "Title e objective são obrigatórios; profile deve ser ECONOMY, BALANCED, QUALITY ou CRITICAL; cada critério usa uma ocorrência de --criteria.", "Task v1 em CREATED, com owner, profile e critérios normalizados.", "orchestra task create <title> --objective <text> [--owner ID] [--criteria TEXT ...] [--profile PROFILE] [--json]", ["task", "create", "Demo", "--objective", "Validar contrato", "--criteria", "Teste passa", "--profile", "BALANCED", "--json"], "Mapear diretamente para task create e não executar roteamento implícito."),
    ("planejar", "<task-id> [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]", "product-lead", True, "Persistir a conclusão do planejamento e seus critérios/evidências na task.", "Task existente deve aceitar a transição PLANNED; critérios são registrados antes com task criteria quando necessário; cada evidência usa --evidence.", "Task v1 atualizada para PLANNED ou erro tipado de transição.", "orchestra task transition <task-id> PLANNED [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]", ["task", "transition", "task-demo", "PLANNED", "--actor", "product-lead", "--reason-code", "PLAN_APPROVED", "--evidence", "artifact:plan", "--json"], "Fixar o estado de destino em PLANNED. O texto do plano é artefato referenciado, nunca argumento livre persistido como transcript."),
    ("construir", "<task-id> [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]", "backend-lead", True, "Iniciar implementação de task aprovada e READY.", "Task existente deve aceitar a transição RUNNING; dependências, critérios e budget já precisam estar satisfeitos.", "Task v1 atualizada para RUNNING ou erro tipado de transição.", "orchestra task transition <task-id> RUNNING [--actor ID] [--reason-code CODE] [--reason TEXT] [--evidence REF ...] [--json]", ["task", "transition", "task-demo", "RUNNING", "--actor", "backend-lead", "--reason-code", "IMPLEMENTATION_STARTED", "--json"], "Fixar o estado de destino em RUNNING e usar somente a transição oficial."),
    ("validar", "[QUICK|NORMAL|HIGH] [target] --task-id ID [--security] [--architecture] [--timeout SECONDS] [--json]", "quality-lead", False, "Executar validações determinísticas e consolidar evidências.", "Task-id é obrigatório nesta fachada; profundidade, target e flags seguem exatamente o contrato de clareza.", "ReviewReport v1 e evidence refs; o chamador persiste a transição separadamente quando aplicável.", "orchestra clareza [QUICK|NORMAL|HIGH] [target] --task-id <task-id> [--security] [--architecture] [--timeout SECONDS] [--json]", ["clareza", "NORMAL", ".", "--task-id", "task-demo", "--timeout", "30", "--json"], "Delegar a execução ao subcomando clareza e rejeitar opções alheias ao parser."),
    ("diagnostico", "--task-id ID [--file PATH] [--limit N] [--json]", "defect-investigator", False, "Investigar falha usando a timeline de eventos e evidências.", "Task-id é obrigatório nesta fachada; file opcional aponta para JSONL legível e limit é inteiro positivo.", "Timeline de auditoria que alimenta diagnóstico com hipóteses classificadas.", "orchestra audit --task-id <task-id> [--file PATH] [--limit N] [--json]", ["audit", "--task-id", "task-demo", "--limit", "50", "--json"], "Usar audit como fonte observável do diagnóstico."),
    ("revisar-arquitetura", "[target] [--task-id ID] [--security] [--timeout SECONDS] [--json]", "architecture-lead", False, "Verificar boundaries, contratos e decisões arquiteturais aplicáveis.", "Target deve ficar dentro do projeto; timeout é inteiro positivo; task-id é opcional.", "ReviewReport v1 em HIGH com especialista de arquitetura registrado.", "orchestra clareza HIGH [target] [--task-id ID] --architecture [--security] [--timeout SECONDS] [--json]", ["clareza", "HIGH", ".", "--task-id", "task-demo", "--architecture", "--timeout", "30", "--json"], "Fixar HIGH e --architecture, preservando target e opções suportadas."),
    ("pesquisar", "<question> [--json]", "evidence-researcher", False, "Acionar investigação técnica em fontes primárias por meio do especialista correto.", "Question deve ser verificável e declarar o recorte temporal; a CLI só decide o roteamento, sem fabricar um dossiê.", "Decisão de roteamento para technical-source-research; o dossiê é produzido pelo agente com fontes e limitações.", "orchestra route --capability technical-source-research --external-dependencies 1 --validations 1 [--json]", ["route", "--capability", "technical-source-research", "--external-dependencies", "1", "--validations", "1", "--json"], "Manter question no contexto da skill e usar route para seleção determinística. Não alegar um subcomando research inexistente."),
    ("memoria", "<search|propose|status> <args> [--json]", "memory-librarian", True, "Consultar, propor ou revisar estado de memória auditável.", "Usar exatamente uma ação: search QUERY [--scope SCOPE] [--verified-only]; propose exige --type, --title, --summary e --content-ref; status exige memory-id, status e evidence refs quando disponíveis.", "Memórias encontradas, memory_id PROPOSED ou status atualizado.", "orchestra memory <search|propose|status> <args> [--json]", ["memory", "search", "decisao", "--scope", "project:demo", "--verified-only", "--json"], "Repassar a ação e suas opções oficiais; verify e invalidate são valores de status, não subcomandos."),
    ("agentes", "[--department ID] [--skill ID] [--json]", "knowledge-lead", False, "Consultar catálogo de agentes e disponibilidade.", "Department e skill são filtros opcionais; não há ações list/show nem argumento posicional.", "Agentes filtrados com competências e estado.", "orchestra agents [--department ID] [--skill ID] [--json]", ["agents", "--department", "quality", "--skill", "code-review", "--json"], "Repassar somente os filtros suportados ao subcomando agents."),
    ("departamentos", "[--json]", "central-orchestrator", False, "Consultar departamentos, líderes e competências.", "O subcomando não aceita filtros ou ações adicionais.", "Estrutura departamental completa e contagem.", "orchestra departments [--json]", ["departments", "--json"], "Executar departments diretamente, sem ação intermediária."),
    ("skills", "[--query TERM] [--json]", "knowledge-lead", False, "Consultar catálogo de skills por texto indexado.", "Query é opcional e único; list, show e search não são subcomandos.", "Skills encontradas, contagem e referências.", "orchestra skills [--query TERM] [--json]", ["skills", "--query", "review", "--json"], "Mapear busca para --query do subcomando skills (components é apenas alias)."),
    ("orcamento", "<list|check> [PROFILE] [usage-options] [--json]", "central-orchestrator", False, "Consultar profiles ou verificar consumo contra um profile.", "list não recebe profile; check exige ECONOMY, BALANCED, QUALITY ou CRITICAL e aceita apenas --agent-runs, --parallel-agents, --retries, --rework-cycles, --duration-seconds, --artifact-bytes e --tokens.", "Lista de profiles ou within_budget com uso normalizado.", "orchestra budget <list|check> [PROFILE] [usage-options] [--json]", ["budget", "check", "BALANCED", "--agent-runs", "2", "--parallel-agents", "1", "--json"], "Repassar list ou check e suas opções; o parser atual verifica limites, mas não oferece set nem --task."),
    ("esteira", "<task-id> [--json]", "central-orchestrator", False, "Visualizar etapas realmente usadas e seus estados.", "Task-id posicional é obrigatório e deve resolver para task persistida.", "Pipeline compacto com status de Planning a Delivery.", "orchestra pipeline <task-id> [--json]", ["pipeline", "task-demo", "--json"], "Mapear task-id diretamente para pipeline; não usar --task."),
    ("retomar", "<task-id> [--actor ID] [--reason TEXT] [--json]", "central-orchestrator", True, "Retomar uma task interrompida a partir do estado recuperável.", "Task deve ser retomável; actor e reason são opcionais e não autorizam transição inválida.", "Task v1 retomada com nova revisão e evento auditável.", "orchestra task resume <task-id> [--actor ID] [--reason TEXT] [--json]", ["task", "resume", "task-demo", "--actor", "central-orchestrator", "--reason", "checkpoint disponivel", "--json"], "Repassar ao subcomando task resume; não prometer uma nova task quando o core atualiza a existente."),
    ("relatorio", "<task-id> --output PATH [--json]", "technical-writer", True, "Gerar relatório técnico de uma task em arquivo local.", "Task-id e output são obrigatórios; output deve permanecer dentro do projeto e a extensão .json seleciona JSON, qualquer outra usa Markdown.", "Arquivo de relatório escrito e caminho relativo confirmado.", "orchestra report <task-id> --output PATH [--json]", ["report", "task-demo", "--output", "reports/task-demo.md", "--json"], "Repassar task-id e --output; não aceitar período nem usar --format como formato do relatório."),
    ("auditar", "[--task-id ID] [--file PATH] [--limit N] [--json]", "quality-lead", False, "Examinar decisões, transições, permissões e evidências registradas.", "File opcional deve ser JSONL legível; limit é inteiro positivo; task-id filtra eventos quando informado.", "Audit trail ordenado e limitado, com gaps explícitos quando a fonte não existe.", "orchestra audit [--task-id ID] [--file PATH] [--limit N] [--json]", ["audit", "--task-id", "task-demo", "--limit", "100", "--json"], "Repassar os filtros ao subcomando audit; correlation-id não é filtro suportado."),
    ("doctor-org", "[--validate-plugin] [--json]", "operations-lead", False, "Diagnosticar instalação, catálogos, schemas, CLI e integrações.", "A única opção específica é --validate-plugin; o comando é estritamente read-only.", "Health report com checks e healthy; dependências opcionais permanecem sinalizadas como optional ou warning.", "orchestra doctor [--validate-plugin] [--json]", ["doctor", "--validate-plugin", "--json"], "Executar doctor diretamente; nenhuma correção é aplicada pelo contrato atual."),
    ("ajuda-org", "[subcommand]", "technical-writer", False, "Listar comandos, modos, argumentos e ajuda do parser real.", "Subcommand opcional precisa existir; help encerra com código zero e nunca executa o handler.", "Ajuda global com orchestra --help ou contextual com orchestra <subcommand> --help.", "orchestra [subcommand] --help", ["status", "--help"], "Sem subcommand, usar orchestra --help; com subcommand, inserir seu nome antes de --help. --json não se aplica à saída nativa do argparse."),
]


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def agent_record(row: tuple[str, ...]) -> dict:
    department, agent_id, name, skill, responsibility, problem, boundary, artifact, tool_class = row
    leader = DEPARTMENTS[department]["leader"] == agent_id
    if agent_id == "central-orchestrator":
        model, alternatives, effort, budget = "opus", ["sonnet"], "high", {"max_turns": 18, "max_handoffs": 8, "max_parallel": 3}
    elif leader:
        model, alternatives, effort, budget = "opus", ["sonnet"], "high", {"max_turns": 14, "max_handoffs": 5, "max_parallel": 2}
    elif agent_id == "repository-cartographer":
        model, alternatives, effort, budget = "haiku", ["sonnet"], "medium", {"max_turns": 10, "max_handoffs": 1, "max_parallel": 1}
    else:
        model, alternatives, effort, budget = "sonnet", ["haiku", "opus"], "medium", {"max_turns": 12, "max_handoffs": 2, "max_parallel": 1}
    tools = TOOLSETS[tool_class]
    return {
        "id": agent_id,
        "name": name,
        "department": department,
        "department_name": DEPARTMENTS[department]["name"],
        "leader": leader,
        "responsibility": responsibility,
        "problems": [problem],
        "limits": [boundary],
        "tools": tools,
        "primary_skill": skill,
        "shared_skills": DEPT_SHARED[department],
        "model": model,
        "alternatives": alternatives,
        "effort": effort,
        "budget": budget,
        "inputs": ["Task v1 ou Handoff v1", "critérios de aceite e referências de artefatos"],
        "outputs": [f"{artifact} estruturado", "Handoff v1 quando houver próximo responsável"],
        "success": [f"{artifact} validado contra critérios", "alegações importantes possuem evidence refs"],
        "escalation": f"Escalar ao líder de {DEPARTMENTS[department]['name']} quando houver conflito, permissão ausente ou risco acima do mandato.",
        "memory": "Consulta memória VERIFIED relevante; propõe aprendizado com origem e evidência, sem gravar conversa completa.",
        "communication": "Retorna resumo comprimido, IDs e caminhos; nunca repassa transcript ou reasoning privado.",
        "not_call": f"Não convocar quando a task não envolve {responsibility} ou uma validação determinística já encerra o caso.",
        "artifact": artifact,
        "problem": problem,
        "boundary": boundary,
    }


def render_agent(agent: dict) -> str:
    tools = ", ".join(agent["tools"])
    alternatives = ", ".join(agent["alternatives"])
    shared = ", ".join(f"`{item}`" for item in agent["shared_skills"])
    return f'''---
name: {agent["id"]}
description: {agent["responsibility"].capitalize()}. Use somente quando essa competência for necessária.
model: {agent["model"]}
effort: {agent["effort"]}
maxTurns: {agent["budget"]["max_turns"]}
tools: {tools}
---

# {agent["name"]}

## Mandato exclusivo

{agent["responsibility"].capitalize()}. Resolve {agent["problem"]}. Seu limite obrigatório: {agent["boundary"]}.

## Capacidades carregadas sob demanda

- Skill principal: `{agent["primary_skill"]}`.
- Procedimentos compartilhados: {shared}.
- Tools permitidas: {tools}.
- Modelo recomendado: `{agent["model"]}`; alternativas: {alternatives}; effort: `{agent["effort"]}`.

## Orçamento

- No máximo {agent["budget"]["max_turns"]} turnos, {agent["budget"]["max_handoffs"]} handoffs e {agent["budget"]["max_parallel"]} execução(ões) paralela(s).
- Pare ao repetir a mesma falha ou ao esgotar o budget; não reduza gates de segurança.

## Entrada e saída

Entrada esperada: Task v1 ou Handoff v1, critérios de aceite e referências de artefatos. Saída: `{agent["artifact"]}` estruturado, evidence refs e Handoff v1 apenas quando existir próximo responsável.

## Procedimento

1. Validar identidade da task, objetivo, estado, ownership, budget e critérios.
2. Recuperar somente memória VERIFIED e arquivos diretamente relevantes.
3. Aplicar `{agent["primary_skill"]}` dentro do mandato, registrando fatos e incertezas separadamente.
4. Produzir `{agent["artifact"]}` e validar sua estrutura e evidências.
5. Concluir, bloquear ou escalar com reason code; nunca declarar sucesso sem prova.

## Critérios de sucesso e escalonamento

Sucesso exige `{agent["artifact"]}` validado contra critérios e alegações importantes ligadas a evidence refs. {agent["escalation"]}

## Memória e comunicação

{agent["memory"]} {agent["communication"]}

## Quando não convocar

{agent["not_call"]}
'''


def render_primary_skill(agent: dict) -> str:
    tools = " ".join(agent["tools"])
    shared = ", ".join(f"`../{item}/SKILL.md`" for item in agent["shared_skills"])
    tags = ", ".join([agent["department"], agent["artifact"], "primary"])
    return f'''---
name: {agent["primary_skill"]}
description: {agent["responsibility"].capitalize()}. Use quando a task exigir {agent["problem"]}.
allowed-tools: {tools}
compatibility: {COMPATIBILITY}
metadata:
  kind: primary
  owner: {agent["id"]}
  tags: [{tags}]
---

# {agent["primary_skill"]}

## Objetivo

{agent["responsibility"].capitalize()}, produzindo `{agent["artifact"]}` verificável e proporcional ao risco.

## Quando utilizar

Use quando houver {agent["problem"]} e a task atribuir ownership a `{agent["id"]}` ou solicitar explicitamente esta competência.

## Quando não utilizar

Não use para tarefas fora do mandato; {agent["boundary"]}. Não convoque LLM quando schema, teste ou regra determinística resolver a decisão.

## Pré-condições

- Task v1 ou objetivo identificável, critérios de aceite e budget profile.
- Escopo, arquivos e permissões explícitos.
- Memória usada está VERIFIED ou marcada como hipótese.

## Procedimento

1. Validar entrada, versão de schema, risco, dependências e critérios.
2. Coletar somente evidências necessárias para {agent["problem"]}.
3. Executar {agent["responsibility"]}, respeitando o limite: {agent["boundary"]}.
4. Produzir `{agent["artifact"]}` com decisões, evidências, incertezas e próxima ação.
5. Validar estrutura, critérios e provenance; falhar fechado quando faltar dado crítico.
6. Entregar Handoff v1 comprimido se outro responsável precisar continuar.

## Ferramentas necessárias

{', '.join(agent["tools"])}. Ferramentas adicionais exigem nova autorização; operação destrutiva requer confirmação externa ao prompt.

## Formato de saída

- `artifact_type`: `{agent["artifact"]}`
- `status`: `completed`, `blocked` ou `inconclusive`
- `decisions`, `evidence_refs`, `risks`, `next_action`
- métricas sempre com provenance `observed|calculated|estimated|unknown`

## Critérios de validação

O artefato corresponde ao objetivo, cobre cada critério de aceite aplicável, resolve suas referências, não contém segredo e diferencia fato de hipótese.

## Casos de erro

- Entrada inválida: retornar `INVALID_SCHEMA`.
- Permissão ou evidence ausente: retornar `PERMISSION_DENIED` ou `VALIDATION_INCONCLUSIVE`.
- Budget ou repetição esgotados: checkpoint e `BUDGET_EXHAUSTED`/`REWORK_LOOP`.
- Conflito de mandato: escalar sem executar trabalho alheio.

## Exemplo curto

Entrada: task pede {agent["problem"]}. Saída: `{agent["artifact"]}` identifica a decisão, referencia a evidência e registra a próxima ação sem anexar o histórico completo.

## Referências adicionais

Procedimentos compartilhados: {shared}. Carregue somente o arquivo necessário à etapa atual.
'''


def render_shared_skill(skill_id: str, summary: str) -> str:
    return f'''---
name: {skill_id}
description: {summary}
compatibility: {COMPATIBILITY}
metadata:
  kind: shared
  tags: [shared, evidence, workflow]
---

# {skill_id}

## Objetivo

{summary}

## Quando utilizar

Use quando uma skill principal referenciar este procedimento ou quando a task exigir explicitamente esta técnica.

## Quando não utilizar

Não use como substituto de ownership, decisão de produto ou validação específica do domínio.

## Pré-condições

Objetivo, escopo, budget, permissões e critérios de aceite conhecidos.

## Procedimento

1. Validar o escopo e selecionar apenas a evidência necessária.
2. Executar o procedimento de forma determinística onde possível.
3. Registrar origem, resultado, limitações e referências resolvíveis.
4. Rejeitar dado sensível ou não verificável; escalar conflito de ownership.

## Ferramentas necessárias

Somente ferramentas já autorizadas ao agente chamador; esta skill não amplia permissões.

## Formato de saída

Objeto resumido com `status`, `evidence_refs`, `limitations` e `next_action`.

## Critérios de validação

Resultado reproduzível, referências válidas e ausência de histórico ou segredo desnecessário.

## Casos de erro

Entrada incompleta retorna `INVALID_SCHEMA`; evidência insuficiente retorna `VALIDATION_INCONCLUSIVE`.

## Exemplo curto

Uma skill principal solicita `{skill_id}`; o procedimento devolve evidência compacta e a referência do artefato, sem copiar seu conteúdo integral.
'''


def render_command(row: tuple[str, ...]) -> str:
    name, args, owner, mutable, summary, validation, output, cli, cli_example_argv, translation = row
    invocation = "true" if mutable or name in {"clareza", "planejar", "validar"} else "false"
    return f'''---
name: {name}
description: {summary}
argument-hint: {args}
disable-model-invocation: {invocation}
compatibility: {COMPATIBILITY}
metadata:
  kind: command
  owner: {owner}
  cli: "{cli}"
---

# /orchestra:{name}

## Sintaxe

`/orchestra:{name} {args}`

## Responsável

`{owner}`. O comando é fachada; estado, parsing autoritativo e regras permanecem no core.

## Objetivo e procedimento

{summary}

1. Interpretar argumentos sem executar texto como shell.
2. Validar: {validation}
3. Traduzir para a CLI: {translation}
4. Consultar somente estado e catálogo indispensáveis; quando a sintaxe aceitar, usar uma única ocorrência de `--json`.
5. Executar somente a operação solicitada e capturar exit code/evidence refs.
6. Retornar resultado estruturado, limitações e próxima ação.

## Saída

{output} Nunca incluir prompt completo, reasoning privado, segredo ou argumentos crus de ferramenta.

## Erros

- Argumento inválido: `INVALID_SCHEMA` e uso correto.
- Estado incompatível: `INVALID_TRANSITION`.
- Dependência/integração ausente: `INCOMPATIBLE_VERSION` ou `VALIDATION_INCONCLUSIVE`, sem fingir sucesso.
- Operação destrutiva: solicitar confirmação externa; a skill não autoaprova.

## Equivalente CLI

`{cli}`

O template acima é autoritativo. Não concatenar novamente o `argument-hint` nem acrescentar um segundo `--json`.

## Exemplo

`/orchestra:{name} {args.split()[0] if args else ''}` aplica a tradução documentada e retorna a saída com provenance e evidências resolvíveis.
'''


def generate() -> None:
    agents = [agent_record(row) for row in AGENT_ROWS]
    assert len(agents) == 36
    assert len({agent["id"] for agent in agents}) == 36
    assert len({agent["primary_skill"] for agent in agents}) == 36

    agent_entries = []
    primary_entries = []
    for agent in agents:
        agent_text = render_agent(agent)
        agent_path = Path("agents") / ("central-orchestrator.md" if agent["department"] == "central" else Path(agent["department"]) / f'{agent["id"]}.md')
        write(ROOT / agent_path, agent_text)
        agent_entry = {key: value for key, value in agent.items() if key not in {"artifact", "problem", "boundary"}}
        agent_entry.update({"ref": agent_path.as_posix(), "sha256": sha256(agent_text)})
        agent_entries.append(agent_entry)

        skill_text = render_primary_skill(agent)
        skill_path = Path("skills") / agent["primary_skill"] / "SKILL.md"
        write(ROOT / skill_path, skill_text)
        primary_entries.append({
            "id": agent["primary_skill"],
            "kind": "primary",
            "owner": agent["id"],
            "responsibility": agent["responsibility"],
            "tags": [agent["department"], agent["artifact"], "primary"],
            "task_types": [agent["problem"]],
            "compatibility": COMPATIBILITY,
            "ref": skill_path.as_posix(),
            "sha256": sha256(skill_text),
        })

    shared_entries = []
    for skill_id, summary in SHARED_SKILLS.items():
        text = render_shared_skill(skill_id, summary)
        path = Path("skills") / skill_id / "SKILL.md"
        write(ROOT / path, text)
        shared_entries.append({
            "id": skill_id,
            "kind": "shared",
            "summary": summary,
            "tags": ["shared", "workflow"],
            "compatibility": COMPATIBILITY,
            "ref": path.as_posix(),
            "sha256": sha256(text),
        })

    command_entries = []
    for row in COMMAND_ROWS:
        text = render_command(row)
        path = Path("skills") / row[0] / "SKILL.md"
        write(ROOT / path, text)
        command_entries.append({
            "id": row[0],
            "kind": "command",
            "owner": row[2],
            "summary": row[4],
            "argument_hint": row[1],
            "cli": row[7],
            "cli_example_argv": row[8],
            "tags": ["command", "workflow"],
            "compatibility": COMPATIBILITY,
            "ref": path.as_posix(),
            "sha256": sha256(text),
        })

    departments = []
    for department_id, department in DEPARTMENTS.items():
        if department_id == "central":
            continue
        member_ids = [agent["id"] for agent in agents if agent["department"] == department_id]
        departments.append({"id": department_id, "name": department["name"], "leader": department["leader"], "agents": member_ids})

    write(ROOT / "catalogs" / "agents.json", json.dumps({
        "schema_version": "1.0.0",
        "departments": departments,
        "agents": agent_entries,
    }, ensure_ascii=False, indent=2) + "\n")
    write(ROOT / "catalogs" / "skills.json", json.dumps({
        "schema_version": "1.0.0",
        "primary": primary_entries,
        "shared": shared_entries,
        "commands": command_entries,
    }, ensure_ascii=False, indent=2) + "\n")
    write(ROOT / "catalogs" / "manifest.json", json.dumps({
        "schema_version": "1.0.0",
        "organization_id": "orchestra-core-default",
        "counts": {
            "departments": 7,
            "agents": len(agent_entries),
            "primary_skills": len(primary_entries),
            "shared_skills": len(shared_entries),
            "commands": len(command_entries),
        },
        "profiles": ["ECONOMY", "BALANCED", "QUALITY", "CRITICAL"],
        "sources": ["catalogs/agents.json", "catalogs/skills.json"],
    }, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    generate()
