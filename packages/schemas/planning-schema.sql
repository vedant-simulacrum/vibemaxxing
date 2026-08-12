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

-- The linked provider identity. PF-007, SR-006.
--
-- One of the three aggregates AGENTS.md keeps separate: an account, a linked provider
-- identity and a ranked identity are not the same thing, and this is the middle one.
-- It held three states, no lifecycle in the registry, and a recorded absence saying
-- its transitions were owned by the enrollment flow and unspecified. The three states
-- could not express any of what `docs/security/AUTHENTICATION_AND_RECOVERY.md` requires
-- of a provider that is compromised, suspended, deleted or renamed, so the document's
-- whole provider-loss section described behaviour the schema could not hold.
--
-- `provider_subject` is the durable linkage key while the binding is live. Mutable
-- usernames are attributes and never identify anything, which is why no handle column
-- exists here.
--
-- `provider_account_created_at` is the D-081 gate input: a linked provider account must
-- be at least 90 days old, measured from the provider-reported creation timestamp, and
-- the gate is evaluated at link time. Nothing persisted that timestamp before, so the
-- gate had no stored input to be evaluated against.
--
-- Both fields are personal data, and `docs/privacy/DATA_MAP.md` retains them "until
-- unlink or account erasure" and deletes the subject "immediately on unlink". The
-- column was `not null`, which made that promise unimplementable without deleting the
-- whole row -- and the row could not be deleted, because a total
-- `unique (provider, provider_subject)` then let an `unlinked` row block its own
-- provider account from ever being linked again, to this account or to any other.
-- Unlinking was silently permanent, product-wide, and the privacy commitment and the
-- uniqueness constraint could not both be honoured. Both fields are now null exactly
-- when the binding has ended, which is the retention rule expressed as a constraint,
-- and the uniqueness is partial over the live states so the rule it encodes -- one live
-- binding per provider subject, never a silent reassignment -- is stated where a reader
-- sees it rather than resting on how the engine treats nulls.
--
-- No recovery-case reference is declared here. `recovery_cases` is created much later
-- in this file, PostgreSQL resolves a foreign key at statement time, and the two rows
-- already join on `account_id`; a nullable unenforced uuid would be a reference that
-- looks checked and is not.
create table linked_identities (
  identity_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  provider text not null check (provider in ('github','x')),
  -- The stable linkage key while the binding is live, and null once it has ended.
  -- Never a username.
  provider_subject text,
  -- D-081. Captured from the provider at link time; the 90-day gate reads it.
  provider_account_created_at timestamptz,
  state text not null check (state in (
    'candidate','linked','unlink-pending','lost','compromised','recovery-pending',
    'unlinked','superseded')),
  -- Set only when this row was replaced by a later binding of the same subject.
  superseded_by_identity_id uuid references linked_identities(identity_id),
  linked_at timestamptz,
  state_changed_at timestamptz not null,
  ended_at timestamptz,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  -- A candidate is a link in flight: it has no confirmed binding yet, so it carries
  -- neither a link instant nor the gate input the link is refused without.
  -- A candidate has not linked yet, and `identity-link-abandon` takes an unconfirmed
  -- candidate straight to `unlinked`, so an ended row may legitimately have no link
  -- instant. Stating this as one equivalence made an abandoned candidate
  -- unrepresentable, which would have forced the abandon transition to invent a
  -- linked_at it never had.
  check (state <> 'candidate' or linked_at is null),
  check (state in ('candidate','unlinked') or linked_at is not null),
  -- `docs/privacy/DATA_MAP.md` retains the provider subject and the D-081 creation
  -- timestamp "until unlink or account erasure" and deletes the subject "immediately on
  -- unlink". Both are constraints here rather than promises a worker has to remember.
  check ((provider_subject is not null) = (state not in ('unlinked','superseded'))),
  check ((provider_account_created_at is not null)
         = (state not in ('candidate','unlinked','superseded'))),
  check ((state in ('unlinked','superseded')) = (ended_at is not null)),
  check ((state = 'superseded') = (superseded_by_identity_id is not null)),
  check (superseded_by_identity_id is null or superseded_by_identity_id <> identity_id),
  check (linked_at is null or linked_at >= created_at),
  check (ended_at is null or ended_at >= created_at),
  check (state_changed_at >= created_at)
);

-- One live binding per provider subject. Ended rows are retained so a re-link after a
-- recovery can name what it replaced, and so an appeal can read the history.
create unique index linked_identities_live_subject_idx
  on linked_identities (provider, provider_subject)
  where state in ('candidate','linked','unlink-pending','lost','compromised','recovery-pending');

-- At most one live identity per account and provider. Without it an account can hold
-- two live GitHub rows and the last-authentication-method count is ambiguous.
create unique index linked_identities_live_provider_idx
  on linked_identities (account_id, provider)
  where state in ('candidate','linked','unlink-pending','lost','compromised','recovery-pending');

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

