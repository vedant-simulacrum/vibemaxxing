# ADR-022: Erasure by cryptographic tombstone and key destruction

Status: accepted
Date: 2026-08-06
Decision: D-085, D-210, D-211, D-212, D-213, D-214
Normative owner of the mechanism: `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md`

**Not reviewed by counsel. Counsel review is an unmet release gate under D-109.** The reasoning below was produced by the controller against primary sources and is the basis the decision was made on, not advice.

## Context

D-085 has been `provisional` since it was recorded, and the reason was written into the register rather than hidden: the erasure outcome it decides collides with two rules the repository treats as binding.

The first is the append-only rule in `AGENTS.md` — accepted claims and historical facts remain immutable, and corrections, consolidation, deletion effects and reversals are appended rather than applied in place. The second is `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`, which requires immutable retained ranking generations with durable cursors.

Deleting one row out of a sealed generation breaks all three properties at once. The content hash no longer matches, every position after the deleted row shifts, and every client cursor anchored on a row identifier or a score points at something that has moved. A leaderboard that renumbers itself when someone leaves is not an immutable generation, and a rebuild that produces a different row set than the one it is verifying against is not a rebuild.

The two mechanisms the register named as candidates were rebuild-under-a-new-generation-identifier and tombstone-with-suppression. Neither was chosen there, deliberately.

## The alternative that was not chosen

**Rebuild under a new generation identifier** is the obvious answer and it is worse in three specific ways.

It multiplies storage by the number of erasures: every affected generation, across six board scopes and six periods, acquires a second full copy. It destroys cursor stability, because a rebuild renumbers positions and a client holding a cursor into the old generation has to be told to restart. And it does not actually erase anything — the old generation is retained, so the participant is still in it, and the only way to finish the job is to delete the old generation, which is the deletion the immutability rule forbids.

Rebuild is the right mechanism for the problem ADR-020 uses it for, which is a trust-state change that ought to produce a new, differently-weighted standing while the old one stays auditable. It is the wrong mechanism for erasure, because erasure is not a recomputation.

## Decision

**An Article 17 erasure appends a signed erasure record and destroys a key. It deletes nothing from any sealed ranking generation.**

Ranking entries stop being keyed on the account and start being keyed on an *erasure domain* — an opaque pseudonym, one per ranked-identity lineage. The only stored binding between that pseudonym and the person is `erasure_domains.bound_subject_ciphertext`, an AES-256-GCM ciphertext of `account_id ‖ lineage_id` under a key held in `erasure_keys` that encrypts nothing else. The erasure destroys that key and appends a hash-chained, COSE_Sign1-signed record to `erasure_records`, in the same transaction that deletes the participant's live personal rows.

Everything the immutability rule protects survives byte for byte. Nothing is deleted from `ranking_entries`, so no position moves, no `content_hash` changes, and no `snapshot_id` is invalidated. The tombstone is appended, which is what the append-only rule asks for. What ends is the controller's ability to say which person a retained row describes.

`docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` is the mechanism in full: key scope, rotation, the physical meaning of destruction, the proof-of-destruction commitment, the sealed-generation projection, cursor behaviour in every case, and the backup and restore procedure. This record is why.

## Why the key hierarchy is shaped this way

**One key per lineage, not per entry.** Erasure operates at ranked-identity granularity. A key per entry multiplies the register by six scopes times six periods times every generation and buys no granularity that anyone can exercise. A single server-wide key would make one erasure erase everybody.

**The key encrypts exactly one plaintext.** A domain key that also protected, say, a device registration would make an erasure destroy the device registration, and the blast radius of an erasure has to be exactly the erasure.

**Destruction is the only state change.** Rotating a key while keeping the old one alive changes nothing, because the old key still opens the ciphertext. Rotating while destroying the old key *is* an erasure. So the key has two states and they are expressed as a check constraint — material present exactly when destruction time is absent — rather than as a lifecycle vocabulary that a worker has to be trusted to advance correctly.

**The lookup digest is not destroyed.** `/rank/me` needs an account-to-domain index or it becomes a scan. That index is an HMAC of the account identifier under a server-wide key, and it survives erasure, because after the account row is deleted its preimage is a 128-bit identifier that no longer exists anywhere. UUIDv7 spends 48 bits on a timestamp, so the unguessable part is 74 bits rather than 122. That is still not searchable, and the number is written down here rather than left to the reader.

**The commitment proves which key, not that no copy exists.** `key_commitment` is SHA-256 over `key_id ‖ key_material`, taken before destruction and retained after. Anyone holding the log can test a candidate key against it and nobody can invert it. What the log proves is that a specific key was destroyed and that the log has not been rewritten. That no copy was taken beforehand is attested by the controller and is not provable by any mechanism. Stating a stronger claim would be the kind of claim this repository's evidence discipline exists to refuse.

