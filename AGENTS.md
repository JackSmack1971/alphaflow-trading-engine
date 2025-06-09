# Algorithmic Trading Bot - Developer Guide

## 🚨 Critical Security Notice
**This system handles real financial assets. Security violations can result in financial loss.**
- NEVER commit API keys, secrets, or configuration with real credentials
- Always use sandbox/testnet for development and testing
- Verify all financial calculations with unit tests
- Implement proper audit logging for all trades

## Project Architecture

### System Components
```
Market Data Collector → Strategy Engine → Order Execution Engine
                           ↓                    ↓
                    Risk Manager ←→ State Persistence
                           ↓
                    Observability Stack
```

### Repository Structure
```
/
├── services/
│   ├── market-data/          # WebSocket data collection
│   ├── strategy-engine/      # Trading algorithms
│   ├── order-execution/      # Binance REST API integration
│   ├── risk-manager/         # Risk assessment and limits
│   └── gateway/              # Optional API gateway
├── shared/
│   ├── proto/                # Protocol buffer definitions
│   ├── schemas/              # JSON schemas for API contracts
│   └── utils/                # Common utilities
├── infrastructure/
│   ├── docker/               # Container definitions
│   ├── k8s/                  # Kubernetes manifests
│   └── terraform/            # Infrastructure as code
└── tools/
    ├── scripts/              # Deployment and utility scripts
    └── monitoring/           # Observability configuration
```

## Technology Stack Decisions

### Programming Languages
- **Python**: Strategy Engine (pandas, NumPy for analysis)
- **Go**: Market Data Collector, Order Execution (performance-critical)
- **Node.js/TypeScript**: API Gateway, Web dashboards

### Data Storage
- **Redis**: Real-time state, caching, pub/sub
- **PostgreSQL**: Persistent trade history, configuration
- **InfluxDB**: Time-series metrics and trade data

### Observability
- **OpenTelemetry**: Distributed tracing across services
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and alerting
- **Loki**: Centralized logging

## Development Guidelines

### Financial Domain Rules
- **Decimal Precision**: Use `decimal.Decimal` in Python, `big.Rat` in Go - NEVER float for money
- **Currency Handling**: Always specify base/quote currency pairs explicitly
- **Rate Limiting**: Respect Binance API limits: 1200 requests/minute, 10 orders/second
- **Order Validation**: Validate all orders against account balance and risk limits
- **Idempotency**: All trading operations must be idempotent with client order IDs

### API Contract Standards
```protobuf
// Example: All services communicate via protobuf
service StrategyEngine {
  rpc GenerateSignal(MarketData) returns (TradingSignal);
  rpc UpdateParameters(StrategyConfig) returns (UpdateResponse);
}
```

### Error Handling Patterns
```python
# Python Example
from typing import Result
import backoff

@backoff.expo(exception=BinanceAPIException, max_tries=3)
def place_order(order: Order) -> Result[OrderResponse, OrderError]:
    # Implementation with proper error handling
```

### Testing Requirements
- **Unit Tests**: 100% coverage for financial calculations
- **Integration Tests**: Mock Binance API responses
- **End-to-End Tests**: Use Binance Testnet
- **Chaos Testing**: Simulate network failures, API timeouts
- **Performance Tests**: Latency < 100ms for order execution

## Security Implementation

### Secrets Management
```bash
# Environment variables for development
BINANCE_API_KEY_TESTNET=your_testnet_key
BINANCE_SECRET_KEY_TESTNET=your_testnet_secret
REDIS_PASSWORD=${vault:redis/password}
DB_CONNECTION_STRING=${vault:postgres/connection}
```

### API Key Permissions
- **Testnet**: Full permissions for development
- **Production**: Spot trading only, no withdrawals
- **Strategy Testing**: Read-only market data access

## Risk Management Integration

### Budget Guardrails
```python
class RiskManager:
    def validate_order(self, order: Order) -> bool:
        # Check position limits
        # Validate against daily loss limits
        # Ensure sufficient balance
        # Apply portfolio diversification rules
```

