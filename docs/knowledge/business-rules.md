# Regras de negócio

| Data | Regra | Motivo | Agente |
|---|---|---|---|
| 2026-11-11 | O Orchestra Core deve selecionar dinamicamente o menor conjunto de agentes suficiente para entregar resultado verificável. | Reduzir contexto, custo e coordenação sem relaxar critérios mínimos de qualidade ou segurança. | Product Owner |
| 2026-11-11 | As 36 competências ficam disponíveis sob demanda; a organização não mantém 36 agentes executando simultaneamente. | O produto representa capacidades especializadas, não uma simulação de empresa nem atividade artificial. | Product Owner |
| 2026-11-11 | Claude Code Native é o modo prioritário e deve funcionar sem Agent SDK, Ledger, TUI, API própria ou servidor permanente. | O caminho nativo preserva autenticação oficial, reduz dependências e atende o uso local-first. | Product Owner |
| 2026-11-11 | Nenhuma task chega a `COMPLETED` sem critérios e evidências persistidos. | Declaração de sucesso de agente não substitui teste, schema, artefato ou outra comprovação observável. | Product Owner |
| 2026-11-11 | Métricas indisponíveis são `unknown`; aproximações são `estimated`; ganhos percentuais não podem ser inventados. | Tokens, custo de billing e baseline sem Orchestra não estavam disponíveis na validação e não devem ser simulados. | Product Owner |
| 2026-11-11 | Claude Ledger é consumidor administrativo/observacional opcional e nunca segundo orquestrador. | Orchestra precisa manter execução independente e autoridade única sobre transições de workflow. | Product Owner |
| 2026-11-11 | Operações destrutivas, instalação externa e elevação de permissão exigem confirmação externa ao prompt do modelo. | Prompts não são boundary de segurança e extensões/MCP podem trazer código ou instruções não confiáveis. | Product Owner |

## Evidência de aceite

QA aprovou a baseline em 2026-11-11 com 77/77 testes, 23/23 categorias obrigatórias e 8/8 cenários. O benchmark aprovado permanece limitado a roteamento determinístico local; chamadas reais de modelo, billing e comparação equivalente sem Orchestra não foram executadas.
