-- P-1140D REPAIRED PLANNING MIGRATION CONTRACT.
-- PostgreSQL 16 executable ownership, constraint, and transaction-boundary contract.
-- It becomes implementation input only after the explicit P-1104 authorization gate.
-- Country leaderboards remain post-launch under D-052 and are intentionally absent.

create table accounts (
  account_id uuid primary key,
  state text not null check (state in ('active','restricted','deletion-pending','deleted')),
  created_at timestamptz not null
);

create table account_handles (
  account_id uuid primary key references accounts(account_id),
  normalized_handle text not null unique,
  confusable_skeleton text not null unique,
  policy_version text not null
);

create table linked_identities (
  identity_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  provider text not null check (provider in ('github','x')),
  provider_subject text not null,
  state text not null check (state in ('linked','unlink-pending','unlinked')),
  unique (provider, provider_subject)
);

create table web_sessions (
  session_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  token_family_id uuid not null,
  token_hash bytea not null unique,
  state text not null check (state in ('active','rotated','revoked','expired')),
  expires_at timestamptz not null
);

create table recovery_codes (
  recovery_code_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  code_hash bytea not null unique,
  consumed_at timestamptz
);

create table optional_authenticators (
  authenticator_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  kind text not null,
  credential_id bytea not null unique,
  public_key bytea not null
);

