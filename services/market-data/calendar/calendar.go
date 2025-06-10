package calendar

import "time"

type Calendar struct {
	Open  time.Duration
	Close time.Duration
}

func New(open, close string) (Calendar, error) {
	o, err := time.Parse("15:04", open)
	if err != nil {
		return Calendar{}, err
	}
	c, err := time.Parse("15:04", close)
	if err != nil {
		return Calendar{}, err
	}
	return Calendar{Open: time.Duration(o.Hour())*time.Hour + time.Duration(o.Minute())*time.Minute,
		Close: time.Duration(c.Hour())*time.Hour + time.Duration(c.Minute())*time.Minute}, nil
}

func (cal Calendar) IsOpen(t time.Time) bool {
	d := time.Duration(t.Hour())*time.Hour + time.Duration(t.Minute())*time.Minute
	return d >= cal.Open && d <= cal.Close
}