## Why an erased entry renders nothing

The retained entry keeps its position and its credited figure, because the generation's aggregate integrity depends on them. The question is what the public surface does with it.

Rendering the figure without a name looks like the privacy-preserving option and is not. A third party who archived the board before the erasure holds handle, position and figure; a retained row that publishes position and figure joins to that archive on two columns. Rendering a placeholder that says the position was erased is worse still, because it publishes the fact of an erasure against a position the archive already names.

So an erased entry contributes nothing to a page. The cost is that a page can return fewer items than requested while more remain, which is why pagination anchors on position rather than on item count.

**The published aggregates for a sealed generation are frozen at seal and never recomputed**, for the same reason. If the participant count and total credited burn for a generation were recomputed after an erasure, an observer who recorded both publications would recover the departed participant's exact figure by subtraction. Refusing to publish the second observation is the same move ADR-020 makes with the confidence weight, and it has the same cost: a historical count includes participants who have since been erased, which is what the count meant when it was taken.

## Why the cursor anchors on position

The previous contract put a score, a first-reached timestamp and an account identifier inside the cursor. That is a personal-data leak into a token the client keeps indefinitely, and it makes the cursor depend on values that erasure removes.

Positions inside a sealed generation are immutable, so a position is the one anchor that survives everything: erasure of the anchor row, supersession of the generation, a handle rename, a block, a visibility change. A client holding a stale cursor whose anchor entry was erased receives the next page from that position with the erased entry absent and every other entry where it always was. No restart, no renumbering, no error.

The only case that produces a restart is purge at the retention window, which is a retention event and not an erasure event. That is a strictly better property than the previous contract, which restarted on any snapshot change.

## What this costs

**A generation that carries an erasure is no longer rebuildable from source claims.** The erasure deletes the participant's claims, so the sealed rows become the only remaining authority for that generation. A rebuild spanning it carries the erased entries forward verbatim rather than re-deriving them. Determinism is preserved and derivability is not, permanently and in one direction.

That is a real loss and it is not avoidable. Keeping the claims would mean refusing the erasure of the participant's own data, which is the right being exercised.

**Deleting accepted claims is a stated exception to the immutability rule**, not an oversight. Immutability protects an accepted claim against mutation — nobody edits a number after the fact. Article 17 is a lawful terminal event and the append-only obligation is discharged by the tombstone that records it.

**Logical destruction leads physical destruction by up to 35 days**, through the heap tuple, the write-ahead log, the archive and the backups. Point-in-time recovery is physical and cannot exclude a row. The erasure journal and the mandatory reapply-before-traffic restore procedure close the gap operationally, and the interval between restore completion and reapply completion is a real window in which an operator with credentials can re-identify. It is bounded by the replay and is not zero.

**Co-locating the keyring with the ciphertext gives no confidentiality.** An attacker who reads the database reads both halves. This is a deletion control, not encryption at rest, and no surface may present it as the latter.

## Consequences

- D-085 moves from `provisional` to `accepted`. The outcome it recorded is unchanged; the mechanism that reconciles it with immutable generations is now stated.
- `ranking_entries`, `erasure_domains`, `erasure_keys`, `erasure_records`, `erasure_domain_links`, `erasure_restore_receipts` and a repaired `deletion_tombstones` enter `packages/schemas/planning-schema.sql`.
- The ranking projection acquires a join through the key register on every read, and the handle is resolved per surviving entry at read time rather than frozen into the snapshot.
- `LeaderboardPage` needs a position-range field so a client can distinguish a short page from the end of the board. `packages/schemas/openapi-v1.yaml` is owned by another work unit and does not carry it, so the API under-describes the projection this contract states.
- The restore procedure becomes a gate on serving traffic, with a receipt whose ordering constraint makes an out-of-order claim unrepresentable. No restore drill has been run and nothing is provisioned.
- Article 17(2) obligations toward downstream copies, caches and mirrors are unchanged and undischarged by any of this.

## What would cause this to be revisited

- **A supervisory authority or a court holding that key destruction is not erasure** for data of this kind. The fallback is deletion of the sealed generations themselves, which requires reopening the immutability rule rather than this record.
- **Counsel review under D-109** reaching a different view of the Recital 26 position, which is the single most likely trigger and is why this record states the position as defensible rather than certain.
- **A demonstrated re-identification** of a key-destroyed entry by any route, which would mean the binding was not the only one and would reopen the audit of what else holds a link.
- **The keyring becoming genuinely separable within budget**, which would shorten the restore window from "duration of the replay" to "zero" and is currently blocked behind the unresolved cost conflict in D-094.
- **A retention policy that keeps sealed generations beyond the point where the pseudonymous series itself becomes identifying** through its own shape. Singling out survives this mechanism, and a long enough retained series is its own risk.
