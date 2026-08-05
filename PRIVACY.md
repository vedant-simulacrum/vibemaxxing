# VibeMaxxing Privacy Notice

Last updated: 2026-08-06

**This notice has not been reviewed by a lawyer.** It was written by the controller against primary sources. Counsel review is a release gate that is not satisfied, recorded as D-109 and in `docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md`. Nothing here is legal advice, and the service it describes does not yet exist: no server is provisioned, no account has been created, and no personal data has been collected.

This is the notice required by Articles 13 and 14 of Regulation (EU) 2016/679. The complete internal record it derives from is `docs/privacy/DATA_MAP.md`, which is also the controller's Article 30 record of processing activities. Where the two differ, the data map is correct and this notice is the defect.

## The short version, before the detail

VibeMaxxing is a public leaderboard of how many language-model tokens you burn. If you sign up and connect an agent, **your handle and your token totals become visible to anyone on the internet.** That is the product, not a side effect.

Your prompts, your code, your file paths, your project names and your transcripts never leave your machine. That guarantee is absolute and is enforced by a fixed outbound schema. It is a guarantee about *content*. It is not a guarantee about *metadata*: your token totals and your presence state reveal when you work, how much you work, and roughly at what scale, and this notice says so out loud because the project has recorded that exposure internally and it would be worse to omit it.

Everything is consent-based. You can refuse any part of it, withdraw at any time, and have your data erased.

## Who is responsible

The controller is the repository owner, personally. There is no company, no legal entity and no engaged data protection officer.

| | |
|---|---|
| Controller | `[CONTROLLER LEGAL NAME]` |
| Postal address | `[CONTROLLER POSTAL ADDRESS]` |
| Contact for anything in this notice | `vedant@simulacrum.world` |
| Supervisory authority of establishment | `[SUPERVISORY AUTHORITY]` |

The three bracketed fields are not filled in. They are a publication gate under D-109: this notice cannot be published as it stands, and it is committed in this state so the gap is visible rather than pending in a draft nobody can see.

A data protection officer has not been appointed. The controller's assessment is that Article 37(1) does not require one. An Article 27 representative in the Union is not required, because the controller is established in the Union and Article 3(1) applies directly. A United Kingdom representative would be required before accepting participants in the United Kingdom, and has not been appointed.

## What is collected, why, and on what legal basis

### On your machine, and staying there

The VibeMaxxing daemon reads the local logs and databases that your agent CLI writes: Claude Code, and other supported tools. It reads them to count tokens.

**None of that content is ever transmitted.** Not the prompts, not the responses, not the transcripts, not the code, not the diffs, not the tool arguments or results, not the filenames, not the paths, not the project or repository names. Not a hash of any of them, and not an embedding, summary or classification derived from any of them. `docs/privacy/PRIVACY_CONTRACT.md` states this as an absolute boundary, and the process that can read your source content has no network access at all.

Where the daemon reads Claude Code's telemetry channel, that channel attaches your provider email, three stable provider-account identifiers and an organization identifier to every datapoint. **All five are destroyed inside the receiver on your own machine**, before anything is aggregated, and none is written to disk, to a log, to a crash report or to a diagnostic capture. A datapoint they cannot be removed from is thrown away whole. D-099 makes that a requirement rather than a setting, and no configuration option can turn it off.

The daemon also keeps a local ledger of everything it did send, so you can check. Its default retention is 90 days and you control it.

Reading files your agent CLI wrote is access to information stored on your terminal equipment, which Article 5(3) of the ePrivacy Directive covers independently of the GDPR. **We ask for that consent separately.** It is per source: each agent CLI is separately permitted, separately refusable, and separately revocable, and refusing one does not disable the rest of the product. We do not rely on the "strictly necessary" exemption, because reading your logs is necessary to rank you, not to deliver a service you could not otherwise have.

### What crosses to the server

Only a fixed-schema aggregate claim, enumerated field by field in `packages/schemas/egress-allowlist-v1.json`. In plain terms: token counts, a coarse time interval, which registered agent and model produced them, cryptographic digests identifying the software that observed them, a device signature, and sequence numbers that let the server detect replay. There is no free-text field, no generic metadata map and no extension channel, so there is nowhere for anything else to hide.

Alongside that, and only if you create an account:

- your handle;
- an identifier for your GitHub or X account, and the date that account was created;
- your devices and their public signing keys;
- friend, rival and block relationships you create, and boards you join;
- your presence state, while you are working;
- your notification preferences.

