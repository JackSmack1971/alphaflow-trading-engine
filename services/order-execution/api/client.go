package api

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	backoff "github.com/cenkalti/backoff/v4"
)

// Client wraps HTTP interactions with Binance REST API.
type Client struct {
	httpClient *http.Client
	apiKey     string
	secretKey  string
	baseURL    string
}

// New creates a new API client using environment variables.
func New() (*Client, error) {
	key := os.Getenv("BINANCE_API_KEY")
	secret := os.Getenv("BINANCE_SECRET_KEY")
	if key == "" || secret == "" {
		return nil, errors.New("missing API credentials")
	}
	base := os.Getenv("BINANCE_REST_URL")
	if base == "" {
		base = "https://api.binance.com"
	}
	return &Client{
		httpClient: &http.Client{Timeout: 5 * time.Second},
		apiKey:     key,
		secretKey:  secret,
		baseURL:    base,
	}, nil
}

// OrderRequest represents an order to submit.
type OrderRequest struct {
	Symbol   string
	Side     string
	Quantity string
	Price    string
	ID       string
}

// OrderResponse captures Binance order response.
type OrderResponse struct {
	OrderID int64 `json:"orderId"`
	Status  string
}

// APIError describes failures returned by Binance.
type APIError struct{ Err error }

func (e *APIError) Error() string { return e.Err.Error() }

// PlaceOrder sends an order with retries and exponential backoff.
func (c *Client) PlaceOrder(ctx context.Context, o OrderRequest) (*OrderResponse, error) {
	var resp OrderResponse
	operation := func() error {
		data := url.Values{}
		data.Set("symbol", o.Symbol)
		data.Set("side", o.Side)
		data.Set("quantity", o.Quantity)
		data.Set("price", o.Price)
		data.Set("newClientOrderId", o.ID)
		r, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/api/v3/order", strings.NewReader(data.Encode()))
		if err != nil {
			return backoff.Permanent(err)
		}
		r.Header.Set("X-MBX-APIKEY", c.apiKey)
		r.Header.Set("Content-Type", "application/x-www-form-urlencoded")
		res, err := c.httpClient.Do(r)
		if err != nil {
			return err
		}
		defer res.Body.Close()
		if res.StatusCode >= http.StatusInternalServerError {
			return errors.New("server error")
		}
		if res.StatusCode != http.StatusOK {
			return backoff.Permanent(&APIError{Err: errors.New(res.Status)})
		}
		return json.NewDecoder(res.Body).Decode(&resp)
	}
	b := backoff.WithContext(backoff.NewExponentialBackOff(), ctx)
	if err := backoff.Retry(operation, b); err != nil {
		return nil, err
	}
	return &resp, nil
}

// GetOrder retrieves order status from the exchange.
func (c *Client) GetOrder(ctx context.Context, id, symbol string) (*OrderResponse, error) {
	var resp OrderResponse
	operation := func() error {
		q := url.Values{}
		q.Set("symbol", symbol)
		q.Set("origClientOrderId", id)
		r, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+"/api/v3/order?"+q.Encode(), nil)
		if err != nil {
			return backoff.Permanent(err)
		}
		r.Header.Set("X-MBX-APIKEY", c.apiKey)
		res, err := c.httpClient.Do(r)
		if err != nil {
			return err
		}
		defer res.Body.Close()
		if res.StatusCode >= http.StatusInternalServerError {
			return errors.New("server error")
		}
		if res.StatusCode != http.StatusOK {
			return backoff.Permanent(&APIError{Err: errors.New(res.Status)})
		}
		return json.NewDecoder(res.Body).Decode(&resp)
	}
	b := backoff.WithContext(backoff.NewExponentialBackOff(), ctx)
	if err := backoff.Retry(operation, b); err != nil {
		return nil, err
	}
	return &resp, nil
}

// CancelOrder cancels an open order on the exchange.
func (c *Client) CancelOrder(ctx context.Context, id, symbol string) error {
	operation := func() error {
		q := url.Values{}
		q.Set("symbol", symbol)
		q.Set("origClientOrderId", id)
		r, err := http.NewRequestWithContext(ctx, http.MethodDelete, c.baseURL+"/api/v3/order?"+q.Encode(), nil)
		if err != nil {
			return backoff.Permanent(err)
		}
		r.Header.Set("X-MBX-APIKEY", c.apiKey)
		res, err := c.httpClient.Do(r)
		if err != nil {
			return err
		}
		defer res.Body.Close()
		if res.StatusCode >= http.StatusInternalServerError {
			return errors.New("server error")
		}
		if res.StatusCode != http.StatusOK {
			return backoff.Permanent(&APIError{Err: errors.New(res.Status)})
		}
		return nil
	}
	b := backoff.WithContext(backoff.NewExponentialBackOff(), ctx)
	return backoff.Retry(operation, b)
}
