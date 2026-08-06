# Data Map and Record of Processing Activities

Status: normative planning contract. **Not reviewed by counsel. Counsel review is an unmet release gate.**
Updated: 2026-08-06
Decisions: D-101, D-102, D-103, D-104, D-105, D-106, D-107, D-108, D-109

This document is the single owner of what personal data VibeMaxxing processes, why, on which lawful basis, for how long, and who receives it. `PRIVACY.md` is the participant-facing notice derived from this map and may not state anything this map does not.

## This is the Article 30 record

This document is also the controller's record of processing activities under Article 30(1) of Regulation (EU) 2016/679. It is not a supplementary document that a record will later be built from; it is the record.

**The Article 30(5) small-organisation exemption does not apply**, and the project does not rely on it. Article 30(5) removes the obligation for an organisation with fewer than 250 employees *unless* the processing is likely to result in a risk to the rights and freedoms of data subjects, *or* the processing is not occasional, *or* the processing includes special categories or criminal-conviction data. The Article 29 Working Party position paper of 19 April 2018 confirms that the three carve-outs are alternative rather than cumulative: any one of them restores the obligation. Continuous collection of agent usage from an always-on daemon under ADR-010 is by definition not occasional, and D-102 records the risk assessment. Two carve-outs are met. The record is mandatory.

The record is maintained in English, in version control, with the register of changes visible in the repository history, and is producible to a supervisory authority on request under Article 30(4).

## Controller

| Field | Value |
|---|---|
| Controller | The repository owner, personally. There is no legal entity, no company, and no engaged counsel. |
| Legal name and postal address | `[CONTROLLER LEGAL NAME]`, `[CONTROLLER POSTAL ADDRESS]`. These are unfilled and are a publication gate, recorded in D-109. |
| Contact | `vedant@simulacrum.world` |
| Data protection officer | None. Article 37(1) does not require one: the controller is not a public authority, the core activity is not regular and systematic monitoring of data subjects on a large scale within the meaning of Article 37(1)(b) at the scale targeted, and no Article 9 or Article 10 data is processed. This is the controller's own assessment and is one of the items counsel review is expected to test. |
| Article 27 representative in the Union | Not required and not appointed. The controller is established in the Union, so Article 3(1) applies and Article 27 is definitionally inapplicable to it. D-106 records this. |
| Representative in the United Kingdom | Required if participants in the United Kingdom are accepted, under Article 27 of the UK GDPR. Not appointed. D-106 records this as an unmet gate on accepting UK participants. |
| Supervisory authority | The supervisory authority of the member state of the controller's establishment, named in `PRIVACY.md` at publication. The right to complain under Article 77 is exercisable at the authority of the participant's habitual residence, place of work, or place of the alleged infringement, and is not restricted to the controller's authority. |

## Lawful bases used, and the two that are not used

Three bases are used and they are used for disjoint purposes. A single processing operation has exactly one basis, and a basis is never swapped after the fact.

**Article 6(1)(a) — consent.** The basis for everything the participant sees and everything that reaches a leaderboard: account creation, provider linking, usage collection, claim submission, publication of a handle and a score, social relationships, presence, and notifications. D-101 records why. Consent is separately refusable for the local daemon's access to terminal equipment under D-104 and the ePrivacy requirement below.

**Article 6(1)(f) — legitimate interests.** Used only for network and information security and for fraud and abuse prevention, which Recital 49 names directly as a legitimate interest: transport-layer processing of network addresses, rate limiting, replay and Sybil detection, and the security audit log. It is not used for anything that produces a public output, and it is never used as a fallback for a purpose whose consent has been withdrawn.

**Article 6(1)(c) — legal obligation.** Used only for records the law requires the controller to keep or produce: the Article 30 record itself, personal-data-breach records under Article 33(5), and responses to a supervisory authority.

**Article 6(1)(b) — contract — is not used and is not available.** EDPB Guidelines 2/2019 on the processing of personal data under Article 6(1)(b) in the context of online services state that processing is necessary for performance of a contract only where it is objectively necessary for the service the data subject requested, and specifically that improvement, personalisation and engagement-driving metrics do not meet that test. A leaderboard is an engagement metric. Characterising publication as contractual necessity because the terms describe a leaderboard would be exactly the reasoning those guidelines reject.