`docs/privacy/DATA_MAP.md` lists every one of these with its retention period and recipients.

### The legal bases

**Consent, Article 6(1)(a), for everything you can see.** Account creation, provider linking, usage collection, publication of your handle and score, social features, presence and notifications. We do not rely on "necessary for a contract" under Article 6(1)(b) for any of it. EDPB Guidelines 2/2019 say plainly that engagement metrics are not objectively necessary to perform a contract, and a leaderboard is an engagement metric. Claiming otherwise would be using a legal basis we are not entitled to.

**Legitimate interests, Article 6(1)(f), narrowly.** Only for network and information security and for fraud and abuse prevention: rate limiting, replay and Sybil detection, the security audit log, and transport-level handling of your network address. Recital 49 names these as legitimate interests directly. You can object under Article 21 and we will assess the objection on its merits.

**Legal obligation, Article 6(1)(c).** Only for records the law requires: the record of processing, breach records, and responses to a supervisory authority.

**We will not swap bases.** If you withdraw consent, we do not keep processing the same data by re-labelling it a legitimate interest. That is prohibited and we are not going to do it.

### Where your provider data comes from (Article 14(2)(f))

Two pieces of data do not come from you. When you link an account, **GitHub** or **X** tells us a stable identifier for your account there and the date that account was created. We use the identifier to know it is the same account each time, and the creation date because an account must be at least 90 days old before it can support a ranked identity — a minimum age is a weak Sybil control and nothing more. We never receive your provider password, and we never see your repositories.

## What becomes public

The global leaderboard is public by default and is readable by anyone, with no account, worldwide. It shows your handle, your Token Burn at period granularity, your rank, an Estimated Cash Burn figure that is always labelled as an estimate and is never an invoice, and the evidence profile the server awarded you.

Friend boards, private boards, organization, hacker-house and community boards require the viewer to be authorized. Presence is shown only to viewers you have authorized, and `private` is an independent setting that withdraws it from everyone.

**A token count attached to your handle is personal data about you.** We are not going to pretend otherwise on the basis that it is "just a number". The public-by-default choice was made deliberately, with the legal analysis in front of the owner, and `docs/decisions/ADR-021-PUBLIC_BY_DEFAULT_RISK_ACCEPTANCE.md` records that analysis, the risk, and the acceptance without softening any of it. If you would rather not be in a public dataset of personal spend, do not connect an account; that refusal costs you nothing else.

## What your numbers reveal, stated plainly

The content boundary holds. The metadata is a different matter and the project has recorded two exposures internally, in `docs/decisions/ADR-019-ACCEPTED_RESIDUAL_RISKS.md`, that it is shipping without fixing.

**Presence can be used to watch you.** Presence updates every 30 seconds, goes idle after 90 seconds and offline after 300. Anyone you have authorized — a friend, a rival, a co-member of a board — can read it as often as they like, for as long as they like. Sampled over a month that is a minute-resolution record of your working hours, your sleep, your timezone, your weekends and your absences. Nothing in the product limits it, nothing tells you it is happening, and no rule is broken while it happens. Blocks are directional and take effect immediately, which helps after you know. Setting presence to private withdraws it from everyone.

**Your token totals leak your working pattern.** They are the same timeline derived from a different field, plus the approximate scale of what you are doing. They are also, in principle, a low-bandwidth channel: a modified collector could encode information in the counts it reports, and public score deltas are readable by anyone. Both facts are consequences of publishing how much you spend, and there is no version of this product where they are not true.

We will never tell you that presence is safe from monitoring, or that publishing aggregates leaks nothing. Both statements are false and we have written down that they are unavailable to us.

## How long we keep things

Real numbers, not "as long as necessary". The complete table is in `docs/privacy/DATA_MAP.md`.

| | |
|---|---|
| Your account, handle and profile | Life of the account. Erased within 30 days of a completed erasure request |
| A handle you stopped using | 90 days of redirect, then gone |
| Provider account identifier | Deleted immediately when you unlink, or on account erasure |
| Sign-in session | Access handle 15 minutes; refresh handle 30 days; a browser session must reauthenticate after 90 days |
| Sign-in attempt records | The transaction expires within 15 minutes; the row is deleted within 24 hours |
| Accepted claims and your standings | Life of your ranked identity; then subject to erasure, below |
| Minute-level score projections | 400 days. Never published at that granularity |
| Presence | Current state only. The record expires 300 seconds after your last activity. **No presence history is kept** |
| Notifications | 90 days |
| Friend requests you never answered | 30 days |
| Security and abuse audit records | 365 days |
| Moderation cases and appeals | 365 days after they close |
| Server logs containing a network address | 30 days |
| An export bundle you requested | Purged 7 days after it is ready |
| Backups and point-in-time recovery | 35 days. This is the outer bound on how long anything can survive erasure |
| The local ledger on your machine | 90 days by default, and you control it |

