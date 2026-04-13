.DEFAULT_GOAL := help

# ------------------------------------------------------------------------------
# Variables
# ------------------------------------------------------------------------------
UV = uv
DBT = $(UV) run dbt
STREAMLIT = $(UV) run python -m streamlit
PROFILES_DIR = .

# ------------------------------------------------------------------------------
# Help Menu
# ------------------------------------------------------------------------------
.PHONY: help
help:
	@echo "------------------------------------------------------------------------------"
	@echo "       🤖 Analytics Engineering Portfolio - Development Workflows             "
	@echo "------------------------------------------------------------------------------"
	@echo "Setup & Environment:"
	@echo "  install          - Install dependencies using uv sync"
	@echo "  clean            - Remove .venv, target/, logs/, and __pycache__"
	@echo ""
	@echo "Application:"
	@echo "  app              - Launch the Streamlit Resume/Dashboard"
	@echo ""
	@echo "dbt Data Pipeline:"
	@echo "  run              - Run all dbt models (src -> dim -> mrt)"
	@echo "  test             - Run dbt data and schema tests"
	@echo "  build            - Execute 'dbt build' (run + test + seed + snapshot)"
	@echo "  debug            - Test connection to the local DuckDB database"
	@echo "  docs             - Generate and serve dbt documentation"
	@echo "  dbt-clean        - Remove dbt-generated artifacts (target/)"
	@echo "------------------------------------------------------------------------------"

# ------------------------------------------------------------------------------
# Setup & Environment
# ------------------------------------------------------------------------------
.PHONY: install
install:
	$(UV) sync

.PHONY: clean
clean:
	rm -rf .venv target/ dbt_packages/ logs/
	find . -type d -name "__pycache__" -exec rm -rf {} +

# ------------------------------------------------------------------------------
# Application
# ------------------------------------------------------------------------------
.PHONY: app
app:
	$(STREAMLIT) run Resume.py

# ------------------------------------------------------------------------------
# dbt Workflow
# ------------------------------------------------------------------------------
.PHONY: run
run:
	$(DBT) run --profiles-dir $(PROFILES_DIR)

.PHONY: test
test:
	$(DBT) test --profiles-dir $(PROFILES_DIR)

.PHONY: build
build:
	$(DBT) build --profiles-dir $(PROFILES_DIR)

.PHONY: debug
debug:
	$(DBT) debug --profiles-dir $(PROFILES_DIR)

.PHONY: docs
docs:
	$(DBT) docs generate --profiles-dir $(PROFILES_DIR)
	$(DBT) docs serve --profiles-dir $(PROFILES_DIR)

.PHONY: dbt-clean
dbt-clean:
	$(DBT) clean
