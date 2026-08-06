# ADR-017: Hosting region and residency

Status: accepted
Date: 2026-08-06
Decision: D-080, D-093, D-094, D-360, D-361, D-362, D-363

## Context

`docs/operations/OPERATIONS_OPEN_SOURCE_AND_LAUNCH_CONTRACT.md` states that provider and region are selected through an ADR using latency, price, compliance, operational maturity, available credits and portability, and that core behaviour cannot depend on one provider. That ADR is this one, and it had no prior existence, so every downstream artifact that assumed a hosting decision had been made was assuming something that did not exist.

Two things were conflated in that sentence and this ADR separates them. **Region and residency are a product and legal commitment.** **Provider is a procurement choice.** The first constrains what the product may promise a participant; the second constrains what it costs to run. They resolve on different evidence and on different timescales, and binding them together is what kept both undecided.

The owner is personally the controller for the purposes of the General Data Protection Regulation. There is no legal entity and no engaged counsel. That is not a reason to defer residency; it is a reason to make the residency commitment the conservative one, because a personal controller has no corporate structure absorbing the consequence of a wrong answer, and because retrofitting residency after launch means migrating live personal data across a jurisdictional boundary.

The budget position was fixed by D-093 at under 100 USD per month. **D-093 and D-094 are now superseded.** The owner amended the ceiling — D-360 — which is one of the three amendments step 4 permits, and selected AWS under D-361. The amendment is what unblocked the gate; the owner's credit balance is not, and step 4's refusal to count credits stands unchanged. The rest of this section is retained because it records why the gate existed. The recovery objectives inherited from the operations contract are a PostgreSQL recovery point objective of at most 5 minutes and a recovery time objective of at most 60 minutes, with monthly restore tests and quarterly disaster-recovery exercises. D-094 records that those objectives, that ceiling and the stated 100,000 ranked-identity target do not all hold at once. This ADR does not resolve that conflict and does not pretend to; it makes the conflict a gate in the selection procedure so that a provider cannot be chosen by quietly relaxing one of the three.

## Decision

### Region and residency: decided

All persistent stores holding personal data — the PostgreSQL primary and its replicas, backups, point-in-time recovery archives, object storage holding export bundles, and any queue or cache holding account-linked rows — are located in the European Union. The product is built GDPR-native from the first migration rather than retrofitted: the data map, the lawful-basis record, the retention windows, the export bundle and the erasure path are contract obligations from the start, not launch-blocking additions.

Two categories are exempt and the exemption is narrow and stated rather than assumed:

- **Public release artifacts and their signed metadata** may be served from a global content delivery network, because they contain no personal data and their availability target is higher than the API's. Their origin remains in the European Union.
- **Static hosted-web assets** may be served globally for the same reason.

Nothing else leaves the region. Observability, reviewer tooling, support systems and backup copies stay in the European Union, which means an observability or error-tracking vendor that processes outside it is not adoptable without amending this ADR.

### Provider: not decided here, and decided by the rule below

The provider is selected by the procedure in this ADR rather than named in it, because the inputs the procedure needs — measured launch load, priced against published list prices on the day of selection — do not exist yet, and a provider named without them would be a preference presented as an analysis.

The shortlist is the three platforms on which the owner already holds credits: **Render, Cloudflare and AWS**. A candidate outside the shortlist enters only by clearing the same gates.

Credits are excluded from the selection arithmetic. A credit balance is a one-off subsidy with an expiry; a hosting dependency is permanent. Selecting on credit-adjusted cost chooses the provider that is cheapest for the first year and most expensive for the rest, and the project has no funding line to absorb the difference when the balance runs out. Credits legitimately affect *when* spend starts, and they are recorded as a runway figure, not as a discount on the comparison.

### Selection criteria

Each is a stated fact about a candidate, verified against that provider's published documentation and terms on the day of selection, because provider regions, pricing and sub-processor lists change without notice and a verification older than the decision is not a verification.

