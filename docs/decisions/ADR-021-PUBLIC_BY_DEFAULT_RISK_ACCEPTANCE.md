# ADR-021: Public-by-default leaderboard, and the risk the owner accepted

Status: accepted
Date: 2026-08-06
Decision: D-101, D-102, D-103, D-104, D-105, D-106, D-107, D-108, D-109

**Not reviewed by counsel. Counsel review is an unmet release gate.** The analysis below was produced by the controller against primary sources. It is the reasoning the decision was made on, not advice, and one of the reasons for writing it down is so that a lawyer can eventually be shown exactly what was and was not considered.

## Context

The global leaderboard publishes a natural person's handle next to their aggregate language-model token spend, to the whole internet, with no account required to read it. That is the product. The question this record answers is not whether to build it but whether the owner may publish it by default to participants in the European Union, and on what terms.

The owner is EU-primary and personally the controller under ADR-017. There is no legal entity absorbing consequence and no engaged counsel. The analysis was put in front of the owner in full, including the parts that argue against publication, and the owner decided to keep the global leaderboard public by default with EU participants included. **This record documents that as an informed risk acceptance. It does not relitigate it.**

ADR-019 is the register for accepted residual risks that no normative owner has adopted. This is a separate record because RR-001 and RR-002 there are risks to participants arising from design choices; this is a legal-exposure risk arising from a publication choice, it is owned by the privacy documents rather than by the threat model, and merging the two would bury a regulatory exposure inside a product-harm register.

## The analysis the decision was made on

### The data is personal data, and the recent case law does not rescue it

A token count next to a GitHub or X handle is personal data within Article 4(1) of Regulation (EU) 2016/679. Recital 30 treats online identifiers as identifying, and C-434/16 *Nowak* establishes that "any information" is a deliberately wide formulation covering objective and subjective information of any kind, provided it relates to an identified or identifiable natural person. A per-person spend figure does.

The obvious counter-argument is C-413/23 P *EDPS v SRB*, decided 4 September 2025, which is read in some quarters as establishing that pseudonymised data may not be personal data in the hands of a recipient without the means of re-identification. **It does not help here.** Paragraph 76 of that judgment is explicit that the data remain personal data for the party holding the means of re-identification. The controller holds the mapping from handle to count. The controller *is* the mapping. The relative-identifiability reasoning applies to a downstream recipient, and the controller is never that recipient.

### Not Article 9, and that is not comfort

The Article 9(1) list of special categories is exhaustive and financial information is absent from it. Aggregate token spend is not special-category data, so the Article 9(2) condition machinery does not engage.

That narrows the obligation without lowering the risk. WP248 rev.01 instances financial data under its fourth criterion, and it treats two of its nine criteria as sufficient to require a data protection impact assessment. This processing meets five: evaluation and scoring, systematic monitoring, data processed on a large scale, matching or combining datasets, and innovative use of a new technological solution. Independently, entry 7 of the German Datenschutzkonferenz *Muss-Liste* makes a DPIA mandatory for a public rating portal that scores named individuals, which is an accurate description of a public leaderboard of personal spend. **A DPIA is mandatory and has not been carried out.** D-109 records it as an unmet release gate.

### Consent is the only lawful basis that survives

**Article 6(1)(b) fails.** EDPB Guidelines 2/2019 on Article 6(1)(b) in the context of online services hold that processing is necessary for performance of a contract only where it is objectively necessary for the service the subject requested, and specifically that engagement metrics, personalisation and improvement do not meet that test. A leaderboard is an engagement metric. Writing "you agree to appear on a leaderboard" into the terms and then treating publication as contractual necessity is precisely the circular reasoning those guidelines exist to defeat.

**Article 6(1)(f) is available in principle and strains in practice.** C-621/22 *Koninklijke Nederlandse Lawn Tennisbond* requires that the processing be strictly necessary for the interest pursued and, crucially, asks what the data subject could reasonably expect **at the time the data were collected**. Data collected to count a participant's own usage, published to the open internet next to their handle, is not obviously within that expectation. EDPB Guidelines 1/2024 on legitimate interests reinforce it at footnote 52: the fact that data are manifestly public does not by itself justify further processing under 6(1)(f). Legitimate interest could probably be argued. It could not be argued comfortably, and a personal controller with no counsel should not be relying on a basis they would have to argue.

**Consent under Article 6(1)(a) is the basis, and it has a condition attached.** Article 7(4) and Recital 43 mean consent is not freely given where it is bundled with a service the subject cannot get without it. The product satisfies that only because refusing costs the participant nothing they would otherwise have: there is no other product behind the leaderboard, so declining to create an account is a real option rather than a coerced one, and the ePrivacy consent for each agent CLI is separately refusable without disabling the rest. D-101 records the choice.

### Consent has a consequence the design has to absorb

Choosing consent makes Article 17(1)(b) directly available: withdraw consent, and where no other ground supports the processing, erasure follows. The EDPB no-swapping rule closes the escape hatch — the controller may not, on withdrawal, re-characterise the same publication as a legitimate interest in order to keep the row.