create table oauth_transactions (
  oauth_transaction_id uuid primary key,
  provider text not null check (provider in ('github','x')),
  state_hash bytea not null unique,
  pkce_verifier_ciphertext bytea,
  intended_action text not null,
  state text not null check (state in ('created','redirected','callback-received','consumed','expired','failed')),
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create table devices (
  device_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  installation_id uuid not null unique,
  lineage_id uuid not null,
  platform_profile_id text not null,
  state text not null check (state in ('pending','active','quarantined','revoked','deleted'))
);

create table device_keys (
  device_key_id text primary key,
  device_id uuid not null references devices(device_id),
  public_key bytea not null,
  algorithm text not null check (algorithm = 'Ed25519'),
  protection_class text not null,
  state text not null check (state in ('active','rotated','revoked'))
);

create table device_enrollment_grants (
  enrollment_grant_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  public_key_hash bytea not null,
  collector_digest bytea not null,
  state text not null check (state in ('pending','approved','denied','expired','consumed')),
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create table adapter_installations (
  adapter_installation_id uuid primary key,
  device_id uuid not null references devices(device_id),
  adapter_id text not null,
  artifact_digest bytea not null,
  certification_digest bytea,
  evidence_ceiling text not null,
  unique (device_id, adapter_id)
);

create table claim_challenges (
  challenge_id text primary key,
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  nonce bytea not null,
  expires_at timestamptz not null,
  consumed_by_batch_id uuid,
  consumed_at timestamptz
);

create table device_sequences (
  device_id uuid primary key references devices(device_id),
  next_sequence bigint not null,
  local_commitment_head bytea,
  server_checkpoint_head bytea,
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken','revoked'))
);

create table claims (
  claim_id uuid primary key,
  batch_id uuid not null,
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  device_sequence bigint not null,
  challenge_id text not null references claim_challenges(challenge_id),
  payload_hash bytea not null,
  accounting_profile_id text not null,
  token_burn_total bigint not null check (token_burn_total >= 0),
  received_at timestamptz not null,
  unique (device_id, device_sequence),
  unique (device_id, payload_hash)
);

create table claim_payloads (
  claim_id uuid primary key references claims(claim_id),
  canonical_payload bytea not null,
  signature bytea not null
);

create table claim_rejections (
  rejection_id uuid primary key,
  payload_hash bytea,
  reason_code text not null,
  retryable boolean not null,
  created_at timestamptz not null
);

create table claim_corrections (
  correction_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  replacement_claim_id uuid references claims(claim_id),
  reason_code text not null,
  created_at timestamptz not null
);

create table quarantines (
  quarantine_id uuid primary key,
  account_id uuid references accounts(account_id),
  device_id uuid references devices(device_id),
  claim_id uuid references claims(claim_id),
  reason_code text not null,
  state text not null check (state in ('active','released'))
);

create table evidence_assessments (
  evidence_assessment_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  verifier_profile_id text not null,
  public_state text not null check (public_state in ('hardened','standard','imported','private-analytics')),
  provenance_state text not null check (provenance_state in ('verified','partial','unverified','rejected')),
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken')),
  integrity_state text not null check (integrity_state in ('verified','degraded','failed')),
  reason_codes text[] not null default '{}',
  created_at timestamptz not null
);

create table moderation_cases (
  case_id uuid primary key,
  account_id uuid references accounts(account_id),
  state text not null check (state in ('open','investigating','actioned','awaiting-appeal','reversed','closed')),
  policy_version text not null,
  created_at timestamptz not null
);

create table moderation_actions (
  moderation_action_id uuid primary key,
  case_id uuid not null references moderation_cases(case_id),
  action text not null,
  actor_id text not null,
  reason_code text not null,
  created_at timestamptz not null
);

create table appeals (
  appeal_id uuid primary key,
  case_id uuid not null references moderation_cases(case_id),
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('submitted','screening','needs-information','reviewing','approved','denied','withdrawn','expired')),
  created_at timestamptz not null
);

-- Season lifecycle. The inequality chain is the executable form of the exact
-- boundary order the ranking contract requires: a season ends, then freezes
-- against late claims, then closes, then leaves its appeal window, then
-- archives. A season whose dates do not order that way cannot be inserted.
create table seasons (
  season_id uuid primary key,
  ordinal integer not null unique check (ordinal >= 1),
  starts_at timestamptz not null,
  ends_at timestamptz not null,
  freeze_at timestamptz not null,
  close_at timestamptz not null,
  appeal_window_ends_at timestamptz not null,
  archive_at timestamptz not null,
  rules_version text not null,
  check (starts_at < ends_at),
  check (ends_at <= freeze_at),
  check (freeze_at <= close_at),
  check (close_at <= appeal_window_ends_at),
  check (appeal_window_ends_at <= archive_at)
);

create table periods (
  period_id uuid primary key,
  period_type text not null check (period_type in ('daily','weekly','monthly','seasonal','yearly','lifetime')),
  season_id uuid references seasons(season_id),
  starts_at timestamptz,
  ends_at timestamptz,
  rules_version text not null,
  check ((period_type = 'lifetime') = (starts_at is null)),
  check ((starts_at is null) = (ends_at is null)),
  check (starts_at is null or starts_at < ends_at),
  check ((period_type = 'seasonal') = (season_id is not null)),
  unique nulls not distinct (period_type, starts_at)
);

-- Minute-resolution raw projection. `score` is banned as a column name by
-- ADR-020 because it is the word that lets the raw and credited quantities
-- merge; this column holds the raw accepted quantity and says so. Partitioned
-- by minute because it is the highest-volume table in the model, is append-only
-- per key, is referenced by no foreign key, and is discarded wholesale at the
-- retention window in `data-disposition-v1.json`.
create table minute_scores (
  period_id uuid not null references periods(period_id),
  account_id uuid not null references accounts(account_id),
  minute_start timestamptz not null,
  token_burn_total bigint not null check (token_burn_total >= 0),
  primary key (period_id, account_id, minute_start)
) partition by range (minute_start);

create table minute_scores_default partition of minute_scores default;

-- Live per-period projection, keyed on the account. It is a live personal
-- record: an erasure deletes it. The sealed generation in `ranking_entries` is
-- the retained artifact and is keyed on the erasure-domain pseudonym instead.
create table period_scores (
  ranking_view_id text not null,
  period_id uuid not null references periods(period_id),
  account_id uuid not null references accounts(account_id),
  token_burn_total bigint not null check (token_burn_total >= 0),
  confidence_weight_hundredths smallint not null check (confidence_weight_hundredths between 25 and 100),
  credited_token_burn bigint not null check (credited_token_burn >= 0),
  generation bigint not null check (generation >= 0),
  primary key (ranking_view_id, period_id, account_id),
  check (credited_token_burn <= token_burn_total)
);

-- One snapshot per sealed generation. The uniqueness is what makes
-- `snapshot_id` a durable client-visible name for a generation: a client that
-- holds a snapshot identifier holds a name for exactly one sealed generation,
-- and an erasure never mints a new one.
create table score_snapshots (
  snapshot_id uuid primary key,
  ranking_view_id text not null,
  generation bigint not null,
  content_hash bytea not null check (octet_length(content_hash) = 32),
  sealed_at timestamptz not null,
  created_at timestamptz not null,
  unique (ranking_view_id, generation)
  -- The foreign key to ranking_projection_generations is added at the end of
  -- this contract, because that table is declared after this one.
);

create table ranking_corrections (
  ranking_correction_id uuid primary key,
  correction_id uuid not null references claim_corrections(correction_id),
  ranking_view_id text not null,
  token_burn_total_delta bigint not null
);

create table pricing_datasets (
  pricing_dataset_id text primary key,
  state text not null check (state in ('active','superseded','revoked')),
  effective_at timestamptz not null,
  provenance text not null,
  content_hash bytea not null
);

create table pricing_entries (
  pricing_dataset_id text not null references pricing_datasets(pricing_dataset_id),
  model_alias_id text not null,
  category text not null,
  unit_price numeric(30,12) not null,
  primary key (pricing_dataset_id, model_alias_id, category)
);

create table cost_interpretations (
  cost_interpretation_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  pricing_dataset_id text references pricing_datasets(pricing_dataset_id),
  state text not null check (state in ('active','superseded','revoked')),
  estimated_cost numeric(30,12)
);

create table profiles (
  account_id uuid primary key references accounts(account_id),
  visibility text not null check (visibility in ('public','friends','private')),
  updated_at timestamptz not null
);

create table friend_requests (
  friend_request_id uuid primary key,
  requester_account_id uuid not null references accounts(account_id),
  target_account_id uuid not null references accounts(account_id),
  state text not null check (state in ('none','pending-a-to-b','pending-b-to-a','active','blocked','ended'))
);

create table friend_edges (
  account_id_a uuid not null references accounts(account_id),
  account_id_b uuid not null references accounts(account_id),
  established_at timestamptz not null,
  primary key (account_id_a, account_id_b),
  check (account_id_a < account_id_b)
);

create table blocks (
  blocker_account_id uuid not null references accounts(account_id),
  blocked_account_id uuid not null references accounts(account_id),
  primary key (blocker_account_id, blocked_account_id)
);

create table rival_edges (
  account_id uuid not null references accounts(account_id),
  rival_account_id uuid not null references accounts(account_id),
  state text not null check (state in ('none','active','ended','blocked')),
  primary key (account_id, rival_account_id)
);

create table organizations (
  organization_id uuid primary key,
  owner_account_id uuid not null references accounts(account_id),
  name text not null,
  state text not null check (state in ('active','archived'))
);

create table communities (
  community_id uuid primary key,
  owner_account_id uuid not null references accounts(account_id),
  name text not null,
  state text not null check (state in ('active','archived'))
);

create table boards (
  board_id uuid primary key,
  board_type text not null check (board_type in ('private','organization','hacker-house','community')),
  policy_version text not null,
  state text not null check (state in ('active','archived'))
);

create table board_memberships (
  board_id uuid not null references boards(board_id),
  account_id uuid not null references accounts(account_id),
  role text not null check (role in ('owner','admin','member','viewer')),
  state text not null check (state in ('invited','active-viewer','active-member','active-admin','active-owner','left','removed','blocked')),
  primary key (board_id, account_id),
  check (
    (state = 'active-owner' and role = 'owner')
    or (state = 'active-admin' and role = 'admin')
    or (state = 'active-member' and role = 'member')
    or (state = 'active-viewer' and role = 'viewer')
    or state in ('invited','left','removed','blocked')
  )
);

create table board_invites (
  board_invite_id uuid primary key,
  board_id uuid not null references boards(board_id),
  state text not null check (state in ('pending','accepted','declined','expired','revoked','invalidated-by-block')),
  expires_at timestamptz not null
);

create table presence_leases (
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  state text not null check (state in ('absent','active','idle','expired','revoked')),
  expires_at timestamptz not null,
  primary key (account_id, device_id)
);

-- Partitioned by creation month: retention is 90 days, no foreign key points
-- at it, and its only uniqueness is its own identity, so the partition key can
-- join the primary key without weakening any invariant.
create table notifications (
  notification_id uuid not null,
  account_id uuid not null references accounts(account_id),
  event_type text not null check (event_type in ('friend_request','board_invitation','rank_overtake','moderation','appeal','security','compatibility','release')),
  state text not null check (state in ('created','grouped','ready','delivered','read','suppressed','retracted','expired')),
  actor_account_id uuid references accounts(account_id),
  scope_id uuid,
  grouping_digest bytea not null check (octet_length(grouping_digest) = 32),
  created_at timestamptz not null,
  primary key (notification_id, created_at)
) partition by range (created_at);

create table notifications_default partition of notifications default;

create table notification_preferences (
  account_id uuid primary key references accounts(account_id),
  social_enabled boolean not null,
  ranking_enabled boolean not null,
  moderation_enabled boolean not null,
  security_enabled boolean not null check (security_enabled),
  quiet_hours_start_minute smallint check (quiet_hours_start_minute between 0 and 1439),
  quiet_hours_end_minute smallint check (quiet_hours_end_minute between 0 and 1439),
  timezone_name text not null
);

create table outbox_events (
  outbox_id uuid primary key,
  event_type text not null,
  aggregate_id uuid not null,
  aggregate_revision bigint not null check (aggregate_revision >= 0),
  event_digest bytea not null check (octet_length(event_digest) = 32),
  created_at timestamptz not null,
  processed_at timestamptz,
  unique (aggregate_id, aggregate_revision)
);

create table worker_checkpoints (
  worker_name text primary key,
  source_revision bigint not null check (source_revision >= 0),
  checkpoint_digest bytea not null check (octet_length(checkpoint_digest) = 32),
  updated_at timestamptz not null
);

-- Partitioned by creation month for the same three reasons as `notifications`,
-- against a 365-day security-audit window.
create table audit_events (
  audit_event_id uuid not null,
  actor_type text not null,
  actor_id uuid,
  event_type text not null,
  target_type text not null,
  target_digest bytea not null check (octet_length(target_digest) = 32),
  reason_code text not null,
  created_at timestamptz not null,
  primary key (audit_event_id, created_at)
) partition by range (created_at);

create table audit_events_default partition of audit_events default;

create table exports (
  export_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('requested','snapshotting','encrypting','ready','downloaded','purged','failed')),
  expires_at timestamptz
);

