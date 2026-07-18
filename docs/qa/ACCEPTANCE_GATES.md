# Acceptance Gates

The project is not production-ready until:

1. Editing historical logs cannot affect active rankings.
2. A local token-field edit cannot directly alter accepted competitive totals.
3. The client cannot submit authoritative rank or lifetime total.
4. Replaying a claim has no effect.
5. Claim reordering and omitted sequences are detected.
6. Environment rollback or state restoration cannot replay accepted activity.
7. Host and guest cannot double-count the same session.
8. Unknown adapter/source versions downgrade or fail closed.
9. Every public aggregate is reproducible from accepted claims.
10. The outbound protocol accepts no arbitrary text.
11. Packet capture contains no transcript, code, path, project, secret, embedding, or summary.
12. Transcript analyzer has no network capability.
13. Sync process has no transcript capability.
14. Prompt injection cannot grant the SLM tools, shell, network, or filesystem expansion.
15. SLM cannot permanently ban without deterministic corroboration and review.
16. Canonical accounting reproduces across macOS, Windows, and Linux.
17. Current user is easy to locate in every leaderboard layout.
18. All major routes have loading, empty, error, offline, unauthorized, private, and suspicious states.
19. WCAG 2.2 AA checks pass.
20. External security review finds no trivial JSONL-editing-equivalent attack.

## Engineering and release gates

21. Every frozen invariant has a versioned deterministic eval fixture.
22. Pull requests pass policy, build, conformance, privacy, frontend and security checks.
23. High-risk changes have an ADR, negative tests, two reviewers and rollback notes.
24. Release artifacts include SBOM and provenance; binaries and containers are signed when introduced.
25. Production launch has measured load/soak results, approved SLOs, exercised incident runbooks and a successful restoration test.
26. No workflow reports a false pass when its required implementation or fixture is absent.
