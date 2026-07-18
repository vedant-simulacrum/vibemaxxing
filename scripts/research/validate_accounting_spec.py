#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "conformance/accounting/accounting-schema-v1.json"
REQUIRED = {
    "schema_version", "required_categories", "relationships", "source_precedence"
}

def main() -> int:
    data = json.loads(SCHEMA.read_text())
    missing = REQUIRED - data.keys()
    if missing:
        raise SystemExit(f"missing keys: {sorted(missing)}")
    cats = data["required_categories"]
    if len(cats) != len(set(cats)):
        raise SystemExit("duplicate accounting categories")
    if data["source_precedence"][0] != "provider_authoritative":
        raise SystemExit("authoritative provider usage must have highest precedence")
    print(json.dumps({"status": "pass", "schema": str(SCHEMA.relative_to(ROOT))}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
