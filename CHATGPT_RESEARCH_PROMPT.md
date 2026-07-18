# VibeMaxxing Continuous Research Prompt

Use this prompt with ChatGPT or another research-capable model that can inspect the GitHub repository and browse current primary sources.

---

Audit `vedant-simulacrum/vibemaxxing` as the current authoritative project repository.

First read, in order:

1. `PROJECT_CONTEXT.md`
2. `PROJECT_INSTRUCTIONS.md`
3. `CURRENT_STATUS.md`
4. `MODEL_OPERATING_MANUAL.md`
5. `docs/research/CHATGPT_CONTINUOUS_RESEARCH_WORKFLOW.md`
6. `docs/planning/PLANNING_AUDIT.md`
7. `docs/planning/DECISION_REGISTER.md`
8. `docs/planning/DEPENDENCY_MAP.md`
9. `docs/planning/TASK_CATALOG.md`
10. `docs/planning/SPECIFICATION_INDEX.md`
11. `docs/security/ANTI_CHEAT_RESEARCH_PROGRAM.md`
12. All directly relevant specifications, ADRs, research audits, and threat models.

The project is in planning and decision-closing mode. Do not implement or execute the product. You may improve specifications, ADRs, schemas, state machines, API contracts, threat models, research plans, test designs, benchmark plans, acceptance gates, and model-facing context.

The complete product is the public-launch target. Internal development may be staged, but public launch must meet the complete launch scope and quality bar. Do not narrow the intended product into a minimal public MVP.

Perform the following work:

1. Audit repository truth: implemented versus specification-only versus placeholder versus stale artifact.
2. Find contradictions, duplicated authority, unsupported claims, missing contracts, stale external facts, and ambiguous decisions.
3. Identify the highest-risk assumptions that could cause architectural rework, cheating, privacy leakage, weak agent coverage, poor UX, or launch failure.
4. Select the highest-value unresolved decision or planning task.
5. Research it using current primary sources, standards, upstream repositories, conformance suites, official platform documentation, or authoritative security research.
6. Compare viable approaches with explicit criteria, failure modes, maintenance burden, privacy impact, security impact, performance impact, and compatibility impact.
7. Close the decision when evidence permits. Otherwise define the exact executable spike, benchmark, attack campaign, user study, or conformance test required.
8. Update the minimum authoritative repository documents needed so no important conclusion remains only in chat.
9. Preserve stable decision IDs, task IDs, authority order, privacy requirements, staged delivery, and complete public-launch scope.
10. Report what changed, what remains uncertain, and the next five planning tasks in dependency order.

For anti-cheat work, deterministic accounting and cryptographic controls remain authoritative. Rules, statistics, and SLMs are secondary risk signals. An SLM may not rewrite token totals or permanently ban users by itself.

Do not produce broad generic research. Every research activity must close or sharpen a named decision, task, schema, threat, benchmark, or acceptance gate.

End with:

- executive summary;
- critical findings;
- evidence and sources;
- decisions closed or reopened;
- files changed;
- next tasks;
- user decisions required;
- explicit list of product implementation not performed.

---