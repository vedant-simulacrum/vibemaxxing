# Build Plan

## Phase 0 — repository, contracts, and measurable budgets

- Establish monorepo
- Configure CI, formatting, linting, testing
- Add ADR process
- Freeze privacy contract
- Freeze initial claim schema
- Define adapter capability manifest
- Create realistic fixture dataset
- Pin Rust 2024, Go 1.26, Node, and package-manager versions
- Add Protobuf + Buf internal contract workspace
- Establish performance budgets and benchmark baselines
- Add cross-language golden claim fixtures

## Phase 1 — complete UI shell

- Brand tokens and wordmark
- Global leaderboard
- Friends and presence
- Public profile
- Private boards
- Settings/privacy/deletion
- Mobile compositions
- Complete state coverage

Use typed mock services first, then replace with production APIs.

## Phase 2 — Go server vertical slice

- Authentication: GitHub OAuth + passkeys
- User/profile/social graph
- Board membership and privacy
- Go claim ingestion and verification orchestration
- PostgreSQL append-only accepted-claim ledger and transactional outbox
- Go ranking materialization worker
- Minute-scale updates
- SSE presence and overtakes; introduce WebSockets only if bidirectional semantics are proven

## Phase 3 — portable VibeProof prototype

- npm bootstrapper
- Native Rust collector
- Device registration
- ACP/OTel/PTY adapters
- Claude Code and Codex reference adapters
- Fixed outbound schema
- Local audit ledger
- Signed claims and server receipts

## Phase 4 — privacy and SLM

- Networkless transcript analyzer
- Secret redaction
- Micro verifier
- Challenge verifier
- Structured risk result
- Prompt-injection corpus
- Packet-capture privacy tests

## Phase 5 — broad platform/agent support

- Cursor
- Droid
- Copilot
- OpenCode
- Gemini/Antigravity
- Cline
- Aider
- Goose
- OpenHands
- Kimi
- Qwen
- Kiro
- Roo
- Mistral Vibe
- OpenClaw
- WSL/containers/Codespaces/CI

## Phase 6 — hardening

- macOS Endpoint Security
- Windows process/file/network evidence
- Linux fanotify/eBPF/IMA
- Optional device attestation
- External security review
- Reproducible builds and signed releases

## Phase 7 — public protocol

- Publish VibeProof specification
- Publish adapter SDK
- Publish conformance suite
- Publish threat model
- Publish compatibility registry
