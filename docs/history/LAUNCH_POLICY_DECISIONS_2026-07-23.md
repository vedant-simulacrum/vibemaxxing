# Public launch policy decisions

Updated: 2026-07-23

This document closes the product-policy questions raised by the consolidated audit. It is a planning decision record and does not authorize implementation.

## Terminology correction

The relevant term is **Hardened evidence**, not “heart and evidence.”

- **Standard** means the usage is accepted as genuine enough for competition but lacks the strongest available source binding, continuity, device assurance or certification.
- **Hardened** means a server verifier has awarded a named, versioned evidence profile after all required checks pass.
- Neither label is selected by the client.

## Locked decisions

### 1. Local-model and fully offline usage counts competitively

Authentic local-model usage is first-class usage. A user who burns 20 million tokens on a local model must appear in the relevant active leaderboards when the collector can deterministically observe and account for that usage.

The product must not discriminate against local models merely because no cloud provider receipt exists.

The rule is:

- deterministic, source-bound local accounting may receive Standard or Hardened according to its certified evidence profile;
- fully offline activity may enter active competition after later synchronization;
- lack of a live server connection does not by itself make usage private-only or ineligible;
- uncertainty, gaps, rollback risk or unverifiable reconstruction lower the evidence profile rather than automatically deleting genuine usage;
- generic estimates that cannot be deterministically reconstructed remain private analytics and do not enter active competition.

Offline claims must preserve a local append-only chain and later bind to server checkpoints. Long unanchored intervals may have a lower assurance ceiling, but they still count when the accounting source is certified and internally consistent.

### 2. Global leaderboards permit both Standard and Hardened

The public global leaderboard includes accepted Standard and Hardened claims. Requiring Hardened for the main leaderboard would unfairly exclude legitimate local agents and platforms that cannot expose equivalent hardware or provider attestations.

The interface must:

- display evidence status clearly;
- allow filtering to Hardened-only views;
- let private boards and organizations require a minimum evidence profile;
- never mix Imported analytics into active competition;
- avoid presenting Standard as fraudulent or second-class usage.

Hardened is a stronger evidence statement, not a separate game.

### 3. Launch uses strong practical uniqueness, not government-ID proofing

Launch enforces one active ranked identity per person as aggressively as practical without collecting government identity documents by default.

Controls include:

- provider-account uniqueness;
- linked-account graph analysis;
- device and recovery lineage;
- account maturity and abuse velocity;
- duplicate-payment or organization signals where lawfully available;
- progressive restrictions;
- human review and appeal;
- public profile separation from private integrity signals.

The product must not claim mathematically proven or universally verified human uniqueness. Public language should say that VibeMaxxing actively enforces one ranked identity per person and may restrict suspected duplicate identities.

Higher-assurance private boards may require stronger organization-managed verification, but the global product does not require government ID at launch.

### 4. Country leaderboards are postponed

Country boards are removed from the public-launch requirement and remain a post-launch feature.

Reasons:

- country affiliation is not yet semantically or temporally defined;
- privacy and cohort-suppression rules are incomplete;
- country switching and historical attribution are unresolved;
- country integrity would create disproportionate moderation complexity at launch.

The underlying schema may reserve future support, but public country ranking, country profile disclosure and country notifications must not be advertised as launch features.

### 5. SLM is not a launch dependency

The small language model detector remains a post-launch research track only.

Launch integrity relies on deterministic controls:

- source-bound evidence;
- accounting profiles;
- claim continuity;
- replay prevention;
- device lineage;
- certification;
- rate and resource governance;
- moderation and appeal ledgers.

An SLM may later provide an advisory risk score only after a reproducible bakeoff proves useful lift over deterministic baselines under explicit false-positive limits. It may not alter token totals, automatically ban users, or become required for launch.

### 6. Full social product remains the public-launch target

The public launch must include the complete core social vision:

- global, friends, private-board, organization, hacker-house and community leaderboards;
- daily, weekly, monthly, seasonal, yearly and lifetime periods;
- friend requests, rivals, overtakes and rank movement;
- source-bound active presence;
- groups and boards;
- notifications;
- moderation, restrictions and appeals;
- public profiles with privacy-safe evidence disclosure;
- Token Burn and Estimated Cash Burn.

Country boards are the sole explicit exception and are postponed.

“Everything at launch” does not mean every feature ships with weak contracts. Public launch remains blocked until each included system has implementation and executable evidence.

### 7. VibeProof v1 may be rewritten before implementation

The existing planning schema has no compatibility obligation because no production protocol has shipped. Breaking corrections are preferred over preserving flawed draft fields.

VibeProof v1 should therefore be rewritten now at planning level to close:

- evidence/appraisal separation;
- accounting-profile binding;
- COSE exact-byte profile;
- batch and replay semantics;
- offline continuity and checkpoints;
- device rotation and lineage;
- numeric limits;
- source provenance;
- removal of open-ended extensions.

## Consequences for launch architecture

1. Local agents and local models are first-class competitive sources.
2. Hardened cannot depend exclusively on cloud-provider receipts or hardware attestation.
3. Certified local adapters need deterministic source-specific accounting and conformance fixtures.
4. Offline synchronization must support bounded delayed submission without treating connectivity as authenticity.
5. The global leaderboard needs evidence labels and Hardened-only filters, not a Hardened-only admission rule.
6. Ranked identity enforcement must be strong and appealable while privacy-preserving.
7. Country work moves behind the launch gate rather than blocking it.
8. SLM research moves behind deterministic launch integrity.
9. The full social system remains in launch scope and must be planned as typed, privacy-safe state machines.

## Planning status

These decisions close the seven user-policy questions in `CONSOLIDATED_AUDIT_2026-07-23.md`.

P-1140A should apply them across the decision register, status, task catalog, launch scope, threat model, integrity model, protocol, ranking and social contracts. P-1104 remains blocked until the reopened planning program is complete and implementation is explicitly authorized.
