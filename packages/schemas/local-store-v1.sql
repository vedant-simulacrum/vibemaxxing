-- LOCAL DEVICE PERSISTENCE CONTRACT v1. SQLite.
--
-- `docs/architecture/NATIVE_RUNTIME_AND_STORAGE_CONTRACT.md` is the normative
-- owner. This file is the executable form of the local half of the storage
-- contract and is deliberately a separate file from
-- `packages/schemas/planning-schema.sql`: that one is the server's source of
-- truth and runs on PostgreSQL 16, this one never leaves the participant's
-- machine and runs on SQLite. Nothing in this file is implemented. No daemon
-- opens this database and no migration applies it.
--
-- The four properties this file exists to make executable, each of which the
-- inventory previously recorded as absent:
--
--   1. Encrypted stores. Every table holding participant-derived material is
--      encrypted at rest through SQLCipher-class page encryption under a key
--      held by the operating system keystore and never by this database. There
--      is no key column anywhere in this schema. A key stored beside the
--      ciphertext it protects is not encryption, and the same reasoning that
--      D-213 applies to the server keyring applies here.
--   2. Commitment, receipt and outbox. A claim is committed locally before it
--      is offered to the server, so a crash between the two loses nothing and
--      duplicates nothing.
--   3. Crash consistency. Write-ahead logging, full synchronous durability, one
--      writer, and every apply keyed so that replaying it is a no-op.
--   4. Deletion. A local deletion is executed and receipted per device under
--      D-076, and the receipt records what could not be proved rather than
--      claiming a forensic erase.
--
-- Two rules bind every column below. No column holds a prompt, a response, a
-- transcript, code, a diff, a tool result, a filename, a path, a project or
-- repository name, a credential, an embedding, a summary, a classification or
-- a content-derived hash. And nothing here is transmissible: only the
-- fixed-schema aggregate claim already admitted by
-- `packages/schemas/egress-allowlist-v1.json` crosses the device boundary, so
-- the evidence bundle this store holds is an at-rest record under D-266 and
-- never a wire format.

pragma journal_mode = wal;
pragma synchronous = full;
pragma foreign_keys = on;

-- One row. The store's own identity and the schema version the binary expects.
-- `schema_version` is compared against the binary's declared range at open, and
-- a store from the future is refused rather than opened read-only: a newer
-- daemon may have written a column this binary would silently drop on rewrite.
create table local_meta (
  singleton integer primary key check (singleton = 1),
  schema_version integer not null check (schema_version >= 1),
  installation_id text not null,
  lineage_id text not null,
  lineage_generation integer not null check (lineage_generation >= 0),
  created_at text not null
);

-- Consent under Article 5(3) of Directive 2002/58/EC, which D-104 records as a
-- second and independent requirement from the GDPR basis. Consent is per agent
-- source, separately refusable and separately withdrawable, so it is a row per
-- source and not a flag on the installation. A source with no row here is a
-- source the collector does not read.
create table source_consents (
  source_id text primary key,
  granted_at text not null,
  withdrawn_at text,
  policy_version text not null
);

-- Raw observations, before accounting. This is the only table holding anything
-- close to per-execution detail, and it holds counts and identifiers rather
-- than content. `execution_name` is the source-assigned name D-269 admits into
-- the duplicate-domain preimage; it is a source-derived fact and never a
-- collector-derived one.
create table observations (
  observation_id text primary key,
  source_id text not null references source_consents(source_id),
  adapter_id text not null,
  -- Exactly the nine modes `packages/schemas/observer-equivalence-v1.json`
  -- declares, in that spelling.
  observation_mode text not null check (observation_mode in ('native-event','official-hook','extension-api','local-runtime','acp','otel','proxy','wrapper','live-log')),
  execution_name text,
  source_cursor text,
  model_alias text,
  input_tokens integer check (input_tokens >= 0),
  output_tokens integer check (output_tokens >= 0),
  cache_read_tokens integer check (cache_read_tokens >= 0),
  cache_write_tokens integer check (cache_write_tokens >= 0),
  observed_at text not null,
  -- A retried delivery of one observation is the same row. This is the local
  -- half of the deduplication D-269 owns at the equivalence level.
  unique (source_id, observation_mode, observation_id)
);

