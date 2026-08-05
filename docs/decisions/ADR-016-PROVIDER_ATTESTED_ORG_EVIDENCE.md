# ADR-016: Provider-attested organization evidence

Status: accepted
Date: 2026-08-06
Decision: D-078

## Context

The default ranked metric is accepted live Token Burn, scored as an additive `sum(token_burn_total)` with no stated cap. The product deliberately counts authentic intentionally pointless activity, and Token Burn may use authoritative counts from subscription-backed agents. Those three properties compose into a ranking that a determined participant can inflate cheaply and truthfully: every field of the resulting claim is accurate, the device signed it correctly, the accounting is deterministic, and no privacy rule was broken. Deterministic controls detect fabrication, duplication and replay. They cannot detect sincerity, and the product has decided not to try.

Every launch evidence class is therefore bounded by the user-controlled device. E2 observes an official source hook on that device. E3 observes a local gateway on that device. E4 derives counts on that device. A participant who controls the device controls the volume of genuine work fed into all three. The only class that escapes this is one whose count originates with the party that billed the work.

E1 was written for exactly that case and then reserved, because no provider shipped anything that qualified.

Research completed 2026-08-05 established that this is now half wrong. Provider-operated usage retrieval exists today, but only at organization scope:

- Anthropic exposes `/v1/organizations/usage_report/messages` and a Claude Code analytics endpoint, requiring an `sk-ant-admin01-` class administrative key. Anthropic's documentation states that the Admin API is unavailable for individual accounts. Buckets are 1m, 1h and 1d, groupable by API key, workspace, model and service tier.
- OpenAI exposes `/v1/organization/usage/completions` and `/v1/organization/costs`, requiring an administrative key held by an Org Owner. Usage arising from a ChatGPT-plan Codex session is not exposed there; the only route to it is the Enterprise Compliance API, which is content-bearing.
- Cursor exposes a team-administrator usage endpoint.
- Google exposes no usage REST API for AI Studio keys. Consumption is observable only through Cloud Monitoring, and only for callers using a GCP project.

No provider offers an OAuth scope by which an individual authorizes a third party to read that individual's own consumption. "Sign in with ChatGPT" conveys identity, not usage.

The consequence is asymmetric and unavoidable: a credible external evidence source is reachable now for organizations and is not reachable at any price for individuals. This ADR records what the product does with that asymmetry.

The provider facts above are research input dated 2026-08-05, re-checked against published provider documentation on 2026-08-06. That re-check confirmed the Anthropic Admin API usage report, its administrative key requirement and the documented unavailability for individual accounts; the OpenAI organization usage and cost endpoints and the Org Owner requirement for administrative keys; the Cursor `POST /teams/daily-usage-data` endpoint, its team-administrator key and its ninety-day per-request range limit; and the absence of a Google usage retrieval API for AI Studio keys. It also confirmed that the OpenAI compliance surface now exports Codex usage logs as part of a broader compliance logs platform for Enterprise and Edu customers, retained for thirty days — which reinforces rather than weakens the rejection below, because that surface carries conversation and audit content this product must never receive.

Documentation review establishes what a provider currently publishes. It does not establish endpoint behaviour, field stability, rate limits or contractual availability, none of which were exercised. Each surface is a third-party product that may change without notice.

## Decision

Organization, hacker-house and community boards may enrol a provider administrative usage source, and the server may retrieve aggregate consumption from it as a board-scope evidence input.

Individual accounts, the global board, friend boards and private boards remain self-reported under the existing local evidence classes. No individual is asked for a provider credential, and no per-account evidence state is derived from an organization retrieval.

E1 is no longer a single reserved class. It splits into a provider-signed limb that remains unavailable and a provider-retrieved limb that is available now at organization scope only.

## Evidence class mapping

E1 required an artifact that is cryptographically signed by the provider or verified through a provider-operated interface, binding exact model/version, usage categories, outcome, issuance time and anti-replay identity. It excluded ordinary JSON usage metadata, request IDs and invoices standing alone.

