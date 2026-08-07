// Exploratory prototype, quarantined under P-1140F-1. This file is not the
// VibeProof v1 protocol.
//
// It decodes an eleven-field shadow payload predating the normative schema. The
// normative authority is packages/schemas/vibeproof-claim-v1.cddl, owned by
// docs/architecture/VIBEPROOF_V1_PROTOCOL.md; where the two disagree the CDDL is
// correct and this file is the defect.
//
// Known incompatibilities with the normative schema:
//   - expects unsigned 11-field payload
//   - does not verify COSE Sign1
//
// Prohibited uses:
//   - claim-ingestion
//   - ranking
//   - normative-conformance
//   - support-claim
//
// Its evidence ceiling is cross-language-parity: it agrees with
// crates/vibeproof-core, which consumes the same shadow schema. Two implementations
// agreeing about the wrong authority is not conformance.
//
// conformance/p1140f/artifact-authority-v1.json is the authority for this file's
// status, and scripts/repository/validate_artifact_quarantine.py checks this notice
// against it. Edit the record, not this comment.

package main

const maximumClaimBytes = 1024

func verifyCanonicalFixture(input []byte) bool {
	if len(input) > maximumClaimBytes {
		return false
	}
	decoder := cborFixtureDecoder{input: input}
	if !decoder.expectMap(11) || !decoder.fieldText(1, "v1") || !decoder.fieldBytes(2, 16) || !decoder.fieldBytes(3, 16) || !decoder.fieldBytes(4, 16) || !decoder.fieldBytes(5, 32) || !decoder.fieldUnsigned(6) || !decoder.fieldNonzeroUnsigned(7) || !decoder.fieldBytes(8, 32) || !decoder.fieldUnsigned(9) || !decoder.fieldTokenTotals(10) || !decoder.fieldEnum(11, 4) {
		return false
	}
	return decoder.offset == len(input)
}

type cborFixtureDecoder struct {
	input  []byte
	offset int
}

func (decoder *cborFixtureDecoder) fieldText(key uint64, expected string) bool {
	return decoder.fieldKey(key) && decoder.text() == expected
}

func (decoder *cborFixtureDecoder) fieldBytes(key uint64, length uint64) bool {
	return decoder.fieldKey(key) && decoder.bytes(2, length)
}

func (decoder *cborFixtureDecoder) fieldUnsigned(key uint64) bool {
	if !decoder.fieldKey(key) {
		return false
	}
	_, ok := decoder.head(0)
	return ok
}

func (decoder *cborFixtureDecoder) fieldNonzeroUnsigned(key uint64) bool {
	if !decoder.fieldKey(key) {
		return false
	}
	value, ok := decoder.head(0)
	return ok && value != 0
}

func (decoder *cborFixtureDecoder) fieldEnum(key uint64, maximum uint64) bool {
	if !decoder.fieldKey(key) {
		return false
	}
	value, ok := decoder.head(0)
	return ok && value <= maximum
}

func (decoder *cborFixtureDecoder) fieldTokenTotals(key uint64) bool {
	return decoder.fieldKey(key) && decoder.expectMap(3) && decoder.fieldUnsigned(1) && decoder.fieldUnsigned(2) && decoder.fieldUnsigned(3)
}

func (decoder *cborFixtureDecoder) fieldKey(key uint64) bool {
	value, ok := decoder.head(0)
	return ok && value == key
}

func (decoder *cborFixtureDecoder) expectMap(size uint64) bool {
	value, ok := decoder.head(5)
	return ok && value == size
}

func (decoder *cborFixtureDecoder) text() string {
	length, ok := decoder.head(3)
	if !ok || length > uint64(len(decoder.input)-decoder.offset) {
		return ""
	}
	start := decoder.offset
	decoder.offset += int(length)
	return string(decoder.input[start:decoder.offset])
}

func (decoder *cborFixtureDecoder) bytes(major uint8, expectedLength uint64) bool {
	length, ok := decoder.head(major)
	if !ok || length != expectedLength || length > uint64(len(decoder.input)-decoder.offset) {
		return false
	}
	decoder.offset += int(length)
	return true
}

func (decoder *cborFixtureDecoder) head(expectedMajor uint8) (uint64, bool) {
	first, ok := decoder.take()
	if !ok || first>>5 != expectedMajor {
		return 0, false
	}
	additional := first & 0x1f
	switch additional {
	case 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23:
		return uint64(additional), true
	case 24:
		value, ok := decoder.take()
		return uint64(value), ok && value >= 24
	case 25:
		return decoder.readUnsigned(2, 256)
	case 26:
		return decoder.readUnsigned(4, 65536)
	case 27:
		return decoder.readUnsigned(8, 4294967296)
	default:
		return 0, false
	}
}

func (decoder *cborFixtureDecoder) readUnsigned(length int, minimum uint64) (uint64, bool) {
	if len(decoder.input)-decoder.offset < length {
		return 0, false
	}
	var value uint64
	for index := 0; index < length; index++ {
		value = value<<8 | uint64(decoder.input[decoder.offset])
		decoder.offset++
	}
	return value, value >= minimum
}

func (decoder *cborFixtureDecoder) take() (uint8, bool) {
	if decoder.offset == len(decoder.input) {
		return 0, false
	}
	value := decoder.input[decoder.offset]
	decoder.offset++
	return value, true
}
