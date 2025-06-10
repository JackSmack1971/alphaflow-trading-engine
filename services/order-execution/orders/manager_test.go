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

func TestManager_FillAndReconcile(t *testing.T) {
	m := NewManager()
	id, err := m.Create(&Order{Symbol: "ETHUSDT", Side: "BUY", Quantity: decimal.NewFromInt(2), Price: decimal.NewFromInt(10)})
	if err != nil {
		t.Fatal(err)
	}
	if err := m.AddFill(id, decimal.NewFromInt(1), decimal.NewFromInt(10)); err != nil {
		t.Fatal(err)
	}
	ord, _ := m.Get(id)
	if ord.Status != Partial {
		t.Fatalf("expected partial got %s", ord.Status)
	}
	if err := m.Reconcile(id, Filled); err != nil {
		t.Fatal(err)
	}
	ord, _ = m.Get(id)
	if ord.Status != Filled {
		t.Fatalf("expected filled got %s", ord.Status)
	}
}

func TestManager_Cancel(t *testing.T) {
	m := NewManager()
	id, err := m.Create(&Order{Symbol: "BTCUSDT", Side: "BUY", Quantity: decimal.NewFromInt(1), Price: decimal.NewFromInt(1)})
	if err != nil {
		t.Fatal(err)
	}
	if err := m.Cancel(id); err != nil {
		t.Fatal(err)
	}
	ord, _ := m.Get(id)
	if ord.Status != Cancelled {
		t.Fatalf("expected cancelled got %s", ord.Status)
	}
}