**Article 9 does not apply.** The Article 9(1) list of special categories is exhaustive and financial information is absent from it. Aggregate spend on language-model tokens is not special-category data. That conclusion narrows the compliance obligation and does not lower the risk assessment: WP248 rev.01 instances financial data under its fourth criterion, and D-102 records that the processing meets five of the nine WP248 criteria where two are sufficient.

## Aggregate token counts are personal data

Recorded here because the whole map depends on it and because the opposite conclusion is a tempting one.

A token count attached to a GitHub or X handle is personal data within Article 4(1). The handle identifies a natural person directly in the ordinary case and indirectly in every case, and Recital 30 treats online identifiers as identifying. Case C-434/16 *Nowak* establishes that "any information" is a wide formulation covering objective and subjective information of any kind provided it relates to an identified or identifiable person, which a per-person spend figure does.

Case C-413/23 P *EDPS v SRB*, decided 4 September 2025, does not change this for the controller. Paragraph 76 of that judgment holds that pseudonymised data remain personal data for the party that holds the means of re-identification. The controller holds the mapping from handle to count; it is the mapping. The relative-identifiability reasoning in that case helps a recipient who lacks the key. The controller is never that recipient.

## Categories of processing

Every row is a processing activity in the Article 30(1) sense. "Crosses device boundary" states whether the category ever leaves the participant's machine; the absolute rule in `docs/privacy/PRIVACY_CONTRACT.md` is that only fixed-schema aggregate accounting and integrity claims do.

### Account and identity

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Account record and lifecycle state (`accounts`) | Server, on sign-up | Server-side only | 6(1)(a) consent | Life of the account; erased within 30 days of a completed erasure request | Hosting processor |
| Normalized handle and confusable skeleton (`account_handles`) | Server, from the participant's chosen handle | Server-side only | 6(1)(a) consent | Life of the account | Hosting processor; **public** |
| Superseded handle redirect | Server, on rename | Server-side only | 6(1)(a) consent | 90 days from rename, per `old_handle_redirect_days` in `packages/schemas/policy-defaults-v1.json` | Hosting processor; **public** |
| Provider subject identifier (`linked_identities.provider_subject`) | Received from GitHub or X during the authorization exchange | Received server-side; never sent to the device | 6(1)(a) consent | Until unlink or account erasure; deleted immediately on unlink | Hosting processor. Never public, never shared with board administrators |
| Provider-reported account creation timestamp | Received from GitHub or X during the authorization exchange, under D-081 | Server-side only | 6(1)(a) consent | Until unlink or account erasure | Hosting processor. Never public |
| Profile visibility setting (`profiles`) | Server, from the participant | Server-side only | 6(1)(a) consent | Life of the account | Hosting processor |
| Private-beta invite redemption, binding the issuing owner to the admitted account (`invite_redemptions`) | Server, when the participant redeems the code the owner sent them | Server-side only | 6(1)(a) consent | Life of the account; deleted on account deletion and on erasure, in the same transaction that retires the code | Hosting processor. Never public, never shared with board administrators, and never disclosed to the invitee |
| Private-beta invite code record: issuing account, issue, expiry, redemption and retirement times, and a SHA-256 digest of the code (`invite_codes`) | Server, at issuance | Server-side only | 6(1)(a) consent | Indefinite. The row names no invitee, so an erasure leaves it in place; retaining it is what stops a spent 125-bit code from being issued a second time | Hosting processor |

Article 14 applies to the two provider-sourced rows because they are obtained from GitHub and X rather than from the participant. The Article 14(2)(f) source statement is in `PRIVACY.md` and names those two providers.

**The invite redemption is a social-graph edge held by the controller.** It records that the owner admitted this specific person, and it is the only place that edge is stored — no chain, no ancestry, and no depth beyond one, because participants cannot issue invites. It is processed on consent as part of account creation rather than on Article 6(1)(f), because the edge exists to admit the participant rather than to secure the service, and D-101 confines the legitimate-interests basis to security and fraud prevention. The issuer is not disclosed to the invitee on any surface. `docs/security/PRIVATE_BETA_ADMISSION.md` is the mechanism and D-284 records the disclosure decision.

