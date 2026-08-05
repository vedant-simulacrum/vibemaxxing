# ADR-019: Accepted residual risks

Status: accepted
Date: 2026-08-06
Decision: D-095

## Context

Two risks surfaced during the 2026-08-06 owner review that the product does not currently mitigate, cannot mitigate without a scope change, and is shipping with anyway. The owner directed that both be documented and accepted rather than fixed, and revisited after launch.

This is a risk acceptance record. It is not a reassurance document, and it deliberately does not end each entry on a comforting note. An accepted risk that is written up as though it were half-mitigated is worse than an undocumented one, because it gives a later reader a reason not to look again.

Both risks are registered here with local identifiers because neither maps to an entry in `docs/security/ANTI_CHEAT_ATTACK_CATALOG.md`, whose `AC-A-` series enumerates attacks against ranking integrity rather than harms to participants or leaks across the privacy boundary. This ADR is their register until a normative owner adopts them.

## Decision

**RR-001 and RR-002 below are accepted as residual risk for launch.** Neither blocks launch. Neither is presented anywhere as mitigated, controlled, or acceptable in the abstract — each is acceptable only under the specific compensating controls named here, and only until one of its named revisit signals fires.

No public surface, marketing claim, privacy policy or support answer may state or imply that presence is private-safe or that aggregate accounting is leak-free. Those two sentences are false and this ADR is the reason they are unavailable.

---

## RR-001 — Presence disclosure supports monitoring of a participant

### The risk, precisely

Presence is server-derived from qualifying device activity. D-073 fixes the resolution: a qualifying native pulse every 30 seconds, `idle` after 90 seconds without one, `offline` after 300 seconds. `packages/schemas/state-machine-registry-v1.json` carries `presence-lease` with `absent`, `active`, `idle`, `expired` and `revoked`.

An authorized viewer — a friend, a rival, or a co-member of a board — can read that state repeatedly. Nothing in the design bounds how often, for how long, or against how many targets. A viewer who samples one participant's presence every 30 seconds for a month holds a minute-resolution activity timeline for that person: working hours, sleep schedule, timezone, weekend pattern, an interruption in routine, an absence consistent with travel, and a return. Correlating that timeline against the participant's per-period leaderboard movement sharpens it further, because the movement says how much work happened inside each observed window.

None of this requires an attack. Every read is authorized, every value is one the product intends to publish to that viewer, and no rule is broken. The harm is not in any single disclosure; it is in the aggregate that repeated authorized disclosure composes into, and the product has no concept of that aggregate.

The population this matters for is the ordinary one for social products: an ex-partner, a former colleague, a harasser who reached authorized status before being recognized as a harasser, or a person whose employer is on the same board. Directional blocks, which D-073 and the binding rules already provide, help after the participant knows. This risk is about the interval before they know, which is the interval that matters.

### Why it is not being fixed now

Presence is inside the frozen launch scope. D-059 and D-088 commit to the complete core social product, and D-029 forbids a staged cut. Removing presence is a scope change the owner has declined twice.

Coarsening it to the point where the timeline stops being useful — hourly buckets, a binary "active today", multi-hour hysteresis — removes the property presence exists for, which is knowing that a rival is working right now. There is no setting of the resolution dial that both preserves the feature and defeats the aggregate; a resolution fine enough to feel live is fine enough to timeline.

The mitigations that would actually work are per-viewer presence granularity, per-viewer-per-target read rate limiting with a participant-visible audit of who read their presence and how often, and bounded jitter on transition timestamps. Each is real machinery. None of it is owned by a work unit, none of it is specified, and specifying it now would extend a scope the owner has frozen. The honest statement is that this is unfixed for schedule reasons and not because it is small.

### Compensating controls that exist today

These reduce the population exposed and the content of each disclosure. **None of them reduces the timeline resolution available to an already-authorized viewer, which is the actual risk.**

- Presence is not universally public. Only the global leaderboard view is public by default; friend, rival, private and unlisted views require current viewer authorization, so a stranger cannot sample a participant's presence.
- `private` is an independent visibility policy under D-073, so a participant who suspects monitoring can withdraw presence from all viewers without leaving the product or the board.
- Blocks are directional and independent of friendship, and the threat model already requires immediate presence invalidation on block, revocation or privacy change, so withdrawal takes effect at once rather than at lease expiry.
- The presence record stores account and device, a coarse agent enum, evidence state, a start bucket and privacy status. It carries no project, path, repository name or transcript detail, so the timeline says when and not what.
- Authorization is re-evaluated at delivery and at render rather than only at subscribe, so a revoked viewer stops receiving updates rather than continuing on a stale grant.
- Country leaderboards, which would add coarse geography to the same timeline and materially worsen this risk, are post-launch under D-052.

