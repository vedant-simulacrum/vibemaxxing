"""Drift-injection tests for scripts/ci/measure_coverage.py.

`docs/verification/TEST_STRATEGY.md` stated coverage floors for months against no
measured number, which made every floor unfalsifiable. The measurer removes that, and a
gate that removes an unfalsifiable claim has to be falsifiable itself: these tests drive
each direction and assert which way it fires.

Both directions, explicitly:

* a scope that gets worse than the record fails, and the failure says whether the
  denominator grew (new uncovered code), shrank (a deletion or a move) or held (a test
  was weakened);
* a scope that improves never fails and is reported so the ceiling can be tightened;
* a baseline that is missing, unparseable, wrongly versioned, incomplete or internally
  impossible fails closed;
* a surface the toolchain could not measure is not silently a pass.

The real measurers are not run here. They take about two minutes and they are exercised
by the CI job that runs them; what these tests own is the comparison, which is the part
that can be wrong in a way nobody notices.
"""

from __future__ import annotations

import importlib.util
import io
import json
import re
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MEASURER = ROOT / "scripts" / "ci" / "measure_coverage.py"
BASELINE = ROOT / "scripts" / "ci" / "measured-coverage-baseline-v1.json"


def load_measurer() -> object:
    specification = importlib.util.spec_from_file_location("measure_coverage", MEASURER)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def baseline_document() -> dict:
    return json.loads(BASELINE.read_text())


def substituted(measurements: list, replacement) -> list:
    """Swap one scope's measurement, keyed by scope name rather than by position.

    Position would silently start testing a different scope the day a fourth one is
    added, which is exactly the class of quiet drift these tests exist to catch.
    """
    swapped = [
        replacement if entry.scope == replacement.scope else entry
        for entry in measurements
    ]
    assert any(entry is replacement for entry in swapped), (
        f"no measurement named {replacement.scope}"
    )
    return swapped


class MeasurementFactory:
    """Build a Measurement matching a recorded scope, then perturb it."""

    def __init__(self, module: object) -> None:
        self.module = module

    def at_record(self, scope: str, document: dict | None = None, **overrides: object):
        record = (document or baseline_document())["scopes"][scope]
        values: dict[str, object] = {
            "scope": scope,
            "language": record["language"],
            "metric": record["metric"],
            "measured": True,
            "percent": record["percent"],
            "covered_units": record["covered_units"],
            "total_units": record["total_units"],
            "tool": "test",
        }
        values.update(overrides)
        return self.module.Measurement(**values)  # type: ignore[attr-defined]


class RecordedNumbersMatchTheDocumentTests(unittest.TestCase):
    """The prose must not drift from the record it is quoting.

    `docs/verification/TEST_STRATEGY.md` restates the measured number for every surface
    and states the floor each is held to. Two files holding the same number is how one
    of them goes stale: the baseline moves on the commit that changes coverage and the
    document keeps quoting whatever it quoted before, and a reader takes the document at
    its word. Nothing else in this repository would catch that, so this does.
    """

    def setUp(self) -> None:
        self.document = baseline_document()
        self.strategy = (
            ROOT / "docs" / "verification" / "TEST_STRATEGY.md"
        ).read_text()

    def test_every_measured_percentage_appears_in_the_strategy(self) -> None:
        for scope, record in self.document["scopes"].items():
            with self.subTest(scope=scope):
                self.assertIn(
                    f"{record['percent']:.2f}%",
                    self.strategy,
                    f"{scope} is recorded at {record['percent']:.2f}% and TEST_STRATEGY.md does not "
                    "quote that number; one of the two is stale",
                )

    def test_every_recorded_unit_count_appears_in_the_strategy(self) -> None:
        # Denominators are what the regression attribution is read against, so a stale
        # one in the document misleads exactly the reader trying to interpret a failure.
        for scope, record in self.document["scopes"].items():
            with self.subTest(scope=scope):
                self.assertIn(
                    f"{record['covered_units']:,} of {record['total_units']:,}",
                    self.strategy,
                    f"{scope} is recorded at {record['covered_units']} of {record['total_units']} "
                    "units and TEST_STRATEGY.md does not quote that pair",
                )

    def test_every_recorded_floor_is_the_one_the_strategy_states(self) -> None:
        # A floor recorded here that the document does not state is a floor nobody
        # agreed to, and floor_source claims the document as its authority.
        for scope, record in self.document["scopes"].items():
            floor = record.get("floor_percent")
            if floor is None:
                continue
            with self.subTest(scope=scope):
                self.assertEqual(
                    record["floor_source"], "docs/verification/TEST_STRATEGY.md"
                )
                self.assertIn(
                    f"{floor:g}% ",
                    self.strategy,
                    f"{scope} is held to a {floor:g}% floor that TEST_STRATEGY.md does not state",
                )

    def test_the_zero_coverage_modules_named_in_the_baseline_still_exist(self) -> None:
        # The list is the argument for where the Python floor starts. A module in it
        # that has been deleted or renamed makes that argument quietly wrong.
        note = self.document["scopes"]["python-planning-tooling"]["note"]
        # Only the enumerated list, not every filename the prose happens to mention:
        # the note also names coverage.py, which is the tool rather than a module here.
        listed = re.search(r"are at 0%: (.+?)\. ", note)
        self.assertIsNotNone(
            listed, "the baseline note no longer enumerates the uncovered modules"
        )
        assert listed is not None
        named = re.findall(r"\b([a-z0-9_]+\.py)\b", listed.group(1))
        self.assertEqual(len(named), 10)
        for module in named:
            with self.subTest(module=module):
                candidates = [
                    ROOT / "scripts" / "ci" / module,
                    ROOT / "scripts" / "repository" / module,
                ]
                self.assertTrue(
                    any(path.is_file() for path in candidates),
                    f"the baseline names {module} as uncovered and no such module exists",
                )


