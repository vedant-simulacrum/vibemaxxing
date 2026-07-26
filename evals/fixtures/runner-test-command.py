#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "evals/fixtures/runner-test-fixtures.json"


def main() -> int:
    commit = sys.argv[1]
    manifest_text = MANIFEST.read_text()
    manifest = json.loads(manifest_text)
    fixture = manifest["fixtures"][0]
    fixture_path = ROOT / fixture["path"]
    fixture_digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()
    print(json.dumps({
        "version": "1",
        "status": "pass",
        "suite": manifest["suite"],
        "commit": commit,
        "started_at": now,
        "finished_at": now,
        "cases": [{"id": fixture["id"], "status": "pass"}],
        "fixtures": {
            "manifest_sha256": hashlib.sha256(manifest_text.encode()).hexdigest(),
            "fixtures": [{"id": fixture["id"], "sha256": fixture_digest}],
        },
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