-- One normalized accounting event per counted execution, produced by the
-- arithmetic in `packages/schemas/accounting-arithmetic-v1.json` under a named
-- profile. `duplicate_domain_commitment` is the 32-byte observer-equivalence
-- key; the preimage contains source-derived facts only, so two observers of one
-- execution produce one commitment and exactly one of them counts.
create table accounting_events (
  accounting_event_id text primary key,
  accounting_profile_id text not null,
  accounting_profile_sha256 blob not null check (length(accounting_profile_sha256) = 32),
  arithmetic_sha256 blob not null check (length(arithmetic_sha256) = 32),
  duplicate_domain_commitment blob not null check (length(duplicate_domain_commitment) = 32),
  token_burn_total integer not null check (token_burn_total >= 0),
  period_start_at text not null,
  period_end_at text not null,
  created_at text not null,
  check (period_end_at > period_start_at)
);

-- One receipt per accounting event under D-265. It records every observation
-- that saw the execution and which single one counted, because a receipt that
-- kept only the survivor could not explain to an appeal why a discarded
-- observation was discarded. `attestation` is fixed at none: under D-100 no
-- provider offers an individual-account attestation path, so no receipt can
-- assert that a provider verified a figure.
create table source_receipts (
  source_receipt_id text primary key,
  accounting_event_id text not null unique references accounting_events(accounting_event_id),
  counted_observation_id text not null references observations(observation_id),
  attestation text not null check (attestation = 'none'),
  attestation_basis text not null check (attestation_basis = 'self-reported-at-source'),
  certification_state text not null,
  created_at text not null
);

create table source_receipt_considerations (
  source_receipt_id text not null references source_receipts(source_receipt_id),
  observation_id text not null references observations(observation_id),
  outcome text not null check (outcome in ('counted','superseded-by-stronger-mode','duplicate-domain-collision','quarantined-disagreement','below-certification-ceiling')),
  primary key (source_receipt_id, observation_id)
);

-- The at-rest evidence bundle of D-266. It binds the signed claim bytes, the
-- receipt, the profile and arithmetic digests, the provenance chain and the
-- privacy decision by digest rather than by copy, so the bundle is what makes
-- an accepted claim explainable later without making it transmissible.
create table evidence_bundles (
  evidence_bundle_id text primary key,
  accounting_event_id text not null unique references accounting_events(accounting_event_id),
  source_receipt_id text not null references source_receipts(source_receipt_id),
  claim_bytes_sha256 blob not null check (length(claim_bytes_sha256) = 32),
  bundle_sha256 blob not null unique check (length(bundle_sha256) = 32),
  created_at text not null
);

-- The local commitment chain. `sequence` is dense from 1 per lineage
-- generation, and `previous_commitment` chains it, so a gap is visible and a
-- rewritten entry breaks every digest after it. A commitment is written before
-- the claim is offered to the server, which is the property that makes a crash
-- between the two lose nothing.
create table claim_commitments (
  sequence integer primary key check (sequence >= 1),
  lineage_generation integer not null check (lineage_generation >= 0),
  accounting_event_id text not null unique references accounting_events(accounting_event_id),
  commitment blob not null unique check (length(commitment) = 32),
  previous_commitment blob check (length(previous_commitment) = 32),
  committed_at text not null,
  check ((sequence = 1) = (previous_commitment is null))
);

-- Claims waiting to be offered to the server. The outbox is the transactional
-- half of the pattern D-017 names: a commitment and its outbox row are written
-- in one transaction, so a claim is never offered without being committed and
-- never committed without being scheduled.
--
-- `idempotency_key` is generated once and reused across every attempt, which is
-- what makes a retry a replay rather than a second mutation under D-225.
-- `attempt_count` has no ceiling here because D-233 makes the daemon claim
-- queue unbounded-with-capped-delay: dropping a queued claim loses activity the
-- append-only ledger cannot recreate.
create table outbox_claims (
  sequence integer primary key references claim_commitments(sequence),
  idempotency_key text not null unique,
  state text not null check (state in ('pending','in-flight','acknowledged','rejected','superseded')),
  attempt_count integer not null default 0 check (attempt_count >= 0),
  next_attempt_at text,
  last_reason_code text,
  acknowledged_at text,
  check ((state = 'acknowledged') = (acknowledged_at is not null)),
  check (state <> 'pending' or next_attempt_at is not null)
);

