# Privacy Contract

## Never transmitted

- Prompts
- Responses
- Source code
- Diffs
- Commands
- Tool arguments/results
- File names or paths
- Project/repository names
- Session titles
- Emails
- API keys
- Cookies or credentials
- Raw provider request identifiers
- Embeddings
- Topics
- Summaries
- Coaching findings
- Transcript hashes

## Allowed outbound data

Only bounded fields such as:

- Schema/protocol version
- Source and model enums
- Adapter/source versions
- Coarse time bucket
- Token categories
- Event counts or bands
- Capture/environment state
- Duplicate/replay state
- Collector build digest
- Device sequence
- Previous-claim hash
- Server challenge
- Device signature
- Optional attestation evidence

No arbitrary text fields.

## Exact timestamps

- Exact timestamps remain local.
- Server may receive minute/hour-scale claim windows needed for live ranking and replay defense.
- Public UI shows day-level history by default.
- Presence is a separate opt-out signal.

## Local outbound audit ledger

Maintain an encrypted local audit ledger for 90 days by default.

It records:

- Every sent claim
- Every field sent
- Receipt status
- Server receipt
- Local contributing session reference

It contains no transcript content and can be exported or deleted.
