# ADR-020: Confidence-weighted ranking

Status: accepted
Date: 2026-08-06
Decision: D-082, D-083

## Context

The default ranked metric is accepted live Token Burn, scored additively with no cap. The product deliberately counts authentic intentionally pointless activity. Every launch evidence class is bounded by a device the participant controls. Those three properties compose into a leaderboard that a participant can climb cheaply, and — this is the part that makes it hard — climb *truthfully*: every field of the resulting claim is accurate, the device signed it correctly, the accounting is deterministic, and no privacy rule was broken.

ADR-016 established that no provider offers an individual-scope usage authorization, so there is no external witness for an individual claim, and there is not going to be one at any price the product can pay. The claim cannot be made self-evidencing. That closed the most attractive escape and left the problem where it was.

The structural comparison is uncomfortable and worth stating. A leaderboard that ranks a number the client reports, with no independent witness, is Duolingo's configuration: experience points are submitted by the client with a client-chosen start time, end time and success flag, and functional cheating tools have remained available and maintained for years while the company's public position has been that abuse is rare. Credibility maintained by assertion rather than by mechanism is the failure mode this product is currently walking into.

Strava's most effective control does not transfer. Its machine-learning purge removed millions of mislabelled activities and reprocessed the top efforts on every global segment, and it worked because the model is calibrated against a physical plausibility ceiling — there is a known fastest a human rides. **There is no equivalent ceiling for money.** No upper bound exists on what a person can plausibly spend, which removes the highest-yield control in the prior art. What does transfer from Strava is retroactive reprocessing of the whole ranked history, and this ADR uses it.

Kaggle's durable countermeasure is that the score deciding the outcome is computed on data the competitor never touched, with the public leaderboard as a deliberate decoy. The attack it defends against needs no cheating at all: adaptive probing of public feedback moved a competitor from roughly rank 146 to rank 6 on a large competition without ever reading the data. The transferable rule is that the client-visible, client-influenced number must not be the number that determines standing. This ADR takes that rule and applies it in the weaker form the product's constraints allow.

The model built for exactly this problem is Sweatcoin's and STEPN's: both rank a client-measured metric that converts to money, and both separate the *claimed* quantity from the *credited* quantity and gate value on a continuous trust score rather than a binary ban.

- **Sweatcoin** converts approximately 65% of phone-registered steps into currency. The payout is deliberately lossy relative to the client's claim, as a standing property rather than a penalty.
- **STEPN** assigns every account a Turing Score on a 0–120 scale starting at 100. A score of 81 or above permits withdrawal; 80 or below blocks it. Abnormal movement costs 10 points, each additional device costs 5, a confirmed bot hack is a permanent ban, and a score below 50 routes to manual review.

The repository already contains the rule this implements and has never implemented it: *public evidence status and competitive eligibility are assigned by the server verifier, never selected by the client.* It has been an authorization rule. This ADR makes it a weighting.

## Decision

**Public rank is computed on Credited Token Burn, not on Token Burn.** Credited Token Burn is Token Burn multiplied by a server-assigned confidence weight derived from the awarded evidence profile and the ranked-identity trust state.

### Naming, so the two figures are never confused

Three terms, used consistently in schemas, SQL, API, UI copy and this repository's prose:

| Term | Field name | What it is |
|---|---|---|
| **Token Burn** | `token_burn_total` | The accepted, immutable, unnormalized accounting quantity. Unchanged by this ADR. |
| **Confidence weight** | `confidence_weight_hundredths` | A server-assigned integer in hundredths, between 25 and 100 inclusive. |
| **Credited Token Burn** | `credited_token_burn` | `Token Burn × confidence weight`. The quantity `rank()` orders. |

"Score" alone is banned as a field name and as UI copy, because it is the word that lets the two figures merge. Every surface that shows a number says which of the two it is showing.

Token Burn remains exactly what D-004 and D-037 make it: raw, unnormalized across model capability, and immutable once accepted. The weight is applied at ranking projection, never at claim acceptance. No accepted claim is rewritten, and the append-only rule is untouched.

### The discount function

All arithmetic is integer. No floating point appears anywhere in this path, because a rebuild has to reproduce a generation exactly and floating-point determinism across a Rust producer and a Go consumer is the most reliable source of divergence available.

```
w = max(25, floor(w_profile × w_trust / 100))
credited_token_burn = floor(token_burn_total × w / 100)
```

`w_profile` and `w_trust` are integers in hundredths. `w` is clamped below at 25 and cannot exceed 100, because neither factor exceeds 100.

