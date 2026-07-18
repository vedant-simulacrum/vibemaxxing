#!/usr/bin/env python3
"""Fail when seeded sensitive canaries appear in exported telemetry artifacts."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

DEFAULT_CANARIES = [
    "VMX_CANARY_PROMPT_7d8241",
    "VMX_CANARY_SECRET_sk-test-never-real",
    "/Users/vmx/private/project-alpha/source.rs",
    "repo-private-vmx-canary",
    "TRANSCRIPT_CANARY_DO_NOT_EXPORT",
]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--canary", action="append", default=[])
    ap.add_argument("--out", default="artifacts/evals/telemetry-canary-leakage.json")
    args = ap.parse_args()
    canaries = DEFAULT_CANARIES + args.canary
    findings = []
    for file in args.path.rglob("*"):
        if not file.is_file() or file.stat().st_size > 50_000_000:
            continue
        try:
            data = file.read_text(errors="ignore")
        except OSError:
            continue
        for canary in canaries:
            if canary in data:
                findings.append({"file": str(file), "canary": canary})
        if re.search(r"(?i)authorization\s*[:=]\s*bearer\s+\S+", data):
            findings.append({"file": str(file), "pattern": "authorization bearer token"})
    result = {"status": "fail" if findings else "pass", "findings": findings,
              "files_scanned_root": str(args.path)}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if findings else 0)

if __name__ == "__main__":
    main()
