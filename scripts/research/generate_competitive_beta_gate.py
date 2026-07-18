#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime, json
from pathlib import Path

REQUIRED = {
    "adapter-gemini": "artifacts/evidence/adapter-gemini.json",
    "adapter-claude-code": "artifacts/evidence/adapter-claude-code.json",
    "adapter-codex": "artifacts/evidence/adapter-codex.json",
    "accounting-conformance": "artifacts/evidence/accounting-conformance.json",
    "privacy-canaries": "artifacts/evals/telemetry-canary-leakage.json",
    "adversarial-integrity": "artifacts/evidence/adversarial-integrity.json",
    "collector-macos": "artifacts/benchmarks/collector-macos.json",
    "collector-windows": "artifacts/benchmarks/collector-windows.json",
    "collector-linux": "artifacts/benchmarks/collector-linux.json",
    "postgres-ranking": "artifacts/benchmarks/postgres-ranking.json",
    "onboarding-study": "artifacts/evidence/onboarding-study.json",
    "pricing-provenance": "artifacts/evidence/pricing-provenance.json",
    "release-verification": "artifacts/evidence/release-consumer-verification.json",
    "deletion-restore": "artifacts/evidence/deletion-restore.json",
    "moderation-tabletop": "artifacts/evidence/moderation-tabletop.json"
}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="artifacts/evals/competitive-beta-go-no-go.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    checks = []
    for name, rel in REQUIRED.items():
        path = root / rel
        status = "missing"
        detail = None
        if path.is_file() and path.stat().st_size:
            try:
                payload = json.loads(path.read_text())
                status = "pass" if payload.get("status") == "pass" else "fail"
                detail = payload.get("reason") or payload.get("summary")
            except Exception as exc:
                status, detail = "invalid", str(exc)
        checks.append({"name": name, "path": rel, "status": status, "detail": detail})
    overall = "pass" if all(c["status"] == "pass" for c in checks) else "fail"
    result = {
        "schema_version": "1",
        "status": overall,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "checks": checks,
        "reason": None if overall == "pass" else "One or more mandatory competitive-beta evidence artifacts are missing, invalid, or failing."
    }
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if overall == "pass" else 1

if __name__ == "__main__":
    raise SystemExit(main())