**Evidence factor `w_profile`,** keyed by the awarded `profile_id` from `packages/schemas/evidence-profile-policy-v1.json`:

| Awarded profile | `public_state` | `w_profile` |
|---|---|---|
| `hardened-source-bound-v1` | `hardened` | 100 |
| `standard-competitive-v1` | `standard` | 70 |
| `imported-v1` | `imported` | not ranked |

**Trust factor `w_trust`,** keyed by the current state of the `ranked-identity-eligibility` machine in `packages/schemas/state-machine-registry-v1.json`:

| State | `w_trust` | Reasoning |
|---|---|---|
| `eligible` | 100 | The ordinary case. |
| `consolidating` | 100 | D-070 consolidation is administrative, not an integrity signal. |
| `reversed` | 100 | A successful appeal restores the participant fully. |
| `unverified` | 50 | Not yet resolved to a person under D-054, and not yet past the D-081 provider-account age gate. |
| `investigating` | 75 | An open case is a signal and not a finding. Reversible by construction. |
| `restricted` | 25 | Sanctioned under D-084. |
| `appealed` | the value in force when the appeal opened | Appealing neither adds nor removes penalty. |
| `retired` | not ranked | No entry is produced. |

`appealed` requires one additional persisted field on the ranked-identity aggregate: the `w_trust` in force at the moment the appeal was opened. Without it the weight would depend on which state the appeal was entered from, which is not recoverable from the current state alone. This is the only new persisted field this ADR introduces.

Worked values: `hardened` + `eligible` gives 100. `standard` + `eligible` gives 70 — close to Sweatcoin's conversion rate, arrived at independently and worth noticing as corroboration rather than as derivation. `standard` + `investigating` gives 52. `standard` + `restricted` computes to 17 and clamps to 25.

### Why the floor is 25 and not zero

A weight of zero removes a participant from the standings without saying so. That is exactly the silent removal D-084 rejected, and it destroys the appeal right in the same way: a participant whose entry has vanished cannot tell whether they were sanctioned, whether the board is broken, or whether they simply stopped competing. The private notice required by D-084 is the signal; the floor keeps the board from contradicting it.

The floor also bounds the damage of a wrong sanction. A false `restricted` costs a participant three quarters of their standing and is fully recoverable on appeal. A false zero costs them their presence in the product, and the prior art is unambiguous that graduated reversible sanctions outperform removals — Niantic reports that more than 90% of players who received a first warning stopped cheating, the strongest efficacy figure in the evidence set, and it works because the player is told.

### Why the ceiling is 100

The weight only ever discounts. There is no bonus multiplier for strong evidence, because a multiplier above 1 would let evidence quality manufacture burn that was never spent — which breaks the D-004 and D-037 property that Token Burn is a raw unnormalized volume, and would put Credited Token Burn permanently out of proportion with Estimated Cash Burn, which is derived from the same consumption through a priced dataset. Strong evidence earns the absence of a discount, which is the entire prize.

### Interaction with the evidence policy

`packages/schemas/evidence-profile-policy-v1.json` is **unchanged** by this decision. Its seven dimensions — `source`, `capture`, `accounting`, `device_key`, `continuity`, `environment`, `freshness` — its three profiles, its three-step `downgrade_order` of `hardened-source-bound-v1` → `standard-competitive-v1` → `private-analytics`, and its five rules all stand exactly as written.

The weight is a lookup keyed by the **awarded** `profile_id`, which is the output of that evaluation. It deliberately does not read the seven dimensions itself. Composing those dimensions a second time, differently, would create two competing evaluations of the same inputs with no stated precedence, which is the condition the repository's duplication rule exists to prevent. The downgrade order is the accepted composition; the weight consumes its result.

Three consequences follow from the policy's existing rules and are worth stating because they mean less new machinery than it first appears:

- `source-E5` maps to `imported-private-only`, and `approximate-accounting` maps to `private-analytics`, so anything that reaches a weight is already competitively eligible. The weight never has to decide eligibility; the policy already did.
- `client-requested-public-state` maps to `ignore-client-field`, so the client cannot influence its own weight through the claim. This is the binding rule restated as arithmetic.
- The `E1-R` provider-retrieved organization aggregate of ADR-016 and D-078 explicitly never alters raw score. It correspondingly never enters the weight. `E1-R` corroborates a board's aggregate; it is not evidence about an individual and it does not become so by way of a multiplier.

### Interaction with the state machine registry

`packages/schemas/state-machine-registry-v1.json` is **unchanged**. Two machines are read and neither gains a state:

