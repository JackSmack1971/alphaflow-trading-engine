package validation

import (
    "encoding/json"
    "io"
    "net/http"

    "github.com/xeipuuv/gojsonschema"
)

// Middleware validates JSON requests against a schema.
func Middleware(schemaLoader gojsonschema.JSONLoader, maxSize int64) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if r.Header.Get("Content-Type") != "application/json" {
                http.Error(w, "unsupported content type", http.StatusUnsupportedMediaType)
                return
            }
            r.Body = http.MaxBytesReader(w, r.Body, maxSize)
            body, err := io.ReadAll(r.Body)
            if err != nil {
                http.Error(w, "request too large", http.StatusRequestEntityTooLarge)
                return
            }
            var data interface{}
            if err := json.Unmarshal(body, &data); err != nil {
                http.Error(w, "invalid json", http.StatusBadRequest)
                return
            }
            result, err := gojsonschema.Validate(schemaLoader, gojsonschema.NewGoLoader(data))
            if err != nil || !result.Valid() {
                http.Error(w, "invalid payload", http.StatusBadRequest)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}
