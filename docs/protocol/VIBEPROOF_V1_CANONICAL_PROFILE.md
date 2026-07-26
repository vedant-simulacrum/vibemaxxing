# VibeProof v1 Canonical Profile

VibeProof v1 public claims use only the fixed safe fields in
`protocol/vibeproof-v1.cddl`: version, fixed-length claim/device/key identifiers,
challenge, issued timestamp, sequence, previous-claim hash, accounting version,
token totals, and evidence class. No arbitrary text, provider payload, content,
path, prompt, response, or transcript field is representable.

The Rust reference implements a deliberately small CBOR profile: the exact fixed
11-key outer map and 3-key token-total map, definite byte/text strings, canonical
shortest integer encodings, ascending integer map keys, and a 1024-byte input limit.
It rejects duplicate or unknown keys, indefinite lengths, tags, floats,
noncanonical integers, truncated or malformed lengths, trailing bytes, oversized
input, wrong map cardinality, unordered keys, missing required keys, invalid
versions, zero sequences, invalid evidence enums, malformed nested token totals,
and fields outside the CDDL shape. Golden vectors carry an explicit `accept`
outcome and are shared with Go. Go validates only this restricted canonical profile
against those fixtures; Rust remains the semantic authority.

COSE signing and verification are intentionally out of scope for this foundation.
No key, signature, or COSE library has been selected. `protocol-library-bakeoff`
remains not applicable pending malformed-vector, differential decode, fuzz,
resource-limit, throughput, and maintenance evidence.

## Rollback

If a canonical-profile defect is found, stop accepting the affected protocol version,
retain claims for investigation, and release a versioned replacement with new vectors.
Never reinterpret old bytes under a changed profile. Accounting or pricing fixture
defects quarantine affected totals until deterministic replay against a reviewed
replacement fixture is complete.
