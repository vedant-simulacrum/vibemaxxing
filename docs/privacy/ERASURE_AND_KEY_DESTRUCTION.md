# Erasure by Cryptographic Tombstone and Key Destruction

Status: normative planning contract. **Not reviewed by counsel. Counsel review is an unmet release gate under D-109.**
Version: 1
Decisions: D-085, D-210, D-211, D-212, D-213, D-214
Reasoning: `docs/decisions/ADR-022-ERASURE_BY_KEY_DESTRUCTION.md`

This document is the single normative owner of what an Article 17 erasure does to server-side data. `docs/privacy/DATA_MAP.md` is the record of processing and states the retention windows; this document states the mechanism those windows describe. `packages/schemas/planning-schema.sql` is the persistence authority and `packages/schemas/erasure-record-v1.schema.json` is the machine-readable form of the signed record.

Nothing here is implemented. No key exists, no erasure has been executed, no restore has been drilled, and no infrastructure is provisioned.

## The problem this resolves

Two accepted rules point in opposite directions.

D-085 decides the outcome: an erasure request removes the account, the ranked identity, and that identity's historical ranking entries, so that no erased participant remains visible or reconstructible in any published standing.

Against that, `AGENTS.md` binds the product to append-only history — accepted claims and historical facts remain immutable, and corrections, consolidation, deletion effects and reversals are appended rather than applied in place — and `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md` requires immutable retained ranking generations with durable cursors. Deleting a row out of a sealed generation invalidates its content hash, changes every position after it, and breaks every cursor a client is holding.

The mechanism the owner chose reconciles them by changing what is deleted. **Nothing is deleted from the sealed side. A key is destroyed and a signed record is appended.** The hash chain survives because no hashed byte changes. The cursor survives because no position moves. Identifiability does not survive, because the only stored binding between the retained pseudonym and the person is ciphertext under the destroyed key.

## What is deleted and what is retained

The split is by whether the record is a live personal record or a published historical standing. It is not negotiable per request and it is not configurable.

`packages/schemas/data-disposition-v1.json` is the exhaustive authority: it carries one row for every persistence owner in `packages/schemas/planning-schema.sql`, and a planning validator fails when a table is missing from it. The three groups below name the significant members of each `erasure_action` class rather than repeating the registry, and where the two disagree the registry is correct and this section is the defect.

**Deleted outright, within 30 days of the request.** `accounts`, `account_handles`, `linked_identities`, `web_sessions`, `session_families`, `native_sessions`, `recovery_codes`, `optional_authenticators`, `oauth_transactions`, `devices`, `device_keys`, `device_lineages`, `device_key_events`, `device_enrollment_grants`, `adapter_installations`, `claim_challenges`, `device_sequences`, `claims`, `claim_payloads`, `claim_corrections`, `checkpoint_receipts`, `evidence_assessments`, `verifier_appraisals`, `cost_interpretations`, `minute_scores`, `period_scores`, `profiles`, `friend_requests`, `friend_edges`, `blocks`, `rival_edges`, `board_memberships`, `presence_leases`, `notifications`, `notification_preferences`, `exports`, `export_artifacts`.

Claims are included, and that is a deliberate exception to the immutability rule rather than an oversight. Immutability protects an accepted claim against *mutation*: nobody edits a number after the fact. Article 17 is a lawful terminal event, and the append-only obligation is discharged by the tombstone that records it. `docs/privacy/DATA_MAP.md` already promised the deletion; this document states the consequence, in the rebuild section below.

**Retained, pseudonymous, key-destroyed.** `ranking_projection_generations`, `ranking_entries`, `score_snapshots`, `score_contributions`, `ranking_movement_events`, `erasure_domains`, `erasure_domain_links`, `erasure_keys`, `erasure_records`, `deletion_tombstones`.

**Retained, unlinked.** `outbox_events`, `worker_checkpoints`, `audit_events`, `moderation_cases`, `moderation_actions`, `moderation_effects`, `appeals`, `appeal_decisions`, `deletion_jobs`, `deletion_effects`. Their retention windows are in `packages/schemas/data-disposition-v1.json`, which is the machine-readable authority, and each carries either a digest or an identifier whose subject row is gone.

## Key material

### What exists

Two kinds of key, and they are not interchangeable.

**The domain key.** One AES-256-GCM key per erasure domain, held in `erasure_keys`. An erasure domain is one ranked-identity lineage. It is the smallest unit that can be destroyed independently, because erasure operates at ranked-identity granularity; a key per entry would multiply the register by six board scopes times six periods times every generation and buy no additional granularity.