1. **Data residency guarantee.** Whether the candidate offers a region in the European Union for every service on the critical path, and whether region pinning is a contractual guarantee for data at rest rather than a default that a control plane may override. A candidate whose managed database is EU-pinned but whose backup destination or metrics store is not fails this criterion.
2. **Managed PostgreSQL meeting the recovery objectives.** Whether the candidate's managed PostgreSQL offers point-in-time recovery at a granularity of 5 minutes or finer, a documented restore procedure a single operator can execute, and a published or measurable restore time for the modelled data volume. `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` makes tested rollback and preproduction restore drills mandatory, so a restore path that exists on paper and has never been executed does not count.
3. **Steady-state monthly cost at list price** for the modelled launch configuration, against the D-093 ceiling, with credits excluded.
4. **Data processing agreement and sub-processor terms.** Whether the candidate offers a GDPR Article 28 data processing agreement that a sole trader can execute without enterprise negotiation, publishes its sub-processor list, and commits to advance notice of changes with a right to object. A personal controller who cannot name the processors under their processor cannot answer a subject access request accurately.
5. **Egress cost.** Priced separately for the two shapes that dominate: release-artifact distribution, which is large, cacheable and grows with installed base; and database backup extraction, which is the cost of leaving.
6. **Exit path.** The count of provider-proprietary interfaces the critical path would depend on, and the measured hours to restore a production-equivalent environment at a different provider from backups and infrastructure code alone. The operations contract requires that core behaviour cannot depend on one provider, and the only honest measurement of that is an executed restore elsewhere.
7. **Operational maturity for a single operator.** Whether routine operations — restore, failover, key rotation, certificate renewal, migration application — are executable by one person without a support contract, given that D-092 accepts best-effort availability with no on-call.

### Decision rule

Applied in order. The first four steps are eliminations; a candidate that fails one is out regardless of how it scores elsewhere.

1. **Residency gate.** Eliminate any candidate that cannot pin every persistent store holding personal data, including backups and point-in-time recovery archives, to a European Union region under criterion 1.
2. **Recovery gate.** Eliminate any candidate whose managed PostgreSQL cannot meet a 5-minute recovery point objective and a 60-minute recovery time objective under criterion 2. A candidate that offers no first-party managed PostgreSQL does not satisfy this gate on its own; it may still be selected for the artifact-distribution role under step 6.
3. **Agreement gate.** Eliminate any candidate that does not offer an executable Article 28 data processing agreement and a published sub-processor list under criterion 4.
4. **Budget gate.** Eliminate any surviving candidate whose steady-state monthly list cost under criterion 3 exceeds the D-093 ceiling. **If no candidate survives this step, the selection halts.** It does not proceed by relaxing the recovery objective, silently accepting the overrun, or counting credits. It returns to the owner as the D-094 conflict, and the owner amends exactly one of the ceiling, the scale target or the recovery objectives before selection resumes. This step is the reason the D-094 conflict cannot be resolved by accident.
5. **Rank survivors by exit cost** under criterion 6: fewest proprietary interfaces on the critical path first, then lowest measured restore-elsewhere time, then lowest backup-extraction egress cost.
6. **Split the roles if that is cheaper.** Compute and managed PostgreSQL are one role; release-artifact and static-asset distribution is another. The rule selects independently for each, because zero-egress artifact distribution and EU-pinned managed PostgreSQL are different products and there is no requirement that one vendor supply both. A split increases the sub-processor count under criterion 4, which is a cost the split has to justify.
7. **Break remaining ties by egress price** for release-artifact distribution under criterion 5, since that cost grows with adoption and the others do not.

### What is already known about the shortlist

Recorded as orientation, not as the verified inputs the rule needs. Each item is rechecked at selection.

