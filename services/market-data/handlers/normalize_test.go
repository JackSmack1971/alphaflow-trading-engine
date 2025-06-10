package handlers

import "testing"

func TestNormalize(t *testing.T) {
	input := []byte("{\"a\":1}")
	out, err := Normalize(input)
	if err != nil {
		t.Fatal(err)
	}
	if string(out) != string(input) {
		t.Fatalf("expected %s got %s", input, out)
	}
}
