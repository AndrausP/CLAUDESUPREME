# Graph Report - knowledge  (2026-11-11)

## Corpus Check
- Corpus is ~1,009 words - fits in a single context window. You may not need a graph.

## Summary
- 23 nodes · 18 edges · 6 communities (2 shown, 4 thin omitted)
- Extraction: 50% EXTRACTED · 50% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Workflow Safety and Evidence
- Optional Interfaces and Boundaries
- QA Release Evidence
- On-Demand Agent Organization
- Honest Benchmark Metrics

## God Nodes (most connected - your core abstractions)
1. `Evidence-Gated Completion` - 4 edges
2. `QA Approved Baseline 2026-11-11` - 3 edges
3. `36 On-Demand Competencies` - 2 edges
4. `Claude Code Native Priority` - 2 edges
5. `Optional Observational Claude Ledger` - 2 edges
6. `Late Dependency Validation` - 2 edges
7. `Safe Cancellation Pattern` - 2 edges
8. `Parser-Verified Command Skills` - 2 edges
9. `Plain and JSON Renderer Baseline` - 2 edges
10. `Hashed Release Artifact` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Namespaced Progressive Skills` --conceptually_related_to--> `36 On-Demand Competencies`  [INFERRED]
  patterns.md → business-rules.md
- `Plain and JSON Renderer Baseline` --conceptually_related_to--> `Claude Code Native Priority`  [INFERRED]
  patterns.md → business-rules.md
- `Late Dependency Validation` --conceptually_related_to--> `Evidence-Gated Completion`  [INFERRED]
  patterns.md → business-rules.md
- `Parser-Verified Command Skills` --conceptually_related_to--> `Evidence-Gated Completion`  [INFERRED]
  patterns.md → business-rules.md
- `Safe Cancellation Pattern` --conceptually_related_to--> `Evidence-Gated Completion`  [INFERRED]
  patterns.md → business-rules.md

## Hyperedges (group relationships)
- **Validated Quality Baseline** — business_rules_qa_acceptance, business_rules_evidence_gated_completion, patterns_hashed_release_artifact [EXTRACTED 1.00]
- **QA Corrective Controls** — patterns_late_dependency_validation, patterns_safe_cancellation, patterns_parser_verified_commands, errors_aprendidos_readme_missing [INFERRED 0.85]
- **Local-First Architecture** — patterns_deterministic_core, patterns_sqlite_jsonl, business_rules_claude_code_native, business_rules_optional_ledger [INFERRED 0.95]

## Communities (6 total, 4 thin omitted)

### Community 0 - "Workflow Safety and Evidence"
Cohesion: 0.29
Nodes (3): Dependency Blocked Regression, Parser and Command Example Synchronization, Pre-Cancellation Checkpoint Fix

### Community 2 - "QA Release Evidence"
Cohesion: 0.50
Nodes (3): QA Approved Baseline 2026-11-11, Optional Validator Warnings, README Missing Packaging Failure

## Knowledge Gaps
- **7 isolated node(s):** `Dependency Blocked Regression`, `Pre-Cancellation Checkpoint Fix`, `Parser and Command Example Synchronization`, `README Missing Packaging Failure`, `TUI Runtime Validation Limitation` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 13 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Evidence-Gated Completion` connect `Workflow Safety and Evidence` to `QA Release Evidence`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Evidence-Gated Completion` (e.g. with `Late Dependency Validation` and `Parser-Verified Command Skills`) actually correct?**
  _`Evidence-Gated Completion` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Dependency Blocked Regression`, `Pre-Cancellation Checkpoint Fix`, `Parser and Command Example Synchronization` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `QA Approved Baseline 2026-11-11` connect `QA Release Evidence` to `Workflow Safety and Evidence`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._