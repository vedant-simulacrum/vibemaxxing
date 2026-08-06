# Universal Agent Compatibility Architecture

Updated: 2026-07-19
Status: planning contract

## Objective

Support every materially relevant AI-agent category through a living compatibility system without falsely claiming equal evidence quality or bespoke certification for unknown tools.

## Support states

1. **Hardened-certified** — source-bound live capture, official adapter, exercised conformance, supported version, signed build, continuity and available platform hardening.
2. **Competitive-certified** — live structured capture, stable accounting, privacy-negative tests, versioned probe, eligible for Standard ranking.
3. **Community-certified** — community-maintained adapter that passes required automated and human review gates; evidence state is explicit.
4. **Generic live** — ACP, OpenTelemetry, proxy, wrapper, gateway, or local-server integration with lower assurance.
5. **Imported** — retrospective mutable records, private analytics only.
6. **Unsupported** — no safe credible measurement path; must be stated honestly.

## Agent families

The registry must classify CLI agents, IDE extensions, desktop agents, browser/cloud agents, autonomous coding platforms, orchestration frameworks, subagent systems, ACP-compatible tools, OpenTelemetry-capable tools, API gateways, OpenAI-compatible servers, Anthropic-compatible servers, local inference servers, CI agents, remote development environments, and unknown tools.

## Required registry fields

- stable adapter ID and agent family;
- vendor/project and ownership;
- open/closed source;
- supported versions and modes;
- platforms and environments;
- capture mechanism and source authority;
- token categories and known omissions;
- session, request, retry, cache, tool, image, reasoning, compaction, and subagent semantics;
- model identity quality;
- required permissions;
- privacy hazards and forbidden fields;
- double-count risks;
- evidence tier eligibility;
- capability-probe version and latest exercised result;
- conformance suite and fixture versions;
- maintainer, review status, emergency-disable state, and sunset date.

## The atomic compatibility tuple

The registry fields above describe an adapter. The tuple describes the exact thing a certification is about, and `packages/schemas/compatibility-tuple-v1.schema.json` is its machine-readable form. D-327 records why each dimension is inside it.

| Dimension | Why changing it changes the tuple |
|---|---|
| Collector artifact SHA-256 | D-058 makes trust digest-addressed; a rebuilt collector is a different observer |
| Source product and bounded version range | the observation surface moves between major versions, and an open-ended upper bound would certify software that does not exist yet |
| Observation mode | the nine values `packages/schemas/observer-equivalence-v1.json` declares, in that spelling. Two modes observing one execution have different precedence and different ceilings |
| Platform profile | key-protection class, supervision mechanism and isolation strength all differ per profile, and the evidence ceiling depends on them |
| Accounting profile and arithmetic digests | a profile edit changes what the same numbers mean |
| Privacy binding digests | a changed attribute allowlist or strip list is a changed boundary, which D-099 makes a collector obligation rather than a setting |

The tuple digest is SHA-256 over the RFC 8949 core deterministic CBOR encoding of the record with the digest field omitted, computed the way D-261 computes every planning policy digest, so two implementations cannot disagree about the identity of a tuple.

A certification of one tuple says nothing about any other. This is what the phrase "exact certified source and accounting tuple" means everywhere it appears in the binding rules, and `source_certifications` is where it lives.

## Capability ladder

Prefer, in order:

1. provider- or agent-issued authenticated usage evidence;
2. protocol-bound broker/proxy or ACP path;
3. native structured telemetry such as OpenTelemetry;
4. official hooks or plugins;
5. structured programmatic output;
6. PTY or stdio wrapper;
7. live source-bound local observation;
8. generic local gateway observation;
9. historical import only.

A weaker mechanism may not be described as equivalent to a stronger one.

## Adapter lifecycle

`discovered → experimental → community-certified → competitive-certified → hardened-certified`

Any state may transition to `degraded`, `suspended`, `unsupported`, or `retired` after source/version change, privacy failure, conformance failure, security incident, or maintainer abandonment.

## Runtime rules

- Detect source and version before accepting ranked activity.
- Unknown or changed versions fail closed or downgrade according to the adapter contract.
- Never ingest content-bearing telemetry merely because it is available.
- Prevent duplicate accounting when multiple capture paths observe the same activity.
- Preserve adapter, source, version, mode, and evidence provenance in every normalized event and claim.
- Emergency eligibility revocation may be server-controlled, but remote code execution or hidden local behavior is forbidden.
- Support pages are generated from exercised registry evidence, not handwritten marketing lists.

## Community adapters

Community contributions require:

- documented source authority;
- privacy threat analysis;
- deterministic normalization;
- version probes;
- positive and negative fixtures;
- double-count tests;
- unsupported-mode behavior;
- maintainer ownership;
- signed contribution provenance;
- review and revocation process.

Community certification does not automatically grant Hardened eligibility.

## Universal coverage interpretation

Public launch must cover all major agent families and provide a credible generic path for unknown tools. It does not claim bespoke Hardened certification for every private or future agent. Unsupported tools are visible as gaps with contribution and research paths.

## Required research outputs

- machine-readable agent census;
- adapter manifest JSON Schema;
- normalized event schema;
- source-precedence and reconciliation matrix;
- certification conformance plan;
- community governance policy;
- compatibility dashboard and generated support claims;
- release-blocking coverage matrix for all major agent families.