### Authentication and session

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Access handle digest (`web_sessions`) | Server, at authentication | Handle is held by the client; only its SHA-256 digest is stored | 6(1)(a) consent | 15 minutes from issue, per ADR-015 | Hosting processor |
| Refresh handle digest and family state | Server, at authentication | As above | 6(1)(a) consent | 30 days from issue; browser families are capped at 90 days absolute, per ADR-015. Revoked and expired rows are purged 30 days after they leave `active` | Hosting processor |
| OAuth transaction state, `state` value digest, encrypted PKCE verifier (`oauth_transactions`) | Server, during the authorization exchange | Server-side only | 6(1)(a) consent | The transaction expires within 15 minutes; the row is deleted within 24 hours of reaching a terminal state | Hosting processor |
| Recovery codes, stored as digests (`recovery_codes`) | Server, at issue | Digest only | 6(1)(a) consent | Until consumed or account erasure | Hosting processor |
| Optional authenticator credentials (`optional_authenticators`) | Server, at enrolment | Public key only | 6(1)(a) consent | Until removed by the participant or account erasure | Hosting processor |
| Network address and user agent | Observed at the transport layer on every request | Not applicable | 6(1)(f) security, Recital 49 | Not stored in any account-linked table. Where a network address appears in operational logs it is retained 30 days, per `operational_telemetry_retention_days` | Hosting processor |

### Device and collection

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Raw agent CLI logs, transcripts, prompts, responses, code, file paths, project and repository names | The participant's own machine, by the collector | **Never.** This is class L0 in `docs/privacy/PRIVACY_CONTRACT.md` and the boundary forbids it absolutely | 6(1)(a) consent, plus separate ePrivacy Article 5(3) consent under D-104 | Shortest practical window on the device; excluded from backups; never uploaded | Nobody. It does not leave the machine |
| `user.email`, `user.id`, `user.account_id`, `user.account_uuid`, `organization.id` on OpenTelemetry datapoints | Emitted by the Claude Code CLI on the participant's machine into a loopback receiver the participant runs | **Never.** D-099 requires the receiver to strip all five from the decoded in-memory datapoint before it is admitted to the observation queue, and therefore before any aggregation, counter-delta state or grouping | 6(1)(a) consent and ePrivacy Article 5(3) consent for the read; no basis is needed for the retained form because none is retained | **Zero.** A stripped value is never written to disk, a log, a crash report or a diagnostic capture, and never keys any local structure or cache. A datapoint from which they cannot be removed is rejected whole | Nobody. They are destroyed at the receiver |
| Normalized local accounting facts (class L1) | The participant's machine | Never in this form | 6(1)(a) consent and ePrivacy Article 5(3) consent | Local, participant-configurable and participant-visible | Nobody |
| Local outbound audit ledger | The participant's machine | Never | 6(1)(a) consent | 90 days by default, participant-controlled, per `docs/privacy/PRIVACY_CONTRACT.md` | Nobody |
| Device registration, lineage, platform profile (`devices`) | Server, at enrolment | Enrolment data crosses; it contains no content | 6(1)(a) consent | Life of the device registration; 365 days after revocation as a security record, per `security_audit_retention_days` | Hosting processor. Device identifiers are never public |
| Device signing public keys (`device_keys`) | Server, at enrolment | Public key crosses | 6(1)(a) consent | As above | Hosting processor. Never public |
| Adapter installation and certification digests | Server, with a claim | Digests cross | 6(1)(a) consent | Life of the device registration | Hosting processor |

