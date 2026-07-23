# Anti-cheat systems research

Updated: 2026-07-23
Status: research and planning input; not implementation evidence

## Executive conclusion

VibeMaxxing cannot make arbitrary user-controlled computers mathematically prove genuine AI usage while also preserving an absolute no-content-upload privacy boundary. Strong anti-cheat is nevertheless achievable as a layered risk-reduction system.

The best current architecture is not a gaming-style kernel anti-cheat and not a standalone SLM. It is a combination of:

1. source-specific deterministic accounting;
2. signed, versioned adapters and collector builds;
3. protected device keys and explicit device lineage;
4. precommitted local continuity plus server checkpoints;
5. atomic replay, duplicate and fork rejection;
6. server-derived evidence appraisal;
7. privacy-safe anomaly detection;
8. a locally sandboxed SLM only where it provides measured incremental value;
9. progressive enforcement, human review and reversible ranking effects;
10. secure release and update provenance.

The system should make casual fabrication difficult, scalable fabrication expensive, cloning and retrospective history generation detectable, and enforcement reviewable. It must not claim that cheating is impossible.

## Research questions and answers

### Can local usage be proven without uploading logs?

Not universally. A local collector can accurately count usage from runtime-native counters, emitted token IDs or an exact tokenizer, but a user with full control of the machine can modify the source, collector or operating environment.

The appropriate claim is therefore bounded:

- a named adapter observed a named source through a named capture path;
- a protected key signed an ordered claim;
- deterministic accounting and privacy rules passed;
- continuity, freshness and compatibility checks passed;
- the server appraised the claim under a versioned policy.

This follows the IETF RATS separation between Attester evidence, Verifier appraisal and Relying Party decisions. The claimant must not self-award a public integrity tier.

### Are ordinary API usage fields provider receipts?

No. Ordinary response usage metadata is useful local accounting input, but it is not a standardized provider-signed artifact independently verifiable by VibeMaxxing.

Provider-signed evidence should remain a reserved evidence class that is unavailable unless a provider actually exposes a signed artifact or verification interface binding model identity, usage, time and anti-replay data.

### Should VibeMaxxing proxy model traffic to obtain stronger evidence?

No for the normal launch product. A VibeMaxxing-controlled inference gateway would violate the product's strongest privacy proposition and disadvantage local models. Any future hosted inference offering must be a separate, explicit product mode and not a prerequisite for competitive ranking.

### Is hardware or OS attestation sufficient?

No. Attestation can establish facts such as app identity, key protection or device posture. It does not establish that token counts are semantically genuine unless the complete measurement and accounting path is covered.

Apple explicitly warns that an app cannot securely perform its own integrity decision and provides App Attest as server-verified app-instance evidence. However, App Attest is unavailable for macOS apps, so it cannot solve the desktop launch problem. Android Play Integrity can provide app, device, environment and replay-resistant request verdicts, but VibeMaxxing is primarily a desktop product. Windows TPM-backed non-migratable keys can strengthen device-key protection but do not automatically attest the entire collector and source path.

Attestation should therefore be an optional evidence dimension, not the definition of genuine usage.

### Should VibeMaxxing use a kernel anti-cheat?

No.

A kernel component would create severe privacy, security, signing, support and platform-equity costs while still failing to prove remote API usage or semantic authenticity. It would also contradict the product's privacy posture and make open-source adoption substantially harder.

The default architecture should be an unprivileged per-user collector. Narrow privileged helpers may be considered only for a specific Hardened capture capability after a separate threat and privacy review.

### Can an SLM detect edited or fabricated logs?

Potentially, but it should not be trusted as an authority.

Research on log anomaly detection shows that sequence models can identify deviations, but performance is highly dependent on dataset construction, parsing, grouping, noise and class balance. Evaluations that report very high scores on standard datasets often fail to generalize. Adversarial research also shows that anomaly detectors can be evaded by adding cover events.

Raw log content is additionally an adversarial prompt-injection surface. Recent work on LLM-based security log analysis reports successful instruction injection through attacker-controlled log fields, with mitigations reducing but not eliminating the risk.

