-- Planning-grade PostgreSQL DDL. Not an executable migration history.
-- UUIDv7 generation is application-owned until implementation selects a database function.

create table accounts (
  account_id uuid primary key,
  state text not null check (state in ('active','restricted','suspended','deleting','deleted')),
  created_at timestamptz not null,
  deleted_at timestamptz
);

create table account_handles (
  account_id uuid primary key references accounts(account_id),
  display_handle text not null,
  normalized_handle text not null unique,
  confusable_skeleton text not null unique,
  unicode_policy_version text not null,
  changed_at timestamptz not null
);

create table linked_identities (
  identity_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  provider text not null check (provider in ('github','x')),
  provider_subject text not null,
  created_at timestamptz not null,
  unique (provider, provider_subject)
);

create table web_sessions (
  session_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  token_hash bytea not null unique,
  created_at timestamptz not null,
  expires_at timestamptz not null,
  revoked_at timestamptz
);

create table recovery_codes (
  recovery_code_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  code_hash bytea not null unique,
  created_at timestamptz not null,
  consumed_at timestamptz
);

create table optional_authenticators (
  authenticator_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  kind text not null check (kind in ('passkey','hardware-key')),
  credential_id bytea not null unique,
  public_key bytea not null,
  created_at timestamptz not null,
  revoked_at timestamptz
);