An organization usage report satisfies the second limb and fails the first. It is retrieved through an interface the provider operates, authenticated by a credential the provider issued, and its contents are not writable by the party being measured — that is where its authority comes from. It is also unsigned, carries no per-request outcome, carries no anti-replay identity, and is re-queryable rather than issued once. Read as an artifact in isolation it is precisely the ordinary JSON usage metadata that E1 excluded. Read as a channel it is the provider-operated verification interface that E1 was reserved for.

The class therefore splits rather than expands:

- `E1-S` — provider-signed claim receipt. Reserved and unavailable. No provider ships one.
- `E1-R` — provider-retrieved organization aggregate. Available now. Authority derives from the retrieval channel and the credential, not from the artifact.

This preserves the existing `source` dimension enum in `packages/schemas/evidence-profile-policy-v1.json` unchanged, and it matches the two limbs D-077 already recognized when it permitted either provider-signed receipts or server-side retrieval under verified account binding to be labelled source-bound.

`E1-R` binds at board scope and never at claim scope. It corroborates an organization board's aggregate total for an interval. It does not attach to an individual `EvidenceClaim`, does not travel with a member who leaves, and does not survive as a property of any account.

`E1-R` alone does not satisfy the E1 minimum of Hardened Source-Bound v1. Hardened additionally requires exact per-member runtime, model/tokenizer, mode, platform, adapter and collector certification and no unresolved observation gap, none of which an organization-level aggregate supplies. Hardened must not depend exclusively on cloud-provider receipts, and that constraint is unchanged by this decision.

## Organization enrolment

An administrator of the organization supplies a provider administrative credential scoped to that organization, together with the exact provider and endpoint being enrolled. Scheduled retrieval — performed by the server or by organization-operated infrastructure, according to the custody shape chosen below — collects aggregates, records the retrieval interval, the policy version and the exact endpoint, and stores the result as an immutable retrieval record.

Enrolment is administrator-initiated and organization-level. Members are not asked for keys, and a member's individual evidence state is unaffected by whether the organization enrolled. Asking individuals for provider API keys merely to prove usage remains an explicit product non-goal.

That non-goal is stated without qualification, so this ADR states its reading rather than assuming one. The non-goal governs the contestant relationship: no person is asked for a credential as the price of a ranked position. An organization administrator enrolling an organization-scoped credential on the organization's own board is a different act — voluntary, made by a party who already holds the credential, on behalf of an entity rather than a contestant, and refusable with no ranking cost. `docs/product/PRODUCT_SPEC.md` needs a scoping clarification saying so; that file is outside this unit's ownership and the edit is a required follow-up. Until it is made, the non-goal as written is in tension with organization enrolment, and enrolment must not be implemented on this ADR alone.

Retrieval is a fetch by the server from a third party. It is not a claim submitted by a device, and it does not enter the device claim path.

## Ingested field allowlist

The privacy contract governs what may cross from device to server. It does not currently govern what may cross from a provider to the server, because until now nothing did. This ADR defines that ingress explicitly rather than assuming the existing outbound allowlist covers it.

Permitted from a provider usage endpoint:

- token counts by usage category;
- the provider's model identifier;
- the time bucket boundaries;
- opaque organization, workspace and API-key identifiers;
- the service tier, where the provider reports it.

Forbidden from a provider usage endpoint, regardless of what the endpoint returns:

- workspace, project, repository and API-key display names, which are content-adjacent identifiers the absolute boundary already excludes;
- every non-token field of the Claude Code analytics surface, including lines-of-code, commit and pull-request counts, which measure productivity and are explicit product non-goals;
- anything from a compliance or export API, which is content-bearing by design.

A field absent from this allowlist is forbidden. Where a provider returns a forbidden field, it is discarded at the ingestion boundary and never persisted, including in raw response logs.

