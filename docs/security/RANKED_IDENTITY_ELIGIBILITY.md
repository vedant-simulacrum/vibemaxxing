# Ranked Identity Eligibility

Updated: 2026-07-20
Status: normative planning contract

## Product rule

VibeMaxxing permits one active ranked identity per human. A person may use private local analytics without verification, but must establish an eligible ranked identity before appearing on any leaderboard or affecting competitive totals.

This is a product and abuse-policy rule, not a claim that OAuth proves legal identity or mathematically guarantees human uniqueness. Google, GitHub, and X authentication prove control of provider accounts. VibeMaxxing combines linked provider subjects, account history, recovery continuity, device relationships, and abuse review to enforce the rule without government identity documents or facial biometrics.

## Verification boundary

Launch verification uses supported OAuth providers only:

- Google;
- GitHub;
- X/Twitter, subject to current provider availability and protocol constraints.

No legal name, government document, facial scan, biometric template, address, or exact date of birth is required by default. Public profiles remain pseudonymous. Provider subject identifiers are private account-control data and are never public leaderboard fields.

A ranked identity becomes eligible only after:

1. at least one supported provider identity is successfully linked;
2. the provider subject is not bound to another active ranked identity;
3. the account accepts the one-human-one-ranking rule;
4. required account, session, and abuse checks pass.

Additional linked providers strengthen recovery and duplicate detection but do not create additional ranked identities.

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