### Usage claims and scores

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Signed evidence claim: token counts, bounded interval, sequence, commitment heads, rule results (`claims`, `claim_payloads`) | Produced on the participant's machine, submitted to the server | **Yes.** This is the only content-bearing crossing and it is fixed-schema aggregate accounting under `packages/schemas/egress-allowlist-v1.json` | 6(1)(a) consent | Life of the ranked identity. On erasure, see the erasure section below | Hosting processor |
| Raw Token Burn total per claim | Derived on the device, submitted | Yes | 6(1)(a) consent | As above | Hosting processor. Not public. Under D-144 and D-217 the public figure is Credited Token Burn at period granularity; the raw figure appears on the participant's own surface and on surfaces they authorize |
| Minute-resolution score projection (`minute_scores`) | Derived server-side from accepted claims | Server-side only | 6(1)(a) consent | 400 days, then discarded. It is a projection and is rebuildable from accepted claims; it is never published at minute granularity | Hosting processor |
| Live period projection (`period_scores`) | Derived server-side | Server-side only | 6(1)(a) consent | Life of the ranked identity. Keyed on the account and deleted outright on erasure | Hosting processor |
| Sealed ranking generations, entries and snapshots (`ranking_projection_generations`, `ranking_entries`, `score_snapshots`) | Derived server-side | Server-side only | 6(1)(a) consent | The rows are retained as historical standing. The ability to attribute one to a person lasts for the life of the ranked identity: an erasure destroys the key and the row remains, countable and nameless | Hosting processor; **public** for the global board, and an entry whose key is destroyed is rendered on no surface |
| Estimated Cash Burn (`cost_interpretations`) | Derived server-side from a versioned pricing dataset | Server-side only | 6(1)(a) consent | Life of the claim it interprets | Hosting processor; **public**, always labelled estimated |
| Imported historical usage | The participant's machine, on request | Yes, as a claim marked imported | 6(1)(a) consent | Life of the account | Hosting processor. Private to the participant under D-087; never ranked, never public |

### Social, presence and notifications

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Friend requests (`friend_requests`) | Server, from participants | Server-side only | 6(1)(a) consent | 30 days if unanswered, per `friend_request_expiry_days`; otherwise until the relationship ends | Hosting processor; the two participants |
| Friend, rival and block edges (`friend_edges`, `rival_edges`, `blocks`) | Server | Server-side only | 6(1)(a) consent | Until removed by the participant or account erasure. Blocks are directional and are not disclosed to the blocked participant | Hosting processor; authorized viewers only |
| Board membership and role (`board_memberships`, `boards`) | Server | Server-side only | 6(1)(a) consent | Until the membership ends or the account is erased | Hosting processor; board members |
| Presence state (`presence_leases`) | Derived server-side from qualifying device activity | Activity pulse crosses; it carries no project, path or repository detail | 6(1)(a) consent | Current state only. The row expires 300 seconds after the last qualifying pulse under D-073. **No presence history is retained** | Hosting processor; viewers the participant has authorized |
| Notifications (`notifications`, `notification_preferences`) | Derived server-side | Server-side only | 6(1)(a) consent | 90 days from creation, then deleted. The server inbox is the only delivery channel at launch under D-086 | Hosting processor; the recipient |

Presence is the subject of an accepted, unmitigated residual risk. RR-001 in ADR-019 records that an authorized viewer sampling presence repeatedly can reconstruct a participant's working hours, sleep schedule and absences, that nothing in the design bounds this, and that it is not being fixed for launch. `PRIVACY.md` states it to participants because a privacy notice that omits a recorded internal exposure is a worse position than one that describes it.

### Integrity, moderation and appeals

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Verifier appraisals and evidence assessments (`evidence_assessments`) | Derived server-side | Server-side only | 6(1)(f) fraud prevention, Recital 47 and Recital 49 | Life of the claim | Hosting processor. The awarded evidence profile is **public**; the appraisal detail is not |
| Duplicate-identity and Sybil signals | Derived server-side | Server-side only | 6(1)(f) fraud prevention | 365 days, per `security_audit_retention_days` | Hosting processor. Never public under `docs/privacy/PRIVACY_CONTRACT.md` |
| Moderation cases and actions (`moderation_cases`, `moderation_actions`) | Server | Server-side only | 6(1)(f) fraud prevention | 365 days from case closure | Hosting processor. Sanctions are silent toward the public under D-084 |
| Appeals (`appeals`) | Server, from the participant | Server-side only | 6(1)(a) consent for the submission; 6(1)(f) for the record | 365 days from resolution | Hosting processor; the appellant |
| Security audit events (`audit_events`) | Server | Server-side only | 6(1)(f) security, Recital 49 | 365 days, per `security_audit_retention_days` | Hosting processor |

