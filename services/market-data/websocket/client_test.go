package websocket

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/stretchr/testify/require"

	"github.com/alphaflow-trading/market-data/config"
)

type mockPublisher struct{ msgs chan []byte }

func (m *mockPublisher) Publish(_ context.Context, msg []byte) error {
	m.msgs <- msg
	return nil
}

func TestClientReceives(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		up := websocket.Upgrader{}
		c, _ := up.Upgrade(w, r, nil)
		defer c.Close()
		c.WriteMessage(websocket.TextMessage, []byte("{\"s\":\"BTCUSDT\",\"p\":100}"))
		time.Sleep(50 * time.Millisecond)
	}))
	defer srv.Close()

	url := "ws" + srv.URL[4:]
	cfg := &config.Config{Symbols: []string{"btcusdt"}, BaseURL: url, MarketOpen: "00:00", MarketClose: "23:59"}
	pub := &mockPublisher{msgs: make(chan []byte, 1)}
	client := New(cfg, pub, ":memory:")
	require.NoError(t, client.Start())
	defer client.Stop()
	select {
	case <-time.After(time.Second):
		t.Fatal("timeout")
	case msg := <-pub.msgs:
		require.JSONEq(t, "{\"s\":\"BTCUSDT\",\"p\":100}", string(msg))
	}
}
