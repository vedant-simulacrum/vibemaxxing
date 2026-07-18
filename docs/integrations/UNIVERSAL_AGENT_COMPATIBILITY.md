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
