#!/usr/bin/env python3
"""Record what real Ed25519 verifiers answer for the divergence corpus.

`generate_ed25519_divergence_corpus.py` computes its own ZIP-215 verdicts.
Those are the weakest evidence the corpus can carry, because a misreading of
ZIP-215 in the generator agrees with the same misreading in the comment beside
it. This script produces the second opinion and writes it to
`conformance/vibeproof/v1/zip215-oracle-run.json`, which the generator then
consumes: a case whose digest that file covers is emitted `confirmed`, a case it
does not cover is emitted `unconfirmed`, and a case where the oracle contradicts
the computed verdict stops the generator.

Three implementations are exercised and they are not interchangeable:

* `github.com/hdevalence/ed25519consensus` is the ZIP-215 authority here. It is
  the implementation Zcash and CometBFT use and its author co-wrote the ZIP.
  Its answer is the only one recorded as the ZIP-215 verdict.
* Go's `crypto/ed25519` is cofactorless. It is a contrast oracle.
* Python's `cryptography`, over OpenSSL, is also cofactorless and libsodium-like.
  It is a contrast oracle. It is explicitly **not** ZIP-215 and its verdict is
  never recorded as one.

The two contrast columns exist because half of each case is the classic verdict,
and because they disagree with each other and with the strict reading of RFC
8032 in ways worth having on record rather than assumed.

Running this proves that three libraries answered these bytes this way on one
machine at one time. It does not prove any VibeProof implementation conformant;
none consumes the corpus yet.

Usage:
    run_ed25519_oracles.py             # rewrite the oracle run record
    run_ed25519_oracles.py --check     # exit 1 if a re-run would change a verdict
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "conformance" / "vibeproof" / "v1" / "ed25519-divergence-corpus.json"
ORACLE_DIRECTORY = ROOT / "conformance" / "vibeproof" / "v1" / "zip215-oracle"
RUN_RECORD = ROOT / "conformance" / "vibeproof" / "v1" / "zip215-oracle-run.json"

ORACLE_MODULE = "github.com/hdevalence/ed25519consensus"


def module_version() -> str:
    text = (ORACLE_DIRECTORY / "go.mod").read_text(encoding="utf-8")
    match = re.search(rf"^\s*require\s+{re.escape(ORACLE_MODULE)}\s+(\S+)", text, re.M)
    if not match:
        raise SystemExit(f"{ORACLE_MODULE} is not required by the oracle go.mod")
    return match.group(1)


def module_checksum(version: str) -> str:
    """The go.sum h1 line for the pinned module, so the record names exact bytes."""
    for line in (ORACLE_DIRECTORY / "go.sum").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == ORACLE_MODULE and parts[1] == version:
            return parts[2]
    raise SystemExit(f"no go.sum h1 entry for {ORACLE_MODULE} {version}")


def run_go_oracle() -> list[dict]:
    completed = subprocess.run(
        ["go", "run", "-C", str(ORACLE_DIRECTORY), ".", str(CORPUS)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            "the ZIP-215 oracle did not run: "
            + (completed.stderr.strip() or "no output")
        )
    return json.loads(completed.stdout)


def go_version() -> str:
    completed = subprocess.run(
        ["go", "version"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unknown"


def openssl_observations(cases: list[dict]) -> dict[str, str]:
    """The OpenSSL contrast column, recorded as contrast and never as ZIP-215."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    verdicts = {}
    for case in cases:
        public_key = bytes.fromhex(case["public_key_hex"])
        signature = bytes.fromhex(case["signature_hex"])
        message = bytes.fromhex(case["message_hex"])
        try:
            Ed25519PublicKey.from_public_bytes(public_key).verify(signature, message)
            verdicts[case["id"]] = "accept"
        except Exception:  # any refusal, at load or at verify, is a reject
            verdicts[case["id"]] = "reject"
    return verdicts


def openssl_identity() -> str:
    import cryptography
    from cryptography.hazmat.backends.openssl.backend import backend

    return f"python cryptography {cryptography.__version__} over {backend.openssl_version_text()}"


def build_record() -> dict:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    cases = corpus["cases"]
    results = run_go_oracle()
    openssl = openssl_observations(cases)
    openssl_label = openssl_identity()

    by_id = {case["id"]: case for case in cases}
    for entry in results:
        case = by_id.get(entry["case_id"])
        if case is None:
            raise SystemExit(f"oracle returned an unknown case: {entry['case_id']}")
        entry["cofactorless_observations"].append(
            {
                "implementation": openssl_label,
                "criterion": "cofactorless",
                "verdict": openssl[entry["case_id"]],
            }
        )

    version = module_version()
    return {
        "schema_version": 1,
        "record_kind": "reproducible-generated-artifact",
        "produced_by": "scripts/repository/run_ed25519_oracles.py",
        "command": "go run ./conformance/vibeproof/v1/zip215-oracle <corpus>",
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "zip215_oracle": {
            "id": ORACLE_MODULE,
            "version": version,
            "go_sum_h1": module_checksum(version),
            "toolchain": go_version(),
            "why_this_one": (
                "the ZIP-215 implementation Zcash and CometBFT use, written by a "
                "co-author of the ZIP. It is independent of the generator: the "
                "generator's arithmetic is Python written for this corpus and this "
                "is not a port of it."
            ),
        },
        "contrast_oracles": [
            {
                "id": "go crypto/ed25519",
                "criterion": "cofactorless",
                "role": "contrast only; never recorded as a ZIP-215 verdict",
            },
            {
                "id": openssl_label,
                "criterion": "cofactorless, libsodium-like",
                "role": "contrast only; never recorded as a ZIP-215 verdict",
            },
        ],
        "establishes": (
            "that these three libraries returned these verdicts for these exact "
            "bytes, each case bound by a SHA-256 digest over its own id, public "
            "key, R, S and message"
        ),
        "does_not_establish": [
            "that any VibeProof implementation is conformant; none consumes this corpus",
            "cross-language parity, which needs the Rust and Go verifiers of P-002 and S-002",
            "anything about security, privacy or launch readiness",
        ],
        "results": results,
    }


def render(record: dict) -> str:
    return json.dumps(record, indent=2, ensure_ascii=False) + "\n"


def verdict_map(record: dict) -> dict:
    """Everything in the record except when it was produced.

    `--check` compares verdicts, not timestamps: a re-run on another day is
    supposed to produce a new `generated_at` and the same answers, and a check
    that failed on the timestamp would train readers to ignore it.
    """
    return {
        entry["case_id"]: {
            "case_digest": entry["case_digest"],
            "zip215_verdict": entry["zip215_verdict"],
            "cofactorless_observations": entry["cofactorless_observations"],
        }
        for entry in record["results"]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if a fresh oracle run disagrees with the committed record",
    )
    arguments = parser.parse_args(argv)

    fresh = build_record()
    if arguments.check:
        if not RUN_RECORD.is_file():
            print(f"{RUN_RECORD} does not exist", file=sys.stderr)
            return 1
        committed = json.loads(RUN_RECORD.read_text(encoding="utf-8"))
        if verdict_map(committed) != verdict_map(fresh):
            print(
                "a fresh oracle run disagrees with the committed record; "
                "run run_ed25519_oracles.py and review every changed verdict",
                file=sys.stderr,
            )
            return 1
        confirmed = len(fresh["results"])
        print(f"ed25519 oracle run: {confirmed} case verdicts reproduced")
        return 0

    RUN_RECORD.write_text(render(fresh), encoding="utf-8")
    print(f"wrote {RUN_RECORD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
