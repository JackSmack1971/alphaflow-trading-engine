package auth

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestGenerateValidate(t *testing.T) {
	token, err := Generate("secret", "svc", time.Second)
	if err != nil {
		t.Fatal(err)
	}
	if err := Validate(token, "secret", "svc"); err != nil {
		t.Fatal(err)
	}
	if err := Validate(token, "secret", "other"); err == nil {
		t.Fatal("expected issuer error")
	}
}

func TestMiddleware(t *testing.T) {
	token, _ := Generate("secret", "svc", time.Second)
	h := Middleware("secret", "svc")(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(200)
	}))
	r := httptest.NewRequest("GET", "/", nil)
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	if w.Result().StatusCode != 401 {
		t.Fatalf("expected 401 got %d", w.Result().StatusCode)
	}
	r = httptest.NewRequest("GET", "/", nil)
	r.Header.Set("Authorization", "Bearer "+token)
	w = httptest.NewRecorder()
	h.ServeHTTP(w, r)
	if w.Result().StatusCode != 200 {
		t.Fatalf("expected 200 got %d", w.Result().StatusCode)
	}
}