-- The last checkpoint the server acknowledged. A claim below an acknowledged
-- checkpoint is safe to discard from the outbox; one above it is not, which is
-- the local expression of the D-075 rule that a claim-batch result stays
-- replayable until a later acknowledged checkpoint supersedes it.
create table acknowledged_checkpoints (
  checkpoint_id text primary key,
  lineage_generation integer not null check (lineage_generation >= 0),
  through_sequence integer not null check (through_sequence >= 1),
  server_receipt blob not null,
  acknowledged_at text not null
);

-- Local deletion under D-076. Each device reports independently and the product
-- never claims all local data erased while any device is offline, expired,
-- unreachable, waived or unverified. `residual_risk` is the honest half: SQLite
-- vacuuming, a copy-on-write filesystem, a snapshot and a backup are all
-- outside this process's reach, so a receipt records what was deleted and what
-- could not be proved gone rather than asserting a forensic erase.
create table local_deletion_receipts (
  local_deletion_command_id text primary key,
  outcome text not null check (outcome in ('complete','partial','refused','expired')),
  tables_cleared integer not null check (tables_cleared >= 0),
  keystore_entries_destroyed integer not null check (keystore_entries_destroyed >= 0),
  residual_risk text not null check (residual_risk in ('filesystem-snapshot-possible','backup-copy-possible','none-observed')),
  executed_at text not null,
  reported_at text
);

-- Crash consistency.
--
-- One writer. The daemon holds the only write handle; the shell and the command
-- line interface read through it over the local control protocol rather than
-- opening the file, because two writers under WAL is where a partially applied
-- accounting event becomes possible.
--
-- Every apply is idempotent by key. Replaying an observation, an accounting
-- event, a commitment or an outbox transition after a crash is a no-op, because
-- each is keyed on an identifier the producer computes before the write rather
-- than on one the database assigns after it.
--
-- Recovery reconciles in one direction only. On open, the daemon finds the
-- highest `claim_commitments.sequence` and the outbox rows at or below it; a
-- commitment with no outbox row is scheduled, and an outbox row with no
-- commitment is impossible because they are written in one transaction. The
-- reconciliation never deletes a commitment, so an ambiguous commit resolves
-- toward retaining the participant's work.
create index outbox_claims_due_idx on outbox_claims (next_attempt_at) where state = 'pending';
create index accounting_events_commitment_idx on accounting_events (duplicate_domain_commitment);
create index observations_source_idx on observations (source_id, observed_at);
create index source_receipt_considerations_observation_idx on source_receipt_considerations (observation_id);

-- SUBSYSTEM PROJECTIONS (PF-013).
--
-- `interactive-shell` carried fifteen states covering six different subsystems:
-- collection was `paused`, connectivity was `offline` and `degraded`, authentication
-- was `auth-required`, updates were `update-required` and `update-blocked`, and
-- permissions were `permission-repair`. One state variable cannot hold six independent
-- facts. A device whose collection is paused *and* whose network is offline had no
-- representable shell state, and the transition table had to pretend one of the two
-- had not happened.
--
-- Each subsystem is now its own single-row projection, so the combinations are
-- expressible and the shell owns process and connection state alone. They live here
-- rather than in `planning-schema.sql` because they never leave the device: none of
-- them is a fixed-schema aggregate accounting figure or an integrity claim, and those
-- are the only things AGENTS.md permits across the boundary.

create table local_collection_state (
  singleton integer primary key check (singleton = 1),
  state text not null check (state in ('collecting','paused','stopped')),
  changed_at text not null
);

create table local_sync_state (
  singleton integer primary key check (singleton = 1),
  state text not null check (state in ('syncing','paused','backing-off','stopped')),
  changed_at text not null
);

create table local_auth_state (
  singleton integer primary key check (singleton = 1),
  state text not null check (state in ('authenticated','auth-required','locked-out')),
  changed_at text not null
);

create table local_permission_state (
  singleton integer primary key check (singleton = 1),
  state text not null check (state in ('granted','repair-required','denied')),
  changed_at text not null
);

create table local_connectivity_state (
  singleton integer primary key check (singleton = 1),
  state text not null check (state in ('online','degraded','offline')),
  changed_at text not null
);
