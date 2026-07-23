-- P-1140D REPAIRED PLANNING MIGRATION CONTRACT.
-- PostgreSQL 16 executable ownership, constraint, and transaction-boundary contract.
-- It becomes implementation input only after the explicit P-1104 authorization gate.
-- Country leaderboards remain post-launch under D-052 and are intentionally absent.

create table accounts (
  account_id uuid primary key,
  state text not null,
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
  unique (provider, provider_subject)
);

create table web_sessions (
  session_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  token_family_id uuid not null,
  token_hash bytea not null unique,
  state text not null,
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
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create table devices (
  device_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  installation_id uuid not null unique,
  lineage_id uuid not null,
  platform_profile_id text not null,
  state text not null
);

create table device_keys (
  device_key_id text primary key,
  device_id uuid not null references devices(device_id),
  public_key bytea not null,
  algorithm text not null check (algorithm = 'Ed25519'),
  protection_class text not null,
  state text not null
);

create table device_enrollment_grants (
  enrollment_grant_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  public_key_hash bytea not null,
  collector_digest bytea not null,
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
  continuity_state text not null
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
  state text not null
);

create table evidence_assessments (
  evidence_assessment_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  verifier_profile_id text not null,
  public_state text not null,
  provenance_state text not null check (provenance_state in ('verified','partial','unverified','rejected')),
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken')),
  integrity_state text not null check (integrity_state in ('verified','degraded','failed')),
  reason_codes text[] not null default '{}',
  created_at timestamptz not null
);

create table moderation_cases (
  case_id uuid primary key,
  account_id uuid references accounts(account_id),
  state text not null,
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
  state text not null,
  created_at timestamptz not null
);

create table periods (
  period_id uuid primary key,
  period_type text not null check (period_type in ('daily','weekly','monthly','seasonal','yearly','lifetime')),
  starts_at timestamptz,
  ends_at timestamptz,
  rules_version text not null
);

create table minute_scores (
  period_id uuid not null references periods(period_id),
  account_id uuid not null references accounts(account_id),
  minute_start timestamptz not null,
  score bigint not null,
  primary key (period_id, account_id, minute_start)
);

create table period_scores (
  ranking_view_id text not null,
  period_id uuid not null references periods(period_id),
  account_id uuid not null references accounts(account_id),
  score bigint not null,
  generation bigint not null,
  primary key (ranking_view_id, period_id, account_id)
);

create table score_snapshots (
  snapshot_id uuid primary key,
  ranking_view_id text not null,
  generation bigint not null,
  content_hash bytea not null,
  created_at timestamptz not null
);

create table ranking_corrections (
  ranking_correction_id uuid primary key,
  correction_id uuid not null references claim_corrections(correction_id),
  ranking_view_id text not null,
  delta bigint not null
);

create table pricing_datasets (
  pricing_dataset_id text primary key,
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
  state text not null,
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
  state text not null
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
  state text not null,
  primary key (account_id, rival_account_id)
);

create table organizations (
  organization_id uuid primary key,
  owner_account_id uuid not null references accounts(account_id),
  name text not null
);

create table communities (
  community_id uuid primary key,
  owner_account_id uuid not null references accounts(account_id),
  name text not null
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
  role text not null,
  state text not null,
  primary key (board_id, account_id)
);

create table board_invites (
  board_invite_id uuid primary key,
  board_id uuid not null references boards(board_id),
  state text not null,
  expires_at timestamptz not null
);

create table presence_leases (
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  state text not null,
  expires_at timestamptz not null,
  primary key (account_id, device_id)
);

create table notifications (
  notification_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  event_type text not null check (event_type in ('friend_request','board_invitation','rank_overtake','moderation','appeal','security','compatibility','release')),
  state text not null check (state in ('queued','delivered','read','suppressed','expired')),
  actor_account_id uuid references accounts(account_id),
  scope_id uuid,
  grouping_digest bytea not null check (octet_length(grouping_digest) = 32),
  created_at timestamptz not null
);

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

create table audit_events (
  audit_event_id uuid primary key,
  actor_type text not null,
  actor_id uuid,
  event_type text not null,
  target_type text not null,
  target_digest bytea not null check (octet_length(target_digest) = 32),
  reason_code text not null,
  created_at timestamptz not null
);

create table exports (
  export_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null,
  expires_at timestamptz
);

create table deletion_jobs (
  deletion_job_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  scope text not null,
  state text not null
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
  state text not null check (state in ('reserved','committed','failed')),
  expires_at timestamptz not null,
  primary key (actor_account_id, idempotency_key)
);

create table session_families (
  token_family_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('active','revoked','compromised','expired')),
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
  provenance_state text not null,
  continuity_state text not null,
  integrity_state text not null,
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

create table ranking_projection_generations (
  ranking_view_id text not null references ranking_views(ranking_view_id),
  generation bigint not null check (generation >= 0),
  state text not null check (state in ('building','published','superseded','failed')),
  source_revision bigint not null check (source_revision >= 0),
  published_at timestamptz,
  primary key (ranking_view_id, generation)
);

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
  decision text not null check (decision in ('needs_information','upheld','partially_upheld','reversed','expired')),
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
  state text not null check (state in ('pending','executing','completed','failed','not-applicable')),
  effect_digest bytea,
  completed_at timestamptz,
  primary key (deletion_job_id, subsystem)
);

create table local_deletion_commands (
  command_id uuid primary key,
  deletion_job_id uuid not null references deletion_jobs(deletion_job_id),
  device_id uuid not null references devices(device_id),
  command_digest bytea not null check (octet_length(command_digest) = 32),
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
  validation_state text not null check (validation_state in ('planned-validation-required','certified','blocked','retired'))
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
  state text not null check (state in ('draft','signed','published','revoked','expired')),
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
  state text not null check (state in ('candidate','certified','failed','revoked')),
  certified_at timestamptz
);

create table update_installations (
  update_installation_id uuid primary key,
  device_id uuid not null references devices(device_id),
  release_set_id uuid not null references release_sets(release_set_id),
  state text not null check (state in ('available','downloading','verified','installing','active','rolled_back','blocked','failed')),
  previous_release_set_id uuid references release_sets(release_set_id),
  revision bigint not null check (revision >= 0),
  updated_at timestamptz not null
);

create unique index board_one_active_owner
  on board_memberships (board_id)
  where role = 'owner' and state = 'active';

create index claims_account_received_idx on claims (account_id, received_at desc);
create index notifications_account_created_idx on notifications (account_id, created_at desc);
create index social_integrity_events_aggregate_idx on social_integrity_events (aggregate_id, aggregate_revision);
