package validation

import (
    "errors"

    "github.com/shopspring/decimal"
    "github.com/alphaflow-trading/order-execution/orders"
)

// Validator performs risk checks before order placement.
type Validator struct {
    maxPosition decimal.Decimal
}

// New creates a validator with a position limit.
func New(limit decimal.Decimal) *Validator {
    return &Validator{maxPosition: limit}
}

// Validate ensures the order does not exceed limits.
func (v *Validator) Validate(o *orders.Order, current decimal.Decimal) error {
    next := current.Add(o.Quantity)
    if next.GreaterThan(v.maxPosition) {
        return errors.New("position limit exceeded")
    }
    return nil
}


