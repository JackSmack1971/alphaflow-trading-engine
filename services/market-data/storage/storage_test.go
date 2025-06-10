package storage

import "testing"

func TestStore(t *testing.T) {
	s, err := New(":memory:")
	if err != nil {
		t.Fatal(err)
	}
	if err := s.Save("BTCUSDT", []byte("test")); err != nil {
		t.Fatal(err)
	}
	hist, err := s.History("BTCUSDT", 1)
	if err != nil || len(hist) != 1 {
		t.Fatalf("unexpected: %v", err)
	}
	if string(hist[0]) != "test" {
		t.Fatal("wrong data")
	}
}
