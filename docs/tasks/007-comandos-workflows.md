# [BACKEND] Comandos e workflows operacionais

- Status: COMPLETED
- Fase: C
- Estimativa: 3 dias
- Depende de: 004, 006
- Responsável: Dev Backend

## O que fazer

Implementar `/organizar`, `/planejar`, `/construir`, `/validar`, `/diagnostico`, `/revisar-arquitetura`, `/pesquisar`, `/memoria`, `/agentes`, `/departamentos`, `/skills`, `/orcamento`, `/esteira`, `/retomar`, `/relatorio`, `/auditar`, `/doctor-org` e `/ajuda-org`, todos sob namespace `orchestra` e com equivalentes CLI.

## Critério de conclusão

- Cada comando possui argumentos, ajuda, validação, erro, responsável, procedimento e saída.
- Parser rejeita combinações inválidas.
- Workflows usam contratos e não históricos livres.
- Testes cobrem descoberta e parsing.

## Limites de arquivos

`skills/{organizar,planejar,construir,validar,diagnostico,revisar-arquitetura,pesquisar,memoria,agentes,departamentos,skills,orcamento,esteira,retomar,relatorio,auditar,doctor-org,ajuda-org}/**`, `workflows/**`, `src/orchestra/commands/**`, `tests/unit/commands/**`.

## Risco

Conflitos globais; nenhum atalho sem namespace deve ser instalado automaticamente.

## Contrato técnico consolidado

- Ownership: skills dos 18 comandos, `src/orchestra/commands/**`, `workflows/**` e testes de parser.
- Skills são fachada nativa; parser/validação/estado ficam no Application/CLI.
- Todo comando oferece `--json`, exit code estável, help e erro tipado; comandos mutáveis são invocação manual.
- Handoffs usam `Handoff v1` e referências a artefatos; não incorporam transcript.
- Dynamic workflows podem ser adapter futuro, mas a correção depende apenas do core persistente.

## Evidência de conclusão

- [x] 19 command skills sincronizadas com a CLI.
- [x] Todos os exemplos aceitos pelo parser real.
- [x] Nenhum exemplo repete `--json` ou depende de histórico livre.

