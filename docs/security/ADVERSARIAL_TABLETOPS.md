# Adversarial Tabletop Scenarios

Status: normative planning evidence
Updated: 2026-07-19

Each scenario defines authoritative transitions and required tests.

## T-01 Modified adapter fabricates usage

Detect unsupported binary/version or invariant violation; downgrade or quarantine affected claims; preserve raw local evidence; issue stable reason code; never alter unrelated accepted claims. Test forged categories, impossible totals, source mismatch, and adapter-signature substitution.

## T-02 Device state cloned or VM snapshot restored

Server observes sequence/hash-chain fork or reused device state; quarantine forked device claims; require device re-enrollment; preserve appeal path. Test simultaneous clones and delayed snapshot replay.

## T-03 Concurrent duplicate submission

Unique claim ID and device-sequence constraints make one transaction authoritative; all others return idempotent accepted response without score increase.

## T-04 Sync crashes after server acceptance

Local item remains pending until acknowledgement; retry returns idempotent acceptance; local queue advances only after authenticated acknowledgement.

## T-05 GitHub identity lost or compromised

Existing sessions may be revoked; linked X identity or optional stronger factor may recover after cooling-off and notifications. A single newly compromised provider cannot silently replace all identities.

## T-06 Two existing accounts are linked accidentally

No automatic merge. Enter reviewed merge flow, display consequences, preserve both histories, select canonical account, revoke old sessions, and create reversible audit record before final deletion window.

## T-07 Pricing dataset error

Publish immutable corrected dataset; recompute estimates as explicit correction version; never rewrite usage facts; show affected period and provenance.

## T-08 Season closes with offline claims

Claims observed before cutoff may enter during configured grace period; after grace they remain analytics-only for that closed season unless appeal proves service-side outage. Season results become immutable after correction window.

## T-09 Aggregates corrupted

Stop affected reads or mark stale; rebuild deterministically from accepted ledger; compare checksums; atomically swap rebuilt state; investigate root cause.

## T-10 Wrongful quarantine

Freeze competitive effect, not data access; expose reason family; allow appeal; independent reviewer may restore claims and trigger deterministic aggregate rebuild; moderator actions remain audited.

## T-11 Compromised update metadata

TUF threshold, expiry, rollback and freeze checks reject metadata; retain current version; notify safely; rotate affected keys according to role separation.

## T-12 Collector disk full or database corruption

Stop accepting new local events before violating durability; surface clear local status; never fabricate continuity; recover from last verified checkpoint or re-enroll device if chain continuity is lost.

## T-13 Deletion during appeal

User may delete immediately; deletion cancels ranking participation and removes content according to policy. Minimal legally required case metadata may be retained separately with strict access and expiry; no score is preserved.

## T-14 Duplicate nested-agent observation

Source reconciliation uses stable request/session ancestry and adapter precedence; one authoritative observation counts; conflicting observations quarantine rather than sum.

## T-15 Genuine intentionally wasteful usage

Accept when live, authentic, policy-compliant and nonduplicated. Do not judge productivity or purpose. Apply ordinary rate, integrity and provider constraints only.

## T-16 Presence farming

Presence requires qualifying live heartbeat tied to accepted session evidence. Expire on missed heartbeats; repeated synthetic heartbeats trigger downgrade or review without changing historical token totals.

## T-17 Sybil and colluding accounts

Rate-limit account/device creation, analyze graph/cohort patterns, restrict board effects and review suspicious clusters. Do not require government ID by default. Appeals remain available.

## T-18 Privacy exfiltration disguised as integrity

Any proposed field not on the outbound allowlist is rejected at schema and process boundary. Canary tests and packet capture must prove absence; integrity value never overrides privacy contract.

## Closure rule

Every tabletop must become an executable fixture or test campaign during implementation. A launch-blocking scenario cannot be waived without an accepted residual-risk decision and named owner.