The domain key encrypts exactly one thing: `erasure_domains.bound_subject_ciphertext`, which is `AES-256-GCM(key, account_id ‖ lineage_id)` with `erasure_domain_id` as associated data and a 12-byte nonce. That is 32 bytes of plaintext and a 16-byte tag, which is why the column is fixed at 48 bytes. It encrypts nothing else, ever. A domain key that protected a second thing would make destruction destroy that second thing too, and the blast radius of an erasure has to be exactly the erasure.

**The subject index key.** One server-wide HMAC-SHA-256 key producing `erasure_domains.subject_lookup_digest = HMAC(K_index, account_id)`. It exists so `/rank/me` is an index lookup rather than a table scan. It is not destroyed by any erasure, and it does not need to be: its preimage is a 128-bit identifier that the erasure deletes, and a digest whose preimage is high-entropy and gone confirms a guess but produces nothing on its own. UUIDv7 encodes a millisecond timestamp, so the unguessable part is 74 bits rather than 122; that is still not searchable, and it is stated here rather than left implied.

### Where it lives

The domain keys live in a keyring that is logically separate from the ranking data and physically separate from it wherever the budget permits. `packages/schemas/planning-schema.sql` declares `erasure_keys` in the same contract as everything else because the contract is one file; the deployment target is a distinct PostgreSQL database with its own credentials, reachable only by the erasure and projection roles.

**Co-locating the keyring with the ciphertext gives no confidentiality at all.** An attacker who reads the database reads the keys and the ciphertext together. That is not a defect in this design, it is a statement of what the design is for: crypto-shredding here is a *deletion* control, not a confidentiality control, and it must never be presented as encryption at rest.

D-093 caps hosted spend below 100 USD per month and D-094 already records that cap as being in unresolved conflict with the recovery objectives and the scale target. A separately backed keyring is a cost input to that unresolved conflict. The mechanism works either way; what changes is the length of the restore window in the backups section below.

### Rotation

**The domain key is never rotated, and destruction is its only state change.** A rotation that keeps the old key alive gains nothing, because the old key still opens the ciphertext. A rotation that destroys the old key *is* an erasure. There is no volume-based rotation pressure, because the key encrypts one 32-byte plaintext once. The key row therefore has exactly two lifecycle states and they are expressed as a constraint rather than as a vocabulary:

```sql
check ((key_material is null) = (destroyed_at is not null))
```

A row that claims destruction while retaining material cannot exist, and neither can a row that has lost its material without a destruction time to answer for it.

The subject index key is rotated on the ordinary schedule for a long-lived MAC key. Rotating it rewrites every `subject_lookup_digest`, which is a bulk update of one column on one table and touches nothing else.

## What destruction physically means

Destruction is a sequence, not an instant, and each step is stated because the difference between them is the difference between an honest claim and a marketing one.

1. **T+0, one transaction.** `update erasure_keys set key_material = null, destroyed_at = now() where key_id = ...`, insert the `erasure_records` row with the pre-destruction `key_commitment`, insert the `deletion_tombstones` row, and delete the live personal rows listed above. One transaction, serializable. After commit, every live read path resolves nothing for that domain.
2. **T+0, mirror.** The erasure record is written to the erasure journal described below. The transaction is not acknowledged to the participant until the mirror is durable.
3. **Heap.** PostgreSQL's update wrote a new tuple version and left the old one, which still contains the key bytes, on the heap. The old version is removed by vacuum. `erasure_keys` is small and is vacuumed on a dedicated schedule rather than left to autovacuum's thresholds, and destruction is not reported complete for the heap until that vacuum has run.
4. **Write-ahead log and backups.** The pre-image is in the WAL, and the WAL is in the archive, and the archive backs point-in-time recovery. It ages out with the 35-day backup retention and not before. There is no way to redact it: PITR is physical and cannot exclude a row.
5. **Replicas.** A physical replica replays the same WAL and holds the same heap, so it clears on the same schedule. A replica that is not replaying — a detached copy, a forensic snapshot, a developer restore — is outside this sequence entirely and is governed by the rule that no such copy is taken.

So: **cryptographically non-attributable to every live read path at T+0, physically complete at T+35 days.** The 35 days is the same window `docs/privacy/DATA_MAP.md` already states for backups, which is not a coincidence and is not an improvement on it.

What the mechanism does improve is the *shape* of the failure. Without it, a restore inside the window resurrects a handle attached to a published standing. With it, a restore inside the window resurrects an opaque pseudonym attached to a published standing, plus a separate key row that the journal replay destroys again before the instance takes traffic. The degradation is from "the erased participant is back on the leaderboard under their name" to "a row remains countable and nameless". That is the whole benefit, stated at its real size.

