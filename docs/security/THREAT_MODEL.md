# Threat Model

## Security objective

Make ordinary manipulation substantially harder than editing local logs, while never uploading transcript content.

## In-scope attackers

- User with full access to their own files
- User calling ingestion endpoints directly
- User replaying valid claims
- User copying another person's records
- User modifying collector output
- User restoring cloned or rolled-back environment state
- User running modified adapters or models
- User manipulating timestamps and model/source identifiers
- Colluding users
- Compromised account or device credential
- Supply-chain attacker
- Malicious transcript content targeting the local SLM

## Fundamental limitation

On an unrestricted machine controlled by the contestant, local evidence cannot universally prove provider origin without external issuer evidence, controlled execution, hardware-backed attestation across the full path, or privacy-preserving authenticated transport proofs.

Do not market the system as mathematically cheat-proof.

## Cheating definition

Cheating includes:

- Editing token fields
- Fabricating records
- Copying records
- Replaying sessions or claims
- Backdating activity
- Double-counting host and guest
- Modifying collector/verifier behavior
- Simulating fake source events
- Misrepresenting source/model/configuration

Genuine but pointless activity is not cheating.

## Core controls

- Live observation before activity begins
- Historical imports excluded from competitive ranking
- Server challenges
- Monotonic device sequences
- Previous-claim hash chains
- Idempotency keys
- Transactional duplicate rejection
- Source-version conformance
- Signed official builds
- Optional source-process observation
- Optional device/OS attestation
- Fixed outbound schema
- Append-only server ledger
- SLM as a risk signal only
- Human review and appeals for high-impact decisions

## SLM safety

The transcript is adversarial input.

The anti-cheat SLM must have:

- No network
- No tools
- No shell
- No MCP
- No plugins
- No autonomous loop
- Bounded input
- Constrained structured output
- Signed weights
- Pinned runtime
- Deterministic policy engine above it

The SLM may quarantine or request a stronger check. It may not permanently ban a user by itself.
