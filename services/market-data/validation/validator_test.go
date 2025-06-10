package validation

import "testing"

func TestValidate(t *testing.T) {
	v := New()
	msg := []byte(`{"s":"BTCUSDT","p":100}`)
	out, sym, err := v.Validate(msg)
	if err != nil || sym != "BTCUSDT" || len(out) == 0 {
		t.Fatalf("unexpected error: %v", err)
	}
	bad := []byte(`{"s":"BTCUSDT","p":-1}`)
	if _, _, err := v.Validate(bad); err == nil {
		t.Fatal("expected error")
	}
	outlier := []byte(`{"s":"BTCUSDT","p":500}`)
	if _, _, err := v.Validate(outlier); err == nil {
		t.Fatal("expected outlier error")
	}
}