## Proving destruction afterwards

`erasure_records` is an append-only, hash-chained, signed log.

- `chain_sequence` is dense and unique from 1; `previous_record_digest` is the previous record's digest and is null only at sequence 1, which is a database constraint rather than a convention.
- `record_digest` is SHA-256 over the deterministic CBOR encoding of the record body, under the Core Deterministic Encoding profile D-191 fixes for the whole protocol.
- `cose_sign1` is a COSE_Sign1 over that digest with Ed25519, algorithm identifier −19 per D-190, verified under the ZIP-215 rules D-192 pins. The erasure log uses the same signing profile as the evidence protocol so that one verifier implementation covers both.
- `key_commitment` is SHA-256 over `key_id ‖ key_material`, computed before destruction and retained after it.

The commitment is what makes destruction checkable. Given a candidate key, anyone holding the log can test whether it is the key that was destroyed. Nobody can run the test in the other direction, because a 256-bit uniformly random preimage is not searchable. So the log proves *which* key was destroyed and proves the log has not been rewritten since.

**It does not prove that no copy of the key exists anywhere.** No mechanism can. A signed erasure record is evidence of the controller's own act, attested by the controller. An auditor can verify the chain, verify the signature, verify that `erasure_keys.key_material is null`, and verify that the constraint above makes the alternative unrepresentable — and then has to trust that no copy was taken before destruction. That is the honest ceiling and no document in this repository may state a stronger one.

## Sealed generations

### What survives

A sealed generation is `ranking_projection_generations` in state `active` or `superseded`, with `sealed_at` and `content_hash` set. Its entries are `ranking_entries` rows keyed `(ranking_view_id, generation, position)`.

An erasure changes none of it. Specifically, all of the following are unchanged by an erasure that affects an entry in the generation:

- every `position`, including the positions of entries after the erased one;
- `token_burn_total`, `credited_token_burn`, the three weight columns, `evidence_class`, `evidence_profile_id`, `trust_state_at_projection` and `first_reached_at` on every entry, including the erased one;
- `content_hash`, `sealed_entry_count` and `sealed_total_credited_token_burn` on the generation;
- `snapshot_id` on `score_snapshots`.

The row stays countable. Rank arithmetic, participant counts, tie behaviour and the reconciliation hash are all computed over a row set that erasure does not touch.

`content_hash` covers the entry rows and nothing that can change afterwards: no handle, no account identifier, no appraisal detail. That is what lets a handle rename, a block, a visibility change and an erasure all leave the hash intact, and it is the reason `snapshot_id` remains a valid name for the generation after an erasure inside it.

### What it projects to

An entry projects through the domain, and the domain resolves only while its key lives.

```sql
select e.position, e.credited_token_burn, e.evidence_class
from ranking_entries e
join erasure_domains d using (erasure_domain_id)
join erasure_keys k using (key_id)
where e.ranking_view_id = $1
  and e.generation = $2
  and e.position > $3
  and k.destroyed_at is null
order by e.position
limit $4;
```

The handle is resolved separately, per surviving entry, by opening `bound_subject_ciphertext` and reading the current handle from `account_handles`. Resolving the handle at read time rather than freezing it into the snapshot is also what lets every display boundary recheck current authorization instead of replaying a historical projection.

**An erased entry is not rendered.** It contributes no item to a page, no handle, no figure and no placeholder. The public surface does not say that position 7 was erased, because saying so would publish the fact of an erasure against a position that a third party's archived copy of the board already names.

The consequence a client sees is that a page can return fewer items than it asked for while more items remain. `LeaderboardPage` therefore reports the position range the page covered, so a client can distinguish "the board ended" from "this window contained suppressed entries", and pagination continues from the position anchor rather than from the item count. The OpenAPI document is owned by another work unit and does not yet carry that field; until it does, this contract states the projection and the API under-describes it.

### Aggregates are frozen at seal

`sealed_entry_count` and `sealed_total_credited_token_burn` are written once, when the generation seals, and are never recomputed.

This matters more than it looks. If the published aggregate for a generation were recomputed after an erasure, an observer who recorded the aggregate before and after would recover the erased participant's exact credited figure by subtraction, and — with an archived copy of the board — attach it to a name. Freezing the aggregate means the published totals stay consistent with the moment they described and stop being a differencing oracle. It is the same class of leak ADR-020 records for the confidence weight, closed the same way: refuse to publish the second observation.