create table deletion_jobs (
  deletion_job_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  scope text not null check (scope in ('server','local','everything')),
  state text not null check (state in ('requested','recent-auth-verified','cooling-off','processing','rebuilding-projections','awaiting-local-receipt','complete','failed'))
);

create table feature_flags (
  flag_key text primary key,
  value_type text not null check (value_type in ('boolean','integer','string')),
  boolean_value boolean,
  integer_value bigint,
  string_value text,
  revision bigint not null check (revision >= 0),
  check (num_nonnulls(boolean_value, integer_value, string_value) = 1)
);

create table schema_migrations (
  version text primary key,
  checksum bytea not null,
  applied_at timestamptz not null
);


-- Repaired append-only authority, identity, verification, ranking, and social tables.
create table idempotency_records (
  actor_account_id uuid not null references accounts(account_id),
  idempotency_key uuid not null,
  operation_id text not null,
  request_digest bytea not null check (octet_length(request_digest) = 32),
  response_digest bytea,
  state text not null check (state in ('reserved','committed','conflict','expired','failed')),
  expires_at timestamptz not null,
  primary key (actor_account_id, idempotency_key)
);

create table session_families (
  token_family_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('active','rotating','replay-detected','revoked','device-revoked','expired')),
  created_at timestamptz not null,
  revoked_at timestamptz
);

create table native_sessions (
  native_session_id uuid primary key,
  token_family_id uuid not null references session_families(token_family_id),
  device_id uuid not null references devices(device_id),
  dpop_key_thumbprint bytea not null check (octet_length(dpop_key_thumbprint) = 32),
  state text not null check (state in ('active','rotated','revoked','expired')),
  expires_at timestamptz not null
);

create table device_lineages (
  lineage_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  root_installation_id uuid not null,
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken','revoked')),
  revision bigint not null check (revision >= 0)
);

create table device_key_events (
  device_key_event_id uuid primary key,
  device_id uuid not null references devices(device_id),
  previous_key_id text,
  next_key_id text not null,
  action text not null check (action in ('enrolled','rotated','revoked','recovered')),
  continuity_signature bytea,
  occurred_at timestamptz not null
);

create table verifier_appraisals (
  appraisal_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  evidence_profile_id text not null,
  provenance_state text not null check (provenance_state in ('verified','partial','unverified','rejected')),
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken')),
  integrity_state text not null check (integrity_state in ('verified','degraded','failed')),
  reason_codes text[] not null default '{}',
  policy_digest bytea not null check (octet_length(policy_digest) = 32),
  created_at timestamptz not null
);

