# VibeMaxxing Terms of Service

Last updated: 2026-08-06

**These terms have not been reviewed by a lawyer.** Counsel review is a release gate that is not satisfied, recorded as D-109 and in `docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md`. Nothing here is legal advice.

**There is no service yet.** No server is provisioned, no account exists and no data has been collected. These terms are published now so that what the service will require of you, and what it refuses to promise you, is legible before anyone can sign up rather than after.

Privacy is governed by `PRIVACY.md`, which is a separate document and takes precedence over these terms on any question of personal data.

## 1. What VibeMaxxing is

VibeMaxxing counts the language-model tokens you burn through supported agent CLI tools and publishes the total on a leaderboard. A local daemon reads your agent tools' own logs on your own machine, counts tokens there, and sends only a fixed-schema aggregate claim to the server. Your prompts, responses, transcripts, code, file paths, project names and repository names never leave your machine.

The service is free. There is no paid tier, no subscription and no advertising. It is not monetised and there is no plan to monetise it.

## 2. Eligibility

**You must be at least 16 years old.** This is a single threshold applied everywhere, and it is not adjusted downward for member states whose national law permits a lower digital-consent age. If you are under 16 you may not create an account, and an account we learn belongs to someone under 16 is closed and its data erased.

You must control a GitHub or X account that is at least 90 days old at the time you link it. Account age is a weak control against throwaway accounts and it is nothing more than that: linking a provider account proves you control that account, and it does not prove you are a unique human being.

You may hold **one active ranked identity**. Multiple accounts belonging to one person do not produce multiple competitors, and their scores are never added together. Where duplicate accounts are consolidated, valid historical contributions are combined under the surviving identity with their original period attribution preserved, and overlapping contributions count once.

## 3. Your account

You are responsible for keeping control of the provider account you link and of the devices you enrol. Revoking a device takes effect immediately and stops it producing claims.

You may close your account at any time. Closing it is not the same as erasure; the erasure right and what it actually removes are described in `PRIVACY.md`, and if you want your published standings gone, use the erasure route, which is designed to remove them.

## 4. What gets published

By creating an account and connecting an agent you are asking to be put on a public leaderboard. Your handle, your Credited Token Burn at period granularity, your rank, an Estimated Cash Burn figure and the evidence profile the server awarded you are visible to anyone on the internet with no account. Your raw Token Burn total and the confidence weight applied to it are not public; they are on your own page and on surfaces you authorize.

**Estimated Cash Burn is an estimate and never an invoice.** It is computed on the server from a versioned public pricing dataset, and it is not what you were charged, not what your provider billed you, and not a claim about your actual spending. It is always labelled as estimated wherever it appears.

Friend, rival, private, organization, hacker-house and community boards require the viewer to be authorized. Presence is visible only to viewers you authorize, and setting presence to private withdraws it from everyone.

## 5. What counts, and what does not

**Genuine but pointless usage counts.** Burning tokens on something deliberately useless is within the spirit of the product, and it is not cheating, provided the usage is real and is not counted twice. That is the whole joke and it is protected here on purpose.

**Fabricated usage does not count.** Claims must come from the certified adapter and collector reporting what actually happened on your machine. Forging a claim, tampering with the collector, replaying claims, cloning device keys, or driving a script whose purpose is to inflate a count without the corresponding real consumption are all violations.

**Historical imports never compete.** Usage imported from before you joined renders as a single private lifetime statistic on your own surface. It is labelled imported, it never enters any board or period standing, and it never affects anyone else's rank.

**Nothing here is verified by your provider.** No provider offers a usage-attestation path for an individual account — every usage endpoint that exists requires an organization administrator key — so every figure on this leaderboard is self-reported by software running on a participant's own machine. D-100 records that as a permanent constraint. Do not read a rank, an evidence profile or a score as proof that the usage happened.

**The server decides your evidence profile, not you.** Your client submits facts; a server-side verifier decides what those facts are worth and whether they are competitively eligible. Public rank is computed on a credited figure — your raw count multiplied by a confidence weight derived from that profile and from your identity's trust state, under `docs/decisions/ADR-020-CONFIDENCE_WEIGHTED_RANKING.md`. Your raw count is stored unchanged and is never rewritten.

**The metric is uncapped and this is a known property.** A participant willing to spend money can raise their own score, and the design does not prevent that. It is documented in `SECURITY.md` as known and accepted, so you do not need to report it.

## 6. Acceptable use

Do not:

- forge, replay, tamper with or automate the fabrication of usage claims;
- operate more than one ranked identity, or coordinate accounts to manufacture standings;
- attempt to deanonymise, track, stalk or monitor another participant, including by systematically polling their presence;
- harass, threaten or abuse another participant through any surface the product provides, including handles, board names and invitations;
- use a handle designed to impersonate another person or to evade handle policy through visually confusable characters;
- attack the service, its supply chain, its release infrastructure or other participants' devices;
- test security against systems or data you do not own or have permission to test — see `SECURITY.md` for the reporting route and for the safe-harbour position, which is not yet published;
- circumvent a sanction, including by creating a replacement account.

