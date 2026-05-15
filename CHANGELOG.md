# Changelog

All notable changes to this project are tracked here as an engineering log.

## [1.0.0] - 2026-05-14

### Shipped
- Published **cyberark-access-review-sync** as a public Python and FastAPI integration surface for turning CyberArk privileged-account metadata into access-review queues, stale-access findings, and approval-ready payloads.
- Added HTML proof surfaces for overview, review queue, findings matrix, methodology, and API summary.
- Added JSON APIs for account catalog records, review queues, findings, and sample governance payloads.
- Added generated SVG proof assets, tests, smoke checks, CI, architecture notes, and origin narrative.

## [0.1.0] - 2026-03-19

### Prototype
- Landed the first internal version of the sync model with stale-account scoring, owner-gap detection, and ticket/evidence readiness checks.
- Started expressing privileged-review risk as an operator queue instead of a flat certification export.
- Added the first approval-payload shape so downstream review systems could consume the same account record without translation glue.

## [Design Phase] - 2025-10-07

### Framing
- Refined the repo around a simple enterprise reality: vaulting is only one part of privileged-access governance, and review operations often remain too manual to trust.
- Chose FastAPI and a control-plane-style surface so the same record could serve both security operators and downstream audit or review workflows.
- Focused the decision model on stale access, review age, approval evidence age, ownership quality, and dual-approval expectations.

## [Idea Origin] - 2024-05-29

### Observation
- Noticed that privileged-access reviews often fail because the operational story around an account is weak, not because the vault is missing the credential.
- Started sketching a review-sync layer where CyberArk account records could be enriched with review age, ticket state, and manager verification instead of being exported as static inventory.

## [Background Signals] - 2023-01-25

### Early signals
- Collected repeated patterns from enterprise identity and platform environments where stale accounts survived multiple review cycles because nobody had a clean way to rank them by risk and review readiness.
- Logged examples where ownership gaps and missing evidence created more real approval friction than the vault controls themselves.

## [Prehistory] - 2022-09-14

### Foundations
- Captured the first notes around making privileged-access review feel more like an operator workflow and less like a spreadsheet ceremony.
- Marked down the core principle that the most important CyberArk record is often not the password state alone, but the evidence proving why the account still deserves to exist.
