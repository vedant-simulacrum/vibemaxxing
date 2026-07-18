#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(__file__).resolve().parents[2]
required = [
    'AGENTS.md', 'SECURITY.md', 'docs/privacy/PRIVACY_CONTRACT.md',
    'docs/security/THREAT_MODEL.md', 'docs/qa/ACCEPTANCE_GATES.md',
    'docs/evals/EVAL_SYSTEM.md', 'docs/operations/PRODUCTION_READINESS.md',
]
errors = [f'missing required file: {p}' for p in required if not (root / p).is_file()]
forbidden_patterns = {
    'private-key': re.compile(r'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY'),
    'obsolete-remote-control-plane': re.compile(r'vibemaxxing-(private-)?control-plane|ONE_PROMPT_AUTONOMOUS_BOOTSTRAP'),
}
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts or p.name in {'SHA256SUMS'} or p == Path(__file__).resolve():
        continue
    try: text = p.read_text(errors='ignore')
    except Exception: continue
    for name, pat in forbidden_patterns.items():
        if pat.search(text): errors.append(f'{name}: {p.relative_to(root)}')
if errors:
    print('\n'.join(errors), file=sys.stderr)
    raise SystemExit(1)
print('repository policy: pass')