- **Render** is a managed-container platform with first-party managed PostgreSQL and a European Union region, and its surface is close to the portable baseline the operations contract describes: containers, PostgreSQL, object storage. Its proprietary-interface count on the critical path is therefore low, which scores well at step 5. The open questions are whether point-in-time recovery at the required granularity is available on a plan within the D-093 ceiling, and what the restore time is at the modelled volume.
- **Cloudflare** has the strongest egress position of the three for artifact distribution and is the natural candidate for the step 6 artifact role, which matters because signed release metadata and update artifacts are distributed to every installed client under ADR-013. It has no first-party managed PostgreSQL, so it does not clear the step 2 gate for the database role on its own. Its edge compute model is also the least portable of the three, so a critical path built on it scores badly at step 5.
- **AWS** clears the residency and recovery gates most comfortably and has the deepest managed-PostgreSQL recovery tooling. It is the most likely of the three to fail the step 4 budget gate at a highly available configuration, and it has the highest exit cost if the design reaches for services beyond managed PostgreSQL, containers and object storage. Restricting AWS usage to those three services keeps the exit cost comparable to Render's; every additional managed service moves it.

### The tension, stated plainly

**The recovery objectives and the budget ceiling are in tension, and one of them is likely to move.** A managed PostgreSQL configuration with a 5-minute recovery point objective, a 60-minute recovery time objective, monthly tested restores and quarterly disaster-recovery exercises is not, on any of the three shortlisted providers, obviously reachable for under 100 USD per month at the scale the product targets — and that is before compute, object storage and the 36 board projections implied by D-088.

This ADR does not resolve that. It refuses to hide it. Step 4 halts the selection rather than absorbing the overrun, so the conflict recorded in D-094 surfaces as a blocked decision rather than as a quiet downgrade discovered during an incident. Whichever way the owner resolves it, the resolution is recorded as an amendment to D-093, to the scale target, or to the operations contract's recovery objectives, and D-094 is superseded by that amendment.

## Consequences

- Residency is a fixed constraint on every later infrastructure choice, including observability, error tracking, email delivery when it eventually ships, and any managed service that touches account-linked rows. A vendor that processes outside the European Union requires an amendment to this ADR before adoption.
- The product can make an accurate residency statement to participants before the provider exists, which is what a privacy policy needs and what a deferred provider decision was blocking.
- Excluding credits from the selection arithmetic means the chosen provider is likely to be one where the owner's credit balance is not largest. The credits still fund the runway; they do not choose the platform.
- The design stays on the portable baseline the operations contract already requires — containers, managed PostgreSQL, object storage, a PostgreSQL transactional outbox instead of a broker — because criterion 6 penalises anything else. This closes off provider-specific managed services that would otherwise be attractive on cost.
- A split between a compute-and-database provider and an artifact-distribution provider is an expected outcome rather than a failure of the rule, and it adds a sub-processor the data processing documentation has to name.
- The budget gate can halt the launch decision. That is deliberate, and it means the D-094 conflict is on the critical path rather than deferred to whoever is on call — which, under D-092, is nobody.
- Nothing here is provisioned. No account, region, database, backup schedule or restore drill exists, and this ADR is a selection procedure rather than evidence that anything runs.

## What would cause this to be revisited

- **A participant population or obligation outside the European Union** that EU-primary residency serves badly — measured latency that damages the product, or a jurisdiction requiring local storage. The response is an additional region under an amended residency statement, never a silent relocation of the primary.
- **A legal entity is formed or counsel is engaged**, which changes the controller analysis, may change the acceptable data processing agreement terms, and is the point at which the residency commitment is checked against advice rather than against caution.
- **The D-094 conflict is resolved** by amending the ceiling, the scale target or the recovery objectives, which changes the step 4 gate and can change the surviving candidate set.
- **A shortlisted provider changes its European Union region availability, its point-in-time recovery granularity, its data processing agreement terms, its sub-processor list or its egress pricing.** Each is an input to a gate, and a changed input reruns the rule rather than grandfathering the previous outcome.
- **A measured restore-elsewhere exercise fails**, which invalidates the criterion 6 score for the selected provider and reopens the ranking at step 5.
- **The provider is selected.** It now is: AWS, under D-361, restricted to managed PostgreSQL, containers and object storage by D-362. What this ADR still owes is the *verified* input to each gate on the date of selection — measured steady-state cost, confirmed point-in-time recovery granularity, the executed data processing agreement and its sub-processor list, and a concrete exit plan. None of those has been measured, and the selection rests on the shortlist assessment recorded above rather than on evidence. D-363 records that the measurement falls due before the credits are consumed.
