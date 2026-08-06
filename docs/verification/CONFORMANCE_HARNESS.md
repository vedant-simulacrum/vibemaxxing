# Conformance Harness Design

Status: normative planning contract
Version: 1
Updated: 2026-08-06
Decisions: D-242

## The problem this addresses

`conformance/` holds sixteen directories of fixture data. Five of them — `adversarial`, `auth`, `release`, `sandbox` and `telemetry` — carried a three-line README saying the directory "defines the future conformance fixtures" and that the eval must remain `not_applicable` until real fixtures and runners exist. That honesty is right and it is not a design. Nothing said what a runner would do, what a fixture must contain, how a case is identified, or how a result becomes an eval status.

The result was fixture data with no harness, which is the condition `AGENTS.md` names directly: an unexecuted fixture is not authority, and a suite name must describe what it actually executes.

This document is the harness design. It does not change any suite's status, does not claim any suite executes, and does not modify `evals/suites/suites.yaml` or its status baseline — `docs/verification/EVAL_SYSTEM.md` owns those and the baseline exists precisely so that a status cannot be improved by prose.

## Directory contract

Every conformance suite is a directory under `conformance/` with this shape.

```
conformance/<suite>/
  README.md          what the suite proves, and what is currently absent
  manifest.json      the machine contract: cases, expectations, fixture digests
  <fixture files>    the data, in whatever form the suite's subject reads
```

`conformance/p1140e/` and `conformance/p1140f/` are exempt. They hold planning-review registries rather than executable conformance fixtures, they have their own validators and their own owners, and forcing them into this shape would break those.

### `manifest.json`

The manifest is the only thing a runner reads. It names the authority the suite tests against, so a suite cannot drift into testing an implementation against itself.

| Field | Meaning |
|---|---|
| `schema_version` | integer, 1 |
| `suite_id` | matches the directory name and the `id` in `evals/suites/suites.yaml` |
| `authorities` | repository-relative paths to the normative documents and machine contracts this suite tests conformance *to* |
| `subjects` | which implementations must run it: any of `rust`, `go`, `typescript`, `sql` |
| `cases` | the case list, below |
| `generated_by` | the deterministic generator path, or `null` for hand-authored fixtures |

Each case:

| Field | Meaning |
|---|---|
| `case_id` | `<SUITE>-<NNN>`, uppercase suite abbreviation, three digits, never reused |
| `title` | one line, imperative |
| `fixtures` | repository-relative paths, each with its SHA-256 |
| `expect` | `accept` or `reject` |
| `expect_reason_code` | required when `expect` is `reject`; must resolve in `packages/schemas/reason-codes-v1.json` |
| `authority_ref` | the specific clause, section or schema member this case exists to enforce |
| `negative` | boolean; true when the case exists to prove something fails |

Three of those fields carry most of the weight.

**`authorities` and `authority_ref`.** A conformance case with no pointer to the rule it enforces is a regression test. When the rule changes, nothing tells the engineer that the case must change too, so the suite quietly starts enforcing the old rule against the new specification. Requiring every case to name its clause makes that link mechanical: a validator can assert the path resolves, and a reviewer changing a contract can find every case bound to it.

**The fixture digest.** A fixture is data, and data edited without its expectation being revisited is the standard way a conformance suite becomes self-confirming. Recording the SHA-256 in the manifest means changing a fixture requires changing the manifest in the same diff, where a reviewer sees the expectation next to it.

**`negative`.** Every suite must contain at least one case with `negative: true`, and a manifest without one fails validation. A suite composed entirely of things that should work proves that the happy path exists; it does not prove that the boundary rejects anything, and the boundary is what conformance is about.

## Runners

A runner is per-language and per-suite, reads the manifest, executes each case against its subject, and emits the result document `EVAL_SYSTEM.md` already defines — `suite`, `version`, `commit`, `status`, `cases[]`, `started_at`, `finished_at`. Nothing about that schema changes here.

| Subject | Runner | Invocation |
|---|---|---|
| Rust | a binary in the workspace | `cargo run -p conformance-runner -- --suite <id>` |
| Go | a command under `apps/api` | `go run ./cmd/conformance --suite <id>` |
| TypeScript | a `vitest` entry point | driven by the manifest, not by hand-written cases |
| SQL | a Python stage in the existing planning validators | applies fixtures against `postgres:16` |

The runner is generic over the suite. Per-suite logic lives in the manifest and in the subject's decoder, not in a bespoke script, because a bespoke script per suite is where the expectation and the implementation start agreeing with each other.

### The cross-language rule

A case is `pass` only when **every declared subject produces the expected outcome, and the subjects agree with each other**. Two implementations agreeing on the wrong answer is a `fail`, not a pass, and the runner reports the disagreement class:

| Outcome | Meaning |
|---|---|
| `pass` | every subject matched `expect`, and matched each other |
| `fail: expectation` | subjects agreed with each other and not with `expect` — the implementations share a defect, or the expectation is wrong |
| `fail: divergence` | subjects disagreed with each other — at least one is wrong and the corpus cannot say which |
| `fail: reason` | the outcome was correct and the `reason_code` was not |

The distinction exists because `AGENTS.md` states the rule this enforces: cross-language agreement is not conformance when both implementations consume the wrong authority. A harness that reports only pass and fail cannot express the difference between "we are both wrong" and "we disagree", and those two need different responses.

