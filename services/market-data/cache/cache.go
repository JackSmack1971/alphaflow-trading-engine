package cache

import (
	"sync"
	"time"
)

type entry struct {
	data []byte
	exp  time.Time
}

type Cache struct {
	ttl time.Duration
	m   sync.Map
}

func New(ttl time.Duration) *Cache {
	return &Cache{ttl: ttl}
}

func (c *Cache) Set(key string, val []byte) {
	c.m.Store(key, entry{data: val, exp: time.Now().Add(c.ttl)})
}

func (c *Cache) Get(key string) ([]byte, bool) {
	v, ok := c.m.Load(key)
	if !ok {
		return nil, false
	}
	e := v.(entry)
	if time.Now().After(e.exp) {
		c.m.Delete(key)
		return nil, false
	}
	return e.data, true
}
