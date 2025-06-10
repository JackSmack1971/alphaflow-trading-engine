package validation

import (
    "testing"

    "github.com/shopspring/decimal"
    "github.com/alphaflow-trading/order-execution/orders"
)

func TestValidator(t *testing.T) {
    v := New(decimal.NewFromInt(10))
    ord := &orders.Order{Quantity: decimal.NewFromInt(5)}
    if err := v.Validate(ord, decimal.NewFromInt(6)); err == nil {
        t.Fatal("expected limit error")
    }
    if err := v.Validate(ord, decimal.NewFromInt(2)); err != nil {
        t.Fatal(err)
    }
}