### Signals that force a revisit

- Any report of stalking, harassment or unwanted monitoring in which presence is named, whether or not the report is substantiated. One report is the signal; a pattern is not required.
- A measured heavy tail in presence read volume per viewer-target pair — a small number of pairs generating a disproportionate share of reads is polling, and polling is the mechanism this risk describes. Instrumenting that count is the cheapest possible early warning and it does not exist today.
- Any proposal to make presence visible to a wider audience, to publish it on the global board, or to retain presence history rather than current state.
- Country leaderboards leaving post-launch status under D-052.
- A participant support request asking who can see their presence, which indicates the disclosure surface is not understood from the product alone.

### Post-launch owner

`docs/security/THREAT_MODEL.md` acquires this risk as a named limitation, and `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md` acquires the per-viewer controls if they are built. Until either adopts it, this ADR is the owner. Under D-091 the accountable person is the single maintainer, which means there is no separate reviewer who will notice the revisit signals — the instrumentation named above is the substitute for that reviewer, and it is not built.

---

## RR-002 — Aggregate token counts are a low-bandwidth channel out of the device

### The risk, precisely

The absolute privacy boundary forbids prompts, responses, transcripts, code, diffs, tool contents, filenames, paths, project and repository names, credentials, embeddings, summaries, classifications, personal insights and content-derived hashes from reaching a server. Only fixed-schema aggregate accounting and integrity claims cross. `packages/schemas/egress-allowlist-v1.json` enumerates the permitted fields.

An allowlist constrains which fields exist. It does not constrain how much information a permitted field carries. Token counts are attacker-chosen quantities at attacker-chosen times, and any such quantity is a channel.

Two limbs, with different reach:

**Device to server.** A compromised adapter, a modified collector, or simply a script the participant runs to drive an agent can modulate token consumption to encode arbitrary data — issuing requests sized to hit target counts in successive minute buckets. The server receives well-formed, correctly signed, deterministically accounted claims and has no way to distinguish encoded traffic from genuine usage, because at the accounting layer there is no difference. The threat model already concedes the general form of this: a device signature proves only that the registered key signed bytes, not that the local source was honest. The channel capacity is low — on the order of a few bits per accounting bucket — and low is not zero, and a covert channel does not need bandwidth to exfiltrate a key or a short identifier.

**Server to public.** Published standings are readable by anyone. A participant's score deltas across periods are a broadcast channel that needs no account to read. This is the limb that matters most, because the recipient is unauthenticated and the product cannot even observe that a read happened. Public granularity is coarser than the internal minute buckets, which lowers the rate substantially, but a participant can modulate across periods indefinitely.

There is also a passive form that requires no adversary at all. Genuine token counts at fine granularity leak the participant's working pattern — the same timeline as RR-001, derived from a different field — and leak the approximate scale of their work. The privacy contract's guarantee is about content, and it holds; this is metadata the guarantee was never about, and the product has not said so out loud anywhere a participant would read it.

### Why it is not being fixed now

The fixes are information-theoretic and each one damages the product's core metric.

- **Quantization** — publishing only coarse buckets — reduces capacity and directly contradicts D-004, which makes raw Token Burn the ranking metric, and D-037, which keeps it unnormalized.
- **Bounded noise** in the manner of differential privacy reduces capacity, and it breaks deterministic rebuild. `AC-A-031` requires reconciliation hashes and a deterministic rebuild that produces identical output, which a randomized publication function cannot provide, and it breaks the append-only correction model that lets an accepted claim be explained to the participant who filed it.
- **Publication delay** reduces the channel's usefulness for interactive exfiltration and does nothing to its capacity, while removing the live rank movement that D-088 and the retention hypothesis behind D-086 depend on.
- **Detecting encoded traffic** requires distinguishing deliberate patterns from genuine ones, which is statistical, and the repository's own rule is that statistical detection stays local-only and advisory under D-053 and never acts against a named individual on its own.

The channel is a direct consequence of the product's purpose. A product whose function is to publish how much you spent cannot also guarantee that the amount you spent carries no information. That is not a defect to be engineered away; it is the shape of the thing.

