# Repository Layout Contract

Status: normative planning contract
Updated: 2026-07-19

## Current planning tree

The current repository is documentation- and planning-heavy. Confirmed implementation seed areas include:

```text
/apps/api                 minimal Go module seed
/apps/web                 web implementation area or seed when present
/crates/                  Rust implementation areas already present
/packages/protocol        protocol implementation placeholder
/packages/schemas         authoritative planning-grade schemas
/conformance              registries and future executable fixtures
/docs                     project authority, contracts, ADRs, planning and research
/scripts                  repository and future engineering tooling
/.github                  repository policy and planning validation
```

A path not present in the current Git tree must not be treated as implemented or initialized.

## Approved future implementation tree

The following is the intended tree created incrementally by the PR-sized work breakdown after explicit implementation approval:

```text
/apps/web                         Next.js hosted product
/apps/api                         Go API and workers
/apps/desktop                     native shell packaging and platform UI
/apps/docs                        public protocol/product documentation
/crates/vibeproof-core            events, accounting, claims and cryptographic profile
/crates/vibeproof-adapters        adapter SDK and built-in adapters
/crates/vibeproof-collector       transcript-capable no-network collection
/crates/vibeproof-sync            network-capable safe-claim synchronization
/crates/vibemaxxing-daemon        supervisor and local control API
/crates/vibemaxxing-cli           installer and control CLI
/packages/protocol                generated cross-language bindings
/packages/schemas                 OpenAPI, JSON Schema, Protobuf and CDDL sources
/migrations                       executable PostgreSQL migration history
/conformance                      protocol, accounting, adapter, privacy and attack fixtures
/benchmarks                       native, server, database and frontend benchmarks
/infrastructure                   cloud-portable reference deployment
/artifacts                        generated non-authoritative evidence and metadata
```

D-636 deleted the component system and its written rules, and D-637 then deleted the brand, the governed asset library and the brand tooling. The UI package, the style-guide directory, the asset directory and the brand script directory are named in neither tree above and none is demoted to a future path, because nothing has decided where any replacement would live. A successor reserves its path in this document when it is decided, and not before.

## Creation rules

- Directories are created only by their owning work unit.
- Empty directories are not evidence; use a README only when a future location must be reserved.
- The implementation handoff may describe future paths only by linking to this document.
- The repository doctor validates current required paths and does not require uncreated future paths.
- A material change to component boundaries requires an ADR and updates to this file, CODEOWNERS, schemas, and work breakdown.