- `ranked-identity-eligibility` supplies `w_trust`. Every one of its eight states has a defined treatment in the table above, so no state produces an undefined weight.
- `ranking-projection` — `building`, `validating`, `active`, `superseded`, `failed` — is where the weight is applied. Weighting happens during `building`; `validating` checks that every entry's recorded weight matches a recomputation from the recorded inputs.

A trust-state transition does not mutate a published generation. It supersedes it: a new generation is built with the new weight, the previous generation moves to `superseded`, and both are retained. This is Strava's retroactive-reprocessing property, which is the part of that prior art that does transfer, and it is how a successful appeal restores a participant's historical standings rather than only their current one.

Generation rebuild here is a ranking-integrity operation over retained generations. It is **not** a mechanism for the erasure conflict recorded in D-085, which remains undecided and is not decided by this ADR.

### Binding and determinism

The weight table lives in a versioned policy file with a content digest, and that digest is bound into the `rules_digest` of `packages/schemas/ranking-view-v1.schema.json`, alongside the `evidence_policy_digest` and `pricing_dataset_digest` the schema already requires. A published generation therefore records which weight table produced it, and a rebuild that reproduces the generation proves it used the same table. Changing a weight produces a different `rules_digest` and therefore a different `ranking_view_id`, which makes a silent recalibration impossible — the identifier changes whether or not anyone announces it.

Each ranking entry persists `token_burn_total`, `confidence_weight_hundredths`, `credited_token_burn`, the awarded `profile_id` and the trust state used. Every entry is independently recomputable from its own recorded inputs, which is what the `validating` step checks and what makes the participant-facing explanation below possible.

### Visibility

**To the participant, about themselves: fully visible.** Their own surface shows Token Burn, the confidence weight, both factors separately, and the reason any factor is below 100 — the awarded evidence profile with the dimension that limited it, and the trust state with a reference to the notice that produced it. A participant who is discounted and cannot see that they are discounted has no appeal right in practice, whatever the appeal machinery says.

**To the public: the credited figure and the evidence profile only.** Public surfaces publish Credited Token Burn and the participant's public evidence label — Standard, Hardened or Imported, which D-008 already makes public. Public surfaces do **not** publish the composite weight, the trust factor, or the trust state.

**Token Burn is not published on public surfaces.** This is a change and it is the price of D-084. If both Token Burn and Credited Token Burn were public, anyone could compute the weight by division; the evidence profile is already public, so the trust factor would follow immediately, and the sanction would be public — which is exactly what D-084 forbids. `docs/product/PRODUCT_SPEC.md` currently permits profiles to expose Token Burn, and that permission needs narrowing to the participant's own surface and to viewers they authorize. That edit is owned by the product specification and is a required follow-up rather than something this ADR performs.

**The residual inference leak, stated rather than papered over.** An observer who watches a participant's published Credited Token Burn across periods sees a discontinuity when a trust state changes, and no evidence-profile change explains it. From that they can infer that something happened. The design does not prevent this and cannot: any weighting visible in its output leaks its input to an observer patient enough to difference the series. What it does is keep the inference deniable — there is no marker, no badge, no label, and an ordinary drop in activity looks the same. That is a materially weaker property than secrecy, and it is the honest one.

### What this does to farmability

**This mitigates the finding. It does not eliminate it, and the reason is worth being exact about.**

The confidence weight discounts by *evidence quality*. Evidence quality measures capture fidelity — whether the counts were observed by a certified source under a certified accounting profile on a continuously attested device. It does not and cannot measure *sincerity*. A participant who instruments their setup properly, runs a certified adapter on an enrolled device with unbroken continuity, and then spends genuine money on genuinely pointless work is awarded `hardened-source-bound-v1`, is `eligible`, is weighted 100, and is ranked at full value. Every part of that is working as designed, because D-032 says authentic intentionally pointless activity counts.

So the weighting addresses the fabrication limb: burn that is invented, weakly captured, replayed, or produced under a discontinuous or uncertified configuration is discounted, and discounted the further the further it sits from a clean capture. It does not touch the sincerity limb at all.

The reason nothing here can touch the sincerity limb is the one Strava's success illuminates by contrast: their model works against a physical plausibility ceiling, and money has none. There is no spend figure a person cannot plausibly have incurred. Any control that tried would have to guess at intent, which is the guess this product has decided not to make.