class BaselineLoadingTests(unittest.TestCase):
    """A ceiling that cannot be read is a broken constraint, not an absent one."""

    def setUp(self) -> None:
        self.module = load_measurer()

    def test_the_committed_baseline_loads(self) -> None:
        document = self.module.load_baseline(BASELINE)
        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(document["rule"], "non-regression")
        self.assertEqual(
            sorted(document["scopes"]),
            ["go-apps-api", "python-planning-tooling", "rust-vibeproof-core"],
        )

    def test_the_committed_baseline_records_every_scope_the_measurer_measures(
        self,
    ) -> None:
        # A scope the measurer produces and the baseline omits is a hole that the
        # comparison would otherwise have nothing to compare against.
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory)
            measured = {
                measurement.scope for measurement in self.module.measure_all(empty)
            }
        self.assertEqual(measured, set(baseline_document()["scopes"]))

    def test_a_missing_baseline_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError) as raised:
                self.module.load_baseline(Path(directory) / "absent.json")
        self.assertIn("unreadable coverage baseline", str(raised.exception))

    def test_unparseable_json_fails_closed(self) -> None:
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write("{ not json"))
        self.assertIn("invalid JSON", str(raised.exception))

    def test_a_wrong_schema_version_fails_closed(self) -> None:
        document = baseline_document()
        document["schema_version"] = 2
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("schema_version 1", str(raised.exception))

    def test_a_missing_tolerance_fails_closed(self) -> None:
        document = baseline_document()
        del document["tolerance_percentage_points"]
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("tolerance_percentage_points", str(raised.exception))

    def test_an_empty_scopes_object_fails_closed(self) -> None:
        document = baseline_document()
        document["scopes"] = {}
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("nonempty scopes", str(raised.exception))

    def test_a_scope_missing_a_required_field_fails_closed(self) -> None:
        document = baseline_document()
        del document["scopes"]["rust-vibeproof-core"]["total_units"]
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("missing total_units", str(raised.exception))

    def test_a_percent_outside_the_range_fails_closed(self) -> None:
        document = baseline_document()
        document["scopes"]["rust-vibeproof-core"]["percent"] = 140
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("outside 0-100", str(raised.exception))

    def test_more_covered_units_than_total_units_fails_closed(self) -> None:
        # An impossible record would otherwise be a ceiling nothing can ever reach,
        # which fails every run for a reason nobody can act on.
        document = baseline_document()
        document["scopes"]["go-apps-api"]["covered_units"] = 999
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("more covered units than total units", str(raised.exception))

    def test_an_absent_floor_without_a_reason_fails_closed(self) -> None:
        document = baseline_document()
        del document["scopes"]["go-apps-api"]["floor_absent_reason"]
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("floor_absent_reason", str(raised.exception))

    def test_a_floor_without_a_source_fails_closed(self) -> None:
        document = baseline_document()
        del document["scopes"]["rust-vibeproof-core"]["floor_source"]
        with self.assertRaises(ValueError) as raised:
            self.module.load_baseline(self.write(json.dumps(document)))
        self.assertIn("floor_source", str(raised.exception))

    def write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        return Path(handle.name)