These endpoints return aggregates, so this ingress does not weaken the absolute server boundary — no prompt, response, transcript, code, diff, tool content, filename or path is available through them. The boundary is nonetheless newly bidirectional, and `docs/privacy/PRIVACY_CONTRACT.md` requires a provider-ingress section stating the above with the same force as the outbound allowlist. That section is a required follow-up and is not written by this ADR.

## Credential custody

No provider offers a read-only, usage-scoped credential. Every route requires a credential that administers the organization.

- An Anthropic admin key administers organization members, workspaces and API keys.
- An OpenAI admin key requires Org Owner.
- A Cursor team-admin credential administers the team.

Holding one of these means holding organization takeover capability for a third party, on behalf of a customer, for the sole purpose of reading a number. The blast radius of a custody failure is the customer's provider account, not the leaderboard. That is a materially larger liability than anything else the product stores, and it is the dominant risk this decision introduces.

There is also a direct textual conflict to record. The absolute server boundary states that VibeMaxxing servers, hosted web, observability, reviewer tools, support systems and release telemetry must never receive API keys, cookies, OAuth tokens or credentials. Read literally, that sentence forbids the enrolment step this ADR describes. The boundary was written to stop credentials leaving a user's device, not to describe a customer voluntarily delegating retrieval, but the words do not carry that distinction and the product does not get to read its own privacy contract loosely.

Two custody shapes can satisfy both the boundary and the decision, and this ADR deliberately chooses neither:

- retrieval runs on infrastructure the organization operates, the credential never reaches VibeMaxxing infrastructure at all, and only allowlisted aggregates are submitted;
- the credential is held in a separately consented, isolated custody service that no claim-processing, leaderboard, observability, reviewer or support component can read, under the same separately consented least-privilege framing D-067 applied to privileged supervision.

This ADR records the risk and does not invent the mitigation. The custody mechanism, rotation policy, revocation path, retrieval-host isolation, blast-radius containment and breach procedure are a security work item that must be accepted before any enrolment is implemented, and the privacy contract must be amended to state which shape is permitted. Enrolment must not ship ahead of either. Revocation by the organization at any time must degrade the board to self-reported without deleting accepted history, and every use of a custodied credential must be audited.

Providers should be asked for a read-only usage scope. Until one exists, the custody burden is the price of `E1-R`, and an organization that declines to pay it is not disadvantaged in ranking, because `E1-R` does not alter score.

## Public language

The words verified, proof and cheat-proof are not used on any surface arising from this decision. The forbidden-claims list makes "Provider-verified usage" conditional on a future provider mechanism supporting it, and the non-goals list forbids claiming provider authentication without evidence. It is arguable that an administrative usage endpoint is such a mechanism, and this ADR declines the argument.

The reason is not caution about wording. It is that the claim would be false at the level a reader applies it. A retrieved organization aggregate says the provider billed this organization for this many tokens in this interval. It says nothing about which member generated them, whether the work was sincere, or whether any individual on the board did what their row implies. A user reading "verified" next to a name will understand it to mean that person's usage was checked. It was not.

Organization boards therefore carry a board-scope, non-claiming source label describing what was retrieved and for what interval. No per-member badge is derived from it. No individual anywhere in the product becomes verified as a result of this decision.

The term attested is used in this ADR and in `E1-R` because it is precise engineering vocabulary for a count asserted by an external party. It remains banned from user-facing surfaces, and the tension between the internal and external vocabulary is real: an engineer reading `E1-R` will correctly understand it as attested, and must not carry that word into product copy.

## Rejected alternatives

- Collect provider API keys from individuals. Barred as an explicit non-goal, and no provider offers an individual read-only usage scope, so the credential collected would be a full-capability key. It would also become a farming instrument rather than a control, since the holder of a key controls the usage it reports.
- Wait for an individual OAuth usage scope before establishing any external evidence class. No provider has announced one, and identity-only sign-in does not approximate it. This defers the only available external evidence indefinitely in exchange for nothing.
- Admit the usage report as full E1 and let organizations reach Hardened on it. This treats a re-queryable unsigned aggregate as a signed per-claim receipt, and it contradicts the existing rule that Hardened must not depend exclusively on cloud-provider receipts.
- Use the Enterprise Compliance API to reach ChatGPT-plan Codex usage. That surface is content-bearing and incompatible with the absolute boundary at any configuration.
- Cap or re-weight Token Burn instead, so that farming stops paying. This is a coherent response to the same problem and is out of scope here. It also contradicts the rule that authentic intentionally pointless activity counts, so it requires its own decision rather than arriving as a side effect of this one.

