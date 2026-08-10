.DEFAULT_GOAL := help
PY ?= python3
VENV := .venv
VENV_PY := $(VENV)/bin/python3

.PHONY: help doctor validate plan evals test coverage venv clean-venv

help: ## Show available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  This repository is in planning contract repair. No target builds or runs a product."
	@echo "  See docs/project/STATUS.md for what is and is not implemented."

doctor: ## Repository invariants (no dependencies required)
	$(PY) scripts/repository/doctor.py

$(VENV_PY):
	$(PY) -m venv $(VENV)
	$(VENV)/bin/pip install --quiet --upgrade pip
	$(VENV)/bin/pip install --quiet -r requirements-planning.txt

venv: $(VENV_PY) ## Create the planning virtualenv

validate: $(VENV_PY) ## Run the planning validator suite
	$(VENV_PY) scripts/repository/doctor.py
	$(VENV_PY) scripts/repository/validate_p1140f_authority.py
	$(VENV_PY) scripts/repository/validate_t20_contract.py
	$(VENV_PY) scripts/repository/validate_p1140e_contracts.py
	$(VENV_PY) scripts/repository/validate_artifact_quarantine.py
	$(VENV_PY) scripts/repository/validate_repair_task_binding.py
	$(VENV_PY) scripts/repository/validate_batch_challenge_binding.py
	$(VENV_PY) scripts/repository/validate_planning_coverage.py
	$(VENV_PY) scripts/repository/validate_state_vocabularies.py
	$(VENV_PY) scripts/repository/validate_oauth_identity_contract.py
	$(VENV_PY) scripts/repository/validate_work_unit_status.py
	$(VENV_PY) scripts/repository/validate_load_scenarios.py
	$(VENV_PY) scripts/repository/validate_planning_artifacts.py --allow-no-postgres
	$(VENV_PY) scripts/ci/run_evals.py --validate-registry
	@echo ""
	@echo "The cross-reference dangle set is pinned at empty. Any dangling reference"
	@echo "this reports is a defect introduced by the change under test."
	$(VENV_PY) scripts/repository/validate_cross_references.py
	@echo ""
	@echo "Skipped locally: the PostgreSQL DDL stage of validate_planning_artifacts.py."
	@echo "CI runs it against a real instance; set PLANNING_DATABASE_URL to run it here."
	@echo "Run 'make test' for the unit suite and 'make evals' for the eval registry."

plan: $(VENV_PY) ## Regenerate the deterministic work-unit issue plan
	$(VENV_PY) scripts/repository/generate_issue_plan.py

evals: $(VENV_PY) ## Validate the evaluation registry
	$(VENV_PY) scripts/ci/run_evals.py --validate-registry

test: $(VENV_PY) ## Run the validator unit tests
	$(VENV_PY) -m unittest discover -s tests

coverage: $(VENV_PY) ## Measure coverage per surface against the recorded ceiling
	@echo "Measuring Python, Rust and Go. This re-runs the unit suite under coverage"
	@echo "and builds the Rust workspace instrumented, so it takes minutes rather than"
	@echo "seconds. It is deliberately not part of 'make validate'."
	@echo ""
	@echo "Rust needs 'rustup component add llvm-tools-preview'. Without it the Rust"
	@echo "surface reports unmeasured, which fails: an absent toolchain is an absence"
	@echo "of evidence, never a pass. Pass --allow-unmeasured only when that is true"
	@echo "and you are saying so."
	$(VENV_PY) scripts/ci/measure_coverage.py

clean-venv: ## Remove the planning virtualenv
	rm -rf $(VENV)
