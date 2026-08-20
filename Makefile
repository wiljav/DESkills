.PHONY: ci validate lint test links readme marketplace docs scaffold

# Python interpreter: prefer the local venv, fall back to system python3.
PYTHON ?= .venv/bin/python
ifeq ($(wildcard $(PYTHON)),)
PYTHON := python3
endif

RUFF := $(PYTHON) -m ruff

# Run the full local validation pipeline (CI parity).
ci: validate lint test links readme marketplace

# Validate SKILL.md frontmatter + registry sync against schema.
validate:
	$(PYTHON) tools/validate_skills.py --catalog catalog.yaml

# Lint Python; markdownlint requires npm i -g markdownlint-cli2 (CI runs it
# via DavidAnson/markdownlint-cli2-action).
lint:
	$(RUFF) check tools
	$(RUFF) check skills --config pyproject.toml
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint '**/*.md' --ignore node_modules; \
	else \
		echo "WARN: markdownlint not installed; skipping (CI runs it)"; \
	fi

# Run all tests (tooling + skill scripts).
test:
	$(PYTHON) -m pytest tools/tests -q
	$(PYTHON) tools/run_script_tests.py

# Check internal markdown links across skills.
links:
	$(PYTHON) tools/check_links.py

# Ensure the README index is up to date.
readme:
	$(PYTHON) tools/generate_readme.py --catalog catalog.yaml --check

# Validate plugin marketplace manifests.
marketplace:
	$(PYTHON) tools/validate_marketplace.py

# Regenerate the README index from the catalog.
docs:
	$(PYTHON) tools/generate_readme.py --catalog catalog.yaml

# Scaffold a new skill: make scaffold DOMAIN=orchestration NAME=my-skill
scaffold:
	$(PYTHON) tools/scaffold_skill.py --domain $(DOMAIN) --name $(NAME) --catalog catalog.yaml