### Requests, exports and deletion

| Data | Where collected | Crosses device boundary | Article 6 basis | Retention | Recipients |
|---|---|---|---|---|---|
| Export jobs and bundles (`exports`) | Server, on request | The bundle is downloaded by the participant | 6(1)(a) consent; Article 20 where the request is a portability request | The download grant is short-lived and revocable; the bundle is purged 7 days after it becomes ready | Hosting processor; object storage processor; the participant |
| Deletion jobs (`deletion_jobs`) | Server, on request | Local deletion commands cross to enrolled devices | 6(1)(c) legal obligation | Cooling-off is 7 days, during which the request is cancellable. The job record is retained 365 days after completion in pseudonymous form as proof the request was honoured | Hosting processor |
| Idempotency records (`idempotency_records`) | Server | Server-side only | 6(1)(f) correctness of high-impact mutations | 30 days, per D-075 | Hosting processor |
| Personal-data-breach records | Server and controller notes | Not applicable | 6(1)(c) legal obligation, Article 33(5) | 5 years from the incident | Hosting processor; supervisory authorities on request |

The deletion cooling-off window is 7 days and is cancellable within it. `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` already records that the server-deletion machine has no `cancelled` state and no transition out of `cooling-off` other than forward, so the cancellation this map promises is not currently expressible in the state machine. That is a defect in the machine, not a softening of the window, and it is owned by PF-029.

### Data that is not held at all

Recorded because an accurate map has to say what is absent, and because a subject access request has to be answerable with the absences as well as the presences.

- No prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project names or repository names, at any tier, under any configuration. The privacy contract forbids them absolutely and no privileged mode may bypass it.
- **No provider-account identity from the telemetry channel.** The five attributes named in the device table above are the participant's provider email, three stable provider-account identifiers, and their employer or team identifier. All five arrive on the device and none is retained anywhere for any period, because D-099 destroys them before aggregation. The strip is not a configuration setting: `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` removes only the account UUIDs, no documented setting removes `user.email`, and the strip runs regardless of either. `validate_adapter_one_boundary` in `scripts/repository/validate_planning_artifacts.py` enforces it against the fixtures in `conformance/adapters/claude-code-otel/`.
- No content-derived hashes, embeddings, summaries, classifications or personal insights. Hashing forbidden content does not make it permitted.
- No government identifiers, facial scans, biometric templates, legal names, addresses or exact dates of birth.
- No special-category data within Article 9(1) and no criminal-conviction data within Article 10.
- No advertising identifiers, no third-party trackers, no analytics vendor, and no external avatar embedding that would let a third party observe a page view.
- No payment data. The product is not monetised.
- No country or geolocation field. Country leaderboards remain post-launch under D-052.

## Recipients and processors

| Recipient | Role | What it receives | Location |
|---|---|---|---|
| Hosting and managed PostgreSQL provider | Article 28 processor | Everything in the server-side rows above | European Union, per ADR-017 |
| Object storage provider | Article 28 processor | Export bundles only | European Union, per ADR-017 |
| Release-artifact and static-asset content delivery network | Article 28 processor | Release artifacts and static assets, which contain no personal data | Global edge, EU origin, per the narrow ADR-017 exemption |
| GitHub | Independent controller, and a source under Article 14 | Receives an authorization request; supplies a subject identifier and an account creation timestamp | Its own terms govern |
| X | Independent controller, and a source under Article 14 | As above | Its own terms govern |
| The public | Not a recipient in the Article 4(9) sense, but the effect is the same | Handle, Credited Token Burn at period granularity, rank, Estimated Cash Burn, awarded evidence profile, and any board membership the participant chose to make public. Not raw Token Burn, and not the confidence weight or either of its factors | Worldwide |

No processor is named yet. ADR-017 fixes the region and the selection procedure and deliberately does not name the provider. A named sub-processor list is a publication gate under D-109, because Article 28(2) requires the controller to know its sub-processors and Article 15(1)(c) requires it to be able to tell a participant who they are.

