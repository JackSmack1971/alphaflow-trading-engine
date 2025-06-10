package portfolio

import (
    "testing"

    "github.com/shopspring/decimal"
)

func TestPortfolio_Update(t *testing.T) {
    p := New()
    p.Update("BTCUSDT", decimal.NewFromInt(1))
    p.Update("BTCUSDT", decimal.NewFromInt(2))
    qty := p.Get("BTCUSDT")
    if !qty.Equal(decimal.NewFromInt(3)) {
        t.Fatalf("expected 3 got %s", qty)
    }
}

