package config

import (
	"errors"
	"os"
	"strings"
)

type Config struct {
	Symbols   []string
	RedisAddr string
	Channel   string
	BaseURL   string
}

func Load() (*Config, error) {
	symbols := os.Getenv("MD_SYMBOLS")
	if symbols == "" {
		return nil, errors.New("MD_SYMBOLS required")
	}
	addr := os.Getenv("REDIS_ADDR")
	if addr == "" {
		addr = "localhost:6379"
	}
	channel := os.Getenv("REDIS_CHANNEL")
	if channel == "" {
		channel = "market-data"
	}
	base := os.Getenv("BINANCE_WS")
	if base == "" {
		base = "wss://stream.binance.com:9443"
	}
	return &Config{Symbols: strings.Split(symbols, ","), RedisAddr: addr, Channel: channel, BaseURL: base}, nil
}
