# Ranked Identity Eligibility

Updated: 2026-07-20
Status: normative planning contract

## Product rule

VibeMaxxing permits one active ranked identity per human. A person may use private local analytics without verification, but must establish an eligible ranked identity before appearing on any leaderboard or affecting competitive totals. At launch, GitHub and X are the supported OAuth providers; Google is deferred until its contracts are added coherently.

This is a product and abuse-policy rule, not a claim that OAuth proves legal identity or mathematically guarantees human uniqueness. GitHub and X authentication prove control of provider accounts at launch. VibeMaxxing combines linked provider subjects, account history, recovery continuity, device relationships, and abuse review to enforce the rule without government identity documents or facial biometrics.

## Verification boundary

Launch verification uses supported OAuth providers only:

- GitHub;
- X/Twitter, subject to current provider availability and protocol constraints.

No legal name, government document, facial scan, biometric template, address, or exact date of birth is required by default. Public profiles remain pseudonymous. Provider subject identifiers are private account-control data and are never public leaderboard fields.

A ranked identity becomes eligible only after:

1. at least one supported provider identity is successfully linked;
2. the provider subject is not bound to another active ranked identity;
3. the account accepts the one-human-one-ranking rule;
4. required account, session, and abuse checks pass.

Additional linked providers strengthen recovery and duplicate detection but do not create additional ranked identities.

Eligibility is not admission. During the private beta the account must also hold an invite redemption before it may reach any surface other than its own data-subject-rights routes, and `docs/security/PRIVATE_BETA_ADMISSION.md` owns that mechanism, the order the age floor of D-103 and the 90-day provider-account gate of D-081 are evaluated in relative to it, and what each refusal discloses. An invite is admission control and is not evidence about the person: it proves that the owner chose to admit the account and nothing else, so it neither establishes unique humanity nor substitutes for the duplicate handling below.

## Unverified accounts

Unverified users may:

- use private analytics;
- browse public surfaces;
- create or maintain a private profile;
- join boards where board policy allows it;
- participate in non-ranking board and social surfaces.

Unverified users must not:

- appear in any leaderboard;
- affect global, country, organization, community, friend, private-board, seasonal, yearly, or lifetime competitive totals;
- trigger overtakes or ranked-rival events;
- receive a public rank;
- vote or act in ways whose weight depends on ranked identity.

Every social surface must visibly distinguish unranked participation where confusion is possible.

## Duplicate and related-account handling

When the system determines that two active ranked accounts are controlled by the same person:

1. competitive activity on the newer or less-established account is restricted;
2. duplicated competitive claims are excluded or quarantined without being silently transferred;
3. the user is offered recovery, account consolidation, or appeal;
4. one canonical ranked identity remains after resolution;
5. the duplicate account may remain as an unranked private-analytics account or be deleted at the user's choice;
6. no public cheating label is applied solely because a duplicate relationship was detected.

A single shared IP address, household, workplace, school, device, or network is never sufficient on its own to merge or remove accounts. High-impact outcomes require multiple corroborating signals and human review.

## The three aggregates behind those rules

The three lists above are outcomes. Three aggregates produce them, and each has one lifecycle, one persistence owner, one revision model and one transaction boundary. D-381 and D-382 record the choices.

| Aggregate | Lifecycle | Persistence | Record |
|---|---|---|---|
| Ranked identity | `ranked-identity-eligibility` | `ranked_identities` | `packages/schemas/ranked-identity-v1.schema.json` |
| Integrity investigation | `identity-investigation` | `identity_investigations` | the same file |
| Account consolidation | `account-consolidation` | `consolidation_cases`, `consolidation_contributions` | `packages/schemas/consolidation-plan-v1.schema.json` |

`identity_events` is the append-only ledger all three write to, inside the transaction that performed the act rather than by a follower reading a queue, because it is what an appeal reads.

### What the engine enforces, and what it does not

D-054 permits one active resolved ranked identity per person. A partial unique index enforces one non-retired ranked identity per account, which is the weaker half. The stronger half — that two accounts do not belong to one person — is not a constraint and is not claimed to be. It is reached through an investigation and a consolidation, both appealable, and neither asserts a verified human. Under D-100 no provider offers an individual-account attestation path, so `resolution_basis` records which appealable server process resolved the identity and never a provider confirming one.

### Investigation

The states are `opened`, `gathering`, `awaiting-participant`, `concluded-no-action`, `concluded-restricted`, `concluded-consolidation`, `withdrawn` and `expired`. They are `integrity-private`: the participant reads the effect on their standing through the `ranked-identity-eligibility` machine, whose investigation states the binding table already marks internal, and is never told a case is open, because that is itself an anti-cheat signal.

Concluding a case never reverses anything. A reversal is an `appeals` outcome that moves the ranked identity, which is why the machine has no `reversed` state and why every conclusion is terminal. There is no statistical trigger: D-053 keeps statistical and small-language-model detection local, advisory and post-launch, so nothing statistical opens a server-side case. A partial unique index permits one open case per identity.

Expiry is `expires_at`, after which an unanswered case moves to `expired` rather than staying open indefinitely. The error path is `withdrawn`, for a case opened in error.

### Consolidation

Rule 2 above — duplicated claims are excluded or quarantined and never silently transferred — is the constraint this aggregate exists to make executable. `consolidation_contributions` holds one row per considered claim with its original period attribution, its raw quantity and a disposition of `absorbed`, `excluded-duplicate`, `excluded-imported` or `excluded-quarantined`. An excluded claim is recorded with why rather than omitted, so the case explains what it dropped.