create table checkpoint_receipts (
  checkpoint_receipt_id uuid primary key,
  device_id uuid not null references devices(device_id),
  first_sequence bigint not null check (first_sequence >= 0),
  last_sequence bigint not null check (last_sequence >= first_sequence),
  batch_digest bytea not null check (octet_length(batch_digest) = 32),
  previous_receipt_digest bytea,
  signed_receipt bytea not null,
  created_at timestamptz not null
);

create table ranking_views (
  ranking_view_id text primary key check (ranking_view_id ~ '^[0-9a-f]{64}$'),
  period_id uuid not null references periods(period_id),
  scope text not null check (scope in ('global','friends','rivals','board')),
  board_id uuid references boards(board_id),
  rules_digest bytea not null check (octet_length(rules_digest) = 32),
  pricing_dataset_digest bytea not null check (octet_length(pricing_dataset_digest) = 32),
  evidence_policy_digest bytea not null check (octet_length(evidence_policy_digest) = 32),
  source_checkpoint_digest bytea not null check (octet_length(source_checkpoint_digest) = 32),
  projection_generation bigint not null check (projection_generation >= 0),
  created_at timestamptz not null,
  check ((scope = 'board') = (board_id is not null))
);

-- A generation is sealed exactly once. `content_hash` covers the sealed entry
-- rows and nothing that can change afterwards: no handle, no account
-- identifier, no evidence appraisal detail. That is what lets a handle rename,
-- a block, a privacy change and an erasure all leave the hash intact, and it is
-- why `snapshot_id` survives an erasure of one of the entries it covers.
-- `sealed_entry_count` and `sealed_total_credited_token_burn` are frozen at
-- seal and are never recomputed, because republishing a recomputed aggregate
-- for the same generation would let an observer difference the two
-- publications and recover the exact figure of the participant who left.
create table ranking_projection_generations (
  ranking_view_id text not null references ranking_views(ranking_view_id),
  generation bigint not null check (generation >= 0),
  state text not null check (state in ('building','validating','active','superseded','failed')),
  source_revision bigint not null check (source_revision >= 0),
  weight_table_digest bytea not null check (octet_length(weight_table_digest) = 32),
  sealed_entry_count bigint not null default 0 check (sealed_entry_count >= 0),
  sealed_total_credited_token_burn bigint not null default 0 check (sealed_total_credited_token_burn >= 0),
  content_hash bytea check (octet_length(content_hash) = 32),
  sealed_at timestamptz,
  published_at timestamptz,
  superseded_by_generation bigint,
  primary key (ranking_view_id, generation),
  check ((sealed_at is not null) = (content_hash is not null)),
  check ((state in ('active','superseded')) = (sealed_at is not null)),
  check ((state = 'superseded') = (superseded_by_generation is not null)),
  check (superseded_by_generation is null or superseded_by_generation > generation),
  foreign key (ranking_view_id, superseded_by_generation)
    references ranking_projection_generations (ranking_view_id, generation)
);

-- A snapshot identifier a client holds must name a generation that exists.
-- Without this the durable name is a string that happens to look right.
alter table score_snapshots
  add constraint score_snapshots_generation_fk
  foreign key (ranking_view_id, generation)
  references ranking_projection_generations (ranking_view_id, generation);

create table model_alias_facts (
  model_alias_id text not null,
  provider text not null,
  canonical_model_id text not null,
  effective_at timestamptz not null,
  superseded_at timestamptz,
  source_digest bytea not null check (octet_length(source_digest) = 32),
  primary key (model_alias_id, effective_at)
);

create table social_integrity_events (
  event_id uuid primary key,
  aggregate_id uuid not null,
  aggregate_revision bigint not null check (aggregate_revision >= 0),
  event_type text not null,
  actor_account_id uuid references accounts(account_id),
  idempotency_key uuid,
  reason_code text not null,
  policy_version_digest bytea not null check (octet_length(policy_version_digest) = 32),
  event_bytes bytea not null,
  occurred_at timestamptz not null,
  unique (aggregate_id, aggregate_revision)
);

create table moderation_effects (
  moderation_effect_id uuid primary key,
  case_id uuid not null references moderation_cases(case_id),
  target_id uuid not null,
  effect text not null,
  effective_at timestamptz not null,
  review_at timestamptz,
  retracted_at timestamptz
);

create table appeal_decisions (
  appeal_decision_id uuid primary key,
  appeal_id uuid not null references appeals(appeal_id),
  decision text not null check (decision in ('upheld','partially-upheld','reversed')),
  decision_digest bytea not null check (octet_length(decision_digest) = 32),
  decided_at timestamptz not null
);


create table export_artifacts (
  export_id uuid not null references exports(export_id),
  logical_name text not null,
  media_type text not null check (media_type in ('application/jsonl','application/json','application/cbor')),
  artifact_digest bytea not null check (octet_length(artifact_digest) = 32),
  size_bytes bigint not null check (size_bytes >= 0),
  record_count bigint not null check (record_count >= 0),
  primary key (export_id, logical_name)
);

create table deletion_effects (
  deletion_job_id uuid not null references deletion_jobs(deletion_job_id),
  subsystem text not null,
  state text not null check (state in ('pending','executing','complete','failed','not-applicable')),
  effect_digest bytea,
  completed_at timestamptz,
  primary key (deletion_job_id, subsystem)
);

create table local_deletion_commands (
  command_id uuid primary key,
  deletion_job_id uuid not null references deletion_jobs(deletion_job_id),
  device_id uuid not null references devices(device_id),
  command_digest bytea not null check (octet_length(command_digest) = 32),
  state text not null check (state in ('issued','acknowledged','executing','complete','expired','failed')),
  expires_at timestamptz not null
);

