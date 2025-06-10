package validation

import (
	"encoding/json"
	"errors"
	"math"
	"sync"
)

type Validator struct {
	mu  sync.Mutex
	avg map[string]float64
}

func New() *Validator {
	return &Validator{avg: make(map[string]float64)}
}

func (v *Validator) Validate(msg []byte) ([]byte, string, error) {
	var data map[string]interface{}
	if err := json.Unmarshal(msg, &data); err != nil {
		return nil, "", err
	}
	symbol, _ := data["s"].(string)
	price, ok := data["p"].(float64)
	if !ok || price <= 0 || math.IsNaN(price) {
		return nil, symbol, errors.New("invalid price")
	}
	v.mu.Lock()
	defer v.mu.Unlock()
	avg := v.avg[symbol]
	if avg == 0 {
		v.avg[symbol] = price
	} else {
		if math.Abs(price-avg)/avg > 0.2 {
			return nil, symbol, errors.New("outlier detected")
		}
		v.avg[symbol] = 0.8*avg + 0.2*price
	}
	out, err := json.Marshal(data)
	return out, symbol, err
}