Report a vulnerability through the private channel in `SECURITY.md`. Do not include real prompts, transcripts, code, repository names, paths or credentials in a report; the product exists to keep those off our servers and a bug report is not an exception.

## 7. Sanctions and appeals

Integrity enforcement is progressive, it is appealable, and it does not require you to submit identity documents.

**A sanction is silent toward the public and explicit toward you.** The public leaderboard carries no mark against a sanctioned participant — no badge, no asterisk, no gap where you used to be that is labelled as a sanction. You receive a notice in your server inbox that states what the effect is and how to appeal it.

**A first sanction is reversible.** If your appeal succeeds, the ranking effect is fully reversed rather than partially credited or applied going forward only.

**Appeals are decided by a human.** The maintainer decides them. There is one maintainer, so there is no separate reviewer and no appeal above that decision inside the product. That is a limitation and it is stated rather than dressed up as an independent process.

A shared network address, a shared machine or a shared workplace is never on its own sufficient grounds for a high-impact sanction.

## 8. Availability, and the absence of a promise

**Service availability is best effort.** There is no service level agreement, no paging rotation, no on-call engineer and no committed incident response time. Hours of downtime are acceptable and are not a breach of these terms. Any availability or latency figure published in this repository is an aspirational target, not a commitment, and any document that presents one as a commitment is wrong.

The project is run by one person. There is no support team. There is no guarantee that a message gets a reply on any particular timescale — except a request under `PRIVACY.md`, which is answered within one month because the law requires it and because ignoring one is the single worst thing this project could do.

Features may change. Country leaderboards and local statistical detection are explicitly out of the initial scope and may never ship.

## 9. Disclaimers and liability

The service is provided **as is** and **as available**, without warranties of any kind, express or implied, including any implied warranty of merchantability, fitness for a particular purpose, non-infringement, accuracy or uninterrupted availability.

Token counts and rankings are produced by software reading logs written by third-party tools that the controller does not control and whose formats can change without notice. They may be wrong. Estimated Cash Burn may be wrong in either direction. Do not rely on any figure here for accounting, tax, expense reporting or any decision that matters financially.

To the maximum extent permitted by applicable law, the controller is not liable for indirect, incidental, special, consequential or punitive damages, or for lost profits, lost data or reputational harm, arising from use of the service.

**Nothing in this section limits liability that cannot lawfully be limited.** That includes liability for death or personal injury caused by negligence, for fraud or fraudulent misrepresentation, and — importantly for a consumer service in the Union — any liability that mandatory consumer protection law reserves. If you deal as a consumer, your statutory rights are unaffected by these terms, and the limitations above apply only so far as that law permits.

## 10. Intellectual property

The software is open source. Original code is licensed under Apache License 2.0 and documentation and specifications under CC BY 4.0, per `docs/decisions/ADR-009-LICENSING_AND_CONTRIBUTION_MODEL.md` and `LICENSES.md`. Contributions use the Developer Certificate of Origin.

Those licences do not grant use of the VibeMaxxing or VibeProof names and marks for confusing product branding. A trademark policy is required before public release and has not been published.

You keep whatever rights you have in the content on your own machine. We never receive it, so we never acquire any rights in it. You grant permission to display your handle, your scores and the public profile fields you chose, for as long as your account exists.

## 11. Suspension and termination

You may stop using the service at any time, and you may close your account and request erasure through the routes in `PRIVACY.md`.

The controller may suspend or terminate an account that violates section 6, subject to the notice and appeal process in section 7. Termination for a violation does not by itself erase your data; erasure is your right to exercise and is honoured on request regardless of why the account ended.

If the service is discontinued, participants are notified in advance through the server inbox and given an opportunity to export their data before it is deleted.

## 12. Changes to these terms

Material changes are announced in the server inbox before taking effect. Every revision of this file is in the repository's public git history. A change that widens what is collected or published requires fresh consent under `PRIVACY.md` and does not take effect by silence.

## 13. Governing law and disputes

These terms are governed by the law of `[GOVERNING JURISDICTION]`, being the jurisdiction in which the controller is established, and the courts of that jurisdiction have jurisdiction over disputes arising from them.

That placeholder is unfilled and is a publication gate under D-109, together with the controller's legal name and address in `PRIVACY.md`. It is committed in this state so the gap is visible.

**If you are a consumer resident in the European Union, this clause does not deprive you of the protection of the mandatory law of your own country of residence, and it does not deprive you of the right to bring proceedings in the courts of that country.** Article 6 of Regulation (EC) 593/2008 and Article 18 of Regulation (EU) 1215/2012 secure that, and a choice-of-law clause cannot override it. The clause above is a default, not a waiver.

Your right to complain to a data protection supervisory authority under Article 77 of the GDPR is separate from this section, is not affected by it, and does not require you to contact the controller first.

## 14. Contact

`vedant@simulacrum.world`

## 15. What these terms are not

- They are not legal advice, and no lawyer has read them.
- They do not describe a running service. Nothing is deployed.
- They do not claim compliance with any regime. `docs/privacy/DATA_MAP.md` records the analysis and the unmet gates behind both this document and `PRIVACY.md`.
