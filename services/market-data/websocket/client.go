package websocket

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/url"
	"strings"
	"sync"
	"time"

	backoff "github.com/cenkalti/backoff/v4"
	"github.com/gorilla/websocket"
	"github.com/prometheus/client_golang/prometheus"

	"github.com/alphaflow-trading/market-data/config"
	"github.com/alphaflow-trading/market-data/handlers"
	"github.com/alphaflow-trading/market-data/publisher"
)

var (
	connectedGauge = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "market_data_ws_connected",
		Help: "WebSocket connection status",
	})
)

func init() {
	prometheus.MustRegister(connectedGauge)
}

type Client struct {
	cfg    *config.Config
	pub    publisher.Publisher
	mu     sync.Mutex
	conn   *websocket.Conn
	ctx    context.Context
	cancel context.CancelFunc
}

type subscribeMsg struct {
	Method string   `json:"method"`
	Params []string `json:"params"`
	ID     int      `json:"id"`
}

func New(cfg *config.Config, pub publisher.Publisher) *Client {
	return &Client{cfg: cfg, pub: pub}
}

func (c *Client) Start() error {
	c.ctx, c.cancel = context.WithCancel(context.Background())
	go c.loop()
	return nil
}

func (c *Client) loop() {
	bo := backoff.NewExponentialBackOff()
	for {
		if err := c.connect(); err != nil {
			wait := bo.NextBackOff()
			time.Sleep(wait)
			continue
		}
		bo.Reset()
		c.read()
	}
}

func (c *Client) connect() error {
	c.mu.Lock()
	defer c.mu.Unlock()
	streams := make([]string, 0, len(c.cfg.Symbols)*3)
	for _, s := range c.cfg.Symbols {
		streams = append(streams,
			fmt.Sprintf("%s@ticker", s),
			fmt.Sprintf("%s@depth", s),
			fmt.Sprintf("%s@trade", s))
	}
	base, err := url.Parse(c.cfg.BaseURL)
	if err != nil {
		return err
	}
	u := url.URL{Scheme: base.Scheme, Host: base.Host, Path: "/stream"}
	q := u.Query()
	q.Set("streams", strings.Join(streams, "/"))
	u.RawQuery = q.Encode()

	conn, _, err := websocket.DefaultDialer.DialContext(c.ctx, u.String(), nil)
	if err != nil {
		connectedGauge.Set(0)
		return err
	}
	connectedGauge.Set(1)
	c.conn = conn
	return nil
}

func (c *Client) read() {
	for {
		select {
		case <-c.ctx.Done():
			return
		default:
			_, msg, err := c.conn.ReadMessage()
			if err != nil {
				connectedGauge.Set(0)
				c.conn.Close()
				return
			}
			c.handleMessage(msg)
		}
	}
}

func (c *Client) handleMessage(msg []byte) {
	if !json.Valid(msg) {
		return
	}
	normalized, err := handlers.Normalize(msg)
	if err != nil {
		log.Printf("normalize error: %v", err)
		return
	}
	if err := c.pub.Publish(c.ctx, normalized); err != nil {
		log.Printf("publish error: %v", err)
	}
}

func (c *Client) Stop() {
	c.cancel()
	c.mu.Lock()
	if c.conn != nil {
		c.conn.Close()
	}
	c.mu.Unlock()
}
