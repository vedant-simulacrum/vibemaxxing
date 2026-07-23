# Privacy-preserving usage evidence

Updated: 2026-07-23

## Absolute privacy boundary

VibeMaxxing must never upload or receive:

- prompts or responses;
- source code or diffs;
- tool inputs or outputs;
- filenames, repository names, project names or working directories;
- raw local logs, transcripts, traces or database rows;
- provider API keys, local model weights or user documents;
- hashes of content-bearing fields that could enable dictionary attacks or correlation.

The hosted service receives only a compact, fixed-schema usage claim containing aggregate counters and integrity metadata that cannot reconstruct what the user worked on.

## Correction: cloud providers generally do not issue standardized signed receipts

OpenAI, Anthropic and Google commonly return token-usage metadata in ordinary API responses. Those fields are useful local accounting inputs, but they are not standardized cryptographic receipts signed by the provider for third-party verification.

Therefore:

- VibeMaxxing must not claim that cloud usage is proven by provider receipts unless a provider later exposes a documented signed-verification mechanism;
- provider response metadata is observed and normalized locally;
- no complete provider response is uploaded;
- provider request IDs are not uploaded by default because they can create cross-service correlation and may be sensitive;
- a provider-specific adapter may classify response metadata as stronger than estimated reconstruction, but not as independently provider-signed evidence.

## Local evidence pipeline

1. A source-specific adapter observes the smallest available usage metadata at the source boundary.
2. It immediately extracts only allowlisted fields such as model identifier, input-token count, output-token count, cache-token categories, reasoning-token categories, request outcome and event time.
3. It discards all content-bearing fields before the event enters shared collector storage.
4. The collector validates the event against a provider/runtime accounting profile.
5. The collector updates local aggregate counters and an append-only commitment chain.
6. The sync process submits only signed aggregate claims plus bounded integrity references.

The raw source event remains local and should be deleted according to a short configurable retention policy after aggregation and recovery windows expire.

## Data allowed to leave the device

A competitive claim may contain only:

- account-scoped pseudonymous device key identifier;
- claim sequence and previous-claim commitment;
- period bucket or server-anchor references;
- canonical provider/runtime and model identifiers from versioned registries;
- adapter certification artifact identifier;
- accounting-profile version;
- aggregate input, output, cache, reasoning and other explicitly typed billable counters;
- aggregate request/session counts where required;
- source-authority class;
- platform assurance class without unique hardware serials;
- verifier challenge or checkpoint reference;
- claim signature.

It must not contain per-request records, raw timestamps precise enough to reveal work patterns unless necessary, request IDs, hostnames, usernames, paths or content-derived commitments.

## What the server can and cannot prove

The server can verify:

- that a registered device key signed the claim;
- sequence continuity and replay resistance;
- that the claim used a certified adapter/accounting-profile tuple;
- that counters obey deterministic accounting and range rules;
- that server challenges/checkpoints are fresh;
- that device, adapter and policy states were eligible at acceptance time;
- whether duplicate or conflicting chains exist.

The server cannot prove the semantic content, usefulness or productivity of the activity, and must not attempt to do so.

Without a provider-signed mechanism or trusted hardware path, the server also cannot obtain mathematical proof that a compromised local client did not fabricate counters. The product manages that residual risk through transparent evidence tiers, deterministic controls, certification, continuity, anomaly review and appeals rather than content collection.

## Evidence classes under the privacy boundary

### Certified source metadata

The adapter reads explicit usage counters returned by a cloud API, agent runtime or local inference server. Only the counters are retained. This is stronger than estimating from text, but it is not called provider-signed unless cryptographically verifiable provider evidence exists.

### Certified deterministic local accounting

For local models, the adapter reads counters directly from a supported inference runtime or deterministically counts tokens using the exact tokenizer/model profile. Local-model usage is fully eligible for active competition.

### Generic reconstruction

A generic adapter reconstructs counts from incomplete non-content metadata. It may receive Standard only when a certified deterministic reconstruction profile exists. Otherwise it remains private analytics.

### Imported history

Historical imports remain private analytics and never enter active competition.

## Hardened without uploading logs

Hardened is awarded from the quality of the collection and integrity path, not from uploading raw evidence.

A privacy-preserving Hardened profile may require:

- an exact digest-addressed adapter build;
- a certified provider/runtime/model/accounting tuple;
- typed allowlisted local events;
- protected device keys where available;
- append-only sequence and hash continuity;
- server checkpoints before and after delayed offline intervals;
- bounded clock uncertainty;
- rollback and duplicate-chain detection;
- no unresolved gaps or unsupported estimation;
- a server verifier appraisal against a named policy version.

Hardware attestation may strengthen a profile on platforms where it is privacy-safe and available, but it is not universally required and must not expose stable hardware identifiers.

## Anti-cheat limits

Absolute privacy and perfect cheat prevention cannot both be guaranteed on arbitrary user-controlled machines. VibeMaxxing chooses:

1. absolute content privacy;
2. deterministic minimization;
3. transparent evidence strength;
4. strong replay, continuity, certification and identity controls;
5. progressive, appealable enforcement.

The product must never weaken the privacy boundary to inspect prompts, code or raw logs merely to improve leaderboard confidence.

## Public language

Approved claims:

- “Your prompts, code, filenames and local logs never leave your device.”
- “Only aggregate usage counters and privacy-safe integrity metadata are synchronized.”
- “Cloud and local models compete under transparent evidence profiles.”

Forbidden claims unless future provider mechanisms support them:

- “Provider-verified usage.”
- “Cryptographically proven cloud bill.”
- “Impossible to cheat.”
- “We verify your work without qualification.”
