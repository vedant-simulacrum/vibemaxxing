-- Planning-grade PostgreSQL DDL. Not an executable migration history.
-- UUIDv7 generation is application-owned until implementation selects a database function.

create table accounts (
  account_id uuid primary key,
  state text not null check (state in ('active','restricted','suspended','deleting','deleted')),
  created_at timestamptz not null,
  deleted_at timestamptz
);

create table linked_identities (
  identity_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  provider text not null check (provider in ('github','x')),
  provider_subject text not null,
  created_at timestamptz not null,
  unique (provider, provider_subject)
);

create table devices (
  device_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('active','quarantined','revoked')),
  platform text not null,
  created_at timestamptz not null
);

create table device_keys (
  device_key_id text primary key,
  device_id uuid not null references devices(device_id),
  public_key bytea not null,
  algorithm text not null check (algorithm = 'Ed25519'),
  state text not null check (state in ('active','rotated','revoked')),
  created_at timestamptz not null,
  revoked_at timestamptz
);

create table claim_challenges (
  challenge_id text primary key,
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  nonce bytea not null check (octet_length(nonce) = 32),
  max_claims integer not null check (max_claims between 1 and 500),
  expires_at timestamptz not null,
  consumed_by_batch_id uuid,
  consumed_at timestamptz
);

create table device_sequences (
  device_id uuid primary key references devices(device_id),
  next_sequence bigint not null check (next_sequence > 0),
  previous_claim_hash bytea,
  updated_at timestamptz not null
);

create table claims (
  claim_id uuid primary key,
  batch_id uuid not null,
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  device_sequence bigint not null check (device_sequence > 0),
  challenge_id text not null references claim_challenges(challenge_id),
  previous_claim_hash bytea,
  payload_hash bytea not null check (octet_length(payload_hash) = 32),
  token_burn_total bigint not null check (token_burn_total >= 0),
  evidence_state text not null check (evidence_state in ('standard','hardened')),
  received_at timestamptz not null,
  unique (device_id, device_sequence),
  unique (device_id, payload_hash)
);

create table claim_corrections (
  correction_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  replacement_claim_id uuid references claims(claim_id),
  reason_code text not null,
  created_at timestamptz not null
);

create table outbox_events (
  outbox_id uuid primary key,
  event_type text not null,
  aggregate_id uuid not null,
  source_claim_id uuid references claims(claim_id),
  payload jsonb not null,
  created_at timestamptz not null,
  processed_at timestamptz
);

create table period_scores (
  scope_type text not null,
  scope_id uuid not null,
  period_type text not null,
  period_start timestamptz not null,
  account_id uuid not null references accounts(account_id),
  evidence_filter text not null,
  score bigint not null check (score >= 0),
  first_reached_score_at timestamptz not null,
  generation bigint not null,
  primary key (scope_type, scope_id, period_type, period_start, account_id, evidence_filter)
);

create table moderation_cases (
  case_id uuid primary key,
  account_id uuid references accounts(account_id),
  device_id uuid references devices(device_id),
  state text not null check (state in ('open','under_review','resolved','appealed','closed')),
  reason_code text not null,
  policy_version text not null,
  created_at timestamptz not null
);

create table deletion_jobs (
  deletion_job_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  scope text not null check (scope in ('server','local','everything')),
  state text not null check (state in ('accepted','cooling_off','running','completed','failed')),
  created_at timestamptz not null,
  completed_at timestamptz
);