No summed total exists anywhere in the path. `packages/schemas/consolidation-plan-v1.schema.json` has no combined-total field and `scripts/repository/validate_planning_artifacts.py` fails if one is added, which is D-070's no-stored-total rule expressed as a check rather than as a convention. A duplicate domain commitment is unique within a case, so an overlapping contribution counts once under D-269.

The transaction boundary is `consolidation-identity-and-contributions`: retiring the absorbed identity, writing every contribution, establishing the `erasure_domain_links` edge and appending the identity events commit together, because a partial consolidation leaves two live identities that each believe they own one history.

`applied` is not terminal. A successful appeal reaches `reversed`, which appends inverse contributions under D-263 rather than editing an accepted claim, and does not un-retire the absorbed identity: its account may have been deleted in the interval, and resurrecting the identifier is what D-085 forbids.

#### What the plan must cover, and which identity survives

A consolidation touches every domain a duplicate account owns, and the plan record covered three of them — identities, claims and periods. `docs/security/AUTHENTICATION_AND_RECOVERY.md` requires a merge to define ownership of usernames, devices, claims, boards, friendships, moderation state and deletion requests, so a case could apply while saying nothing about the absorbed account's devices, blocks, board ownership, open moderation case, running export or pending deletion. `packages/schemas/consolidation-plan-v1.schema.json` now requires a disposition for all eight — `identities`, `devices`, `claims`, `social`, `boards`, `moderation`, `exports`, `deletions` — with `additionalProperties: false`, so the coverage cannot be satisfied by an empty object and a ninth domain has to be added to the schema rather than invented in a plan.

Each disposition is `transferred`, `retained`, `excluded` or `recomputed`, with a count of affected rows and the rule that produced it. There is deliberately no `not-applicable` value: a domain with nothing in it is `retained` with a count of zero, which is a statement, whereas a value meaning "we did not look" would let every domain be covered by declining to answer. The counts are counts of rows and never quantities; no field anywhere in the path holds a figure derived from two accounts' token burn.

D-564 fixes which side survives: **the older ranked identity survives and the newer is retired, without summation.** The plan records both identities' creation instants so that rule is checkable rather than a sentence in a register. JSON Schema cannot compare two of its own fields, so `scripts/repository/validate_oauth_identity_contract.py` compares them on every committed plan and refuses one where the newer identity survived; a fixture written to violate the ordering is checked to actually violate it, so the rule is exercised in both directions.

#### The participant's route

The machine declares `consolidation-confirm` with actor `user`, `web-session` authentication and recent authentication required, and `packages/schemas/openapi-v1.yaml` declared no consolidation operation at all. The participant was required by the lifecycle to perform a transition the contract gave them no way to perform, so a case could leave `awaiting-confirmation` only by expiring.

`getConsolidationPlan` is the read half and `confirmConsolidation` is the write half. Neither publishes a lifecycle value, which is why `account-consolidation` still records no API state enum: a value like `applying` is an operational fact, and the participant is being asked about the plan rather than about the case. The plan view carries a `plan_digest`, and the confirmation names it, so a plan cannot be substituted between being read and being confirmed. Confirmation moves the case to `applying` and does nothing else; the surviving standing is recomputed from the contributions.

## Devices and account continuity

One ranked identity may use many registered devices. Each device retains its own key, daemon identity, sequence state, evidence lineage, and revocation state, while all accepted claims accrue to the same ranked account.

Multiple people may share a computer. Implementations must support separate authenticated sessions and device-user bindings. Shared hardware is a risk signal only when combined with stronger evidence; it is not proof of duplicate identity.

## Provider and account changes

A person may link multiple provider accounts to one VibeMaxxing account. Only one public provider identity needs to be displayed, and the user may keep all provider identities private.

A provider subject already linked to another ranked identity cannot be silently reassigned. The user must enter recovery, consolidation, or appeal.

A user may change handles, public profile fields, linked providers, and devices without creating a new ranked identity. Loss of access or a desired provider change is handled as identity-bound migration. Competitive history, moderation state, and audit continuity remain attached to the canonical account.

A person who leaves and later returns recovers the original ranked identity. Deletion does not create a right to reset ranking history, restrictions, or duplicate-prevention state. Any retained anti-reenrollment record must be minimal, access-controlled, disclosed, and legally reviewed before launch.

## Organizations and boards

Organizations, employers, board owners, and community administrators receive only eligibility and membership state required for their role. They do not receive legal names, provider credentials, private provider subjects, duplicate-detection signals, or internal review evidence.

The policy launches globally wherever the product and selected OAuth providers are available. Country does not change the verification method. Regional legal, provider, or safety constraints may require availability restrictions without changing the public pseudonymity promise.

## Decisions deferred to implementation evidence

The following remain policy-tunable rather than user-facing identity claims:

- exact related-account signals and thresholds;
- cooling-off periods during consolidation or recovery;
- which duplicate account is canonical when history is ambiguous;
- retention duration for minimal anti-reenrollment records;
- provider-specific assurance weighting;
- transferable identity credentials;
- exact user-safe reason codes and appeal service levels.

These controls must minimize false positives, provide human appeal for high-impact restrictions, and never present OAuth account control as government-grade identity proof.
