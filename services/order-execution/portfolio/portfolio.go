package portfolio

import (
    "sync"

    "github.com/shopspring/decimal"
)

// Position represents asset holding.
type Position struct {
    Symbol   string
    Quantity decimal.Decimal
}

// Portfolio tracks positions per symbol.
type Portfolio struct {
    mu        sync.RWMutex
    positions map[string]decimal.Decimal
}

// New creates an empty portfolio.
func New() *Portfolio {
    return &Portfolio{positions: make(map[string]decimal.Decimal)}
}

// Update modifies position quantity.
func (p *Portfolio) Update(symbol string, qty decimal.Decimal) {
    p.mu.Lock()
    defer p.mu.Unlock()
    val := p.positions[symbol]
    p.positions[symbol] = val.Add(qty)
}

// Get retrieves current quantity for a symbol.
func (p *Portfolio) Get(symbol string) decimal.Decimal {
    p.mu.RLock()
    defer p.mu.RUnlock()
    return p.positions[symbol]
}