### Circuit Breakers
- **Strategy Level**: Stop trading if consecutive losses exceed threshold
- **Account Level**: Halt all trading if daily loss exceeds limit
- **System Level**: Emergency stop via manual intervention

## Observability Requirements

### Metrics to Track
- `trading_signals_generated_total{strategy, symbol}`
- `orders_placed_total{status, symbol}`
- `execution_latency_seconds{operation}`
- `api_requests_total{endpoint, status_code}`
- `balance_usd{asset}`
- `pnl_realized_usd{strategy, timeframe}`

### Logging Standards
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "level": "INFO",
  "service": "order-execution",
  "correlation_id": "uuid-here",
  "event": "order_placed",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": "0.001",
  "price": "45000.00",
  "order_id": "binance-order-id"
}
```

### Alerting Rules
- Failed order executions
- API rate limit warnings
- Unusual trading volumes
- Risk limit breaches
- System health degradation

## Deployment & Operations

### Environment Strategy
- **Local**: Docker Compose with mock services
- **Development**: Kubernetes with Binance Testnet
- **Staging**: Production-like with paper trading
- **Production**: Full deployment with real trading

### Validation Scripts
```bash
# Pre-deployment checks
./tools/scripts/validate-config.sh
./tools/scripts/test-api-connectivity.sh
./tools/scripts/verify-risk-limits.sh
```

### Configuration Management
- Use Helm charts for Kubernetes deployments
- Environment-specific values in separate files
- Secrets injected via init containers
- Configuration validation on startup

## Development Workflow

### Branch Strategy
- `main`: Production releases only
- `develop`: Integration branch
- `feature/strategy-xyz`: New trading strategies
- `fix/risk-manager-bug`: Bug fixes
- `infra/monitoring-update`: Infrastructure changes

### Testing Pipeline
1. **Local Tests**: Unit tests, linting, type checking
2. **Integration Tests**: Component interaction tests
3. **Testnet Validation**: End-to-end with Binance Testnet
4. **Performance Tests**: Load testing and latency validation
5. **Security Scan**: Dependency vulnerabilities, secret detection

### Deployment Process
1. Merge to `develop` triggers staging deployment
2. Staging validation includes paper trading tests
3. Manual approval required for production deployment
4. Blue-green deployment with rollback capability
5. Post-deployment monitoring and validation

## Performance Requirements

### Latency Targets
- Market data processing: < 50ms
- Signal generation: < 100ms
- Order execution: < 200ms
- Risk validation: < 50ms

### Throughput Requirements
- Handle 1000+ market data updates/second
- Process 100+ strategy evaluations/second
- Execute 10+ orders/second (within Binance limits)

## Compliance & Audit

### Trade Record Keeping
- Immutable trade history in PostgreSQL
- Export capabilities for regulatory reporting
- Audit trail for all system decisions
- Data retention policies per jurisdiction

### Monitoring & Alerts
- Real-time P&L tracking
- Risk metric dashboards
- System health monitoring
- Compliance violation alerts

## Common Patterns

### Service Communication
```go
// Go example for async communication
type TradingSignal struct {
    Symbol    string    `json:"symbol"`
    Action    string    `json:"action"`
    Quantity  decimal.Decimal `json:"quantity"`
    Price     decimal.Decimal `json:"price"`
    Timestamp time.Time `json:"timestamp"`
}
```

### Error Recovery
- Implement exponential backoff for API calls
- Use dead letter queues for failed messages
- Graceful degradation when external services fail
- Automatic restart with state recovery

When working on this codebase, always prioritize:
1. **Financial Accuracy**: Verify all calculations
2. **Security**: Protect API keys and trading logic
3. **Observability**: Log everything for debugging
4. **Risk Management**: Implement safeguards first
5. **Performance**: Optimize for low latency
6. **Reliability**: Handle failures gracefully