-- The OAuth transaction is the only route by which a callback may change identity.
-- PF-006, SR-006.
--
-- It previously held eight columns and bound almost nothing that
-- `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` says a transaction
-- binds: no provider revision, no issuer, no redirect, no PKCE method, no initiating
-- session, no recent-auth instant, no result. The consequence was not that the table
-- was thin. It was that `packages/schemas/openapi-v1.yaml#IdentityMutationRequest`
-- took a bare `authorization_code` and `/identities/link` mutated identity from it, so
-- there was a second identity-mutating path that referenced no transaction at all and
-- therefore verified no redirect, no state, no PKCE and no lifetime. Everything the
-- transaction exists to bind was optional in practice.
--
-- `provider_revision` records which row of `packages/schemas/oauth-provider-registry-v1.json`
-- this transaction agreed to, so a configuration change cannot retroactively alter what
-- an in-flight transaction was started under. `issuer`, `redirect_uri` and `pkce_method`
-- are copied at creation for the same reason: the callback is compared against what was
-- stored, never against what the registry says now, and never against anything the
-- callback itself carries.
--
-- Four constraints carry rules the documents state in prose and no code could enforce:
--
-- * a link transaction is startable only from an authenticated account under recent
--   authentication, which is the reauthentication requirement in
--   `docs/security/AUTHENTICATION_AND_RECOVERY.md`;
-- * a link transaction never produces a session, so the linking flow cannot be used to
--   mint browser access;
-- * a consumed transaction produced the thing its action names — a session for a
--   sign-in, a linked identity for a link — so `consumed` cannot mean "finished with
--   no effect";
-- * a transaction that started on one account cannot finish on another, which is the
--   silent-reassignment `docs/security/RANKED_IDENTITY_ELIGIBILITY.md` forbids.
create table oauth_transactions (
  oauth_transaction_id uuid primary key,
  provider text not null check (provider in ('github','x')),
  -- The registry revision this transaction agreed to, never re-read at callback time.
  provider_revision integer not null check (provider_revision > 0),
  -- Copied from the registry at creation. A callback-controlled value never selects
  -- any of these three.
  issuer text not null,
  redirect_uri text not null,
  pkce_method text not null check (pkce_method = 'S256'),
  state_hash bytea not null unique check (octet_length(state_hash) = 32),
  pkce_verifier_ciphertext bytea,
  intended_action text not null check (intended_action in ('sign-in','link-identity')),
  -- Who started it. Null for a sign-in from an unauthenticated browser.
  initiating_account_id uuid references accounts(account_id),
  initiating_web_session_id uuid references web_sessions(session_id),
  recent_auth_at timestamptz,
  -- What it produced.
  resulting_account_id uuid references accounts(account_id),
  resulting_session_id uuid references web_sessions(session_id),
  resulting_identity_id uuid references linked_identities(identity_id),
  failure_reason_code text,
  state text not null check (state in ('created','redirected','callback-received','consumed','expired','failed')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  expires_at timestamptz not null,
  consumed_at timestamptz,
  check (expires_at > created_at),
  check ((state = 'consumed') = (consumed_at is not null)),
  check ((state = 'failed') = (failure_reason_code is not null)),
  -- Linking requires an existing authenticated session and reauthentication.
  check (intended_action <> 'link-identity'
         or (initiating_account_id is not null
             and initiating_web_session_id is not null
             and recent_auth_at is not null)),
  -- Linking never mints browser access.
  check (intended_action <> 'link-identity' or resulting_session_id is null),
  -- A consumed transaction produced what its action names.
  check (state <> 'consumed' or resulting_account_id is not null),
  check (state <> 'consumed' or intended_action <> 'sign-in' or resulting_session_id is not null),
  check (state <> 'consumed' or intended_action <> 'link-identity' or resulting_identity_id is not null),
  -- A transaction cannot finish on an account other than the one it started on.
  check (initiating_account_id is null
         or resulting_account_id is null
         or resulting_account_id = initiating_account_id)
);

-- One live transaction per account, provider and action. Without it a client can hold
-- many redirected link transactions for one provider at once, and the callback that
-- returns has a set of stored states to match against rather than one.
create unique index oauth_transactions_live_link_idx
  on oauth_transactions (initiating_account_id, provider, intended_action)
  where state in ('created','redirected','callback-received')
    and initiating_account_id is not null;

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

-- A challenge is scoped to the lineage that must answer it. device_id records which
-- device row asked, which stays useful for audit, but consumption is checked against
-- the lineage so a re-enrolled device inside one lineage cannot replay a challenge
-- issued to its predecessor.
-- Moved above claim_challenges and device_sequences under PF-009: both now carry a
-- foreign key to it, and PostgreSQL rejects a reference to a table that does not yet
-- exist. Verified by applying this file to postgres:16, which failed with
-- 'relation "device_lineages" does not exist' before the move.
create table device_lineages (
  lineage_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  root_installation_id uuid not null,
  continuity_state text not null check (continuity_state in ('continuous','gap-declared','broken','revoked')),
  revision bigint not null check (revision >= 0)
);

-- Moved above `claim_challenges` under PF-070, for the reason PF-009 moved
-- `device_lineages`: `claim_challenges.expected_checkpoint_receipt_id` now names the
-- receipt a challenge expects the device to be standing on, and PostgreSQL rejects a
-- reference to a table that does not yet exist. The table itself is unchanged by that
-- move.
-- The server's acknowledged head, and the third table SR-007 named as disagreeing
-- with the lineage-scoped continuity rule. It was keyed on the device row while
-- `device_sequences.server_checkpoint_head` — the value a receipt is supposed to
-- advance — is keyed on the lineage, so the head and the receipts that produce it were
-- scoped differently. A restored or cloned store enrolling as a second device row
-- acquired its own private receipt chain, and no index in this file objected.
--
-- `unique (lineage_id, accepted_through_claim_sequence)` is the constraint, and it is
-- the `checkpoint-mismatch` detection basis expressed as a write refusal: two receipts
-- acknowledging the same head inside one lineage are two branches, and the second
-- insert fails rather than quietly creating a fork nobody counted.
--
-- Newest wins. When a lineage presents two acknowledged heads the receipt with the
-- greater `accepted_through_claim_sequence` is authoritative and the server never rolls
-- its head backwards; a device arriving with an older head is behind, not correct, and
-- must declare a gap or requalify. Ordering by `created_at` instead would let a clone
-- with a fast clock win, so the ordering is over the sequence the server itself issued.
-- `docs/security/INTEGRITY_MODEL.md` owns the rule; this table is where it is stored.
--
-- PF-073, and the sixth divergence D-043 records. This table and
-- `packages/schemas/vibeproof-claim-v1.cddl#checkpoint-receipt-v1` had near-disjoint
-- column sets: the receipt the server signs binds a pseudonym, an accepted local head,
-- a last accepted claim digest, a policy id, an issue and expiry time and a signing key
-- id, and not one of the six had a column. The column named `last_sequence` was the only
-- concept the two shared, under a name neither the wire nor the protocol document uses.
-- It is renamed to the label it stores. `server_receipt_sequence` — which
-- `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` lists in the server-state sentence and
-- which `checkpoint-receipt-v1` label 7 signs — was stored nowhere and read by nothing,
-- so the monotonic counter the protocol attributes to the server did not exist in the
-- only place server state is kept. `scripts/repository/validate_checkpoint_receipt_binding.py`
-- holds the three-way table over the CDDL, this table and
-- `packages/schemas/openapi-v1.yaml#CheckpointReceipt`, and fails when a field is
-- present in one of the three and absent from another, in either direction.
--
-- Label 0 of the wire receipt, the protocol major, has no column on purpose: the DDL
-- expresses its own version by being the shape it is, and is versioned by migration
-- rather than by a constant repeated in every row.
create table checkpoint_receipts (
  -- checkpoint-receipt-v1 label 1: receipt_id.
  checkpoint_receipt_id uuid primary key,
  -- Label 2. The pseudonym the device signs, and the only account-shaped value that
  -- crosses the boundary; the server's own `account_id` is deliberately not here,
  -- because a receipt is answered to a lineage.
  account_pseudonym bytea not null check (octet_length(account_pseudonym) = 32),
  -- Label 3: device_lineage_id.
  lineage_id uuid not null references device_lineages(lineage_id),
  -- Server-only. Which device row presented the batch. The receipt is lineage-scoped on
  -- the wire because continuity is lineage-scoped under PF-009, and the device is
  -- operational attribution the participant is not asked to carry.
  device_id uuid not null references devices(device_id),
  -- Server-only. The batch's lower bound. The receipt acknowledges a head; the server
  -- records the span that produced it, which is what makes a partially applied batch
  -- visible as a row rather than as an absence.
  first_sequence bigint not null check (first_sequence >= 0),
  -- Label 4. Previously `last_sequence`, a name that appeared in no other authority.
  accepted_through_claim_sequence bigint not null
    check (accepted_through_claim_sequence >= 0),
  -- Label 5. The local commitment head the server has accepted, which
  -- `device_sequences.server_checkpoint_head` is supposed to be advanced to and which
  -- this table could not previously supply.
  accepted_local_commitment_head bytea not null
    check (octet_length(accepted_local_commitment_head) = 32),
  -- Label 6. The digest of the last claim admitted, so a receipt names the claim it
  -- stops at and not only the number of it.
  last_accepted_claim_sha256 bytea not null
    check (octet_length(last_accepted_claim_sha256) = 32),
  -- Label 7, and the field PF-073 exists for: the monotonic receipt counter
  -- `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` names as server state. It was defined
  -- once, in the CDDL, and stored nowhere.
  server_receipt_sequence bigint not null check (server_receipt_sequence >= 0),
  -- Label 8. Which verifier policy issued this acknowledgement; an appeal that cannot
  -- name the policy it was decided under cannot be decided again.
  verifier_policy_id text not null,
  -- Labels 9 and 10.
  issued_at timestamptz not null,
  expires_at timestamptz not null,
  -- Label 11. Which server signing key to verify `signed_receipt` under, so a rotated
  -- server key does not invalidate every receipt already issued.
  server_signing_key_id uuid not null,
  -- Server-only. The batch this receipt answered.
  batch_digest bytea not null check (octet_length(batch_digest) = 32),
  -- Server-only. The chain link, kept server-side: the device carries the previous
  -- receipt id on its claims, and the server keeps the digest it chains over.
  previous_receipt_digest bytea,
  -- Server-only. The COSE bytes themselves. The wire *is* this, so the column stores the
  -- artifact rather than a field of it, and every label above is a projection of it that
  -- SQL can index.
  signed_receipt bytea not null,
  -- Server-only. When the row was written, which is not `issued_at`: the receipt states
  -- when the server says it issued, and this states when the transaction landed.
  created_at timestamptz not null,
  -- The acknowledged head cannot precede the span that produced it.
  constraint checkpoint_receipts_head_within_span
    check (accepted_through_claim_sequence >= first_sequence),
  constraint checkpoint_receipts_expiry_follows_issue check (expires_at > issued_at),
  -- The `checkpoint-mismatch` basis: two receipts at one head inside one lineage.
  unique (lineage_id, accepted_through_claim_sequence),
  -- The monotonic receipt counter the protocol document names as server state, as a
  -- constraint. This is a DIFFERENT counter from the claim sequence above and the two
  -- move at different rates: one accepted batch advances
  -- `accepted_through_claim_sequence` by up to 256 — `batch-context` label 4 admits that
  -- many claims — and advances `server_receipt_sequence` by exactly one, because one
  -- committed batch returns one receipt. Reading either as the other is how a receipt
  -- chain with 4 links and a claim chain with 900 links look like a fork.
  unique (lineage_id, server_receipt_sequence)
);

-- The persistence half of the challenge. `packages/schemas/vibeproof-claim-v1.cddl#challenge-v1`
-- is the canonical form and this table stores every one of its eleven fields;
-- `scripts/repository/validate_batch_challenge_binding.py` holds the three-way table
-- and fails when a field exists in one authority and not the others.
--
-- What was wrong, and it was the load-bearing half of SR-007. The CDDL challenge
-- bound the expected next sequence, the expected local head and the expected
-- checkpoint. This table stored none of the three, and
-- `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` says the server "verifies challenge
-- ownership, expiry, expected tuple and single use" in step 5 of the atomic
-- transaction. The expected tuple had no row to be verified against, so a
-- verification the protocol describes could not be performed at all — not
-- incorrectly performed, not performed. The three columns below are that tuple.
--
-- `challenge_id` was `text` while the CDDL binds `uuid7` and the API published a
-- 64-hex string. Three types for one identifier, and `claims.challenge_id`
-- referenced the text one, so the width a verifier compared depended on which
-- document it had read.
--
-- `device_id` is audit and is deliberately not part of the bound tuple: it records
-- which device row asked, and the CDDL challenge carries no device at all. A
-- challenge is answered by the lineage, so consumption is checked against
-- `lineage_id` and a re-enrolled device inside one lineage cannot replay a
-- challenge issued to its predecessor.
create table claim_challenges (
  challenge_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  account_pseudonym bytea not null check (octet_length(account_pseudonym) = 32),
  lineage_id uuid not null references device_lineages(lineage_id),
  device_id uuid not null references devices(device_id),
  nonce bytea not null check (octet_length(nonce) = 32),
  expected_next_sequence bigint not null check (expected_next_sequence >= 0),
  expected_local_commitment_head bytea not null check (octet_length(expected_local_commitment_head) = 32),
  expected_checkpoint_receipt_id uuid references checkpoint_receipts(checkpoint_receipt_id),
  issued_at timestamptz not null,
  expires_at timestamptz not null,
  -- ADR-007 requires both ceilings on the challenge. `batch-context` admits at most
  -- 256 claims, so a challenge authorizing more authorizes a batch that cannot be
  -- encoded; the byte ceiling is the `maximum encoded bytes` ADR-007 names and which
  -- previously existed in no artifact at all.
  max_batch_claims integer not null check (max_batch_claims between 1 and 256),
  max_encoded_bytes bigint not null check (max_encoded_bytes > 0),
  -- ADR-007: "A challenge is consumed only when the full batch commits. A challenge
  -- cannot authorize multiple batches." One nullable batch reference, unique across
  -- the table, is that rule as a write refusal rather than as prose: a second batch
  -- claiming the same challenge cannot be recorded, and a challenge consumed by
  -- nothing has both columns null.
  consumed_by_batch_id uuid,
  consumed_at timestamptz,
  constraint claim_challenges_expiry_follows_issue check (expires_at > issued_at),
  constraint claim_challenges_consumption_is_atomic
    check ((consumed_by_batch_id is null) = (consumed_at is null)),
  unique (consumed_by_batch_id)
);

-- Keyed on the lineage, not the device row. AGENTS.md states as a binding rule that
-- continuity is lineage-scoped rather than device-row-scoped, and this table is the
-- mechanism that enforces it. Keyed on device_id it did the opposite: a copied device
-- store enrols as a second device row, gets its own sequence starting from zero, and
-- both rows are then internally continuous forever. The fork that the D-072 quarantine
-- exists to catch was invisible to the counter meant to catch it. One row per lineage
-- means two devices sharing a lineage contend for one sequence, which is what makes a
-- clone observable.
--
-- continuity_state is deliberately absent. device_lineages owns it. It previously sat
-- on both tables with nothing stating which won, so a device row reading `continuous`
-- while its lineage read `broken` was representable and unresolvable.
create table device_sequences (
  lineage_id uuid primary key references device_lineages(lineage_id),
  next_sequence bigint not null check (next_sequence >= 0),
  local_commitment_head bytea,
  server_checkpoint_head bytea
);

-- Scoped to the lineage for the same reason `device_sequences` is, and repaired in
-- the same direction under PF-010. D-592 rekeyed the counter and stopped there: the
-- counter became lineage-scoped while the uniqueness that enforces it stayed
-- device-scoped, so the sequence a clone could no longer obtain from the counter it
-- could still write into `claims`. Two device rows inside one lineage could each hold
-- `device_sequence` 42 and each hold the same `payload_hash`, and both unique indexes
-- accepted it, because `device_id` discriminated the pair. That is the same defect one
-- table further along, and `duplicate-sequence-continuation` — the first of the four
-- detection bases D-072 recognises — is exactly the collision these indexes now refuse.
--
-- `device_id` is retained: which device row submitted a claim is what names a branch
-- when a fork case is opened, and `lineage_fork_branches.device_id` reads it. It is
-- audit and attribution, and it is no longer a uniqueness discriminator.
-- The batch itself, which had no table. `claims.batch_id` was a bare `uuid not null`
-- pointing at nothing, so the question "is partial acceptance prohibited by a
-- constraint?" answered no at every layer: prose in ADR-007, VIBEPROOF_V1_PROTOCOL.md
-- and AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md, and nothing in the schemas.
--
-- `unique (batch_id, outcome)` exists so the two tables below can reference the pair.
-- `batch_id` is already the primary key, so the pair is unique for free; declaring it
-- makes it a legal foreign-key target, which is what turns "no partial acceptance"
-- into a constraint PostgreSQL enforces rather than a rule a handler is trusted to
-- apply. `claims` may reference a batch only at an outcome that committed and
-- `claim_rejections` only at an outcome that did not, so a row admitting a claim from
-- a refused batch, or refusing one from a committed batch, cannot be written.
--
-- The six outcomes are `atomic-batch-result-v1` label 2 in the same order. The API
-- publishes two states, `accepted` and `rejected`; validate_batch_challenge_binding.py
-- holds the mapping from these six onto those two and fails if either side changes
-- without the other.
create table claim_batches (
  batch_id uuid primary key,
  challenge_id uuid not null references claim_challenges(challenge_id),
  account_id uuid not null references accounts(account_id),
  lineage_id uuid not null references device_lineages(lineage_id),
  outcome text not null check (outcome in ('committed','idempotent-replay','conflict','rejected','quarantined','retryable')),
  claim_count integer not null check (claim_count between 1 and 256),
  encoded_bytes bigint not null check (encoded_bytes > 0),
  request_fingerprint bytea not null check (octet_length(request_fingerprint) = 32),
  received_at timestamptz not null,
  unique (batch_id, outcome)
);

-- `batch_id`, `batch_index` and `batch_claim_count` are the columns for
-- `vibeproof-claim-v1` labels 31, 32 and 33, which the claim now signs. ADR-007
-- rejects a batch for "missing indices, duplicate indices, changed order", and until
-- those labels existed the only statement of a claim's position was the order of the
-- unsigned outer `batch-context` array, which the submitter writes. `unique (batch_id,
-- batch_index)` refuses a duplicate index; a missing one is `claim_count` disagreeing
-- with the number of rows; a changed order is an index disagreeing with the signed
-- payload. All three are now answerable from stored signed material.
create table claims (
  claim_id uuid primary key,
  batch_id uuid not null,
  batch_outcome text not null check (batch_outcome in ('committed','idempotent-replay')),
  batch_index integer not null check (batch_index between 0 and 255),
  batch_claim_count integer not null check (batch_claim_count between 1 and 256),
  account_id uuid not null references accounts(account_id),
  lineage_id uuid not null references device_lineages(lineage_id),
  device_id uuid not null references devices(device_id),
  device_sequence bigint not null,
  challenge_id uuid not null references claim_challenges(challenge_id),
  payload_hash bytea not null,
  accounting_profile_id text not null,
  token_burn_total bigint not null check (token_burn_total >= 0),
  received_at timestamptz not null,
  constraint claims_index_within_count check (batch_index < batch_claim_count),
  foreign key (batch_id, batch_outcome) references claim_batches (batch_id, outcome),
  unique (batch_id, batch_index),
  unique (lineage_id, device_sequence),
  unique (lineage_id, payload_hash)
);

create table claim_payloads (
  claim_id uuid primary key references claims(claim_id),
  canonical_payload bytea not null,
  signature bytea not null
);

-- The other half of the no-partial-acceptance constraint. A rejection may only name a
-- batch at an outcome that did not commit, so "batch accepted, claims 3 and 7
-- rejected" — a valid instance of the published API schema until PF-070 — has no
-- representation here either. `claim_index` is the signed `batch_index` of the claim
-- the rejection refers to; the table previously carried no batch reference at all, so
-- a rejection could not be attributed to a submission.
create table claim_rejections (
  rejection_id uuid primary key,
  batch_id uuid not null,
  batch_outcome text not null check (batch_outcome in ('conflict','rejected','quarantined','retryable')),
  claim_index integer not null check (claim_index between 0 and 255),
  payload_hash bytea,
  reason_code text not null,
  retryable boolean not null,
  created_at timestamptz not null,
  foreign key (batch_id, batch_outcome) references claim_batches (batch_id, outcome),
  unique (batch_id, claim_index)
);

-- D-043 says "bounded signed gap declarations downgrade continuity" and ADR-007 says
-- "a signed `gap-declaration` included in the first claim after the gap". Before
-- PF-070 the declaration had a CBOR shape and nothing else: no COSE wrapper, so
-- nothing could sign it; no slot in a claim or a batch, so nothing could carry it; no
-- table, so nothing could store it; and no expression of the 10,000-sequence maximum,
-- so "bounded" was a word in D-043's own text with no enforcement anywhere. Meanwhile
-- `device_lineages.continuity_state` could already be set to `gap-declared` with no
-- record of which gap, which is a mutable aggregate with no persistence owner.
--
-- The bound lives here because it cannot live in the CDDL: it is a relation between
-- two labels and CDDL constrains each label independently. `policy-defaults-v1.json`
-- carries the same number as configuration and
-- `scripts/repository/validate_batch_challenge_binding.py` fails if this CHECK, that
-- default and the figure ADR-007 states stop agreeing.
--
-- The cause vocabulary is ADR-007's four, in the ordinal order `gap-declaration`
-- label 7 encodes. That label was `0..5`: two ordinals were representable with no
-- registered meaning, so a declaration the grammar accepted could name a cause no
-- policy resolved.
create table gap_declarations (
  gap_declaration_id uuid primary key,
  lineage_id uuid not null references device_lineages(lineage_id),
  first_post_gap_claim_id uuid not null unique references claims(claim_id),
  sequence_before_gap bigint not null check (sequence_before_gap >= 0),
  sequence_after_gap bigint not null check (sequence_after_gap >= 0),
  local_commitment_head_before bytea not null check (octet_length(local_commitment_head_before) = 32),
  local_commitment_head_after bytea not null check (octet_length(local_commitment_head_after) = 32),
  cause text not null check (cause in ('local-corruption','acknowledged-state-loss','interrupted-migration','key-recovery')),
  local_audit_commitment bytea not null check (octet_length(local_audit_commitment) = 32),
  -- SHA-256 of the COSE_Sign1 declaration, which is `vibeproof-claim-v1` label 34 on
  -- the first post-gap claim. Storing the digest beside the bytes is what makes the
  -- claim's signature cover this row: an envelope substituted in transport no longer
  -- matches the digest the device signed.
  declaration_digest bytea not null check (octet_length(declaration_digest) = 32),
  signed_declaration bytea not null,
  declared_at timestamptz not null,
  -- A declaration must skip at least one sequence, or it is not a gap.
  constraint gap_declarations_skips_at_least_one
    check (sequence_after_gap > sequence_before_gap + 1),
  -- ADR-007: "The maximum recoverable gap is 10,000 sequences." The missing count is
  -- the open interval between the two, so it is after - before - 1.
  constraint gap_declarations_within_recoverable_bound
    check (sequence_after_gap - sequence_before_gap - 1 <= 10000),
  unique (lineage_id, sequence_before_gap)
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
  -- Deliberately not a foreign key: the case survives erasure unlinked; a nullable reference still blocks the delete.
  account_id uuid,
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
  -- Deliberately not a foreign key: the appeal survives erasure unlinked; the account row does not.
  account_id uuid not null,
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

-- A period has a lifecycle and did not have one. `seasons` carried five
-- timestamps in a checked order and `periods` carried none of it, so "period
-- results remain provisional through the lateness window, then finalize" was a
-- sentence in the time contract with nothing to record which side of it a period
-- was on, and a correction applied to a closed period was indistinguishable from
-- a claim landing in an open one.
--
-- open      admits claims and rebuilds freely.
-- frozen    admits no further claim however late its interval; the final
--           generation has not sealed.
-- closed    the final generation is sealed and is the standing.
-- corrected an appeal or a verified server correction has superseded that
--           standing with a later generation. The closed one is not edited.
-- archived  the appeal window has passed; nothing supersedes it again.
--
-- The lifetime period never leaves `open`: it is unbounded, so it has no end to
-- freeze at, and a lifetime row in any other state would be a period whose
-- boundary the calendar says does not exist.
create table periods (
  period_id uuid primary key,
  period_type text not null check (period_type in ('daily','weekly','monthly','seasonal','yearly','lifetime')),
  season_id uuid references seasons(season_id),
  starts_at timestamptz,
  ends_at timestamptz,
  state text not null check (state in ('open','frozen','closed','corrected','archived')),
  rules_version text not null,
  check ((period_type = 'lifetime') = (starts_at is null)),
  check ((starts_at is null) = (ends_at is null)),
  check (starts_at is null or starts_at < ends_at),
  check ((period_type = 'seasonal') = (season_id is not null)),
  check (period_type <> 'lifetime' or state = 'open'),
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

-- One correction's effect on one participant in one period of one view.
--
-- The table held `(correction_id, ranking_view_id, token_burn_total_delta)` and
-- nothing else, so it named no subject and no period: every row said that some
-- total somewhere moved by some amount. `ranking_corrections_correction_idx`
-- was documented as serving "applying or reversing one correction across views",
-- and a rebuild from these rows could not reproduce any participant's figure
-- because no row said whose figure it was. `erasure_domain_id` and `period_id`
-- are the discriminators the key omitted, and `direction` with an unsigned
-- `magnitude` is D-263's form: additions and retractions are summed separately
-- and checked, rather than a signed column that can be made to cancel itself.
--
-- `erasure_domain_id` carries no foreign key on purpose. The disposition
-- registry classes this table `retain-unlinked`: the row outlives the domain it
-- described, unlinked, so a correction stays auditable after an erasure without
-- the erasure having to rewrite it.
create table ranking_corrections (
  ranking_correction_id uuid primary key,
  -- Deliberately not a foreign key: claim_corrections is deleted by erasure; the correction is retained pseudonymously.
  correction_id uuid not null,
  -- The foreign key to ranking_views is added after that table is declared,
  -- because this one is declared first and PostgreSQL executes the file in order.
  ranking_view_id text not null,
  period_id uuid not null references periods(period_id),
  erasure_domain_id uuid not null,
  direction text not null check (direction in ('addition','retraction')),
  magnitude bigint not null check (magnitude >= 0),
  applied_generation bigint not null check (applied_generation >= 0),
  created_at timestamptz not null,
  unique (correction_id, ranking_view_id, period_id, erasure_domain_id, direction)
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

-- The per-account visibility policies. `visibility` governs the profile;
-- `presence_visibility` governs the presence projection and is separate because
-- the contract gives presence an independent control. PF-026 moved the presence
-- policy here from `presence_leases`, where it was stored once per device against
-- a projection that produces one answer per account.
create table profiles (
  account_id uuid primary key references accounts(account_id),
  visibility text not null check (visibility in ('public','friends','private')),
  presence_visibility text not null default 'authorized-viewers' check (presence_visibility in ('authorized-viewers','private')),
  updated_at timestamptz not null
);

create table friend_requests (
  friend_request_id uuid primary key,
  requester_account_id uuid not null references accounts(account_id),
  target_account_id uuid not null references accounts(account_id),
  state text not null check (state in ('none','pending-a-to-b','pending-b-to-a','active','ended'))
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
  state text not null check (state in ('none','active','ended')),
  primary key (account_id, rival_account_id)
);

create table organizations (
  organization_id uuid primary key,
  -- Deliberately not a foreign key: an organization outlives its owner's erasure.
  owner_account_id uuid not null,
  name text not null,
  state text not null check (state in ('active','archived'))
);

create table communities (
  community_id uuid primary key,
  -- Deliberately not a foreign key: a community outlives its owner's erasure.
  owner_account_id uuid not null,
  name text not null,
  state text not null check (state in ('active','archived'))
);

-- PF-025. `name` and `visibility` were published by the API and stored nowhere.
-- `Board` required `name` and `BoardCreateRequest` accepted one, so the request
-- carried a value the persistence owner could not hold; and board visibility is
-- the input AGENTS.md makes load-bearing — only the global leaderboard is
-- universally public, every other board view requires current viewer
-- authorization — so a board with no visibility column gave that rule nothing to
-- read. The four values are the ones
-- `docs/product/SOCIAL_INTEGRITY_AND_UX_CONTRACT.md` states.
--
-- `membership_revision` is the board-scoped counter the D-386 recheck compares
-- against. It advances on every membership or role change, which is what lets a
-- notification generated under one authorization state be refused when the
-- board's membership has moved on. `board_memberships.state` used to serve as
-- the revision source in `packages/schemas/projection-authorization-v1.json`; a
-- state detects a change and cannot order two, and a promotion followed by a
-- demotion back to the same state was invisible to it.
create table boards (
  board_id uuid primary key,
  board_type text not null check (board_type in ('private','organization','hacker-house','community')),
  name text not null,
  visibility text not null check (visibility in ('public','unlisted','invite-only','private')),
  policy_version text not null,
  membership_revision bigint not null default 0 check (membership_revision >= 0),
  state text not null check (state in ('active','archived')),
  created_at timestamptz not null
);

-- PF-025. `state` carried a terminal `blocked` and the `board-membership` machine
-- carried a `block-cascade` transition into it from four states, with no
-- transition out. That is the D-585 defect one aggregate over: a directional
-- block between two accounts destroyed a membership a third party — the board
-- owner — had granted, permanently, and unblocking could not restore it because
-- terminal means terminal. A board can still refuse a person: `removed` is that
-- act, it is taken by a board admin under recent authentication, and it is
-- reversible. Block effects on a board surface are read-time effects under
-- `packages/schemas/projection-authorization-v1.json#directional-block`, exactly
-- as they are for friendship.
--
-- `revision` is per membership row and advances with each transition; the board's
-- own `membership_revision` advances in the same transaction. Two counters rather
-- than one because a member's own row moves for reasons the board-wide view does
-- not care about, and a board-wide check that read a single member's counter
-- would pass whenever that member happened not to have moved.
create table board_memberships (
  board_id uuid not null references boards(board_id),
  account_id uuid not null references accounts(account_id),
  role text not null check (role in ('owner','admin','member','viewer')),
  state text not null check (state in ('invited','active-viewer','active-member','active-admin','active-owner','left','removed')),
  revision integer not null default 1 check (revision > 0),
  updated_at timestamptz not null,
  primary key (board_id, account_id),
  check (
    (state = 'active-owner' and role = 'owner')
    or (state = 'active-admin' and role = 'admin')
    or (state = 'active-member' and role = 'member')
    or (state = 'active-viewer' and role = 'viewer')
    or state in ('invited','left','removed')
  )
);

-- PF-025. The invitation is the operation the unit's acceptance says cannot grant
-- an admin or owner role, and until now it held no role column and no invitee: it
-- was a board id, a state and an expiry. A refusal that compares a field no record
-- holds refuses nothing, and `BoardInvitationRequest.role` admitted `owner` and
-- `admin` on the wire with nothing downstream to reject them. Both columns exist
-- now and `role` is constrained to the two non-privileged values, so privilege
-- escalation by invitation is unrepresentable rather than checked in a handler.
-- Admin promotion is a separate transition under recent authentication, and
-- ownership moves only through the paired transfer.
--
-- `invalidated-by-block` is gone for the same reason `blocked` left the membership
-- table. An invitation killed by a block could not be revived by an unblock; a
-- pending invitation is suppressed at read time while the block stands and expires
-- on its own clock if nobody acts.
create table board_invites (
  board_invite_id uuid primary key,
  board_id uuid not null references boards(board_id),
  invited_account_id uuid not null references accounts(account_id),
  invited_by_account_id uuid not null references accounts(account_id),
  role text not null check (role in ('member','viewer')),
  state text not null check (state in ('pending','accepted','declined','expired','revoked')),
  created_at timestamptz not null,
  expires_at timestamptz not null,
  check (invited_account_id <> invited_by_account_id)
);

-- The current presence answer for one device, server-derived under D-073 from
-- qualifying native pulses. `lease_generation` is monotonic per row and is what
-- makes a pulse from a resumed process unable to revive an expired lease: the
-- pulse names the generation it was minted under, and a pulse naming a
-- superseded generation is discarded rather than applied.
--
-- Visibility is an independent policy and not a state. A private participant
-- still has a lease and still transitions; what changes is who may read the
-- projection of it. Collapsing the two would make going private look like going
-- offline to the server as well as to the viewer.
--
-- PF-025..PF-027 moved that policy off this row. It was `presence_leases.visibility`,
-- one value per device, while the thing it decides is one answer per account: the
-- projection merges every device into a single availability, so two devices could
-- hold `private` and `authorized-viewers` and nothing said which the merge takes.
-- Going private on a laptop while a desktop stayed authorized would have published
-- the participant anyway. It lives on `profiles.presence_visibility` now, which is
-- the per-account visibility owner, and the lease row holds only what the device
-- observed.
create table presence_leases (
  account_id uuid not null references accounts(account_id),
  device_id uuid not null references devices(device_id),
  state text not null check (state in ('absent','active','idle','expired','revoked')),
  lease_generation bigint not null default 0 check (lease_generation >= 0),
  revision integer not null default 1 check (revision > 0),
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
  -- PF-027. The column existed and admitted any string, so the "registered reason
  -- code" the contract promises was a convention rather than a vocabulary. These
  -- are the three notification-transport codes in
  -- `packages/schemas/reason-codes-v1.json`; the same three are the enum in
  -- `notification-delivery-v1.schema.json#/$defs/retraction`, and
  -- `scripts/repository/validate_social_surface_contracts.py` compares the two sets
  -- so a code added to one and not the other fails.
  retraction_reason_code text check (retraction_reason_code in (
    'NOTIFICATION_RETRACTED_BY_CORRECTION',
    'NOTIFICATION_RETRACTED_BY_MODERATION_REVERSAL',
    'NOTIFICATION_RETRACTED_BY_RANKING_REBUILD')),
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
--
-- PF-027 added `product_enabled` and, with it, the mapping that was missing. Four
-- flags governed eight event types and nothing anywhere said which flag governed
-- which type, so `suppression_cause = 'category-disabled'` named a category no
-- artifact defined and `compatibility` and `release` fell under no flag at all: a
-- worker had to invent the mapping, and whether `security` could be muted depended
-- on which mapping it invented. The map is declared in
-- `packages/schemas/notification-delivery-v1.schema.json#/$defs/event_categories`
-- and `scripts/repository/validate_social_surface_contracts.py` requires every
-- event type to name a category and every category to have a column here.
create table notification_preferences (
  account_id uuid primary key references accounts(account_id),
  social_enabled boolean not null,
  ranking_enabled boolean not null,
  moderation_enabled boolean not null,
  product_enabled boolean not null,
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

-- One Article 15 or Article 20 request. PF-028, SR-013.
--
-- The row held four columns: an id, an account, a state and a nullable expiry. Every
-- other thing `docs/privacy/PRIVACY_CONTRACT.md` requires of an export -- a typed
-- scope, a coherent snapshot time, a manifest, checksums, encryption, and a
-- short-lived revocable grant -- had no column, so the `export-job` machine could
-- move through `snapshotting`, `encrypting` and `ready` while the table recorded
-- nothing any of those three words produced.
--
-- `snapshot_cutoff_at` is one instant for the whole package rather than one per
-- domain. Two domains read at two instants produce a package whose claims and whose
-- social edges disagree about what existed, and a reader cannot tell which half is
-- current. The privacy contract records the export as the single snapshot-time
-- exception to rechecking authorization at read time, and that exception holds only
-- because the subject and the viewer are the same person.
--
-- `recent_auth_verified_at` is the frozen grant. It is recorded when the request is
-- made and never refreshed, so a package produced minutes later rests on the
-- authentication the participant actually performed rather than on the session still
-- being open when a worker got to it.
--
-- The state-dependent checks are the part a worker cannot skip. A job cannot reach
-- `ready` without a manifest digest, an encryption key reference and an expiry: an
-- export that is downloadable and unsealed, or downloadable and eternal, is refused
-- by the table rather than by a worker's discipline.
create table exports (
  export_id uuid primary key,
  account_id uuid not null references accounts(account_id),
  scope text not null check (scope in ('account','claims','social','all')),
  state text not null check (state in ('requested','snapshotting','encrypting','ready','downloaded','purged','failed')),
  revision integer not null default 1 check (revision > 0),
  requested_at timestamptz not null,
  recent_auth_verified_at timestamptz not null,
  snapshot_cutoff_at timestamptz,
  manifest_digest bytea check (octet_length(manifest_digest) = 32),
  encryption_key_reference text,
  generated_at timestamptz,
  expires_at timestamptz,
  purged_at timestamptz,
  check (recent_auth_verified_at <= requested_at),
  check (snapshot_cutoff_at is null or snapshot_cutoff_at >= requested_at),
  check (state not in ('snapshotting','encrypting','ready','downloaded','purged') or snapshot_cutoff_at is not null),
  check (
    state not in ('ready','downloaded')
    or (manifest_digest is not null and encryption_key_reference is not null
        and generated_at is not null and expires_at is not null)
  ),
  check (expires_at is null or expires_at > requested_at),
  check ((state = 'purged') = (purged_at is not null))
);

-- One Article 17 request and the plan it executes. PF-029, SR-013.
--
-- The row held four columns and could not express the thing the Article 30 record
-- promises about it. `docs/privacy/DATA_MAP.md` states a seven-day cooling-off window
-- that is cancellable within it; the machine had no `cancelled` state, the table had no
-- window to be inside, and `docs/architecture/AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md`
-- recorded the gap as an open item. A cancellation the participant is promised and the
-- schema cannot hold is a promise made to a supervisory authority and to nobody else.
--
-- `effective_after` is that window as a value rather than as a sentence, and
-- `cancelled_at < effective_after` is the rule that a cancellation happens inside it.
-- The constraint is on the write. A worker reading "is it still cooling off?" and
-- deciding correctly every time is not a control; a row that cannot record a
-- cancellation after the window closed is.
--
-- `recent_auth_verified_at` is frozen at request time and never refreshed, so the
-- erasure a worker performs a week later rests on the authentication the participant
-- actually performed.
--
-- The legal hold is two columns and one refusal. A held job may sit in the states
-- before execution and may be cancelled or fail; it may not be in `processing`,
-- `rebuilding-projections`, `awaiting-local-receipt` or `complete`. Article 12(4)
-- requires the participant to be told the request is not being acted on, which is what
-- `DeletionJob.blocked_by_legal_hold` publishes -- that it is held, and not what the
-- hold is.
create table deletion_jobs (
  deletion_job_id uuid primary key,
  -- Deliberately not a foreign key: the job is the proof the deletion happened; it cannot reference what it deleted.
  account_id uuid not null,
  scope text not null check (scope in ('server','local','everything')),
  state text not null check (state in ('requested','recent-auth-verified','cooling-off','processing','rebuilding-projections','awaiting-local-receipt','complete','cancelled','failed')),
  revision integer not null default 1 check (revision > 0),
  requested_at timestamptz not null,
  recent_auth_verified_at timestamptz not null,
  effective_after timestamptz not null,
  legal_hold_reference text,
  legal_hold_placed_at timestamptz,
  cancelled_at timestamptz,
  completed_at timestamptz,
  check (recent_auth_verified_at <= requested_at),
  check (effective_after > requested_at),
  check ((state = 'cancelled') = (cancelled_at is not null)),
  check ((state = 'complete') = (completed_at is not null)),
  check (cancelled_at is null or cancelled_at < effective_after),
  check ((legal_hold_reference is null) = (legal_hold_placed_at is null)),
  check (
    legal_hold_reference is null
    or state in ('requested','recent-auth-verified','cooling-off','cancelled','failed')
  )
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
-- Keyed on the full scope openapi-v1.yaml#x-idempotency-contract declares:
-- (principal_type, principal_id, operation_id, idempotency_key). It previously keyed
-- on (actor_account_id, idempotency_key), so `operation_id` was a column outside the
-- key and a client reusing one key across two operations collided. The dangerous half
-- of that collision is not the spurious 409: a committed row stores the exact response
-- for replay, so the second operation could be answered with the first operation's
-- recorded body.
--
-- `principal_id` deliberately carries no foreign key. The contract's principal is the
-- account for a web session and the bound device enrollment for a native session, so
-- the column addresses two tables and a reference could only point at one of them.
-- `principal_type` says which.
create table idempotency_records (
  principal_type text not null check (principal_type in ('account','device')),
  principal_id uuid not null,
  operation_id text not null,
  idempotency_key uuid not null,
  request_digest bytea not null check (octet_length(request_digest) = 32),
  -- The wire contract promises a replay returns the original response body
  -- byte for byte. A digest cannot produce a body, so the body itself is stored:
  -- a ledger that can only prove a response was equal cannot return it, and the
  -- contract read as satisfied while nothing could satisfy it.
  --
  -- Only the server's own fixed-schema response is stored here. No request body,
  -- no client content: the privacy boundary is what may be written, not what this
  -- column can hold, and `expires_at` bounds how long even that is kept.
  response_status smallint check (response_status between 100 and 599),
  response_body bytea,
  response_digest bytea check (response_digest is null or octet_length(response_digest) = 32),
  state text not null check (state in ('executing','committed','replayable-failure','conflict','expired','abandoned')),
  -- The end of the replay window: after this the response bytes are discarded and
  -- the row moves to `expired`. D-225 fixes it at 168 hours.
  expires_at timestamptz not null,
  -- The end of the *row*, which is a different date and was doing the same job
  -- through the same column. PF-020.
  --
  -- One column cannot bound both, and while it did, the only way to stop answering
  -- a replay was to delete the row -- which makes the key fresh again, so the next
  -- request carrying it is executed as a new mutation instead of refused. That is
  -- the ambiguous-commit failure this ledger exists to prevent, reintroduced by the
  -- cleanup. `x-idempotency-contract.expiry` already says the request "is not
  -- re-executed under the same key", and nothing here could hold that promise past
  -- the 168th hour.
  --
  -- `retain_until` is governed by `idempotency_record_retention_days` in
  -- `packages/schemas/policy-defaults-v1.json`, default 30 days, and is strictly
  -- later than `expires_at` so the refusal outlives the answer. Between the two
  -- dates the row holds a key, a request digest and a state, and no response: enough
  -- to refuse a reuse with 410, not enough to replay anything.
  retain_until timestamptz not null,
  -- A committed or replayable-failure record is one a replay must be able to
  -- answer from. Leaving any of the three nullable in those states is what let a
  -- row claim to be replayable while holding nothing to replay.
  constraint idempotency_records_replayable_is_answerable check (
    state not in ('committed','replayable-failure')
    or (response_status is not null and response_body is not null and response_digest is not null)
  ),
  -- The digest is over `response_body`. SQL cannot check that without an
  -- extension, so the pairing is constrained instead: neither appears alone.
  constraint idempotency_records_digest_pairs_with_body check (
    (response_body is null) = (response_digest is null)
  ),
  -- The refusal outlives the answer, by construction rather than by sweeper
  -- ordering. Equality is refused too: a row whose retention ends the instant its
  -- replay window does is the deleted row again.
  constraint idempotency_records_retained_past_replay_window check (
    retain_until > expires_at
  ),
  -- An expired row holds nothing to replay. Stated because the alternative --
  -- keeping the bytes and relying on the read path to ignore them -- is a privacy
  -- promise enforced in application code over data that is still there.
  constraint idempotency_records_expired_holds_no_response check (
    state <> 'expired'
    or (response_status is null and response_body is null and response_digest is null)
  ),
  primary key (principal_type, principal_id, operation_id, idempotency_key)
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


-- The authorization ledger for every device-key transition, and the row that has to
-- carry *both* authorizations of an ordinary rotation.
--
-- It carried one. `continuity_signature` was a single nullable blob, so the row could
-- not distinguish a rotation signed by the outgoing key from one signed by the
-- incoming key, and it had no column at all for the account-level authorization.
-- `docs/architecture/VIBEPROOF_V1_PROTOCOL.md` section "Rotation, recovery and gaps"
-- names three separate things — one payload "signed independently by both old and new
-- keys", and a server that "verifies recent authentication" — and
-- `packages/schemas/device-lineage.schema.json` records `old_key_signature`,
-- `account_recent_auth` and `recovery_approval` as three separate fields. One blob
-- could represent none of that, so an ordinary rotation and a single-signature
-- forgery were the same row.
--
-- Dual authorization is the key pair: `dual-authorized-rotation-v1` in the CDDL is
-- literally two COSE_Sign1 rotation envelopes over identical payload bytes, one from
-- the outgoing key proving continuity and one from the incoming key proving control.
-- Account recent authentication is a third, separate gate at a different layer, and it
-- is recorded rather than conflated because a rotation authorized by an account
-- session alone is precisely the takeover the key signatures exist to refuse.
--
-- Lost-key recovery is the case that cannot satisfy the pair: the old key is gone, so
-- `old_key_signature` is null and an approved recovery case is the authority instead.
-- The check constraints make the two paths mutually exclusive rather than merely
-- discouraged — a `recovered` row carrying an old-key signature would be a rotation
-- claiming to be a recovery, and a `rotated` row missing either signature would be a
-- recovery claiming to be a rotation.
--
-- `lineage_id` is here because continuity is lineage-scoped. A key event on a device
-- row that could not be resolved to its lineage was unusable to the fork counter.
create table device_key_events (
  device_key_event_id uuid primary key,
  lineage_id uuid not null references device_lineages(lineage_id),
  device_id uuid not null references devices(device_id),
  previous_key_id text,
  next_key_id text not null,
  action text not null check (action in ('enrolled','rotated','revoked','recovered')),
  old_key_signature bytea,
  new_key_signature bytea,
  account_recent_auth boolean not null default false,
  recovery_approval text not null default 'not-required'
    check (recovery_approval in ('not-required','pending','approved','denied')),
  occurred_at timestamptz not null,
  -- An ordinary rotation carries both key signatures and the account authorization.
  constraint device_key_events_rotation_is_dual_authorized check (
    action <> 'rotated'
    or (old_key_signature is not null
        and new_key_signature is not null
        and account_recent_auth
        and previous_key_id is not null)
  ),
  -- A recovery cannot forge the old signature and is authorized by an approved case.
  constraint device_key_events_recovery_has_no_old_signature check (
    action <> 'recovered'
    or (old_key_signature is null
        and new_key_signature is not null
        and recovery_approval = 'approved')
  ),
  -- Only a recovery is authorized by a recovery case.
  constraint device_key_events_recovery_approval_is_scoped check (
    action = 'recovered' or recovery_approval = 'not-required'
  ),
  -- Enrolment has no predecessor; every other action does. An enrolment that names
  -- one is a rotation, and calling it an enrolment is how a rotation would avoid
  -- needing the outgoing key's signature.
  constraint device_key_events_enrolment_has_no_predecessor check (
    (action = 'enrolled') = (previous_key_id is null)
  ),
  -- Every action that installs a key proves control of it. A revocation installs
  -- none, which is the whole point of revoking a key you no longer hold.
  constraint device_key_events_new_key_is_authorized check (
    action = 'revoked' or new_key_signature is not null
  ),
  -- A revocation is authorized by the account, because the key it revokes is
  -- exactly the thing that may be lost or in someone else's hands.
  constraint device_key_events_revocation_is_account_authorized check (
    action <> 'revoked' or account_recent_auth
  )
);

-- The persistence owner of the verifier appraisal aggregate, and the third of the three
-- authorities that describe it: `verifier-appraisal-v1` in
-- packages/schemas/vibeproof-claim-v1.cddl is the wire form,
-- packages/schemas/appraisal-result-v1.schema.json is the normative record, and this table
-- stores it. Column names are the record's field names on purpose. The previous shape kept
-- three states -- `provenance_state`, `continuity_state`, `integrity_state` -- that appeared
-- in neither other authority, and stored none of the claim digest, evidence digest,
-- validity interval or supersession chain the record requires, so the aggregate's own
-- persistence disagreed with its definition on twenty of twenty-six fields.
--
-- Which table wins, stated because two of them held this aggregate and nothing said which.
-- `evidence_assessments` persisted the same three assessed states against the same
-- `claim_id`, with a non-unique index and no supersession, while
-- `AUTHORITATIVE_STATE_AND_PLATFORM_CONTRACT.md` and `DATA_MAP.md` read the two as one
-- thing. This table is the appraisal aggregate's sole owner:
-- packages/schemas/appraisal-policy-v1.json names it and only it as
-- `appraisal_record.sql_binding.table`, and the appraisal is what an appeal argues from.
-- The three assessed states leave this table entirely -- they were never a second spelling
-- of the seven dimensions, they were a coarser pre-D-267 judgement of the same claim, and
-- keeping a copy here would have made the finding's own defect permanent. They remain on
-- `evidence_assessments`, which is that older record and is retained because `public_state`
-- has a consumer PF-046 owns and because the erasure and data-disposition contracts name
-- the table by name. One aggregate, one owner; the older record is not a competing copy of
-- this one and does not decide anything this one decides.
--
-- `evidence_profile_id` is nullable, which the previous `not null` made unrepresentable: a
-- rejected or quarantined claim is awarded no profile, which is what CDDL label 14 and the
-- record's `awarded_profile_id` have always said. It sat in `bound_columns` and was
-- therefore declared reconciled while contradicting both.
create table verifier_appraisals (
  appraisal_id uuid primary key,
  claim_id uuid not null references claims(claim_id),
  canonical_claim_sha256 bytea not null check (octet_length(canonical_claim_sha256) = 32),
  -- Null when the device retained no bundle, which is an input to the capture dimension
  -- rather than a neutral absence.
  evidence_bundle_sha256 bytea check (octet_length(evidence_bundle_sha256) = 32),
  policy_bundle_id text not null,
  policy_content_sha256 bytea not null check (octet_length(policy_content_sha256) = 32),
  -- Null while no verifier implementation is built. The policy bundle records the same null.
  verifier_implementation_sha256 bytea check (octet_length(verifier_implementation_sha256) = 32),
  acceptance_outcome text not null check (acceptance_outcome in ('accepted','accepted-with-downgrade','accepted-private-analytics','idempotent-replay','quarantined','rejected','superseded','retracted')),
  -- The seven dimensions of packages/schemas/evidence-profile-policy-v1.json, with the
  -- source limbs D-078 splits E1 into. Evaluation is dimensional: a stronger value in one
  -- never compensates for a failed mandatory requirement in another, which is why each is
  -- stored rather than collapsed into a single assessed state.
  source_class text not null check (source_class in ('E1-S','E1-R','E2','E3','E4','E5')),
  capture_class text not null check (capture_class in ('certified-structured','certified-gateway','certified-reconstruction','uncertified')),
  accounting_class text not null check (accounting_class in ('authoritative-profile','exact-reconstruction','approximate','contradictory')),
  device_key_class text not null check (device_key_class in ('K1','K2','K3','K4','K5','KU')),
  continuity_class text not null check (continuity_class in ('C0','C1','C2','C3','C4')),
  environment_class text not null check (environment_class in ('A0','A1','A2','A3','A4')),
  freshness_class text not null check (freshness_class in ('anchored','bounded-delayed','unbounded','contradictory')),
  certification_bundle_sha256 bytea check (octet_length(certification_bundle_sha256) = 32),
  certification_state text not null check (certification_state in ('uncertified','candidate','testing','active','degraded','suspended','expired','superseded','retired')),
  deterministic_rule_bundle_id text not null,
  accounting_profile_id text not null,
  observer_equivalence_rule_id text not null,
  anomaly_disposition text not null check (anomaly_disposition in ('not-evaluated','no-signal','advisory-signal','under-review','shadow-only')),
  evidence_profile_id text check (evidence_profile_id in ('hardened-source-bound-v1','standard-competitive-v1','imported-v1')),
  public_state text check (public_state in ('hardened','standard','imported')),
  ranking_eligibility text not null check (ranking_eligibility in ('competitive','competitive-pending-finalization','private-analytics','quarantined','excluded','retracted')),
  reason_codes text[] not null default '{}',
  effective_from timestamptz not null,
  effective_until timestamptz,
  supersedes_appraisal_id uuid references verifier_appraisals(appraisal_id),
  superseded_by_appraisal_id uuid references verifier_appraisals(appraisal_id),
  re_evaluation_trigger text check (re_evaluation_trigger in ('policy-revision','implementation-revision','certification-change','correction-record','appeal-decision','operator-review')),
  created_at timestamptz not null,
  -- The public label follows from the awarded profile and is never selected by a client, so
  -- the two are present or absent together. Stated as an equality rather than as two
  -- nullable columns, because a row carrying a public state and no profile is exactly the
  -- shape a client-selected state would take.
  constraint verifier_appraisals_public_state_follows_profile check (
    (evidence_profile_id is null) = (public_state is null)
  ),
  -- An outcome that awards nothing cannot carry an award.
  constraint verifier_appraisals_refusal_awards_no_profile check (
    acceptance_outcome not in ('quarantined','rejected','retracted')
    or evidence_profile_id is null
  ),
  -- The same binding PF-071 put on the adapter manifest, in both directions: an uncertified
  -- appraisal has no bundle digest and a certified one has exactly one. Without the reverse
  -- arm a row that forgot the digest would be indistinguishable from one appraised under no
  -- certification at all.
  constraint verifier_appraisals_certification_digest_is_bound check (
    (certification_state = 'uncertified') = (certification_bundle_sha256 is null)
  ),
  -- A validity interval that ends before it starts is not an interval.
  constraint verifier_appraisals_validity_is_ordered check (
    effective_until is null or effective_until > effective_from
  ),
  -- Supersession is a chain, not a self-loop.
  constraint verifier_appraisals_supersession_is_not_reflexive check (
    supersedes_appraisal_id is distinct from appraisal_id
    and superseded_by_appraisal_id is distinct from appraisal_id
  ),
  -- A superseded appraisal names what replaced it and a live one does not, so "which
  -- appraisal is current" is answerable from the row rather than by ordering on a timestamp.
  constraint verifier_appraisals_supersession_names_its_successor check (
    (acceptance_outcome = 'superseded') = (superseded_by_appraisal_id is not null)
  ),
  -- A re-evaluation trigger explains a supersession and belongs to one.
  constraint verifier_appraisals_trigger_belongs_to_a_supersession check (
    re_evaluation_trigger is null or supersedes_appraisal_id is not null
  )
);

-- The stable half of a ranking view: what is ranked and in what order. It names
-- no viewer, no cohort and no board, which is what lets one definition serve
-- many audiences without either of them being able to read the other's page.
-- `filters_digest` covers the five filter dimensions of
-- `packages/schemas/ranking-view-v1.schema.json`; each of those is stated there
-- as a mode rather than as a list, because a list read as a filter is satisfied
-- by emptiness and a filter that lost its values would look unrestricted.
create table ranking_definitions (
  ranking_definition_id text primary key check (ranking_definition_id ~ '^[0-9a-f]{64}$'),
  metric text not null check (metric = 'credited-token-burn'),
  metric_version integer not null check (metric_version >= 1),
  period_id uuid not null references periods(period_id),
  filters_digest bytea not null check (octet_length(filters_digest) = 32),
  tie_policy text not null check (tie_policy = 'shared-rank-with-gaps'),
  display_order text not null check (display_order = 'credited-token-burn-desc,first-reached-at-asc,erasure-domain-id-asc'),
  rules_digest bytea not null check (octet_length(rules_digest) = 32),
  pricing_dataset_digest bytea not null check (octet_length(pricing_dataset_digest) = 32),
  evidence_policy_digest bytea not null check (octet_length(evidence_policy_digest) = 32),
  weight_table_digest bytea not null check (octet_length(weight_table_digest) = 32),
  source_checkpoint_digest bytea not null check (octet_length(source_checkpoint_digest) = 32),
  created_at timestamptz not null
);

-- The audience half, and the pair. One row is one definition read by one
-- audience. `default_visibility` is not free: the second check makes
-- `universally-public` reachable only from the global scope, so AGENTS.md's rule
-- that only the global leaderboard is universally public by default is enforced
-- where the row is written rather than only where a page is rendered. Until
-- PF-021 the rule existed at the read site alone, and the write site admitted a
-- friends view that called itself public.
create table ranking_views (
  ranking_view_id text primary key check (ranking_view_id ~ '^[0-9a-f]{64}$'),
  ranking_definition_id text not null references ranking_definitions(ranking_definition_id),
  audience_id text not null check (audience_id ~ '^[0-9a-f]{64}$'),
  scope text not null check (scope in ('global','friends','rivals','board')),
  board_id uuid references boards(board_id),
  default_visibility text not null check (default_visibility in ('universally-public','viewer-authorized')),
  created_at timestamptz not null,
  unique (ranking_definition_id, audience_id),
  check ((scope = 'board') = (board_id is not null)),
  check ((scope = 'global') = (default_visibility = 'universally-public'))
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

-- `period_scores.generation` records which generation produced the live figures
-- in the row. It was a bare bigint pointing at nothing, so a projection could
-- name a generation that was never built and a reader comparing the live figure
-- against the sealed one had no way to tell which sealed one to compare against.
alter table period_scores
  add constraint period_scores_generation_fk
  foreign key (ranking_view_id, generation)
  references ranking_projection_generations (ranking_view_id, generation);

-- `ranking_corrections` is declared before `ranking_views`, so its view reference
-- is added here rather than inline.
alter table ranking_corrections
  add constraint ranking_corrections_view_fk
  foreign key (ranking_view_id)
  references ranking_views (ranking_view_id);

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
  -- Deliberately not a foreign key: the event survives erasure unlinked; a nullable reference still blocks the delete.
  actor_account_id uuid,
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


-- One file inside one package, and the domain it answers for. PF-028.
--
-- `data_domain` is the seven-key vocabulary `docs/privacy/DATA_MAP.md` declares and
-- `packages/schemas/data-disposition-v1.json` carries on every row it covers. Without
-- it a package was a list of file names, so "the export covers every domain" could not
-- be evaluated against anything: a logical name is whatever the producer typed.
create table export_artifacts (
  export_id uuid not null references exports(export_id),
  logical_name text not null,
  data_domain text not null check (data_domain in ('account-identity','authentication-session','device-collection','usage-claims-scores','social-presence-notifications','integrity-moderation-appeals','requests-exports-deletion')),
  media_type text not null check (media_type in ('application/jsonl','application/json','application/cbor')),
  artifact_digest bytea not null check (octet_length(artifact_digest) = 32),
  size_bytes bigint not null check (size_bytes >= 0),
  record_count bigint not null check (record_count >= 0),
  primary key (export_id, logical_name)
);

-- The immutable domain-and-effect plan: one row per data domain per job. PF-029.
--
-- The column named a subsystem, was declared not null, and carried no vocabulary at
-- all, so "the plan covers every domain" was unevaluable in the strongest sense -- any
-- two workers could spell one subsystem two ways and both rows were accepted. `data_domain`
-- is the seven-key set `docs/privacy/DATA_MAP.md` declares and
-- `packages/schemas/data-disposition-v1.json` carries on every row it covers, so a
-- plan is complete against the Article 30 record or it is not, and the primary key
-- makes a domain appear exactly once.
--
-- `not-applicable` is gone from the state vocabulary, for the reason
-- `packages/schemas/consolidation-plan-v1.schema.json` refuses the same value in the
-- same position: it is a member meaning "we did not look", and with it every domain
-- could be covered by declining to answer. A domain that held nothing for this account
-- reaches `complete` with `affected_row_count` zero, which is a statement about the
-- account rather than about the worker.
--
-- `erasure_action` repeats the disposition registry's own vocabulary rather than
-- inventing a second one. It is what this job did to the domain -- deleted the rows,
-- destroyed the key that bound them, kept them unlinked, kept them pseudonymous -- and
-- because it is the registry's spelling, the effect can be compared to what the
-- registry says the domain's tables were supposed to receive.
create table deletion_effects (
  deletion_job_id uuid not null references deletion_jobs(deletion_job_id),
  data_domain text not null check (data_domain in ('account-identity','authentication-session','device-collection','usage-claims-scores','social-presence-notifications','integrity-moderation-appeals','requests-exports-deletion')),
  state text not null check (state in ('pending','executing','complete','failed')),
  erasure_action text not null check (erasure_action in ('delete','key-destroy-retain','retain-pseudonymous','retain-unlinked')),
  affected_row_count bigint check (affected_row_count >= 0),
  effect_digest bytea check (effect_digest is null or octet_length(effect_digest) = 32),
  completed_at timestamptz,
  primary key (deletion_job_id, data_domain),
  check ((state = 'complete') = (completed_at is not null)),
  check (state <> 'complete' or affected_row_count is not null)
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

-- The release set, and the TUF target that authorizes the manifest describing it.
--
-- `manifest_tuf_role`, `manifest_target_path` and `manifest_digest` are the three
-- columns that make the manifest itself an authenticated target rather than an
-- unauthenticated index over authenticated files. Without them a client that
-- verified every artifact digest in the set would still have taken the list of
-- artifacts from whoever served it, which is the whole of the mix-and-match attack
-- ADR-013 requires clients to defend against. The role check refuses `root`,
-- `timestamp` and `snapshot` in the same position `release-set-v1.schema.json`
-- refuses them: root delegates authority and signs no artifact, timestamp asserts
-- freshness, snapshot asserts which metadata versions belong together, and none of
-- the three has inspected the thing it would be authorizing.
--
-- `mandatory_after` is a signed deadline, so it may not precede publication. The
-- constraint is on the table rather than in the publisher because a deadline is
-- read by every client and written once.
create table release_sets (
  release_set_id uuid primary key,
  version text not null unique,
  source_commit text not null check (source_commit ~ '^[0-9a-f]{40}$'),
  tuf_root_version bigint not null references tuf_roots(root_version),
  compatibility_registry_digest bytea not null check (octet_length(compatibility_registry_digest) = 32),
  manifest_tuf_role text not null check (manifest_tuf_role ~ '^targets(/[a-z0-9][a-z0-9.-]*){1,4}$'),
  manifest_target_path text not null,
  manifest_digest bytea not null check (octet_length(manifest_digest) = 32),
  manifest_signature_bundle_digest bytea not null check (octet_length(manifest_signature_bundle_digest) = 32),
  signing_threshold smallint not null check (signing_threshold between 2 and 10),
  state text not null check (state in ('draft','threshold-signed','published','active','superseded','revoked','expired')),
  published_at timestamptz,
  mandatory_after timestamptz,
  unique (manifest_target_path),
  check (mandatory_after is null or (published_at is not null and mandatory_after > published_at))
);

-- One row per component. Eight facts per component, and each of them is a fact a
-- client checks rather than a label a publisher chooses.
--
-- `tuf_role` and `target_path` are what was missing: a component that carried a hash
-- and no role was authenticated by whoever served it, and a component that carried no
-- path was fetched from wherever the client guessed. `unique (release_set_id,
-- target_path)` is the constraint the JSON Schema cannot express -- two array entries
-- naming one path are two distinct objects and `uniqueItems` sees nothing wrong with
-- them -- so it is enforced here, where the row is written, as well as by the computed
-- check in validate_planning_artifacts.py, which is where the manifest is read.
--
-- `architecture` uses exactly the three spellings the platform profile registry
-- admits. A second spelling for one machine word is how two artifacts describe the
-- same build and compare unequal.
--
-- `signature_bundle_digest` is the platform-native signature -- notarization ticket,
-- Authenticode signature, repository signature -- and is separate from the TUF
-- signature over the metadata. TUF says the repository authorized this file; the
-- native signature is what the operating system checks before it will run it.
--
-- `update_class` is per component because one set can carry an emergency fix for one
-- platform and a routine change for another. Collapsed to the set, either every
-- platform inherits the strictest deadline or the strictest one inherits the loosest.
create table release_targets (
  release_set_id uuid not null references release_sets(release_set_id),
  component_id text not null,
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  tuf_role text not null check (tuf_role ~ '^targets(/[a-z0-9][a-z0-9.-]*){1,4}$'),
  target_path text not null,
  architecture text not null check (architecture in ('arm64','aarch64','x86-64')),
  artifact_kind text not null check (artifact_kind in ('pkg','dmg','msix','msi','deb','rpm','apk','tar-zst','oci','ci-bundle')),
  artifact_digest bytea not null check (octet_length(artifact_digest) = 32),
  sbom_digest bytea not null check (octet_length(sbom_digest) = 32),
  provenance_digest bytea not null check (octet_length(provenance_digest) = 32),
  signature_bundle_digest bytea not null check (octet_length(signature_bundle_digest) = 32),
  compatibility_tuple_digest bytea not null check (octet_length(compatibility_tuple_digest) = 32),
  update_class text not null check (update_class in ('emergency-security-integrity','required-compatibility','routine-product')),
  size_bytes bigint not null check (size_bytes > 0),
  primary key (release_set_id, platform_profile_id, artifact_kind),
  unique (release_set_id, component_id),
  unique (release_set_id, target_path)
);

create table platform_certifications (
  certification_id uuid primary key,
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  release_set_id uuid not null references release_sets(release_set_id),
  test_run_digest bytea not null check (octet_length(test_run_digest) = 32),
  state text not null check (state in ('candidate','exercised','certified','failed','revoked')),
  certified_at timestamptz
);

-- One device's position in the update lifecycle, and the two facts that decide
-- whether it may go backwards.
--
-- `applied_migration_version` binds the installation to a step in the ordered
-- migration chain, and `rollback_available` records the answer D-074 makes
-- conditional: automatic binary rollback is permitted only while the previous
-- release stays read/write compatible with every committed mutation. The updater
-- must not discover that at run time, so the column is `not null` -- there is no
-- "unknown" -- and the `rolled-back` state is refused without it. That refusal sits
-- here, where the state is written, and not only in the code that reads the state
-- afterwards.
--
-- `recovery-required` is the state a forward-only failure lands in. It exists
-- because the machine previously had one rollback edge out of `failed` and no way to
-- express that a step whose `rollback_class` is `forward-only` or
-- `snapshot-required` has no such edge, so an installation that had destroyed its
-- own downgrade path could still be recorded as rolled back. Recovery from there is
-- roll-forward or an operator restoring a verified pre-migration snapshot, and
-- neither is this aggregate going backwards.
--
-- `installed_release_version` is what the version floor is evaluated against.
-- `blocked_reason_code` is the code the refusal carries, present exactly when the
-- installation is blocked, so a blocked device and the reason it was blocked cannot
-- disagree.
create table update_installations (
  update_installation_id uuid primary key,
  device_id uuid not null references devices(device_id),
  release_set_id uuid not null references release_sets(release_set_id),
  installed_release_version text not null,
  state text not null check (state in ('current','available','deferred','deadline','downloading','staged','installing','health-check','complete','rolled-back','recovery-required','blocked-version','failed')),
  previous_release_set_id uuid references release_sets(release_set_id),
  applied_migration_version text references schema_migrations(version),
  rollback_available boolean not null,
  health_check_passed boolean,
  health_checked_at timestamptz,
  blocked_reason_code text check (blocked_reason_code = 'CLIENT_VERSION_UNSUPPORTED'),
  revision bigint not null check (revision >= 0),
  updated_at timestamptz not null,
  -- A rollback is only recordable when one was available.
  check (state <> 'rolled-back' or rollback_available),
  -- And `recovery-required` is only recordable when one was not; the two states
  -- answer the same question and may not both be reachable from one row.
  check (state <> 'recovery-required' or not rollback_available),
  -- There is nothing to roll back to without a prior release.
  check (not rollback_available or previous_release_set_id is not null),
  -- The health check is bounded and its result is not optional before promotion.
  check (state <> 'complete' or health_check_passed is true),
  check ((health_check_passed is null) = (health_checked_at is null)),
  check ((state = 'blocked-version') = (blocked_reason_code is not null))
);

create index update_installations_applied_migration_idx
  on update_installations (applied_migration_version);

-- At most one owner per board. Said precisely, because "exactly one" is what the
-- board contract requires and this index cannot deliver it: a partial unique index
-- refuses a second `active-owner` row and is silent about a board that has none.
-- The other half is the creation transaction, which writes the `boards` row and its
-- owner `board_memberships` row together or writes neither -- planned as
-- `board-create-owner` in `conformance/p1140e/sql-race-plans-v1.json` -- and the
-- paired transfer, which demotes the outgoing owner and promotes the incoming one
-- inside the same `board-owner-transfer` boundary. A board owner therefore cannot
-- be created by an update, and the last owner cannot leave without a successor.
create unique index board_one_active_owner
  on board_memberships (board_id)
  where state = 'active-owner';

create index claims_account_received_idx on claims (account_id, received_at desc);
create index notifications_account_created_idx on notifications (account_id, created_at desc);

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
  state text not null check (state in ('absent','headless','starting','connected','daemon-unavailable','stale','exiting','crashed')),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null
);

-- The compatibility window, per interface and per update class.
--
-- This table previously held a copy of the twelve `update-lifecycle` states and
-- nothing else. It was a persistence-owner stub: the machine had to name a table, so
-- a table was created with the machine's own vocabulary in it, and the result was two
-- tables holding one aggregate's state with nothing saying which of the two won. A
-- policy has no update lifecycle. It is read by the lifecycle, which is why
-- `update_installations` is now the machine's only persistence owner.
--
-- What it holds instead is the thing the machine had no way to read. D-570 refuses a
-- client below a moving version floor with an upgrade prompt rather than degrading it
-- silently, and the floor was a sentence in a decision with no column anywhere.
-- `minimum_supported_release_version` is that floor, `floor_effective_at` is when it
-- moves, and `refusal_reason_code` pins the refusal to the one code the reason
-- registry declares for it -- so a floor cannot be enforced with a code that says
-- something else, and the reason a participant is shown cannot drift from the reason
-- the server acted on.
--
-- `max_deferral_seconds` is bounded below `deadline_seconds` because the operations
-- contract requires that competitive profiles cannot permanently disable a required
-- update, and a deferral as long as the deadline is that disabling written as a
-- number. An emergency security or integrity update admits no deferral at all.
create table update_policies (
  update_policy_id uuid primary key,
  update_class text not null check (update_class in ('emergency-security-integrity','required-compatibility','routine-product')),
  interface text not null check (interface in (
    'vibeproof-protocol','http-api','local-ipc','local-storage','server-schema','platform-profile')),
  minimum_supported_release_version text not null check (minimum_supported_release_version ~ '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'),
  floor_effective_at timestamptz not null,
  max_deferral_seconds integer not null check (max_deferral_seconds >= 0),
  deadline_seconds integer not null check (deadline_seconds > 0),
  refusal_reason_code text not null check (refusal_reason_code = 'CLIENT_VERSION_UNSUPPORTED'),
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  check (max_deferral_seconds < deadline_seconds),
  check (update_class <> 'emergency-security-integrity' or max_deferral_seconds = 0),
  unique (update_class, interface, floor_effective_at)
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

-- The short-lived revocable download grant. PF-028.
--
-- It held a subject, a revision and a creation time: no expiry, no revocation, and no
-- reference to the export it granted access to. "Short-lived" and "revocable" are the
-- two words `docs/privacy/PRIVACY_CONTRACT.md` uses about it, and the row could express
-- neither, so the only thing bounding a download link was that nobody had written the
-- code yet.
--
-- `expires_at` is `not null`, which is the shortness. A nullable expiry is an eternal
-- grant one omitted value away, and the table is where that is refused rather than in
-- the issuing worker.
--
-- Revocation and consumption are separate timestamps because they are separate facts:
-- a participant who revokes a link that was already used is telling the product
-- something different from one who revokes an unused link, and one column meaning
-- "over" would lose which of the two happened.
create table export_download_grants (
  export_download_grant_id uuid primary key,
  export_id uuid not null references exports(export_id),
  grant_digest bytea not null check (octet_length(grant_digest) = 32),
  revision integer not null default 1 check (revision > 0),
  issued_at timestamptz not null,
  expires_at timestamptz not null,
  revoked_at timestamptz,
  consumed_at timestamptz,
  created_at timestamptz not null,
  check (expires_at > issued_at),
  check (revoked_at is null or revoked_at >= issued_at),
  check (consumed_at is null or consumed_at >= issued_at)
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

-- The append-only record of what happened to one OAuth transaction. PF-006.
--
-- It carried `subject_id uuid not null` with no reference and `event_type text not null`
-- with no CHECK, so it was a table that could hold a row about anything and say
-- anything about it. `event_type` is now exactly the transition identifier set of the
-- `oauth-transaction` machine in `packages/schemas/state-machine-registry-v1.json`, and
-- `scripts/repository/validate_oauth_identity_contract.py` compares the two sets, so a
-- transition added to the machine with no way to record it fails rather than passing
-- unnoticed.
--
-- No column here carries a code, a redirect target, a token or a provider handle. The
-- ledger records that a transition happened and, when it failed, which registered
-- reason refused it.
create table oauth_authorization_events (
  oauth_authorization_event_id uuid primary key,
  oauth_transaction_id uuid not null references oauth_transactions(oauth_transaction_id),
  event_type text not null check (event_type in (
    'oauth-begin','oauth-callback','oauth-consume','oauth-expire','oauth-fail')),
  reason_code text,
  created_at timestamptz not null,
  check ((event_type = 'oauth-fail') = (reason_code is not null))
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
  -- Deliberately not a foreign key: trusted-client state outlives the device row an erasure deletes.
  device_id uuid not null,
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
  check (superseded_by_contribution_id <> contribution_id),
  -- D-263 composes a period total as the checked sum of additions minus the
  -- checked sum of retractions. That decomposition is only available if the two
  -- are distinguishable, and a signed column alone does not distinguish them:
  -- an addition of -5 and a retraction of -5 are the same row. The direction is
  -- the origin and the sign follows from it, in both directions.
  check ((origin = 'retraction') = (token_burn_delta < 0))
);

-- `score_contributions` is the append-only ledger the period figures are folded
-- from, and until PF-023 nothing stopped an update to it. A correction that
-- edits the contribution it corrects destroys the property the whole design
-- rests on: the accepted claim is immutable, and a correction appends an
-- inverse and a replacement rather than rewriting arithmetic that has already
-- been published.
--
-- Two columns are deliberately outside the refusal. `claim_id` is cleared by
-- `on delete set null` when an erasure deletes the claim -- which PostgreSQL
-- performs as an UPDATE on this row, so a blanket update trigger would make the
-- erasure path fail rather than the rewrite path. `superseded_by_contribution_id`
-- may be set once, from null, because that is the forward link a superseding
-- contribution installs; it may not then be changed or cleared, because
-- re-pointing it rewrites which row is current without appending anything.
-- The message carries no format placeholder on purpose. This file is executed as
-- one multi-statement string by the planning DDL check, and a percent sign in it
-- is one client library away from being read as a parameter marker; the detail
-- string concatenates instead and says the same thing.
create function score_contributions_refuse_rewrite() returns trigger
  language plpgsql as $refuse$
begin
  raise exception 'score_contributions is append-only'
    using errcode = 'restrict_violation',
          detail = tg_op || ' refused on contribution ' || old.contribution_id::text;
end;
$refuse$;

create trigger score_contributions_no_delete
  before delete on score_contributions
  for each row execute function score_contributions_refuse_rewrite();

create trigger score_contributions_no_rewrite
  before update on score_contributions
  for each row
  when (
    old.contribution_id is distinct from new.contribution_id
    or old.period_id is distinct from new.period_id
    or old.erasure_domain_id is distinct from new.erasure_domain_id
    or old.origin is distinct from new.origin
    or old.token_burn_delta is distinct from new.token_burn_delta
    or old.source_revision is distinct from new.source_revision
    or old.created_at is distinct from new.created_at
    or (
      old.superseded_by_contribution_id is not null
      and old.superseded_by_contribution_id is distinct from new.superseded_by_contribution_id
    )
  )
  execute function score_contributions_refuse_rewrite();

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
  -- Deliberately not a foreign key: an issued code outlives the issuer's erasure.
  issued_by_account_id uuid not null,
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
-- `plan_kind` is the discriminator this key was missing. The unique key was
-- `(platform_profile_id, release_set_id)`, which admits exactly one plan per profile
-- and release -- so the install plan and the uninstall plan for one build were the
-- same row, and a repair plan could not be recorded at all. The launch gates require
-- installation, update, rollback and uninstall evidence per exact tuple, and four
-- kinds of evidence cannot be produced from a table that holds one.
--
-- `orphan-cleanup` is why `release_set_id` is nullable. An orphan is by definition
-- what is left when the thing that installed it is gone: a service registration whose
-- binary was deleted, an IPC endpoint from a build that no longer resolves, a
-- keystore grant held by a version that was never uninstalled. Requiring the plan to
-- name a live release set made the one case the plan exists for the one case it could
-- not express. Every other kind names its release.
create table platform_install_plans (
  platform_install_plan_id uuid primary key,
  platform_profile_id text not null references platform_profiles(platform_profile_id),
  plan_kind text not null check (plan_kind in ('install','upgrade','repair','uninstall','orphan-cleanup')),
  release_set_id uuid references release_sets(release_set_id),
  requires_privileged_consent boolean not null default false,
  revision integer not null default 1 check (revision > 0),
  created_at timestamptz not null,
  unique (platform_profile_id, plan_kind, release_set_id),
  check ((release_set_id is null) = (plan_kind = 'orphan-cleanup'))
);

-- The eighteen operations: ten that change the machine forwards and the eight
-- reversals, which are operations in their own right once a plan may be an uninstall
-- or an orphan cleanup. Before `plan_kind` existed, the reversal names could appear
-- only in `reversal_operation`, so an uninstall sequence had no way to be written
-- down and the reversal column was doing duty as a plan nobody could order.
--
-- `reversal_operation` is populated only on a forward operation. A reversal has no
-- reversal: undoing an uninstall is an install, which is a different plan, and
-- pretending otherwise is how a cleanup acquires a rollback that reinstalls the thing
-- it was cleaning up.
create table platform_install_operations (
  platform_install_plan_id uuid not null references platform_install_plans(platform_install_plan_id),
  sequence integer not null check (sequence >= 1),
  operation text not null check (operation in (
    'verify-release-signature','place-binary','register-service','set-autostart',
    'grant-keystore-access','create-ipc-endpoint','register-privileged-supervisor',
    'start-service','verify-health','remove-previous-version',
    'unregister-service','clear-autostart','revoke-keystore-access','remove-ipc-endpoint',
    'remove-privileged-supervisor','stop-service','restore-previous-version','remove-binary')),
  irreversible boolean not null default false,
  reversal_operation text check (reversal_operation in (
    'unregister-service','clear-autostart','revoke-keystore-access','remove-ipc-endpoint',
    'remove-privileged-supervisor','stop-service','restore-previous-version','remove-binary')),
  primary key (platform_install_plan_id, sequence),
  -- An operation names the reversal a rollback runs, or declares that it has
  -- none — because it changes nothing, as a verification does, or because its
  -- effect cannot be undone. A rollback that discovers the answer at run time
  -- is D-074's failure mode rather than its contract.
  check (irreversible = (reversal_operation is null)),
  -- A reversal is itself irreversible within its plan.
  check (operation not in (
    'unregister-service','clear-autostart','revoke-keystore-access','remove-ipc-endpoint',
    'remove-privileged-supervisor','stop-service','restore-previous-version','remove-binary')
    or irreversible)
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
-- `predecessor_version` is what makes this a chain rather than a set.
-- migration-chain-v1.schema.json has always said that "a chain with a gap is not a
-- chain", and nothing read that sentence: the steps sat in a JSON array, array order
-- is a property of the file rather than of the record, and the table held versions
-- with no edge between them at all. Two migrations could each claim to follow the
-- baseline, or none could, and the ordered chain the update policy has to walk was a
-- convention nobody could check.
--
-- Three constraints make it linear at write time. The predecessor is a real
-- migration; it sorts before its successor, so a step cannot follow one that comes
-- after it; and `unique (interface, predecessor_version)` refuses a fork, because two
-- steps sharing one predecessor are a branch and not a chain. The partial unique
-- index below refuses a second root: NULL is distinct from NULL in a unique
-- constraint, so without it "no predecessor" was the one value any number of rows
-- could hold.
create table storage_migrations (
  storage_migration_id uuid primary key,
  version text not null unique references schema_migrations(version),
  predecessor_version text references schema_migrations(version),
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
  check (rollback_class <> 'binary-reversible' or down_sql_present),
  check (predecessor_version is null or predecessor_version < version),
  unique (interface, predecessor_version)
);

-- One chain per interface, so exactly one step per interface has no predecessor.
create unique index storage_migrations_chain_root_idx
  on storage_migrations (interface)
  where predecessor_version is null;

-- The chain is walked backwards as often as forwards, and `unique (interface,
-- predecessor_version)` leads on the interface, so it supports no lookup by
-- predecessor alone.
create index storage_migrations_predecessor_idx
  on storage_migrations (predecessor_version);

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
-- The erasure path in particular deletes from `accounts`, which thirty-one
-- tables reference.
--
-- Two rules, both enforced by `validate_index_coverage` in
-- `scripts/repository/validate_planning_artifacts.py` rather than by this
-- comment:
--
--   1. every foreign key's referencing columns are the leading columns of a
--      total index, primary key or unique constraint on the referencing table.
--      A *partial* index does not satisfy it: PostgreSQL's referential check on
--      a parent delete scans the child for any matching row, including the rows
--      the predicate excludes;
--   2. every index that supports no foreign key names the query it serves, in
--      the access-path table of
--      `docs/architecture/LEADERBOARD_STORAGE_AND_RANKING.md`. An index that
--      names no query cannot be shown to be wrong, and cannot be dropped by
--      anyone who did not write it.
--
-- Deliberately not stated: a count. Eighteen foreign keys were unindexed while
-- this file held a hundred and thirty-two indexes and the sentence above claimed
-- otherwise, because a total goes up when a redundant index is added and down
-- when a wrong one is removed. Coverage is the signal; the total is not one.
--
-- Each is created with CONCURRENTLY in the migration that introduces it, which
-- is one of the reasons D-097 selected a migration tool with a no-transaction
-- directive; this contract states the target shape rather than the migration
-- text.
-- ---------------------------------------------------------------------------

-- Foreign-key referencing side: identity and session.
create index linked_identities_account_idx on linked_identities (account_id);
-- The self-reference. A superseded identity row is read from its successor, and
-- until PF-020 the reverse was the only direction with an index.
create index linked_identities_superseded_idx on linked_identities (superseded_by_identity_id);
create index web_sessions_account_idx on web_sessions (account_id);
-- `token_family_id` carries no foreign key here; the index is the revoke-family path.
create index web_sessions_family_idx on web_sessions (token_family_id);
create index recovery_codes_account_idx on recovery_codes (account_id);
create index optional_authenticators_account_idx on optional_authenticators (account_id);
create index session_families_account_idx on session_families (account_id);
create index native_sessions_family_idx on native_sessions (token_family_id);
create index native_sessions_device_idx on native_sessions (device_id);

-- Foreign-key referencing side: the OAuth transaction.
--
-- Five references and no index on any of them. `oauth_transactions_live_link_idx`
-- covers `initiating_account_id`, but only `where state in
-- ('created','redirected','callback-received')`; a delete on `accounts` has to
-- find consumed, expired and failed transactions too, and a partial index cannot
-- be used to prove their absence.
create index oauth_transactions_initiating_account_idx on oauth_transactions (initiating_account_id);
create index oauth_transactions_initiating_session_idx on oauth_transactions (initiating_web_session_id);
create index oauth_transactions_resulting_account_idx on oauth_transactions (resulting_account_id);
create index oauth_transactions_resulting_session_idx on oauth_transactions (resulting_session_id);
create index oauth_transactions_resulting_identity_idx on oauth_transactions (resulting_identity_id);
create index oauth_authorization_events_transaction_idx
  on oauth_authorization_events (oauth_transaction_id);

-- Foreign-key referencing side: device and lineage.
create index devices_account_idx on devices (account_id);
create index device_keys_device_idx on device_keys (device_id);
create index device_enrollment_grants_account_idx on device_enrollment_grants (account_id);
create index adapter_installations_device_idx on adapter_installations (device_id);
create index device_lineages_account_idx on device_lineages (account_id);
create index device_key_events_device_idx on device_key_events (device_id, occurred_at desc);
-- The lineage ordering is the one a rotation audit and a fork case both read.
create index device_key_events_lineage_idx on device_key_events (lineage_id, occurred_at desc);
create index checkpoint_receipts_device_idx
  on checkpoint_receipts (device_id, accepted_through_claim_sequence desc);

-- Foreign-key referencing side: claims and verification.
create index claim_challenges_account_idx on claim_challenges (account_id);
create index claim_challenges_device_idx on claim_challenges (device_id);
-- D-592 rekeyed the sequence onto the lineage; the challenge acquired the lineage
-- reference in the same change and did not acquire its index.
create index claim_challenges_lineage_idx on claim_challenges (lineage_id);
-- The expected checkpoint a challenge was issued against. Nullable, because a lineage
-- that has never been acknowledged has no receipt to expect.
create index claim_challenges_expected_checkpoint_idx on claim_challenges (expected_checkpoint_receipt_id);
create index claim_batches_challenge_idx on claim_batches (challenge_id);
create index claim_batches_account_idx on claim_batches (account_id);
create index claim_batches_lineage_idx on claim_batches (lineage_id);
create index claims_device_idx on claims (device_id);
create index claims_challenge_idx on claims (challenge_id);
-- The composite foreign key that carries the no-partial-acceptance rule. `unique
-- (batch_id, batch_index)` leads on `batch_id` and does not cover `(batch_id,
-- batch_outcome)`, so the constraint would have no index behind it on the referencing
-- side.
create index claims_batch_outcome_idx on claims (batch_id, batch_outcome);
create index claim_rejections_batch_outcome_idx on claim_rejections (batch_id, batch_outcome);
create index claim_corrections_claim_idx on claim_corrections (claim_id);
create index claim_corrections_replacement_idx on claim_corrections (replacement_claim_id);
create index quarantines_account_idx on quarantines (account_id);
create index quarantines_device_idx on quarantines (device_id);
create index quarantines_claim_idx on quarantines (claim_id);
create index evidence_assessments_claim_idx on evidence_assessments (claim_id);
create index verifier_appraisals_claim_idx on verifier_appraisals (claim_id);
-- One appraisal is current per claim. Without this a re-evaluation could leave two rows
-- neither of which names the other as its successor, and "the claim's appraisal" would be
-- whichever the reader's ordering happened to surface. The partial predicate is what makes
-- the superseded history unbounded and the current row unique at the same time.
create unique index verifier_appraisals_current_per_claim_idx
  on verifier_appraisals (claim_id)
  where superseded_by_appraisal_id is null;
-- Both directions of the supersession chain are walked: forward to find what replaced an
-- appraisal a participant is appealing, backward to rebuild the history that produced the
-- current one. Total rather than partial, because an unindexed self-referencing foreign key
-- makes every delete of a superseded row scan the table.
create index verifier_appraisals_supersedes_idx on verifier_appraisals (supersedes_appraisal_id);
create index verifier_appraisals_superseded_by_idx on verifier_appraisals (superseded_by_appraisal_id);
create index cost_interpretations_claim_idx on cost_interpretations (claim_id);
create index cost_interpretations_dataset_idx on cost_interpretations (pricing_dataset_id);

-- Moderation and appeal.
--
-- `moderation_cases.account_id` and `appeals.account_id` are deliberately not
-- foreign keys -- both survive erasure unlinked -- so these two are documented
-- query paths rather than referential ones. The heading used to say otherwise,
-- which is how a reader would have concluded the delete on `accounts` was
-- covered here.
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
create index ranking_corrections_view_idx
  on ranking_corrections (ranking_view_id, period_id, erasure_domain_id);
create index ranking_corrections_period_idx on ranking_corrections (period_id);
create index ranking_definitions_period_idx on ranking_definitions (period_id);
create index ranking_views_definition_idx on ranking_views (ranking_definition_id);
create index ranking_views_board_idx on ranking_views (board_id);
create index periods_season_idx on periods (season_id);
create index ranking_entries_domain_idx on ranking_entries (erasure_domain_id);
create index score_contributions_period_domain_idx on score_contributions (period_id, erasure_domain_id);
-- The domain alone. `score_contributions_period_domain_idx` leads with the period,
-- so enumerating one participant's contributions across every period -- which is
-- what an erasure does before it destroys the key -- could not use it.
create index score_contributions_domain_idx on score_contributions (erasure_domain_id);
create index score_contributions_claim_idx on score_contributions (claim_id);
create index score_contributions_superseded_idx on score_contributions (superseded_by_contribution_id);
create index ranking_movement_events_subject_idx on ranking_movement_events (subject_erasure_domain_id, created_at desc);
create index ranking_movement_events_counterpart_idx on ranking_movement_events (counterpart_erasure_domain_id);
create index ranking_movement_events_prior_idx on ranking_movement_events (ranking_view_id, prior_generation);
create index ranking_movement_events_current_idx on ranking_movement_events (ranking_view_id, current_generation);
create index ranking_projection_generations_supersede_idx
  on ranking_projection_generations (ranking_view_id, superseded_by_generation);

-- Exactly one active generation per view. The ranking-projection machine calls
-- its promotion transition `atomic-promote` and the storage contract calls a
-- generation the current standing; without this index both were words. Two
-- workers could each promote and leave two rows in `active`, after which "the
-- current standing" is whichever one a reader's plan happened to find, and the
-- two readers who found different ones both saw a real row. Partial, because
-- `building`, `validating`, `superseded` and `failed` are all many-per-view.
create unique index ranking_projection_generations_active_idx
  on ranking_projection_generations (ranking_view_id)
  where state = 'active';

-- Referencing side of the composite key period_scores pins its figures to.
create index period_scores_generation_idx
  on period_scores (ranking_view_id, generation);

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
create index board_invites_invited_idx on board_invites (invited_account_id);
create index board_invites_inviter_idx on board_invites (invited_by_account_id);
create index presence_leases_device_idx on presence_leases (device_id);
create index notifications_actor_idx on notifications (actor_account_id);
create index notification_events_actor_idx on notification_events (actor_account_id);
-- `social_integrity_events.actor_account_id` carries no foreign key: the event
-- outlives the actor. The index is a documented query path.
create index social_integrity_events_actor_idx on social_integrity_events (actor_account_id);
-- `social_integrity_events_aggregate_idx on (aggregate_id, aggregate_revision)`
-- was here and is gone. `unique (aggregate_id, aggregate_revision)` on the table
-- is implemented as a btree index over the same two columns in the same order, so
-- the second one served no query the first did not and cost a write on every
-- insert. It survived because nothing compared an index against the constraints
-- around it.

-- Foreign-key referencing side: admission.
--
-- `invite_redemptions.account_id` and `invite_redemptions.invite_code_id` need
-- no index here: the first is unique and the second is the primary key, so both
-- already carry one, and those two constraints are also the atomicity control.
create index invite_codes_issuer_idx on invite_codes (issued_by_account_id);

-- Foreign-key referencing side: rights, erasure, release.
create index exports_account_idx on exports (account_id);
create index export_download_grants_export_idx on export_download_grants (export_id);
create index deletion_jobs_account_idx on deletion_jobs (account_id);
create index local_deletion_commands_job_idx on local_deletion_commands (deletion_job_id);
create index local_deletion_commands_device_idx on local_deletion_commands (device_id);
create index local_deletion_receipts_device_idx on local_deletion_receipts (device_id);
create index erasure_records_job_idx on erasure_records (deletion_job_id);
create index deletion_tombstones_erasure_record_idx on deletion_tombstones (erasure_record_id);
create index erasure_domain_links_absorbed_idx on erasure_domain_links (absorbed_erasure_domain_id);
create index release_sets_root_idx on release_sets (tuf_root_version);
create index tuf_metadata_root_idx on tuf_metadata (root_version);
create index release_targets_profile_idx on release_targets (platform_profile_id);
create index platform_certifications_profile_idx on platform_certifications (platform_profile_id);
create index platform_certifications_release_idx on platform_certifications (release_set_id);
create index platform_install_plans_release_idx on platform_install_plans (release_set_id);
create index compatibility_edges_release_idx on compatibility_edges (release_set_id);
-- Certification. `source_certifications_active_idx` is unique `where state =
-- 'active'`, so it covers neither of these: retiring a platform profile has to
-- see the candidate, testing, degraded, suspended, expired, superseded and
-- retired rows as well.
create index source_certifications_profile_idx on source_certifications (platform_profile_id);
create index source_certifications_superseded_idx
  on source_certifications (superseded_by_source_certification_id);
create index certification_results_certification_idx
  on certification_results (source_certification_id);
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
-- The second sweep. `expires_at` finds the rows whose response bytes are due to be
-- discarded; `retain_until` finds the rows themselves, days later. One index over
-- one column cannot drive two sweeps with different dates and different effects.
create index idempotency_records_retention_idx on idempotency_records (retain_until);
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
-- Total, beside the partial `ranked_identities_account_live_idx`. That one is
-- unique `where retired_at is null` and enforces one live identity per account;
-- it cannot answer the delete on `accounts`, which has to see the retired rows a
-- consolidation survivor keeps around precisely so they can be named.
create index ranked_identities_account_idx on ranked_identities (account_id);
create index identity_investigations_identity_idx on identity_investigations (ranked_identity_id);
-- Same shape: `consolidation_cases_absorbed_idx` is unique over five open states,
-- and `applied`, `rejected`, `reversed` and `expired` rows are outside it.
create index consolidation_cases_absorbed_all_idx
  on consolidation_cases (absorbed_ranked_identity_id);
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
