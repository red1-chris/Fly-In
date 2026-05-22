PYTHON = python3
MAIN_SCRIPT = main.py

.PHONY: install run debug clean lint build

install:
	uv sync

run: install
	uv run $(PYTHON) $(MAIN_SCRIPT)

exo: install
	uv run $(PYTHON) $(MAIN_SCRIPT) --capacity-info

debug:
	uv run $(PYTHON) -m pdb $(MAIN_SCRIPT)

clean:
	rm -rf __pycache__ .mypy_cache .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 . --exclude=.venv,venv,__pycache__,build,dist
	uv run mypy . --ignore-missing-imports --exclude '(.venv|venv|build)/'

build:
	uv build