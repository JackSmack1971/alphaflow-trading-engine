# Risk Manager Service

This service enforces portfolio level risk controls for the trading engine.

## Features

- Position size and portfolio limits
- Daily loss and drawdown checks
- Concentration and trade velocity restrictions
- Circuit breaker for extreme drawdowns
- Simple reporting API for dashboards

Configuration is provided via environment variables:

- `POSITION_LIMIT_SYMBOL`
- `POSITION_LIMIT_TOTAL`
- `DAILY_LOSS_LIMIT`
- `CONCENTRATION_LIMIT`
- `VELOCITY_LIMIT`, `VELOCITY_WINDOW`
- `DRAWDOWN_LIMIT`
- `CIRCUIT_BREAKER_DRAWDOWN`
