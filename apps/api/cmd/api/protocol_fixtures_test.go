package main

import (
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

type protocolFixtureCorpus struct {
	Valid   []protocolFixtureVector `json:"valid"`
	Invalid []protocolFixtureVector `json:"invalid"`
}

type protocolFixtureVector struct {
	BytesHex string `json:"bytes_hex"`
	Accept   bool   `json:"accept"`
}

func TestProtocolFixtures_match_Rust_acceptance_outcomes(t *testing.T) {
	// Given
	path := filepath.Join("..", "..", "..", "..", "conformance", "protocol", "vibeproof-v1-vectors.json")
	bytes, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read shared fixture: %v", err)
	}
	var corpus protocolFixtureCorpus
	if err := json.Unmarshal(bytes, &corpus); err != nil {
		t.Fatalf("decode shared fixture: %v", err)
	}

	// When / Then
	for _, group := range []struct {
		vectors []protocolFixtureVector
		accept  bool
	}{
		{vectors: corpus.Valid, accept: true},
		{vectors: corpus.Invalid, accept: false},
	} {
		for _, vector := range group.vectors {
			payload, err := hex.DecodeString(vector.BytesHex)
			if err != nil {
				t.Fatalf("fixture bytes are not hex: %v", err)
			}
			if vector.Accept != group.accept {
				t.Fatalf("fixture %q declares accept=%t in the wrong corpus group", vector.BytesHex, vector.Accept)
			}
			if got := verifyCanonicalFixture(payload); got != vector.Accept {
				t.Fatalf("fixture %q accepted=%t, want %t", vector.BytesHex, got, vector.Accept)
			}
		}
	}
}
