package validation

import (
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/xeipuuv/gojsonschema"
)

var schema = gojsonschema.NewStringLoader(`{
  "type": "object",
  "properties": {"foo": {"type": "string"}},
  "required": ["foo"],
  "additionalProperties": false
}`)

func testHandler(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
}

func TestMiddlewareValid(t *testing.T) {
    mux := http.NewServeMux()
    mux.HandleFunc("/", testHandler)
    srv := Middleware(schema, 1024)(mux)
    r := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{"foo":"bar"}`))
    r.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    srv.ServeHTTP(w, r)
    if w.Result().StatusCode != http.StatusOK {
        t.Fatalf("expected 200 got %d", w.Result().StatusCode)
    }
}

func TestMiddlewareInvalid(t *testing.T) {
    mux := http.NewServeMux()
    mux.HandleFunc("/", testHandler)
    srv := Middleware(schema, 1024)(mux)
    r := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{"foo":1}`))
    r.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    srv.ServeHTTP(w, r)
    if w.Result().StatusCode != http.StatusBadRequest {
        t.Fatalf("expected 400 got %d", w.Result().StatusCode)
    }
}

func TestMiddlewareLarge(t *testing.T) {
    mux := http.NewServeMux()
    mux.HandleFunc("/", testHandler)
    srv := Middleware(schema, 10)(mux)
    r := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(`{"foo":"`+strings.Repeat("x", 20)+`"}`))
    r.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    srv.ServeHTTP(w, r)
    if w.Result().StatusCode != http.StatusRequestEntityTooLarge {
        t.Fatalf("expected 413 got %d", w.Result().StatusCode)
    }
}

func TestMiddlewareContentType(t *testing.T) {
    mux := http.NewServeMux()
    mux.HandleFunc("/", testHandler)
    srv := Middleware(schema, 1024)(mux)
    r := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(""))
    w := httptest.NewRecorder()
    srv.ServeHTTP(w, r)
    if w.Result().StatusCode != http.StatusUnsupportedMediaType {
        t.Fatalf("expected 415 got %d", w.Result().StatusCode)
    }
}
