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

## Migration chain and rollback classes

"Failed migration and rollback" above is an exercise. Whether a rollback is available at all is a property of the migration, and `storage_migrations` with `packages/schemas/migration-chain-v1.schema.json` is where that property lives. D-332 records the choices.

| Class | What recovery means |
|---|---|
| `binary-reversible` | the previous binary reads and writes the post-migration shape, so a rollback is a binary swap and nothing else |
| `forward-only` | it does not, so recovery is roll-forward or restoration of a verified pre-migration snapshot |
| `snapshot-required` | forward-only, and a verified snapshot must exist before the migration runs |

A check constraint requires the snapshot digest on the class that needs one, so a snapshot-required migration cannot run having removed its own recovery path.

`down_sql_present` is a separate column from the class, and the separation is the point. D-097 requires every goose migration to carry an explicit down section, and a present down section is not reversibility: dropping a column back is syntactically valid and loses everything that was written into it. Conflating the two is how a forward-only migration acquires a rollback plan nobody tested, which is the failure D-074 exists to prevent.

A forward-only step names the operations that made it one — a dropped column, a narrowed type, a tightened constraint, a destructive backfill, a detached partition, a key destruction — so the judgement can be re-examined later rather than trusted.

Key destruction is the sharpest case. A rollback past the erasure migration restores a key an Article 17 erasure destroyed, which is precisely the window D-214 records as the one interval in which a restore can resurrect an identifier.