create table oauth_transactions (
  oauth_transaction_id uuid primary key,
  provider text not null check (provider in ('github','x')),
  state_hash bytea not null unique,
  pkce_verifier_hash bytea,
  created_at timestamptz not null,
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create table devices (
  device_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('active','quarantined','revoked')),
  platform text not null,
  build_version text,
  created_at timestamptz not null,
  revoked_at timestamptz
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

create table device_enrollment_grants (
  enrollment_grant_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  public_key_hash bytea not null,
  nonce bytea not null,
  created_at timestamptz not null,
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create table adapter_installations (
  adapter_installation_id uuid primary key,
  device_id uuid not null references devices(device_id),
  adapter_id text not null,
  adapter_version text not null,
  lifecycle text not null,
  evidence_ceiling text not null,
  installed_at timestamptz not null,
  unique (device_id, adapter_id)
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
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','forked','reset')),
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
  adapter_id text not null,
  adapter_version text not null,
  model_id text not null,
  token_burn_total bigint not null check (token_burn_total >= 0),
  evidence_state text not null check (evidence_state in ('standard','hardened')),
  policy_version text not null,
  received_at timestamptz not null,
  unique (device_id, device_sequence),
  unique (device_id, payload_hash)
);

create table claim_payloads (
  claim_id uuid primary key references claims(claim_id),
  canonical_payload bytea not null,
  signature bytea not null,
  encoded_bytes integer not null check (encoded_bytes between 1 and 65536)
);

create table claim_rejections (
  rejection_id uuid primary key,
  account_id uuid references accounts(account_id),
  device_id uuid references devices(device_id),
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
  scope text not null,
  reason_code text not null,
  policy_version text not null,
  created_at timestamptz not null,
  expires_at timestamptz,
  lifted_at timestamptz
);

create table evidence_assessments (
  evidence_assessment_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  evidence_state text not null check (evidence_state in ('standard','hardened')),
  policy_version text not null,
  reason_code text,
  created_at timestamptz not null
);

create table moderation_cases (
  case_id uuid primary key,
  account_id uuid references accounts(account_id),
  device_id uuid references devices(device_id),
  state text not null check (state in ('open','under_review','resolved','appealed','closed')),
  reason_code text not null,
  policy_version text not null,
  created_at timestamptz not null,
  closed_at timestamptz
);

create table moderation_actions (
  moderation_action_id uuid primary key,
  case_id uuid not null references moderation_cases(case_id),
  action text not null,
  actor_type text not null,
  actor_id text not null,
  reason_code text not null,
  evidence_commitment bytea,
  appeal_eligible boolean not null,
  created_at timestamptz not null
);

create table appeals (
  appeal_id uuid primary key,
  case_id uuid not null references moderation_cases(case_id),
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('submitted','needs_information','under_review','upheld','partially_upheld','reversed','expired')),
  created_at timestamptz not null,
  resolved_at timestamptz
);

create table periods (
  period_id uuid primary key,
  period_type text not null check (period_type in ('daily','weekly','monthly','seasonal','yearly','lifetime')),
  starts_at timestamptz,
  ends_at timestamptz,
  rules_version text not null,
  finalized_at timestamptz
);

create table minute_scores (
  period_id uuid not null references periods(period_id),
  account_id uuid not null references accounts(account_id),
  minute_start timestamptz not null,
  score bigint not null check (score >= 0),
  primary key (period_id, account_id, minute_start)
);

create table period_scores (
  scope_type text not null,
  scope_id uuid not null,
  period_id uuid not null references periods(period_id),
  account_id uuid not null references accounts(account_id),
  evidence_filter text not null,
  score bigint not null check (score >= 0),
  first_reached_score_at timestamptz not null,
  generation bigint not null,
  primary key (scope_type, scope_id, period_id, account_id, evidence_filter)
);

create table score_snapshots (
  snapshot_id uuid primary key,
  scope_type text not null,
  scope_id uuid not null,
  period_id uuid not null references periods(period_id),
  generation bigint not null,
  content_hash bytea not null,
  created_at timestamptz not null
);

create table ranking_corrections (
  ranking_correction_id uuid primary key,
  correction_id uuid not null references claim_corrections(correction_id),
  period_id uuid not null references periods(period_id),
  delta bigint not null,
  created_at timestamptz not null
);

create table pricing_datasets (
  pricing_dataset_id text primary key,
  currency text not null,
  effective_at timestamptz not null,
  provenance text not null,
  content_hash bytea not null,
  created_at timestamptz not null
);

create table pricing_entries (
  pricing_dataset_id text not null references pricing_datasets(pricing_dataset_id),
  provider_id text not null,
  model_id text not null,
  category text not null,
  unit_price numeric(30,12) not null check (unit_price >= 0),
  primary key (pricing_dataset_id, provider_id, model_id, category)
);

create table cost_interpretations (
  cost_interpretation_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  pricing_dataset_id text not null references pricing_datasets(pricing_dataset_id),
  estimated_cost numeric(30,12),
  state text not null check (state in ('estimated','unpriced','local-compute')),
  created_at timestamptz not null
);

create table profiles (
  account_id uuid primary key references accounts(account_id),
  avatar_url text,
  bio text,
  visibility jsonb not null,
  updated_at timestamptz not null
);

create table friend_requests (
  friend_request_id uuid primary key,
  requester_account_id uuid not null references accounts(account_id),
  target_account_id uuid not null references accounts(account_id),
  state text not null check (state in ('pending','accepted','declined','cancelled','expired','blocked')),
  created_at timestamptz not null,
  expires_at timestamptz not null,
  unique (requester_account_id, target_account_id)
);

create table friend_edges (
  account_id_a uuid not null references accounts(account_id),
  account_id_b uuid not null references accounts(account_id),
  created_at timestamptz not null,
  primary key (account_id_a, account_id_b),
  check (account_id_a <> account_id_b)
);

create table blocks (
  blocker_account_id uuid not null references accounts(account_id),
  blocked_account_id uuid not null references accounts(account_id),
  created_at timestamptz not null,
  primary key (blocker_account_id, blocked_account_id),
  check (blocker_account_id <> blocked_account_id)
);

create table rival_edges (
  account_id uuid not null references accounts(account_id),
  rival_account_id uuid not null references accounts(account_id),
  source text not null check (source in ('selected','suggested')),
  visibility text not null,
  created_at timestamptz not null,
  primary key (account_id, rival_account_id)
);

create table organizations (
  organization_id uuid primary key,
  name text not null,
  owner_account_id uuid not null references accounts(account_id),
  created_at timestamptz not null
);

create table communities (
  community_id uuid primary key,
  name text not null,
  owner_account_id uuid not null references accounts(account_id),
  created_at timestamptz not null
);

create table boards (
  board_id uuid primary key,
  board_type text not null check (board_type in ('private','organization','hacker-house','community','country')),
  visibility text not null check (visibility in ('public','unlisted','invite-only','private')),
  owner_account_id uuid not null references accounts(account_id),
  organization_id uuid references organizations(organization_id),
  community_id uuid references communities(community_id),
  policy_version text not null,
  created_at timestamptz not null
);

create table board_memberships (
  board_id uuid not null references boards(board_id),
  account_id uuid not null references accounts(account_id),
  role text not null check (role in ('owner','admin','moderator','member','viewer')),
  state text not null,
  joined_at timestamptz not null,
  primary key (board_id, account_id)
);

create table board_invites (
  board_invite_id uuid primary key,
  board_id uuid not null references boards(board_id),
  inviter_account_id uuid not null references accounts(account_id),
  target_account_id uuid references accounts(account_id),
  state text not null,
  created_at timestamptz not null,
  expires_at timestamptz not null
);

create table country_assertions (
  account_id uuid primary key references accounts(account_id),
  country_code text not null,
  evidence_level text not null,
  visibility text not null,
  policy_version text not null,
  asserted_at timestamptz not null,
  change_allowed_at timestamptz not null
);

create table presence_leases (
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  state text not null check (state in ('active','idle','private')),
  agent_family text,
  evidence_state text,
  renewed_at timestamptz not null,
  expires_at timestamptz not null,
  primary key (account_id, device_id)
);

create table notifications (
  notification_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  event_type text not null,
  grouping_key text,
  reason_code text,
  payload jsonb not null,
  created_at timestamptz not null,
  read_at timestamptz
);

create table notification_preferences (
  account_id uuid primary key references accounts(account_id),
  preferences jsonb not null,
  quiet_hours jsonb,
  updated_at timestamptz not null
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

create table worker_checkpoints (
  worker_name text primary key,
  checkpoint jsonb not null,
  updated_at timestamptz not null
);

create table audit_events (
  audit_event_id uuid primary key,
  actor_type text not null,
  actor_id text,
  event_type text not null,
  reason_code text,
  safe_metadata jsonb not null,
  created_at timestamptz not null
);

create table exports (
  export_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('accepted','running','completed','failed','expired')),
  object_key text,
  created_at timestamptz not null,
  expires_at timestamptz
);

create table deletion_jobs (
  deletion_job_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  scope text not null check (scope in ('server','local','everything')),
  state text not null check (state in ('accepted','cooling_off','running','completed','failed')),
  created_at timestamptz not null,
  completed_at timestamptz
);

create table feature_flags (
  flag_key text primary key,
  value jsonb not null,
  updated_at timestamptz not null
);

create table schema_migrations (
  version text primary key,
  checksum bytea not null,
  applied_at timestamptz not null
);
