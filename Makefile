.PHONY: setup lint test validate-structure docker-up

setup:
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

lint:
	pre-commit run --all-files

test:
	pytest --cov=tools/scripts --cov-report=term-missing

validate-structure:
	python tools/scripts/validate_structure.py

docker-up:
	docker compose up --build