create table local_deletion_receipts (
  command_id uuid primary key references local_deletion_commands(command_id),
  device_id uuid not null references devices(device_id),
  receipt_digest bytea not null check (octet_length(receipt_digest) = 32),
  completed_at timestamptz not null
);

create table platform_profiles (
  platform_profile_id text primary key,
  os_family text not null,
  os_version text not null,
  architecture text not null,
  environment text not null,
  advertised boolean not null default false check (not advertised),
  validation_state text not null check (validation_state in ('planned','candidate','exercised','certified','published','degraded','blocked','suspended','retired'))
);

create table tuf_roots (
  root_version bigint primary key check (root_version > 0),
  root_digest bytea not null unique check (octet_length(root_digest) = 32),
  threshold smallint not null check (threshold between 2 and 10),
  expires_at timestamptz not null
);

create table release_sets (
  release_set_id uuid primary key,
  version text not null unique,
  tuf_root_version bigint not null references tuf_roots(root_version),
  compatibility_registry_digest bytea not null check (octet_length(compatibility_registry_digest) = 32),
  state text not null check (state in ('draft','threshold-signed','published','active','superseded','revoked','expired')),
  published_at timestamptz,
  mandatory_after timestamptz
);

create table release_targets (
  release_set_id uuid not null references release_sets(release_set_id),
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  artifact_kind text not null check (artifact_kind in ('pkg','dmg','msix','msi','deb','rpm','apk','tar-zst','oci','ci-bundle')),
  artifact_digest bytea not null check (octet_length(artifact_digest) = 32),
  sbom_digest bytea not null check (octet_length(sbom_digest) = 32),
  provenance_digest bytea not null check (octet_length(provenance_digest) = 32),
  size_bytes bigint not null check (size_bytes > 0),
  primary key (release_set_id, platform_profile_id, artifact_kind)
);

create table platform_certifications (
  certification_id uuid primary key,
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  release_set_id uuid not null references release_sets(release_set_id),
  test_run_digest bytea not null check (octet_length(test_run_digest) = 32),
  state text not null check (state in ('candidate','exercised','certified','failed','revoked')),
  certified_at timestamptz
);

create table update_installations (
  update_installation_id uuid primary key,
  device_id uuid not null references devices(device_id),
  release_set_id uuid not null references release_sets(release_set_id),
  state text not null check (state in ('current','available','deferred','deadline','downloading','staged','installing','health-check','complete','rolled-back','blocked-version','failed')),
  previous_release_set_id uuid references release_sets(release_set_id),
  revision bigint not null check (revision >= 0),
  updated_at timestamptz not null
);

create unique index board_one_active_owner
  on board_memberships (board_id)
  where state = 'active-owner';

create index claims_account_received_idx on claims (account_id, received_at desc);
create index notifications_account_created_idx on notifications (account_id, created_at desc);
create index social_integrity_events_aggregate_idx on social_integrity_events (aggregate_id, aggregate_revision);

-- Persistence owners for state-machine aggregates that the registry named
-- but this contract did not define. AGENTS.md requires every mutable
-- aggregate to have one persistence owner; a machine pointing at a table
-- that does not exist has none. validate_state_vocabularies.py now fails
-- when a persistence_owner does not resolve here.

