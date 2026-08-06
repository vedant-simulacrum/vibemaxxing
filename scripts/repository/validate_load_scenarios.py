#!/usr/bin/env python3
"""Resolve every load scenario against the contracts it claims to be derived from.

`docs/verification/TEST_STRATEGY.md` names six load scenarios and
`evals/load/load-scenarios-v1.json` writes them out concretely. A scenario is only
worth writing if its numbers stay tied to something: a rate chosen once and then left
alone becomes a figure nobody can justify the moment the policy under it moves.

So every operation in every scenario names a `policy_ref`, and this resolves that key
against `packages/schemas/policy-defaults-v1.json`. A scenario naming a policy that
does not exist fails here rather than at the moment somebody tries to run it against a
limit that was renamed two quarters ago.

What this checks:

* every scenario TEST_STRATEGY.md names is declared, and no scenario is declared that
  the document does not name — a scenario neither side knows about is a scenario nobody
  will run;
* every `policy_ref` resolves to a policy that exists;
* every operation class is one the API edge contract declares;
* every scenario carries a duration, a pass condition and a fails-when sentence, and
  every pass condition is a metric, a comparison and a number rather than a judgement;
* the population is the private-beta ring size that `invite_outstanding_max` holds,
  rather than a round number that drifted away from it;
* the claim scope still says these are unrun specifications.

What this cannot check: whether any scenario is a good test, or whether the pass
conditions are the right ones. It checks that they are resolvable and that they say
what they are derived from. None of these has been written as a k6 script and none has
been run, which the file itself records and this validator refuses to let it stop
recording.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "evals" / "load" / "load-scenarios-v1.json"
POLICIES = ROOT / "packages" / "schemas" / "policy-defaults-v1.json"
STRATEGY = ROOT / "docs" / "verification" / "TEST_STRATEGY.md"

# docs/architecture/API_EDGE_CONTRACT.md declares these eleven classes. `mixed` is not
# one of them: it is this file's word for a scenario that drives the whole beta-steady
# mix at once rather than a single class, and it is allowed only for that.
OPERATION_CLASSES = frozenset(
    {
        "public-read",
        "authenticated-read",
        "claim-ingest",
        "presence",
        "social-mutate",
        "board-create",
        "auth-start",
        "device-poll",
        "subject-rights",
        "appeal",
        "report",
        "mixed",
    }
)

COMPARISONS = frozenset({"<=", ">=", "==", "<", ">"})

REQUIRED_SCENARIO_FIELDS = (
    "intent",
    "duration_seconds",
    "operations",
    "pass_conditions",
    "fails_when",
)


def load_json(path: Path, label: str, defects: list[str]) -> dict | None:
    try:
        document = json.loads(path.read_text())
    except OSError as error:
        defects.append(f"{label} is unreadable: {error}")
        return None
    except json.JSONDecodeError as error:
        defects.append(f"{label} is not valid JSON: {error.msg} at line {error.lineno}")
        return None
    if not isinstance(document, dict):
        defects.append(f"{label} must be a JSON object")
        return None
    return document


def scenarios_named_by_the_strategy(text: str) -> set[str]:
    """The scenario identifiers TEST_STRATEGY.md's table names, read from the table.

    Read rather than hardcoded, so the two cannot drift apart without this noticing.
    """
    names: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^\|\s*`([a-z][a-z-]*)`\s*\|", line)
        if match:
            names.add(match.group(1))
    return names


def validate(
    scenarios_path: Path, policies_path: Path, strategy_path: Path
) -> list[str]:
    defects: list[str] = []
    document = load_json(scenarios_path, "the load scenario file", defects)
    policy_document = load_json(policies_path, "the policy defaults", defects)
    if document is None or policy_document is None:
        return defects

    if document.get("schema_version") != 1:
        defects.append("the load scenario file must declare schema_version 1")
    if document.get("claim_scope") != "specification-only":
        defects.append(
            "the load scenario file must keep claim_scope specification-only; no scenario has been "
            "written as a script or run, and a file that stops saying so starts implying evidence"
        )

    policies = policy_document.get("policies")
    if not isinstance(policies, dict):
        defects.append(
            "packages/schemas/policy-defaults-v1.json declares no policies object"
        )
        return defects

    scenarios = document.get("scenarios")
    if not isinstance(scenarios, dict) or not scenarios:
        defects.append(
            "the load scenario file must declare a nonempty scenarios object"
        )
        return defects

    defects.extend(validate_population(document, policies))
    defects.extend(validate_against_the_strategy(scenarios, strategy_path, defects))

    for name in sorted(scenarios):
        scenario = scenarios[name]
        if not isinstance(scenario, dict):
            defects.append(f"scenario {name} must be an object")
            continue
        for field in REQUIRED_SCENARIO_FIELDS:
            if field not in scenario:
                defects.append(f"scenario {name} is missing {field}")
        duration = scenario.get("duration_seconds")
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            defects.append(
                f"scenario {name} declares a non-positive duration_seconds: {duration!r}"
            )
        if not str(scenario.get("fails_when", "")).strip():
            defects.append(
                f"scenario {name} declares no fails_when; a scenario whose failure has to be judged "
                "is not a scenario, because two people will judge it differently"
            )
        defects.extend(validate_operations(name, scenario.get("operations"), policies))
        defects.extend(validate_pass_conditions(name, scenario.get("pass_conditions")))
    return defects


def validate_population(document: dict, policies: dict) -> list[str]:
    """The ring size must still be the one the invite quota holds."""
    population = document.get("population")
    if not isinstance(population, dict):
        return ["the load scenario file declares no population object"]
    reference = population.get("policy_ref")
    if reference not in policies:
        return [
            f"the population names policy_ref {reference!r}, which packages/schemas/policy-defaults-v1.json does not declare"
        ]
    declared = population.get("participants")
    actual = policies[reference].get("value")
    if declared != actual:
        return [
            f"the population is {declared!r} participants and {reference} is {actual!r}; the private-beta "
            "ring size is a row count under D-180, so the scenarios move when the quota moves"
        ]
    return []


def validate_against_the_strategy(
    scenarios: dict, strategy_path: Path, defects: list[str]
) -> list[str]:
    """TEST_STRATEGY.md owns the scenario set; this file may not hold a different one."""
    try:
        text = strategy_path.read_text()
    except OSError as error:
        return [f"docs/verification/TEST_STRATEGY.md is unreadable: {error}"]
    named = scenarios_named_by_the_strategy(text)
    if not named:
        return [
            "docs/verification/TEST_STRATEGY.md names no load scenario; its scenario table is the owner and it is missing"
        ]
    problems: list[str] = []
    for missing in sorted(named - set(scenarios)):
        problems.append(
            f"docs/verification/TEST_STRATEGY.md names scenario {missing} and evals/load/load-scenarios-v1.json "
            "does not declare it"
        )
    for extra in sorted(set(scenarios) - named):
        problems.append(
            f"evals/load/load-scenarios-v1.json declares scenario {extra} and "
            "docs/verification/TEST_STRATEGY.md does not name it"
        )
    return problems


def validate_operations(name: str, operations: object, policies: dict) -> list[str]:
    if not isinstance(operations, list) or not operations:
        return [
            f"scenario {name} declares no operations; a scenario that drives nothing is a sentence"
        ]
    problems: list[str] = []
    for index, operation in enumerate(operations):
        where = f"scenario {name} operation {index}"
        if not isinstance(operation, dict):
            problems.append(f"{where} must be an object")
            continue
        operation_class = operation.get("operation_class")
        if operation_class not in OPERATION_CLASSES:
            problems.append(
                f"{where} names operation_class {operation_class!r}, which docs/architecture/API_EDGE_CONTRACT.md does not declare"
            )
        rate = operation.get("requests_per_second")
        if not isinstance(rate, (int, float)) or isinstance(rate, bool) or rate <= 0:
            problems.append(
                f"{where} declares a non-positive requests_per_second: {rate!r}"
            )
        if not str(operation.get("derivation", "")).strip():
            problems.append(
                f"{where} declares no derivation; a rate without one is a round number, which is what "
                "docs/architecture/API_EDGE_CONTRACT.md refuses for exactly this reason"
            )
        reference = operation.get("policy_ref")
        if reference not in policies:
            problems.append(
                f"{where} names policy_ref {reference!r}, which packages/schemas/policy-defaults-v1.json does not declare"
            )
    return problems


def validate_pass_conditions(name: str, conditions: object) -> list[str]:
    if not isinstance(conditions, list) or not conditions:
        return [
            f"scenario {name} declares no pass_conditions; without one the result is read off a feeling "
            "rather than off a number"
        ]
    problems: list[str] = []
    seen: set[str] = set()
    for index, condition in enumerate(conditions):
        where = f"scenario {name} pass condition {index}"
        if not isinstance(condition, dict):
            problems.append(f"{where} must be an object")
            continue
        metric = condition.get("metric")
        if not isinstance(metric, str) or not metric.strip():
            problems.append(f"{where} names no metric")
        elif metric in seen:
            problems.append(
                f"{where} repeats metric {metric!r}; two bounds on one metric is one bound too many"
            )
        else:
            seen.add(metric)
        if condition.get("comparison") not in COMPARISONS:
            problems.append(
                f"{where} declares comparison {condition.get('comparison')!r}, which is not one of {sorted(COMPARISONS)}"
            )
        value = condition.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            problems.append(f"{where} declares a non-numeric value: {value!r}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--scenarios", type=Path, default=SCENARIOS)
    parser.add_argument("--policies", type=Path, default=POLICIES)
    parser.add_argument("--strategy", type=Path, default=STRATEGY)
    arguments = parser.parse_args(argv)

    defects = validate(arguments.scenarios, arguments.policies, arguments.strategy)
    if defects:
        print("load scenario validation: FAIL")
        for defect in defects:
            print(f"- {defect}")
        print(f"load scenario validation: FAIL ({len(defects)} defect(s))")
        return 1
    document = json.loads(arguments.scenarios.read_text())
    operations = sum(
        len(scenario["operations"]) for scenario in document["scenarios"].values()
    )
    print(
        f"load scenario validation: PASS ({len(document['scenarios'])} scenarios, {operations} operations, "
        "every rate resolved against packages/schemas/policy-defaults-v1.json)"
    )
    print(
        "claim_scope=specification-only; no scenario has been written as a script and none has been run"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