Article 17(2) then obliges reasonable steps, including technical measures, to inform other controllers processing the data that erasure was requested. For a public leaderboard that reaches search-engine caches, archives and mirrors. The steps committed to in `PRIVACY.md` are removal from the live surface within 30 days, removal from backups within 35 days, archive-suppression markup, and removal requests to the search engines that offer an interface — together with an explicit statement of what the controller cannot reach.

**No Article 17(3) exemption covers this.** The candidate is 17(3)(a), freedom of expression and information. That argument was tested on closely comparable facts in *Satakunnan Markkinapörssi Oy and Satamedia Oy v Finland*, European Court of Human Rights Grand Chamber, application 931/13, 27 June 2017: mass republication of lawfully obtained personal tax data. The publisher lost by fifteen votes to two. A leaderboard of individual token spend is not in a stronger position than a newspaper was, and pretending otherwise is the kind of assumption that turns a reprimand into a fine.

The tension this creates with the repository's own immutability rules is real and is recorded rather than resolved: D-085 decides the erasure outcome and remains `provisional` precisely because the mechanism that reconciles it with immutable ranking generations is undecided. That is an open engineering problem owned by PF-029 and PF-022, not a softening of the outcome.

### Article 25(2) is the provision this decision is in tension with

Article 25(2) requires that, by default, only personal data necessary for each specific purpose are processed, and states in terms that the measures must ensure that **personal data are not made accessible without the individual's intervention to an indefinite number of natural persons**.

A leaderboard that is public by default makes personal data accessible to an indefinite number of natural persons. The controller's position is that the individual's intervention is present, because publication happens only after an affirmative, informed, separately refusable consent, and because there is no way to participate in a public competition without being publicly ranked. **That is a defensible reading of Article 25(2) and it is not a certain one.** A supervisory authority could read "by default" as requiring the private setting to be the initial state, with public as an opt-in on top. The decision was taken with that specific uncertainty stated, and this paragraph exists so that no later reader concludes the provision was overlooked.

### Records, representatives and jurisdictions

**Article 30 records are mandatory.** The under-250 exemption in Article 30(5) does not apply: the Article 29 Working Party position paper of 19 April 2018 confirms the three carve-outs are alternative rather than cumulative, and continuous collection from an always-on daemon is not "occasional" under any reading. `docs/privacy/DATA_MAP.md` is the record. D-105.

**No Article 27 Union representative is required.** The controller is established in the Union, so Article 3(1) applies and Article 27 is definitionally inapplicable — it addresses controllers outside the Union caught by Article 3(2). A United Kingdom representative probably is required under Article 27 of the UK GDPR if UK participants are accepted, and none is appointed. D-106 records both, and makes the UK representative a precondition on accepting UK participants rather than a launch-wide blocker.

**A hard age floor of 16 moots the parental-consent machinery entirely.** Article 8(1) sets 16 and permits member states to lower it to no less than 13, and they have: 13 in Belgium, Denmark, Estonia, Finland, Latvia, Malta, Portugal and Sweden; 14 in Austria, Bulgaria, Cyprus, Italy, Lithuania and Spain; 15 in Czechia, France and Greece; 16 in Germany, Ireland, the Netherlands, Poland and others. Implementing that table means determining each participant's member state and then building verifiable parental consent for the ones below the floor — both of which require collecting *more* personal data about minors in order to protect them. A single Union-wide 16 collects less and needs neither. D-103.

**ePrivacy Article 5(3) is a second, independent consent that the repository did not mention anywhere before this record.** It requires consent to gain access to information stored in terminal equipment. EDPB Guidelines 2/2023 confirm it is technology-neutral and not confined to cookies: any access to information stored on a device, by any technical means, by any entity, is in scope. A local daemon reading an agent CLI's logs is squarely within it, regardless of which GDPR basis covers the downstream processing, and several member states enforce their Article 5(3) implementations outside the one-stop-shop, so the lead-authority mechanism does not consolidate the exposure. The controller does not rely on the strictly-necessary exemption, because the access exists to produce a ranking rather than to deliver a transmission or an unavoidable service function. D-104.

**United States exposure is smaller than it looks and is not zero.** No state comprehensive privacy law applies: the California Consumer Privacy Act requires a for-profit business meeting a revenue threshold of 26.625 million dollars or a 100,000-consumer volume threshold, and the controller meets none of them, and the other state regimes are similarly gated. Two obligations have no threshold at all. CalOPPA, at California Business and Professions Code section 22575(a), requires any commercial website operator collecting personal information from California residents to post a conspicuous privacy policy. Breach notification applies in all fifty states with no size threshold — California Civil Code section 1798.82(a) binds "an individual or business" in terms. D-107.

**Portability splits on the observed-versus-derived line.** Article 20 applies because the basis is consent. WP242 rev.01 puts data observed from the subject's activity inside the right and data derived or inferred by the controller outside it. Raw token counts are portable; computed rank, percentile, generation identifiers, Estimated Cash Burn and the confidence weight of ADR-020 are not. They remain fully accessible under Article 15, which has no derived-data carve-out. D-108.

## Decision

**The global leaderboard is public by default, including for participants in the European Union.** The owner made that decision with the analysis above in front of them, and this ADR records it as an informed acceptance rather than an oversight.

