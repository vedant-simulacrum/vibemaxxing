# Data Lifecycle, Deletion, and Recovery

## Data classes

- account identity and authentication
- public profile and social graph
- device registrations and revocations
- accepted safe claims
- aggregate scores and ranks
- security and abuse events
- pricing datasets
- local audit ledger
- backups and release evidence

Each class must have purpose, lawful/business basis, retention, access, deletion behavior, backup behavior, and owner.

## Deletion model

- remove account-identifying and public-profile data promptly;
- revoke devices and sessions immediately;
- remove social edges and presence;
- delete local content and local audit data on request;
- dissociate or delete server claim records where feasible and legally appropriate;
- when integrity records must remain, minimize and pseudonymize them and document why;
- ensure deleted identity data is not restored from backups after the backup expiry window;
- produce a deletion receipt without exposing internal secrets.

## Recovery exercises

At minimum test:

- complete leaderboard rebuild from accepted safe claims;
- aggregate corruption;
- transactional-outbox backlog;
- duplicate workers;
- failed migration and rollback;
- authentication-key rotation;
- device-signing-key revocation;
- pricing-dataset corruption and rollback;
- bad release rollback;
- backup restore followed by deletion replay;
- regional/service outage when production architecture exists.

A backup is not valid until restored and verified. A deletion process is not valid until a restore test proves deleted identity data does not reappear.

## What this operation claims, and what it does not

Deletion here is logical, not forensic. Nothing in this document, in any receipt the product issues, in any operator runbook derived from it, and on any participant-facing surface may say or imply that a byte was destroyed in place, that a storage medium was cleansed of it, or that a copy outside this system was reached. Those are claims a user-space process and a managed database cannot observe, and stating one would be the strongest sentence in this repository with the least evidence behind it.

What the product does claim is bounded and is owned elsewhere, and this section deliberately points rather than restates. `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` owns the hosted half: rows deleted, an erasure-domain key destroyed, a signed record appended, and a stated 35-day lag of physical destruction behind logical destruction through the heap, the write-ahead log and the backups. `docs/privacy/PRIVACY_CONTRACT.md` owns the device half: a daemon ran delete operations over the stores it controls, counted what it cleared, and reported what it could not rule out. Neither half speaks for the other, and no operations document may merge them into one sentence.

The check on this section is not that the word is absent. An absent word is satisfied by an empty file, and this document was empty of it while making no statement about the ceiling at all — which is the same defect the missing statement was supposed to prevent. The check is that the ceiling is stated here and that no claim above it appears anywhere in the file.

### What makes the restore-and-replay exercise pass

"Backup restore followed by deletion replay" is in the exercise list above. It passes when, and only when:

- the reapply ran against the restored cluster before any application traffic was admitted;
- an `erasure_restore_receipts` row exists for the restore, carrying the journal head digest, the counts, and a `traffic_admitted_at` no earlier than `reapply_completed_at`;
- every deletion tombstone the journal names exists in the restored cluster;
- no live personal row for any erased subject remains.

A restore that came up clean and served traffic without a receipt did not pass this exercise. It produced no evidence either way, and the receipt exists so that its absence is the thing an audit looks for. **No such drill has been run.** Nothing is provisioned, and the four conditions above are a specification.

## Migration chain and rollback classes

"Failed migration and rollback" above is an exercise. Whether a rollback is available at all is a property of the migration, and `storage_migrations` with `packages/schemas/migration-chain-v1.schema.json` is where that property lives. D-392 records the choices.

| Class | What recovery means |
|---|---|
| `binary-reversible` | the previous binary reads and writes the post-migration shape, so a rollback is a binary swap and nothing else |
| `forward-only` | it does not, so recovery is roll-forward or restoration of a verified pre-migration snapshot |
| `snapshot-required` | forward-only, and a verified snapshot must exist before the migration runs |

A check constraint requires the snapshot digest on the class that needs one, so a snapshot-required migration cannot run having removed its own recovery path.

`down_sql_present` is a separate column from the class, and the separation is the point. D-097 requires every goose migration to carry an explicit down section, and a present down section is not reversibility: dropping a column back is syntactically valid and loses everything that was written into it. Conflating the two is how a forward-only migration acquires a rollback plan nobody tested, which is the failure D-074 exists to prevent.

A forward-only step names the operations that made it one — a dropped column, a narrowed type, a tightened constraint, a destructive backfill, a detached partition, a key destruction — so the judgement can be re-examined later rather than trusted.

Key destruction is the sharpest case. A rollback past the erasure migration restores a key an Article 17 erasure destroyed, which is precisely the window D-214 records as the one interval in which a restore can resurrect an identifier.
