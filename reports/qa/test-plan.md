# Plano de QA — Orchestra Core

## Categorias obrigatórias

| # | Categoria | Evidência automatizada |
|---|---|---|
| 1 | Instalação do plugin | `MandatoryCategoryTests.test_Should_BeDirectoryInstallable_When_PluginIsSubmitted` + `claude plugin validate . --profile directory` |
| 2 | Carregamento dos 36 agentes | `test_Should_LoadExactlyThirtySixAgents_When_CatalogIsRead` |
| 3 | Frontmatters | `test_Should_UseSupportedFrontmatter_When_AgentsAreDiscovered` |
| 4 | Descoberta das skills | `test_Should_DiscoverThirtySixPrimarySkills_When_CatalogIsRead` |
| 5 | Parsing dos comandos | `test_Should_ParseEveryDocumentedCliEquivalent_When_CommandSkillIsLoaded` |
| 6 | Bootstrap | `test_Should_KeepProjectIdentity_When_BootstrapRunsTwice` |
| 7 | Classificação | `test_Should_ClassifyAllModes_When_RiskSignalsChange` |
| 8 | Seleção de departamentos | `test_Should_SelectSmallestDepartmentSet_When_CapabilitiesOverlap` |
| 9 | Orçamentos | `test_Should_RejectBoundaryOverflow_When_BudgetIsExceeded` |
| 10 | Transições | `test_Should_RejectEveryInvalidStateEdge_When_StateMachineRuns` |
| 11 | Handoffs | `test_Should_ValidateHandoffSchema_When_FixtureIsComplete` |
| 12 | Recuperação | `test_Should_RecoverTaskAndCheckpoint_When_ProcessRestarts` |
| 13 | Memória | `test_Should_SaveAndRetrieveAllMemoryTypes_When_Verified` |
| 14 | Duplicatas | `test_Should_DetectDuplicateMemory_When_ContentMatches` |
| 15 | Falha de ferramenta | `test_Should_NotRetryToolFailure_When_ErrorIsDeterministic` |
| 16 | Cancelamento | `test_Should_SaveCheckpointBeforeCancellation_When_TaskIsRunning` |
| 17 | Anti-loop | `test_Should_StopRepeatedDefect_When_ReworkLoops` |
| 18 | Permissões | `test_Should_RequireExternalConfirmation_When_ComponentIsEnabled` |
| 19 | Eventos | `test_Should_ExportSanitizedEventsOnce_When_OutboxIsFlushed` |
| 20 | Sem Ledger | `test_Should_RunWithoutLedger_When_OptionalIntegrationIsAbsent` |
| 21 | Ledger opcional | `test_Should_ValidateLedgerManifest_When_OptionalExportRuns` |
| 22 | Terminal | `test_Should_KeepTerminalWrappersAsciiSafe_When_LegacyConsoleRuns` |
| 23 | Atualização/desinstalação | `test_Should_RemoveRegisteredComponent_When_ChecksumAndConfirmationMatch` |

## Oito cenários

`tests/end_to_end/test_real_scenarios.py` comprova: bug simples, endpoint, componente frontend, migração de banco, erro intermitente, feature completa, revisão com falha conhecida e recuperação após interrupção.

## Gates externos

- `python -m unittest discover -s tests -v`
- `python -m compileall -q src scripts tests benchmarks`
- `claude plugin validate .`
- `claude plugin validate . --profile directory`
- `python -m pip wheel . --no-deps`
- smoke CLI em JSON, plain, `TERM=dumb` e `NO_COLOR`.

Nenhum skip é aceito como aprovação. Dependência opcional ausente deve aparecer como limitação explícita.