The cost is that the published participant count for a historical generation includes participants who have since been erased. That is correct and it is what the count meant when it was taken.

### Rebuild after an erasure

ADR-020 makes generation rebuild the mechanism for a trust-state change: a new generation supersedes the affected one and both are retained. That still works, with one restriction.

**A generation that carries an erasure is no longer rebuildable from source claims,** because the erased participant's claims are deleted. Its sealed rows are the only remaining authority for it. A rebuild that spans such a generation carries the erased entries forward verbatim from the sealed rows rather than re-deriving them, and the hash comparison covers the full row set including them. Determinism is preserved; derivability is not.

This is a real and permanent cost of Article 17 against a rebuildable projection, and it runs one way: once a generation has an erasure in it, it can be verified against its hash forever and can never again be independently re-derived from the claim ledger. The alternative — refusing to delete the claims — is not available, because the claims are the participant's personal data and the erasure right is what is being exercised.

## Cursors

A durable cursor is the part of this design most likely to break, so it is specified before anything reads it.

**A cursor anchors on `(ranking_view_id, generation, position)` and carries no subject identifier.** It is an opaque token — the deterministic CBOR encoding of that triple plus the page size and an issue time, with a MAC under a server key so a client cannot forge a position. It does not contain an account identifier, a handle, a score, or a first-reached timestamp. The previous contract put an account identifier and a score inside a token the client keeps indefinitely; that is a personal-data leak into client storage and it is removed by this change independently of erasure.

Positions inside a sealed generation are immutable. That single property is what makes every case below have an answer.

**A client holding a stale cursor whose anchor entry was erased gets the next page, starting immediately after that position, with the erased entry absent and every surviving entry at the position it always had.** No error, no restart, no renumbering. The anchor is a number, and the number is still there whether or not the row behind it renders.

The other cases, stated exactly:

- **Anchor entry erased, cursor still on the active generation.** As above. The page continues from `position > anchor`.
- **Generation superseded while the cursor was held.** The cursor stays valid and reads the generation it names, which is retained. The response reports the generation it served and the current active generation, so a client can decide whether to continue the consistent historical page or restart on the current one. It does not silently jump generations, because jumping would show the client a mixture of two rank orders.
- **The ranking view was retired and its generations purged.** The cursor returns the restart outcome. This is the only case that produces one, and it is a retirement event rather than an erasure event. Sealed generations carry no clock-based retention: `packages/schemas/data-disposition-v1.json` classifies them as retained indefinitely and non-personal, which they become when the key is destroyed.
- **Filter or scope changed.** The cursor names a `ranking_view_id`, which is a digest over the full rule set, so a different filter is a different view and a cursor from one is not accepted by the other. Restart outcome.
- **Viewer authorization changed** — a block appeared, a board membership ended, a profile went private. The page is re-projected under current authorization on every request, so entries disappear from a friends or board page between two requests with a stable cursor. Positions still do not move; only rendering changes.

`snapshot_id` is unaffected by an erasure. A client that pinned a snapshot identifier keeps reading the same generation, the same content hash and the same positions, with one fewer rendered item. A snapshot identifier is invalidated only by purge, never by erasure.

## Backups and point-in-time recovery

`docs/privacy/DATA_MAP.md` commits to backups and PITR archives retained 35 days, and to restores reapplying deletion tombstones before serving traffic. That commitment is executable as follows.

### The erasure journal

Every `erasure_records` row is mirrored, before the participant is acknowledged, to an append-only journal held outside the database backup set. The journal is the same hash chain: each entry is the signed record body plus the identifiers the replay needs, which are the `key_id`, the `erasure_domain_id`, and the primary keys of the live rows the transaction deleted.

The journal therefore contains an account identifier for a participant who has been erased. That is unavoidable — a replay that cannot name what to delete cannot delete it — and it is bounded rather than argued away:

- **journal retention is 36 days**, one day longer than the 35-day backup retention, because after the backup window no restore can resurrect anything the journal would need to re-erase;
- the invariant `erasure_journal_retention_days = backup_retention_days + 1` is recorded in `packages/schemas/policy-defaults-v1.json` and is checked by the planning validator, so the two cannot drift apart;
- the journal holds identifiers and digests only. No handle, no provider subject, no token count.

### The restore procedure

A restore is not complete when the database is up. It is complete when the reapply has run.

