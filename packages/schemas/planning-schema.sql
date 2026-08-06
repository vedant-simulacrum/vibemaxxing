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

-- A block is the existence of a row rather than a state, which is why it has
-- no state column and no machine. `established_at` is not decoration: current
-- viewer authorization under D-386 compares what it read against what is
-- present when the response is emitted, and existence alone cannot order two
-- changes to the same pair.
create table blocks (
  blocker_account_id uuid not null references accounts(account_id),
  blocked_account_id uuid not null references accounts(account_id),
  established_at timestamptz not null,
  primary key (blocker_account_id, blocked_account_id),
  check (blocker_account_id <> blocked_account_id)
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

-- The current presence answer for one device, server-derived under D-073 from
-- qualifying native pulses. `lease_generation` is monotonic per row and is what
-- makes a pulse from a resumed process unable to revive an expired lease: the
-- pulse names the generation it was minted under, and a pulse naming a
-- superseded generation is discarded rather than applied.
--
-- `visibility` is an independent policy and not a state. A private participant
-- still has a lease and still transitions; what changes is who may read the
-- projection of it. Collapsing the two would make going private look like going
-- offline to the server as well as to the viewer.
create table presence_leases (
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  state text not null check (state in ('absent','active','idle','expired','revoked')),
  lease_generation bigint not null default 0 check (lease_generation >= 0),
  visibility text not null default 'authorized-viewers' check (visibility in ('authorized-viewers','private')),
  last_qualifying_pulse_at timestamptz,
  expires_at timestamptz not null,
  primary key (account_id, device_id),
  check (state not in ('active','idle') or last_qualifying_pulse_at is not null)
);

-- The recipient inbox projection, and the notification authority: an item exists
-- for the recipient exactly when a row is here. Push and email are hints about
-- this row and are recorded in `notification_deliveries`; neither can create an
-- item, mark one read, or keep one alive.
--
-- Partitioned by creation month: retention is 90 days, no foreign key points
-- at it, and its only uniqueness is its own identity, so the partition key can
-- join the primary key without weakening any invariant.
--
-- The row carries references and no rendered text. There is no title, body or
-- summary column, and D-421 records why: a stored sentence would freeze a handle,
-- a figure and an authorization decision at write time, so a rename would be
-- wrong, a block would leak, and a retraction would arrive after the recipient
-- had already read the claim it withdraws. The surface renders from current state
-- at read time or renders nothing.
create table notifications (
  notification_id uuid not null,
  account_id uuid not null references accounts(account_id),
  event_type text not null check (event_type in ('friend_request','board_invitation','rank_overtake','moderation','appeal','security','compatibility','release')),
  state text not null check (state in ('created','grouped','ready','delivered','read','suppressed','retracted','expired')),
  actor_account_id uuid references accounts(account_id),
  scope_id uuid,
  grouping_digest bytea not null check (octet_length(grouping_digest) = 32),
  -- How many source events this one item stands for. A group is one item with a
  -- count, never n items, so grouping cannot be undone into the flood it collapsed.
  group_count integer not null default 1 check (group_count >= 1),
  -- The D-386 authorization revision the item was generated under. It is recorded
  -- rather than trusted: the read path rechecks current authorization and refuses
  -- to render an item whose recorded revision is stale, so a board removal or a
  -- block between generation and read cannot be served out of the inbox.
  authorization_revision bigint not null check (authorization_revision >= 0),
  created_at timestamptz not null,
  delivered_at timestamptz,
  read_at timestamptz,
  retracted_at timestamptz,
  retraction_reason_code text,
  primary key (notification_id, created_at),
  -- `delivered_at` is set exactly when the item reached the inbox, which is what
  -- makes a read impossible to fake: a `read` row with no delivery time is the
  -- shape a push acknowledgement would produce if acknowledgement were allowed to
  -- stand in for a read, and it cannot exist. Retraction and expiry are reachable
  -- from before delivery as well as after, so they constrain the time in one
  -- direction only.
  check (state not in ('delivered','read') or delivered_at is not null),
  check (delivered_at is null or state in ('delivered','read','retracted','expired')),
  check ((state = 'read') = (read_at is not null)),
  check ((state = 'retracted') = (retracted_at is not null)),
  check ((retraction_reason_code is not null) = (state = 'retracted')),
  check (read_at is null or read_at >= delivered_at),
  check (retracted_at is null or delivered_at is null or retracted_at >= delivered_at)
) partition by range (created_at);

create table notifications_default partition of notifications default;

-- Preferences gate two different things and the columns say which. The four
-- category booleans decide whether an inbox item is created at all. Quiet hours
-- and the two opt-in timestamps decide only whether a best-effort transport
-- carries a hint about an item that exists either way: D-422 records that quiet
-- hours never withhold an inbox item, because the inbox is the authority and a
-- silenced authority is a lost notification rather than a deferred one.
--
-- `security_enabled` is constrained true. Security and recovery notices cannot be
-- muted, and a preferences row that claims otherwise is unrepresentable rather
-- than overridden in application code.
create table notification_preferences (
  account_id uuid primary key references accounts(account_id),
  social_enabled boolean not null,
  ranking_enabled boolean not null,
  moderation_enabled boolean not null,
  security_enabled boolean not null check (security_enabled),
  quiet_hours_start_minute smallint check (quiet_hours_start_minute between 0 and 1439),
  quiet_hours_end_minute smallint check (quiet_hours_end_minute between 0 and 1439),
  timezone_name text not null,
  -- Null until the participant opts in. No transport other than the inbox ships
  -- at launch under D-086, so both stay null and the constraint on
  -- `notification_deliveries` makes a push or email row unwritable.
  push_opt_in_at timestamptz,
  email_opt_in_at timestamptz
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

-- One command per enrolled device per deletion job. The state column is the
-- device-reported lifecycle and the `local-deletion-command` machine owns it; the
-- disposition column is what the participant is shown, and it is the state
-- coarsened by two facts the state alone cannot carry.
--
-- `unreachable` and `expired` are the same machine state and are not the same
-- answer. A command that expired without ever being acknowledged reached no
-- device; one that expired after acknowledgement reached a device that then
-- stopped. Telling a participant "expired" for both hides which of their devices
-- never heard the request at all, and D-076 requires each device to be reported
-- independently.
--
-- `waived` is not derivable from the machine, because a waiver is the
-- participant's act rather than the device's. It is recorded and it is not
-- terminal: a waived device that later returns and completes reports `complete`,
-- which is why the disposition expression tests completion first.
--
-- The disposition is not a second opinion about the row. The check makes it equal
-- the coarsening by construction, so it cannot drift from the state it summarizes.
--
-- `device_id` carries no foreign key. D-425 records why: `packages/schemas/data-disposition-v1.json`
-- classifies this table `retain-unlinked` and `devices` `delete`, so an erasure
-- deletes the device row while this row survives as proof the request was
-- honoured. A foreign key makes that transaction fail, which is the opposite of
-- what a retained-unlinked identifier means.
create table local_deletion_commands (
  command_id uuid primary key,
  deletion_job_id uuid not null references deletion_jobs(deletion_job_id),
  device_id uuid not null,
  scope text not null check (scope in ('local-store','everything')),
  command_digest bytea not null check (octet_length(command_digest) = 32),
  state text not null check (state in ('issued','acknowledged','executing','complete','expired','failed')),
  disposition text not null check (disposition in ('pending','complete','failed','expired','unreachable','waived')),
  issued_at timestamptz not null,
  acknowledged_at timestamptz,
  waived_at timestamptz,
  expires_at timestamptz not null,
  unique (deletion_job_id, device_id),
  check (expires_at > issued_at),
  check (state <> 'issued' or acknowledged_at is null),
  check (state not in ('acknowledged','executing','complete','failed') or acknowledged_at is not null),
  check (
    disposition = case
      when state = 'complete' then 'complete'
      when state = 'failed' then 'failed'
      when waived_at is not null then 'waived'
      when state = 'expired' and acknowledged_at is null then 'unreachable'
      when state = 'expired' then 'expired'
      else 'pending'
    end
  )
);

-- What the device signed. The receipt attests that the daemon holding that device
-- key ran the delete operations the command named, over the paths that daemon
-- controls, at the time stated.
--
-- It attests nothing else, and the columns are chosen so that it cannot be read as
-- attesting more. There is no column for unrecoverability, sanitization, media
-- wiping or verification of free space, because a user-space process cannot
-- observe any of them: an operating-system backup, a filesystem snapshot, a
-- cloud-synced home directory, a copy the participant made, and the physical
-- residue that block remapping leaves on flash storage are all outside the
-- receipt and outside the product. D-424 records that ceiling.
--
-- `outcome`, `tables_cleared`, `keystore_entries_destroyed` and `residual_risk`
-- are the four columns `packages/schemas/local-store-v1.sql` already declares on
-- the device's own receipt row, with the same spellings. The server record is the
-- transported form of the device record and not a second vocabulary for the same
-- fact; inventing one here is the duplication SR-009 exists to remove.
--
-- `partial` is a first-class outcome rather than a rounded success or a rounded
-- failure: the claim outbox emptied and one locked adapter store refused is a real
-- result, and a single boolean would have to lie in one direction about it.
--
-- `residual_risk` is the honest ceiling stated in the row rather than in a
-- footnote. `none-observed` is the strongest value available and it says observed,
-- not none.
create table local_deletion_receipts (
  command_id uuid primary key references local_deletion_commands(command_id),
  device_id uuid not null,
  receipt_digest bytea not null check (octet_length(receipt_digest) = 32),
  outcome text not null check (outcome in ('complete','partial','refused','expired')),
  tables_cleared integer not null check (tables_cleared >= 0),
  keystore_entries_destroyed integer not null check (keystore_entries_destroyed >= 0),
  residual_risk text not null check (residual_risk in ('filesystem-snapshot-possible','backup-copy-possible','none-observed')),
  cose_sign1 bytea not null,
  signing_device_key_id text not null,
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

-- The source event: what a changed aggregate appends when something happened that
-- a recipient may need to know. It is not the inbox item. One event may be
-- discarded as a duplicate, collapsed into a group, or suppressed by preference,
-- and only an event that survives all three produces a `notifications` row.
--
-- Deduplication is a database constraint and not worker logic. `source_aggregate`
-- and `source_revision` are the same pair `outbox_events` uses, so the unique
-- index below makes an at-least-once outbox exactly-once for the recipient: a
-- redelivered outbox record cannot produce a second event, and no worker has to
-- get that right.
--
-- Grouping is separate and is a digest rather than a decision. `grouping_digest`
-- is SHA-256 over the deterministic CBOR encoding of the recipient, the event
-- type, the scope and the group window under D-191, so two workers presented with
-- the same facts compute the same group without coordinating.
create table notification_events (
  notification_event_id uuid primary key,
  event_type text not null check (event_type in ('friend_request','board_invitation','rank_overtake','moderation','appeal','security','compatibility','release')),
  recipient_account_id uuid not null references accounts(account_id),
  source_aggregate_id uuid not null,
  source_revision bigint not null check (source_revision >= 0),
  actor_account_id uuid references accounts(account_id),
  scope_id uuid,
  grouping_digest bytea not null check (octet_length(grouping_digest) = 32),
  authorization_revision bigint not null check (authorization_revision >= 0),
  suppression_cause text check (suppression_cause in ('category-disabled','overtake-below-material-lead','overtake-within-hysteresis-window','recipient-blocked-actor','viewer-authorization-withdrawn')),
  state text not null check (state in ('created','grouped','suppressed','ready','delivered','read','retracted','expired')),
  revision integer not null default 1 check (revision > 0),
  occurred_at timestamptz not null,
  created_at timestamptz not null,
  -- Exact deduplication. One recipient learns about one revision of one aggregate
  -- once, whatever the outbox does.
  unique (recipient_account_id, event_type, source_aggregate_id, source_revision),
  -- A suppressed event says why it was suppressed, and no other state may claim a
  -- cause. Without this the suppression register would be a set of events that
  -- silently produced nothing, which is indistinguishable from a lost event.
  check ((suppression_cause is not null) = (state = 'suppressed')),
  -- A security event has no suppression path at all: `security_enabled` is
  -- constrained true on the preferences row, so `category-disabled` cannot apply
  -- to it, and the other four causes are social and ranking causes.
  check (state <> 'suppressed' or event_type <> 'security')
);

create table privileged_supervisor_instances (
  privileged_supervisor_instance_id uuid primary key,
  state text not null check (state in ('absent','consent-pending','installing','active','degraded','removing','removed')),
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

-- One row per transport attempt. This table exists at launch and holds only
-- `server-inbox` rows, because D-086 ships no push and no email. It is specified
-- now so that shipping one later adds rows rather than columns.
--
-- Three constraints carry the binding rule that the server inbox is notification
-- authority and every other transport is a best-effort hint.
--
-- First, an inbox attempt is written in the same transaction as the
-- `notifications` row and therefore has exactly one outcome, `accepted`. It
-- cannot queue, defer, fail or expire, because there is nothing between the write
-- and the authority — they are the same write.
--
-- Second, a non-inbox attempt requires the opt-in timestamp that authorized it,
-- copied from the preferences row at send time. So the row records which consent
-- permitted the send rather than asserting that consent existed; and at launch,
-- with no opt-in reachable, a push or email row cannot be written at all.
--
-- Third, there is no read column and there never may be. `accepted` means a
-- provider took the message; `acknowledged` means a device confirmed receipt.
-- Neither is a read, a read lives only on `notifications.read_at`, and D-423
-- records that a transport that could mark an item read would make the inbox stop
-- being the authority.
create table notification_deliveries (
  notification_delivery_id uuid primary key,
  notification_id uuid not null,
  transport text not null check (transport in ('server-inbox','push','email')),
  attempt integer not null check (attempt >= 1),
  state text not null check (state in ('queued','deferred','accepted','acknowledged','failed','expired')),
  failure_reason_code text,
  preference_opt_in_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  unique (notification_id, transport, attempt),
  check (transport <> 'server-inbox' or state = 'accepted'),
  check (transport <> 'server-inbox' or attempt = 1),
  check (transport = 'server-inbox' or preference_opt_in_at is not null),
  check ((failure_reason_code is not null) = (state = 'failed'))
);

create table oauth_authorization_events (
  oauth_authorization_event_id uuid primary key,
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

-- The trusted client state one device holds for one TUF role, which is the
-- record SR-014 says the repository lacked. TUF is a client-side protocol: the
-- security property is that a client refuses metadata that is older, expired or
-- signed below threshold, so what has to be persisted is the client's own view
-- and not the server's.
--
-- `version` is monotonic per role per device and the check that enforces it
-- lives in the update path rather than here, because PostgreSQL cannot express
-- "never decreases" on a row that is updated in place. What this table does
-- carry is the rollback-attack evidence: `previous_version` and
-- `previous_metadata_digest` are retained, so a client presented with metadata
-- at or below the version it already trusts can record the refusal rather than
-- silently discard it.
--
-- Expiry is per role and deliberately short for `timestamp` and `snapshot`,
-- which is the freeze-attack control: a client that has not seen fresh
-- timestamp metadata inside its window stops trusting the repository rather
-- than continuing on stale data.
create table tuf_metadata (
  tuf_metadata_id uuid primary key,
  device_id uuid not null references devices(device_id),
  role text not null check (role in ('root','timestamp','snapshot','targets','delegated-targets')),
  version bigint not null check (version > 0),
  metadata_digest bytea not null check (octet_length(metadata_digest) = 32),
  previous_version bigint check (previous_version > 0),
  previous_metadata_digest bytea check (octet_length(previous_metadata_digest) = 32),
  signature_count smallint not null check (signature_count >= 0),
  threshold smallint not null check (threshold >= 1),
  root_version bigint not null references tuf_roots(root_version),
  expires_at timestamptz not null,
  verified_at timestamptz not null,
  last_refusal_reason_code text,
  last_refused_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  -- One trusted state per role per device. Two would mean the client trusted
  -- two versions of one role at once, which is the ambiguity the protocol
  -- exists to remove.
  unique (device_id, role),
  check (version > coalesce(previous_version, 0)),
  check ((previous_version is null) = (previous_metadata_digest is null)),
  check (previous_metadata_digest is null or metadata_digest <> previous_metadata_digest),
  -- Trusted metadata was signed at or above threshold. A row that records
  -- fewer signatures than its threshold is a client that accepted metadata it
  -- should have refused.
  check (signature_count >= threshold),
  check ((last_refusal_reason_code is null) = (last_refused_at is null))
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


-- Private-beta admission. D-180, and D-280 through D-288.
--
-- The invite code is the whole admission boundary of the private beta. There is
-- no public signup, so an account that holds no row in `invite_redemptions` is
-- an account the owner did not admit.
--
-- Two properties are carried by constraints rather than by worker discipline,
-- because both are races an application-level check loses. `invite_redemptions`
-- is keyed on `invite_code_id`, so a code binds at most one account and two
-- concurrent redemptions of one code cannot both insert. `account_id` is unique
-- in the same table, so an account holds at most one redemption and cannot
-- accumulate invites. Neither outcome is representable, so neither depends on a
-- transaction the application remembered to make serializable.
--
-- The code itself is never stored. `code_hash` is SHA-256 over the domain
-- separator, a zero byte and the 25-character canonical code, which carries 125
-- bits of entropy from a cryptographically secure source. A plain digest rather
-- than a memory-hard derivation is deliberate: at 125 bits a preimage search is
-- infeasible, and a slow derivation would turn the redemption lookup into a
-- sequential scan of every live code. `docs/security/PRIVATE_BETA_ADMISSION.md`
-- is the normative owner of the format, the gate order and the guessing controls.

create table invite_codes (
  invite_code_id uuid primary key,
  -- SHA-256 over 'vibemaxxing-invite-v1' || 0x00 || canonical_code. The code is
  -- displayed once at issuance and is never recoverable from this table.
  code_hash bytea not null unique check (octet_length(code_hash) = 32),
  state text not null check (state in ('issued','redeemed','expired','revoked','retired')),
  issued_by_account_id uuid not null references accounts(account_id),
  issued_at timestamptz not null,
  expires_at timestamptz not null,
  redeemed_at timestamptz,
  revoked_at timestamptz,
  retired_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  check (expires_at > issued_at),
  -- The timestamp set is the state, so a row cannot claim one lifecycle and
  -- record another. A retired code was redeemed first, which is what keeps a
  -- code the owner already spent from returning to the pool when the account
  -- that spent it is erased.
  check ((state = 'redeemed') = (redeemed_at is not null and retired_at is null)),
  check ((state = 'revoked') = (revoked_at is not null)),
  check ((state = 'retired') = (retired_at is not null)),
  check (retired_at is null or redeemed_at is not null)
);

-- One row per redeemed code. The row is the issuer-to-invitee edge, so it is
-- deleted outright on account deletion or Article 17 erasure rather than
-- retained pseudonymously; the code moves to `retired` in the same transaction
-- so the deletion cannot recycle an invite.
create table invite_redemptions (
  invite_code_id uuid primary key references invite_codes(invite_code_id),
  account_id uuid not null unique references accounts(account_id),
  redeemed_at timestamptz not null
);


-- ---------------------------------------------------------------------------
-- Identity lifecycle: ranked identity, investigation, recovery, consolidation
-- and lineage fork resolution. D-054, D-070, D-072, D-081, D-085, D-100.
--
-- These five aggregates were the densest remaining gap in
-- `docs/planning/SCHEMA_AND_INTERFACE_INVENTORY.md`: each was named by a
-- normative document and by a decision, and none had a persistence owner, a
-- revision model or a transaction boundary. They are placed here rather than in
-- the earlier persistence-owner block because four of them hold a foreign key
-- to `erasure_domains`, which is created below that block, and PostgreSQL
-- resolves a foreign key at statement time rather than at the end of the file.
--
-- Three rules bind every table in this section.
--
-- Nothing here resurrects an identifier. D-085 erases by destroying the key
-- that binds an erasure-domain pseudonym to a person. A recovery, a
-- consolidation and a fork resolution all operate on live rows that an erasure
-- deletes, so none of them can reintroduce a destroyed binding: the rows they
-- would need are gone, and the pseudonym they would need to re-bind has no
-- decryptable preimage.
--
-- Nothing here implies provider verification. Under D-100 no provider offers an
-- individual-account usage attestation path, so no column in this section
-- records a provider confirming a person, an account or a figure. The strongest
-- thing any of them records is which locally-held factor the participant
-- presented.
--
-- Nothing here sums a stored total. D-070 requires consolidation to carry
-- claim-level contributions, so `consolidation_contributions` holds one row per
-- absorbed claim with its original period attribution and no summed figure
-- exists anywhere in the path.
-- ---------------------------------------------------------------------------

-- The ranked identity is the competitive subject. D-054 permits one active
-- resolved ranked identity per person; what the engine can enforce is the
-- weaker half of that, one non-retired ranked identity per account, which the
-- partial unique index below carries. The stronger half — that two accounts do
-- not belong to one person — is not a constraint and is not claimed to be. It
-- is reached through `identity_investigations` and `consolidation_cases`, both
-- of which are appealable and neither of which asserts a verified human.
--
-- `erasure_domain_id` is the pseudonym a sealed ranking entry is keyed on, so
-- an erased ranked identity leaves its entries in place and unattributable
-- under D-085 and D-210. It is null only before the first sealed generation
-- names the identity.
--
-- No confidence weight is stored here. ADR-020 applies the weight at projection
-- and freezes it into `ranking_entries`; a weight column on the identity would
-- be a second authority for one number.
create table ranked_identities (
  ranked_identity_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  erasure_domain_id uuid references erasure_domains(erasure_domain_id),
  state text not null check (state in ('unverified','eligible','investigating','restricted','consolidating','appealed','reversed','retired')),
  -- Which route resolved this identity. `self-asserted` is the launch default
  -- and carries no verification claim at all.
  resolution_basis text not null check (resolution_basis in ('self-asserted','investigation-resolved','consolidation-survivor')),
  -- The surviving identity this one was absorbed into, set only by an applied
  -- consolidation. Self-reference is refused.
  absorbed_into_ranked_identity_id uuid references ranked_identities(ranked_identity_id),
  resolved_at timestamptz,
  retired_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  check ((state = 'retired') = (retired_at is not null)),
  check (resolution_basis = 'self-asserted' or resolved_at is not null),
  check (resolved_at is null or resolved_at >= created_at),
  check (absorbed_into_ranked_identity_id is null or absorbed_into_ranked_identity_id <> ranked_identity_id),
  -- An absorbed identity is retired in the same transaction that absorbs it,
  -- so a live identity can never point at a survivor.
  check (absorbed_into_ranked_identity_id is null or retired_at is not null)
);

-- One non-retired ranked identity per account. The retired row survives so a
-- consolidation survivor can name what it absorbed.
create unique index ranked_identities_account_live_idx
  on ranked_identities (account_id)
  where retired_at is null;

-- An integrity investigation into whether a ranked identity is a duplicate, a
-- fork, or otherwise ineligible. Its states are `integrity-private` under the
-- binding table: telling a participant an investigation is open is itself an
-- anti-cheat signal, so the ranked identity shows `restricted` and nothing
-- finer. Concluding an investigation never reverses anything by itself; a
-- reversal is an `appeals` outcome that moves `ranked_identities.state`, which
-- is why this table has no `reversed` state of its own.
create table identity_investigations (
  identity_investigation_id uuid primary key,
  ranked_identity_id uuid not null references ranked_identities(ranked_identity_id),
  state text not null check (state in (
    'opened','gathering','awaiting-participant','concluded-no-action',
    'concluded-restricted','concluded-consolidation','withdrawn','expired')),
  -- What triggered it. `statistical-signal` is deliberately absent: D-053 keeps
  -- statistical detection local, advisory and post-launch, so it cannot open a
  -- server-side case.
  trigger text not null check (trigger in ('deterministic-control','operator-review','participant-report','fork-detection')),
  opened_at timestamptz not null,
  response_due_at timestamptz,
  concluded_at timestamptz,
  expires_at timestamptz not null,
  revision integer not null default 1 check (revision > 0),
  check (expires_at > opened_at),
  check ((state in ('concluded-no-action','concluded-restricted','concluded-consolidation','withdrawn')) = (concluded_at is not null)),
  check (state <> 'awaiting-participant' or response_due_at is not null),
  check (concluded_at is null or concluded_at >= opened_at)
);

-- At most one open investigation per ranked identity. Two open cases would let
-- two operators reach two conclusions about one subject.
create unique index identity_investigations_open_idx
  on identity_investigations (ranked_identity_id)
  where state in ('opened','gathering','awaiting-participant');

-- Account recovery. The whole aggregate exists because D-055 makes provider
-- OAuth the only routine access path and a lost provider account would
-- otherwise be an unrecoverable loss of a competitive history.
--
-- What a recovery proves is control of a locally-held factor: a recovery code
-- from `recovery_codes`, an authenticator from `optional_authenticators`, or a
-- device signature from an enrolled row in `devices`. Under D-100 none of these
-- is a provider confirming anything, so `verified_factor_class` names the
-- factor and never a provider.
--
-- The cooling-off window is the control that makes a stolen factor survivable:
-- the case is announced to every existing session and inbox at the moment it is
-- opened, and the participant who still holds access can cancel it. Applying
-- before the window closes is unrepresentable rather than discouraged.
--
-- Applying a recovery revokes every session family and quarantines every
-- enrolled device, because the case admits that the previous access path is
-- compromised. Both effects are recorded as booleans on the row and the last
-- check makes an applied case that did neither impossible to write.
create table recovery_cases (
  recovery_case_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  state text not null check (state in ('requested','verifying','cooling-off','applied','denied','cancelled','expired')),
  verified_factor_class text not null check (verified_factor_class in (
    'none','recovery-code','optional-authenticator','enrolled-device','recovery-code-and-device')),
  requested_at timestamptz not null,
  cooling_off_ends_at timestamptz,
  applied_at timestamptz,
  denied_at timestamptz,
  cancelled_at timestamptz,
  expires_at timestamptz not null,
  sessions_revoked boolean not null default false,
  devices_quarantined boolean not null default false,
  revision integer not null default 1 check (revision > 0),
  check (expires_at > requested_at),
  check ((state = 'applied') = (applied_at is not null)),
  check ((state = 'denied') = (denied_at is not null)),
  check ((state = 'cancelled') = (cancelled_at is not null)),
  check (state not in ('cooling-off','applied') or cooling_off_ends_at is not null),
  check (state not in ('cooling-off','applied') or verified_factor_class <> 'none'),
  -- The cooling-off window cannot be skipped.
  check (applied_at is null or applied_at >= cooling_off_ends_at),
  -- An applied recovery has performed both effects.
  check (applied_at is null or (sessions_revoked and devices_quarantined))
);

-- One live recovery case per account. Two concurrent cases would let an
-- attacker open a second case to outlast the notice on the first.
create unique index recovery_cases_live_idx
  on recovery_cases (account_id)
  where state in ('requested','verifying','cooling-off');

-- D-070 duplicate-account consolidation. The surviving and absorbed identities
-- are named on the case, the plan is the set of rows in
-- `consolidation_contributions`, and the result is the case reaching `applied`.
--
-- The transaction boundary is the whole case: absorbing identity retirement,
-- every contribution row, the `erasure_domain_links` edge and the
-- `identity_events` rows commit together or not at all, because a partial
-- consolidation leaves two live identities that each believe they own the same
-- history.
--
-- Reversal is an explicit transition rather than a delete. `reversed` retracts
-- the contributions by appending inverse rows in `score_contributions`; the
-- absorbed identity is not un-retired, because its account may have been
-- deleted in the interval and a resurrection would be exactly the identifier
-- revival D-085 forbids.
create table consolidation_cases (
  consolidation_case_id uuid primary key,
  surviving_ranked_identity_id uuid not null references ranked_identities(ranked_identity_id),
  absorbed_ranked_identity_id uuid not null references ranked_identities(ranked_identity_id),
  state text not null check (state in (
    'requested','planning','awaiting-confirmation','applying','applied','rejected','reversed','expired')),
  -- Who asked. A participant-initiated consolidation and an
  -- investigation-initiated one differ in what the participant is told, not in
  -- what the arithmetic does.
  initiated_by text not null check (initiated_by in ('participant','investigation')),
  identity_investigation_id uuid references identity_investigations(identity_investigation_id),
  requested_at timestamptz not null,
  confirmed_at timestamptz,
  applied_at timestamptz,
  reversed_at timestamptz,
  expires_at timestamptz not null,
  revision integer not null default 1 check (revision > 0),
  check (expires_at > requested_at),
  check (surviving_ranked_identity_id <> absorbed_ranked_identity_id),
  check ((initiated_by = 'investigation') = (identity_investigation_id is not null)),
  check ((state = 'applied') = (applied_at is not null and reversed_at is null)),
  check ((state = 'reversed') = (reversed_at is not null)),
  check (applied_at is null or confirmed_at is not null),
  check (reversed_at is null or applied_at is not null)
);

-- An identity is absorbed at most once, and a live identity is never the
-- absorbed side of two cases at the same time.
create unique index consolidation_cases_absorbed_idx
  on consolidation_cases (absorbed_ranked_identity_id)
  where state in ('requested','planning','awaiting-confirmation','applying','applied');

-- One row per absorbed claim. This is the executable form of the D-070 rule
-- that stored account totals are never added together: the case carries claim
-- identities and original period attribution, and the surviving standing is
-- recomputed from them rather than incremented by a figure.
--
-- `claim_id` is nullable and clears on delete for the same reason it does in
-- `score_contributions`: an erasure deletes the claim and the arithmetic that
-- produced a sealed standing stays auditable without it.
--
-- `duplicate_domain_commitment` is the observer-equivalence key from
-- `packages/schemas/observer-equivalence-v1.json`. A contribution whose
-- commitment already appears under the surviving identity is excluded rather
-- than counted twice, which is the overlapping-contribution rule of D-070
-- expressed as a unique constraint.
create table consolidation_contributions (
  consolidation_contribution_id uuid primary key,
  consolidation_case_id uuid not null references consolidation_cases(consolidation_case_id),
  claim_id uuid references claims(claim_id) on delete set null,
  period_id uuid not null references periods(period_id),
  duplicate_domain_commitment bytea not null check (octet_length(duplicate_domain_commitment) = 32),
  token_burn_total bigint not null check (token_burn_total >= 0),
  disposition text not null check (disposition in ('absorbed','excluded-duplicate','excluded-imported','excluded-quarantined')),
  created_at timestamptz not null,
  -- One commitment counts once inside a case. Imported records are excluded by
  -- disposition rather than by omission, so the case explains what it dropped.
  unique (consolidation_case_id, duplicate_domain_commitment)
);

-- D-072 lineage fork and clone resolution. A fork is detected when two device
-- installations present continuations of one lineage generation; the case
-- quarantines every post-fork branch, preserves accepted pre-fork claims, and
-- resumes through a new lineage generation rather than merging two commitment
-- chains.
--
-- `fork_generation` is the lineage generation at which the branches diverged,
-- and `resumed_generation` is the new one the survivor continues on. They are
-- separate columns because a resumed lineage is not the forked one repaired:
-- it is a successor, and the constraint that it be strictly greater is what
-- keeps a resolution from replaying the fork.
create table lineage_fork_cases (
  lineage_fork_case_id uuid primary key,
  lineage_id uuid not null references device_lineages(lineage_id),
  ranked_identity_id uuid not null references ranked_identities(ranked_identity_id),
  state text not null check (state in (
    'detected','quarantined','survivor-selected','requalifying','resumed','unresolved','appealed','reversed')),
  fork_generation bigint not null check (fork_generation >= 0),
  resumed_generation bigint,
  survivor_device_id uuid references devices(device_id),
  appeal_id uuid references appeals(appeal_id),
  detected_at timestamptz not null,
  quarantined_at timestamptz,
  resumed_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  check (state not in ('quarantined','survivor-selected','requalifying','resumed') or quarantined_at is not null),
  check ((state = 'resumed') = (resumed_at is not null)),
  check (resumed_generation is null or resumed_generation > fork_generation),
  check ((state = 'resumed') = (resumed_generation is not null)),
  check (state not in ('survivor-selected','requalifying','resumed') or survivor_device_id is not null),
  check ((state in ('appealed','reversed')) = (appeal_id is not null))
);

-- One open fork case per lineage generation. Two cases over one fork would let
-- two survivors be selected.
create unique index lineage_fork_cases_open_idx
  on lineage_fork_cases (lineage_id, fork_generation)
  where state in ('detected','quarantined','survivor-selected','requalifying');

-- Every branch a fork produced, including the one that becomes the survivor.
-- Claims accepted before `fork_generation` are untouched; claims on a
-- quarantined branch are held by `quarantines` and are not deleted, because
-- D-072 makes the resolution appealable and an appeal needs the evidence.
create table lineage_fork_branches (
  lineage_fork_branch_id uuid primary key,
  lineage_fork_case_id uuid not null references lineage_fork_cases(lineage_fork_case_id),
  device_id uuid not null references devices(device_id),
  branch_head_sequence bigint not null check (branch_head_sequence >= 0),
  disposition text not null check (disposition in ('survivor','quarantined','requalified','abandoned')),
  post_fork_claim_count bigint not null check (post_fork_claim_count >= 0),
  created_at timestamptz not null,
  unique (lineage_fork_case_id, device_id)
);

-- Exactly one survivor per case, and only while the case has selected one.
create unique index lineage_fork_branches_survivor_idx
  on lineage_fork_branches (lineage_fork_case_id)
  where disposition = 'survivor';

-- The append-only history of every identity-affecting act. It is the record an
-- appeal reads, so it is written inside the same transaction as the act it
-- describes rather than by a follower reading a queue. It is last in this
-- section because it holds a foreign key to each of the four case tables above.
--
-- At most one case reference is set, so an event names one cause rather than a
-- correlation. `reason_code` is drawn from `packages/schemas/reason-codes-v1.json`
-- and this column never carries free text, a path, a project name or any other
-- content-derived value.
create table identity_events (
  identity_event_id uuid primary key,
  ranked_identity_id uuid not null references ranked_identities(ranked_identity_id),
  event_type text not null check (event_type in (
    'identity-created','identity-resolved','investigation-opened','investigation-concluded',
    'recovery-applied','consolidation-applied','consolidation-reversed',
    'fork-quarantined','fork-resumed','restriction-applied','restriction-reversed','identity-retired')),
  identity_investigation_id uuid references identity_investigations(identity_investigation_id),
  recovery_case_id uuid references recovery_cases(recovery_case_id),
  consolidation_case_id uuid references consolidation_cases(consolidation_case_id),
  lineage_fork_case_id uuid references lineage_fork_cases(lineage_fork_case_id),
  reason_code text,
  occurred_at timestamptz not null,
  check (
    (case when identity_investigation_id is null then 0 else 1 end)
    + (case when recovery_case_id is null then 0 else 1 end)
    + (case when consolidation_case_id is null then 0 else 1 end)
    + (case when lineage_fork_case_id is null then 0 else 1 end) <= 1
  )
);


-- ---------------------------------------------------------------------------
-- Source certification: the exact tuple, its lifecycle and its signed results.
-- D-022, D-030, D-058, D-089, D-098, D-100, D-264.
-- ---------------------------------------------------------------------------

-- One row per exact compatibility tuple that has ever been submitted for
-- certification. The tuple is the unit the whole product advertises against,
-- and the reason the binding rules keep saying "exact": a certification of
-- Claude Code on macOS through OpenTelemetry says nothing about the same
-- product on Windows through a session log.
--
-- `tuple_digest` is SHA-256 over the RFC 8949 core deterministic CBOR encoding
-- of the tuple record in `packages/schemas/compatibility-tuple-v1.schema.json`,
-- computed the same way D-261 computes every other planning policy digest. It
-- is unique, so two rows cannot describe one tuple, and it is what a claim
-- binds to rather than a mutable product name — D-058 makes trust
-- digest-addressed precisely because a name and a version alone establish
-- nothing.
--
-- `effective_ceiling` is the honest half. A tuple below `active` cannot exceed
-- `private-analytics`, whatever its adapter claims, which is the same
-- constraint `packages/schemas/producer-accounting-binding-v1.schema.json`
-- already carries at the binding level. The last check makes the pairing
-- unrepresentable rather than a rule somebody has to apply.
create table source_certifications (
  source_certification_id uuid primary key,
  tuple_digest bytea not null unique check (octet_length(tuple_digest) = 32),
  state text not null check (state in (
    'candidate','testing','active','degraded','suspended','expired','superseded','retired')),
  adapter_id text not null,
  source_product_id text not null,
  -- Exactly the nine modes `packages/schemas/observer-equivalence-v1.json`
  -- declares. A second spelling of one vocabulary is the duplication SR-009
  -- exists to remove.
  observation_mode text not null check (observation_mode in (
    'native-event','official-hook','extension-api','local-runtime','acp','otel','proxy','wrapper','live-log')),
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  accounting_profile_id text not null,
  evidence_profile_id text not null,
  effective_ceiling text not null check (effective_ceiling in ('hardened','standard','private-analytics')),
  -- The tuple this one replaced. A superseded tuple keeps its own row, because
  -- a claim accepted under it stays explainable after the successor lands.
  superseded_by_source_certification_id uuid references source_certifications(source_certification_id),
  valid_from timestamptz,
  valid_until timestamptz,
  revoked_at timestamptz,
  revocation_reason_code text,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  check (valid_until is null or valid_from is not null),
  check (valid_until is null or valid_until > valid_from),
  check ((state = 'active') = (valid_from is not null and revoked_at is null and superseded_by_source_certification_id is null)),
  check ((state = 'superseded') = (superseded_by_source_certification_id is not null)),
  check ((revoked_at is null) = (revocation_reason_code is null)),
  check (superseded_by_source_certification_id is null or superseded_by_source_certification_id <> source_certification_id),
  -- Only an active tuple may exceed private analytics. A registry that
  -- advertised a planned, expired or suspended certification would be exactly
  -- the overclaim the binding rules forbid.
  check (state = 'active' or effective_ceiling = 'private-analytics')
);

-- At most one active certification per tuple shape. Two would make "the exact
-- certified tuple" ambiguous at the moment a claim is appraised.
create unique index source_certifications_active_idx
  on source_certifications (adapter_id, source_product_id, observation_mode, platform_profile_id)
  where state = 'active';

-- The signed record of one conformance run against one tuple. It is append-only
-- and immutable: a later run is a new row, never an edit, because the appraisal
-- of a claim accepted last month has to stay reproducible.
--
-- `suite_manifest_digest` binds the suite that ran, under the D-242 manifest
-- contract, so a result cannot claim a pass against a suite whose cases changed
-- afterwards. `negative_case_count` is separate from `case_count` and must be
-- non-zero for a passing result: a suite with no negative case has not
-- demonstrated that it can fail.
create table certification_results (
  certification_result_id uuid primary key,
  source_certification_id uuid not null references source_certifications(source_certification_id),
  suite_id text not null,
  suite_manifest_digest bytea not null check (octet_length(suite_manifest_digest) = 32),
  outcome text not null check (outcome in ('passed','failed','inconclusive')),
  case_count integer not null check (case_count > 0),
  negative_case_count integer not null check (negative_case_count >= 0),
  failed_case_count integer not null check (failed_case_count >= 0),
  result_digest bytea not null unique check (octet_length(result_digest) = 32),
  cose_sign1 bytea not null,
  signing_key_id text not null,
  executed_at timestamptz not null,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  check (failed_case_count <= case_count),
  check (negative_case_count <= case_count),
  check ((outcome = 'passed') = (failed_case_count = 0)),
  -- A pass with no negative case is an untested suite reporting success.
  check (outcome <> 'passed' or negative_case_count > 0)
);

-- The typed platform operations one release performs on one platform profile.
-- D-014 and ADR-010 through ADR-013 require exact OS mechanisms rather than a
-- generic lifecycle verb, so an install plan is a sequence of named operations
-- and never a script. `sequence` is dense from 1 within a plan, and
-- `reversal_operation` is what a rollback runs, which is why an operation with
-- no reversal has to declare itself irreversible rather than leave the column
-- empty and let a rollback discover it.
create table platform_install_plans (
  platform_install_plan_id uuid primary key,
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  release_set_id uuid not null references release_sets(release_set_id),
  requires_privileged_consent boolean not null default false,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  unique (platform_profile_id, release_set_id)
);

create table platform_install_operations (
  platform_install_plan_id uuid not null references platform_install_plans(platform_install_plan_id),
  sequence integer not null check (sequence >= 1),
  operation text not null check (operation in (
    'verify-release-signature','place-binary','register-service','set-autostart',
    'grant-keystore-access','create-ipc-endpoint','register-privileged-supervisor',
    'start-service','verify-health','remove-previous-version')),
  irreversible boolean not null default false,
  reversal_operation text check (reversal_operation in (
    'unregister-service','clear-autostart','revoke-keystore-access','remove-ipc-endpoint',
    'remove-privileged-supervisor','stop-service','restore-previous-version','remove-binary')),
  primary key (platform_install_plan_id, sequence),
  -- An operation names the reversal a rollback runs, or declares that it has
  -- none — because it changes nothing, as a verification does, or because its
  -- effect cannot be undone. A rollback that discovers the answer at run time
  -- is D-074's failure mode rather than its contract.
  check (irreversible = (reversal_operation is null))
);

-- ---------------------------------------------------------------------------
-- Compatibility graph, migrations and rollback classes. D-024, D-068, D-074,
-- D-097, D-234, SR-014.
-- ---------------------------------------------------------------------------

-- One row per compatibility relation the product actually has to hold. Six
-- interfaces move independently and each has its own range, which is the whole
-- reason a single "version" number was never going to work: a client can be
-- current on the HTTP API and behind on the local IPC contract at the same
-- time, and the answer to "may this build run" differs per interface.
--
-- The range is closed on the left and open on the right, which removes the
-- off-by-one that an inclusive upper bound invites, and `minimum_supported`
-- being strictly less than `maximum_exclusive` makes an empty range
-- unrepresentable.
--
-- `breaking` is not derived from the numbers. D-234 permits only additive
-- change inside a major version and makes adding a member to a closed state
-- vocabulary a major change, which no version arithmetic can detect; so the
-- edge records the judgement and the check makes a breaking edge that did not
-- move the major version impossible to write.
create table compatibility_edges (
  compatibility_edge_id uuid primary key,
  interface text not null check (interface in (
    'vibeproof-protocol','http-api','local-ipc','local-storage','server-schema','platform-profile')),
  producer_component text not null,
  consumer_component text not null,
  minimum_supported bigint not null check (minimum_supported >= 1),
  maximum_exclusive bigint not null,
  breaking boolean not null default false,
  deprecated_after timestamptz,
  sunset_at timestamptz,
  release_set_id uuid references release_sets(release_set_id),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  check (maximum_exclusive > minimum_supported),
  check (producer_component <> consumer_component),
  -- A breaking edge starts a new major range, so its lower bound is its own
  -- upper bound minus one: it supports exactly one major version.
  check (not breaking or maximum_exclusive = minimum_supported + 1),
  -- D-234 sets a 180-day minimum deprecation window. A sunset with no
  -- deprecation notice is the removal that window exists to prevent.
  check ((sunset_at is null) or (deprecated_after is not null and sunset_at > deprecated_after)),
  unique (interface, producer_component, consumer_component, minimum_supported)
);

-- The migration chain, and the rollback class each step belongs to. D-074
-- permits automatic binary rollback only while the previous release stays
-- read/write compatible with every committed mutation, and this table is where
-- that condition becomes checkable rather than remembered.
--
-- `rollback_class` is the load-bearing column. `binary-reversible` means the
-- previous binary can read and write the post-migration shape, so a rollback is
-- a binary swap. `forward-only` means it cannot, so recovery is roll-forward or
-- restoration of a verified pre-migration snapshot. `snapshot-required` is
-- forward-only plus the additional statement that a snapshot must exist before
-- the migration runs, and the last check makes a `snapshot-required` row
-- without a recorded snapshot digest unrepresentable.
--
-- `down_sql_present` is separate from the rollback class on purpose. D-097
-- requires every `goose` migration to carry an explicit down section, and a
-- present down section does not make a migration reversible: dropping a column
-- back is syntactically fine and loses the data that was written into it. The
-- two columns say different things and conflating them is how a forward-only
-- migration acquires a rollback plan nobody tested.
create table storage_migrations (
  storage_migration_id uuid primary key,
  version text not null unique references schema_migrations(version),
  interface text not null check (interface in ('local-storage','server-schema')),
  rollback_class text not null check (rollback_class in ('binary-reversible','forward-only','snapshot-required')),
  down_sql_present boolean not null,
  pre_migration_snapshot_digest bytea check (octet_length(pre_migration_snapshot_digest) = 32),
  minimum_binary_version bigint not null check (minimum_binary_version >= 1),
  applied_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  check ((rollback_class = 'snapshot-required') = (pre_migration_snapshot_digest is not null)),
  -- A binary-reversible migration has a down section. The converse does not
  -- hold and is not asserted.
  check (rollback_class <> 'binary-reversible' or down_sql_present)
);

-- ---------------------------------------------------------------------------
-- Presence pulses and lease generations. D-073, D-095.
-- ---------------------------------------------------------------------------

-- Pulse admission for the current lease generation, and nothing older.
--
-- This is deliberately not a presence history. ADR-019 accepts a live-sampling
-- risk — an authorized viewer can infer working hours by watching — on the
-- stated basis that no stored history exists, and `presence_events` carries
-- `no-retention` in `packages/schemas/data-disposition-v1.json` for exactly
-- that reason: rows are discarded when the generation they belong to closes.
-- Keeping them would convert an accepted risk into a different and larger one
-- without anybody deciding to.
--
-- What the table does is make the lease derivable rather than asserted. The
-- unique constraint is the deduplication rule for a retried pulse delivery, and
-- the lease generation is what stops a pulse from a resumed process reviving an
-- expired lease.
--
-- A pulse carries no content of any kind. It names the device, the generation
-- and whether the device was doing qualifying work — never what the work was.
-- That is why `qualifying` is a boolean rather than a description.
create table presence_events (
  presence_event_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  -- Monotonic per (account, device). A restart mints a new generation rather
  -- than continuing the old one, so a stale pulse from a resumed process
  -- cannot revive an expired lease.
  lease_generation bigint not null check (lease_generation >= 0),
  event_type text not null check (event_type in ('pulse','lease-opened','lease-idled','lease-expired','lease-revoked')),
  qualifying boolean not null,
  occurred_at timestamptz not null,
  -- A pulse is idempotent per generation and per second. A duplicate delivery
  -- is a no-op rather than a second observation.
  unique (account_id, device_id, lease_generation, occurred_at)
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

-- Foreign-key referencing side: admission.
--
-- `invite_redemptions.account_id` and `invite_redemptions.invite_code_id` need
-- no index here: the first is unique and the second is the primary key, so both
-- already carry one, and those two constraints are also the atomicity control.
create index invite_codes_issuer_idx on invite_codes (issued_by_account_id);

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
create index invite_codes_expiry_idx on invite_codes (expires_at) where state = 'issued';
create index local_deletion_commands_expiry_idx on local_deletion_commands (expires_at);
-- Identity lifecycle: referencing side of every foreign key added with the
-- ranked identity, investigation, recovery, consolidation and fork tables.
create index ranked_identities_erasure_domain_idx on ranked_identities (erasure_domain_id);
create index ranked_identities_absorbed_into_idx on ranked_identities (absorbed_into_ranked_identity_id);
create index identity_investigations_identity_idx on identity_investigations (ranked_identity_id);
create index recovery_cases_account_idx on recovery_cases (account_id);
create index recovery_cases_expiry_idx on recovery_cases (expires_at) where state in ('requested','verifying','cooling-off');
create index identity_investigations_expiry_idx on identity_investigations (expires_at) where state = 'awaiting-participant';
create index consolidation_cases_surviving_idx on consolidation_cases (surviving_ranked_identity_id);
create index consolidation_cases_investigation_idx on consolidation_cases (identity_investigation_id);
create index consolidation_cases_expiry_idx on consolidation_cases (expires_at) where state = 'awaiting-confirmation';
create index consolidation_contributions_case_idx on consolidation_contributions (consolidation_case_id);
create index consolidation_contributions_claim_idx on consolidation_contributions (claim_id);
create index consolidation_contributions_period_idx on consolidation_contributions (period_id);
create index lineage_fork_cases_lineage_idx on lineage_fork_cases (lineage_id);
create index lineage_fork_cases_identity_idx on lineage_fork_cases (ranked_identity_id);
create index lineage_fork_cases_survivor_device_idx on lineage_fork_cases (survivor_device_id);
create index lineage_fork_cases_appeal_idx on lineage_fork_cases (appeal_id);
create index lineage_fork_branches_case_idx on lineage_fork_branches (lineage_fork_case_id);
create index lineage_fork_branches_device_idx on lineage_fork_branches (device_id);
create index identity_events_identity_idx on identity_events (ranked_identity_id, occurred_at desc);
create index identity_events_investigation_idx on identity_events (identity_investigation_id);
create index identity_events_recovery_idx on identity_events (recovery_case_id);
create index identity_events_consolidation_idx on identity_events (consolidation_case_id);
create index identity_events_fork_idx on identity_events (lineage_fork_case_id);
create index presence_events_account_device_idx on presence_events (account_id, device_id, occurred_at desc);
create index presence_events_device_idx on presence_events (device_id);

create index seasons_window_idx on seasons (starts_at, ends_at);
create index periods_type_window_idx on periods (period_type, starts_at desc);
create index score_snapshots_view_generation_idx on score_snapshots (ranking_view_id, generation desc);