### Compensating controls that exist today

**None of these reduce channel capacity.** They reduce the number of fields available to carry a payload, not the number of bits in the field that has to exist.

- The egress allowlist is fixed-schema with no free-text, opaque-blob or extension field, so there is no high-bandwidth carrier. An adversary is confined to modulating counts, which is the narrow channel rather than a wide one.
- Content-derived hashes are explicitly forbidden, which closes the highest-capacity encoding available to a compromised collector.
- Accounting is deterministic under a versioned profile, so a count cannot be an arbitrary number the client chose — it has to be produced by consumption the profile accounts for. Encoding therefore costs real tokens, which prices the channel rather than closing it.
- Observability is allowlisted to route template, status class, latency, bytes, reason code, worker type, queue age, database operation class, adapter identity and evidence state, so the channel does not widen inside the server.
- The local privacy inspector lets a participant see what leaves their device, which makes a compromised local component discoverable by the person best placed to notice.
- Public projections are period-scoped rather than minute-scoped, so the unauthenticated read limb runs at a small fraction of the internal rate.
- The confidence weighting of ADR-020 lowers the value of a manipulated count to the attacker's ranking, which discourages one motive. It does not touch capacity, and an attacker exfiltrating data does not care about their rank.

### Signals that force a revisit

- A demonstrated extraction, in this product or in a structurally similar one, that recovers a secret through an aggregate metrics channel.
- Any proposal to increase public temporal granularity below the period scope, to publish minute or hourly series, or to add dimensions — model mix, per-adapter splits, per-hour histograms — to a public projection. Each new dimension multiplies capacity, and each will look individually harmless.
- Any proposal to add a field to `packages/schemas/egress-allowlist-v1.json` that is not a fixed-range enumeration or a deterministically derived count.
- Adoption of a real-time public feed, a public API returning fine-grained series, or webhooks.
- A participant asking what their token counts reveal about them, which indicates the metadata disclosure is not stated anywhere they can find it.

### Post-launch owner

`docs/privacy/PRIVACY_CONTRACT.md` and `docs/security/THREAT_MODEL.md` share this. The threat model's "Fundamental limitations" section is where the device-to-server limb belongs, since it already concedes that a signature does not prove local honesty. The privacy contract needs a plain statement that the boundary is a content guarantee and not a metadata guarantee — that edit is owned by the privacy contract and is a required follow-up rather than something this ADR performs. Under D-091 the accountable person is the single maintainer.

---

## Consequences

- The product ships with two known, unmitigated exposures, and both are recorded where a later reader can find them rather than being discovered during an incident.
- Two claims become permanently unavailable on every surface: that presence is safe from monitoring, and that the privacy boundary prevents information leakage. The boundary prevents *content* crossing, which is a narrower and true claim, and the difference has to survive contact with marketing copy.
- The privacy policy, once written, has to describe both. A privacy policy that omits an exposure the project has recorded internally is a worse legal position than one that describes it, particularly with a personal controller under ADR-017 and no engaged counsel.
- The instrumentation that would surface RR-001's revisit signal — per-viewer-per-target presence read counts — does not exist, so the earliest realistic detection is a participant report. That is an accepted weakness of this acceptance, not an oversight in it.
- Neither risk is a P-1140F semantic finding and neither is closed by this ADR. Recording an accepted risk is not closing a finding.
- Nothing here is implemented, measured or tested. Both risks are described from the specifications; neither has been exercised against a running system, because there is no running system.

## What would cause this to be revisited

- Any signal listed under either risk.
- **The scheduled post-launch review**, which is the condition the owner attached to this acceptance. It is a review of both entries against real usage, not a formality, and its absence is itself a defect.
- **Country leaderboards leaving post-launch status** under D-052, which adds coarse geography to RR-001's timeline.
- **A second maintainer joins** under D-091, which makes a reviewer available for the revisit signals and removes the reason instrumentation was substituting for one.
- **An entry is adopted by a normative owner** — the threat model, the privacy contract, or the social integrity contract — at which point that document governs and this ADR records the history of the acceptance rather than the risk itself.
- **A mitigation becomes cheap.** For RR-001 that is per-viewer read rate limiting with a participant-visible audit; for RR-002 there is no cheap mitigation, and if one appears the analysis above is wrong and should be rewritten rather than amended.