1. Restore the cluster to the target point.
2. Start PostgreSQL with application connections refused. Only the reapply role may connect.
3. Read the journal from its head backwards to the restore point, verifying the chain and every signature. A journal that does not verify aborts the restore.
4. For each record, in chain order: confirm `erasure_keys.key_material is null` for its `key_id` and destroy it if the restore brought it back; re-delete the live rows the record names; confirm the `deletion_tombstones` row exists and insert it if the restore predates it.
5. Vacuum `erasure_keys`.
6. Verify: for every journal record, the key is destroyed, the tombstone exists, and no live personal row for the subject remains. Any failure aborts.
7. Write the `erasure_restore_receipts` row with the journal head digest and the counts.
8. Admit application traffic, and record `traffic_admitted_at`.

The ordering is enforced rather than documented:

```sql
check (traffic_admitted_at is null or traffic_admitted_at >= reapply_completed_at)
```

A receipt that admits traffic before the reapply completed cannot be written. That does not stop an operator from admitting traffic without writing a receipt, and no schema constraint can; what it does is make the absence of a receipt the thing an audit looks for.

### The window in which a restore can resurrect an identifier

Stated plainly, because this is the question the mechanism exists to answer.

**Between step 1 and step 6, the restored cluster contains a live domain key and therefore contains the means to re-identify every entry in every generation that key covers.** The window is the duration of the journal replay, from restore completion to reapply verification. During it the cluster serves no application traffic, but an operator with database credentials can read it.

The window is bounded by the replay, which is linear in the number of erasures since the restore point and is expected to be seconds. It is not zero and it is not eliminable: PITR restores what was in the WAL, and what was in the WAL includes the key.

Two cases sit outside the window and are worse:

- **A restore performed without the reapply.** The identifiers stay live for as long as that cluster does. Nothing in the schema prevents it. The control is that the reapply is the only supported restore path and the receipt is the evidence it ran.
- **A copy taken from the restored cluster during the window.** It is outside the mechanism entirely, and the only control is that no such copy is taken.

Beyond 35 days no restore can resurrect anything, because no backup that predates the erasure still exists. That is the outer bound on every statement in this section, and it is the same bound `docs/privacy/DATA_MAP.md` and `PRIVACY.md` already state.

**No restore drill has been run.** Nothing is provisioned. The procedure above is a specification and not evidence, and `docs/operations/DATA_LIFECYCLE_AND_RECOVERY.md` already records that a deletion process is not valid until a restore test proves deleted identity data does not reappear. That test does not exist.

## The limits, stated

Six of them, in descending order of how much they matter.

1. **This is computational infeasibility for the controller, not metaphysical erasure.** The retained rows still exist and still describe a person. What is gone is the controller's means of saying which person. Recital 26 asks whether identification is reasonably likely by means available to the controller or another person; after destruction it is not likely for the controller. It is a defensible position, not a certain one, and D-109's unmet counsel review covers exactly this kind of judgement.

2. **Article 17(2) is not discharged by any of this.** Having made the standing public, the controller must take reasonable steps to inform other controllers processing it. The steps committed to are unchanged from `docs/privacy/DATA_MAP.md`: removal from the live surface within 30 days, removal from backups within 35, `noarchive` and removal requests to the search engines that expose an interface, and a plain statement that a third party who copied a standing before erasure is outside the controller's reach. A key destroyed on this side does nothing to a copy on that side.

3. **An observer who archived the board before the erasure keeps the attribution permanently.** They hold handle, position and figure. The retained entry still holds position and figure. Joining them is trivial. This is the reason an erased entry renders nothing at all rather than rendering a figure without a name, and it is still not a fix.

4. **The retained rows remain a coherent per-subject series.** One pseudonym runs through every generation for one lineage, so the retained data still singles out an individual across time even with no name attached. Crypto-shredding removes attribution, not singling out.

5. **Physical destruction lags logical destruction by up to 35 days**, through the heap, the WAL archive and the backups, as set out above.

6. **Co-located keys give no confidentiality.** An attacker who reads the database reads both halves. This mechanism defends against a restore and against a controller who no longer wants to be able to answer the question. It does not defend against a breach.

## What is not decided here

- The API projection of a suppressed entry is stated above but is not yet expressed in `packages/schemas/openapi-v1.yaml`, which is owned by another work unit.
- The keyring's deployment topology depends on the unresolved cost conflict in D-094.
- SR-013 in `conformance/p1140f/semantic-findings-v1.json` covers export, deletion, retention and backup tombstones. This document supplies the deletion and backup half of what that finding needs. It does not close it, and no closure evidence or review verdict is recorded by this change.
- SR-015 covers the current-authorization recheck at every display and delivery boundary. Resolving the handle at read time rather than freezing it into a snapshot is a precondition for that recheck and is not the recheck. It does not close SR-015.