create table notification_events (
  notification_event_id uuid primary key,
  state text not null check (state in ('created','grouped','suppressed','ready','delivered','read','retracted','expired')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table privileged_supervisor_instances (
  privileged_supervisor_instance_id uuid primary key,
  state text not null check (state in ('absent','consent-pending','installing','active','degraded','removing','removed')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table ranked_identities (
  ranked_identity_id uuid primary key,
  state text not null check (state in ('unverified','eligible','investigating','restricted','consolidating','appealed','reversed','retired')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table service_instances (
  service_instance_id uuid primary key,
  state text not null check (state in ('unregistered','registered','starting','healthy','paused','offline','degraded','recovery','stopping','stopped','uninstalled')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table shell_sessions (
  shell_session_id uuid primary key,
  state text not null check (state in ('absent','headless','starting','connected','daemon-unavailable','stale','paused','offline','degraded','auth-required','update-required','update-blocked','permission-repair','exiting','crashed')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table update_policies (
  update_policy_id uuid primary key,
  state text not null check (state in ('current','available','deferred','deadline','downloading','staged','installing','health-check','rolled-back','complete','blocked-version','failed')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table board_membership_events (
  board_membership_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table certification_results (
  certification_result_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

-- Erasure by key destruction. D-085 and D-210.
--
-- An Article 17 erasure may not delete a sealed ranking generation, because
-- generations are immutable and durable cursors name positions inside them.
-- It also may not leave the participant attributable. The reconciliation is
-- that nothing is deleted from the sealed side at all: the retained entry
-- names an `erasure_domains` row, that row holds the only stored binding
-- between the pseudonym and the account, the binding is AEAD ciphertext under
-- a key held in `erasure_keys`, and the erasure destroys the key and appends a
-- signed record. The append-only rule survives intact; identifiability does
-- not. `docs/privacy/ERASURE_AND_KEY_DESTRUCTION.md` is the normative owner and
-- states the limits, including the ones this schema cannot enforce.

create table erasure_keys (
  key_id uuid primary key,
  algorithm text not null check (algorithm = 'AES-256-GCM'),
  key_material bytea check (key_material is null or octet_length(key_material) = 32),
  key_commitment bytea not null unique check (octet_length(key_commitment) = 32),
  created_at timestamptz not null,
  destroyed_at timestamptz,
  -- The whole mechanism in one constraint: a key is present or it is destroyed,
  -- never both and never neither. A row that claims destruction while retaining
  -- material cannot exist, and neither can a row that has silently lost its key
  -- without a destruction time to answer for it.
  check ((key_material is null) = (destroyed_at is not null))
);

create table erasure_domains (
  erasure_domain_id uuid primary key,
  key_id uuid not null unique references erasure_keys(key_id),
  -- HMAC-SHA-256 under the server-wide subject index key, over the account
  -- identifier. It exists so that `/rank/me` is an index lookup rather than a
  -- scan. It is retained after erasure and is safe to retain: its preimage is a
  -- 128-bit random identifier with no dictionary, so it confirms a guess and
  -- produces nothing on its own.
  subject_lookup_digest bytea not null unique check (octet_length(subject_lookup_digest) = 32),
  -- AES-256-GCM under `key_id`, over account_id || lineage_id, with
  -- erasure_domain_id as associated data. 32 bytes of plaintext, 16 of tag.
  bound_subject_nonce bytea not null check (octet_length(bound_subject_nonce) = 12),
  bound_subject_ciphertext bytea not null check (octet_length(bound_subject_ciphertext) = 48),
  created_at timestamptz not null
);

-- D-070 consolidation absorbs a duplicate identity's history under a surviving
-- one while preserving original period attribution, so a person may own more
-- than one erasure domain. An erasure walks this closure and destroys every key
-- in it; destroying only the survivor's key would leave the absorbed history
-- attributable.
create table erasure_domain_links (
  surviving_erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),
  absorbed_erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),
  established_at timestamptz not null,
  primary key (surviving_erasure_domain_id, absorbed_erasure_domain_id),
  check (surviving_erasure_domain_id <> absorbed_erasure_domain_id)
);

-- The signed, hash-chained erasure log. `key_commitment` is copied from the key
-- row before destruction, so the log proves which key was destroyed without
-- retaining it: a candidate key can be checked against the commitment and the
-- commitment yields nothing in the other direction.
create table erasure_records (
  erasure_record_id uuid primary key,
  chain_sequence bigint not null unique check (chain_sequence >= 1),
  previous_record_digest bytea check (octet_length(previous_record_digest) = 32),
  deletion_job_id uuid not null references deletion_jobs(deletion_job_id),
  erasure_domain_id uuid not null unique references erasure_domains(erasure_domain_id),
  key_id uuid not null unique references erasure_keys(key_id),
  key_commitment bytea not null check (octet_length(key_commitment) = 32),
  affected_generation_count bigint not null check (affected_generation_count >= 0),
  record_digest bytea not null unique check (octet_length(record_digest) = 32),
  cose_sign1 bytea not null,
  signing_key_id text not null,
  destroyed_at timestamptz not null,
  journal_mirrored_at timestamptz,
  check ((chain_sequence = 1) = (previous_record_digest is null))
);

-- Point-in-time recovery cannot exclude a table, so a restore to a point before
-- an erasure necessarily restores the key it destroyed. The erasure journal is
-- mirrored outside the backup set and replayed after every restore. The last
-- constraint is the executable form of the launch commitment that a restore
-- reapplies erasure before serving traffic: a receipt that admits traffic
-- before the reapply completed cannot be written.
create table erasure_restore_receipts (
  restore_receipt_id uuid primary key,
  restored_to timestamptz not null,
  journal_head_digest bytea not null check (octet_length(journal_head_digest) = 32),
  records_replayed bigint not null check (records_replayed >= 0),
  keys_reconfirmed_destroyed bigint not null check (keys_reconfirmed_destroyed >= 0),
  live_rows_redeleted bigint not null check (live_rows_redeleted >= 0),
  reapply_started_at timestamptz not null,
  reapply_completed_at timestamptz not null,
  traffic_admitted_at timestamptz,
  check (reapply_completed_at >= reapply_started_at),
  check (traffic_admitted_at is null or traffic_admitted_at >= reapply_completed_at)
);

create table deletion_tombstones (
  deletion_tombstone_id uuid primary key,
  subject_id uuid not null,
  tombstone_class text not null check (tombstone_class in ('account','ranked-identity','erasure-domain','local-device')),
  erasure_record_id uuid references erasure_records(erasure_record_id),
  effective_at timestamptz not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  unique (tombstone_class, subject_id),
  check ((tombstone_class = 'erasure-domain') = (erasure_record_id is not null))
);

create table export_download_grants (
  export_download_grant_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table identity_events (
  identity_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table identity_investigations (
  identity_investigation_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table notification_deliveries (
  notification_delivery_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table oauth_authorization_events (
  oauth_authorization_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table presence_events (
  presence_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table pricing_interpretations (
  pricing_interpretation_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table privileged_consents (
  privileged_consent_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table projection_generations (
  projection_generation_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table ranking_events (
  ranking_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table release_transparency_events (
  release_transparency_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table service_events (
  service_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table session_tokens (
  session_token_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table shell_ipc_peers (
  shell_ipc_peer_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

create table social_events (
  social_event_id uuid primary key,
  subject_id uuid not null,
  event_type text not null,
  created_at timestamptz not null
);

create table tuf_metadata (
  tuf_metadata_id uuid primary key,
  subject_id uuid not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);


-- ---------------------------------------------------------------------------
-- Sealed ranking generations, entries, contributions and events. PF-052.
-- ---------------------------------------------------------------------------

-- One immutable row per position in a sealed generation. It is keyed on the
-- erasure-domain pseudonym rather than on the account, which is the single
-- change that makes an Article 17 erasure expressible without deleting a row or
-- rebuilding a generation. Every ADR-020 input is persisted alongside the
-- result, so an entry is recomputable from its own record and explainable to
-- the participant it describes without reading anything else.
--
-- There is no erasure column here. Erasure is recorded once, on the domain's
-- key, and the projection derives suppression from it. Marking entries would
-- mean an update per entry per erasure against a table the contract calls
-- immutable, which is the thing this design exists to avoid.
create table ranking_entries (
  ranking_view_id text not null,
  generation bigint not null,
  position integer not null check (position >= 1),
  erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),
  token_burn_total bigint not null check (token_burn_total >= 0),
  evidence_profile_id text not null,
  evidence_class text not null check (evidence_class in ('hardened','standard')),
  trust_state_at_projection text not null check (trust_state_at_projection in ('unverified','eligible','investigating','restricted','consolidating','appealed','reversed')),
  evidence_weight_hundredths smallint not null check (evidence_weight_hundredths between 25 and 100),
  trust_weight_hundredths smallint not null check (trust_weight_hundredths between 25 and 100),
  confidence_weight_hundredths smallint not null check (confidence_weight_hundredths between 25 and 100),
  credited_token_burn bigint not null check (credited_token_burn >= 0),
  first_reached_at timestamptz not null,
  primary key (ranking_view_id, generation, position),
  unique (ranking_view_id, generation, erasure_domain_id),
  foreign key (ranking_view_id, generation)
    references ranking_projection_generations (ranking_view_id, generation),
  -- The weight only ever discounts, so the credited figure can never exceed the
  -- raw one. ADR-020 fixes the ceiling at 100 for exactly this reason.
  check (credited_token_burn <= token_burn_total)
);

-- Claim-level explainability for a period figure. `claim_id` is nullable and
-- clears on delete because an erasure deletes the claim while this row is
-- retained: the arithmetic that produced a sealed standing stays auditable and
-- the link to the claim that produced it does not.
create table score_contributions (
  contribution_id uuid primary key,
  period_id uuid not null references periods(period_id),
  erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),
  claim_id uuid references claims(claim_id) on delete set null,
  origin text not null check (origin in ('claim','correction','consolidation','retraction')),
  token_burn_delta bigint not null,
  source_revision bigint not null check (source_revision >= 0),
  superseded_by_contribution_id uuid references score_contributions(contribution_id),
  created_at timestamptz not null,
  unique (period_id, claim_id, origin),
  check (superseded_by_contribution_id <> contribution_id)
);

-- Movement, overtake and streak events. The unique constraint is the duplicate
-- suppression rule the product specification requires, expressed as a
-- constraint rather than as worker discipline: one event of a given type per
-- subject per generation per view, whatever the worker retries.
create table ranking_movement_events (
  ranking_movement_event_id uuid primary key,
  ranking_view_id text not null,
  event_type text not null check (event_type in ('rank-movement','overtake','streak-started','streak-extended','streak-broken')),
  subject_erasure_domain_id uuid not null references erasure_domains(erasure_domain_id),
  counterpart_erasure_domain_id uuid references erasure_domains(erasure_domain_id),
  prior_generation bigint not null check (prior_generation >= 0),
  current_generation bigint not null,
  prior_position integer check (prior_position >= 1),
  current_position integer check (current_position >= 1),
  streak_length integer check (streak_length >= 1),
  retracted_at timestamptz,
  retraction_reason_code text,
  created_at timestamptz not null,
  foreign key (ranking_view_id, prior_generation)
    references ranking_projection_generations (ranking_view_id, generation),
  foreign key (ranking_view_id, current_generation)
    references ranking_projection_generations (ranking_view_id, generation),
  check (current_generation > prior_generation),
  check ((event_type = 'overtake') = (counterpart_erasure_domain_id is not null)),
  check ((retracted_at is null) = (retraction_reason_code is null)),
  check (subject_erasure_domain_id <> counterpart_erasure_domain_id),
  unique (ranking_view_id, event_type, subject_erasure_domain_id, current_generation)
);


-- ---------------------------------------------------------------------------
-- Indexes. PF-048.
--
-- PostgreSQL indexes the referenced side of a foreign key and not the
-- referencing side, so every unindexed referencing column turns a delete on the
-- parent into a sequential scan of the child and holds a lock while it runs.
-- Ninety-eight tables carried four indexes. The erasure path in particular
-- deletes from `accounts`, which thirty-one tables reference.
--
-- Every index below is either the referencing side of a foreign key or a
-- documented query path named in
-- `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`. Each is created with
-- CONCURRENTLY in the migration that introduces it, which is one of the reasons
-- D-097 selected a migration tool with a no-transaction directive; this
-- contract states the target shape rather than the migration text.
-- ---------------------------------------------------------------------------

-- Foreign-key referencing side: identity and session.
create index linked_identities_account_idx on linked_identities (account_id);
create index web_sessions_account_idx on web_sessions (account_id);
create index web_sessions_family_idx on web_sessions (token_family_id);
create index recovery_codes_account_idx on recovery_codes (account_id);
create index optional_authenticators_account_idx on optional_authenticators (account_id);
create index session_families_account_idx on session_families (account_id);
create index native_sessions_family_idx on native_sessions (token_family_id);
create index native_sessions_device_idx on native_sessions (device_id);

-- Foreign-key referencing side: device and lineage.
create index devices_account_idx on devices (account_id);
create index device_keys_device_idx on device_keys (device_id);
create index device_enrollment_grants_account_idx on device_enrollment_grants (account_id);
create index adapter_installations_device_idx on adapter_installations (device_id);
create index device_lineages_account_idx on device_lineages (account_id);
create index device_key_events_device_idx on device_key_events (device_id, occurred_at desc);
create index checkpoint_receipts_device_idx on checkpoint_receipts (device_id, last_sequence desc);

-- Foreign-key referencing side: claims and verification.
create index claim_challenges_account_idx on claim_challenges (account_id);
create index claim_challenges_device_idx on claim_challenges (device_id);
create index claims_device_idx on claims (device_id);
create index claims_challenge_idx on claims (challenge_id);
create index claim_corrections_claim_idx on claim_corrections (claim_id);
create index claim_corrections_replacement_idx on claim_corrections (replacement_claim_id);
create index quarantines_account_idx on quarantines (account_id);
create index quarantines_device_idx on quarantines (device_id);
create index quarantines_claim_idx on quarantines (claim_id);
create index evidence_assessments_claim_idx on evidence_assessments (claim_id);
create index verifier_appraisals_claim_idx on verifier_appraisals (claim_id);
create index cost_interpretations_claim_idx on cost_interpretations (claim_id);
create index cost_interpretations_dataset_idx on cost_interpretations (pricing_dataset_id);

-- Foreign-key referencing side: moderation and appeal.
create index moderation_cases_account_idx on moderation_cases (account_id);
create index moderation_actions_case_idx on moderation_actions (case_id);
create index moderation_effects_case_idx on moderation_effects (case_id);
create index appeals_case_idx on appeals (case_id);
create index appeals_account_idx on appeals (account_id);
create index appeal_decisions_appeal_idx on appeal_decisions (appeal_id);

-- Foreign-key referencing side: ranking.
create index minute_scores_account_idx on minute_scores (account_id, minute_start desc);
create index period_scores_period_idx on period_scores (period_id);
create index period_scores_account_idx on period_scores (account_id);
create index ranking_corrections_correction_idx on ranking_corrections (correction_id);
create index ranking_views_period_idx on ranking_views (period_id);
create index ranking_views_board_idx on ranking_views (board_id);
create index periods_season_idx on periods (season_id);
create index ranking_entries_domain_idx on ranking_entries (erasure_domain_id);
create index score_contributions_period_domain_idx on score_contributions (period_id, erasure_domain_id);
create index score_contributions_claim_idx on score_contributions (claim_id);
create index score_contributions_superseded_idx on score_contributions (superseded_by_contribution_id);
create index ranking_movement_events_subject_idx on ranking_movement_events (subject_erasure_domain_id, created_at desc);
create index ranking_movement_events_counterpart_idx on ranking_movement_events (counterpart_erasure_domain_id);
create index ranking_movement_events_prior_idx on ranking_movement_events (ranking_view_id, prior_generation);
create index ranking_movement_events_current_idx on ranking_movement_events (ranking_view_id, current_generation);
create index ranking_projection_generations_supersede_idx
  on ranking_projection_generations (ranking_view_id, superseded_by_generation);

-- Foreign-key referencing side: social and boards.
create index friend_requests_requester_idx on friend_requests (requester_account_id);
create index friend_requests_target_idx on friend_requests (target_account_id);
create index friend_edges_reverse_idx on friend_edges (account_id_b, account_id_a);
create index blocks_reverse_idx on blocks (blocked_account_id, blocker_account_id);
create index rival_edges_reverse_idx on rival_edges (rival_account_id, account_id);
create index organizations_owner_idx on organizations (owner_account_id);
create index communities_owner_idx on communities (owner_account_id);
create index board_memberships_account_idx on board_memberships (account_id);
create index board_invites_board_idx on board_invites (board_id);
create index presence_leases_device_idx on presence_leases (device_id);
create index notifications_actor_idx on notifications (actor_account_id);
create index social_integrity_events_actor_idx on social_integrity_events (actor_account_id);

-- Foreign-key referencing side: rights, erasure, release.
create index exports_account_idx on exports (account_id);
create index deletion_jobs_account_idx on deletion_jobs (account_id);
create index local_deletion_commands_job_idx on local_deletion_commands (deletion_job_id);
create index local_deletion_commands_device_idx on local_deletion_commands (device_id);
create index local_deletion_receipts_device_idx on local_deletion_receipts (device_id);
create index erasure_records_job_idx on erasure_records (deletion_job_id);
create index deletion_tombstones_erasure_record_idx on deletion_tombstones (erasure_record_id);
create index erasure_domain_links_absorbed_idx on erasure_domain_links (absorbed_erasure_domain_id);
create index release_sets_root_idx on release_sets (tuf_root_version);
create index release_targets_profile_idx on release_targets (platform_profile_id);
create index platform_certifications_profile_idx on platform_certifications (platform_profile_id);
create index platform_certifications_release_idx on platform_certifications (release_set_id);
create index update_installations_device_idx on update_installations (device_id);
create index update_installations_release_idx on update_installations (release_set_id);
create index update_installations_previous_release_idx on update_installations (previous_release_set_id);

-- Documented query paths that no foreign key implies.
--
-- The leaderboard page itself needs no index beyond the `ranking_entries`
-- primary key: a sealed generation is read by ascending position from a
-- position anchor, which is a range scan on the leading columns of that key.
-- That is the whole reason the cursor anchors on position.
create index erasure_keys_live_idx on erasure_keys (key_id) where destroyed_at is null;
create index outbox_events_unprocessed_idx on outbox_events (created_at) where processed_at is null;
create index idempotency_records_expiry_idx on idempotency_records (expires_at);
create index claim_challenges_expiry_idx on claim_challenges (expires_at) where consumed_at is null;
create index presence_leases_expiry_idx on presence_leases (expires_at);
create index board_invites_expiry_idx on board_invites (expires_at) where state = 'pending';
create index exports_expiry_idx on exports (expires_at);
create index oauth_transactions_expiry_idx on oauth_transactions (expires_at);
create index device_enrollment_grants_expiry_idx on device_enrollment_grants (expires_at) where consumed_at is null;
create index local_deletion_commands_expiry_idx on local_deletion_commands (expires_at);
create index seasons_window_idx on seasons (starts_at, ends_at);
create index periods_type_window_idx on periods (period_type, starts_at desc);
create index score_snapshots_view_generation_idx on score_snapshots (ranking_view_id, generation desc);
