.PHONY: setup lint test validate-structure docker-up generate-protos test-shared validate-config test-vault-integration test-market-data benchmark-throughput test-execution test-api-integration

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

generate-protos:
	bash tools/scripts/generate_protos.sh

test-shared:
        PYTHONPATH=. pytest --cov=shared --cov-report=term-missing
validate-config:
	PYTHONPATH=. python tools/config-validator.py
test-vault-integration:
PYTHONPATH=. pytest tests/config/test_vault.py --cov=shared/config --cov-report=term-missing

test-market-data:
	cd services/market-data && go test ./... -cover

benchmark-throughput:
	cd services/market-data && go test -bench=. ./...

test-strategies:
		PYTHONPATH=. pytest tests/strategy_engine --cov=services/strategy-engine --cov-report=term-missing
backtest-validation:
		PYTHONPATH=. pytest tests/strategy_engine/test_backtesting.py --cov=services/strategy-engine/backtesting --cov-report=term-missing

test-execution:
	cd services/order-execution && go test ./... -cover
test-api-integration:
	cd services/order-execution && go test ./api -cover -run Integration

test-risk-scenarios:
	PYTHONPATH=. pytest tests/risk_manager/test_limits.py --cov='services/risk-manager' --cov-report=term-missing

test-emergency-stops:
	PYTHONPATH=. pytest tests/risk_manager/test_circuit_breaker.py --cov='services/risk-manager' --cov-report=term-missing

security-scan:
	gitleaks detect --no-git --config=gitleaks.toml

test-vault-rotation:
	PYTHONPATH=. pytest tests/security --cov=shared/security --cov-report=term-missing

deploy-monitoring:
	python tools/scripts/deploy_monitoring.py

test-alerts:
	python tools/scripts/test_alerts.py