class RegressionDirectionTests(unittest.TestCase):
    """Worse fails, the same passes, better passes and is reported."""

    def setUp(self) -> None:
        self.module = load_measurer()
        self.document = baseline_document()
        self.factory = MeasurementFactory(self.module)

    def measured(self) -> list:
        return [
            self.factory.at_record(scope, self.document)
            for scope in self.document["scopes"]
        ]

    def test_sitting_exactly_at_the_record_does_not_fail(self) -> None:
        self.assertEqual(
            self.module.regressions(self.measured(), self.document, False), []
        )

    def test_a_fall_inside_the_tolerance_does_not_fail(self) -> None:
        # Rust rather than Python, because Python is recorded 0.86 points above its
        # floor and a 0.9-point fall would breach the floor instead of demonstrating
        # the band. That narrowness is a fact about the record, not about the band.
        record = self.document["scopes"]["rust-vibeproof-core"]
        measurements = substituted(
            self.measured(),
            self.factory.at_record(
                "rust-vibeproof-core", self.document, percent=record["percent"] - 0.9
            ),
        )
        self.assertEqual(
            self.module.regressions(measurements, self.document, False), []
        )

    def test_a_fall_beyond_the_tolerance_fails(self) -> None:
        record = self.document["scopes"]["python-planning-tooling"]
        measurements = substituted(
            self.measured(),
            self.factory.at_record(
                "python-planning-tooling",
                self.document,
                percent=record["percent"] - 5.0,
            ),
        )
        failures = self.module.regressions(measurements, self.document, False)
        self.assertTrue(any("regressed from" in failure for failure in failures))
        self.assertTrue(any("-5.00 points" in failure for failure in failures))

    def test_an_improvement_never_fails_and_is_reported(self) -> None:
        record = self.document["scopes"]["rust-vibeproof-core"]
        improved = self.factory.at_record(
            "rust-vibeproof-core",
            self.document,
            percent=record["percent"] + 4.0,
            covered_units=record["total_units"],
        )
        measurements = substituted(self.measured(), improved)
        self.assertEqual(
            self.module.regressions(measurements, self.document, False), []
        )
        self.assertEqual(
            self.module.improvements(measurements, self.document),
            [
                f"rust-vibeproof-core {record['percent']:.2f}% -> {record['percent'] + 4.0:.2f}%"
            ],
        )

    def test_a_below_floor_number_fails_even_when_it_is_not_a_regression(self) -> None:
        # The floor and the ceiling are different constraints. A scope recorded below
        # its own floor would otherwise sit there forever without failing anything.
        document = baseline_document()
        document["scopes"]["rust-vibeproof-core"]["percent"] = 80.0
        measurements = [
            self.factory.at_record(scope, document) for scope in document["scopes"]
        ]
        failures = self.module.regressions(measurements, document, False)
        self.assertTrue(any("its floor is 90.00%" in failure for failure in failures))
        self.assertTrue(
            any(
                "a floor is not lowered to fit a measurement" in failure
                for failure in failures
            )
        )

    def test_a_recorded_scope_that_is_no_longer_measured_fails(self) -> None:
        # Without this the gate is evaded by deleting the scope.
        measurements = [m for m in self.measured() if m.scope != "go-apps-api"]
        failures = self.module.regressions(measurements, self.document, False)
        self.assertTrue(
            any(
                "go-apps-api" in failure and "nothing measured it" in failure
                for failure in failures
            )
        )

    def test_a_measured_scope_that_is_not_recorded_fails(self) -> None:
        # And without this it is evaded by renaming the scope.
        measurements = self.measured()
        measurements.append(
            self.module.Measurement(
                scope="typescript-apps-web",
                language="typescript",
                metric="statement",
                measured=True,
                percent=99.0,
                covered_units=99,
                total_units=100,
            )
        )
        failures = self.module.regressions(measurements, self.document, False)
        self.assertTrue(
            any(
                "typescript-apps-web" in failure and "not recorded" in failure
                for failure in failures
            )
        )

    def test_a_changed_metric_fails_rather_than_being_compared(self) -> None:
        measurements = substituted(
            self.measured(),
            self.factory.at_record(
                "rust-vibeproof-core", self.document, metric="region", percent=99.0
            ),
        )
        failures = self.module.regressions(measurements, self.document, False)
        self.assertTrue(
            any(
                "two different units cannot be compared" in failure
                for failure in failures
            )
        )