## Where your data is

In the European Union. Every persistent store holding personal data — the database, its replicas, its backups, its point-in-time recovery archives, and the object storage holding export bundles — is located there under `docs/decisions/ADR-017-HOSTING_REGION_AND_RESIDENCY.md`. Only release artifacts and static web assets, which contain no personal data, are served from a global content delivery network with an origin in the Union.

**No personal data is transferred outside the European Union.** Adopting any vendor that would change that requires amending that decision record first, in public, in this repository.

The hosting provider is not yet chosen. The region and residency commitment is decided; the procurement is not, and naming the specific processors is part of the publication gate under D-109, because you are entitled under Article 15(1)(c) to be told who they are.

## Automated decisions

Three things happen to you automatically.

1. A server-side verifier decides what evidence profile your claims receive and whether they are competitively eligible. Your client never chooses this.
2. That profile, combined with a trust state, produces a confidence weight that is applied to your raw token count to compute the rank shown publicly. `docs/decisions/ADR-020-CONFIDENCE_WEIGHTED_RANKING.md` owns the function. Your raw count is stored unchanged; the weight applies at ranking time and never rewrites an accepted claim.
3. Deterministic integrity rules can quarantine a claim or sanction a ranked identity.

**None of this is verification, and we are not going to let it read like verification.** No provider — not Anthropic, not OpenAI, not anyone — offers a way for an individual account to prove its own usage to a third party. Every usage endpoint that exists requires an organization administrator key. So every number attributed to you here is **self-reported by software running on your own machine**, and the evidence profile is our assessment of how good that self-report is, not a confirmation from your provider that it happened. D-100 records that as a permanent structural constraint on the product.

We do not claim Article 22 is inapplicable to the third of these. A sanction that removes your competitive eligibility can significantly affect you, and it would be self-serving for us to decide otherwise. So the Article 22(3) safeguards apply by design: **a first sanction is reversible**, the public leaderboard shows no mark against you, you receive a notice in your inbox stating what happened and how to appeal, and a human — the maintainer — decides the appeal. If the appeal succeeds the ranking effect is fully reversed.

Statistical and machine-learning detection stays on your own machine, is advisory only, is never authoritative, and never acts against you on its own.

## Your rights

You can exercise any of these by writing to `vedant@simulacrum.world`. We will respond within one month, as Article 12(3) requires, and will tell you if we need the two-month extension it permits and why. **We will not ignore you.** Ignoring a request is the single behaviour most likely to turn a minor compliance problem into an enforcement action, and it is written down here so that it stays true.

- **Access** (Article 15) — a copy of everything we hold about you, including the derived figures.
- **Rectification** (Article 16) — correction of anything wrong.
- **Erasure** (Article 17) — see below; it is not hedged.
- **Restriction** (Article 18) — processing paused while a dispute is resolved.
- **Portability** (Article 20) — see below for exactly what is and is not portable.
- **Objection** (Article 21) — to the security and abuse-prevention processing that runs on legitimate interests.
- **Withdraw consent** (Article 7(3)) — at any time, as easily as you gave it. Withdrawal does not affect processing that already happened lawfully.
- **Not be subject to a solely automated decision** (Article 22) — the appeal route above.
- **Complain to a supervisory authority** (Article 77) — to `[SUPERVISORY AUTHORITY]`, or to the authority where you live, where you work, or where you think the problem happened. You do not have to come to us first, and you do not need our permission.

Consent is genuinely refusable. Article 7(4) and Recital 43 mean it is not real consent if refusing costs you the service, so: refusing the ePrivacy consent for a particular agent CLI disables collection from that CLI and nothing else. Refusing to be on the public leaderboard means not creating an account, and creating an account is not required for anything else, because there is nothing else.

### Erasure, without the hedging

If you withdraw consent, Article 17(1)(b) applies and there is no other basis under which we could keep publishing you — so the data goes.

**What that means concretely.** Your account, your ranked identity and that identity's historical ranking entries are removed, so that you are neither visible nor reconstructible in any published standing. Not anonymised in place while the row stays. Removed.

