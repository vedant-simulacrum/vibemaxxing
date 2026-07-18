#!/usr/bin/env python3
"""Metadata-only local agent capability probe.

It never reads prompts, transcripts, credentials, or project files. It checks only
executable availability/version output and writes a machine-readable report.
"""
from __future__ import annotations
import argparse, datetime, json, shutil, subprocess
from pathlib import Path

CANDIDATES = {
    "codex": [["codex", "--version"]],
    "claude": [["claude", "--version"]],
    "opencode": [["opencode", "--version"]],
    "gemini": [["gemini", "--version"]],
    "openhands": [["openhands", "--version"]],
    "goose": [["goose", "--version"]],
}

def safe_version(commands: list[list[str]]) -> dict:
    exe = commands[0][0]
    path = shutil.which(exe)
    if not path:
        return {"available": False}
    for command in commands:
        try:
            p = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
            text = (p.stdout or p.stderr).strip().splitlines()
            return {"available": True, "path": path, "exit_code": p.returncode,
                    "version_output": text[0][:300] if text else ""}
        except (OSError, subprocess.TimeoutExpired) as exc:
            last = str(exc)
    return {"available": True, "path": path, "error": last}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts/research/agent-capabilities.json")
    args = ap.parse_args()
    result = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "privacy": "metadata-only; no prompts, transcripts, environment values, or config contents",
        "agents": {name: safe_version(cmds) for name, cmds in CANDIDATES.items()},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