### Determinism

A runner must be deterministic. No wall-clock dependence, no network, no randomness without a recorded seed, and no ordering dependence between cases. Running the same commit against the same fixtures twice produces byte-identical results, which is what makes a result diffable and a regression attributable.

## Case identifier scheme

| Suite | Prefix | Subject |
|---|---|---|
| `vibeproof` | `VP` | canonical encoding, signatures, exact-byte vectors |
| `protocol` | `PR` | claim, batch, challenge and checkpoint exchange |
| `accounting` | `AC` | normalisation, token categories, retries, duplicates |
| `pricing` | `PC` | pricing datasets, effective dates, unpriced outcomes |
| `adapters` | `AD` | per-adapter receive surface and stage mapping |
| `auth` | `AU` | OAuth exchanges, session and refresh families, recovery |
| `privacy` | `PV` | boundary canaries and forbidden-field rejection |
| `social` | `SO` | friends, blocks, rivals, board authorization |
| `models` | `MD` | model registry and selection |
| `onboarding` | `ON` | first-run consent and verification flow |
| `release` | `RL` | release sets, TUF metadata, update deadlines, rollback |
| `sandbox` | `SB` | process isolation, loopback origin controls, IPC boundaries |
| `telemetry` | `TM` | emitted attribute allowlist and log-field allowlist |
| `adversarial` | `AV` | the attack catalogue, one case per catalogued attack |

Identifiers are permanent. A retired case keeps its number and is marked retired in the manifest rather than being deleted and its number reused, because a result document from six months ago cites the number and must remain readable.

## What each of the five empty suites needs

The five directories that carried three-line READMEs, with the specific content that would make each executable. This is the work, stated so it can be estimated rather than discovered.

**`auth` (`AU`).** Fixtures for each OAuth transaction shape: an authorization code replayed, a `state` mismatch, an expired code, a code redeemed twice, a refresh handle presented twice (which ADR-015 makes always an incident), a session family past its 90-day absolute cap, a device-authorization code polled faster than the 5-second minimum, and a recovery attempt inside the cooling-off period. Authority: `docs/security/AUTHENTICATION_AND_RECOVERY.md` and ADR-015.

**`release` (`RL`).** A well-formed release set; then one each for rollback, freeze, mix-and-match, fast-forward and endless-data — the five attacks the operations contract requires clients to defend against, which is a case list of exactly five plus the positive. Add expired timestamp metadata, expired snapshot, a targets delegation outside its scope, and a client past a signed update deadline. Authority: the operations contract, ADR-013, `packages/schemas/release-set-v1.schema.json`.

**`sandbox` (`SB`).** The loopback and isolation cases in `docs/security/ORIGIN_AND_LOOPBACK_CONTROLS.md`: a rebinding-shaped `Host`, a foreign `Origin` on a state-changing route, a preflight from a non-allowlisted origin, an expired dashboard token, an unauthenticated request past the 10-per-minute probe limit. Plus the process-boundary cases already specified in the privacy eval: a transcript-reading component attempting network access, a sync component attempting to open transcript storage. Authority: `docs/security/PLATFORM_ISOLATION.md`, `docs/security/LOCAL_IPC_AND_DEVICE_IDENTITY.md`, and the origin controls document.

**`telemetry` (`TM`).** A datapoint carrying each forbidden class, asserted dropped; a log line carrying each, asserted dropped; an unknown attribute, asserted dropped and flagged rather than passed; the five OTLP identity attributes of D-099, asserted stripped inside the receiver; a high-entropy value in an allowed field, asserted caught by the entropy scan. Authority: `packages/schemas/observability-allowlist-v1.yaml`, `docs/operations/OBSERVABILITY_PRIVACY.md`, `docs/operations/LOGGING_AND_INSTRUMENTATION.md`.

**`adversarial` (`AV`).** One case per entry in `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`, each asserting the catalogued control produces the catalogued outcome. This is the largest of the five and the most mechanical: the catalogue already states attack, control, expected outcome and confounder for every row, which is a case definition in all but format. `conformance/adversarial/anti-cheat-registry-v1.json` and `wave4-cases.json` are the partial start.

## Validation now, execution later

The manifest format can be validated today, against fixture data that no runner executes, and that validation is worth having because it catches the failures that would otherwise be discovered by the first runner:

- every path in `authorities`, `fixtures` and `authority_ref` resolves;
- every `expect_reason_code` resolves in `packages/schemas/reason-codes-v1.json`;
- every fixture's recorded digest matches the file;
- `case_id` values are unique, correctly prefixed and unreused;
- every suite declares at least one `negative` case;
- every `suite_id` matches an `id` in `evals/suites/suites.yaml`.

**Passing that validation is not conformance and does not change any suite's status.** It proves a manifest is well-formed. A suite whose manifest validates and whose runner does not exist stays `not_applicable`, and the `not_applicable_until` paths in the eval registry keep naming the runner whose absence is the justification — which means the moment a runner appears, the registry fails until the status is raised. That mechanism already exists; this document supplies the thing it is waiting for.

## Evidence

No runner exists in any language. No manifest exists in any suite. The five suites named above hold no executable fixture. Three eval suites are `ready` and 24 are `not_applicable`. Everything in this document is a design for a harness that has never run, and nothing in it may be cited as coverage.
