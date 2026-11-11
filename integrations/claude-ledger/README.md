# Claude Ledger integration contract

The Orchestra Core integration is unilateral and optional. Consumers may read:

- `organization.manifest.json`, validated against `schemas/organization-manifest.schema.json`;
- `events.jsonl`, whose records validate against `schemas/event.schema.json`.

The adapter never writes to the Ledger database, never starts a permanent HTTP server and never
changes workflow state outside Orchestra application services. Missing, incompatible or failing
consumers do not block Orchestra. Prompts, responses, reasoning, secrets and raw tool arguments are
excluded from the public protocol.

Protocol version `1.x` permits additive optional fields. A consumer must reject unknown major
versions and preserve `event_id` idempotency.

