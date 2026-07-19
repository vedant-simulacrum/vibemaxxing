# Threat Model

Updated: 2026-07-19
Status: normative planning contract

## Security objective

Make ordinary manipulation substantially harder than editing local logs while never uploading transcript content. Controls provide bounded, inspectable assurance; they do not claim mathematical cheat-proofness on an unrestricted user-controlled machine.

## In-scope attackers

- user with full access to their own files and processes;
- user calling ingestion endpoints directly;
- user replaying valid claims, events, challenges or commitments;
- user copying another person's records or device state;
- user modifying collector, adapter, proxy or verifier output;
- user restoring cloned, migrated or rolled-back environment state;
- user running modified adapters, agents, gateways or local models;
- user manipulating timestamps, model/source identifiers, parent-child relationships or retry semantics;
- colluding users;
- compromised OAuth account, provider token, device key or trusted session;
- supply-chain attacker;
- malicious transcript or source metadata targeting local parsers or an optional SLM;
- malicious moderator, operator or support actor exceeding authorization.

## Fundamental limitations

On an unrestricted machine controlled by the contestant, local evidence cannot universally prove provider origin, truthful source output, non-cloning or complete execution history without external issuer evidence, controlled execution, hardware-backed attestation across the relevant path or another independently verifiable binding.

A server challenge proves submission freshness, not that an offline event existed before the challenge. A device signature proves possession or use of the enrolled key, not that the signed token counts are true. A hash chain detects many forks after conflicting successors become visible; it does not by itself prevent snapshot rollback or exported-key cloning.

Public claims and evidence profiles preserve these distinctions.

## Cheating definition

Cheating includes:

- editing token fields or category semantics;
- fabricating or copying records;
- replaying sessions, events, commitments or claims;
- backdating activity or fabricating offline chronology;
- double-counting host/guest, IDE/CLI, proxy/provider or orchestrator/subagent observations;
- modifying collector/verifier behavior;
- simulating fake source events;
- misrepresenting source, model, version, mode, platform, evidence or key class;
- cloning keys or device state to create competing chains;
- collusive account/device sharing intended to manipulate rankings.

Genuine but pointless activity is not cheating when authentic and non-duplicated.

## Deterministic control layers

1. **Privacy boundary** — fixed outbound schema, forbidden-field canaries, process separation and telemetry allowlists.
2. **Identity/session controls** — provider-subject binding, OAuth transaction binding, session rotation, reauthentication and recovery controls.
3. **Source compatibility** — exact adapter/runtime/version probes, evidence ceilings and fail-closed unknown revisions.
4. **Accounting** — versioned provider/API profiles, checked arithmetic, deterministic reconciliation, parent-child inclusion and explicit corrections.
5. **Replay/continuity** — event IDs, duplicate domains, idempotency, server challenges, device sequences, previous hashes and pre-challenge commitments.
6. **Clone/rollback handling** — key classes, server checkpoints, clone/restore fixtures, fork quarantine and explicit new-device recovery.
7. **Server integrity** — append-only claim ledger, transactional duplicate rejection, idempotent aggregates, authorization and privacy-safe audit events.
8. **Progressive response** — downgrade, quarantine, rate limit, stronger-check request, human review and appeal.

Named assurance classes and public profiles are normative in `docs/security/EVIDENCE_AND_ATTESTATION_PROFILES.md`. Platform privilege and key assumptions are normative in `docs/architecture/PLATFORM_KEY_AND_PRIVILEGE_MATRIX.md`.

## Device cloning and replay cases

The adversarial registry includes at least:

- exact claim replay;
- conflicting claim with reused sequence;
- event ID reuse across claims or accounts;
- challenge reuse or cross-device challenge substitution;
- commitment reuse and commitment-chain fork;
- concurrent successors from a cloned key/state;
- filesystem, home-directory, credential-store and VM snapshot rollback;
- restored state behind the server checkpoint;
- copied K3/K4 key material;
- provider request-ID reuse and local fingerprint collision;
- duplicated nested-agent and proxy/provider observations.

A control that only detects a conflict after both branches submit is documented as detection, not prevention.

## OAuth and account integrity

OAuth identity is account access, not activity evidence. Threats include login CSRF, provider mix-up, account pre-hijacking, link substitution, stolen refresh tokens, revoked installations, provider-account compromise and recovery abuse. Controls are owned by `AUTHENTICATION_AND_RECOVERY.md` and do not increase VibeProof source assurance.

## SLM boundary and staging

An SLM is optional residual-risk analysis, not a source of truth. Initial launch does not depend on an SLM unless a measured bakeoff shows incremental value over deterministic and classical baselines using a frozen privacy-safe feature schema.

Any SLM has:

- no network, tools, shell, MCP, plugins or autonomous loop;
- bounded structured input with no transcript, code, path, repository, filename or tool-body content;
- constrained structured output;
- signed weights and pinned runtime;
- deterministic policy engine above it;
- versioned feature schema, calibration set and false-positive thresholds;
- no authority to alter totals, award a stronger evidence profile or permanently ban a user.

It may contribute a bounded risk signal, quarantine recommendation or stronger-check request. High-impact outcomes require deterministic reasons and an appealable human-controlled policy path.
