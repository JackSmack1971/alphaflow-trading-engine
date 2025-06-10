package calendar

import "testing"
import "time"

func TestCalendar(t *testing.T) {
	c, err := New("09:30", "16:00")
	if err != nil {
		t.Fatal(err)
	}
	open := time.Date(2023, 1, 1, 10, 0, 0, 0, time.UTC)
	if !c.IsOpen(open) {
		t.Fatal("should be open")
	}
	closed := time.Date(2023, 1, 1, 17, 0, 0, 0, time.UTC)
	if c.IsOpen(closed) {
		t.Fatal("should be closed")
	}
}