The acceptance is conditioned on the following, which are decisions rather than mitigations and which are not optional parts of it:

1. The lawful basis is consent, and consent is genuinely refusable. D-101.
2. `PRIVACY.md` states what becomes public in the first screen of text, not in a clause.
3. Erasure is honoured as decided in D-085, without a legitimate-interest fallback and without an Article 17(3) claim.
4. A DPIA is carried out before launch. D-109.
5. The controller answers every data subject request within the Article 12(3) month, and answers a supervisory authority.

## The risk, with the base rates

Recorded numerically because a risk stated only in adjectives cannot be revisited.

**Likelihood of enforcement contact is low but not remote.** A public leaderboard of named individuals' spend is exactly the shape of thing that generates a complaint from a participant who wanted off it. One complaint is sufficient to open a file.

**Severity, if contact happens, is modest at the base rate.** The CMS GDPR Enforcement Tracker recorded 385 fines against individuals as of 2026, with a **median of 1,000 euros** and most below 2,000 euros. Individual controllers are not where the headline numbers come from.

**The realistic worst case is not a fine.** It is an Article 58(2)(g) erasure order plus an Article 58(2)(d) compliance order — do this, by this date. Both are survivable and both are cheap to comply with if the systems already do what this record says they do.

**The tail risk is an Article 58(2)(f) processing ban**, which for this product is indistinguishable from shutdown, because the processing is the product.

**Two behaviours convert the modest case into the tail case, and neither is a technical failure:**

1. **Ignoring a data subject request.** A participant who asks to be erased and is not answered escalates to a supervisory authority with a complete, undisputed record. There is no defence to it and it costs nothing to avoid.
2. **Not answering a supervisory authority.** A regulator writing to a controller who does not reply is the reliable route from a reprimand to a fine plus an order, in almost every published decision against a small controller.

Both are failures of correspondence by a single maintainer with no support process — which under D-091 and D-092 is exactly the operational profile this project has. That is the actual risk here, and it is larger than the legal analysis above.

## Mitigations that remain available without changing the default

Recorded so that a later reader knows what the response space is, and knows that none of these was chosen now.

- **A per-participant public/unlisted toggle**, defaulting to public. This preserves the default while making Article 25(2) markedly easier to defend and giving a complainant a remedy short of erasure.
- **Coarsening the public figure** to buckets or to a rank without an absolute number, which reduces the personal-data content of the publication. It costs the raw metric that D-004 and D-037 fix.
- **A published, fast, self-service erasure path** that removes a standing without correspondence, which removes the single highest-probability escalation route.
- **A named contact and a documented response process**, which is the cheapest possible defence against both escalation behaviours above and requires no code.
- **`noindex` on individual profile pages** while leaving the board itself public, which limits the search-engine cache surface that Article 17(2) obliges the controller to chase.
- **Carrying out the DPIA**, which is mandatory anyway and which converts an undocumented risk acceptance into a documented one that Article 35 recognises.
- **Engaging counsel**, which is a release gate under ADR-009 and which would replace this entire section with advice.

## Consequences

- The product ships, if it ships, with a documented legal exposure rather than an assumed absence of one.
- `PRIVACY.md`, `TERMS.md` and `docs/privacy/DATA_MAP.md` are bound to this analysis and may not state a weaker position than it. In particular, no surface may claim compliance, claim that token counts are not personal data, or claim an Article 17(3) exemption.
- The DPIA is a launch blocker and appears as one in `docs/operations/PRODUCTION_READINESS.md`.
- Counsel review is a launch blocker and appears as one in the same place and in `docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md`.
- The controller's legal name, postal address, supervisory authority and governing jurisdiction are unfilled placeholders in the participant-facing documents. Those documents cannot be published in that state, and D-109 owns the gate.
- No processor is contracted and no sub-processor is named, so a subject access request under Article 15(1)(c) could not currently be answered accurately. ADR-017 owns the selection procedure and the gate is real until it runs.
- Nothing here is implemented. There is no consent flow, no erasure job, no export path and no record of any request being answered, because there is no running system.

## What would cause this to be revisited

- **A complaint, a supervisory-authority letter, or a data subject request that is not answered within the Article 12(3) month.** Any of the three is the signal, and the third is the one that is entirely within the controller's control.
- **The DPIA producing a residual high risk**, which triggers the Article 36 prior-consultation obligation and is a materially different decision from this one.
- **A legal entity being formed or counsel being engaged**, which changes the controller analysis and replaces this record's reasoning with advice.
- **Accepting participants in the United Kingdom**, which requires an Article 27 UK representative that does not exist.
- **A supervisory authority or a court reading Article 25(2) as requiring private-by-default for a public ranking of named individuals**, which is the specific uncertainty this record states and does not resolve.
- **Monetisation**, which would move the controller inside thresholds it is currently outside — the California Consumer Privacy Act's for-profit requirement most directly — and would change the United States analysis in D-107.
- **Adding a dimension to the public projection** — geography, per-model splits, finer time granularity — each of which increases the personal-data content of the publication and reopens both this record and RR-002 in ADR-019.
