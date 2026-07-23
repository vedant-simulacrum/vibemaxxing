-- BLOCKED STRUCTURAL PLANNING PLACEHOLDER.
-- This file is intentionally executable only for inventory validation. It is not a
-- production migration history and must not generate implementation code. P-1140B-D
-- own the authoritative fields, constraints, transactions, indexes and migrations.
-- Country leaderboards are post-launch under D-052 and are absent from this schema.

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
  dimensions jsonb not null,
  reason_codes jsonb not null,
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
  visibility jsonb not null,
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
  primary key (account_id_a, account_id_b)
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
  owner_account_id uuid not null references accounts(account_id),
  policy_version text not null
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
  event_type text not null,
  payload jsonb not null,
  created_at timestamptz not null
);

create table notification_preferences (
  account_id uuid primary key references accounts(account_id),
  preferences jsonb not null,
  quiet_hours jsonb
);

create table outbox_events (
  outbox_id uuid primary key,
  event_type text not null,
  aggregate_id uuid not null,
  payload jsonb not null,
  processed_at timestamptz
);

create table worker_checkpoints (
  worker_name text primary key,
  checkpoint jsonb not null,
  updated_at timestamptz not null
);

create table audit_events (
  audit_event_id uuid primary key,
  actor_type text not null,
  event_type text not null,
  safe_metadata jsonb not null,
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
  value jsonb not null
);

create table schema_migrations (
  version text primary key,
  checksum bytea not null,
  applied_at timestamptz not null
);