What weighting genuinely buys is a change in the cost curve. Cheap farming — fabricate a number, replay a claim, run an uncertified generator — now yields a discounted position rather than a full one. Expensive farming — actually spend the money, properly instrumented — yields a full position and costs what the tokens cost. The floor on farming moves from approximately zero to the provider's price, which is the same shift ADR-016 identified at organization scope. That is a real improvement and it is not a solution.

### Calibration is provisional by construction

The numbers 100, 70, 50, 75 and 25 are chosen by argument and not by measurement, because there is no traffic to measure. They are anchored on two external points — Sweatcoin's roughly 65% conversion and STEPN's blocking threshold at the low end of a 0–120 range — and on the internal requirement that the floor be nonzero and the ceiling be exactly the undiscounted case. They are recorded in a digest-bound table specifically so that recalibrating them is visible, versioned, and forces a new `ranking_view_id`.

## Consequences

- The public standing is no longer the raw client-reported figure. This is the Kaggle rule in the weakest form the product's constraints permit: the client cannot select the multiplier applied to what it reports, and the server assigns it.
- The rule that public evidence status and competitive eligibility are assigned by the server verifier acquires a mechanism. It has been an authorization statement with nothing consuming it.
- Evidence tiers stop being cosmetic. Hardened attestation now buys a measurable ranking outcome without introducing a second eligibility-filtered board, which was the alternative the owner declined.
- `docs/architecture/SERVER_API_DATA_AND_RANKING_CONTRACT.md` currently states that evidence badges never alter raw score unless the selected leaderboard explicitly filters eligibility. The first half stays true and the second half is now misleading, because evidence affects standing without any board filtering. That sentence needs restating as: evidence profiles never alter Token Burn, and they determine the confidence weight applied to Credited Token Burn at projection. The edit is owned by that contract and is a required follow-up.
- `docs/product/PRODUCT_SPEC.md` needs the Token Burn publication narrowing described above.
- One new persisted field is introduced — the trust factor in force when an appeal opened — and one new versioned, digest-bound weight table. No existing schema changes.
- Sanction reversal becomes a ranking operation with a defined shape: a new generation supersedes the affected one and both are retained. The appeal lifecycle machine and the `retracted` exceptional state stay live rather than becoming unreachable.
- Every ranking entry becomes independently explainable to the participant it describes, from data recorded on the entry, which is what makes an appeal about a number rather than about a feeling.
- The projection worker acquires two more inputs and a validation step. It stays integer-only, which keeps deterministic rebuild and reconciliation hashes intact.
- The product acquires an honest public sentence it did not have: standings are weighted by evidence confidence, and the weighting reduces the value of poorly evidenced burn. It does not acquire the sentence that the leaderboard is not farmable, and that sentence remains unavailable.
- Nothing here is implemented. No weight table, no projection code, no entry field and no participant-facing explanation exists.

## What would cause this to be revisited

- **A provider ships an individual-scope usage authorization or a signed per-claim receipt.** That makes the claim self-evidencing, which is a strictly better answer than weighting, and it would reduce this design to a fallback for participants without provider coverage. ADR-016 and D-078 carry the same trigger.
- **Measured evidence that weighting misranks honest participants** — for example, that a common legitimate configuration cannot reach `hardened-source-bound-v1` and is therefore permanently held at 70. That is a calibration failure, and the response is to recalibrate the table or to fix the profile minimums, not to remove the weighting.
- **Measured farming that the weighting does not touch**, which is the expected outcome for the sincerity limb and would confirm rather than refute this analysis. A response to that requires the capped, normalized or reserve-settled ranking designs this ADR did not choose, each of which contradicts an accepted decision and therefore needs its own.
- **The `investigating` weight is shown to be punitive before a finding.** A weight below 100 on an open case is a penalty applied on suspicion. It is set at 75 rather than lower for that reason, and if appeals data shows a meaningful share of investigations closing without a finding, 75 is too low and should move toward 100.
- **The inference leak proves to be a practical sanction disclosure** — a third party reliably identifying sanctions by differencing published series. The response is not to hide the number further, since that trades one honesty for another; it is to reconsider whether D-084's public silence is achievable at all under any weighted design, and to say so.
- **A ranking function change that introduces coupling between participants** — curves, percentiles, relative shares, or any rating derived from pairwise comparison. Coupled functions are separately attackable: published work has shown that ranks in a large pairwise-comparison arena can be moved by injecting a few hundred votes against millions of historical ones, without touching the target's own records. The additive, uncoupled function this ADR weights does not have that property, and losing it is a reason to revisit rather than a detail.
- **Calibration against real traffic**, which is the first opportunity to replace argued numbers with measured ones and is expected to change at least one of them.