class UnmeasuredSurfaceTests(unittest.TestCase):
    """An absent toolchain is an absence of evidence, never a pass."""

    def setUp(self) -> None:
        self.module = load_measurer()
        self.document = baseline_document()
        self.factory = MeasurementFactory(self.module)

    def unmeasured(self) -> list:
        at_record = [
            self.factory.at_record(scope, self.document)
            for scope in self.document["scopes"]
        ]
        return substituted(
            at_record,
            self.module.Measurement(
                scope="rust-vibeproof-core",
                language="rust",
                metric="line",
                measured=False,
                note="llvm-profdata and llvm-cov were not found in the active toolchain",
            ),
        )

    def test_an_unmeasured_scope_fails_by_default(self) -> None:
        failures = self.module.regressions(self.unmeasured(), self.document, False)
        self.assertTrue(any("was not measured" in failure for failure in failures))
        self.assertTrue(any("never a pass" in failure for failure in failures))

    def test_allow_unmeasured_downgrades_it_and_nothing_else(self) -> None:
        self.assertEqual(
            self.module.regressions(self.unmeasured(), self.document, True), []
        )
        # The escape hatch does not also excuse a regression in a scope that was measured.
        measurements = substituted(
            self.unmeasured(),
            self.factory.at_record(
                "python-planning-tooling", self.document, percent=10.0
            ),
        )
        self.assertTrue(self.module.regressions(measurements, self.document, True))


class AttributionTests(unittest.TestCase):
    """Say whether a fall is added code, a moved file, or a weakened test."""

    def setUp(self) -> None:
        self.module = load_measurer()

    def test_a_grown_denominator_reads_as_new_uncovered_code(self) -> None:
        message = self.module.classify(6430, 6867)
        self.assertIn("437 unit(s) of new code arrived", message)
        self.assertIn("rather than a file moving", message)

    def test_a_shrunken_denominator_reads_as_a_deletion_or_a_move(self) -> None:
        message = self.module.classify(6430, 6000)
        self.assertIn("the scope lost 430 unit(s)", message)
        self.assertIn("Check whether another scope gained the same units", message)

    def test_an_unchanged_denominator_reads_as_a_weakened_test(self) -> None:
        message = self.module.classify(321, 321)
        self.assertIn("units that used to execute no longer do", message)

    def test_the_failure_message_carries_the_attribution(self) -> None:
        document = baseline_document()
        factory = MeasurementFactory(self.module)
        record = document["scopes"]["python-planning-tooling"]
        measurements = substituted(
            [factory.at_record(scope, document) for scope in document["scopes"]],
            factory.at_record(
                "python-planning-tooling",
                document,
                percent=record["percent"] - 9.89,
                total_units=record["total_units"] + 437,
            ),
        )
        failure = next(
            f
            for f in self.module.regressions(measurements, document, False)
            if "regressed" in f
        )
        self.assertIn("437 unit(s) of new code arrived", failure)


class GoFloorSubjectTests(unittest.TestCase):
    """The absent Go floor has to stop being absent the moment it gains a subject."""

    def setUp(self) -> None:
        self.module = load_measurer()
        self.document = baseline_document()
        self.factory = MeasurementFactory(self.module)

    def at_record_with_go_detail(self, packages: list[str]) -> list:
        return substituted(
            [
                self.factory.at_record(scope, self.document)
                for scope in self.document["scopes"]
            ],
            self.factory.at_record(
                "go-apps-api", self.document, detail={"non_main_packages": packages}
            ),
        )

    def test_a_main_only_module_needs_no_floor(self) -> None:
        measurements = self.at_record_with_go_detail([])
        self.assertEqual(
            self.module.regressions(measurements, self.document, False), []
        )

    def test_a_non_main_package_without_a_recorded_floor_fails(self) -> None:
        measurements = self.at_record_with_go_detail(
            ["github.com/vibemaxxing/vibemaxxing/apps/api/internal/ranking"]
        )
        failures = self.module.regressions(measurements, self.document, False)
        self.assertTrue(
            any("the 85% and 75% Go floors have a" in failure for failure in failures)
        )


