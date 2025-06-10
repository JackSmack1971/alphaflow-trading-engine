package websocket

import (
	"context"
	"fmt"
	"log"
	"net/url"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"

	backoff "github.com/cenkalti/backoff/v4"
	"github.com/gorilla/websocket"
	"github.com/prometheus/client_golang/prometheus"

	"github.com/alphaflow-trading/market-data/cache"
	"github.com/alphaflow-trading/market-data/calendar"
	"github.com/alphaflow-trading/market-data/config"
	"github.com/alphaflow-trading/market-data/handlers"
	"github.com/alphaflow-trading/market-data/publisher"
	"github.com/alphaflow-trading/market-data/storage"
	"github.com/alphaflow-trading/market-data/validation"
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
	val    *validation.Validator
	store  *storage.Store
	cache  *cache.Cache
	cal    calendar.Calendar
	log    *log.Logger
}

type subscribeMsg struct {
	Method string   `json:"method"`
	Params []string `json:"params"`
	ID     int      `json:"id"`
}

func New(cfg *config.Config, pub publisher.Publisher, path string) *Client {
	cal, _ := calendar.New(cfg.MarketOpen, cfg.MarketClose)
	id := uuid.NewString()
	logger := log.New(os.Stdout, fmt.Sprintf("cid:%s ", id), log.LstdFlags)
	store, _ := storage.New(path)
	return &Client{
		cfg:   cfg,
		pub:   pub,
		val:   validation.New(),
		store: store,
		cache: cache.New(time.Minute),
		cal:   cal,
		log:   logger,
	}
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
	urls := []string{c.cfg.BaseURL}
	if c.cfg.SecondaryURL != "" {
		urls = append(urls, c.cfg.SecondaryURL)
	}
	for _, baseURL := range urls {
		base, err := url.Parse(baseURL)
		if err != nil {
			continue
		}
		u := url.URL{Scheme: base.Scheme, Host: base.Host, Path: "/stream"}
		q := u.Query()
		q.Set("streams", strings.Join(streams, "/"))
		u.RawQuery = q.Encode()
		conn, _, err := websocket.DefaultDialer.DialContext(c.ctx, u.String(), nil)
		if err == nil {
			connectedGauge.Set(1)
			c.conn = conn
			return nil
		}
		c.log.Printf("connect error to %s: %v", baseURL, err)
	}
	connectedGauge.Set(0)
	return fmt.Errorf("all connections failed")
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
	if !c.cal.IsOpen(time.Now()) {
		return
	}
	out, symbol, err := c.val.Validate(msg)
	if err != nil {
		c.log.Printf("validation error: %v", err)
		return
	}
	normalized, err := handlers.Normalize(out)
	if err != nil {
		c.log.Printf("normalize error: %v", err)
		return
	}
	if err := c.store.Save(symbol, normalized); err != nil {
		c.log.Printf("store error: %v", err)
	}
	c.cache.Set(symbol, normalized)
	if err := c.pub.Publish(c.ctx, normalized); err != nil {
		c.log.Printf("publish error: %v", err)
	}
}

func (c *Client) Stop() {
	c.cancel()
	c.mu.Lock()
	if c.conn != nil {
		c.conn.Close()
	}
	if c.store != nil {
		c.store.DB().Close()
	}
	c.mu.Unlock()
}
