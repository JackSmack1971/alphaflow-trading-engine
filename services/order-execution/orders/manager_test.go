package orders

import (
    "testing"

    "github.com/shopspring/decimal"
)

func TestManager_CreateAndUpdate(t *testing.T) {
    m := NewManager()
    id, err := m.Create(&Order{Symbol: "BTCUSDT", Side: "BUY", Quantity: decimal.NewFromInt(1), Price: decimal.NewFromInt(1)})
    if err != nil {
        t.Fatal(err)
    }
    if _, err := m.Create(&Order{ID: id}); err == nil {
        t.Fatal("expected duplicate error")
    }
    if err := m.UpdateStatus(id, Filled); err != nil {
        t.Fatal(err)
    }
    ord, ok := m.Get(id)
    if !ok || ord.Status != Filled {
        t.Fatal("status not updated")
    }
}

