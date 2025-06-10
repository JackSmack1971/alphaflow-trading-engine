package main

import (
    "context"
    "log"
    "os"
    "os/signal"
    "syscall"

    "github.com/shopspring/decimal"

    "github.com/alphaflow-trading/order-execution/api"
    "github.com/alphaflow-trading/order-execution/orders"
    "github.com/alphaflow-trading/order-execution/portfolio"
    "github.com/alphaflow-trading/order-execution/validation"
)

func main() {
    ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer cancel()

    client, err := api.New()
    if err != nil {
        log.Fatal(err)
    }

    mgr := orders.NewManager()
    pf := portfolio.New()
    validator := validation.New(decimal.NewFromInt(100))

    // Example: consume a single signal from env for demo
    symbol := os.Getenv("TEST_SYMBOL")
    if symbol == "" {
        symbol = "BTCUSDT"
    }
    qty := decimal.NewFromFloat(0.001)
    order := &orders.Order{Symbol: symbol, Side: "BUY", Quantity: qty, Price: decimal.NewFromInt(0)}
    if err := validator.Validate(order, pf.Get(order.Symbol)); err != nil {
        log.Fatal(err)
    }
    id, err := mgr.Create(order)
    if err != nil {
        log.Fatal(err)
    }
    resp, err := client.PlaceOrder(ctx, api.OrderRequest{
        Symbol:   order.Symbol,
        Side:     order.Side,
        Quantity: order.Quantity.String(),
        Price:    order.Price.String(),
        ID:       id,
    })
    if err != nil {
        log.Fatal(err)
    }
    pf.Update(order.Symbol, order.Quantity)
    if err := mgr.UpdateStatus(id, orders.Filled); err != nil {
        log.Fatal(err)
    }
    log.Printf("order executed id=%d status=%s", resp.OrderID, resp.Status)
}


