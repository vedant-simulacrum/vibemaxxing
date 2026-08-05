.DEFAULT_GOAL := help
PY ?= python3
VENV := .venv
VENV_PY := $(VENV)/bin/python3

.PHONY: help doctor validate plan evals test venv clean-venv

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
	$(VENV_PY) scripts/repository/validate_planning_coverage.py
	$(VENV_PY) scripts/repository/validate_state_vocabularies.py
	$(VENV_PY) scripts/repository/validate_planning_artifacts.py --allow-no-postgres
	$(VENV_PY) scripts/ci/run_evals.py --validate-registry
	@echo ""
	@echo "Known failing at HEAD: the cross-reference validator reports three dangling"
	@echo "references it must not hide — ADR-015, which PF-039 has not authored yet,"
	@echo "and the superseded SR-001/SR-004 numbering in DOCUMENTATION.md."
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

clean-venv: ## Remove the planning virtualenv
	rm -rf $(VENV)