The correct SLM role is therefore:

- local only;
- no network, tools, shell, plugins or autonomous actions;
- bounded input;
- fixed registered output schema;
- unable to change accounting totals;
- unable to award Hardened;
- unable to permanently ban;
- evaluated against deterministic and classical baselines;
- deployed first in shadow/advisory mode.

Two modes should be benchmarked:

1. structured-feature mode, consuming typed counters, timings, source versions and deterministic-rule results;
2. sandboxed raw-local-record mode, reading bounded records locally while emitting only registered anomaly classes and no content-derived identifiers.

### What prevents retrospective offline fabrication?

A fresh challenge at upload time does not prove that events existed during the offline interval.

The client needs a precommitment mechanism:

- append-only local event commitments;
- a rolling accumulator or hash-chain head;
- protected checkpoint state;
- previous server checkpoint receipt;
- explicit offline interval boundaries;
- reconnect challenge bound to the current head;
- fork and rollback outcomes.

Where the platform cannot provide rollback-resistant state, the continuity class must be lower. Long offline intervals may still count, but their public evidence profile must accurately reflect the weaker anchoring.

### How should replay and cloning be handled?

Every competitive claim must bind:

- account and device lineage;
- claim sequence;
- previous local commitment;
- previous server-accepted checkpoint;
- challenge;
- adapter and build digests;
- accounting profile;
- source event range;
- duplicate-domain identifier.

The server acceptance operation must be atomic. Exact duplicate submissions return the original result. Conflicting reuse of a sequence, challenge, event, commitment or duplicate-domain identifier is rejected or quarantined. Concurrent successors create a fork and quarantine the device lineage.

A restored or cloned state must never silently continue the old trust chain. Recovery creates an explicit new lineage or lowers its evidence profile.

### How should OAuth contribute to anti-cheat?

OAuth proves control of an account at an identity provider; it does not prove one human, one device or non-collusion.

Use OAuth for login, provider linking and recovery. Follow RFC 9700 with authorization code flow, transaction-specific PKCE, exact redirect validation and refresh-token replay protection. DPoP can sender-constrain VibeMaxxing access and refresh tokens and reduce token replay, but RFC 9449 does not make it proof of human uniqueness.

The one-human/one-ranking-identity policy needs a separate private integrity system based on linked-account, device, recovery and enforcement lineage, with appeals and no public disclosure of private linkage signals.

### How should universal agent support work?

Universal support must mean universal discovery and graceful capability grading, not universal eligibility for the strongest ranking tier.

Each adapter declares capabilities such as:

- native usage counters;
- generated token IDs;
- exact tokenizer availability;
- retry and cancellation visibility;
- cache accounting;
- stable source execution identifier;
- process binding;
- source version discovery;
- monotonic counters;
- structured event stream;
- import-only mutable history.

The registry derives a support ceiling:

- Hardened-capable competitive;
- Standard competitive;
- private analytics only;
- unsupported.

Unknown versions fail closed for stronger profiles and may downgrade only to an exercised compatible profile.

### What should the desktop architecture be?

Use a shared collector core with thin platform integrations.

macOS:

- unprivileged per-user LaunchAgent registered through `SMAppService`;
- menu-bar UI as a separate process;
- XPC or an equivalently authenticated local IPC boundary;
- LaunchDaemon only for separately approved privileged capabilities.

Windows:

- prefer a per-user background process for the normal collector;
- use a Windows Service only when system-level or pre-login behavior is genuinely required;
- separate tray UI from service/background logic;
- protect IPC with OS security descriptors and peer identity.

Linux:

- user-level systemd service where available;
- optional tray UI;
- documented fallback for non-systemd environments;
- no root daemon by default.

The menu-bar/tray app is a control and diagnostics surface, not the trusted counting boundary.

### How should release integrity be protected?

Anti-cheat collapses if attackers can distribute modified adapters, collectors or detector models as official builds.

Use:

- signed release artifacts;
- digest-addressed adapter and detector manifests;
- reproducible or independently rebuildable release targets where feasible;
- provenance metadata;
- transparency logging;
- rollback-resistant update metadata;
- explicit key rotation and compromise recovery.

TUF provides protections against rollback, freeze and inconsistent repository views. in-toto provides signed supply-chain step metadata. Sigstore/Rekor provides signature transparency. These mechanisms protect official build identity; they do not prove local usage by themselves.

## Recommended anti-cheat architecture

### Layer 1: source accounting

Use this authority order:

1. source/runtime-native structured counters;
2. token IDs observed at generation;
3. exact model tokenizer reconstruction;
4. certified agent session counters;
5. estimates, private analytics only unless separately approved.

Preserve input, output, cache read, cache write, reasoning and modality fields independently. A versioned accounting profile defines score semantics and prevents double counting.

### Layer 2: typed local collection

Separate four data types:

1. ephemeral source observation;
2. normalized local accounting event;
3. detector feature/result bundle;
4. outbound aggregate claim.

Only the fourth crosses the network. Privileged boundaries accept fixed typed schemas, never arbitrary provider JSON or free text.

### Layer 3: deterministic local validation

Run deterministic checks before any SLM:

- schema and range validity;
- monotonic ordering;
- source-version and adapter digest;
- token-category invariants;
- retry/cancellation reconciliation;
- duplicate-domain collision;
- cross-source mismatch;
- runtime throughput envelope;
- clock rollback, suspension and counter reset;
- privacy allowlist and forbidden-content canaries.

### Layer 4: local anomaly analysis

Use classical statistical and sequence baselines first. Evaluate the SLM only for incremental detection of format manipulation, cross-record inconsistencies and synthetic generation patterns.

SLM output is a bounded risk input. Contradictions from deterministic checks cannot be overridden by the SLM.

### Layer 5: device and build integrity

- per-installation signing key;
- strongest non-exportable platform storage available;
- explicit protection class;
- official build digest;
- adapter and detector digest;
- optional platform attestation;
- signed update provenance;
- lineage changes after recovery, restore or clone uncertainty.

### Layer 6: continuity and freshness

- local append-only commitments;
- rolling commitment head;
- server checkpoint receipts;
- single-use challenges;
- exact sequence and previous-state binding;
- explicit offline intervals;
- fork, rollback and gap outcomes.

### Layer 7: atomic server verifier

The server validates facts and produces a separate appraisal.

Possible outcomes:

- accepted;
- accepted idempotently;
- accepted with a lower profile;
- quarantined;
- rejected for replay, privacy, unsupported source, invalid accounting, invalid signature or invalid continuity.

### Layer 8: server anomaly detection

Use only privacy-safe aggregate and integrity features:

- model/runtime throughput distributions;
- claim burst and offline interval patterns;
- repeated forks and recoveries;
- duplicate chain structures;
- impossible accounting ratios;
- linked ranked-identity risk;
- board-level collusion patterns.

Operate new detectors in shadow mode and calibrate thresholds before enforcement.

### Layer 9: enforcement and appeals

Progressive outcomes:

1. lower evidence profile;
2. quarantine claim or period;
3. temporary ranking restriction;
4. exclude claims;
5. duplicate-identity resolution;
6. permanent ranking exclusion for repeated deliberate fraud.

All actions require registered reasons, affected claim/period scope, policy version, reviewer audit and deterministic reversal/rebuild behavior.

## Explicitly rejected approaches

- uploading raw usage logs;
- uploading prompts, outputs, code, paths or repositories;
- hashing content for server-side deduplication;
- mandatory provider proxying;
- kernel anti-cheat as the default architecture;
- treating OAuth as proof of one human;
- letting the client assert Hardened;
- letting the SLM alter totals or ban users;
- claiming provider verification without provider-signed evidence;
- claiming universal Hardened support;
- relying on upload-time challenges as proof of offline event existence.

## Required evaluation program

### Deterministic corpus

Create source-specific positive, negative and adversarial fixtures for:

