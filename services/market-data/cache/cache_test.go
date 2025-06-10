package cache

import (
	"testing"
	"time"
)

func TestCache(t *testing.T) {
	c := New(100 * time.Millisecond)
	c.Set("k", []byte("v"))
	if v, ok := c.Get("k"); !ok || string(v) != "v" {
		t.Fatal("cache miss")
	}
	time.Sleep(150 * time.Millisecond)
	if _, ok := c.Get("k"); ok {
		t.Fatal("expected expire")
	}
}