**No transfer outside the European Union is made or planned.** ADR-017 pins every persistent store holding personal data to the Union, including backups and point-in-time recovery archives. Chapter V does not currently engage. Adopting a vendor that processes outside the Union requires amending ADR-017 first, and then requires a Chapter V transfer mechanism and a transfer impact assessment.

## Retention, stated once

Every window above is stated in real units. The windows are the controller's decision, and they now exist in machine-readable form: `packages/schemas/data-disposition-v1.json` carries one row for every persistence owner in `packages/schemas/planning-schema.sql`, stating its classification, its retention window, what an erasure does to it, whether it sits inside the backup set, and which worker enforces the window. Numeric windows are keys in `packages/schemas/policy-defaults-v1.json` and the value there governs. D-216 records that split. This table remains the Article 30 record and the prose authority; the registry is the executable form of it, and a planning validator fails when the two disagree.

Backups and point-in-time recovery archives are retained 35 days, recorded as `backup_retention_days`. That is the outer bound on how long an erased row can survive anywhere, and it is why the erasure completion statement in `PRIVACY.md` is 30 days for live systems and 35 days for backups rather than "immediately". Restores reapply erasure before serving traffic, through the journal and receipt procedure in `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md`, which `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md` requires and which no restore drill has demonstrated, because nothing is provisioned.

## Erasure

Article 17(1)(b) makes erasure available on withdrawal of consent where no other ground supports the processing, and there is no other ground here: the no-swapping rule means the controller may not re-characterise leaderboard publication as a legitimate interest in order to keep the row. D-085 decides the outcome: erasure removes the account, the ranked identity, and that identity's historical ranking entries, so that no erased participant remains visible or reconstructible in any published standing.

**The mechanism that reconciles that outcome with immutable ranking generations is now decided, and D-085 is `accepted`.** D-210 records it and `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` is its normative owner. In outline: a ranking entry names an opaque pseudonym rather than an account; the only stored binding between that pseudonym and the person is an AES-256-GCM ciphertext under a key that encrypts nothing else; an erasure destroys that key, appends a hash-chained signed record, and deletes every live personal record including accepted claims. Nothing is deleted from a sealed generation, so no position moves, no content hash changes and no client cursor breaks. The append-only rule is satisfied because a tombstone is appended; identifiability ends because the key is gone.

Three limits belong in this record rather than only in the mechanism document.

- Key destruction makes re-identification computationally infeasible **for the controller**. It is not metaphysical erasure, and the position under Recital 26 is defensible rather than certain. It is one of the judgements the unmet counsel review in D-109 is expected to test.
- Logical destruction leads physical destruction by up to 35 days, through the heap tuple, the write-ahead log, the archive and the backups. Point-in-time recovery is physical and cannot exclude a row.
- The retained rows still single out an individual across time, under one pseudonym, with no name attached. Key destruction removes attribution, not singling out.

Article 17(2) obliges the controller, having made the data public, to take reasonable steps including technical measures to inform other controllers processing it that the subject has requested erasure. **Nothing in the mechanism discharges that obligation**, and a key destroyed on the controller's side does nothing to a copy on someone else's. For a public leaderboard the reach is search-engine caches, archive services, and any mirror. The reasonable steps the controller commits to are: removal from the live surface within 30 days, removal from backups within 35 days, `noarchive` and removal-request submission to the search engines that expose a removal interface, and an honest statement in `PRIVACY.md` that a third party who copied a standing before erasure is outside the controller's reach.

**No Article 17(3) exemption applies.** The one that would be reached for is 17(3)(a), freedom of expression and information. That argument was tested on closely comparable facts in *Satakunnan Markkinapörssi Oy and Satamedia Oy v Finland*, European Court of Human Rights Grand Chamber, application 931/13, 27 June 2017, where the publication of lawfully obtained personal tax data was held not to be journalism for these purposes and the publisher lost by fifteen votes to two. A leaderboard of individual spend is closer to that publication than to journalism.

## Portability scope

Article 20 applies, because the basis is consent and the processing is carried out by automated means. WP242 rev.01 distinguishes data "provided by" the subject, which includes data observed from their activity, from data derived or inferred by the controller, which is out of scope.

