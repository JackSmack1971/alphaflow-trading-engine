package api

import (
    "context"
    "net/http"
    "net/http/httptest"
    "os"
    "sync/atomic"
    "testing"
)

func TestPlaceOrder_Retry(t *testing.T) {
    var attempts int32
    srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if atomic.AddInt32(&attempts, 1) == 1 {
            w.WriteHeader(http.StatusInternalServerError)
            return
        }
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"orderId":1,"status":"FILLED"}`))
    }))
    defer srv.Close()
    os.Setenv("BINANCE_API_KEY", "k")
    os.Setenv("BINANCE_SECRET_KEY", "s")
    os.Setenv("BINANCE_REST_URL", srv.URL)

    c, err := New()
    if err != nil {
        t.Fatal(err)
    }
    ctx := context.Background()
    resp, err := c.PlaceOrder(ctx, OrderRequest{Symbol: "BTCUSDT", Side: "BUY", Quantity: "1", Price: "1", ID: "test"})
    if err != nil {
        t.Fatal(err)
    }
    if resp.OrderID != 1 || resp.Status != "FILLED" {
        t.Fatalf("unexpected response %+v", resp)
    }
    if attempts < 2 {
        t.Fatalf("expected retry, got %d attempts", attempts)
    }
}