## Limits

- This does not make individual rankings trustworthy. Individuals remain self-reported, no provider route exists for them, and the global board's integrity is unchanged by this decision.
- This does not eliminate farming inside an organization. An administrator can spend the organization's tokens on nothing, and the provider will report it accurately. What changes is the floor: fabricating a number costs nothing, while causing a provider to report one costs the provider's price for those tokens. The decision raises the cost of a false count, not the cost of a pointless one.
- A usage report is not a per-claim cryptographic receipt. It is unsigned, carries no per-request outcome, carries no anti-replay identity, is retrieved rather than issued, and can be re-queried to a different answer if the provider restates. It must never be described as a receipt.
- Coverage is partial and uneven. Google has no qualifying route. ChatGPT-plan Codex usage has no qualifying route. Organizations on providers without an administrative usage endpoint cannot enrol at all. The administrative endpoints that do exist report API-key traffic, while subscription-backed agent usage — which Token Burn explicitly permits — is the least covered case on every provider, so an organization can be fully enrolled and still have a large share of genuine activity that no retrieval corroborates. Partial coverage must never be presented as whole-board corroboration.
- Provider totals and claim totals will disagree transiently, through aggregation windows, late-arriving usage and provider-side restatement. Reconciliation must define a tolerance window and treat disagreement inside it as normal rather than as a contradiction, or the mechanism will manufacture false integrity signals against honest organizations.
- This introduces a dependency on three third-party product surfaces that may change shape, be rate-limited, be repriced, be restricted or be withdrawn, under no commitment to this product. Loss of a provider endpoint must degrade an enrolled board to self-reported without invalidating history.
- Nothing described here is implemented. No enrolment path, retrieval scheduler, ingestion filter, custody mechanism or board label exists.

## Required evidence

Before enrolment may be implemented:

- an accepted credential-custody decision covering storage, rotation, revocation, isolation and breach response;
- a provider-ingress section in the privacy contract carrying the allowlist above;
- a machine-readable representation distinguishing `E1-S` from `E1-R` in the appraisal policy, since the current policy file carries no marker for either;
- fixtures proving that a forbidden field returned by a provider is discarded at ingestion and never persisted;
- fixtures proving that loss of provider access degrades a board without mutating accepted history;
- fixtures covering late-arriving usage, provider restatement and partial coverage, proving that ordinary disagreement inside the tolerance window raises no integrity signal;
- a scoping clarification in the product specification distinguishing organization-administrator enrolment from asking a contestant for a provider key;
- comprehension testing that the board-scope source label is not read as a claim about individual members.

## Consequences

- E1 is no longer wholly reserved. `E1-S` remains unavailable; `E1-R` becomes available at organization scope.
- `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md` no longer states that E1 is unavailable outright.
- The server acquires an inbound third-party data path, which the privacy contract does not yet describe, and whose enrolment step conflicts with the absolute boundary as currently worded.
- The privacy contract, the product specification, `packages/schemas/evidence-profile-policy-v1.json` and the documentation map all require follow-up edits owned outside this unit before enrolment can be designed.
- The product acquires custody of organization-administrative third-party credentials, which is the largest security liability it holds.
- Organization boards can be corroborated externally; individual and global boards cannot, and that gap is permanent until a provider changes.
- Hardened Source-Bound v1 minimums are unchanged, and no board or account reaches Hardened by way of `E1-R`.
- No user-facing surface gains the words verified, proof or cheat-proof.
- Ranking scores are unchanged. `E1-R` is corroboration, not weight.
