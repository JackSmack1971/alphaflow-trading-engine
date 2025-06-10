package orders

import (
    "errors"
    "sync"

    "github.com/google/uuid"
    "github.com/shopspring/decimal"
)

// Status represents order lifecycle stages.
type Status string

const (
    Pending   Status = "pending"
    Filled    Status = "filled"
    Cancelled Status = "cancelled"
)

// Order stores basic order data.
type Order struct {
    ID       string
    Symbol   string
    Side     string
    Quantity decimal.Decimal
    Price    decimal.Decimal
    Status   Status
}

// ErrDuplicate indicates order already exists.
var ErrDuplicate = errors.New("duplicate order")

// Manager tracks orders and prevents duplicates.
type Manager struct {
    mu     sync.RWMutex
    orders map[string]*Order
}

// NewManager creates a new order manager.
func NewManager() *Manager {
    return &Manager{orders: make(map[string]*Order)}
}

// Create adds a new order and returns generated ID.
func (m *Manager) Create(o *Order) (string, error) {
    m.mu.Lock()
    defer m.mu.Unlock()
    if o.ID == "" {
        o.ID = uuid.NewString()
    }
    if _, ok := m.orders[o.ID]; ok {
        return "", ErrDuplicate
    }
    o.Status = Pending
    m.orders[o.ID] = o
    return o.ID, nil
}

// UpdateStatus updates existing order state.
func (m *Manager) UpdateStatus(id string, status Status) error {
    m.mu.Lock()
    defer m.mu.Unlock()
    ord, ok := m.orders[id]
    if !ok {
        return errors.New("order not found")
    }
    ord.Status = status
    return nil
}

// Get returns an order by id.
func (m *Manager) Get(id string) (*Order, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()
    ord, ok := m.orders[id]
    return ord, ok
}


