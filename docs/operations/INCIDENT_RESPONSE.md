# Incident Response

Severity levels:

- **SEV-0:** confirmed privacy breach, signing-key compromise or leaderboard-wide integrity corruption.
- **SEV-1:** major outage, widespread incorrect rankings or loss of accepted claims.
- **SEV-2:** partial degradation, delayed aggregation or contained security issue.
- **SEV-3:** minor defect with a workaround.

For SEV-0/1: appoint incident commander, stop unsafe writes when necessary, preserve evidence, communicate status, rotate affected credentials, execute the recovery runbook and publish a blameless post-incident review. Never destroy evidence during remediation.
