# Market Data Collector Service

This service connects to Binance WebSocket streams and publishes normalized market data to Redis.

## Environment Variables
- `MD_SYMBOLS` - comma separated symbols e.g. `btcusdt,ethusdt`
- `REDIS_ADDR` - Redis connection address
- `REDIS_CHANNEL` - Redis pub/sub channel
- `BINANCE_WS` - Binance WebSocket base URL (for tests)

## Development
```bash
make test-market-data
make benchmark-throughput
```
