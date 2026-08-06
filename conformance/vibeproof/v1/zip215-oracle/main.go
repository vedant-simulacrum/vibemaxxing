// Command zip215-oracle answers, for every case in the Ed25519 divergence
// corpus, what an independent ZIP-215 implementation actually does.
//
// The corpus generator computes its own ZIP-215 verdicts from its own curve
// arithmetic. That is the weakest evidence a conformance corpus can carry: a
// misreading of ZIP-215 in the generator and the same misreading in the comment
// beside it agree with each other and neither is right. This program is the
// second opinion, and it is deliberately not the generator's code in another
// language - it calls github.com/hdevalence/ed25519consensus, which is the
// implementation Zcash and CometBFT use for ZIP-215 and whose author co-wrote
// the ZIP.
//
// It also records Go's crypto/ed25519 for contrast. That verifier is
// cofactorless by design and is expected to reject cases ZIP-215 accepts; its
// answer is half of every case and is what makes the divergence measured rather
// than argued. It is never recorded as the ZIP-215 verdict.
//
// This program confirms verdicts. It does not make VibeProof conformant, and
// running it is not evidence that any VibeProof implementation exists.
//
// Usage:
//
//	go run ./conformance/vibeproof/v1/zip215-oracle <corpus.json>
//
// It writes a JSON results array to stdout. scripts/repository/run_ed25519_oracles.py
// is the driver that adds provenance and the OpenSSL contrast column and writes
// zip215-oracle-run.json.
package main

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"

	"github.com/hdevalence/ed25519consensus"
)

type corpusCase struct {
	ID           string `json:"id"`
	PublicKeyHex string `json:"public_key_hex"`
	SignatureHex string `json:"signature_hex"`
	MessageHex   string `json:"message_hex"`
}

type corpus struct {
	Cases []corpusCase `json:"cases"`
}

type observation struct {
	Implementation string `json:"implementation"`
	Criterion      string `json:"criterion"`
	Verdict        string `json:"verdict"`
}

type result struct {
	CaseID                   string        `json:"case_id"`
	CaseDigest               string        `json:"case_digest"`
	OracleID                 string        `json:"oracle_id"`
	ZIP215Verdict            string        `json:"zip215_verdict"`
	CofactorlessObservations []observation `json:"cofactorless_observations"`
}

// oracleID names the implementation whose answer is recorded as the ZIP-215
// verdict. The version is filled in by the driver from go.mod, so this string
// cannot drift from the module that was actually linked.
const oracleID = "github.com/hdevalence/ed25519consensus"

// caseDigest must be recomputed here from the case bytes rather than copied
// from the corpus. A confirmation that trusts the corpus's own digest field
// confirms whatever the corpus claims its bytes were.
func caseDigest(id string, publicKey, signature, message []byte) string {
	sum := sha256.New()
	sum.Write([]byte(id))
	sum.Write([]byte("|"))
	sum.Write(publicKey)
	sum.Write([]byte("|"))
	sum.Write(signature[:32])
	sum.Write([]byte("|"))
	sum.Write(signature[32:])
	sum.Write([]byte("|"))
	sum.Write(message)
	return hex.EncodeToString(sum.Sum(nil))
}

func verdict(accepted bool) string {
	if accepted {
		return "accept"
	}
	return "reject"
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: zip215-oracle <corpus.json>")
		os.Exit(2)
	}

	raw, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot read corpus: %v\n", err)
		os.Exit(1)
	}
	var document corpus
	if err := json.Unmarshal(raw, &document); err != nil {
		fmt.Fprintf(os.Stderr, "cannot parse corpus: %v\n", err)
		os.Exit(1)
	}
	if len(document.Cases) == 0 {
		fmt.Fprintln(os.Stderr, "corpus carries no cases")
		os.Exit(1)
	}

	results := make([]result, 0, len(document.Cases))
	for _, item := range document.Cases {
		publicKey, err := hex.DecodeString(item.PublicKeyHex)
		if err != nil || len(publicKey) != ed25519.PublicKeySize {
			fmt.Fprintf(os.Stderr, "%s: public key is not 32 hex-encoded bytes\n", item.ID)
			os.Exit(1)
		}
		signature, err := hex.DecodeString(item.SignatureHex)
		if err != nil || len(signature) != ed25519.SignatureSize {
			fmt.Fprintf(os.Stderr, "%s: signature is not 64 hex-encoded bytes\n", item.ID)
			os.Exit(1)
		}
		message, err := hex.DecodeString(item.MessageHex)
		if err != nil {
			fmt.Fprintf(os.Stderr, "%s: message is not hex-encoded\n", item.ID)
			os.Exit(1)
		}

		results = append(results, result{
			CaseID:        item.ID,
			CaseDigest:    caseDigest(item.ID, publicKey, signature, message),
			OracleID:      oracleID,
			ZIP215Verdict: verdict(ed25519consensus.Verify(publicKey, message, signature)),
			CofactorlessObservations: []observation{
				{
					Implementation: "go crypto/ed25519",
					Criterion:      "cofactorless",
					Verdict:        verdict(ed25519.Verify(publicKey, message, signature)),
				},
			},
		})
	}

	encoded, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot encode results: %v\n", err)
		os.Exit(1)
	}
	fmt.Println(string(encoded))
}