- edited counters;
- duplicated requests;
- retry and cancellation edge cases;
- cache and reasoning double counting;
- malformed versions;
- clock rollback;
- suspend/resume;
- source reset;
- clone and restore;
- offline reconnect;
- schema smuggling and privacy canaries.

### SLM and anomaly corpus

Use synthetic and consented test data, never production user logs.

Include:

- benign format drift;
- legitimate extreme usage;
- fabricated records;
- sparse edits;
- copied sessions;
- synthetic distributions;
- prompt injection embedded in every content-bearing field;
- multilingual and encoded injection;
- fragmented cross-record injection;
- detector-model substitution and rollback.

Compare:

- deterministic rules;
- robust statistics;
- isolation/one-class models;
- sequence models;
- structured-feature SLM;
- raw-local-record SLM.

Predeclare false-positive ceilings. Detection lift without calibration is not sufficient.

## Launch gate

Public competitive launch remains no-go until there is executable evidence for:

- at least one cloud API source and one local runtime;
- deterministic accounting and duplicate handling;
- signed claims and atomic replay protection;
- device key lifecycle;
- offline checkpoint semantics;
- privacy canaries;
- ranking exclusion and reversal;
- hostile clone/restore tests;
- modified adapter/collector tests;
- legitimate high-volume stress tests;
- operational appeals.

An SLM is not automatically required for launch. It becomes launch-required only if a measured bakeoff demonstrates material incremental value at the declared false-positive ceiling.

## Primary and authoritative sources

- IETF RFC 9334, Remote ATtestation procedureS Architecture: https://www.rfc-editor.org/rfc/rfc9334.html
- IETF RFC 9999, RATS Conceptual Message Wrapper: https://www.rfc-editor.org/rfc/rfc9999.html
- IETF RFC 9700, Best Current Practice for OAuth 2.0 Security: https://www.rfc-editor.org/rfc/rfc9700.html
- IETF RFC 9449, OAuth 2.0 Demonstrating Proof of Possession: https://www.rfc-editor.org/rfc/rfc9449.html
- Apple, Establishing your app's integrity: https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity
- Apple, App Attest support limitations: https://developer.apple.com/documentation/devicecheck/dcappattestservice/issupported
- Apple, Service Management and SMAppService: https://developer.apple.com/documentation/servicemanagement/smappservice
- Google, Play Integrity overview: https://developer.android.com/google/play/integrity/overview
- Google, Play Integrity standard requests and request binding: https://developer.android.com/google/play/integrity/standard
- Microsoft, Windows services: https://learn.microsoft.com/en-us/windows/win32/services/about-services
- Microsoft, TPM key attestation: https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/adc2aab5-701b-4f91-9dc0-5615543712bf
- NIST AI 100-2 E2025, Adversarial Machine Learning: https://csrc.nist.gov/pubs/ai/100/2/e2025/final
- NIST SP 800-218, Secure Software Development Framework: https://csrc.nist.gov/pubs/sp/800/218/final
- The Update Framework security model: https://theupdateframework.io/docs/security/
- The Update Framework metadata roles: https://theupdateframework.io/docs/metadata/
- in-toto specification and model: https://in-toto.io/docs/specs/
- Sigstore Rekor transparency log: https://docs.sigstore.dev/logging/overview/
- Loghub datasets and benchmarks: https://github.com/logpai/loghub
- Log-based anomaly detection evaluation caveats: https://arxiv.org/abs/2202.04301
- Adversarial evasion of log anomaly detection: https://www.usenix.org/conference/usenixsecurity23/presentation/xu-xiaojun
- Prompt injection through adversarial log content: https://arxiv.org/abs/2605.24421
- Passive prompt injection in security-log analysis: https://arxiv.org/abs/2607.14493

## Research confidence and limitations

The cryptographic, OAuth, attestation, desktop service and supply-chain conclusions are grounded in standards and official platform documentation. The SLM-specific conclusion is necessarily more tentative: direct research on detecting tampering in AI-agent usage logs is limited, and recent log-prompt-injection papers are early research rather than mature standards. This strengthens the case for an empirical bakeoff instead of committing the launch architecture to an SLM in advance.