class ProfileParsingTests(unittest.TestCase):
    """The arithmetic under each surface, so a wrong number is not a silent one."""

    def setUp(self) -> None:
        self.module = load_measurer()

    def test_percentage_is_computed_from_integers(self) -> None:
        self.assertEqual(self.module.percentage(292, 321), 90.97)
        self.assertEqual(self.module.percentage(51, 70), 72.86)
        self.assertEqual(self.module.percentage(0, 0), 0.0)
        self.assertEqual(self.module.percentage(7, 7), 100.0)

    def test_a_go_profile_totals_statements_rather_than_lines(self) -> None:
        profile = "\n".join(
            [
                "mode: set",
                "example.com/m/a.go:10.20,12.3 4 1",
                "example.com/m/a.go:14.20,16.3 3 0",
                "example.com/m/b/b.go:1.1,2.2 3 2",
            ]
        )
        covered, total, packages = self.module.read_go_profile(profile)
        self.assertEqual((covered, total), (7, 10))
        self.assertEqual(packages, ["example.com/m", "example.com/m/b"])

    def test_a_go_profile_with_only_a_header_totals_nothing(self) -> None:
        self.assertEqual(self.module.read_go_profile("mode: set\n"), (0, 0, []))

    def test_only_test_executables_are_collected_from_the_cargo_stream(self) -> None:
        stream = "\n".join(
            [
                json.dumps(
                    {
                        "reason": "compiler-artifact",
                        "executable": "/t/lib-1",
                        "profile": {"test": True},
                    }
                ),
                json.dumps(
                    {
                        "reason": "compiler-artifact",
                        "executable": "/t/bin-1",
                        "profile": {"test": False},
                    }
                ),
                json.dumps(
                    {
                        "reason": "compiler-artifact",
                        "executable": None,
                        "profile": {"test": True},
                    }
                ),
                json.dumps({"reason": "build-finished", "success": True}),
                "not json at all",
            ]
        )
        self.assertEqual(self.module.test_binaries(stream), ["/t/lib-1"])


class EntryPointTests(unittest.TestCase):
    """The command-line surface, which is what CI actually runs."""

    def setUp(self) -> None:
        self.module = load_measurer()

    def test_an_unreadable_baseline_exits_non_zero_before_comparing(self) -> None:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        handle.write("{")
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = self.module.main(
                ["--baseline", handle.name, "--scope", "nothing-matches-this"]
            )
        self.assertEqual(code, 1)
        self.assertIn("invalid coverage baseline", err.getvalue())

    def test_write_refuses_to_record_an_unmeasured_scope(self) -> None:
        # Writing an absence into a ceiling is how a hole becomes invisible.
        document = baseline_document()
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        handle.write(json.dumps(document))
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        unmeasured = self.module.Measurement(
            scope="rust-vibeproof-core",
            language="rust",
            metric="line",
            measured=False,
            note="cargo is not on PATH",
        )
        err = io.StringIO()
        with redirect_stderr(err):
            code = self.module.write_baseline(Path(handle.name), document, [unmeasured])
        self.assertEqual(code, 1)
        self.assertIn("refusing to record unmeasured scope", err.getvalue())
        self.assertEqual(json.loads(Path(handle.name).read_text()), baseline_document())

    def test_write_keeps_the_floor_and_replaces_the_number(self) -> None:
        document = baseline_document()
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        handle.write(json.dumps(document))
        handle.close()
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        improved = self.module.Measurement(
            scope="rust-vibeproof-core",
            language="rust",
            metric="line",
            measured=True,
            percent=95.0,
            covered_units=305,
            total_units=321,
        )
        out = io.StringIO()
        with redirect_stdout(out):
            code = self.module.write_baseline(Path(handle.name), document, [improved])
        self.assertEqual(code, 0)
        written = json.loads(Path(handle.name).read_text())["scopes"][
            "rust-vibeproof-core"
        ]
        self.assertEqual(written["percent"], 95.0)
        self.assertEqual(written["covered_units"], 305)
        self.assertEqual(written["floor_percent"], 90.0)
        self.assertEqual(written["floor_source"], "docs/verification/TEST_STRATEGY.md")


class UnmeasurableToolchainTests(unittest.TestCase):
    """Every measurer returns an explained absence rather than a zero."""

    def setUp(self) -> None:
        self.module = load_measurer()

    def test_an_empty_tree_measures_nothing_and_says_why(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory)
            rust = self.module.measure_rust(empty)
            go = self.module.measure_go(empty)
        self.assertFalse(rust.measured)
        self.assertIsNone(rust.percent)
        self.assertIn("Cargo.toml", rust.note)
        self.assertFalse(go.measured)
        self.assertIsNone(go.percent)
        self.assertIn("go.mod", go.note)

    def test_an_interpreter_without_coverage_is_unmeasured_rather_than_zero(
        self,
    ) -> None:
        measurement = self.module.measure_python(
            ROOT, python=sys.executable + "-does-not-exist"
        )
        self.assertFalse(measurement.measured)
        self.assertIn("coverage.py is not importable", measurement.note)

    def test_an_unmeasured_measurement_serialises_without_a_percent(self) -> None:
        payload = self.module.Measurement(
            scope="go-apps-api",
            language="go",
            metric="statement",
            measured=False,
            note="go is not on PATH",
        ).as_json()
        self.assertNotIn("percent", payload)
        self.assertNotIn("total_units", payload)
        self.assertEqual(payload["note"], "go is not on PATH")


if __name__ == "__main__":
    unittest.main()