- The live surface: within 30 days of the request completing.
- Backups and point-in-time recovery: within 35 days, which is our backup retention. A restore reapplies deletion records before serving traffic.
- There is a 7-day cooling-off period first, during which you can cancel. It exists so that an account is not destroyed by a misclick.

**Article 17(2) — telling other people.** Because we made the data public, we have to take reasonable steps to inform others processing it. What we will actually do: remove it from the live surface, mark pages so archives do not retain them, and submit removal requests to the search engines that offer a removal interface. What we cannot do: reach a person who copied a leaderboard screenshot, or an archive service with no removal process. We are telling you that limit rather than implying a completeness we cannot deliver.

**We are not going to claim a Article 17(3) exemption.** The one that would be reached for is freedom of expression. That argument was tested on very similar facts — republishing lawfully obtained personal financial data — in *Satakunnan Markkinapörssi Oy and Satamedia Oy v Finland* before the Grand Chamber of the European Court of Human Rights, application 931/13, decided 27 June 2017, and the publisher lost fifteen votes to two. We do not think a leaderboard of token spend is in a stronger position than a newspaper was.

One honest limitation. Our own binding rules say accepted claims and historical facts are immutable and that corrections are append-only, and erasure of historical ranking entries pulls against that. The outcome above is decided and is not going to be quietly weakened. The internal mechanism that reconciles it with immutable ranking generations is still being specified, and `docs/privacy/DATA_MAP.md` says so in the same words rather than presenting a resolved design.

**Local deletion is separate and we will not overstate it.** We can delete what is on our servers. We cannot guarantee erasure of data on a device that is offline, unreachable or no longer yours. Deleting everything is a coordinated flow across your devices that reports each device's outcome honestly, including "we could not reach this one". No screen will ever tell you all local data is erased while a device has not confirmed it.

### Portability, and what is not portable

Article 20 applies because your basis is consent.

**You can take with you:** your raw token counts and their time intervals, your account and handle, your linked provider identifiers, your device registrations, the social connections you made, your board memberships, and your local audit ledger. Structured, machine-readable, on request.

**You cannot take, because we made it rather than you:** your computed rank, your percentile, generation and snapshot identifiers, Estimated Cash Burn, the confidence weight applied to you, and the verifier's appraisal detail. WP242 rev.01 draws that line between observed and derived data. You can still *see* all of it under your Article 15 right of access — it is just not an Article 20 output.

We do not offer direct transmission to another controller under Article 20(2), because there is no other controller running this. Article 20(2) requires it where technically feasible, and it is not.

## Children

**You must be at least 16 to use VibeMaxxing.** This is a single Union-wide floor and it is deliberately set at the ceiling of the range Article 8(1) permits, rather than at each member state's own digital-consent age — which varies from 13 to 16 across the Union. A uniform 16 means the product never has to verify a parent's consent, never has to determine which member state's age applies to you, and never has to hold the extra personal data that either of those would require. It is the more restrictive choice and it is the one that collects less.

If we learn that an account belongs to someone under 16, we close it and erase the data.

## Security

The technical design is public. `docs/security/THREAT_MODEL.md` and `docs/privacy/PRIVACY_CONTRACT.md` describe what is defended and what is not, and they are readable by you, not summarised for you.

If personal data is breached, we notify the supervisory authority within 72 hours under Article 33 where the threshold is met, and we notify you directly under Article 34 where the risk to you is high. We keep breach records for 5 years. Separately, breach notification law in all fifty United States states applies to us with no size threshold at all — California Civil Code section 1798.82(a) binds "an individual or business" — so a breach affecting a participant there is notifiable regardless of how small this project is.

We are not subject to the California Consumer Privacy Act, which requires a for-profit business meeting a revenue or volume threshold that this project does not meet. CalOPPA, at California Business and Professions Code section 22575(a), has no threshold, applies to any operator of a commercial website collecting personal information from California residents, and requires a conspicuously posted privacy policy that discloses the categories collected and the process for reviewing changes. This document is that policy.

## Changes to this notice

Material changes are announced in your server inbox before they take effect, and the full history of every change to this file is in the repository's git history, which is public. A change that widens what is collected or published requires fresh consent; it does not take effect by silence.

## Things this notice does not do

- It does not constitute legal advice, and no lawyer has read it.
- It does not describe a running system. Nothing is deployed and no data has been collected.
- It does not claim compliance. It states what the controller intends and what the controller has not done, and `docs/privacy/DATA_MAP.md` and `docs/decisions/ADR-021-PUBLIC_BY_DEFAULT_RISK_ACCEPTANCE.md` record the analysis and the gaps behind it.