**Portable, in a structured, commonly used and machine-readable format:** raw token counts and their bounded intervals, the account and handle, linked provider identifiers, device registrations, social edges the participant created, board memberships, and the local audit ledger.

**Not portable, because it is derived:** computed rank, percentile, generation and snapshot identifiers, Estimated Cash Burn, the confidence weight of ADR-020, the awarded evidence profile, and every verifier appraisal dimension. These are supplied under the Article 15 right of access, which has no derived-data carve-out, but they are not Article 20 outputs. D-108 records this split.

Article 20(2) direct transmission to another controller is not offered, because no interoperable recipient exists. That is a statement of fact, not a refusal, and Article 20(2) requires it only where technically feasible.

## Automated decision-making

Three automated processes act on a participant without a human in the loop at the moment they act.

1. **Verifier appraisal.** The server assigns the public evidence profile and competitive eligibility. The client never selects it.
2. **Confidence weighting.** ADR-020 applies a server-assigned weight, derived from the evidence profile and the ranked-identity trust state, to raw Token Burn to produce the credited figure that public rank is computed on.
3. **Deterministic integrity controls.** Duplicate-domain, replay, sequence and lineage rules can quarantine a claim or sanction a ranked identity.

None of the three verifies that the underlying usage happened. D-100 records that no provider offers a usage-attestation path for an individual account, so every claim from an individual participant is self-reported at the source whatever the local capture quality. An appraisal is an assessment of evidence quality, not a confirmation from a provider, and no document in this set may imply otherwise.

The controller does not assert that Article 22(1) is inapplicable. A sanction that removes competitive eligibility is capable of significantly affecting a participant, and asserting otherwise would be the controller marking its own homework. The Article 22(3) safeguards are therefore provided as a matter of design rather than as a concession: under D-084 a first sanction is reversible, the affected participant receives a server-inbox notice stating the effect and the appeal route, and the appeal is decided by the maintainer as a human. Statistical and small-language-model detection stays local, advisory and non-authoritative under D-053 and never acts against a named individual on its own.

## ePrivacy Article 5(3) is a second, independent consent

This obligation is separate from the GDPR basis and is not satisfied by it. Article 5(3) of Directive 2002/58/EC as amended requires consent to store information in, or gain access to information already stored in, the terminal equipment of a user. EDPB Guidelines 2/2023 confirm the provision is technology-neutral: it is not confined to cookies, it covers any access to information stored on the device by any technical means, and the entity gaining access need not be the one that stored it.

The VibeMaxxing daemon reads information stored on the participant's machine by a third-party agent CLI. That is gaining access to information stored in terminal equipment. Consent is required regardless of which GDPR basis covers the subsequent processing, and several member states enforce Article 5(3) through national implementations that sit outside the GDPR one-stop-shop, so the controller's lead-authority position does not consolidate it.

The controller does not rely on the strictly-necessary exemption in Article 5(3), even though an argument for it exists, because the access exists to produce a competitive ranking rather than to carry out transmission or to provide a service the user could not otherwise receive. D-104 records the decision. The consent is per source: each agent CLI the collector is permitted to read is separately consented, separately refusable, and separately withdrawable, and refusing one does not disable the rest of the product.

## Data protection impact assessment

A DPIA is mandatory here and has not been carried out. D-109 records it as an unmet release gate.

Two independent routes reach that conclusion. First, WP248 rev.01 lists nine criteria and treats two as sufficient to require a DPIA; this processing meets five — evaluation and scoring, systematic monitoring, data processed on a large scale, matching or combining datasets, and innovative use of a new technological solution — with financial data instanced under the fourth criterion. Second, entry 7 of the German Datenschutzkonferenz *Muss-Liste* makes a DPIA mandatory for a public rating portal that scores named individuals, which is a fair description of a public leaderboard of personal spend.

The DPIA is not written here. Writing it inside the record of processing would produce a document that is neither, and Article 35(7) requires a specific structure this map does not have.

## What this document is not

- It is not legal advice and it has not been reviewed by a lawyer.
- It is not evidence that any described control is implemented. Nothing is provisioned, no processor is contracted, no data has been collected, and no erasure or export path has been executed.
- A passing repository validator proves that this document's references resolve. It proves nothing about whether the analysis is right.
