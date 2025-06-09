# AlphaFlow Trading Engine

AlphaFlow is a modular algorithmic trading bot. The repository is organized into individual services as defined in [AGENTS.md](AGENTS.md).

## Setup

1. Copy `.env.example` to `.env` and provide your configuration values.
2. Run `make setup` to install dependencies and pre-commit hooks.
3. Launch the development stack with `docker compose up --build`.

## Development Commands

- `make lint` - run linting via pre-commit
- `make test` - execute unit tests with coverage
- `make validate-structure` - verify required folders exist
- `make docker-up` - start local Docker services

## Security

No real API keys are stored in the repository. Use environment variables and the provided `.env.example` template. Pre-commit hooks include secret scanning using `detect-secrets`.
