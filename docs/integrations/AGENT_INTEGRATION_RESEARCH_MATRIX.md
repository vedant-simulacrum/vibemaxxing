# Agent Integration Research Matrix

| Agent | Best current candidate path | Initial evidence | Main risk | Required spike |
|---|---|---:|---|---|
| Gemini CLI | Local OTel token metrics plus hooks | Strong candidate | Prompt logging defaults/config drift | Run local OTLP fixture with content disabled and compare usage |
| Claude Code | Structured stream output and hooks | Medium candidate | Output schema may include content; usage stability | Capture synthetic runs and extract only approved usage fields |
| Codex CLI | OTel for supported modes | Medium candidate | Different entry points expose different signals | Probe interactive, exec, and MCP modes independently |
| OpenCode | Plugin/event interface or live wrapper | Unresolved | API churn and incomplete authoritative usage | Pin version and implement lifecycle probe |
| Cursor | Official extension/API or local live source | Unresolved | Closed product, brittle local storage | Verify documented integration path; otherwise label Open |
| Gemini IDE agent | Gemini CLI/IDE surface telemetry | Medium candidate | IDE surface differences | Exercise terminal and IDE surfaces separately |
| OpenHands | Runtime event stream and model usage metadata | Candidate | Worker version/schema variability | Run containerized synthetic task and verify safe fields |
| Goose | Extension/recipe/event interfaces | Unresolved | Token authority and schema stability | Executable local probe |
| Unknown terminal agent | PTY wrapper and live process accounting | Weak baseline | No provider-authoritative token data | Estimate-only adapter with explicit evidence downgrade |

## Acceptance rule

An adapter is not production-supported until it has:

1. a machine-readable manifest;
2. deterministic synthetic fixtures;
3. a version probe;
4. token reconciliation tests;
5. forbidden-field negative tests;
6. upgrade-breakage tests;
7. an explicit evidence class.
