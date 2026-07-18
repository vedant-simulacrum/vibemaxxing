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
